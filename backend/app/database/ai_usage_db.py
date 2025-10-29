"""
AI usage database operations.

Handles CRUD operations for AI usage tracking (token consumption, latency).
"""
from typing import Optional, List
from datetime import datetime
from .connection import get_db_connection
from app.models.ai_usage import AiUsage, AiUsageCreate, UserAiStats


class AiUsageDB:
    """AI usage database class for CRUD operations."""

    @staticmethod
    def create_ai_usage(
        topic_id: int,
        message_id: int,
        usage_data: AiUsageCreate
    ) -> AiUsage:
        """Creates a new AI usage record.

        Args:
            topic_id: Parent topic ID
            message_id: Source message ID
            usage_data: AI usage data

        Returns:
            Created AI usage entity

        Examples:
            >>> usage_data = AiUsageCreate(
            ...     model="claude-sonnet-4-5-20250929",
            ...     input_tokens=1500,
            ...     output_tokens=800,
            ...     latency_ms=3200
            ... )
            >>> usage = AiUsageDB.create_ai_usage(1, 2, usage_data)
            >>> print(usage.total_tokens)
            2300
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        total_tokens = usage_data.input_tokens + usage_data.output_tokens
        now = datetime.now()

        cursor.execute(
            """
            INSERT INTO ai_usage (
                topic_id, message_id, model,
                input_tokens, output_tokens, total_tokens,
                latency_ms, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                message_id,
                usage_data.model,
                usage_data.input_tokens,
                usage_data.output_tokens,
                total_tokens,
                usage_data.latency_ms,
                now
            )
        )

        conn.commit()
        usage_id = cursor.lastrowid

        # Retrieve created usage record
        cursor.execute("SELECT * FROM ai_usage WHERE id = ?", (usage_id,))
        row = cursor.fetchone()
        conn.close()

        return AiUsageDB._row_to_ai_usage(row)

    @staticmethod
    def get_ai_usage_by_id(usage_id: int) -> Optional[AiUsage]:
        """Retrieves AI usage by ID.

        Args:
            usage_id: AI usage ID

        Returns:
            AI usage entity or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ai_usage WHERE id = ?", (usage_id,))
        row = cursor.fetchone()
        conn.close()

        return AiUsageDB._row_to_ai_usage(row) if row else None

    @staticmethod
    def get_ai_usage_by_message(message_id: int) -> Optional[AiUsage]:
        """Retrieves AI usage for a specific message.

        Args:
            message_id: Message ID

        Returns:
            AI usage entity or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM ai_usage WHERE message_id = ?",
            (message_id,)
        )
        row = cursor.fetchone()
        conn.close()

        return AiUsageDB._row_to_ai_usage(row) if row else None

    @staticmethod
    def get_ai_usage_by_topic(topic_id: int) -> List[AiUsage]:
        """Retrieves all AI usage records for a topic.

        Args:
            topic_id: Topic ID

        Returns:
            List of AI usage records ordered by created_at DESC

        Examples:
            >>> usages = AiUsageDB.get_ai_usage_by_topic(topic_id=1)
            >>> total_tokens = sum(u.total_tokens for u in usages)
            >>> print(f"Total tokens used: {total_tokens}")
            Total tokens used: 15430
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM ai_usage WHERE topic_id = ? ORDER BY created_at DESC",
            (topic_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [AiUsageDB._row_to_ai_usage(row) for row in rows]

    @staticmethod
    def get_user_stats(user_id: int) -> UserAiStats:
        """Calculates aggregated AI usage statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Aggregated statistics

        Examples:
            >>> stats = AiUsageDB.get_user_stats(user_id=1)
            >>> print(f"Total topics: {stats.total_topics}")
            >>> print(f"Total tokens: {stats.total_tokens}")
            Total topics: 5
            Total tokens: 45230
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get topic count
        cursor.execute(
            "SELECT COUNT(*) FROM topics WHERE user_id = ?",
            (user_id,)
        )
        total_topics = cursor.fetchone()[0]

        # Get message count
        cursor.execute(
            """
            SELECT COUNT(*) FROM messages m
            JOIN topics t ON m.topic_id = t.id
            WHERE t.user_id = ?
            """,
            (user_id,)
        )
        total_messages = cursor.fetchone()[0]

        # Get aggregated usage stats
        cursor.execute(
            """
            SELECT
                COALESCE(SUM(input_tokens), 0) as total_input,
                COALESCE(SUM(output_tokens), 0) as total_output,
                COALESCE(SUM(total_tokens), 0) as total,
                COALESCE(AVG(latency_ms), 0) as avg_latency
            FROM ai_usage au
            JOIN topics t ON au.topic_id = t.id
            WHERE t.user_id = ?
            """,
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()

        return UserAiStats(
            user_id=user_id,
            total_topics=total_topics,
            total_messages=total_messages,
            total_input_tokens=row["total_input"],
            total_output_tokens=row["total_output"],
            total_tokens=row["total"],
            avg_latency_ms=round(row["avg_latency"], 2)
        )

    @staticmethod
    def delete_ai_usage(usage_id: int) -> bool:
        """Deletes an AI usage record.

        Args:
            usage_id: AI usage ID

        Returns:
            True if deleted, False if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM ai_usage WHERE id = ?", (usage_id,))
        conn.commit()

        deleted = cursor.rowcount > 0
        conn.close()

        return deleted

    @staticmethod
    def _row_to_ai_usage(row) -> AiUsage:
        """Converts database row to AiUsage model.

        Args:
            row: SQLite row object

        Returns:
            AiUsage entity
        """
        return AiUsage(
            id=row["id"],
            topic_id=row["topic_id"],
            message_id=row["message_id"],
            model=row["model"],
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            total_tokens=row["total_tokens"],
            latency_ms=row["latency_ms"],
            created_at=datetime.fromisoformat(row["created_at"])
        )
