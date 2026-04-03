from __future__ import annotations

from typing import TYPE_CHECKING

from .assemblyai import AssemblyAIAdapter
from .base import BaseAdapter
from .deepgram import DeepgramAdapter
from .revai import RevAIAdapter
from .whisper_openai import WhisperOpenAIAdapter

if TYPE_CHECKING:
    from ..config import Config

ADAPTERS: dict[str, type[BaseAdapter]] = {
    "deepgram": DeepgramAdapter,
    "assemblyai": AssemblyAIAdapter,
    "whisper-openai": WhisperOpenAIAdapter,
    "revai": RevAIAdapter,
}


def get_adapter(name: str, config: Config) -> BaseAdapter:
    cls = ADAPTERS.get(name)
    if cls is None:
        available = ", ".join(sorted(ADAPTERS.keys()))
        raise ValueError(f"Unknown adapter: {name}. Available: {available}")
    return cls(config)
