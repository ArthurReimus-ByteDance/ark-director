# Slot Mapping — breakdown → prompt slots

How each `VideoBreakdown` field maps into Seedream and Seedance prompt slots.
This keeps the mapping reproducible and prevents slot drift.

## Seedance 2.5 six-part formula (via `seedance-prompt-25`)

| Six-part slot | Source field(s) | Notes |
|---|---|---|
| Subject | `elements[]` descriptors, bound to `@Image N` | Copy descriptors word for word; never summarize |
| Action | `shots[].action` + `shots[].motion` imperative wording | Per-shot stages with end states; motion wording is the anti-static fix |
| Scene | `elements[]` location descriptors | `@Image` binding |
| Visual style | `visual_style.grade` + `lighting_direction` + `lens` + `film_look` | Order: lighting → lens → grade → film |
| Camera | `camera` + per-shot `shots[].camera` + `shots[].motion.camera_motion` | ≤2 moves per clip |
| Audio | `audio` | `( )` music, `< >` SFX, `{ }` dialogue; transcribe dialogue in braces; `No audio at all` when source is silent |

## Reference binding order (Seedance)

1. `@Image 1` — sketch storyboard grid (shot order + composition; do not use
   grid lines/panel numbers/dividers)
2. `@Image 2..N` — element sheets (character → location → prop), each bound to
   its role.

The ordered `images[]` array must match `shot.md` `references:` exactly.

## Seedream element sheets

| Type | Skill | Output prefix |
|---|---|---|
| character | `seedream-character-sheet` | `char_<id>_turnaround_vNN.png` |
| location | `seedream-location-asset` | `loc_<id>_wide_vNN.png` |
| prop | `seedream-prompt` | `prop_<id>_<view>_vNN.png` |
| screen | `seedream-prompt` | `screen_<id>_vNN.png` |

Bind the source keyframe as `@Image 1` (I2I) where the breakdown flags one.

## Storyboard

- Panel count = `shots.length` (dynamic).
- Render = monochrome sketch (pencil/ink), never full color.
- Delivery = single-image grid; smallest grid that fits the count.
- 3 variants (same prompt, distinct seeds), selection gate: human review by
  default (`storyboard.review: true`), auto when `false`.
