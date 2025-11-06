"""MarkdownParser 동작 검증."""

from __future__ import annotations

import textwrap

from DesktopApp.src.converter.markdown_parser import MarkdownParser


def test_parse_basic_sections() -> None:
    """H1/H2 구조를 올바르게 파싱하는지 확인한다."""
    md_text = textwrap.dedent(
        """
        # 금융 산업 리포트

        ## 핵심 요약

        **은행권**은 2026년 순이익이 약 18.5조원으로 증가할 전망입니다.

        ## 추진 배경

        한컴오피스 2024 및 pyhwpx 기반의 자동화를 추진합니다.

        ## 주요 분석

        1. 시장 규모 확대
        2. 경쟁 심화

        ## 결론 및 제언

        향후 2년간 지속적인 모니터링이 필요합니다.
        """
    ).strip()

    parser = MarkdownParser()
    result = parser.parse(md_text)

    assert result.title == "금융 산업 리포트"
    sections = {section.role: section for section in result.sections}

    assert sections["summary"].title == "핵심 요약"
    assert "은행권은 2026년" in sections["summary"].content
    assert "**은행권**" in sections["summary"].raw_content
    assert sections["background"].title == "추진 배경"
    assert sections["main_content"].content.startswith("1. 시장 규모 확대")
    assert sections["conclusion"].content.endswith("필요합니다.")
