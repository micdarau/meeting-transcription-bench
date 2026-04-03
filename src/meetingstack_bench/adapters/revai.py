import asyncio
from pathlib import Path

import httpx

from ..config import Config
from ..types import Segment, Transcript
from .base import BaseAdapter


class RevAIAdapter(BaseAdapter):
    name = "revai"
    BASE_URL = "https://api.rev.ai/speechtotext/v1"

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        if not config.revai_access_token:
            raise ValueError("REVAI_ACCESS_TOKEN is required for the Rev AI adapter")
        self.token = config.revai_access_token

    async def transcribe(self, audio_path: Path) -> Transcript:
        headers = {"Authorization": f"Bearer {self.token}"}

        async with httpx.AsyncClient(timeout=300) as client:
            with open(audio_path, "rb") as f:
                resp = await client.post(
                    f"{self.BASE_URL}/jobs",
                    headers=headers,
                    files={"media": (audio_path.name, f, "audio/wav")},
                    data={"options": '{"skip_diarization": false}'},
                )
            resp.raise_for_status()
            job_id = resp.json()["id"]

            max_polls = 60
            for _ in range(max_polls):
                poll_resp = await client.get(
                    f"{self.BASE_URL}/jobs/{job_id}",
                    headers=headers,
                )
                poll_resp.raise_for_status()
                job = poll_resp.json()
                status = job["status"]

                if status == "transcribed":
                    break
                if status == "failed":
                    raise RuntimeError(f"Rev AI error: {job.get('failure_detail')}")
                await asyncio.sleep(3)
            else:
                raise RuntimeError(
                    f"Rev AI polling timed out after {max_polls} attempts"
                )

            transcript_resp = await client.get(
                f"{self.BASE_URL}/jobs/{job_id}/transcript",
                headers={**headers, "Accept": "application/vnd.rev.transcript.v1.0+json"},
            )
            transcript_resp.raise_for_status()
            data = transcript_resp.json()

        segments = []
        for mono in data.get("monologues", []):
            speaker = f"Speaker {mono.get('speaker', 0)}"
            elements = mono.get("elements", [])
            text_parts = []
            start = None
            end = None
            for el in elements:
                if el.get("type") == "text":
                    if start is None:
                        start = el.get("ts", 0.0)
                    end = el.get("end_ts", el.get("ts", 0.0))
                    text_parts.append(el.get("value", ""))
                elif el.get("type") == "punct":
                    text_parts.append(el.get("value", ""))

            if text_parts and start is not None:
                segments.append(
                    Segment(
                        speaker=speaker,
                        start=start,
                        end=end or start,
                        text="".join(text_parts).strip(),
                    )
                )

        full_text = " ".join(s.text for s in segments)
        return Transcript(segments=segments, full_text=full_text)
