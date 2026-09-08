# Integration And Timing

Focused reference for `seedance-vfx-prompt`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [7. Lighting (embedded)](#7-lighting-embedded)
- [8. Space (layered)](#8-space-layered)
- [9. Timing (if applicable)](#9-timing-if-applicable)
- [10. Audio (diegetic only)](#10-audio-diegetic-only)
- [11. Quality and constraints](#11-quality-and-constraints)

## 7. Lighting (embedded)

**Lighting must live inside the world.** Never describe lighting as a layer
pasted on top of the footage — the model will produce a flat, artificial look.

```text
Lighting: The bioluminescent fungi cast cool blue light upward onto Man@Video 1's
raincoat and face from below. Warm amber light leaks from distant fire-spores
deep in the jungle, creating a warm-cool contrast. The mist catches the light
as a soft volumetric haze. No flat ambient fill.
```

Embedded lighting rules:
- Light **sources** must be physically present in the new world (fungi, fires,
  neon signs, portal glow, moonlight through canopy).
- Describe **where the light falls** on the subject (direction, color, intensity).
- Describe **how the light interacts** with the environment (volumetric mist,
  reflections on wet surfaces, shadows cast by foreground elements).
- Never say "cinematic lighting" or "dramatic lighting" alone — name the source.

### The integration fork

Decide explicitly which of these two paths the shot takes — it changes the
lighting instruction and the identity risk. State the choice in the `Lighting:`
section.

- **Preserve the subject's lighting; grade only the new elements.** Lock the
  subject's original key light; light and grade the added environment/creature
  to match that existing key so they integrate. Lowest identity risk — use this
  as the default.
- **Relight the whole frame under one look.** Subject included. Use this for a
  unified cinematic or commercial grade. Higher risk to the face — keep
  identity, expression, and wardrobe explicitly locked in the `Locks:` section
  while only lighting and grade change.

### The "looks pasted in" failure

Color matching alone is **not enough** to make a preserved subject sit in a new
world — that is the most common composite failure. When integrating a subject
(or a creature) into a plate, go beyond color with this recipe:

- **Light:** same key direction (name it — screen-left or screen-right), same
  softness, same shadow density and direction across the subject.
- **Environmental bounce:** let the world spill onto the subject — cool skylight
  from above, a warm bounce from sunlit ground or foliage, subtle ambient
  occlusion where forms meet.
- **Optics & atmosphere:** match lens character and micro-contrast; add a touch
  of the scene's atmospheric haze over the subject so they aren't unnaturally
  crisp against a hazy background; match depth of field, focus falloff, and film
  grain to the rest of the frame.
- **Edges & grounding:** remove hard cut-out edges, halos, and mismatched rims;
  ground the subject with believable depth so they occupy the same space.

State the time of day and key direction concretely: "soft, diffused midday
daylight with the key from screen-right." "Softer" means a larger, more diffuse
source — gentle soft-edged shadows, low contrast, smooth highlight rolloff,
light haze. **Warm, directional daylight worlds are safer** for face/identity
consistency than night or neon — those force a full relight of the subject and
raise drift risk. Flag this tradeoff and bake the relight instruction in when
the user wants night or neon anyway.

## 8. Space (layered)

Build depth with explicit foreground, midground, and background layers.

```text
Space: Foreground — wet fern fronds and low mist passing close to camera as it
moves. Midground — Man@Video 1 on the jungle path, the bioluminescent fungi
lining both sides. Background — towering fungal columns receding into blue-black
fog, distant waterfall.
```

Layered space rules:
- Foreground elements should **pass through frame** as the camera moves — this
  sells the parallax and makes the composite feel real.
- Midground holds the subject and the primary environment.
- Background provides atmosphere and scale, often partially obscured by fog,
  mist, or darkness.

## 9. Timing (if applicable)

For sequential or progressive VFX, describe when each event triggers and how it
develops.

```text
Timing:
0:00 — Environment is fully replaced; Man@Video 1 is already on the jungle path.
0:02 — Creature emerges from right foliage, initially just glowing eyes.
0:02.5 — Creature fully visible, begins following at a distance of 2 meters.
0:04 — Creature ducks back into foliage as the man turns a corner.
```

### Timed camera moves synced to dialogue

A crash zoom or smooth push-in landing on a beat is a recurring payoff. Anchor
it **two ways at once** so it lands even if Seedance's internal timing drifts:
a semantic cue and a numeric cue.

- **Semantic:** `At the line "<exact words>," the camera <snaps into a hard
  crash zoom | begins a smooth, steady push-in>…` Requires `SFX and source
  dialogue only` in the audio section so the talk track survives.
- **Numeric:** `At about <T> seconds… the camera…` Derive `T` from the source
  audio — measure the timecode of the spoken line and convert.
- **Crash zoom** = fast hard punch-in; **smooth push-in** = slow steady glide,
  no snap. Match the user's word.
- If a landmark or subject must stay visible **through** the move, say so
  explicitly — the camera pushes toward the element, keeping the landmark in
  frame throughout, never cropping it.
- Leave enough tail after the trigger for the payoff to play (a creature slowly
  turning to camera needs ~2–3s). If the clip is short, fire the zoom on the
  first word of the line rather than after it.

### Reveal pull-back (the outward move)

The mirror of the push-in: open tight on the **added** element in isolation —
a long-telephoto, compressed framing of the creature or effect with the subject
out of frame — then move outward to land on the real plate.

- **Hard / snap zoom-out** = fast punch outward, abrupt.
- **Smooth pull-back** = slow steady decompression, no snap.

Anchor the landing the same two ways (semantic + numeric). Critically, demand
a **100% match of the source composition** at the landing: name the matched
attributes — same angle, headroom, horizon, lens character — or the model
lands on a near-miss framing that no longer cuts against the original. After
the landing, hand off to the preserved take and keep the source's own camera
motion running.

### Preserving lip-sync to a known line

When the payoff is the subject's mouth matching a specific line, quote it
**verbatim** and anchor it twice: once inside the change or action
("…lips matching the source exactly, saying clearly: '<line>'…") and once in
the audio section. Require `SFX and source dialogue only` so the talk track
survives, and add "lips matching the source exactly" to the `Locks:` section.
Then check the line against the surviving dialogue window (see **Duration
discipline**) — a line that runs ~6s cannot sit in a 5s tail. If it doesn't fit,
resolve the runtime before delivering; do not ship a prompt that cannot lip-sync.

## 10. Audio (diegetic only)

Seedance 2.0 generates native audio with video. In VFX, **only diegetic sound**
— sound that physically exists in the new world — should be requested. Do not
request non-diegetic music or narration unless the source clip already contains
it and must be preserved.

```text
Audio: Jungle ambience — distant waterfall, dripping moisture, insect chirps,
soft undergrowth crunching under Man@Video 1's boots. The creature emits a
faint chittering sound when it emerges. Wet footsteps preserved from source.
SFX and source dialogue only.
```

Diegetic audio rules:
- Every sound must have a **physical source** in the new world.
- Preserve source-clip diegetic sounds that still make sense (footsteps on a
  surface, breath, wind if the new world has wind).
- Do not request background music, score, or voiceover unless it is part of the
  source footage and must be locked.

## 11. Quality and constraints

Close with image quality, style, and negative constraints. This section
tightens the generation boundaries and holds the guards — NON-IP, face
protection, no-warp, camera-motion lock.

```text
Quality and constraints:
Quality: photoreal, 4K, cinematic texture, natural colors, soft lighting.
Constraints: NON-IP — no recognizable real persons, no copyrighted characters,
no brand logos. Face protection — Man@Video 1's face must remain real human skin
with visible pores, stubble texture, and natural catchlights in the eyes. Never
waxy, smoothed, blurred, or warped. The jaw and lip sync must match the source
frame-for-frame. No morphing artifacts at the boundary between the man and the
new environment.
```

Face protection is the most important guard for footage involving people:

> "Real human skin with pores, stubble, and catchlights — never waxy, smoothed
> or warped."

Treat face fidelity as an observable output-QA requirement. Resolve model and
supported resolution first; a face does not force a model switch or guarantee
quality at any resolution. The 4K examples in the legacy sections apply only
to a tool/model combination that explicitly supports 4K.
