"""
관리자 API 라우터 테스트
"""
import pytest

from app.database.user_db import UserDB
from app.models.user import UserCreate, UserUpdate
from app.utils.auth import hash_password


@pytest.mark.api
class TestAdminRouter:
    """Admin API 테스트"""

    def test_get_all_users_as_admin(self, client, admin_auth_headers, create_test_user):
        resp = client.get("/api/admin/users", headers=admin_auth_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["success"] is True
        users = result["data"]["users"]
        assert isinstance(users, list)
        assert any(u["email"] == create_test_user.email for u in users)

    def test_approve_user(self, client, admin_auth_headers, test_db):
        # 비활성 사용자 생성
        pending = UserDB.create_user(
            UserCreate(email="pending@example.com", username="pending_user", password="Temp1234!@#"),
            hash_password("Temp1234!@#"),
        )
        assert pending.is_active is False

        resp = client.patch(f"/api/admin/users/{pending.id}/approve", headers=admin_auth_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["success"] is True
        assert "승인" in result["data"]["message"]

        updated = UserDB.get_user_by_id(pending.id)
        assert updated.is_active is True

    def test_reject_user(self, client, admin_auth_headers, test_db):
        # 활성 사용자 생성 후 비활성로 변경
        user = UserDB.create_user(
            UserCreate(email="reject@example.com", username="reject_user", password="Temp1234!@#"),
            hash_password("Temp1234!@#"),
        )
        UserDB.update_user(user.id, UserUpdate(is_active=True))

        resp = client.patch(f"/api/admin/users/{user.id}/reject", headers=admin_auth_headers)
        assert resp.status_code == 200
        updated = UserDB.get_user_by_id(user.id)
        assert updated.is_active is False

    def test_reset_user_password(self, client, admin_auth_headers, test_db):
        user = UserDB.create_user(
            UserCreate(email="reset@example.com", username="reset_user", password="OldPass123!@#"),
            hash_password("OldPass123!@#"),
        )
        # 활성화 필요 (관리자 엔드포인트에서는 필수는 아니지만 일반흐름 가정)
        UserDB.update_user(user.id, UserUpdate(is_active=True))

        resp = client.post(f"/api/admin/users/{user.id}/reset-password", headers=admin_auth_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["success"] is True
        assert "temporary_password" in result["data"]
        assert len(result["data"]["temporary_password"]) >= 8

        updated = UserDB.get_user_by_id(user.id)
        assert updated.password_reset_required is True

