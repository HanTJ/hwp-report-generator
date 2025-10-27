"""
관리자 전용 API 라우터
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models.user import UserResponse, UserUpdate
from app.models.token_usage import UserTokenStats
from app.database.user_db import UserDB
from app.database.token_usage_db import TokenUsageDB
from app.utils.auth import get_current_admin_user, hash_password
import secrets
import string

router = APIRouter(prefix="/api/admin", tags=["관리자"])


class MessageResponse(BaseModel):
    """메시지 응답 모델"""
    message: str


class PasswordResetResponse(BaseModel):
    """비밀번호 초기화 응답 모델"""
    message: str
    temporary_password: str


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_admin = Depends(get_current_admin_user)):
    """
    모든 사용자 목록 조회 (관리자 전용)
    """
    try:
        users = UserDB.get_all_users()

        return [
            UserResponse(
                id=u.id,
                email=u.email,
                username=u.username,
                is_active=u.is_active,
                is_admin=u.is_admin,
                password_reset_required=u.password_reset_required,
                created_at=u.created_at
            )
            for u in users
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사용자 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/users/{user_id}/approve", response_model=MessageResponse)
async def approve_user(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """
    사용자 승인 (관리자 전용)

    - is_active를 True로 변경
    """
    try:
        user = UserDB.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        if user.is_active:
            return MessageResponse(message="이미 승인된 사용자입니다.")

        update = UserUpdate(is_active=True)
        UserDB.update_user(user_id, update)

        return MessageResponse(message=f"{user.username} 사용자가 승인되었습니다.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사용자 승인 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/users/{user_id}/reject", response_model=MessageResponse)
async def reject_user(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """
    사용자 승인 거부 (관리자 전용)

    - is_active를 False로 변경
    """
    try:
        user = UserDB.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        update = UserUpdate(is_active=False)
        UserDB.update_user(user_id, update)

        return MessageResponse(message=f"{user.username} 사용자의 승인이 취소되었습니다.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사용자 승인 취소 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/users/{user_id}/reset-password", response_model=PasswordResetResponse)
async def reset_user_password(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """
    사용자 비밀번호 초기화 (관리자 전용)

    - 랜덤한 임시 비밀번호 생성
    """
    try:
        user = UserDB.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 임시 비밀번호 생성 (12자리)
        alphabet = string.ascii_letters + string.digits
        temporary_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        # 비밀번호 해싱 및 업데이트
        hashed_password = hash_password(temporary_password)
        UserDB.update_password(user_id, hashed_password)

        # password_reset_required 플래그 설정
        update = UserUpdate(password_reset_required=True)
        UserDB.update_user(user_id, update)

        return PasswordResetResponse(
            message=f"{user.username} 사용자의 비밀번호가 초기화되었습니다. 사용자는 다음 로그인 시 비밀번호를 변경해야 합니다.",
            temporary_password=temporary_password
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"비밀번호 초기화 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/token-usage", response_model=List[UserTokenStats])
async def get_all_token_usage(current_admin = Depends(get_current_admin_user)):
    """
    모든 사용자의 토큰 사용량 통계 조회 (관리자 전용)
    """
    try:
        stats = TokenUsageDB.get_all_user_stats()
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"토큰 사용량 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/token-usage/{user_id}", response_model=UserTokenStats)
async def get_user_token_usage(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """
    특정 사용자의 토큰 사용량 통계 조회 (관리자 전용)
    """
    try:
        stats = TokenUsageDB.get_user_stats(user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        return stats

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"토큰 사용량 조회 중 오류가 발생했습니다: {str(e)}"
        )
