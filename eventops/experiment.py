from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_SCENARIO_PATH = Path("experiment/scenario.json")


def load_scenario(path: str | Path = DEFAULT_SCENARIO_PATH) -> dict[str, Any]:
    scenario_path = Path(path)
    if not scenario_path.exists():
        return {
            "id": "local-default",
            "pipeline_mode": "parallel",
            "synthetic_test_cases": 8,
            "load_event_count": 120,
            "slow_test_seconds": 0,
            "force_failure": False,
            "conflict_profile": "none",
        }
    return json.loads(scenario_path.read_text(encoding="utf-8"))
