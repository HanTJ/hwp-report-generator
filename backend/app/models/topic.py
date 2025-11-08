"""
Topic models for chat-based report system.

A topic represents a conversation thread about a specific report subject.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from shared.types.enums import TopicStatus


class TopicCreate(BaseModel):
    """Request model for creating a new topic.

    Attributes:
        input_prompt: User's original input describing the report subject
        language: Primary language for the report (default: 'ko')
        template_id: Optional template ID to use for dynamic system prompt generation
    """
    input_prompt: str = Field(..., min_length=1, max_length=1000, description="Report topic input")
    language: str = Field(default="ko", description="Primary language (ko/en)")
    template_id: Optional[int] = Field(default=None, description="Template ID for dynamic system prompt generation")


class TopicUpdate(BaseModel):
    """Request model for updating an existing topic.

    Attributes:
        generated_title: AI-generated title for the topic (optional)
        status: Topic status (active/archived/deleted) (optional)
    """
    generated_title: Optional[str] = Field(None, max_length=200, description="AI-generated title")
    status: Optional[TopicStatus] = Field(None, description="Topic status")


class Topic(BaseModel):
    """Full topic entity model.

    Attributes:
        id: Topic ID
        user_id: ID of the user who created the topic
        input_prompt: Original user input
        generated_title: AI-generated title (may be null initially)
        language: Primary language code
        status: Current topic status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    user_id: int
    input_prompt: str
    generated_title: Optional[str] = None
    language: str = "ko"
    status: TopicStatus = TopicStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2


class TopicResponse(BaseModel):
    """Public topic response model.

    Excludes internal fields. Suitable for API responses.

    Attributes:
        id: Topic ID
        input_prompt: Original user input
        generated_title: AI-generated title
        language: Primary language
        status: Topic status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    input_prompt: str
    generated_title: Optional[str] = None
    language: str
    status: TopicStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TopicListResponse(BaseModel):
    """Paginated list of topics.

    Attributes:
        topics: List of topic responses
        total: Total number of topics
        page: Current page number
        page_size: Number of items per page
    """
    topics: list[TopicResponse]
    total: int
    page: int = 1
    page_size: int = 20


class TopicMessageRequest(BaseModel):
    """Request model for asking a question on a topic.

    Attributes:
        user_message: The user's message or question
        template_id: Optional template ID to use for dynamic system prompt generation
        selected_artifact_ids: Optional list of artifact IDs to include in context
    """
    user_message: str = Field(..., min_length=1, max_length=5000)
    template_id: Optional[int] = Field(None, description="사용할 템플릿 ID (선택)")
    selected_artifact_ids: Optional[list[int]] = Field(None, description="컨텍스트에 포함할 아티팩트 ID 목록")
