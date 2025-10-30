"""
Topic management API router.

Handles CRUD operations for topics (conversation threads).
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.models.user import User
from app.models.topic import TopicCreate, TopicUpdate, TopicResponse, TopicListResponse
from app.models.message import MessageCreate, MessageResponse, AskRequest
from app.models.artifact import ArtifactCreate, ArtifactResponse
from app.models.ai_usage import AiUsageCreate
from app.database.topic_db import TopicDB
from app.database.message_db import MessageDB
from app.database.artifact_db import ArtifactDB
from app.database.ai_usage_db import AiUsageDB
from app.utils.auth import get_current_active_user
from app.utils.response_helper import success_response, error_response, ErrorCode
from shared.types.enums import TopicStatus, MessageRole, ArtifactKind
from app.utils.markdown_builder import build_report_md
from app.utils.file_utils import next_artifact_version, build_artifact_paths, write_text, sha256_of
from app.utils.claude_client import ClaudeClient
import time
import logging
from shared.constants import ProjectPath

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/topics", tags=["Topics"])


@router.post("", summary="Create a new topic")
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_active_user)
):
    """새로운 주제(대화 스레드)를 생성합니다.

    요청 본문(Request Body):
        - input_prompt: 사용자가 입력한 보고서 주제 또는 설명 (필수)
        - language: 보고서의 기본 언어 (기본값: 'ko')

    반환(Returns):
        TopicResponse 데이터를 포함한 표준 ApiResponse 객체를 반환합니다.

    에러 코드(Error Codes):
        - TOPIC.CREATION_FAILED: 주제 생성에 실패함
        - SERVER.DATABASE_ERROR: 데이터베이스 작업 중 오류 발생

    예시(Examples):
        요청(Request):  
        ```json
        {
        "input_prompt": "디지털뱅킹 트렌드 분석",
        "language": "ko"
        }
        ```

        응답(Response, 200):  
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
            "artifact_id": artifact.id
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
    """현재 사용자의 주제(Topic) 목록을 페이지네이션 형태로 조회합니다.

    쿼리 파라미터(Query Parameters):
        - status: 주제 상태 필터 (active / archived / deleted) (선택)
        - page: 페이지 번호 (기본값: 1)
        - page_size: 페이지당 항목 수 (기본값: 20, 최대: 100)

    반환(Returns):
        TopicListResponse 데이터를 포함한 표준 ApiResponse 객체를 반환합니다.

    예시(Examples):
        요청(Request):  
        GET /api/topics?status=active&page=1&page_size=10

        응답(Response, 200):  
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
    """특정 주제(Topic) ID로 주제 정보를 조회합니다.

    경로 파라미터(Path Parameters):
        - topic_id: 조회할 주제의 ID

    반환(Returns):
        TopicResponse 데이터를 포함한 표준 ApiResponse 객체를 반환합니다.

    에러 코드(Error Codes):
        - TOPIC.NOT_FOUND: 해당 주제를 찾을 수 없음
        - TOPIC.UNAUTHORIZED: 사용자가 해당 주제에 대한 소유 권한이 없음

    예시(Examples):
        요청(Request):  
        GET /api/topics/1

        응답(Response, 200):  
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
    """주제(Topic) 정보를 수정합니다.

    경로 파라미터(Path Parameters):
        - topic_id: 수정할 주제의 ID

    요청 본문(Request Body):
        - generated_title: AI가 생성한 제목 (선택)
        - status: 주제 상태 (active / archived / deleted) (선택)

    반환(Returns):
        수정된 TopicResponse 데이터를 포함한 표준 ApiResponse 객체를 반환합니다.

    에러 코드(Error Codes):
        - TOPIC.NOT_FOUND: 해당 주제를 찾을 수 없음
        - TOPIC.UNAUTHORIZED: 사용자가 해당 주제에 대한 소유 권한이 없음

    예시(Examples):
        요청(Request):  
        PATCH /api/topics/1  
        ```json
        {
        "generated_title": "2025 디지털뱅킹 트렌드 분석 보고서",
        "status": "archived"
        }
        ```

        응답(Response, 200):  
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
    """주제(Topic)를 삭제합니다. (하드 삭제 — 관련 메시지 및 아티팩트도 함께 삭제됨)

    경로 파라미터(Path Parameters):
        - topic_id: 삭제할 주제의 ID

    반환(Returns):
        성공 메시지를 포함한 표준 ApiResponse 객체를 반환합니다.

    에러 코드(Error Codes):
        - TOPIC.NOT_FOUND: 해당 주제를 찾을 수 없음
        - TOPIC.UNAUTHORIZED: 사용자가 해당 주제에 대한 소유 권한이 없음

    ⚠️ 경고(Warning):
        이 작업은 **하드 삭제(Hard Delete)** 방식으로 수행됩니다.  
        해당 주제와 연결된 모든 메시지(messages), 아티팩트(artifacts),  
        그리고 AI 사용 기록(ai_usage)은 **영구적으로 삭제**됩니다.

    예시(Examples):
        요청(Request):  
        DELETE /api/topics/1

        응답(Response, 200):  
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


