"""Application entry point."""

from __future__ import annotations

import sys
import warnings

# Suppress all warnings from qt_material
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*qt_material.*")
warnings.filterwarnings("ignore", message=".*QFontDatabase.*")

from PyQt5.QtWidgets import QApplication, QDialog

from DesktopApp.src.api.session_manager import SessionManager
from DesktopApp.src.api.token_manager import TokenManager
from DesktopApp.src.config import SettingsStore
from DesktopApp.src.logging import app_logger
from DesktopApp.src.ui.login_window import LoginWindow
from DesktopApp.src.ui.main_window import MainWindow
from DesktopApp.src.ui.theme import apply_material_theme


def bootstrap() -> int:
    """Initialize and run the PyQt application."""
    # Suppress Qt warnings
    import os
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.svg.warning=false'

    app = QApplication(sys.argv)

    settings_store = SettingsStore()
    settings = settings_store.load()
    session_manager = SessionManager()

    app_logger.configure(settings.log_mode)
    apply_material_theme(app, settings.material_theme)
    app_logger.info("애플리케이션을 시작합니다.")

    token_manager = TokenManager()

    if token_manager.ensure_valid_token(grace_seconds=0):
        app_logger.info("저장된 토큰으로 자동 로그인을 시도합니다.")
        window = MainWindow(
            token_manager=token_manager,
            settings_store=settings_store,
            session_manager=session_manager,
        )
        window.show()
        return app.exec_()

    login_dialog = LoginWindow(
        token_manager=token_manager,
        settings_store=settings_store,
        session_manager=session_manager,
    )
    result = login_dialog.exec_()
    if result == QDialog.Accepted:
        window = MainWindow(
            token_manager=token_manager,
            settings_store=settings_store,
            session_manager=session_manager,
        )
        window.show()
        return app.exec_()

    app_logger.warning("로그인에 실패하거나 취소하여 애플리케이션을 종료합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(bootstrap())
