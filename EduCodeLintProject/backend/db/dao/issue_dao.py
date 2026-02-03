import sqlite3

from backend.entity.dto.issue_dto import IssueDTO


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
