from dataclasses import dataclass

from backend.entity.dto.issue_dto import IssueDTO


@dataclass
class MetricSummaryDTO:
    file_id: int
    metric_category: str
    issue_count: int
    score: float

    issues: list[IssueDTO]
