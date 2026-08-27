---
name: transcribe-captions
description: Transcribing audio to generate captions in Remotion (via speech_to_text in this workspace)
metadata:
  tags: captions, transcribe, speech-to-text, audio
---

# Transcribing audio

In this workspace, transcribe audio with the `speech_to_text` MCP tool. Do not
install `@remotion/install-whisper-cpp` or a local Whisper model — that bypasses
the workspace's canonical transcription pipeline. (A standalone Remotion project
outside this workspace may still use `@remotion/install-whisper-cpp`.)

## Transcribing

1. Call `speech_to_text` on the audio clip.
2. Convert the returned word- or sentence-level timestamps into Remotion
   caption segments and write them to `public/`:

```json
[{"text": "Hello world", "startMs": 0, "endMs": 1260}]
```

3. Feed the JSON into [Displaying captions](display-captions.md) to render the
   captions in the composition.

Transcribe each clip individually and create multiple JSON files.

See [Displaying captions](display-captions.md) for how to display the captions in Remotion.
