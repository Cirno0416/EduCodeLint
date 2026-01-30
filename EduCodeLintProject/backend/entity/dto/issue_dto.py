from dataclasses import dataclass


@dataclass
class IssueDTO:
    metric_summary_id: str
    tool: str
    metric_category: str
    metric_name: str
    rule_id: str
    line: int
    severity: str
    message: str
