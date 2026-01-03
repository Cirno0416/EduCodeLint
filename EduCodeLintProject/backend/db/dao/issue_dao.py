from backend.entity.dto.issue_dto import IssueDTO
from backend.db.init_database import get_connection


def insert_issue(issue: IssueDTO):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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
    """, (
        issue.analysis_id,
        issue.file_path,
        issue.tool,
        issue.metric_category,
        issue.metric_name,
        issue.rule_id,
        issue.line,
        issue.severity,
        issue.message
    ))

    conn.commit()
    conn.close()
