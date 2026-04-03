import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .adapters import get_adapter
from .config import Config
from .diarization import compute_diarization_accuracy
from .metrics import compute_cost_per_hour, compute_wer
from .types import BenchmarkReport, BenchmarkResult, Segment, Transcript


def discover_samples(samples_dir: Path) -> list[tuple[str, Path]]:
    samples = []
    if not samples_dir.exists():
        return samples
    for d in sorted(samples_dir.iterdir()):
        if d.is_dir() and (d / "audio.wav").exists() and (d / "transcript.json").exists():
            samples.append((d.name, d))
    return samples


def load_ground_truth(path: Path) -> Transcript:
    data = json.loads((path / "transcript.json").read_text())
    segments = [Segment(**s) for s in data["segments"]]
    full_text = data.get("full_text", " ".join(s.text for s in segments))
    return Transcript(segments=segments, full_text=full_text)


async def run_single(
    adapter_name: str, sample_name: str, sample_dir: Path, config: Config
) -> BenchmarkResult:
    adapter = get_adapter(adapter_name, config)
    ground_truth = load_ground_truth(sample_dir)
    audio_path = sample_dir / "audio.wav"

    start = time.perf_counter()
    hypothesis = await adapter.transcribe(audio_path)
    latency = time.perf_counter() - start

    wer_score = compute_wer(ground_truth.full_text, hypothesis.full_text)
    diar_score = compute_diarization_accuracy(ground_truth.segments, hypothesis.segments)
    cost = compute_cost_per_hour(adapter_name)

    return BenchmarkResult(
        adapter_name=adapter_name,
        sample_name=sample_name,
        wer=wer_score,
        diarization_accuracy=diar_score,
        latency_seconds=latency,
        cost_per_hour_usd=cost,
        transcript=hypothesis,
    )


async def run_benchmark(
    adapter_names: list[str], samples_dir: Path, config: Config
) -> BenchmarkReport:
    samples = discover_samples(samples_dir)
    if not samples:
        raise RuntimeError(f"No samples found in {samples_dir}")

    tasks = []
    for adapter_name in adapter_names:
        for sample_name, sample_dir in samples:
            tasks.append(run_single(adapter_name, sample_name, sample_dir, config))

    results = await asyncio.gather(*tasks)

    return BenchmarkReport(
        results=list(results),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
