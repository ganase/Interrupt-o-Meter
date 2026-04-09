from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CalendarEvent:
    source_user: str
    calendar_owner: str
    event_id: str
    start_at: datetime
    end_at: datetime
    duration_min: int
    is_all_day: bool
    show_as: str
    response_status: str
    is_organizer: bool
    fetched_at: datetime


@dataclass
class AnalysisResult:
    source_user: str
    captured_at: datetime
    schedule_busy_score: int
    visual_busy_score: int
    blended_busy_score: int
    talk_ok_score: int
    confidence: float
    reasons_json: str
    comment_text: str
    image_saved_flag: bool
    created_at: datetime
