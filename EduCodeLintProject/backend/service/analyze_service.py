import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone

from backend.constant.weights import DEFAULT_WEIGHTS
from backend.db.dao.weight_dao import get_latest_weights_and_Ek
from backend.db.writer_worker import db_writer_worker, db_queue, STOP
from backend.entity.dto.analysis_dto import AnalysisDTO
from backend.entity.dto.file_dto import FileDTO
from backend.entity.dto.metric_summary_dto import MetricSummaryDTO
from backend.service.calc_score_service import build_metric_summaries, calc_file_score
from backend.service.calc_weight_service import calc_Ek, update_adaptive_weights
from backend.service.linter_service import run_linters
from backend.service.issue_parse_service import parse_issues_to_dtos


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
    all_summaries: list[MetricSummaryDTO] = []

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
            result = future.result()
            results.append(result)

            # 收集每个文件的 summaries
            if result.get("summaries"):
                all_summaries.extend(result["summaries"])

    # 更新权重
    prev_weights, prev_E = get_latest_weights_and_Ek()

    curr_E = calc_Ek(all_summaries)

    if not prev_E:
        # 第一次运行
        new_weights = DEFAULT_WEIGHTS.copy()
    else:
        new_weights = update_adaptive_weights(
            prev_weights=prev_weights,
            prev_E=prev_E,
            curr_E=curr_E
        )

    db_queue.put(("save_weights", analysis_id, new_weights, curr_E))

    # 通知 writer 线程结束
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
            total_score=calc_file_score(summaries),
        )

        # 由 writer 顺序写
        db_queue.put(("file_result", file, summaries))

        # 分析成功，修改 analysis 状态为 success
        db_queue.put(("update_analysis_status", analysis_id, "success"))

        return {
            "file_name": os.path.basename(path),
            "issues": [asdict(d) for d in issues],      # 不返回也行
            "score": file.total_score,
            "status": "success",
            "summaries": summaries
        }

    except Exception as e:
        # 分析失败，修改 analysis 状态为 failed
        db_queue.put(("update_analysis_status", analysis_id, "failed"))

        return {
            "file_name": os.path.basename(path),
            "issues": [],
            "status": "failed",
            "error": str(e),
            "summaries": []
        }


def _generate_analysis_id() -> str:
    return str(uuid.uuid4())
