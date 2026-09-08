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
`desc`, and one of four `kind`s.

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
targets a `selected_variants` map). Browser selection requires **server mode**; explicit CLI selection uses the same service:

- **`--serve`** (browser save path) — runs a local HTTP server with a
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

### `kind: "takes"` (video take comparison with synchronized playback + pick-winner)

A section that groups multiple video takes of the same shot side-by-side,
with synchronized playback and an optional "pick winner" selection that
writes back to `shot.md`. Each scene becomes one takes group.

```json
{
  "id": "video-review",
  "title": "Video Generation Review",
  "icon": "🎥",
  "iconBg": "var(--accent-soft)",
  "count": "4 scenes · 2 takes each",
  "desc": "Same prompt, distinct stochastic samples. Play both in sync, then pick a winner.",
  "kind": "takes",
  "groups": [
    {
      "title": "Scene 01 — Slot Game Opening",
      "uc": "UC-01 · Lucky Lion",
      "meta": ["720p", "16:9", "8s"],
      "promptFile": "scenes/scene-01/s01_sh010/prompt_s01_sh010_t01_v01.md",
      "takes": [
        {
          "label": "Take t01",
          "media": { "type": "video", "src": "scenes/scene-01/s01_sh010/s01_sh010_t01_v01.mp4" },
          "chips": ["7.4 MB", "8.04s", "24fps"],
          "contactSheet": "scenes/scene-01/s01_sh010/s01_sh010_t01_v01_contacts.jpg",
          "id": "s01_sh010",
          "manifest": "scenes/scene-01/s01_sh010/shot.md",
          "filename": "s01_sh010_t01_v01.mp4"
        },
        {
          "label": "Take t02",
          "media": { "type": "video", "src": "scenes/scene-01/s01_sh010/s01_sh010_t02_v01.mp4" },
          "chips": ["8.1 MB", "8.04s", "24fps"],
          "contactSheet": "scenes/scene-01/s01_sh010/s01_sh010_t02_v01_contacts.jpg",
          "id": "s01_sh010",
          "manifest": "scenes/scene-01/s01_sh010/shot.md",
          "filename": "s01_sh010_t02_v01.mp4"
        }
      ]
    }
  ]
}
```

**Group fields:**

| Field | Type | Notes |
|---|---|---|
| `title` | string | Scene title (e.g. "Scene 01 — Slot Game Opening"). |
| `uc` | string | Use-case label (e.g. "UC-01 · Lucky Lion"). |
| `meta` | string[] | Chips shown in the group header (resolution, ratio, duration). |
| `promptFile` | string | Relative path to the prompt snapshot. Rendered in a collapsible `<pre>`. |
| `takes` | array | List of take objects (see below). |

**Take fields:**

| Field | Type | Notes |
|---|---|---|
| `label` | string | Take label (e.g. "Take t01"). |
| `media` | object | `{type: "video", src}` — the video file. |
| `chips` | string[] | Metadata chips (file size, duration, fps). Auto-populated by `generate_showcase.py` when `ffprobe` is available. |
| `contactSheet` | string | Optional. Relative path to a contact sheet image (4 frames: opening, 1/3, 2/3, ending). Auto-generated by `generate_showcase.py --contact-sheets`. |
| `id` | string | **Selection key** — the shot id (e.g. `s01_sh010`). All takes of one scene share the same `id`. Required for pick-winner. |
| `manifest` | string | Relative path to `shot.md` for write-back. |
| `filename` | string | The take's filename, written as `selected_variant` in the manifest. |

**Selection:** When a take carries `id` + `manifest` + `filename`, the renderer adds a "Pick winner" button. In `--serve` mode, clicking it marks a choice; pressing Save writes `selected_variant: <filename>` into the shot's `shot.md` frontmatter. The selection flows through the same `/api/select` endpoint as element variants — no separate API.

**Synchronized playback:** Each takes group has a "Play all" button that starts all videos in the group simultaneously, and a "Pause all" button. This lets you compare motion side-by-side in real time.

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


## Selection API and CLI contract

The generator injects `selectableRegistry`; do not author it by hand. Each
asset id maps to `manifest`, `field`, optional `key`, and `variants` mapping
allowed filenames to project-relative media paths. All cards for one id must
agree on the target field. Duplicate filenames cannot refer to different media.

`GET /api/session` returns `{token, revision, selections}` from current manifests.
`POST /api/select` takes `{selections, expected_revision}` with JSON content type,
a same-origin `Origin`, and `X-Showcase-Token`. Success returns
`{ok: true, applied, errors: [], selections, revision}`. Invalid input is 400,
stale state or interrupted commit is 409, unauthorized origin/token is 403,
and an oversized body is 413. A failed batch never reports `ok: true`.

`--apply '{"asset-id":"filename.png"}'` performs the same validated batch write.
Use `--expected-revision` when applying a previously reviewed snapshot; otherwise
the CLI checks a fresh revision under its writer lock. This is an explicit
selection tool, not permission to convert recommended variants into approvals.
An omitted asset id preserves its current manifest selection. Clicking the
current browser choice leaves it selected; clearing existing approval is not
part of this endpoint.

The audit JSONL save event includes `ts`, `event`, `applied`, `selections`,
`total`, and `errors`. `.selection.lock` and `.selection-journal.json` are local
recovery state; keep them out of Git along with the project itself.
