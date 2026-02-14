from backend.constant.metric_category import MetricCategory, METRIC_CATEGORIES
from backend.constant.severity_level import SeverityLevel


LEARNING_RATE = 0.01


def calc_Ek(all_summaries):
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


def update_adaptive_weights(prev_weights, prev_E, curr_E):
    # 计算 Δ_k
    delta = {}
    for cat in prev_weights:
        delta[cat] = curr_E.get(cat, 0.0) - prev_E.get(cat, 0.0)

    # 更新权重
    new_weights = {}
    for cat, w in prev_weights.items():
        updated = w + LEARNING_RATE * delta.get(cat, 0.0)
        # 防止权重为负
        new_weights[cat] = max(updated, 0.01)

    # 归一化
    total = sum(new_weights.values())
    for cat in new_weights:
        new_weights[cat] /= total

    return new_weights
