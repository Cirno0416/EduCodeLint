from backend.entity.dto.metric_summary_dto import MetricSummaryDTO
from backend.db.init_database import get_connection


def insert_summary(metric_summary: MetricSummaryDTO):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metric_summary (
            file_id,
            metric_category,
            issue_count,
            score
        ) VALUES (?, ?, ?, ?)
    """, (
        metric_summary.file_id,
        metric_summary.metric_category,
        metric_summary.issue_count,
        metric_summary.score
    ))

    conn.commit()
    conn.close()
