"""Main application window."""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, replace
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from DesktopApp.src.api import sample_data
from DesktopApp.src.api.client import APIClient, APIClientError, TokenExpiredError
from DesktopApp.src.api.dto import ArtifactDTO, TopicDTO
from DesktopApp.src.api.session_manager import SessionManager, SessionData
from DesktopApp.src.api.token_manager import TokenManager
from DesktopApp.src.config import AppSettings, SettingsStore
from DesktopApp.src.converter.engine import (
    ConversionEngine,
    ConversionError,
    InvalidMarkdownError,
    MissingDependencyError,
)
from DesktopApp.src.logging import app_logger
from DesktopApp.src.ui.login_window import LoginWindow
from DesktopApp.src.ui.progress_dialog import ProgressDialog
from DesktopApp.src.ui.settings_window import SettingsWindow
from DesktopApp.src.ui.theme import apply_material_theme

CHECKBOX_STYLE = """
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 3px;
    background-color: rgba(0, 0, 0, 0.2);
}
QCheckBox::indicator:hover {
    border: 1px solid #1abc9c;
}
QCheckBox::indicator:checked {
    background-color: #1abc9c;
    border: 1px solid #16a085;
}
QCheckBox::indicator:unchecked {
    background-color: rgba(0, 0, 0, 0.2);
}
"""


@dataclass(frozen=True)
class ArtifactPreview:
    """Phase 2 UI scaffold data for artifacts."""

    id: str
    title: str
    summary: str
    updated_at: str
    size_kb: int
    kind: str = ""
    locale: str = ""
    version: int = 1
    file_path: str = ""
    author: str = ""


@dataclass(frozen=True)
class TopicPreview:
    """Phase 2 UI scaffold data for topics."""

    id: str
    name: str
    description: str
    artifacts: List[ArtifactPreview]


