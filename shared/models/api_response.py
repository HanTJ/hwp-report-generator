"""
Standard API response format for all backend-frontend communication.

This module defines the standardized response structure used across all API endpoints
to ensure consistency and better error handling.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from enum import Enum


class FeedbackLevel(str, Enum):
    """Level/severity of user feedback.

    Attributes:
        INFO: Informational message (e.g., helpful hints)
        WARNING: Warning message (e.g., incomplete data)
        ERROR: Error message (e.g., validation failures)
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Feedback(BaseModel):
    """User feedback/hint model.

    Attributes:
        code: Feedback identifier code
        level: Severity level (info/warning/error)
        feedbackCd: Human-readable feedback message
    """
    code: str = Field(..., description="Feedback identifier code")
    level: FeedbackLevel = Field(..., description="Feedback severity level")
    feedbackCd: str = Field(..., description="User-friendly feedback message")


class ErrorResponse(BaseModel):
    """Error details model.

    Attributes:
        code: Unique error code in DOMAIN.DETAIL format (e.g., AUTH.INVALID_TOKEN)
        httpStatus: HTTP status code (401, 404, 500, etc.)
        message: User-friendly error message
        details: Additional error details (optional)
        traceId: Unique ID for error tracing
        hint: Suggested action for user (optional)
    """
    code: str = Field(..., description="Unique error code (DOMAIN.DETAIL)")
    httpStatus: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="User-friendly error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    traceId: str = Field(..., description="Unique trace ID for debugging")
    hint: Optional[str] = Field(None, description="Suggested action for user")


class ApiResponse(BaseModel):
    """Standard API response format.

    All API endpoints should return responses in this format for consistency.

    Attributes:
        success: Boolean indicating request success/failure
        data: Actual response data (null on failure)
        error: Error details object (null on success)
        meta: Metadata including requestId for tracing
        feedback: Array of optional user feedback/hints

    Examples:
        Success response:
        >>> ApiResponse(
        ...     success=True,
        ...     data={"reportId": 123, "filename": "report.hwpx"},
        ...     error=None,
        ...     meta={"requestId": "req_abc123"},
        ...     feedback=[]
        ... )

        Error response:
        >>> ApiResponse(
        ...     success=False,
        ...     data=None,
        ...     error=ErrorResponse(
        ...         code="AUTH.INVALID_TOKEN",
        ...         httpStatus=401,
        ...         message="Invalid authentication token",
        ...         traceId="trace_xyz789",
        ...         hint="Please log in again"
        ...     ),
        ...     meta={"requestId": "req_def456"},
        ...     feedback=[]
        ... )
    """
    success: bool = Field(..., description="Request success indicator")
    data: Optional[Any] = Field(None, description="Response data (null on error)")
    error: Optional[ErrorResponse] = Field(None, description="Error details (null on success)")
    meta: Dict[str, str] = Field(..., description="Metadata (requestId, etc.)")
    feedback: List[Feedback] = Field(default_factory=list, description="User feedback messages")
