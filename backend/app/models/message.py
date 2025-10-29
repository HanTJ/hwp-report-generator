"""
Message models for chat-based conversation.

Messages represent individual turns in a conversation (user/assistant).
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from shared.types.enums import MessageRole


class MessageCreate(BaseModel):
    """Request model for creating a new message.

    Attributes:
        role: Message role (user/assistant/system)
        content: Message content text
    """
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., min_length=1, max_length=50000, description="Message content")


class Message(BaseModel):
    """Full message entity model.

    Attributes:
        id: Message ID
        topic_id: ID of the parent topic
        role: Message role (user/assistant/system)
        content: Message text content
        seq_no: Sequential number within the topic (for ordering)
        created_at: Creation timestamp
    """
    id: int
    topic_id: int
    role: MessageRole
    content: str
    seq_no: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Public message response model.

    Suitable for API responses.

    Attributes:
        id: Message ID
        topic_id: Parent topic ID
        role: Message role
        content: Message content
        seq_no: Sequential order
        created_at: Creation timestamp
    """
    id: int
    topic_id: int
    role: MessageRole
    content: str
    seq_no: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Paginated list of messages.

    Attributes:
        messages: List of message responses
        total: Total number of messages in the topic
        topic_id: Parent topic ID
    """
    messages: list[MessageResponse]
    total: int
    topic_id: int
