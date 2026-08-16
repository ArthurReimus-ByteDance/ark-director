# PLAN Brief-Intake Flow: Genre-Aware Defaults via Q&A

> Two-mode brief intake that suggests genre-appropriate defaults per directorial
> axis and confirms them with the user. Fast mode is the default; full Q&A mode
> is opt-in. Recommended defaults are derived from the brief, not user-specified.

## Problem

`film-production`'s brief stage collects only high-level fields (audience,
format, runtime, tone, budget). The directorial axes — camera, lens, lighting,
grade, pacing, acting, staging, medium, audio — are decided ad-hoc inside each
prompt, so the agent neither proposes nor confirms them. The user wants the
agent to **suggest the best defaults per axis** via a Q&A loop, with a fast mode
that accepts the proposal with minimal friction.

## Decision

Add a `brief-intake` step to `film-production` (implemented as its own skill,
`brief-intake`, so it stays modular and testable). The intake:

1. Reads the brief (genre, audience, runtime, tone, story).
2. Derives a genre-aware default for every directorial axis, each with a
   one-line rationale.
3. Runs either **fast mode** (default) or **full Q&A mode** (opt-in) to confirm.
4. Persists confirmed choices as locked decisions in `project.md` / `scene.md`.

## Skill structure: `.agents/skills/brief-intake/SKILL.md`

### Frontmatter

```yaml
name: brief-intake
description: >
  Run the two-mode brief intake that proposes genre-appropriate defaults for
  every directorial axis (structure, acting, camera, lens, lighting, grade,
  pacing, staging, medium, audio) and confirms them with the user. Fast mode
  (default) accepts the proposed set, surfacing only high-risk choices; full
  Q&A mode walks every axis for confirmation. Invoke from film-production at
  the brief/development stage, or when the user starts a new project and wants
  recommended defaults. Never generates media.
```

### Two modes

| Mode | When | Behavior |
|---|---|---|
| **Fast (default)** | Any new project unless user asks for full Q&A | Propose the full default set silently; present only the high-risk choices for confirmation; accept the rest as locked |
| **Full Q&A** | User says "full Q&A", "walk me through it", "ask me everything", or opts in | Present every axis with proposed default + rationale + confirm/adjust prompt |

Trigger for full Q&A mode: explicit user request. Otherwise fast mode.

### Axis table (10 axes, mapped to owning preset skills)

| # | Axis | Skill that owns the knob | Default derivation |
|---|---|---|---|
| 1 | Structure | `tig-scene-engine` | Present only when the user is developing story/narrative, not one-off shots |
| 2 | Acting | `seedance-acting-console` | Present when dialogue or a mood ask exists; otherwise neutral (no over-direction) |

> **Implementation note (deviation):** the implemented skill always presents an
> acting default — with dialogue, direct it; without dialogue, the genre acting
> row supplies a mood-level default (e.g. Fear/Vigilance for noir). "Neutral /
> none" is only legal when the user explicitly opts into an undirected
> performance. This is a stricter, more consistent rule than the plan's
> "otherwise neutral".
| 3 | Camera | `seedance-camera-presets` | Genre move + default shot size/angle |
| 4 | Lens | `seedance-lens-presets` | Focal length/aperture paired with visible result |
| 5 | Lighting | `seedance-lighting-presets` | Motivated source, key direction, softness |
| 6 | Grade | `color-grade-palettes` | One project-wide palette; propose genre palette |
| 7 | Pacing | `seedance-pacing-presets` | One ramp + one pacing; propose genre rhythm |
| 8 | Staging | `tig-blocking-map` | Present only when multi-character spatial precision matters |
| 9 | Medium | `seedance-animation-styles` | Live-action default; present only if stylized animation |
| 10 | Audio | `seed-audio-prompt` / `seed-audio-commercial` | Native audio default; lip-sync only if user requests |

### High-risk choices surfaced even in fast mode

These materially change cost, identity, or pipeline, so fast mode still asks:

1. **Audio mode** — native vs lip-synced (`reference_audio` pipeline + cost)
2. **Acting direction** — whether dialogue/mood needs directed performance
3. **Grade palette** — project-wide choice that all later prompts must match
4. **Medium** — stylized animation vs live-action (changes everything downstream)

