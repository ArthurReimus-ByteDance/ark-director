---
name: ffmpeg-side-by-side-comparison
description: >
  Assemble two or more videos into a single side-by-side (or N-up) comparison
  clip with FFmpeg — before/after, A/B, or a review grid. Handles uniform
  scaling, pixel-aspect alignment, duration sync, optional labels, and audio.
  Use whenever the user wants a before-and-after split screen, an A/B
  comparison of two takes or versions, a compare or review grid, a
  side-by-side demo, or asks to put clip X and clip Y next to each other —
  even if they never say "side-by-side". For chronological assembly with
  crossfades, use `ffmpeg-scene-transitions`; this skill places clips
  simultaneously, not sequentially. Complements the `ffmpeg` skill.
---

# FFmpeg Side-by-Side Comparison

Build a single comparison video from two or more source clips. The canonical
use is **before/after**: two versions of the same shot, placed left and right
in one frame, so a viewer can compare them at the same moment in time.

## Core recipe (2-up before/after)

```bash
ffmpeg -y \
  -i before.mp4 \
  -i after.mp4 \
  -filter_complex \
    "[0:v]scale=640:360,setsar=1[a]; \
     [1:v]scale=640:360,setsar=1[b]; \
     [a][b]hstack" \
  -an -c:v libx264 -crf 23 -preset fast \
  compare.mp4
```

Result: one 1280x360 frame with `before` on the left and `after` on the right.

## The two rules that make seams line up

1. **Scale every input to the same size** before stacking. Clips from different
   generators or sources will differ in resolution and aspect; pick one target
   (e.g. `640:360`, `960:540`) and apply it to every input.
2. **Add `setsar=1`** after scaling. If sources have non-square pixels (common
   with phone/vertical captures or certain containers), the scaled frames keep
   a non-1:1 sample aspect ratio and the halves will not align — seams split,
   content squashes. `setsar=1` forces square pixels so `hstack` edges match.

Always use explicit, equal target dimensions — never relative expressions such
as `scale=iw/2:ih/2`. `iw`/`ih` refer to each chain's own input, so that
shorthand halves every source to its own size and the halves will not match
(and the stack fails on resolution mismatch).

### Mixed aspect ratios (portrait / vertical sources)

`scale=W:H` **stretches** — a portrait 1080x1920 clip scaled to `640:360`
comes out squeezed into 16:9. When inputs differ in aspect ratio, letterbox
instead:

```bash
[0:v]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,setsar=1[a];
[1:v]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,setsar=1[b];
[a][b]hstack
```

`force_original_aspect_ratio=decrease` shrinks each source to fit inside the
target while keeping its shape; `pad` centers it on the target canvas with
bars. Every input still ends up exactly `640:360` with square pixels, so the
stack lines up.

## Choosing the canvas

- **2-up (before | after):** `hstack` after scaling both to `W:H` → canvas `2W x H`.
- **Vertical stack (before over after):** `vstack` → canvas `W x 2H`.
- **4-up grid (2x2):** `xstack` (below).
- **Ladder / arbitrary layout:** `xstack` with an explicit `layout`.

## 4-up grid with xstack

```bash
ffmpeg -y \
  -i a.mp4 -i b.mp4 -i c.mp4 -i d.mp4 \
  -filter_complex \
    "[0:v]scale=640:360,setsar=1[a]; \
     [1:v]scale=640:360,setsar=1[b]; \
     [2:v]scale=640:360,setsar=1[c]; \
     [3:v]scale=640:360,setsar=1[d]; \
     [a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0" \
  -an -c:v libx264 -crf 23 -preset fast \
  grid.mp4
```

`layout` positions each input: `0_0` (top-left), `w0_0` (right of input 0),
`0_h0` (below input 0, at x=0), `w0_h0` (right of input 0 and below input 1,
i.e. the bottom-right). For 3-up, use `xstack=inputs=3:layout=0_0|w0_0|w0+w1_0`
for a top row of three.

## Adding labels (BEFORE / AFTER)

Labels sit on each scaled stream before stacking. **Prefer `drawtext` when your
ffmpeg build has it** — check with `ffmpeg -filters | grep drawtext`; it needs
libfreetype and many builds omit it.

**`drawtext` variant (requires libfreetype):** this follows documented filter
syntax; on builds without libfreetype it will not run, so the PIL `overlay`
variant below is the machine-validated path.

```bash
ffmpeg -y \
  -i before.mp4 -i after.mp4 \
  -filter_complex \
    "[0:v]scale=640:360,setsar=1,drawtext=text='BEFORE':x=10:y=10:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=8[a]; \
     [1:v]scale=640:360,setsar=1,drawtext=text='AFTER':x=10:y=10:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5[b]; \
     [a][b]hstack" \
  -an -c:v libx264 -crf 23 -preset fast \
  compare_labeled.mp4
```

- If `drawtext` cannot find a font, pass one explicitly:
  `drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:...` (path varies by
  platform). A colon inside the label text must be escaped as `\:`.

