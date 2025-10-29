"""
Topic management API router.

Handles CRUD operations for topics (conversation threads).
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.models.user import User
from app.models.topic import TopicCreate, TopicUpdate, TopicResponse, TopicListResponse
from app.models.message import MessageCreate
from app.models.artifact import ArtifactCreate
from app.models.ai_usage import AiUsageCreate
from app.database.topic_db import TopicDB
from app.database.message_db import MessageDB
from app.database.artifact_db import ArtifactDB
from app.database.ai_usage_db import AiUsageDB
from app.utils.auth import get_current_active_user
from app.utils.response_helper import success_response, error_response, ErrorCode
from shared.types.enums import TopicStatus
from shared.types.enums import MessageRole, ArtifactKind
from app.utils.markdown_builder import build_report_md
from app.utils.file_utils import next_artifact_version, build_artifact_paths, write_text, sha256_of
from app.utils.claude_client import ClaudeClient
import time
from shared.constants import ProjectPath

router = APIRouter(prefix="/api/topics", tags=["Topics"])


@router.post("", summary="Create a new topic")
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Creates a new topic (conversation thread).

    Request Body:
        - input_prompt: User's original input describing the report subject (required)
        - language: Primary language for the report (default: 'ko')

    Returns:
        Standard ApiResponse with TopicResponse data

    Error Codes:
        - TOPIC.CREATION_FAILED: Failed to create topic
        - SERVER.DATABASE_ERROR: Database operation failed

    Examples:
        Request:
        ```json
        {
          "input_prompt": "디지털뱅킹 트렌드 분석",
          "language": "ko"
        }
        ```

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "input_prompt": "디지털뱅킹 트렌드 분석",
            "generated_title": null,
            "language": "ko",
            "status": "active",
            "created_at": "2025-10-28T10:30:00",
            "updated_at": "2025-10-28T10:30:00"
          },
          "error": null,
          "meta": {"requestId": "req_abc123"},
          "feedback": []
        }
        ```
    """
    try:
        topic = TopicDB.create_topic(current_user.id, topic_data)
        return success_response(TopicResponse.model_validate(topic))

    except Exception as e:
        return error_response(
            code=ErrorCode.TOPIC_CREATION_FAILED,
            http_status=500,
            message="주제 생성에 실패했습니다.",
            details={"error": str(e)},
            hint="잠시 후 다시 시도해주세요."
        )


