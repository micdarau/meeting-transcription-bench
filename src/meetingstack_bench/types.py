from pydantic import BaseModel


class Segment(BaseModel):
    speaker: str
    start: float
    end: float
    text: str


class Transcript(BaseModel):
    segments: list[Segment]
    full_text: str


class BenchmarkResult(BaseModel):
    adapter_name: str
    sample_name: str
    wer: float
    diarization_accuracy: float | None
    latency_seconds: float
    cost_per_hour_usd: float | None
    transcript: Transcript


class BenchmarkReport(BaseModel):
    results: list[BenchmarkResult]
    timestamp: str
