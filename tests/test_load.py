from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from eventops.models import Event
from eventops.scheduler import schedule_events


@pytest.mark.load
def test_scheduler_handles_large_generated_agenda() -> None:
    start = datetime.fromisoformat("2026-06-10T08:00:00")
    events = [
        Event(
            name=f"Atividade {index:03d}",
            start=start + timedelta(minutes=30 * (index % 24)),
            duration_minutes=45,
            expected_attendees=18 + (index % 20),
            required_features=frozenset({"projector"}),
            priority=1 + (index % 5),
            room_id=f"A{(index % 13) + 1:02d}",
        )
        for index in range(120)
    ]

    result = schedule_events(events, search_horizon_hours=12)

    assert len(result.assignments) >= 100
