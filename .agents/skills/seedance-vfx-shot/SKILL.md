---
name: seedance-vfx-shot
description: End-to-end pipeline for Seedance 2.0 video-to-video VFX shot production. Composes the seedance-vfx-prompt skill with the modelark MCP tools to take a source clip and a change description through to a saved, manifested asset. Invoke when the user wants to run a full VFX shot — write prompt, submit task, poll, download, save manifest — rather than just write a prompt. Supports both Seedance 2.0 and 2.5; default to 2.5 (omni_reference_task_type=edit) for full-duration edits.
---

# Seedance VFX Shot Pipeline

End-to-end pipeline for producing a Seedance 2.0 VFX shot from a source clip.
This skill composes the `seedance-vfx-prompt` skill (prompt writing) with the
`modelark-mcp` tools (task submission, polling, download) to produce a saved,
manifested asset following the workspace's `projects/<project>/` directory
conventions.

> **Version note**: This pipeline runs on **both** Seedance generations.
> **Default to Seedance 2.5** (`dreamina-seedance-2-5-260628`,
> `omni_reference_task_type=edit`) for full-duration edits — 2.5 preserves ~the
> source length, while **2.0's `edit_video` caps output at ~5s** in practice.
> Use 2.0 only for 4K output or Fast/Mini variants. For 2.0 T2V/R2V prompts,
> use `seedance-prompt-20`.

Use this skill when the user wants to:
- **run a complete VFX shot** from source clip to saved output
- **submit a VFX edit** to Seedance and get the result back as a local file
- **produce a manifested, reproducible VFX asset** with `shot.md` + prompt file

Do **not** use this skill when the user only wants to:
- write a VFX prompt without submitting (use `seedance-vfx-prompt`)
- generate text-to-video or image-to-video (use `seedance-prompt`)
- generate images or audio (use Seedream / Seed Audio skills)

## Prerequisites

- `ARK_API_KEY` (or `BYTEPLUS_MODELARK_API_KEY`) set in environment or `.env`
- `mcp_modelark-seed` MCP server running and healthy
- Source video clip accessible as a local file path or URL
- Project directory exists under `projects/<project-name>/`

## Pipeline overview

```mermaid
flowchart TD
    IN[Inputs: source clip, change description, project context] --> PROMPT
    PROMPT[1. Write VFX prompt via seedance-vfx-prompt] --> VALIDATE
    VALIDATE[2. Validate inputs and references] --> SUBMIT
    SUBMIT[3. Submit via seedance_create_task MCP] --> POLL
    POLL[4. Poll via seedance_get_task until terminal] --> CHECK
    CHECK{status?} -->|succeeded| SAVE
    CHECK -->|failed/cancelled/expired| ERROR[Report error + retry guidance]
    SAVE[5. Download asset to scene shot directory] --> MANIFEST
    MANIFEST[6. Write shot.md manifest] --> PROMPTFILE
    PROMPTFILE[7. Write standalone prompt .md] --> REPORT
    REPORT[8. Report cost, latency, paths, last-frame]
```

## Before/after demo recipe (turnkey)

The workspace's recurring pattern for a text-only before/after VFX demo:

1. BEFORE — Seedance 2.5 T2V, `720p`, `16:9`, natural duration (4–30s), no
   references. Save + manifest.
2. `media_upload` the BEFORE clip; record its `object_key` in the project
   `ref_cache.json`. Presign on demand; never re-upload.
3. AFTER — `seedance_2_5_create_task`, `omni_reference_task_type=edit`, `1080p`,
   `@Video 1` = the BEFORE URL; `duration` and `ratio` auto-lock. Write the
   prompt with `seedance-vfx-prompt` (2.5 editing section).
4. Transcode the AFTER (usually HEVC) to H.264 for review/Lark — see the
   "Delivery transcode" recipe in Step 5. Keep the HEVC master.
5. Comparison — if the halves differ mainly in audio (language swap / dialogue
   rewrite), use the staggered one-at-a-time split from
   `ffmpeg-side-by-side-comparison`; otherwise a simultaneous `hstack`.
6. Manifests — Steps 6–7 of this skill; then set `review`, and only explicit
   user approval sets `approved`.

## Inputs

