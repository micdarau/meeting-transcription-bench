# Audio samples

Each sample directory contains:

- `audio.wav` -- the meeting recording (WAV, 16kHz mono recommended)
- `transcript.json` -- human-verified ground-truth transcript

## Transcript format

```json
{
  "segments": [
    {
      "speaker": "Speaker 1",
      "start": 0.0,
      "end": 3.2,
      "text": "Let's begin the standup."
    },
    {
      "speaker": "Speaker 2",
      "start": 3.5,
      "end": 6.1,
      "text": "Sure. I finished the API migration yesterday."
    }
  ],
  "full_text": "Let's begin the standup. Sure. I finished the API migration yesterday."
}
```

## Contributing samples

To add a new sample:

1. Create a directory under `samples/` with a descriptive name (e.g., `four-speaker-retro`)
2. Include `audio.wav` and `transcript.json`
3. Verify the transcript manually, word by word
4. Tag the audio characteristics in the directory name: speaker count, noise level, meeting type

Audio should be recorded or scripted with consent. Do not submit recordings of real meetings without all participants' written permission.
