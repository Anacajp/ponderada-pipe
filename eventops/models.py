from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Room:
    id: str
    capacity: int
    features: frozenset[str]

    def supports(self, event: Event) -> bool:
        has_capacity = event.expected_attendees <= self.capacity
        has_features = event.required_features <= self.features
        return has_capacity and has_features


@dataclass(frozen=True)
class Event:
    name: str
    start: datetime
    duration_minutes: int
    expected_attendees: int
    required_features: frozenset[str]
    priority: int = 1
    room_id: str | None = None

    @property
    def end(self) -> datetime:
        return self.start + timedelta(minutes=self.duration_minutes)

    def with_start(self, start: datetime) -> Event:
        return Event(
            name=self.name,
            start=start,
            duration_minutes=self.duration_minutes,
            expected_attendees=self.expected_attendees,
            required_features=self.required_features,
            priority=self.priority,
            room_id=self.room_id,
        )

    def overlaps(self, other: Event) -> bool:
        return self.start < other.end and other.start < self.end

    def minutes_until(self, other: Event) -> int:
        if self.end <= other.start:
            return int((other.start - self.end).total_seconds() // 60)
        return 10**9
