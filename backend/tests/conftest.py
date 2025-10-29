"""
Pytest fixtures 및 설정
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from fastapi.testclient import TestClient

# 환경 변수 로드
load_dotenv(find_dotenv())

# PATH_PROJECT_HOME 설정
path_project_home = os.getenv("PATH_PROJECT_HOME")
if path_project_home and path_project_home not in sys.path:
    sys.path.insert(0, path_project_home)

from app.main import app
from app.database.connection import get_db_connection, init_db
from app.database.user_db import UserDB
from app.models.user import UserCreate
from app.utils.auth import hash_password


@pytest.fixture(scope="function")
def test_db():
    """
    테스트용 SQLite 데이터베이스 생성
    """
    # 임시 DB 파일 생성
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # 원래 DB_PATH 백업
    from app.database import connection
    original_db_path = connection.DB_PATH
    connection.DB_PATH = db_path

    # 테스트 DB 초기화
    init_db()

    yield db_path

    # 정리
    connection.DB_PATH = original_db_path
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_db):
    """
    FastAPI 테스트 클라이언트
    """
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """
    테스트 사용자 데이터
    """
    return {
        "email": "test@example.com",
        "username": "테스트사용자",
        "password": "Test1234!@#"
    }


@pytest.fixture
def test_admin_data():
    """
    테스트 관리자 데이터
    """
    return {
        "email": "admin@example.com",
        "username": "관리자",
        "password": "Admin1234!@#"
    }


@pytest.fixture
def create_test_user(test_db, test_user_data):
    """
    테스트 사용자 생성
    """
    user_create = UserCreate(**test_user_data)
    hashed_password = hash_password(test_user_data["password"])
    user = UserDB.create_user(user_create, hashed_password)

    # 사용자 활성화
    from app.models.user import UserUpdate
    UserDB.update_user(user.id, UserUpdate(is_active=True))

    return user


@pytest.fixture
def create_test_admin(test_db, test_admin_data):
    """
    테스트 관리자 생성
    """
    admin_create = UserCreate(**test_admin_data)
    hashed_password = hash_password(test_admin_data["password"])
    admin = UserDB.create_user(admin_create, hashed_password)

    # 관리자 권한 부여 및 활성화
    from app.models.user import UserUpdate
    UserDB.update_user(
        admin.id,
        UserUpdate(is_active=True, is_admin=True)
    )

    return admin


@pytest.fixture
def auth_headers(client, create_test_user, test_user_data):
    """
    인증 헤더 생성 (일반 사용자)
    """
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    # 표준 API 응답 형식: data 필드에서 access_token 추출
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, create_test_admin, test_admin_data):
    """
    인증 헤더 생성 (관리자)
    """
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_admin_data["email"],
            "password": test_admin_data["password"]
        }
    )
    # 표준 API 응답 형식: data 필드에서 access_token 추출
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def temp_dir():
    """
    임시 디렉토리 생성
    """
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


@pytest.fixture
def mock_claude_response():
    """
    Claude API 응답 mock
    """
    return {
        "title": "테스트 보고서",
        "summary": "테스트 요약 내용입니다.",
        "background": "테스트 배경입니다.",
        "main_content": "테스트 주요 내용입니다.",
        "conclusion": "테스트 결론입니다."
    }


@pytest.fixture
def sample_hwpx_content():
    """
    샘플 HWPX 파일 내용
    """
    return {
        "title": "테스트 보고서",
        "summary": "요약 내용",
        "background": "배경 및 목적",
        "main_content": "주요 내용",
        "conclusion": "결론 및 제언"
    }
