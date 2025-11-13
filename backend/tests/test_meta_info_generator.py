"""Tests for meta_info_generator.py functionality."""

import pytest
from datetime import datetime
from app.utils.meta_info_generator import (
    create_meta_info_from_placeholders,
    _get_display_name,
    _get_description,
    _get_examples
)
from app.models.template import Placeholder


class TestMetaInfoGenerator:
    """Test suite for meta_info_generator module."""

    @pytest.fixture
    def sample_placeholders(self):
        """Create sample placeholder objects for testing."""
        return [
            Placeholder(
                id=1,
                template_id=1,
                placeholder_key="{{TITLE}}",
                created_at=datetime.now()
            ),
            Placeholder(
                id=2,
                template_id=1,
                placeholder_key="{{SUMMARY}}",
                created_at=datetime.now()
            ),
            Placeholder(
                id=3,
                template_id=1,
                placeholder_key="{{BACKGROUND}}",
                created_at=datetime.now()
            ),
            Placeholder(
                id=4,
                template_id=1,
                placeholder_key="{{CONCLUSION}}",
                created_at=datetime.now()
            ),
            Placeholder(
                id=5,
                template_id=1,
                placeholder_key="{{DATE}}",
                created_at=datetime.now()
            ),
        ]

    @pytest.fixture
    def mixed_placeholders(self):
        """Create placeholders with both known and unknown keywords."""
        return [
            Placeholder(
                id=1,
                template_id=1,
                placeholder_key="{{TITLE}}",
                created_at=datetime.now()
            ),
            Placeholder(
                id=2,
                template_id=1,
                placeholder_key="{{RISK_ANALYSIS}}",
                created_at=datetime.now()
            ),
            Placeholder(
                id=3,
                template_id=1,
                placeholder_key="{{DATE_CREATED}}",
                created_at=datetime.now()
            ),
            Placeholder(
                id=4,
                template_id=1,
                placeholder_key="{{CUSTOM_FIELD}}",
                created_at=datetime.now()
            ),
        ]

    # === Test create_meta_info_from_placeholders ===

    def test_create_meta_info_all_known_keywords(self, sample_placeholders):
        """TC-Unit-001: Generate meta-info for all known keywords."""
        result = create_meta_info_from_placeholders(sample_placeholders)

        # Check total count
        assert len(result) == 5

        # Check TITLE (section_title)
        title_item = result[0]
        assert title_item["key"] == "{{TITLE}}"
        assert title_item["type"] == "section_title"
        assert title_item["display_name"] == "보고서 제목"
        assert title_item["required"] is True
        assert isinstance(title_item["examples"], list)
        assert len(title_item["examples"]) > 0

        # Check SUMMARY (section_content)
        summary_item = result[1]
        assert summary_item["key"] == "{{SUMMARY}}"
        assert summary_item["type"] == "section_content"
        assert summary_item["display_name"] == "요약"
        assert summary_item["required"] is True

        # Check BACKGROUND (section_content)
        bg_item = result[2]
        assert bg_item["key"] == "{{BACKGROUND}}"
        assert bg_item["type"] == "section_content"
        assert bg_item["display_name"] == "배경"
        assert bg_item["required"] is True

        # Check CONCLUSION (section_content)
        conc_item = result[3]
        assert conc_item["key"] == "{{CONCLUSION}}"
        assert conc_item["type"] == "section_content"
        assert conc_item["display_name"] == "결론"
        assert conc_item["required"] is True

        # Check DATE (metadata)
        date_item = result[4]
        assert date_item["key"] == "{{DATE}}"
        assert date_item["type"] == "metadata"
        assert date_item["display_name"] == "작성 날짜"
        assert date_item["required"] is False  # metadata는 선택

    def test_create_meta_info_mixed_keywords(self, mixed_placeholders):
        """TC-Unit-002: Generate meta-info for mixed known/unknown keywords."""
        result = create_meta_info_from_placeholders(mixed_placeholders)

        assert len(result) == 4

        # TITLE (known)
        title_item = result[0]
        assert title_item["key"] == "{{TITLE}}"
        assert title_item["type"] == "section_title"
        assert title_item["display_name"] == "보고서 제목"

        # RISK_ANALYSIS (unknown, but contains RISK - not in keywords, so default)
        risk_item = result[1]
        assert risk_item["key"] == "{{RISK_ANALYSIS}}"
        assert risk_item["type"] == "section_content"  # default fallback
        assert "RISK_ANALYSIS" in risk_item["display_name"]

        # DATE_CREATED (contains DATE keyword, so should be metadata)
        date_item = result[2]
        assert date_item["key"] == "{{DATE_CREATED}}"
        assert date_item["type"] == "metadata"  # DATE keyword match
        assert date_item["required"] is False

        # CUSTOM_FIELD (completely unknown)
        custom_item = result[3]
        assert custom_item["key"] == "{{CUSTOM_FIELD}}"
        assert custom_item["type"] == "section_content"  # default fallback
        assert "CUSTOM_FIELD" in custom_item["display_name"]

    def test_create_meta_info_empty_list(self):
        """TC-Unit-003: Handle empty placeholder list."""
        result = create_meta_info_from_placeholders([])
        assert result == []

    def test_meta_info_required_fields(self, sample_placeholders):
        """TC-Unit-004: Verify all meta-info items have required fields."""
        result = create_meta_info_from_placeholders(sample_placeholders)

        required_fields = ["key", "type", "display_name", "description", "examples", "required", "order_hint"]

        for item in result:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
                assert item[field] is not None, f"Field {field} is None"

    # === Test _get_display_name ===

    def test_display_name_known_keywords(self):
        """TC-Unit-005: Generate Korean display names for known keywords."""
        assert _get_display_name("TITLE", "section_title") == "보고서 제목"
        assert _get_display_name("SUMMARY", "section_content") == "요약"
        assert _get_display_name("BACKGROUND", "section_content") == "배경"
        assert _get_display_name("CONCLUSION", "section_content") == "결론"
        assert _get_display_name("DATE", "metadata") == "작성 날짜"
        assert _get_display_name("MAIN_CONTENT", "section_content") == "주요 내용"
        assert _get_display_name("RISK", "section_content") == "위험 요소"

    def test_display_name_unknown_keywords(self):
        """TC-Unit-006: Generate fallback display names for unknown keywords."""
        result = _get_display_name("UNKNOWN_KEY", "section_content")
        assert result == "UNKNOWN_KEY 섹션"  # fallback pattern

        result = _get_display_name("RISK_ANALYSIS", "section_content")
        assert result == "RISK_ANALYSIS 섹션"  # fallback pattern

    # === Test _get_description ===

    def test_description_known_keywords(self):
        """TC-Unit-007: Generate descriptions for known keywords."""
        desc = _get_description("TITLE", {"type": "section_title", "section": "제목"})
        assert len(desc) > 0
        assert "제목" in desc
        assert "간결" in desc or "명확" in desc or "주제" in desc

        desc = _get_description("DATE", {"type": "metadata", "section": "날짜"})
        assert len(desc) > 0
        assert "날짜" in desc or "date" in desc.lower()

    def test_description_unknown_keywords(self):
        """TC-Unit-008: Generate descriptions with warnings for unknown keywords."""
        desc = _get_description("UNKNOWN_KEY", {"type": "section_content", "section": "내용"})
        assert "UNKNOWN_KEY" in desc
        assert "모호" in desc  # Should mention ambiguity warning

    # === Test _get_examples ===

    def test_examples_known_keywords(self):
        """TC-Unit-009: Generate examples for known keywords."""
        examples = _get_examples("TITLE", {})
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all(isinstance(ex, str) for ex in examples)

        examples = _get_examples("SUMMARY", {})
        assert isinstance(examples, list)
        assert len(examples) > 0

        examples = _get_examples("DATE", {})
        assert isinstance(examples, list)
        assert len(examples) > 0

    def test_examples_unknown_keywords(self):
        """TC-Unit-010: Generate fallback examples for unknown keywords."""
        examples = _get_examples("UNKNOWN_KEY", {})
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert "UNKNOWN_KEY" in examples[0]

    # === Test order_hint ===

    def test_order_hint_values(self, sample_placeholders):
        """TC-Unit-011: Verify order_hint values for different types."""
        result = create_meta_info_from_placeholders(sample_placeholders)

        # Find items by type and check order_hint
        for item in result:
            if item["type"] == "section_title":
                assert item["order_hint"] == 1
            elif item["type"] == "section_content":
                assert item["order_hint"] == 2
            elif item["type"] == "metadata":
                assert item["order_hint"] == 0

    # === Integration Test ===

    def test_integration_realistic_template(self, mixed_placeholders):
        """TC-Unit-012: Integration test with realistic template placeholders."""
        result = create_meta_info_from_placeholders(mixed_placeholders)

        # Verify structure matches expectations for a realistic template
        assert len(result) == 4
        assert all("key" in item and item["key"].startswith("{{") for item in result)
        assert all(item["type"] in ["section_title", "section_content", "metadata"] for item in result)

        # Verify total character count of descriptions is reasonable
        total_desc_chars = sum(len(item["description"]) for item in result)
        assert total_desc_chars > 0
        assert total_desc_chars < 10000  # Descriptions shouldn't be too long

        # Verify examples are provided for all items
        assert all(len(item["examples"]) > 0 for item in result)