| Input | Required | Description |
|---|---|---|
| `source_video` | Yes | Local path or URL to the source clip to edit |
| `change_description` | Yes | Plain-language description of the VFX change |
| `project` | Yes | Project name (kebab-case, must exist under `projects/`) |
| `scene` | Yes | Scene ID (e.g. `scene-01`) |
| `shot` | Yes | Shot ID (e.g. `s01_sh010`) |
| `element_refs` | No | List of element reference paths (characters, locations, props) |
| `resolution` | No | Default `4k` for face/detail shots; `1080p` for landscape-only |
| `duration` | No | Default: match source clip duration (max 15s) |
| `ratio` | No | Default `16:9` |
| `return_last_frame` | No | Default `true` (enables shot chaining) |
| `safety_identifier` | No | Default `<project>-<scene>-<shot>` |

## Step 1 — Write the VFX prompt

Use the `seedance-vfx-prompt` skill to write the prompt. The prompt must follow
the natural-language heading structure with all applicable sections:

```text
Asset preparation:
@Video 1: source clip — [subject, action, camera motion, duration]
@Image 1: [element reference] — [role]

Subject definitions:
Define the [features] in @Video 1 as [Label]

Prompt:
Task type: Video Editing
Strictly edit @Video 1, and modify [what changes] at [timestamp]. Preserve [locks].

[New world — full description of the replacement or added environment/element]

Lighting: [embedded lighting]
Space: [foreground, midground, background depth]
Timing: [if applicable]
Audio: [diegetic only]

Quality and constraints:
Quality: photoreal, 4K, [look/grade]
Constraints: [NON-IP, face protection, no-warp, camera-motion lock]
```

Pass the user's `change_description` to the prompt skill. The prompt skill will
produce the structured prompt text.

## Step 2 — Validate inputs

Before submitting, verify:

1. **Source video exists** — confirm the local file path resolves or the URL
   is reachable. If local, note the file size (large base64 uploads compete for
   bandwidth; the MCP server handles encoding).
2. **Element references exist** — for each path in `element_refs`, confirm the
   file exists under `projects/<project>/elements/`. Each reference should be
   a character sheet, location sheet, or prop sheet image.
3. **Prompt is complete** — run through the VFX prompt checklist from
   `seedance-vfx-prompt` (all applicable sections present, `Asset preparation:`
   first with `@Video 1` source clip, face protection in constraints if faces
   are present).
4. **4K check** — if the source clip contains a human face, `resolution` must
   be `4k`. Only allow `1080p` for pure landscape/environment shots with no
   human faces.

> **2.5 guard**: Seedance 2.5 supports 480p/720p/1080p. If using the 2.5 model (`dreamina-seedance-2-5-260628`), set `resolution` to `"720p"` or `"1080p"` — `"4k"` is invalid and will be rejected.

5. **Duration** — 1 to 15 seconds. The API also accepts `-1` (auto/match-source),
   but for VFX prefer an explicit duration matching the source clip. If the
   source clip is longer than 15s, split it into multiple chained shots.

For Seedance 2.5, single-pass duration extends to 30s, and native forward/backward extension can replace the manual `return_last_frame` chaining workflow.

6. **Project/scene/shot directory exists** — create it if missing:
   - `projects/<project>/scenes/scene-NN/sNN_shNNN/`

## Step 3 — Submit via MCP

Call `seedance_create_task` on the `mcp_modelark-seed` MCP server.

**MCP request structure:**

```json
{
  "server_name": "mcp_modelark-seed",
  "tool_name": "seedance_create_task",
  "args": {
    "input": {
      "prompt": "<full VFX prompt text from Step 1>",
      "videos": [
        {
          "kind": "url",
          "url": "<source video URL or local path>",
          "role": "reference_video"
        }
      ],
      "images": [
        {
          "kind": "base64",
          "data": "<base64-encoded character/location sheet>",
          "mime_type": "image/png",
          "role": "reference_image"
        }
      ],
      "model": "{{model_id}}",  # default: dreamina-seedance-2-0-260128 (2.0); use dreamina-seedance-2-5-260628 for 2.5 (note: 2.5 caps at 1080p)
      "resolution": "4k",
      "ratio": "16:9",
      "duration": 5,
      "generate_audio": true,
      "watermark": false,
      "return_last_frame": true,
      "execution_expires_after": 3600,
      "priority": 0,
      "safety_identifier": "<project>-<scene>-<shot>"
    }
  }
}
```

Key parameters for VFX:

