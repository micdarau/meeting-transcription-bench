from pathlib import Path

import httpx

from ..config import Config
from ..types import Segment, Transcript
from .base import BaseAdapter


class DeepgramAdapter(BaseAdapter):
    name = "deepgram"

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        if not config.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY is required for the Deepgram adapter")
        self.api_key = config.deepgram_api_key

    async def transcribe(self, audio_path: Path) -> Transcript:
        url = "https://api.deepgram.com/v1/listen"
        params = {
            "model": "nova-2",
            "diarize": "true",
            "punctuate": "true",
            "utterances": "true",
        }
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            audio_data = audio_path.read_bytes()
            resp = await client.post(url, params=params, headers=headers, content=audio_data)
            resp.raise_for_status()
            data = resp.json()

        utterances = data.get("results", {}).get("utterances", [])
        segments = []
        for u in utterances:
            segments.append(
                Segment(
                    speaker=f"Speaker {u.get('speaker', 0)}",
                    start=u.get("start", 0.0),
                    end=u.get("end", 0.0),
                    text=u.get("transcript", ""),
                )
            )

        full_text = " ".join(s.text for s in segments)
        return Transcript(segments=segments, full_text=full_text)
