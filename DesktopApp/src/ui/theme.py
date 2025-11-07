"""Utility helpers for applying Qt Material themes."""

from __future__ import annotations

import warnings
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QApplication

from DesktopApp.src.logging import app_logger

_THEME_APPLIED = False


def apply_material_theme(app: "QApplication", theme_name: Optional[str]) -> None:
    """Apply qt-material theme to the current application.

    Args:
        app: QApplication instance (must be created before calling this)
        theme_name: Theme name (e.g., 'dark_teal', 'dark_blue')

    Note:
        This function must be called AFTER QApplication is instantiated
        but BEFORE any widgets are created.
    """
    global _THEME_APPLIED

    if _THEME_APPLIED:
        app_logger.debug("테마가 이미 적용되어 있습니다. 스킵합니다.")
        return

    # Normalize theme name
    normalized = (theme_name or "dark_teal").strip()
    if not normalized:
        normalized = "dark_teal"
    if not normalized.endswith(".xml"):
        normalized = f"{normalized}.xml"

    # Suppress qt_material warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", message=".*qt_material.*")
        warnings.filterwarnings("ignore", message=".*QFontDatabase.*")

        try:
            # Import qt_material AFTER PyQt5 to avoid warnings
            import qt_material  # type: ignore

            # Apply stylesheet
            qt_material.apply_stylesheet(
                app,
                theme=normalized,
                invert_secondary=False,
                extra={
                    'font_family': 'Segoe UI, Roboto, Arial',
                    'danger': '#dc3545',
                    'warning': '#ffc107',
                    'success': '#28a745',
                }
            )  # type: ignore[misc]

            _THEME_APPLIED = True
            app_logger.info("Qt Material 테마 적용 완료: %s", normalized)

        except ImportError:
            app_logger.warning("qt-material 패키지가 설치되지 않았습니다. 기본 테마를 사용합니다.")
            _apply_fallback_theme(app)

        except Exception as exc:  # pragma: no cover
            app_logger.error("Qt Material 테마 적용 중 오류: %s", exc)
            app_logger.warning("기본 테마로 폴백합니다.")
            _apply_fallback_theme(app)


def _apply_fallback_theme(app: "QApplication") -> None:
    """Apply a simple fallback theme using Qt stylesheets."""
    stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: "Segoe UI", "Malgun Gothic", sans-serif;
        font-size: 9pt;
    }

    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 3px;
    }

    QPushButton:hover {
        background-color: #1084d8;
    }

    QPushButton:pressed {
        background-color: #006cbe;
    }

    QLineEdit, QTextEdit, QComboBox {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 3px;
        color: #ffffff;
    }

    QTableWidget {
        background-color: #2b2b2b;
        alternate-background-color: #333333;
        gridline-color: #555555;
    }

    QHeaderView::section {
        background-color: #3c3c3c;
        color: #ffffff;
        padding: 5px;
        border: 1px solid #555555;
    }
    """

    app.setStyleSheet(stylesheet)
    app_logger.info("기본 다크 테마 적용 완료")
