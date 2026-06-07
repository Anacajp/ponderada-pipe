from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from eventops.models import Event


def load_events(path: str | Path) -> list[Event]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_events = payload["events"] if isinstance(payload, dict) else payload
    return [event_from_dict(raw_event) for raw_event in raw_events]


def event_from_dict(payload: dict[str, Any]) -> Event:
    return Event(
        name=str(payload["name"]),
        start=datetime.fromisoformat(str(payload["start"])),
        duration_minutes=int(payload["duration_minutes"]),
        expected_attendees=int(payload["expected_attendees"]),
        required_features=frozenset(str(item) for item in payload.get("required_features", [])),
        priority=int(payload.get("priority", 1)),
        room_id=payload.get("room_id"),
    )
