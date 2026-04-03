import json
import wave
from pathlib import Path

import pytest

from meetingstack_bench.types import Segment, Transcript


@pytest.fixture
def sample_ground_truth() -> Transcript:
    return Transcript(
        segments=[
            Segment(speaker="Speaker 1", start=0.0, end=3.0, text="Let's begin the standup."),
            Segment(
                speaker="Speaker 2",
                start=3.5,
                end=7.0,
                text="Sure. I finished the API migration yesterday.",
            ),
        ],
        full_text="Let's begin the standup. Sure. I finished the API migration yesterday.",
    )


@pytest.fixture
def sample_hypothesis() -> Transcript:
    return Transcript(
        segments=[
            Segment(speaker="Speaker A", start=0.0, end=3.1, text="Let's begin the stand up."),
            Segment(
                speaker="Speaker B",
                start=3.4,
                end=7.1,
                text="Sure. I finished the API migration yesterday.",
            ),
        ],
        full_text="Let's begin the stand up. Sure. I finished the API migration yesterday.",
    )


@pytest.fixture
def tmp_sample_dir(tmp_path: Path) -> Path:
    sample_dir = tmp_path / "test-sample"
    sample_dir.mkdir()

    with wave.open(str(sample_dir / "audio.wav"), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(b"\x00\x00" * 16000)

    transcript = {
        "segments": [
            {"speaker": "Speaker 1", "start": 0.0, "end": 1.0, "text": "Hello world."}
        ],
        "full_text": "Hello world.",
    }
    (sample_dir / "transcript.json").write_text(json.dumps(transcript))
    return sample_dir
