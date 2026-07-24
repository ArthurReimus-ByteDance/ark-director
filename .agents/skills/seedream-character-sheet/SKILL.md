---
name: seedream-character-sheet
description: Write structured Seedream prompts for three-panel character sheets and identity references. Invoke when the user asks for character sheets, model sheets, turnaround sheets, or Seedance-facing identity anchors.
---

# Seedream Character Sheet

Write production-grade prompts for BytePlus Seedream character-sheet generation.
This skill is specifically for **identity reference sheets**, not general
character portraits and not environment/location work.

Use this skill when the user wants:
- a character sheet
- a model sheet
- a turnaround-style identity sheet
- a Seedance-facing identity anchor
- a reusable `elements/characters/<id>/sheets/` asset

This skill is designed to partner with:
- `seedream-prompt` for general Seedream image prompting
- `seedream-character-sheet-cleanup` after generation when a full-body panel
  still shows a readable extra face
- `seedream-edit` for cleanup or local post-generation fixes

Do **not** use this skill for:
- one-off portraits
- posters or key art
- location assets
- product sheets
- environment stills

## Default production rule

For project character sheets, default to a **three-panel** layout unless the
user explicitly asks for more angles:

1. **Back full-body**
2. **Front full-body**
3. **Face close-up**

Use a **light gray** studio background by default unless the user provides a
different requirement.

## Why this layout

This layout is optimized for downstream identity consistency:
- the back view preserves costume, silhouette, hair, and headwear logic
- the front full-body view preserves stance and overall costume read
- the close-up panel acts as the canonical face anchor

Compared with a five-view turnaround, this structure is simpler, easier to
read, and more stable for later Seedance and Seedream reference use.

## Mandatory prompt structure

Assemble every character-sheet prompt in this order:

```text
=== INPUT REFERENCES ===
=== TASK TYPE ===
=== SUBJECT ===
=== SETTING ===
=== STYLE ===
=== LIGHTING ===
=== COMPOSITION ===
=== TEXT IN IMAGE ===
=== CONSTRAINTS ===
```

## 1. INPUT REFERENCES

List every reference image the user provides.

```text
=== INPUT REFERENCES ===
@Image 1: character face or approved identity reference
@Image 2: wardrobe or costume reference
@Image 3: style or film still reference
```

Rules:
- Use `None` when no references are provided.
- If an approved character sheet already exists, use it as `@Image 1` for
  continuity.
- If the user has a preferred costume or hair reference, separate those by role
  rather than blending them ambiguously into one description.

## 2. TASK TYPE

Usually this is:

```text
=== TASK TYPE ===
Text-to-Image (T2I)
```

Use **Image-to-Image (I2I)** only when preserving an already-approved
character identity while changing wardrobe, lighting, or sheet quality.

## 3. SUBJECT

Describe the person and the exact three-panel requirement.

```text
=== SUBJECT ===
[Character identity, age, ethnicity, facial features, hair, clothing, accessories, same person in all panels, three panels only: back full-body, front full-body, face close-up.]
```

Always include:
- age
- ethnicity / cultural identity when relevant
- 2–4 stable facial traits
- hair and headwear
- costume
- key accessories
- explicit statement that it is the **same person in all panels**

## 4. SETTING

The setting for character sheets is typically simple and controlled.

```text
=== SETTING ===
Clean light gray studio background, consistent across all three panels.
```

Default:
- light gray seamless background
- no props
- no furniture
- no environmental clutter

Only deviate if the user explicitly wants a stylized or filmic sheet background.

## 5. STYLE

Define the image language.

```text
=== STYLE ===
[Photorealistic, cinematic, editorial, film still, grounded realism, wardrobe-reference quality.]
```

Recommended anchors:
- photorealistic
- cinematic
- naturalistic editorial reference
- grounded realism
- film-photo finish

## 6. LIGHTING

Character sheets should be stable and readable.

```text
=== LIGHTING ===
[Soft studio light, even fill, no harsh shadows, consistent across all panels.]
```

Default:
- soft studio key
- gentle fill
- neutral white balance
- no hotspots
- no blown highlights

If the user asks for a filmic or moodier sheet, keep the lighting consistent
across the three panels even when the mood is more cinematic.

## 7. COMPOSITION

Explicitly enforce the three-panel structure.

```text
=== COMPOSITION ===
Three-panel character sheet with even spacing: back full-body view on the left, front full-body view in the center, face close-up on the right. Eye-level camera, consistent framing across the two body panels.
```

Core rules:
- three panels only
- back full-body first
- front full-body second
- frontal close-up third
- same character identity across all panels
- readable costume silhouette in the body panels
- close-up panel is the face authority