@router.post("/{topic_id}/ask", summary="Ask question in conversation")
async def ask(
    topic_id: int,
    body: AskRequest,
    current_user: User = Depends(get_current_active_user)
):
    """대화(Conversation) 맥락에서 질문을 수행합니다.

    매개변수(Args):
        - topic_id: 질문이 속한 주제의 ID
        - body: 요청 본문 (질문 내용 및 옵션 포함)
        - current_user: 인증된 사용자 정보

    반환(Returns):
        사용자 메시지(user_message), AI 응답(assistant_message),  
        생성된 아티팩트(artifact), 토큰 사용 정보(usage)를 포함한 표준 ApiResponse 객체를 반환합니다.

    에러 코드(Error Codes):
        - TOPIC.NOT_FOUND: 해당 주제를 찾을 수 없음
        - TOPIC.UNAUTHORIZED: 사용자가 해당 주제에 대한 소유 권한이 없음
        - VALIDATION.REQUIRED_FIELD: 입력 내용(content)이 비어 있음
        - ARTIFACT.NOT_FOUND: 지정된 아티팩트를 찾을 수 없음
        - ARTIFACT.INVALID_KIND: 해당 아티팩트는 MD 형식이 아님
        - ARTIFACT.UNAUTHORIZED: 다른 사용자의 아티팩트에 접근 시도
        - MESSAGE.CONTEXT_TOO_LARGE: 대화 컨텍스트 크기가 허용 한도를 초과함
        - SERVER.SERVICE_UNAVAILABLE: Claude API 호출 실패
    """


    # === 1단계: 권한 및 검증 ===
    logger.info(f"[ASK] Start - topic_id={topic_id}, user_id={current_user.id}")

    topic = TopicDB.get_topic_by_id(topic_id)
    if not topic:
        logger.warning(f"[ASK] Topic not found - topic_id={topic_id}")
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="토픽을 찾을 수 없습니다."
        )

    if topic.user_id != current_user.id and not current_user.is_admin:
        logger.warning(f"[ASK] Unauthorized - topic_id={topic_id}, owner={topic.user_id}, requester={current_user.id}")
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 토픽에 접근할 권한이 없습니다."
        )

    content = (body.content or "").strip()
    if not content:
        logger.warning(f"[ASK] Empty content - topic_id={topic_id}")
        return error_response(
            code=ErrorCode.VALIDATION_REQUIRED_FIELD,
            http_status=400,
            message="입력 메시지가 비어있습니다.",
            hint="1자 이상 입력해주세요."
        )

    if len(content) > 50000:
        logger.warning(f"[ASK] Content too long - topic_id={topic_id}, length={len(content)}")
        return error_response(
            code=ErrorCode.VALIDATION_MAX_LENGTH_EXCEEDED,
            http_status=400,
            message="입력 메시지가 너무 깁니다.",
            hint="50,000자 이하로 입력해주세요."
        )

    # === 2단계: 사용자 메시지 저장 ===
    logger.info(f"[ASK] Saving user message - topic_id={topic_id}, length={len(content)}")
    user_msg = MessageDB.create_message(
        topic_id,
        MessageCreate(role=MessageRole.USER, content=content)
    )
    logger.info(f"[ASK] User message saved - message_id={user_msg.id}, seq_no={user_msg.seq_no}")

    # === 3단계: 참조 문서 선택 ===
    reference_artifact = None
    if body.artifact_id is not None:
        logger.info(f"[ASK] Loading specified artifact - artifact_id={body.artifact_id}")
        reference_artifact = ArtifactDB.get_artifact_by_id(body.artifact_id)

        if not reference_artifact:
            logger.warning(f"[ASK] Artifact not found - artifact_id={body.artifact_id}")
            return error_response(
                code=ErrorCode.ARTIFACT_NOT_FOUND,
                http_status=404,
                message="지정한 아티팩트를 찾을 수 없습니다."
            )

        if reference_artifact.topic_id != topic_id:
            logger.warning(f"[ASK] Artifact topic mismatch - artifact.topic_id={reference_artifact.topic_id}, request.topic_id={topic_id}")
            return error_response(
                code=ErrorCode.ARTIFACT_UNAUTHORIZED,
                http_status=403,
                message="이 아티팩트에 접근할 권한이 없습니다."
            )

        if reference_artifact.kind != ArtifactKind.MD:
            logger.warning(f"[ASK] Invalid artifact kind - artifact_id={body.artifact_id}, kind={reference_artifact.kind}")
            return error_response(
                code=ErrorCode.ARTIFACT_INVALID_KIND,
                http_status=400,
                message="MD 형식의 아티팩트만 참조할 수 있습니다.",
                details={"current_kind": reference_artifact.kind.value}
            )
    else:
        logger.info(f"[ASK] Loading latest MD artifact - topic_id={topic_id}")
        reference_artifact = ArtifactDB.get_latest_artifact_by_kind(
            topic_id, ArtifactKind.MD, topic.language
        )
        if reference_artifact:
            logger.info(f"[ASK] Latest artifact found - artifact_id={reference_artifact.id}, version={reference_artifact.version}")
        else:
            logger.info(f"[ASK] No MD artifact found - proceeding without reference")

    # === 4단계: 컨텍스트 구성 ===
    logger.info(f"[ASK] Building context - topic_id={topic_id}")

    all_messages = MessageDB.get_messages_by_topic(topic_id)
    logger.info(f"[ASK] Total messages in topic: {len(all_messages)}")

    # User 메시지 필터링
    user_messages = [m for m in all_messages if m.role == MessageRole.USER]
    if body.max_messages is not None:
        user_messages = user_messages[-body.max_messages:]
    logger.info(f"[ASK] User messages to include: {len(user_messages)}")

    # Assistant 메시지 필터링 (참조 문서 생성 메시지만)
    assistant_messages = []
    if reference_artifact:
        ref_msg = MessageDB.get_message_by_id(reference_artifact.message_id)
        if ref_msg:
            assistant_messages = [ref_msg]
            logger.info(f"[ASK] Including reference assistant message - message_id={ref_msg.id}")

    # 컨텍스트 배열 구성
    context_messages = sorted(
        user_messages + assistant_messages,
        key=lambda m: m.seq_no
    )

    # 문서 내용 주입
    if body.include_artifact_content and reference_artifact:
        logger.info(f"[ASK] Loading artifact content - artifact_id={reference_artifact.id}, path={reference_artifact.file_path}")

        try:
            with open(reference_artifact.file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            original_length = len(md_content)
            MAX_MD_CHARS = 30000
            if len(md_content) > MAX_MD_CHARS:
                md_content = md_content[:MAX_MD_CHARS] + "\n\n... (truncated)"
                logger.info(f"[ASK] Artifact content truncated - original={original_length}, truncated={MAX_MD_CHARS}")

            # Create a temporary message-like object for artifact content
            class ArtifactMessage:
                def __init__(self, content, seq_no):
                    self.role = MessageRole.USER
                    self.content = content
                    self.seq_no = seq_no

            artifact_msg = ArtifactMessage(
                content=f"""현재 보고서(MD) 원문입니다. 개정 시 이를 기준으로 반영하세요.

```markdown
{md_content}
```""",
                seq_no=context_messages[-1].seq_no + 0.5 if context_messages else 0
            )

            context_messages.append(artifact_msg)
            logger.info(f"[ASK] Artifact content injected - length={len(md_content)}")

        except Exception as e:
            logger.error(f"[ASK] Failed to load artifact content - error={str(e)}")
            return error_response(
                code=ErrorCode.ARTIFACT_DOWNLOAD_FAILED,
                http_status=500,
                message="아티팩트 파일을 읽을 수 없습니다.",
                details={"error": str(e)}
            )

    # Claude 메시지 배열 변환
    claude_messages = [
        {"role": m.role.value, "content": m.content}
        for m in context_messages
    ]

    # 길이 검증
    total_chars = sum(len(msg["content"]) for msg in claude_messages)
    MAX_CONTEXT_CHARS = 50000

    logger.info(f"[ASK] Context size - messages={len(claude_messages)}, total_chars={total_chars}, max={MAX_CONTEXT_CHARS}")

    if total_chars > MAX_CONTEXT_CHARS:
        logger.warning(f"[ASK] Context too large - total_chars={total_chars}")
        return error_response(
            code=ErrorCode.MESSAGE_CONTEXT_TOO_LARGE,
            http_status=400,
            message="컨텍스트 크기가 너무 큽니다.",
            details={"total_chars": total_chars, "max_chars": MAX_CONTEXT_CHARS},
            hint="max_messages를 줄이거나 include_artifact_content를 false로 설정해주세요."
        )

    # 시스템 프롬프트 구성
    if body.system_prompt:
        system_prompt = body.system_prompt
        logger.info(f"[ASK] Using custom system prompt - length={len(system_prompt)}")
    else:
        default_prompt = """당신은 금융 기관의 전문 보고서 작성자입니다.
사용자의 요청에 따라 전문적이고 격식있는 금융 업무보고서를 Markdown 형식으로 작성해주세요.

보고서는 다음 섹션을 포함해야 합니다:
- # 제목 (H1)
- ## 요약 (H2)
- ## 배경 및 목적 (H2)
- ## 주요 내용 (H2)
- ## 결론 및 제언 (H2)

명확하고 이해하기 쉽게 작성하되, 금융 용어와 데이터를 적절히 활용하여 신뢰성을 높여주세요.
모든 출력은 Markdown 형식이어야 합니다."""

        topic_context = f"\n\n**대화 주제**: {topic.input_prompt}\n이전 메시지를 문맥으로 활용하여 일관된 문체와 구조로 답변하세요."
        system_prompt = default_prompt + topic_context
        logger.info(f"[ASK] Using default system prompt with topic context")

    # === 5단계: Claude 호출 ===
    logger.info(f"[ASK] Calling Claude API - messages={len(claude_messages)}")

    try:
        t0 = time.time()

        claude_client = ClaudeClient()
        response_text, input_tokens, output_tokens = claude_client.chat_completion(
            claude_messages,
            system_prompt
        )

        latency_ms = int((time.time() - t0) * 1000)

        logger.info(f"[ASK] Claude response received - input_tokens={input_tokens}, output_tokens={output_tokens}, latency_ms={latency_ms}")

    except Exception as e:
        logger.error(f"[ASK] Claude API call failed - error={str(e)}")
        return error_response(
            code=ErrorCode.SERVER_SERVICE_UNAVAILABLE,
            http_status=503,
            message="AI 응답 생성 중 오류가 발생했습니다.",
            details={"error": str(e)},
            hint="잠시 후 다시 시도해주세요."
        )

    # === 6단계: Assistant 메시지 저장 ===
    logger.info(f"[ASK] Saving assistant message - topic_id={topic_id}, length={len(response_text)}")

    asst_msg = MessageDB.create_message(
        topic_id,
        MessageCreate(role=MessageRole.ASSISTANT, content=response_text)
    )

    logger.info(f"[ASK] Assistant message saved - message_id={asst_msg.id}, seq_no={asst_msg.seq_no}")

    # === 7단계: MD 파일 저장 (필수) ===
    logger.info(f"[ASK] Saving MD artifact - topic_id={topic_id}")

    try:
        # 버전 계산
        version = next_artifact_version(topic_id, ArtifactKind.MD, topic.language)
        logger.info(f"[ASK] Artifact version - version={version}")

        # 파일 경로 생성
        base_dir, md_path = build_artifact_paths(topic_id, version, "report.md")
        logger.info(f"[ASK] Artifact path - path={md_path}")

        # 파일 저장
        bytes_written = write_text(md_path, response_text)
        file_hash = sha256_of(md_path)

        logger.info(f"[ASK] File written - size={bytes_written}, hash={file_hash[:16]}...")

        # Artifact DB 레코드 생성
        artifact = ArtifactDB.create_artifact(
            topic_id,
            asst_msg.id,
            ArtifactCreate(
                kind=ArtifactKind.MD,
                locale=topic.language,
                version=version,
                filename=md_path.name,
                file_path=str(md_path),
                file_size=bytes_written,
                sha256=file_hash
            )
        )

        logger.info(f"[ASK] Artifact created - artifact_id={artifact.id}, version={artifact.version}")

    except Exception as e:
        logger.error(f"[ASK] Failed to save artifact - error={str(e)}")
        return error_response(
            code=ErrorCode.ARTIFACT_CREATION_FAILED,
            http_status=500,
            message="응답 파일 저장 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )

    # === 8단계: AI 사용량 저장 ===
    logger.info(f"[ASK] Saving AI usage - message_id={asst_msg.id}")

    try:
        AiUsageDB.create_ai_usage(
            topic_id,
            asst_msg.id,
            AiUsageCreate(
                model=claude_client.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms
            )
        )

        logger.info(f"[ASK] AI usage saved")

    except Exception as e:
        logger.error(f"[ASK] Failed to save AI usage - error={str(e)}")
        # 사용량 저장 실패는 치명적이지 않으므로 계속 진행

    # === 9단계: 성공 응답 반환 ===
    logger.info(f"[ASK] Success - topic_id={topic_id}, artifact_id={artifact.id}")

    return success_response({
        "topic_id": topic_id,
        "user_message": MessageResponse.model_validate(user_msg).model_dump(),
        "assistant_message": MessageResponse.model_validate(asst_msg).model_dump(),
        "artifact": ArtifactResponse.model_validate(artifact).model_dump(),
        "usage": {
            "model": claude_client.model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms
        }
    })
