"""Claude API 기반 Placeholder 메타정보 생성 테스트.

Unit Spec: 20251112_enhance_placeholder_metadata_with_claude.md

테스트 계획:
- TC-001: Claude API 성공 호출 (메타정보 정확성)
- TC-002: Claude API 실패 (타임아웃) - 폴백 작동
- TC-003: 캐싱된 메타정보 조회 (중복 호출 방지)
- TC-004: Integration - Template 업로드 (1개 Placeholder)
- TC-005: Integration - Template 업로드 (10개 Placeholder)
- TC-006: Integration - 이미 존재하는 Placeholder (캐시 활용)
- TC-007: API - Template 업로드 성공 (API 계약 검증)
- TC-008: API - Claude API 실패 (우아한 실패)
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict

from app.utils.placeholder_metadata_generator import (
    generate_metadata_with_claude,
    batch_generate_metadata,
    clear_cache,
    get_cache_size,
)
from app.utils.meta_info_generator import (
    generate_placeholder_metadata,
)
from app.models.placeholder import PlaceholderMetadata, PlaceholdersMetadataCollection


# ============================================================================
# TC-001: Claude API 성공 호출 (메타정보 정확성)
# ============================================================================


@pytest.mark.asyncio
async def test_tc_001_claude_api_success():
    """Claude API 성공 호출 시 정확한 메타정보 반환 검증.

    Scenario:
        - Claude API 호출 성공
        - 올바른 JSON 응답 파싱
        - 필드 완성도 확인

    Expected:
        - metadata에 필수 필드 모두 포함
        - type, description, examples, required 등 존재
    """
    clear_cache()

    # Mock Claude 응답
    mock_claude_response = json.dumps({
        "type": "section_title",
        "description": "보고서의 명확하고 간결한 제목을 작성하세요.",
        "examples": [
            "2025년 디지털뱅킹 트렌드 분석",
            "모바일 결제 확대에 따른 금융 환경 변화",
            "AI 기술 도입이 금융권에 미치는 영향"
        ],
        "max_length": 200,
        "min_length": 10,
        "required": True
    })

    def mock_chat_completion(*args, **kwargs):
        # (response_text, input_tokens, output_tokens) 튜플 반환
        return (mock_claude_response, 100, 150)

    with patch("app.utils.placeholder_metadata_generator.ClaudeClient") as MockClient:
        mock_client = MagicMock()
        mock_client.chat_completion = mock_chat_completion
        MockClient.return_value = mock_client

        # 테스트 - timeout 파라미터 없음 (무제한 대기)
        metadata = await generate_metadata_with_claude(
            placeholder_key="{{TITLE}}",
            placeholder_name="TITLE",
            template_context="금융 보고서",
            existing_placeholders=["{{TITLE}}", "{{SUMMARY}}"]
        )

        # 검증
        assert metadata is not None
        assert metadata["type"] == "section_title"
        assert metadata["description"] is not None
        assert len(metadata["description"]) > 0
        assert "examples" in metadata
        assert len(metadata["examples"]) > 0
        assert metadata["max_length"] == 200
        assert metadata["min_length"] == 10
        assert metadata["required"] is True

        # 캐시 확인
        assert get_cache_size() == 1


# ============================================================================
# TC-002: Claude API 실패 (타임아웃) - 폴백 작동
# ============================================================================


@pytest.mark.asyncio
async def test_tc_002_claude_api_timeout():
    """Claude API 타임아웃 시 에러 발생 검증 (timeout 파라미터가 설정된 경우).

    Scenario:
        - Claude API 호출 시 timeout 파라미터 설정
        - timeout 초과 시 asyncio.TimeoutError 발생

    Expected:
        - asyncio.TimeoutError 발생 (timeout 파라미터가 1.0초인 경우)
        - timeout=None이면 타임아웃 없이 대기
    """
    clear_cache()

    # Mock: Claude API 타임아웃
    def raise_timeout(*args, **kwargs):
        raise asyncio.TimeoutError("Timeout")

    with patch("app.utils.placeholder_metadata_generator.asyncio.wait_for", side_effect=raise_timeout):
        # 타임아웃이 설정된 경우 에러 발생
        with pytest.raises(asyncio.TimeoutError):
            await generate_metadata_with_claude(
                placeholder_key="{{TITLE}}",
                placeholder_name="TITLE",
                template_context="금융 보고서",
                existing_placeholders=["{{TITLE}}"],
                timeout=1.0  # 매우 짧은 타임아웃 설정
            )


# ============================================================================
# TC-003: 캐싱된 메타정보 조회 (중복 호출 방지)
# ============================================================================


@pytest.mark.asyncio
async def test_tc_003_metadata_caching():
    """Placeholder 메타정보 캐싱 기능 검증.

    Scenario:
        - 첫 번째 호출: Claude API 호출, 캐시에 저장
        - 두 번째 호출: 캐시에서 직접 반환 (API 호출 안 함)

    Expected:
        - 두 번째 호출이 매우 빠름
        - Claude API 호출 횟수: 1회 (캐시 덕분)
    """
    clear_cache()

    mock_claude_response = json.dumps({
        "type": "section_title",
        "description": "보고서 제목",
        "examples": ["예1", "예2"],
        "max_length": 200,
        "min_length": 10,
        "required": True
    })

    call_count = 0

    def mock_chat_completion(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return (mock_claude_response, 100, 150)

    with patch("app.utils.placeholder_metadata_generator.ClaudeClient") as MockClient:
        mock_client = MagicMock()
        mock_client.chat_completion = mock_chat_completion
        MockClient.return_value = mock_client

        # 첫 번째 호출 - timeout 없음 (무제한 대기)
        result1 = await generate_metadata_with_claude(
            placeholder_key="{{TITLE}}",
            placeholder_name="TITLE",
            template_context="금융 보고서",
            existing_placeholders=["{{TITLE}}"]
        )

        # 두 번째 호출 (캐시에서) - timeout 없음
        result2 = await generate_metadata_with_claude(
            placeholder_key="{{TITLE}}",
            placeholder_name="TITLE",
            template_context="금융 보고서",
            existing_placeholders=["{{TITLE}}"]
        )

        # 검증
        assert result1 == result2
        assert call_count == 1  # Claude API는 1회만 호출됨  # Claude API는 1회만 호출됨


# ============================================================================
# 기존 규칙 기반 메타정보 생성 테스트
# ============================================================================


def test_fallback_metadata_generation():
    """기본 규칙으로 메타정보 생성 검증.

    Scenario:
        - Claude API 없이 규칙 기반 메타정보 생성
        - 예약된 Placeholder 타입 분류

    Expected:
        - TITLE → section_title
        - SUMMARY → section_content
        - DATE → meta (선택)
    """
    metadata = generate_placeholder_metadata(
        ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
    )

    assert metadata.total_count == 3
    assert metadata.required_count == 2  # TITLE, SUMMARY
    assert metadata.optional_count == 1  # DATE

    # 각 Placeholder 검증 (순서 유지)
    # 입력 순서: TITLE, SUMMARY, DATE
    title_meta = metadata.placeholders[0]
    assert title_meta.name == "TITLE"
    assert title_meta.type == "section_title"
    assert title_meta.required is True

    date_meta = metadata.placeholders[2]
    assert date_meta.name == "DATE"
    assert date_meta.type == "meta"
    assert date_meta.required is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
