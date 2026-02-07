import sqlite3

from backend.entity.dto.analysis_dto import AnalysisDTO
from backend.entity.vo.analysis_vo import AnalysisVO


def insert_analysis(analysis: AnalysisDTO, conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis (id, file_count, created_at)
        VALUES (?, ?, ?)
    """, (
        analysis.id,
        analysis.file_count,
        analysis.created_at
    ))


def update_analysis_status(analysis_id: str, status: str, conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE analysis
        SET status = ?
        WHERE id = ?
    """, (
        status,
        analysis_id
    ))


def get_analysis_by_id(analysis_id: str, conn: sqlite3.Connection) -> AnalysisVO | None:
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, file_count, created_at, status
        FROM analysis
        WHERE id = ?
    """, (analysis_id,))

    row = cursor.fetchone()
    if not row:
        return None

    return AnalysisVO(
        id=row[0],
        file_count=row[1],
        created_at=row[2],
        status=row[3]
    )


