from dataclasses import dataclass


@dataclass
class FileVO:
    id: int
    analysis_id: str
    file_path: str
    total_score: float
