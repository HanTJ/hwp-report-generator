"""
Message management API router.

Handles message creation and retrieval for topics (chat conversations).
"""
from fastapi import APIRouter, Depends
from typing import Optional

from app.models.user import User
from app.models.message import MessageCreate, MessageResponse, MessageListResponse
from app.database.topic_db import TopicDB
from app.database.message_db import MessageDB
from app.utils.auth import get_current_active_user
from app.utils.response_helper import success_response, error_response, ErrorCode
from shared.types.enums import MessageRole

router = APIRouter(prefix="/api/topics/{topic_id}/messages", tags=["Messages"])


@router.post("", summary="Create a new message")
async def create_message(
    topic_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Creates a new message in a topic.

    Path Parameters:
        - topic_id: Topic ID

    Request Body:
        - role: Message role (user/assistant/system)
        - content: Message content text

    Returns:
        Standard ApiResponse with MessageResponse data

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own this topic
        - MESSAGE.CREATION_FAILED: Failed to create message

    Note:
        When role is 'user', this will trigger AI response generation.
        The AI response will be automatically created as a follow-up message.

    Examples:
        Request: POST /api/topics/1/messages
        ```json
        {
          "role": "user",
          "content": "디지털뱅킹 트렌드에 대한 보고서를 작성해주세요."
        }
        ```

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "topic_id": 1,
            "role": "user",
            "content": "디지털뱅킹 트렌드에 대한 보고서를 작성해주세요.",
            "seq_no": 1,
            "created_at": "2025-10-28T10:30:00"
          },
          "error": null,
          "meta": {"requestId": "req_abc123"},
          "feedback": []
        }
        ```
    """
    # Check topic exists and user owns it
    topic = TopicDB.get_topic_by_id(topic_id)
    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다."
        )

    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제에 메시지를 추가할 권한이 없습니다."
        )

    try:
        message = MessageDB.create_message(topic_id, message_data)
        return success_response(MessageResponse.model_validate(message))

    except Exception as e:
        return error_response(
            code=ErrorCode.MESSAGE_CREATION_FAILED,
            http_status=500,
            message="메시지 생성에 실패했습니다.",
            details={"error": str(e)},
            hint="잠시 후 다시 시도해주세요."
        )


@router.get("", summary="Get messages in a topic")
async def get_messages(
    topic_id: int,
    limit: Optional[int] = None,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves messages in a topic ordered by sequence number.

    Path Parameters:
        - topic_id: Topic ID

    Query Parameters:
        - limit: Maximum number of messages to return (optional, default: all)
        - offset: Number of messages to skip (default: 0)

    Returns:
        Standard ApiResponse with MessageListResponse data

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own this topic

    Examples:
        Request: GET /api/topics/1/messages?limit=10&offset=0

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "messages": [
              {
                "id": 1,
                "topic_id": 1,
                "role": "user",
                "content": "디지털뱅킹 트렌드에 대한 보고서를 작성해주세요.",
                "seq_no": 1,
                "created_at": "2025-10-28T10:30:00"
              },
              {
                "id": 2,
                "topic_id": 1,
                "role": "assistant",
                "content": "# 디지털뱅킹 트렌드 분석 보고서...",
                "seq_no": 2,
                "created_at": "2025-10-28T10:30:15"
              }
            ],
            "total": 2,
            "topic_id": 1
          },
          "error": null,
          "meta": {"requestId": "req_def456"},
          "feedback": []
        }
        ```
    """
    # Check topic exists and user owns it
    topic = TopicDB.get_topic_by_id(topic_id)
    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다."
        )

    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제의 메시지를 조회할 권한이 없습니다."
        )

    try:
        messages = MessageDB.get_messages_by_topic(topic_id, limit, offset)
        total = MessageDB.get_message_count_by_topic(topic_id)

        message_responses = [MessageResponse.model_validate(m) for m in messages]
        result = MessageListResponse(
            messages=message_responses,
            total=total,
            topic_id=topic_id
        )

        return success_response(result)

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="메시지 목록 조회에 실패했습니다.",
            details={"error": str(e)}
        )


@router.get("/{message_id}", summary="Get message by ID")
async def get_message(
    topic_id: int,
    message_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves a specific message by ID.

    Path Parameters:
        - topic_id: Topic ID
        - message_id: Message ID

    Returns:
        Standard ApiResponse with MessageResponse data

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own this topic
        - MESSAGE.NOT_FOUND: Message not found

    Examples:
        Request: GET /api/topics/1/messages/2

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "id": 2,
            "topic_id": 1,
            "role": "assistant",
            "content": "# 디지털뱅킹 트렌드 분석 보고서...",
            "seq_no": 2,
            "created_at": "2025-10-28T10:30:15"
          },
          "error": null,
          "meta": {"requestId": "req_ghi789"},
          "feedback": []
        }
        ```
    """
    # Check topic exists and user owns it
    topic = TopicDB.get_topic_by_id(topic_id)
    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다."
        )

    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제의 메시지를 조회할 권한이 없습니다."
        )

    message = MessageDB.get_message_by_id(message_id)
    if not message:
        return error_response(
            code=ErrorCode.MESSAGE_NOT_FOUND,
            http_status=404,
            message="메시지를 찾을 수 없습니다."
        )

    # Verify message belongs to topic
    if message.topic_id != topic_id:
        return error_response(
            code=ErrorCode.MESSAGE_NOT_FOUND,
            http_status=404,
            message="이 주제에 해당 메시지가 없습니다."
        )

    return success_response(MessageResponse.model_validate(message))


@router.delete("/{message_id}", summary="Delete message")
async def delete_message(
    topic_id: int,
    message_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Deletes a message (hard delete, cascades to artifacts/ai_usage).

    Path Parameters:
        - topic_id: Topic ID
        - message_id: Message ID

    Returns:
        Standard ApiResponse with success message

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own this topic
        - MESSAGE.NOT_FOUND: Message not found

    Warning:
        This is a hard delete. All artifacts and AI usage records
        associated with this message will be permanently deleted.

    Examples:
        Request: DELETE /api/topics/1/messages/2

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "message": "메시지가 삭제되었습니다."
          },
          "error": null,
          "meta": {"requestId": "req_jkl012"},
          "feedback": []
        }
        ```
    """
    # Check topic exists and user owns it
    topic = TopicDB.get_topic_by_id(topic_id)
    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다."
        )

    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제의 메시지를 삭제할 권한이 없습니다."
        )

    message = MessageDB.get_message_by_id(message_id)
    if not message:
        return error_response(
            code=ErrorCode.MESSAGE_NOT_FOUND,
            http_status=404,
            message="메시지를 찾을 수 없습니다."
        )

    # Verify message belongs to topic
    if message.topic_id != topic_id:
        return error_response(
            code=ErrorCode.MESSAGE_NOT_FOUND,
            http_status=404,
            message="이 주제에 해당 메시지가 없습니다."
        )

    try:
        deleted = MessageDB.delete_message(message_id)
        if deleted:
            return success_response({"message": "메시지가 삭제되었습니다."})
        else:
            return error_response(
                code=ErrorCode.MESSAGE_NOT_FOUND,
                http_status=404,
                message="메시지를 찾을 수 없습니다."
            )

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="메시지 삭제에 실패했습니다.",
            details={"error": str(e)}
        )
