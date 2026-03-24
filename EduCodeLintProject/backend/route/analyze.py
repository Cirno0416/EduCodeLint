from flask import Blueprint, request

from backend.constant.weights import DEFAULT_WEIGHTS
from backend.db.dao.weight_dao import get_latest_weights_and_Ek, insert_adaptive_weights
from backend.db.init_database import get_connection
from backend.entity.result.result import success, error
from backend.service.analyze_service import analyze_files

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/analyze/single', methods=['POST'])
def analyze_single():
    data = request.get_json()
    path = data.get("path")
    exclude_tools = data.get("exclude_tools", [])

    if not path:
        return error("Path is required")

    result = analyze_files(
        paths=[path],
        exclude_tools=exclude_tools
    )

    if result["status"] != "success":
        return error(result["error"])

    return success(result)


@analyze_bp.route('/analyze/multiple', methods=['POST'])
def analyze_multiple():
    data = request.get_json()
    paths = data.get("paths", [])
    exclude_tools = data.get("exclude_tools", [])

    if not paths:
        return error("Paths cannot be empty")

    result = analyze_files(
        paths=paths,
        exclude_tools=exclude_tools
    )

    if result["status"] != "success":
        return error(result["error"])

    return success(result)


@analyze_bp.route('/analyze/weights', methods=['GET'])
def get_weights():
    weights, _ = get_latest_weights_and_Ek()

    if not weights:
        return error("获取权重失败")

    return success(weights)


@analyze_bp.route('/analyze/weights/reset', methods=['POST'])
def reset_weights():
    with get_connection() as conn:
        insert_adaptive_weights("默认权重", DEFAULT_WEIGHTS, {}, conn)

        return success()
