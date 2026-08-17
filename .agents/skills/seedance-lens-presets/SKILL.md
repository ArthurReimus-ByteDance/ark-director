---
name: seedance-lens-presets
description: >
  Turns a lens, focal length, aperture, or sensor request into a canonical
  visible-result phrase for Seedance 2.5 prompts or the Seedream style.
  Trigger words: lens, focal length, 35mm, 50mm, 85mm, wide angle, telephoto,
  anamorphic, fisheye, macro, aperture, f-stop, f/1.4, depth of field, bokeh,
  shallow DOF, deep focus. For 4K optics requests, route to the
  `seedance-prompt-20` skill instead.
---

# Seedance Lens Presets

This skill converts a lens, focal length, aperture, or sensor request into a
canonical **visible-result** phrase that drops into a Seedance 2.5 prompt's
camera or visual-style line, or into a Seedream style section. It is
**prompt-composition only** — it writes text, it does not run any generation.

Numeric optical values (35mm, f/1.4, shutter speed) are **advisory** on
Seedance: the official guide states the intended **visible result** is usually
clearer than a numeric value alone. So this skill always pairs any number with
the observable outcome it produces — depth of field, compression, bokeh shape,
flare, distortion, grain. There is **no true optical simulation**: the model
does not compute lens physics, so this skill describes the visible look, not
the optics. Never promise exact bokeh geometry or aberration physics.

## Source authority

The rules and phrases in this skill are sourced from:

