---
name: seedance-prompt-25
description: >
  Write production-grade Seedance 2.5 video prompts with the flexible six-part
  formula, 50-material multimodal referencing, variable-duration scene staging
  (4-30s), timestamp pacing, structured video editing (subject replacement,
  background replacement, audio editing), forward and backward video extension,
  keyframe sequences, storyboard grids, coarse and fine blockout references,
  one-click video, seamless transitions, audio bracket syntax, dialogue
  language reinforcement, emotional direction, and camera language. Use this
  skill for Seedance 2.5 prompts, multi-reference asset orchestration, scene
  staging, video editing, extension, and corrections to generated motion or
  continuity. For legacy Seedance 2.0 prompts, use seedance-prompt-20 instead.
  For 4K output resolution (unsupported by 2.5) or Fast/Mini speed variants,
  also use `seedance-prompt-20`.
---

# Seedance Prompt

Write production-grade prompts for the BytePlus Seedance 2.5 video generation
model. Seedance 2.5 generates **up to 30 seconds** of video with native audio in
a single pass (set the actual duration via the `duration` parameter — 30s is
the ceiling, not the target), accepts up to **50 multimodal reference
materials**, and supports video editing, extension, one-click video, and
seamless transitions. The model co-generates audio and video in one latent
space, so sound direction in the prompt shapes the final result.

## Source authority

