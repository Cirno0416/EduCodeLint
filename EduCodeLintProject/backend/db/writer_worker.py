from queue import Queue

from backend.db.dao.analysis_dao import insert_analysis, update_analysis_status
from backend.db.dao.file_dao import insert_file
from backend.db.dao.issue_dao import insert_issue
from backend.db.dao.metric_summary_dao import insert_metric_summary
from backend.db.init_database import get_connection

db_queue: Queue = Queue()
STOP = object()


def db_writer_worker(queue: Queue):
    conn = get_connection()
    try:
        while True:
            item = queue.get()

            if item is STOP:
                break

            op_type = item[0]

            if op_type == "analysis":
                payload = item[1]
                insert_analysis(payload, conn)
            elif op_type == "file_result":
                file_dto, metric_summaries = item[1], item[2]

                # 插入 file，拿到 file_id
                file_id = insert_file(file_dto, conn)
                file_dto.id = file_id

                # 插入每个 metric_summary
                for summary in metric_summaries:
                    summary.file_id = file_id
                    summary_id = insert_metric_summary(summary, conn)
                    summary.id = summary_id

                    # 插入 issue，回填 metric_summary_id
                    for issue in summary.issues:
                        issue.metric_summary_id = summary_id
                        insert_issue(issue, conn)
            elif op_type == "update_analysis_status":
                analysis_id, status = item[1], item[2]
                update_analysis_status(analysis_id, status, conn)

            conn.commit()
    finally:
        conn.close()
