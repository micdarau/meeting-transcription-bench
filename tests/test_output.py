import json

from meetingstack_bench.output import format_report
from meetingstack_bench.types import BenchmarkReport, BenchmarkResult, Transcript


def _make_report() -> BenchmarkReport:
    transcript = Transcript(segments=[], full_text="test")
    return BenchmarkReport(
        results=[
            BenchmarkResult(
                adapter_name="deepgram",
                sample_name="test-sample",
                wer=0.042,
                diarization_accuracy=0.913,
                latency_seconds=1.23,
                cost_per_hour_usd=0.22,
                transcript=transcript,
            ),
            BenchmarkResult(
                adapter_name="whisper-openai",
                sample_name="test-sample",
                wer=0.068,
                diarization_accuracy=None,
                latency_seconds=3.45,
                cost_per_hour_usd=0.36,
                transcript=transcript,
            ),
        ],
        timestamp="2026-04-03T00:00:00Z",
    )


def test_markdown_output():
    report = _make_report()
    md = format_report(report, "markdown")
    assert "| deepgram |" in md
    assert "| whisper-openai |" in md
    assert "N/A" in md
    assert md.startswith("|")


def test_json_output():
    report = _make_report()
    raw = format_report(report, "json")
    data = json.loads(raw)
    assert len(data["results"]) == 2
    assert data["results"][0]["adapter_name"] == "deepgram"
