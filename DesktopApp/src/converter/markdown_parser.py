"""Markdown 파서 구현.

백엔드의 Markdown → HWP 변환 로직을 데스크톱 앱용으로 경량 이식한다.
pyhwpx 변환 엔진이 기대하는 섹션(요약·배경·주요 내용·결론) 단위로 Markdown을
정리하고, 텍스트 내 Markdown 마크업을 제거해 HWPX에 삽입 가능한 평문으로 가공한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union


@dataclass(frozen=True)
class ParsedSection:
    """섹션 제목과 내용을 보관한다."""

    role: str
    title: str
    content: str
    raw_content: str


@dataclass(frozen=True)
class ParsedMarkdown:
    """변환 엔진이 사용하는 Markdown 파싱 결과."""

    title: str
    sections: List[ParsedSection]
    raw_text: str

    def as_content_dict(self) -> Dict[str, str]:
        """백엔드와 동일한 content dict 형태로 반환한다."""
        mapping = {
            "title": self.title,
            "summary": "",
            "background": "",
            "main_content": "",
            "conclusion": "",
            "title_summary": "요약",
            "title_background": "배경 및 목적",
            "title_main_content": "주요 내용",
            "title_conclusion": "결론 및 제언",
        }

        for section in self.sections:
            key_map = {
                "summary": ("title_summary", "summary"),
                "background": ("title_background", "background"),
                "main_content": ("title_main_content", "main_content"),
                "conclusion": ("title_conclusion", "conclusion"),
            }
            if section.role in key_map:
                title_key, content_key = key_map[section.role]
                mapping[title_key] = section.title
                mapping[content_key] = section.content

        return mapping


class MarkdownParser:
    """Markdown 문서를 파싱하여 pyhwpx에 전달 가능한 구조로 변환한다."""

    def parse(self, source: Union[Path, str]) -> ParsedMarkdown:
        """Markdown 내용을 파싱한다.

        Args:
            source: Markdown 파일 경로 또는 Markdown 문자열

        Returns:
            ParsedMarkdown: 제목과 섹션별 평문이 포함된 파싱 결과.
        """
        if isinstance(source, Path):
            raw_text = source.read_text(encoding="utf-8")
        else:
            raw_text = source

        content_dict = parse_markdown_to_content(raw_text)
        payloads = extract_section_payloads(raw_text)
        role_to_payload = {}
        for payload in payloads:
            role_to_payload.setdefault(payload.role, payload)

        def build_section(role: str, title_key: str, content_key: str) -> ParsedSection:
            payload = role_to_payload.get(role)
            raw_body = payload.raw if payload else content_dict[content_key]
            return ParsedSection(
                role=role,
                title=content_dict[title_key],
                content=content_dict[content_key],
                raw_content=raw_body,
            )

        sections = [
            build_section("summary", "title_summary", "summary"),
            build_section("background", "title_background", "background"),
            build_section("main_content", "title_main_content", "main_content"),
            build_section("conclusion", "title_conclusion", "conclusion"),
        ]

        # 내용이 없는 섹션은 제외
        filtered_sections = [section for section in sections if section.content.strip()]

        return ParsedMarkdown(
            title=content_dict["title"],
            sections=filtered_sections,
            raw_text=raw_text,
        )


def markdown_to_plain_text(md_text: str) -> str:
    """Markdown 문법을 제거하고 평문으로 변환한다."""
    text = md_text

    # H3~H6 헤더 마커 제거
    header_patterns = (
        r"^######\s+(.+)$",
        r"^#####\s+(.+)$",
        r"^####\s+(.+)$",
        r"^###\s+(.+)$",
    )
    for pattern in header_patterns:
        text = re.sub(pattern, r"\1", text, flags=re.MULTILINE)

    # 굵게 + 기울임, 굵게, 기울임
    emphasis_patterns: Iterable[Tuple[str, str]] = (
        (r"\*\*\*(.+?)\*\*\*", r"\1"),
        (r"___(.+?)___", r"\1"),
        (r"\*\*(.+?)\*\*", r"\1"),
        (r"__(.+?)__", r"\1"),
        (r"\*(.+?)\*", r"\1"),
        (r"(?<!\w)_(.+?)_(?!\w)", r"\1"),
    )
    for pattern, replacement in emphasis_patterns:
        text = re.sub(pattern, replacement, text)

    # 취소선, 인라인 코드
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)

    # 링크와 이미지
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"[이미지: \1]", text)

    # 리스트 마커
    text = re.sub(r"^[\s]*[-\*\+]\s+", "• ", text, flags=re.MULTILINE)

    # 인용, 수평선
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s]*[-\*_]{3,}[\s]*$", "", text, flags=re.MULTILINE)

    # 문단 들여쓰기
    paragraphs = text.split("\n\n")
    indented: List[str] = []
    for para in paragraphs:
        stripped = para.strip()
        if not stripped:
            continue
        if not re.match(r"^\d+\.", stripped) and not stripped.startswith("•"):
            para = f"  {stripped}"
        else:
            para = stripped
        indented.append(para)
    return "\n\n".join(indented).strip()


def parse_markdown_to_content(md_text: str) -> Dict[str, str]:
    """Markdown 텍스트를 섹션별 평문 dict로 변환한다."""
    content = {
        "title": "",
        "summary": "",
        "background": "",
        "main_content": "",
        "conclusion": "",
        "title_summary": "요약",
        "title_background": "배경 및 목적",
        "title_main_content": "주요 내용",
        "title_conclusion": "결론 및 제언",
    }

    title_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    if title_match:
        content["title"] = title_match.group(1).strip()

    payloads = extract_section_payloads(md_text)
    for payload in payloads:
        if payload.role == "summary":
            content["title_summary"] = payload.title
            content["summary"] = payload.plain
        elif payload.role == "background":
            content["title_background"] = payload.title
            content["background"] = payload.plain
        elif payload.role == "main_content":
            content["title_main_content"] = payload.title
            content["main_content"] = payload.plain
        elif payload.role == "conclusion":
            content["title_conclusion"] = payload.title
            content["conclusion"] = payload.plain

    if not any(
        (
            content["summary"],
            content["background"],
            content["main_content"],
            content["conclusion"],
        )
    ):
        if title_match:
            raw_body = md_text[title_match.end() :].strip()
        else:
            raw_body = md_text.strip()
        content["main_content"] = markdown_to_plain_text(raw_body)

    return content


def extract_all_h2_sections(md_text: str) -> List[Tuple[str, str]]:
    """Markdown에서 H2 섹션을 추출한다."""
    pattern = r"^##\s+(.+?)\s*$\n+(.*?)(?=\n+^##\s|\Z)"
    matches = re.findall(pattern, md_text, re.MULTILINE | re.DOTALL)
    return [
        (title.strip(), markdown_to_plain_text(body.strip()))
        for title, body in matches
    ]


def extract_section_payloads(md_text: str) -> List[SectionPayload]:
    """H2 섹션을 파싱해 서식 정보를 유지한다."""
    pattern = r"^##\s+(.+?)\s*$\n+(.*?)(?=\n+^##\s|\Z)"
    matches = re.findall(pattern, md_text, re.MULTILINE | re.DOTALL)
    payloads: List[SectionPayload] = []
    for title, body in matches:
        cleaned_title = title.strip()
        raw_body = body.strip()
        plain_body = markdown_to_plain_text(raw_body)
        role = classify_section(cleaned_title)
        payloads.append(
            SectionPayload(
                role=role,
                title=cleaned_title,
                plain=plain_body,
                raw=raw_body,
            )
        )
    return payloads


def classify_section(section_title: str) -> str:
    """H2 제목을 기반으로 섹션 타입을 추론한다."""
    lowered = section_title.lower()

    summary_keywords = ("요약", "summary", "핵심", "개요", "executive")
    if any(keyword in lowered for keyword in summary_keywords):
        return "summary"

    conclusion_keywords = ("결론", "제언", "conclusion", "향후", "계획", "시사점", "recommendation")
    if any(keyword in lowered for keyword in conclusion_keywords):
        return "conclusion"

    background_keywords = ("배경", "목적", "background", "추진", "사업", "필요성", "경위")
    if any(keyword in lowered for keyword in background_keywords):
        return "background"

    main_keywords = ("주요", "내용", "분석", "결과", "세부", "상세", "내역", "현황", "main", "detail", "analysis")
    if any(keyword in lowered for keyword in main_keywords):
        return "main_content"

    return "unknown"


def extract_title_from_markdown(md_text: str) -> str:
    """Markdown 본문에서 제목(H1)을 추출한다."""
    match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "보고서"
@dataclass(frozen=True)
class SectionPayload:
    """H2 섹션에서 추출한 페이로드."""

    role: str
    title: str
    plain: str
    raw: str
