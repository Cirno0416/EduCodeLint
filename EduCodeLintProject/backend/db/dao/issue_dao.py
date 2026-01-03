import sqlite3

from backend.entity.dto.issue_dto import IssueDTO


def insert_issues_bulk(issues: list[IssueDTO], conn: sqlite3.Connection):
    if not issues:
        return

    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO issue (
            analysis_id,
            file_path,
            tool,
            metric_category,
            metric_name,
            rule_id,
            line,
            severity,
            message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            issue.analysis_id,
            issue.file_path,
            issue.tool,
            issue.metric_category,
            issue.metric_name,
            issue.rule_id,
            issue.line,
            issue.severity,
            issue.message
        )
        for issue in issues
    ])
