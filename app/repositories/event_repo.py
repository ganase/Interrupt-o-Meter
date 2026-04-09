from __future__ import annotations

from datetime import datetime

from app.repositories.db import get_connection
from app.schemas import GraphEventNormalized


def insert_events(events: list[GraphEventNormalized]) -> int:
    if not events:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO calendar_events (
            source_user, calendar_owner, event_id, start_at, end_at,
            duration_min, is_all_day, show_as, response_status, is_organizer, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                e.source_user,
                e.calendar_owner,
                e.event_id,
                e.start_at.isoformat(),
                e.end_at.isoformat(),
                e.duration_min,
                int(e.is_all_day),
                e.show_as,
                e.response_status,
                int(e.is_organizer),
                e.fetched_at.isoformat(),
            )
            for e in events
        ],
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def list_events(source_user: str, start_at: datetime, end_at: datetime) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT source_user, calendar_owner, event_id, start_at, end_at,
               duration_min, is_all_day, show_as, response_status, is_organizer, fetched_at
        FROM calendar_events
        WHERE source_user = ? AND start_at >= ? AND end_at <= ?
        ORDER BY start_at ASC
        """,
        (source_user, start_at.isoformat(), end_at.isoformat()),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    for row in rows:
        row["is_all_day"] = bool(row["is_all_day"])
        row["is_organizer"] = bool(row["is_organizer"])
        row["start_at"] = datetime.fromisoformat(row["start_at"])
        row["end_at"] = datetime.fromisoformat(row["end_at"])
        row["fetched_at"] = datetime.fromisoformat(row["fetched_at"])
    return rows
