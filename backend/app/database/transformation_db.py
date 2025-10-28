"""
Transformation database operations.

Handles CRUD operations for transformations (file conversion lineage).
"""
from typing import Optional, List
from datetime import datetime
from .connection import get_db_connection
from app.models.transformation import Transformation, TransformationCreate
from shared.types.enums import TransformOperation


class TransformationDB:
    """Transformation database class for CRUD operations."""

    @staticmethod
    def create_transformation(transform_data: TransformationCreate) -> Transformation:
        """Creates a new transformation record.

        Args:
            transform_data: Transformation creation data

        Returns:
            Created transformation entity

        Examples:
            >>> transform_data = TransformationCreate(
            ...     from_artifact_id=1,  # MD file
            ...     to_artifact_id=2,    # HWPX file
            ...     operation=TransformOperation.CONVERT,
            ...     params_json='{"template": "report_template.hwpx"}'
            ... )
            >>> transform = TransformationDB.create_transformation(transform_data)
            >>> print(transform.operation)
            TransformOperation.CONVERT
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO transformations (
                from_artifact_id, to_artifact_id, operation, params_json, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transform_data.from_artifact_id,
                transform_data.to_artifact_id,
                transform_data.operation.value,
                transform_data.params_json,
                now
            )
        )

        conn.commit()
        transform_id = cursor.lastrowid

        # Retrieve created transformation
        cursor.execute("SELECT * FROM transformations WHERE id = ?", (transform_id,))
        row = cursor.fetchone()
        conn.close()

        return TransformationDB._row_to_transformation(row)

    @staticmethod
    def get_transformation_by_id(transform_id: int) -> Optional[Transformation]:
        """Retrieves transformation by ID.

        Args:
            transform_id: Transformation ID

        Returns:
            Transformation entity or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transformations WHERE id = ?", (transform_id,))
        row = cursor.fetchone()
        conn.close()

        return TransformationDB._row_to_transformation(row) if row else None

    @staticmethod
    def get_transformations_from_artifact(artifact_id: int) -> List[Transformation]:
        """Retrieves transformations originating from an artifact.

        Args:
            artifact_id: Source artifact ID

        Returns:
            List of transformations

        Examples:
            >>> transforms = TransformationDB.get_transformations_from_artifact(1)
            >>> for t in transforms:
            ...     print(f"{t.operation}: {t.from_artifact_id} -> {t.to_artifact_id}")
            CONVERT: 1 -> 2
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM transformations WHERE from_artifact_id = ? ORDER BY created_at DESC",
            (artifact_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [TransformationDB._row_to_transformation(row) for row in rows]

    @staticmethod
    def get_transformations_to_artifact(artifact_id: int) -> List[Transformation]:
        """Retrieves transformations targeting an artifact.

        Args:
            artifact_id: Target artifact ID

        Returns:
            List of transformations

        Examples:
            >>> transforms = TransformationDB.get_transformations_to_artifact(2)
            >>> if transforms:
            ...     source_id = transforms[0].from_artifact_id
            ...     print(f"Artifact {artifact_id} was created from artifact {source_id}")
            Artifact 2 was created from artifact 1
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM transformations WHERE to_artifact_id = ? ORDER BY created_at DESC",
            (artifact_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [TransformationDB._row_to_transformation(row) for row in rows]

    @staticmethod
    def delete_transformation(transform_id: int) -> bool:
        """Deletes a transformation record.

        Args:
            transform_id: Transformation ID

        Returns:
            True if deleted, False if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM transformations WHERE id = ?", (transform_id,))
        conn.commit()

        deleted = cursor.rowcount > 0
        conn.close()

        return deleted

    @staticmethod
    def _row_to_transformation(row) -> Transformation:
        """Converts database row to Transformation model.

        Args:
            row: SQLite row object

        Returns:
            Transformation entity
        """
        return Transformation(
            id=row["id"],
            from_artifact_id=row["from_artifact_id"],
            to_artifact_id=row["to_artifact_id"],
            operation=TransformOperation(row["operation"]),
            params_json=row["params_json"],
            created_at=datetime.fromisoformat(row["created_at"])
        )
