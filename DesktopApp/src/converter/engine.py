"""pyhwpx 기반 Markdown → HWPX 변환 엔진."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING

from DesktopApp.src.converter.markdown_parser import MarkdownParser, ParsedSection
from DesktopApp.src.logging import app_logger

if TYPE_CHECKING:  # pragma: no cover
    from pyhwpx import Hwp  # type: ignore


class ConversionError(Exception):
    """변환 과정에서 발생한 일반적인 오류."""


class MissingDependencyError(ConversionError):
    """pyhwpx 또는 필수 구성 요소가 누락된 경우 발생."""


class InvalidMarkdownError(ConversionError):
    """파싱 가능한 콘텐츠가 없는 경우 발생."""


@dataclass(frozen=True)
class SectionStyle:
    """섹션별 서식 설정."""

    font_size: float
    bold: bool
    indent_mm: float
    line_spacing: int
    prev_spacing_pt: float = 0.0
    next_spacing_pt: float = 0.0


TITLE_STYLE = SectionStyle(font_size=20, bold=True, indent_mm=0.0, line_spacing=160, next_spacing_pt=12)
SUBTITLE_STYLE = SectionStyle(font_size=16, bold=True, indent_mm=0.0, line_spacing=160, next_spacing_pt=6)
BODY_STYLE = SectionStyle(font_size=11, bold=False, indent_mm=5.0, line_spacing=160, prev_spacing_pt=2)
TABLE_HEADER_STYLE = SectionStyle(font_size=11, bold=True, indent_mm=0.0, line_spacing=160)
TABLE_BODY_STYLE = SectionStyle(font_size=11, bold=False, indent_mm=0.0, line_spacing=160)


class ConversionEngine:
    """pyhwpx 엔진을 사용한 Markdown → HWPX 변환 래퍼."""

    def __init__(
        self,
        *,
        parser: Optional[MarkdownParser] = None,
        hwp_factory: Optional[Callable[[], "Hwp"]] = None,
        visible: bool = False,
    ) -> None:
        self._parser = parser or MarkdownParser()
        self._visible = visible
        self._hwp_factory = hwp_factory

    def convert(self, markdown_path: Path, output_path: Path) -> Path:
        """Markdown 파일을 HWPX로 변환한다."""
        if not markdown_path.exists():
            raise ConversionError(f"Markdown 파일을 찾을 수 없습니다: {markdown_path}")

        raw_text = markdown_path.read_text(encoding="utf-8")
        parsed = self._parser.parse(raw_text)

        if not parsed.sections:
            raise InvalidMarkdownError("변환 가능한 섹션이 없습니다. Markdown 구조를 확인하세요.")

        output_path = self._ensure_output_path(output_path)

        try:
            hwp = self._create_hwp_instance()
        except MissingDependencyError:
            raise
        except Exception as exc:  # pragma: no cover - pyhwpx 환경 의존
            app_logger.exception("pyhwpx 초기화 중 오류가 발생했습니다.")
            raise ConversionError(f"pyhwpx 초기화에 실패했습니다: {exc}") from exc

        try:
            self._prepare_document(hwp)
            self._write_title(hwp, parsed)
            for section in parsed.sections:
                self._write_section(hwp, section)
            self._finalize_document(hwp, output_path)
            app_logger.info("Markdown 변환이 완료되었습니다: %s", output_path)
        except ConversionError:
            raise
        except Exception as exc:  # pragma: no cover - pyhwpx 환경 의존
            app_logger.exception("HWPX 변환 중 예외가 발생했습니다.")
            raise ConversionError(f"문서를 변환하는 동안 오류가 발생했습니다: {exc}") from exc
        finally:
            self._shutdown_hwp(hwp)

        return output_path

    # --- pyhwpx 초기화/정리 -------------------------------------------------

    def _create_hwp_instance(self) -> "Hwp":
        if self._hwp_factory is not None:
            return self._hwp_factory()

        try:
            from pyhwpx import Hwp  # type: ignore
        except ImportError as exc:  # pragma: no cover
            message = "pyhwpx 모듈이 설치되어 있지 않습니다. 'pip install pyhwpx' 후 다시 시도하세요."
            app_logger.error(message)
            raise MissingDependencyError(message) from exc

        hwp = Hwp(new=True, visible=self._visible)
        hwp.clear()  # 빈 문서 상태로 초기화
        return hwp

    def _shutdown_hwp(self, hwp: "Hwp") -> None:  # pragma: no cover - pyhwpx 환경 의존
        try:
            hwp.save(False)
        except Exception:
            pass
        try:
            hwp.quit(save=False)
        except Exception:
            pass

    # --- 문서 준비/저장 -----------------------------------------------------

    def _prepare_document(self, hwp: "Hwp") -> None:
        hwp.set_visible(self._visible)
        hwp.clear()

    def _finalize_document(self, hwp: "Hwp", output_path: Path) -> None:
        saved = hwp.save_as(str(output_path), format="HWPX")
        if not saved:
            raise ConversionError("HWPX 파일 저장에 실패했습니다.")

    # --- 작성 로직 ----------------------------------------------------------

    def _write_title(self, hwp: "Hwp", parsed: ParsedMarkdown) -> None:
        if not parsed.title:
            return
        self._apply_style(hwp, TITLE_STYLE)
        hwp.insert_text(parsed.title)
        self._break_para(hwp, count=2)

    def _write_section(self, hwp: "Hwp", section: ParsedSection) -> None:
        self._apply_style(hwp, SUBTITLE_STYLE)
        hwp.insert_text(section.title)
        self._break_para(hwp)

        paragraphs = [chunk for chunk in section.content.split("\n\n") if chunk.strip()]
        if not paragraphs:
            self._break_para(hwp)
            return

        for index, paragraph in enumerate(paragraphs):
            trimmed = paragraph.strip()
            if self._is_table_block(trimmed):
                header, rows = self._parse_table_block(trimmed)
                if header or rows:
                    self._write_table(hwp, header, rows)
                    continue

            lines = paragraph.splitlines()
            bullet_mode = self._is_bullet(lines[0] if lines else "")
            self._apply_style(hwp, BODY_STYLE, bullet_mode=bullet_mode)
            for line_idx, line in enumerate(lines):
                if line_idx:
                    self._break_para(hwp)
                text = line.rstrip()
                if text:
                    hwp.insert_text(text)
            self._break_para(hwp)
            if index < len(paragraphs) - 1:
                self._break_para(hwp)

    # --- 서식/헬퍼 ----------------------------------------------------------

    def _is_table_block(self, block: str) -> bool:
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            return False
        if "|" not in lines[0]:
            return False
        for line in lines[1:]:
            stripped = line.strip().replace(" ", "")
            if stripped and set(stripped) <= {"|", "-", ":"}:
                return True
            if "|" not in line:
                break
        return False

    def _parse_table_block(self, block: str) -> Tuple[List[str], List[List[str]]]:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            return [], []

        separator_index = -1
        for idx, line in enumerate(lines[1:], start=1):
            stripped = line.replace(" ", "")
            if stripped and set(stripped) <= {"|", "-", ":"}:
                separator_index = idx
                break

        if separator_index == -1:
            return [], []

        header = self._split_table_row(lines[0])
        body_lines = lines[separator_index + 1 :]
        rows = [self._split_table_row(line) for line in body_lines]
        return header, rows

    @staticmethod
    def _split_table_row(line: str) -> List[str]:
        parts = [cell.strip() for cell in line.strip().strip("|").split("|")]
        return [part for part in parts]

    def _write_table(self, hwp: "Hwp", header: List[str], rows: List[List[str]]) -> None:
        all_rows: List[List[str]] = []
        if header:
            all_rows.append(header)
        all_rows.extend(rows)
        if not all_rows:
            return

        column_count = max(len(row) for row in all_rows)
        normalized_rows = [row + [""] * (column_count - len(row)) for row in all_rows]

        hwp.create_table(len(normalized_rows), column_count, treat_as_char=True)
        hwp.MovePos(104)

        for row_index, row in enumerate(normalized_rows):
            for col_index, cell in enumerate(row):
                is_header = bool(header) and row_index == 0
                style = TABLE_HEADER_STYLE if is_header else TABLE_BODY_STYLE
                self._apply_style(hwp, style, bullet_mode=False)

                text = cell.strip()
                if text:
                    hwp.insert_text(text)

                if col_index < column_count - 1:
                    hwp.TableRightCell()

            if row_index < len(normalized_rows) - 1:
                hwp.TableLowerCell()
                for _ in range(column_count - 1):
                    hwp.TableLeftCell()

        hwp.MovePos(3)
        self._break_para(hwp)

    def _apply_style(self, hwp: "Hwp", style: SectionStyle, *, bullet_mode: bool = False) -> None:
        indent_mm = 0.0 if bullet_mode else style.indent_mm
        hwp.set_font(
            FaceName="맑은 고딕",
            Height=style.font_size,
            Bold=style.bold,
        )
        hwp.set_para(
            AlignType="Left",
            LineSpacing=style.line_spacing,
            Indentation=self._points_for_para(self._mm_to_points(indent_mm)),
            PrevSpacing=self._points_for_para(style.prev_spacing_pt),
            NextSpacing=self._points_for_para(style.next_spacing_pt),
        )

    @staticmethod
    def _points_for_para(points: float) -> float:
        if points <= 0:
            return 0.0
        return round(points / 2.0, 2)

    @staticmethod
    def _break_para(hwp: "Hwp", *, count: int = 1) -> None:
        for _ in range(max(1, count)):
            hwp.BreakPara()

    @staticmethod
    def _is_bullet(text: str) -> bool:
        stripped = text.lstrip()
        if not stripped:
            return False
        if stripped.startswith("• "):
            return True
        for prefix in ("- ", "* ", "+ "):
            if stripped.startswith(prefix):
                return True
        number_part = stripped.split(".", 1)
        if len(number_part) == 2 and number_part[0].isdigit():
            return True
        return False

    @staticmethod
    def _ensure_output_path(output_path: Path) -> Path:
        output_path = output_path.with_suffix(".hwpx")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    @staticmethod
    def _mm_to_points(mm: float) -> float:
        if mm <= 0:
            return 0.0
        return mm * 72.0 / 25.4
