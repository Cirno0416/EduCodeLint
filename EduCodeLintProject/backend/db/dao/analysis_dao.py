from backend.entity.dto.analysis_dto import AnalysisDTO
from backend.db.init_database import get_connection


def insert_analysis(analysis: AnalysisDTO):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis (id, created_at, project_path)
        VALUES (?, ?, ?)
    """, (
        analysis.id,
        analysis.created_at,
        analysis.project_path
    ))

    conn.commit()
    conn.close()
