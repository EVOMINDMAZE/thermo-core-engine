import datetime
import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "history.db"

def init_db():
    """Initialize the SQLite database with the runs table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            asset_id TEXT,
            failure_mode TEXT,
            confidence TEXT,
            total_risk TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_run(analysis_dict, asset_id="Asset-1"):
    """Save a run result into the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    run_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    failure_mode = analysis_dict.get("failure_mode", "N/A")
    confidence = str(analysis_dict.get("confidence", "N/A"))
    total_risk = str(analysis_dict.get("total_risk", "$0"))

    cursor.execute("""
        INSERT INTO runs (id, timestamp, asset_id, failure_mode, confidence, total_risk)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (run_id, timestamp, asset_id, failure_mode, confidence, total_risk))

    conn.commit()
    conn.close()