class MainWindow(QMainWindow):
    """Container window for conversion workflow."""

    def __init__(
        self,
        parent=None,
        token_manager: TokenManager | None = None,
        settings_store: SettingsStore | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("HWPX Desktop Converter")
        self.resize(1024, 768)

        self._token_manager = token_manager or TokenManager()
        self._settings_store = settings_store or SettingsStore()
        self._session_manager = session_manager or SessionManager()
        self._session_grace_seconds = 120
        self._settings: AppSettings = self._settings_store.load()
        self._api_client = APIClient(
            settings_store=self._settings_store,
            token_manager=self._token_manager,
            session_manager=self._session_manager,
        )

        self._topics: Dict[str, TopicPreview] = {}
        self._selected_topic_id: Optional[str] = None
        self._is_populating_table = False
        self._using_sample_data = False
        self._session_timer: Optional[QTimer] = None
        self._conversion_engine = ConversionEngine()
        self._progress_dialog = ProgressDialog(self)

        self._build_menu()
        self._build_ui()
        self._bind_events()
        self._load_initial_state()
        self._start_session_timer()
        app_logger.info("메인 윈도우가 초기화되었습니다.")

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("설정")

        open_settings_action = QAction("환경 설정", self)
        open_settings_action.triggered.connect(self._open_settings_dialog)
        settings_menu.addAction(open_settings_action)

        logout_action = QAction("로그아웃", self)
        logout_action.triggered.connect(self._logout)
        settings_menu.addAction(logout_action)

    def _open_settings_dialog(self) -> None:
        dialog = SettingsWindow(self, settings_store=self._settings_store)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                self._settings = dialog.get_settings()
            except AttributeError:
                self._settings = self._settings_store.load()
            self._apply_settings_to_ui()
            app_logger.info("환경 설정이 적용되었습니다.")

    def _logout(self, *, confirm: bool = True) -> None:
        if confirm:
            confirm_result = QMessageBox.question(
                self,
                "로그아웃",
                "정말 로그아웃하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if confirm_result != QMessageBox.Yes:
                return

        if self._session_timer is not None:
            self._session_timer.stop()

        self._token_manager.clear()
        self._session_manager.save(SessionData())
        app_logger.info("사용자가 로그아웃했습니다.")

        login_dialog = LoginWindow(
            self,
            token_manager=self._token_manager,
            settings_store=self._settings_store,
            session_manager=self._session_manager,
        )

        if login_dialog.exec_() == QDialog.Accepted:
            self._settings = self._settings_store.load()
            self._load_initial_state()
            self._start_session_timer()
        else:
            self.close()

    def _build_ui(self) -> None:
        central_widget = QWidget(self)
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Topic"))

        self._topic_combo = QComboBox()
        self._topic_combo.setEditable(False)
        self._topic_combo.setMinimumWidth(260)
        filter_layout.addWidget(self._topic_combo)

        self._refresh_button = QPushButton("새로고침")
        filter_layout.addWidget(self._refresh_button)

        self._artifact_count_label = QLabel("0건")
        filter_layout.addWidget(self._artifact_count_label)
        filter_layout.addStretch()

        central_layout.addLayout(filter_layout)

        splitter = QSplitter(self)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        self._artifacts_table = QTableWidget(0, 4)
        self._artifacts_table.setHorizontalHeaderLabels(["선택", "제목", "최종 수정", "파일 크기"])
        self._artifacts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._artifacts_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._artifacts_table.setAlternatingRowColors(True)
        self._artifacts_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._artifacts_table.verticalHeader().setVisible(False)

        header: QHeaderView = self._artifacts_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        left_layout.addWidget(self._artifacts_table)
        left_panel.setLayout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Artifact 상세"))
        self._detail_view = QTextEdit()
        self._detail_view.setReadOnly(True)
        self._detail_view.setPlaceholderText("Artifact를 선택하면 요약 정보가 표시됩니다.")
        right_layout.addWidget(self._detail_view)
        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        central_layout.addWidget(splitter)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("출력 폴더"))
        self._output_path_input = QLineEdit()
        self._output_path_input.setReadOnly(True)
        output_layout.addWidget(self._output_path_input)
        self._browse_output_button = QPushButton("찾아보기")
        output_layout.addWidget(self._browse_output_button)
        central_layout.addLayout(output_layout)

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self._convert_button = QPushButton("선택 항목 변환 (HWPX)")
        self._convert_button.setEnabled(False)
        action_layout.addWidget(self._convert_button)
        self._download_button = QPushButton("선택 항목 다운로드")
        self._download_button.setEnabled(False)
        action_layout.addWidget(self._download_button)
        central_layout.addLayout(action_layout)

    def _bind_events(self) -> None:
        self._topic_combo.currentIndexChanged.connect(self._on_topic_changed)  # type: ignore[attr-defined]
        self._refresh_button.clicked.connect(self._on_refresh_clicked)  # type: ignore[attr-defined]
        self._artifacts_table.itemSelectionChanged.connect(self._update_detail_panel)  # type: ignore[attr-defined]
        self._artifacts_table.cellClicked.connect(self._on_cell_clicked)  # type: ignore[attr-defined]
        self._browse_output_button.clicked.connect(self._select_output_directory)  # type: ignore[attr-defined]
        self._convert_button.clicked.connect(self._handle_convert_clicked)  # type: ignore[attr-defined]
        self._download_button.clicked.connect(self._handle_download_clicked)  # type: ignore[attr-defined]

    def _load_initial_state(self) -> None:
        self._apply_settings_to_ui()
        self._refresh_topics(initial_load=True)

    def _apply_settings_to_ui(self) -> None:
        self._output_path_input.setText(self._settings.output_directory or "")
        app = QApplication.instance()
        if app is not None:
            apply_material_theme(app, self._settings.material_theme)

    def _start_session_timer(self) -> None:
        if self._session_timer is None:
            self._session_timer = QTimer(self)
            self._session_timer.setTimerType(Qt.VeryCoarseTimer)
            self._session_timer.timeout.connect(self._check_session_validity)  # type: ignore[attr-defined]

        if self._session_timer.isActive():
            self._session_timer.stop()

        # 체크 간격: 60초
        self._session_timer.start(60_000)
        app_logger.debug("세션 상태 점검 타이머를 시작했습니다.")

    def _check_session_validity(self) -> None:
        if self._token_manager.ensure_valid_token(grace_seconds=self._session_grace_seconds):
            return

        self._handle_session_expired()

    def _handle_session_expired(self) -> None:
        """세션 만료 시 재로그인을 유도한다."""
        if self._session_timer is not None:
            self._session_timer.stop()

        app_logger.warning("세션이 만료되었거나 토큰이 유효하지 않아 다시 로그인이 필요합니다.")
        QMessageBox.warning(
            self,
            "세션 만료",
            "로그인 세션이 만료되었습니다. 다시 로그인해 주세요.",
        )
        self._logout(confirm=False)

    def _show_error_dialog(self, title: str, message: str, detail: Optional[str] = None) -> None:
        """오류 메시지를 사용자에게 표시한다."""
        text = message if detail is None else f"{message}\n\n{detail}"
        QMessageBox.critical(self, title, text)

    def _clear_topics_ui(self) -> None:
        """Topic 관련 UI 컴포넌트를 초기화한다."""
        self._topic_combo.blockSignals(True)
        self._topic_combo.clear()
        self._topic_combo.addItem("Topic을 선택하세요", userData=None)
        self._topic_combo.blockSignals(False)
        self._selected_topic_id = None
        self._topics.clear()
        self._reset_artifacts_table()

    def _reset_artifacts_table(self) -> None:
        """Artifact 테이블과 상세 패널을 초기 상태로 되돌린다."""
        self._artifacts_table.clearContents()
        self._artifacts_table.setRowCount(0)
        self._artifact_count_label.setText("0건")
        self._detail_view.clear()
        self._detail_view.setPlaceholderText("Topic을 선택하면 Artifact 목록이 표시됩니다.")
        self._update_download_button_state()

    def _refresh_topics(self, *, initial_load: bool = False) -> None:
        try:
            topics = self._fetch_topics()
            self._using_sample_data = False
            self._update_download_button_state()
        except TokenExpiredError:
            self._handle_session_expired()
            return
        except APIClientError as exc:
            app_logger.error("Topic 목록을 불러오지 못했습니다: %s", exc)
            self._show_error_dialog(
                "Topic 불러오기 실패",
                "Topic 목록을 불러오는 중 오류가 발생했습니다. 네트워크 상태와 API URL을 확인해 주세요.",
                str(exc),
            )
            if not self._topics and self._try_show_sample_data():
                return
            if not self._topics:
                self._clear_topics_ui()
            return
        except Exception as exc:
            app_logger.exception("Topic 목록 처리 중 예기치 못한 오류가 발생했습니다.")
            self._show_error_dialog(
                "Topic 불러오기 실패",
                "Topic 목록을 불러오는 중 예기치 못한 오류가 발생했습니다.",
                str(exc),
            )
            if not self._topics and self._try_show_sample_data():
                return
            if not self._topics:
                self._clear_topics_ui()
            return

        self._topics = {topic.id: topic for topic in topics}
        self._populate_topics(list(self._topics.values()), auto_select_first=True)

        if initial_load:
            app_logger.info("Topic 목록을 불러왔습니다. (count=%s)", len(topics))
        else:
            app_logger.info("Topic 목록을 새로고침했습니다. (count=%s)", len(topics))

    def _fetch_topics(self) -> List[TopicPreview]:
        """백엔드에서 Topic 목록을 받아온다."""
        page = self._api_client.get_topics(status="active", page=1, page_size=50)
        return [self._build_topic_preview(item) for item in page.topics]

    def _try_show_sample_data(self) -> bool:
        """API 실패 시 샘플 데이터를 로드해 UI를 구성한다."""
        sample_topics = self._load_sample_topics()
        if not sample_topics:
            return False
        self._using_sample_data = True
        self._update_download_button_state()
        self._topics = {topic.id: topic for topic in sample_topics}
        self._populate_topics(list(self._topics.values()), auto_select_first=True)
        QMessageBox.information(
            self,
            "데모 데이터 표시",
            "API 연결에 실패해 데모 데이터를 표시합니다.\n네트워크 설정을 확인한 뒤 다시 새로고침해 주세요.",
        )
        app_logger.info("API 연결 실패로 데모 데이터를 표시합니다. (count=%s)", len(sample_topics))
        return True

    def _load_sample_topics(self) -> List[TopicPreview]:
        """샘플 Topic/Artifact 데이터를 TopicPreview 형태로 변환해 반환한다."""
        sample_page = sample_data.sample_topics_page()
        topics: List[TopicPreview] = []
        for topic_dto in sample_page.topics:
            preview = self._build_topic_preview(topic_dto)
            artifact_page = sample_data.sample_artifacts(topic_dto.id)
            artifact_previews = [self._build_artifact_preview(item) for item in artifact_page.artifacts]
            topics.append(replace(preview, artifacts=artifact_previews))
        return topics

    def _build_topic_preview(self, dto: TopicDTO) -> TopicPreview:
        """API DTO를 TopicPreview 객체로 변환한다."""
        title_source = (dto.generated_title or dto.input_prompt or "").strip()
        name = title_source or f"Topic #{dto.id}"
        description = (dto.input_prompt or "설명이 없습니다.").strip()
        return TopicPreview(id=str(dto.id), name=name, description=description, artifacts=[])

    def _populate_topics(self, topics: List[TopicPreview], *, auto_select_first: bool) -> None:
        self._topic_combo.blockSignals(True)
        self._topic_combo.clear()
        self._topic_combo.addItem("Topic을 선택하세요", userData=None)
        for topic in topics[:10]:
            self._topic_combo.addItem(topic.name, userData=topic.id)
        self._topic_combo.blockSignals(False)

        if auto_select_first and topics:
            self._topic_combo.setCurrentIndex(1)
            self._on_topic_changed(1)
        else:
            self._selected_topic_id = None
            self._populate_artifacts(None)

    def _populate_artifacts(self, topic_id: Optional[str]) -> None:
        self._is_populating_table = True
        self._artifacts_table.clearContents()
        self._artifacts_table.setRowCount(0)

        if topic_id is None or topic_id not in self._topics:
            self._reset_artifacts_table()
            self._is_populating_table = False
            return

        try:
            topic = self._ensure_topic_artifacts(topic_id)
        except TokenExpiredError:
            self._is_populating_table = False
            self._handle_session_expired()
            return
        except APIClientError as exc:
            self._is_populating_table = False
            app_logger.error("Artifact 목록을 불러오지 못했습니다 (topic_id=%s): %s", topic_id, exc)
            self._show_error_dialog(
                "Artifact 불러오기 실패",
                "Artifact 목록을 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
                str(exc),
            )
            self._reset_artifacts_table()
            return
        except Exception as exc:
            self._is_populating_table = False
            app_logger.exception("Artifact 목록 처리 중 예기치 못한 오류가 발생했습니다 (topic_id=%s).", topic_id)
            self._show_error_dialog(
                "Artifact 불러오기 실패",
                "Artifact 목록을 불러오는 중 예기치 못한 오류가 발생했습니다.",
                str(exc),
            )
            self._reset_artifacts_table()
            return

        artifacts = topic.artifacts
        self._artifacts_table.setRowCount(len(artifacts))

        for row, artifact in enumerate(artifacts):
            checkbox = QCheckBox()
            checkbox.setStyleSheet(CHECKBOX_STYLE)
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(partial(self._on_checkbox_state_changed, row))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)
            layout.addWidget(checkbox)
            self._artifacts_table.setCellWidget(row, 0, container)

            title_item = QTableWidgetItem(artifact.title)
            title_item.setData(Qt.UserRole, artifact)
            self._artifacts_table.setItem(row, 1, title_item)

            updated_item = QTableWidgetItem(artifact.updated_at)
            self._artifacts_table.setItem(row, 2, updated_item)

            size_item = QTableWidgetItem(f"{artifact.size_kb:,} KB")
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._artifacts_table.setItem(row, 3, size_item)

        self._artifact_count_label.setText(f"{len(artifacts)}건")
        self._is_populating_table = False
        self._artifacts_table.clearSelection()
        detail_message = (
            f"[{topic.name}]\n{topic.description}\n\nArtifact를 선택하면 요약 정보가 표시됩니다."
            if artifacts
            else f"[{topic.name}]\n{topic.description}\n\n다운로드 가능한 Artifact가 없습니다."
        )
        self._detail_view.setPlainText(detail_message)
        self._update_download_button_state()

    def _ensure_topic_artifacts(self, topic_id: str) -> TopicPreview:
        """Topic 캐시를 확인하고 필요 시 Artifact를 로드한다."""
        topic = self._topics[topic_id]
        if topic.artifacts:
            return topic

        artifacts = self._fetch_artifacts(topic_id)
        updated_topic = replace(topic, artifacts=artifacts)
        self._topics[topic_id] = updated_topic
        return updated_topic

    def _fetch_artifacts(self, topic_id: str) -> List[ArtifactPreview]:
        """백엔드에서 Artifact 목록을 조회한다."""
        try:
            numeric_id = int(topic_id)
        except ValueError as exc:
            raise APIClientError("유효하지 않은 Topic ID입니다.") from exc

        result = self._api_client.get_artifacts_by_topic(
            numeric_id,
            kind="md",
            page=1,
            page_size=100,
        )
        return [self._build_artifact_preview(item) for item in result.artifacts]

    def _build_artifact_preview(self, dto: ArtifactDTO) -> ArtifactPreview:
        """API DTO를 ArtifactPreview로 변환한다."""
        filename = (dto.filename or f"artifact-{dto.id}").strip()
        size_int = max(dto.file_size, 0)
        size_kb = max(1, (size_int + 1023) // 1024) if size_int else 0

        raw_kind = dto.kind or ""
        locale = dto.locale or ""
        version = dto.version or 1
        file_path = dto.file_path or ""

        summary = " | ".join(
            [
                f"종류: {(raw_kind or '-').upper()}",
                f"언어: {locale or '-'}",
                f"버전: v{version if version else '-'}",
            ]
        )

        return ArtifactPreview(
            id=str(dto.id),
            title=filename,
            summary=summary,
            updated_at=self._format_timestamp(dto.created_at),
            size_kb=size_kb,
            kind=raw_kind,
            locale=locale,
            version=version,
            file_path=file_path,
        )

    def _format_timestamp(self, value: str) -> str:
        """ISO8601 문자열을 표시용 문자열로 변환한다."""
        if not value:
            return "-"

        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            app_logger.debug("날짜 문자열 파싱에 실패했습니다: %s", value)
            return value
        return parsed.strftime("%Y-%m-%d %H:%M")

    def _sanitize_filename(self, filename: str, fallback: str) -> str:
        """파일 시스템에 안전한 파일 이름을 생성한다."""
        candidate = (filename or "").strip()
        if not candidate:
            candidate = fallback

        sanitized = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", candidate)
        sanitized = re.sub(r"_+", "_", sanitized).strip()
        return sanitized or fallback

    def _ensure_unique_filepath(self, base_dir: Path, filename: str) -> Path:
        """중복되지 않는 파일 경로를 반환한다."""
        candidate = base_dir / filename
        if not candidate.exists():
            return candidate

        stem = candidate.stem or "artifact"
        suffix = candidate.suffix
        counter = 1

        while True:
            candidate = base_dir / f"{stem} ({counter}){suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _checkbox_at(self, row: int) -> Optional[QCheckBox]:
        widget = self._artifacts_table.cellWidget(row, 0)
        if widget is None:
            return None
        if isinstance(widget, QCheckBox):
            return widget
        return widget.findChild(QCheckBox)

    def _collect_selected_artifacts(self) -> List[Tuple[int, ArtifactPreview]]:
        """체크된 Artifact 목록을 반환한다."""
        selected: List[Tuple[int, ArtifactPreview]] = []
        for row in range(self._artifacts_table.rowCount()):
            checkbox = self._checkbox_at(row)
            if checkbox is None or not checkbox.isChecked():
                continue
            artifact = self._get_artifact_by_row(row)
            if artifact is not None:
                selected.append((row, artifact))
        return selected

    def _resolve_output_directory(self) -> Optional[Path]:
        """출력 폴더를 확인하고 경로 객체를 반환한다."""
        output_dir_value = (self._settings.output_directory or "").strip()
        if not output_dir_value:
            self._show_error_dialog(
                "출력 폴더 필요",
                "파일을 저장할 폴더가 설정되어 있지 않습니다.",
                "우측 상단의 출력 폴더 선택 버튼을 사용해 저장 위치를 먼저 지정해 주세요.",
            )
            return None

        output_dir = Path(output_dir_value).expanduser()
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            app_logger.error("출력 폴더를 생성/사용할 수 없습니다: %s", exc)
            self._show_error_dialog(
                "출력 폴더 오류",
                "선택한 출력 폴더에 접근할 수 없습니다. 다른 경로를 선택해 주세요.",
                str(exc),
            )
            return None
        return output_dir

    def _on_topic_changed(self, index: int) -> None:
        topic_id = self._topic_combo.itemData(index)
        self._selected_topic_id = str(topic_id) if topic_id is not None else None
        self._populate_artifacts(self._selected_topic_id)

    def _on_refresh_clicked(self) -> None:
        app_logger.debug("Topic 새로고침을 실행합니다.")
        self._refresh_topics()

    def _on_cell_clicked(self, row: int, column: int) -> None:
        if column != 0:
            return
        checkbox = self._checkbox_at(row)
        if checkbox is None:
            return
        if not checkbox.rect().contains(checkbox.mapFromGlobal(QCursor.pos())):
            checkbox.toggle()

    def _on_checkbox_state_changed(self, row: int, state: int) -> None:
        if self._is_populating_table:
            return
        self._update_download_button_state()

    def _update_download_button_state(self) -> None:
        any_checked = any(
            (checkbox := self._checkbox_at(row)) is not None and checkbox.isChecked()
            for row in range(self._artifacts_table.rowCount())
        )
        self._download_button.setEnabled(any_checked and not self._using_sample_data)
        self._convert_button.setEnabled(any_checked and not self._using_sample_data)

    def _get_artifact_by_row(self, row: int) -> Optional[ArtifactPreview]:
        title_item = self._artifacts_table.item(row, 1)
        if title_item is None:
            return None
        artifact = title_item.data(Qt.UserRole)
        if isinstance(artifact, ArtifactPreview):
            return artifact
        return None

    def _update_detail_panel(self) -> None:
        selected_rows = {index.row() for index in self._artifacts_table.selectionModel().selectedRows()}
        if not selected_rows:
            if self._selected_topic_id and self._selected_topic_id in self._topics:
                topic = self._topics[self._selected_topic_id]
                self._detail_view.setPlainText(
                    f"[{topic.name}]\n{topic.description}\n\nArtifact를 선택하면 요약 정보가 표시됩니다."
                )
            else:
                self._detail_view.clear()
            return

        row = min(selected_rows)
        artifact = self._get_artifact_by_row(row)
        if artifact is None:
            self._detail_view.clear()
            return

        detail_lines = [
            f"제목: {artifact.title}",
            f"작성자: {artifact.author or '미상'}",
            f"최종 수정: {artifact.updated_at}",
            f"파일 크기: {artifact.size_kb:,} KB",
            "",
            "요약",
            artifact.summary.strip() or "(요약 정보 없음)",
        ]
        self._detail_view.setPlainText("\n".join(detail_lines))

    def _select_output_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "출력 폴더 선택", self._output_path_input.text())
        if not directory:
            return

        self._output_path_input.setText(directory)
        self._settings = AppSettings(
            api_base_url=self._settings.api_base_url,
            hwp_executable_path=self._settings.hwp_executable_path,
            output_directory=directory,
            log_mode=self._settings.log_mode,
            material_theme=self._settings.material_theme,
        )
        self._settings_store.save(self._settings)
        app_logger.info("출력 폴더가 업데이트되었습니다: %s", directory)

    def _handle_download_clicked(self) -> None:
        if self._using_sample_data:
            QMessageBox.information(
                self,
                "데모 데이터",
                "데모 데이터는 다운로드할 수 없습니다.\nAPI 연결을 복구한 후 새로고침해 주세요.",
            )
            return

        selected_items = self._collect_selected_artifacts()

        if not selected_items:
            QMessageBox.information(
                self,
                "선택된 항목 없음",
                "다운로드할 Markdown 아티팩트를 선택해 주세요.",
            )
            return

        output_dir = self._resolve_output_directory()
        if output_dir is None:
            return

        saved_files: List[Path] = []
        failures: List[Tuple[ArtifactPreview, str]] = []
        checkboxes_to_clear: List[QCheckBox] = []
        session_expired = False

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            for row, artifact in selected_items:
                checkbox = self._checkbox_at(row)
                try:
                    artifact_id = int(artifact.id)
                except (TypeError, ValueError):
                    reason = "유효하지 않은 Artifact ID입니다."
                    failures.append((artifact, reason))
                    app_logger.error("잘못된 Artifact ID(%s)로 인해 다운로드를 건너뜁니다.", artifact.id)
                    continue

                try:
                    content = self._api_client.get_artifact_content(artifact_id)
                except TokenExpiredError:
                    app_logger.warning("토큰 만료로 인해 다운로드를 중단합니다 (artifact_id=%s).", artifact_id)
                    session_expired = True
                    break
                except APIClientError as exc:
                    app_logger.error("Markdown 콘텐츠 조회 실패 (artifact_id=%s): %s", artifact_id, exc)
                    failures.append((artifact, str(exc)))
                    continue
                except Exception as exc:
                    app_logger.exception("Markdown 다운로드 중 예기치 못한 오류가 발생했습니다 (artifact_id=%s).", artifact_id)
                    failures.append((artifact, str(exc)))
                    continue

                sanitized_name = self._sanitize_filename(content.filename, f"artifact-{content.artifact_id}.md")
                candidate = Path(sanitized_name)
                if candidate.suffix.lower() != ".md":
                    sanitized_name = f"{candidate.stem or sanitized_name}.md"

                target_path = self._ensure_unique_filepath(output_dir, sanitized_name)

                try:
                    target_path.write_text(content.content, encoding="utf-8")
                except OSError as exc:
                    app_logger.error("Markdown 파일 저장 실패 (%s): %s", target_path, exc)
                    failures.append((artifact, f"파일 저장 실패: {exc}"))
                    continue

                app_logger.info("Markdown 아티팩트를 저장했습니다: %s", target_path)
                saved_files.append(target_path)
                if checkbox is not None:
                    checkboxes_to_clear.append(checkbox)
        finally:
            QApplication.restoreOverrideCursor()

        if session_expired:
            self._update_download_button_state()
            self._handle_session_expired()
            return

        if checkboxes_to_clear:
            self._is_populating_table = True
            try:
                for checkbox in checkboxes_to_clear:
                    checkbox.setChecked(False)
            finally:
                self._is_populating_table = False

        self._artifacts_table.clearSelection()
        self._update_download_button_state()

        if saved_files and not failures:
            QMessageBox.information(
                self,
                "다운로드 완료",
                f"{len(saved_files)}개의 Markdown 파일을 저장했습니다.\n\n저장 위치: {output_dir}",
            )
            return

        if saved_files and failures:
            detail_lines = "\n".join(f"- {item.title}: {reason}" for item, reason in failures)
            self._show_error_dialog(
                "일부 다운로드 실패",
                f"{len(saved_files)}개는 저장했지만 {len(failures)}개 파일에서 오류가 발생했습니다.",
                detail_lines,
            )
            return

        detail_lines = "\n".join(f"- {item.title}: {reason}" for item, reason in failures) if failures else None
        self._show_error_dialog(
            "다운로드 실패",
            "선택한 Markdown 아티팩트를 저장하지 못했습니다.",
            detail_lines,
        )

    def _handle_convert_clicked(self) -> None:
        if self._using_sample_data:
            QMessageBox.information(
                self,
                "데모 데이터",
                "데모 데이터는 변환할 수 없습니다.\nAPI 연결을 복구한 후 새로고침해 주세요.",
            )
            return

        selected_items = self._collect_selected_artifacts()
        if not selected_items:
            QMessageBox.information(
                self,
                "선택된 항목 없음",
                "변환할 Markdown 아티팩트를 선택해 주세요.",
            )
            return

        output_dir = self._resolve_output_directory()
        if output_dir is None:
            return

        total = len(selected_items)
        saved_files: List[Path] = []
        failures: List[Tuple[ArtifactPreview, str]] = []
        checkboxes_to_clear: List[QCheckBox] = []
        session_expired = False
        cancelled = False

        self._progress_dialog.start(total)
        self._progress_dialog.show()
        QApplication.processEvents()

        try:
            with tempfile.TemporaryDirectory(prefix="hwpx_convert_") as temp_dir:
                temp_dir_path = Path(temp_dir)
                for index, (row, artifact) in enumerate(selected_items, start=1):
                    if self._progress_dialog.is_cancelled():
                        cancelled = True
                        break

                    display_title = artifact.title or f"artifact-{artifact.id}"
                    status_prefix = f"[{index}/{total}] {display_title}"
                    self._progress_dialog.update_progress(index - 1, f"{status_prefix} 다운로드 중…")
                    QApplication.processEvents()

                    checkbox = self._checkbox_at(row)

                    try:
                        artifact_id = int(artifact.id)
                    except (TypeError, ValueError):
                        reason = "유효하지 않은 Artifact ID입니다."
                        failures.append((artifact, reason))
                        app_logger.error("잘못된 Artifact ID(%s)로 인해 변환을 건너뜁니다.", artifact.id)
                        continue

                    try:
                        content = self._api_client.get_artifact_content(artifact_id)
                    except TokenExpiredError:
                        app_logger.warning("토큰 만료로 인해 변환 작업을 중단합니다 (artifact_id=%s).", artifact_id)
                        session_expired = True
                        break
                    except APIClientError as exc:
                        app_logger.error("Markdown 콘텐츠 조회 실패 (artifact_id=%s): %s", artifact_id, exc)
                        failures.append((artifact, str(exc)))
                        continue
                    except Exception as exc:  # pragma: no cover - 예외 추적 목적
                        app_logger.exception("Markdown 조회 중 예기치 못한 오류가 발생했습니다 (artifact_id=%s).", artifact_id)
                        failures.append((artifact, str(exc)))
                        continue

                    sanitized_name = self._sanitize_filename(
                        content.filename,
                        f"artifact-{content.artifact_id}.md",
                    )
                    temp_md_path = temp_dir_path / sanitized_name
                    try:
                        temp_md_path.write_text(content.content, encoding="utf-8")
                    except OSError as exc:
                        app_logger.error("임시 Markdown 파일 작성 실패 (%s): %s", temp_md_path, exc)
                        failures.append((artifact, f"임시 파일 저장 실패: {exc}"))
                        continue

                    target_name = Path(sanitized_name).with_suffix(".hwpx").name
                    target_path = self._ensure_unique_filepath(output_dir, target_name)

                    self._progress_dialog.update_progress(index - 1, f"{status_prefix} 변환 중…")
                    QApplication.processEvents()

                    try:
                        self._conversion_engine.convert(temp_md_path, target_path)
                    except MissingDependencyError as exc:
                        self._progress_dialog.hide()
                        self._show_error_dialog(
                            "pyhwpx 미설치",
                            "pyhwpx 모듈이 설치되어 있지 않아 변환을 실행할 수 없습니다.",
                            str(exc),
                        )
                        return
                    except InvalidMarkdownError as exc:
                        failures.append((artifact, str(exc)))
                        app_logger.warning("Markdown 파싱 실패 (artifact_id=%s): %s", artifact_id, exc)
                        continue
                    except ConversionError as exc:
                        failures.append((artifact, str(exc)))
                        app_logger.error("HWPX 변환 실패 (artifact_id=%s): %s", artifact_id, exc)
                        continue
                    except Exception as exc:  # pragma: no cover - 예외 추적 목적
                        failures.append((artifact, str(exc)))
                        app_logger.exception("HWPX 변환 중 예기치 못한 오류가 발생했습니다 (artifact_id=%s).", artifact_id)
                        continue

                    saved_files.append(target_path)
                    if checkbox is not None:
                        checkboxes_to_clear.append(checkbox)

                    self._progress_dialog.update_progress(index, f"{status_prefix} 변환 완료")
                    QApplication.processEvents()

            if not session_expired and not cancelled:
                self._progress_dialog.mark_complete("변환 작업이 완료되었습니다.")
                QApplication.processEvents()
        finally:
            self._progress_dialog.hide()

        if session_expired:
            self._update_download_button_state()
            self._handle_session_expired()
            return

        if cancelled:
            app_logger.info("사용자가 변환 작업을 취소했습니다.")
            if saved_files or failures:
                detail_lines = "\n".join(f"- {item.title}: {reason}" for item, reason in failures) if failures else ""
                QMessageBox.information(
                    self,
                    "변환 취소",
                    "사용자가 변환을 취소했습니다.\n완료된 항목과 실패한 항목을 확인해 주세요.",
                )
                if detail_lines:
                    app_logger.debug("취소 시 실패 내역: %s", detail_lines)
            return

        if checkboxes_to_clear:
            self._is_populating_table = True
            try:
                for checkbox in checkboxes_to_clear:
                    checkbox.setChecked(False)
            finally:
                self._is_populating_table = False

        self._artifacts_table.clearSelection()
        self._update_download_button_state()

        app_logger.info(
            "HWPX 변환 작업 결과 - 성공: %s건, 실패: %s건",
            len(saved_files),
            len(failures),
        )

        if saved_files and not failures:
            QMessageBox.information(
                self,
                "변환 완료",
                f"{len(saved_files)}개의 HWPX 파일을 생성했습니다.\n\n저장 위치: {output_dir}",
            )
            return

        if saved_files and failures:
            detail_lines = "\n".join(f"- {item.title}: {reason}" for item, reason in failures)
            self._show_error_dialog(
                "일부 변환 실패",
                f"{len(saved_files)}개는 성공했지만 {len(failures)}개 항목에서 오류가 발생했습니다.",
                detail_lines,
            )
            return

        detail_lines = "\n".join(f"- {item.title}: {reason}" for item, reason in failures) if failures else None
        self._show_error_dialog(
            "변환 실패",
            "선택한 Markdown 아티팩트를 HWPX로 변환하지 못했습니다.",
            detail_lines,
        )
