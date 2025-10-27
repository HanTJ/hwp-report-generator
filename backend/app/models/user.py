"""
사용자 모델
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """사용자 모델"""
    id: Optional[int] = None
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str
    is_active: bool = False  # 관리자 승인 대기
    is_admin: bool = False
    password_reset_required: bool = False  # 비밀번호 변경 필요 여부
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """사용자 생성 요청 모델"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """사용자 로그인 요청 모델"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """사용자 응답 모델 (비밀번호 제외)"""
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool
    password_reset_required: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """사용자 정보 수정 모델"""
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password_reset_required: Optional[bool] = None


class PasswordChange(BaseModel):
    """비밀번호 변경 요청 모델"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
