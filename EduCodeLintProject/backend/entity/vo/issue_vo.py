from dataclasses import dataclass


@dataclass
class IssueVO:
    id: int
    metric_summary_id: int
    tool: str
    metric_category: str
    metric_name: str
    rule_id: str
    line: int
    severity: str
    message: str
