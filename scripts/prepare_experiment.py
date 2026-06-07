from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

SCENARIOS_PATH = Path("experiment/scenarios.json")
SCENARIO_PATH = Path("experiment/scenario.json")
CACHE_SALT_PATH = Path("experiment/cache_salt.txt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aplica cenarios controlados para gerar as 12 execucoes reais."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="Lista os cenarios disponiveis.")

    apply_parser = subparsers.add_parser(
        "apply",
        help="Aplica um cenario em experiment/scenario.json.",
    )
    apply_parser.add_argument("scenario_id", help="ID do cenario: 01 a 12.")
    apply_parser.add_argument(
        "--commit",
        action="store_true",
        help="Cria commit com a mensagem padronizada do cenario.",
    )

    return parser.parse_args()


def load_scenarios() -> list[dict[str, Any]]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


def find_scenario(scenario_id: str) -> dict[str, Any]:
    normalized = scenario_id.zfill(2)
    for scenario in load_scenarios():
        if scenario["id"] == normalized:
            return scenario
    raise SystemExit(
        f"Cenario {scenario_id} nao encontrado. "
        "Use: python scripts/prepare_experiment.py list"
    )


def scenario_payload(scenario: dict[str, Any]) -> dict[str, Any]:
    ignored_keys = {"commit_message"}
    return {key: value for key, value in scenario.items() if key not in ignored_keys}


def write_scenario(scenario: dict[str, Any]) -> None:
    payload = scenario_payload(scenario)
    SCENARIO_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    CACHE_SALT_PATH.write_text(f"{scenario['cache_salt']}\n", encoding="utf-8")


def commit_scenario(scenario: dict[str, Any]) -> None:
    subprocess.run(["git", "add", str(SCENARIO_PATH), str(CACHE_SALT_PATH)], check=True)
    subprocess.run(["git", "commit", "-m", scenario["commit_message"]], check=True)


def list_scenarios() -> None:
    for scenario in load_scenarios():
        print(f"{scenario['id']} - {scenario['title']} ({scenario['pipeline_mode']})")


def main() -> int:
    args = parse_args()

    if args.command == "list":
        list_scenarios()
        return 0

    if args.command == "apply":
        scenario = find_scenario(args.scenario_id)
        write_scenario(scenario)
        print(f"Cenario {scenario['id']} aplicado: {scenario['title']}")
        print(f"Mensagem de commit sugerida: {scenario['commit_message']}")
        if args.commit:
            commit_scenario(scenario)
            print("Commit criado. Agora rode: git push origin main")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
