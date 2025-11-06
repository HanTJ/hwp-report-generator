"""Template database operations.

Handles CRUD operations for user custom templates and their placeholders.
"""

from datetime import datetime
from typing import List, Optional

from .connection import get_db_connection
from app.models.template import Template, TemplateCreate, Placeholder, PlaceholderCreate


class TemplateDB:
    """Template database class for CRUD operations."""

    @staticmethod
    def create_template(user_id: int, template_data: TemplateCreate) -> Template:
        """Creates a new template.

        Args:
            user_id: User ID who owns this template
            template_data: Template creation data

        Returns:
            Created template entity

        Raises:
            Exception: Database insertion error

        Examples:
            >>> template_data = TemplateCreate(
            ...     title="재무보고서 템플릿",
            ...     filename="template.hwpx",
            ...     file_path="backend/templates/user_1/template_1/template.hwpx",
            ...     file_size=45678,
            ...     sha256="abc123..."
            ... )
            >>> template = TemplateDB.create_template(1, template_data)
            >>> print(template.title)
            재무보고서 템플릿
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()
        try:
            cursor.execute(
                """
                INSERT INTO templates (
                    user_id, title, description, filename,
                    file_path, file_size, sha256, is_active,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    template_data.title,
                    template_data.description,
                    template_data.filename,
                    template_data.file_path,
                    template_data.file_size,
                    template_data.sha256,
                    True,  # is_active
                    now,
                    now
                )
            )
            conn.commit()
            template_id = cursor.lastrowid

            # Retrieve created template
            cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            conn.close()

            return TemplateDB._row_to_template(row)
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def get_template_by_id(template_id: int, user_id: Optional[int] = None) -> Optional[Template]:
        """Retrieves a template by ID.

        Args:
            template_id: Template ID to retrieve
            user_id: User ID for permission check (optional)

        Returns:
            Template entity or None if not found

        Examples:
            >>> template = TemplateDB.get_template_by_id(1)
            >>> if template:
            ...     print(template.title)
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        if user_id is not None:
            cursor.execute(
                "SELECT * FROM templates WHERE id = ? AND user_id = ?",
                (template_id, user_id)
            )
        else:
            cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))

        row = cursor.fetchone()
        conn.close()

        return TemplateDB._row_to_template(row) if row else None

    @staticmethod
    def list_templates_by_user(user_id: int) -> List[Template]:
        """Lists all templates owned by a user.

        Args:
            user_id: User ID

        Returns:
            List of template entities

        Examples:
            >>> templates = TemplateDB.list_templates_by_user(1)
            >>> print(len(templates))
            3
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM templates WHERE user_id = ? AND is_active = ? ORDER BY created_at DESC",
            (user_id, True)
        )
        rows = cursor.fetchall()
        conn.close()

        return [TemplateDB._row_to_template(row) for row in rows]

    @staticmethod
    def list_all_templates() -> List[Template]:
        """Lists all active templates (admin only).

        Returns:
            List of all template entities

        Examples:
            >>> all_templates = TemplateDB.list_all_templates()
            >>> print(len(all_templates))
            10
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM templates WHERE is_active = ? ORDER BY created_at DESC",
            (True,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [TemplateDB._row_to_template(row) for row in rows]

    @staticmethod
    def delete_template(template_id: int, user_id: int) -> bool:
        """Soft deletes a template (marks as inactive).

        Args:
            template_id: Template ID to delete
            user_id: User ID for permission check

        Returns:
            True if deleted successfully, False if not found

        Examples:
            >>> success = TemplateDB.delete_template(1, 1)
            >>> print(success)
            True
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE templates
                SET is_active = 0, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (datetime.now(), template_id, user_id)
            )
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def _row_to_template(row) -> Optional[Template]:
        """Converts database row to Template entity.

        Args:
            row: Database row tuple

        Returns:
            Template entity or None if row is None
        """
        if not row:
            return None

        return Template(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            filename=row[4],
            file_path=row[5],
            file_size=row[6],
            sha256=row[7],
            is_active=row[8],
            created_at=datetime.fromisoformat(row[9]),
            updated_at=datetime.fromisoformat(row[10])
        )


