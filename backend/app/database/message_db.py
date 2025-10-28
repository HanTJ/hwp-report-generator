"""
Message database operations.

Handles CRUD operations for messages (chat conversation turns).
"""
from typing import Optional, List
from datetime import datetime
from .connection import get_db_connection
from app.models.message import Message, MessageCreate
from shared.types.enums import MessageRole


class MessageDB:
    """Message database class for CRUD operations."""

    @staticmethod
    def create_message(topic_id: int, message_data: MessageCreate) -> Message:
        """Creates a new message in a topic.

        Args:
            topic_id: Parent topic ID
            message_data: Message creation data

        Returns:
            Created message entity

        Examples:
            >>> msg_data = MessageCreate(role=MessageRole.USER, content="Write a report")
            >>> message = MessageDB.create_message(topic_id=1, message_data=msg_data)
            >>> print(message.seq_no)
            1
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get next sequence number for this topic
        cursor.execute(
            "SELECT COALESCE(MAX(seq_no), 0) + 1 FROM messages WHERE topic_id = ?",
            (topic_id,)
        )
        seq_no = cursor.fetchone()[0]

        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO messages (topic_id, role, content, seq_no, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (topic_id, message_data.role.value, message_data.content, seq_no, now)
        )

        conn.commit()
        message_id = cursor.lastrowid

        # Retrieve created message
        cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        conn.close()

        return MessageDB._row_to_message(row)

    @staticmethod
    def get_message_by_id(message_id: int) -> Optional[Message]:
        """Retrieves message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message entity or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        conn.close()

        return MessageDB._row_to_message(row) if row else None

    @staticmethod
    def get_messages_by_topic(
        topic_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """Retrieves messages for a topic ordered by sequence number.

        Args:
            topic_id: Topic ID
            limit: Maximum number of messages to return (None for all)
            offset: Number of messages to skip

        Returns:
            List of messages ordered by seq_no

        Examples:
            >>> messages = MessageDB.get_messages_by_topic(topic_id=1)
            >>> for msg in messages:
            ...     print(f"{msg.seq_no}: {msg.role} - {msg.content[:50]}")
            1: user - Write a report on digital banking
            2: assistant - # Digital Banking Trends Report...
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM messages WHERE topic_id = ? ORDER BY seq_no ASC"
        params = [topic_id]

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [MessageDB._row_to_message(row) for row in rows]

    @staticmethod
    def get_message_count_by_topic(topic_id: int) -> int:
        """Counts messages in a topic.

        Args:
            topic_id: Topic ID

        Returns:
            Total number of messages
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE topic_id = ?",
            (topic_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        return count

    @staticmethod
    def delete_message(message_id: int) -> bool:
        """Deletes a message (hard delete, cascades to artifacts/ai_usage).

        Args:
            message_id: Message ID

        Returns:
            True if deleted, False if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()

        deleted = cursor.rowcount > 0
        conn.close()

        return deleted

    @staticmethod
    def _row_to_message(row) -> Message:
        """Converts database row to Message model.

        Args:
            row: SQLite row object

        Returns:
            Message entity
        """
        return Message(
            id=row["id"],
            topic_id=row["topic_id"],
            role=MessageRole(row["role"]),
            content=row["content"],
            seq_no=row["seq_no"],
            created_at=datetime.fromisoformat(row["created_at"])
        )
