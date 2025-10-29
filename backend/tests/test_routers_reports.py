"""
보고서 API 라우터 테스트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from app.database.report_db import ReportDB
from app.models.report import ReportCreate


@pytest.fixture
def mock_claude_client_response():
    """Claude Client mock 응답 fixture"""
    return {
        "title": "테스트 보고서",
        "title_background": "배경",
        "background": "배경 내용",
        "title_main_content": "주요 내용",
        "main_content": "주요 내용",
        "title_conclusion": "결론",
        "conclusion": "결론 내용",
        "title_summary": "요약",
        "summary": "요약 내용"
    }


@pytest.fixture
def mock_hwp_handler_path(temp_dir):
    """HWP Handler mock 파일 경로 fixture"""
    file_path = os.path.join(temp_dir, "report_test.hwpx")
    # 빈 파일 생성
    with open(file_path, 'wb') as f:
        f.write(b'test hwpx content')
    return file_path


@pytest.mark.api
class TestGenerateReportEndpoint:
    """POST /api/reports/generate 테스트"""

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_generate_report_success(self, mock_hwp_handler_class, mock_claude_client_class,
                                     client, auth_headers, mock_claude_client_response, mock_hwp_handler_path):
        """보고서 생성 성공 테스트"""
        # Mock ClaudeClient 설정
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.return_value = mock_claude_client_response
        mock_claude_instance.last_input_tokens = 1500
        mock_claude_instance.last_output_tokens = 3200
        mock_claude_instance.last_total_tokens = 4700

        # Mock HWPHandler 설정
        mock_hwp_instance = Mock()
        mock_hwp_handler_class.return_value = mock_hwp_instance
        mock_hwp_instance.generate_report.return_value = mock_hwp_handler_path

        response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "2025년 디지털 뱅킹 트렌드"}
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        assert "id" in data
        assert "filename" in data
        assert "file_size" in data
        assert data["topic"] == "2025년 디지털 뱅킹 트렌드"
        assert data["title"] == "테스트 보고서"

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_generate_report_saves_to_db(self, mock_hwp_handler_class, mock_claude_client_class,
                                         client, auth_headers, test_db, mock_claude_client_response, mock_hwp_handler_path):
        """DB에 보고서 정보 저장 확인"""
        # Mock 설정
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.return_value = mock_claude_client_response
        mock_claude_instance.last_input_tokens = 1000
        mock_claude_instance.last_output_tokens = 2000
        mock_claude_instance.last_total_tokens = 3000

        mock_hwp_instance = Mock()
        mock_hwp_handler_class.return_value = mock_hwp_instance
        mock_hwp_instance.generate_report.return_value = mock_hwp_handler_path

        response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "테스트 주제"}
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        data = result["data"]

        # DB에 저장되었는지 확인
        report = ReportDB.get_report_by_id(data["id"])
        assert report is not None
        assert report.topic == "테스트 주제"
        assert report.title == "테스트 보고서"

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_generate_report_tracks_token_usage(self, mock_hwp_handler_class, mock_claude_client_class,
                                                client, auth_headers, test_db, mock_claude_client_response, mock_hwp_handler_path):
        """토큰 사용량 저장 확인"""
        # Mock 설정
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.return_value = mock_claude_client_response
        mock_claude_instance.last_input_tokens = 1500
        mock_claude_instance.last_output_tokens = 3200
        mock_claude_instance.last_total_tokens = 4700

        mock_hwp_instance = Mock()
        mock_hwp_handler_class.return_value = mock_hwp_instance
        mock_hwp_instance.generate_report.return_value = mock_hwp_handler_path

        response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "테스트"}
        )

        assert response.status_code == 200

        # 응답에서 user_id 추출
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        user_id = data["user_id"]

        # 토큰 사용량이 DB에 저장되었는지 확인 (실제 메서드 사용)
        from app.database.token_usage_db import TokenUsageDB

        usage_list = TokenUsageDB.get_usage_by_user(user_id)
        assert len(usage_list) > 0

        latest_usage = usage_list[0]
        assert latest_usage.input_tokens == 1500
        assert latest_usage.output_tokens == 3200
        assert latest_usage.total_tokens == 4700

    @patch('app.routers.reports.ClaudeClient')
    def test_generate_report_claude_api_error(self, mock_claude_client_class, client, auth_headers):
        """Claude API 실패 시 500 에러"""
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.side_effect = Exception("Claude API Error")

        response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "테스트 주제"}
        )

        assert response.status_code == 500

    def test_generate_report_unauthorized(self, client):
        """인증 없이 호출 시 403 에러"""
        response = client.post(
            "/api/reports/generate",
            json={"topic": "테스트"}
        )

        assert response.status_code == 403

    def test_generate_report_empty_topic(self, client, auth_headers):
        """빈 주제로 호출 시 422 에러"""
        response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": ""}
        )

        assert response.status_code == 422


@pytest.mark.api
class TestGetMyReportsEndpoint:
    """GET /api/reports/my-reports 테스트"""

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_get_my_reports_success(self, mock_hwp_handler_class, mock_claude_client_class,
                                    client, auth_headers, create_test_user, test_db,
                                    mock_claude_client_response, mock_hwp_handler_path):
        """내 보고서 목록 조회 성공"""
        # 먼저 보고서 생성
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.return_value = mock_claude_client_response
        mock_claude_instance.last_input_tokens = 1000
        mock_claude_instance.last_output_tokens = 2000
        mock_claude_instance.last_total_tokens = 3000

        mock_hwp_instance = Mock()
        mock_hwp_handler_class.return_value = mock_hwp_instance
        mock_hwp_instance.generate_report.return_value = mock_hwp_handler_path

        # 보고서 생성
        client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "테스트 보고서 1"}
        )

        # 목록 조회
        response = client.get("/api/reports/my-reports", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        assert "reports" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_get_my_reports_empty(self, client, auth_headers):
        """보고서가 없을 때 빈 배열 반환"""
        response = client.get("/api/reports/my-reports", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        assert data["reports"] == []
        assert data["total"] == 0

    def test_get_my_reports_unauthorized(self, client):
        """인증 없이 호출 시 403 에러"""
        response = client.get("/api/reports/my-reports")
        assert response.status_code == 403


@pytest.mark.api
class TestDownloadReportEndpoint:
    """GET /api/reports/download/{report_id} 테스트"""

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_download_report_success(self, mock_hwp_handler_class, mock_claude_client_class,
                                     client, auth_headers, create_test_user, test_db,
                                     mock_claude_client_response, mock_hwp_handler_path):
        """보고서 다운로드 성공"""
        # 보고서 생성
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.return_value = mock_claude_client_response
        mock_claude_instance.last_input_tokens = 1000
        mock_claude_instance.last_output_tokens = 2000
        mock_claude_instance.last_total_tokens = 3000

        mock_hwp_instance = Mock()
        mock_hwp_handler_class.return_value = mock_hwp_instance
        mock_hwp_instance.generate_report.return_value = mock_hwp_handler_path

        create_response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "테스트"}
        )
        report_id = create_response.json()["data"]["id"]

        # 다운로드
        response = client.get(f"/api/reports/download/{report_id}", headers=auth_headers)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
        assert "attachment" in response.headers["content-disposition"]

    def test_download_report_not_found(self, client, auth_headers):
        """존재하지 않는 보고서 다운로드 시 404"""
        response = client.get("/api/reports/download/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_download_report_unauthorized(self, client):
        """인증 없이 호출 시 403"""
        response = client.get("/api/reports/download/1")
        assert response.status_code == 403


@pytest.mark.api
@pytest.mark.skip(reason="DELETE /api/reports/{id} 엔드포인트가 아직 구현되지 않음")
class TestDeleteReportEndpoint:
    """DELETE /api/reports/{report_id} 테스트"""

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_delete_report_success(self, mock_hwp_handler_class, mock_claude_client_class,
                                   client, auth_headers, create_test_user, test_db,
                                   mock_claude_client_response, mock_hwp_handler_path):
        """보고서 삭제 성공"""
        # 보고서 생성
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.return_value = mock_claude_client_response
        mock_claude_instance.last_input_tokens = 1000
        mock_claude_instance.last_output_tokens = 2000
        mock_claude_instance.last_total_tokens = 3000

        mock_hwp_instance = Mock()
        mock_hwp_handler_class.return_value = mock_hwp_instance
        mock_hwp_instance.generate_report.return_value = mock_hwp_handler_path

        create_response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "삭제할 보고서"}
        )
        report_id = create_response.json()["data"]["id"]

        # 삭제
        response = client.delete(f"/api/reports/{report_id}", headers=auth_headers)

        assert response.status_code == 200

        # DB에서 삭제 확인
        report = ReportDB.get_report_by_id(report_id)
        assert report is None

    def test_delete_report_not_found(self, client, auth_headers):
        """존재하지 않는 보고서 삭제 시 404"""
        response = client.delete("/api/reports/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_report_unauthorized(self, client):
        """인증 없이 호출 시 403"""
        response = client.delete("/api/reports/1")
        assert response.status_code == 403


@pytest.mark.integration
class TestReportsEndToEnd:
    """보고서 API 전체 플로우 통합 테스트"""

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_full_report_lifecycle(self, mock_hwp_handler_class, mock_claude_client_class,
                                   client, auth_headers, test_db, temp_dir,
                                   mock_claude_client_response, mock_hwp_handler_path):
        """생성 → 조회 → 다운로드 전체 플로우 (삭제 기능은 미구현)"""
        # Mock 설정
        mock_claude_instance = Mock()
        mock_claude_client_class.return_value = mock_claude_instance
        mock_claude_instance.generate_report.return_value = mock_claude_client_response
        mock_claude_instance.last_input_tokens = 1000
        mock_claude_instance.last_output_tokens = 2000
        mock_claude_instance.last_total_tokens = 3000

        mock_hwp_instance = Mock()
        mock_hwp_handler_class.return_value = mock_hwp_instance
        mock_hwp_instance.generate_report.return_value = mock_hwp_handler_path

        # 1. 보고서 생성
        create_response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "전체 플로우 테스트"}
        )
        assert create_response.status_code == 200
        report_id = create_response.json()["data"]["id"]

        # 2. 내 보고서 목록에서 확인
        list_response = client.get("/api/reports/my-reports", headers=auth_headers)
        assert list_response.status_code == 200
        reports = list_response.json()["data"]["reports"]
        assert any(r["id"] == report_id for r in reports)

        # 3. 다운로드
        download_response = client.get(f"/api/reports/download/{report_id}", headers=auth_headers)
        assert download_response.status_code == 200

        # Note: DELETE 엔드포인트는 아직 구현되지 않음
