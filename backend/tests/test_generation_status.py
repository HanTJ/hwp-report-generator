"""
메모리 기반 보고서 생성 상태 관리 모듈 테스트

generation_status.py의 모든 함수를 테스트합니다.
"""

import pytest
from datetime import datetime
from app.utils.generation_status import (
    update_generation_status,
    get_generation_status,
    clear_generation_status,
    is_generating,
    init_generation_status,
    update_progress,
    mark_completed,
    mark_failed,
    get_all_statuses,
    clear_all_statuses,
    get_status_count
)


class TestGenerationStatusUpdate:
    """update_generation_status 함수 테스트"""

    def test_update_status_basic(self):
        """기본 상태 업데이트"""
        clear_all_statuses()

        status_dict = {
            "status": "generating",
            "progress_percent": 50,
            "current_step": "Processing..."
        }

        update_generation_status(1, status_dict)

        result = get_generation_status(1)
        assert result is not None
        assert result["status"] == "generating"
        assert result["progress_percent"] == 50

    def test_update_status_invalid_topic_id(self):
        """유효하지 않은 topic_id 처리"""
        with pytest.raises(ValueError):
            update_generation_status(-1, {})

        with pytest.raises(ValueError):
            update_generation_status(0, {})

        with pytest.raises(ValueError):
            update_generation_status("invalid", {})

    def test_update_status_invalid_dict(self):
        """유효하지 않은 딕셔너리 처리"""
        with pytest.raises(ValueError):
            update_generation_status(1, "not_a_dict")

    def test_update_status_overwrites_previous(self):
        """이전 상태를 덮어씌우는 것을 확인"""
        clear_all_statuses()

        update_generation_status(1, {"status": "generating", "progress_percent": 10})
        update_generation_status(1, {"status": "generating", "progress_percent": 20})

        result = get_generation_status(1)
        assert result["progress_percent"] == 20


class TestGenerationStatusGet:
    """get_generation_status 함수 테스트"""

    def test_get_existing_status(self):
        """존재하는 상태 조회"""
        clear_all_statuses()

        status_dict = {"status": "generating", "progress_percent": 50}
        update_generation_status(1, status_dict)

        result = get_generation_status(1)
        assert result is not None
        assert result["progress_percent"] == 50

    def test_get_nonexistent_status(self):
        """존재하지 않는 상태 조회"""
        clear_all_statuses()

        result = get_generation_status(999)
        assert result is None

    def test_get_invalid_topic_id(self):
        """유효하지 않은 topic_id로 조회"""
        with pytest.raises(ValueError):
            get_generation_status(-1)


class TestIsGenerating:
    """is_generating 함수 테스트"""

    def test_is_generating_true(self):
        """생성 중인 경우"""
        clear_all_statuses()

        update_generation_status(1, {"status": "generating"})

        assert is_generating(1) is True

    def test_is_generating_false_completed(self):
        """완료된 경우"""
        clear_all_statuses()

        update_generation_status(1, {"status": "completed"})

        assert is_generating(1) is False

    def test_is_generating_false_not_exists(self):
        """상태가 없는 경우"""
        clear_all_statuses()

        assert is_generating(1) is False

    def test_is_generating_false_failed(self):
        """실패한 경우"""
        clear_all_statuses()

        update_generation_status(1, {"status": "failed"})

        assert is_generating(1) is False


class TestInitGenerationStatus:
    """init_generation_status 함수 테스트"""

    def test_init_status_basic(self):
        """초기 상태 설정"""
        clear_all_statuses()

        result = init_generation_status(1)

        assert result["status"] == "generating"
        assert result["progress_percent"] == 0
        assert result["started_at"] is not None
        assert "artifact_id" in result

    def test_init_status_with_custom_time(self):
        """사용자 정의 시간으로 초기 상태 설정"""
        clear_all_statuses()

        custom_time = "2025-11-12T10:00:00"
        result = init_generation_status(1, started_at=custom_time)

        assert result["started_at"] == custom_time

    def test_init_status_creates_new_status(self):
        """새로운 상태를 생성하는 것을 확인"""
        clear_all_statuses()

        init_generation_status(1)

        status = get_generation_status(1)
        assert status is not None
        assert status["status"] == "generating"


class TestUpdateProgress:
    """update_progress 함수 테스트"""

    def test_update_progress_basic(self):
        """기본 진행률 업데이트"""
        clear_all_statuses()
        init_generation_status(1)

        update_progress(1, 50, "Processing content...")

        status = get_generation_status(1)
        assert status["progress_percent"] == 50
        assert status["current_step"] == "Processing content..."

    def test_update_progress_with_estimated_time(self):
        """예상 완료 시간 포함 업데이트"""
        clear_all_statuses()
        init_generation_status(1)

        estimated_time = "2025-11-12T10:30:00"
        update_progress(1, 75, "Almost done", estimated_time)

        status = get_generation_status(1)
        assert status["progress_percent"] == 75
        assert status["estimated_completion"] == estimated_time

    def test_update_progress_invalid_percent(self):
        """유효하지 않은 진행률"""
        clear_all_statuses()
        init_generation_status(1)

        with pytest.raises(ValueError):
            update_progress(1, 101, "Invalid")

        with pytest.raises(ValueError):
            update_progress(1, -1, "Invalid")

    def test_update_progress_nonexistent_status(self):
        """존재하지 않는 상태에 업데이트"""
        clear_all_statuses()

        with pytest.raises(ValueError):
            update_progress(999, 50, "Processing")


