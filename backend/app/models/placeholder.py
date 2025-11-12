"""Placeholder 메타정보 모델 정의.

Placeholder의 구조화된 메타정보를 정의하는 Pydantic 모델들입니다.
각 Placeholder의 타입, 필수 여부, 길이 제한 등을 관리합니다.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class PlaceholderMetadata(BaseModel):
    """개별 Placeholder의 메타정보.

    Template 업로드 시 HWPX에서 추출된 각 Placeholder의 상세 정보를 저장합니다.
    이 정보는 System Prompt 생성 시 활용되며, 사용자에게 제시됩니다.
    """

    # 필수 필드
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Placeholder 이름 (예: TITLE, SUMMARY)"
    )
    placeholder_key: str = Field(
        ...,
        pattern=r"^\{\{[A-Z_]+\}\}$",
        description="Placeholder 키 (예: {{TITLE}})"
    )
    type: str = Field(
        ...,
        description="Placeholder 타입 (section_title, section_content, field, table, meta)"
    )
    required: bool = Field(
        default=True,
        description="필수 여부"
    )
    position: int = Field(
        default=0,
        ge=0,
        description="순서 위치"
    )

    # 선택 필드
    max_length: Optional[int] = Field(
        default=None,
        ge=1,
        description="최대 문자 길이"
    )
    min_length: Optional[int] = Field(
        default=None,
        ge=0,
        description="최소 문자 길이"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Placeholder 설명"
    )
    example: Optional[str] = Field(
        default=None,
        description="예시 값"
    )
    allowed_values: Optional[List[str]] = Field(
        default=None,
        description="허용된 값 목록 (enum)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "TITLE",
                "placeholder_key": "{{TITLE}}",
                "type": "section_title",
                "required": True,
                "position": 0,
                "max_length": 200,
                "description": "보고서 제목"
            }
        }


class PlaceholdersMetadataCollection(BaseModel):
    """Template의 모든 Placeholder 메타정보.

    하나의 Template에 포함된 모든 Placeholder의 메타정보를 집계합니다.
    이 JSON 구조는 Placeholders 테이블의 metadata 컬럼에 저장됩니다.
    """

    placeholders: List[PlaceholderMetadata] = Field(
        ...,
        description="Placeholder 메타정보 리스트"
    )
    total_count: int = Field(
        ...,
        ge=0,
        description="전체 Placeholder 개수"
    )
    required_count: int = Field(
        ...,
        ge=0,
        description="필수 Placeholder 개수"
    )
    optional_count: int = Field(
        ...,
        ge=0,
        description="선택 Placeholder 개수"
    )

    def to_json(self) -> str:
        """JSON 문자열로 직렬화.

        Returns:
            JSON 문자열 형태의 메타정보

        Examples:
            >>> collection = PlaceholdersMetadataCollection(
            ...     placeholders=[...],
            ...     total_count=3,
            ...     required_count=2,
            ...     optional_count=1
            ... )
            >>> json_str = collection.to_json()
        """
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "PlaceholdersMetadataCollection":
        """JSON 문자열에서 복원.

        Args:
            json_str: JSON 문자열

        Returns:
            PlaceholdersMetadataCollection 객체

        Raises:
            ValueError: JSON 파싱 실패

        Examples:
            >>> json_str = '{"placeholders": [...], "total_count": 3, ...}'
            >>> collection = PlaceholdersMetadataCollection.from_json(json_str)
        """
        return cls.model_validate_json(json_str)
