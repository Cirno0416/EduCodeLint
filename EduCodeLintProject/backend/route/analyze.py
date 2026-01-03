import os
import sqlite3
import uuid
from dataclasses import asdict
from datetime import datetime, timezone

from flask import Blueprint, request

from backend.db.dao.analysis_dao import insert_analysis
from backend.db.dao.issue_dao import insert_issues_bulk
from backend.entity.dto.analysis_dto import AnalysisDTO
from backend.service.linter_service import run_linters
from backend.entity.result.result import success, error
from backend.utils.parse_util import parse_issues_to_dtos
from backend.db.init_database import get_connection


analyze_bp = Blueprint('upload', __name__)


@analyze_bp.route('/analyze/single', methods=['POST'])
def analyze_single():
    data = request.get_json()
    path = data.get('path')
    exclude_tools = data.get('exclude_tools', [])

    if not path or not os.path.isfile(path) or not path.endswith('.py'):
        return error("Invalid python file path")

    conn = get_connection()
    try:
        # 插入 analysis 记录
        analysis_id = _create_and_persist_analysis(file_path=path, conn=conn)

        # 调用插件分析
        raw = run_linters(path, exclude_tools)

        # 解析 issue 记录
        issues = parse_issues_to_dtos(
            raw=raw,
            analysis_id=analysis_id,
            file_path=path,
            exclude_tools=exclude_tools
        )

        # 插入 issue 记录
        insert_issues_bulk(issues=issues, conn=conn)

        # 提交事务
        conn.commit()

    except Exception as e:
        # 回滚整个事务
        conn.rollback()
        return error(f"Analysis failed: {e}")

    finally:
        conn.close()

    return success({
        "file_name": os.path.basename(path),
        "issues": [asdict(d) for d in issues]
    })


@analyze_bp.route('/analyze/multiple', methods=['POST'])
def analyze_multiple():
    data = request.get_json()
    paths = data.get('paths', [])
    exclude_tools = data.get('exclude_tools', [])

    results = []

    for path in paths:
        if not path or not os.path.isfile(path) or not path.endswith('.py'):
            continue

        conn = get_connection()
        try:
            # 插入 analysis 记录
            analysis_id = _create_and_persist_analysis(file_path=path, conn=conn)

            # 调用插件分析
            raw = run_linters(path, exclude_tools)

            # 解析 issue 记录
            issues = parse_issues_to_dtos(
                raw=raw,
                analysis_id=analysis_id,
                file_path=path,
                exclude_tools=exclude_tools
            )

            # 插入 issue 记录
            insert_issues_bulk(issues=issues, conn=conn)

            # 提交事务
            conn.commit()

            results.append({
                'file_name': os.path.basename(path),
                'issues': [asdict(d) for d in issues],
                'status': 'success'
            })

        except Exception as e:
            # 回滚事务
            conn.rollback()
            results.append({
                'file_name': os.path.basename(path),
                'issues': [],
                'status': 'failed',
                'error': str(e)
            })

        finally:
            conn.close()

    return success({
        'file_count': len(results),
        'results': results
    })


def _create_and_persist_analysis(file_path: str, conn: sqlite3.Connection) -> str:
    analysis_id = _generate_analysis_id()
    analysis = AnalysisDTO(
        id=analysis_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        file_path=file_path
    )
    insert_analysis(analysis, conn)

    return analysis_id


def _generate_analysis_id() -> str:
    return str(uuid.uuid4())
