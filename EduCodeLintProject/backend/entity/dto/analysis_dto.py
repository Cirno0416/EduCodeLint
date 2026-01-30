from dataclasses import dataclass, field


@dataclass
class AnalysisDTO:
    id: str
    file_count: int
    created_at: str
    status: str = field(default="pending")
