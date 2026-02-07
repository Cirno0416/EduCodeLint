import sqlite3

from backend.entity.dto.issue_dto import IssueDTO
from backend.entity.vo.issue_vo import IssueVO


def insert_issue(issue: IssueDTO, conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO issue (
            metric_summary_id, tool, metric_category,
            metric_name, rule_id, line, severity, message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        issue.metric_summary_id,
        issue.tool,
        issue.metric_category,
        issue.metric_name,
        issue.rule_id,
        issue.line,
        issue.severity,
        issue.message
    ))


def get_issues_by_metric_summary_id(summary_id: int, conn) -> list[IssueVO]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, metric_summary_id, tool, metric_category,
               metric_name, rule_id, line, severity, message
        FROM issue
        WHERE metric_summary_id = ?
    """, (summary_id,))
    rows = cursor.fetchall()

    return [
        IssueVO(
            id=r[0],
            metric_summary_id=r[1],
            tool=r[2],
            metric_category=r[3],
            metric_name=r[4],
            rule_id=r[5],
            line=r[6],
            severity=r[7],
            message=r[8]
        )
        for r in rows
    ]
