from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from eventops.models import Event, Room
from eventops.rooms import DEFAULT_ROOMS


@dataclass(frozen=True)
class Assignment:
    event_name: str
    room_id: str
    start: datetime
    duration_minutes: int
    changed_room: bool
    priority: int

    @property
    def end(self) -> datetime:
        return self.start + timedelta(minutes=self.duration_minutes)

    def to_event(self) -> Event:
        return Event(
            name=self.event_name,
            start=self.start,
            duration_minutes=self.duration_minutes,
            expected_attendees=0,
            required_features=frozenset(),
            priority=self.priority,
            room_id=self.room_id,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "event_name": self.event_name,
            "room_id": self.room_id,
            "start": self.start.isoformat(timespec="minutes"),
            "end": self.end.isoformat(timespec="minutes"),
            "changed_room": self.changed_room,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class UnresolvedEvent:
    event_name: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"event_name": self.event_name, "reason": self.reason}


@dataclass(frozen=True)
class ScheduleResult:
    assignments: list[Assignment]
    unresolved: list[UnresolvedEvent]

    def to_dict(self) -> dict[str, object]:
        return {
            "assignment_count": len(self.assignments),
            "unresolved_count": len(self.unresolved),
            "assignments": [assignment.to_dict() for assignment in self.assignments],
            "unresolved": [event.to_dict() for event in self.unresolved],
        }


def schedule_events(
    events: list[Event],
    rooms: tuple[Room, ...] = DEFAULT_ROOMS,
    buffer_minutes: int = 15,
    search_horizon_hours: int = 8,
) -> ScheduleResult:
    assignments: list[Assignment] = []
    unresolved: list[UnresolvedEvent] = []

    ordered_events = sorted(events, key=lambda event: (-event.priority, event.start, event.name))
    for event in ordered_events:
        scheduled = _find_assignment(event, assignments, rooms, buffer_minutes)
        if scheduled is None:
            scheduled = _find_later_assignment(
                event,
                assignments,
                rooms,
                buffer_minutes,
                search_horizon_hours,
            )

        if scheduled is None:
            unresolved.append(
                UnresolvedEvent(
                    event_name=event.name,
                    reason="Nenhuma sala compativel foi encontrada dentro da janela de busca.",
                )
            )
        else:
            assignments.append(scheduled)

    assignments.sort(
        key=lambda assignment: (assignment.start, assignment.room_id, assignment.event_name)
    )
    return ScheduleResult(assignments=assignments, unresolved=unresolved)


def _find_later_assignment(
    event: Event,
    assignments: list[Assignment],
    rooms: tuple[Room, ...],
    buffer_minutes: int,
    search_horizon_hours: int,
) -> Assignment | None:
    for offset_minutes in range(30, search_horizon_hours * 60 + 1, 30):
        candidate = event.with_start(event.start + timedelta(minutes=offset_minutes))
        assignment = _find_assignment(candidate, assignments, rooms, buffer_minutes)
        if assignment is not None:
            return assignment
    return None


def _find_assignment(
    event: Event,
    assignments: list[Assignment],
    rooms: tuple[Room, ...],
    buffer_minutes: int,
) -> Assignment | None:
    for room in _candidate_rooms(event, rooms):
        if _room_is_available(room.id, event, assignments, buffer_minutes):
            return Assignment(
                event_name=event.name,
                room_id=room.id,
                start=event.start,
                duration_minutes=event.duration_minutes,
                changed_room=event.room_id is not None and event.room_id != room.id,
                priority=event.priority,
            )
    return None


def _candidate_rooms(event: Event, rooms: tuple[Room, ...]) -> list[Room]:
    compatible = [room for room in rooms if room.supports(event)]
    compatible.sort(key=lambda room: (room.capacity, room.id))

    if event.room_id is None:
        return compatible

    requested = [room for room in compatible if room.id == event.room_id]
    alternatives = [room for room in compatible if room.id != event.room_id]
    return requested + alternatives


def _room_is_available(
    room_id: str,
    event: Event,
    assignments: list[Assignment],
    buffer_minutes: int,
) -> bool:
    candidate = Event(
        name=event.name,
        start=event.start,
        duration_minutes=event.duration_minutes,
        expected_attendees=event.expected_attendees,
        required_features=event.required_features,
        priority=event.priority,
        room_id=room_id,
    )

    for assignment in assignments:
        if assignment.room_id != room_id:
            continue

        scheduled = assignment.to_event()
        if candidate.overlaps(scheduled):
            return False
        if candidate.minutes_until(scheduled) < buffer_minutes:
            return False
        if scheduled.minutes_until(candidate) < buffer_minutes:
            return False

    return True
