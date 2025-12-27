import os

from flask import Blueprint, request, jsonify

from backend.services.linter_service import run_linters

analyze_bp = Blueprint('upload', __name__)


@analyze_bp.route('/analyze/single', methods=['POST'])
def analyze_single():
    data = request.get_json()
    path = data.get('path')
    exclude_tools = data.get('exclude_tools', [])

    if not path or not os.path.isfile(path):
        return jsonify({'error': 'Invalid file path'}), 400

    if not path.endswith('.py'):
        return jsonify({'error': 'Only .py files allowed'}), 400

    results = run_linters(path, exclude_tools)

    return jsonify({
        'filename': os.path.basename(path),
        'issue_count': len(results),
        'issues': results
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
            'issues': issues
        })

    return jsonify({
        'file_count': len(results),
        'results': results
    })