### Genre default table (v1)

Seed table mapping brief genre → axis defaults. Extendable; unknown genres fall
back to a neutral cinematic default set.

| Genre | Camera | Lens | Lighting | Grade | Pacing | Acting |
|---|---|---|---|---|---|---|
| Noir / neon | Handheld + slow push-in, ≤2 moves | 35mm f/1.8, shallow DOF | Cool neon key screen-left, warm rim | Teal-orange or B&W | Ramp Up into beats | Fear/Vigilance I2, motive-driven |
| Pop music video | Kinetic, tracking/handheld | Wide 24mm, high-key | Colorful high-key, motivated | Vibrant, one palette | Beat-driven, Impact on chorus | Joy/Rage I2-I3, performance-as-escape |
| Horror | Slow push-ins, handheld | Wide 28mm, deep-ish | Low-key green/moonlight | Desaturated, muted | Slow menacing, Flash In scares | Terror I3, freeze responses |
| Comedy | Static or light handheld | 24mm bright | Bright soft fill | Warm, natural | Snappy, Calm-to-Dynamic | Comedic timing, reactive |
| Documentary | Observational handheld | 24mm natural | Natural available light | Natural, neutral | Natural/auto | Authentic, non-actor |
| Luxury/commercial | Slow dolly + static | 50mm f/2, controlled | Soft key + product fill | High-contrast premium | Slow, controlled | Serenity I1-I2, poised |
| (unknown) | Medium shot, subtle push-in | 35mm neutral | Motivated soft key | Neutral project palette | Auto/natural | Neutral |

### Output grammar

Fast mode summary:

```
Proposed defaults (fast mode):
  Audio: native  ·  Grade: teal-orange  ·  Acting: none (no dialogue)
  Medium: live-action
High-risk confirmations:
  - Grade palette [teal-orange]: ✓ / change to ___
  - Audio [native]: ✓ / lip-sync
  - Acting [none]: ✓ / direct ___
  - Medium [live-action]: ✓ / stylized ___
Confirm all → locked.
```

Full Q&A mode, per axis:

```
<Axis> — proposed default: <value>
  Why: <rationale>
  ✓ accept / adjust: <value>
```

### Persistence

Write confirmed choices into `project.md` frontmatter under a new `locked` block:

```yaml
locked:
  audio_mode: native            # native | lip-sync
  grade_palette: teal-orange
  acting_direction: none        # none | directed
  medium: live-action           # live-action | stylized
  camera: handheld-slow-pushin
  lens: 35mm-f1.8-shallow
  lighting: cool-neon-key
  pacing: ramp-up
  staging: none                 # none | blocking-map
  structure: none               # none | scene-engine
```

For multi-scene projects, scene-level overrides may add a per-scene `locked`
block in `scene.md`. The intake records which axes were confirmed vs accepted
by default, so a later full-Q&A pass only revisits confirmed decisions.

## Integration with film-production

Add a stage-1 sub-step to `film-production/SKILL.md`:

> **1a. Brief intake.** Before writing the brief's Required output, run
> `brief-intake` to propose genre-aware defaults. Fast mode by default; full
> Q&A when the user opts in. Persist the confirmed `locked` block to
> `project.md`.

Update `film-production/references/stage-contracts.md` stage 1 Required output
to include: "confirmed directorial `locked` defaults from `brief-intake`".

## Files

- NEW `.agents/skills/brief-intake/SKILL.md` — the intake skill (core deliverable)
- EDIT `film-production/SKILL.md` — route stage 1a to `brief-intake`
- EDIT `film-production/references/stage-contracts.md` — add locked-defaults to stage 1 output
- EDIT `docs/SKILL_AUDIT_REPORT.md` — add brief-intake to routing table

## Verification

- Smoke: run the intake on a 30s noir music-video brief in fast mode → assert
  it proposes the noir default set, surfaces the 4 high-risk choices, and
  persists a `locked` block to `project.md`.
- Smoke: run with "full Q&A" → assert all 10 axes are presented with
  rationale and confirm/adjust prompts.
- Unit: unknown genre → falls back to the neutral cinematic set.
- Edge: multi-scene project → per-scene overrides only revisit confirmed axes.
