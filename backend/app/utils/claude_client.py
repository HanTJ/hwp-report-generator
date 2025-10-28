"""
Claude API 클라이언트
보고서 내용을 생성하기 위한 Claude API 통신 모듈
"""
import os
import logging
from typing import Dict
from anthropic import Anthropic

# shared.constants를 import하면 자동으로 sys.path 설정됨
from shared.constants import ClaudeConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClaudeClient:
    """Claude API를 사용하여 보고서 내용을 생성하는 클라이언트"""

    def __init__(self):
        """Claude 클라이언트 초기화"""
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", ClaudeConfig.MODEL)
        self.max_tokens = ClaudeConfig.MAX_TOKENS

        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY 환경 변수가 설정되지 않았습니다.")

        self.client = Anthropic(api_key=self.api_key)

        # 토큰 사용량 추적
        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_total_tokens = 0

    def generate_report(self, topic: str) -> Dict[str, str]:
        """
        주제를 받아 금융 업무보고서 내용을 생성합니다.

        Args:
            topic: 보고서 주제

        Returns:
            Dict[str, str]: 보고서 각 섹션의 내용
                - title: 보고서 제목
                - title_background: 배경 섹션 제목
                - title_main_content: 주요내용 섹션 제목
                - title_conclusion: 결론 섹션 제목
                - title_summary: 요약 섹션 제목
                - summary: 요약
                - background: 배경 및 목적
                - main_content: 주요 내용
                - conclusion: 결론 및 제언
        """

        prompt = f"""당신은 금융 기관의 전문 보고서 작성자입니다.
다음 주제에 대한 금융 업무보고서를 작성해주세요.

주제: {topic}

아래 형식에 맞춰 각 섹션을 작성해주세요:

1. 제목 (간결하고 명확하게)
2. 배경 섹션 제목 (예: "배경 및 목적", "추진 배경" 등)
3. 배경 및 목적 (왜 이 보고서가 필요한지 설명)
4. 주요내용 섹션 제목 (예: "주요 내용", "분석 결과" 등)
5. 주요 내용 (구체적이고 상세한 분석 및 설명, 3-5개 소제목 포함)
6. 결론 섹션 제목 (예: "결론 및 제언", "향후 계획" 등)
7. 결론 및 제언 (요약과 향후 조치사항)
8. 요약 섹션 제목 (예: "요약", "핵심 요약" 등)
9. 요약 (2-3문단, 핵심 내용 요약)

각 섹션은 반드시 다음 구분자로 시작해야 합니다:
[제목]
[배경제목]
[배경]
[주요내용제목]
[주요내용]
[결론제목]
[결론]
[요약제목]
[요약]

전문적이고 격식있는 문체로 작성하되, 명확하고 이해하기 쉽게 작성해주세요.
금융 용어와 데이터를 적절히 활용하여 신뢰성을 높여주세요."""

        try:
            logger.info(f"Claude API 호출 시작 - 주제: {topic}")
            logger.info(f"사용 모델: {self.model}")
            logger.info(f"최대 토큰: {self.max_tokens}")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답 텍스트 파싱
            content = message.content[0].text

            logger.info("=" * 80)
            logger.info("Claude API 응답 내용:")
            logger.info("=" * 80)
            logger.info(content)
            logger.info("=" * 80)

            logger.info(f"응답 길이: {len(content)} 문자")
            logger.info(f"토큰 사용량 - Input: {message.usage.input_tokens}, Output: {message.usage.output_tokens}")

            # 토큰 사용량 저장
            self.last_input_tokens = message.usage.input_tokens
            self.last_output_tokens = message.usage.output_tokens
            self.last_total_tokens = self.last_input_tokens + self.last_output_tokens

            parsed_content = self._parse_report_content(content)

            logger.info("내용 파싱 완료:")
            for key, value in parsed_content.items():
                logger.info(f"  - {key}: {len(value)} 문자")

            return parsed_content

        except Exception as e:
            logger.error(f"Claude API 호출 중 오류 발생: {str(e)}")
            raise Exception(f"Claude API 호출 중 오류 발생: {str(e)}")

    def _parse_report_content(self, content: str) -> Dict[str, str]:
        """
        Claude의 응답을 파싱하여 각 섹션으로 분리합니다.

        Args:
            content: Claude API 응답 텍스트

        Returns:
            Dict[str, str]: 파싱된 보고서 섹션
        """
        sections = {
            "title": "",
            "title_background": "",
            "title_main_content": "",
            "title_conclusion": "",
            "title_summary": "",
            "summary": "",
            "background": "",
            "main_content": "",
            "conclusion": ""
        }

        # 구분자로 내용 분리
        parts = content.split("[제목]")
        if len(parts) > 1:
            remaining = parts[1]

            # 제목 추출
            if "[배경제목]" in remaining:
                sections["title"] = remaining.split("[배경제목]")[0].strip()
                remaining = "[배경제목]" + remaining.split("[배경제목]")[1]

            # 배경 섹션 제목 추출
            if "[배경제목]" in remaining and "[배경]" in remaining:
                sections["title_background"] = remaining.split("[배경제목]")[1].split("[배경]")[0].strip()
                remaining = "[배경]" + remaining.split("[배경]")[1]

            # 배경 추출
            if "[배경]" in remaining and "[주요내용제목]" in remaining:
                sections["background"] = remaining.split("[배경]")[1].split("[주요내용제목]")[0].strip()
                remaining = "[주요내용제목]" + remaining.split("[주요내용제목]")[1]

            # 주요내용 섹션 제목 추출
            if "[주요내용제목]" in remaining and "[주요내용]" in remaining:
                sections["title_main_content"] = remaining.split("[주요내용제목]")[1].split("[주요내용]")[0].strip()
                remaining = "[주요내용]" + remaining.split("[주요내용]")[1]

            # 주요내용 추출
            if "[주요내용]" in remaining and "[결론제목]" in remaining:
                sections["main_content"] = remaining.split("[주요내용]")[1].split("[결론제목]")[0].strip()
                remaining = "[결론제목]" + remaining.split("[결론제목]")[1]

            # 결론 섹션 제목 추출
            if "[결론제목]" in remaining and "[결론]" in remaining:
                sections["title_conclusion"] = remaining.split("[결론제목]")[1].split("[결론]")[0].strip()
                remaining = "[결론]" + remaining.split("[결론]")[1]

            # 결론 추출
            if "[결론]" in remaining and "[요약제목]" in remaining:
                sections["conclusion"] = remaining.split("[결론]")[1].split("[요약제목]")[0].strip()
                remaining = "[요약제목]" + remaining.split("[요약제목]")[1]

            # 요약 섹션 제목 추출
            if "[요약제목]" in remaining and "[요약]" in remaining:
                sections["title_summary"] = remaining.split("[요약제목]")[1].split("[요약]")[0].strip()
                remaining = "[요약]" + remaining.split("[요약]")[1]

            # 요약 추출
            if "[요약]" in remaining:
                sections["summary"] = remaining.split("[요약]")[1].strip()

        # 빈 섹션이 있는지 확인
        for key, value in sections.items():
            if not value:
                sections[key] = f"(내용이 생성되지 않았습니다: {key})"

        return sections

    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        system_prompt: str = None
    ) -> tuple[str, int, int]:
        """Chat-based completion for conversational report generation.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
                     Example: [{"role": "user", "content": "Write a report"}]
            system_prompt: Optional system prompt (default: financial report writer)

        Returns:
            Tuple of (response_content, input_tokens, output_tokens)

        Raises:
            Exception: If API call fails

        Examples:
            >>> client = ClaudeClient()
            >>> messages = [{"role": "user", "content": "디지털뱅킹 트렌드 보고서 작성"}]
            >>> response, input_tokens, output_tokens = client.chat_completion(messages)
            >>> print(response[:100])
            # 디지털뱅킹 트렌드 분석 보고서

## 요약

2025년 디지털뱅킹 산업은...
        """
        # Default system prompt for financial reports
        if system_prompt is None:
            system_prompt = """당신은 금융 기관의 전문 보고서 작성자입니다.
사용자의 요청에 따라 전문적이고 격식있는 금융 업무보고서를 Markdown 형식으로 작성해주세요.

보고서는 다음 섹션을 포함해야 합니다:
- # 제목 (H1)
- ## 요약 (H2)
- ## 배경 및 목적 (H2)
- ## 주요 내용 (H2)
- ## 결론 및 제언 (H2)

명확하고 이해하기 쉽게 작성하되, 금융 용어와 데이터를 적절히 활용하여 신뢰성을 높여주세요.
모든 출력은 Markdown 형식이어야 합니다."""

        try:
            logger.info(f"Claude chat completion 시작 - 메시지 수: {len(messages)}")
            logger.info(f"사용 모델: {self.model}")
            logger.info(f"최대 토큰: {self.max_tokens}")

            # API call with system prompt
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages
            )

            # Extract response content
            content = response.content[0].text

            logger.info("=" * 80)
            logger.info("Claude API 응답 (채팅 모드):")
            logger.info("=" * 80)
            logger.info(content[:500] + "..." if len(content) > 500 else content)
            logger.info("=" * 80)

            logger.info(f"응답 길이: {len(content)} 문자")
            logger.info(f"토큰 사용량 - Input: {response.usage.input_tokens}, Output: {response.usage.output_tokens}")

            # Track token usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            self.last_input_tokens = input_tokens
            self.last_output_tokens = output_tokens
            self.last_total_tokens = input_tokens + output_tokens

            return content, input_tokens, output_tokens

        except Exception as e:
            logger.error(f"Claude chat completion 중 오류 발생: {str(e)}")
            raise Exception(f"Claude chat completion 중 오류 발생: {str(e)}")

    def get_token_usage(self) -> Dict[str, int]:
        """Gets the last API call's token usage.

        Returns:
            Dictionary with input_tokens, output_tokens, total_tokens

        Examples:
            >>> client = ClaudeClient()
            >>> client.chat_completion([{"role": "user", "content": "Test"}])
            >>> usage = client.get_token_usage()
            >>> print(usage["total_tokens"])
            1250
        """
        return {
            "input_tokens": self.last_input_tokens,
            "output_tokens": self.last_output_tokens,
            "total_tokens": self.last_total_tokens
        }
