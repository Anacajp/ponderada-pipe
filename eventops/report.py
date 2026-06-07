from __future__ import annotations

import json
from pathlib import Path

from eventops.scheduler import ScheduleResult


def write_schedule_report(result: ScheduleResult, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
