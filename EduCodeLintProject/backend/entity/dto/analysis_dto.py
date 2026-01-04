from dataclasses import dataclass, field


@dataclass
class AnalysisDTO:
    id: str
    created_at: str
    status: str = field(default="pending")
