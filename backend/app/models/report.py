"""
보고서 모델
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Report(BaseModel):
    """보고서 모델"""
    id: Optional[int] = None
    user_id: int
    topic: str = Field(..., min_length=3)
    title: str
    filename: str
    file_path: str
    file_size: int = 0
    created_at: Optional[datetime] = None


class ReportCreate(BaseModel):
    """보고서 생성 요청 모델"""
    topic: str = Field(..., min_length=3)


class ReportResponse(BaseModel):
    """보고서 응답 모델"""
    id: int
    user_id: int
    topic: str
    title: str
    filename: str
    file_size: int
    created_at: datetime


class ReportListResponse(BaseModel):
    """보고서 목록 응답 모델"""
    total: int
    reports: list[ReportResponse]
