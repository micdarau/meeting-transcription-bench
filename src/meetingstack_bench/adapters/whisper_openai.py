from pathlib import Path

import httpx

from ..config import Config
from ..types import Segment, Transcript
from .base import BaseAdapter


class WhisperOpenAIAdapter(BaseAdapter):
    name = "whisper-openai"

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for the Whisper adapter")
        self.api_key = config.openai_api_key

    async def transcribe(self, audio_path: Path) -> Transcript:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=120) as client:
            with open(audio_path, "rb") as f:
                resp = await client.post(
                    url,
                    headers=headers,
                    data={"model": "whisper-1", "response_format": "verbose_json"},
                    files={"file": (audio_path.name, f, "audio/wav")},
                )
            resp.raise_for_status()
            data = resp.json()

        segments = []
        for s in data.get("segments", []):
            segments.append(
                Segment(
                    speaker="unknown",
                    start=s.get("start", 0.0),
                    end=s.get("end", 0.0),
                    text=s.get("text", "").strip(),
                )
            )

        full_text = data.get("text", "")
        return Transcript(segments=segments, full_text=full_text)
