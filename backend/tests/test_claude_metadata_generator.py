"""
Claude Metadata Generator 테스트

메타정보 생성 유틸의 단위 테스트를 포함합니다.
"""

import json
import pytest
from typing import Optional
from unittest.mock import Mock, patch, MagicMock

from app.utils.claude_metadata_generator import (
    generate_placeholder_metadata,
    _parse_json_response,
    SYSTEM_PROMPT_GENERATOR,
)


class TestParseJsonResponse:
    """JSON 파싱 함수 테스트"""

    def test_parse_pure_json_array(self):
        """순수 JSON 배열 파싱"""
        response = '[{"key": "{{TITLE}}", "type": "section_title"}]'
        result = _parse_json_response(response)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["key"] == "{{TITLE}}"

    def test_parse_markdown_code_block(self):
        """마크다운 코드블록 파싱"""
        response = '```json\n[{"key": "{{TITLE}}", "type": "section_title"}]\n```'
        result = _parse_json_response(response)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1

    def test_parse_markdown_code_block_without_json_lang(self):
        """마크다운 코드블록 (json 언어 지정 없음) 파싱"""
        response = '```\n[{"key": "{{TITLE}}", "type": "section_title"}]\n```'
        result = _parse_json_response(response)
        assert result is not None
        assert isinstance(result, list)

    def test_parse_json_with_surrounding_text(self):
        """주변 텍스트가 있는 JSON 파싱"""
        response = "다음은 메타정보입니다:\n[{\"key\": \"{{TITLE}}\"}]\n감사합니다."
        result = _parse_json_response(response)
        assert result is not None
        assert isinstance(result, list)

    def test_parse_invalid_json(self):
        """잘못된 JSON 파싱"""
        response = "invalid json"
        result = _parse_json_response(response)
        assert result is None

    def test_parse_non_array_json(self):
        """배열이 아닌 JSON 파싱"""
        response = '{"key": "{{TITLE}}"}'
        result = _parse_json_response(response)
        assert result is None

    def test_parse_empty_array(self):
        """빈 배열 파싱"""
        response = "[]"
        result = _parse_json_response(response)
        assert result is None  # 빈 배열은 None 반환

    def test_parse_unclosed_markdown_block(self):
        """닫히지 않은 마크다운 블록"""
        response = "```json\n[{\"key\": \"{{TITLE}}\"}]"
        result = _parse_json_response(response)
        assert result is None


class TestGeneratePlaceholderMetadata:
    """메타정보 생성 함수 테스트"""

    def test_empty_placeholder_list(self):
        """빈 Placeholder 리스트"""
        result = generate_placeholder_metadata([])
        assert result is None

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_single_placeholder(self, mock_claude_class):
        """단일 Placeholder 처리"""
        # Mock Claude 응답
        mock_response_content = json.dumps(
            [
                {
                    "key": "{{TITLE}}",
                    "type": "section_title",
                    "display_name": "제목",
                    "description": "보고서의 제목입니다.",
                    "examples": ["2024년 금융시장 동향"],
                    "required": True,
                    "order_hint": 1,
                }
            ]
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (mock_response_content, 100, 200)
        mock_claude_class.return_value = mock_claude

        result = generate_placeholder_metadata(["{{TITLE}}"])

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["key"] == "{{TITLE}}"
        assert result[0]["type"] == "section_title"
        assert result[0]["display_name"] == "제목"

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_multiple_placeholders(self, mock_claude_class):
        """여러 Placeholder 처리"""
        mock_response = json.dumps(
            [
                {
                    "key": "{{TITLE}}",
                    "type": "section_title",
                    "display_name": "제목",
                    "description": "보고서 제목",
                    "examples": ["제목1"],
                    "required": True,
                    "order_hint": 1,
                },
                {
                    "key": "{{SUMMARY}}",
                    "type": "section_content",
                    "display_name": "요약",
                    "description": "요약 내용",
                    "examples": ["요약1"],
                    "required": True,
                    "order_hint": 2,
                },
            ]
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (mock_response, 150, 250)
        mock_claude_class.return_value = mock_claude

        result = generate_placeholder_metadata(
            ["{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}"]
        )

        assert result is not None
        assert len(result) == 2  # 응답은 2개

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_claude_api_failure(self, mock_claude_class):
        """Claude API 호출 실패"""
        mock_claude = MagicMock()
        mock_claude.chat_completion.side_effect = Exception("API Error")
        mock_claude_class.return_value = mock_claude

        result = generate_placeholder_metadata(["{{TITLE}}"])
        assert result is None

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_invalid_response_format(self, mock_claude_class):
        """잘못된 응답 형식"""
        mock_claude = MagicMock()
        mock_claude.chat_completion.return_value = "invalid response"
        mock_claude_class.return_value = mock_claude

        result = generate_placeholder_metadata(["{{TITLE}}"])
        assert result is None

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_markdown_code_block_response(self, mock_claude_class):
        """마크다운 코드블록 응답 처리"""
        mock_response_content = (
            "다음은 메타정보입니다:\n"
            "```json\n"
            '[{"key": "{{TITLE}}", "type": "section_title", "display_name": "제목", '
            '"description": "제목입니다.", "examples": [], "required": true, "order_hint": 1}]\n'
            "```"
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (mock_response_content, 120, 200)
        mock_claude_class.return_value = mock_claude

        result = generate_placeholder_metadata(["{{TITLE}}"])

        assert result is not None
        assert len(result) == 1
        assert result[0]["key"] == "{{TITLE}}"


class TestSystemPromptGenerator:
    """System Prompt Generator 상수 테스트"""

    def test_system_prompt_generator_exists(self):
        """System Prompt Generator 존재 확인"""
        assert SYSTEM_PROMPT_GENERATOR is not None
        assert isinstance(SYSTEM_PROMPT_GENERATOR, str)
        assert "JSON 배열" in SYSTEM_PROMPT_GENERATOR
        assert "section_title" in SYSTEM_PROMPT_GENERATOR
        assert "section_content" in SYSTEM_PROMPT_GENERATOR
        assert "metadata" in SYSTEM_PROMPT_GENERATOR


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
