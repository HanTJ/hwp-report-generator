"""
메시지 API 라우터 테스트
"""
import pytest

from app.database.topic_db import TopicDB
from app.database.message_db import MessageDB
from app.models.topic import TopicCreate
from app.models.message import MessageCreate
from shared.types.enums import MessageRole


@pytest.mark.api
class TestMessagesRouter:
    """Messages API 테스트"""

    def _create_user_topic(self, user_id):
        return TopicDB.create_topic(user_id=user_id, topic_data=TopicCreate(input_prompt="테스트 토픽", language="ko"))

    def test_create_message_success(self, client, auth_headers, create_test_user):
        topic = self._create_user_topic(create_test_user.id)
        response = client.post(
            f"/api/topics/{topic.id}/messages",
            headers=auth_headers,
            json={"role": "user", "content": "보고서를 작성해 주세요."}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["topic_id"] == topic.id
        assert body["data"]["role"] == MessageRole.USER.value

    def test_create_message_topic_not_found(self, client, auth_headers):
        response = client.post(
            "/api/topics/999999/messages",
            headers=auth_headers,
            json={"role": "user", "content": "내용"}
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TOPIC.NOT_FOUND"

    def test_create_message_unauthorized(self, client, auth_headers, create_test_admin):
        admin_topic = self._create_user_topic(create_test_admin.id)
        response = client.post(
            f"/api/topics/{admin_topic.id}/messages",
            headers=auth_headers,
            json={"role": "user", "content": "권한 없음"}
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "TOPIC.UNAUTHORIZED"

    def test_get_messages_success(self, client, auth_headers, create_test_user):
        topic = self._create_user_topic(create_test_user.id)
        MessageDB.create_message(topic.id, MessageCreate(role=MessageRole.USER, content="첫번째"))
        MessageDB.create_message(topic.id, MessageCreate(role=MessageRole.ASSISTANT, content="두번째"))

        response = client.get(f"/api/topics/{topic.id}/messages", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total"] == 2
        seqs = [m["seq_no"] for m in body["data"]["messages"]]
        assert seqs == sorted(seqs)

    def test_get_message_not_found(self, client, auth_headers, create_test_user):
        topic = self._create_user_topic(create_test_user.id)
        response = client.get(f"/api/topics/{topic.id}/messages/999999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "MESSAGE.NOT_FOUND"

    def test_get_message_wrong_topic(self, client, auth_headers, create_test_user):
        topic1 = self._create_user_topic(create_test_user.id)
        topic2 = self._create_user_topic(create_test_user.id)
        msg = MessageDB.create_message(topic1.id, MessageCreate(role=MessageRole.USER, content="t1 msg"))

        response = client.get(f"/api/topics/{topic2.id}/messages/{msg.id}", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "MESSAGE.NOT_FOUND"

    def test_delete_message_success(self, client, auth_headers, create_test_user):
        topic = self._create_user_topic(create_test_user.id)
        msg = MessageDB.create_message(topic.id, MessageCreate(role=MessageRole.USER, content="삭제대상"))

        response = client.delete(f"/api/topics/{topic.id}/messages/{msg.id}", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["message"]

    def test_delete_message_unauthorized(self, client, auth_headers, create_test_admin):
        admin_topic = self._create_user_topic(create_test_admin.id)
        msg = MessageDB.create_message(admin_topic.id, MessageCreate(role=MessageRole.USER, content="관리자 메시지"))

        response = client.delete(f"/api/topics/{admin_topic.id}/messages/{msg.id}", headers=auth_headers)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "TOPIC.UNAUTHORIZED"

    def test_delete_message_not_found(self, client, auth_headers, create_test_user):
        topic = self._create_user_topic(create_test_user.id)
        response = client.delete(f"/api/topics/{topic.id}/messages/999999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "MESSAGE.NOT_FOUND"

    def test_get_messages_empty(self, client, auth_headers, create_test_user):
        """메시지가 없는 토픽 조회"""
        topic = self._create_user_topic(create_test_user.id)
        response = client.get(f"/api/topics/{topic.id}/messages", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total"] == 0
        assert body["data"]["messages"] == []

    def test_get_messages_with_pagination(self, client, auth_headers, create_test_user):
        """페이지네이션 테스트 (limit, offset)"""
        topic = self._create_user_topic(create_test_user.id)
        # 5개 메시지 생성
        for i in range(5):
            MessageDB.create_message(topic.id, MessageCreate(role=MessageRole.USER, content=f"메시지 {i+1}"))

        # limit=2, offset=0
        response = client.get(f"/api/topics/{topic.id}/messages?limit=2&offset=0", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]["messages"]) == 2
        assert body["data"]["total"] == 5

        # limit=2, offset=2
        response = client.get(f"/api/topics/{topic.id}/messages?limit=2&offset=2", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]["messages"]) == 2
        assert body["data"]["total"] == 5

    def test_get_messages_topic_not_found(self, client, auth_headers):
        """존재하지 않는 토픽의 메시지 조회"""
        response = client.get("/api/topics/999999/messages", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TOPIC.NOT_FOUND"

    def test_get_messages_unauthorized(self, client, auth_headers, create_test_admin):
        """권한 없는 토픽의 메시지 조회"""
        admin_topic = self._create_user_topic(create_test_admin.id)
        response = client.get(f"/api/topics/{admin_topic.id}/messages", headers=auth_headers)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "TOPIC.UNAUTHORIZED"

    def test_get_message_success(self, client, auth_headers, create_test_user):
        """단일 메시지 조회 성공"""
        topic = self._create_user_topic(create_test_user.id)
        msg = MessageDB.create_message(topic.id, MessageCreate(role=MessageRole.USER, content="단일 메시지"))

        response = client.get(f"/api/topics/{topic.id}/messages/{msg.id}", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == msg.id
        assert body["data"]["content"] == "단일 메시지"

    def test_create_message_invalid_role(self, client, auth_headers, create_test_user):
        """잘못된 role 값으로 메시지 생성"""
        topic = self._create_user_topic(create_test_user.id)
        response = client.post(
            f"/api/topics/{topic.id}/messages",
            headers=auth_headers,
            json={"role": "invalid_role", "content": "내용"}
        )
        # Pydantic validation error
        assert response.status_code == 422

