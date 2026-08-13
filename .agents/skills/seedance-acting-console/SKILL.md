---
name: seedance-acting-console
description: >
  Turn a per-character (emotion, intensity, dialogue) directive into a
  production-grade Seedance acting block: an emotion bank of six emotions with
  graduated observable cues, an intensity encoding guide (levels 1-3), the
  single-transition and multi-stage acting templates, and an optional audio-first
  pipeline that reinforces the performance through Seed Audio. Use this skill
  when directing the performance, acting, emotional intensity, mood of the scene,
  facial expression, delivering a line, or asking a character to act
  happy/sad/angry/fearful. It composes with seedance-prompt-25 and
  seed-audio-prompt, never calling generation tools itself.
---

# Seedance Acting Console

The Acting Console turns a single creative directive — `(emotion, intensity,
dialogue)` for one character — into a complete, generation-ready performance
spec. It mirrors Higgsfield Cinema Studio's per-character emotion controls
(emotion dropdown + intensity slider) as a prompt-composition skill on the
BytePlus stack.

It produces two composable layers:

1. **Prompt layer** — an acting block for the Seedance prompt built from
   directly observable physical cues, using the single-emotional-transition or
   multi-stage template from `seedance-prompt-25`, with the `{dialogue}` bracket
   syntax and a delivery style.
2. **Audio-first layer (reinforcement)** — an optional pipeline that generates
   a Seed Audio dialogue track carrying the same emotion, verifies
   `audio_duration <= video_duration`, passes the WAV to Seedance as
   `reference_audio` (bound as `@Audio 1`), keeps the identical `{dialogue}`
   text in both prompts, and aligns shot timestamps to the actual audio. This
   is the stronger "acting" lever: lip-sync constrains the on-screen
   performance to the voice emotion.

This skill is **prompt-composition only**. It never calls MCP/Ark generation
tools directly; it composes with `seedance-prompt-25` (prompt grammar), the
`seedance_2_5_create_task` MCP tool (generation), and `seed-audio-prompt`
(Seed Audio voice profiles).

## Source authority

Accessed 2026-08-13. Emotion words are direction, not control; the official
Seedance 2.5 guidance requires observable cues for stable performance:

