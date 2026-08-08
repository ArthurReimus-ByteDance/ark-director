---
name: seedream-storyboard
description: Create, revise, and optionally generate production-ready cinematic storyboards—from one hero panel with alternatives to a multi-panel continuity sequence—with BytePlus Seedream. Use whenever the user asks for storyboards, shot boards, continuity boards, storyboard frames, visual sequences, previsualization, scene panels, or image planning for film, advertising, animation, games, or AI video.
compatibility: Actual image creation requires callable BytePlus Seedream image-generation tools. Without them, produce complete copy-paste prompts, generation parameters, filenames, and manifests.
---

# Seedream Storyboard

Create storyboards that make narrative, shot, staging, and continuity decisions
clear before expensive production. A storyboard is a sequence-level decision
artifact, not merely a collection of attractive images.

## Source authority

Follow the official [capability matrix](https://docs.byteplus.com/en/docs/ModelArk/1824121),
[prompt guide](https://docs.byteplus.com/en/docs/ModelArk/1829186), and
[interactive editing guide](https://docs.byteplus.com/en/docs/ModelArk/2582775).
If live documentation conflicts with a detail below, use it and state the
changed capability.

## What this produces

Depending on the request, produce a beat and panel plan, reference inventory,
spatial and continuity contract, exact prompts and parameters, generated panel
variants, immutable prompt snapshots and metadata, an ordered review package,
and a selection record after the user chooses a variant.

Keep these artifacts distinct:

- **Storyboard panel:** communicates a decisive story and staging state.
- **Look frame:** locks style, palette, lighting, and materials.
- **Video keyframe:** a polished image promoted as a generation anchor.

A storyboard panel may later become a keyframe, but only after it passes both
storyboard and visual-anchor review.

## Core rules

- Optimize for instant story clarity before polish.
- Describe one frozen, decisive moment per panel.
- Honor an explicit panel budget. When the user requests one panel, select the
  strongest representative moment instead of silently expanding the board.
- Without an explicit panel budget, add a panel when visual information or
  state materially changes.
- Keep recurring identities, locations, props, and style in an explicit canon.
- When matching canonical Element sheets exist, attach the selected character,
  location, and visible-prop sheets to the live generation request. A text
  description or an earlier storyboard panel is not a substitute for them.
- Treat screen direction and location geography as sequence-level constraints.
- Use coherent natural language, not comma-heavy keyword piles.
- Bind every reference by role and target with exact `@Image N` tokens.
- Prefer local edits to full re-generation after a composition is approved.
- Use seeds for experiment tracking, not as the identity system.
- Put arrows, labels, dialogue, timing, and production notes outside the
  generated image unless visible story-world text is required.
- A technically successful generation enters `review`; only an explicit user
  choice can set `selected_variant` or `approved`.

## Model selection

Choose the path according to the production need.

| Need | Preferred path | Important limits |
|---|---|---|
| Precise single panel, local correction, marked-region edit | Seedream 5.0 Pro, `dola-seedream-5-0-pro-260628` | Single-image output; up to 10 references; 1K/2K; interactive editing |
| Coordinated multi-panel sequence in one request | Seedream 5.0 Lite or configured 4.x binding | Supports multiple outputs; input references + outputs must stay within the live model limit |
| Three alternatives for one panel | Parallel variation generation | Each output is a candidate, not an ordered story sequence |
| No configured sequence-capable model | Pro, one panel at a time from the same canon | Reuse the same approved anchors and continuity record |

Never invent a model binding. If Lite or 4.x is not configured, either generate
individual Pro panels or deliver the sequence prompt and state what binding is
needed.

Use the delivery aspect ratio from the brief. If absent:

- `16:9` for landscape film, television, presentation, and horizontal ads;
- `9:16` for vertical short-form work;
- use another ratio only when the intended delivery format requires it.

For rough Pro panels, prefer the smallest valid size that preserves the target
ratio, such as `1280x720` for 16:9. Increase resolution only after composition
and continuity are accepted.

## Workflow

### 1. Inspect existing project context

Before creating files:

- search for the project, scene, shot, character, location, and prop;
- reuse approved assets and existing IDs;
- open every relevant `elements/characters/*/character.md`,
  `elements/locations/*/location.md`, and `elements/props/*/prop.md`; resolve
  one selected sheet/reference file per visible Element, its lifecycle state,
  and SHA-256 before writing prompts;
- preserve user-written descriptions and lifecycle states;
- do not create a duplicate project, scene, element, or same-purpose note.

If a project has relevant Element sheets, a generated panel must bind them by
role in both the submitted request and its metadata. If an Element has no
selected sheet, use the best available approved reference; otherwise record the
asset as `unresolved` and keep the output as an unlocked draft, ineligible for
video handoff. Do not quietly use a storyboard output as the canonical source.

If the request is not tied to a local project, keep the output in chat unless
the user asks for files.

### 2. Lock the brief

Extract or infer:

- project and scene;
- storyboard purpose: editorial board, continuity board, pitch board, or video
  keyframe planning;
- target medium and aspect ratio;
- cast, locations, props, wardrobe, and visible state;
- the selected character, location, and prop sheet for every visible Element;
- visual style, palette, lighting rules, and realism level;
- forbidden content or transformations;
- target runtime only when it affects the edit;
- panel budget, including whether the user wants one hero panel or sequence
  coverage;
- whether the user wants prompts only or actual image generation.

Ask only when a missing answer would materially change identity, format, cost,
or story meaning. Otherwise state reasonable assumptions and continue. An
explicit request to generate the storyboard authorizes a low-cost draft pass;
higher resolution, large batches, or repeated paid re-generation requires a
new explicit request or approval.

### 3. Break the scene into observable beats

Create a beat table before writing image prompts.

| Field | Meaning |
|---|---|
| Beat ID | Stable identifier |
| Purpose | New information or emotion delivered |
| Start state | What is true before the beat |
| Decisive moment | The exact instant the panel depicts |
| End state | What must be true for the next beat |
| Subjects and props | Visible entities and their state |
| Geography | Location, travel axis, entrances, exits |
| Sound/dialogue cue | Only when it changes timing or interpretation |

For a sequence board, do not convert a long action sentence directly into one
panel. Split actions such as “enters, notices the threat, drops the vial, and
attacks” into decisive states. For a requested one-panel board, still identify
all beats, then choose the single decisive moment that best communicates the
scene's subject, conflict or product, environment, and intended emotion.

### 4. Decide panel density

When the user specifies a panel count, treat it as a creative constraint.
Otherwise, panel count follows information and state changes, not duration
alone.

Add a panel for:

- a new camera position or cut;
- a decisive pose, reveal, or reaction;
- a material blocking or screen-direction change;
- an entrance, exit, boundary crossing, or axis re-establishment;
- a prop, wardrobe, damage, weather, or location-state change;
- a camera move whose start and end compositions both matter;
- a transition whose visual hookup must be reviewed.

For a camera move, use start and end panels when framing or revealed information
changes. For complex action, use anticipation, contact/change, and
consequence/reaction when each state matters. Add no mandatory second-by-second
timestamps; estimate duration only for timing or animatic-ready requests.

For a one-panel board:

- select one hero beat and one frozen composition;
- favor the image that best sells the scene's central story, emotion, or product;
- record important omitted transitions as motion notes rather than extra panels;
- recommend I2V or R2V for video handoff; request a second approved panel only
  if exact start-and-end locking through FLF2V becomes necessary. R2V bundle
  sizing is version-dependent: Seedance 2.0 allows ≤9 images; 2.5 allows ≤30.

### 5. Preflight every reference

Classify each input:

| Role | Controls |
|---|---|
| Character identity | Face, body, hair, costume, silhouette |
| Location geometry | Architecture, layout, landmarks, dressing |
| Prop identity | Shape, material, markings, orientation |
| Composition control | Blocking, pose, camera layout, depth |
| Style | Medium, texture, palette, grade |
| Continuity anchor | An approved prior panel’s exact state |

Check for:

- conflicts between the brief and visible reference content;
- extra faces, split panels, labels, watermarks, or effects that may leak;
- incompatible lighting, costume, age, scale, or perspective;
- ambiguous images that combine several reference roles;
- more references than the chosen model supports.

Use the smallest sufficient reference set, but include one selected source for
each visible character, the active location, and each story-critical prop. If
that exceeds the live model limit, split the panel/task or resolve the asset
set; do not silently drop an Element. If a visible reference conflicts with the
requested result, clean or replace it instead of relying only on an exclusion
sentence.

Control-only floor plans and sketches may guide structure, but state that their
lines, labels, and colors must not appear in the finished panel.

### 6. Establish geography and continuity

For dialogue, pursuit, combat, or multi-character action, define:

- durable landmarks and location boundaries;
- subject start/end positions;
- entrances and exits;
- travel direction;
- the line of action;
- camera side of the axis;
- screen-left/screen-right assignment;
- intentional axis crossings and how they are shown.

Maintain a continuity ledger:

```yaml
continuity:
  location_id: church-ruins
  time_of_day: night
  axis_id: altar-door-axis
  camera_side: south
  screen_direction:
    hunter: left-to-right
    creature: right-to-left
  subjects:
    hunter:
      wardrobe: hunter-coat-v01
      position: foreground-left
      pose_state: braced-at-threshold
      damage_state: cut-right-cheek
      held_props:
        right_hand: whip
        left_hand: none
  props:
    oil-vial-02:
      state: broken
      position: behind-hunter-right-boot
  environment_state:
    left_candle_bank: extinguished
    church_door: open-inward
```

Use permanent canon anchors plus one or two nearby approved panels. Do not chain
every panel automatically: re-anchor from canon after a rejected or compromised
frame.

### 7. Build the panel plan

Use this table:

| Panel | Beat | Decisive moment | Shot / angle | Staging and direction | State change | References | Target file |
|---|---|---|---|---|---|---|---|
| p010 | beat-01 | ... | ... | ... | ... | ... | ... |

Use panel numbers in increments of 10 so panels can be inserted without
renumbering.

For a one-panel board, create only `p010`. Generate alternatives as variants of
`p010`; do not mislabel three alternatives as three narrative panels.

### 8. Write the exact prompt for each panel

Use only the sections that add value. Keep the submitted prompt within the live
tool limit.

```text
References:
@Image 1: character identity — [character]
@Image 2: location geometry — [location]
@Image 3: prop identity — [prop]
@Image 4: composition control — [layout only]
@Image 5: approved style — [style, palette, and lighting only]

Task:
Image-to-Image (I2I) — single cinematic storyboard panel

Panel purpose:
[The new story information or emotion this panel communicates.]

Subject and decisive moment:
[One frozen moment. Name every visible subject, pose, expression, action, and
prop. Bind identity and prop references inline.]

Setting and state:
[Location, time, weather, persistent landmarks, visible object state. Bind the
location reference inline.]

Staging and continuity:
[Screen-left/right positions, foreground/midground/background, eyelines,
distances, overlaps, travel direction, entrances/exits, and what must match the
previous panel.]

Style:
[Medium, realism level, palette, and stable treatment. Bind the style reference
inline when provided.]

Lighting:
[Source, direction, quality, color, and atmosphere.]

Composition:
[Aspect ratio, shot size, camera height/angle, lens intent, framing, depth, and
focus priority. Bind the composition guide inline when provided.]

Constraints:
Quality: [appropriate draft or final quality]
Preserve: [approved identity, geometry, pose, state, and style]
Exclude: [only material faults; no text overlays, labels, storyboard borders,
watermarks, unintended subjects, duplicated faces, or control-guide marks]
```

For text-to-image, omit `References` only when there are no applicable
canonical Element sheets. When character, location, or prop sheets exist, use
image-to-image/reference generation and bind them with exact `@Image N` tokens.
Use:

```text
Task:
Text-to-Image (T2I) — single cinematic storyboard panel
```

Reference inventory alone is insufficient. Repeat each binding in the section
it controls:

```text
Use the face, hair, and wardrobe from @Image 1 for Mara. Preserve the room
geometry and altar position from @Image 2. Use @Image 4 only for blocking and
camera composition; remove all sketch lines and labels.
```

### 9. Write a cohesive sequence prompt for a multi-panel board

Use this section only when the board contains multiple narrative panels and the
selected model supports sequential output.

```text
Task:
Sequential Generation — [N] separate cinematic storyboard images

Sequence contract:
Generate a cohesive ordered set of [N] separate images, one image per numbered
panel. Keep recurring character identity, wardrobe, location geometry, prop
design, palette, and rendering style consistent. Each image must depict one
frozen decisive moment, not a collage or multi-panel grid.

References:
@Image 1: character identity — selected character sheet
@Image 2: location geometry — selected location sheet
@Image 3: prop identity — selected prop sheet

Global visual canon:
[Stable identity, location, prop, style, aspect ratio, and lighting rules.]

Panel 1 — [panel ID and purpose]:
[Decisive moment, staging, camera, and state.]

Panel 2 — [panel ID and purpose]:
[Decisive moment, staging, camera, and state change.]

[Continue in order.]

Constraints:
Return [N] separate images in narrative order. No captions, borders, panel
numbers, speech bubbles, watermarks, or contact-sheet layout inside the images.
Preserve character count, identity, handedness, screen direction, location
landmarks, and prop state unless a numbered panel explicitly changes them.
```

Set `max_images` to the requested panel count. Ensure references plus outputs do
not exceed the live model limit. If the sequence prompt approaches the tool
length limit, split it by scene or shot rather than deleting continuity rules.

### 10. Generate variants when requested or authorized

For actual image creation:

- use `seedream_generate_image` for a single panel or a sequence-capable batch;
- use `seedream_generate_image_variations` for independent alternatives;
- use `seedream_edit_image` for point- or bounding-box-guided corrections;
- set `persist: true`;
- use the lowest suitable draft size;
- set `watermark: false` unless the user requires a visible watermark;
- use `prompt_optimization: standard` for final candidates and `fast` only when
  latency matters more than fidelity.
- Upload and pass the resolved local Element files as ordered reference inputs;
  keep their `@Image N` indices identical in the prompt, request, and manifest.

For a one-panel board, generate three alternatives of that same panel by
default: `p010 v01`, `p010 v02`, and `p010 v03`. They share the same decisive
moment and continuity contract but explore useful composition, lens, staging,
or lighting differences. They are candidates, not a narrative sequence.

For a multi-panel board, generate three variants by default for keyframes and
high-risk panels. For ordinary continuity panels, first generate one low-cost
draft sequence; add alternatives only where composition or continuity is
unresolved.

If the user explicitly says they are working in Lumina, return clean
copy-pasteable prompts and parameters only. Do not call generation tools or
write local assets.

### 11. Persist every generated result locally

Never rely only on a provider URL. Use durable artifact persistence and save the
actual file under:

```text
projects/<project>/scenes/scene-NN/
```

Use:

```text
<scene>_sh<NNN>_p<NNN>_t<NN>_v<NN>.<ext>
```

Example:

```text
s01_sh010_p020_t01_v01.png
s01_sh010_p020_t01_v01_prompt.md
```

The prompt snapshot must contain the exact submitted prompt and parameters, with
its SHA-256 in the manifest. When an approved panel is explicitly promoted to a
video keyframe, use the project keyframe naming convention separately:

```text
s01_kf01_v01.png
```

Do not overwrite the storyboard source panel.

Record:

- model and model ID;
- ordered reference list and role of each image;
- prompt file and hash;
- size, format, watermark, seed, optimization mode, and batch count;
- output path, byte size, and hash;
- provider artifact ID when available;
- generated variants;
- requested delta and acceptance criteria;
- status;
- `source_assets` with each path, role, selected variant, approval state, and
  SHA-256;
- `video_handoff` with eligibility, promoted keyframe path, recommended image
  mode, target Seedance version (2.5 or 2.0), reference budget, and any
  invalidation reason.

Set a newly generated output to `review`, not `approved`.
Set `video_handoff.eligible: true` only after explicit panel approval and after
verifying that all recorded source-asset variants and hashes still match. A
changed character, location, or prop returns the dependent panel to `review`;
do not silently carry a stale panel into motion generation.

Use this minimum `source_assets` record for every visible canonical Element:

```yaml
source_assets:
  - element_id: lola-maria
    element_type: character
    role: character_identity
    path: elements/characters/lola-maria/references/ref_01_front.png
    selected_variant: ref_01_front.png
    status: approved
    sha256: "..."
    prompt_token: "@Image 1"
```

### 12. Review the board

Evaluate every individual panel. For multi-panel boards, also evaluate the
ordered contact sheet. For a one-panel board, compare its three variants side
by side; a comparison sheet is a review artifact, not another storyboard panel
and not the canonical video input.

| Dimension | Review question |
|---|---|
| Narrative clarity | Does each panel communicate one necessary beat? |
| Composition | Is the story point immediately dominant? |
| Spatial continuity | Are geography, axis, eyelines, entrances, exits, and travel direction coherent? |
| Character consistency | Do identity, body, wardrobe, scale, handedness, and damage state persist? |
| Environment and props | Are geometry, landmarks, ownership, position, and state correct? |
| Camera and motion | Are shot, angle, subject movement, and camera movement unambiguous? |
| Sequence logic | Do cause, effect, reveals, reactions, and transitions connect? |
| Reproducibility | Are prompt, references, model, parameters, files, and status recorded? |

Reject or repair:

- swapped, omitted, duplicated, or blended subjects;
- wrong subject count or screen order;
- accidental axis reversal;
- location geometry drift;
- missing, duplicated, or changed props;
- visible reference-sheet panels, labels, or sketch marks;
- a frame that is attractive but depicts the wrong beat;
- near-identical copy-paste panels that suppress required action change;
- a local correction that breaks previously approved areas.

### 13. Present variants and capture selection

Present candidates in panel order with filename or artifact ID, material
differences, known continuity or anatomy issues, and a recommendation.

Ask the user to choose a variant. After an explicit choice:

- set `selected_variant` to the chosen file;
- mark the chosen output `approved` only if the user approved it;
- mark rejected candidates `rejected` without deleting them;
- preserve prompts, hashes, and metadata for every take.

## Edit pattern for a failed panel

Use a narrow revision contract:

```text
References:
@Image 1: base storyboard panel to edit
@Image 2: approved character identity

Task:
Image Editing — local storyboard correction

Edit instructions:
In @Image 1, [single requested change at the marked point or bounding box].
Use the identity from @Image 2 for [character]. Preserve the camera, composition,
pose, screen direction, background geometry, lighting, palette, and all
unmarked subjects and props.

Acceptance criteria:
- [observable result]
- [continuity property that must remain unchanged]

Constraints:
No new subjects, no wardrobe change, no background redesign, no text, no
watermark, and no changes outside the target region.
```

Change one failed dimension at a time. Use the corrected result as a continuity
anchor only after it passes review.

## Default response structure

For a one-panel request, return a compact hero-beat decision, one `p010` panel
plan, reference inventory, exact prompt, three variant records, video-handoff
recommendation, review checklist, and selection needed. For a multi-panel plan
or prompt package, return assumptions and locks, reference inventory, beat and
panel plan, spatial and continuity contract, generation setup, exact panel
prompts, review checklist, and open decisions. When images were actually
generated, add generated variants and the technical record.

Do not claim that a storyboard, asset, or variant exists unless it was actually
generated and saved.