## 8. TEXT IN IMAGE

Default:

```text
=== TEXT IN IMAGE ===
None
```

For production character sheets, avoid text overlays unless the user asks for
labels.

## 9. CONSTRAINTS

Use quality + negative constraints together:

```text
=== CONSTRAINTS ===
Quality: 4K, consistent character identity across all panels
Negative: no extra panels, no side profile, no 3/4 view, no props, no text overlays, no watermarks, no distorted anatomy
```

Common negatives:
- no extra panels
- no profile panel
- no 3/4 panel
- no props in hands
- no background variation
- no distorted hands
- no extra fingers
- no watermark

## Standard prompt template

```text
=== INPUT REFERENCES ===
None

=== TASK TYPE ===
Text-to-Image (T2I)

=== SUBJECT ===
Character reference sheet, single character [name / description]. Same person in all panels, consistent identity. Three-panel sheet only: one full-body back view, one full-body front view, and one face close-up panel.

=== SETTING ===
Clean light gray studio background, consistent across all three panels. No props, no furniture, no background variation.

=== STYLE ===
Photorealistic, cinematic, professional character-sheet quality, consistent skin tone and wardrobe detail across all panels.

=== LIGHTING ===
Soft studio key light at 45 degrees left, gentle fill from the right, even illumination, neutral white balance, no dramatic shadows.

=== COMPOSITION ===
Three-panel character sheet with even spacing: back full-body view on the left, front full-body view in the center, face close-up on the right. Eye-level camera, consistent framing across the two body panels.

=== TEXT IN IMAGE ===
None

=== CONSTRAINTS ===
Quality: 4K, rich skin texture, natural hair detail, consistent character identity across all panels
Negative: no props in hands, no background variation, no extra panels, no side profile, no 3/4 view, no text overlays, no watermarks, no distorted anatomy, no extra fingers
```

## Worked example: Film-style pirate sheet

This example mirrors the user-provided sample image in `examples/`.

```text
=== INPUT REFERENCES ===
None

=== TASK TYPE ===
Text-to-Image (T2I)

=== SUBJECT ===
3-view character reference sheet for a film character. The same man in all three views: youthful attractive man in his early 30s, warm olive-brown skin, dark thick curly hair, thin mustache with a small soul-patch under the lip, faint stubble along the jaw, two small silver hoop earrings on the left ear, thin silver chain necklace, subtly asymmetrical face, a small subtle healed scar near the right eye. Age-of-sail pirate costume: faded mustard-yellow durag tied at the back with the tails hanging down, small shark tooth pendant attached to the durag above the left temple, open off-white linen shirt, worn dark leather vest, wide sash belt, baggy dark breeches, scuffed leather boots, weathered and dirty fabrics. Three panels only: full-body back view, full-body front view, and frontal face close-up.

=== SETTING ===
Neutral medium-gray seamless studio backdrop, consistent across all three panels, with thin subtle vertical divider lines separating the panels.

=== STYLE ===
Gritty cinematic 35mm film photograph, naturalistic editorial reference, fine film grain, organic matte skin texture, never plastic CGI skin.

=== LIGHTING ===
Very soft, low, diffused natural light, like soft shade or thin overcast through a scrim, wrapping gently around the face with extremely smooth gradual falloff. Slightly underexposed, moody, low-key, no harsh shadows, no hotspots, no blown highlights, no hard edges of light.

=== COMPOSITION ===
Three panels side by side in a single horizontal row. Left panel: full-body back view. Center panel: full-body front view. Right panel: frontal close-up portrait from the chest up, face square to camera. Consistent identity, costume, scar, accessories, proportions, and lighting across all panels.

=== TEXT IN IMAGE ===
None

=== CONSTRAINTS ===
Quality: 16:9 horizontal sheet, film-photo finish, consistent identity across all panels
Negative: no extra panels, no 3/4 view, no profile view, no props, no missing limbs, no prosthesis, no glossy skin, no watermarks, no text overlays
```

## Workflow pairing

Recommended sequence:
1. Use this skill to write the character-sheet prompt.
2. Generate the sheet with Seedream.
3. Inspect the body panels for extra readable faces.
4. If needed, invoke `seedream-character-sheet-cleanup`.
5. Save the approved result under `elements/characters/<character-id>/sheets/`.
6. Promote the approved version to `references/` for downstream use.

## Example asset

The user-provided sample image is stored beside this skill:
- `examples/pirate-character-sheet-generated-sample.png`

Use it as a visual target for layout and panel balance, not as a literal
identity reference unless the user explicitly asks for that specific character.
