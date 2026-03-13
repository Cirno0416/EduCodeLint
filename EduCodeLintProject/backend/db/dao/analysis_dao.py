import sqlite3

from backend.db.dao.file_dao import get_files_by_analysis_id, delete_files_by_analysis_id
from backend.db.dao.issue_dao import get_issues_by_metric_summary_id, delete_issues_by_metric_summary_id
from backend.db.dao.metric_summary_dao import get_metric_summaries_by_file_id, delete_metric_summaries_by_file_id
from backend.db.dao.weight_dao import get_weights_by_analysis_id
from backend.db.init_database import get_connection
from backend.entity.dto.analysis_dto import AnalysisDTO
from backend.entity.vo.analysis_vo import AnalysisVO


def insert_analysis(analysis: AnalysisDTO, conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis (id, file_count, created_at)
        VALUES (?, ?, ?)
    """, (
        analysis.id,
        analysis.file_count,
        analysis.created_at
    ))


def update_analysis_status(analysis_id: str, status: str, conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE analysis
        SET status = ?
        WHERE id = ?
    """, (
        status,
        analysis_id
    ))


def get_analysis_by_id(analysis_id: str, conn: sqlite3.Connection) -> AnalysisVO | None:
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, file_count, created_at, status
        FROM analysis
        WHERE id = ?
    """, (analysis_id,))

    row = cursor.fetchone()
    if not row:
        return None

    return AnalysisVO(
        id=row[0],
        file_count=row[1],
        created_at=row[2],
        status=row[3]
    )


def get_analysis_detail(analysis_id: str) -> dict:
    with get_connection() as conn:
        analysis = get_analysis_by_id(analysis_id, conn)
        if not analysis:
            return {}

        results = []

        weight_config = get_weights_by_analysis_id(analysis_id, conn)
        files = get_files_by_analysis_id(analysis_id, conn)

        for file in files:
            summaries = get_metric_summaries_by_file_id(file.id, conn)

            for summary in summaries:
                issues = get_issues_by_metric_summary_id(summary.id, conn)
                summary.issues = issues

            results.append({
                "file_path": file.file_path,
                "status": "success",
                "score": file.total_score,
                "summaries": summaries
            })

        return {
            "analysis_id": analysis_id,
            "file_count": analysis.file_count,
            "results": results,
            "weight_config": weight_config,
            "status": analysis.status,
            "created_at": analysis.created_at
        }


def get_analysis_list(page_size: int, offset: int) -> list[AnalysisVO]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, file_count, created_at, status
            FROM analysis
            WHERE status='success'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))

        rows = cursor.fetchall()
        return [
            AnalysisVO(
                id=row[0],
                file_count=row[1],
                created_at=row[2],
                status=row[3]
            )
            for row in rows
        ]


def get_analysis_count() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM analysis
            WHERE status='success'
        """)

        row = cursor.fetchone()
        return row[0] if row else 0


def delete_analysis_by_id(analysis_id: str):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # 开启事务
            conn.execute("BEGIN")

            # 获取所有 file
            files = get_files_by_analysis_id(analysis_id, conn)

            for f in files:
                file_id = f.id

                # 获取 file 下的 metric_summary
                summaries = get_metric_summaries_by_file_id(file_id, conn)

                for s in summaries:
                    summary_id = s.id

                    # 删除 issue
                    delete_issues_by_metric_summary_id(summary_id, conn)

                # 删除 metric_summary
                delete_metric_summaries_by_file_id(file_id, conn)

            # 删除 file
            delete_files_by_analysis_id(analysis_id, conn)

            # 删除 analysis
            cursor.execute("""
                DELETE FROM analysis
                WHERE id = ?
            """, (analysis_id,))

            # 判断是否删除成功
            if cursor.rowcount == 0:
                conn.rollback()
                return False, "记录不存在"

            # 提交事务
            conn.commit()
            return True, "删除成功"

    except Exception as e:
        conn.rollback()
        return False, f"删除失败: {str(e)}"
