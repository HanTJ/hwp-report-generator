"""
API 라우터 패키지
"""
from .auth import router as auth_router
from .reports import router as reports_router
from .admin import router as admin_router
from .topics import router as topics_router
from .messages import router as messages_router
from .artifacts import router as artifacts_router

__all__ = [
    "auth_router",
    "reports_router",
    "admin_router",
    "topics_router",
    "messages_router",
    "artifacts_router",
]
