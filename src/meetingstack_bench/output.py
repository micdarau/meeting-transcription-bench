from rich.console import Console
from rich.table import Table

from .types import BenchmarkReport


def format_report(report: BenchmarkReport, fmt: str) -> str:
    if fmt == "json":
        return report.model_dump_json(indent=2)
    return format_markdown(report)


def format_markdown(report: BenchmarkReport) -> str:
    lines = [
        "| Adapter | Sample | WER | Diarization | Latency (s) | Cost/hr |",
        "|---------|--------|-----|-------------|-------------|---------|",
    ]
    for r in report.results:
        diar = f"{r.diarization_accuracy:.1%}" if r.diarization_accuracy is not None else "N/A"
        cost = f"${r.cost_per_hour_usd:.2f}" if r.cost_per_hour_usd is not None else "N/A"
        row = f"| {r.adapter_name} | {r.sample_name} | {r.wer:.1%}"
        row += f" | {diar} | {r.latency_seconds:.1f} | {cost} |"
        lines.append(row)
    return "\n".join(lines)


def print_table(report: BenchmarkReport) -> None:
    table = Table(title="Transcription Benchmark Results")
    table.add_column("Adapter", style="cyan")
    table.add_column("Sample")
    table.add_column("WER", justify="right")
    table.add_column("Diarization", justify="right")
    table.add_column("Latency (s)", justify="right")
    table.add_column("Cost/hr", justify="right")

    for r in report.results:
        diar = f"{r.diarization_accuracy:.1%}" if r.diarization_accuracy is not None else "N/A"
        cost = f"${r.cost_per_hour_usd:.2f}" if r.cost_per_hour_usd is not None else "N/A"
        table.add_row(
            r.adapter_name,
            r.sample_name,
            f"{r.wer:.1%}",
            diar,
            f"{r.latency_seconds:.1f}",
            cost,
        )

    console = Console()
    console.print(table)
