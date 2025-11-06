"""ConversionEngine 동작 검증."""

from __future__ import annotations

import textwrap
from pathlib import Path

from DesktopApp.src.converter.engine import ConversionEngine


class DummyHwp:
    """pyhwpx.Hwp 대체용 테스트 더블."""

    def __init__(self) -> None:
        self.font_calls: list[dict] = []
        self.para_calls: list[dict] = []
        self.inserted: list[str] = []
        self.break_count = 0
        self.visible = None
        self.cleared = 0
        self.saved_path: tuple[str, str] | None = None
        self.save_called = False
        self.quit_called = False
        self.table_calls: list[tuple[int, int, bool]] = []
        self.move_pos_calls: list[tuple[int, int, int]] = []
        self.table_right_calls = 0
        self.table_lower_calls = 0
        self.table_left_calls = 0

    # pyhwpx 인터페이스 모방 -----------------------
    def clear(self) -> None:
        self.cleared += 1

    def set_visible(self, visible: bool) -> None:
        self.visible = visible

    def set_font(self, **kwargs) -> bool:
        self.font_calls.append(kwargs)
        return True

    def set_para(self, **kwargs) -> bool:
        self.para_calls.append(kwargs)
        return True

    def insert_text(self, text: str) -> bool:
        self.inserted.append(text)
        return True

    def BreakPara(self) -> None:  # noqa: N802 - pyhwpx 메서드명 그대로 사용
        self.break_count += 1

    def save_as(self, path: str, format: str = "HWP") -> bool:
        self.saved_path = (path, format)
        return True

    def save(self, save_if_dirty: bool = True) -> bool:
        self.save_called = True
        return True

    def quit(self, save: bool = False) -> None:
        self.quit_called = True

    def create_table(self, rows: int, cols: int, treat_as_char: bool = True) -> bool:
        self.table_calls.append((rows, cols, treat_as_char))
        return True

    def MovePos(self, moveID: int = 1, Para: int = 0, pos: int = 0) -> bool:  # noqa: N802 - pyhwpx 메서드명 그대로 사용
        self.move_pos_calls.append((moveID, Para, pos))
        return True

    def TableRightCell(self) -> bool:
        self.table_right_calls += 1
        return True

    def TableLowerCell(self) -> bool:
        self.table_lower_calls += 1
        return True

    def TableLeftCell(self) -> bool:
        self.table_left_calls += 1
        return True


def test_convert_writes_sections(tmp_path: Path) -> None:
    """변환 시 제목/섹션 본문이 올바르게 처리되는지 확인한다."""
    md_text = textwrap.dedent(
        """
        # 테스트 리포트

        ## 핵심 요약

        - 첫 번째 항목
        - 두 번째 항목

        ## 주요 내용

        일반 문단 입니다.

        | 구분 | 값 |
        |------|----|
        | A | 1 |
        | B | 2 |

        ## 결론

        마무리 문단입니다.
        """
    ).strip()

    source_md = tmp_path / "sample.md"
    source_md.write_text(md_text, encoding="utf-8")

    dummy = DummyHwp()
    engine = ConversionEngine(hwp_factory=lambda: dummy)

    output_path = tmp_path / "result.hwpx"
    result = engine.convert(source_md, output_path)

    assert result == output_path
    assert dummy.saved_path == (str(output_path), "HWPX")
    assert dummy.quit_called is True

    # 제목 + 3개 섹션 제목 + 본문 단위 set_font 호출 여부
    assert dummy.font_calls[0]["Height"] == 20
    assert dummy.font_calls[0]["Bold"] is True
    assert any(call["Height"] == 16 for call in dummy.font_calls if call["Bold"] is True)
    assert any(call["Height"] == 11 for call in dummy.font_calls if call["Bold"] is False)

    # 텍스트 삽입 순서 확인
    assert dummy.inserted[0] == "테스트 리포트"
    assert dummy.inserted[1] == "핵심 요약"
    assert "• 첫 번째 항목" in dummy.inserted
    assert "구분" in dummy.inserted
    assert "값" in dummy.inserted
    assert "A" in dummy.inserted
    assert "2" in dummy.inserted

    # 표 생성 및 이동 호출 여부
    assert dummy.table_calls == [(3, 2, True)]
    assert dummy.table_right_calls == 3  # 3행 × (2열-1)
    assert dummy.table_lower_calls == 2  # (3행-1)
    assert dummy.table_left_calls == 2   # (3행-1) × (2열-1)
