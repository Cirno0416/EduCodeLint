from dataclasses import dataclass
from typing import Optional


@dataclass
class MetricSummaryDTO:
    analysis_id: str
    file_path: str
    metric_category: str
    metric_name: str
    count: int
    value: Optional[float]
