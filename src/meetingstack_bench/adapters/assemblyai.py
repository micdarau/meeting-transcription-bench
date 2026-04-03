import asyncio
from pathlib import Path

import httpx

from ..config import Config
from ..types import Segment, Transcript
from .base import BaseAdapter


class AssemblyAIAdapter(BaseAdapter):
    name = "assemblyai"
    BASE_URL = "https://api.assemblyai.com/v2"

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        if not config.assemblyai_api_key:
            raise ValueError("ASSEMBLYAI_API_KEY is required for the AssemblyAI adapter")
        self.api_key = config.assemblyai_api_key

    async def transcribe(self, audio_path: Path) -> Transcript:
        headers = {"Authorization": self.api_key}

        async with httpx.AsyncClient(timeout=300) as client:
            upload_resp = await client.post(
                f"{self.BASE_URL}/upload",
                headers=headers,
                content=audio_path.read_bytes(),
            )
            upload_resp.raise_for_status()
            upload_url = upload_resp.json()["upload_url"]

            transcript_resp = await client.post(
                f"{self.BASE_URL}/transcript",
                headers=headers,
                json={"audio_url": upload_url, "speaker_labels": True},
            )
            transcript_resp.raise_for_status()
            transcript_id = transcript_resp.json()["id"]

            max_polls = 60
            for _ in range(max_polls):
                poll_resp = await client.get(
                    f"{self.BASE_URL}/transcript/{transcript_id}",
                    headers=headers,
                )
                poll_resp.raise_for_status()
                status_data = poll_resp.json()
                status = status_data["status"]

                if status == "completed":
                    break
                if status == "error":
                    raise RuntimeError(f"AssemblyAI error: {status_data.get('error')}")
                await asyncio.sleep(3)
            else:
                raise RuntimeError(
                    f"AssemblyAI polling timed out after {max_polls} attempts"
                )

        utterances = status_data.get("utterances", [])
        segments = []
        for u in utterances:
            segments.append(
                Segment(
                    speaker=f"Speaker {u.get('speaker', 'A')}",
                    start=u.get("start", 0) / 1000,
                    end=u.get("end", 0) / 1000,
                    text=u.get("text", ""),
                )
            )

        full_text = " ".join(s.text for s in segments)
        return Transcript(segments=segments, full_text=full_text)
