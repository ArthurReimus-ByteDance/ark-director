---
name: showcase-html
description: >
  Build a self-contained local HTML review page for a project's generated media.
  Turns the project's elements (images, audio, base footage), videos, and prompts
  into a polished dark-mode gallery with color-coded cards, an "elements used"
  list per video, before/after comparison tables, and a combined grid/side-by-side
  view. Generates a data-driven page from a single showcase.json manifest plus an
  embedded template (no external assets), and optionally composes a combined-view
  MP4 with FFmpeg. Also supports locking variant selections back into element
  manifests via a local server (--serve) with a timestamped activity log. Use
  whenever the user wants an HTML review page, a media showcase or gallery, a
  before/after comparison page, a combined grid view, or a local template to
  preview generated assets, their prompts, and pick winning variants.
---

# Showcase HTML

Build a **self-contained, data-driven HTML review page** for a project's
generated media. The page is one portable file: it embeds a fixed template, the
project data as JSON, and a small renderer — no build step, no external CSS/JS,
works by double-clicking `index.html` in any browser.

This skill captures the page design used across the `seedance-lens-showcase`
and `honda-civic-location-swap` projects: color-coded asset cards, an
"elements used" list per video, before/after comparison tables, and a combined
grid view.

## When to use

- The user asks for an **HTML review page**, **showcase page**, **gallery**, or
  **template** for generated media.
- A project has multiple assets + prompts that need to be viewed side by side.
- The user wants a **before/after** or **combined view** in the same page.

Do **not** use for Lark/Feishu documents — that is `lark-showcase-aigc`. For
opening files directly on macOS, use `media-review`. For composing the
side-by-side/grid video itself, use `ffmpeg-side-by-side-comparison`.

## The data-driven model

Edit the **manifest**, not the HTML. The page is produced by:

1. `template.html` — fixed layout + CSS (dark, color-coded cards, sticky nav,
   showcase table, panel). Never hand-edit for per-project content.
2. `showcase.json` — the project's actual data (sections, cards, prompts, refs,
   media paths). **This is the file you author per project.**
3. `renderer.js` — reads the embedded JSON and builds the DOM.
4. `scripts/generate_showcase.py` — inlines the JSON + renderer into the
   template and writes `index.html`.

Full field reference: [references/schema.md](references/schema.md).

## Workflow

1. **Inventory the project.** Walk the project tree for media + prompts:
   - Elements → `elements/**` (characters, locations, props, audio, base
     footage) and their `prompt_*.md` snapshots.
   - Videos → `scenes/**/sNN_shNNN/` shot folders: the take `.mp4` and its
     `prompt_*.md` snapshot beside it.
   - The `references:` list in each `shot.md` frontmatter tells you which
     elements a shot binds (`@Image N` / `@Video N` / `@Audio N`) — use it to
     populate the card's `refs` ("Elements used").

