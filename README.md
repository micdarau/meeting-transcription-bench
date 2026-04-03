# meeting-transcription-bench

Benchmark transcription APIs against real meeting audio. Measure what matters: word error rate, speaker diarization, latency, and cost.

Built and maintained by [meetingstack.io](https://meetingstack.io), the independent research site covering the meeting tool ecosystem.

---

## Why this exists

Existing ASR benchmarks (LibriSpeech, Common Voice) test clean speech: audiobooks, read sentences, podcast-quality audio. Meetings are different. Meetings have crosstalk, bad laptop mics, screen-share audio bleeding through, engineers reading out variable names, and people switching languages mid-sentence.

If you're choosing a transcription API for meeting recordings, you need a benchmark that tests meeting conditions. That's what this does.

## What it measures

| Metric | What it tells you |
|--------|-------------------|
| **WER** (Word Error Rate) | How many words the service got wrong vs. a human-verified transcript |
| **Diarization accuracy** | Did it correctly identify who said what |
| **Latency** | Time from upload to transcript |
| **Cost per hour** | What you'll actually pay at current API pricing |

## Quick start

```bash
pip install meetingstack-bench
```

Set your API keys:

```bash
export DEEPGRAM_API_KEY=your-key
export ASSEMBLYAI_API_KEY=your-key
export OPENAI_API_KEY=your-key
export REVAI_ACCESS_TOKEN=your-token
```

Run against all configured services:

```bash
msb run
```

Run against specific adapters:

```bash
msb run -a deepgram -a assemblyai
```

Output as markdown or JSON:

```bash
msb run -o markdown -f results.md
msb run -o json -f results.json
```

## Sample output

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Transcription Benchmark Results                     │
├────────────────┬──────────────────┬───────┬─────────────┬─────────────┤
│ Adapter        │ Sample           │   WER │ Diarization │ Latency (s) │
├────────────────┼──────────────────┼───────┼─────────────┼─────────────┤
│ deepgram       │ two-speaker-st.. │  4.2% │       91.3% │         1.2 │
│ assemblyai     │ two-speaker-st.. │  5.1% │       88.7% │         4.8 │
│ whisper-openai │ two-speaker-st.. │  6.8% │         N/A │         3.4 │
│ revai          │ two-speaker-st.. │  4.9% │       90.1% │         5.1 │
└────────────────┴──────────────────┴───────┴─────────────┴─────────────┘
```

## Supported adapters

- **Deepgram** (Nova-2)
- **AssemblyAI**
- **OpenAI Whisper** (no diarization)
- **Rev AI**

You don't need keys for all of them. The CLI skips adapters with missing keys and runs the rest.

## Using your own audio

Bring your own meeting recordings:

```bash
mkdir -p my-samples/team-standup
# Add audio.wav and transcript.json (see samples/README.md for format)
msb run -s my-samples/
```

Ground-truth transcripts use a simple JSON format with speaker labels and timestamps. See [`samples/README.md`](samples/README.md) for the full spec.

## Adding a new adapter

Create a file in `src/meetingstack_bench/adapters/`:

```python
from pathlib import Path
from ..types import Transcript
from .base import BaseAdapter

class MyAdapter(BaseAdapter):
    name = "my-service"

    async def transcribe(self, audio_path: Path) -> Transcript:
        # Call the API, normalize the response
        ...
```

Register it in `adapters/__init__.py` and open a PR.

## Development

```bash
git clone https://github.com/micdarau/meeting-transcription-bench.git
cd meeting-transcription-bench
make install
make test
```

Tests run without API keys. All adapter tests use mocked HTTP responses.

## How this connects to meetingstack.io

The benchmark numbers published on [meetingstack.io](https://meetingstack.io) are produced using this tool. Open-sourcing the methodology means anyone can verify our results, run the same tests, or contribute improvements.

Read our transcription accuracy reviews at [meetingstack.io/transcription](https://meetingstack.io/transcription).

## License

MIT. See [LICENSE](LICENSE).
