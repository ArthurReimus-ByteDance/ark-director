---
name: seedream-edit
description: Guide for using the seedream_edit_image MCP tool for interactive image editing with Seedream 5.0 Pro. Use when the user wants to edit an existing image (replace objects, change regions, add elements at specific positions), especially when coordinate-based precision is needed via point or bounding-box selection.
---

# Seedream Interactive Image Editing

The `seedream_edit_image` MCP tool wraps Seedream 5.0 Pro's interactive
editing capability with structured coordinate inputs. It is the dedicated
editing tool — distinct from `seedream_generate_image` which is primarily for
text-to-image generation.

## When to Use `seedream_edit_image`

Use `seedream_edit_image` when the user wants to **edit an existing image**
with spatial precision. The tool is a better fit than `seedream_generate_image`
when:

- The user provides a reference image and wants to modify a specific region
- The user says "replace the X with Y", "change this area to Z", "put a crown
  on the cat's head"
- The user has UI coordinates (from a canvas, click event, or drawn box) that
  need to be converted to normalized coordinates

Use `seedream_generate_image` instead when:

- The user wants text-to-image generation (no reference image)
- The edit is a global style change ("make it look like a watercolor painting")
  without spatial targeting
- The user does not provide specific coordinates or region information

## Coordinate System

Seedream 5.0 Pro uses **normalized coordinates** in the range **0 to 999**:

| Corner | Coordinates |
|---|---|
| Top-left | `(0, 0)` |
| Bottom-right | `(999, 999)` |

### Converting Pixel Coordinates to Normalized

When the user provides pixel coordinates relative to an image of known
dimensions (width × height):

```
normalized_x = round(pixel_x / image_width * 1000)
normalized_y = round(pixel_y / image_height * 1000)
```

Always clamp to `[0, 999]` after conversion.

### Tool Input: Point vs Bbox

The tool accepts structured coordinates, not raw markup strings:

**Point** — for object-level editing near a position:
```json
{
  "prompt": "Replace the object with a crown.",
  "images": [{"kind": "url", "url": "https://example.com/photo.png"}],
  "point": {"x": 520, "y": 460}
}
```

**Bounding-box** — for region-based editing:
```json
{
  "prompt": "Replace with a garden.",
  "images": [{"kind": "url", "url": "https://example.com/photo.png"}],
  "bbox": {"x1": 120, "y1": 180, "x2": 640, "y2": 760}
}
```

**Both** — for cross-image or multi-target editing:
```json
{
  "prompt": "Place the subject from Image 1 at the position of Image 2, and replace the object at Image 2 with a crown.",
  "images": [
    {"kind": "url", "url": "https://example.com/source.png"},
    {"kind": "url", "url": "https://example.com/target.png"}
  ],
  "bbox": {"x1": 179, "y1": 283, "x2": 796, "y2": 986},
  "point": {"x": 50, "y": 50}
}
```

The tool automatically constructs the `<point>` and `<bbox>` markup from these
structured inputs and prepends it to the user's prompt.

## Prompt Engineering for Editing

### Effective Prompts

- **Be specific about what changes.** "Replace the cat with a golden retriever"
  is better than "change the animal".
- **Describe the desired result, not the current state.** "Make the sky sunset
  orange" rather than "the sky is blue, change it".
- **Keep the instruction focused on the target region.** The model knows the
  spatial context from the coordinates.

### Prompt Patterns by Scenario

| Scenario | Prompt Pattern | Coordinates |
|---|---|---|
| Replace object | `Replace the object with a [description].` | Point |
| Change region | `Replace the area with a [description].` | Bbox |
| Add element | `Add a [description] at this position.` | Point |
| Remove object | `Remove the object and fill with [background description].` | Bbox |
| Style transfer | `Apply [style] to this area.` | Bbox |

## Reference Images

At least one reference image is required. The tool accepts:

```json
{
  "kind": "url",
  "url": "https://example.com/photo.png"
}
```

or:

```json
{
  "kind": "base64",
  "data": "iVBORw0KGgo...",
  "mime_type": "image/png"
}
```

URLs are validated for SSRF safety (HTTPS only, public IPs, no metadata
endpoints). Base64 data is limited to 10 MiB.

## Model Compatibility

The edit tool works with all Seedream models:

| Model | Max References | Notes |
|---|---|---|
| `dola-seedream-5-0-pro-260628` (default) | 10 | Pro model, no batch |
| Lite models (via `SEEDREAM_MODEL_BINDINGS`) | 14 | Supports batch |
| 4.x models (via `SEEDREAM_MODEL_BINDINGS`) | 14 | JPEG output only |

The `<point>` and `<bbox>` markup is specifically documented for
`seedream-5-0-pro` but may work with other models.

## Common Pitfalls

1. **Coordinates outside 0-999 range.** The tool rejects these at validation
   time. Always normalize pixel coordinates first.

2. **Bbox ordering.** `x1` must be ≤ `x2` and `y1` must be ≤ `y2`. The tool
   validates this.

3. **Too many reference images.** Pro models accept up to 10; Lite/4x accept
   up to 14. The tool validates this against the capability registry.

4. **Assuming the model knows image context.** The prompt should explicitly
   describe the edit. Don't rely on the model inferring intent from
   coordinates alone — they only specify *where*, not *what*.

5. **Using `seedream_generate_image` with raw markup.** While possible, it
   shifts coordinate validation onto the agent. Prefer `seedream_edit_image`
   when you have structured coordinates.

## Artifact Persistence

Like all Seedream tools, `persist=true` (the default) saves the edited image
to the local artifact store. The returned `ArtifactRef.uri` (e.g.
`seed-media://artifacts/abc123`) survives provider URL expiry (24 hours for
images). Always use `persist=true` unless you have a specific reason not to.

## Related Tools

- `seedream_generate_image` — text-to-image and reference-based generation
  (without coordinate markup)
- `seedream_generate_image_variations` — parallel image generation with
  distinct seeds
- `seedream-character-sheet-cleanup` — post-generation cleanup workflow for
  removing duplicate faces from Seedance-facing character sheets
- `seedance_create_task` — video generation from images or text
