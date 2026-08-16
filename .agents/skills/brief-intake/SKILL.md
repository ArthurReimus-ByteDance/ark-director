---
name: brief-intake
description: >
  Run the two-mode brief intake that proposes genre-appropriate defaults for
  every directorial axis (structure, acting, camera, lens, lighting, grade,
  pacing, staging, medium, audio) and confirms them with the user. Fast mode
  (default) accepts the proposed set, surfacing only high-risk choices; full
  Q&A mode walks every axis for confirmation. Invoke from film-production at
  the brief/development stage, or when the user starts a new project and wants
  recommended defaults. Never generates media.
---

# Brief Intake

Run the two-mode brief intake: analyze the brief, propose genre-appropriate
defaults per directorial axis, and confirm them with the user before any
generation. The intake **suggests defaults** — it does not ask the user to
specify every knob. The user confirms or adjusts, and the confirmed set is
persisted as locked decisions.

## When to use

- At the brief/development stage of a new project (via `film-production`).
- When the user starts a project and wants recommended defaults.
- When a project's brief is being revised and directorial defaults need
  re-confirmation.

Do not use this skill to generate media. It is prompt-composition and
question-asking only.

## Two modes

| Mode | When | Behavior |
|---|---|---|
| **Fast (default)** | Any new project unless the user asks for full Q&A | Propose the full default set silently; present only the high-risk choices for confirmation; accept the rest as locked |
| **Full Q&A** | User says "full Q&A", "walk me through it", "ask me everything", or opts in | Present every axis with proposed default + rationale + confirm/adjust prompt |

Full Q&A mode is opt-in — trigger only on an explicit user request. Otherwise
fast mode.

## Step 1 — Read the brief

Collect or read from the existing brief / `project.md`:

| Field | Example | Used for |
|---|---|---|
| Genre / category | noir music video, horror short, food commercial | Genre default table |
| Audience | pop listeners, families, B2B | Tone and pacing calibration |
| Runtime | 30s, 60–120s, full short film | Scene and pacing right-sizing |
| Tone | tense, stylish, warm, comedic | Lighting/grade/acting defaults |
| Story objective | emotional hook, product trigger, scare beat | Structure and acting defaults |
| Format / ratio | 16:9, 9:16, 1:1 | Pass-through to project config |
| Budget posture | low-cost prototype vs final render | Resolution / take count |

If the genre is unclear, ask one clarifying question to classify it before
proposing defaults. If the brief is entirely absent, ask for at minimum: genre,
runtime, and tone.

## Step 2 — Derive genre-appropriate defaults

Map the brief to the genre table below. For each axis, produce a default value
**and a one-line rationale** tied to the brief's tone and genre. Unknown genres
fall back to the neutral cinematic set.

### Axis table (10 axes, mapped to owning preset skills)

| # | Axis | Owning skill | Default derivation |
|---|---|---|---|
| 1 | Structure | `tig-scene-engine` | Present only when developing story/narrative, not one-off shots |
| 2 | Acting | `seedance-acting-console` | Always present an acting default. With dialogue, direct it; without dialogue, the genre acting row still supplies a mood-level default (e.g. Fear/Vigilance for noir) — never "none" unless the user wants a neutral, undirected performance |
| 3 | Camera | `seedance-camera-presets` | Genre move + default shot size/angle |
| 4 | Lens | `seedance-lens-presets` | Focal length/aperture paired with visible result |
| 5 | Lighting | `seedance-lighting-presets` | Motivated source, key direction, softness |
| 6 | Grade | `color-grade-palettes` | One project-wide palette; propose genre palette |
| 7 | Pacing | `seedance-pacing-presets` | One ramp + one pacing; propose genre rhythm |
| 8 | Staging | `tig-blocking-map` | Present only when multi-character spatial precision matters |
| 9 | Medium | `seedance-animation-styles` | Live-action default; present only if stylized animation |
| 10 | Audio | `seed-audio-prompt` / `seed-audio-commercial` | Always present. Native audio default; lip-sync only if user requests |

### Genre default table (v1)

Unknown genres fall back to the neutral cinematic row.

| Genre | Camera | Lens | Lighting | Grade | Pacing | Acting |
|---|---|---|---|---|---|---|
| Noir / neon | Handheld + slow push-in, ≤2 moves | 35mm f/1.8, shallow DOF | Cool neon key screen-left, warm rim | Teal-orange or B&W | Ramp Up into beats | Fear/Vigilance I2, motive-driven |
| Pop music video | Kinetic, tracking/handheld | Wide 24mm, high-key | Colorful high-key, motivated | Vibrant, one palette | Beat-driven, Impact on chorus | Joy/Rage I2-I3, performance-as-escape |
| Horror | Slow push-ins, handheld | Wide 28mm, deep-ish | Low-key green/moonlight | Desaturated, muted | Slow menacing, Flash In scares | Terror I3, freeze responses |
| Comedy | Static or light handheld | 24mm bright | Bright soft fill | Warm, natural | Snappy, Calm-to-Dynamic | Comedic timing, reactive |
| Documentary | Observational handheld | 24mm natural | Natural available light | Natural, neutral | Natural/auto | Authentic, non-actor |
| Luxury/commercial | Slow dolly + static | 50mm f/2, controlled | Soft key + product fill | High-contrast premium | Slow, controlled | Serenity I1-I2, poised |
| (unknown) | Medium shot, subtle push-in | 35mm neutral | Motivated soft key | Neutral project palette | Auto/natural | Neutral |

