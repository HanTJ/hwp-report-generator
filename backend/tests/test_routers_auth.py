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
        # 표준 API 응답 형식 확인
        assert result["success"] is True
        assert result["data"] is not None
        assert "message" in result["data"]
        assert "email" in result["data"]

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
        result = response.json()
        assert result["success"] is True
        assert "access_token" in result["data"]
        assert result["data"]["token_type"] == "bearer"

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
        result = response.json()
        assert result["success"] is True
        assert "email" in result["data"]
        assert "username" in result["data"]

    def test_get_me_unauthorized(self, client):
        """인증 없이 사용자 정보 조회 실패 테스트"""
        response = client.get("/api/auth/me")

        # 인증 헤더 없을 때 403 Forbidden 반환
        assert response.status_code == 403

    def test_logout_success(self, client, auth_headers):
        """로그아웃 성공 테스트"""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "message" in result["data"]

    def test_change_password_success(self, client, auth_headers, create_test_user, test_user_data):
        """비밀번호 변경 성공 테스트"""
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": test_user_data["password"],
                "new_password": "NewPass1234!@#"
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "message" in result["data"]

    def test_change_password_wrong_current(self, client, auth_headers):
        """현재 비밀번호가 틀린 경우 400"""
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "Wrong123!",
                "new_password": "Another1234!@#"
            }
        )
        assert response.status_code == 400
