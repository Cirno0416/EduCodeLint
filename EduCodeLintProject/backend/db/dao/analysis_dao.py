import sqlite3

from backend.entity.dto.analysis_dto import AnalysisDTO


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
