"""PyQt dialog that handles user login."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from DesktopApp.src.api.client import APIClient, APIClientError
from DesktopApp.src.api.session_manager import SessionManager
from DesktopApp.src.api.token_manager import TokenManager
from DesktopApp.src.config import SettingsStore
from DesktopApp.src.logging import app_logger
from DesktopApp.src.ui.settings_window import SettingsWindow


class LoginWindow(QDialog):
    """Dialog that authenticates the user and stores JWT tokens."""

    def __init__(
        self,
        parent=None,
        token_manager: TokenManager | None = None,
        settings_store: SettingsStore | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("HWPX Desktop Converter - 로그인")
        self._token_manager = token_manager or TokenManager()
        self._settings_store = settings_store or SettingsStore()
        self._session_manager = session_manager or SessionManager()
        self._api_client = APIClient(
            settings_store=self._settings_store,
            token_manager=self._token_manager,
            session_manager=self._session_manager,
        )
        self._build_ui()
        self._bind_events()
        self._load_session_defaults()

    def _build_ui(self) -> None:
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("이메일")

        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setPlaceholderText("비밀번호")

        form_layout = QFormLayout()
        form_layout.addRow("이메일", self._email_input)
        form_layout.addRow("비밀번호", self._password_input)

        self._login_button = QPushButton("로그인")
        self._settings_button = QPushButton("환경 설정")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self._settings_button)
        button_layout.addStretch()
        button_layout.addWidget(self._login_button)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _bind_events(self) -> None:
        self._login_button.clicked.connect(self._handle_login)  # type: ignore[attr-defined]
        self._settings_button.clicked.connect(self._open_settings)  # type: ignore[attr-defined]

    def _load_session_defaults(self) -> None:
        session = self._session_manager.load()
        if session.email:
            self._email_input.setText(session.email)
            self._password_input.setFocus()

    def _open_settings(self) -> None:
        dialog = SettingsWindow(self, settings_store=self._settings_store)
        dialog.exec_()

    def _handle_login(self) -> None:
        email = self._email_input.text().strip()
        password = self._password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "입력 오류", "이메일과 비밀번호를 모두 입력해 주세요.")
            return

        try:
            self._api_client.login(email=email, password=password)
        except APIClientError as exc:
            app_logger.error("로그인 실패: %s", exc)
            QMessageBox.critical(
                self,
                "로그인 실패",
                f"로그인에 실패했습니다.\n{exc}",
            )
            return

        QMessageBox.information(self, "로그인", "로그인에 성공했습니다.")
        self.accept()
