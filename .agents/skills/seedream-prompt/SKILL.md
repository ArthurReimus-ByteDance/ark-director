---
name: seedream-prompt
description: Write structured Seedream 5.0 Pro/Lite image generation prompts with input reference labeling, subject definitions, style and composition control, interactive image editing (local edits, sketch rendering, layer separation, multi-image fusion, color/material replacement), high-density infographics, sequential generation, and constraints. Invoke when the user asks to generate a Seedream prompt, write an image prompt, create infographics, edit images, or design posters/UI/branding assets with BytePlus image generation.
---

# Seedream Prompt

Write production-grade prompts for BytePlus Seedream 5.0 Pro (`dola-seedream-5-0-pro-260628`) and Seedream 5.0 Lite. Seedream 5.0 Pro is a multimodal image creation model that goes beyond generation — it understands design intent, supports interactive precision editing, produces high-density infographics, natively renders text in 14 languages, and delivers cinematic realism with accurate lighting and materials.

## Source authority

The prompt structure and rules in this skill are sourced from:
- [Seedream 5.0 Pro official blog](https://seed.bytedance.com/en/blog/beyond-generation-it-understands-design-introducing-seedream-5-0-pro) (2026-07-08)
- [Seedream 4.0-5.0 API Tutorial](https://docs.byteplus.com/en/docs/ModelArk/1824121)
- [Seedream 4.0-4.5 Prompt Guide](https://docs.byteplus.com/en/docs/ModelArk/1829186)
- Seedream 5.0 Pro User Manual (Lark wiki, internal)

When the official guide is updated, prefer the live page over this skill where they conflict.

## Recommended prompt structure — Image generation

Use this order for the sections that apply. Do not add empty boilerplate sections:

```
References:          # only when images are provided
Task:                # include when the mode needs clarification
Subject:
Setting:             # when environment matters
Style:               # when style is specified or useful
Lighting:            # when lighting matters
Composition:         # when framing matters
Text in image:       # only when readable text is requested
Constraints:         # only useful quality or exclusion requirements
```

### 1. References (when provided)

List every reference image the user provides. Label them with `@Image 1`, `@Image 2`, ... using sequential numbering starting from 1 (space separator). Include a short role or description.

```
References:
@Image 1: [role, e.g. "subject reference — female character portrait"]
@Image 2: [role, e.g. "style reference — oil painting texture"]
@Image 3: [role, e.g. "material reference — leather sofa"]
@Image 4: [role, e.g. "color swatch — target palette"]
```

Rules for references:
- Seedream 5.0 Pro: up to 10 input images. Seedream 5.0 Lite: reference images + generated images ≤ 15 (so up to 14 refs when generating 1 image).
- First reference image is free. Each additional image: $0.003 (Pro).
- Formats: JPEG, PNG, WebP, BMP, TIFF, GIF, HEIC, HEIF.
- Up to 30 MB per image.
- Input resolution: each dimension > 14px, aspect ratio [1/16, 16], total pixels ≤ 36,000,000 (per API reference).
- When no references are provided, omit the References section.
- The reference list is an inventory, not the instruction. Bind each reference
  again where it affects the output, naming both its role and target:
  `Use the face and hairstyle from @Image 1 for the main character, apply the
  oil-paint texture from @Image 2 to the full scene, and use the leather from
  @Image 3 on the sofa.`
- Use the exact `@Image N` token every time; do not drop the `@` or replace the
  token with an ambiguous phrase such as “the references.”

### 2. Task type

Declare which generation mode applies.

```
Task:
Text-to-Image (T2I)  |  Image-to-Image (I2I)  |  Image Editing  |  Sequential Generation  |  Infographic / Information Visualization
```

**Text-to-Image (T2I)**: Pure text prompt, no reference images.

**Image-to-Image (I2I)**: Reference images guide subject, style, composition, or material. Use patterns like:
- `Using @Image 1 as the subject reference, generate...`
- `In the style of @Image 1, create...`

Reference-based generation sub-types (Reference Target + Generated Scene Description):
- **Reference Character**: `Use @Image 1 as the character reference, generate [scene description].`
- **Reference Style**: `In the style of @Image 1, generate [scene description].`
- **Reference Virtual Entity**: `Using the [entity] in @Image 1, generate [scene].`
- **Reference Product**: `Using the [product] in @Image 1, generate [commercial scene].`

**Image Editing**: Modify an existing image with localized changes. See the editing modes section below.

**Sequential Generation**: Generate multiple coordinated images in one call. **Not supported on Seedream 5.0 Pro** — Pro supports only single-image and multi-layer output. Sequential/batch generation requires Seedream 5.0 Lite (or 4.5/4.0) with `sequential_image_generation` set to `auto` (or `disabled`). Include "series", "set", or "sequence" in the prompt.

**Infographic / Information Visualization**: Transform data, concepts, and dense text into professional layouts. Seedream 5.0 Pro is specifically optimized for this.

### 3. Subject

Describe the main subject clearly and concisely. Order matters — concepts placed earlier carry more weight.

```
Subject:
[Who or what. Key attributes: appearance, clothing, hair, expression, pose, motion, props.]
```

Rules:
- Put the most important subject first.
- Use 2-3 stable attributes to define each subject.
- For multi-subject images, list subjects in order of visual priority.
- Describe pose, expression, and action: "standing confidently with arms crossed," "leaning forward, eyes wide with curiosity."

### 4. Setting

Describe the environment, time, weather, and background.

```
Setting:
[Location, time of day, season, weather, background elements, spatial context.]
```

Examples:
- "A sunlit Tokyo alley at golden hour, cherry blossoms drifting in the breeze, wooden shop signs overhead."
- "A futuristic cyberpunk city at night, neon reflections on wet asphalt, holographic billboards flickering."
- "A minimalist Scandinavian living room, morning light through sheer curtains, white walls and oak floors."

### 4b. Prop / product sheets (Seedance identity references)

For any prop or product sheet that will be used as a Seedance `@Image` identity
reference, isolate the subject on a **pure white seamless background** by
default. This prevents the sheet's backdrop from leaking into the generated
video. Apply the same rule to character and location identity references.

- Setting: "Isolated product shot on a pure white seamless background." with at
  most a soft, faint contact shadow directly beneath the object.
- Constraints (negative): no colored backdrop, no gradient background, no props,
  no hands, no reflections of other objects.
- When the sheet will be used with a Seedance blockout or R2V reference, also
  state in the video prompt "Use only the <subject> from @Image N — do not use
  its background."

**Prop threshold test — before generating a prop sheet, verify it is needed.**
Not every held or visible object requires a `prop_` sheet. A prop needs a
locked Element only if it meets **at least one** of these criteria:

| Criterion | Example | Needs Element? |
|---|---|---|
| Branded product with logo or specific design | GFiber modem, smartphone with app UI | Yes |
| Object the camera lingers on or that drives the plot | A key, a device screen the camera shows | Yes |
| Object that recurs across 2+ shots or scenes | Same phone in multiple ads | Yes |
| Generic, unbranded, briefly visible background object | A coffee cup, a birthday cake, a tablet in a montage | No — describe in prompt text |
| Object held for only 1-2 seconds in a single shot | A pen, a glass of water | No — text is sufficient |

Generating a `prop_` sheet for a generic, briefly-visible object wastes credits
and adds reference noise to the Seedance prompt. When in doubt, describe the
object in the Seedance prompt text and skip the Element.

### 5. Style

Define the artistic direction, medium, rendering quality, and aesthetic keywords.

```
Style:
[Art style, medium, rendering quality, aesthetic keywords.]
```

**Art style and medium**: photorealistic, cinematic, oil painting, watercolor, 3D render, anime, illustration, flat design, pencil sketch, charcoal, vector art, pixel art.

**Aesthetic keywords** (from the Seedream 5.0 Pro manual):

| Category | Keywords |
|---|---|
| Lighting style | Soft Light, Hard Light, Backlit, Dappled Light, Golden Hour, Night Neon, Low Key, Overexposed |
| Color tone | Warm Tone, Cool Tone, Blue Tone, Purple Tone, Monochrome, Low Saturation, Black and White Tone |
| Lens & perspective | Fisheye Lens, Macro Photography, Bird's Eye View, Wide Angle, Tilt-Shift |
| Mood & atmosphere | Cinematic, Motion Blur, Out of Focus, Diagonal Composition, Symmetrical Composition, Rule of Thirds |
| Genre | Cyberpunk, Retro Film, Minimalism, Japanese Fresh Style, Baroque, Art Deco, Brutalist |

### 6. Lighting

Describe light direction, quality, color temperature, and time of day.

```
Lighting:
[Direction, quality, color, time, key-to-fill ratio.]
```

Examples:
- "Soft studio key light at 45 degrees left, warm 3200K, gentle fill from right."
- "Golden hour backlight, rim light on subject's hair, warm amber tones."
- "Moody low-key lighting, single overhead source, deep shadows, cool blue moonlight through window."

### 7. Composition

Specify shot type, viewing angle, and composition method.

```
Composition:
[Shot type, angle, composition rule, framing.]
```

**Shot types**: close-up, medium shot, long shot, extreme close-up, wide shot, full body.

**Viewing angles**: high angle, low angle, eye level, bird's eye view, worm's eye view, Dutch angle.

**Composition methods**: symmetric, diagonal, rule of thirds, leading lines, frame within a frame, negative space, golden ratio.

### 8. Text in image (when requested)

Include this section only when the image should contain rendered text.

```
Text in image:
"Exact text to render" — [surface it appears on, style, color, size hint]
```

Rules:
- Put exact text in double quotes.
- Describe the surface: "on a storefront window," "on a vintage paper scroll," "on a digital screen."
- Seedream 5.0 Pro natively renders text in 14 languages: Arabic, Filipino, French, German, Indonesian, Japanese, Korean, Malay, Portuguese, Russian, Spanish, Thai, Turkish, Vietnamese. English is the base language. Other languages also work but with weaker in-image text rendering and cultural understanding.
- Small text may still be unstable — manual refinement after generation is recommended.

### 9. Constraints (when useful)

Close with only the quality directives and negative constraints that materially affect the output.

```
Constraints:
Quality: [HD, 4K, 2K, rich details, cinematic texture]
Negative: [no watermarks, no signatures, clean background, no text overlays, no distorted anatomy]
```

All constraints go inline in the text prompt. The Seedream API has no separate `negative_prompt` field.

## Recommended prompt structure — Image Editing

Seedream 5.0 Pro supports five editing modes. Pick one or combine multiple.
Use only the sections needed for the edit:

```
References:          # required for image editing
Task:                # include when the mode needs clarification
Editing mode:        # include when it helps disambiguate the operation
Edit instructions:
Constraints:         # only preservation and exclusion requirements that matter
```

### Editing Modes

The four image-editing operation types are: **addition** (add an element at a location), **deletion** (remove an element), **replacement** (swap one element for another), and **modification** (change an attribute of an element). Every edit prompt maps to one of these four.

#### 1. Interactive Control / Positioning

Position an edit using one of two official forms.

**Form 1 — Free-form marker + natural-language location**: Mark the edit area with hand-drawn sketches, doodles, circles, or colored frames, then describe the marker and intent in natural language.

```
References:
@Image 1: base image to edit

Task:
Image Editing

Editing mode:
Interactive Control — Free-form marker

Edit instructions:
In @Image 1, [describe exactly what to modify at the marked location]. [Describe what to add/remove/change].
```

Colored-frame region isolation (Form 1 pattern): outline locations with differently colored frames, and the model generates the specified items within each designated area, each strictly respecting its coordinate boundaries.
```
Generate a blue furry monster watching bubbles in the red frame, and a grass-green blanket in the purple frame.
```

Anchor grounding works best on clear row-and-column layouts:
```
Shift the red chariot at the bottom left one square to the right, and move the black pawn on the second line counting from the left side of Black's position one square downwards.
```

Layout-preserving translation (Form 1 pattern): the model translates text while preserving the original spatial layout.
```
Translate the menu into Chinese.
```

**Form 2 — Precise coordinate location (Pro only)**: Use `<point>` or `<bbox>x1 y1 x2 y2</bbox>` inline coordinate tags to pin the edit to exact pixels. Coordinates are obtained via an annotation tool.

```
Edit instructions:
Use the subject from @Image 1 <bbox>118 331 933 871</bbox> to replace the subject in @Image 2 <bbox>179 283 796 986</bbox>.
```

The model can also lock onto semantic regions without explicit coordinates — e.g., "Complete all the multiple-choice questions above and write out the corresponding calculation steps in the blank spaces below each question."

#### 2. Sketch Rendering

Use doodles, color blocks, lines, or simple sketches as control signals. The model recognizes the intent of each block and renders it as a high-fidelity visual.

```
References:
@Image 1: sketch / doodle / color block layout

Task:
Image Editing

Editing mode:
Sketch Rendering

Edit instructions:
Using the sketch in @Image 1 as the layout guide, generate [describe the final output]. [Describe what each block should become, e.g. "the red rectangle at the top becomes a title banner," "the blue circle on the left becomes a product photo"].
```

#### 3. Layer Separation

Split an image into independently editable layers output as PNGs with alpha (transparency) channels. Returns 2-20 images, billed per image.

```
References:
@Image 1: composite image to separate

Task:
Image Editing

Editing mode:
Layer Separation

Edit instructions:
Separate @Image 1 into independent layers: [list desired layers, e.g. "background, main subject, text overlay, decorative elements"]. Output each layer as a PNG with transparent background.
```

Layers retain transparency and can be freely dragged, scaled, or recomposed. Background areas obscured by the main subject are seamlessly inpainted.

#### 4. Color & Material Replacement

The model accepts Hex color codes or external color swatches and replaces materials while preserving lighting and perspective.

```
References:
@Image 1: material reference (e.g. velvet, wood, metal)
@Image 2: color swatch reference (e.g. palette card)
@Image 3: target image to modify

Task:
Image Editing

Editing mode:
Color & Material Replacement

Edit instructions:
Using the material from @Image 1 and the color swatch from @Image 2, modify the [specific object or region] in @Image 3. [Optional: specify Hex codes, e.g. "change to #3E4A2E dark green and #DB973E turmeric yellow in alternating pattern"].
```

#### 5. Multi-Image Fusion

Fuse objects, styles, and materials from multiple reference images into a target scene.

```
References:
@Image 1: first object on a white background
@Image 2: second object on a white background
@Image 3: third object on a white background
@Image 4: fourth object on a white background
@Image 5: fifth object on a white background
@Image 6: sixth object on a white background
@Image 7: seventh object on a white background
@Image 8: target scene and composition layout

Task:
Image Editing

Editing mode:
Multi-Image Fusion

Edit instructions:
Precisely cut out the first object from @Image 1, the second from @Image 2, the third from @Image 3, the fourth from @Image 4, the fifth from @Image 5, the sixth from @Image 6, and the seventh from @Image 7. Compose them into a real still-life photograph using the scene geometry and placement from @Image 8. Ensure correct perspective, light-and-shadow, and spatial relationships. Faithfully reproduce material details such as wood grain, leather, lace, glass, and feathers.
```

### Combining Editing Modes

Editing modes can be combined freely. Example:
```
Change the pumpkins to an alternating pattern of dark green #3E4A2E and turmeric yellow #DB973E, while giving the background typography an embroidered texture.
```

## Full example: T2I — Cinematic scene

```
Task:
Text-to-Image (T2I)

Subject:
A young woman in a flowing red dress, windswept dark hair, standing at the edge of a cliff, arms slightly raised, face turned toward the horizon with a serene expression.

Setting:
A dramatic coastal cliff at golden hour. The ocean stretches endlessly below, waves crashing against rocks. Distant seabirds circle. A lighthouse is visible on a far promontory.

Style:
Cinematic, photorealistic, widescreen anamorphic look. Kodak Portra 400 film stock aesthetic.

Lighting:
Golden hour backlight, warm amber and rose tones, soft rim light on the subject's hair and dress, gentle fill from the ocean reflection. God rays breaking through scattered clouds.

Composition:
Wide shot, eye level, rule of thirds — subject positioned on the left third line, horizon on the lower third, negative space to the right filled by the ocean and sky.

Constraints:
Quality: 4K, rich textures, cinematic depth of field
Negative: no watermarks, no text overlays, no distorted anatomy, natural skin texture
```

## Full example: Infographic

```
Task:
Infographic / Information Visualization

Subject:
A visual infographic chronicling scientific research at Antarctica's Qinling Station. Place the main Qinling Station building at the center. Surround it with a timeline of research station development, a bar chart comparing the sizes of five research stations, a pie chart of the station's energy sources, and a line chart of monthly sunshine. Supplement with realistic photos of research equipment, a summer weather panel, a seven-step fieldwork flowchart, and on-site sampling photography.

Setting:
Clean, academic presentation layout. Antarctic landscape references in the background — ice shelves, penguin colonies, aurora.

Style:
Scientific infographic, National Geographic editorial style, clean data visualization, modern sans-serif typography.

Lighting:
Even, bright studio lighting for charts and diagrams. Dramatic natural lighting for the landscape elements.

Composition:
Central anchor (research station) with radial layout. Timeline along the top, charts on the left, flowchart on the right, photos in the bottom section.

Text in image:
"Qinling Station" — main title
Chart labels and data values as appropriate

Constraints:
Quality: 2K, crisp text rendering, professional color palette
Negative: no distorted charts, no misaligned text, consistent font sizes
```

## Full example: Image Editing — Color & Material Replacement

```
References:
@Image 1: velvet fabric swatch (material reference)
@Image 2: color palette card — teal and gold
@Image 3: living room photo — brown leather sofa to modify

Task:
Image Editing

Editing mode:
Color & Material Replacement

Edit instructions:
Using the velvet material from @Image 1 and the teal color from @Image 2, modify the sofa in @Image 3. Replace the brown leather with teal velvet. Keep the wood frame, surrounding decor, and room lighting unchanged. The new material should catch light naturally with the same highlights and shadows as the original.

Constraints:
Quality: 2K, photorealistic material rendering
Negative: do not change the room background, do not alter the sofa's shape or proportions
```

## Full example: Multi-image fusion

```
References:
@Image 1: wooden desk on white background
@Image 2: leather-bound journal on white background
@Image 3: brass desk lamp on white background
@Image 4: porcelain teacup on white background
@Image 5: fountain pen on white background
@Image 6: composition layout sketch
@Image 7: window light reference photo

Task:
Image Editing

Editing mode:
Multi-Image Fusion

Edit instructions:
Precisely cut out the objects from @Image 1 through @Image 5 and compose them according to the layout in @Image 6 into a real still-life photograph on the desk. Use the window lighting from @Image 7 as the scene lighting reference. Ensure correct perspective, light-and-shadow, and spatial relationships. Faithfully reproduce material details — wood grain, leather texture, polished brass, glazed ceramic.

Constraints:
Quality: 2K, photorealistic, natural shadow casting
Negative: no floating objects, no mismatched lighting directions
```

## Character-sheet routing

For character sheets, identity sheets, turnaround sheets, or Seedance-facing
character references, use the partner `seedream-character-sheet` skill instead
of embedding that workflow here.

If the generated character sheet later needs duplicate-face cleanup, follow it
with the companion `seedream-character-sheet-cleanup` skill.

## Usage tips

### Prompt formula
**Subject > Setting > Style > Lighting > Composition > Technical** — order matters, concepts placed earlier carry more weight.

### Prompt length
- Recommended: 30-100 words for standard images.
- Infographics and complex scenes can go longer but stay focused.

### The more specific, the better
- Clearly describe subject appearance, state, motion, expression, and attire.
- Use style keywords to define artistic direction.
- Describe light direction, quality (hard/soft), color tone, and time of day.
- Specify shot type, viewing angle, and composition method.
- For multi-image fusion, style transfer, and outfit transfer, uploading reference images improves fidelity.

### Break complex tasks into steps
For multi-element composition or fine editing, step-by-step operation improves controllability.

### What Seedream 5.0 Pro is good at
- Precise local editing through interactive controls
- Multi-image fusion of objects, styles, and materials
- High-density information visualization (data, text, concepts into images)
- Design productivity: posters, presentations, branding, e-commerce assets
- Multilingual text: 14 languages with accurate character structures
- Cinematic imagery: high-fidelity narrative scenes and portrait retouching

### What Seedream 5.0 Pro is not suited for
- Fully replacing professional designer judgment
- Highly complex layouts requiring precise typographic control
- Generating non-compliant or infringing content
- UI design requiring pixel-level precision
- Small text may still be unstable — manual refinement after generation is recommended

## Avoiding the AI look

Seedream images often look AI-generated even when prompted for "realistic" results. The root cause is almost always **insufficient specificity** — the model fills visual gaps with its default plastic-smooth aesthetic. The fixes below apply to both T2I and reference-based generation.

### 1. "Realistic" is not enough — use concrete photorealism signals

The word "realistic" or "photorealistic" alone does little. The model needs **specific** references to real-world imaging pipelines:

- **Film stocks**: Kodak Portra 400, Fujifilm Superia 400, Ilford HP5, CineStill 800T
- **Lens characteristics**: anamorphic widescreen, 35mm prime, shallow depth of field, natural lens flare, chromatic aberration
- **Camera bodies**: shot on ARRI Alexa, Sony A7R IV, Hasselblad medium format
- **Photographic genres**: documentary photography, photojournalism, editorial portrait, street photography

**Bad:** `Style: realistic, high quality`

**Good:** `Style: photorealistic, cinematic, Kodak Portra 400 film stock aesthetic, anamorphic widescreen look, shot on 35mm prime lens`

### 2. Lighting is the #1 AI tell

Flat, even, shadowless lighting is the most common reason an image reads as AI-generated. Real photographs have **directional, imperfect light** with falloff, spill, and environmental contamination.

Always specify:
- **Direction**: "key light at 45 degrees camera-left"
- **Quality**: hard, soft, diffused, dappled
- **Color temperature**: warm 3200K, cool 5600K, golden-hour amber
- **Falloff / spill**: "light spills onto the background wall," "shadows deepen at the edges"
- **Environmental contamination**: "window light mixed with neon signage reflection," "dust particles catching the backlight"

**Bad:** `Lighting: well lit, bright`

**Good:** `Lighting: golden hour backlight, warm amber and rose tones, soft rim light on subject's hair, god rays breaking through scattered clouds, gentle fill from ocean reflection`

### 3. Add skin and texture imperfections

AI models default to airbrushed, plastic-smooth skin. Counteract this by explicitly requesting imperfections in the **Subject** section:

- Visible pores, subtle freckles, fine lines
- Flyaway hair strands, stray eyebrow hairs
- Slight asymmetry in features or smile
- Skin texture: dewy, matte, perspiring, wind-chapped
- Fabric texture: visible weave, wrinkling, stray threads

**Bad:** `Subject: A beautiful woman with perfect skin`

**Good:** `Subject: A woman in her early 30s, visible pores and subtle freckles across the nose, flyaway hair strands catching the light, slight asymmetry in her smile, faint laugh lines`

### 4. Prompt order carries weight

Concepts placed earlier in the prompt carry more weight. If "photorealistic" is buried at the end after Constraints, the model treats it as an afterthought. Put the most important visual directives (style, lighting) high in the order:

**Subject > Setting > Style > Lighting > Composition > Constraints**

### 5. Use negative constraints aggressively

Seedream has no separate `negative_prompt` field — all exclusions go inline in the Constraints section. AI-looking outputs are best prevented by explicitly forbidding the artifacts the model tends to produce:

```
Constraints:
Quality: 4K, rich textures, cinematic depth of field
Negative: no plastic skin, no over-smoothing, no waxy textures, no watermarks, no text overlays, no distorted anatomy, no unnatural symmetry, no CG render look
```

### 6. Avoid over-description that forces perfection

Long lists of superlatives ("flawless, stunning, breathtaking, perfect, gorgeous") push the model toward an idealized, plastic look. Prefer **observed detail** over **value judgment**:

- "windswept dark hair" not "beautiful stunning gorgeous hair"
- "weathered hands resting on a wooden railing" not "perfect elegant hands"
- "slightly rumpled linen shirt" not "beautiful designer outfit"

### 7. Use `prompt_optimization: standard`

The `fast` prompt optimization mode trades quality for latency. For photorealistic final output, always use `standard` (the default). Only use `fast` for quick iterations and concept exploration.

### 8. Before-and-after example

**Prompt that produces AI-looking output:**
```
Subject: A beautiful young woman with perfect skin and stunning features, wearing a gorgeous red dress, standing on a cliff.

Setting: A beautiful ocean view at sunset.

Style: Realistic, high quality, 4K.

Lighting: Well lit.

Composition: Wide shot.

Constraints:
Quality: HD
Negative: no watermarks
```

**Prompt that produces photorealistic output:**
```
Subject: A young woman in her late 20s, visible pores and subtle freckles, flyaway dark hair strands catching the light, slight asymmetry in her smile, wearing a slightly windswept red linen dress, standing at the edge of a cliff with arms slightly raised, face turned toward the horizon.

Setting: A dramatic coastal cliff at golden hour. Ocean stretches below, waves crashing against rocks. Distant seabirds. A lighthouse on a far promontory.

Style: Photorealistic, cinematic, Kodak Portra 400 film stock aesthetic, anamorphic widescreen look, shot on 35mm prime lens.

Lighting: Golden hour backlight, warm amber and rose tones, soft rim light on subject's hair and dress, god rays breaking through scattered clouds, gentle fill from ocean reflection.

Composition: Wide shot, eye level, rule of thirds — subject on left third line, horizon on lower third, negative space to the right.

Constraints:
Quality: 4K, rich textures, cinematic depth of field
Negative: no plastic skin, no over-smoothing, no waxy textures, no watermarks, no text overlays, no distorted anatomy, no unnatural symmetry, no CG render look
```

## Quick reference card

### Model IDs
| Model | Model ID |
|---|---|
| Seedream 5.0 Pro | `dola-seedream-5-0-pro-260628` |
| Seedream 5.0 Lite | `seedream-5-0-260128` (alias: `seedream-5-0-lite-260128`) |

### Pricing (Seedream 5.0 Pro)
| Tier | Price |
|---|---|
| Output ≤ ~2.36M pixels (1K tier) | $0.045 / image |
| Output > ~2.36M pixels (2K tier) | $0.09 / image |
| First reference image | Free |
| Each additional reference image | $0.003 |

The 2.36M-pixel threshold is the practical 1K/2K billing boundary. Only the $0.045 base is shown on the public pricing page.

### Resolution and size (Seedream 5.0 Pro)
The `size` parameter accepts either a resolution tier (`1K` / `2K`, set via natural-language aspect-ratio/shape description; default `2K`) or explicit `widthxheight`.
- Pixel range: [921600, 4624220] (~0.92M–4.6M)
- Aspect-ratio range: [1/16, 16]
- 1K examples: 1024×1024, 1424×800 (16:9)
- 2K examples: 2048×2048, 2816×1584 (16:9, 2K tier)

Input per image: ≤ 36,000,000 pixels, ≤ 30 MB (per API reference).

### Prompt optimization mode (Pro)
`optimize_prompt_options.mode`:
- `standard` (default) — higher quality, slower.
- `fast` — lower latency, slightly lower quality. Recommended when latency-sensitive.

### Output parameters
- `response_format`, `output_format`: png / jpeg (default jpeg).
- `watermark`: bool.
- Layer separation: PNG with alpha (transparency) channel, 2-20 images.

### Supported prompt languages (Seedream 5.0 Pro)
Native support for 14 languages: Arabic, Filipino, French, German, Indonesian, Japanese, Korean, Malay, Portuguese, Russian, Spanish, Thai, Turkish, Vietnamese. English is the base language. Other languages also work but with weaker in-image text rendering and cultural understanding.

### Throughput and streaming
- Rate limit: 500 images/minute.
- Streaming output: not supported on Pro (supported on Lite/4.5/4.0).
- Sequential/batch output: not supported on Pro (supported on Lite/4.5/4.0).

### Regions
Supported in `ap-southeast-1` and `eu-west-1`.

### Trust ecosystem with Seedance
- Images from Seedream 5.0 Pro and Lite are trusted inputs across all Seedance models (2.5 `dreamina-seedance-2-5-260628`, 2.0 `dreamina-seedance-2-0-260128`, Fast/Mini via `SEEDANCE_MODEL_BINDINGS`).
- Text-to-Image outputs are trusted automatically for all customers.
- Image-to-Image outputs become trusted after the account passes KYC verification.
- Trust exempts input moderation only, not output moderation.
