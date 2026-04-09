from __future__ import annotations

import csv
import io

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.repositories.event_repo import insert_events, list_events
from app.schemas import CalendarEventOut, CalendarFetchRequest, CalendarFetchResponse
from app.services.cache import TTLCache
from app.services.graph_calendar import fetch_calendar_view
from app.config import settings

router = APIRouter(prefix="/api/calendar", tags=["calendar"])
cache = TTLCache[list]()


@router.post("/fetch", response_model=CalendarFetchResponse)
async def fetch_calendar(req: CalendarFetchRequest) -> CalendarFetchResponse:
    cache_key = f"{req.source_user}:{req.start_at.isoformat()}:{req.end_at.isoformat()}"
    events = cache.get(cache_key) if req.use_cache else None

    if events is None:
        try:
            events = await fetch_calendar_view(req.source_user, req.start_at, req.end_at)
            if req.use_cache:
                cache.set(cache_key, events, settings.calendar_cache_ttl_sec)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Graph fetch failed: {exc}") from exc

    saved = insert_events(events)
    return CalendarFetchResponse(fetched_count=len(events), saved_count=saved, source_user=req.source_user)


@router.get("/events", response_model=list[CalendarEventOut])
def get_events(
    source_user: str = Query("me"),
    start_at: str = Query(...),
    end_at: str = Query(...),
) -> list[CalendarEventOut]:
    from datetime import datetime

    start = datetime.fromisoformat(start_at)
    end = datetime.fromisoformat(end_at)
    rows = list_events(source_user=source_user, start_at=start, end_at=end)
    return [CalendarEventOut(**r) for r in rows]


@router.get("/events.csv")
def export_events_csv(
    source_user: str = Query("me"),
    start_at: str = Query(...),
    end_at: str = Query(...),
) -> StreamingResponse:
    from datetime import datetime

    rows = list_events(source_user, datetime.fromisoformat(start_at), datetime.fromisoformat(end_at))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "source_user",
            "calendar_owner",
            "event_id",
            "start_at",
            "end_at",
            "duration_min",
            "is_all_day",
            "show_as",
            "response_status",
            "is_organizer",
            "fetched_at",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                r["source_user"],
                r["calendar_owner"],
                r["event_id"],
                r["start_at"].isoformat(),
                r["end_at"].isoformat(),
                r["duration_min"],
                r["is_all_day"],
                r["show_as"],
                r["response_status"],
                r["is_organizer"],
                r["fetched_at"].isoformat(),
            ]
        )
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
