"""HTTP client for communicating with the FastAPI backend."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from requests import Response
from requests.exceptions import RequestException

from DesktopApp.src.api.dto import (
    ArtifactContentDTO,
    ArtifactDTO,
    ArtifactListDTO,
    TopicDTO,
    TopicsPage,
)
from DesktopApp.src.api.session_manager import SessionManager
from DesktopApp.src.api.token_manager import TokenManager, TokenPayload
from DesktopApp.src.config import AppSettings, SettingsStore
from DesktopApp.src.logging import app_logger


class APIClientError(Exception):
    """Raised when a backend API call fails."""

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        http_status: Optional[int] = None,
        hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.hint = hint
        self.details = details


class TokenExpiredError(APIClientError):
    """Raised when an API call is attempted with an expired token."""


@dataclass
class AuthResponse:
    """Represents a successful authentication response."""

    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None


class APIClient:
    """HTTP client wrapper that respects application settings."""

    def __init__(
        self,
        settings_store: Optional[SettingsStore] = None,
        token_manager: Optional[TokenManager] = None,
        session_manager: Optional[SessionManager] = None,
    ) -> None:
        self._settings_store = settings_store or SettingsStore()
        self._token_manager = token_manager or TokenManager()
        self._session_manager = session_manager or SessionManager()
        self._settings = self._settings_store.load()

    @property
    def base_url(self) -> str:
        """Return sanitized API base URL."""
        return self._settings.api_base_url.rstrip("/")

    def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate and persist the returned JWT."""
        url = f"{self.base_url}/api/auth/login"
        app_logger.debug("POST %s (로그인)", url)
        try:
            response = requests.post(
                url,
                json={"email": email, "password": password},
                timeout=30,
            )
        except RequestException as exc:
            app_logger.error("로그인 요청 중 네트워크 오류 발생: %s", exc)
            raise APIClientError(f"로그인 요청 실패: {exc}") from exc

        data = self._handle_response(response)
        if not isinstance(data, dict) or "access_token" not in data:
            app_logger.error("로그인 응답에 access_token이 없습니다: %s", data)
            raise APIClientError("로그인 응답에 access_token이 없습니다.")

        payload = AuthResponse(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
        )

        expires_at = None
        if payload.expires_in:
            try:
                expires_at = int(time.time()) + int(payload.expires_in)
            except (TypeError, ValueError):
                app_logger.warning("expires_in 값을 파싱하지 못했습니다: %s", payload.expires_in)
                expires_at = None

        self._token_manager.save(
            TokenPayload(
                access_token=payload.access_token,
                refresh_token=payload.refresh_token,
                expires_at=expires_at,
            )
        )
        self._session_manager.update(email=email, refresh_token=payload.refresh_token)
        app_logger.info("로그인 요청이 성공적으로 처리되었습니다.")
        return payload

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Perform an authenticated GET request."""
        url = f"{self.base_url}{path}"
        headers = self._authorized_headers()
        app_logger.debug("GET %s params=%s", url, params)
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )
        except RequestException as exc:
            app_logger.error("GET 요청 중 네트워크 오류가 발생했습니다: %s", exc)
            raise APIClientError(f"GET 요청 실패: {exc}") from exc
        return self._handle_response(response)

    def refresh_settings(self, settings: AppSettings) -> None:
        """Persist changed settings and refresh client state."""
        self._settings = settings
        self._settings_store.save(settings)
        app_logger.info("API 클라이언트 설정이 갱신되었습니다.")

    def get_topics(
        self,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TopicsPage:
        """현재 사용자 Topic 목록을 조회한다."""
        safe_page = page if page > 0 else 1
        safe_page_size = min(max(page_size, 1), 100)
        params: Dict[str, Any] = {"page": safe_page, "page_size": safe_page_size}
        if status:
            params["status"] = status

        payload = self.get("/api/topics", params=params)
        return self._parse_topics_page(payload)

    def get_artifacts_by_topic(
        self,
        topic_id: int,
        *,
        kind: Optional[str] = None,
        locale: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> ArtifactListDTO:
        """특정 Topic의 Artifact 목록을 조회한다."""
        safe_page = page if page > 0 else 1
        safe_page_size = min(max(page_size, 1), 100)
        params: Dict[str, Any] = {"page": safe_page, "page_size": safe_page_size}
        if kind:
            params["kind"] = kind
        if locale:
            params["locale"] = locale

        payload = self.get(f"/api/artifacts/topics/{topic_id}", params=params)
        return self._parse_artifact_list(payload)

    def get_artifact_content(self, artifact_id: int) -> ArtifactContentDTO:
        """Markdown 아티팩트 콘텐츠를 조회한다."""
        try:
            numeric_id = int(artifact_id)
        except (TypeError, ValueError) as exc:
            raise APIClientError("유효하지 않은 Artifact ID입니다.") from exc

        if numeric_id <= 0:
            raise APIClientError("Artifact ID는 양수여야 합니다.")

        data = self.get(f"/api/artifacts/{numeric_id}/content")
        if not isinstance(data, dict):
            app_logger.error("Artifact 콘텐츠 응답 형식이 잘못되었습니다: %s", data)
            raise APIClientError("Artifact 콘텐츠 응답 형식이 올바르지 않습니다.")

        content = data.get("content")
        filename = data.get("filename")
        kind = data.get("kind")

        if not isinstance(content, str):
            raise APIClientError("Artifact 콘텐츠 데이터가 문자열이 아닙니다.")

        resolved_filename = str(filename or f"artifact-{numeric_id}.md")
        resolved_kind = str(kind or "").lower() or "md"
        if resolved_kind != "md":
            raise APIClientError("Markdown 아티팩트만 다운로드할 수 있습니다.")

        return ArtifactContentDTO(
            artifact_id=numeric_id,
            filename=resolved_filename,
            content=content,
            kind=resolved_kind,
        )

    def _authorized_headers(self) -> Dict[str, str]:
        """Return Authorization header if token is valid."""
        if not self._token_manager.ensure_valid_token(grace_seconds=0):
            app_logger.warning("토큰이 만료되어 Authorization 헤더를 생성할 수 없습니다.")
            raise TokenExpiredError(
                "토큰이 만료되었습니다. 다시 로그인해 주세요.",
                code="AUTH.TOKEN_EXPIRED",
            )

        token = self._token_manager.load()
        if token is None:
            app_logger.warning("토큰을 로드하지 못했습니다.")
            raise APIClientError("유효한 토큰이 없습니다.")
        return {"Authorization": f"Bearer {token.access_token}"}

    def _handle_response(self, response: Response) -> Any:
        """Parse API response and raise friendly errors."""
        try:
            body = response.json()
        except ValueError as exc:
            app_logger.error("JSON 응답 디코딩 실패: %s", exc)
            raise APIClientError(
                "JSON 응답 디코딩 실패",
                http_status=response.status_code,
            ) from exc

        if isinstance(body, dict) and "success" in body:
            if body.get("success", False):
                app_logger.debug("API 응답 성공: %s", body.get("data"))
                return body.get("data")
            error = body.get("error") or {}
            message = error.get("message") or "API 호출이 실패했습니다."
            app_logger.error(
                "API 호출 실패 - code=%s status=%s message=%s",
                error.get("code"),
                error.get("httpStatus", response.status_code),
                message,
            )
            raise APIClientError(
                message,
                code=error.get("code"),
                http_status=error.get("httpStatus", response.status_code),
                hint=error.get("hint"),
                details=error.get("details"),
            )

        if response.status_code >= 400:
            message = f"API 호출 실패: {response.status_code}"
            app_logger.error("%s - body=%s", message, body)
            raise APIClientError(message, http_status=response.status_code)

        app_logger.debug("API 응답 (래핑 없음): %s", body)
        return body

    def _parse_topics_page(self, payload: Any) -> TopicsPage:
        if not isinstance(payload, dict):
            raise APIClientError("Topic 목록 응답 형식이 올바르지 않습니다.")

        raw_topics = payload.get("topics", [])
        if not isinstance(raw_topics, list):
            raise APIClientError("Topic 목록 데이터가 올바르지 않습니다.")

        topics: List[TopicDTO] = []
        for item in raw_topics:
            try:
                topics.append(self._parse_topic(item))
            except APIClientError as exc:
                app_logger.warning("무시된 Topic 항목: %s", exc)

        total = self._coerce_int(payload.get("total"), "total", default=len(topics))
        page = self._coerce_int(payload.get("page"), "page", default=1)
        page_size = self._coerce_int(payload.get("page_size"), "page_size", default=len(topics))
        return TopicsPage(topics=topics, total=total, page=page, page_size=page_size)

    def _parse_artifact_list(self, payload: Any) -> ArtifactListDTO:
        if not isinstance(payload, dict):
            raise APIClientError("Artifact 목록 응답 형식이 올바르지 않습니다.")

        raw_artifacts = payload.get("artifacts", [])
        if not isinstance(raw_artifacts, list):
            raise APIClientError("Artifact 목록 데이터가 올바르지 않습니다.")

        artifacts: List[ArtifactDTO] = []
        for item in raw_artifacts:
            try:
                artifacts.append(self._parse_artifact(item))
            except APIClientError as exc:
                app_logger.warning("무시된 Artifact 항목: %s", exc)

        total = self._coerce_int(payload.get("total"), "total", default=len(artifacts))
        topic_id = self._coerce_int(payload.get("topic_id"), "topic_id")
        return ArtifactListDTO(artifacts=artifacts, total=total, topic_id=topic_id)

    def _parse_topic(self, payload: Any) -> TopicDTO:
        if not isinstance(payload, dict):
            raise APIClientError("Topic 항목 데이터가 올바르지 않습니다.")

        generated_title = payload.get("generated_title")
        try:
            return TopicDTO(
                id=self._coerce_int(payload.get("id"), "id"),
                input_prompt=str(payload.get("input_prompt") or ""),
                generated_title=None if generated_title is None else str(generated_title),
                language=str(payload.get("language") or ""),
                status=str(payload.get("status") or ""),
                created_at=str(payload.get("created_at") or ""),
                updated_at=str(payload.get("updated_at") or ""),
            )
        except (TypeError, ValueError) as exc:
            raise APIClientError("Topic 항목 데이터를 파싱할 수 없습니다.") from exc

    def _parse_artifact(self, payload: Any) -> ArtifactDTO:
        if not isinstance(payload, dict):
            raise APIClientError("Artifact 항목 데이터가 올바르지 않습니다.")
        try:
            return ArtifactDTO(
                id=self._coerce_int(payload.get("id"), "id"),
                topic_id=self._coerce_int(payload.get("topic_id"), "topic_id"),
                message_id=self._coerce_int(payload.get("message_id"), "message_id"),
                kind=str(payload.get("kind") or ""),
                locale=str(payload.get("locale") or ""),
                version=self._coerce_int(payload.get("version"), "version", default=1),
                filename=str(payload.get("filename") or ""),
                file_path=str(payload.get("file_path") or ""),
                file_size=self._coerce_int(payload.get("file_size"), "file_size", default=0),
                created_at=str(payload.get("created_at") or ""),
            )
        except (TypeError, ValueError) as exc:
            raise APIClientError("Artifact 항목 데이터를 파싱할 수 없습니다.") from exc

    def _coerce_int(self, value: Any, field: str, *, default: Optional[int] = None) -> int:
        if value is None:
            if default is None:
                raise APIClientError(f"{field} 값이 응답에 없습니다.")
            return default
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise APIClientError(f"{field} 값을 정수로 변환할 수 없습니다.") from exc
