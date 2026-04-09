from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.schemas import GraphEventNormalized
from app.services.graph_auth import acquire_graph_access_token


def normalize_response_status(raw: str | None, is_organizer: bool) -> str:
    if is_organizer:
        return "organizer"
    if not raw:
        return "unknown"
    valid = {"accepted", "tentativelyAccepted", "declined", "notResponded", "none"}
    if raw not in valid:
        return "unknown"
    if raw == "tentativelyAccepted":
        return "tentative"
    if raw == "none":
        return "unknown"
    return raw


def _dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


async def fetch_calendar_view(source_user: str, start_at: datetime, end_at: datetime) -> list[GraphEventNormalized]:
    token = acquire_graph_access_token()
    base = "https://graph.microsoft.com/v1.0"
    if source_user == "me":
        path = "/me/calendar/calendarView"
        owner = "me"
    else:
        path = f"/users/{source_user}/calendar/calendarView"
        owner = source_user

    params = {
        "startDateTime": start_at.isoformat(),
        "endDateTime": end_at.isoformat(),
        "$select": "id,start,end,isAllDay,showAs,responseStatus,organizer",
    }
    headers = {"Authorization": f"Bearer {token}"}

    events: list[GraphEventNormalized] = []
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{base}{path}", params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    now = datetime.now(timezone.utc)
    for item in data.get("value", []):
        start_dt = _dt(item["start"]["dateTime"])
        end_dt = _dt(item["end"]["dateTime"])
        duration = max(0, int((end_dt - start_dt).total_seconds() // 60))
        is_org = item.get("organizer", {}).get("emailAddress", {}).get("address") is None
        response = item.get("responseStatus", {}).get("response")
        events.append(
            GraphEventNormalized(
                source_user=source_user,
                calendar_owner=owner,
                event_id=str(item.get("id", "")),
                start_at=start_dt,
                end_at=end_dt,
                duration_min=duration,
                is_all_day=bool(item.get("isAllDay", False)),
                show_as=str(item.get("showAs", "unknown")),
                response_status=normalize_response_status(response, is_org),
                is_organizer=is_org,
                fetched_at=now,
            )
        )
    return events
