from collections import defaultdict

from backend.constant.metric_category import METRIC_CATEGORIES
from backend.constant.weights import WEIGHTS
from backend.db.dao.analysis_dao import get_analysis_by_id
from backend.db.dao.file_dao import get_files_by_analysis_id
from backend.db.dao.issue_dao import get_issues_by_metric_summary_id
from backend.db.dao.metric_summary_dao import get_metric_summaries_by_file_id
from backend.db.init_database import get_connection


def get_analysis_full(analysis_id: str) -> dict:
    conn = get_connection()

    try:
        analysis = get_analysis_by_id(analysis_id, conn)
        if not analysis:
            return {}

        result_files = []

        files = get_files_by_analysis_id(analysis_id, conn)

        for file in files:
            summaries = get_metric_summaries_by_file_id(file.id, conn)

            for summary in summaries:
                issues = get_issues_by_metric_summary_id(summary.id, conn)
                summary.issues = issues

            result_files.append({
                "file": file,
                "metric_summaries": summaries
            })

        return {
            "analysis": analysis,
            "files": result_files
        }

    finally:
        conn.close()


def _calculate_metric_stats(summaries: list) -> dict[str, dict[str, any]]:
    """计算单个文件的指标统计"""
    stats = {}

    for summary in summaries:
        category = summary.metric_category

        if category not in stats:
            stats[category] = {
                "total_issues": 0,
                "total_score": 0.0,
                "severity_counts": defaultdict(int)
            }

        stats[category]["total_issues"] += summary.issue_count
        stats[category]["total_score"] += summary.score

        # 统计严重程度
        for issue in summary.issues:
            severity = issue.severity
            stats[category]["severity_counts"][severity] += 1

    return stats


def _analyze_single_batch(batch_data: dict) -> dict[str, any]:
    """分析单个批次的数据"""
    file_count = len(batch_data["files"])

    # 初始化批次统计
    batch_stats = {
        category: {
            "total_issues": 0,
            "total_score": 0.0,
            "files_with_issues": 0,
            "severity_counts": defaultdict(int)
        }
        for category in METRIC_CATEGORIES.keys()
    }

    # 聚合所有文件的统计
    for file_item in batch_data["files"]:
        file_stats = _calculate_metric_stats(file_item["metric_summaries"])

        for category, stats in file_stats.items():
            if category not in batch_stats:
                continue

            batch_stats[category]["total_issues"] += stats["total_issues"]
            batch_stats[category]["total_score"] += stats["total_score"]

            if stats["total_issues"] > 0:
                batch_stats[category]["files_with_issues"] += 1

            # 合并严重程度统计
            for severity, count in stats["severity_counts"].items():
                batch_stats[category]["severity_counts"][severity] += count

    # 计算平均值
    result = {
        "file_count": file_count,
        "metrics": {}
    }

    for category, stats in batch_stats.items():
        result["metrics"][category] = {
            **stats,
            "avg_issues_per_file": stats["total_issues"] / file_count if file_count > 0 else 0,
            "avg_score": stats["total_score"] / file_count if file_count > 0 else 0,
            "files_with_issues_percentage": (stats["files_with_issues"] / file_count * 100
                                             if file_count > 0 else 0),
            "severity_counts": dict(stats["severity_counts"])
        }

    return result


def _calculate_metric_comparison(batch1_metrics: dict, batch2_metrics: dict) -> dict[str, any]:
    """计算单个指标的对比结果"""
    issues_diff = batch2_metrics["avg_issues_per_file"] - batch1_metrics["avg_issues_per_file"]
    score_diff = batch2_metrics["avg_score"] - batch1_metrics["avg_score"]

    def _get_trend(diff: float, metric_type: str = "score") -> str:
        if abs(diff) < 0.001:
            return "unchanged"
        if metric_type == "score":
            return "improved" if diff > 0 else "worsened"
        return "improved" if diff < 0 else "worsened"

    return {
        "avg_issues_per_file": {
            "batch1": round(batch1_metrics["avg_issues_per_file"], 2),
            "batch2": round(batch2_metrics["avg_issues_per_file"], 2),
            "difference": round(issues_diff, 2),
            "trend": _get_trend(issues_diff, "issues")
        },
        "avg_score": {
            "batch1": round(batch1_metrics["avg_score"], 2),
            "batch2": round(batch2_metrics["avg_score"], 2),
            "difference": round(score_diff, 2),
            "trend": _get_trend(score_diff, "score")
        },
        "files_with_issues_percentage": {
            "batch1": round(batch1_metrics["files_with_issues_percentage"], 1),
            "batch2": round(batch2_metrics["files_with_issues_percentage"], 1),
            "difference": round(
                batch2_metrics["files_with_issues_percentage"] -
                batch1_metrics["files_with_issues_percentage"], 1
            )
        },
        "severity_distribution": {
            "batch1": batch1_metrics["severity_counts"],
            "batch2": batch2_metrics["severity_counts"]
        }
    }


def _calculate_weighted_score(metrics: dict, weights: dict) -> float:
    """计算加权总分"""
    weighted_score = 0.0
    for category, weight in weights.items():
        if category in metrics:
            weighted_score += metrics[category]["avg_score"] * weight
    return weighted_score


def compare_analysis_batches(batch1_data: dict, batch2_data: dict) -> dict[str, any]:
    """
    对比两个批次的分析结果

    Args:
        batch1_data: get_analysis_full()返回的第一个批次数据
        batch2_data: get_analysis_full()返回的第二个批次数据

    Returns:
        包含六类指标对比结果的字典
    """
    # 分析两个批次
    batch1_analysis = _analyze_single_batch(batch1_data)
    batch2_analysis = _analyze_single_batch(batch2_data)

    # 对比每个指标
    metrics_comparison = {}
    for category in METRIC_CATEGORIES.keys():
        if category in batch1_analysis["metrics"] and category in batch2_analysis["metrics"]:
            category_name = METRIC_CATEGORIES[category]
            metrics_comparison[category_name] = _calculate_metric_comparison(
                batch1_analysis["metrics"][category],
                batch2_analysis["metrics"][category]
            )

    # 计算加权总分
    batch1_weighted = _calculate_weighted_score(
        batch1_analysis["metrics"],
        WEIGHTS
    )
    batch2_weighted = _calculate_weighted_score(
        batch2_analysis["metrics"],
        WEIGHTS
    )

    weighted_diff = batch2_weighted - batch1_weighted
    overall_trend = "improved" if weighted_diff > 0 else "worsened" if weighted_diff < 0 else "unchanged"

    return {
        "batch_info": {
            "batch1": {
                "id": batch1_data["analysis"].id,
                "file_count": batch1_analysis["file_count"],
                "created_at": batch1_data["analysis"].created_at
            },
            "batch2": {
                "id": batch2_data["analysis"].id,
                "file_count": batch2_analysis["file_count"],
                "created_at": batch2_data["analysis"].created_at
            }
        },
        "metrics_comparison": metrics_comparison,
        "overall_summary": {
            "batch1_weighted_score": round(batch1_weighted, 2),
            "batch2_weighted_score": round(batch2_weighted, 2),
            "weighted_difference": round(weighted_diff, 2),
            "trend": overall_trend
        }
    }

