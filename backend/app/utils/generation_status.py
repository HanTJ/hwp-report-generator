"""
메모리 기반 보고서 생성 상태 관리 모듈

보고서 생성의 진행 상황을 메모리의 dictionary에 저장하여
빠른 조회와 업데이트를 지원합니다.

구조:
_generation_status[topic_id] = {
    "status": "generating" | "completed" | "failed",
    "progress_percent": 0-100,
    "current_step": "현재 진행 중인 단계",
    "started_at": "ISO 8601 timestamp",
    "estimated_completion": "ISO 8601 timestamp",
    "artifact_id": null or integer,
    "error_message": null or string,
    "sse_connections": []  # 내부 사용
}
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# 메모리 기반 상태 저장소
_generation_status: Dict[int, Dict[str, Any]] = {}


def update_generation_status(
    topic_id: int,
    status_dict: Dict[str, Any]
) -> None:
    """
    보고서 생성 상태 업데이트

    Args:
        topic_id: 토픽 ID
        status_dict: 상태 정보 딕셔너리
                    {
                        "status": "generating" | "completed" | "failed",
                        "progress_percent": 0-100,
                        "current_step": "...",
                        "started_at": "ISO timestamp",
                        "estimated_completion": "ISO timestamp",
                        "artifact_id": null or int,
                        "error_message": null or str
                    }

    Example:
        >>> update_generation_status(1, {
        ...     "status": "generating",
        ...     "progress_percent": 50,
        ...     "current_step": "Generating content..."
        ... })
    """
    if not isinstance(topic_id, int) or topic_id <= 0:
        raise ValueError("topic_id must be a positive integer")

    if not isinstance(status_dict, dict):
        raise ValueError("status_dict must be a dictionary")

    _generation_status[topic_id] = status_dict
    logger.debug(
        f"Generation status updated - "
        f"topic_id={topic_id}, "
        f"status={status_dict.get('status')}, "
        f"progress={status_dict.get('progress_percent')}%"
    )


def get_generation_status(topic_id: int) -> Optional[Dict[str, Any]]:
    """
    보고서 생성 상태 조회

    Args:
        topic_id: 토픽 ID

    Returns:
        상태 정보 딕셔너리 또는 None (상태가 없을 때)

    Example:
        >>> status = get_generation_status(1)
        >>> if status:
        ...     print(status['status'])  # "generating"
    """
    if not isinstance(topic_id, int) or topic_id <= 0:
        raise ValueError("topic_id must be a positive integer")

    return _generation_status.get(topic_id)


def clear_generation_status(topic_id: int) -> None:
    """
    보고서 생성 상태 초기화 (완료 후 정리용)

    Args:
        topic_id: 토픽 ID

    Example:
        >>> clear_generation_status(1)
    """
    if not isinstance(topic_id, int) or topic_id <= 0:
        raise ValueError("topic_id must be a positive integer")

    if topic_id in _generation_status:
        del _generation_status[topic_id]
        logger.debug(f"Generation status cleared - topic_id={topic_id}")


def is_generating(topic_id: int) -> bool:
    """
    현재 생성 중인지 확인

    Args:
        topic_id: 토픽 ID

    Returns:
        True if status is "generating", False otherwise

    Example:
        >>> if is_generating(1):
        ...     return error_response("Generation already in progress")
    """
    if not isinstance(topic_id, int) or topic_id <= 0:
        raise ValueError("topic_id must be a positive integer")

    status = get_generation_status(topic_id)
    return status is not None and status.get("status") == "generating"


def init_generation_status(
    topic_id: int,
    started_at: Optional[str] = None
) -> Dict[str, Any]:
    """
    보고서 생성 시작 시 초기 상태 설정

    Args:
        topic_id: 토픽 ID
        started_at: 시작 시간 (ISO 8601, None이면 현재 시간)

    Returns:
        생성된 상태 딕셔너리

    Example:
        >>> init_generation_status(1)
        {'status': 'generating', 'progress_percent': 0, ...}
    """
    if started_at is None:
        started_at = datetime.utcnow().isoformat()

    initial_status = {
        "status": "generating",
        "progress_percent": 0,
        "current_step": "Starting report generation...",
        "started_at": started_at,
        "estimated_completion": None,
        "artifact_id": None,
        "error_message": None,
    }

    update_generation_status(topic_id, initial_status)
    logger.info(f"Generation status initialized - topic_id={topic_id}, started_at={started_at}")

    return initial_status


def update_progress(
    topic_id: int,
    progress_percent: int,
    current_step: str,
    estimated_completion: Optional[str] = None
) -> None:
    """
    생성 진행 상황 업데이트

    Args:
        topic_id: 토픽 ID
        progress_percent: 진행률 (0-100)
        current_step: 현재 진행 단계 설명
        estimated_completion: 예상 완료 시간 (ISO 8601)

    Example:
        >>> update_progress(1, 50, "Generating main content...")
    """
    if not 0 <= progress_percent <= 100:
        raise ValueError("progress_percent must be between 0 and 100")

    status = get_generation_status(topic_id)

    if status is None:
        raise ValueError(f"No generation status found for topic_id {topic_id}")

    status["progress_percent"] = progress_percent
    status["current_step"] = current_step
    if estimated_completion:
        status["estimated_completion"] = estimated_completion

    update_generation_status(topic_id, status)
    logger.debug(f"Progress updated - topic_id={topic_id}, progress={progress_percent}%")


def mark_completed(
    topic_id: int,
    artifact_id: int,
    completed_at: Optional[str] = None
) -> None:
    """
    보고서 생성 완료 표시

    Args:
        topic_id: 토픽 ID
        artifact_id: 생성된 artifact ID
        completed_at: 완료 시간 (ISO 8601, None이면 현재 시간)

    Example:
        >>> mark_completed(1, artifact_id=123)
    """
    if completed_at is None:
        completed_at = datetime.utcnow().isoformat()

    status = get_generation_status(topic_id)

    if status is None:
        raise ValueError(f"No generation status found for topic_id {topic_id}")

    status["status"] = "completed"
    status["progress_percent"] = 100
    status["artifact_id"] = artifact_id
    status["completed_at"] = completed_at

    update_generation_status(topic_id, status)
    logger.info(f"Generation marked as completed - topic_id={topic_id}, artifact_id={artifact_id}")


def mark_failed(
    topic_id: int,
    error_message: str,
    failed_at: Optional[str] = None
) -> None:
    """
    보고서 생성 실패 표시

    Args:
        topic_id: 토픽 ID
        error_message: 에러 메시지
        failed_at: 실패 시간 (ISO 8601, None이면 현재 시간)

    Example:
        >>> mark_failed(1, "Claude API timeout")
    """
    if failed_at is None:
        failed_at = datetime.utcnow().isoformat()

    status = get_generation_status(topic_id)

    if status is None:
        raise ValueError(f"No generation status found for topic_id {topic_id}")

    status["status"] = "failed"
    status["error_message"] = error_message
    status["failed_at"] = failed_at

    update_generation_status(topic_id, status)
    logger.error(f"Generation marked as failed - topic_id={topic_id}, error={error_message}")


def get_all_statuses() -> Dict[int, Dict[str, Any]]:
    """
    모든 생성 상태 조회 (디버깅 및 모니터링용)

    Returns:
        모든 topic_id의 상태 딕셔너리 (깊은 복사)

    Example:
        >>> statuses = get_all_statuses()
        >>> for topic_id, status in statuses.items():
        ...     print(f"Topic {topic_id}: {status['status']}")
    """
    import copy
    return copy.deepcopy(_generation_status)


def clear_all_statuses() -> None:
    """
    모든 생성 상태 초기화 (테스트용)

    Example:
        >>> clear_all_statuses()
    """
    global _generation_status
    _generation_status.clear()
    logger.debug("All generation statuses cleared")


def get_status_count() -> int:
    """
    현재 저장된 상태의 개수 (모니터링용)

    Returns:
        저장된 상태의 개수

    Example:
        >>> count = get_status_count()
        >>> print(f"Active generations: {count}")
    """
    return len(_generation_status)
