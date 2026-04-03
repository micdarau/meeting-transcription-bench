from meetingstack_bench.metrics import compute_cost_per_hour, compute_wer


def test_wer_perfect_match():
    assert compute_wer("hello world", "hello world") == 0.0


def test_wer_completely_wrong():
    score = compute_wer("hello world", "foo bar baz")
    assert score > 0.5


def test_wer_partial_match():
    score = compute_wer("the quick brown fox", "the quick brown dog")
    assert 0 < score < 1.0


def test_wer_ignores_punctuation():
    score = compute_wer("Hello, world!", "hello world")
    assert score == 0.0


def test_wer_empty_reference():
    assert compute_wer("", "") == 0.0
    assert compute_wer("", "something") == 1.0


def test_cost_known_adapter():
    cost = compute_cost_per_hour("deepgram")
    assert cost is not None
    assert cost > 0


def test_cost_unknown_adapter():
    assert compute_cost_per_hour("unknown-service") is None
