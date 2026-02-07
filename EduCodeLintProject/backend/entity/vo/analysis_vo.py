from dataclasses import field, dataclass


@dataclass
class AnalysisVO:
    id: str
    file_count: int
    created_at: str
    status: str = field(default="pending")
