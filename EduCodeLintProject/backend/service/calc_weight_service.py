from backend.constant.metric_category import MetricCategory, METRIC_CATEGORIES
from backend.constant.severity_level import SeverityLevel
from backend.constant.weights import DEFAULT_WEIGHTS, WEIGHT_LOWER_BOUNDS, WEIGHT_UPPER_BOUNDS


# 学习率
LEARNING_RATE = 0.01

# 单次调整最大幅度（防止震荡）
MAX_SINGLE_ADJUSTMENT = 0.05


def calc_Ek(all_summaries):
    """
    计算每个指标类别的加权错误率 E_k
    Args:
        all_summaries: 所有文件的分析结果汇总
    Returns:
        dict: 各指标类别的平均错误率 E_k
    """
    weighted_error = {}
    file_ids = set()

    for summary in all_summaries:
        file_ids.add(summary.file_id)
        category = summary.metric_category

        if category not in weighted_error:
            weighted_error[category] = 0.0

        for issue in summary.issues:
            severity = issue.severity
            alpha = SeverityLevel.COEFFICIENTS.get(
                severity,
                SeverityLevel.COEFFICIENTS[SeverityLevel.LOW]
            )

            weighted_error[category] += alpha

    file_count = max(len(file_ids), 1)

    for category in METRIC_CATEGORIES.values():
        weighted_error.setdefault(category, 0.0)
        weighted_error[category] /= file_count

    return weighted_error


def apply_weight_bounds(weights):
    """
    应用权重上下限约束，并进行归一化
    Args:
        weights: 原始权重字典
    Returns:
        dict: 约束并归一化后的权重字典
    """
    # 第一步：应用上下限约束
    bounded_weights = {}
    for cat, w in weights.items():
        lower = WEIGHT_LOWER_BOUNDS.get(cat, 0.01)
        upper = WEIGHT_UPPER_BOUNDS.get(cat, 1.0)
        bounded_weights[cat] = max(lower, min(w, upper))

    # 第二步：归一化，确保总和为 1.0
    total = sum(bounded_weights.values())
    if total > 0:
        normalized_weights = {}
        for cat, w in bounded_weights.items():
            normalized_weights[cat] = w / total
        return normalized_weights
    else:
        # 异常情况：返回默认权重
        return DEFAULT_WEIGHTS.copy()


def update_adaptive_weights(prev_weights, prev_E, curr_E):
    """
    自适应更新权重，包含上下限约束和单次调整幅度限制

    Args:
        prev_weights: 上一次分析使用的权重
        prev_E: 上一次分析的错误率 E_k
        curr_E: 本次分析的错误率 E_k

    Returns:
        dict: 更新后的权重
    """
    # 计算 Δ_k
    delta = {}
    for cat in prev_weights:
        delta[cat] = curr_E.get(cat, 0.0) - prev_E.get(cat, 0.0)

    # 计算原始更新值
    raw_weights = {}
    for cat, w in prev_weights.items():
        adjustment = LEARNING_RATE * delta.get(cat, 0.0)

        # 限制单次调整幅度
        adjustment = max(-MAX_SINGLE_ADJUSTMENT, min(adjustment, MAX_SINGLE_ADJUSTMENT))

        updated = w + adjustment
        # 防止权重为负
        raw_weights[cat] = max(updated, 0.0)

    # 应用上下限约束并归一化
    new_weights = apply_weight_bounds(raw_weights)

    return new_weights
