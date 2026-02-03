import sqlite3

from backend.entity.dto.file_dto import FileDTO


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
