"""
API 공통 상수
constants.properties 파일을 파싱하여 상수를 제공
"""

import os
from pathlib import Path
from typing import Dict


class PropertiesParser:
    """Properties 파일 파서"""

    def __init__(self, file_path: str):
        self.properties: Dict[str, str] = {}
        self._load(file_path)

    def _load(self, file_path: str):
        """Properties 파일 로드"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Properties file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # 주석 또는 빈 줄 건너뛰기
                if not line or line.startswith('#'):
                    continue

                # key=value 파싱
                if '=' in line:
                    key, value = line.split('=', 1)
                    self.properties[key.strip()] = value.strip()

    def get(self, key: str, default: str = None) -> str:
        """속성 값 가져오기"""
        return self.properties.get(key, default)

    def get_int(self, key: str, default: int = None) -> int:
        """정수 값 가져오기"""
        value = self.get(key)
        return int(value) if value else default

    def get_bool(self, key: str, default: bool = None) -> bool:
        """불린 값 가져오기"""
        value = self.get(key)
        if value:
            return value.lower() in ('true', 'yes', '1')
        return default


# Properties 파일 로드
_current_dir = Path(__file__).parent
_props = PropertiesParser(str(_current_dir / "constants.properties"))


# ============================================================
# 에러 코드
# ============================================================

class ErrorCode:
    """API 에러 코드"""

    class AUTH:
        INVALID_TOKEN = _props.get("ERROR.AUTH.INVALID_TOKEN")
        TOKEN_EXPIRED = _props.get("ERROR.AUTH.TOKEN_EXPIRED")
        UNAUTHORIZED = _props.get("ERROR.AUTH.UNAUTHORIZED")
        FORBIDDEN = _props.get("ERROR.AUTH.FORBIDDEN")
        INVALID_CREDENTIALS = _props.get("ERROR.AUTH.INVALID_CREDENTIALS")
        USER_NOT_FOUND = _props.get("ERROR.AUTH.USER_NOT_FOUND")
        PASSWORD_MISMATCH = _props.get("ERROR.AUTH.PASSWORD_MISMATCH")

    class VALIDATION:
        ERROR = _props.get("ERROR.VALIDATION.ERROR")
        MISSING_FIELD = _props.get("ERROR.VALIDATION.MISSING_FIELD")
        INVALID_FORMAT = _props.get("ERROR.VALIDATION.INVALID_FORMAT")
        FIELD_TOO_SHORT = _props.get("ERROR.VALIDATION.FIELD_TOO_SHORT")
        FIELD_TOO_LONG = _props.get("ERROR.VALIDATION.FIELD_TOO_LONG")
        INVALID_EMAIL = _props.get("ERROR.VALIDATION.INVALID_EMAIL")
        INVALID_TYPE = _props.get("ERROR.VALIDATION.INVALID_TYPE")

    class REPORT:
        GENERATION_FAILED = _props.get("ERROR.REPORT.GENERATION_FAILED")
        NOT_FOUND = _props.get("ERROR.REPORT.NOT_FOUND")
        TOPIC_TOO_SHORT = _props.get("ERROR.REPORT.TOPIC_TOO_SHORT")
        TOPIC_EMPTY = _props.get("ERROR.REPORT.TOPIC_EMPTY")
        GENERATION_TIMEOUT = _props.get("ERROR.REPORT.GENERATION_TIMEOUT")
        INVALID_TEMPLATE = _props.get("ERROR.REPORT.INVALID_TEMPLATE")

    class HWP:
        PROCESSING_ERROR = _props.get("ERROR.HWP.PROCESSING_ERROR")
        TEMPLATE_NOT_FOUND = _props.get("ERROR.HWP.TEMPLATE_NOT_FOUND")
        INVALID_FORMAT = _props.get("ERROR.HWP.INVALID_FORMAT")
        EXTRACTION_FAILED = _props.get("ERROR.HWP.EXTRACTION_FAILED")
        COMPRESSION_FAILED = _props.get("ERROR.HWP.COMPRESSION_FAILED")
        XML_PARSE_ERROR = _props.get("ERROR.HWP.XML_PARSE_ERROR")

    class CLAUDE:
        API_ERROR = _props.get("ERROR.CLAUDE.API_ERROR")
        RATE_LIMIT = _props.get("ERROR.CLAUDE.RATE_LIMIT")
        TIMEOUT = _props.get("ERROR.CLAUDE.TIMEOUT")
        INVALID_RESPONSE = _props.get("ERROR.CLAUDE.INVALID_RESPONSE")
        CONNECTION_ERROR = _props.get("ERROR.CLAUDE.CONNECTION_ERROR")
        QUOTA_EXCEEDED = _props.get("ERROR.CLAUDE.QUOTA_EXCEEDED")

    class FILE:
        NOT_FOUND = _props.get("ERROR.FILE.NOT_FOUND")
        UPLOAD_FAILED = _props.get("ERROR.FILE.UPLOAD_FAILED")
        SIZE_EXCEEDED = _props.get("ERROR.FILE.SIZE_EXCEEDED")
        INVALID_TYPE = _props.get("ERROR.FILE.INVALID_TYPE")
        DOWNLOAD_FAILED = _props.get("ERROR.FILE.DOWNLOAD_FAILED")

    class SYSTEM:
        INTERNAL_ERROR = _props.get("ERROR.SYSTEM.INTERNAL_ERROR")
        SERVICE_UNAVAILABLE = _props.get("ERROR.SYSTEM.SERVICE_UNAVAILABLE")
        DATABASE_ERROR = _props.get("ERROR.SYSTEM.DATABASE_ERROR")
        NETWORK_ERROR = _props.get("ERROR.SYSTEM.NETWORK_ERROR")
        TIMEOUT = _props.get("ERROR.SYSTEM.TIMEOUT")


# ============================================================
# 피드백 코드
# ============================================================

class FeedbackCode:
    """피드백 코드"""

    class PROFILE:
        INCOMPLETE = _props.get("FEEDBACK.PROFILE.INCOMPLETE")
        PHOTO_MISSING = _props.get("FEEDBACK.PROFILE.PHOTO_MISSING")
        UPDATE_SUCCESS = _props.get("FEEDBACK.PROFILE.UPDATE_SUCCESS")

    class REPORT:
        GENERATION_SUCCESS = _props.get("FEEDBACK.REPORT.GENERATION_SUCCESS")
        GENERATION_IN_PROGRESS = _props.get("FEEDBACK.REPORT.GENERATION_IN_PROGRESS")
        TOPIC_SUGGESTION = _props.get("FEEDBACK.REPORT.TOPIC_SUGGESTION")
        TEMPLATE_UPDATED = _props.get("FEEDBACK.REPORT.TEMPLATE_UPDATED")

    class SYSTEM:
        MAINTENANCE_SCHEDULED = _props.get("FEEDBACK.SYSTEM.MAINTENANCE_SCHEDULED")
        NEW_FEATURE = _props.get("FEEDBACK.SYSTEM.NEW_FEATURE")
        UPDATE_AVAILABLE = _props.get("FEEDBACK.SYSTEM.UPDATE_AVAILABLE")

    class SECURITY:
        PASSWORD_EXPIRING = _props.get("FEEDBACK.SECURITY.PASSWORD_EXPIRING")
        UNUSUAL_LOGIN = _props.get("FEEDBACK.SECURITY.UNUSUAL_LOGIN")
        TWO_FACTOR_RECOMMENDED = _props.get("FEEDBACK.SECURITY.TWO_FACTOR_RECOMMENDED")


# ============================================================
# 피드백 레벨
# ============================================================

class FeedbackLevel:
    """피드백 레벨"""
    INFO = _props.get("FEEDBACK_LEVEL.INFO")
    WARNING = _props.get("FEEDBACK_LEVEL.WARNING")
    ERROR = _props.get("FEEDBACK_LEVEL.ERROR")


# ============================================================
# HTTP 상태 코드
# ============================================================

class HttpStatus:
    """HTTP 상태 코드"""

    # 2xx Success
    OK = _props.get_int("HTTP_STATUS.OK")
    CREATED = _props.get_int("HTTP_STATUS.CREATED")
    ACCEPTED = _props.get_int("HTTP_STATUS.ACCEPTED")
    NO_CONTENT = _props.get_int("HTTP_STATUS.NO_CONTENT")

    # 4xx Client Error
    BAD_REQUEST = _props.get_int("HTTP_STATUS.BAD_REQUEST")
    UNAUTHORIZED = _props.get_int("HTTP_STATUS.UNAUTHORIZED")
    FORBIDDEN = _props.get_int("HTTP_STATUS.FORBIDDEN")
    NOT_FOUND = _props.get_int("HTTP_STATUS.NOT_FOUND")
    CONFLICT = _props.get_int("HTTP_STATUS.CONFLICT")
    UNPROCESSABLE_ENTITY = _props.get_int("HTTP_STATUS.UNPROCESSABLE_ENTITY")
    TOO_MANY_REQUESTS = _props.get_int("HTTP_STATUS.TOO_MANY_REQUESTS")

    # 5xx Server Error
    INTERNAL_SERVER_ERROR = _props.get_int("HTTP_STATUS.INTERNAL_SERVER_ERROR")
    BAD_GATEWAY = _props.get_int("HTTP_STATUS.BAD_GATEWAY")
    SERVICE_UNAVAILABLE = _props.get_int("HTTP_STATUS.SERVICE_UNAVAILABLE")
    GATEWAY_TIMEOUT = _props.get_int("HTTP_STATUS.GATEWAY_TIMEOUT")


# ============================================================
# API 메시지
# ============================================================

class Message:
    """API 메시지"""

    class SUCCESS:
        REPORT_GENERATED = _props.get("MESSAGE.SUCCESS.REPORT_GENERATED")
        LOGIN_SUCCESS = _props.get("MESSAGE.SUCCESS.LOGIN_SUCCESS")
        LOGOUT_SUCCESS = _props.get("MESSAGE.SUCCESS.LOGOUT_SUCCESS")
        PROFILE_UPDATED = _props.get("MESSAGE.SUCCESS.PROFILE_UPDATED")

    class ERROR:
        INVALID_TOKEN = _props.get("MESSAGE.ERROR.INVALID_TOKEN")
        TOKEN_EXPIRED = _props.get("MESSAGE.ERROR.TOKEN_EXPIRED")
        UNAUTHORIZED = _props.get("MESSAGE.ERROR.UNAUTHORIZED")
        FORBIDDEN = _props.get("MESSAGE.ERROR.FORBIDDEN")
        REPORT_GENERATION_FAILED = _props.get("MESSAGE.ERROR.REPORT_GENERATION_FAILED")
        TOPIC_TOO_SHORT = _props.get("MESSAGE.ERROR.TOPIC_TOO_SHORT")
        TOPIC_EMPTY = _props.get("MESSAGE.ERROR.TOPIC_EMPTY")
        INTERNAL_ERROR = _props.get("MESSAGE.ERROR.INTERNAL_ERROR")
        SERVICE_UNAVAILABLE = _props.get("MESSAGE.ERROR.SERVICE_UNAVAILABLE")
        INVALID_CREDENTIALS = _props.get("MESSAGE.ERROR.INVALID_CREDENTIALS")
        USER_NOT_FOUND = _props.get("MESSAGE.ERROR.USER_NOT_FOUND")
        HWP_TEMPLATE_NOT_FOUND = _props.get("MESSAGE.ERROR.HWP_TEMPLATE_NOT_FOUND")
        CLAUDE_API_ERROR = _props.get("MESSAGE.ERROR.CLAUDE_API_ERROR")
        CLAUDE_RATE_LIMIT = _props.get("MESSAGE.ERROR.CLAUDE_RATE_LIMIT")

    class HINT:
        LOGIN_AGAIN = _props.get("MESSAGE.HINT.LOGIN_AGAIN")
        CONTACT_ADMIN = _props.get("MESSAGE.HINT.CONTACT_ADMIN")
        TRY_AGAIN_LATER = _props.get("MESSAGE.HINT.TRY_AGAIN_LATER")
        CHECK_INPUT = _props.get("MESSAGE.HINT.CHECK_INPUT")
        CHECK_TEMPLATE = _props.get("MESSAGE.HINT.CHECK_TEMPLATE")
        REDUCE_REQUEST_RATE = _props.get("MESSAGE.HINT.REDUCE_REQUEST_RATE")


# ============================================================
# 검증 제약조건
# ============================================================

class ValidationConstraint:
    """검증 제약조건"""

    class REPORT_TOPIC:
        MIN_LENGTH = _props.get_int("VALIDATION.REPORT_TOPIC.MIN_LENGTH")
        MAX_LENGTH = _props.get_int("VALIDATION.REPORT_TOPIC.MAX_LENGTH")

    class PASSWORD:
        MIN_LENGTH = _props.get_int("VALIDATION.PASSWORD.MIN_LENGTH")
        MAX_LENGTH = _props.get_int("VALIDATION.PASSWORD.MAX_LENGTH")

    class EMAIL:
        REGEX = _props.get("VALIDATION.EMAIL.REGEX")

    class FILE:
        MAX_SIZE_MB = _props.get_int("VALIDATION.FILE.MAX_SIZE_MB")


# ============================================================
# 토큰 설정
# ============================================================

class TokenConfig:
    """토큰 설정"""
    ACCESS_TOKEN_EXPIRE_MINUTES = _props.get_int("TOKEN.ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS = _props.get_int("TOKEN.REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM = _props.get("TOKEN.ALGORITHM")


# ============================================================
# API 엔드포인트
# ============================================================

class Endpoint:
    """API 엔드포인트"""

    class AUTH:
        LOGIN = _props.get("ENDPOINT.AUTH.LOGIN")
        LOGOUT = _props.get("ENDPOINT.AUTH.LOGOUT")
        REFRESH = _props.get("ENDPOINT.AUTH.REFRESH")

    class REPORT:
        GENERATE = _props.get("ENDPOINT.REPORT.GENERATE")
        DOWNLOAD = _props.get("ENDPOINT.REPORT.DOWNLOAD")

    class USER:
        PROFILE = _props.get("ENDPOINT.USER.PROFILE")


# ============================================================
# 쿠키 설정
# ============================================================

class CookieConfig:
    """쿠키 설정"""

    class REFRESH_TOKEN:
        NAME = _props.get("COOKIE.REFRESH_TOKEN.NAME")
        HTTPONLY = _props.get_bool("COOKIE.REFRESH_TOKEN.HTTPONLY")
        SECURE = _props.get_bool("COOKIE.REFRESH_TOKEN.SECURE")
        SAMESITE = _props.get("COOKIE.REFRESH_TOKEN.SAMESITE")
        MAX_AGE = _props.get_int("COOKIE.REFRESH_TOKEN.MAX_AGE")


# ============================================================
# 비즈니스 규칙
# ============================================================

class BusinessRule:
    """비즈니스 규칙"""

    class REPORT:
        DEFAULT_DATE_FORMAT = _props.get("BUSINESS.REPORT.DEFAULT_DATE_FORMAT")
        OUTPUT_DIRECTORY = _props.get("BUSINESS.REPORT.OUTPUT_DIRECTORY")
        TEMP_DIRECTORY = _props.get("BUSINESS.REPORT.TEMP_DIRECTORY")
        TEMPLATE_PATH = _props.get("BUSINESS.REPORT.TEMPLATE_PATH")
        GENERATION_TIMEOUT_SECONDS = _props.get_int("BUSINESS.REPORT.GENERATION_TIMEOUT_SECONDS")


# ============================================================
# Claude API 설정
# ============================================================

class ClaudeConfig:
    """Claude API 설정"""
    MODEL = _props.get("CLAUDE.MODEL")
    MAX_TOKENS = _props.get_int("CLAUDE.MAX_TOKENS")
    TEMPERATURE = float(_props.get("CLAUDE.TEMPERATURE", "1.0"))
    TIMEOUT_SECONDS = _props.get_int("CLAUDE.TIMEOUT_SECONDS")


# ============================================================
# 피드백 메시지
# ============================================================

class FeedbackMessage:
    """피드백 메시지"""
    PROFILE_INCOMPLETE = _props.get("FEEDBACK.MESSAGE.PROFILE_INCOMPLETE")
    PROFILE_PHOTO_MISSING = _props.get("FEEDBACK.MESSAGE.PROFILE_PHOTO_MISSING")
    REPORT_GENERATION_SUCCESS = _props.get("FEEDBACK.MESSAGE.REPORT_GENERATION_SUCCESS")
    REPORT_GENERATION_IN_PROGRESS = _props.get("FEEDBACK.MESSAGE.REPORT_GENERATION_IN_PROGRESS")
    PASSWORD_EXPIRING = _props.get("FEEDBACK.MESSAGE.PASSWORD_EXPIRING")
    MAINTENANCE_SCHEDULED = _props.get("FEEDBACK.MESSAGE.MAINTENANCE_SCHEDULED")
    NEW_FEATURE = _props.get("FEEDBACK.MESSAGE.NEW_FEATURE")


# ============================================================
# 헬퍼 함수
# ============================================================

def get_error_message(error_code: str) -> str:
    """에러 코드에 해당하는 메시지 반환"""
    error_message_map = {
        ErrorCode.AUTH.INVALID_TOKEN: Message.ERROR.INVALID_TOKEN,
        ErrorCode.AUTH.TOKEN_EXPIRED: Message.ERROR.TOKEN_EXPIRED,
        ErrorCode.AUTH.UNAUTHORIZED: Message.ERROR.UNAUTHORIZED,
        ErrorCode.AUTH.FORBIDDEN: Message.ERROR.FORBIDDEN,
        ErrorCode.AUTH.INVALID_CREDENTIALS: Message.ERROR.INVALID_CREDENTIALS,
        ErrorCode.REPORT.GENERATION_FAILED: Message.ERROR.REPORT_GENERATION_FAILED,
        ErrorCode.REPORT.TOPIC_TOO_SHORT: Message.ERROR.TOPIC_TOO_SHORT,
        ErrorCode.REPORT.TOPIC_EMPTY: Message.ERROR.TOPIC_EMPTY,
        ErrorCode.HWP.TEMPLATE_NOT_FOUND: Message.ERROR.HWP_TEMPLATE_NOT_FOUND,
        ErrorCode.CLAUDE.API_ERROR: Message.ERROR.CLAUDE_API_ERROR,
        ErrorCode.CLAUDE.RATE_LIMIT: Message.ERROR.CLAUDE_RATE_LIMIT,
    }
    return error_message_map.get(error_code, Message.ERROR.INTERNAL_ERROR)


def get_error_hint(error_code: str) -> str:
    """에러 코드에 해당하는 힌트 반환"""
    error_hint_map = {
        ErrorCode.AUTH.INVALID_TOKEN: Message.HINT.LOGIN_AGAIN,
        ErrorCode.AUTH.TOKEN_EXPIRED: Message.HINT.LOGIN_AGAIN,
        ErrorCode.AUTH.UNAUTHORIZED: Message.HINT.LOGIN_AGAIN,
        ErrorCode.VALIDATION.ERROR: Message.HINT.CHECK_INPUT,
        ErrorCode.HWP.TEMPLATE_NOT_FOUND: Message.HINT.CHECK_TEMPLATE,
        ErrorCode.CLAUDE.RATE_LIMIT: Message.HINT.REDUCE_REQUEST_RATE,
        ErrorCode.SYSTEM.INTERNAL_ERROR: Message.HINT.TRY_AGAIN_LATER,
    }
    return error_hint_map.get(error_code, Message.HINT.CONTACT_ADMIN)
