import math
from collections import defaultdict

from backend.constant.metric_category import METRIC_CATEGORIES
from backend.constant.weights import DEFAULT_WEIGHTS


def compare_multiple_batches(batch_list: list[dict]) -> dict:
    # 批次分析 + 基础结果
    batch_results, metrics_summary = _analyze_and_collect_batches(batch_list)

    # 共性问题分析
    common_issues = _calculate_common_issues(metrics_summary)

    return {
        "batches": batch_results,
        "metrics_summary": metrics_summary,
        "common_issues": common_issues
    }


def _analyze_and_collect_batches(batch_list):
    """批次分析 + 聚合"""
    batch_results = []
    metrics_summary = _init_metrics_summary()

    for batch in batch_list:
        analysis = _analyze_single_batch(batch)

        batch_info = _build_batch_info(batch, analysis)
        batch_results.append(batch_info)

        _aggregate_metrics_summary(metrics_summary, batch, analysis)

    return batch_results, metrics_summary


def _init_metrics_summary():
    """初始化 summary 结构"""
    return {
        category: {
            "avg_score": [],
            "avg_issues_per_file": [],
            "files_with_issues_percentage": [],
            "severity_distribution": [],
            "secondary_metrics": []
        }
        for category in METRIC_CATEGORIES.keys()
    }


def _build_batch_info(batch, analysis):
    """构建单个 batch 信息"""
    weight_config = batch.get("weight_config", {}) or DEFAULT_WEIGHTS

    weighted_score = _calculate_weighted_score(
        analysis["metrics"],
        weight_config
    )

    return {
        "id": batch["analysis_id"],
        "created_at": batch["created_at"],
        "file_count": analysis["file_count"],
        "weighted_score": round(weighted_score, 2),
        "metrics": analysis["metrics"]
    }


def _aggregate_metrics_summary(metrics_summary, batch, analysis):
    """聚合 metrics"""
    for category, data in analysis["metrics"].items():
        metrics_summary[category]["avg_score"].append({
            "analysis_id": batch["analysis_id"],
            "value": round(data["avg_score"], 2)
        })

        metrics_summary[category]["avg_issues_per_file"].append({
            "analysis_id": batch["analysis_id"],
            "value": round(data["avg_issues_per_file"], 2)
        })

        metrics_summary[category]["files_with_issues_percentage"].append({
            "analysis_id": batch["analysis_id"],
            "value": round(data["files_with_issues_percentage"], 1)
        })

        metrics_summary[category]["severity_distribution"].append({
            "analysis_id": batch["analysis_id"],
            "value": data["avg_severity_count"]
        })

        metrics_summary[category]["secondary_metrics"].append({
            "analysis_id": batch["analysis_id"],
            "value": data["avg_issues_by_name"]
        })


def _calculate_common_issues(metrics_summary):
    """全局共性问题分析"""
    all_metric_stats = []

    for category, data in metrics_summary.items():
        secondary_list = data["secondary_metrics"]
        total_batches = len(secondary_list)

        if total_batches == 0:
            continue

        metric_values_map = _build_metric_values_map(secondary_list)

        stats = _calculate_metric_stats(
            metric_values_map,
            total_batches,
            category
        )

        all_metric_stats.extend(stats)

    # ===== 全局筛选 + 排序 =====
    return _filter_and_sort_global_common_metrics(all_metric_stats)


def _build_metric_values_map(secondary_list):
    """构建 metric_values_map"""
    metric_values_map = defaultdict(list)

    all_metric_names = set()
    for item in secondary_list:
        all_metric_names.update(item["value"].keys())

    for metric_name in all_metric_names:
        for item in secondary_list:
            metric_dict = item["value"]
            metric_values_map[metric_name].append(
                metric_dict.get(metric_name, 0)
            )

    return metric_values_map


def _calculate_metric_stats(metric_values_map, total_batches, category):
    """计算统计值（增加 category 信息）"""
    stats = []

    for metric_name, values in metric_values_map.items():
        appear_count = sum(1 for v in values if v > 0)
        support = appear_count / total_batches

        mean_val = sum(values) / total_batches

        variance = sum((v - mean_val) ** 2 for v in values) / total_batches
        std_val = math.sqrt(variance)

        # 计算公式
        common_score = support * mean_val / (1 + std_val)

        stats.append({
            "metric_name": metric_name,
            "category": category,
            "support": round(support, 2),
            "mean": round(mean_val, 2),
            "std": round(std_val, 2),
            "common_score": round(common_score, 2)
        })

    return stats


def _filter_and_sort_global_common_metrics(metric_stats):
    """全局筛选 + 排序"""
    # 过滤低共性
    filtered = [
        m for m in metric_stats if m["support"] >= 0.5
    ]

    # 排序
    filtered.sort(
        key=lambda x: x["common_score"],
        reverse=True
    )

    # 取 Top10
    return [
        {
            "metric_name": m["metric_name"],
            "category": m["category"],
            "common_score": m["common_score"]
        }
        for m in filtered[:10]
    ]


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
    分析单个批次的数据，计算每个维度的问题数、得分、文件中问题严重度分布
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

        # 计算严重程度平均每文件问题数
        avg_severity_count = {
            severity: count / file_count if file_count else 0
            for severity, count in stats["severity_counts"].items()
        }

        metrics_result[category] = {
            **stats,
            "avg_issues_per_file": stats["total_issues"] / file_count if file_count else 0,
            "avg_score": stats["total_score"] / file_count if file_count else 0,
            "files_with_issues_percentage": (stats["files_with_issues"] / file_count * 100
                                             if file_count else 0),
            "avg_severity_count": avg_severity_count,
            "avg_issues_by_name": avg_issues_by_name
        }

    return {
        "file_count": file_count,
        "metrics": metrics_result
    }


def _calculate_weighted_score(metrics: dict, weights: dict) -> float:
    """计算加权总分"""
    weighted_score = 0.0
    for category, weight in weights.items():
        if category in metrics:
            weighted_score += metrics[category]["avg_score"] * weight
    return weighted_score
