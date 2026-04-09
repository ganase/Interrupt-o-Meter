from __future__ import annotations

import json
from datetime import datetime, timezone

from app.repositories.db import get_connection


def insert_result(
    source_user: str,
    captured_at: datetime,
    schedule_busy_score: int,
    visual_busy_score: int,
    blended_busy_score: int,
    talk_ok_score: int,
    confidence: float,
    reasons: list[str],
    comment_text: str,
    image_saved_flag: bool,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO analysis_results (
            source_user, captured_at, schedule_busy_score, visual_busy_score,
            blended_busy_score, talk_ok_score, confidence, reasons_json,
            comment_text, image_saved_flag, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_user,
            captured_at.isoformat(),
            schedule_busy_score,
            visual_busy_score,
            blended_busy_score,
            talk_ok_score,
            confidence,
            json.dumps(reasons, ensure_ascii=False),
            comment_text,
            int(image_saved_flag),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
