"""
관리자 전용 API 라우터
"""
from fastapi import APIRouter, Depends
import secrets
import string

from app.models.user import UserResponse, UserUpdate
from app.models.token_usage import UserTokenStats
from app.database.user_db import UserDB
from app.database.token_usage_db import TokenUsageDB
from app.utils.auth import get_current_admin_user, hash_password
from app.utils.response_helper import success_response, error_response, ErrorCode

router = APIRouter(prefix="/api/admin", tags=["관리자"])


@router.get("/users")
async def get_all_users(current_admin = Depends(get_current_admin_user)):
    """모든 사용자 목록 조회 (관리자 전용).

    Args:
        current_admin: 현재 관리자 사용자

    Returns:
        표준 API 응답 (사용자 목록)
    """
    try:
        users = UserDB.get_all_users()

        user_list = [
            UserResponse(
                id=u.id,
                email=u.email,
                username=u.username,
                is_active=u.is_active,
                is_admin=u.is_admin,
                password_reset_required=u.password_reset_required,
                created_at=u.created_at
            ).dict()
            for u in users
        ]

        return success_response({
            "users": user_list,
            "total": len(user_list)
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="사용자 목록 조회 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.patch("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """사용자 승인 (관리자 전용).

    is_active를 True로 변경.

    Args:
        user_id: 승인할 사용자 ID
        current_admin: 현재 관리자 사용자

    Returns:
        표준 API 응답 (승인 성공 메시지)
    """
    try:
        user = UserDB.get_user_by_id(user_id)
        if not user:
            return error_response(
                code=ErrorCode.ADMIN_USER_NOT_FOUND,
                http_status=404,
                message="사용자를 찾을 수 없습니다."
            )

        if user.is_active:
            return success_response({
                "message": "이미 승인된 사용자입니다.",
                "user_id": user_id,
                "username": user.username
            })

        update = UserUpdate(is_active=True)
        UserDB.update_user(user_id, update)

        return success_response({
            "message": f"{user.username} 사용자가 승인되었습니다.",
            "user_id": user_id,
            "username": user.username
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="사용자 승인 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.patch("/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """사용자 승인 거부 (관리자 전용).

    is_active를 False로 변경.

    Args:
        user_id: 거부할 사용자 ID
        current_admin: 현재 관리자 사용자

    Returns:
        표준 API 응답 (거부 성공 메시지)
    """
    try:
        user = UserDB.get_user_by_id(user_id)
        if not user:
            return error_response(
                code=ErrorCode.ADMIN_USER_NOT_FOUND,
                http_status=404,
                message="사용자를 찾을 수 없습니다."
            )

        update = UserUpdate(is_active=False)
        UserDB.update_user(user_id, update)

        return success_response({
            "message": f"{user.username} 사용자의 승인이 취소되었습니다.",
            "user_id": user_id,
            "username": user.username
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="사용자 승인 취소 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """사용자 비밀번호 초기화 (관리자 전용).

    랜덤한 임시 비밀번호를 생성하여 설정.

    Args:
        user_id: 비밀번호를 초기화할 사용자 ID
        current_admin: 현재 관리자 사용자

    Returns:
        표준 API 응답 (임시 비밀번호 포함)
    """
    try:
        user = UserDB.get_user_by_id(user_id)
        if not user:
            return error_response(
                code=ErrorCode.ADMIN_USER_NOT_FOUND,
                http_status=404,
                message="사용자를 찾을 수 없습니다."
            )

        # 임시 비밀번호 생성 (12자리)
        alphabet = string.ascii_letters + string.digits
        temporary_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        # 비밀번호 해싱 및 업데이트
        hashed_password = hash_password(temporary_password)
        UserDB.update_password(user_id, hashed_password)

        # password_reset_required 플래그 설정
        update = UserUpdate(password_reset_required=True)
        UserDB.update_user(user_id, update)

        return success_response({
            "message": f"{user.username} 사용자의 비밀번호가 초기화되었습니다. 사용자는 다음 로그인 시 비밀번호를 변경해야 합니다.",
            "temporary_password": temporary_password,
            "user_id": user_id,
            "username": user.username
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="비밀번호 초기화 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.get("/token-usage")
async def get_all_token_usage(current_admin = Depends(get_current_admin_user)):
    """모든 사용자의 토큰 사용량 통계 조회 (관리자 전용).

    Args:
        current_admin: 현재 관리자 사용자

    Returns:
        표준 API 응답 (모든 사용자의 토큰 사용량 통계)
    """
    try:
        stats = TokenUsageDB.get_all_user_stats()

        return success_response({
            "stats": [s.dict() if hasattr(s, 'dict') else s for s in stats],
            "total": len(stats)
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="토큰 사용량 조회 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.get("/token-usage/{user_id}")
async def get_user_token_usage(
    user_id: int,
    current_admin = Depends(get_current_admin_user)
):
    """특정 사용자의 토큰 사용량 통계 조회 (관리자 전용).

    Args:
        user_id: 조회할 사용자 ID
        current_admin: 현재 관리자 사용자

    Returns:
        표준 API 응답 (특정 사용자의 토큰 사용량 통계)
    """
    try:
        stats = TokenUsageDB.get_user_stats(user_id)
        if not stats:
            return error_response(
                code=ErrorCode.ADMIN_USER_NOT_FOUND,
                http_status=404,
                message="사용자를 찾을 수 없습니다."
            )

        return success_response(stats.dict() if hasattr(stats, 'dict') else stats)

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="토큰 사용량 조회 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )
