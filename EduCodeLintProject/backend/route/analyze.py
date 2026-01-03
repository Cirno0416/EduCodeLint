import os
from dataclasses import asdict

from flask import Blueprint, request

from backend.service.linter_service import run_linters
from backend.entity.result.result import success, error

analyze_bp = Blueprint('upload', __name__)


@analyze_bp.route('/analyze/single', methods=['POST'])
def analyze_single():
    data = request.get_json()
    path = data.get('path')
    exclude_tools = data.get('exclude_tools', [])

    if not path or not os.path.isfile(path):
        return error("Invalid file path")

    if not path.endswith('.py'):
        return error("Only .py files allowed")

    results = run_linters(path, exclude_tools)

    return success({
        "file_name": os.path.basename(path),
        "results": [asdict(d) for d in results]
    })


@analyze_bp.route('/analyze/multiple', methods=['POST'])
def analyze_multiple():
    data = request.get_json()
    paths = data.get('paths', [])
    exclude_tools = data.get('exclude_tools', [])

    results = []

    for path in paths:
        if not path.endswith('.py') or not os.path.isfile(path):
            continue

        issues = run_linters(path, exclude_tools)

        results.append({
            'filename': os.path.basename(path),
            'issue_count': len(issues),
            'issues': [asdict(d) for d in issues]
        })

    return success({
        'file_count': len(results),
        'results': results
    })
