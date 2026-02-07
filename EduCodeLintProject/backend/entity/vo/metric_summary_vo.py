from dataclasses import dataclass

from backend.entity.vo.issue_vo import IssueVO


@dataclass
class MetricSummaryVO:
    id: int
    file_id: int
    metric_category: str
    issue_count: int
    score: float

    issues: list[IssueVO]