For axes not in the table (staging, medium, structure, audio), apply the rules
in the axis table: staging only for multi-character precision, medium only for
stylized animation, structure only for narrative development, audio native
unless lip-sync is requested.

## Step 3 — Run the confirmation loop

### Fast mode (default)

Present the full proposed set silently, then surface only the **high-risk
choices** for confirmation:

1. **Audio mode** — native vs lip-synced (`reference_audio` pipeline + cost)
2. **Acting direction** — whether dialogue/mood needs directed performance
3. **Grade palette** — project-wide choice that all later prompts must match
4. **Medium** — stylized animation vs live-action (changes everything downstream)

Output shape — compact full-set line first, then the high-risk confirmations:

```
Proposed defaults (fast mode):
  Camera: handheld+slow push-in · Lens: 35mm f/1.8 · Lighting: cool neon key
  Grade: teal-orange · Pacing: ramp-up · Acting: Fear/Vigilance I2
  Audio: native · Medium: live-action
High-risk confirmations:
  - Grade palette [teal-orange]: ✓ / change to ___
  - Audio [native]: ✓ / lip-sync
  - Acting [Fear/Vigilance I2]: ✓ / direct ___
  - Medium [live-action]: ✓ / stylized ___
Confirm all → locked.
```

If the user confirms all (e.g. "✓ all" or "fine"), record the entire proposed
set as locked and stop. If they adjust any high-risk choice, update that axis
and continue.

If the genre is ambiguous, apply the hybrid-genre resolution rule (see Edge
cases).

### Full Q&A mode (opt-in)

Present every axis in the axis-table order, one at a time, each with the
proposed default, a one-line rationale, and a confirm/adjust prompt:

```
<Axis> — proposed default: <value>
  Why: <rationale tied to the brief>
  ✓ accept / adjust: <value>
```

Omit only axes that do not apply (per the axis-table rules): structure when
there is no narrative development, staging when spatial precision is not
needed, medium when live-action. Always present camera, lens, lighting, grade,
pacing, acting, and audio.

## Step 4 — Persist confirmed decisions

Write the confirmed set into `project.md` frontmatter under a `locked` block:

```yaml
locked:
  audio_mode: native            # native | lip-sync
  grade_palette: teal-orange
  acting_direction: directed    # directed | none (none only when the user opts into a neutral, undirected performance)
  medium: live-action           # live-action | stylized
  camera: handheld-slow-pushin
  lens: 35mm-f1.8-shallow
  lighting: cool-neon-key
  pacing: ramp-up
  staging: none                 # none | blocking-map
  structure: none               # none | scene-engine
```

- Record which axes were **confirmed by the user** vs **accepted by default**
  (e.g. a `confirmed: [grade_palette, audio_mode]` list alongside `locked`).
- For multi-scene projects, scene-level overrides may add a per-scene `locked`
  block in `scene.md`; a later full-Q&A pass revisits only confirmed decisions.

## Edge cases

- **Unknown genre** — fall back to the neutral cinematic set and note the
  assumption to the user.
- **Hybrid genre** (matches multiple rows, e.g. "noir-style pop MV") — resolve
  by priority: the brief's explicit tone statement wins over genre conventions;
  if no tone statement exists, the first-listed matching genre row wins. Name
  the resolution explicitly and flag it for confirmation.
- **Conflicting brief signals** (e.g. "noir" + "bright and cheerful") — resolve
  toward the dominant tone, state the resolution, and flag the conflict for
  confirmation.
- **User wants to change one axis only** — update that axis and keep the rest
  of the proposal locked.
- **Multi-scene project** — propose a project-wide default set, then let the
  user override per scene; record both levels in `locked`.

## Self-check checklist

Before finalizing the intake, verify:

- [ ] The brief was read and its genre/runtime/tone extracted.
- [ ] Every applicable axis has a proposed default with a one-line rationale.
- [ ] Fast mode presented the compact full-set line and surfaced the four
      high-risk choices (audio, acting, grade, medium) for confirmation.
- [ ] Full Q&A mode presented every applicable axis with a confirm/adjust
      prompt, including acting and audio.
- [ ] Inapplicable axes were omitted, not presented empty.
- [ ] The confirmed set was persisted as a `locked` block in `project.md`.
- [ ] Confirmed-vs-default acceptance was recorded.
