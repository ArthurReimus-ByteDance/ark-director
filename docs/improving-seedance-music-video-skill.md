# Improving the Seedance Music Video Skill — Lessons from mv-bryce-vine

> Based on a full end-to-end production: character sheet → location references →
> audio trimming → ASR transcription → prompt engineering → 3 generation takes
> (t01 video-only, t02 native audio with dropped lyrics, t03 timestamped lyric
> timeline — approved). ~20 min prompting + ~39 min generation across 3 takes.

## Summary of what broke and what fixed it

| Take | Config | What happened | Root cause |
|---|---|---|---|
| t01 | `generate_audio: false` | Video-only output, clean lip-sync to reference | Worked as designed — required remux |
| t02 | `generate_audio: true`, two big `{}` blocks | **~⅓ of lyrics dropped** ("ever really took charge like a wiring fee" + "trying to manifest the things I aspire to be" missing entirely; "my dog needs a walk" reordered) | Native audio re-performs the track; large `{}` blocks give the model freedom to skip/reorder |
| t03 | `generate_audio: true`, **13-line timestamped lyric timeline** | ✅ All 13 lines present, in order, at correct timestamps | Each line bound to its own `[X-Ys] { line }` beat slot + explicit "no line may be skipped, shortened, or reordered" mandate |

---

## Proposed skill improvements

### 1. Add the "timestamped lyric timeline" technique as a first-class method

**Current state:** The skill mentions `【word】` for lyric videos and `{...}` for sung lines, but treats the lyric block as a single continuous text. It says "the exact sung lines must appear in {...}" without guidance on how to structure them for coverage.

**What we learned:** Grouping all lyrics into 1–2 large `{}` blocks lets the model skip, shorten, or reorder lines — especially in rap, where the delivery is fast and dense. Binding each line to its own timestamped slot forces complete coverage.

**Proposed addition to the skill:**

```text
### Timestamped lyric timeline (for performance videos with lip-sync)

When the performer must lip-sync the full verse and complete lyric coverage
is critical, do NOT group all lyrics into one or two large {…} blocks.
Instead, bind each lyric line to its own timestamped slot:

[2-4 seconds] { I used to pray before I went to bed, }
[5-7 seconds] { back when I was like eleven or ten. }
[7-8 seconds] { I don't remember the facts, }
...

Add an explicit mandate:
"The performer performs every line below in full, in order, at its
timestamp. No line may be skipped, shortened, mumbled, or reordered."

When to use this technique:
- Rap or fast-paced vocal delivery (high dropout risk)
- Any performance video where complete lyric coverage is a hard requirement
- When the audio reference has dense, continuous vocals with no long pauses

How to get the timestamps:
1. Run speech recognition (ASR) on the audio master
2. Extract word-level start/end times
3. Group words into lyric lines
4. Round each line's start/end to the nearest beat (or clean second)
5. Use those as the [X-Ys] { line } slots in the prompt

When NOT needed:
- Ballads with long pauses between lines
- Videos where the visual story matters more than lyric accuracy
- Native audio where the model has space to breathe
```

### 2. Add a "native audio re-performs, not copies" warning

**Current state:** The skill says "the generated file may not carry the master as a usable track, so re-mux the original master onto the approved video in assembly." This implies the audio might not be usable — but doesn't warn that the model will RE-PERFORM the track and may drop/reorder/garble lyrics.

**What we learned:** `generate_audio: true` with a reference audio does NOT copy the reference. The model generates a new audio performance inspired by the reference. This means:
- Lyrics can be dropped (we lost 2 of 13 lines in t02)
- Lyrics can be reordered ("my dog needs a walk" moved to the end)
- Words can be doubled or stuttered ("cause I need to lock it" repeated)
- The instruction "Retain @Audio 1 exactly as the soundtrack" does NOT force bit-for-bit fidelity

**Proposed addition:**

```text
### Native audio caveat: re-performance, not reproduction

When `generate_audio` is enabled with a reference audio, the model
RE-PERFORMS the track — it does not copy the reference bit-for-bit.
This means:

- Lyrics may be dropped, shortened, reordered, or garbled
- The music may differ in arrangement, tempo, or instrumentation
- The instruction "retain @Audio 1 exactly" nudges but does not guarantee fidelity

Risk factors for lyric dropout:
- Fast/dense vocal delivery (rap, fast pop)
- Long verses with no pauses
- Large {…} blocks (the model has freedom to skip within a block)

Mitigations:
1. Use the timestamped lyric timeline technique (see above) to force coverage
2. After generation, run ASR on the output audio to verify all lines are present
3. For distribution requiring the exact master, set generate_audio: false and
   re-mux the original audio onto the approved video in assembly
```

### 3. Add an ASR verification step to the workflow

**Current state:** The skill's workflow ends at "submit generation → review." There's no automated check for lyric coverage.

**What we learned:** Running ASR on the generated video's audio track was the key diagnostic — it immediately revealed which lyrics were dropped and at what timestamps. This is a cheap, fast verification that catches a failure mode visual review alone cannot.

**Proposed addition to the workflow:**

