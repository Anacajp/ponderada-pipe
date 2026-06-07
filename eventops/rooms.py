from eventops.models import Room

DEFAULT_ROOMS: tuple[Room, ...] = (
    Room("A01", 24, frozenset({"projector", "whiteboard"})),
    Room("A02", 28, frozenset({"projector", "whiteboard"})),
    Room("A03", 32, frozenset({"projector", "whiteboard", "accessibility"})),
    Room("A04", 40, frozenset({"projector", "whiteboard", "hybrid"})),
    Room("A05", 35, frozenset({"whiteboard"})),
    Room("A06", 45, frozenset({"projector", "whiteboard"})),
    Room("A07", 30, frozenset({"projector", "sound", "whiteboard"})),
    Room("A08", 36, frozenset({"projector", "whiteboard", "accessibility"})),
    Room("A09", 28, frozenset({"whiteboard"})),
    Room("A10", 42, frozenset({"projector", "whiteboard", "hybrid"})),
    Room("A11", 50, frozenset({"projector", "recording", "sound", "whiteboard"})),
    Room("A12", 26, frozenset({"computers", "projector", "whiteboard"})),
    Room("A13", 30, frozenset({"computers", "projector", "whiteboard"})),
    Room(
        "Auditorio",
        160,
        frozenset({"accessibility", "projector", "recording", "sound", "stage"}),
    ),
    Room("Multiuso", 80, frozenset({"accessibility", "modular", "projector", "sound"})),
)


def get_room(room_id: str, rooms: tuple[Room, ...] = DEFAULT_ROOMS) -> Room:
    for room in rooms:
        if room.id == room_id:
            return room
    raise KeyError(f"Sala desconhecida: {room_id}")
