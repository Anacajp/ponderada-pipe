"""EventOps Campus public API."""

from eventops.conflicts import Conflict, detect_conflicts
from eventops.models import Event, Room
from eventops.rooms import DEFAULT_ROOMS, get_room
from eventops.scheduler import ScheduleResult, schedule_events

__all__ = [
    "Conflict",
    "DEFAULT_ROOMS",
    "Event",
    "Room",
    "ScheduleResult",
    "detect_conflicts",
    "get_room",
    "schedule_events",
]