```text
### Post-generation lyric verification (for audio-first / native audio)

After generation, verify that the output audio contains all expected lyrics:

1. Extract the audio track from the generated video (ffmpeg -vn)
2. Run speech recognition (ASR) on the extracted audio
3. Compare the transcription against the expected lyrics
4. Flag any missing, reordered, or garbled lines
5. If lines are missing: use the timestamped lyric timeline technique
   and regenerate, OR re-mux the original master if exact fidelity is needed

This step is especially important for:
- Rap and fast vocal delivery
- Long verses (10+ lines)
- Native audio generation (re-performance risk)
```

### 4. Add a music-video section to the prompt-review checklist

**Current state:** The `prompt-review` skill's `review-checklists.md` has sections for Seedance 2.5, Seedance 2.0, Seedance VFX, Seed Audio, and Seedream — but no dedicated music-video checklist. The `seedance-music-video` skill has a 10-point self-check, but it's not integrated into the review pipeline.

**Proposed addition to `review-checklists.md`:**

```text
## Seedance music video

Source skill: `seedance-music-video`

### Format and genre
1. **Format declared.** Performance, narrative, conceptual, lyric, visualizer,
   or hybrid — with address mode (direct/indirect/none).
2. **Genre lock is a single recipe.** Not a mixture of two genres.

### Song map
3. **One event per section.** Each song section has one primary visual
   assignment and a visible end state.
4. **Chorus repeats escalate.** Second chorus has rising visual energy.
5. **Bridge departs.** New angle, location, wardrobe, or image.

### Audio contract
6. **Audio treatment explicit.** Native brackets OR @Audio N timing authority —
   never ambiguous.
7. **Lip-sync lines verbatim in {…}.** Match the audio master exactly.
8. **Timestamped lyric timeline used when coverage is critical.** Each line
   bound to its own [X-Ys] slot with a "no line skipped" mandate.
9. **Native audio caveat acknowledged.** If generate_audio is true, the prompt
   accounts for re-performance risk.

### Beat contract
10. **Audio events named.** Which beats trigger cuts and camera moves.
11. **Cut density matches section energy.** Low for verses, high for chorus.

### Structure
12. **Right-sized (4–30s).** One section per pass, or explicit continuous take.
13. **Style seal present.** Compact closing sentence with genre, palette, motion,
    beat contract, and tone.
```

### 5. Document the ASR-to-timestamp workflow as a concrete technique

**Current state:** The skill says "map each song section to a visual assignment" but doesn't explain HOW to get precise lyric timing from an audio file.

**What we learned:** The most valuable technique was:
1. Run ASR on the audio master (speech_to_text tool)
2. Get word-level timestamps
3. Group words into lyric lines
4. Round to beat slots
5. Use as `[X-Ys] { line }` blocks

This should be a documented, step-by-step procedure in the skill.

### 6. Clarify the "hybrid audio mode" (reference audio + native generation)

**Current state:** The skill presents native audio and audio-first as "mutually exclusive" patterns. In practice, the user wanted BOTH: pass the reference audio for timing/lip-sync AND generate native audio.

**What we learned:** This hybrid mode works — you pass `reference_audio` AND set `generate_audio: true`. The reference drives timing and lip-sync; the native audio follows it (imperfectly). The skill should document this as a valid third mode with its tradeoffs.

```text
### Hybrid audio mode (reference + native generation)

When you need both lip-sync to a specific track AND a native audio output:

1. Pass the audio master as reference_audio (@Audio 1)
2. Set generate_audio: true
3. The model uses the reference for timing and lip-sync
4. The model generates a native audio track that follows (but does not copy) the reference

Tradeoffs:
- Lip-sync timing is good (driven by the reference)
- Audio fidelity is approximate (re-performed, not copied)
- Lyric coverage may drop (use timestamped lyric timeline to mitigate)
- For exact audio fidelity, use generate_audio: false and re-mux the master
```

### 7. Add "rap" as a specific vocal delivery mode with its own risks

**Current state:** The skill treats all lip-sync the same. Rap is fundamentally different from singing — it's faster, denser, and the model has more room to drop words without obvious gaps.

**Proposed addition:**

```text
### Rap and fast vocal delivery

Rap is the highest-risk vocal mode for lyric dropout:
- Dense, continuous delivery with few pauses
- The model can skip bars without creating obvious silence
- ASR verification is essential after generation

Specific guidance:
- ALWAYS use the timestamped lyric timeline for rap (not large {…} blocks)
- Set the "no line may be skipped, shortened, mumbled, or reordered" mandate
- Run ASR on the output to verify coverage
- Consider splitting very long verses (>15 lines) into multiple clips
```

---

## Summary table

| Improvement | Priority | Effort |
|---|---|---|
| Timestamped lyric timeline technique | **High** — the core breakthrough | Low (add to skill) |
| Native audio re-performance warning | **High** — prevents wasted generations | Low (add caveat) |
| ASR verification step | **High** — catches the failure mode | Low (add to workflow) |
| Music-video review checklist | Medium — quality gate integration | Low (add to review-checklists.md) |
| ASR-to-timestamp procedure | Medium — makes the technique reproducible | Low (add step-by-step) |
| Hybrid audio mode documentation | Medium — clarifies a common use case | Low (add a section) |
| Rap-specific delivery guidance | Medium — highest-risk vocal mode | Low (add subsection) |

All improvements are documentation-level changes to the `seedance-music-video`
skill and `prompt-review/references/review-checklists.md` — no code changes
needed.
