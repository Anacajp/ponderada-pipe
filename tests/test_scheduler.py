from __future__ import annotations

from datetime import datetime

import pytest

from eventops.models import Event
from eventops.scheduler import schedule_events


def event(
    name: str,
    *,
    room_id: str | None = None,
    start: str = "2026-06-10T10:00:00",
    duration_minutes: int = 60,
    attendees: int = 20,
    features: frozenset[str] = frozenset({"projector"}),
    priority: int = 1,
) -> Event:
    return Event(
        name=name,
        room_id=room_id,
        start=datetime.fromisoformat(start),
        duration_minutes=duration_minutes,
        expected_attendees=attendees,
        required_features=features,
        priority=priority,
    )


def test_scheduler_assigns_compatible_room_for_large_event() -> None:
    result = schedule_events(
        [
            event(
                "Feira de carreiras",
                attendees=70,
                features=frozenset({"projector", "sound"}),
            )
        ]
    )

    assert result.unresolved == []
    assert result.assignments[0].room_id == "Multiuso"


def test_scheduler_keeps_higher_priority_event_in_requested_room() -> None:
    high = event("Keynote", room_id="A01", priority=5)
    low = event("Oficina paralela", room_id="A01", priority=1)

    result = schedule_events([low, high])

    by_name = {assignment.event_name: assignment for assignment in result.assignments}
    assert by_name["Keynote"].room_id == "A01"
    assert by_name["Oficina paralela"].room_id != "A01"
    assert by_name["Oficina paralela"].changed_room is True


def test_scheduler_moves_event_to_next_slot_when_all_rooms_conflict() -> None:
    compatible_room_ids = [
        "A01",
        "A02",
        "A03",
        "A04",
        "A06",
        "A07",
        "A08",
        "A10",
        "A11",
        "A12",
        "A13",
    ]
    busy_events = [
        event(
            f"Reserva {index}",
            room_id=room_id,
            attendees=20,
            features=frozenset({"projector", "whiteboard"}),
            priority=3,
        )
        for index, room_id in enumerate(compatible_room_ids, start=1)
    ]
    target = event(
        "Evento flexivel",
        room_id="A01",
        attendees=20,
        features=frozenset({"projector", "whiteboard"}),
        priority=1,
    )

    result = schedule_events([*busy_events, target], search_horizon_hours=2)
    target_assignment = next(
        assignment
        for assignment in result.assignments
        if assignment.event_name == "Evento flexivel"
    )

    assert target_assignment.start == datetime.fromisoformat("2026-06-10T11:30:00")


def test_scheduler_reports_unresolved_event_when_no_room_supports_requirements() -> None:
    result = schedule_events(
        [
            event(
                "Sessao de planetario",
                attendees=40,
                features=frozenset({"planetarium"}),
            )
        ]
    )

    assert result.assignments == []
    assert result.unresolved[0].event_name == "Sessao de planetario"


@pytest.mark.integration
def test_sample_schedule_can_be_rescheduled_without_unresolved_events() -> None:
    events = [
        event("Credenciamento", room_id="Multiuso", start="2026-06-10T08:00:00", attendees=60),
        event("Abertura", room_id="Auditorio", start="2026-06-10T09:00:00", attendees=130),
        event("Trilha dados", room_id="A12", start="2026-06-10T11:00:00", attendees=24),
        event("Trilha produto", room_id="A13", start="2026-06-10T11:00:00", attendees=25),
    ]

    result = schedule_events(events)

    assert len(result.assignments) == 4
    assert result.unresolved == []
