---
name: seedance-music-video
description: >
  Write production-grade Seedance 2.5 music-video prompts: pick a video format
  (performance, narrative, conceptual, lyric, music visualizer, hybrid), map the
  song's sections to a visual plan, direct beat-synced cuts and camera, drive
  native audio or an audio-first lip-sync pipeline, and lock a per-genre visual
  style. Use whenever the user asks for a music video, a lyric video, a music or
  audio-reactive visualizer, a K-pop or idol video, a band/performer/performance
  clip, a song-driven scene, or a prompt whose timing and energy must follow the
  music rather than a spoken story. For an isolated speed ramp, cut rhythm, or
  montage pacing that is not tied to a whole song, use seedance-pacing-presets
  instead. Compose with seedance-prompt-25 for the full six-part grammar and
  with seed-audio-prompt when an original music master or lip-synced vocal track
  is needed first.
---

# Seedance Music Video

Write ready-to-use Seedance 2.5 prompts for music videos. The music is the
fixed brief: every visual decision is planned backward from the track's
sections, beats, and energy. Make the format, the song map, the beat contract,
and the genre lock visible in the prompt, not just the scene content.

## Source basis

- Official Seedance 2.5 prompt guide, launch blog, and ModelArk docs — audio
  bracket syntax, `@Audio N` timing-authority contract, the one-take singer
  example, timestamp grammar, and limitations. See `seedance-prompt-25`.
- Music-video craft and beat-sync practice — format taxonomy, song-section
  energy mapping, and section-relative cut density (sources below).
- Genre conventions — per-genre visual recipes, vertical-vs-landscape norms.

