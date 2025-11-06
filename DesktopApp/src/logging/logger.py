"""Centralized logging utilities for the desktop application."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from DesktopApp.src.config import APP_DATA_DIR, LOG_MODE_OPERATIONAL, LOG_MODE_DEBUG


class LogMode:
    """Utility namespace for log mode strings."""

    OPERATIONAL = LOG_MODE_OPERATIONAL
    DEBUG = LOG_MODE_DEBUG


class AppLogger:
    """Wrapper around Python logging with operational/debug modes."""

    def __init__(self) -> None:
        self._log_dir = APP_DATA_DIR / "logs"
        self._log_dir.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger("DesktopApp")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        self._handler = RotatingFileHandler(
            filename=self._log_dir / "application.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        self._handler.setFormatter(formatter)
        self._logger.addHandler(self._handler)

        self._mode = LogMode.OPERATIONAL
        self.configure(self._mode)

    def configure(self, mode: str) -> None:
        """Change logging mode."""
        mode = mode.lower()
        if mode not in {LogMode.OPERATIONAL, LogMode.DEBUG}:
            mode = LogMode.OPERATIONAL
        self._mode = mode
        self.debug("로깅 모드가 '%s'로 설정되었습니다.", mode)

    def debug(self, msg: str, *args: object) -> None:
        """Log debug level messages when in debug mode."""
        if self._mode == LogMode.DEBUG:
            self._logger.debug(msg, *args)

    def info(self, msg: str, *args: object) -> None:
        """Log informational message depending on mode."""
        if self._mode == LogMode.DEBUG:
            self._logger.info(msg, *args)

    def warning(self, msg: str, *args: object) -> None:
        """Log warning messages. Always recorded in debug mode."""
        if self._mode == LogMode.DEBUG:
            self._logger.warning(msg, *args)

    def error(self, msg: str, *args: object) -> None:
        """Log errors regardless of mode."""
        self._logger.error(msg, *args)

    def exception(self, msg: str, *args: object) -> None:
        """Log exception information with traceback."""
        self._logger.exception(msg, *args)

    @property
    def mode(self) -> str:
        """Return current log mode."""
        return self._mode

    @property
    def log_file(self) -> Path:
        """Return current log file path."""
        return Path(self._handler.baseFilename)


app_logger = AppLogger()

