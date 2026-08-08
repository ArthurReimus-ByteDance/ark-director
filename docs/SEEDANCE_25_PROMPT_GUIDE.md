# Seedance 2.5 Prompt Guide — Key Points & Best Practices

> **Source**: [Dreamina Seedance 2.5 Prompt Guide](https://bytedance.larkoffice.com/docx/A88jd0B47oAd8zxWp5ycZFMfnxh) (Lark doc, revision 117)
> **Supplementary**: [Seedance 2.5 Launch Blog](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
> **Created**: 2026-08-03

---

## Table of Contents

1. [Model Overview](#1-model-overview)
2. [Core Prompt Formula](#2-core-prompt-formula)
3. [Reference Materials](#3-reference-materials)
4. [Special Audio & Text Syntax](#4-special-audio--text-syntax)
5. [Multi-Reference Workflow (5 Steps)](#5-multi-reference-workflow-5-steps)
6. [30-Second Video Staging](#6-30-second-video-staging)
7. [Timestamps & Pacing Control](#7-timestamps--pacing-control)
8. [Parameter Auto-Lock Rules](#8-parameter-auto-lock-rules)
9. [Video Editing](#9-video-editing)
10. [Video Extension](#10-video-extension)
11. [Keyframes, Storyboards & Blockouts](#11-keyframes-storyboards--blockouts)
12. [One-Click Video](#12-one-click-video)
13. [Seamless Video Transitions](#13-seamless-video-transitions)
14. [Emotional Direction](#14-emotional-direction)
15. [Camera Language](#15-camera-language)
16. [Pre-Submission Checklist](#16-pre-submission-checklist)
17. [Usage Limitations](#17-usage-limitations)
18. [Best Practices Summary](#18-best-practices-summary)

---

## 1. Model Overview

| Spec | Value |
|---|---|
| **Max duration per generation** | 30 seconds (up from 15s in 2.0) |
| **Multi-round extensions** | Up to 180 seconds (beta) |
| **Max images** | 30 (each ≤ 4K) |
| **Max videos** | 10 (combined ≤ 30s) |
| **Max audio** | 10 (combined ≤ 30s) |
| **Total references** | 50 |
| **Languages** | 10+ (native support) |
| **Native audio** | Yes — co-generated with video in one pass |
| **API status** | "Coming soon" on BytePlus ModelArk; live on Jimeng AI / Doubao Pro |

**Four major advances over 2.0:**
1. **Wider narrative canvas** — 30s native + high-fidelity temporal extension
2. **Expanded omni-modal referencing** — up to 50 references, higher fidelity for 3D blockouts, product packaging, brand identity
3. **Precise video editing** — localized editing (background, product, person swaps), timestamp-level control
4. **10+ languages & stronger instruction following** — complex camera choreography, emotional turns, layered scene descriptions

---

## 2. Core Prompt Formula

> **Subject + Action or Event + Scene and Environment (optional) + Visual Style (optional) + Camera Movement/Cut (optional) + Audio (optional)**

- **Only Subject + Action is required.** All other parts are optional — omit what you don't need.
- Summarize the main action first; add detail only to critical movements.
- **Do not describe the same action twice.**
- Generation parameters (duration, resolution, aspect ratio) belong in the generation interface or API — **not in the prompt**.

### Basic Template

```text
<Subject> performs <primary action or event> in <scene and environment>.
The visuals feature <visual style>.
Use <shot size, camera angle, camera movement, or cuts>.
Audio includes <dialogue, ambience, sound effects, or music>.
```

### Example

```text
A ceramic artist finishes a pale blue cup in a studio at dawn, lifts it from the wheel,
and places it in the center of a wooden shelf.
Soft morning light enters through the window. The wet clay has a delicate sheen, and the
workbench remains tidy.
Begin with a medium shot of the wheel-throwing process, slowly push in toward the cup's
surface texture, then cut to a frontal view of the shelf.
Retain the low hum of the pottery wheel, the friction of clay, and subtle indoor ambience.
```

---

## 3. Reference Materials

### 3.1 Limits & Recommended Ranges

| Material Type | Input Limit | Recommended Range |
|---|---|---|
| **Images** | Up to 30, each ≤ 4K | Prefer 1–8 distinct subjects |
| **Videos** | Up to 10, combined ≤ 30s | Prefer 1–5 subjects, 5–10s each |
| **Audio** | Up to 10, combined ≤ 30s | Keep only directly relevant dialogue/voice/ambience/music |
| **Video Editing** | Source video + reference images | Source < 20s, 1–5 reference images |

- You can push beyond recommended ranges (9–12 subjects in images, 6–10 in audio/video, 6–8 editing refs), but **stability decreases** as count grows.
- If >5 subjects need multiple views, use **separate images per view** — independent view images are more stable than collages.

### 3.2 Define Each Material's Role

**Three non-negotiable rules:**
1. Put the material mapping **directly in the prompt** — do not rely on text labels inside images.
2. **Never make the model guess** which asset belongs to which person, prop, or scene.
3. Add exclusions ("Do not use...") **only when** a person, background, or composition could unintentionally leak into the output.

### Role Definition Template

```text
@Image 1 defines <subject>'s <appearance, clothing, structure, or material>.
@Video 1 defines <motion, camera movement, or pacing>.
@Audio 1 defines <character or sound type>'s <voice, dialogue, ambience, or music>.

<Subject> completes <primary action or event> in <scene>.
The visuals feature <visual style>, with <camera treatment>.
```

### Role Definition Example

```text
@Image 1 defines the ceramic artist's facial features, hairstyle, and dark green apron. Do not use the image background.
@Image 2 defines the wooden workbench, window placement, and morning light of the pottery studio. Do not use the people in the image.
@Video 1 defines the pacing of throwing clay with both hands, lifting the cup, and placing it down. Do not use the person's identity, clothing, or scene from the video.

The ceramic artist finishes a pale blue cup in the pottery studio at dawn, lifts it from the wheel,
and places it in the center of a wooden shelf.
Begin with a medium shot of the wheel-throwing process, then slowly push in toward the cup's surface texture.
Retain the sound of the wheel, the friction of clay, and indoor ambience.
```

### 3.3 Multiple Views of the Same Subject

When several images show different angles of one person or product, **state this explicitly**:

```text
@Image 1 defines the front view of the same folding desk lamp.
@Image 2 defines the left-side structure of the same folding desk lamp.
@Image 3 defines the right-side structure of the same folding desk lamp.
@Image 4 defines the rear structure of the same folding desk lamp.
All four images define one folding desk lamp. The output must contain only one lamp throughout.
```

### 3.4 Inheritance from Reference Videos

- If a reference video already defines the motion, camera movement, and sequence accurately, **state only which attributes to inherit** — do not restate every action.
- Repeating the motion description may **conflict with the reference itself**.
- A blockout video mainly provides motion and spatial structure — the prompt must **still define** the intended subjects, scene, action, and visual style.

---

## 4. Special Audio & Text Syntax

Prompts can be written entirely in natural language. When you need to distinguish music, SFX, dialogue, and subtitles explicitly, use these brackets:

| Content | Syntax | Example |
|---|---|---|
| **Music** | `()` | `(Soft, rhythmic piano music plays in the background)` |
| **Sound Effects** | `<>` | `<A bell rings in the distance>` |
| **Dialogue** | `{}` | `{Hello, welcome back.}` |
| **Subtitles** | `【】` | `【Chapter One: Departure】` |

### Dialogue Language Reinforcement

When dialogue is **not in Chinese**, specify the language before the line:

```text
The girl says softly in Japanese: {もう大丈夫です}
```

For regional accents or to prevent language mixing, use this formula:

> **Dialogue Language + Regional Variety or Accent + Delivery Style + Speaker + {Dialogue}**

```text
Dialogue language: American English. The girl says in natural, conversational American English: {I thought you weren't coming.}

Dialogue language: authentic Los Angeles English. The young man says in natural Los Angeles vernacular: {No way, you actually made it.}
```

### Direct Audio Controls

```text
No background music. Keep only the characters' dialogue, ambience, and action sound effects.
No subtitles.
No audio at all.
```

---

## 5. Multi-Reference Workflow (5 Steps)

When working with many reference materials, the goal is **not** to put every reference into one sentence. The goal is to **define relationships** among characters, props, scenes, actions, and audio, and help the model select the correct materials for each scene.

> **Define Each Material's Role → Map Subjects → Group by Type → Create Subject Profiles → Select References by Scene**

### Step 1: Name and Map Each Subject Individually

Bind each person, product, and prop to its reference material **separately**:

```text
<Character A> corresponds to @Image 1. Use only the appearance, hairstyle, and clothing.
<Character B> corresponds to @Image 2. Use only the appearance, hairstyle, and clothing.
<Prop A> corresponds to @Image 3. Use only the structure, material, and color.
<Scene A> references @Image 4. Use only the spatial layout, architecture, and lighting. Do not use the people in the image.
```

> **Bad**: `"@Images 1 through 4 define four characters respectively."` — This never says which image maps to which character.

### Step 2: Group Materials by Type

Sort larger asset sets into typed groups:

```text
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

### Step 3: Create a Centralized Profile for Important Subjects

When the same character uses several references across multiple scenes, build a single consolidated profile:

```text
[Subject Profile: Conservator]
Appearance and clothing: @Image 1.
Fixed prop: <Sample Case> from @Image 5.
Locations: <Conservation Lab> and <Gallery>.
Motion references: the case-opening motion from @Video 1 and the sample-placement motion from @Video 2.
Do not use: other characters' clothing. Do not give this character <Record Board> or guide equipment.
```

### Step 4: Select References by Scene

Each scene names **only** the assets it uses, the event that occurs, and the required end state:

```text
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

> **Key principle**: The goal is to help the model select the correct materials for the current scene, **not** to make every material appear at the same time.

---

## 6. 30-Second Video Staging

When a video contains several events, divide the story into **consecutive stages**. Give each stage:
- **Only one primary state change**
- **A clear end state** (what should be directly visible at the end)

### Long-Video Template

```text
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

### Example: Flower Shop Order-Packing

```text
[Generation Goal]
Generate an instructional video showing a flower shop's order-packing process. <Florist> and
<Store Assistant> arrange, wrap, and hand off a bouquet together.

[Stage 1]
Initial state: <Florist> stands behind the workbench. Loose flower stems, scissors, and wrapping
paper lie on the tabletop.
Primary event: <Florist> arranges the stems and trims them to length.
End state: <Florist> holds the bouquet in the left hand, and the scissors are back on the right
side of the workbench.

[Stage 2]
Continue from the previous stage: both characters retain the same identities and clothing, and
<Florist> still holds the bouquet.
Primary event: <Store Assistant> unfolds the wrapping paper. <Florist> places the bouquet inside
and ties it with a green ribbon.
End state: the wrapped bouquet lies flat in the center of the workbench, with the ribbon bow
facing the camera.

[Stage 3]
Primary event: <Store Assistant> picks up the bouquet and places it on the pickup shelf.
End state: the bouquet is centered on the pickup shelf, and both characters stand behind the
workbench inspecting the finished order.

[Maintain Consistency]
Keep <Florist> and <Store Assistant>'s identities, clothing, workbench orientation, scissors
position, and bouquet ownership consistent.
```

---

## 7. Timestamps & Pacing Control

- **Use stages by default.** Use one-second precision **only** when you need to control a critical handoff, entrance/exit, transition, or explicit beat.
- Three timing patterns:

| Pattern | Example |
|---|---|
| **Time range** | `0-3 seconds... 3-7 seconds... 7-12 seconds...` |
| **Exact time point** | `At 5 seconds, the camera whip-pans rapidly to the left and completes the transition.` |
| **Relative timing** | `Three seconds after the character presses the button, the room lights gradually turn off.` |

### Rules

- Time ranges should be **consecutive and non-overlapping**.
- They represent an event's **time budget**, not a precise edit point — actions may occur slightly before or after a boundary.
- **Too little content** in a range gives the model too much freedom.
- **Too much content** can cause excessive cutting or omitted events.
- **Do not** use timestamps to demand impossible frequencies (e.g., "complete three actions in one second").

---

## 8. Parameter Auto-Lock Rules

Three task types automatically lock generation parameters based on input materials:

| Task Type | Aspect Ratio | Duration |
|---|---|---|
| **Video editing** | Locked to input video's ratio; **cannot be set separately** | Locked to ~input duration (±0.3s); **cannot be set separately** |
| **First/last-frame generation** | Locked to **first image's ratio**. First & last images must share the same ratio to avoid stretching | Can be set freely |
| **Video extension** | Locked to input video's ratio; **cannot be set separately** | Can be set freely |

> Parameters automatically locked for these tasks **cannot** be overridden on the generation page or through the API.

---

## 9. Video Editing

When editing an existing video:
1. Define the source video as the **sole editing master**.
2. Specify the **edit target**, **edit scope**, **target material**, and **content to preserve**.

The output automatically preserves the input video's aspect ratio and approximately preserves its duration (±0.3s from transition-frame handling).

### 9.1 General Editing Pattern

```text
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

### 9.2 Subject Replacement with Timeline Inheritance

The new object **inherits every appearance, motion, occlusion, and exit** of the original object, including timing, duration, path, and speed changes.

```text
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

### 9.3 Background Replacement

Swap the background while preserving the subject's silhouette, identity, motion, and occlusion relationships.

```text
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
Keep the character actions and occlusion relationships from @Video 1. Except for the object or
area explicitly modified above, keep all other people, props, scene content, camera movements,
cuts, and event order from @Video 1 unchanged.
```

### 9.4 Audio Editing

Dialogue, language, voice, background music, and sound effects can be edited **separately** from visuals.

```text
Edit @Video 1. Remove only the original background music. Keep the character dialogue, lip sync,
ambience, and action sound effects; preserve the visuals, camera treatment, and editing rhythm
from @Video 1.

Edit @Video 1. Change <Presenter>'s spoken language to natural American English while preserving
the dialogue content and speaking times. Keep all other character voices, background music,
ambience, and visuals from @Video 1.
```

---

## 10. Video Extension

Video extension creates content beyond the boundary of a source video.
- **Forward extension**: extension's first frame continues from the source video's last frame.
- **Backward extension**: extension's last frame connects to the source video's first frame.

### 10.1 Forward Extension (Basic)

```text
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

### 10.2 Forward Extension (With Additional References)

Define the role of every additional material first, then state that the source video controls the extension boundary. New materials may supplement characters, props, or audio, but **must not override** the source video's last-frame control over the extension's opening image.

```text
@Image 1 defines <Character A>'s facial features.
@Image 2 defines <Character A>'s clothing.
@Image 3 defines <key prop>'s structure and material.
@Video 1 is the source video to extend forward.

Extend @Video 1 forward. The first frame of the extended segment directly continues from the last
frame of @Video 1. Maintain continuity in <boundary-frame state>.

Then, <Character A uses the key prop to complete a new action or event>.

Throughout the extension, maintain continuity in <character identity and clothing>, <key prop>,
<background layout>, and <axis of action>.
Keep each subject as the same continuous instance throughout: do not duplicate or split it, and
keep the person's appearance or the object's number of parts stable.
```

### 10.3 Backward Extension (Basic)

Describe what happens **before** the source video begins, then define the source video's first frame as the **explicit end state** of the extended segment.

> Writing only "then connect to the source video" is **not enough**. It can let characters or effects enter too early, or cause the image to change again after reaching the target state.

```text
@Video 1 is the source video to extend backward.

Extend @Video 1 backward. Before the source video begins, <describe the preceding action, event,
camera treatment, or audio>.

The last frame of the extended segment naturally connects to the first frame of @Video 1:
<subject pose and orientation>, <prop position>, and <background and spatial relationships>.
Match the <camera position and composition>, <lighting>, and <motion direction> of @Video 1's
first frame.

Throughout the extension, maintain continuity in <character identity and clothing>, <key props>,
<background layout>, and <axis of action>.
Keep each subject as the same continuous instance throughout: do not duplicate or split it, and
keep the person's appearance or the object's number of parts stable.
```

### 10.4 Backward Extension (With Additional References)

Define each material's role, and state which materials are used in the backward extension and which should appear **only after** the source video begins. This reduces the chance that later characters, props, or effects enter the preceding segment too early.

```text
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

Keep each subject as the same continuous instance throughout: do not duplicate or split it, and
keep the person's appearance or the object's number of parts stable.
<Materials that should appear only after the source video begins> must not appear early in the
backward extension.
```

### 10.5 Boundary Frame Note

Boundary frames should connect naturally at a visual level; this does **not** mean they will be pixel-identical. During review, inspect both sides of the boundary and the complete extended segment.

---

## 11. Keyframes, Storyboards & Blockouts

### 11.1 First and Last Frames with Additional References

In multimodal reference mode, state in the first line that `@Image 1 is the first frame` and `@Image 2 is the last frame`. **No separate mode switch needed.** The system locks the output aspect ratio to the first image.

- First and last images **should use the same aspect ratio** — mismatched ratios may stretch the last frame.
- Additional images can still define characters, props, scenes, and materials.
- Describe each anchor image **separately** — do not combine into one sentence like "@Images 1 and 2 are the first and last frames."
- Other references should supplement **only** their specified attributes and **must not** replace the first- or last-frame composition.

```text
@Image 1 is the first frame. It defines the opening composition, subject position, pose, prop
state, scene, and camera direction.
@Image 2 is the last frame. It defines the ending composition, subject position, pose, prop
state, scene, and camera direction.
@Image 3 defines <Subject A>'s <appearance, clothing, structure, or material>. Do not change
the first-frame composition defined by @Image 1 or the last-frame composition defined by @Image 2.
@Image 4 defines <specified attributes> of <Subject B, prop, or scene>. Do not change the
first-frame composition defined by @Image 1 or the last-frame composition defined by @Image 2.

<Describe one continuous action or event>.
The video begins naturally from the first frame defined by @Image 1 and reaches the last frame
defined by @Image 2 after the continuous action.
Between the first and last frames, maintain continuity in <character identity, prop structure
and ownership, scene layout, and camera direction>.
```

### 11.2 Multi-Keyframe Sequence Control

When separate images define different stages of a process:

```text
Use @Image 1 through @Image N as keyframes in this order.

@Image 1 is the first frame. It defines <opening composition, subject position, pose, prop
state, and camera direction>.
@Image 2 defines the second keyframe: <visible end state of Stage 1>.
@Image 3 defines the third keyframe: <visible end state of Stage 2>.
@Image N is the last frame. It defines <ending composition, subject position, pose, prop
state, and camera direction>.

The video passes through the states defined by @Image 1, @Image 2, @Image 3, and @Image N in
order, using continuous action to transition naturally between stages.
Maintain continuity in <subject identity, prop structure and ownership, scene layout, lighting,
and axis of action> throughout.
```

> Independent keyframe images are usually easier to align than several frames combined into one grid. They control stage order and key states; they do **not** reproduce every frame exactly.

### 11.3 Storyboard Grids

- A storyboard grid communicates overall story, shot order, and approximate compositions — **not strict reproduction** of every detail.
- **Prefer ≤ 15 panels.**
- Use clean line art or simple diagrams; minimize text labels.
- State the reading order, then describe each panel's subject action, shot size or camera movement, final visual style, and audio.

```text
@Image 1 provides an <N-panel storyboard grid> for shot order and approximate composition.
Read it <left to right, top to bottom>. Do not use the grid's <line-art style, text labels,
or placeholder characters>.
@Image 2 defines <Subject A>'s <appearance and clothing>.
@Image 3 defines <key prop or scene>'s <structure, material, or lighting>.

Shot 1: <shot size, subject action, and scene state>.
Shot 2: <shot size, subject action, camera movement, or transition>.
...
Shot N: <closing action and final visible state>.

The final video uses <visual style>. Audio includes <dialogue, ambience, action sound effects,
or music>.
```

### 11.4 Blockout References

Two categories — first determine whether the blockout controls a **motion skeleton** or a **complete model**:

| Type | Best For | Requirements | Prompt Focus |
|---|---|---|---|
| **Coarse blockout** | Simple geometry previewing action, paths, blocking, camera movement, or cuts | Clear relationships between shapes; complete action sequence; character/prop/scene images may be added | Map every blockout subject; state which temporal and spatial info to inherit |
| **Fine blockout** | Complete modeling needing new characters, materials, colors, scenes, or style | Complete, clean model; avoid path lines, coordinate axes, camera frustums | Preserve structure, action, and camera treatment; define attributes to re-render |

#### Coarse Blockout — What to State

| Blockout Info | What to State |
|---|---|
| Path | Action trajectory, motion direction, subject blocking, entrance/exit order |
| Camera movement | Camera position, path, direction, speed changes |
| Lighting | Light direction, brightness changes, when changes occur |
| Cuts | Cut positions and the subject/composition before and after each cut |
| Audio | Whether to inherit dialogue, music, ambience, or action SFX |

> Prefer simple geometry with clear relationships. Arms, wings, and other appendages should be used only when the action sequence is complete; otherwise they may cause stiff motion or structural misinterpretation.

#### Coarse Blockout Template

```text
@Video 1 is a coarse blockout reference. It provides only <motion paths, subject blocking,
camera position, camera movement, cuts, lighting changes, sound rhythm, or spatial relationships>.
Do not use its blockout appearance, materials, or scene.
<Blockout Subject A> in @Video 1 corresponds to <Subject A>.
<Blockout Subject B or geometric prop> in @Video 1 corresponds to <Subject B or key prop>.
@Image 1 defines <Subject A>'s <appearance, clothing, or structure>.
@Image 2 defines <specified attributes> of <Subject B, key prop, or scene>.

<Subject> completes <primary action or event> in <scene>.
Keep <motion path, blocking, camera movement, cuts, lighting, or sound rhythm> from @Video 1.
The final video uses <characters, scene, materials, and visual style>. Audio includes <dialogue,
ambience, or action sound effects>.
```

#### Fine Blockout Template

```text
@Video 1 is a fine blockout reference. Preserve <subject structure, action, spatial layout,
camera position, camera movement, and cuts>. Do not use its original gray materials or empty
background.
@Image 1 defines <subject>'s <character appearance, material, color, or surface details>.
@Image 2 defines <scene>'s <space, materials, lighting, or visual style>.

Re-render <subject> from @Video 1 as <final subject>, and re-render the scene as <final scene>.
Keep <structure, action, camera treatment, and spatial relationships> from @Video 1.
Use <materials, colors, and style>. Audio includes <ambience, sound effects, or music>.
```

---

## 12. One-Click Video

Designed to organize multiple images, or images plus a style-reference video, into a complete video with consistent pacing and visual packaging.

> **Material Roles → Image Order → Motion Amount → Editing Style → Visual Treatment → Audio**

> Do **not** write only "turn these materials into a video." State each material's role, image order, amount of motion, editing rhythm, visual treatment, and audio.

```text
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

> If image order matters, state the exact sequence. If the model may arrange freely, say it may organize by theme. When several characters or products appear, continue to name and bind each one separately.

---

## 13. Seamless Video Transitions

Generates continuous bridge content between two videos. Identify the before-transition and after-transition videos, then describe:

> **Before Video → After Video → Trigger Action → Camera Movement → Visual Transformation → Arrival State → Audio**

| Transition Method | What to Specify |
|---|---|
| Dive or reverse movement | Camera direction, speed change, when the next scene begins |
| Character rotation | Pose, rotation direction, how clothing or background changes continuously |
| Foreground occlusion | When the foreground object fills the frame and the composition that follows |
| Object morph | Corresponding shapes, materials, and the transformation process |
| Push/pull or focus change | Camera movement, focus target, continuous spatial relationship |

```text
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

> The goal is visual and audio continuity. A prompt may ask to preserve the primary content of both source videos, but a generated bridge is **not** a pixel-identical edit splice.

---

## 14. Emotional Direction

Emotion words ("tense," "warm," "oppressive") communicate a direction but leave performance open to interpretation. For more stable control, add **directly visible or audible cues**: eye movement, brow tension, mouth movement, breathing, gaze direction, hand movement.

> You do not need to list every facial detail. For a single emotional transition, **2–4 clear cues** are usually enough. Use event-triggered stages only when the emotion changes several times.

### 14.1 Single Emotional Transition

```text
The overall emotion shifts from <starting emotion> to <ending emotion>.
After <triggering event>, <subject> first shows <immediate observable reaction>.
Then, <eyes, brows, mouth, breathing, gaze, or hand movement> gradually <changes>.
Finally, <subject> expresses <target emotion> through <restrained or explicit outward behavior>.
```

### 14.2 Multi-Stage Emotion

```text
When <subject> hears or sees <first triggering event>, <first observable reaction>.
When <second triggering event> occurs, <change in expression, gaze, or breathing>.
After confirming <critical information>, the emotion that <subject> tries to restrain or conceal
gradually becomes visible through <observable behavior>.
Finally, <subject's final action, expression, or manner of speaking>.
```

### 14.3 Example

```text
Applause marking the end of the performance comes from behind the stage. The young actor's fingers
suddenly stop on the program, the gaze turns slowly toward the curtain, and the shoulders remain
tense.
After confirming that the curtain call is over, the actor exhales softly. The shoulders gradually
relax, a restrained smile appears, and the eyes slowly well with tears, but the actor never turns
to leave.
```

---

## 15. Camera Language

### 15.1 Basic Camera Language

| Type | Common Supported Terms |
|---|---|
| **Shot size** | extreme wide shot, wide shot, medium shot, close-up, extreme close-up |
| **Camera movement** | push in, pull out, pan, lateral move, follow shot, orbit, dive, dolly out, tilt up, handheld shake |
| **Camera position** | low angle, overhead view, first-person view |

### 15.2 Popular Camera Techniques

These can be used directly. If the frame contains several subjects, still state **which subject** the camera follows or revolves around, **where** the movement begins, and **where** it ends.

| Technique | What to Specify |
|---|---|
| **One-take shot** | The subjects, spaces, and events the continuous camera passes through in order |
| **Dolly zoom** | The subject size to preserve; whether the background appears to move closer or farther away |
| **Aerial view** | Viewing height, movement direction, and the environmental area to reveal |
| **FPV** | First-person flight or traversal path, speed, and turns |
| **Bullet time** | The action to freeze or slow down; the camera's orbit direction |
| **Handheld camera** | The subject being followed and the amount of shake |
| **Bounce speed ramp** | Where the action accelerates, decelerates, or rebounds; its final resting state |

### 15.3 Uncommon Cinematography Terms

For niche terms, terms with inconsistent industry usage, or terms the model may not recognize:

> **Cinematography Term + Target Subject + Visual Change + Foreground/Background Relationship + Direction or Speed**

```text
Rack focus: shift focus smoothly from the leaves in the foreground to the person in the
background. The leaves gradually blur while the person's face changes from soft to sharp.
```

For a precise transition, also state the **trigger time**, **occluding object**, **camera direction**, **transition method**, and the **composition or motion trend** that should continue afterward.

### 15.4 Cinematography Examples

```text
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

> Aperture, focal length, and shutter values can be included, but the intended **visible result** is usually clearer than a numeric value alone.

---

## 16. Pre-Submission Checklist

Before generating, verify:

1. **Subject & action**: Does the prompt clearly state the subject and primary action or event?
2. **Reference roles**: Does every reference material state what to use and what not to use?
3. **Subject binding**: Is every distinct character, product, and prop named and bound to a reference?
4. **Scene selection**: Are references selected by scene instead of being required to appear all at once?
5. **Stage structure**: Does each stage of a long video contain only one primary change and a clear end state?
6. **Consistency**: Do the number of characters, clothing, prop ownership, and spatial relationships remain consistent?
7. **Editing master**: For video editing, does the prompt define the sole editing master, edit scope, target quantity, and content to preserve?
8. **Emotion & camera**: Are abstract emotions and cinematography terms paired with directly visible or audible cues?
9. **First/last frames**: Are first/last frames and multiple keyframes assigned one role per image, and do the first and last images use the same aspect ratio?
10. **Storyboards & blockouts**: Does the storyboard state which structure to inherit? For blockouts, did you first identify whether the reference is coarse or fine and specify the temporal, structural, material, and style information to inherit?
11. **Auto-lock rules**: Do video editing, first/last-frame generation, and video extension follow their automatically locked aspect-ratio and duration rules?
12. **Extension boundary**: For video extension, did you check the boundary image, motion trend, and audio continuity?
13. **One-click video**: Does the prompt define material roles, image order, motion amount, editing style, and audio?
14. **Seamless transitions**: Does the prompt define the two videos' roles, trigger action, transition process, and arrival state?

---

## 17. Usage Limitations

- **Timestamps allocate time to events**; they are not frame-accurate edit points.
- **Video-editing prompts** can improve the probability that critical events align with the source video, but cannot guarantee frame-by-frame overlap.
- **Multi-reference creation** goal is to select and combine the correct materials, **not** to make every material appear at the same time.
- For **subtitles, formulas, signs, product specifications, or frame-level timing** that must be completely accurate, use prepared reference materials, video generation, and post-production together.
- **Video editing** automatically locks the input video's aspect ratio and approximate duration; neither can be set separately. Output may differ from input by up to ~0.3 seconds.
- **First-frame or first-and-last-frame generation** locks the aspect ratio to the first image; duration can be set. Mismatched first/last image ratios may stretch the last frame.
- **Video extension** locks the input video's aspect ratio; extension duration can be set. The extended segment's volume may differ slightly from the source video.
- For **one-click video**, if image order or character mapping matters, specify it explicitly in the prompt.
- **Seamless video transitions** aim for visual and audio continuity; they do not guarantee pixel-identical preservation of both source videos.

---

## 18. Best Practices Summary

### Do

- **State the subject and action first**, then add optional layers (scene, style, camera, audio) only as needed.
- **Define every reference material's role** in the prompt with explicit `@Image N defines...` syntax.
- **Add exclusion clauses** ("Do not use...") when a reference contains elements that could leak into output.
- **Name and bind every subject** to its reference — never make the model guess.
- **Group references by type** (Characters, Props, Scenes, Motion and Audio) when working with many assets.
- **Build subject profiles** for characters that recur across multiple scenes.
- **Select references by scene** — name only the assets each scene uses.
- **Divide each scene into stages at its natural duration** with one primary change and a clear end state per stage — right-size to 4–30s, do not pad to fill 30s.
- **Use timestamps sparingly** — only for critical handoffs, entrances/exits, transitions, or explicit beats.
- **Use audio brackets** `() <> {} 【】` when you need to distinguish music, SFX, dialogue, and subtitles.
- **Specify dialogue language** for non-Chinese dialogue using the reinforcement formula.
- **Pair emotion words with observable physical cues** (eyes, brows, mouth, breathing, gaze, hands).
- **Translate uncommon cinematography terms** into visible changes (term + subject + visual change + fg/bg + direction/speed).
- **Define the sole editing master** for video editing tasks, with explicit edit scope and content to preserve.
- **Align boundary frames** for video extension — describe the continuous state explicitly.
- **Use one image per view** for multi-angle subjects — separate images beat collages.
- **Keep the first and last frame images at the same aspect ratio.**
- **Keep blockout references clean** — remove path lines, coordinate axes, controllers, camera frustums.

### Don't

- **Don't describe the same action twice** — repetition can conflict with the reference itself.
- **Don't write "@Images 1 through 4 define four characters"** — it never says which image maps to which character.
- **Don't put generation parameters** (duration, resolution, ratio) in the prompt — use the generation interface or API.
- **Don't demand impossible frequencies** in timestamps (e.g., "complete three actions in one second").
- **Don't write only "turn these materials into a video"** for one-click video — state roles, order, motion, style, and audio.
- **Don't write only "connect to the source video"** for backward extension — it can introduce characters or effects too early.
- **Don't combine first/last frame declarations** into one sentence — describe each anchor image separately.
- **Don't let additional references override** the first/last-frame composition or the source video's boundary-frame control.
- **Don't use timestamps as frame-accurate edit points** — they are time budgets, not precise cuts.
- **Don't expect pixel-identical results** from video editing, extension, or seamless transitions.
- **Don't rely on numeric aperture/focal length values alone** — state the intended visible result.
- **Don't add "Do not use" clauses for every asset** — add them only when leakage is genuinely possible.
- **Don't force every reference to appear at once** — the goal is correct selection per scene.
