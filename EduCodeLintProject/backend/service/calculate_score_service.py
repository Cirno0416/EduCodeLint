import logging
from collections import defaultdict

from backend.constant.metric_category import MetricCategory
from backend.constant.metric_name import MetricName
from backend.constant.severity_level import SeverityLevel
from backend.constant.weights import WEIGHTS
from backend.entity.dto.issue_dto import IssueDTO
from backend.entity.dto.metric_summary_dto import MetricSummaryDTO


def calculate_file_score(summaries: list[MetricSummaryDTO]) -> float:
    s_final = 0.0
    s_base = 0.0
    r = 1.0
    category_scores = {category: 100.0 for category in WEIGHTS.keys()}

    for summary in summaries:
        if summary.metric_category in category_scores:
            category_scores[summary.metric_category] = summary.score
        elif summary.metric_category == MetricCategory.DOCUMENTATION:
            r = summary.score

    for category, weight in WEIGHTS.items():
        s_metric = category_scores[category]
        s_base += weight * s_metric

    s_final = s_base * r
    return s_final


def build_metric_summaries(issues: list[IssueDTO]) -> list[MetricSummaryDTO]:
    grouped: dict[str, list[IssueDTO]] = defaultdict(list)

    # 按 metric_category 分组
    for issue in issues:
        grouped[issue.metric_category].append(issue)

    summaries: list[MetricSummaryDTO] = []

    # 对每一类 issue 生成 MetricSummaryDTO
    for metric_category, group in grouped.items():
        issue_count = len(group)
        score = _calculate_score(metric_category, group)

        summaries.append(MetricSummaryDTO(
            file_id=-1,
            metric_category=metric_category,
            issue_count=issue_count,
            score=score,
            issues=group
        ))

    return summaries


def _calculate_score(metric_category: str, issues: list[IssueDTO]) -> float:
    score = 100.0
    if metric_category == MetricCategory.COMPLEXITY:
        if len(issues) > 1:
            logging.error("复杂度指标的 issue 数量不为 1")
            return score

        issue = issues[0]
        threshold = 10
        # 这里 rule_id 存储了复杂度数值
        complexity = int(issue.rule_id)
        gamma = SeverityLevel.COEFFICIENTS[issue.severity]
        score = 100 - gamma * (complexity - threshold)

    elif metric_category == (
            MetricCategory.CODE_STYLE or
            MetricCategory.CODE_SMELL or
            MetricCategory.SECURITY_VULNERABILITY or
            MetricCategory.POTENTIAL_ERROR
    ):
        for issue in issues:
            score -= SeverityLevel.COEFFICIENTS[issue.severity]

    elif metric_category == MetricCategory.DOCUMENTATION:
        score = 1.0
        for issue in issues:
            if issue.metric_name == MetricName.MISSING_MODULE_DOCSTRING:
                score = 0.90
                break
            if issue.metric_name == MetricName.NONSTANDARD_DOCSTRING:
                score = 0.95
                break

    return max(score, 0.0)
