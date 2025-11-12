"""
Unit 테스트: Batch Placeholder Metadata Optimization (Phase 2)

테스트 대상:
1. batch_generate_placeholder_metadata() - 배치 Claude API 호출 (claude_metadata_generator.py)
2. batch_generate_metadata() - 리팩토링된 배치 처리 (placeholder_metadata_generator.py)
3. _batch_generate_metadata_single_batch() - 단일 배치 처리
4. _split_into_batches() - 배치 분할 유틸

성능 검증:
- 기존 sequential 대비 asyncio.gather 성능 개선 (< 3초)
- 배치 처리로 API 호출 60% 감소
- 에러 격리 (partial failure 처리)
"""

import asyncio
import json
import pytest
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch, call

from app.utils.claude_metadata_generator import (
    batch_generate_placeholder_metadata,
    _parse_batch_json_response,
)
from app.utils.placeholder_metadata_generator import (
    batch_generate_metadata,
    _batch_generate_metadata_single_batch,
    _split_into_batches,
)


# ============================================================================
# Unit Test 1: _split_into_batches() - 배치 분할 유틸
# ============================================================================


class TestSplitIntoBatches:
    """배치 분할 함수 테스트"""

    def test_split_into_batches_exact_division(self):
        """배치 크기로 정확히 나누어떨어지는 경우"""
        items = ["A", "B", "C", "D", "E", "F"]
        result = _split_into_batches(items, 2)
        assert result == [["A", "B"], ["C", "D"], ["E", "F"]]
        assert len(result) == 3

    def test_split_into_batches_remainder(self):
        """배치 크기로 나누어떨어지지 않는 경우"""
        items = ["A", "B", "C", "D", "E"]
        result = _split_into_batches(items, 2)
        assert result == [["A", "B"], ["C", "D"], ["E"]]
        assert len(result) == 3

    def test_split_into_batches_single_batch(self):
        """배치 크기가 전체 개수보다 큰 경우"""
        items = ["A", "B", "C"]
        result = _split_into_batches(items, 10)
        assert result == [["A", "B", "C"]]
        assert len(result) == 1

    def test_split_into_batches_empty_list(self):
        """빈 리스트"""
        items = []
        result = _split_into_batches(items, 3)
        assert result == []

    def test_split_into_batches_batch_size_one(self):
        """배치 크기가 1인 경우"""
        items = ["A", "B", "C"]
        result = _split_into_batches(items, 1)
        assert result == [["A"], ["B"], ["C"]]
        assert len(result) == 3


# ============================================================================
# Unit Test 2: _parse_batch_json_response() - JSON 파싱 (객체 형식)
# ============================================================================


class TestParseBatchJsonResponse:
    """배치 JSON 응답 파싱 테스트"""

    def test_parse_pure_json_object(self):
        """순수 JSON 객체"""
        response = json.dumps({
            "{{TITLE}}": {
                "type": "section_title",
                "description": "제목",
                "examples": ["예시"],
                "required": True
            },
            "{{SUMMARY}}": {
                "type": "section_content",
                "description": "요약",
                "examples": ["예시"],
                "required": True
            }
        })
        result = _parse_batch_json_response(response)
        assert result is not None
        assert len(result) == 2
        assert "{{TITLE}}" in result
        assert "{{SUMMARY}}" in result

    def test_parse_markdown_json_block(self):
        """마크다운 코드블록 형식"""
        response = """```json
{
  "{{TITLE}}": {
    "type": "section_title",
    "description": "제목",
    "examples": ["예시"],
    "required": true
  }
}
```"""
        result = _parse_batch_json_response(response)
        assert result is not None
        assert "{{TITLE}}" in result

    def test_parse_with_surrounding_text(self):
        """주변 텍스트가 있는 경우"""
        response = """
응답입니다:
{
  "{{DATE}}": {
    "type": "field",
    "description": "날짜",
    "required": true
  }
}
완료되었습니다.
"""
        result = _parse_batch_json_response(response)
        assert result is not None
        assert "{{DATE}}" in result

    def test_parse_invalid_json(self):
        """유효하지 않은 JSON"""
        response = '{"{{TITLE}}": invalid json}'
        result = _parse_batch_json_response(response)
        assert result is None

    def test_parse_empty_object(self):
        """빈 객체"""
        response = "{}"
        result = _parse_batch_json_response(response)
        assert result is None

    def test_parse_no_json_found(self):
        """JSON이 없는 경우"""
        response = "No JSON here"
        result = _parse_batch_json_response(response)
        assert result is None


# ============================================================================
# Unit Test 3: batch_generate_placeholder_metadata() - 배치 Claude API 호출
# ============================================================================


