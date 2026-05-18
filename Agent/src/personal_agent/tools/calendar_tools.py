import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from personal_agent.config import BASE_DIR, MAX_READ_CHARS


EVENTS_PATH = BASE_DIR / "data" / "calendar_events.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_events() -> list[dict[str, Any]]:
    if not EVENTS_PATH.exists():
        return []

    try:
        data = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(data, list):
        return [event for event in data if isinstance(event, dict)]

    return []


def _save_events(events: list[dict[str, Any]]) -> None:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_PATH.write_text(json.dumps(events, indent=2), encoding="utf-8")


def add_calendar_event(
    title: str,
    start: str,
    end: str = "",
    location: str = "",
    notes: str = "",
) -> str:
    """
    Add a calendar event to Agent/data/calendar_events.json.

    Args:
        title: Event title.
        start: Start date or datetime, ideally ISO formatted.
        end: Optional end date or datetime.
        location: Optional location.
        notes: Optional notes.
    """
    if not title or not title.strip():
        return "event title must not be empty."
    if not start or not start.strip():
        return "event start must not be empty."

    events = _load_events()
    event = {
        "id": uuid4().hex[:8],
        "title": title.strip(),
        "start": start.strip(),
        "end": end.strip(),
        "location": location,
        "notes": notes,
        "created_at": _now(),
        "updated_at": _now(),
        "cancelled": False,
    }
    events.append(event)
    events.sort(key=lambda item: str(item.get("start", "")))
    _save_events(events)
    return f"added calendar event {event['id']}: {event['title']}"


def list_calendar_events(from_date: str = "", to_date: str = "", include_cancelled: bool = False) -> str:
    """
    List calendar events with optional lexical date filtering.

    Args:
        from_date: Optional lower bound date or datetime.
        to_date: Optional upper bound date or datetime.
        include_cancelled: Include cancelled events when true.
    """
    events = _load_events()

    filtered = []
    for event in events:
        start = str(event.get("start", ""))
        if not include_cancelled and event.get("cancelled"):
            continue
        if from_date and start < from_date:
            continue
        if to_date and start > to_date:
            continue
        filtered.append(event)

    if not filtered:
        return "no calendar events found."

    lines = []
    for event in filtered:
        end = f" - {event.get('end')}" if event.get("end") else ""
        location = f" @ {event.get('location')}" if event.get("location") else ""
        state = " [cancelled]" if event.get("cancelled") else ""
        lines.append(
            f"{event.get('id')} {event.get('start')}{end}: {event.get('title')}{location}{state}"
        )

    result = "\n".join(lines)
    if len(result) > MAX_READ_CHARS:
        return result[:MAX_READ_CHARS] + "\n\n[TRUNCATED: too many events]"

    return result


def update_calendar_event(
    event_id: str,
    title: str = "",
    start: str = "",
    end: str = "",
    location: str = "",
    notes: str = "",
) -> str:
    """
    Update an existing calendar event.

    Args:
        event_id: Event id returned by add_calendar_event.
        title: Optional replacement title.
        start: Optional replacement start date or datetime.
        end: Optional replacement end date or datetime.
        location: Optional replacement location.
        notes: Optional replacement notes.
    """
    events = _load_events()
    for event in events:
        if event.get("id") != event_id:
            continue

        if title:
            event["title"] = title.strip()
        if start:
            event["start"] = start.strip()
        if end:
            event["end"] = end.strip()
        if location:
            event["location"] = location
        if notes:
            event["notes"] = notes
        event["updated_at"] = _now()
        events.sort(key=lambda item: str(item.get("start", "")))
        _save_events(events)
        return f"updated calendar event {event_id}"

    return f"calendar event not found: {event_id}"


def cancel_calendar_event(event_id: str) -> str:
    """
    Mark a calendar event as cancelled.

    Args:
        event_id: Event id returned by add_calendar_event.
    """
    events = _load_events()
    for event in events:
        if event.get("id") != event_id:
            continue

        event["cancelled"] = True
        event["updated_at"] = _now()
        _save_events(events)
        return f"cancelled calendar event {event_id}"

    return f"calendar event not found: {event_id}"
