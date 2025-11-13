"""
Custom exceptions for HWP Report Generator backend.

이 파일은 백엔드에서 사용하는 커스텀 예외들을 정의합니다.
"""


class InvalidTemplateError(Exception):
    """Template 조회 실패 시 발생하는 예외

    Template이 존재하지 않거나 사용자가 접근 권한이 없을 때 발생합니다.

    Attributes:
        code: ErrorCode 상수 (예: ErrorCode.TEMPLATE_NOT_FOUND)
        http_status: HTTP 상태 코드 (예: 404)
        message: 사용자에게 표시할 에러 메시지
        hint: 사용자에게 표시할 해결 방법 (선택사항)
    """

    def __init__(
        self,
        code: str,
        http_status: int,
        message: str,
        hint: str = None,
    ):
        """
        Args:
            code: ErrorCode 상수 (예: ErrorCode.TEMPLATE_NOT_FOUND)
            http_status: HTTP 상태 코드 (예: 404)
            message: 사용자에게 표시할 에러 메시지
            hint: 사용자에게 표시할 해결 방법 (선택사항)
        """
        self.code = code
        self.http_status = http_status
        self.message = message
        self.hint = hint
        super().__init__(message)
