from flask import Blueprint, request

from backend.db.dao.analysis_dao import get_analysis_list, get_analysis_detail, get_analysis_count, \
    delete_analysis_by_id
from backend.entity.result.result import success, error

record_bp = Blueprint('record', __name__)


@record_bp.route('/records', methods=['GET'])
def get_records():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    offset = (page - 1) * page_size

    total_records = get_analysis_count()
    analysis_list = get_analysis_list(page_size, offset)

    records = [
        {
            "id": a.id,
            "file_count": a.file_count,
            "created_at": a.created_at,
            "status": a.status
        }
        for a in analysis_list
    ]

    result = {
        "page": page,
        "page_size": page_size,
        "total": total_records,
        "records": records
    }

    return success(result)


@record_bp.route('/records/analysis', methods=['GET'])
def get_report():
    analysis_id = request.args.get("analysis_id")

    result = get_analysis_detail(analysis_id)

    return success(result)


@record_bp.route('/records/delete', methods=['DELETE'])
def delete_record():
    analysis_id = request.args.get("analysis_id")

    result, msg = delete_analysis_by_id(analysis_id)

    if result:
        return success(data=[], msg=msg)
    else:
        return error(data=[], msg=msg)
