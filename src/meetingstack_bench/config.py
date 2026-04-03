import os
from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    deepgram_api_key: str | None = None
    assemblyai_api_key: str | None = None
    openai_api_key: str | None = None
    revai_access_token: str | None = None
    samples_dir: Path = Path(__file__).parent.parent.parent / "samples"
    output_format: str = "markdown"


def load_config(**overrides: str | Path | None) -> Config:
    env_values = {
        "deepgram_api_key": os.environ.get("DEEPGRAM_API_KEY"),
        "assemblyai_api_key": os.environ.get("ASSEMBLYAI_API_KEY"),
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "revai_access_token": os.environ.get("REVAI_ACCESS_TOKEN"),
    }
    merged = {k: v for k, v in {**env_values, **overrides}.items() if v is not None}
    return Config(**merged)
