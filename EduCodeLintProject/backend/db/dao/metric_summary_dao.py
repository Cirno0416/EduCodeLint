import sqlite3

from backend.entity.dto.metric_summary_dto import MetricSummaryDTO


def insert_metric_summary(metric_summary: MetricSummaryDTO, conn: sqlite3.Connection):
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

    return cursor.lastrowid