2. **Author `showcase.json`.** One `grid` section for elements, one for videos,
   plus a `panel` section for the combined view and/or a `table` section for
   before/after. Use relative paths (resolved against the project dir). Read
   prompts verbatim from the `prompt_*.md` snapshots — never retype them.

   **Mark selectable cards** so variants can be locked from the page. Every card
   that represents a *variant* of an approved asset gets:
   - `id` — the asset's stable key (the element id, e.g. `lucky-lion`; or a
     short key like `lockup` for a multi-asset brand kit). All variant cards of
     one asset share the same `id`.
   - `manifest` — relative path to the manifest to write back to
     (e.g. `elements/lucky-lion/character.md`).
   - `field` — `selected_variant` (default) or `selected_variants` (map, for a
     multi-asset kit). When `selected_variants`, also set `key`.
   See [references/schema.md](references/schema.md#variant-selection-in-browser-lock-of-a-chosen-version).

3. **(Optional) Compose the combined view.** Use `ffmpeg-side-by-side-comparison`
   to build a grid/side-by-side MP4, then reference it in a `panel` section.

4. **Generate and open** (review-only, no selection write-back):

```bash
python3 .agents/skills/showcase-html/scripts/generate_showcase.py \
  projects/<project> --out index.html
open projects/<project>/index.html
```

   **To let the user lock variants from the browser**, run the server — it is the
   single supported save path. It serves the page and persists selections back
   to the manifests:

```bash
python3 .agents/skills/showcase-html/scripts/generate_showcase.py \
  projects/<project> --serve --port 8000
```

   The user clicks a variant to mark it, then presses **Ctrl+S / ⌘S** (or clicks
   the "Save" button) to persist. Saving writes the matching
   `selected_variant` / `selected_variants.<key>` into the element manifest,
   records it in `selection.json`, and appends a timestamped audit log at
   `selection.log` (JSON Lines: one record per event, with UTC `ts`, `event`,
   and per-event fields). The page shows an **Activity log** panel at the
   bottom with this history.

   **Plain HTML (`file://`) is read-only.** Double-clicking `index.html` is for
   *viewing* media and prompts only: no select buttons, no save, no activity
   log. The page shows a banner directing the user to `--serve` if they want to
   select and save. This keeps one unambiguous path — a browser cannot write
   files to disk by default, so persistence is deliberately server-only rather
   than a confusing mix of downloads and pickers.

5. **Verify.** Run `--check` to confirm every media `src` resolves (relative
   paths are the #1 failure), then spot-check sections, prompts, and the
   combined view in the opened page:

```bash
python3 .agents/skills/showcase-html/scripts/generate_showcase.py projects/<project> --check
```

## Section recipes

### Elements grid (color-coded cards)

Blue top border = element, amber = video, green = audio. Each card carries a
media frame (with a `kindPill`), meta chips, and a prompt block. For a project
whose "element" is base footage, that video is the element — there is no
separate image sheet.

### Videos grid + "elements used"

Each video card lists the exact references it consumed under **Elements used**,
with a color dot keyed to asset kind (`vid`/`img`/`aud`). This is the
machine-readable trace of the shot's `references:` frontmatter.

### Before/after comparison table

For VFX scenarios, use a `kind: "table"` section with `Stage | Prompt / Input |
Generated Result` columns and `BEFORE`/`AFTER` rows. Mirrors the Lark showcase
table convention.

### Combined view (panel)

A single full-width media panel for the combined grid / side-by-side MP4 with a
caption. The grid itself is built by `ffmpeg-side-by-side-comparison`.

## Building the combined grid (quick reference)

For N same-aspect 16:9 clips, a uniform grid is `(cols×16):(rows×9)`. Pick the
clean factorization closest to a landscape ratio:

- 6 clips → **3×2 = 8:3 (2880×1080)** — the default for landscape monitors.
- 4 clips → 2×2 = 16:9 (2560×1440).
- 2 clips → 1×2 side-by-side = 32:9, or 2×1 vertical = 8:9.

See `ffmpeg-side-by-side-comparison` for the exact `hstack`/`vstack`/`xstack`
filter graph and the PIL label fallback when `drawtext` is unavailable.

## Self-check

1. `showcase.json` is valid JSON and every media `src` resolves relative to the
   project dir (run `--check`).
2. Prompts are copied verbatim from `prompt_*.md` snapshots (not retyped).
3. Each video card's `refs` matches its `shot.md` `references:` list 1:1.
4. Selectable cards carry `id` + `manifest` (+ `key` for `selected_variants`),
   and multiple variant cards of one asset share the same `id`.
5. The page is a single portable `index.html` (no external CSS/JS/fonts).
6. The generated file opens cleanly and the combined view plays.
7. The page was opened in the browser via `open projects/<project>/index.html`
   (never asking the user to open it manually).

## Concurrency warning

`showcase.json` is **not merge-safe**. If two agents edit it at once, one edit is
silently lost. When regenerating alongside other work, read the file fresh
immediately before editing, make a minimal targeted change, and write it back
atomically — do not hold a stale copy across multiple tool calls.
