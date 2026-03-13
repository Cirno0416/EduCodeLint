from collections import defaultdict

from backend.constant.metric_category import METRIC_CATEGORIES
from backend.constant.metric_name import MetricName
from backend.constant.weights import WEIGHTS


def _calc_metric_stats(summaries: list) -> dict[str, dict[str, any]]:
    """
    计算单个文件的指标统计，包括二级指标问题数量
    """
    stats = {
        category: {
            "total_issues": 0,
            "total_score": 100.0,
            "issues_by_name": defaultdict(int),  # 记录二级指标数量
            "severity_counts": defaultdict(int)
        }
        for category in METRIC_CATEGORIES.keys()
    }

    for summary in summaries:
        category = summary.metric_category

        # 更新问题数量和得分
        stats[category]["total_issues"] = summary.issue_count
        stats[category]["total_score"] = summary.score

        for issue in summary.issues:
            # 统计严重程度
            severity = issue.severity
            stats[category]["severity_counts"][severity] += 1

            # 统计二级指标问题数量
            metric_name = issue.metric_name
            stats[category]["issues_by_name"][metric_name] += 1

    return stats


def _analyze_single_batch(batch_data: dict) -> dict[str, any]:
    """
    分析单个批次的数据
    - 计算每个维度的问题数、得分、文件中问题严重度分布
    """
    file_count = batch_data["file_count"]

    # 初始化批次统计
    batch_stats = {
        category: {
            "total_issues": 0,
            "total_score": 0.0,
            "files_with_issues": 0,
            "severity_counts": defaultdict(int),
            "issues_by_name": defaultdict(int)
        }
        for category in METRIC_CATEGORIES.keys()
    }

    # 聚合所有文件的统计
    for file_item in batch_data["results"]:
        file_stats = _calc_metric_stats(file_item["summaries"])

        for category, stats in file_stats.items():
            if category not in batch_stats:
                continue

            # 累加问题数量和得分
            batch_stats[category]["total_issues"] += stats["total_issues"]
            batch_stats[category]["total_score"] += stats["total_score"]

            # 统计有问题的文件数量
            if stats["total_issues"] > 0:
                batch_stats[category]["files_with_issues"] += 1

            # 合并严重程度统计
            for severity, count in stats["severity_counts"].items():
                batch_stats[category]["severity_counts"][severity] += count

            # 二级指标问题数量累加
            for metric_name, count in stats["issues_by_name"].items():
                batch_stats[category]["issues_by_name"][metric_name] += count

    # 计算平均值
    metrics_result = {}
    for category, stats in batch_stats.items():
        # 计算二级指标平均每文件问题数
        avg_issues_by_name = {
            metric_name: count / file_count for metric_name, count in stats["issues_by_name"].items()
        }

        metrics_result[category] = {
            **stats,
            "avg_issues_per_file": stats["total_issues"] / file_count if file_count else 0,
            "avg_score": stats["total_score"] / file_count if file_count else 0,
            "files_with_issues_percentage": (stats["files_with_issues"] / file_count * 100
                                             if file_count else 0),
            "severity_counts": dict(stats["severity_counts"]),
            "avg_issues_by_name": avg_issues_by_name
        }

    return {
        "file_count": file_count,
        "metrics": metrics_result
    }


def _calculate_metric_comparison(batch1_metrics: dict, batch2_metrics: dict) -> dict[str, any]:
    """计算单个指标及二级指标的对比结果"""

    def _get_trend(diff: float, metric_type: str = "score") -> str:
        if abs(diff) < 0.001:
            return "unchanged"
        if metric_type == "score":
            return "improved" if diff > 0 else "worsened"
        return "improved" if diff < 0 else "worsened"

    # 总体问题数与分数
    issues_diff = batch2_metrics["avg_issues_per_file"] - batch1_metrics["avg_issues_per_file"]
    score_diff = batch2_metrics["avg_score"] - batch1_metrics["avg_score"]

    # 二级指标对比
    secondary_diff = {}
    all_secondary_keys = set(batch1_metrics.get("avg_issues_by_name", {}).keys()) | \
                         set(batch2_metrics.get("avg_issues_by_name", {}).keys())

    for key in all_secondary_keys:
        b1_count = batch1_metrics.get("avg_issues_by_name", {}).get(key, 0)
        b2_count = batch2_metrics.get("avg_issues_by_name", {}).get(key, 0)
        diff = b2_count - b1_count
        secondary_diff[key] = {
            "batch1": round(b1_count, 2),
            "batch2": round(b2_count, 2),
            "difference": round(diff, 2),
            "trend": _get_trend(diff, "issues")
        }

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
        },
        "secondary_metric_comparison": secondary_diff
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
    batch1_weight_config = batch1_data.get("weight_config", {})
    batch2_weight_config = batch2_data.get("weight_config", {})

    batch1_weighted = _calculate_weighted_score(
        batch1_analysis["metrics"],
        batch1_weight_config if batch1_weight_config else WEIGHTS
    )
    batch2_weighted = _calculate_weighted_score(
        batch2_analysis["metrics"],
        batch2_weight_config if batch2_weight_config else WEIGHTS
    )

    weighted_diff = batch2_weighted - batch1_weighted
    overall_trend = "improved" if weighted_diff > 0 else "worsened" if weighted_diff < 0 else "unchanged"

    return {
        "batch_info": {
            "batch1": {
                "id": batch1_data["analysis_id"],
                "file_count": batch1_analysis["file_count"],
                "created_at": batch1_data["created_at"]
            },
            "batch2": {
                "id": batch2_data["analysis_id"],
                "file_count": batch2_analysis["file_count"],
                "created_at": batch2_data["created_at"]
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
