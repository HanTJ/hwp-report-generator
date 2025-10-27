"""
auth.py 유틸리티 함수 테스트
"""
import pytest
from datetime import timedelta
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """비밀번호 해싱 테스트"""

    def test_hash_password(self):
        """비밀번호 해싱 테스트"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

    def test_verify_password_success(self):
        """비밀번호 검증 성공 테스트"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """비밀번호 검증 실패 테스트"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


@pytest.mark.unit
@pytest.mark.auth
class TestJWTToken:
    """JWT 토큰 테스트"""

    def test_create_access_token(self):
        """액세스 토큰 생성 테스트"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expires(self):
        """만료 시간이 있는 토큰 생성 테스트"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_access_token_success(self):
        """토큰 디코딩 성공 테스트"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == 1

    def test_decode_access_token_invalid(self):
        """잘못된 토큰 디코딩 테스트"""
        from fastapi import HTTPException

        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)

        assert exc_info.value.status_code == 401

    def test_decode_access_token_expired(self):
        """만료된 토큰 디코딩 테스트"""
        from fastapi import HTTPException

        data = {"sub": "test@example.com"}
        # 음수 시간으로 이미 만료된 토큰 생성
        expires_delta = timedelta(minutes=-1)
        token = create_access_token(data, expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == 401
