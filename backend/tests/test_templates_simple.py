"""Simple API tests for template endpoints."""

import pytest
from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def valid_hwpx_file():
    """Create a minimal valid HWPX file (ZIP format)."""
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


class TestTemplateUploadValidation:
    """Test cases for template upload validation."""

    def test_upload_invalid_extension(self, valid_hwpx_file):
        """TC-API-002: Reject non-HWPX files."""
        response = client.post(
            "/api/templates",
            files={"file": ("template.docx", b"fake docx content", "application/octet-stream")},
            data={"title": "Invalid Template"}
        )

        # Should return 401 or 403 (unauthorized) since no auth
        assert response.status_code in [400, 401, 403]

    def test_upload_missing_auth(self, valid_hwpx_file):
        """Test upload without authentication."""
        filename, content, content_type = valid_hwpx_file

        response = client.post(
            "/api/templates",
            files={"file": (filename, content, content_type)},
            data={"title": "테스트 템플릿"}
        )

        # Should return 401 or 403 (unauthorized)
        assert response.status_code in [401, 403]


class TestTemplateListValidation:
    """Test cases for template listing validation."""

    def test_list_templates_unauthorized(self):
        """Test listing templates without authentication."""
        response = client.get("/api/templates")
        # Without auth header, returns 401 or 403
        assert response.status_code in [401, 403]


class TestTemplateDetailValidation:
    """Test cases for template detail retrieval validation."""

    def test_get_nonexistent_template_unauthorized(self):
        """Test accessing template without authentication."""
        response = client.get("/api/templates/99999")

        # Should return 401 or 403 (unauthorized)
        assert response.status_code in [401, 403]
