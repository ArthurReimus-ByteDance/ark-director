# showcase.json schema

The generator consumes a single `showcase.json` in the project root. Relative
media `src` values are resolved against the project directory. The renderer
(`renderer.js`) builds the DOM from this JSON; you edit the JSON, never the
HTML.

## Top level

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | Document title and `<h1>`. |
| `kicker` | string | no | Small uppercase eyebrow above the title. |
| `lede` | string | no | One-paragraph description under the title. |
| `badges` | array | no | `{label, value}` pills (e.g. model, resolution). |
| `sections` | array | yes | Ordered section list. |
| `footer` | string | no | One-line footer text. |

## Section

Common fields: `id`, `title`, `icon` (emoji), `iconBg` (CSS color), `count`,
`desc`, and one of three `kind`s.

### `kind: "grid"` (Elements / Videos)

```json
{
  "id": "videos",
  "title": "Videos",
  "icon": "🎬",
  "iconBg": "var(--accent-soft)",
  "count": "5 · lens variants",
  "desc": "Optional section description.",
  "kind": "grid",
  "mediaOnly": false,
  "cards": [ /* card list */ ]
}
```

Card fields:

| Field | Type | Notes |
|---|---|---|
| `type` | string | `video` (default), `elem`, or `audio` — sets the top border color. |
| `kindPill` | string | Overlay label on the media frame (e.g. "V2V Edit"). |
| `media` | object | `{type: "video"|"image"|"audio", src, alt?}`. |
| `tag` | string | Uppercase tag line. |
| `title` | string | Card title. |
| `sub` | string | Sub-line (usually the filename). |
| `chips` | string[] | Meta chips (resolution, duration, size). |
| `refs` | array | `{name, role, kind}` — "Elements used" list. `kind` is `vid`/`img`/`aud`. |
| `prompt` | string | Prompt text, rendered in a `<pre>`. |
| `id` | string | **Selection key** — the asset's stable id (e.g. `lucky-lion`, or `lockup` for a multi-asset brand kit). Present only on selectable cards. Multiple variant cards may share one `id`. |
| `manifest` | string | Relative path to the element manifest this asset writes its selection back to (e.g. `elements/lucky-lion/character.md`). |
| `field` | string | Which frontmatter field the selection writes: `selected_variant` (default) or `selected_variants` (map). |
| `key` | string | Required when `field: "selected_variants"` — the map key to write (e.g. `lockup`). |

### Variant selection (in-browser "lock" of a chosen version)

A card is **selectable** when it carries `id` + `manifest` (+ `key` when it
targets a `selected_variants` map). Selection is a **server-only** feature:

- **`--serve`** (the one supported save path) — runs a local HTTP server with a
  write-back endpoint. The user clicks a variant to mark it, then presses
  **Ctrl+S / ⌘S** (or the "Save" button). The page POSTs the selections to the
  server, which writes the asset's `selected_variant` (or a single
  `selected_variants.<key>`) into the manifest frontmatter, records
  `selection.json`, and appends a timestamped audit log at `selection.log`. An
  **Activity log** panel shows the history.
- **`file://` (double-clicked `index.html`)** — **read-only**. No select buttons,
  no save, no activity log; a banner directs the user to `--serve`. This is
  deliberate: a browser cannot write to disk from `file://`, so persistence is
  server-only rather than a mix of downloads and pickers.

On load (server mode), the page reads the *current* selection from the manifests
so already-locked variants show as selected.

### `kind: "table"` (before/after or VFX scenarios)

```json
{
  "id": "comparison",
  "title": "Comparison",
  "icon": "🔄",
  "count": "before / after",
  "desc": "Optional description.",
  "kind": "table",
  "columns": ["Stage", "Prompt / Input", "Generated Result"],
  "rows": [
    {
      "stage": "BEFORE",
      "stageClass": "before",
      "stageTitle": "T2V · Seedance 2.5",
      "stageSub": "Optional sub-line.",
      "prompt": "Exact prompt text…",
      "media": { "type": "video", "src": "scenes/…/before.mp4" },
      "meta": "1280×720 · 6.0s · 8.0 MB"
    }
  ]
}
```

`stageClass` defaults to `before`/`after` based on the lowercase `stage`.

### `kind: "panel"` (single media with caption — combined/grid view)

```json
{
  "id": "combined",
  "title": "Combined",
  "icon": "🧩",
  "count": "3×2 grid · 8:3",
  "kind": "panel",
  "media": { "type": "video", "src": "scenes/…/grid.mp4" },
  "caption": "Caption text…"
}
```

## Minimal example

```json
{
  "title": "Lens Swap Showcase",
  "kicker": "AIGC Production Showcase",
  "lede": "One base shot re-lensed through five focal lengths.",
  "badges": [{ "label": "Model", "value": "dreamina-seedance-2-5-260628" }],
  "sections": [
    { "id": "elements", "title": "Elements", "icon": "🖼️", "kind": "grid", "mediaOnly": true, "cards": [] },
    { "id": "videos", "title": "Videos", "icon": "🎬", "kind": "grid", "cards": [] },
    { "id": "combined", "title": "Combined", "icon": "🧩", "kind": "panel", "media": { "type": "video", "src": "combined.mp4" }, "caption": "" }
  ],
  "footer": "Generated with Seedance 2.5."
}
```
