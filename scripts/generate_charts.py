from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera graficos a partir do CSV de metricas.")
    parser.add_argument(
        "--input",
        default="entregaveis/dados/pipeline_metrics.csv",
        help="CSV gerado pelo script collect_metrics.py.",
    )
    parser.add_argument(
        "--output-dir",
        default="entregaveis/graficos",
        help="Pasta onde os PNGs serao salvos.",
    )
    return parser.parse_args()


def load_metrics(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"CSV nao encontrado: {path}")
    dataframe = pd.read_csv(path)
    if dataframe.empty:
        raise SystemExit(
            "CSV existe, mas ainda nao tem dados. Rode as 12 execucoes reais e colete metricas."
        )
    return dataframe


def run_level(dataframe: pd.DataFrame) -> pd.DataFrame:
    runs = dataframe.sort_values(["timestamp", "run_id"]).drop_duplicates("run_id")
    return runs.sort_values("timestamp")


def save_pipeline_duration(runs: pd.DataFrame, output_dir: Path) -> None:
    plt.figure(figsize=(11, 5))
    labels = runs["run_number"].astype(str)
    plt.plot(labels, runs["workflow_duration"], marker="o", color="#2563eb")
    plt.title("Tempo total do pipeline por execucao")
    plt.xlabel("Numero da run")
    plt.ylabel("Duracao do workflow (s)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "01_tempo_total_pipeline.png", dpi=160)
    plt.close()


def save_job_duration(dataframe: pd.DataFrame, output_dir: Path) -> None:
    jobs = dataframe.drop_duplicates(["run_id", "job_name"]).copy()
    summary = jobs.groupby("job_name", as_index=False)["job_duration"].mean()
    summary = summary.sort_values("job_duration", ascending=True)

    plt.figure(figsize=(11, 6))
    plt.barh(summary["job_name"], summary["job_duration"], color="#0891b2")
    plt.title("Tempo medio por job")
    plt.xlabel("Duracao media (s)")
    plt.ylabel("Job")
    plt.grid(axis="x", alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "02_tempo_medio_por_job.png", dpi=160)
    plt.close()


def save_success_rate(runs: pd.DataFrame, output_dir: Path) -> None:
    counts = runs["status"].value_counts().sort_index()
    colors = ["#16a34a" if status == "success" else "#dc2626" for status in counts.index]

    plt.figure(figsize=(7, 5))
    plt.bar(counts.index, counts.values, color=colors)
    plt.title("Taxa de sucesso e falha")
    plt.xlabel("Status")
    plt.ylabel("Quantidade de execucoes")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "03_sucesso_vs_falha.png", dpi=160)
    plt.close()


def save_tests_vs_duration(runs: pd.DataFrame, output_dir: Path) -> None:
    plt.figure(figsize=(8, 5))
    plt.scatter(runs["test_count"], runs["workflow_duration"], color="#7c3aed", s=70)
    for _, row in runs.iterrows():
        plt.annotate(str(row["run_number"]), (row["test_count"], row["workflow_duration"]))
    plt.title("Quantidade de testes vs duracao do pipeline")
    plt.xlabel("Quantidade de testes")
    plt.ylabel("Duracao do workflow (s)")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "04_testes_vs_duracao.png", dpi=160)
    plt.close()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataframe = load_metrics(Path(args.input))
    runs = run_level(dataframe)

    save_pipeline_duration(runs, output_dir)
    save_job_duration(dataframe, output_dir)
    save_success_rate(runs, output_dir)
    save_tests_vs_duration(runs, output_dir)

    print(f"Graficos gerados em {output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