**Seedance 2.5 (default for full-duration edits):** use `seedance_2_5_create_task`
instead, with `"omni_reference_task_type": "edit"` (2.5 accepts
`auto|reference|edit|extend`; `edit_video` is 2.0-only and will be rejected).
Omit `ratio` and `duration` — they auto-lock to the source. 2.5 caps at 1080p.
2.0 (`edit_video`) caps output at ~5s, so use 2.5 for any edit longer than ~5s.
- **`videos[].role = "reference_video"`** — the source clip to edit. This is
  what makes it a video-to-video (VFX) task rather than text-to-video.
- **`images[].role = "reference_image"`** — element references (character
  sheets, location sheets, prop sheets) for identity consistency.
- **`resolution = "4k"`** — face protection; preserves skin texture, prevents
  waxy warping.
- **`generate_audio = true`** — Seedance 2.0 native audio. The prompt's
  `Audio:` section guides the audio generation.
- **`return_last_frame = true`** — returns the last frame image, enabling
  shot chaining for multi-shot VFX sequences.
- **`safety_identifier`** — set to `<project>-<scene>-<shot>` for
  traceability.

The tool returns a `task_id` and `polling_interval`. Immediately store the task,
shot, take, version, model, status, intended asset path, and submission time in
`projects/<project>/task_ids.json` before polling. A local timeout never
authorizes a duplicate submission; resume the recorded task until terminal.

## Step 4 — Poll for completion

Call `seedance_get_task` repeatedly, respecting the `polling_interval` from
creation:

```json
{
  "server_name": "mcp_modelark-seed",
  "tool_name": "seedance_get_task",
  "args": {
    "task_id": "<task_id from Step 3>",
    "persist_output": true
  }
}
```

Task states transition through: `queued` → `running` → `succeeded` / `failed`
/ `cancelled` / `expired`.

Poll until the status is terminal:
- **`succeeded`** — proceed to Step 5. The response includes `artifacts` (the
  generated video, and optionally the last frame image if
  `return_last_frame=true`), `usage` (token counts, cost), and `settings`.
- **`failed`** — check the `error` field. Common causes: content safety
  rejection, invalid reference format, prompt too long. Report the error and
  retry guidance to the user.
- **`cancelled`** — the task was cancelled (manually or by timeout). Report
  and ask the user whether to resubmit.
- **`expired`** — the `execution_expires_after` window elapsed before the task
  completed. Resubmit with a longer expiry.

## Step 5 — Download and save the asset

On `succeeded`, the MCP response includes `artifacts` with the generated video
(and optionally the last frame image). The MCP server's artifact store
(`persist_output: true`) has already persisted the asset.

Save the video in its shot directory:

```
projects/<project>/scenes/scene-NN/sNN_shNNN/sNN_shNNN_t01_v01.mp4
```

File naming follows the workspace convention:
- `<scene>_sh<NNN>_t<NN>_v<NN>.mp4` — e.g. `s01_sh010_t01_v01.mp4`
- If approved as final: `<scene>_sh<NNN>_final_v<NN>.mp4`

If `return_last_frame=true`, save the last frame image alongside the video for
chaining:

```
projects/<project>/scenes/scene-NN/sNN_shNNN/sNN_shNNN_t01_v01_lastframe.png
```

> **Delivery transcode (HEVC → H.264).** Seedance 2.5 edit outputs are usually
> HEVC (`video_codec: hevc`). Lark/doc previews and many players need H.264. Keep
> the HEVC master as the archival take and produce a browser-safe derivative:
>
> `ffmpeg -i <take>.mp4 -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 20 -c:a aac -b:a 128k -movflags +faststart <take>_lark_h264.mp4`

## Step 6 — Write the shot.md manifest

Write the `shot.md` file in the shot directory with full YAML frontmatter for
reproducibility:

```
projects/<project>/scenes/scene-NN/sNN_shNNN/shot.md
```

**Manifest template:**

