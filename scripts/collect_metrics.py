from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

CSV_FIELDS = [
    "run_id",
    "run_number",
    "run_url",
    "commit_sha",
    "commit_message",
    "status",
    "workflow_duration",
    "job_name",
    "job_duration",
    "step_name",
    "step_duration",
    "test_count",
    "test_failures",
    "test_avg_time",
    "timestamp",
]


@dataclass(frozen=True)
class TestSummary:
    count: int = 0
    failures: int = 0
    total_time: float = 0.0

    @property
    def average_time(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_time / self.count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Coleta metricas reais do GitHub Actions e gera CSV estruturado."
    )
    parser.add_argument("--repo", default="Anacajp/ponderada-pipe", help="Repositorio owner/name.")
    parser.add_argument("--workflow", default="eventops-ci.yml", help="Arquivo do workflow.")
    parser.add_argument("--branch", default="main", help="Branch usada no experimento.")
    parser.add_argument("--limit", type=int, default=12, help="Quantidade de runs mais recentes.")
    parser.add_argument(
        "--output",
        default="entregaveis/dados/pipeline_metrics.csv",
        help="Caminho do CSV final.",
    )
    parser.add_argument(
        "--runs-output",
        default="entregaveis/dados/workflow_runs.json",
        help="JSON auxiliar com links das execucoes.",
    )
    parser.add_argument(
        "--skip-artifacts",
        action="store_true",
        help="Nao baixa artefatos JUnit; deixa metricas de teste zeradas.",
    )
    return parser.parse_args()


def run_gh_json(args: list[str], retries: int = 3) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, retries + 1):
        completed = subprocess.run(
            ["gh", *args],
            check=False,
            capture_output=True,
            encoding="utf-8",
            timeout=60,
        )
        if completed.returncode == 0:
            return json.loads(completed.stdout)

        last_error = completed.stderr.strip() or completed.stdout.strip()
        if attempt < retries:
            time.sleep(2 * attempt)

    raise RuntimeError(f"gh {' '.join(args)} falhou apos {retries} tentativas: {last_error}")


def gh_available() -> bool:
    return shutil.which("gh") is not None


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def duration_seconds(started_at: str | None, completed_at: str | None) -> float:
    start = parse_timestamp(started_at)
    end = parse_timestamp(completed_at)
    if start is None or end is None:
        return 0.0
    return round((end - start).total_seconds(), 3)


def fetch_runs(repo: str, workflow: str, branch: str, limit: int) -> list[dict[str, Any]]:
    path = (
        f"/repos/{repo}/actions/workflows/{workflow}/runs"
        f"?branch={branch}&per_page={max(limit, 1)}"
    )
    payload = run_gh_json(["api", path])
    runs = payload.get("workflow_runs", [])
    return runs[:limit]


def fetch_jobs(repo: str, run_id: int) -> list[dict[str, Any]]:
    payload = run_gh_json(["api", f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"])
    return payload.get("jobs", [])


def download_artifacts(repo: str, run_id: int, destination: Path) -> None:
    for attempt in range(1, 4):
        completed = subprocess.run(
            ["gh", "run", "download", str(run_id), "--repo", repo, "--dir", str(destination)],
            check=False,
            capture_output=True,
            encoding="utf-8",
            timeout=90,
        )
        if completed.returncode == 0:
            return
        if attempt < 3:
            time.sleep(2 * attempt)


def parse_junit_files(root: Path) -> TestSummary:
    total = TestSummary()
    for xml_path in root.rglob("*.xml"):
        try:
            xml_root = ET.parse(xml_path).getroot()
        except ET.ParseError:
            continue
        total = add_summary(total, summary_from_xml(xml_root))
    return total


def summary_from_xml(element: ET.Element) -> TestSummary:
    suites = list(element.findall("testsuite")) if element.tag == "testsuites" else [element]
    count = 0
    failures = 0
    total_time = 0.0

    for suite in suites:
        count += int(float(suite.attrib.get("tests", 0)))
        failures += int(float(suite.attrib.get("failures", 0)))
        failures += int(float(suite.attrib.get("errors", 0)))
        total_time += float(suite.attrib.get("time", 0.0))

    return TestSummary(count=count, failures=failures, total_time=round(total_time, 3))


def add_summary(first: TestSummary, second: TestSummary) -> TestSummary:
    return TestSummary(
        count=first.count + second.count,
        failures=first.failures + second.failures,
        total_time=round(first.total_time + second.total_time, 3),
    )


def build_rows(repo: str, runs: list[dict[str, Any]], skip_artifacts: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="eventops-metrics-") as temp_dir:
        artifacts_root = Path(temp_dir)

        for run in runs:
            run_id = run["id"]
            jobs = fetch_jobs(repo, run_id)
            test_summary = TestSummary()

            if not skip_artifacts:
                run_artifacts_dir = artifacts_root / str(run_id)
                run_artifacts_dir.mkdir(parents=True, exist_ok=True)
                download_artifacts(repo, run_id, run_artifacts_dir)
                test_summary = parse_junit_files(run_artifacts_dir)

            run_duration = duration_seconds(run.get("run_started_at"), run.get("updated_at"))
            status = run.get("conclusion") or run.get("status") or "unknown"
            commit_message = (run.get("head_commit") or {}).get("message") or ""
            commit_message = commit_message.splitlines()[0]

            for job in jobs:
                job_duration = duration_seconds(job.get("started_at"), job.get("completed_at"))
                steps = job.get("steps") or [{"name": "", "started_at": None, "completed_at": None}]
                for step in steps:
                    rows.append(
                        {
                            "run_id": run_id,
                            "run_number": run.get("run_number", ""),
                            "run_url": run.get("html_url", ""),
                            "commit_sha": run.get("head_sha", ""),
                            "commit_message": commit_message,
                            "status": status,
                            "workflow_duration": run_duration,
                            "job_name": job.get("name", ""),
                            "job_duration": job_duration,
                            "step_name": step.get("name", ""),
                            "step_duration": duration_seconds(
                                step.get("started_at"),
                                step.get("completed_at"),
                            ),
                            "test_count": test_summary.count,
                            "test_failures": test_summary.failures,
                            "test_avg_time": round(test_summary.average_time, 6),
                            "timestamp": run.get("created_at", ""),
                        }
                    )

    return rows


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_runs_json(runs: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    slim_runs = [
        {
            "run_id": run.get("id"),
            "run_number": run.get("run_number"),
            "status": run.get("conclusion") or run.get("status"),
            "url": run.get("html_url"),
            "commit_sha": run.get("head_sha"),
            "commit_message": ((run.get("head_commit") or {}).get("message") or "").splitlines()[0],
            "created_at": run.get("created_at"),
        }
        for run in runs
    ]
    output_path.write_text(json.dumps(slim_runs, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not gh_available():
        raise SystemExit("GitHub CLI nao encontrado. Instale o gh e rode gh auth login.")

    runs = fetch_runs(args.repo, args.workflow, args.branch, args.limit)
    rows = build_rows(args.repo, runs, args.skip_artifacts)
    write_csv(rows, Path(args.output))
    write_runs_json(runs, Path(args.runs_output))

    print(f"CSV gerado em {args.output} com {len(rows)} linhas.")
    print(f"JSON auxiliar gerado em {args.runs_output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
