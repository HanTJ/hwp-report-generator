#!/usr/bin/env python3
"""
Chat-based report system migration script.

This script migrates the database from report-based to chat-based architecture:
- Creates new tables: topics, messages, artifacts, ai_usage, transformations
- Drops legacy tables: reports, token_usage
- Creates indexes for performance optimization
"""
import os
import sys
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# PATH_PROJECT_HOME 환경 변수 확인 및 sys.path 설정
path_project_home = os.getenv("PATH_PROJECT_HOME")
if not path_project_home:
    print("ERROR: PATH_PROJECT_HOME 환경 변수가 설정되지 않았습니다.")
    print(".env 파일에 PATH_PROJECT_HOME을 설정해주세요.")
    sys.exit(1)

# 프로젝트 루트를 sys.path에 추가
if path_project_home not in sys.path:
    sys.path.insert(0, path_project_home)

from app.database.connection import get_db_connection


def create_new_tables():
    """Creates new tables for chat-based architecture.

    Tables created:
        - topics: Conversation threads about report topics
        - messages: Chat messages (user/assistant interactions)
        - artifacts: Generated files (MD, HWPX, PDF)
        - ai_usage: AI token usage tracking per message
        - transformations: File conversion lineage (MD→HWPX, EN→KO)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Creating new tables for chat-based architecture...")

    # Topics table - 대화 주제/스레드
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            input_prompt TEXT NOT NULL,
            generated_title TEXT,
            language TEXT DEFAULT 'ko',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    print("✅ Created 'topics' table")

    # Messages table - 대화 메시지
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            seq_no INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
        )
    """)
    print("✅ Created 'messages' table")

    # Artifacts table - 생성된 파일
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            locale TEXT DEFAULT 'ko',
            version INTEGER DEFAULT 1,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            sha256 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE,
            FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE
        )
    """)
    print("✅ Created 'artifacts' table")

    # AI Usage table - AI 사용량 추적
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            latency_ms INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE,
            FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE
        )
    """)
    print("✅ Created 'ai_usage' table")

    # Transformations table - 파일 변환 이력
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transformations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_artifact_id INTEGER NOT NULL,
            to_artifact_id INTEGER NOT NULL,
            operation TEXT NOT NULL,
            params_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_artifact_id) REFERENCES artifacts (id) ON DELETE CASCADE,
            FOREIGN KEY (to_artifact_id) REFERENCES artifacts (id) ON DELETE CASCADE
        )
    """)
    print("✅ Created 'transformations' table")

    conn.commit()
    conn.close()


def create_indexes():
    """Creates indexes for performance optimization.

    Indexes created:
        - topics: user_id, created_at
        - messages: topic_id+seq_no, created_at
        - artifacts: topic_id+created_at, kind+locale, sha256
        - ai_usage: topic_id+created_at, model
        - transformations: from_artifact_id, to_artifact_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\nCreating indexes for performance optimization...")

    # Topics indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_created ON topics(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status)")
    print("✅ Created indexes for 'topics'")

    # Messages indexes (critical for chat pagination)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_topic_seq ON messages(topic_id, seq_no)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)")
    print("✅ Created indexes for 'messages'")

    # Artifacts indexes (critical for file lookup)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_topic_created ON artifacts(topic_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_kind_locale ON artifacts(kind, locale)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_sha256 ON artifacts(sha256)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_message_id ON artifacts(message_id)")
    print("✅ Created indexes for 'artifacts'")

    # AI Usage indexes (critical for analytics)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_usage_topic_created ON ai_usage(topic_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_usage_model ON ai_usage(model)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_usage_message_id ON ai_usage(message_id)")
    print("✅ Created indexes for 'ai_usage'")

    # Transformations indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transformations_from ON transformations(from_artifact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transformations_to ON transformations(to_artifact_id)")
    print("✅ Created indexes for 'transformations'")

    conn.commit()
    conn.close()


def drop_legacy_tables():
    """Drops legacy tables (reports, token_usage).

    Warning:
        This operation is irreversible. All existing report data will be lost.
        Ensure you have backups if needed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\nDropping legacy tables...")

    # Drop indexes first
    cursor.execute("DROP INDEX IF EXISTS idx_reports_user_id")
    cursor.execute("DROP INDEX IF EXISTS idx_token_usage_user_id")
    print("✅ Dropped legacy indexes")

    # Drop tables
    cursor.execute("DROP TABLE IF EXISTS token_usage")
    print("✅ Dropped 'token_usage' table")

    cursor.execute("DROP TABLE IF EXISTS reports")
    print("✅ Dropped 'reports' table")

    conn.commit()
    conn.close()


def verify_migration():
    """Verifies that migration completed successfully.

    Returns:
        bool: True if all new tables exist and legacy tables are dropped
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\nVerifying migration...")

    # Check new tables exist
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('topics', 'messages', 'artifacts', 'ai_usage', 'transformations')
        ORDER BY name
    """)
    new_tables = [row[0] for row in cursor.fetchall()]

    expected_tables = ['ai_usage', 'artifacts', 'messages', 'topics', 'transformations']
    if set(new_tables) == set(expected_tables):
        print(f"✅ All new tables exist: {', '.join(new_tables)}")
    else:
        print(f"❌ Missing tables: {set(expected_tables) - set(new_tables)}")
        return False

    # Check legacy tables are dropped
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('reports', 'token_usage')
    """)
    legacy_tables = [row[0] for row in cursor.fetchall()]

    if not legacy_tables:
        print("✅ Legacy tables dropped successfully")
    else:
        print(f"❌ Legacy tables still exist: {', '.join(legacy_tables)}")
        return False

    conn.close()
    return True


def main():
    """Main migration execution function.

    Steps:
        1. Create new tables for chat-based architecture
        2. Create indexes for performance
        3. Drop legacy tables (reports, token_usage)
        4. Verify migration success
    """
    print("=" * 60)
    print("Chat-Based Report System Migration")
    print("=" * 60)

    # Confirmation prompt
    response = input("\n⚠️  WARNING: This will DROP existing 'reports' and 'token_usage' tables.\n"
                     "All existing report data will be LOST.\n"
                     "Do you want to continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Migration cancelled.")
        return

    try:
        # Step 1: Create new tables
        create_new_tables()

        # Step 2: Create indexes
        create_indexes()

        # Step 3: Drop legacy tables
        drop_legacy_tables()

        # Step 4: Verify migration
        if verify_migration():
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Run backend server: uv run uvicorn app.main:app --reload")
            print("2. Check Swagger docs: http://localhost:8000/docs")
            print("3. Test new API endpoints: /api/topics, /api/messages, /api/artifacts")
        else:
            print("\n❌ Migration verification failed. Please check the database manually.")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
