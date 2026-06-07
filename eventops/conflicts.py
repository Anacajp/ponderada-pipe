from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from eventops.models import Event, Room
from eventops.rooms import DEFAULT_ROOMS


@dataclass(frozen=True)
class Conflict:
    kind: str
    event_name: str
    room_id: str
    message: str
    other_event_name: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "kind": self.kind,
            "event_name": self.event_name,
            "room_id": self.room_id,
            "message": self.message,
            "other_event_name": self.other_event_name,
        }


def detect_conflicts(
    events: list[Event],
    rooms: tuple[Room, ...] = DEFAULT_ROOMS,
    buffer_minutes: int = 15,
) -> list[Conflict]:
    room_map = {room.id: room for room in rooms}
    conflicts: list[Conflict] = []

    for event in events:
        if event.room_id is None:
            continue

        room = room_map.get(event.room_id)
        if room is None:
            conflicts.append(
                Conflict(
                    kind="unknown_room",
                    event_name=event.name,
                    room_id=event.room_id,
                    message=f"Sala {event.room_id} nao existe no catalogo do campus.",
                )
            )
            continue

        if event.expected_attendees > room.capacity:
            conflicts.append(
                Conflict(
                    kind="capacity",
                    event_name=event.name,
                    room_id=room.id,
                    message=(
                        f"{event.name} espera {event.expected_attendees} pessoas, "
                        f"mas {room.id} comporta {room.capacity}."
                    ),
                )
            )

        missing_features = sorted(event.required_features - room.features)
        if missing_features:
            conflicts.append(
                Conflict(
                    kind="missing_feature",
                    event_name=event.name,
                    room_id=room.id,
                    message=(
                        f"{event.name} precisa de {', '.join(missing_features)}, "
                        f"mas {room.id} nao oferece esses recursos."
                    ),
                )
            )

    assigned_events = [event for event in events if event.room_id is not None]
    for first, second in combinations(assigned_events, 2):
        if first.room_id != second.room_id:
            continue

        if first.overlaps(second):
            conflicts.append(
                Conflict(
                    kind="room_overlap",
                    event_name=first.name,
                    other_event_name=second.name,
                    room_id=first.room_id or "",
                    message=(
                        f"{first.name} e {second.name} usam {first.room_id} "
                        "em horarios sobrepostos."
                    ),
                )
            )
        elif (
            first.minutes_until(second) < buffer_minutes
            or second.minutes_until(first) < buffer_minutes
        ):
            conflicts.append(
                Conflict(
                    kind="short_buffer",
                    event_name=first.name,
                    other_event_name=second.name,
                    room_id=first.room_id or "",
                    message=(
                        f"{first.name} e {second.name} deixam menos de "
                        f"{buffer_minutes} minutos de intervalo em {first.room_id}."
                    ),
                )
            )

    return conflicts
