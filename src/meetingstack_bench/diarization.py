from collections import defaultdict

from .types import Segment


def compute_diarization_accuracy(
    reference: list[Segment], hypothesis: list[Segment]
) -> float | None:
    if not reference or not hypothesis:
        return None

    hyp_speakers = {s.speaker for s in hypothesis}
    if hyp_speakers == {"unknown"}:
        return None

    time_end = max(s.end for s in reference)
    resolution = 0.1
    steps = int(time_end / resolution) + 1

    def speaker_at(segments: list[Segment], t: float) -> str | None:
        for s in segments:
            if s.start <= t < s.end:
                return s.speaker
        return None

    overlap: dict[tuple[str, str], float] = defaultdict(float)
    for i in range(steps):
        t = i * resolution
        ref_spk = speaker_at(reference, t)
        hyp_spk = speaker_at(hypothesis, t)
        if ref_spk and hyp_spk:
            overlap[(ref_spk, hyp_spk)] += resolution

    mapping: dict[str, str] = {}
    used_ref: set[str] = set()
    used_hyp: set[str] = set()

    sorted_pairs = sorted(overlap.items(), key=lambda x: x[1], reverse=True)
    for (ref_spk, hyp_spk), _ in sorted_pairs:
        if ref_spk not in used_ref and hyp_spk not in used_hyp:
            mapping[hyp_spk] = ref_spk
            used_ref.add(ref_spk)
            used_hyp.add(hyp_spk)

    correct_time = 0.0
    total_time = 0.0
    for i in range(steps):
        t = i * resolution
        ref_spk = speaker_at(reference, t)
        if ref_spk:
            total_time += resolution
            hyp_spk = speaker_at(hypothesis, t)
            if hyp_spk and mapping.get(hyp_spk) == ref_spk:
                correct_time += resolution

    if total_time == 0:
        return None
    return correct_time / total_time
