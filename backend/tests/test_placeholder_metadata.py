"""Unit tests for Placeholder metadata structuring.

Tests for:
- PlaceholderMetadata and PlaceholdersMetadataCollection models
- generate_placeholder_metadata() function
- Validation and duplicate detection
"""

import pytest
from app.models.placeholder import PlaceholderMetadata, PlaceholdersMetadataCollection
from app.utils.meta_info_generator import generate_placeholder_metadata


class TestPlaceholderMetadataModel:
    """Test PlaceholderMetadata Pydantic model."""

    def test_placeholder_metadata_creation(self):
        """TC-UNIT-001: PlaceholderMetadata 모델 생성 성공."""
        metadata = PlaceholderMetadata(
            name="TITLE",
            placeholder_key="{{TITLE}}",
            type="section_title",
            required=True,
            position=0,
            max_length=200,
            description="보고서 제목",
            example="2025년 금융 시장 분석"
        )

        assert metadata.name == "TITLE"
        assert metadata.placeholder_key == "{{TITLE}}"
        assert metadata.type == "section_title"
        assert metadata.required is True
        assert metadata.position == 0
        assert metadata.max_length == 200
        assert metadata.description == "보고서 제목"
        assert metadata.example == "2025년 금융 시장 분석"

    def test_placeholder_metadata_with_optional_fields(self):
        """Optional 필드가 None일 수 있음."""
        metadata = PlaceholderMetadata(
            name="TITLE",
            placeholder_key="{{TITLE}}",
            type="section_title",
            required=True,
            position=0
        )

        assert metadata.max_length is None
        assert metadata.min_length is None
        assert metadata.description is None
        assert metadata.example is None
        assert metadata.allowed_values is None

    def test_placeholder_metadata_with_constraints(self):
        """필드 제약 조건 검증."""
        # name은 1-50 문자
        with pytest.raises(Exception):
            PlaceholderMetadata(
                name="",  # Empty string, min_length=1
                placeholder_key="{{TEST}}",
                type="section_content",
                required=True
            )

        # placeholder_key는 {{NAME}} 형식
        with pytest.raises(Exception):
            PlaceholderMetadata(
                name="TEST",
                placeholder_key="INVALID",  # Not {{...}} format
                type="section_content",
                required=True
            )

    def test_placeholder_metadata_json_serialization(self):
        """JSON 직렬화."""
        metadata = PlaceholderMetadata(
            name="TITLE",
            placeholder_key="{{TITLE}}",
            type="section_title",
            required=True,
            position=0,
            max_length=200,
            description="보고서 제목"
        )

        json_data = metadata.model_dump()
        assert json_data["name"] == "TITLE"
        assert json_data["placeholder_key"] == "{{TITLE}}"
        assert json_data["type"] == "section_title"
        assert json_data["required"] is True


class TestPlaceholdersMetadataCollection:
    """Test PlaceholdersMetadataCollection model."""

    def test_metadata_collection_creation(self):
        """TC-UNIT-002: PlaceholdersMetadataCollection 생성."""
        metadata_list = [
            PlaceholderMetadata(
                name="TITLE",
                placeholder_key="{{TITLE}}",
                type="section_title",
                required=True,
                position=0
            ),
            PlaceholderMetadata(
                name="SUMMARY",
                placeholder_key="{{SUMMARY}}",
                type="section_content",
                required=True,
                position=1
            ),
            PlaceholderMetadata(
                name="DATE",
                placeholder_key="{{DATE}}",
                type="meta",
                required=False,
                position=2
            )
        ]

        collection = PlaceholdersMetadataCollection(
            placeholders=metadata_list,
            total_count=3,
            required_count=2,
            optional_count=1
        )

        assert collection.total_count == 3
        assert collection.required_count == 2
        assert collection.optional_count == 1
        assert len(collection.placeholders) == 3

    def test_metadata_collection_to_json(self):
        """JSON 문자열로 직렬화."""
        collection = PlaceholdersMetadataCollection(
            placeholders=[
                PlaceholderMetadata(
                    name="TITLE",
                    placeholder_key="{{TITLE}}",
                    type="section_title",
                    required=True,
                    position=0
                )
            ],
            total_count=1,
            required_count=1,
            optional_count=0
        )

        json_str = collection.to_json()
        assert isinstance(json_str, str)
        assert "TITLE" in json_str
        assert "section_title" in json_str

    def test_metadata_collection_from_json(self):
        """JSON 문자열에서 복원."""
        collection = PlaceholdersMetadataCollection(
            placeholders=[
                PlaceholderMetadata(
                    name="TITLE",
                    placeholder_key="{{TITLE}}",
                    type="section_title",
                    required=True,
                    position=0,
                    max_length=200,
                    description="보고서 제목"
                )
            ],
            total_count=1,
            required_count=1,
            optional_count=0
        )

        json_str = collection.to_json()
        restored = PlaceholdersMetadataCollection.from_json(json_str)

        assert restored.total_count == 1
        assert restored.required_count == 1
        assert restored.optional_count == 0
        assert len(restored.placeholders) == 1
        assert restored.placeholders[0].name == "TITLE"