```yaml
---
project: <project>
scene: <scene>
shot: <shot>
model: dreamina-seedance-2-0-260128  # 2.0 default; use dreamina-seedance-2-5-260628 for 2.5 (1080p max)
mode: V2V
vfx_level: <1 | 2 | 3>
references:
  - <source video path or URL>
  - elements/<character-id>/<character-sheet>.png
  - elements/<location-id>/<location-sheet>.png
prompt_file: scenes/scene-NN/sNN_shNNN/prompt_sNN_shNNN_t01_v01.md
prompt_sha256: <sha256 of exact submitted prompt>
seed: null
params:
  resolution: 4k
  ratio: "16:9"
  duration: 5
  audio: true
  watermark: false
  return_last_frame: true
  submission_mode: single
take: t01
version: v01
status: review
cost_usd: <from MCP response>
billing_tokens_total: <from MCP response>
artifacts:
  - take: t01
    id: <artifact_id from MCP>
    uri: <seed-media:// URI from MCP>
    task_id: <task_id from MCP>
    media_type: video
    mime_type: video/mp4
    bytes: <file size>
    sha256: <hash>
    width: 3840
    height: 2160
    duration: <actual duration>
    audio_channels: 2
    audio_sample_rate: <from MCP>
    completion_tokens: <from MCP>
    cost_usd: <per-take cost>
    created_at: <ISO timestamp>
safety_identifier: <project>-<scene>-<shot>
---

# <shot> — VFX edit (<vfx_level>, 4K, audio)

<Description of the VFX edit performed on the source clip.>

## Source clip

- **Source**: `<source video path or URL>`
- **VFX level**: <1 — World Swap | 2 — Element Change | 3 — Handheld Showcase>

## Element references

- **@Image 1**: `<sheet>` — <element description>
- **@Video 1**: `<source>` — source clip for VFX edit

## Generation parameters

- **Model**: `dreamina-seedance-2-0-260128` (Seedance 2.0 Standard; for 2.5 use `dreamina-seedance-2-5-260628` — note 2.5 caps at 1080p)
- **Resolution**: 4K (3840×2160)
- **Ratio**: 16:9
- **Duration**: <N>s
- **generate_audio**: `true` (native diegetic audio)
- **watermark**: `false`
- **return_last_frame**: `true` (for shot chaining)
- **safety_identifier**: `<project>-<scene>-<shot>`

## Cost

- <N> take × $<cost>/take = **$<total> total**
- <N> × <tokens> completion tokens = <total> total tokens

## Prompt

Full prompt text saved at:
- `scenes/scene-NN/sNN_shNNN/prompt_sNN_shNNN_t01_v01.md`

## Reproduction

To re-create this take from this manifest alone:

1. Encode the source video and element reference images.
2. Call `seedance_create_task` on `mcp_modelark-seed` with the prompt from
   `prompt_sNN_shNNN_t01_v01.md`, `model=dreamina-seedance-2-0-260128  # or dreamina-seedance-2-5-260628 for 2.5 (1080p max)`,
   `resolution=4k`, `ratio=16:9`, `duration=<N>`, `generate_audio=true`,
   `return_last_frame=true`.
3. Poll with `seedance_get_task` until `status=succeeded`.
4. Download via `runtime.artifact_store.get(artifact_id)`.
5. Expect ~<N>s of 4K `video/mp4` with AAC audio, cost ~$<cost>/take.
```

## Step 7 — Write the standalone prompt file

Save the exact submitted prompt once, alongside the asset:

```
projects/<project>/scenes/scene-NN/sNN_shNNN/prompt_sNN_shNNN_t01_v01.md
```

The file is plain Markdown containing the full VFX prompt text (from
`Asset preparation:` through `Quality and constraints:`), human-readable and
shareable without parsing YAML frontmatter.

## Step 8 — Report results

After completion, report to the user:

| Field | Source |
|---|---|
| **Status** | `succeeded` / `failed` |
| **Local file path** | `projects/<project>/scenes/scene-NN/sNN_shNNN/<file>.mp4` |
| **Artifact URI** | `seed-media://artifacts/<id>` (MCP artifact store) |
| **Task ID** | From MCP response |
| **Cost** | `cost_usd` from MCP response |
| **Tokens** | `completion_tokens` from MCP response |
| **Resolution** | Confirmed 4K (3840×2160) |
| **Duration** | Actual output duration |
| **Last frame** | Path to saved last-frame PNG (if `return_last_frame=true`) |
| **Latency** | Wall-clock time from submit to succeeded |
| **Manifest** | `projects/<project>/scenes/scene-NN/sNN_shNNN/shot.md` |

If the task failed, report:
- The `error` field from the MCP response
- The `task_id` for support reference
- Suggested retry action (fix prompt, change reference, resubmit)

## Error handling