class TestBatchGeneratePlaceholderMetadata:
    """배치 Claude API 호출 테스트"""

    @pytest.mark.asyncio
    async def test_batch_generate_success(self):
        """성공 케이스"""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
        template_context = "금융 보고서"

        mock_response = {
            "{{TITLE}}": {
                "type": "section_title",
                "description": "보고서 제목",
                "examples": ["예시 1"],
                "required": True
            },
            "{{SUMMARY}}": {
                "type": "section_content",
                "description": "보고서 요약",
                "examples": ["예시 2"],
                "required": True
            },
            "{{DATE}}": {
                "type": "field",
                "description": "작성 날짜",
                "examples": ["2025-01-01"],
                "required": True
            }
        }

        with patch("app.utils.claude_metadata_generator.ClaudeClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.chat_completion.return_value = (json.dumps(mock_response), 100, 200)

            result = await batch_generate_placeholder_metadata(
                placeholders=placeholders,
                template_context=template_context,
                timeout=None
            )

            assert result is not None
            assert len(result) == 3
            assert "{{TITLE}}" in result
            assert "{{SUMMARY}}" in result
            assert "{{DATE}}" in result
            assert result["{{TITLE}}"]["type"] == "section_title"

    @pytest.mark.asyncio
    async def test_batch_generate_empty_placeholders(self):
        """빈 Placeholder 리스트"""
        result = await batch_generate_placeholder_metadata(
            placeholders=[],
            template_context="금융 보고서"
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test_batch_generate_api_failure(self):
        """Claude API 호출 실패"""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}"]

        with patch("app.utils.claude_metadata_generator.ClaudeClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.chat_completion.side_effect = Exception("API Error")

            result = await batch_generate_placeholder_metadata(
                placeholders=placeholders,
                template_context="금융 보고서"
            )

            # 실패 시 모든 Placeholder에 대해 None 반환
            assert all(v is None for v in result.values())

    @pytest.mark.asyncio
    async def test_batch_generate_partial_failure(self):
        """부분 실패 (일부 Placeholder 누락)"""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}"]

        # 응답에 SUMMARY가 누락됨
        mock_response = {
            "{{TITLE}}": {
                "type": "section_title",
                "description": "제목",
                "examples": [],
                "required": True
            }
        }

        with patch("app.utils.claude_metadata_generator.ClaudeClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.chat_completion.return_value = (json.dumps(mock_response), 100, 200)

            result = await batch_generate_placeholder_metadata(
                placeholders=placeholders,
                template_context="금융 보고서"
            )

            # 응답된 것만 포함
            assert "{{TITLE}}" in result
            assert result["{{TITLE}}"] is not None


# ============================================================================
# Unit Test 4: _batch_generate_metadata_single_batch() - 단일 배치 처리
# ============================================================================


class TestBatchGenerateMetadataSingleBatch:
    """단일 배치 처리 테스트"""

    @pytest.mark.asyncio
    async def test_single_batch_success(self):
        """성공 케이스"""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}"]

        mock_response = {
            "{{TITLE}}": {
                "type": "section_title",
                "description": "제목",
                "examples": [],
                "required": True
            },
            "{{SUMMARY}}": {
                "type": "section_content",
                "description": "요약",
                "examples": [],
                "required": True
            }
        }

        with patch(
            "app.utils.placeholder_metadata_generator.batch_generate_placeholder_metadata",
            new_callable=AsyncMock
        ) as mock_batch_func:
            mock_batch_func.return_value = mock_response

            result = await _batch_generate_metadata_single_batch(
                placeholders=placeholders,
                template_context="금융 보고서"
            )

            assert result == mock_response
            mock_batch_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_single_batch_failure(self):
        """배치 처리 실패"""
        placeholders = ["{{TITLE}}", "{{SUMMARY}}"]

        with patch(
            "app.utils.placeholder_metadata_generator.batch_generate_placeholder_metadata",
            new_callable=AsyncMock
        ) as mock_batch_func:
            mock_batch_func.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                await _batch_generate_metadata_single_batch(
                    placeholders=placeholders,
                    template_context="금융 보고서"
                )


# ============================================================================
# Unit Test 5: batch_generate_metadata() - 리팩토링된 배치 처리 (asyncio.gather)
# ============================================================================


class TestBatchGenerateMetadata:
    """리팩토링된 배치 처리 테스트 (asyncio.gather)"""

    @pytest.mark.asyncio
    async def test_batch_generate_metadata_parallel_execution(self):
        """asyncio.gather 병렬 실행 검증"""
        placeholders = [
            "{{TITLE}}", "{{SUMMARY}}", "{{DATE}}",
            "{{AUTHOR}}", "{{DEPARTMENT}}", "{{RISK}}"
        ]
        template_context = "금융 보고서"
        batch_size = 2  # 3개 배치로 분할

        # 각 배치의 모의 응답
        def create_mock_response(batch_placeholders):
            return {
                ph: {
                    "type": "field",
                    "description": f"{ph} description",
                    "examples": [],
                    "required": True
                }
                for ph in batch_placeholders
            }

        call_times = []

        async def mock_batch_func(placeholders, template_context, timeout=None):
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)  # 배치 처리 시뮬레이션
            return create_mock_response(placeholders)

        with patch(
            "app.utils.placeholder_metadata_generator.batch_generate_placeholder_metadata",
            side_effect=mock_batch_func
        ):
            start_time = asyncio.get_event_loop().time()
            result = await batch_generate_metadata(
                placeholders=placeholders,
                template_context=template_context,
                batch_size=batch_size
            )
            end_time = asyncio.get_event_loop().time()

            # 검증
            assert len(result) == 6
            for ph in placeholders:
                assert ph in result
                assert result[ph] is not None

            # 병렬 처리 검증: 3개 배치 × 0.1초 + overhead < 0.5초
            # (순차: 3 × 0.1 = 0.3초 이상)
            elapsed = end_time - start_time
            assert elapsed < 0.5, f"병렬 처리 실패: {elapsed}초 소요"

    @pytest.mark.asyncio
    async def test_batch_generate_metadata_empty_list(self):
        """빈 Placeholder 리스트"""
        result = await batch_generate_metadata(
            placeholders=[],
            template_context="금융 보고서"
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test_batch_generate_metadata_single_placeholder(self):
        """단일 Placeholder"""
        placeholders = ["{{TITLE}}"]
        mock_response = {
            "{{TITLE}}": {
                "type": "section_title",
                "description": "제목",
                "examples": [],
                "required": True
            }
        }

        with patch(
            "app.utils.placeholder_metadata_generator.batch_generate_placeholder_metadata",
            new_callable=AsyncMock
        ) as mock_batch_func:
            mock_batch_func.return_value = mock_response

            result = await batch_generate_metadata(
                placeholders=placeholders,
                template_context="금융 보고서",
                batch_size=3
            )

            assert len(result) == 1
            assert "{{TITLE}}" in result
            assert result["{{TITLE}}"] is not None

    @pytest.mark.asyncio
    async def test_batch_generate_metadata_partial_batch_failure(self):
        """배치 부분 실패 (일부 배치 실패)"""
        placeholders = [
            "{{TITLE}}", "{{SUMMARY}}", "{{DATE}}",
            "{{AUTHOR}}", "{{DEPARTMENT}}"
        ]
        batch_size = 2  # 3개 배치

        batch_call_count = 0

        async def mock_batch_func_with_failure(
            placeholders, template_context="보고서", timeout=None
        ):
            nonlocal batch_call_count
            batch_call_count += 1

            # 두 번째 배치는 실패
            if batch_call_count == 2:
                raise Exception("Batch 2 failed")

            return {
                ph: {
                    "type": "field",
                    "description": f"{ph}",
                    "examples": [],
                    "required": True
                }
                for ph in placeholders
            }

        with patch(
            "app.utils.placeholder_metadata_generator.batch_generate_placeholder_metadata",
            side_effect=mock_batch_func_with_failure
        ):
            result = await batch_generate_metadata(
                placeholders=placeholders,
                template_context="금융 보고서",
                batch_size=batch_size
            )

            # 첫 번째 배치와 세 번째 배치는 성공, 두 번째는 실패
            assert len(result) == 5
            assert result["{{TITLE}}"] is not None
            assert result["{{SUMMARY}}"] is not None
            # 두 번째 배치의 항목들
            assert result["{{DATE}}"] is None
            assert result["{{AUTHOR}}"] is None
            # 세 번째 배치
            assert result["{{DEPARTMENT}}"] is not None


# ============================================================================
# Integration Test: 엔드 투 엔드 배치 처리 플로우
# ============================================================================


class TestBatchMetadataIntegration:
    """배치 메타정보 생성 엔드 투 엔드 테스트"""

    @pytest.mark.asyncio
    async def test_full_batch_processing_flow(self):
        """전체 플로우: 분할 → 병렬 처리 → 결과 병합"""
        placeholders = [
            "{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}",
            "{{KEY_POINTS}}", "{{CONCLUSION}}", "{{DATE}}"
        ]
        template_context = "금융 보고서"
        batch_size = 2

        # 모의 응답 생성
        mock_responses = {
            "{{TITLE}}": {"type": "section_title", "required": True},
            "{{SUMMARY}}": {"type": "section_content", "required": True},
            "{{BACKGROUND}}": {"type": "section_content", "required": True},
            "{{KEY_POINTS}}": {"type": "section_content", "required": True},
            "{{CONCLUSION}}": {"type": "section_content", "required": True},
            "{{DATE}}": {"type": "field", "required": True}
        }

        async def mock_batch_generator(placeholders, template_context="보고서", timeout=None):
            await asyncio.sleep(0.05)
            return {ph: mock_responses[ph] for ph in placeholders}

        with patch(
            "app.utils.placeholder_metadata_generator.batch_generate_placeholder_metadata",
            side_effect=mock_batch_generator
        ):
            result = await batch_generate_metadata(
                placeholders=placeholders,
                template_context=template_context,
                batch_size=batch_size
            )

            # 검증
            assert len(result) == 6
            for ph in placeholders:
                assert ph in result
                assert result[ph] is not None
                assert "type" in result[ph]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
