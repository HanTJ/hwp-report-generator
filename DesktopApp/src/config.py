"""애플리케이션 설정 및 저장소 유틸리티."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict

APP_NAME = "HWPConverter"
APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / APP_NAME
SETTINGS_FILENAME = "settings.json"

LOG_MODE_OPERATIONAL = "operational"
LOG_MODE_DEBUG = "debug"
VALID_LOG_MODES = {LOG_MODE_OPERATIONAL, LOG_MODE_DEBUG}
DEFAULT_MATERIAL_THEME = "dark_teal"


@dataclass
class AppSettings:
    """로컬 환경 설정 정보를 보관한다."""

    api_base_url: str = "http://localhost:8000"
    hwp_executable_path: str = "C:\Program Files (x86)\Hnc\Office 2024\HOffice130\Bin\Hwp.exe"
    output_directory: str = str(Path.home() / "Documents" / "HWPX")
    log_mode: str = LOG_MODE_OPERATIONAL
    material_theme: str = DEFAULT_MATERIAL_THEME


class SettingsStore:
    """설정 파일을 로드/저장하는 저장소."""

    def __init__(self, base_dir: Path = APP_DATA_DIR) -> None:
        self._base_dir = base_dir
        self._settings_path = self._base_dir / SETTINGS_FILENAME
        self._ensure_base_dir()

    def _ensure_base_dir(self) -> None:
        """설정 파일 디렉터리가 존재하도록 보장한다."""
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppSettings:
        """저장된 설정을 불러온다."""
        if not self._settings_path.exists():
            return AppSettings()

        with self._settings_path.open("r", encoding="utf-8") as fp:
            payload: Dict[str, Any] = json.load(fp)

        defaults = AppSettings()
        merged = {**defaults.__dict__, **payload}
        settings = AppSettings(**merged)
        if settings.log_mode not in VALID_LOG_MODES:
            settings.log_mode = LOG_MODE_OPERATIONAL
        if not settings.material_theme:
            settings.material_theme = DEFAULT_MATERIAL_THEME
        settings.material_theme = settings.material_theme.replace(".xml", "")
        return settings

    def save(self, settings: AppSettings) -> None:
        """설정 데이터를 저장한다."""
        payload = asdict(settings)
        if payload.get("log_mode") not in VALID_LOG_MODES:
            payload["log_mode"] = LOG_MODE_OPERATIONAL
        theme_value = str(payload.get("material_theme") or DEFAULT_MATERIAL_THEME)
        payload["material_theme"] = theme_value.replace(".xml", "")

        with self._settings_path.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)