- [Seedance 2.5 Prompt Guide (Lark)](https://bytedance.larkoffice.com/docx/A88jd0B47oAd8zxWp5ycZFMfnxh) and
  [Seedance 2.5 Prompt Guide (ModelArk)](https://docs.byteplus.com/en/docs/ModelArk/2607689) —
  the camera-language section, which states: "Aperture, focal length, and
  shutter values can be included, but the intended **visible result** is
  usually clearer than a numeric value alone."
- [Seedream 4.0-4.5 Prompt Guide](https://docs.byteplus.com/en/docs/ModelArk/1829186) — official ModelArk prompt guide. The film-stock and lens-character vocabulary used here (e.g. "shot on 35mm prime lens", "widescreen anamorphic look") follows the `seedream-prompt` skill's *Avoiding the AI look* guidance, which derives from the official Seedream manual and tutorial.
- [Higgsfield Cinema Studio 3.5 Full Tutorial](https://higgsfield.ai/blog/cinema-studio-3.5-full-tutorial) —
  its Lens, Focal Length, and Aperture console options (f/1.4 Wide Open, f/4
  Moderate, f/11 Deep Focus; 8–135mm focal lengths; Anamorphic, Fisheye, Macro,
  Warm Halation, Vintage Haze, Clinical Sharp) are the inspiration for this
  preset bank.

All sources accessed **2026-08-13**. When the official guides are updated,
prefer the live pages over this skill where they conflict.

The base prompt grammar this skill composes into lives in the
`seedance-prompt-25` skill (six-part formula, camera language, emotional
direction) and the `seedream-prompt` skill (Subject / Setting / Style / Lighting
/ Composition structure). Load those skills alongside this one; this skill only
resolves the optics axis.

## Preset bank

Every preset below is a canonical **visible-result** phrase. The numeric value
is advisory — always pair it with the phrase, never ship the number alone.

### Focal lengths

| Focal length | Intent | Canonical visible-result phrase |
|---|---|---|
| **8 / 14mm** | Extreme wide | Extreme wide angle: vast space dominates the frame, near objects loom large, edges curve with a subtle barrel distortion. |
| **24 / 35mm** | Wide | Wide angle with strong environmental context: subject stays in frame while the surrounding space, architecture, and depth stretch away from the camera. |
| **50mm** | Natural human perspective | 50mm natural perspective: subject and background relate the way the human eye sees them, no obvious compression or stretch. |
| **75 / 85mm** | Portrait compression | 85mm portrait compression: the face fills the frame, the background is compressed and feels closer to the subject. |
| **135mm** | Strong compression | 135mm telephoto compression: subject stands out sharply while the background is flattened, stacked, and pulled tight against the subject. |

Numeric focal values are advisory — always pair the number with the visible
result phrase. Focal length and camera distance are not interchangeable: a
telephoto look comes from the compressed perspective, not from cropping a wide
shot.

### Apertures / depth of field

| Aperture | Intent | Canonical visible-result phrase |
|---|---|---|
| **f/1.4** | Very shallow DOF | f/1.4 wide open: very shallow depth of field, the subject's eyes are sharp while foreground and background dissolve into creamy circular bokeh. |
| **f/4** | Moderate DOF | f/4 moderate: subject clearly separated from the background, near details stay soft but readable, background falls off gently. |
| **f/11** | Deep focus | f/11 deep focus: near-to-far sharpness, foreground and background details both stay crisp and in focus. |

Do not rely on a single number. "Shallow depth of field" alone is weak; state
what is sharp and what is soft, and the bokeh shape.

### Lens character

| Lens | Canonical visible-result phrase |
|---|---|
| **Anamorphic** | Anamorphic widescreen look: oval, stretched bokeh in the background and a horizontal anamorphic lens flare streaking across the frame. |
| **Fisheye** | Fisheye: strong barrel distortion, straight lines bow outward, the edges of the frame curve into a sphere. |
| **Macro** | Macro: extreme close view, tiny detail fills the frame, the background is a soft, blurred wash behind the subject. |
| **Telephoto** | Telephoto: compressed background stacked close behind the subject, atmospheric haze thickening toward the distance. |
| **Clinical Sharp** | Clinical sharp lens: crisp focus edge to edge, minimal aberration, no glow or softening. |
| **Warm Halation** | Warm halation: a soft warm glow blooming around highlights, gentle bleed where light meets dark. |
| **Vintage Haze** | Vintage haze: soft low-contrast image with a slight bloom, muted colors, the diffused look of an old film lens. |

For anamorphic, always include the flare and bokeh cues explicitly — "oval
bokeh" and "horizontal lens flare" — because those are the observable markers.

### Sensor / body character

| Sensor | Canonical visible-result phrase |
|---|---|
| **VHS** | VHS camcorder look: low resolution, visible scanlines, colors bleeding into each other, soft analog noise. |
| **Film** | Film stock look: visible grain, gentle halation around highlights, natural tonal range. |
| **Digital Cinema** | Digital cinema look: clean, crisp image with high dynamic range and minimal noise or grain. |

Sensor character is a texture and tone choice, not a resolution guarantee.
Pair it with the actual output resolution set in the generation interface.

## Parameter schema

| Parameter | Type | Meaning |
|---|---|---|
| `lens` | string | Named lens character (anamorphic, fisheye, macro, telephoto, clinical sharp, warm halation, vintage haze, auto) |
| `focal_length` | string | Numeric focal request (8, 14, 24, 35, 50, 75, 85, 135mm) |
| `aperture` | string | Aperture request (f/1.4, f/4, f/11) |
| `sensor` | string | Sensor / body character (vhs, film, digital cinema) |
| `subject` | string | The subject the optics apply to (the sharp plane target) |
| `target_model` | string | `seedance` \| `seedream` \| `both` — where the phrase lands |

Only supply the parameters the user asked for. Do not invent an aperture or
focal length the user never mentioned. `lens`, `focal_length`, and `aperture`
are independent axes; a shot can request one, two, or all three.

## Output grammar

Resolve each requested axis to its canonical phrase, then assemble it into a
single camera/visual line. **Pair the number with the visible result** using
this template:

```
Camera: <focal length>mm, <aperture> — <visible result>.
```

Example:

```
Camera: 85mm, f/1.4 — shallow depth of field, face sharp, background soft with
compressed creamy bokeh.
```

### Seedance 2.5 placement

Drop the optics line into the six-part formula's **Camera** line (or the
visual-style line when sensor character dominates). The optics line replaces or
refines the camera-treatment slot; do not duplicate it elsewhere in the prompt.
Match the canonical prose formula — do not use labeled `Subject:`/`Camera:`
scaffolding:

```
<Subject> performs <primary action> in <scene>.
The visuals feature <sensor or lens character phrase>.
Use <focal length>mm, <aperture> — <visible result>.
Audio includes <dialogue, ambience, sound effects, or music>.
```

Full worked Seedance example:

```
A film student examines an old camera in a dusty repair shop at golden hour.
Visual style: digital cinema look, clean and high dynamic range.
Camera: 85mm, f/1.4 — shallow depth of field, the student's eyes stay sharp
while the shelf of lenses behind dissolves into compressed creamy bokeh.
Audio: soft ticking of the wall clock and faint street ambience.
```

### Seedream placement

For a still image, put the phrase in the **Style** section and let the
**Lighting** section carry the DOF/light interplay:

```
Task:
Text-to-Image (T2I)

Subject:
<subject description>

Setting:
<environment description>

Style:
Cinematic, photorealistic, shot on 35mm prime lens, widescreen anamorphic look.

Lighting:
Soft window light, gentle falloff behind the subject, shallow depth of field
with the background dissolving into soft bokeh.

Composition:
<shot type and framing>
```

## Edge cases / guardrails

- **No true optical simulation.** There is no lens-physics renderer. Never
  promise exact bokeh geometry, aberration, or exposure behavior — only the
  visible look the phrase describes.
- **Numeric values alone are weak.** Always pair focal length, aperture, or
  shutter with the visible-result phrase. A lone "50mm" or "f/1.4" is
  under-specified.
- **Anamorphic needs the flare cue.** Include "oval/stretched bokeh" and
  "horizontal lens flare" explicitly; without them the anamorphic intent is
  ambiguous.
- **4K optics route to Seedance 2.0.** Seedance 2.5 outputs up to 1080p.
  When the user asks for high-resolution optics (e.g. "4K anamorphic"),
  route to `seedance-prompt-20` and the 2.0 model
  (`dreamina-seedance-2-0-260128`).
- **One lens intent per shot.** Do not overload a single shot with multiple
  competing optics (e.g. anamorphic plus fisheye). Choose one intent; split
  distinct optics across separate shots.
- **Focal length is not crop.** Telephoto look comes from perspective
  compression, not from enlarging a wide shot in post.
- **Watermark off by default.** Set `watermark: false` on image, video, and
  audio generation unless the user explicitly requests the AIGC watermark.
- **Record the resolved phrase.** When a generation is submitted, the exact
  prompt snapshot (including the optics line) is saved beside the asset as
  `prompt_<asset>.md` and referenced from the shot manifest.

## Self-check checklist

Before delivering a prompt built with this skill, verify:

1. **Every numeric optical value is paired with a visible result** — no bare
   "50mm" or "f/1.4" standing alone.
2. **One lens intent per shot** — no anamorphic-and-fisheye conflicts in a
   single shot.
3. **Anamorphic includes the flare and bokeh cue** — "horizontal lens flare"
   and "oval/stretched bokeh" wording is present.
4. **4K / 1080p requests route to `seedance-prompt-20`** — high-res optics are
   flagged as a Seedance 2.0 concern, not silently placed in a 2.5 prompt.
5. **The phrase sits in the camera line (Seedance) or Style section (Seedream)** —
   the optics line is not duplicated elsewhere in the prompt.
6. **The subject of the sharp plane is named** — "face sharp", "eyes sharp"
   names the subject the DOF acts on.
7. **No optical physics promises** — no claims of exact bokeh geometry or
   aberration behavior.
8. **`watermark: false`** is the default on any generation the user runs from
   the prompt.

## Guide disclaimer

The examples in this skill illustrate prompt-writing techniques only. Actual
generation results may vary depending on the input materials, task complexity,
and generation parameters. Numeric optics are advisory; validate the visible
result in review before locking a take.
