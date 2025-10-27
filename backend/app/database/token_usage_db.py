"""
토큰 사용량 데이터베이스 작업
"""
from typing import Optional, List
from datetime import datetime
from .connection import get_db_connection
from app.models.token_usage import TokenUsage, TokenUsageCreate, UserTokenStats


class TokenUsageDB:
    """토큰 사용량 데이터베이스 클래스"""

    @staticmethod
    def create_token_usage(usage: TokenUsageCreate) -> TokenUsage:
        """토큰 사용량 기록 생성"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO token_usage (user_id, report_id, input_tokens, output_tokens, total_tokens)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usage.user_id, usage.report_id, usage.input_tokens, usage.output_tokens, usage.total_tokens)
        )

        conn.commit()
        usage_id = cursor.lastrowid

        # 생성된 기록 조회
        cursor.execute("SELECT * FROM token_usage WHERE id = ?", (usage_id,))
        row = cursor.fetchone()
        conn.close()

        return TokenUsageDB._row_to_token_usage(row)

    @staticmethod
    def get_usage_by_user(user_id: int) -> List[TokenUsage]:
        """사용자별 토큰 사용량 조회"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM token_usage WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [TokenUsageDB._row_to_token_usage(row) for row in rows]

    @staticmethod
    def get_all_user_stats() -> List[UserTokenStats]:
        """모든 사용자의 토큰 통계 조회"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                u.id as user_id,
                u.username,
                u.email,
                COALESCE(SUM(t.input_tokens), 0) as total_input_tokens,
                COALESCE(SUM(t.output_tokens), 0) as total_output_tokens,
                COALESCE(SUM(t.total_tokens), 0) as total_tokens,
                COUNT(DISTINCT t.report_id) as report_count,
                MAX(t.created_at) as last_usage
            FROM users u
            LEFT JOIN token_usage t ON u.id = t.user_id
            GROUP BY u.id, u.username, u.email
            ORDER BY total_tokens DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        return [TokenUsageDB._row_to_user_stats(row) for row in rows]

    @staticmethod
    def get_user_stats(user_id: int) -> Optional[UserTokenStats]:
        """특정 사용자의 토큰 통계 조회"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                u.id as user_id,
                u.username,
                u.email,
                COALESCE(SUM(t.input_tokens), 0) as total_input_tokens,
                COALESCE(SUM(t.output_tokens), 0) as total_output_tokens,
                COALESCE(SUM(t.total_tokens), 0) as total_tokens,
                COUNT(DISTINCT t.report_id) as report_count,
                MAX(t.created_at) as last_usage
            FROM users u
            LEFT JOIN token_usage t ON u.id = t.user_id
            WHERE u.id = ?
            GROUP BY u.id, u.username, u.email
            """,
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()

        return TokenUsageDB._row_to_user_stats(row) if row else None

    @staticmethod
    def _row_to_token_usage(row) -> TokenUsage:
        """데이터베이스 행을 TokenUsage 객체로 변환"""
        return TokenUsage(
            id=row["id"],
            user_id=row["user_id"],
            report_id=row["report_id"],
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            total_tokens=row["total_tokens"],
            created_at=datetime.fromisoformat(row["created_at"])
        )

    @staticmethod
    def _row_to_user_stats(row) -> UserTokenStats:
        """데이터베이스 행을 UserTokenStats 객체로 변환"""
        last_usage = None
        if row["last_usage"]:
            last_usage = datetime.fromisoformat(row["last_usage"])

        return UserTokenStats(
            user_id=row["user_id"],
            username=row["username"],
            email=row["email"],
            total_input_tokens=row["total_input_tokens"],
            total_output_tokens=row["total_output_tokens"],
            total_tokens=row["total_tokens"],
            report_count=row["report_count"],
            last_usage=last_usage
        )
