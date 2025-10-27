"""
토큰 사용량 모델
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TokenUsage(BaseModel):
    """토큰 사용량 모델"""
    id: Optional[int] = None
    user_id: int
    report_id: Optional[int] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    created_at: Optional[datetime] = None


class TokenUsageCreate(BaseModel):
    """토큰 사용량 생성 모델"""
    user_id: int
    report_id: Optional[int] = None
    input_tokens: int
    output_tokens: int
    total_tokens: int


class TokenUsageResponse(BaseModel):
    """토큰 사용량 응답 모델"""
    id: int
    user_id: int
    report_id: Optional[int]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    created_at: datetime


class UserTokenStats(BaseModel):
    """사용자별 토큰 통계 모델"""
    user_id: int
    username: str
    email: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    report_count: int
    last_usage: Optional[datetime]
