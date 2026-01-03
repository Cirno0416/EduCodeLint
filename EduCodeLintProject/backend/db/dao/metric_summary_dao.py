from backend.entity.dto.metric_summary_dto import MetricSummaryDTO
from backend.db.init_database import get_connection


def insert_summary(metric_summary: MetricSummaryDTO):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metric_summary (
            analysis_id,
            file_path,
            metric_category,
            metric_name,
            count,
            value
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        metric_summary.analysis_id,
        metric_summary.file_path,
        metric_summary.metric_category,
        metric_summary.metric_name,
        metric_summary.count,
        metric_summary.value
    ))

    conn.commit()
    conn.close()


def delete_by_analysis_id(analysis_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM metric_summary WHERE analysis_id = ?",
        (analysis_id,)
    )

    conn.commit()
    conn.close()
