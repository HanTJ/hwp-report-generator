"""변환 진행 상태를 표시하는 다이얼로그."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
)


class ProgressDialog(QDialog):
    """변환 진행률과 메시지를 표시하는 다이얼로그."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("변환 진행 중")
        self.setModal(True)
        self._cancelled = False

        self._message_label = QLabel("", self)
        self._progress_bar = QProgressBar(self)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(0)

        self._cancel_button = QPushButton("취소", self)
        self._cancel_button.clicked.connect(self._on_cancel)  # type: ignore[attr-defined]

        layout = QVBoxLayout()
        layout.addWidget(self._message_label)
        layout.addWidget(self._progress_bar)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self._cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def start(self, total: int) -> None:
        """진행률을 초기화한다."""
        maximum = max(int(total), 1)
        self._progress_bar.setRange(0, maximum)
        self._progress_bar.setValue(0)
        self._message_label.clear()
        self._cancelled = False
        self._cancel_button.setEnabled(True)

    def update_progress(self, value: int, message: Optional[str] = None) -> None:
        """현재 진행 상태와 메시지를 갱신한다."""
        clamped = max(0, min(value, self._progress_bar.maximum()))
        self._progress_bar.setValue(clamped)
        if message:
            self._message_label.setText(message)

    def mark_complete(self, message: Optional[str] = None) -> None:
        """작업 완료 상태로 표시한다."""
        self._progress_bar.setValue(self._progress_bar.maximum())
        if message:
            self._message_label.setText(message)
        self._cancel_button.setEnabled(False)

    def is_cancelled(self) -> bool:
        """사용자가 취소를 요청했는지 여부."""
        return self._cancelled

    def _on_cancel(self) -> None:
        self._cancelled = True
        self._cancel_button.setEnabled(False)
        self._message_label.setText("작업을 취소하는 중입니다…")
