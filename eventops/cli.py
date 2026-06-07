from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from eventops.conflicts import detect_conflicts
from eventops.io import load_events
from eventops.rooms import DEFAULT_ROOMS
from eventops.scheduler import schedule_events


def _rooms_payload() -> list[dict[str, object]]:
    return [
        {
            "id": room.id,
            "capacity": room.capacity,
            "features": sorted(room.features),
        }
        for room in DEFAULT_ROOMS
    ]


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eventops",
        description="Valida e agenda eventos academicos em salas do campus.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("rooms", help="Lista as salas disponiveis.")

    validate_parser = subparsers.add_parser("validate", help="Valida conflitos em uma agenda.")
    validate_parser.add_argument("schedule_path", help="Arquivo JSON com eventos.")

    schedule_parser = subparsers.add_parser("schedule", help="Sugere uma agenda sem conflitos.")
    schedule_parser.add_argument("schedule_path", help="Arquivo JSON com eventos.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "rooms":
        _print_json({"rooms": _rooms_payload()})
        return 0

    if args.command == "validate":
        events = load_events(args.schedule_path)
        conflicts = detect_conflicts(events)
        _print_json(
            {
                "event_count": len(events),
                "conflict_count": len(conflicts),
                "conflicts": [conflict.to_dict() for conflict in conflicts],
            }
        )
        return 1 if conflicts else 0

    if args.command == "schedule":
        events = load_events(args.schedule_path)
        result = schedule_events(events)
        _print_json(result.to_dict())
        return 1 if result.unresolved else 0

    parser.error(f"Comando desconhecido: {args.command}")
    return 2
