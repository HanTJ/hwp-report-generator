"""
데이터베이스 패키지
"""
from .connection import init_db, get_db_connection
from .user_db import UserDB
from .topic_db import TopicDB
from .message_db import MessageDB
from .artifact_db import ArtifactDB
from .ai_usage_db import AiUsageDB
from .transformation_db import TransformationDB

# Legacy imports (deprecated, will be removed)
try:
    from .report_db import ReportDB
    from .token_usage_db import TokenUsageDB
    _legacy_available = True
except ImportError:
    _legacy_available = False

__all__ = [
    "init_db",
    "get_db_connection",
    "UserDB",
    "TopicDB",
    "MessageDB",
    "ArtifactDB",
    "AiUsageDB",
    "TransformationDB",
]

# Add legacy exports if available
if _legacy_available:
    __all__.extend(["ReportDB", "TokenUsageDB"])
