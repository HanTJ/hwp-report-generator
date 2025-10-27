"""
인증 관련 API 라우터
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models.user import UserCreate, UserLogin, UserResponse, PasswordChange, UserUpdate
from app.database.user_db import UserDB
from app.utils.auth import (
    hash_password,
    verify_password,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user
)

router = APIRouter(prefix="/api/auth", tags=["인증"])


class TokenResponse(BaseModel):
    """토큰 응답 모델"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """메시지 응답 모델"""
    message: str


@router.post("/register", response_model=MessageResponse)
async def register(user_data: UserCreate):
    """
    회원가입 API

    - 이메일, 사용자명, 비밀번호를 입력받아 회원가입
    - 초기 상태는 is_active=False (관리자 승인 대기)
    """
    try:
        # 이메일 중복 확인
        existing_user = UserDB.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="이미 등록된 이메일입니다."
            )

        # 비밀번호 해싱
        hashed_password = hash_password(user_data.password)

        # 사용자 생성
        user = UserDB.create_user(user_data, hashed_password)

        return MessageResponse(
            message="회원가입이 완료되었습니다. 관리자의 승인을 기다려주세요."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"회원가입 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    로그인 API

    - 이메일과 비밀번호로 로그인
    - JWT 토큰 반환
    """
    try:
        # 사용자 인증
        user = authenticate_user(credentials.email, credentials.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )

        # 계정 활성화 확인
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="계정이 활성화되지 않았습니다. 관리자의 승인을 기다려주세요."
            )

        # JWT 토큰 생성
        access_token = create_access_token(
            data={"user_id": user.id, "email": user.email}
        )

        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_admin=user.is_admin,
            password_reset_required=user.password_reset_required,
            created_at=user.created_at
        )

        return TokenResponse(
            access_token=access_token,
            user=user_response
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"로그인 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_active_user)):
    """
    현재 로그인한 사용자 정보 조회
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        password_reset_required=current_user.password_reset_required,
        created_at=current_user.created_at
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user = Depends(get_current_user)):
    """
    로그아웃 API

    - JWT는 stateless이므로 클라이언트에서 토큰 삭제 처리
    """
    return MessageResponse(
        message="로그아웃되었습니다."
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user)
):
    """
    비밀번호 변경 API

    - 현재 비밀번호 확인 후 새 비밀번호로 변경
    - 변경 후 password_reset_required 플래그 해제
    """
    try:
        # 현재 비밀번호 확인
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="현재 비밀번호가 올바르지 않습니다."
            )

        # 새 비밀번호 해싱
        new_hashed_password = hash_password(password_data.new_password)

        # 비밀번호 업데이트
        success = UserDB.update_password(current_user.id, new_hashed_password)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="비밀번호 업데이트에 실패했습니다."
            )

        # password_reset_required 플래그 해제
        update = UserUpdate(password_reset_required=False)
        UserDB.update_user(current_user.id, update)

        return MessageResponse(
            message="비밀번호가 성공적으로 변경되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}"
        )
