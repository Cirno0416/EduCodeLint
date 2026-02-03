import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone

from flask import Blueprint, request

from backend.db.writer_worker import db_writer_worker, db_queue, STOP
from backend.entity.dto.analysis_dto import AnalysisDTO
from backend.entity.dto.file_dto import FileDTO
from backend.service.calculate_score_service import build_metric_summaries, calculate_file_score
from backend.service.linter_service import run_linters
from backend.entity.result.result import success, error
from backend.service.issue_parse_service import parse_issues_to_dtos


analyze_bp = Blueprint('upload', __name__)


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


def analyze_files(paths: list[str], exclude_tools: list[str]) -> dict:
    analysis_id = _generate_analysis_id()

    analysis = AnalysisDTO(
        id=analysis_id,
        file_count=len(paths),
        created_at=datetime.now(timezone.utc).isoformat()
    )

    # 启动数据库写线程（唯一写入口）
    writer = threading.Thread(
        target=db_writer_worker,
        args=(db_queue,),
        daemon=True
    )
    writer.start()

    # 先写 analysis
    db_queue.put(("analysis", analysis))

    results = []

    max_workers = min(8, os.cpu_count() or 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _analyze_one_file,
                path,
                analysis_id,
                exclude_tools
            )
            for path in paths
        ]

        for future in as_completed(futures):
            results.append(future.result())

    db_queue.put(STOP)
    writer.join()

    return {
        "status": "success",
        "analysis_id": analysis_id,
        "file_count": len(results),
        "results": results
    }


def _analyze_one_file(
    path: str,
    analysis_id: str,
    exclude_tools: list[str]
) -> dict:
    if not path or not os.path.isfile(path) or not path.endswith(".py"):
        return {
            "file_name": os.path.basename(path),
            "issues": [],
            "status": "invalid"
        }

    try:
        raw = run_linters(path, exclude_tools)

        issues = parse_issues_to_dtos(raw, exclude_tools)

        summaries = build_metric_summaries(issues)

        file = FileDTO(
            analysis_id=analysis_id,
            file_path=path,
            total_score=calculate_file_score(summaries),
        )

        # 由 writer 顺序写
        db_queue.put(("file_result", file, summaries))

        # 分析成功，修改 analysis 状态为 success
        db_queue.put(("update_analysis_status", analysis_id, "success"))

        return {
            "file_name": os.path.basename(path),
            "issues": [asdict(d) for d in issues],
            "score": file.total_score,
            "status": "success"
        }

    except Exception as e:
        # 分析失败，修改 analysis 状态为 failed
        db_queue.put(("update_analysis_status", analysis_id, "failed"))

        return {
            "file_name": os.path.basename(path),
            "issues": [],
            "status": "failed",
            "error": str(e)
        }


def _generate_analysis_id() -> str:
    return str(uuid.uuid4())
