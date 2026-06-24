"""
보고서 데이터베이스 작업
"""
from typing import Optional, List
from datetime import datetime
from .connection import get_db_connection
from models.report import Report


class ReportDB:
    """보고서 데이터베이스 클래스"""

    @staticmethod
    def create_report(
        user_id: int,
        topic: str,
        title: str,
        filename: str,
        file_path: str,
        file_size: int
    ) -> Report:
        """보고서 생성"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO reports (user_id, topic, title, filename, file_path, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, topic, title, filename, file_path, file_size)
        )

        conn.commit()
        report_id = cursor.lastrowid

        # 생성된 보고서 조회
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        conn.close()

        return ReportDB._row_to_report(row)

    @staticmethod
    def get_report_by_id(report_id: int) -> Optional[Report]:
        """ID로 보고서 조회"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        conn.close()

        return ReportDB._row_to_report(row) if row else None

    @staticmethod
    def get_reports_by_user(user_id: int) -> List[Report]:
        """사용자별 보고서 조회"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [ReportDB._row_to_report(row) for row in rows]

    @staticmethod
    def get_all_reports() -> List[Report]:
        """모든 보고서 조회"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [ReportDB._row_to_report(row) for row in rows]

    @staticmethod
    def delete_report(report_id: int) -> bool:
        """보고서 삭제"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()

        return affected > 0

    @staticmethod
    def _row_to_report(row) -> Report:
        """데이터베이스 행을 Report 객체로 변환"""
        return Report(
            id=row["id"],
            user_id=row["user_id"],
            topic=row["topic"],
            title=row["title"],
            filename=row["filename"],
            file_path=row["file_path"],
            file_size=row["file_size"],
            created_at=datetime.fromisoformat(row["created_at"])
        )
