from meetingstack_bench.diarization import compute_diarization_accuracy
from meetingstack_bench.types import Segment


def test_perfect_diarization():
    segments = [
        Segment(speaker="Speaker 1", start=0.0, end=3.0, text="Hello"),
        Segment(speaker="Speaker 2", start=3.0, end=6.0, text="World"),
    ]
    score = compute_diarization_accuracy(segments, segments)
    assert score is not None
    assert score > 0.99


def test_swapped_labels():
    ref = [
        Segment(speaker="Speaker 1", start=0.0, end=3.0, text="Hello"),
        Segment(speaker="Speaker 2", start=3.0, end=6.0, text="World"),
    ]
    hyp = [
        Segment(speaker="A", start=0.0, end=3.0, text="Hello"),
        Segment(speaker="B", start=3.0, end=6.0, text="World"),
    ]
    score = compute_diarization_accuracy(ref, hyp)
    assert score is not None
    assert score > 0.99


def test_unknown_speakers_returns_none():
    ref = [Segment(speaker="Speaker 1", start=0.0, end=3.0, text="Hello")]
    hyp = [Segment(speaker="unknown", start=0.0, end=3.0, text="Hello")]
    assert compute_diarization_accuracy(ref, hyp) is None


def test_empty_returns_none():
    assert compute_diarization_accuracy([], []) is None


def test_partial_overlap():
    ref = [
        Segment(speaker="Speaker 1", start=0.0, end=5.0, text="Hello"),
    ]
    hyp = [
        Segment(speaker="A", start=0.0, end=2.5, text="Hel"),
        Segment(speaker="B", start=2.5, end=5.0, text="lo"),
    ]
    score = compute_diarization_accuracy(ref, hyp)
    assert score is not None
    assert 0.4 < score < 0.6
