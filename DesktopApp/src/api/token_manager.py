"""Persists JWT tokens securely for the desktop application."""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - Windows 전용 의존성
    import win32crypt  # type: ignore
    import pywintypes  # type: ignore

    PYWINTYPES_ERROR = pywintypes.error  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    win32crypt = None

    class PYWINTYPES_ERROR(Exception):
        """Fallback error when pywintypes is unavailable."""

        pass

from DesktopApp.src.config import APP_DATA_DIR
from DesktopApp.src.logging import app_logger

TOKEN_FILENAME = "token.json"


@dataclass
class TokenPayload:
    """Structure used for storing JWT token information."""

    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None

    @property
    def is_expired(self) -> bool:
        """Return True if the token has expired."""
        if self.expires_at is None:
            return False
        return self.expires_at <= int(time.time())


class TokenManager:
    """File-based token storage with optional Windows DPAPI encryption."""

    def __init__(self, base_dir: Path = APP_DATA_DIR) -> None:
        self._token_path = base_dir / TOKEN_FILENAME
        self._token_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Optional[TokenPayload]:
        """Load a token from disk."""
        if not self._token_path.exists():
            app_logger.debug("저장된 토큰 파일이 존재하지 않습니다.")
            return None

        try:
            with self._token_path.open("r", encoding="utf-8") as fp:
                wrapped = json.load(fp)
            payload_dict = self._decrypt_payload(wrapped["token"])
        except FileNotFoundError:
            app_logger.debug("토큰 파일이 삭제되었습니다.")
            return None
        except (KeyError, json.JSONDecodeError, ValueError) as exc:
            app_logger.error("토큰 파일을 읽는 중 오류가 발생했습니다: %s", exc)
            return None
        except PYWINTYPES_ERROR as exc:  # pragma: no cover
            app_logger.error("토큰 복호화에 실패했습니다: %s", exc)
            return None

        expires_at = payload_dict.get("expires_at")
        if expires_at is None:
            expires_at = self._extract_expiration(payload_dict.get("access_token", ""))
            if expires_at is not None:
                payload_dict["expires_at"] = expires_at
                self._persist_raw(payload_dict)

        app_logger.debug("토큰을 성공적으로 로드했습니다. 만료 시각: %s", expires_at)
        return TokenPayload(
            access_token=payload_dict["access_token"],
            refresh_token=payload_dict.get("refresh_token"),
            expires_at=int(expires_at) if expires_at is not None else None,
        )

    def save(self, token: TokenPayload) -> None:
        """Persist the given token to disk."""
        expires_at = token.expires_at or self._extract_expiration(token.access_token)
        payload = {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "expires_at": expires_at,
        }
        blob = self._encrypt_payload(payload)
        with self._token_path.open("w", encoding="utf-8") as fp:
            json.dump({"token": blob}, fp, ensure_ascii=False, indent=2)
        app_logger.info("토큰이 저장되었습니다.")

    def clear(self) -> None:
        """Remove any stored token."""
        if self._token_path.exists():
            self._token_path.unlink()
            app_logger.info("저장된 토큰을 삭제했습니다.")

    def has_valid_token(self) -> bool:
        """Return True when a non-expired token exists."""
        return self.ensure_valid_token(grace_seconds=0)

    def ensure_valid_token(self, grace_seconds: int = 0) -> bool:
        """Check whether a token exists and is not expired within grace seconds."""
        payload = self.load()
        if payload is None:
            return False
        if payload.is_expired:
            app_logger.warning("저장된 토큰이 만료되었습니다.")
            self.clear()
            return False
        if grace_seconds > 0 and payload.expires_at is not None:
            remaining = payload.expires_at - int(time.time())
            if remaining <= grace_seconds:
                app_logger.info("토큰이 곧 만료될 예정입니다. 남은 시간: %s초", remaining)
                return False
        return True

    def _encrypt_payload(self, payload: dict) -> str:
        """Encrypt payload using DPAPI when available."""
        raw = json.dumps(payload).encode("utf-8")
        if win32crypt is None:
            return base64.urlsafe_b64encode(raw).decode("utf-8")

        try:  # pragma: no cover - Windows DPAPI 전용
            encrypted = win32crypt.CryptProtectData(raw, None, None, None, None, 0)
            if isinstance(encrypted, tuple):
                encrypted_bytes = next(
                    (item for item in encrypted if isinstance(item, (bytes, bytearray))),
                    None,
                )
            else:
                encrypted_bytes = encrypted

            if not isinstance(encrypted_bytes, (bytes, bytearray)):
                raise ValueError("DPAPI 암호화 결과가 올바른 바이트가 아닙니다.")

            return base64.urlsafe_b64encode(encrypted_bytes).decode("utf-8")
        except Exception as exc:
            app_logger.error("DPAPI 암호화에 실패하여 평문 저장으로 폴백합니다: %s", exc)
            return base64.urlsafe_b64encode(raw).decode("utf-8")

    def _decrypt_payload(self, blob: str) -> dict:
        """Decrypt payload using DPAPI when available."""
        data = base64.urlsafe_b64decode(blob.encode("utf-8"))
        if win32crypt is None:
            raw = data
        else:
            try:  # pragma: no cover
                decrypted = win32crypt.CryptUnprotectData(data, None, None, None, 0)
                if isinstance(decrypted, tuple):
                    raw_bytes = next(
                        (item for item in decrypted if isinstance(item, (bytes, bytearray))),
                        None,
                    )
                else:
                    raw_bytes = decrypted
                if not isinstance(raw_bytes, (bytes, bytearray)):
                    raise ValueError("DPAPI 복호화 결과가 올바른 바이트가 아닙니다.")
                raw = raw_bytes
            except Exception as exc:
                app_logger.error("DPAPI 복호화에 실패하여 평문 복호화로 폴백합니다: %s", exc)
                raw = data

        return json.loads(raw.decode("utf-8"))

    def _extract_expiration(self, access_token: str) -> Optional[int]:
        """Extract expiration timestamp from JWT token."""
        if not access_token:
            return None
        parts = access_token.split(".")
        if len(parts) != 3:
            return None

        payload_part = parts[1]
        padding = "=" * (-len(payload_part) % 4)
        try:
            decoded = base64.urlsafe_b64decode(payload_part + padding)
            payload = json.loads(decoded.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return None
        exp = payload.get("exp")
        if isinstance(exp, int):
            return exp
        try:
            return int(exp)
        except (TypeError, ValueError):
            return None

    def _persist_raw(self, payload: dict) -> None:
        """Persist raw payload directly for backward compatibility."""
        blob = self._encrypt_payload(payload)
        with self._token_path.open("w", encoding="utf-8") as fp:
            json.dump({"token": blob}, fp, ensure_ascii=False, indent=2)

