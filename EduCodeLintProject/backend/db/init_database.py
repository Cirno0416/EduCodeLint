import sqlite3
import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "ECL_code_quality.db")


def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(
        DB_PATH,
        timeout=10,                # 防止瞬间锁冲突
        isolation_level=None       # 自动事务
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id TEXT PRIMARY KEY,
            file_count INTEGER,     -- 分析的文件数量
            created_at TEXT,        -- 分析任务创建时间
            status TEXT             -- 分析任务状态 (pending, success, failed)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT,       -- 所属分析任务ID
            file_path TEXT,         -- 源文件路径
            total_score REAL        -- 文件得分
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metric_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INT,            -- 所属的文件ID
            metric_category TEXT,   -- 指标类别
            issue_count INTEGER,    -- 指标出现次数
            score REAL              -- 指标得分
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_summary_id INT, -- 所属指标总结ID
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
        CREATE TABLE IF NOT EXISTS weight_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT NOT NULL,
            metric_category TEXT NOT NULL,
            weight REAL NOT NULL,
            weighted_error REAL NOT NULL,   -- 该轮的 E_k 值
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comparison (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,        -- 对比任务创建时间
            analysis_id_1 TEXT,     -- 进行对比的批次 1
            analysis_id_2 TEXT      -- 进行对比的批次 2
        );
    """)

    conn.commit()
    conn.close()
