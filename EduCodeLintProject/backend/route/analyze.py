from flask import Blueprint, request

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
