"""
토픽(대화 주제) API 라우터 테스트
"""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.database.topic_db import TopicDB
from app.models.topic import TopicCreate, TopicUpdate
from shared.types.enums import TopicStatus


@pytest.mark.api
class TestTopicsRouter:
    """Topics API 테스트"""

    def test_create_topic_success(self, client, auth_headers, create_test_user):
        response = client.post(
            "/api/topics",
            headers=auth_headers,
            json={
                "input_prompt": "디지털뱅킹 트렌드 분석",
                "language": "ko"
            }
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] > 0
        assert body["data"]["input_prompt"] == "디지털뱅킹 트렌드 분석"

    def test_get_my_topics_empty(self, client, auth_headers):
        response = client.get("/api/topics", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total"] == 0
        assert body["data"]["topics"] == []

    def test_get_my_topics_with_one(self, client, auth_headers, create_test_user):
        # 사전 데이터: 토픽 1건 생성
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="금융 리포트", language="ko")
        )

        response = client.get("/api/topics", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["total"] >= 1
        assert any(t["id"] == topic.id for t in body["data"]["topics"])

    def test_get_topic_not_found(self, client, auth_headers):
        response = client.get("/api/topics/999999", headers=auth_headers)
        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "TOPIC.NOT_FOUND"

    def test_get_topic_unauthorized(self, client, auth_headers, create_test_admin):
        # 관리자(다른 사용자) 소유 토픽 생성
        admin_topic = TopicDB.create_topic(
            user_id=create_test_admin.id,
            topic_data=TopicCreate(input_prompt="관리자 토픽", language="ko")
        )

        response = client.get(f"/api/topics/{admin_topic.id}", headers=auth_headers)
        assert response.status_code == 403
        body = response.json()
        assert body["error"]["code"] == "TOPIC.UNAUTHORIZED"

    def test_update_topic_success(self, client, auth_headers, create_test_user):
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="초기 토픽", language="ko")
        )

        response = client.patch(
            f"/api/topics/{topic.id}",
            headers=auth_headers,
            json={
                "generated_title": "업데이트된 제목",
                "status": "archived"
            }
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["generated_title"] == "업데이트된 제목"
        assert body["data"]["status"] == TopicStatus.ARCHIVED.value

    def test_update_topic_unauthorized(self, client, auth_headers, create_test_admin):
        admin_topic = TopicDB.create_topic(
            user_id=create_test_admin.id,
            topic_data=TopicCreate(input_prompt="관리자 토픽", language="ko")
        )

        response = client.patch(
            f"/api/topics/{admin_topic.id}",
            headers=auth_headers,
            json={"generated_title": "허용되지 않음"}
        )

        assert response.status_code == 403
        body = response.json()
        assert body["error"]["code"] == "TOPIC.UNAUTHORIZED"

    def test_delete_topic_success(self, client, auth_headers, create_test_user):
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="삭제 대상", language="ko")
        )

        response = client.delete(f"/api/topics/{topic.id}", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["message"]

    def test_delete_topic_not_found(self, client, auth_headers):
        response = client.delete("/api/topics/123456789", headers=auth_headers)
        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "TOPIC.NOT_FOUND"

    @patch('app.routers.topics.ClaudeClient')
    def test_generate_topic_report_success(
        self,
        mock_claude_class,
        client,
        auth_headers,
        create_test_user,
        temp_dir
    ):
        """보고서 생성 성공 테스트"""
        # Mock Claude response
        mock_claude_instance = MagicMock()
        mock_claude_instance.generate_report.return_value = {
            "title": "디지털뱅킹 트렌드 분석 보고서",
            "title_summary": "요약",
            "summary": "2025년 디지털뱅킹 주요 트렌드입니다.",
            "title_background": "배경 및 목적",
            "background": "디지털 전환이 가속화되고 있습니다.",
            "title_main_content": "주요 내용",
            "main_content": "AI 기반 금융 서비스가 확대되고 있습니다.",
            "title_conclusion": "결론 및 제언",
            "conclusion": "디지털 전환에 적극 대응해야 합니다."
        }
        mock_claude_instance.model = "claude-sonnet-4-5-20250929"
        mock_claude_instance.last_input_tokens = 1000
        mock_claude_instance.last_output_tokens = 2000
        mock_claude_class.return_value = mock_claude_instance

        # API 호출
        response = client.post(
            "/api/topics/generate",
            headers=auth_headers,
            json={
                "input_prompt": "디지털뱅킹 트렌드 분석",
                "language": "ko"
            }
        )

        # 검증
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "topic_id" in body["data"]
        assert "md_path" in body["data"]
        assert body["data"]["topic_id"] > 0

        # Claude가 호출되었는지 확인
        mock_claude_instance.generate_report.assert_called_once_with("디지털뱅킹 트렌드 분석")

        # DB에 저장되었는지 확인
        topic = TopicDB.get_topic_by_id(body["data"]["topic_id"])
        assert topic is not None
        assert topic.input_prompt == "디지털뱅킹 트렌드 분석"
        assert topic.generated_title == "디지털뱅킹 트렌드 분석 보고서"

    def test_generate_topic_report_empty_prompt(self, client, auth_headers):
        """빈 입력 프롬프트 테스트 (Pydantic 검증)"""
        response = client.post(
            "/api/topics/generate",
            headers=auth_headers,
            json={
                "input_prompt": "",
                "language": "ko"
            }
        )

        # Pydantic validation error (422)
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body

    def test_generate_topic_report_whitespace_only(self, client, auth_headers):
        """공백만 있는 입력 프롬프트 테스트"""
        response = client.post(
            "/api/topics/generate",
            headers=auth_headers,
            json={
                "input_prompt": "   ",
                "language": "ko"
            }
        )

        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert body["error"]["httpStatus"] == 400

    @patch('app.routers.topics.ClaudeClient')
    def test_generate_topic_report_claude_error(
        self,
        mock_claude_class,
        client,
        auth_headers
    ):
        """Claude API 오류 테스트"""
        # Mock Claude to raise an exception
        mock_claude_instance = MagicMock()
        mock_claude_instance.generate_report.side_effect = Exception("Claude API Error")
        mock_claude_class.return_value = mock_claude_instance

        response = client.post(
            "/api/topics/generate",
            headers=auth_headers,
            json={
                "input_prompt": "테스트 주제",
                "language": "ko"
            }
        )

        assert response.status_code == 500
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "REPORT.GENERATION_FAILED"
        assert body["error"]["httpStatus"] == 500

