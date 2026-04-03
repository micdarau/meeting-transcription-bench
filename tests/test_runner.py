from pathlib import Path

from meetingstack_bench.runner import discover_samples, load_ground_truth


def test_discover_samples(tmp_sample_dir: Path):
    samples = discover_samples(tmp_sample_dir.parent)
    assert len(samples) == 1
    assert samples[0][0] == "test-sample"


def test_discover_empty(tmp_path: Path):
    assert discover_samples(tmp_path) == []


def test_load_ground_truth(tmp_sample_dir: Path):
    transcript = load_ground_truth(tmp_sample_dir)
    assert transcript.full_text == "Hello world."
    assert len(transcript.segments) == 1
    assert transcript.segments[0].speaker == "Speaker 1"
