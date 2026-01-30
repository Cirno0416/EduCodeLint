from dataclasses import dataclass


@dataclass
class MetricSummaryDTO:
    file_id: int
    metric_category: str
    issue_count: int
    score: float
