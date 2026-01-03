from dataclasses import dataclass
from typing import Optional


@dataclass
class IssueDTO:
    analysis_id: str
    file_path: str
    tool: str
    metric_category: str
    metric_name: str
    rule_id: Optional[str]
    line: Optional[int]
    severity: str
    message: str