The prompt structure and rules in this skill are sourced from the official
Dreamina Seedance 2.5 Prompt Guide:
- [Seedance 2.5 Prompt Guide (Lark)](https://bytedance.larkoffice.com/docx/A88jd0B47oAd8zxWp5ycZFMfnxh)
- [Seedance 2.5 Launch Blog](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
- [BytePlus ModelArk Model List](https://docs.byteplus.com/en/docs/ModelArk/1330310)
- [Seedance 2.0 Prompt Guide](https://docs.byteplus.com/en/docs/ModelArk/2222480) (legacy — for 2.0, use `seedance-prompt-20`)

When the official guide is updated, prefer the live page over this skill where
they conflict.

## Core prompt formula

> **Subject + Action or Event + Scene and Environment (optional) + Visual Style (optional) + Camera Movement/Cut (optional) + Audio (optional)**

Only **Subject + Action** is required. Every other part is optional — omit what
does not apply. Summarize the main action first; add detail only to critical
movements. **Do not describe the same action twice.** Generation parameters
(duration, resolution, aspect ratio) belong in the generation interface or API,
not in the prompt.

```
<Subject> performs <primary action or event> in <scene and environment>.
The visuals feature <visual style>.
Use <shot size, camera angle, camera movement, or cuts>.
Audio includes <dialogue, ambience, sound effects, or music>.
```

### Visual Style slot composition

When combining multiple Visual Style presets (lighting, lens character, color
grade, sensor/film look), chain them in this order within a single "The visuals
feature ..." sentence:

> **lighting → lens character → color grade → sensor/film look**

Example with three presets active:

```
The visuals feature warm golden key light from screen-right, shallow depth of
field with compressed bokeh, a teal-and-orange cinematic grade, and subtle
film grain with soft halation.
```

Each preset skill (`seedance-lighting-presets`, `seedance-lens-presets`,
`color-grade-palettes`) produces one phrase; this rule defines how they
assemble. Use only the presets the user requested — do not pad the slot with
unused defaults.

### Example

```
A ceramic artist finishes a pale blue cup in a studio at dawn, lifts it from the wheel,
and places it in the center of a wooden shelf.
Soft morning light enters through the window. The wet clay has a delicate sheen, and the
workbench remains tidy.
Begin with a medium shot of the wheel-throwing process, slowly push in toward the cup's
surface texture, then cut to a frontal view of the shelf.
Retain the low hum of the pottery wheel, the friction of clay, and subtle indoor ambience.
```

### Stylized animation medium

When the user requests claymation, felt, wood puppets, toy miniatures, vintage
cel/rubber-hose animation, painterly 2D, handcrafted 3D, silicone creatures,
wax crayon, or another medium whose material behavior must persist through
motion, load the partner `seedance-animation-styles` skill. It owns the medium,
construction, deformation, craft-imperfection, and still-anchor contract; this
skill remains the authority for the full six-part prompt, reference roles,
scene staging, timestamps, audio syntax, and generation limitations.

## Reference materials

### Limits and recommended ranges

Seedance 2.5 accepts up to **50 reference materials** per generation.

| Material Type | Input Limit | Recommended Range |
|---|---|---|
| Images | Up to 30, each ≤ 4K | Prefer 1–8 distinct subjects |
| Videos | Up to 10, combined ≤ 30s | Prefer 1–5 subjects, 5–10s each |
| Audio | Up to 10, combined ≤ 30s | Keep only directly relevant dialogue/voice/ambience/music |
| Video Editing | Source video + reference images | Source < 20s, 1–5 reference images |

You may push beyond recommended ranges (9–12 subjects in images, 6–10 in
audio/video, 6–8 editing refs), but **stability decreases** as count grows. If
>5 subjects need multiple views, use **separate images per view** — independent
view images are more stable than collages.

### Role definition syntax

After uploading references, specify exactly what each one contributes. Add
exclusions only when a person, background, or composition could unintentionally
leak into the output.

**Three non-negotiable rules:**
1. Put the material mapping **directly in the prompt**.
2. **Never make the model guess** which asset belongs to which person, prop, or scene.
3. Add `"Do not use..."` exclusions only when leakage is genuinely possible.

```
@Image 1 defines <subject>'s <appearance, clothing, structure, or material>.
@Video 1 defines <motion, camera movement, or pacing>.
@Audio 1 defines <character or sound type>'s <voice, dialogue, ambience, or music>.

<Subject> completes <primary action or event> in <scene>.
The visuals feature <visual style>, with <camera treatment>.
```

Add `"Do not use..."` exclusions **only** when a person, background, or
composition in the reference could unintentionally leak into the output. You do
not need one for every asset.

### Multiple views of the same subject

When several images show different angles of one person or product, state this
explicitly:

```
@Image 1 defines the front view of the same folding desk lamp.
@Image 2 defines the left-side structure of the same folding desk lamp.
@Image 3 defines the right-side structure of the same folding desk lamp.
@Image 4 defines the rear structure of the same folding desk lamp.
All four images define one folding desk lamp. The output must contain only one lamp throughout.
```

### Inheritance from reference videos

If a reference video already defines the motion, camera movement, and sequence
accurately, **state only which attributes to inherit** — do not restate every
action. Repeating the motion description may **conflict with the reference
itself**. A blockout video mainly provides motion and spatial structure, so the
prompt must still define the intended subjects, scene, action, and visual style.

### Reference classification

Classify each reference by how it may influence visible output:

- **Visible identity** — character, creature, costume, prop, or vehicle that should appear.
- **Visible environment** — location, lighting, weather, or production design that should appear.
- **Motion or camera reference** — movement language to transfer without copying pixels.
- **Control-only reference** — route map, blocking diagram, timing chart, or other planning material that must not appear.

Every supplied image can leak visible pixels, colors, lines, labels, or
composition into the result. For a control-only image, prefer translating its
information into concise textual choreography and omitting the image. Reference
content can overpower negative wording — if a character sheet contains an aura,
weapon, logo, or extra face that must not appear, clean or replace the reference
rather than relying on "no aura" constraints.

## Multi-reference workflow (5 steps)

When working with many references, the goal is **not** to put every reference
into one sentence. The goal is to define relationships and help the model
select the correct materials for each scene.

> **Define Each Material's Role → Map Subjects → Group by Type → Create Subject Profiles → Select References by Scene**

### Step 1: Name and map each subject individually

```
<Character A> corresponds to @Image 1. Use only the appearance, hairstyle, and clothing.
<Character B> corresponds to @Image 2. Use only the appearance, hairstyle, and clothing.
<Prop A> corresponds to @Image 3. Use only the structure, material, and color.
<Scene A> references @Image 4. Use only the spatial layout, architecture, and lighting. Do not use the people in the image.
```

Do **not** write `"@Images 1 through 4 define four characters respectively."` —
it never says which image maps to which character.

### Step 2: Group materials by type

```
[Characters]
<Conservator> corresponds to @Image 1. Use only the appearance, hairstyle, and clothing.
<Registrar> corresponds to @Image 2. Use only the appearance, hairstyle, and clothing.
<Exhibition Installer> corresponds to @Image 3. Use only the appearance, hairstyle, and clothing.
<Guide> corresponds to @Image 4. Use only the appearance, hairstyle, and clothing.
Do not interchange the four characters' appearances, clothing, actions, positions, or dialogue.

[Props]
<Sample Case> corresponds to @Image 5 and belongs only to <Conservator>.
<Record Board> corresponds to @Image 6 and belongs only to <Registrar>.

[Scenes]
<Conservation Lab> references @Image 7. Use only the space, materials, and lighting.
<Gallery> references @Image 8. Use only the space, materials, and lighting.

[Motion and Audio]
@Video 1 defines the motion of <Conservator> opening <Sample Case>. Do not use the person or scene from the video.
@Audio 1 defines <Guide>'s voice and specified dialogue.
```

### Step 3: Create a centralized profile for important subjects

When the same character uses several references across multiple scenes:

```
[Subject Profile: Conservator]
Appearance and clothing: @Image 1.
Fixed prop: <Sample Case> from @Image 5.
Locations: <Conservation Lab> and <Gallery>.
Motion references: the case-opening motion from @Video 1 and the sample-placement motion from @Video 2.
Do not use: other characters' clothing. Do not give this character <Record Board> or guide equipment.
```

### Step 4: Select references by scene

Each scene names **only** the assets it uses, the event, and the required end
state:

```
Scene 1 | Inspection in the Conservation Lab
Use: <Conservator>, <Sample Case>, <Conservation Lab>, and the case-opening motion from @Video 1.
Event: <Conservator> opens <Sample Case> at the workbench and inspects the sample inside.
End state: <Conservator> remains on the inner side of the workbench. <Sample Case> stays beside the
conservator's right hand, which is on the left side of the frame.

Scene 2 | Registration in the Gallery
Use: <Registrar>, <Record Board>, and <Gallery>.
Event: <Registrar> checks the number on <Record Board> beside the display case.
End state: <Registrar> still holds <Record Board> with both hands. No other character enters the
display-case area.
```

> The goal is to help the model select the correct materials for the current
> scene, **not** to make every material appear at the same time.

## Scene staging

When a video contains several events, divide the story into **consecutive
stages**. Give each stage only **one primary state change** and a **clear end
state** — what should be directly visible at the end.

**Generate per scene at its natural duration (4–30s), not per 30-second block.**
Right-size each scene using the `duration` parameter — 7s for a single beat,
12s for a short dialogue exchange, 20s for a multi-stage action sequence. Do
not pad scenes to fill 30s. Chain approved scenes via `return_last_frame` /
`first_frame` + a shared reference bundle and assemble in post.

```
[Generation Goal]
Generate a <video type>. The central subject is <subject>, and the primary event is <story summary>.

[Stage 1]
Initial state: <initial state of characters, props, and scene>.
Primary event: <one primary action or event>.
End state: <character positions, prop ownership, or visible scene state>.

[Stage 2]
Continue from the previous stage: <state that must remain unchanged>.
Primary event: <one primary action or event>.
End state: <observable state>.

[Stage 3]
Primary event: <closing event>.
End state: <final visible state>.

[Maintain Consistency]
Keep <character identity, number of characters, clothing, prop ownership, spatial direction,
and audio relationships> consistent.
```

### When to use 30s single-pass or native extension (exception)

Native extension (up to 180s, beta) and full 30s single-pass are the **exception**,
not the default. Use them only when you explicitly need continuous, seamless
motion across what would otherwise be scene boundaries:

- **Single continuous take** — a one-shot with no cuts where seamless motion
  across 30s+ matters more than per-scene iteration control.
- **Minimal scene variation** — same location, same characters, gradual change
  that the model handles well in one pass.
- **Audio-driven long dialogue** — one long dialogue block where lip-sync must
  be continuous across scene boundaries; extension keeps it seamless.

If using extension: generate a 30s base take, then extend it forward/backward
in rounds — **do not force scene changes at every 30s mark**; scene changes
happen naturally where the story needs them.

- **Audio with extension.** Align a single Seed Audio master to the full timeline
  (up to ~2 min) and pass it as `reference_audio` so dialogue and sound stay
  continuous across the extension.
- **Validate seams.** Extension boundaries are not pixel-identical; inspect the
  boundary image, motion trend, and audio continuity on both sides of each seam.
  Multi-round extension is beta — validate each seam before committing.
- **Aspect ratio** is locked to the input video's ratio for extended segments.

### Timestamps and pacing

Use stages by default. Use one-second precision **only** for critical handoffs,
entrances/exits, transitions, or explicit beats.

| Pattern | Example |
|---|---|
| Time range | `0-3 seconds... 3-7 seconds... 7-12 seconds...` |
| Exact time point | `At 5 seconds, the camera whip-pans rapidly to the left.` |
| Relative timing | `Three seconds after the character presses the button, the lights dim.` |

Rules:
- Time ranges must be **consecutive and non-overlapping**.
- They are a **time budget**, not a precise edit point — actions may occur slightly before or after a boundary.
- Too little content gives the model too much freedom; too much causes excessive cutting or omitted events.
- **Never** demand impossible frequencies (e.g., "complete three actions in one second").

## Special audio and text syntax

| Content | Syntax | Example |
|---|---|---|
| **Music** | `()` | `(Soft, rhythmic piano music plays in the background)` |
| **Sound Effects** | `<>` | `<A bell rings in the distance>` |
| **Dialogue** | `{}` | `{Hello, welcome back.}` |
| **Subtitles** | `【】` | `【Chapter One: Departure】` |

### Dialogue language reinforcement

When dialogue is not in Chinese, specify the language before the line:

```
The girl says softly in Japanese: {もう大丈夫です}
```

For regional accents or to prevent language mixing:

> **Dialogue Language + Regional Variety or Accent + Delivery Style + Speaker + {Dialogue}**

```
Dialogue language: American English. The girl says in natural, conversational American English: {I thought you weren't coming.}

Dialogue language: authentic Los Angeles English. The young man says in natural Los Angeles vernacular: {No way, you actually made it.}
```

### Unsupported languages and pronunciation guidance

Seedance 2.5 natively supports 10+ languages: Chinese, English, Spanish,
Indonesian, Malay, Thai, Arabic, Portuguese, Vietnamese, Japanese, and Korean.
**Languages outside this list** — such as Tagalog/Filipino, Hindi, Bengali, or
Swahili — may require additional pronunciation and intonation annotation in
the prompt, or an **audio-first pipeline** (when the user requests lip-synced
audio) where dialogue is generated by Seed Audio (cross-lingual) and passed as
`reference_audio`.

For **Tagalog/Filipino or Taglish** dialogue, use the partner skill
`seedance-prompt-25-filipino`, which provides a phonetic annotation system
(stress markers, glottal-stop notation, syllable breakdown), intonation
direction (flat baseline, L-H/H-L phrase accents, question/statement contours),
Taglish code-switching guidance, and an optional audio-first pipeline. Load that
skill alongside this one whenever the scene contains Filipino dialogue.

### Direct audio controls

```
No background music. Keep only the characters' dialogue, ambience, and action sound effects.
No subtitles.
No audio at all.
```

## Parameter auto-lock rules

Three task types automatically lock generation parameters based on input materials:

| Task Type | Aspect Ratio | Duration |
|---|---|---|
| **Video editing** | Locked to input video's ratio; **cannot be set** | Locked to ~input duration (±0.3s); **cannot be set** |
| **First/last-frame generation** | Locked to **first image's ratio**. First & last must match | Can be set |
| **Video extension** | Locked to input video's ratio; **cannot be set** | Can be set |

## Video editing

When editing, first define the source video as the **sole editing master**, then
specify edit target, scope, target material, and content to preserve. The output
preserves the input's aspect ratio and approximately preserves duration (±0.3s
from transition-frame handling).

### General editing pattern

```
[Edit Goal]
Edit @Video 1. Within <the entire video or a specific time range>,
<add, remove, replace, or adjust> <visual object, region, or audio category>.

[Source Video Role]
@Video 1 is the sole editing master. It defines <characters, scene, actions, composition,
camera movement, occlusion relationships, audio, and event order>.

[Target Material Role]
@Image 1 or @Audio 1 defines <specified attributes of the target object or sound>.

[Edit Scope]
Modify only <object, region, time range, or audio category>.

[Content to Preserve]
Keep <visual content, motion, audio, and timing relationships that must not change> from @Video 1.
```

### Subject replacement with Timeline Inheritance

The target object **inherits every appearance, motion, occlusion, and exit** of
the original object, including timing, duration, path, and speed changes.

```
[Edit Goal]
Edit @Video 1. Change only <original object> to <target object>.

[Source Video Role]
@Video 1 is the sole editing master. It defines the original scene, camera position, camera
movement, motion path, occlusion relationships, and event order.

[Target Reference Role]
@Image 1 defines <target object>'s <appearance, structure, or material>. Do not use <irrelevant
background, people, or composition>.

[Edit Scope]
Modify only <specific object and area>. The entire video contains <number> target object(s).
Do not modify <content to preserve>.

[Timeline Inheritance]
<Target object> inherits every appearance, motion, occlusion, and exit of <original object>,
including timing, duration, path, and speed changes.
Except for the object or area explicitly modified above, keep all other people, props, scene
content, camera movements, cuts, and event order from @Video 1 unchanged.
```

### Background replacement

Swap the background while preserving the subject's silhouette, identity, motion,
and occlusion relationships.

```
[Edit Goal]
Edit @Video 1. Replace only <original background area> with <target environment> from @Image 1.

[Source Video Role]
@Video 1 is the sole editing master. It defines the people, foreground objects, actions,
composition, camera movement, and event order.

[Target Reference Role]
@Image 1 defines only <target environment>'s spatial layout, materials, depth of field, ambient
color, and lighting direction. Do not use the people or foreground objects in the image.

[Edit Scope]
Modify only <background outside the subject's silhouette>. Do not modify <subject identity, facial
features, hairstyle, clothing, expression, position, size, or motion>.

[Timeline Inheritance]
Keep the character actions and occlusion relationships from @Video 1. Except for the modified
area, keep all other content from @Video 1 unchanged.
```

### Audio editing

Dialogue, language, voice, background music, and sound effects can be edited
**separately** from visuals.

```
Edit @Video 1. Remove only the original background music. Keep the character dialogue, lip sync,
ambience, and action sound effects; preserve the visuals, camera treatment, and editing rhythm
from @Video 1.

Edit @Video 1. Change <Presenter>'s spoken language to natural American English while preserving
the dialogue content and speaking times. Keep all other character voices, background music,
ambience, and visuals from @Video 1.
```

## Video extension

Video extension creates content beyond the boundary of a source video.
- **Forward extension**: extension's first frame continues from the source's last frame.
- **Backward extension**: extension's last frame connects to the source's first frame.

### Forward extension

```
@Video 1 is the source video to extend forward.

Extend @Video 1 forward. The first frame of the extended segment directly continues from the last
frame of @Video 1. Maintain continuity in <subject pose and orientation>, <prop position>,
<background and spatial relationships>, <camera position and composition>, <lighting>, and
<motion direction>.

Then, <describe the new action, event, camera treatment, or audio to add>.

Throughout the extension, maintain continuity in <character identity and clothing>, <key props>,
<background layout>, and <axis of action>.
Keep each subject as the same continuous instance throughout: do not duplicate or split it, and
keep the person's appearance or the object's number of parts stable.
```

With additional references — define every material's role first, then state the
source video controls the boundary. New materials may supplement but **must not
override** the source video's last-frame control.

```
@Image 1 defines <Character A>'s facial features.
@Image 2 defines <Character A>'s clothing.
@Image 3 defines <key prop>'s structure and material.
@Video 1 is the source video to extend forward.

Extend @Video 1 forward. The first frame of the extended segment directly continues from the last
frame of @Video 1. Maintain continuity in <boundary-frame state>.

Then, <Character A uses the key prop to complete a new action or event>.

Throughout the extension, maintain continuity in <character identity and clothing>, <key prop>,
<background layout>, and <axis of action>.
Keep each subject as the same continuous instance throughout.
```

### Backward extension

Describe what happens **before** the source video, then define the source's first
frame as the **explicit end state**. Writing only "connect to the source video"
is not enough — it can let characters or effects enter too early.

```
@Video 1 is the source video to extend backward.

Extend @Video 1 backward. Before the source video begins, <describe the preceding action, event,
camera treatment, or audio>.

The last frame of the extended segment naturally connects to the first frame of @Video 1:
<subject pose and orientation>, <prop position>, and <background and spatial relationships>.
Match the <camera position and composition>, <lighting>, and <motion direction> of @Video 1's
first frame.

Throughout the extension, maintain continuity in <character identity and clothing>, <key props>,
<background layout>, and <axis of action>.
Keep each subject as the same continuous instance throughout.
<Materials that should appear only after the source video begins> must not appear early.
```

> Boundary frames connect naturally at a visual level; they will **not** be
> pixel-identical. Inspect both sides of the boundary during review.

### Backward extension with additional references

Define each material's role, and state which materials are used in the backward
extension and which should appear **only after** the source video begins. This
reduces the chance that later characters, props, or effects enter the preceding
segment too early.

```
@Image 1 defines <Character A>'s facial features.
@Image 2 defines <Character A>'s clothing.
@Image 3 defines <key prop>'s structure and material.
@Video 1 is the source video to extend backward.

Extend @Video 1 backward. Before the source video begins, <Character A completes a preceding
action or event>.

The last frame of the extended segment naturally connects to the first frame of @Video 1:
<Character A's pose and orientation>, <key prop's position and state>, and <other characters'
positions>. Match the <background and spatial relationships>, <camera position and composition>,
<lighting>, and <motion direction> of @Video 1's first frame.

Keep each subject as the same continuous instance throughout: do not duplicate or split it.
<Materials that should appear only after the source video begins> must not appear early in the
backward extension.
```

## Keyframes, storyboards, and blockouts

### First and last frames in R2V mode

State `@Image 1 is the first frame` and `@Image 2 is the last frame` directly in
multimodal reference mode — **no separate mode switch needed**. The system locks
the aspect ratio to the first image. First and last images **must share the same
aspect ratio**.

- Describe each anchor image **separately** — do not combine into one sentence.
- Additional references supplement **only** their specified attributes and must
  **not** replace the first/last-frame composition.

```
@Image 1 is the first frame. It defines the opening composition, subject position, pose, prop
state, scene, and camera direction.
@Image 2 is the last frame. It defines the ending composition, subject position, pose, prop
state, scene, and camera direction.
@Image 3 defines <Subject A>'s <appearance, clothing, structure, or material>. Do not change
the first-frame composition defined by @Image 1 or the last-frame composition defined by @Image 2.

<Describe one continuous action or event>.
The video begins naturally from the first frame and reaches the last frame after the continuous action.
Between the first and last frames, maintain continuity in <character identity, prop structure and
ownership, scene layout, and camera direction>.
```

### Multi-keyframe sequences

When separate images define different stages:

```
Use @Image 1 through @Image N as keyframes in this order.

@Image 1 is the first frame. It defines <opening composition>.
@Image 2 defines the second keyframe: <visible end state of Stage 1>.
@Image 3 defines the third keyframe: <visible end state of Stage 2>.
@Image N is the last frame. It defines <ending composition>.

The video passes through the states defined by @Image 1, @Image 2, @Image 3, and @Image N in
order, using continuous action to transition naturally between stages.
Maintain continuity in <subject identity, prop structure and ownership, scene layout, lighting,
and axis of action> throughout.
```

> Independent keyframe images are easier to align than grids. They control stage
> order and key states; they do **not** reproduce every frame exactly.

### Storyboard grids

- Communicate overall story, shot order, and approximate compositions — **not strict reproduction**.
- **Prefer ≤ 15 panels.** Use clean line art or simple diagrams; minimize text labels.
- State the reading order, then describe each panel.

```
@Image 1 provides an <N-panel storyboard grid> for shot order and approximate composition.
Read it <left to right, top to bottom>. Do not use the grid's <line-art style, text labels, or
placeholder characters>.
@Image 2 defines <Subject A>'s <appearance and clothing>.

Shot 1: <shot size, subject action, and scene state>.
Shot 2: <shot size, subject action, camera movement, or transition>.
...
Shot N: <closing action and final visible state>.

The final video uses <visual style>. Audio includes <dialogue, ambience, action sound effects, or music>.
```

### Blockout references

Two categories — first determine whether the blockout is a **motion skeleton**
(coarse) or a **complete model** (fine):

| Type | Best For | Material Requirements | Prompt Focus |
|---|---|---|---|
| **Coarse blockout** | Simple geometry previewing action, paths, blocking, camera, or cuts | Clear relationships between shapes and a complete action sequence; character/prop/scene images may be added | Map every blockout subject; state which temporal/spatial info to inherit |
| **Fine blockout** | Complete modeling needing new materials, colors, scenes, or style | Complete, clean model; avoid path lines, coordinate axes, camera frustums | Preserve structure, action, and camera treatment; define attributes to re-render |

**Coarse blockout** — lock action paths, motion direction, blocking,
entrances/exits, camera paths, cut points, lighting changes, and sound rhythm.
Map each geometric object to its final subject.

| Blockout Information | What to State |
|---|---|
| Path | Action trajectory, motion direction, subject blocking, entrance/exit order |
| Camera movement | Camera position, path, direction, speed changes |
| Lighting | Light direction, brightness changes, when changes occur |
| Cuts | Cut positions and the subject/composition before and after each cut |
| Audio | Whether to inherit dialogue, music, ambience, or action SFX |

```
@Video 1 is a coarse blockout reference. It provides only <motion paths, subject blocking, camera
position, camera movement, cuts, lighting changes, sound rhythm, or spatial relationships>.
Do not use its blockout appearance, materials, or scene.
<Blockout Subject A> in @Video 1 corresponds to <Subject A>.
@Image 1 defines <Subject A>'s <appearance, clothing, or structure>.

<Subject> completes <primary action or event> in <scene>.
Keep <motion path, blocking, camera movement, cuts, lighting, or sound rhythm> from @Video 1.
The final video uses <characters, scene, materials, and visual style>. Audio includes <dialogue,
ambience, or action sound effects>.
```

**Fine blockout** — already contains complete structures. Keep it clean: remove
path lines, coordinate axes, controllers, camera frustums.

```
@Video 1 is a fine blockout reference. Preserve <subject structure, action, spatial layout, camera
position, camera movement, and cuts>. Do not use its original gray materials or empty background.
@Image 1 defines <subject>'s <character appearance, material, color, or surface details>.
@Image 2 defines <scene>'s <space, materials, lighting, or visual style>.

Re-render <subject> from @Video 1 as <final subject>, and re-render the scene as <final scene>.
Keep <structure, action, camera treatment, and spatial relationships> from @Video 1.
Use <materials, colors, and style>. Audio includes <ambience, sound effects, or music>.
```

> Prefer simple geometry with clear relationships. Arms, wings, and other
> appendages should be used only when the action sequence is complete;
> otherwise they may cause stiff motion or structural misinterpretation.

## One-click video

Organize multiple images, or images plus a style-reference video, into a
complete paced video.

> **Material Roles → Image Order → Motion Amount → Editing Style → Visual Treatment → Audio**

Do **not** write only "turn these materials into a video."

```
[Material Roles]
@Image 1 is used for <character, product, scene, or opening image>.
@Image 2 is used for <character, product, scene, or process image>.
@Image 3 is used for <character, product, scene, or ending image>.
@Video 1 is used only for <editing rhythm, transitions, subtitle treatment, or music style>.
Do not use its character identities or scene (optional).

[Arrangement]
Show the images in <upload order, a specified order, or a model-selected thematic order>.
<State the character, product, location, and event relationships that must remain consistent>.

[Image Motion]
Apply <subtle live motion, parallax, push-in/pull-out, lateral movement, or local action> to each
image. Keep <subject appearance, product structure, text, or background relationships> stable.

[Final Style]
Use <editing rhythm, transition style, subtitle or graphic treatment, and color style>.

[Audio]
Include <dialogue, ambience, sound effects, or music>.
```

## Seamless video transitions

Generate continuous bridge content between two videos.

> **Before Video → After Video → Trigger Action → Camera Movement → Visual Transformation → Arrival State → Audio**

| Transition Method | What to Specify |
|---|---|
| Dive or reverse movement | Camera direction, speed change, when next scene begins |
| Character rotation | Pose, rotation direction, how clothing/background changes |
| Foreground occlusion | When foreground fills frame and composition that follows |
| Object morph | Corresponding shapes, materials, transformation process |
| Push/pull or focus change | Camera movement, focus target, continuous spatial relationship |

```
@Video 1 is the before-transition clip. Use its <ending subject, action, composition, camera
direction, and audio>.
@Video 2 is the after-transition clip. Use its <opening subject, composition, camera direction,
and audio>.
Keep <character identity, product structure, scene, and primary action> stable in the original
portions of @Video 1 and @Video 2.

At the end of @Video 1, <subject or foreground object> triggers the transition through <action>.
The camera <movement direction and speed change>, while <shape, material, light, or space>
gradually transforms into <corresponding element> at the start of @Video 2.
The transition ends naturally at @Video 2's opening composition, preserving continuity in
<subject position, camera direction, and motion trend>.
Audio transitions smoothly from <before audio> to <after audio>.
```

> The goal is visual and audio continuity. A generated bridge is **not** a
> pixel-identical edit splice.

## Emotional direction

Emotion words communicate a direction but leave performance open to
interpretation. For stable control, add **directly visible or audible cues**:
eye movement, brow tension, mouth movement, breathing, gaze direction, hand
movement.

> For a single emotional transition, **2–4 clear cues** are usually enough.
> Use event-triggered stages only when emotion changes several times.

### Single emotional transition

```
The overall emotion shifts from <starting emotion> to <ending emotion>.
After <triggering event>, <subject> first shows <immediate observable reaction>.
Then, <eyes, brows, mouth, breathing, gaze, or hand movement> gradually <changes>.
Finally, <subject> expresses <target emotion> through <restrained or explicit outward behavior>.
```

### Multi-stage emotion

```
When <subject> hears or sees <first triggering event>, <first observable reaction>.
When <second triggering event> occurs, <change in expression, gaze, or breathing>.
After confirming <critical information>, the emotion that <subject> tries to restrain or conceal
gradually becomes visible through <observable behavior>.
Finally, <subject's final action, expression, or manner of speaking>.
```

### Emotion externalization reference

| Abstract emotion | Externalize as |
|---|---|
| Sadness | lowering the head, shoulders trembling slightly, eyes reddening, fingers unconsciously clutching clothing, tears welling but not falling |
| Joy | corners of the mouth rising uncontrollably, brows relaxing, steps becoming light, unconsciously humming, spinning in place |
| Nervousness / anxiety | frequently checking watch, fingers tapping tabletop, rapid breathing, eyes darting, unconsciously biting fingernails |
| Anger | both fists clenched, jawline tense, chest heaving, eyes sharp, squeezing words through gritted teeth |
| Relief | long exhale, tense shoulders relaxing completely, a faint smile appearing, looking up toward the distance |

## Camera language

### Basic terms

| Type | Common Terms |
|---|---|
| Shot size | extreme wide shot, wide shot, medium shot, close-up, extreme close-up |
| Camera movement | push in, pull out, pan, lateral move, follow shot, orbit, dive, dolly out, tilt up, handheld shake |
| Camera position and viewpoint | low angle, overhead view, first-person view |

### Popular techniques

These can be used directly. If the frame has several subjects, still state
**which subject** the camera follows, **where** the movement begins, and
**where** it ends.

| Technique | What to Specify |
|---|---|
| One-take shot | Subjects, spaces, and events the camera passes through in order |
| Dolly zoom | Subject size to preserve; whether background moves closer or farther |
| Aerial view | Viewing height, movement direction, environmental area to reveal |
| FPV | First-person flight/traversal path, speed, turns |
| Bullet time | Action to freeze/slow down; camera orbit direction |
| Handheld camera | Subject being followed; amount of shake |
| Bounce speed ramp | Where action accelerates, decelerates, or rebounds; final resting state |

### Uncommon cinematography terms

For niche or potentially unrecognized terms:

> **Cinematography Term + Target Subject + Visual Change + Foreground/Background Relationship + Direction or Speed**

```
Rack focus: shift focus smoothly from the leaves in the foreground to the person in the
background. The leaves gradually blur while the person's face changes from soft to sharp.
```

For a precise transition, also state the **trigger time**, **occluding object**,
**camera direction**, **transition method**, and the **composition or motion
trend** that should continue afterward.

Additional cinematography examples:

```
Shallow depth of field: keep <Pastry Chef>'s eyes and face sharp while the glass jars and lights
in the background become soft, circular bokeh.

Tracking shot: move horizontally at the same speed as <Skateboarder>, keeping the subject sharp
while the roadside wall forms horizontal motion blur from right to left.

Golden hour: warm, low-angle sunlight enters from behind and to the left of <Hiker>, casting
long shadows across the mountain ridge.

Natural vignette: darken the four corners gradually while keeping the brightness and skin tone of
<Pianist> in the center natural, without a black border.

Whip-pan transition: at 5 seconds, move the camera rapidly to the left. Cut when the foreground
bookshelf fully covers the frame, then continue moving left at a similar speed in the next scene.
```

> Aperture, focal length, and shutter values can be included, but the intended
> **visible result** is usually clearer than a numeric value alone.

## Spatial continuity

For movement-heavy scenes, define a spatial continuity contract before writing
shots or stages:

```text
Spatial continuity:
Start: [subject positions and orientation]
Travel axis: [origin → boundary or waypoint → destination]
Subject order: [who leads, follows, blocks, or remains stationary]
Boundary behavior: [who crosses, stops, lands, exits, or disappears]
End: [final subject positions and travel direction]
Forbidden transitions: [reversal, position swap, offshore approach, pursuer crossing ahead, etc.]
```

Use physical locations and ordered states rather than relative verbs alone.
"Enter the beach" can be ambiguous; "forest interior → inland tree line → white
sand → along the shoreline" defines a testable trajectory. When screen direction
matters, state it explicitly and keep it consistent across cuts.

Every cut can reset relationships. Repeat critical invariants — lead/pursuer
order, travel direction, boundary state, and absences — in every shot or stage
where they matter. Describe the positive physical state first, then add the most
important exclusion.

## Revision contract

When revising an existing take, record the creative delta before rewriting:

```text
Locked decisions:
- [approved identity, action, camera, environment, audio, and boundary behavior]

Requested delta:
- [the one behavior that must change]

Acceptance criteria:
- [observable conditions that make the next take pass]

Known rejections:
- [behaviors from earlier takes that must not return]
```

Carry locked decisions into the revised prompt. Change one of prompt wording,
reference bundle, or motion design at a time when practical so the cause of
improvement or regression remains identifiable.

## Preflight review

Before generation, verify:

1. **Subject & action**: Does the prompt clearly state the subject and primary action?
2. **Reference roles**: Does every reference state what to use and what not to use?
3. **Subject binding**: Is every distinct character, product, and prop named and bound to a reference?
4. **Scene selection**: Are references selected by scene, not forced to appear all at once?
5. **Stage structure**: Does each stage contain only one primary change and a clear end state?
6. **Consistency**: Do character count, clothing, prop ownership, and spatial relationships stay consistent?
7. **Editing master**: For editing, is the sole editing master, edit scope, target quantity, and content to preserve defined?
8. **Emotion & camera**: Are abstract emotions and cinematography terms paired with visible/audible cues?
9. **First/last frames**: Are first/last frames assigned one role per image? Do first and last share aspect ratio?
10. **Storyboards & blockouts**: Does the storyboard state which structure to inherit? For blockouts, is coarse vs fine identified?
11. **Auto-lock rules**: Do editing, first/last-frame, and extension follow their locked aspect-ratio and duration rules?
12. **Extension boundary**: For extension, are the boundary image, motion trend, and audio continuity checked?
13. **One-click video**: Are material roles, image order, motion amount, editing style, and audio defined?
14. **Seamless transitions**: Are the two videos' roles, trigger action, transition process, and arrival state defined?

## Usage limitations

- Timestamps allocate time to events; they are **not frame-accurate edit points**.
- Video-editing prompts improve the probability of alignment but cannot guarantee frame-by-frame overlap.
- Multi-reference goal is to select and combine correct materials, **not** to make every material appear at once.
- For subtitles, formulas, signs, product specs, or frame-level timing that must be completely accurate, use prepared reference materials, video generation, and post-production together.
- Video editing locks input aspect ratio and approximate duration (±0.3s); neither can be set separately.
- First/last-frame generation locks aspect ratio to the first image; duration can be set. Mismatched ratios may stretch the last frame.
- Video extension locks input aspect ratio; extension duration can be set.
- For one-click video, specify image order and character mapping explicitly if they matter.
- Seamless transitions aim for visual/audio continuity; they do not guarantee pixel-identical preservation.

## Full example: T2V 30-second one-take

```
One-take handheld gimbal tracking shot. The camera slowly pushes in through a gap in a heavy red
curtain and enters a warm-toned backstage dressing room. A young female singer, with her back to
the camera, is adjusting her earpiece as a staff member reminds her it's time to go on. She turns
toward the camera and starts singing citypop. The camera pulls back and tracks her as she passes
through the curtain into a dim backstage corridor, interacting naturally with her dancers along
the way; one staff member hands her a microphone. She and the dancers then step onto the stage,
and the camera arcs around to the back, gradually revealing the red-and-black stage design, LED
screens, spotlights, haze, and reflective floor. The camera finally pulls out to a wide shot of
the arena, showing the packed audience, light boards, glow sticks, and cheering crowd.
```

## Full example: R2V multi-reference concert

```
A 30-second concert sequence in 16:9 landscape, with cinematic realism, authentic concert hall
lighting and shadows, warm golden stage lighting, and the atmosphere of a formal classical concert.

Use @Image 1 for the venue.
Reference @Image 2 for the pianist.
Reference @Image 3 for the cello.
Reference @Image 4 for the violin.
The lead vocalist must strictly follow @Image 5.
Reference @Images 6 to 10 for the rest of the orchestra.
Reference @Images 11 to 14 for the choir.
Reference @Images 15 to 18 for the audience seating.

The lead vocalist walks from center stage toward the front edge. The pianist is positioned by the
piano. The orchestra is arranged on both sides and toward the rear. The choir stands at the back
of the stage.

Open with a high-angle wide shot of the full concert hall. The pianist strikes the keys, and the
lead vocalist steps into the spotlight and begins singing. The camera naturally moves across the
violin, cello, and orchestra as they perform together, with the violin feeling bright and the
cello warm. In the latter part, the choir joins in. The lead vocalist briefly makes eye contact
with front-row audience members, who respond with a smile and a slight nod. In the closing shot,
the camera pulls back. The singing ends, and the audience joins in the applause.
```

## Full example: Video editing — subject replacement

```
[Edit Goal]
Edit @Video 1. Replace only the yellow folding desk lamp with the white folding desk lamp in @Image 1.

[Source Video Role]
@Video 1 is the sole editing master. It defines the desk, books, hand movements, camera position,
camera movement, occlusion relationships, and event order.

[Target Reference Role]
@Image 1 defines only the white folding desk lamp's appearance, structure, and material. Do not use
the image's background, composition, or other objects.

[Edit Scope]
Keep exactly one white folding desk lamp throughout the video. Replace only the original yellow
folding desk lamp. Do not modify the books, desk, hands, or background.

[Timeline Inheritance]
The white folding desk lamp inherits every appearance, lamp-arm rotation, hand occlusion, and exit
of the original yellow folding desk lamp, including timing, path, and speed changes.
Except for the object or area explicitly modified above, keep all other people, props, scene
content, camera movements, cuts, and event order from @Video 1 unchanged.
```

## Quick reference card

### Model IDs

| Variant | Model ID |
|---|---|
| Seedance 2.5 | `dreamina-seedance-2-5-260628` |
| Seedance 2.0 Standard (legacy) | `dreamina-seedance-2-0-260128` |
| Seedance 2.0 Fast (legacy) | `dreamina-seedance-2-0-fast-260128` |
| Seedance 2.0 Mini (legacy) | `dreamina-seedance-2-0-mini-260615` |

**MCP tools:** `seedance_2_5_create_task` (submit), `seedance_2_5_get_task` (poll), `seedance_list_tasks` / `seedance_cancel_or_delete_task` (shared with 2.0).

> The model ID `dreamina-seedance-2-5-260628` is live on BytePlus ModelArk. Confirm the current ID on the [Model list](https://docs.byteplus.com/en/docs/ModelArk/1330310) before making API calls.

### Reference limits

| Material | Max | Recommended |
|---|---|---|
| Images | 30 (each ≤ 4K) | 1–8 subjects |
| Videos | 10 (combined ≤ 30s) | 1–5 subjects, 5–10s each |
| Audio | 10 (combined ≤ 30s) | Only what's directly relevant |
| **Total** | **50** | — |

### Audio syntax

| Content | Syntax |
|---|---|
| Music | `()` |
| Sound Effects | `<>` |
| Dialogue | `{}` |
| Subtitles | `【】` |

### Parameter auto-lock summary

| Task | Aspect Ratio | Duration |
|---|---|---|
| Video editing | Locked to input | Locked to ~input (±0.3s) |
| First/last-frame | Locked to first image | Settable |
| Video extension | Locked to input | Settable |

### Camera techniques

| Technique | What to Specify |
|---|---|
| One-take shot | Subjects, spaces, events in order |
| Dolly zoom | Subject size; bg closer or farther |
| Aerial view | Height, direction, area to reveal |
| FPV | Flight path, speed, turns |
| Bullet time | Action to freeze; orbit direction |
| Handheld camera | Subject; amount of shake |
| Bounce speed ramp | Acceleration/deceleration points; final state |

### Reproducibility
- `seed`: pin once a look is approved to reproduce the same visual family.
- `camera_fixed`: set to `true` for locked-off shots.
- `return_last_frame`: set to `true` to chain multi-shot continuity.

### Output duration
- 4–30s per generation (up from 4–15s in 2.0).
- Output resolution: 480p, 720p, or 1080p. For 4K output, fall back to Seedance 2.0 (`dreamina-seedance-2-0-260128`) via `seedance-prompt-20`.
- Multi-round extensions up to 180s (beta).

### Cost ladder
- Prototype at lower resolution → finalize at target resolution.
- Video generation is billed per successful task completion.
- Confirm current billing rules on the [Pricing page](https://docs.byteplus.com/en/docs/ModelArk/1544106).

### When to use Seedance 2.0 instead of 2.5

Fall back to `seedance-prompt-20` and the 2.0 model (`dreamina-seedance-2-0-260128`) when:

- You need **4K output resolution** — 2.5 caps at 1080p.
- You need **Fast or Mini speed variants** — 2.5 has no Fast/Mini; 2.0 Fast/Mini are cheaper and faster for prototyping.
- You need the lowest possible cost per generation for quick iteration.

### Languages
- 10+ languages supported natively: Chinese, English, Spanish, Indonesian, Malay, Thai, Arabic, Portuguese, Vietnamese, Japanese, Korean.
- For non-Chinese dialogue, use the dialogue language reinforcement formula.
- For **Tagalog/Filipino or Taglish** (not in the supported list), use the partner skill `seedance-prompt-25-filipino` for pronunciation, intonation, and audio-first pipeline guidance.

### Consistency rules
- Lock character sheets, prop sheets, and scene sheets with Seedream before spending video credits.
- Storyboarding is optional. Generate storyboard panels from approved assets when composition must be reviewed before motion; otherwise generate video directly from canonical Element references (R2V) or text-to-video.
- Reuse the same reference bundle across every shot in a scene.
- Preserve a written locked-decisions and requested-delta record for every retry.
- Change only one of {prompt wording, reference bundle, motion design} per retry when practical.

### Storyboard-to-video handoff

Storyboards are optional. Use a storyboard panel as a derivative composition
and continuity anchor when composition must be reviewed before motion;
otherwise generate video directly from canonical Element references (R2V)
or text-to-video. Character, location, and prop sheets remain the source of
truth. Require explicit approval before using a panel as a video input.

| Need | Mode | Reference rule |
|---|---|---|
| Reproduce the exact approved opening frame | First-frame | Submit only the promoted panel |
| Lock approved start and end states | First + last frame | Submit only the two promoted panels |
| Preserve explicit references while following storyboard composition | R2V | Submit the approved panel and canonical asset set as separate indexed references |
| Generate video without a storyboard | R2V or T2V | Submit canonical Element references only (R2V) or text-only prompt (T2V) |

For R2V, index the panel and canonical assets separately:

```text
@Image 1: approved storyboard panel — composition, blocking, lighting, and visible state
@Image 2: approved character sheet — identity and wardrobe only
@Image 3: approved location sheet — geometry and production design only
@Image 4: approved prop sheet — shape, materials, and markings only
```

These modes are mutually exclusive. Do not combine first/last-frame roles with
an R2V bundle unless the live model explicitly confirms that combination. Record
the chosen mode, ordered reference roles, paths, hashes, selected variants, and
approval states in the shot manifest before submission.

## Guide disclaimer

The examples in this skill illustrate prompt-writing techniques only. Actual
generation results may vary depending on the input materials, task complexity,
and generation parameters.
