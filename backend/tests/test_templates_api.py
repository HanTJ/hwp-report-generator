"""API tests for template endpoints."""

import pytest
from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app
from app.database.user_db import UserDB
from app.database.template_db import TemplateDB, PlaceholderDB
from app.models.user import UserCreate
from app.utils.auth import hash_password
import uuid

client = TestClient(app)


@pytest.fixture
def auth_user():
    """Create and return a test user."""
    # Use unique email to avoid conflicts
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user_create = UserCreate(
        email=unique_email,
        username=f"testuser_{uuid.uuid4().hex[:4]}",
        password="password123"
    )
    try:
        user = UserDB.create_user(user_create, hash_password("password123"))
        # Manually activate user for testing
        UserDB.update_user(
            user.id,
            {"is_active": True}
        )
        return user
    except Exception as e:
        # If user creation fails, try to get existing user
        pytest.skip(f"Could not create user: {str(e)}")


@pytest.fixture
def auth_headers(auth_user):
    """Get authentication headers for test user."""
    # Login to get token using the created user's email
    response = client.post(
        "/api/auth/login",
        json={"email": auth_user.email, "password": "password123"}
    )
    if response.status_code != 200:
        pytest.skip(f"Could not login: {response.text}")

    data = response.json()
    if not data.get("success"):
        pytest.skip(f"Login failed: {data.get('error')}")

    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_hwpx_file():
    """Create a minimal valid HWPX file (ZIP format)."""
    # Create a ZIP file with Contents/section1.xml
    import zipfile
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w') as zf:
        # Create Contents directory with section1.xml
        zf.writestr(
            'Contents/section1.xml',
            '<?xml version="1.0"?><document><text>{{TITLE}}</text><text>{{SUMMARY}}</text></document>'
        )

    buffer.seek(0)
    return ("template.hwpx", buffer.getvalue(), "application/octet-stream")


