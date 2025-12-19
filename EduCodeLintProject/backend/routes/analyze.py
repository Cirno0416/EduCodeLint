import os

from flask import Blueprint, request, jsonify

from backend.services.pylint_service import run_pylint

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/analyze/single', methods=['POST'])
def analyze_single():
    data = request.get_json()
    path = data.get('path')

    if not path or not os.path.isfile(path):
        return jsonify({'error': 'Invalid file path'}), 400

    if not path.endswith('.py'):
        return jsonify({'error': 'Only .py files allowed'}), 400

    pylint_results = run_pylint(path)

    return jsonify({
        'filename': os.path.basename(path),
        'tool': 'pylint',
        'issue_count': len(pylint_results),
        'issues': pylint_results
    })


@upload_bp.route('/analyze/multiple', methods=['POST'])
def analyze_multiple():
    data = request.get_json()
    paths = data.get('paths', [])
    results = []

    for path in paths:
        if not path.endswith('.py') or not os.path.isfile(path):
            continue

        issues = run_pylint(path)

        results.append({
            'filename': os.path.basename(path),
            'issue_count': len(issues),
            'issues': issues
        })

    return jsonify({
        'tool': 'pylint',
        'file_count': len(results),
        'results': results
    })
