from queue import Queue

from backend.db.dao.analysis_dao import insert_analysis, update_analysis_status
from backend.db.dao.issue_dao import insert_issues_bulk
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
            elif op_type == "issues":
                payload = item[1]
                insert_issues_bulk(payload, conn)
            elif op_type == "update_analysis_status":
                analysis_id, status = item[1], item[2]
                update_analysis_status(analysis_id, status, conn)

            conn.commit()

    finally:
        conn.close()
