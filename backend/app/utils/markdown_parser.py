"""
Markdown 파일을 파싱하여 HWPHandler에 필요한 content dict로 변환
"""
import re
from typing import Dict


def parse_markdown_to_content(md_text: str) -> Dict[str, str]:
    """Markdown 텍스트를 파싱하여 HWPHandler.generate_report()에 필요한 content dict로 변환.

    Args:
        md_text: Markdown 형식의 텍스트

    Returns:
        HWP 플레이스홀더에 매핑될 content 딕셔너리:
            - title: 보고서 제목
            - summary: 요약 내용
            - background: 배경 내용
            - main_content: 주요 내용
            - conclusion: 결론 내용
            - title_summary: 요약 섹션 제목 (기본: "요약")
            - title_background: 배경 섹션 제목 (기본: "배경 및 목적")
            - title_main_content: 주요 내용 섹션 제목 (기본: "주요 내용")
            - title_conclusion: 결론 섹션 제목 (기본: "결론 및 제언")

    Examples:
        >>> md = "# 디지털뱅킹 트렌드\\n\\n## 요약\\n\\n2025년 주요 트렌드..."
        >>> content = parse_markdown_to_content(md)
        >>> print(content['title'])
        디지털뱅킹 트렌드
    """
    content = {
        "title": "",
        "summary": "",
        "background": "",
        "main_content": "",
        "conclusion": "",
        "title_summary": "요약",
        "title_background": "배경 및 목적",
        "title_main_content": "주요 내용",
        "title_conclusion": "결론 및 제언"
    }

    # 첫 번째 # 제목을 title로 추출
    title_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    if title_match:
        content["title"] = title_match.group(1).strip()

    # 섹션 추출 함수
    def extract_section(header_pattern: str, next_header_pattern: str = None) -> str:
        """특정 헤더 아래 내용을 추출.

        Args:
            header_pattern: 현재 섹션 헤더 패턴 (정규표현식)
            next_header_pattern: 다음 섹션 헤더 패턴 (옵션)

        Returns:
            추출된 섹션 내용
        """
        if next_header_pattern:
            pattern = rf'{header_pattern}\n\n(.+?)(?=\n\n{next_header_pattern}|\Z)'
        else:
            pattern = rf'{header_pattern}\n\n(.+?)(?=\Z)'

        match = re.search(pattern, md_text, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""

    # 각 섹션 추출 (## 헤더 기준)
    # Claude가 생성하는 MD 형식:
    # ## 요약
    # ## 배경 및 목적
    # ## 주요 내용
    # ## 결론 및 제언

    content["summary"] = extract_section(r'##\s*요약', r'##\s*배경')
    content["background"] = extract_section(r'##\s*배경[^#]*', r'##\s*주요')
    content["main_content"] = extract_section(r'##\s*주요\s*내용', r'##\s*결론')
    content["conclusion"] = extract_section(r'##\s*결론[^#]*')

    # 내용이 비어있으면 전체 텍스트를 main_content로 사용
    if not any([content["summary"], content["background"],
                content["main_content"], content["conclusion"]]):
        # 제목 다음 모든 내용을 main_content로
        if title_match:
            content["main_content"] = md_text[title_match.end():].strip()
        else:
            content["main_content"] = md_text.strip()

    return content


def extract_title_from_markdown(md_text: str) -> str:
    """Markdown에서 제목만 추출 (간편 함수).

    Args:
        md_text: Markdown 텍스트

    Returns:
        추출된 제목 (없으면 "보고서")

    Examples:
        >>> md = "# 2025 디지털뱅킹 보고서\\n\\n내용..."
        >>> title = extract_title_from_markdown(md)
        >>> print(title)
        2025 디지털뱅킹 보고서
    """
    title_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return "보고서"