Key third-party sources (accessed 2026-08-20): Magnific
[Seedance 2.5 animation guide](https://www.magnific.com/blog/seedance-2-5-animation-prompts/),
[AI music-video production workflows](https://www.creativeainews.com/articles/how-to-make-ai-music-video-2026/),
[Beat-synced 30s edits](https://aitoolsguidebook.com/en/articles/ai-music-video-tutorial/),
and [music-video section-arc planning](https://blog.celtx.com/how-to-write-a-music-video-script/).
The recipes generalize these principles rather than copying published prompts.

## Format & genre bank

Read `references/music-video-recipes.md` after identifying the user's format
and genre. Use one genre recipe plus the matching format rule; do not paste the
whole bank into a prompt.

Formats: `performance`, `narrative`, `conceptual`, `lyric`, `visualizer`, `hybrid`.
(Here and throughout, `visualizer` means a music / audio-reactive visualizer,
not a data or code visualizer.)
Genres: `hip-hop-trap`, `edm`, `pop`, `indie-dream-pop`, `rock`, `rnb-soul`,
`country`, `classical-acoustic`, `abstract-visualizer`, plus a custom template.

## Core principle

The song is the brief. The music drives the video, not the other way around.
Do not write a story first and then smear a song over it — map each song
section to a visual assignment, and let the track's energy, tempo, and vocal
set the pacing, framing, and cut density.

For every prompt, define:

```text
format                 which video type this is (and its direct/indirect address)
song map               each section → visual assignment, energy, and end state
performance ratio      how much screen time is performer vs atmosphere per section
beat contract          which audio events the cuts and camera land on
audio treatment        native audio, or audio-first master used as timing authority
genre lock             one recipe controlling palette, lighting, camera, and rhythm
exclusions             only contradictions that would break the format or genre
```

## Prompting workflow

### 1. Resolve the format

Map the user's request to one format. The format decides the address mode,
which shots matter, and where the performer sits in the frame:

- **Performance** — the artist lip-syncs to camera (direct address); energy and
  mouth-to-vocal sync carry it. Close-ups, medium shots, full-body dance.
- **Narrative** — a short film; the song is the score (indirect address);
  characters never address the camera. Lyric relation can be literal
  (illustration), emotional (amplification), or deliberately detached
  (disjuncture).
- **Conceptual** — no plot; one governing visual rule, image, or metaphor that
  encodes the track, executed with mechanical rigor.
- **Lyric** — the lyrics are the primary visual; word-level sync to the vocal.
  The model renders provisional captions; exact text is set in post.
- **Visualizer** — abstract, audio-reactive imagery with no performer and no
  lyrics; the visuals "image the sound" (waveforms, particles, geometry).
- **Hybrid** — the most common commercial structure: performance carries the
  choruses, narrative or concept carries the verses.

Default to `hybrid` when the user does not specify. A ballad usually wants
narrative or conceptual; a high-energy single wants performance or a hard
hybrid.

### 2. Map the song to a visual plan

Plan section by section, backward from the track. Give each section one
primary visual assignment and a visible end state. Use the standard energy arc
and scale it to the actual section lengths and BPM:

| Section | Energy | Visual assignment | Cut density (relative) |
|---|---|---|---|
| Intro | low | establish the visual world, wider shots | lowest |
| Verse | low–medium | situation, character, longer takes | low |
| Pre-chorus | building | cut frequency rises, shot length compresses | rising |
| Chorus / hook | peak | hero shots, close-ups, fastest cuts; **repeats escalate** | highest |
| Bridge | departure | new angle, location, wardrobe, or image not yet shown | pullback |
| Drop / instrumental | peak | highest cut density or one deliberately held shot | peak |
| Outro | resolve | callback, wide, slow | lowest |

Repeat the same hook in each chorus with rising visual energy — a second chorus
that does not escalate reads flat. Use the bridge for the creative risk.

### 3. Set the audio contract

Choose one of two audio modes; state it explicitly.

**Native audio (default).** Seedance co-generates audio and video in one pass.
Use the bracket syntax in the Audio slot and inside `{...}` for sung or spoken
lines. Choose exactly one of these patterns — they are mutually exclusive, do
not combine them:

```
(Soft, rhythmic piano music plays in the background)
{the exact sung line}
<the kick hits on each downbeat>
```

```
No background music. Keep only the singer's voice and the room ambience.
```

```
No audio at all.
```

When the clip must sit under an existing master in post, add a direct control
line so the model does not invent music (the generated file may carry no usable
track — re-mux the master in assembly).

**Audio-first (only when the user requests lip-synced vocals).** Generate the
original music and vocal track with Seed Audio first, verify
`audio_duration ≤ video_duration`, then pass it as a reference and bind it as
the timing authority:

```
@Audio 1 is the exact soundtrack and timing authority. Preserve its music,
vocals, and pauses; do not add dialogue, narration, music, subtitles, or
captions.
Follow the spoken and musical beats in @Audio 1.
Match <performer>'s visible mouth only to <performer>'s voice in @Audio 1.
```

The exact sung lines must appear in the Seed Audio prompt and in the Seedance
prompt inside `{...}` — no paraphrasing, no reordering. If one changes, both
change. `@Audio N` conditions the timing and lip-sync; the generated file may
not carry the master as a usable track, so re-mux the original master onto the
approved video in assembly.

### 4. Set the beat and cut-density contract

The beat grid gives the timing; emotion and story decide what lands on it.
Timestamps are a **time budget, not frame-accurate** — direct the beats in the
prompt, then snap the final cut to the audio master in post.

In-prompt, name each audio event, the visual event it triggers, and their
relationship (simultaneous, leads, or trails):

```
Each direction change lands on a downbeat.
At 5 seconds the camera crash-zooms on the kick.
The chorus cuts land on the beat; the final pose holds on the last hit.
```

Post-sync rules to carry into assembly: cut on the downbeat (beat 1 of each
bar), not "by feel"; cut ~1–2 frames early because eyes are faster than ears;
prefer whole-bar shot lengths (1, 2, or 4 bars) — half-bar cuts are fine in
fast sections but less forgiving; match cut density to section energy; trim a
slightly-too-long clip so its head lands on a downbeat marker instead of
generating an exact arbitrary length. Sung one-take lip-sync drifts more than
spoken dialogue — budget extra margin and re-check the mouth in review.

### 5. Right-size the scenes

Generate per section at its natural duration (4–30s), not per 30-second block.
One song section, one primary event, one visible end state per generation.
Chain approved sections via `return_last_frame` / `first_frame` with a shared
reference bundle and assemble in post. Reserve a 30s single-pass or native
extension for a genuine continuous take (one unbroken performance) where
seamless motion across section boundaries matters more than per-scene iteration.

When the user asks for a lyric video, keep the imagery simple and legible so
the text stays readable; direct word-level pops on the beat via `【word】`, and
keep the type treatment provisional — the exact lyrics and kinetic timing are
set in post.

### 6. Direct the performer

For lip-sync, give the exact line and a delivery cue, and specify the camera
angle to the mouth:

```
The singer looks into the lens and performs in energetic American English,
jaw opening fully on vowels: {I am still the one you know}
```

For acting, use observable cues, not mood words alone — see
`seedance-acting-console`. For a one-take performance, state
`one continuous unbroken shot, no cuts` and list the spaces and events the
camera passes through in order.

### 7. Compose with the six-part formula

Assemble the treatment into the `seedance-prompt-25` formula:

> **Subject + Action or Event + Scene and Environment + Visual Style + Camera Movement/Cut + Audio**

Chain the Visual Style slot as lighting → lens → grade → look. Keep the genre
lock in the Visual Style slot, the beat contract in the Camera/Cut and Audio
slots, and the sung lines in `{...}`. Do not describe the same action twice.

### 8. End with a style seal

Close with one compact sentence that reinforces the genre lock, the palette,
the motion cadence, the beat contract, and the tone. The seal prevents the look
from drifting across the section chain and during later shots.

## Partner-skill routing

This skill owns the music-video layer: format, song map, beat contract, audio
contract, and genre lock. Route every other axis to its owning skill instead of
duplicating it, and never let two skills fight:

| Concern | Route to |
|---|---|
| Full six-part grammar, reference roles, staging, timestamp rules, audio syntax | `seedance-prompt-25` |
| Speed ramps, montage cut rhythm, beat-snapped pacing blocks | `seedance-pacing-presets` |
| Named camera moves, ≤2 moves per clip | `seedance-camera-presets` |
| Acting, emotional cues, lip-sync delivery | `seedance-acting-console` |
| Original music / vocal master, audio-first track | `seed-audio-prompt`, `seed-audio-commercial` |
| Animation medium inside the MV (clay, felt, cel…) | `seedance-animation-styles` |
| Named grade palette / lighting setup | `color-grade-palettes`, `seedance-lighting-presets` |
| Storyboard, full multi-scene production | `seedream-storyboard`, `film-production` |

**Guardrail:** the genre lock is the sole palette, lighting, and camera source
**unless the user names a specific axis** — then load that axis's preset skill
and keep exactly one grade, one dominant lighting direction, and at most two
camera moves per clip. Do not stack a second grade or camera treatment on top
of a genre recipe.

## Output formats

### Music-video block

Use when the user only wants the directing layer:

```text
[Music-Video Format]
<Format name, direct or indirect address, and performance-to-atmosphere ratio.>

[Song Map]
Section 1 (<time range>): <visual assignment, energy, end state>.
Section 2 (<time range>): <visual assignment, energy, end state>.
Final Section (<time range>): <closing assignment and final visible state>.

[Beat & Cut Contract]
<Which audio events the cuts and camera land on; cut density per section.>

[Audio Treatment]
<Native audio brackets, or the @Audio N timing-authority binding for audio-first.>

[Genre Lock]
<Palette, lighting, camera grammar, motion cadence, and tone.>

[Style Seal]
<Compact closing sentence and relevant exclusions.>
```

### Full Seedance prompt

Use when the user asks for a complete prompt:

```text
[Audio First] (only when lip-synced vocals are requested)
@Audio 1 is the exact soundtrack and timing authority. Preserve its music,
vocals, and pauses; do not add dialogue, narration, music, subtitles, or
captions. Match <performer>'s visible mouth only to <performer>'s voice in
@Audio 1.

[Reference Roles] (only when references exist)
@Image 1 defines <performer>'s <appearance, wardrobe, or identity>.
@Image 2 defines <scene or venue>. Do not use <unwanted content>.

<Subject performs the primary action in <scene>.>
The visuals feature <genre lock: palette, lighting, lens, grade, look>.
Use <shot sizes, camera moves, and cuts>, with <beat contract>.
Audio includes <(music)> <{sung lines}> <sound effects>.

[Shot Plan] or [Stage Plan]
Shot 1 (<time range>): <one event and visible end state>.
Shot 2 (<time range>): <one event and visible end state>.
Final Shot (<time range>): <closing event and final visible state>.

[Maintain Consistency]
Keep <performer identity, wardrobe, venue, camera grammar, and audio>
consistent across the section chain.

[Style Seal]
<Compact genre, palette, motion cadence, beat contract, and tone.>
```

Return the prompt directly. Do not add production workflow, tool selection,
asset management, approval gates, or generation instructions unless the user
explicitly asks for them.

## Format-specific rules

- **Performance**: keep the performer on screen and the mouth in frame for
  lip-sync; vary shot size between close-ups (intimacy) and full-body (dance);
  a direct-address close-up reads as intimacy, a 3/4 angle as outward
  performance.
- **Narrative**: indirect address — characters never acknowledge the camera;
  keep the song as score and let the lyric relation be a deliberate choice
  (literal, amplified, or disjunct).
- **Conceptual**: choose one governing visual rule that encodes the track, then
  execute it with mechanical rigor; do not add a plot unless the rule needs it.
- **Lyric**: keep imagery simple and legible; the type is the star. Use `【 】`
  for provisional captions and set exact lyrics in post. Direct word-level
  pops on the beat (`【word】` on each accent), hold every word long enough to
  read, keep to one or two fonts, and dim the background so the text stays
  readable — kinetic type is faster and tighter in the chorus, looser in the
  verses.
- **Visualizer**: no performer, no story, no lyrics; audio-reactive shapes,
  waveforms, particles, or geometry that shift with the sections.
- **Hybrid**: state which sections carry performance and which carry the
  narrative/concept; do not let either strand crowd the other.

### Vertical vs landscape

- **9:16 (vertical)** is the discovery default for TikTok / Reels / Shorts:
  center the subject, prefer close and medium shots, plan fast cuts (roughly
  1–3s), open with the hook, and use vertical motion (reveals, tilts, drops)
  over horizontal pans. Native 9:16 composition beats cropping 16:9.
- **16:9 (landscape)** is the YouTube master: allow richer backgrounds,
  multi-subject staging, and continuity. Render one purpose-built 9:16 cut
  rather than stretching a 16:9 master.
- State the aspect ratio as a generation parameter, never inside the prompt.

## Rights and safety

- Use **original music only**. Never reproduce a real artist's copyrighted song
  in a prompt or as a reference; never write artist-name or copycat prompts.
- Voice-cloning a real, named artist's voice requires written consent from the
  artist or estate.
- Keep `watermark: false` by default; enable the AIGC watermark only when the
  user explicitly requests it.
- Generate the music master with Seed Audio (or another original source) so the
  release stays distribution-clean.

## Custom-format procedure

For an unlisted format or genre:

1. Identify the format's address mode (direct, indirect, or none).
2. Define the song map: which sections carry what visual energy.
3. Choose the audio treatment (native vs audio-first) and the beat contract.
4. Name the genre lock: palette, lighting, camera grammar, and motion cadence.
5. Define the performance-to-atmosphere ratio per section.
6. Write a format-first opening and a compact style seal.
7. Add only exclusions that prevent likely drift or genre leakage.

## Exclusion rules

- Do not use a blanket "no music" — it contradicts the point of a music video;
  use it only inside a specific ambient scene that must stay silent.
- Do not use exclusions as a substitute for positive audio and beat direction.
- Exclude only likely contradictions: a real artist's face or voice, readable
  logos, an unwanted second vocal, or a second genre's palette leaking in.
- Avoid direct imitation of living artists or directors; describe observable
  craft traits (one governing visual rule, structural bookends, contained
  staging).
- Keep genre recipes stereotype-safe: default to positive, progressive
  performer framing; do not reproduce objectifying legacy tropes.

## Self-check

Before returning the prompt, verify:

1. The format is named and its address mode is respected.
2. The song map assigns one primary event and a visible end state per section.
3. The beat contract names the audio events and their visual relationship.
4. Chorus repeats are set to escalate, and the bridge departs tonally.
5. The audio treatment is explicit: native brackets or `@Audio N` timing
   authority, never ambiguous.
6. Lip-sync lines appear verbatim in `{...}` and match the audio-first master.
7. Each generation is right-sized (4–30s) with one section per pass, or is an
   explicit continuous one-take.
8. The genre lock is a single recipe, not a mixture.
9. The style seal is compact and does not contradict the format or genre.
10. The response contains the prompt, not an unrelated production workflow.
