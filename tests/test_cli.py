from __future__ import annotations

import json

from eventops.cli import main


def test_rooms_command_lists_fixed_campus_rooms(capsys) -> None:
    exit_code = main(["rooms"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert len(payload["rooms"]) == 15
    assert payload["rooms"][0]["id"] == "A01"
    assert payload["rooms"][-2]["id"] == "Auditorio"
    assert payload["rooms"][-1]["id"] == "Multiuso"


def test_validate_command_returns_success_for_sample_schedule(capsys) -> None:
    exit_code = main(["validate", "data/sample_schedule.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["event_count"] == 3
    assert payload["conflict_count"] == 0
