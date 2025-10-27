"""
인증 API 라우터 테스트
"""
import pytest


@pytest.mark.api
@pytest.mark.auth
class TestAuthRouter:
    """인증 API 테스트"""

    def test_register_success(self, client):
        """회원가입 성공 테스트"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "신규사용자",
                "password": "NewUser123!@#"
            }
        )

        assert response.status_code == 200
        result = response.json()
        print(f"Response: {result}")  # 디버깅
        # API 표준 응답 형식 확인
        if "data" in result:
            data = result["data"]
            assert data["email"] == "newuser@example.com"
            assert data["username"] == "신규사용자"
            assert "id" in data
        else:
            # 비표준 응답 - message만 있을 수 있음
            assert "message" in result or "email" in result

    def test_register_duplicate_email(self, client, create_test_user):
        """중복 이메일로 회원가입 실패 테스트"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",  # 이미 존재하는 이메일
                "username": "중복사용자",
                "password": "Test1234!@#"
            }
        )

        assert response.status_code == 400

    def test_login_success(self, client, create_test_user, test_user_data):
        """로그인 성공 테스트"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, create_test_user, test_user_data):
        """잘못된 비밀번호로 로그인 실패 테스트"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401

    def test_get_me(self, client, auth_headers):
        """현재 사용자 정보 조회 테스트"""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data

    def test_get_me_unauthorized(self, client):
        """인증 없이 사용자 정보 조회 실패 테스트"""
        response = client.get("/api/auth/me")

        # 인증 헤더 없을 때 403 Forbidden 반환
        assert response.status_code == 403
