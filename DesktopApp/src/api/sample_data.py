"""로컬 데모 실행을 위한 샘플 API 응답 데이터."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from DesktopApp.src.api.dto import ArtifactDTO, ArtifactListDTO, TopicDTO, TopicsPage


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


_BASE_TIME = datetime(2025, 1, 15, 9, 30, 0)

_SAMPLE_TOPICS: List[TopicDTO] = [
    TopicDTO(
        id=101,
        input_prompt="2024년 4분기 AI 사업부 실적 분석과 2025년 전략 제안",
        generated_title="AI 사업부 4Q 실적 리뷰 및 2025 로드맵 제안",
        language="ko",
        status="active",
        created_at=_iso(_BASE_TIME),
        updated_at=_iso(_BASE_TIME + timedelta(minutes=15)),
    ),
    TopicDTO(
        id=102,
        input_prompt="국내 교육기관 대상 HWPX 전환 프로젝트 사례 조사",
        generated_title="교육기관 HWPX 전환 사례 리서치",
        language="ko",
        status="active",
        created_at=_iso(_BASE_TIME - timedelta(hours=5)),
        updated_at=_iso(_BASE_TIME - timedelta(hours=4, minutes=20)),
    ),
    TopicDTO(
        id=103,
        input_prompt="해외 공공기관 문서 규격 비교 및 pyhwpx 확장 아이디어",
        generated_title="해외 공공기관 문서 규격 비교 보고서",
        language="ko",
        status="active",
        created_at=_iso(_BASE_TIME - timedelta(days=1, hours=2)),
        updated_at=_iso(_BASE_TIME - timedelta(days=1, hours=1, minutes=10)),
    ),
]

_SAMPLE_ARTIFACTS: Dict[int, List[ArtifactDTO]] = {
    101: [
        ArtifactDTO(
            id=2101,
            topic_id=101,
            message_id=3101,
            kind="md",
            locale="ko",
            version=1,
            filename="ai-division-q4-summary.md",
            file_path="storage/topics/101/artifacts/ai-division-q4-summary.md",
            file_size=42_560,
            created_at=_iso(_BASE_TIME + timedelta(minutes=12)),
        ),
        ArtifactDTO(
            id=2102,
            topic_id=101,
            message_id=3102,
            kind="md",
            locale="ko",
            version=2,
            filename="ai-division-2025-plan.md",
            file_path="storage/topics/101/artifacts/ai-division-2025-plan.md",
            file_size=51_200,
            created_at=_iso(_BASE_TIME + timedelta(minutes=25)),
        ),
    ],
    102: [
        ArtifactDTO(
            id=2201,
            topic_id=102,
            message_id=3201,
            kind="md",
            locale="ko",
            version=1,
            filename="education-institute-case-study.md",
            file_path="storage/topics/102/artifacts/education-institute-case-study.md",
            file_size=36_864,
            created_at=_iso(_BASE_TIME - timedelta(hours=4, minutes=5)),
        ),
        ArtifactDTO(
            id=2202,
            topic_id=102,
            message_id=3202,
            kind="md",
            locale="ko",
            version=1,
            filename="education-institute-kpi-dashboard.md",
            file_path="storage/topics/102/artifacts/education-institute-kpi-dashboard.md",
            file_size=28_672,
            created_at=_iso(_BASE_TIME - timedelta(hours=3, minutes=45)),
        ),
    ],
    103: [
        ArtifactDTO(
            id=2301,
            topic_id=103,
            message_id=3301,
            kind="md",
            locale="ko",
            version=1,
            filename="global-public-sector-standards.md",
            file_path="storage/topics/103/artifacts/global-public-sector-standards.md",
            file_size=47_104,
            created_at=_iso(_BASE_TIME - timedelta(days=1, hours=1, minutes=40)),
        ),
        ArtifactDTO(
            id=2302,
            topic_id=103,
            message_id=3302,
            kind="md",
            locale="en",
            version=1,
            filename="global-public-sector-appendix.md",
            file_path="storage/topics/103/artifacts/global-public-sector-appendix.md",
            file_size=32_768,
            created_at=_iso(_BASE_TIME - timedelta(days=1, hours=1, minutes=5)),
        ),
    ],
}


def sample_topics_page() -> TopicsPage:
    """Topic 목록에 사용할 샘플 페이지 응답."""
    topics = list(_SAMPLE_TOPICS)
    return TopicsPage(topics=topics, total=len(topics), page=1, page_size=max(20, len(topics)))


def sample_artifacts(topic_id: int) -> ArtifactListDTO:
    """특정 Topic에 대한 샘플 Artifact 목록."""
    artifacts = list(_SAMPLE_ARTIFACTS.get(topic_id, []))
    return ArtifactListDTO(artifacts=artifacts, total=len(artifacts), topic_id=topic_id)
