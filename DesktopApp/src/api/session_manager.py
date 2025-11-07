"""세션 관련 정보를 저장하고 로드한다."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from DesktopApp.src.config import APP_DATA_DIR
from DesktopApp.src.logging import app_logger

SESSION_FILENAME = "session.json"


@dataclass
class SessionData:
    """세션 메타데이터 구조."""

    email: str = ""
    refresh_token: Optional[str] = None
    last_login_at: Optional[int] = None


class SessionManager:
    """세션 메타데이터를 관리한다."""

    def __init__(self, base_dir: Path = APP_DATA_DIR) -> None:
        self._session_path = base_dir / SESSION_FILENAME
        self._session_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> SessionData:
        """세션 정보를 로드한다."""
        if not self._session_path.exists():
            return SessionData()

        try:
            with self._session_path.open("r", encoding="utf-8") as fp:
                payload = json.load(fp)
            return SessionData(**payload)
        except (json.JSONDecodeError, TypeError) as exc:
            app_logger.error("세션 정보를 읽는 중 오류가 발생했습니다: %s", exc)
            return SessionData()

    def save(self, session: SessionData) -> None:
        """세션 정보를 저장한다."""
        payload = asdict(session)
        with self._session_path.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)
        app_logger.debug("세션 정보가 저장되었습니다: %s", payload)

    def update(self, email: Optional[str] = None, refresh_token: Optional[str] = None) -> SessionData:
        """세션 정보를 갱신하고 저장한다."""
        session = self.load()
        if email is not None:
            session.email = email
        if refresh_token is not None:
            session.refresh_token = refresh_token or None
        session.last_login_at = int(time.time())
        self.save(session)
        return session

