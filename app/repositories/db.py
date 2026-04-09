from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import settings


def _sqlite_path_from_url(url: str) -> str:
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in this prototype")
    return url.replace("sqlite:///", "", 1)


def get_connection() -> sqlite3.Connection:
    db_path = _sqlite_path_from_url(settings.database_url)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_user TEXT NOT NULL,
            calendar_owner TEXT NOT NULL,
            event_id TEXT NOT NULL,
            start_at TEXT NOT NULL,
            end_at TEXT NOT NULL,
            duration_min INTEGER NOT NULL,
            is_all_day INTEGER NOT NULL,
            show_as TEXT NOT NULL,
            response_status TEXT NOT NULL,
            is_organizer INTEGER NOT NULL,
            fetched_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_user TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            schedule_busy_score INTEGER NOT NULL,
            visual_busy_score INTEGER NOT NULL,
            blended_busy_score INTEGER NOT NULL,
            talk_ok_score INTEGER NOT NULL,
            confidence REAL NOT NULL,
            reasons_json TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            image_saved_flag INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
