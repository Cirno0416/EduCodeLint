import sqlite3

from backend.entity.dto.metric_summary_dto import MetricSummaryDTO
from backend.entity.vo.metric_summary_vo import MetricSummaryVO


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


def get_metric_summaries_by_file_id(file_id: int, conn) -> list[MetricSummaryVO]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, file_id, metric_category, issue_count, score
        FROM metric_summary
        WHERE file_id = ?
    """, (file_id,))
    rows = cursor.fetchall()

    return [
        MetricSummaryVO(
            id=r[0],
            file_id=r[1],
            metric_category=r[2],
            issue_count=r[3],
            score=r[4],
            issues=[]
        )
        for r in rows
    ]
