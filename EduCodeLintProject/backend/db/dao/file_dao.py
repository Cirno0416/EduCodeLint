import sqlite3

from backend.entity.dto.file_dto import FileDTO
from backend.entity.vo.file_vo import FileVO


def insert_file(file: FileDTO, conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO file (analysis_id, file_path, total_score)
        VALUES (?, ?, ?)
    """, (
        file.analysis_id,
        file.file_path,
        file.total_score
    ))

    return cursor.lastrowid


def get_files_by_analysis_id(analysis_id: str, conn) -> list[FileVO]:
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, analysis_id, file_path, total_score
        FROM file
        WHERE analysis_id = ?
    """, (analysis_id,))

    rows = cursor.fetchall()

    return [
        FileVO(
            id=r[0],
            analysis_id=r[1],
            file_path=r[2],
            total_score=r[3]
        )
        for r in rows
    ]
