from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class CalendarFetchRequest(BaseModel):
    source_user: str = "me"
    start_at: datetime
    end_at: datetime
    use_cache: bool = True


class CalendarFetchResponse(BaseModel):
    fetched_count: int
    saved_count: int
    source_user: str


class CalendarEventOut(BaseModel):
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


class AnalyzeFrameRequest(BaseModel):
    source_user: str = "me"
    captured_at: datetime
    image_base64: str = Field(min_length=10)


class AnalyzeFrameResponse(BaseModel):
    source_user: str
    captured_at: datetime
    schedule_busy_score: int
    visual_busy_score: int
    blended_busy_score: int
    talk_ok_score: int
    confidence: float
    reasons: list[str]
    comment: str
    disclaimer: str


class OpenAIVisionResult(BaseModel):
    visual_busy_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    caution: str


class GraphEventNormalized(BaseModel):
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


class ErrorPayload(BaseModel):
    error: str
    detail: dict[str, Any] | None = None
