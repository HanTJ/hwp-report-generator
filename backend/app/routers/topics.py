"""
Topic management API router.

Handles CRUD operations for topics (conversation threads).
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.models.user import User
from app.models.topic import TopicCreate, TopicUpdate, TopicResponse, TopicListResponse
from app.database.topic_db import TopicDB
from app.utils.auth import get_current_active_user
from app.utils.response_helper import success_response, error_response, ErrorCode
from shared.types.enums import TopicStatus

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
