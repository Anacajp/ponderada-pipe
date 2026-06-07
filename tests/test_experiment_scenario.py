from __future__ import annotations

import time
from datetime import datetime

import pytest

from eventops.conflicts import detect_conflicts
from eventops.experiment import load_scenario
from eventops.models import Event
from eventops.scheduler import schedule_events

SCENARIO = load_scenario()


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "synthetic_case" in metafunc.fixturenames:
        count = int(SCENARIO.get("synthetic_test_cases", 8))
        metafunc.parametrize("synthetic_case", range(count))


def test_controlled_failure_gate() -> None:
    if SCENARIO.get("force_failure", False):
        pytest.fail("Falha controlada do experimento para gerar uma run vermelha no Actions.")


def test_scenario_conflict_profile_is_detected() -> None:
    profile = SCENARIO.get("conflict_profile", "none")
    events = conflict_profile_events(profile)
    conflicts = detect_conflicts(events)

    if profile == "none":
        assert conflicts == []
    else:
        expected_kind = "room_overlap" if profile == "overlap" else profile
        assert any(conflict.kind == expected_kind for conflict in conflicts)


def test_generated_conflict_matrix(synthetic_case: int) -> None:
    room_id = f"A{(synthetic_case % 13) + 1:02d}"
    event = Event(
        name=f"Cenario sintetico {synthetic_case:02d}",
        room_id=room_id,
        start=datetime.fromisoformat("2026-06-10T14:00:00"),
        duration_minutes=45,
        expected_attendees=12 + synthetic_case % 20,
        required_features=frozenset({"whiteboard"}),
        priority=1,
    )

    result = schedule_events([event])

    assert len(result.assignments) == 1


@pytest.mark.load
def test_scenario_load_volume_and_optional_delay() -> None:
    delay = float(SCENARIO.get("slow_test_seconds", 0))
    if delay > 0:
        time.sleep(delay)

    event_count = int(SCENARIO.get("load_event_count", 120))
    start = datetime.fromisoformat("2026-06-10T08:00:00")
    events = [
        Event(
            name=f"Carga controlada {index:03d}",
            start=start,
            duration_minutes=45,
            expected_attendees=18 + (index % 24),
            required_features=frozenset({"projector"}),
            priority=1 + (index % 5),
            room_id=f"A{(index % 13) + 1:02d}",
        )
        for index in range(event_count)
    ]

    result = schedule_events(events, search_horizon_hours=12)

    assert len(result.assignments) >= min(100, int(event_count * 0.65))


def conflict_profile_events(profile: str) -> list[Event]:
    start = datetime.fromisoformat("2026-06-10T10:00:00")
    if profile == "capacity":
        return [
            Event(
                name="Aula magna em sala pequena",
                room_id="A01",
                start=start,
                duration_minutes=60,
                expected_attendees=90,
                required_features=frozenset({"projector"}),
                priority=3,
            )
        ]
    if profile == "missing_feature":
        return [
            Event(
                name="Oficina de dados sem laboratorio",
                room_id="A02",
                start=start,
                duration_minutes=60,
                expected_attendees=22,
                required_features=frozenset({"computers"}),
                priority=3,
            )
        ]
    if profile == "overlap":
        return [
            Event(
                name="Banca A",
                room_id="A03",
                start=start,
                duration_minutes=90,
                expected_attendees=20,
                required_features=frozenset({"projector"}),
                priority=3,
            ),
            Event(
                name="Banca B",
                room_id="A03",
                start=start,
                duration_minutes=60,
                expected_attendees=18,
                required_features=frozenset({"projector"}),
                priority=2,
            ),
        ]
    return []
