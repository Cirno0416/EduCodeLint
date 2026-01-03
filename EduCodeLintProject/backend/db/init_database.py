import sqlite3
import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "ECL_code_quality.db")


def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id TEXT PRIMARY KEY,
            created_at TEXT,        -- 分析任务创建时间
            file_path TEXT       -- 被分析的项目或文件路径
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT,       -- 所属分析任务ID
            file_path TEXT,         -- 问题所在源文件路径
            tool TEXT,              -- 发现问题的静态分析工具名称
            metric_category TEXT,   -- 代码质量指标类别
            metric_name TEXT,       -- 具体代码质量指标名称
            rule_id TEXT,           -- 工具规则编号或名称
            line INTEGER,           -- 问题所在代码行号
            severity TEXT,          -- 问题严重程度
            message TEXT            -- 问题详细描述信息
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metric_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT,       -- 所属分析任务ID
            file_path TEXT,         -- 被统计的源文件路径
            metric_category TEXT,   -- 指标类别
            metric_name TEXT,       -- 指标名称
            count INTEGER,          -- 指标出现次数
            value REAL              -- 指标数值（如复杂度等）
        );
    """)

    conn.commit()
    conn.close()