@router.post("/generate", summary="주제 입력 → 보고서 생성 → MD 저장")
async def generate_topic_report(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_active_user)
):
    """사용자 주제를 받아 Claude로 보고서 생성, 토픽/메시지/아티팩트/사용량 저장 후 경로 반환.

    Request Body:
        - input_prompt: 사용자가 입력한 주제(필수)
        - language: 기본 'ko'

    Returns:
        { "topic_id": int, "md_path": str }
    """
    try:
        if not topic_data.input_prompt or not topic_data.input_prompt.strip():
            return error_response(
                code=ErrorCode.VALIDATION_ERROR if hasattr(ErrorCode, 'VALIDATION_ERROR') else ErrorCode.TOPIC_CREATION_FAILED,
                http_status=400,
                message="입력 주제가 비어있습니다.",
                hint="3자 이상 내용을 입력해주세요."
            )

        # 1) Claude 호출
        start_ms = time.time()
        claude = ClaudeClient()
        result = claude.generate_report(topic_data.input_prompt.strip())
        latency_ms = int((time.time() - start_ms) * 1000)

        generated_title = result.get("title") or "보고서"

        # 2) 토픽 생성 및 제목 반영
        topic = TopicDB.create_topic(current_user.id, topic_data)
        TopicDB.update_topic(topic.id, TopicUpdate(generated_title=generated_title))

        # 3) 사용자 메시지 저장
        user_msg = MessageDB.create_message(
            topic.id,
            MessageCreate(role=MessageRole.USER, content=topic_data.input_prompt.strip())
        )

        # 4) Markdown 파일 생성 및 저장 + 어시스턴트 메시지 저장
        md_text = build_report_md(result)
        version = next_artifact_version(topic.id, ArtifactKind.MD, topic_data.language)
        _, md_path = build_artifact_paths(topic.id, version, "report.md")
        bytes_written = write_text(md_path, md_text)
        file_hash = sha256_of(md_path)

        # 어시스턴트 메시지 (생성 결과 텍스트 저장)
        assistant_msg = MessageDB.create_message(
            topic.id,
            MessageCreate(role=MessageRole.ASSISTANT, content=md_text)
        )

        # 5) 아티팩트 레코드 저장
        artifact = ArtifactDB.create_artifact(
            topic.id,
            assistant_msg.id,
            ArtifactCreate(
                kind=ArtifactKind.MD,
                locale=topic_data.language,
                version=version,
                filename=md_path.name,
                file_path=str(md_path),
                file_size=bytes_written,
                sha256=file_hash,
            )
        )

        # 6) AI 사용량 저장(가능하면)
        in_tok = getattr(claude, 'last_input_tokens', 0)
        out_tok = getattr(claude, 'last_output_tokens', 0)
        if (in_tok + out_tok) > 0:
            AiUsageDB.create_ai_usage(
                topic.id,
                assistant_msg.id,
                AiUsageCreate(
                    model=claude.model,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    latency_ms=latency_ms,
                )
            )

        return success_response({
            "topic_id": topic.id,
            "md_path": str(md_path)
        })

    except Exception as e:
        # Claude 호출/파일/DB 어느 단계에서도 예외 처리
        return error_response(
            code=ErrorCode.REPORT_GENERATION_FAILED,
            http_status=500,
            message="보고서 생성 처리 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.get("", summary="Get user's topics")
async def get_my_topics(
    status: Optional[TopicStatus] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves the current user's topics with pagination.

    Query Parameters:
        - status: Filter by topic status (active/archived/deleted) (optional)
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)

    Returns:
        Standard ApiResponse with TopicListResponse data

    Examples:
        Request: GET /api/topics?status=active&page=1&page_size=10

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "topics": [...],
            "total": 25,
            "page": 1,
            "page_size": 10
          },
          "error": null,
          "meta": {"requestId": "req_def456"},
          "feedback": []
        }
        ```
    """
    try:
        # Validate page_size
        if page_size > 100:
            page_size = 100

        offset = (page - 1) * page_size
        topics, total = TopicDB.get_topics_by_user(
            user_id=current_user.id,
            status=status,
            limit=page_size,
            offset=offset
        )

        topic_responses = [TopicResponse.model_validate(t) for t in topics]
        result = TopicListResponse(
            topics=topic_responses,
            total=total,
            page=page,
            page_size=page_size
        )

        return success_response(result)

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="주제 목록 조회에 실패했습니다.",
            details={"error": str(e)}
        )


@router.get("/{topic_id}", summary="Get topic by ID")
async def get_topic(
    topic_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves a specific topic by ID.

    Path Parameters:
        - topic_id: Topic ID

    Returns:
        Standard ApiResponse with TopicResponse data

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own this topic

    Examples:
        Request: GET /api/topics/1

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "input_prompt": "디지털뱅킹 트렌드 분석",
            "generated_title": "2025 디지털뱅킹 트렌드 분석 보고서",
            "language": "ko",
            "status": "active",
            "created_at": "2025-10-28T10:30:00",
            "updated_at": "2025-10-28T10:35:00"
          },
          "error": null,
          "meta": {"requestId": "req_ghi789"},
          "feedback": []
        }
        ```
    """
    topic = TopicDB.get_topic_by_id(topic_id)

    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다.",
            hint="주제 ID를 확인해주세요."
        )

    # Check ownership
    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제에 접근할 권한이 없습니다."
        )

    return success_response(TopicResponse.model_validate(topic))


@router.patch("/{topic_id}", summary="Update topic")
async def update_topic(
    topic_id: int,
    update_data: TopicUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Updates topic information.

    Path Parameters:
        - topic_id: Topic ID

    Request Body:
        - generated_title: AI-generated title (optional)
        - status: Topic status (active/archived/deleted) (optional)

    Returns:
        Standard ApiResponse with updated TopicResponse data

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own this topic

    Examples:
        Request: PATCH /api/topics/1
        ```json
        {
          "generated_title": "2025 디지털뱅킹 트렌드 분석 보고서",
          "status": "archived"
        }
        ```

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "generated_title": "2025 디지털뱅킹 트렌드 분석 보고서",
            "status": "archived",
            ...
          },
          "error": null,
          "meta": {"requestId": "req_jkl012"},
          "feedback": []
        }
        ```
    """
    topic = TopicDB.get_topic_by_id(topic_id)

    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다."
        )

    # Check ownership
    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제를 수정할 권한이 없습니다."
        )

    try:
        updated_topic = TopicDB.update_topic(topic_id, update_data)
        return success_response(TopicResponse.model_validate(updated_topic))

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="주제 수정에 실패했습니다.",
            details={"error": str(e)}
        )


@router.delete("/{topic_id}", summary="Delete topic")
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Deletes a topic (hard delete, cascades to messages/artifacts).

    Path Parameters:
        - topic_id: Topic ID

    Returns:
        Standard ApiResponse with success message

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own this topic

    Warning:
        This is a hard delete. All messages, artifacts, and AI usage records
        associated with this topic will be permanently deleted.

    Examples:
        Request: DELETE /api/topics/1

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "message": "주제가 삭제되었습니다."
          },
          "error": null,
          "meta": {"requestId": "req_mno345"},
          "feedback": []
        }
        ```
    """
    topic = TopicDB.get_topic_by_id(topic_id)

    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다."
        )

    # Check ownership
    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제를 삭제할 권한이 없습니다."
        )

    try:
        deleted = TopicDB.delete_topic(topic_id)
        if deleted:
            return success_response({"message": "주제가 삭제되었습니다."})
        else:
            return error_response(
                code=ErrorCode.TOPIC_NOT_FOUND,
                http_status=404,
                message="주제를 찾을 수 없습니다."
            )

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="주제 삭제에 실패했습니다.",
            details={"error": str(e)}
        )
