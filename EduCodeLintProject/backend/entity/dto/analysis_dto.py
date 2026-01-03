from dataclasses import dataclass


@dataclass
class AnalysisDTO:
    id: str
    created_at: str
    file_path: str
