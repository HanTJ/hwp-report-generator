#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""
import os
from database import init_db
from database.user_db import UserDB
from models.user import UserCreate, UserUpdate
from utils.auth import hash_password
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def main():
    print("데이터베이스를 초기화합니다...")

    # 필요한 디렉토리 생성
    os.makedirs("data", exist_ok=True)

    # 데이터베이스 초기화
    init_db()
    print("✅ 데이터베이스 테이블이 생성되었습니다.")

    # 관리자 계정 생성
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_username = os.getenv("ADMIN_USERNAME")

    if not admin_email:
        raise ValueError("ADMIN_EMAIL 환경 변수가 설정되지 않았습니다.")
    if not admin_password:
        raise ValueError("ADMIN_PASSWORD 환경 변수가 설정되지 않았습니다.")
    if not admin_username:
        raise ValueError("ADMIN_USERNAME 환경 변수가 설정되지 않았습니다.")

    # 기존 관리자 확인
    existing_admin = UserDB.get_user_by_email(admin_email)
    if existing_admin:
        print(f"✅ 관리자 계정이 이미 존재합니다: {admin_email}")
    else:
        # 관리자 계정 생성
        admin_data = UserCreate(
            email=admin_email,
            username=admin_username,
            password=admin_password
        )

        hashed_password = hash_password(admin_password)
        admin_user = UserDB.create_user(admin_data, hashed_password)

        # 관리자 권한 및 활성화
        update = UserUpdate(is_active=True, is_admin=True)
        UserDB.update_user(admin_user.id, update)

        print(f"✅ 관리자 계정이 생성되었습니다:")
        print(f"   이메일: {admin_email}")
        print(f"   비밀번호: {admin_password}")

    print("\n데이터베이스 초기화가 완료되었습니다!")

if __name__ == "__main__":
    main()
