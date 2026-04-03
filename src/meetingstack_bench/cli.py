import asyncio
from pathlib import Path

import click

from . import __version__
from .adapters import ADAPTERS
from .config import load_config
from .output import format_report, print_table
from .runner import discover_samples, run_benchmark


@click.group()
@click.version_option(version=__version__, prog_name="meetingstack-bench")
def cli() -> None:
    """Benchmark transcription APIs against meeting audio."""


@cli.command()
@click.option(
    "--adapter",
    "-a",
    multiple=True,
    help="Adapter(s) to benchmark. Use multiple times or 'all'.",
)
@click.option(
    "--samples-dir",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to samples directory.",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["markdown", "json", "table"]),
    default="table",
    help="Output format.",
)
@click.option(
    "--output-file",
    "-f",
    type=click.Path(path_type=Path),
    default=None,
    help="Write output to file instead of stdout.",
)
def run(
    adapter: tuple[str, ...],
    samples_dir: Path | None,
    output: str,
    output_file: Path | None,
) -> None:
    """Run benchmarks against one or more transcription services."""
    adapter_names = list(adapter)
    if not adapter_names or "all" in adapter_names:
        adapter_names = list(ADAPTERS.keys())

    overrides: dict = {}
    if samples_dir:
        overrides["samples_dir"] = samples_dir

    config = load_config(**overrides)

    available = []
    skipped = []
    for name in adapter_names:
        try:
            from .adapters import get_adapter

            get_adapter(name, config)
            available.append(name)
        except ValueError as e:
            skipped.append((name, str(e)))

    if not available:
        click.echo("No adapters available. Set API keys in your environment.")
        click.echo("See .env.example for required variables.")
        raise SystemExit(1)

    if skipped:
        for name, reason in skipped:
            click.echo(f"Skipping {name}: missing API key", err=True)

    click.echo(f"Running benchmarks: {', '.join(available)}")
    report = asyncio.run(run_benchmark(available, config.samples_dir, config))

    if output == "table":
        print_table(report)
    else:
        text = format_report(report, output)
        if output_file:
            output_file.write_text(text)
            click.echo(f"Results written to {output_file}")
        else:
            click.echo(text)


@cli.command("list-adapters")
def list_adapters() -> None:
    """List available transcription adapters."""
    for name in sorted(ADAPTERS.keys()):
        click.echo(f"  {name}")


@cli.command("list-samples")
@click.option(
    "--samples-dir",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
def list_samples(samples_dir: Path | None) -> None:
    """List discovered audio samples."""
    config = load_config()
    path = samples_dir or config.samples_dir
    samples = discover_samples(path)
    if not samples:
        click.echo(f"No samples found in {path}")
        return
    for name, _ in samples:
        click.echo(f"  {name}")
