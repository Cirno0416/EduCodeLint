from dataclasses import field, dataclass


@dataclass
class AnalysisVO:
    id: str
    file_count: int
    created_at: str
    exclude_tools: list
    status: str = field(default="pending")
