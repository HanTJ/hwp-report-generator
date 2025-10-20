#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
기존 users 테이블에 password_reset_required 컬럼 추가
"""
import sqlite3
import os

DB_PATH = "data/hwp_reports.db"

def migrate():
    """데이터베이스 마이그레이션 실행"""
    if not os.path.exists(DB_PATH):
        print("❌ 데이터베이스 파일이 존재하지 않습니다.")
        print("먼저 'uv run python init_db.py'를 실행하세요.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # password_reset_required 컬럼이 이미 있는지 확인
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'password_reset_required' in columns:
            print("✅ password_reset_required 컬럼이 이미 존재합니다.")
        else:
            # 컬럼 추가
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN password_reset_required BOOLEAN DEFAULT 0
            """)
            conn.commit()
            print("✅ password_reset_required 컬럼이 추가되었습니다.")

        print("\n마이그레이션이 완료되었습니다!")

    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {str(e)}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
