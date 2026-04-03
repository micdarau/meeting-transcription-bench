import asyncio
import wave
from abc import ABC, abstractmethod
from pathlib import Path

import httpx

from ..config import Config
from ..types import Transcript

MAX_RETRIES = 3
BACKOFF_SECONDS = [1, 2, 4]


class BaseAdapter(ABC):
    name: str

    def __init__(self, config: Config) -> None:
        self.config = config

    @abstractmethod
    async def transcribe(self, audio_path: Path) -> Transcript:
        ...

    def get_audio_duration(self, audio_path: Path) -> float:
        with wave.open(str(audio_path), "rb") as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / rate

    @staticmethod
    async def _request_with_retry(
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(BACKOFF_SECONDS[attempt])
        raise last_exc  # type: ignore[misc]
