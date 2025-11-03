"""
Markdown 파일을 파싱하여 HWPHandler에 필요한 content dict로 변환
"""
import re
from typing import Dict, Tuple, List


def parse_markdown_to_content(md_text: str) -> Dict[str, str]:
    """Markdown 텍스트를 파싱하여 HWPHandler.generate_report()에 필요한 content dict로 변환.

    섹션 제목을 동적으로 추출하여 HWP 템플릿의 {{TITLE_XXX}} 플레이스홀더에 대입합니다.

    Args:
        md_text: Markdown 형식의 텍스트

    Returns:
        HWP 플레이스홀더에 매핑될 content 딕셔너리:
            - title: 보고서 제목
            - summary: 요약 내용
            - background: 배경 내용
            - main_content: 주요 내용
            - conclusion: 결론 내용
            - title_summary: 요약 섹션 제목 (동적 추출)
            - title_background: 배경 섹션 제목 (동적 추출)
            - title_main_content: 주요 내용 섹션 제목 (동적 추출)
            - title_conclusion: 결론 섹션 제목 (동적 추출)

    Examples:
        >>> md = "# 디지털뱅킹 트렌드\\n\\n## 핵심 요약\\n\\n2025년..."
        >>> content = parse_markdown_to_content(md)
        >>> content['title_summary']
        '핵심 요약'
        >>> len(content['summary']) > 0
        True
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

    # 1. H1 제목 추출
    title_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    if title_match:
        content["title"] = title_match.group(1).strip()

    # 2. 모든 H2 섹션 추출 (제목 + 내용)
    h2_sections = extract_all_h2_sections(md_text)

    # 3. 키워드 기반으로 섹션 분류 및 매핑
    for section_title, section_content in h2_sections:
        section_type = classify_section(section_title)

        if section_type == "summary":
            content["title_summary"] = section_title
            content["summary"] = section_content
        elif section_type == "background":
            content["title_background"] = section_title
            content["background"] = section_content
        elif section_type == "main_content":
            content["title_main_content"] = section_title
            content["main_content"] = section_content
        elif section_type == "conclusion":
            content["title_conclusion"] = section_title
            content["conclusion"] = section_content

    # 4. 내용이 비어있으면 전체 텍스트를 main_content로 사용
    if not any([content["summary"], content["background"],
                content["main_content"], content["conclusion"]]):
        if title_match:
            content["main_content"] = md_text[title_match.end():].strip()
        else:
            content["main_content"] = md_text.strip()

    return content


def extract_all_h2_sections(md_text: str) -> List[Tuple[str, str]]:
    """Markdown에서 모든 H2 섹션을 추출합니다.

    Args:
        md_text: Markdown 텍스트

    Returns:
        (섹션 제목, 섹션 내용) 튜플의 리스트

    Examples:
        >>> md = "# Title\\n\\n## 요약\\n\\nSummary text\\n\\n## 배경\\n\\nBackground text"
        >>> sections = extract_all_h2_sections(md)
        >>> len(sections)
        2
        >>> sections[0]
        ('요약', 'Summary text')
    """
    # H2 헤더와 그 내용을 추출하는 정규식
    # 패턴: ## 제목\n\n내용 (다음 ##까지 또는 끝까지)
    pattern = r'^##\s+(.+?)\s*$\n+(.*?)(?=\n+^##\s|\Z)'
    matches = re.findall(pattern, md_text, re.MULTILINE | re.DOTALL)

    return [(title.strip(), content.strip()) for title, content in matches]


def classify_section(section_title: str) -> str:
    """섹션 제목을 분석하여 종류를 분류합니다.

    키워드 기반으로 섹션이 요약/배경/주요내용/결론 중 어디에 해당하는지 판단합니다.

    Args:
        section_title: H2 섹션 제목

    Returns:
        섹션 타입: "summary", "background", "main_content", "conclusion", "unknown"

    Examples:
        >>> classify_section("핵심 요약")
        'summary'
        >>> classify_section("추진 배경")
        'background'
        >>> classify_section("Executive Summary")
        'summary'
        >>> classify_section("향후 계획 및 제언")
        'conclusion'
    """
    title_lower = section_title.lower()

    # 요약 키워드
    summary_keywords = ["요약", "summary", "핵심", "개요", "executive"]
    if any(keyword in title_lower for keyword in summary_keywords):
        return "summary"

    # 결론 키워드 (배경/주요내용보다 먼저 체크)
    # "향후 추진 계획"처럼 "추진"(배경 키워드)과 "향후"(결론 키워드)를 모두 포함하는 경우,
    # 결론으로 분류되도록 순서를 앞으로 이동
    conclusion_keywords = ["결론", "제언", "conclusion", "향후", "계획", "시사점", "recommendation"]
    if any(keyword in title_lower for keyword in conclusion_keywords):
        return "conclusion"

    # 배경 키워드
    background_keywords = ["배경", "목적", "background", "추진", "사업", "필요성", "경위"]
    if any(keyword in title_lower for keyword in background_keywords):
        return "background"

    # 주요내용 키워드
    main_keywords = ["주요", "내용", "분석", "결과", "세부", "상세", "내역", "현황", "main", "detail", "analysis"]
    if any(keyword in title_lower for keyword in main_keywords):
        return "main_content"

    return "unknown"


def extract_title_from_markdown(md_text: str) -> str:
    """Markdown에서 제목만 추출 (간편 함수).

    Args:
        md_text: Markdown 텍스트

    Returns:
        추출된 제목 (없으면 "보고서")

    Examples:
        >>> md = "# 2025 디지털뱅킹 보고서\\n\\n내용..."
        >>> title = extract_title_from_markdown(md)
        >>> title
        '2025 디지털뱅킹 보고서'
    """
    title_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return "보고서"
