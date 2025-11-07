"""Template 모델 정의.

사용자 커스텀 HWPX 템플릿과 플레이스홀더 관리를 위한 Pydantic 모델들입니다.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PlaceholderBase(BaseModel):
    """플레이스홀더 기본 모델."""

    placeholder_key: str = Field(..., description="플레이스홀더 키 (예: {{TITLE}})")


class PlaceholderCreate(PlaceholderBase):
    """플레이스홀더 생성 모델."""

    template_id: int = Field(..., description="템플릿 ID")


class Placeholder(PlaceholderCreate):
    """플레이스홀더 응답 모델."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlaceholderResponse(BaseModel):
    """API 응답용 플레이스홀더 모델."""

    key: str = Field(..., description="플레이스홀더 키 (예: {{TITLE}})")


class TemplateBase(BaseModel):
    """템플릿 기본 모델."""

    title: str = Field(..., description="템플릿 제목")
    description: Optional[str] = Field(None, description="템플릿 설명")


class TemplateCreate(TemplateBase):
    """템플릿 생성 모델 (내부용)."""

    filename: str = Field(..., description="원본 파일명")
    file_path: str = Field(..., description="저장 경로")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    sha256: str = Field(..., description="파일 무결성 체크용 해시")


class Template(TemplateCreate):
    """템플릿 응답 모델."""

    id: int
    user_id: int
    is_active: bool = Field(True, description="활성화 상태")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UploadTemplateRequest(BaseModel):
    """템플릿 업로드 요청 모델."""

    title: str = Field(..., description="템플릿 제목")


class UploadTemplateResponse(BaseModel):
    """템플릿 업로드 응답 모델."""

    id: int = Field(..., description="템플릿 ID")
    title: str = Field(..., description="템플릿 제목")
    filename: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    placeholders: List[PlaceholderResponse] = Field(..., description="플레이스홀더 목록")
    created_at: datetime = Field(..., description="생성 일시")


class TemplateListResponse(BaseModel):
    """템플릿 목록 응답 모델."""

    id: int = Field(..., description="템플릿 ID")
    title: str = Field(..., description="템플릿 제목")
    filename: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    created_at: datetime = Field(..., description="생성 일시")


class TemplateDetailResponse(BaseModel):
    """템플릿 상세 응답 모델."""

    id: int = Field(..., description="템플릿 ID")
    title: str = Field(..., description="템플릿 제목")
    filename: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    placeholders: List[PlaceholderResponse] = Field(..., description="플레이스홀더 목록")
    created_at: datetime = Field(..., description="생성 일시")


class AdminTemplateResponse(BaseModel):
    """관리자용 템플릿 응답 모델."""

    id: int = Field(..., description="템플릿 ID")
    title: str = Field(..., description="템플릿 제목")
    username: str = Field(..., description="사용자명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    placeholder_count: int = Field(..., description="플레이스홀더 개수")
    created_at: datetime = Field(..., description="생성 일시")