| Error | Cause | Action |
|---|---|---|
| Content safety rejection | Source clip or prompt flagged by moderation | Review source clip content; simplify the `New world:` description; remove any borderline language |
| `OutputVideoSensitiveContentDetected.PolicyViolation` ("copyright restrictions") | Output resembles a film/photo cliché (interrogation room, a figure arguing in the rain) | Soften trope wording (e.g. "arguing" → "talking into his phone"); resubmit once; record the failed task. Never retry the identical prompt |
| `resource download failed` (`InvalidParameter` on the video reference) | Presigned reference URL expired or a transient fetch failure | Call `media_presign` with the recorded `object_key` for a fresh URL and resubmit |
| Invalid reference format | Video URL unreachable, image not valid PNG/JPEG | Verify file paths; re-encode images as PNG; use `kind: "base64"` for local files |
| Prompt too long | Exceeds 32,000 character limit (the MCP `seedance_create_task` video-generation tool accepts up to 32,000 characters) | Condense `New world:` and `Lighting:` sections; remove redundant detail |
| Task timeout / expired | `execution_expires_after` too short | Resubmit with `execution_expires_after: 7200` (2 hours) |
| Face warp in output | Resolution too low or face protection not in constraints | Ensure `resolution: "4k"` and face protection guard is present; resubmit |
| Camera motion drift | Camera lock too vague in `Locks:` | Specify exact motion type (handheld bob, lateral sway, tracking speed) and add "frame-for-frame" lock; resubmit |

Always surface the `task_id` in error reports — it is the reference for support
and debugging.

## Cost considerations

VFX shots using Seedance 2.0 at 4K with audio are the **most expensive**
generation mode in the workspace. Each 4K VFX take costs significantly more than
a 1080p text-to-video take.

Seedance 2.5 at 720p is cheaper per generation but cannot produce 4K output — use 2.5 for structured editing and extension, 2.0 for 4K face protection.

Guidelines:
- **Default to a single take** (`t01`) for VFX development. Generate multiple
  takes only for final selection.
- **Use `seedance_create_task_variations`** (1–5 parallel tasks) when the user
  wants multiple takes in one submission — but only for 1080p development
  iterations. For 4K final takes, submit sequentially to avoid bandwidth
  contention from large base64 payloads.
- **Never submit 4K VFX shots without explicit user confirmation** of the cost.
  State the expected per-take cost before submitting.
- **Cache and reuse** — if a take is approved, mark `status: approved` in the
  manifest. Do not regenerate approved takes.

## Shot chaining workflow

For multi-shot VFX sequences (e.g. a character walking through multiple
environments), chain shots using `return_last_frame`:

```mermaid
flowchart LR
    SRC1[Source clip 1] -->|seedance_create_task| SHOT1[Shot 1: VFX edit]
    SHOT1 -->|return_last_frame| LF1[Last frame PNG]
    LF1 -->|first_frame for Shot 2| SRC2[Source clip 2 + last frame]
    SRC2 -->|seedance_create_task| SHOT2[Shot 2: VFX edit]
    SHOT2 -->|return_last_frame| LF2[Last frame PNG]
    LF2 -->|first_frame for Shot 3| SRC3[Source clip 3 + last frame]
```

Chaining procedure:
1. Submit Shot 1 with `return_last_frame: true`.
2. On success, save the last-frame PNG to the shot directory.
3. For Shot 2, submit the source clip as `reference_video` AND the last-frame
   PNG as an image with `role: "first_frame"`.
4. In Shot 2's prompt `Asset preparation:` section, note that the first frame
   is inherited from Shot 1's last frame.
5. Repeat for each subsequent shot.

This ensures visual continuity across cuts — the environment and subject
position carry forward seamlessly.

## Pipeline checklist

Before declaring a VFX shot complete, verify:

- [ ] **Prompt written** — full natural-language heading structure, all applicable
      sections, VFX prompt checklist passed
- [ ] **4K resolution** — if faces or fine detail are present
- [ ] **`return_last_frame: true`** — if chaining to a subsequent shot
- [ ] **`generate_audio: true`** — native diegetic audio enabled
- [ ] **Task submitted** — `seedance_create_task` returned a `task_id`
- [ ] **Task polled** — `seedance_get_task` returned `status: succeeded`
- [ ] **Video saved locally** — asset in `scenes/scene-NN/sNN_shNNN/`
- [ ] **Last frame saved** — PNG alongside the video (if chaining)
- [ ] **`shot.md` manifest written** — full YAML frontmatter with model, prompt
      references, seed, params, cost, status, artifacts
- [ ] **Prompt file written** — one immutable `prompt_...md` snapshot beside
      the generated asset, linked by path and SHA-256 from `shot.md`
- [ ] **Cost recorded** — `cost_usd` and `billing_tokens_total` in manifest
- [ ] **Status set** — `review` (default), `approved`, or `rejected`
- [ ] **No secrets in manifest** — API keys, tokens, credentials never in
      frontmatter or prompt files
