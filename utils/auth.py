"""
인증 및 권한 관리 유틸리티
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from models.user import User
from database.user_db import UserDB

load_dotenv()

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 기본 24시간

# HTTP Bearer 스키마
security = HTTPBearer()


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    # bcrypt는 72바이트까지만 지원하므로 제한
    if len(password.encode('utf-8')) > 72:
        raise ValueError("비밀번호는 72바이트를 초과할 수 없습니다.")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """JWT 액세스 토큰 디코드"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """현재 로그인한 사용자 가져오기"""
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="인증 정보가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = UserDB.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """현재 활성화된 사용자 가져오기 (관리자 승인 완료)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="계정이 활성화되지 않았습니다. 관리자의 승인을 기다려주세요."
        )

    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """현재 관리자 사용자 가져오기"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="관리자 권한이 필요합니다."
        )

    return current_user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """사용자 인증"""
    user = UserDB.get_user_by_email(email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
