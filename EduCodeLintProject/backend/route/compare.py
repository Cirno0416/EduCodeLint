from flask import Blueprint, request

from backend.entity.result.result import error, success
from backend.service.compare_service import get_analysis_full, compare_analysis_batches

compare_bp = Blueprint('compare', __name__)


@compare_bp.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    analysis_id_1 = data.get("analysis_id_1")
    analysis_id_2 = data.get("analysis_id_2")

    if not analysis_id_1 or not analysis_id_2:
        return error("Both analysis IDs are required")

    analysis_1 = get_analysis_full(analysis_id_1)
    analysis_2 = get_analysis_full(analysis_id_2)

    if not analysis_1 or not analysis_2:
        return error("One or both analysis IDs are invalid")

    comparison_result = compare_analysis_batches(analysis_1, analysis_2)

    print_comparison_summary(comparison_result)

    return success(comparison_result)


def print_comparison_summary(comparison: dict):
    """打印对比摘要"""

    print("=" * 80)
    print("代码质量指标对比摘要")
    print("=" * 80)

    batch1_info = comparison["batch_info"]["batch1"]
    batch2_info = comparison["batch_info"]["batch2"]

    print(f"批次A: {batch1_info['id']} ({batch1_info['file_count']}个文件, {batch1_info['created_at']})")
    print(f"批次B: {batch2_info['id']} ({batch2_info['file_count']}个文件, {batch2_info['created_at']})")
    print()

    print("各指标对比:")
    print("-" * 80)

    for category_cn, metrics in comparison["metrics_comparison"].items():
        issues = metrics["avg_issues_per_file"]
        score = metrics["avg_score"]
        trend_symbol = {"improved": "↑", "worsened": "↓", "unchanged": "→"}[score['trend']]

        print(f"{category_cn}:")
        print(f"  平均问题数: {issues['batch1']:.1f} → {issues['batch2']:.1f} "
              f"({issues['difference']:+.2f})")
        print(f"  平均得分: {score['batch1']:.2f} → {score['batch2']:.2f} "
              f"({trend_symbol} {score['trend']})")
        print()

    summary = comparison["overall_summary"]
    print("整体对比:")
    print(f"  批次A加权总分: {summary['batch1_weighted_score']:.2f}")
    print(f"  批次B加权总分: {summary['batch2_weighted_score']:.2f}")
    print(f"  差异: {summary['weighted_difference']:+.2f} ({summary['trend']})")
    print("=" * 80)
