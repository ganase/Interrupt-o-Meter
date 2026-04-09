from datetime import datetime, timedelta, timezone

from app.services.scoring import blend_busy_scores, calculate_schedule_busy_score


def test_blend_busy_scores() -> None:
    blended, talk_ok = blend_busy_scores(80, 20, 0.6, 0.4)
    assert blended == 56
    assert talk_ok == 44


def test_schedule_busy_score_positive() -> None:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    events = [
        {
            "start_at": now + timedelta(minutes=5),
            "end_at": now + timedelta(minutes=65),
            "duration_min": 60,
            "response_status": "notResponded",
            "is_organizer": True,
        },
        {
            "start_at": now + timedelta(minutes=70),
            "end_at": now + timedelta(minutes=130),
            "duration_min": 60,
            "response_status": "accepted",
            "is_organizer": False,
        },
    ]
    score = calculate_schedule_busy_score(events, now)
    assert 30 <= score <= 100
