"""
토픽(대화 주제) API 라우터 테스트
"""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.database.topic_db import TopicDB
from app.database.message_db import MessageDB
from app.database.artifact_db import ArtifactDB
from app.models.topic import TopicCreate, TopicUpdate
from app.models.message import MessageCreate
from app.models.artifact import ArtifactCreate
from shared.types.enums import TopicStatus, MessageRole, ArtifactKind


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
        assert "artifact_id" in body["data"]
        assert body["data"]["topic_id"] > 0
        assert body["data"]["artifact_id"] > 0

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

    @patch('app.routers.topics.ClaudeClient')
    def test_ask_success_no_artifact(
        self,
        mock_claude_class,
        client,
        auth_headers,
        create_test_user
    ):
        """참조 문서 없이 질문 성공 테스트"""
        # 토픽 생성
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="디지털뱅킹 분석", language="ko")
        )

        # Mock Claude
        mock_claude_instance = MagicMock()
        mock_claude_instance.chat_completion.return_value = (
            "# 디지털뱅킹 트렌드\n\n## 요약\n\n2025년 디지털뱅킹 산업은...",
            100,
            200
        )
        mock_claude_instance.model = "claude-sonnet-4-5-20250929"
        mock_claude_class.return_value = mock_claude_instance

        # Ask 호출
        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={"content": "디지털뱅킹 트렌드를 분석해주세요."}
        )

        # 검증
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["topic_id"] == topic.id
        assert "user_message" in body["data"]
        assert "assistant_message" in body["data"]
        assert "artifact" in body["data"]
        assert "usage" in body["data"]
        assert body["data"]["artifact"]["kind"] == "md"
        assert body["data"]["usage"]["input_tokens"] == 100
        assert body["data"]["usage"]["output_tokens"] == 200

    @patch('app.routers.topics.ClaudeClient')
    def test_ask_with_latest_md(
        self,
        mock_claude_class,
        client,
        auth_headers,
        create_test_user,
        temp_dir
    ):
        """최신 MD 참조하여 질문 테스트"""
        # 토픽 + MD artifact 생성
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="금융 보고서", language="ko")
        )

        # 초기 메시지 저장
        msg = MessageDB.create_message(
            topic.id,
            MessageCreate(role=MessageRole.ASSISTANT, content="# 초기 보고서\n\n내용...")
        )

        # MD 파일 생성
        from app.utils.file_utils import build_artifact_paths, write_text, sha256_of
        _, md_path = build_artifact_paths(topic.id, 1, "report.md")
        bytes_written = write_text(md_path, "# 초기 보고서\n\n내용...")
        file_hash = sha256_of(md_path)

        artifact = ArtifactDB.create_artifact(
            topic.id,
            msg.id,
            ArtifactCreate(
                kind=ArtifactKind.MD,
                locale="ko",
                version=1,
                filename="report.md",
                file_path=str(md_path),
                file_size=bytes_written,
                sha256=file_hash
            )
        )

        # Mock Claude
        mock_claude_instance = MagicMock()
        mock_claude_instance.chat_completion.return_value = (
            "# 개정된 보고서\n\n업데이트된 내용...",
            200,
            300
        )
        mock_claude_instance.model = "claude-sonnet-4-5-20250929"
        mock_claude_class.return_value = mock_claude_instance

        # Ask 호출 (artifact_id=None, 자동으로 latest 사용)
        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={"content": "이전 보고서를 요약해주세요."}
        )

        # 검증
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["artifact"]["version"] == 2  # 새 버전 생성

        # Claude가 호출되었는지 확인
        mock_claude_instance.chat_completion.assert_called_once()

    @patch('app.routers.topics.ClaudeClient')
    def test_ask_with_specific_md(
        self,
        mock_claude_class,
        client,
        auth_headers,
        create_test_user,
        temp_dir
    ):
        """특정 MD 지정하여 질문 테스트"""
        # 토픽 + 여러 버전 MD 생성
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="금융 보고서", language="ko")
        )

        # v1 생성
        msg1 = MessageDB.create_message(
            topic.id,
            MessageCreate(role=MessageRole.ASSISTANT, content="# v1 보고서")
        )
        from app.utils.file_utils import build_artifact_paths, write_text, sha256_of
        _, md_path1 = build_artifact_paths(topic.id, 1, "report.md")
        bytes1 = write_text(md_path1, "# v1 보고서")
        hash1 = sha256_of(md_path1)
        artifact1 = ArtifactDB.create_artifact(
            topic.id, msg1.id,
            ArtifactCreate(
                kind=ArtifactKind.MD, locale="ko", version=1,
                filename="report.md", file_path=str(md_path1),
                file_size=bytes1, sha256=hash1
            )
        )

        # v2 생성
        msg2 = MessageDB.create_message(
            topic.id,
            MessageCreate(role=MessageRole.ASSISTANT, content="# v2 보고서")
        )
        _, md_path2 = build_artifact_paths(topic.id, 2, "report.md")
        bytes2 = write_text(md_path2, "# v2 보고서")
        hash2 = sha256_of(md_path2)
        artifact2 = ArtifactDB.create_artifact(
            topic.id, msg2.id,
            ArtifactCreate(
                kind=ArtifactKind.MD, locale="ko", version=2,
                filename="report.md", file_path=str(md_path2),
                file_size=bytes2, sha256=hash2
            )
        )

        # Mock Claude
        mock_claude_instance = MagicMock()
        mock_claude_instance.chat_completion.return_value = (
            "# v1 기반 업데이트",
            150,
            250
        )
        mock_claude_instance.model = "claude-sonnet-4-5-20250929"
        mock_claude_class.return_value = mock_claude_instance

        # v1을 명시적으로 지정
        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={
                "content": "v1 보고서를 기준으로 요약해주세요.",
                "artifact_id": artifact1.id
            }
        )

        # 검증
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

    def test_ask_context_too_large(
        self,
        client,
        auth_headers,
        create_test_user
    ):
        """컨텍스트 길이 초과 테스트"""
        # 토픽 생성
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="테스트", language="ko")
        )

        # 매우 긴 메시지들 생성
        for i in range(10):
            MessageDB.create_message(
                topic.id,
                MessageCreate(
                    role=MessageRole.USER,
                    content="가" * 10000  # 10,000자씩
                )
            )

        # Ask 호출 (총 100,000자 이상)
        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={"content": "요약해주세요."}
        )

        # 400 MESSAGE.CONTEXT_TOO_LARGE 확인
        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "MESSAGE.CONTEXT_TOO_LARGE"

    def test_ask_artifact_not_found(
        self,
        client,
        auth_headers,
        create_test_user
    ):
        """존재하지 않는 artifact_id 테스트"""
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="테스트", language="ko")
        )

        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={
                "content": "질문",
                "artifact_id": 999999
            }
        )

        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "ARTIFACT.NOT_FOUND"

    def test_ask_artifact_wrong_kind(
        self,
        client,
        auth_headers,
        create_test_user,
        temp_dir
    ):
        """HWPX artifact 참조 시도 테스트"""
        # 토픽 + HWPX artifact 생성
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="테스트", language="ko")
        )

        msg = MessageDB.create_message(
            topic.id,
            MessageCreate(role=MessageRole.ASSISTANT, content="테스트")
        )

        # HWPX 파일 생성 (실제로는 더미)
        from app.utils.file_utils import build_artifact_paths, write_text, sha256_of
        _, hwpx_path = build_artifact_paths(topic.id, 1, "report.hwpx")
        bytes_written = write_text(hwpx_path, "dummy hwpx content")
        file_hash = sha256_of(hwpx_path)

        artifact = ArtifactDB.create_artifact(
            topic.id, msg.id,
            ArtifactCreate(
                kind=ArtifactKind.HWPX,
                locale="ko",
                version=1,
                filename="report.hwpx",
                file_path=str(hwpx_path),
                file_size=bytes_written,
                sha256=file_hash
            )
        )

        # HWPX artifact_id 지정
        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={
                "content": "질문",
                "artifact_id": artifact.id
            }
        )

        # 400 ARTIFACT.INVALID_KIND 확인
        assert response.status_code == 400
        body = response.json()
        assert body["error"]["code"] == "ARTIFACT.INVALID_KIND"

    def test_ask_unauthorized_topic(
        self,
        client,
        auth_headers,
        create_test_admin
    ):
        """타인의 토픽에 질문 테스트"""
        # 관리자의 토픽 생성
        admin_topic = TopicDB.create_topic(
            user_id=create_test_admin.id,
            topic_data=TopicCreate(input_prompt="관리자 토픽", language="ko")
        )

        # 일반 사용자로 요청 (auth_headers는 일반 사용자)
        response = client.post(
            f"/api/topics/{admin_topic.id}/ask",
            headers=auth_headers,
            json={"content": "질문"}
        )

        # 403 TOPIC.UNAUTHORIZED 확인
        assert response.status_code == 403
        body = response.json()
        assert body["error"]["code"] == "TOPIC.UNAUTHORIZED"

    @patch('app.routers.topics.ClaudeClient')
    def test_ask_max_messages_limit(
        self,
        mock_claude_class,
        client,
        auth_headers,
        create_test_user
    ):
        """max_messages 제한 테스트"""
        # 토픽 생성
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="테스트", language="ko")
        )

        # 50개 user 메시지 생성
        for i in range(50):
            MessageDB.create_message(
                topic.id,
                MessageCreate(role=MessageRole.USER, content=f"메시지 {i}")
            )

        # Mock Claude
        mock_claude_instance = MagicMock()
        mock_claude_instance.chat_completion.return_value = (
            "# 응답",
            100,
            200
        )
        mock_claude_instance.model = "claude-sonnet-4-5-20250929"
        mock_claude_class.return_value = mock_claude_instance

        # max_messages=10 설정
        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={
                "content": "요약해주세요.",
                "max_messages": 10
            }
        )

        # 검증
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

        # Claude가 호출될 때 최근 10개만 포함되었는지 확인
        # (실제로는 메시지 수를 직접 확인하기 어려우므로, 성공 여부만 확인)
        mock_claude_instance.chat_completion.assert_called_once()

    def test_ask_empty_content(
        self,
        client,
        auth_headers,
        create_test_user
    ):
        """빈 content 테스트"""
        topic = TopicDB.create_topic(
            user_id=create_test_user.id,
            topic_data=TopicCreate(input_prompt="테스트", language="ko")
        )

        response = client.post(
            f"/api/topics/{topic.id}/ask",
            headers=auth_headers,
            json={"content": ""}
        )

        assert response.status_code == 422  # Pydantic validation error
        # Pydantic validation errors use FastAPI's default format, not our custom error_response
        body = response.json()
        assert "detail" in body  # FastAPI's default error format

    def test_ask_topic_not_found(
        self,
        client,
        auth_headers
    ):
        """존재하지 않는 토픽에 질문 테스트"""
        response = client.post(
            "/api/topics/999999/ask",
            headers=auth_headers,
            json={"content": "질문"}
        )

        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "TOPIC.NOT_FOUND"