class TestMetaInfoHelperFunctions:
    """Test individual helper functions in isolation."""

    def test_display_name_type_parameter_ignored(self):
        """Display name should be consistent regardless of type parameter."""
        result1 = _get_display_name("TITLE", "section_title")
        result2 = _get_display_name("TITLE", "section_content")
        assert result1 == result2 == "보고서 제목"

    def test_examples_return_list_always(self):
        """Examples should always return a list."""
        result1 = _get_examples("TITLE", {})
        result2 = _get_examples("UNKNOWN", {})
        assert isinstance(result1, list)
        assert isinstance(result2, list)
        assert len(result1) > 0
        assert len(result2) > 0

    def test_description_contains_keyword_name(self):
        """Descriptions for unknown keywords should mention the keyword."""
        desc = _get_description("MY_CUSTOM_FIELD", {"type": "section_content", "section": "내용"})
        assert "MY_CUSTOM_FIELD" in desc or "custom" in desc.lower() or "모호" in desc


class TestClaudeMetadataGeneration:
    """Test suite for Claude API-based metadata generation."""

    @pytest.mark.asyncio
    async def test_generate_placeholder_metadata_with_claude_success(self):
        """TC-001: Claude API 성공 호출 - 메타정보 정확성 검증."""
        from app.utils.meta_info_generator import generate_placeholder_metadata_with_claude
        from unittest.mock import AsyncMock, patch

        # Mock Claude API 응답
        mock_claude_response = {
            "{{TITLE}}": {
                "type": "section_title",
                "description": "보고서의 명확하고 간결한 제목",
                "examples": ["제목1", "제목2"],
                "max_length": 200,
                "min_length": 10,
                "required": True
            }
        }

        with patch('app.utils.placeholder_metadata_generator.batch_generate_metadata', new_callable=AsyncMock) as mock_batch:
            mock_batch.return_value = mock_claude_response

            result = await generate_placeholder_metadata_with_claude(
                raw_placeholders=["{{TITLE}}"],
                template_context="금융 보고서",
                enable_fallback=True
            )

            assert result is not None
            assert result.total_count == 1
            assert result.required_count == 1
            assert len(result.placeholders) == 1
            assert result.placeholders[0].name == "TITLE"
            assert result.placeholders[0].type == "section_title"

    @pytest.mark.asyncio
    async def test_generate_placeholder_metadata_fallback_on_error(self):
        """TC-002: Claude API 실패 - 폴백 작동 검증."""
        from app.utils.meta_info_generator import generate_placeholder_metadata_with_claude
        from unittest.mock import AsyncMock, patch

        with patch('app.utils.placeholder_metadata_generator.batch_generate_metadata', new_callable=AsyncMock) as mock_batch:
            mock_batch.side_effect = Exception("Claude API timeout")

            result = await generate_placeholder_metadata_with_claude(
                raw_placeholders=["{{TITLE}}", "{{SUMMARY}}"],
                template_context="금융 보고서",
                enable_fallback=True
            )

            # 폴백으로 기본 규칙 적용되어야 함
            assert result is not None
            assert result.total_count == 2
            assert len(result.placeholders) == 2
            # 기본 규칙에 따라 TITLE은 section_title
            assert result.placeholders[0].type == "section_title"

    @pytest.mark.asyncio
    async def test_generate_placeholder_metadata_duplicate_detection(self):
        """테스트: 중복 Placeholder 감지."""
        from app.utils.meta_info_generator import generate_placeholder_metadata_with_claude

        with pytest.raises(ValueError, match="중복된 Placeholder"):
            await generate_placeholder_metadata_with_claude(
                raw_placeholders=["{{TITLE}}", "{{TITLE}}"],
                template_context="금융 보고서"
            )

    @pytest.mark.asyncio
    async def test_generate_placeholder_metadata_mixed_results(self):
        """테스트: Claude 성공 + 실패 혼합 결과."""
        from app.utils.meta_info_generator import generate_placeholder_metadata_with_claude
        from unittest.mock import AsyncMock, patch

        # Claude API가 TITLE은 반환하고 CUSTOM은 None 반환
        mock_claude_response = {
            "{{TITLE}}": {
                "type": "section_title",
                "description": "보고서 제목",
                "examples": ["제목1"],
                "max_length": 200,
                "required": True
            },
            "{{CUSTOM_FIELD}}": None  # 실패
        }

        with patch('app.utils.placeholder_metadata_generator.batch_generate_metadata', new_callable=AsyncMock) as mock_batch:
            mock_batch.return_value = mock_claude_response

            result = await generate_placeholder_metadata_with_claude(
                raw_placeholders=["{{TITLE}}", "{{CUSTOM_FIELD}}"],
                template_context="금융 보고서",
                enable_fallback=True
            )

            assert result.total_count == 2
            # TITLE은 Claude 응답 사용
            assert result.placeholders[0].type == "section_title"
            # CUSTOM_FIELD는 기본 규칙 사용
            assert result.placeholders[1].type == "section_content"

    @pytest.mark.asyncio
    async def test_generate_placeholder_metadata_large_batch(self):
        """테스트: 대량 Placeholder 처리 (10개)."""
        from app.utils.meta_info_generator import generate_placeholder_metadata_with_claude
        from unittest.mock import AsyncMock, patch

        # Valid placeholder names with letters only (regex: ^\{\{[A-Z_]+\}\}$)
        placeholder_names = ["SECTION_A", "SECTION_B", "SECTION_C", "CONTENT_A", "CONTENT_B",
                           "INTRO", "MAIN", "CONCLUSION", "APPENDIX", "REFERENCE"]
        placeholders = [f"{{{{{name}}}}}" for name in placeholder_names]
        mock_response = {ph: {
            "type": "section_content",
            "description": f"Placeholder {i}",
            "examples": [f"예시{i}"],
            "required": True
        } for i, ph in enumerate(placeholders)}

        with patch('app.utils.placeholder_metadata_generator.batch_generate_metadata', new_callable=AsyncMock) as mock_batch:
            mock_batch.return_value = mock_response

            result = await generate_placeholder_metadata_with_claude(
                raw_placeholders=placeholders,
                template_context="복합 문서",
                enable_fallback=True
            )

            assert result.total_count == 10
            assert len(result.placeholders) == 10

    def test_generate_placeholder_metadata_fallback_disabled(self):
        """테스트: 폴백 비활성화 시 에러 발생."""
        from app.utils.meta_info_generator import generate_placeholder_metadata_with_claude
        from unittest.mock import AsyncMock, patch
        import asyncio

        async def run_test():
            with patch('app.utils.placeholder_metadata_generator.batch_generate_metadata', new_callable=AsyncMock) as mock_batch:
                mock_batch.side_effect = Exception("Claude API error")

                with pytest.raises(Exception):
                    await generate_placeholder_metadata_with_claude(
                        raw_placeholders=["{{TITLE}}"],
                        template_context="금융 보고서",
                        enable_fallback=False  # 폴백 비활성화
                    )

        asyncio.run(run_test())
