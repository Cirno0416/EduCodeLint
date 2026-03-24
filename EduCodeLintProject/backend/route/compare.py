from flask import Blueprint, request

from backend.db.dao.analysis_dao import get_analysis_detail
from backend.entity.result.result import error, success
from backend.service.compare_service import compare_multiple_batches

compare_bp = Blueprint('compare', __name__)


@compare_bp.route('/compare', methods=['POST'])
def compare_multiple():
    data = request.get_json()
    analysis_ids = data.get("analysis_ids", [])

    if not analysis_ids or len(analysis_ids) < 2:
        return error("At least two analysis IDs are required")

    analyses = []
    for aid in analysis_ids:
        analysis = get_analysis_detail(aid)
        if not analysis:
            return error(f"Invalid analysis_id: {aid}")
        analyses.append(analysis)

    result = compare_multiple_batches(analyses)

    return success(result)
