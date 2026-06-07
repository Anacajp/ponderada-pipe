from __future__ import annotations

from datetime import datetime

from eventops.conflicts import detect_conflicts
from eventops.models import Event


def make_event(
    name: str,
    room_id: str,
    start: str,
    duration_minutes: int = 60,
    attendees: int = 20,
    features: frozenset[str] = frozenset({"projector"}),
) -> Event:
    return Event(
        name=name,
        room_id=room_id,
        start=datetime.fromisoformat(start),
        duration_minutes=duration_minutes,
        expected_attendees=attendees,
        required_features=features,
        priority=1,
    )


def test_detects_capacity_conflict() -> None:
    event = make_event("Aula magna compacta demais", "A01", "2026-06-10T10:00:00", attendees=90)

    conflicts = detect_conflicts([event])

    assert [conflict.kind for conflict in conflicts] == ["capacity"]


def test_detects_missing_feature_conflict() -> None:
    event = make_event(
        "Laboratorio pratico",
        "A02",
        "2026-06-10T10:00:00",
        features=frozenset({"computers"}),
    )

    conflicts = detect_conflicts([event])

    assert [conflict.kind for conflict in conflicts] == ["missing_feature"]


def test_detects_room_overlap_conflict() -> None:
    first = make_event("Palestra A", "A03", "2026-06-10T10:00:00", duration_minutes=90)
    second = make_event("Palestra B", "A03", "2026-06-10T11:00:00", duration_minutes=60)

    conflicts = detect_conflicts([first, second])

    assert any(conflict.kind == "room_overlap" for conflict in conflicts)


def test_detects_short_buffer_between_events() -> None:
    first = make_event("Mentoria", "A04", "2026-06-10T10:00:00", duration_minutes=60)
    second = make_event("Banca", "A04", "2026-06-10T11:05:00", duration_minutes=60)

    conflicts = detect_conflicts([first, second], buffer_minutes=15)

    assert any(conflict.kind == "short_buffer" for conflict in conflicts)