class PlaceholderDB:
    """Placeholder database class for CRUD operations."""

    @staticmethod
    def create_placeholder(placeholder_data: PlaceholderCreate) -> Placeholder:
        """Creates a new placeholder.

        Args:
            placeholder_data: Placeholder creation data

        Returns:
            Created placeholder entity

        Raises:
            Exception: Database insertion error

        Examples:
            >>> placeholder_data = PlaceholderCreate(
            ...     template_id=1,
            ...     placeholder_key="{{TITLE}}"
            ... )
            >>> placeholder = PlaceholderDB.create_placeholder(placeholder_data)
            >>> print(placeholder.placeholder_key)
            {{TITLE}}
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()
        try:
            cursor.execute(
                """
                INSERT INTO placeholders (template_id, placeholder_key, created_at)
                VALUES (?, ?, ?)
                """,
                (placeholder_data.template_id, placeholder_data.placeholder_key, now)
            )
            conn.commit()
            placeholder_id = cursor.lastrowid

            # Retrieve created placeholder
            cursor.execute("SELECT * FROM placeholders WHERE id = ?", (placeholder_id,))
            row = cursor.fetchone()
            conn.close()

            return PlaceholderDB._row_to_placeholder(row)
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def create_placeholders_batch(template_id: int, placeholder_keys: List[str]) -> List[Placeholder]:
        """Creates multiple placeholders in batch.

        Args:
            template_id: Template ID
            placeholder_keys: List of placeholder keys (e.g., ["{{TITLE}}", "{{SUMMARY}}"])

        Returns:
            List of created placeholder entities

        Raises:
            Exception: Database insertion error

        Examples:
            >>> placeholders = PlaceholderDB.create_placeholders_batch(
            ...     1,
            ...     ["{{TITLE}}", "{{SUMMARY}}", "{{BACKGROUND}}"]
            ... )
            >>> print(len(placeholders))
            3
        """
        if not placeholder_keys:
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()
        try:
            # Prepare data for batch insert
            data = [(template_id, key, now) for key in placeholder_keys]

            cursor.executemany(
                """
                INSERT INTO placeholders (template_id, placeholder_key, created_at)
                VALUES (?, ?, ?)
                """,
                data
            )
            conn.commit()

            # Retrieve all created placeholders
            cursor.execute(
                "SELECT * FROM placeholders WHERE template_id = ? ORDER BY created_at ASC",
                (template_id,)
            )
            rows = cursor.fetchall()
            conn.close()

            return [PlaceholderDB._row_to_placeholder(row) for row in rows]
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def get_placeholders_by_template(template_id: int) -> List[Placeholder]:
        """Gets all placeholders for a template.

        Args:
            template_id: Template ID

        Returns:
            List of placeholder entities

        Examples:
            >>> placeholders = PlaceholderDB.get_placeholders_by_template(1)
            >>> for p in placeholders:
            ...     print(p.placeholder_key)
            {{TITLE}}
            {{SUMMARY}}
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM placeholders WHERE template_id = ? ORDER BY created_at ASC",
            (template_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [PlaceholderDB._row_to_placeholder(row) for row in rows]

    @staticmethod
    def delete_placeholders_by_template(template_id: int) -> bool:
        """Deletes all placeholders for a template.

        Args:
            template_id: Template ID

        Returns:
            True if deleted successfully

        Examples:
            >>> success = PlaceholderDB.delete_placeholders_by_template(1)
            >>> print(success)
            True
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM placeholders WHERE template_id = ?", (template_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def _row_to_placeholder(row) -> Optional[Placeholder]:
        """Converts database row to Placeholder entity.

        Args:
            row: Database row tuple

        Returns:
            Placeholder entity or None if row is None
        """
        if not row:
            return None

        return Placeholder(
            id=row[0],
            template_id=row[1],
            placeholder_key=row[2],
            created_at=datetime.fromisoformat(row[3])
        )
