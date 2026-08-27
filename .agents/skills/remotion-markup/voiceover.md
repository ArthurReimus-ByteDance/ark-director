---
name: voiceover
description: Adding AI-generated voiceover to Remotion compositions using TTS (via Seed Audio in this workspace)
metadata:
  tags: voiceover, audio, tts, speech, seed-audio, calculateMetadata, dynamic duration
---

# Adding AI voiceover to a Remotion composition

Generate speech audio per scene, then use [`calculateMetadata`](./calculate-metadata.md) to dynamically size the composition to match the audio.

## Audio source

In this workspace, all voice audio is generated with BytePlus Seed Audio via the
`seed_audio_generate` MCP tool (credential `BYTEPLUS_SEED_AUDIO_API_KEY`);
transcripts come from `speech_to_text`. Do not use third-party TTS/STT
providers (e.g. ElevenLabs) or a local Whisper install — they bypass the
workspace's canonical pipeline. An external TTS provider is acceptable only for
a Remotion project that is explicitly **not** part of this workspace.

## Generating audio

Call `seed_audio_generate` with the per-scene script (see the `seed-audio-prompt`
skill), download the output locally, then copy it into `public/` with a
deterministic name so Remotion can load it via `staticFile()`:

```bash
cp <generated-audio>.mp3 public/voiceover/${compositionId}/${scene.id}.mp3
```

The dynamic-duration and playback sections below are unchanged.

## Dynamic composition duration with calculateMetadata

Use [`calculateMetadata`](./calculate-metadata.md) to measure the [audio durations](../mediabunny/get-audio-duration.md) and set the composition length accordingly.

```tsx
import { CalculateMetadataFunction, staticFile } from "remotion";
import { getAudioDuration } from "./get-audio-duration";

const FPS = 30;

const SCENE_AUDIO_FILES = [
  "voiceover/my-comp/scene-01-intro.mp3",
  "voiceover/my-comp/scene-02-main.mp3",
  "voiceover/my-comp/scene-03-outro.mp3",
];

export const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  const durations = await Promise.all(
    SCENE_AUDIO_FILES.map((file) => getAudioDuration(staticFile(file))),
  );

  const sceneDurations = durations.map((durationInSeconds) => {
    return durationInSeconds * FPS;
  });

  return {
    durationInFrames: Math.ceil(sceneDurations.reduce((sum, d) => sum + d, 0)),
  };
};
```

The computed `sceneDurations` are passed into the component via a `voiceover` prop so the component knows how long each scene should be.

If the composition uses [`<TransitionSeries>`](./transitions.md), subtract the overlap from total duration: [./transitions.md#calculating-total-composition-duration](./transitions.md#calculating-total-composition-duration)

## Rendering audio in the component

See [audio.md](./audio.md) for more information on how to render audio in the component.

## Delaying audio start

See [audio.md#delaying](./audio.md#delaying) for more information on how to delay the audio start.
