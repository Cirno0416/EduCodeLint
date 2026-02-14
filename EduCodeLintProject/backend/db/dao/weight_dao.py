import sqlite3
from datetime import datetime

from backend.constant.weights import DEFAULT_WEIGHTS
from backend.db.init_database import get_connection


def get_latest_weights_and_Ek():
    with get_connection() as conn:
        cursor = conn.cursor()

        # 找最近一次分析的记录
        cursor.execute("""
                SELECT analysis_id
                FROM weight_history
                ORDER BY id DESC
                LIMIT 1
            """)
        row = cursor.fetchone()

        # 第一次运行用初始权重
        if not row:
            return DEFAULT_WEIGHTS.copy(), {}

        last_analysis_id = row[0]

        cursor.execute("""
            SELECT metric_category, weight, weighted_error
            FROM weight_history
            WHERE analysis_id = ?
        """, (last_analysis_id,))

        prev_weights = {}
        prev_E = {}

        for cat, w, E in cursor.fetchall():
            prev_weights[cat] = w
            prev_E[cat] = E

        return prev_weights, prev_E


def insert_adaptive_weights(analysis_id: str, weights: dict, E_k: dict, conn: sqlite3.Connection):
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    for cat, w in weights.items():
        cursor.execute("""
            INSERT INTO weight_history (
                analysis_id, metric_category, weight, weighted_error, created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            analysis_id,
            cat.value if hasattr(cat, "value") else str(cat),
            float(w),
            float(E_k.get(cat, 0.0)),
            now
        ))

    conn.commit()
