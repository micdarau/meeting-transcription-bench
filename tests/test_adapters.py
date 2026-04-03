import wave
from pathlib import Path

import httpx
import pytest
import respx

from meetingstack_bench.adapters.assemblyai import AssemblyAIAdapter
from meetingstack_bench.adapters.deepgram import DeepgramAdapter
from meetingstack_bench.config import Config


@pytest.fixture
def tmp_audio(tmp_path: Path) -> Path:
    audio_path = tmp_path / "audio.wav"
    with wave.open(str(audio_path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(b"\x00\x00" * 16000)
    return audio_path


DEEPGRAM_RESPONSE = {
    "results": {
        "utterances": [
            {
                "speaker": 0,
                "start": 0.0,
                "end": 2.5,
                "transcript": "Hello from Deepgram.",
            },
            {
                "speaker": 1,
                "start": 3.0,
                "end": 5.0,
                "transcript": "Nice to meet you.",
            },
        ]
    }
}

ASSEMBLYAI_UPLOAD_RESPONSE = {"upload_url": "https://cdn.assemblyai.com/upload/fake123"}

ASSEMBLYAI_TRANSCRIPT_SUBMIT_RESPONSE = {"id": "transcript_abc"}

ASSEMBLYAI_TRANSCRIPT_COMPLETED_RESPONSE = {
    "id": "transcript_abc",
    "status": "completed",
    "utterances": [
        {
            "speaker": "A",
            "start": 0,
            "end": 2500,
            "text": "Hello from AssemblyAI.",
        },
        {
            "speaker": "B",
            "start": 3000,
            "end": 5000,
            "text": "Nice to meet you.",
        },
    ],
}


@respx.mock
@pytest.mark.asyncio
async def test_deepgram_adapter(tmp_audio: Path) -> None:
    respx.post("https://api.deepgram.com/v1/listen").mock(
        return_value=httpx.Response(200, json=DEEPGRAM_RESPONSE)
    )

    config = Config(deepgram_api_key="test-key")
    adapter = DeepgramAdapter(config)
    transcript = await adapter.transcribe(tmp_audio)

    assert len(transcript.segments) == 2
    assert transcript.segments[0].speaker == "Speaker 0"
    assert transcript.segments[0].text == "Hello from Deepgram."
    assert transcript.segments[0].start == 0.0
    assert transcript.segments[0].end == 2.5
    assert transcript.segments[1].speaker == "Speaker 1"
    assert transcript.segments[1].text == "Nice to meet you."
    assert "Hello from Deepgram" in transcript.full_text
    assert "Nice to meet you" in transcript.full_text


@respx.mock
@pytest.mark.asyncio
async def test_assemblyai_adapter(tmp_audio: Path) -> None:
    respx.post("https://api.assemblyai.com/v2/upload").mock(
        return_value=httpx.Response(200, json=ASSEMBLYAI_UPLOAD_RESPONSE)
    )
    respx.post("https://api.assemblyai.com/v2/transcript").mock(
        return_value=httpx.Response(200, json=ASSEMBLYAI_TRANSCRIPT_SUBMIT_RESPONSE)
    )
    respx.get("https://api.assemblyai.com/v2/transcript/transcript_abc").mock(
        return_value=httpx.Response(200, json=ASSEMBLYAI_TRANSCRIPT_COMPLETED_RESPONSE)
    )

    config = Config(assemblyai_api_key="test-key")
    adapter = AssemblyAIAdapter(config)
    transcript = await adapter.transcribe(tmp_audio)

    assert len(transcript.segments) == 2
    assert transcript.segments[0].speaker == "Speaker A"
    assert transcript.segments[0].text == "Hello from AssemblyAI."
    assert transcript.segments[0].start == pytest.approx(0.0)
    assert transcript.segments[0].end == pytest.approx(2.5)
    assert transcript.segments[1].speaker == "Speaker B"
    assert transcript.segments[1].text == "Nice to meet you."
    assert transcript.segments[1].start == pytest.approx(3.0)
    assert transcript.segments[1].end == pytest.approx(5.0)
    assert "Hello from AssemblyAI" in transcript.full_text
