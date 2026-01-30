from dataclasses import dataclass


@dataclass
class FileDTO:
    analysis_id: str
    file_path: str
    total_score: float
