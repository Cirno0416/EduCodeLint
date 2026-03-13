from flask import Blueprint, request, jsonify

from backend.db.dao.analysis_dao import get_analysis_detail
from backend.entity.result.result import error, success
from backend.service.compare_service import compare_analysis_batches

compare_bp = Blueprint('compare', __name__)


@compare_bp.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    analysis_id_1 = data.get("analysis_id_1")
    analysis_id_2 = data.get("analysis_id_2")

    if not analysis_id_1 or not analysis_id_2:
        return error("Both analysis IDs are required")

    analysis_1 = get_analysis_detail(analysis_id_1)
    analysis_2 = get_analysis_detail(analysis_id_2)

    if not analysis_1 or not analysis_2:
        return error("One or both analysis IDs are invalid")

    comparison_result = compare_analysis_batches(analysis_1, analysis_2)

    return success(comparison_result)
