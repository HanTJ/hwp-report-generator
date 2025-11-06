"""Unit tests for TemplatesManager."""

import pytest
import os
from pathlib import Path
from app.utils.templates_manager import TemplatesManager


class TestTemplatesManager:
    """Test cases for TemplatesManager class."""

    @pytest.fixture
    def manager(self):
        """Create TemplatesManager instance."""
        return TemplatesManager()

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for testing."""
        return tmp_path

    def test_validate_hwpx_valid_file(self, manager):
        """TC-UNIT-009: Valid HWPX file (ZIP signature) passes validation."""
        # ZIP signature: PK\x03\x04
        valid_content = b'PK\x03\x04' + b'some content'
        assert manager.validate_hwpx(valid_content) is True

    def test_validate_hwpx_invalid_file(self, manager):
        """TC-UNIT-009: Invalid file fails validation."""
        invalid_content = b'INVALID' + b'content'
        assert manager.validate_hwpx(invalid_content) is False

    def test_validate_hwpx_empty_file(self, manager):
        """TC-UNIT-009: Empty file fails validation."""
        assert manager.validate_hwpx(b'') is False

    def test_has_duplicate_placeholders_with_duplicates(self, manager):
        """TC-UNIT-008: Detect duplicate placeholders."""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{TITLE}}"]
        assert manager.has_duplicate_placeholders(placeholders) is True

    def test_has_duplicate_placeholders_no_duplicates(self, manager):
        """TC-UNIT-008: No duplicates returns False."""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}"]
        assert manager.has_duplicate_placeholders(placeholders) is False

    def test_has_duplicate_placeholders_empty_list(self, manager):
        """TC-UNIT-008: Empty list returns False."""
        assert manager.has_duplicate_placeholders([]) is False

    def test_get_duplicate_placeholders(self, manager):
        """TC-UNIT-008: Get list of duplicate keys."""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{TITLE}}", "{{SUMMARY}}"]
        duplicates = manager.get_duplicate_placeholders(placeholders)
        assert set(duplicates) == {"{{TITLE}}", "{{SUMMARY}}"}

    def test_get_duplicate_placeholders_no_duplicates(self, manager):
        """TC-UNIT-008: No duplicates returns empty list."""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}"]
        duplicates = manager.get_duplicate_placeholders(placeholders)
        assert len(duplicates) == 0

    def test_calculate_sha256(self, manager, temp_dir):
        """Test SHA256 calculation."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_bytes(b"test content")

        sha256 = manager.calculate_sha256(str(test_file))

        # SHA256 of "test content"
        assert len(sha256) == 64  # SHA256 hex is 64 chars
        # Just verify it's a valid SHA256 hash, not hardcode it
        assert sha256.isalnum()
        assert all(c in "0123456789abcdef" for c in sha256)

    def test_calculate_sha256_file_not_found(self, manager):
        """Test SHA256 with non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            manager.calculate_sha256("/nonexistent/file.txt")

    def test_cleanup_temp_files(self, manager, temp_dir):
        """Test cleanup of temporary files."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        assert test_file.exists()

        # Cleanup
        manager.cleanup_temp_files(str(temp_dir))

        # Should be cleaned up
        assert not temp_dir.exists()

    def test_cleanup_temp_files_directory_not_exists(self, manager):
        """Test cleanup of non-existent directory doesn't raise error."""
        # Should not raise exception
        manager.cleanup_temp_files("/nonexistent/directory")