class TestGeneratePlaceholderMetadata:
    """Test generate_placeholder_metadata() function."""

    def test_generate_metadata_basic(self):
        """TC-UNIT-003: 기본 메타정보 생성."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        assert isinstance(result, PlaceholdersMetadataCollection)
        assert result.total_count == 3
        assert result.required_count == 2  # TITLE, SUMMARY
        assert result.optional_count == 1  # DATE

    def test_generate_metadata_types(self):
        """각 Placeholder의 타입이 정확함."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        assert result.placeholders[0].type == "section_title"
        assert result.placeholders[1].type == "section_content"
        assert result.placeholders[2].type == "meta"

    def test_generate_metadata_required_fields(self):
        """필수 여부 검증."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        assert result.placeholders[0].required is True  # TITLE
        assert result.placeholders[1].required is True  # SUMMARY
        assert result.placeholders[2].required is False  # DATE (meta)

    def test_generate_metadata_with_position(self):
        """순서 정보 검증."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}", "{{DATE}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        for i, metadata in enumerate(result.placeholders):
            assert metadata.position == i

    def test_generate_metadata_with_length_constraints(self):
        """길이 제약 조건."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        # TITLE: section_title -> max_length=200
        assert result.placeholders[0].max_length == 200
        # SUMMARY: section_content -> min_length=100, max_length=10000
        assert result.placeholders[1].min_length == 100
        assert result.placeholders[1].max_length == 10000
        # DATE: meta -> max_length=100
        assert result.placeholders[2].max_length == 100

    def test_generate_metadata_duplicate_detection(self):
        """TC-UNIT-004: 중복 Placeholder 감지."""
        raw_placeholders = ["{{TITLE}}", "{{TITLE}}", "{{SUMMARY}}"]

        with pytest.raises(ValueError, match="중복된 Placeholder"):
            generate_placeholder_metadata(raw_placeholders)

    def test_generate_metadata_with_custom_placeholder(self):
        """커스텀 Placeholder (기본값 사용)."""
        raw_placeholders = ["{{CUSTOM_FIELD}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        assert result.total_count == 1
        assert result.required_count == 1  # Custom is required by default
        # Custom type defaults to "section_content"
        assert result.placeholders[0].type == "section_content"

    def test_generate_metadata_empty_list(self):
        """빈 Placeholder 목록."""
        raw_placeholders: list = []
        result = generate_placeholder_metadata(raw_placeholders)

        assert result.total_count == 0
        assert result.required_count == 0
        assert result.optional_count == 0
        assert len(result.placeholders) == 0

    def test_generate_metadata_all_standard_types(self):
        """모든 표준 Placeholder 타입."""
        raw_placeholders = [
            "{{TITLE}}",
            "{{SUMMARY}}",
            "{{BACKGROUND}}",
            "{{MAIN_CONTENT}}",
            "{{CONCLUSION}}",
            "{{DATE}}"
        ]
        result = generate_placeholder_metadata(raw_placeholders)

        assert result.total_count == 6
        assert result.required_count == 5  # All except DATE
        assert result.optional_count == 1  # DATE

        # Type mappings
        assert result.placeholders[0].type == "section_title"  # TITLE
        assert result.placeholders[1].type == "section_content"  # SUMMARY
        assert result.placeholders[2].type == "section_content"  # BACKGROUND
        assert result.placeholders[3].type == "section_content"  # MAIN_CONTENT
        assert result.placeholders[4].type == "section_content"  # CONCLUSION
        assert result.placeholders[5].type == "meta"  # DATE

    def test_generate_metadata_description_and_example(self):
        """설명과 예시 정보."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        # All should have description
        assert all(m.description for m in result.placeholders)

        # All should have example
        assert all(m.example for m in result.placeholders)

        # TITLE should have specific description
        assert "제목" in result.placeholders[0].description
        assert "간결한" in result.placeholders[0].description

    def test_generate_metadata_json_serialization(self):
        """생성된 메타정보를 JSON으로 직렬화."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}"]
        result = generate_placeholder_metadata(raw_placeholders)

        json_str = result.to_json()
        restored = PlaceholdersMetadataCollection.from_json(json_str)

        assert restored.total_count == result.total_count
        assert restored.required_count == result.required_count
        assert len(restored.placeholders) == len(result.placeholders)


class TestPlaceholderMetadataIntegration:
    """Integration tests for placeholder metadata."""

    def test_metadata_generation_and_serialization_cycle(self):
        """TC-INTG-005: 생성 -> 직렬화 -> 복원 사이클."""
        raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}", "{{DATE}}"]

        # Generate
        collection = generate_placeholder_metadata(raw_placeholders)

        # Serialize to JSON
        json_str = collection.to_json()

        # Deserialize
        restored = PlaceholdersMetadataCollection.from_json(json_str)

        # Verify
        assert restored.total_count == collection.total_count
        assert restored.required_count == collection.required_count
        assert restored.optional_count == collection.optional_count
        assert len(restored.placeholders) == len(collection.placeholders)

        for original, restored_meta in zip(collection.placeholders, restored.placeholders):
            assert original.name == restored_meta.name
            assert original.placeholder_key == restored_meta.placeholder_key
            assert original.type == restored_meta.type
            assert original.required == restored_meta.required

    def test_metadata_with_mixed_standard_and_custom(self):
        """표준과 커스텀 Placeholder 혼합."""
        raw_placeholders = [
            "{{TITLE}}",
            "{{CUSTOM_FIELD}}",
            "{{SUMMARY}}",
            "{{DATE}}"
        ]
        result = generate_placeholder_metadata(raw_placeholders)

        assert result.total_count == 4
        # TITLE, CUSTOM_FIELD, SUMMARY required; DATE optional
        assert result.required_count == 3
        assert result.optional_count == 1

        # Check types
        assert result.placeholders[0].type == "section_title"  # TITLE
        assert result.placeholders[1].type == "section_content"  # CUSTOM defaults to section_content
        assert result.placeholders[2].type == "section_content"  # SUMMARY
        assert result.placeholders[3].type == "meta"  # DATE
