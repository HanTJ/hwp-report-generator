"""
토픽(대화 주제) API 라우터 테스트
"""
import pytest

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

