import wave
from abc import ABC, abstractmethod
from pathlib import Path

from ..config import Config
from ..types import Transcript


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
