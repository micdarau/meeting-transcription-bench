import re

from jiwer import wer

PRICING_PER_HOUR_USD: dict[str, float] = {
    "deepgram": 0.22,
    "assemblyai": 0.30,
    "whisper-openai": 0.36,
    "revai": 0.28,
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_wer(reference: str, hypothesis: str) -> float:
    ref = normalize_text(reference)
    hyp = normalize_text(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    return float(wer(ref, hyp))


def compute_cost_per_hour(adapter_name: str) -> float | None:
    return PRICING_PER_HOUR_USD.get(adapter_name)
