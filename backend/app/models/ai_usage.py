"""
AI usage tracking models for token consumption and cost analysis.

Tracks AI model usage at the message level for detailed analytics.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AiUsageCreate(BaseModel):
    """Request model for creating AI usage record.

    Attributes:
        model: AI model identifier (e.g., claude-sonnet-4-5-20250929)
        input_tokens: Number of input tokens consumed
        output_tokens: Number of output tokens generated
        latency_ms: Response latency in milliseconds (optional)
    """
    model: str = Field(..., max_length=100, description="AI model identifier")
    input_tokens: int = Field(default=0, ge=0, description="Input tokens")
    output_tokens: int = Field(default=0, ge=0, description="Output tokens")
    latency_ms: int = Field(default=0, ge=0, description="Latency in milliseconds")


class AiUsage(BaseModel):
    """Full AI usage entity model.

    Attributes:
        id: Usage record ID
        topic_id: ID of the parent topic
        message_id: ID of the message that triggered AI call
        model: AI model identifier
        input_tokens: Input tokens consumed
        output_tokens: Output tokens generated
        total_tokens: Sum of input and output tokens
        latency_ms: Response latency in milliseconds
        created_at: Creation timestamp
    """
    id: int
    topic_id: int
    message_id: int
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class AiUsageResponse(BaseModel):
    """Public AI usage response model.

    Attributes:
        id: Usage record ID
        topic_id: Parent topic ID
        message_id: Source message ID
        model: AI model identifier
        input_tokens: Input tokens
        output_tokens: Output tokens
        total_tokens: Total tokens
        latency_ms: Response latency
        created_at: Creation timestamp
    """
    id: int
    topic_id: int
    message_id: int
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserAiStats(BaseModel):
    """Aggregated AI usage statistics for a user.

    Attributes:
        user_id: User ID
        total_topics: Total number of topics created
        total_messages: Total number of messages
        total_input_tokens: Sum of all input tokens
        total_output_tokens: Sum of all output tokens
        total_tokens: Sum of all tokens
        avg_latency_ms: Average response latency
    """
    user_id: int
    total_topics: int = 0
    total_messages: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    avg_latency_ms: float = 0.0
