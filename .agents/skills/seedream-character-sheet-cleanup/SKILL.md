---
name: seedream-character-sheet-cleanup
description: Cleans Seedream character sheets by removing duplicate faces from full-body panels so only the close-up panel keeps a readable face. Invoke immediately after generating a multi-panel character sheet for Seedance use.
---

# Seedream Character Sheet Cleanup

Use this skill immediately after generating a three-panel character sheet and
before handing that sheet to Seedance or reusing it as a canonical identity
reference.

The purpose is simple: a character sheet with multiple readable faces can
confuse Seedance during downstream video generation. If the front full-body
panel shows a second readable face, the model can drift between faces over time.
The cleanup pass keeps only one face anchor: the dedicated close-up panel.

## Non-destructive output rule

Never overwrite the source character sheet.

Always save cleanup output as a **new image file or new version** so the
original sheet remains available for review, rollback, or alternate use.

This skill is designed to partner with:
- `seedream-character-sheet` for generating the original three-panel sheet
- `seedream-edit` and the `seedream_edit_image` MCP tool for the actual cleanup

## When to Invoke

Invoke this skill when all of the following are true:
- you already generated a character sheet
- the sheet contains a dedicated close-up face panel
- at least one full-body panel still shows a readable face
- the sheet will later be used as a Seedance identity lock or character reference

Do not invoke this skill when:
- the sheet already has only one readable face
- the user explicitly wants visible facial detail in multiple panels
- the image is a regular portrait sheet rather than a Seedance-facing identity sheet

## Core Rule

For Seedance-facing character sheets, keep exactly one readable face on the
sheet: the close-up panel.

The front full-body panel should preserve:
- pose
- clothing
- silhouette
- hair shape or headwear outline
- panel spacing
- background consistency

The front full-body panel should not preserve:
- readable eyes
- readable nose and mouth structure
- any second face that competes with the close-up panel

## Default Cleanup Target

The default target is the front full-body panel's face region.

If the back-view panel accidentally exposes too much face because of head turn
or profile leakage, clean that panel too. The close-up face panel remains the
only authoritative face and should stay untouched.

## Recommended Editing Mode

Use `seedream_edit_image` with a bounding box around the face area in the
full-body panel. This is a deletion or cleanup edit, not a full regeneration.

Target only the head and face region that needs cleanup. Do not box the entire
panel unless absolutely necessary.

## Prompt Template

Use this as the default edit instruction:

```text
Erase the face from the full-body shot on the first panel. Keep the body pose,
head silhouette, hair or headwear, costume details, panel spacing, divider
lines, studio background, and the close-up face panel unchanged. The finished
sheet must contain only one readable face: the close-up panel.
```

## Stronger Prompt Variant

Use this variant when the edit keeps recreating facial features:

```text
Remove all readable facial features from the full-body front-view panel while
preserving the character's head shape, hair, headwear, neck, costume, pose, and
overall panel composition. Do not alter the close-up portrait panel. The sheet
must present a single canonical face only in the close-up panel.
```

## Coordinate Guidance

When using `seedream_edit_image`:
- place the bbox tightly around the front-view face and immediate head area
- include enough surrounding pixels to let the model inpaint naturally
- avoid covering the torso, divider line, or close-up panel
- if the headwear is important, keep enough margin so the model preserves it

## Acceptance Check

The cleanup is successful when:
- the close-up panel is the only readable face on the sheet
- the front full-body panel still reads as the same character and costume
- the sheet layout remains stable
- the background and divider lines stay consistent
- no new facial detail appears elsewhere on the sheet

## Workflow Pairing

Recommended sequence:
1. Use `seedream-character-sheet` to generate the three-panel character sheet.
2. Inspect the full-body panels for duplicate readable faces.
3. If a second face is visible, invoke this skill.
4. Use `seedream-edit` with `seedream_edit_image` to remove the extra face.
5. Save the cleaned sheet as a **new version/file**, not as an overwrite of the
   source image.
6. Use the cleaned sheet as the version that Seedance should trust.

## Example From The User

The user provided a before-and-after pirate character-sheet example:
- Before: the left full-body panel still shows a readable front face, while the
  right close-up panel also shows the face. This creates two competing face
  anchors.
- After: the left full-body panel keeps the body, costume, and headwear, but
  the readable face is removed so the right close-up panel is the only face
  anchor left on the sheet.

Use that exact before-and-after logic whenever the sheet is meant to stabilize a
character for Seedance.

## Notes For Example Images

The example images live beside this skill under `examples/` using these
filenames:
- `examples/before_duplicate-face.png`
- `examples/after_single-face.png`

Treat that pair as the canonical before-and-after reference for future agents.

### Before

![Before cleanup](examples/before_duplicate-face.png)

### After

![After cleanup](examples/after_single-face.png)
