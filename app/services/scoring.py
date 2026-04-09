from __future__ import annotations

from datetime import datetime, timedelta


def _clamp(v: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, v))


def calculate_schedule_busy_score(events: list[dict], now: datetime) -> int:
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    today_events = [e for e in events if e["start_at"] < day_end and e["end_at"] > day_start]
    total_today_min = sum(e["duration_min"] for e in today_events)
    total_today_score = min((total_today_min // 60) * 10, 35)

    window_end = now + timedelta(hours=2)
    near_events = [e for e in events if e["start_at"] < window_end and e["end_at"] > now]
    near_min = sum(e["duration_min"] for e in near_events)
    near_score = min((near_min // 30) * 10, 25)

    upcoming = sorted((e for e in events if e["start_at"] >= now), key=lambda e: e["start_at"])
    gap_score = 0
    if upcoming:
        next_gap_min = int((upcoming[0]["start_at"] - now).total_seconds() // 60)
        if next_gap_min < 15:
            gap_score = 20
        elif next_gap_min < 60:
            gap_score = 10

    consecutive_score = 0
    if len(upcoming) >= 4:
        consecutive_score = 20
    elif len(upcoming) >= 2:
        consecutive_score = 10

    unanswered_count = sum(1 for e in events if e["response_status"] == "notResponded")
    unanswered_score = min(unanswered_count * 5, 15)

    organizer_count = sum(1 for e in events if e["is_organizer"])
    organizer_ratio_score = 5 if events and organizer_count / len(events) >= 0.5 else 0

    return _clamp(
        total_today_score
        + near_score
        + gap_score
        + consecutive_score
        + unanswered_score
        + organizer_ratio_score
    )


def blend_busy_scores(schedule_busy_score: int, visual_busy_score: int, sw: float, vw: float) -> tuple[int, int]:
    blended = _clamp(round(schedule_busy_score * sw + visual_busy_score * vw))
    talk_ok = _clamp(100 - blended)
    return blended, talk_ok
