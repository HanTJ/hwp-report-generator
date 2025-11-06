"""개발 환경 구성을 점검하는 스크립트."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Iterable

CANDIDATE_PATHS: Iterable[Path] = (
    Path(r"C:\Program Files (x86)\Hnc\Office 2024\HOffice130\Bin\Hwp.exe"),
)


def ensure_modules() -> None:
    """필수 파이썬 모듈을 임포트하여 설치 여부를 확인한다."""

    os.environ.setdefault("QT_API", "pyqt5")

    try:
        import PyQt5  # noqa: F401
        from PyQt5 import QtWidgets  # noqa: F401
        from PyQt5 import QtGui  # noqa: F401
    except Exception as exc:
        print(f"[X] PyQt5 임포트 실패: {exc}")
        sys.exit(1)
    else:
        print("[O] 모듈 확인: PyQt5")

    try:
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        created = False
        if app is None:
            app = QApplication([])
            created = True
    except Exception as exc:
        print(f"[X] QApplication 생성 실패: {exc}")
        sys.exit(1)

    for name in ("pyhwpx", "win32com.client"):
        try:
            importlib.import_module(name)
        except ImportError as exc:
            print(f"[X] 모듈 로드 실패: {name} ({exc})")
            sys.exit(1)
        else:
            print(f"[O] 모듈 확인: {name}")

    try:
        import qt_material  # noqa: F401
    except ImportError as exc:
        print(f"[X] 모듈 로드 실패: qt_material ({exc})")
        sys.exit(1)
    else:
        print("[O] 모듈 확인: qt_material")

    if created:
        app.quit()


def detect_hwp() -> None:
    """한컴오피스 실행 파일 존재 여부를 확인한다."""
    for candidate in CANDIDATE_PATHS:
        if candidate.exists():
            print(f"[O] 한컴오피스 실행 파일 감지: {candidate}")
            return
    print("[X] 한컴오피스 2024 실행 파일을 찾지 못했습니다.")
    print("    - 기본 설치 경로에 한글 2024가 설치되어 있는지 확인하세요.")
    print("    - 다른 경로에 설치했다면 설정 창에서 경로를 직접 등록하세요.")
    sys.exit(1)


def main() -> None:
    ensure_modules()
    detect_hwp()
    print("[O] 로컬 개발 환경 점검 완료")


if __name__ == "__main__":
    main()