- [Seedance 2.5 Prompt Guide (Lark)](https://bytedance.larkoffice.com/docx/A88jd0B47oAd8zxWp5ycZFMfnxh) — emotional-direction section (single transition + multi-stage templates, emotion externalization table, 2-4 cue guidance)
- [Seedance 2.5 Prompt Guide (ModelArk)](https://docs.byteplus.com/en/docs/ModelArk/2607689) — same guidance on the official doc surface
- [Seedance 2.5 Launch Blog](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) — audio-first, native audio+video co-generation
- [Seed Audio 1.0 API Reference](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01) — dialogue generation, voice profiles, duration limits
- [Seed Audio 1.0 Prompting Guide](https://bytedance.larkoffice.com/wiki/WgU4wFVQ8iZgvjkHHdbcDmhCnug) — voice profile ingredients (age, gender, accent, emotion, tone, speed, timbre) and T2A/TA2A conventions
- [Higgsfield Cinema Studio help center](https://higgsfield.ai/creator-hub/help-center/tools-and-workflows/how-do-i-use-cinema-studio) and [3.5 tutorial](https://higgsfield.ai/blog/cinema-studio-3.5-full-tutorial) — the per-character emotion + intensity console this skill mirrors

**Provenance note:** Higgsfield documents a per-character emotion control and
an intensity slider. The six-emotion set below (Serenity, Joy, Terror, Rage,
Fear, Vigilance) comes from hands-on review (Modern Creator Cinema Studio
tutorial), not from official Higgsfield documentation, and is adopted here as a
documented design decision. The "3 intensity levels" are likewise a skill
design choice, not a Higgsfield control — treat them as encoding levels, not
model-exposed numbers.

Where the official guide is updated, prefer the live page over this skill where
they conflict.

## Emotion bank

The core of the console. Six emotions, each externalized as **directly
visible or audible cues** at three intensity levels. Intensity is never encoded
with degree adjectives ("very sad", "extremely angry") — it is encoded purely
through graduated cues: number of cue channels engaged, amplitude, movement
degree, and vocal delivery.

| Emotion | Abstract one-liner | Intensity 1 (low) | Intensity 2 (medium) | Intensity 3 (high) | Seed Audio delivery hint |
|---|---|---|---|---|---|
| **Serenity** | A settled, unhurried inner calm with no internal conflict. | Gaze soft and level; breathing slow and even; corners of the mouth at rest. | Eyes half-lidded, brows relaxed; slow, deep breaths; hands loosely folded or open palms. | Shoulders fully dropped; a slow exhale with eyes briefly closed; a subtle, contented smile. | Calm, measured; slow, soft, unhurried. |
| **Joy** | Bright, open, expansive happiness that lifts the body and face. | The corner of the mouth lifts faintly; the eyes soften. | An uncontrollable smile; brows relax; steps become light. | Laughing, spinning in place, breathless; eyes crinkled. | Bright, warm; light and quickening, occasionally breaking into laughter. |
| **Terror** | Overwhelming dread that triggers the freeze response. Built from gaze fixed, brows lowered, tense stillness plus panic respiratory signs. | Gaze fixed; pupils widen; a visible swallow; breathing turns shallow. | Eyes widen fully; brows raised and rigid; chest heaves; hands freeze mid-motion. | Frozen stillness; mouth slightly open; body tensed; a choked, sharp intake of breath. | Thin, breathy; shaky, rapid, strained. |
| **Rage** | Hot, escalating anger pressing outward at a target. | Jawline tense; eyes sharp; nostrils flare slightly. | Both fists clenched; chest heaving; eyes sharp; jaw working. | Veins at the temple; trembling fists; shouts with the voice cracking; whole body coiled. | Shouted, voice cracking; harsh, escalating, clipped. |
| **Fear** | Anxious apprehension and watchfulness about a perceived danger. | Eyes darting; fingers tapping; weight shifting; frequent glancing. | Rapid breathing; eyes darting; biting the lip; hands fidgeting. | Body pulled back; shoulders hunched; gaze searching; voice cracking; quick shallow breaths. | Shaky, rapid; hesitant, tremulous, quickened. |
| **Vigilance** | Sharpened, controlled alertness scanning for threat or opportunity. Built from gaze fixed, brows lowered, tense stillness. | Gaze steady; brows level; posture still but ready. | Gaze fixed and scanning; brows lowered; body still; breathing held. | Utterly still; eyes narrow and unblinking; head slowly panning; hands ready at the sides. | Low, steady; measured, controlled, clipped. |

### Relationship to the official 5-emotion externalization table

`seedance-prompt-25` documents five emotions (Sadness, Joy, Nervousness /
anxiety, Anger, Relief) with canonical cue vocabulary:

| Console emotion | Official table entry | Overlap / build note |
|---|---|---|
| Joy | Joy | Direct: corners of the mouth rising, brows relaxing, light steps, humming, spinning. |
| Rage | Anger | Direct: fists clenched, jawline tense, chest heaving, eyes sharp, words through gritted teeth. |
| Fear | Nervousness / anxiety | Overlaps: eyes darting, rapid breathing, tapping, fidgeting. Fear leans further into withdrawal and flight. |
| Serenity | Relief | Overlaps: long exhale, shoulders relaxing. Serenity is a resting state; Relief is a release after tension. |
| Terror | (none) | Build from cue vocabulary: gaze fixed, brows lowered, tense stillness, plus widened pupils, choked breath, trembling. |
| Vigilance | (none) | Build from cue vocabulary: gaze fixed, brows lowered, tense stillness, plus narrow unblinking scanning, slow head pan, hands ready. |
| Sadness *(routed)* | Sadness | Direct: use the official cues verbatim — lowering the head, shoulders trembling slightly, eyes reddening, fingers unconsciously clutching clothing, tears welling but not falling. Sadness is not in the console six; route any "sad" request here and apply the same 3-level intensity encoding. |

**Terror vs Vigilance:** both borrow the "gaze fixed, brows lowered, tense
stillness" family. Differentiate them by body control — Terror is a panicked
freeze (pupils widen, choking breath, trembling), Vigilance is controlled
scanning (narrow unblinking eyes, slow head pan, hands ready, held breath).
State that difference explicitly in the prompt; do not write the bare emotion
word alone.

## Intensity encoding guide

Intensity level is a **design-level encoding choice**, not a number the model
reads. Levels 1/2/3 differ on the same emotion through three graduated levers:

1. **Number of cue channels engaged** — one or two channels at level 1 (face
   only), more channels at level 3 (face + hands + breathing + body + voice).
2. **Amplitude** — faint and contained (a flicker) vs pronounced (a shaking
   fist, tears streaming).
3. **Movement degree** — static containment (held breath, frozen stillness)
   vs full-body release (spinning, shouting, recoiling).
4. **Vocal delivery** — calm and measured, strained and quickened, or
   shouted / cracking.

Worked example — **Joy** at all three levels:

| Level | Encoding (cues, not adjectives) |
|---|---|
| 1 (low) | The corner of @character's mouth lifts faintly; the eyes soften. |
| 2 (medium) | An uncontrollable smile spreads; the brows relax; the steps become light. |
| 3 (high) | @character laughs, spins in place, breathless, eyes crinkled. |

The same structure applies to every emotion in the bank: level 1 stays in the
face, level 3 releases into the body and voice. Never write "very happy" or
"extremely terrified" — replace the adjective with more cues and more amplitude.

## Parameter schema

The console accepts a single directive object:

| Parameter | Type | Required | Meaning |
|---|---|---|---|
| `character` | string | yes | Character id / element id or named subject (e.g. `gloria` or `@gloria`). |
| `emotion` | string | yes | One of the six bank emotions: `serenity`, `joy`, `terror`, `rage`, `fear`, `vigilance`. |
| `intensity` | int | yes | 1 (low) / 2 (medium) / 3 (high), encoded per the intensity guide. |
| `arc` | list | no | Ordered list of emotion x intensity beats, each with a trigger and timestamp, for multi-stage performance. |
| `dialogue` | string | no | The EXACT spoken line(s), verbatim. If present, used identically in Seed Audio and Seedance prompts. |
| `delivery` | string | no | Optional delivery-style override (e.g. "through gritted teeth", "breathless"). Defaults to the bank's delivery hint for the emotion. |
| `reinforce_with_audio` | bool | no | If true, run the audio-first layer (Seed Audio dialogue → `reference_audio` → Seedance). Recommended whenever `dialogue` is set. |

`arc` beat shape: `{emotion, intensity, trigger, at_seconds}`. Example:
`[{joy,1,"she sees the letter",0}, {rage,2,"she reads the name",6}, {fear,3,"footsteps approach",11}]`.

## Prompt layer output grammar

### Single emotional transition (one emotion, one change)

Use for a single emotional shift over the shot. Keep **2-4 observable cues**
for the transition — cue overload destabilizes the performance.

```
The overall emotion shifts from <starting emotion> to <ending emotion>.
After <triggering event>, <character> first shows <immediate observable reaction>.
Then, <eyes, brows, mouth, breathing, gaze, or hand movement> gradually <changes>.
Finally, <character> expresses <target emotion> through <restrained or explicit outward behavior>.
```

### Multi-stage emotion (arc over time)

Use when the emotion changes several times, with trigger events and
timestamps.

```
When <character> hears or sees <first triggering event>, <first observable reaction>.
When <second triggering event> occurs, <change in expression, gaze, or breathing>.
After confirming <critical information>, the emotion that <character> tries to restrain
or conceal gradually becomes visible through <observable behavior>.
Finally, <character's final action, expression, or manner of speaking>.
```

### Dialogue, delivery, and language

When `dialogue` is set, place the exact line inside `{curly braces}` and give
the delivery style plus the dialogue language (non-Chinese dialogue needs the
language stated):

```
Dialogue language: <language>. <character> <says/shouts/whispers> in <delivery style>: {<exact line>}
```

### Worked prompt example

Directive: `character: gloria, emotion: rage, intensity: 2, dialogue: "Get out
of my way.", delivery: "through gritted teeth", reinforce_with_audio: true`.

```
@Image 1 defines @gloria's appearance, hairstyle, and clothing. Do not use the
background or other people in the image.

The overall emotion shifts from restrained calm to rising rage.
After the locked door does not open, @gloria first clenches both fists and her
jaw tightens.
Then her chest heaves, her eyes sharpen, and her breathing quickens.
Finally, @gloria expresses rage through explicit outward behavior, pushing
against the door.
Dialogue language: American English. @gloria says in a sharp, strained voice
through gritted teeth: {Get out of my way.}
```

For the full scene prompt, drop this acting block into the six-part formula
(Subject + Action + Scene + Visual Style + Camera + Audio) as the subject/action
section, per `seedance-prompt-25`.

## Audio-first layer (reinforcement)

The stronger acting lever. Run this whenever `reinforce_with_audio` is true or
`dialogue` is present. The audio drives the video — never the other way around.

```mermaid
flowchart TD
  A[directive: emotion x intensity x dialogue] --> B[Seed Audio prompt: voice profile from bank + exact dialogue]
  B --> C[generate dialogue track -> dlg_<scene>_sh<NNN>_<char>_t<NN>_v<NN>.wav]
  C --> D{duration <= video duration?}
  D -->|no| E[trim audio prompt - pauses, ambience tails; regenerate]
  E --> C
  D -->|yes| F[pass WAV as reference_audio, bind as @Audio 1]
  F --> G[Seedance task: same {dialogue} text, shot timestamps aligned to audio]
  G --> H[record audio path / SHA-256 / duration + dialogue-to-shot map in shot.md and scene.md]
```

### Step-by-step

1. **Compose the Seed Audio prompt.** Build a voice profile from the bank's
   delivery hint for the emotion plus the character's baseline: age, gender,
   accent, emotion, tone, speed, timbre. Keep the voice profile stable with
   the character's canonical `character.md`. Use T2A for a described voice, or
   TA2A with `<<TGT_SPK1>>` when a voice reference clip exists. Include the
   EXACT dialogue in double quotes. See `seed-audio-prompt`.
2. **Generate the dialogue track.** Save it to the shot folder as
   `dlg_<scene>_sh<NNN>_<character-id>_t<NN>_v<NN>.wav`, with its immutable
   prompt snapshot `prompt_dlg_<scene>_sh<NNN>_<character-id>_t<NN>_v<NN>.md`
   beside it.
3. **Verify `audio_duration <= video_duration`.** Seed Audio output must fit
   within the planned Seedance `duration` parameter. If it exceeds it, trim
   the audio prompt (shorter ambience tails, fewer pauses, tighter scene
   description) and regenerate. Never pad the video to fit an over-long audio.
4. **Pass the WAV as `reference_audio`.** Submit via
   `seedance_2_5_create_task` (2.5, up to 10 audio refs, 30s) or
   `seedance_create_task` (2.0, up to 3 audio refs, 15s). In the Seedance
   prompt, label it `@Audio 1` and bind it in every shot that contains
   dialogue: `@Audio 1 defines <character>'s voice and specified dialogue`.
5. **Keep the SAME `{dialogue}` text.** The exact lines in the Seed Audio
   `text_prompt` must appear verbatim inside `{curly braces}` in the Seedance
   prompt. No paraphrasing, no reordering, no omission. If one changes, both
   change.
6. **Align shot timestamps to actual audio.** After generating the audio,
   inspect it (or transcribe with `speech_to_text`) and set the `Shot N
   (start-end)` time ranges in the Seedance prompt so each line lands at the
   second it actually occurs.
7. **Record the alignment.** `scene.md` records the audio asset path, SHA-256,
   verified duration, and the dialogue-to-shot timestamp mapping; `shot.md`
   records the same audio asset as a reference input with `@Audio 1`. If the
   audio is regenerated, update both files and invalidate any video that used
   the old audio.

### Alignment contract (from AGENTS.md)

1. **Same dialogue text in both prompts** — Seed Audio `text_prompt` and the
   Seedance `{curly braces}` must match verbatim.
2. **Audio duration <= video duration** — trim the audio prompt if needed;
   never pad the video.
3. **Shot timestamps align to audio** — place each line at the second it
   actually occurs in the generated audio.
4. **Audio as `reference_audio`** — pass the `.wav`, label `@Audio 1`, and
   bind it in every dialogue/music shot.
5. **Single source of truth** — audio path, SHA-256, duration, and the
   dialogue-to-shot mapping live in `scene.md` and `shot.md`.

## Edge cases and guardrails

- **Intensity is not numerically controllable.** The model reads cues, not
  numbers. Validate each intensity level with a same-seed A/B before trusting
  it, and record the chosen level in `shot.md`.
- **2-4 cues per single transition.** More cues overload the performance and
  destabilize it. If more beats are needed, switch to the multi-stage template.
- **No degree adjectives.** "Very sad", "extremely angry", "super happy" are
  banned. Encode intensity via graduated cues (channel count, amplitude,
  movement degree, vocal delivery).
- **Dialogue must be verbatim across both prompts.** If the Seed Audio line or
  the Seedance `{line}` changes, change both. A mismatch causes lip-sync drift.
- **Audio longer than video: trim audio, never pad video.** Reduce pauses,
  ambience tails, and scene description in the Seed Audio prompt; regenerate.
- **Emotion arcs need the multi-stage template + timestamps.** A single
  transition template cannot carry several emotion changes.
- **`reference_audio` forces lip-sync, not acting fidelity.** It locks the
  voice and mouth timing to the audio emotion. Whether Seedance visibly acts
  the emotion needs an empirical A/B: same prompt, neutral voice vs angry
  voice.
- **`watermark: false` by default** for all image, video, and audio
  generation. Enable the AIGC watermark only when explicitly requested.
- **Cost.** Audio and video bill per generation. Prototype at the lowest
  suitable resolution and duration; confirm duration fits before submitting
  the video task.
- **Content safety.** Do not direct performances depicting identifiable real
  people without rights or otherwise restricted content.

## Self-check checklist

Before finalizing an acting block or plan, verify:

- [ ] The emotion is one of the six bank emotions, or is built explicitly from
      the cue vocabulary (gaze, brows, mouth, breathing, hands, body) when not
      in the bank.
- [ ] Every cue is directly observable or audible — no bare abstract emotion
      words standing alone.
- [ ] Intensity is encoded via graduated cues (channel count, amplitude,
      movement degree, vocal delivery), with zero degree adjectives.
- [ ] A single emotional transition uses 2-4 cues max; more beats use the
      multi-stage template.
- [ ] Every arc beat carries a trigger event and a timestamp.
- [ ] When `dialogue` is set, the line appears verbatim inside `{}` with a
      delivery style and dialogue language.
- [ ] When `reinforce_with_audio` is true, the plan includes: Seed Audio voice
      profile from the bank, a duration check (`audio_duration <= video_duration`),
      `reference_audio` with `@Audio 1` binding, and identical `{dialogue}` text.
- [ ] Shot timestamps are aligned to actual audio timing (post-audio inspection
      or transcription).
- [ ] `shot.md` records the audio asset path, SHA-256, verified duration, and
      the dialogue-to-shot mapping; `scene.md` carries the same single source
      of truth.
- [ ] `watermark: false` unless the user explicitly requested the AIGC
      watermark.
