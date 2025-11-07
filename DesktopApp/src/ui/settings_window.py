"""Settings dialog for configuring API URL, paths, log mode, and material theme."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from DesktopApp.src.config import (
    AppSettings,
    LOG_MODE_DEBUG,
    LOG_MODE_OPERATIONAL,
    SettingsStore,
)
from DesktopApp.src.logging import app_logger
from DesktopApp.src.ui.theme import apply_material_theme

# _sorted_theme_names 내부에서 qt_material.list_themes 를 지연 임포트한다.

LOG_MODE_LABELS = {
    LOG_MODE_OPERATIONAL: "운영 (오류 중심)",
    LOG_MODE_DEBUG: "디버그 (상세 로그)",
}


class SettingsWindow(QDialog):
    """Dialog for editing API URL, paths, logging mode, and material theme."""

    def __init__(self, parent=None, settings_store: SettingsStore | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("환경 설정")
        self.setModal(True)

        self._store = settings_store or SettingsStore()
        self._settings = self._store.load()

        self._build_ui()
        self._bind_events()
        self._load_values()

    def _build_ui(self) -> None:
        self._api_url_input = QLineEdit()
        self._hwp_path_input = QLineEdit()
        self._output_path_input = QLineEdit()
        self._log_mode_combo = QComboBox()
        self._theme_combo = QComboBox()

        for value, label in LOG_MODE_LABELS.items():
            self._log_mode_combo.addItem(label, userData=value)

        for theme_name in self._sorted_theme_names():
            label = theme_name.replace("_", " ").title()
            self._theme_combo.addItem(label, userData=theme_name)

        browse_hwp_button = QPushButton("찾아보기")
        browse_output_button = QPushButton("폴더 선택")

        form_layout = QFormLayout()
        form_layout.addRow("API URL", self._api_url_input)

        hwp_layout = QHBoxLayout()
        hwp_layout.addWidget(self._hwp_path_input)
        hwp_layout.addWidget(browse_hwp_button)
        form_layout.addRow(QLabel("한컴오피스 실행 파일"), hwp_layout)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self._output_path_input)
        output_layout.addWidget(browse_output_button)
        form_layout.addRow(QLabel("출력 폴더"), output_layout)

        form_layout.addRow("로그 기록 구분", self._log_mode_combo)
        form_layout.addRow("Material 테마", self._theme_combo)

        self._save_button = QPushButton("저장")
        self._cancel_button = QPushButton("취소")

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        action_layout.addWidget(self._save_button)
        action_layout.addWidget(self._cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(action_layout)
        self.setLayout(layout)

        self._browse_hwp_button = browse_hwp_button
        self._browse_output_button = browse_output_button

    def _bind_events(self) -> None:
        self._browse_hwp_button.clicked.connect(self._select_hwp_executable)  # type: ignore[attr-defined]
        self._browse_output_button.clicked.connect(self._select_output_directory)  # type: ignore[attr-defined]
        self._log_mode_combo.currentIndexChanged.connect(self._preview_log_mode_change)  # type: ignore[attr-defined]
        self._theme_combo.currentIndexChanged.connect(self._preview_theme_change)  # type: ignore[attr-defined]
        self._save_button.clicked.connect(self._handle_save)  # type: ignore[attr-defined]
        self._cancel_button.clicked.connect(self.reject)  # type: ignore[attr-defined]

    def _load_values(self) -> None:
        self._api_url_input.setText(self._settings.api_base_url)
        self._hwp_path_input.setText(self._settings.hwp_executable_path)
        self._output_path_input.setText(self._settings.output_directory)

        log_mode_index = self._log_mode_combo.findData(self._settings.log_mode)
        if log_mode_index == -1:
            log_mode_index = self._log_mode_combo.findData(LOG_MODE_OPERATIONAL)
        self._log_mode_combo.setCurrentIndex(log_mode_index)

        theme_index = self._theme_combo.findData(self._settings.material_theme)
        if theme_index == -1:
            theme_index = 0
        self._theme_combo.setCurrentIndex(theme_index)

    def _select_hwp_executable(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "한컴오피스 실행 파일 선택", "", "실행 파일 (*.exe)")
        if file_path:
            self._hwp_path_input.setText(file_path)
            app_logger.debug("한컴오피스 실행 파일 경로 선택: %s", file_path)

    def _select_output_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if directory:
            self._output_path_input.setText(directory)
            app_logger.debug("출력 폴더 선택: %s", directory)

    def _preview_log_mode_change(self) -> None:
        selected_mode = self._log_mode_combo.currentData()
        if selected_mode in LOG_MODE_LABELS:
            app_logger.configure(selected_mode)
            app_logger.info("로그 모드 미리보기 적용: %s", selected_mode)

    def _preview_theme_change(self) -> None:
        theme = self._theme_combo.currentData()
        if isinstance(theme, str) and theme:
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                apply_material_theme(app, theme)

    def _handle_save(self) -> None:
        if not self._validate():
            return

        output_dir_str = self._output_path_input.text().strip()

        self._settings = AppSettings(
            api_base_url=self._api_url_input.text().strip(),
            hwp_executable_path=self._hwp_path_input.text().strip(),
            output_directory=output_dir_str,
            log_mode=self._log_mode_combo.currentData(),
            material_theme=self._theme_combo.currentData(),
        )

        if output_dir_str:
            Path(output_dir_str).mkdir(parents=True, exist_ok=True)

        self._store.save(self._settings)
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            apply_material_theme(app, self._settings.material_theme)
        app_logger.configure(self._settings.log_mode)
        app_logger.info(
            "환경 설정이 저장되었습니다. (로그 모드: %s, 테마: %s)",
            self._settings.log_mode,
            self._settings.material_theme,
        )
        self.accept()

    def get_settings(self) -> AppSettings:
        """Return last saved settings."""
        return self._settings

    def _validate(self) -> bool:
        api_url = self._api_url_input.text().strip()
        hwp_path_str = self._hwp_path_input.text().strip()
        output_dir_str = self._output_path_input.text().strip()
        hwp_path = Path(hwp_path_str) if hwp_path_str else None
        output_dir = Path(output_dir_str) if output_dir_str else None

        if not api_url:
            QMessageBox.warning(self, "검증 실패", "API URL을 입력해 주세요.")
            return False

        parsed = urlparse(api_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            QMessageBox.warning(self, "검증 실패", "올바른 형태의 API URL을 입력해 주세요.")
            return False

        if hwp_path and (not hwp_path.exists() or hwp_path.suffix.lower() != ".exe"):
            QMessageBox.warning(self, "검증 실패", "한컴오피스 실행 파일(.exe)을 정확히 선택해 주세요.")
            return False

        if output_dir and not output_dir.exists():
            create_dir = QMessageBox.question(
                self,
                "출력 폴더 생성",
                f"출력 폴더가 존재하지 않습니다.\n{output_dir}\n생성하시겠습니까?",
            )
            if create_dir == QMessageBox.Yes:
                output_dir.mkdir(parents=True, exist_ok=True)
                app_logger.debug("출력 폴더 생성: %s", output_dir)
            else:
                return False
        return True

    @staticmethod
    def _sorted_theme_names() -> list[str]:
        from qt_material import list_themes  # 지연 임포트

        themes: list[str] = []
        for name in list_themes():
            clean_name = name.replace(".xml", "")
            themes.append(clean_name)
        themes.sort()
        return themes
