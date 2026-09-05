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
