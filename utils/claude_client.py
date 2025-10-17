"""
Claude API 클라이언트
보고서 내용을 생성하기 위한 Claude API 통신 모듈
"""
import os
from typing import Dict
from anthropic import Anthropic


class ClaudeClient:
    """Claude API를 사용하여 보고서 내용을 생성하는 클라이언트"""

    def __init__(self):
        """Claude 클라이언트 초기화"""
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY 환경 변수가 설정되지 않았습니다.")

        self.client = Anthropic(api_key=self.api_key)

    def generate_report(self, topic: str) -> Dict[str, str]:
        """
        주제를 받아 금융 업무보고서 내용을 생성합니다.

        Args:
            topic: 보고서 주제

        Returns:
            Dict[str, str]: 보고서 각 섹션의 내용
                - title: 보고서 제목
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
2. 요약 (2-3문단, 핵심 내용 요약)
3. 배경 및 목적 (왜 이 보고서가 필요한지 설명)
4. 주요 내용 (구체적이고 상세한 분석 및 설명, 3-5개 소제목 포함)
5. 결론 및 제언 (요약과 향후 조치사항)

각 섹션은 반드시 다음 구분자로 시작해야 합니다:
[제목]
[요약]
[배경]
[주요내용]
[결론]

전문적이고 격식있는 문체로 작성하되, 명확하고 이해하기 쉽게 작성해주세요.
금융 용어와 데이터를 적절히 활용하여 신뢰성을 높여주세요."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답 텍스트 파싱
            content = message.content[0].text

            return self._parse_report_content(content)

        except Exception as e:
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
            if "[요약]" in remaining:
                sections["title"] = remaining.split("[요약]")[0].strip()
                remaining = "[요약]" + remaining.split("[요약]")[1]

            # 요약 추출
            if "[요약]" in remaining and "[배경]" in remaining:
                sections["summary"] = remaining.split("[요약]")[1].split("[배경]")[0].strip()
                remaining = "[배경]" + remaining.split("[배경]")[1]

            # 배경 추출
            if "[배경]" in remaining and "[주요내용]" in remaining:
                sections["background"] = remaining.split("[배경]")[1].split("[주요내용]")[0].strip()
                remaining = "[주요내용]" + remaining.split("[주요내용]")[1]

            # 주요내용 추출
            if "[주요내용]" in remaining and "[결론]" in remaining:
                sections["main_content"] = remaining.split("[주요내용]")[1].split("[결론]")[0].strip()
                remaining = "[결론]" + remaining.split("[결론]")[1]

            # 결론 추출
            if "[결론]" in remaining:
                sections["conclusion"] = remaining.split("[결론]")[1].strip()

        # 빈 섹션이 있는지 확인
        for key, value in sections.items():
            if not value:
                sections[key] = f"(내용이 생성되지 않았습니다: {key})"

        return sections