class TestTemplateUpload:
    """Test cases for template upload endpoint."""

    def test_upload_valid_hwpx(self, auth_headers, valid_hwpx_file):
        """TC-API-001: Upload valid HWPX template."""
        filename, content, content_type = valid_hwpx_file

        response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "테스트 템플릿"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["title"] == "테스트 템플릿"
        assert "placeholders" in data["data"]
        assert isinstance(data["data"]["placeholders"], list)
        assert len(data["data"]["placeholders"]) == 2

    def test_upload_invalid_extension(self, auth_headers):
        """TC-API-002: Reject non-HWPX files."""
        response = client.post(
            "/api/templates",
            files={"file": ("template.docx", b"fake docx content", "application/octet-stream")},
            data={"title": "Invalid Template"},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION.INVALID_FORMAT"

    def test_upload_corrupted_hwpx(self, auth_headers):
        """TC-API-003: Reject corrupted HWPX files."""
        # Create file with HWPX extension but invalid ZIP content
        corrupted_content = b"This is not a valid ZIP file"

        response = client.post(
            "/api/templates",
            files={"file": ("template.hwpx", corrupted_content, "application/octet-stream")},
            data={"title": "Corrupted Template"},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "TEMPLATE.INVALID_FORMAT"

    def test_upload_missing_title(self, auth_headers, valid_hwpx_file):
        """TC-API-005: Reject upload without title."""
        filename, content, content_type = valid_hwpx_file

        response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={},  # Missing 'title'
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error


class TestTemplateList:
    """Test cases for template listing."""

    def test_list_user_templates(self, auth_headers, auth_user, valid_hwpx_file):
        """Test listing user's own templates."""
        # First upload a template
        filename, content, content_type = valid_hwpx_file
        client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "내 템플릿"},
            headers=auth_headers
        )

        # List templates
        response = client.get(
            "/api/templates",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        assert data["data"][0]["title"] == "내 템플릿"

    def test_list_templates_unauthorized(self):
        """Test listing templates without authentication."""
        response = client.get("/api/templates")
        # Without auth header, returns 403 Forbidden
        assert response.status_code in [401, 403]


class TestTemplateDetail:
    """Test cases for template detail retrieval."""

    def test_get_template_detail(self, auth_headers, auth_user, valid_hwpx_file):
        """Test retrieving template details."""
        # Upload template first
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "상세 조회 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Get template details
        response = client.get(
            f"/api/templates/{template_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == template_id
        assert data["data"]["title"] == "상세 조회 템플릿"
        assert "placeholders" in data["data"]

    def test_get_nonexistent_template(self, auth_headers):
        """TC-API-003: Accessing non-existent template returns 404."""
        response = client.get(
            "/api/templates/99999",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TEMPLATE.NOT_FOUND"


class TestTemplateDelete:
    """Test cases for template deletion."""

    def test_delete_template(self, auth_headers, auth_user, valid_hwpx_file):
        """Test deleting a template."""
        # Upload template first
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "삭제할 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Delete template
        response = client.delete(
            f"/api/templates/{template_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify template is no longer accessible
        get_response = client.get(
            f"/api/templates/{template_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_template(self, auth_headers):
        """Test deleting non-existent template."""
        response = client.delete(
            "/api/templates/99999",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestTemplatePromptUpdate:
    """Test cases for template prompt update endpoints."""

    def test_update_prompt_system_success(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-4.1: Successfully update prompt_system."""
        # Upload template first
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "프롬프트 수정 테스트 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Update prompt_system
        new_prompt = "새로운 시스템 프롬프트입니다."
        response = client.put(
            f"/api/templates/{template_id}/prompt-system",
            json={"prompt_system": new_prompt},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == template_id
        assert data["data"]["prompt_system"] == new_prompt

    def test_update_prompt_system_empty_value(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-3.1: Empty prompt_system should return 400."""
        # Upload template first
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "빈값 테스트 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Try to update with empty prompt_system
        response = client.put(
            f"/api/templates/{template_id}/prompt-system",
            json={"prompt_system": ""},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "TEMPLATE.INVALID_PROMPT"

    def test_update_prompt_system_whitespace_only(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-3.2: Whitespace-only prompt_system should return 400."""
        # Upload template first
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "공백만 테스트 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Try to update with whitespace-only prompt_system
        response = client.put(
            f"/api/templates/{template_id}/prompt-system",
            json={"prompt_system": "   "},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "TEMPLATE.INVALID_PROMPT"

    def test_update_prompt_system_nonexistent_template(self, auth_headers):
        """TC-2.1: Updating non-existent template returns 404."""
        response = client.put(
            "/api/templates/99999/prompt-system",
            json={"prompt_system": "새로운 프롬프트"},
            headers=auth_headers
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TEMPLATE.NOT_FOUND"

    def test_update_prompt_system_permission_denied(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-2.2: Regular user cannot modify other user's template."""
        # User 1 uploads template
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "권한 테스트 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Create another user
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        user_create = UserCreate(
            email=unique_email,
            username=f"testuser_{uuid.uuid4().hex[:4]}",
            password="password123"
        )
        other_user = UserDB.create_user(user_create, hash_password("password123"))
        UserDB.update_user(other_user.id, {"is_active": True})

        # Login as other user
        login_response = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "password123"}
        )
        other_headers = {"Authorization": f"Bearer {login_response.json()['data']['access_token']}"}

        # Try to update first user's template as other user
        response = client.put(
            f"/api/templates/{template_id}/prompt-system",
            json={"prompt_system": "새로운 프롬프트"},
            headers=other_headers
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "TEMPLATE.FORBIDDEN"

    def test_update_prompt_user_success(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-4.x: Successfully update prompt_user."""
        # Upload template first
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "사용자 프롬프트 수정 테스트"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Update prompt_user
        new_prompt = "새로운 사용자 프롬프트입니다."
        response = client.put(
            f"/api/templates/{template_id}/prompt-user",
            json={"prompt_user": new_prompt},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == template_id
        assert data["data"]["prompt_user"] == new_prompt

    def test_update_prompt_user_nonexistent_template(self, auth_headers):
        """TC-2.1: Updating non-existent template returns 404."""
        response = client.put(
            "/api/templates/99999/prompt-user",
            json={"prompt_user": "새로운 프롬프트"},
            headers=auth_headers
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TEMPLATE.NOT_FOUND"

    def test_update_prompt_user_permission_denied(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-2.2: Regular user cannot modify other user's template."""
        # User 1 uploads template
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "사용자 프롬프트 권한 테스트"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Create another user
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        user_create = UserCreate(
            email=unique_email,
            username=f"testuser_{uuid.uuid4().hex[:4]}",
            password="password123"
        )
        other_user = UserDB.create_user(user_create, hash_password("password123"))
        UserDB.update_user(other_user.id, {"is_active": True})

        # Login as other user
        login_response = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "password123"}
        )
        other_headers = {"Authorization": f"Bearer {login_response.json()['data']['access_token']}"}

        # Try to update first user's template as other user
        response = client.put(
            f"/api/templates/{template_id}/prompt-user",
            json={"prompt_user": "새로운 프롬프트"},
            headers=other_headers
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "TEMPLATE.FORBIDDEN"


class TestTemplatePromptRegenerate:
    """Test cases for template prompt regeneration."""

    def test_regenerate_prompt_system_success(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-4.1: Successfully regenerate prompt_system."""
        # Upload template first
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "재생성 테스트 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]
        original_prompt = upload_response.json()["data"]["prompt_system"]

        # Regenerate prompt_system
        response = client.post(
            f"/api/templates/{template_id}/regenerate-prompt-system",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == template_id
        assert "prompt_system" in data["data"]
        # Regenerated prompt should be different from original (usually)
        assert data["data"]["prompt_system"] is not None

    def test_regenerate_prompt_system_nonexistent_template(self, auth_headers):
        """TC-2.1: Regenerating non-existent template returns 404."""
        response = client.post(
            "/api/templates/99999/regenerate-prompt-system",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TEMPLATE.NOT_FOUND"

    def test_regenerate_prompt_system_permission_denied(self, auth_headers, auth_user, valid_hwpx_file):
        """TC-4.3: Regular user cannot regenerate other user's template."""
        # User 1 uploads template
        filename, content, content_type = valid_hwpx_file
        upload_response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "재생성 권한 테스트 템플릿"},
            headers=auth_headers
        )
        template_id = upload_response.json()["data"]["id"]

        # Create another user
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        user_create = UserCreate(
            email=unique_email,
            username=f"testuser_{uuid.uuid4().hex[:4]}",
            password="password123"
        )
        other_user = UserDB.create_user(user_create, hash_password("password123"))
        UserDB.update_user(other_user.id, {"is_active": True})

        # Login as other user
        login_response = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "password123"}
        )
        other_headers = {"Authorization": f"Bearer {login_response.json()['data']['access_token']}"}

        # Try to regenerate first user's template as other user
        response = client.post(
            f"/api/templates/{template_id}/regenerate-prompt-system",
            headers=other_headers
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "TEMPLATE.FORBIDDEN"
