"""
Template 메타정보 생성 Integration 테스트

Template 업로드 시 메타정보 생성 전체 흐름을 테스트합니다.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from app.utils.claude_metadata_generator import generate_placeholder_metadata
from app.utils.prompts import create_system_prompt_with_metadata


class TestTemplateMetadataGenerationFlow:
    """Template 메타정보 생성 흐름 테스트"""

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_full_metadata_pipeline(self, mock_claude_class):
        """메타정보 생성 전체 파이프라인"""
        # Mock Claude 응답
        metadata_response = json.dumps(
            [
                {
                    "key": "{{TITLE}}",
                    "type": "section_title",
                    "display_name": "제목",
                    "description": "보고서의 주요 제목입니다.",
                    "examples": ["2024년 금융시장 동향"],
                    "required": True,
                    "order_hint": 1,
                },
                {
                    "key": "{{SUMMARY}}",
                    "type": "section_content",
                    "display_name": "요약",
                    "description": "보고서의 핵심을 요약합니다.",
                    "examples": ["본 보고서는 최근 금융시장 동향을 분석합니다."],
                    "required": True,
                    "order_hint": 2,
                },
            ]
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (metadata_response, 100, 200)
        mock_claude_class.return_value = mock_claude

        # Step 1: Placeholder 리스트
        placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}"]

        # Step 2: Claude API로 메타정보 생성
        metadata = generate_placeholder_metadata(placeholders)

        assert metadata is not None
        assert len(metadata) == 2  # 응답은 2개만 있음

        # Step 3: System Prompt 생성
        system_prompt = create_system_prompt_with_metadata(placeholders, metadata)

        assert "제목" in system_prompt
        assert "요약" in system_prompt
        assert "보고서의 주요 제목입니다." in system_prompt
        assert "보고서의 핵심을 요약합니다." in system_prompt
        assert "{{TITLE}}" in system_prompt
        assert "{{SUMMARY}}" in system_prompt
        assert "{{BACKGROUND}}" in system_prompt

        # Step 4: DB에 저장될 System Prompt 확인
        assert len(system_prompt) > 700  # 충분히 자세한 프롬프트
        assert "마크다운" in system_prompt
        assert "섹션별 상세 지침" in system_prompt

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_metadata_generation_with_fallback(self, mock_claude_class):
        """메타정보 생성 실패 시 폴백"""
        # Claude API 실패
        mock_claude = MagicMock()
        mock_claude.chat_completion.side_effect = Exception("API Error")
        mock_claude_class.return_value = mock_claude

        placeholders = ["{{TITLE}}", "{{SUMMARY}}"]

        # Step 1: Claude API 호출 실패
        metadata = generate_placeholder_metadata(placeholders)

        assert metadata is None

        # Step 2: 메타정보 없이 System Prompt 생성
        system_prompt = create_system_prompt_with_metadata(placeholders, metadata)

        # 메타정보 없어도 기본 구조는 생성됨
        assert "{{TITLE}}" in system_prompt
        assert "{{SUMMARY}}" in system_prompt
        assert "메타정보 미생성" in system_prompt  # 폴백 표시

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_metadata_generation_with_invalid_response(self, mock_claude_class):
        """잘못된 Claude 응답 처리"""
        # Claude가 잘못된 형식의 응답 반환
        mock_claude = MagicMock()
        mock_claude.chat_completion.return_value = "이것은 JSON이 아닙니다."
        mock_claude_class.return_value = mock_claude

        placeholders = ["{{TITLE}}", "{{SUMMARY}}"]

        # Step 1: Claude 응답 파싱 실패
        metadata = generate_placeholder_metadata(placeholders)

        assert metadata is None

        # Step 2: 폴백으로 System Prompt 생성
        system_prompt = create_system_prompt_with_metadata(placeholders, metadata)

        assert "{{TITLE}}" in system_prompt
        assert "메타정보 미생성" in system_prompt

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_partial_metadata_response(self, mock_claude_class):
        """일부만 메타정보를 반환"""
        # Claude가 일부 Placeholder에만 메타정보 반환
        metadata_response = json.dumps(
            [
                {
                    "key": "{{TITLE}}",
                    "type": "section_title",
                    "display_name": "제목",
                    "description": "제목입니다.",
                    "examples": [],
                    "required": True,
                    "order_hint": 1,
                }
                # SUMMARY는 없음
            ]
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (metadata_response, 100, 200)
        mock_claude_class.return_value = mock_claude

        placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}"]

        # Step 1: 일부 메타정보 생성
        metadata = generate_placeholder_metadata(placeholders)

        assert metadata is not None
        assert len(metadata) == 1  # TITLE만

        # Step 2: System Prompt 생성
        system_prompt = create_system_prompt_with_metadata(placeholders, metadata)

        # TITLE 메타정보는 포함, 나머지는 미생성 표시
        assert "제목" in system_prompt
        assert "메타정보 미생성" in system_prompt  # SUMMARY, BACKGROUND

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_complex_metadata_structure(self, mock_claude_class):
        """복잡한 메타정보 구조"""
        metadata_response = json.dumps(
            [
                {
                    "key": "{{TITLE}}",
                    "type": "section_title",
                    "display_name": "보고서 제목",
                    "description": "보고서의 주요 제목입니다. 명확하고 임팩트 있는 제목을 작성하세요.",
                    "examples": [
                        "2024년 금융시장 동향 분석",
                        "디지털 뱅킹 시장 성장 현황",
                    ],
                    "required": True,
                    "order_hint": 1,
                },
                {
                    "key": "{{DATE}}",
                    "type": "metadata",
                    "display_name": "보고 날짜",
                    "description": "보고서 작성 날짜입니다.",
                    "examples": ["2025-11-11"],
                    "required": False,
                    "order_hint": 0,
                },
            ]
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (metadata_response, 100, 200)
        mock_claude_class.return_value = mock_claude

        placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]

        metadata = generate_placeholder_metadata(placeholders)
        system_prompt = create_system_prompt_with_metadata(placeholders, metadata)

        # 메타정보 타입 반영 확인
        assert "보고서 제목" in system_prompt
        assert "보고 날짜" in system_prompt
        assert "명확하고 임팩트 있는 제목을 작성하세요." in system_prompt
        assert "필수" in system_prompt  # TITLE은 필수
        assert "선택" in system_prompt  # DATE는 선택

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_metadata_with_special_characters(self, mock_claude_class):
        """특수문자가 포함된 메타정보"""
        metadata_response = json.dumps(
            [
                {
                    "key": "{{TITLE}}",
                    "type": "section_title",
                    "display_name": "제목",
                    "description": '보고서 제목 (예: "2024년 금융시장" 동향)',
                    "examples": ["금융시장 & 기술 트렌드 분석"],
                    "required": True,
                    "order_hint": 1,
                }
            ],
            ensure_ascii=False,  # 한글 처리
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (metadata_response, 100, 200)
        mock_claude_class.return_value = mock_claude

        placeholders = ["{{TITLE}}"]

        metadata = generate_placeholder_metadata(placeholders)
        assert metadata is not None

        system_prompt = create_system_prompt_with_metadata(placeholders, metadata)

        assert "2024년 금융시장" in system_prompt
        assert "금융시장 & 기술 트렌드 분석" in system_prompt

    @patch("app.utils.claude_metadata_generator.ClaudeClient")
    def test_empty_examples_handling(self, mock_claude_class):
        """빈 예시 처리"""
        metadata_response = json.dumps(
            [
                {
                    "key": "{{TITLE}}",
                    "type": "section_title",
                    "display_name": "제목",
                    "description": "제목입니다.",
                    "examples": [],  # 빈 예시
                    "required": True,
                    "order_hint": 1,
                }
            ]
        )

        mock_claude = MagicMock()
        # chat_completion() returns tuple: (content, input_tokens, output_tokens)
        mock_claude.chat_completion.return_value = (metadata_response, 100, 200)
        mock_claude_class.return_value = mock_claude

        placeholders = ["{{TITLE}}"]

        metadata = generate_placeholder_metadata(placeholders)
        system_prompt = create_system_prompt_with_metadata(placeholders, metadata)

        # 빈 예시도 처리됨
        assert "예시 미제공" in system_prompt or "예시" in system_prompt


class TestErrorHandling:
    """에러 처리 테스트"""

    def test_none_placeholders(self):
        """None Placeholder 리스트"""
        # None 입력은 None을 반환함 (방어적 프로그래밍)
        result = generate_placeholder_metadata(None)
        assert result is None

    def test_invalid_placeholder_format(self):
        """잘못된 Placeholder 형식"""
        # 형식이 맞지 않아도 Claude API 호출은 시도됨
        placeholders = ["TITLE", "SUMMARY"]  # {{}} 없음

        # Placeholder 형식 검증은 이전 단계에서 수행되므로
        # 여기서는 그냥 API 호출만 시도됨


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