class TestMarkCompleted:
    """mark_completed 함수 테스트"""

    def test_mark_completed_basic(self):
        """기본 완료 표시"""
        clear_all_statuses()
        init_generation_status(1)

        mark_completed(1, artifact_id=123)

        status = get_generation_status(1)
        assert status["status"] == "completed"
        assert status["progress_percent"] == 100
        assert status["artifact_id"] == 123
        assert status["completed_at"] is not None

    def test_mark_completed_with_custom_time(self):
        """사용자 정의 완료 시간"""
        clear_all_statuses()
        init_generation_status(1)

        custom_time = "2025-11-12T10:30:00"
        mark_completed(1, artifact_id=123, completed_at=custom_time)

        status = get_generation_status(1)
        assert status["completed_at"] == custom_time

    def test_mark_completed_nonexistent_status(self):
        """존재하지 않는 상태에 완료 표시"""
        clear_all_statuses()

        with pytest.raises(ValueError):
            mark_completed(999, artifact_id=123)


class TestMarkFailed:
    """mark_failed 함수 테스트"""

    def test_mark_failed_basic(self):
        """기본 실패 표시"""
        clear_all_statuses()
        init_generation_status(1)

        mark_failed(1, "Claude API timeout")

        status = get_generation_status(1)
        assert status["status"] == "failed"
        assert status["error_message"] == "Claude API timeout"
        assert "failed_at" in status

    def test_mark_failed_with_custom_time(self):
        """사용자 정의 실패 시간"""
        clear_all_statuses()
        init_generation_status(1)

        custom_time = "2025-11-12T10:20:00"
        mark_failed(1, "Error occurred", failed_at=custom_time)

        status = get_generation_status(1)
        assert status["failed_at"] == custom_time

    def test_mark_failed_nonexistent_status(self):
        """존재하지 않는 상태에 실패 표시"""
        clear_all_statuses()

        with pytest.raises(ValueError):
            mark_failed(999, "Error")


class TestClearGenerationStatus:
    """clear_generation_status 함수 테스트"""

    def test_clear_status_basic(self):
        """기본 상태 삭제"""
        clear_all_statuses()
        update_generation_status(1, {"status": "generating"})

        clear_generation_status(1)

        assert get_generation_status(1) is None

    def test_clear_nonexistent_status(self):
        """존재하지 않는 상태 삭제 시도"""
        clear_all_statuses()

        # 에러 없이 수행되어야 함
        clear_generation_status(999)

        assert get_generation_status(999) is None


class TestGetAllStatuses:
    """get_all_statuses 함수 테스트"""

    def test_get_all_statuses_empty(self):
        """빈 상태 목록 조회"""
        clear_all_statuses()

        result = get_all_statuses()
        assert result == {}

    def test_get_all_statuses_multiple(self):
        """여러 상태 조회"""
        clear_all_statuses()

        update_generation_status(1, {"status": "generating"})
        update_generation_status(2, {"status": "completed"})
        update_generation_status(3, {"status": "failed"})

        result = get_all_statuses()

        assert len(result) == 3
        assert 1 in result
        assert 2 in result
        assert 3 in result

    def test_get_all_statuses_returns_copy(self):
        """복사본을 반환하는 것을 확인"""
        clear_all_statuses()

        update_generation_status(1, {"status": "generating"})

        result1 = get_all_statuses()
        result1[1]["status"] = "modified"

        result2 = get_all_statuses()

        # 원본이 수정되지 않았는지 확인
        assert result2[1]["status"] == "generating"


class TestGetStatusCount:
    """get_status_count 함수 테스트"""

    def test_get_status_count_empty(self):
        """빈 상태의 개수"""
        clear_all_statuses()

        count = get_status_count()
        assert count == 0

    def test_get_status_count_multiple(self):
        """여러 상태의 개수"""
        clear_all_statuses()

        for i in range(1, 6):
            update_generation_status(i, {"status": "generating"})

        count = get_status_count()
        assert count == 5

    def test_get_status_count_after_clear(self):
        """삭제 후 개수"""
        clear_all_statuses()

        update_generation_status(1, {"status": "generating"})
        assert get_status_count() == 1

        clear_generation_status(1)
        assert get_status_count() == 0


class TestClearAllStatuses:
    """clear_all_statuses 함수 테스트"""

    def test_clear_all_statuses(self):
        """모든 상태 삭제"""
        clear_all_statuses()

        for i in range(1, 6):
            update_generation_status(i, {"status": "generating"})

        assert get_status_count() == 5

        clear_all_statuses()

        assert get_status_count() == 0


class TestWorkflow:
    """전체 워크플로우 테스트"""

    def test_complete_workflow(self):
        """초기화 → 진행 → 완료의 전체 워크플로우"""
        clear_all_statuses()

        # 1. 초기화
        init_generation_status(1)
        assert is_generating(1) is True

        # 2. 진행 업데이트
        update_progress(1, 25, "Starting...")
        status = get_generation_status(1)
        assert status["progress_percent"] == 25

        update_progress(1, 50, "Processing...")
        status = get_generation_status(1)
        assert status["progress_percent"] == 50

        # 3. 완료
        mark_completed(1, artifact_id=123)
        status = get_generation_status(1)
        assert status["status"] == "completed"
        assert is_generating(1) is False

    def test_failure_workflow(self):
        """초기화 → 진행 → 실패의 전체 워크플로우"""
        clear_all_statuses()

        # 1. 초기화
        init_generation_status(1)
        assert is_generating(1) is True

        # 2. 진행 업데이트
        update_progress(1, 30, "Processing...")

        # 3. 실패
        mark_failed(1, "Unexpected error")
        status = get_generation_status(1)
        assert status["status"] == "failed"
        assert is_generating(1) is False
        assert "Unexpected error" in status["error_message"]
