---
name: media-review
description: Open generated media (images and videos) for the user to visually review on macOS. Use whenever the user wants to review, compare, or choose between generated assets — image variations, video takes, character/environment sheets, or side-by-side source-vs-output comparisons. Builds montage/contact sheets for images to compare many at once, and opens videos directly in the default player (no keyframe extraction). Triggers include "review the variants", "open these for me to look at", "compare the takes", "which one should I pick".
---

# Media Review

Help the user visually review generated media assets on macOS. Since the agent
runs in a CLI with no graphical display, the practical way to let the user
compare assets is to open them via the operating system's default apps.

## Core principle

- **Images** → build contact sheets (montages) so many variants can be compared
  in a single view, and/or open them directly.
- **Videos** → open them directly in the default player. **Do NOT extract
  keyframes** to build contact sheets — just open the video files so the user
  can play them.

## Opening files

Use the macOS `open` command to launch the default apps:

```bash
open path/to/file.mp4
```

Open multiple assets at once (each opens in its own window):

```bash
open variant_a.mp4 variant_b.mp4 variant_c.mp4
```

To force a specific app (optional):

```bash
open -a "QuickTime Player" file.mp4
open -a Preview file.png
```

## Contact sheets for images

To compare many image variations at once, build a montage/contact sheet with
Python (PIL). This puts all variants in a single image with labels.

### Contact sheet helper

```python
from PIL import Image, ImageDraw

def contact_sheet(images, labels, out, cols=3, cell_pad=10, header_h=60, bg=(255,255,255)):
    """images: list of PIL Images (assumed same size), labels: list of str."""
    W, H = images[0].size
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new('RGB', (cols*W + (cols+1)*cell_pad, rows*H + (rows+1)*cell_pad + header_h), bg)
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(zip(images, labels)):
        r, c = divmod(i, cols)
        x = cell_pad + c*(W+cell_pad)
        y = header_h + cell_pad + r*(H+cell_pad)
        sheet.paste(im, (x, y))
        d.text((x, 12), lab, fill='black')
    return sheet

def sheet_from_paths(paths, labels, out):
    imgs = [Image.open(p) for p in paths]
    contact_sheet(imgs, labels, out).save(out)
```

### Typical usage

```bash
# Build and open a contact sheet comparing 3 map variants
python3 - <<'EOF'
from PIL import Image
# (use the helper above, or inline)
EOF
open _review_sheet.png
```

## Workflow

1. **Confirm what to review** — which assets and whether image or video.
2. **Images**: build a labeled contact sheet (all variants in one view) and open
   it. Optionally also open the individual files.
3. **Videos**: open the files directly with `open`. Do not extract keyframes.
4. Tell the user the file paths and ask which variant they prefer.

## Notes

- Works on macOS (uses `open`, `sips`, and Python PIL).
- Contact sheets preserve the original images unchanged — they only composite
  copies into a labeled grid for viewing.
- Clean up any throwaway `_review_*.png` sheets after the user has decided
  (CLAYGO), unless the user wants to keep them.