**Overlay variant (no libfreetype needed, always available):** generate label
PNGs with Python PIL (requires `pip install pillow` if not present), then
`overlay` them onto the stacked canvas. Note PIL's default bitmap font is small
(≈8px); for larger labels set a font via `ImageFont.truetype`:

```python
from PIL import Image, ImageDraw
def label(text, path):
    im = Image.new("RGBA", (180, 48), (0, 0, 0, 128))
    ImageDraw.Draw(im).text((10, 10), text, fill="white")
    im.save(path)
label("BEFORE", "label_before.png")
label("AFTER", "label_after.png")
```

```bash
ffmpeg -y \
  -i before.mp4 -i after.mp4 -i label_before.png -i label_after.png \
  -filter_complex \
    "[0:v]scale=640:360,setsar=1[a]; \
     [1:v]scale=640:360,setsar=1[b]; \
     [a][b]hstack[v]; \
     [v][2:v]overlay=10:10[vl]; \
     [vl][3:v]overlay=650:10" \
  -an -c:v libx264 -crf 23 -preset fast \
  compare_labeled.mp4
```

The second overlay x is `canvas_width/2 + 10` (e.g. 650 for a 1280-wide
canvas). Labels are optional and only needed when the halves are not
self-evident.

## Duration sync (clips of different lengths)

Decide the target length explicitly; do not let FFmpeg guess.

- **Trim both to the shortest** (end together):
  `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 -i short.mp4`
  then pass `-t <that duration>` on the output.
- **Fixed window:** `-t 30` on the output caps every stream at 30s.
- **Pad the short one to the long one** (keep full content): use `tpad`
  `[0:v]scale=640:360,setsar=1,tpad=stop_mode=clone:stop_duration=5[a]`.

For frame-rate mismatch, insert `fps=24` (or the target rate) after each
`setsar=1` so both halves advance frame-for-frame.

## Audio

Comparison clips default to **no audio** (`-an`) — the visual split is the
point, and two soundtracks on one canvas are confusing. When audio is needed:

```bash
ffmpeg -y \
  -i before.mp4 -i after.mp4 \
  -filter_complex \
    "[0:v]scale=640:360,setsar=1[a]; \
     [1:v]scale=640:360,setsar=1[b]; \
     [a][b]hstack[v]; \
     [0:a][1:a]amix=inputs=2:duration=shortest[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 23 -c:a aac \
  compare_with_audio.mp4
```

Notes:
- `[0:a]` / `[1:a]` assume **both** sources carry an audio stream. If either is
  silent (common for blockout or proxy takes), drop the `amix` line and keep
  `-an` — do not guess a stream that is not there.
- `amix` **sums levels**, so two identical soundtracks come out roughly +6 dB
  louder. That is why `-an` is the right default for review comparisons; mix
  only when the combined sound is genuinely wanted.

## Quality / size knobs

- `-crf 23` is a good default (visually near-lossless, small file). Lower =
  better/heavier (`18`), higher = worse/lighter (`28`).
- `-preset fast` balances speed and compression; `slow` for smaller files.
- Match the deliverable: review proxy → `640:360` / `720p`; presentation →
  scale to `960:540` or `1280:720` halves and `-crf 18`.

## Worked example (from the graybox→cinematic project)

```bash
# BEFORE — graybox blockout; AFTER — cinematic R2V render
ffmpeg -y \
  -i s01_sh010_t04_v01.mp4 \
  -i s01_sh010_t10_v01.mp4 \
  -filter_complex \
    "[0:v]scale=640:360,setsar=1[a]; \
     [1:v]scale=640:360,setsar=1[b]; \
     [a][b]hstack" \
  -an -c:v libx264 -crf 23 -preset fast -t 30 \
  s01_compare_before_after_v01.mp4
```

Both sources were already 1280x720 / 30s, so `-t 30` just caps the length; the
output is 1280x360, ~2.8 MB.

## Self-check

1. Every input is scaled to the same dimensions with `setsar=1` — and, when
   aspect ratios differ, letterboxed (`force_original_aspect_ratio=decrease`
   + `pad`) rather than stretched — no misaligned seams, no squashed content.
2. The stack operator matches the layout (`hstack` / `vstack` / `xstack`).
3. The target duration is explicit when lengths differ (`-t`, `-shortest`, or
   `tpad`); no silent truncation surprises.
4. Frame rates are synced (`fps=` filter) when inputs differ.
5. Audio is `-an` for review comparisons, or explicitly mixed and mapped when
   required.
6. Output codec is `libx264` (or requested), `crf` tuned to the deliverable.
7. The output was decoded (`ffmpeg -v error -i out.mp4 -f null -`) and
   inspected for seam alignment before shipping.
8. Labels, when used, come from an available mechanism — `drawtext` only if
   libfreetype is present (`ffmpeg -filters | grep drawtext`), otherwise the
   PIL `overlay` fallback.
