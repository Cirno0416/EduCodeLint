import sqlite3

from backend.entity.dto.analysis_dto import AnalysisDTO


def insert_analysis(analysis: AnalysisDTO, conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis (id, created_at, file_path)
        VALUES (?, ?, ?)
    """, (
        analysis.id,
        analysis.created_at,
        analysis.file_path
    ))
