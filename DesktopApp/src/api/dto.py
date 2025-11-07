"""API 응답 데이터를 위한 DTO 정의."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class TopicDTO:
    """주제 목록/조회 응답의 단일 Topic 항목."""

    id: int
    input_prompt: str
    generated_title: Optional[str]
    language: str
    status: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class TopicsPage:
    """Topic 목록 API의 페이지 응답."""

    topics: List[TopicDTO]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class ArtifactDTO:
    """Artifact 목록 응답의 단일 항목."""

    id: int
    topic_id: int
    message_id: int
    kind: str
    locale: str
    version: int
    filename: str
    file_path: str
    file_size: int
    created_at: str


@dataclass(frozen=True)
class ArtifactListDTO:
    """Artifact 목록 API 응답."""

    artifacts: List[ArtifactDTO]
    total: int
    topic_id: int


@dataclass(frozen=True)
class ArtifactContentDTO:
    """Artifact 콘텐츠 조회 응답."""

    artifact_id: int
    filename: str
    content: str
    kind: str

