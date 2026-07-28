---
name: modelark-mcp
description: Guide for using the ModelArk Seed Multimodal MCP server to generate or edit images, audio, and video, transcribe speech to text, poll and manage Seedance tasks, upload reference media to object storage (TOS or S3), and fetch persisted artifacts.
---

# ModelArk Seed Multimodal MCP Server

The ModelArk Seed MCP server exposes BytePlus multimodal generation through a
typed, safe MCP tool surface. It wraps multiple BytePlus AI product families
behind one server:

- **Seedream** — image generation and editing (text-to-image, reference-based
  editing, batch generation).
- **Seed Audio** — full-scene audio generation with voice cloning, subtitles,
  and watermarking.
- **Seedance** — asynchronous video generation with task-based lifecycle
  (create, poll, list, cancel/delete).
- **Speech-to-Text** — synchronous audio transcription via Seed Speech ASR.
- **Artifacts** — durable media access after provider URLs expire.
- **Object storage upload** — presigned URL generation for URL-only media
  workflows such as Seedance video references.

The server is built on FastMCP v3 and runs locally via `stdio` or as a
deployable Streamable HTTP service. Generated media is persisted to a local
artifact store with stable `seed-media://` resource URIs that survive provider
URL expiry (2 hours for audio, 24 hours for image/video).

## When To Use

Invoke this skill when the user wants to:

- generate or edit an image;
- generate audio, voice-clone from references, or request several variations;
- create, poll, list, cancel, or delete Seedance video tasks;
- transcribe audio or video into timestamped, speaker-diarized text;
- fetch a previously persisted artifact by ID;
- upload local or Base64 media to object storage (TOS or S3) to obtain a
  presigned HTTPS URL;
- verify which products are configured on the running server.

## Registration Model

Do not assume a fixed tool count. Registration is conditional on environment
variables. Tools for a product appear only when its API key is set; the server
gracefully degrades to whatever is configured.

### Always registered

- `seed_media_get_artifact`
- `seed-health://status` resource

### Requires `BYTEPLUS_SEED_AUDIO_API_KEY`

- `seed_audio_generate`
- `seed_audio_generate_variations`

### Requires `SEED_SPEECH_ASR_API_KEY`

- `speech_to_text`

### Requires `BYTEPLUS_MODELARK_API_KEY`

- `seedream_generate_image`
- `seedream_edit_image`
- `seedream_generate_image_variations`
- `seedance_create_task`
- `seedance_create_task_variations`
- `seedance_get_task`
- `seedance_list_tasks`
- `seedance_cancel_or_delete_task`

### Requires object storage credentials (TOS or S3)

- `media_upload`

---

## Quick Start

### Prerequisites

- Python 3.12+
- `uv` package manager
- BytePlus API keys for the products you intend to use

### Environment Variables

Copy `.env.example` to `.env` and configure at minimum:

```bash
BYTEPLUS_MODELARK_API_KEY=your-modelark-key   # required for Seedream + Seedance
BYTEPLUS_SEED_AUDIO_API_KEY=your-audio-key    # required for Seed Audio
SEED_SPEECH_ASR_API_KEY=your-asr-key          # required for Speech-to-Text
```

Optional object storage upload support (TOS default, S3 alternative):

```bash
# TOS backend (default)
TOS_ACCESS_KEY=your-ak
TOS_SECRET_KEY=your-sk
TOS_BUCKET=your-private-bucket

# S3 backend
S3_ACCESS_KEY=your-ak
S3_SECRET_KEY=your-sk
S3_BUCKET=your-private-bucket
OBJECT_STORAGE_BACKEND=s3
```

### Running

```bash
uv run modelark-mcp          # stdio transport (default, for local MCP clients)
MCP_TRANSPORT=http uv run modelark-mcp  # Streamable HTTP on 127.0.0.1:3000
```

Verify with the `seed-health://status` resource or the `/health`, `/ready`, or
`/metrics` HTTP endpoints.

---

## Tool Reference

All tools are Pydantic-validated and return structured outputs. Below is the
complete reference organized by product.

### Artifact Access

#### `seed_media_get_artifact`

Retrieve a persisted media artifact by its UUID as inline Base64 content. Use
when the client needs the artifact data directly rather than reading the
resource URI. Read-only, idempotent, ownership-checked. Requires
`artifacts:read` scope in JWT mode.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `artifact_id` | `str` | Yes | Artifact UUID from a previous generation call |

Returns `SeedMediaGetArtifactOutput` with `artifact_id`, `media_type`,
`mime_type`, `sha256`, `bytes`, optional `expires_at`, and Base64 `data`.

---

### Seed Audio Tools

Requires `BYTEPLUS_SEED_AUDIO_API_KEY`. Auth scope: `seed:audio:generate`.

#### `seed_audio_generate`

Generate a full-scene audio clip from a text prompt. Supports voice cloning via
audio references, optional image input for context-aware audio, subtitle
generation, and watermarking.

**Constraint:** `audio_references` and `image_reference` are mutually
exclusive.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `text_prompt` | `str` | Yes | 1–3000 characters |
| `audio_references` | `list[AudioReference]` | No | Up to 3 references (speaker ID, URL, or Base64) |
| `image_reference` | `MediaSource` | No | Image for context-aware audio |
| `output` | `AudioOutputOptions` | No | Format (wav/mp3/pcm/ogg), sample_rate, speech_rate, loudness_rate, pitch_rate, subtitle options |
| `watermark` | `AudioWatermarkOptions` | No | Enable watermark and optional metadata |
| `persist` | `bool` | Yes (default `true`) | Persist to artifact store |

Returns `SeedAudioGenerateOutput` with `artifact: ArtifactRef`,
`duration_seconds`, `billing_duration_seconds`, optional `subtitle`,
`request_id`, `provider_log_id`, optional `source_url`.

**Example — basic audio generation:**

```json
{
  "text_prompt": "A gentle rain falling on a tin roof, with distant thunder rumbling every few seconds",
  "output": {
    "format": "wav",
    "sample_rate": 44100
  },
  "persist": true
}
```

**Example — voice cloning with a speaker ID:**

```json
{
  "text_prompt": "Hello, welcome to our presentation. Today we will discuss the quarterly results.",
  "audio_references": [
    { "kind": "speaker", "speaker_id": "zh_female_qingxin" }
  ],
  "output": {
    "format": "mp3",
    "subtitle": true,
    "subtitle_type": "word"
  },
  "persist": true
}
```

#### `seed_audio_generate_variations`

Generate 1–5 audio variations in parallel. Each variation is an independent
generation (no seeds are supported for audio).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `text_prompt` | `str` | Yes | Base prompt (1–3000 chars) |
| `variations` | `int` | Yes | 1–5 |
| `variation_prompts` | `list[str]` | No | Per-variation prompts (one per variation) |
| All other audio params | — | No | Same as `seed_audio_generate` |

Returns `SeedAudioVariationsOutput` with `VariationSummary` (total, succeeded,
failed, per-variation results with partial failure capture).

**Example — 3 variations with per-variation prompts:**

```json
{
  "variation_prompts": [
    "A calm ocean waves soundscape",
    "A busy city street ambient noise",
    "A quiet forest with birds chirping"
  ],
  "variations": 3,
  "output": { "format": "mp3" },
  "persist": true
}
```

---

### Seedream (Image) Tools

Requires `BYTEPLUS_MODELARK_API_KEY`. Auth scope: `seedream:generate`.

#### `seedream_edit_image`

Interactive image editing with spatial precision. Supports point-based and
bounding-box editing through structured coordinate inputs. At least one
reference image and one coordinate (point or bbox) are required.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | `str` | Yes | 1–4000 characters. Natural-language edit instruction. |
| `images` | `list[MediaSource]` | Yes | Reference images to edit (at least 1). |
| `point` | `EditCoordinate` | No* | Point coordinate `{x, y}` (0–999). *Required if bbox not provided. |
| `bbox` | `EditBbox` | No* | Bounding-box `{x1, y1, x2, y2}` (0–999). *Required if point not provided. |
| All other image params | — | No | Same as `seedream_generate_image` |

Returns `SeedreamEditOutput` with `artifacts: list[ArtifactRef]` and
`usage: SeedreamUsage`.

**Example — replace an object near a point:**

```json
{
  "prompt": "Replace the object with a crown.",
  "images": [{"kind": "url", "url": "https://example.com/photo.png"}],
  "point": {"x": 520, "y": 460}
}
```

**Example — replace a region with a bounding box:**

```json
{
  "prompt": "Replace with a garden.",
  "images": [{"kind": "url", "url": "https://example.com/photo.png"}],
  "bbox": {"x1": 120, "y1": 180, "x2": 640, "y2": 760}
}
```

Coordinates are normalized to 0–999 (top-left = `0,0`, bottom-right =
`999,999`). Convert pixel coordinates: `normalized = round(pixel / dimension * 1000)`.

---

#### `seedream_generate_image`

Generate images from text prompts. Supports text-to-image, reference-based
generation, batch generation (Lite/4x models), seed-based reproducibility, and
prompt optimization. For interactive editing with spatial coordinates, use
`seedream_edit_image` instead.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | `str` | Yes | 1–4000 characters |
| `images` | `list[MediaSource]` | No | Reference images for editing |
| `model` | `str` | No | Model ID. Default: `dola-seedream-5-0-pro-260628` (Pro). Lite and 4x IDs are configured via `SEEDREAM_MODEL_BINDINGS`. |
| `size` | `str` | No | e.g. `1024x1024` |
| `seed` | `int` | No | -1 to 2147483647; -1 = client-randomized |
| `max_images` | `int` | No | 1–15 (batch for Lite/4x models only) |
| `output_format` | `"png"` \| `"jpeg"` | No | Default: `png` |
| `response_format` | `"url"` \| `"b64_json"` | No | Default: `url` |
| `watermark` | `bool` | No | Provider watermark |
| `prompt_optimization` | `"standard"` \| `"fast"` | No | Prompt enhancement |
| `persist` | `bool` | Yes (default `true`) | Persist to artifact store |

Returns `SeedreamGenerateOutput` with `artifacts: list[ArtifactRef]` and
`usage: SeedreamUsage`.

**Example — text-to-image:**

```json
{
  "prompt": "A serene mountain landscape at sunset, digital art style",
  "size": "1024x1024",
  "output_format": "jpeg",
  "persist": true
}
```

**Example — image editing with a reference:**

```json
{
  "prompt": "Change the background to a beach scene while keeping the subject unchanged",
  "images": [
    { "kind": "url", "url": "https://cdn.example.com/original.png" }
  ],
  "size": "1024x1024",
  "persist": true
}
```

**Example — reproducible generation with a seed:**

```json
{
  "prompt": "A cat sitting on a windowsill looking outside",
  "seed": 42,
  "size": "1024x1024",
  "persist": true
}
```

#### `seedream_generate_image_variations`

Generate 1–10 image variations in parallel. Each variation gets a distinct
seed, making every result different. Supports per-variation prompts and
deterministic seed sequences.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | `str` | Yes | Base prompt (1–4000 chars) |
| `variations` | `int` | Yes | 1–10 |
| `variation_prompts` | `list[str]` | No | Per-variation prompts |
| `base_seed` | `int` | No | None=random, -1=client-randomized, N=deterministic sequence |
| All other image params | — | No | Same as `seedream_generate_image` |

Returns `SeedreamVariationsOutput` with `VariationSummary`.

**Example — 4 variations with deterministic seeds:**

```json
{
  "prompt": "A futuristic city skyline, cyberpunk aesthetic",
  "variations": 4,
  "base_seed": 100,
  "size": "1024x1024",
  "persist": true
}
```

This produces 4 images with seeds [100, 101, 102, 103].

**Example — per-variation seasonal prompts:**

```json
{
  "variation_prompts": [
    "A cat in spring, cherry blossoms",
    "A cat in summer, sunny garden",
    "A cat in autumn, fallen leaves",
    "A cat in winter, snow"
  ],
  "variations": 4,
  "persist": true
}
```

---

### Seedance (Video) Tools

Requires `BYTEPLUS_MODELARK_API_KEY`. Auth scopes: `seedance:create`,
`seedance:read`, `seedance:delete`.

Video generation is **asynchronous**. You create a task, then poll for
completion. Tasks transition through states:

```text
queued -> running -> succeeded | failed | cancelled | expired
```

#### `seedance_create_task`

Create an async video generation task. Returns a task ID for subsequent
polling.

**Constraints:**
- At least one of `prompt`, `images`, or `videos` is required.
- Audio references cannot be the sole media input; at least one image or
  video must accompany audio.
- Text-only (prompt with no media) is supported for pure text-to-video.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | `str` | No | 1–32,000 characters. BytePlus recommends staying under 1,000 words for focus; that recommendation is not a hard API limit. |
| `images` | `list[SeedanceImageInput]` | No | Up to 9 images with roles: `first_frame`, `last_frame`, `reference_image` |
| `videos` | `list[SeedanceVideoInput]` | No | Up to 3 videos with role: `reference_video` |
| `audios` | `list[SeedanceAudioInput]` | No | Up to 3 audios with role: `reference_audio` |
| `model` | `str` | No | Model ID. Default: `dreamina-seedance-2-0-260128` (Standard). Fast and Mini IDs are configured via `SEEDANCE_MODEL_BINDINGS`. |
| `resolution` | `"480p"` \| `"720p"` \| `"1080p"` \| `"4k"` | No | |
| `ratio` | `str` | No | Aspect ratio |
| `duration` | `int` | No | -1 to 15 seconds |
| `generate_audio` | `bool` | No | Generate audio track |
| `watermark` | `bool` | No | Provider watermark |
| `return_last_frame` | `bool` | No | Include last frame image in output |
| `execution_expires_after` | `int` | No | 3600–259200 seconds |
| `priority` | `int` | No | 0–9 |
| `safety_identifier` | `str` | No | Max 64 characters |

Returns `SeedanceCreateTaskOutput` with `task_id`, `status="queued"`, and
`recommended_poll_after_ms`.

**Example — text-to-video:**

```json
{
  "prompt": "A drone flying over a tropical island, crystal clear water, aerial view",
  "resolution": "1080p",
  "duration": 8,
  "generate_audio": true
}
```

**Example — image-to-video with first and last frame:**

```json
{
  "prompt": "Smooth transition between the two scenes",
  "images": [
    { "role": "first_frame", "kind": "url", "url": "https://cdn.example.com/start.png" },
    { "role": "last_frame", "kind": "url", "url": "https://cdn.example.com/end.png" }
  ],
  "resolution": "720p",
  "duration": 5
}
```

#### `seedance_create_task_variations`

Create 1–5 video generation tasks in parallel. Each variation creates a
separate task.

| Parameter | Type | Required | Description |
|---|---|---|---|
| Same as `seedance_create_task` | — | — | — |
| `variations` | `int` | Yes | 1–5 |
| `variation_prompts` | `list[str]` | No | Per-variation prompts |

Returns `SeedanceVariationsOutput` with per-variation task IDs and
`recommended_poll_after_ms` values.

#### `seedance_get_task`

Retrieve the status and output of a video generation task. On success,
automatically persists the video (and optional last frame) to the artifact
store. Results are cached for 24 hours.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | `str` | Yes | Task ID from `seedance_create_task` |
| `persist_output` | `bool` | Yes (default `true`) | Persist to artifact store |

Returns `SeedanceTaskOutput` with `task_id`, `model`, `created_at`,
`updated_at`, `status`, optional `error`, optional `video: ArtifactRef`,
optional `last_frame: ArtifactRef`, optional `usage`, `settings`.

**Typical polling pattern:**

```json
{"task_id": "task_abc123", "persist_output": true}
```

Call this repeatedly (respecting the `recommended_poll_after_ms` from
creation) until `status` is `succeeded`, `failed`, `cancelled`, or `expired`.

#### `seedance_list_tasks`

List recent video generation tasks (last 7 days). Supports filtering by status,
model, and service tier.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `page` | `int` | No | 1–500 |
| `page_size` | `int` | No | 1–100 |
| `status` | `SeedanceTaskStatus` | No | Filter by status |
| `task_ids` | `list[str]` | No | Filter by specific task IDs |
| `model` | `str` | No | Filter by model |
| `service_tier` | `"default"` \| `"flex"` | No | Filter by tier |

Returns `SeedanceTaskPage` with paginated task summaries.

#### `seedance_cancel_or_delete_task`

Cancel a queued task or delete a terminal task. **Destructive** — requires
explicit confirmation.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | `str` | Yes | Task to act on |
| `mode` | `"cancel"` \| `"delete"` | Yes | Action to perform |
| `expected_status` | `SeedanceTaskStatus` | Yes | Must match current status |
| `confirm` | `Literal[true]` | Yes | Must be `true` |

- `mode=cancel` + `expected_status=queued`: Cancel a pending task.
- `mode=delete` + `expected_status=succeeded|failed|expired`: Delete a completed
  task.

Returns `SeedanceCancelOrDeleteOutput`.

---

### Speech-to-Text

Requires `SEED_SPEECH_ASR_API_KEY`. Auth scope: `seed:asr:transcribe`.

#### `speech_to_text`

Transcribe audio to text via Seed Speech ASR (synchronous HTTP). The tool
internally submits the audio to the provider, polls until complete, and
returns the full result in a single call — no task ID, no object-storage
upload, no second tool required.

The call is capped by `SEED_SPEECH_ASR_POLL_MAX_SECONDS` (default 600s).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `audio` | `AsrAudioInput` | Yes | Audio source (see below) |
| `options` | `AsrRequestOptions` | No | Transcription feature toggles |

**`AsrAudioInput`** (provide exactly one source):

| Field | Type | Required | Description |
|---|---|---|---|
| `audio_url` | `str` | No* | HTTPS URL of the audio file |
| `audio_data` | `str` | No* | Base64-encoded audio bytes. Mutually exclusive with other inputs. |
| `audio_file_path` | `str` | No* | Absolute local file path. stdio transport only. Mutually exclusive with other inputs. |
| `audio_format` | `"wav"` \| `"mp3"` \| `"ogg"` \| `"raw"` \| `"flac"` | Yes | Audio format |

**`AsrRequestOptions`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `language` | `str` | No (default `en-US`) | BCP-47 language code |
| `enable_punc` | `bool` | No | Enable punctuation |
| `enable_itn` | `bool` | No | Enable ITN |

Returns `SpeechToTextOutput` with `result: TranscriptionResult` and optional
`log_id`. `TranscriptionResult` includes `text` (full transcript),
`utterances` (with word-level timestamps and speaker labels), and
`duration_ms`.

Transcription output is text — no artifact persistence needed.

---

### Object Storage Upload

Requires object storage credentials (TOS or S3). No auth scope in stdio mode.

#### `media_upload`

Upload media to object storage (TOS or S3) and receive a presigned HTTPS URL.
Especially useful for URL-only workflows such as Seedance video references,
which cannot be inlined as Base64.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `media_type` | `"image"` \| `"audio"` \| `"video"` | Yes | Media category for MIME and size validation |
| `mime_type` | `str` | Yes | e.g. `video/mp4`, `image/png`, `audio/wav` |
| `data` | `str` | No* | Base64-encoded media bytes. Mutually exclusive with `file_path`. |
| `file_path` | `str` | No* | Absolute path to a local file. stdio transport only. Mutually exclusive with `data`. |
| `key_prefix` | `str` | No | Object key prefix (default `references`). Alphanumeric, `-`, `_`, `/` only. |

Returns `MediaUploadOutput` with `url`, `expires_at`, `object_key`, `bytes`.

**Example — upload a local video for use as a Seedance reference:**

```json
{
  "media_type": "video",
  "mime_type": "video/mp4",
  "file_path": "/absolute/path/clip.mp4"
}
```

**Example — upload Base64 audio:**

```json
{
  "media_type": "audio",
  "mime_type": "audio/wav",
  "data": "UklGRiQAAABXQVZFZm10..."
}
```

---

## Resources

The server exposes two MCP resources:

### `seed-media://artifacts/{artifact_id}`

Retrieves a persisted media artifact by its UUID. Requires `artifacts:read`
scope in JWT mode. Returns the media content with the correct MIME type.

Artifacts are the durable, locally-persisted copies of generated media. Provider
URLs expire (2h for audio, 24h for image/video), but artifacts survive for 7
days (configurable via `ARTIFACT_TTL_SECONDS`). Always use `persist=true` (the
default) and reference the returned `ArtifactRef.uri` for long-lived access.

### `seed-health://status`

Returns a health summary with no authentication required. Lists which products
are configured (ModelArk, Seed Audio, Seed Speech ASR, object storage), the
artifact backend, and the active transport.

---

## Architecture

### Three-Provider Design

The server normalizes three distinct BytePlus API surfaces:

| Provider | Auth | Base URL | Products |
|---|---|---|---|
| **ModelArk** | `Authorization: Bearer <key>` | `https://ark.ap-southeast.bytepluses.com/api/v3` | Seedream, Seedance |
| **Seed Speech (TTS)** | `X-Api-Key: <key>` | `https://voice.ap-southeast-1.bytepluses.com` | Seed Audio |
| **Seed Speech (ASR)** | `X-Api-Key: <key>` (separate key) | `https://voice.ap-southeast-1.bytepluses.com` | Speech-to-Text |

ModelArk and Seed Speech ASR use separate API keys even though ASR shares the
host with TTS. Tools for a product are only registered when its provider API
key is set.

### Runtime Services

Each server process maintains shared runtime services:

- **Artifact Store** — Filesystem-backed durable media persistence with
  ownership metadata and TTL-based cleanup.
- **Budget Ledger** — SQLite-backed per-principal daily spend tracking.
- **Task Ownership Store** — SQLite-backed task ID to principal mapping for
  Seedance ownership enforcement.
- **Provider Limiters** — Dual-layer concurrency control: per-provider (default
  5) and per-principal (default 3) semaphores.
- **Safe Downloader** — SSRF-safe URL downloads with IP pinning and redirect
  validation.

### Model Capability Registry

The server validates inputs against known model capabilities before spending
quota. Six model families, with these default model IDs:

| Family | Default Model ID | Key Traits |
|---|---|---|
| **Seedream Pro** | `dola-seedream-5-0-pro-260628` | 10 refs, no batch, PNG/JPEG |
| **Seedream Lite** | *(configured via `SEEDREAM_MODEL_BINDINGS`)* | 14 refs, batch, streaming, PNG/JPEG |
| **Seedream 4.x** | *(configured via `SEEDREAM_MODEL_BINDINGS`)* | 14 refs, batch, streaming, JPEG only |
| **Seedance 2 Standard** | `dreamina-seedance-2-0-260128` | 9 imgs / 3 vids / 3 audios, 480p–4K, 0–15s |
| **Seedance 2 Fast** | *(configured via `SEEDANCE_MODEL_BINDINGS`)* | 480p, 720p only |
| **Seedance 2 Mini** | *(configured via `SEEDANCE_MODEL_BINDINGS`)* | 480p, 720p only |

Custom model IDs must be explicitly bound via `SEEDREAM_MODEL_BINDINGS` or
`SEEDANCE_MODEL_BINDINGS` JSON. When a client omits the `model` parameter, the
default model for that product is used.

---

## Usage Patterns

### Standard Generation Workflow

1. Call the generate tool with `persist=true` (default).
2. The tool returns an `ArtifactRef` with `uri` (e.g.
   `seed-media://artifacts/abc123`).
3. Use the artifact URI as a stable reference to the media. The artifact
   survives provider URL expiry.

### Seedance Async Workflow

1. Call `seedance_create_task` to create a task.
2. Immediately persist the returned `task_id`, request parameters, prompt hash,
   and intended output path to the shot manifest before polling.
3. Poll `seedance_get_task` with the persisted `task_id` until the status is terminal.
   Respect the `recommended_poll_after_ms` from the creation response.
4. On a local timeout, disconnect, or client restart, retrieve and continue
   polling the same task. Do not submit a replacement task because the provider
   may still be running and a resubmission can create duplicate cost.
5. On success, the video is automatically persisted to the artifact store.
   Download it to the project asset path and record artifact ID, byte size,
   SHA-256, provider timestamps, and usage.
6. Optionally call `seedance_list_tasks` to browse recent tasks.
7. Call `seedance_cancel_or_delete_task` only when cleanup is explicitly wanted.

### URL-only Video References

1. If the user has Base64 video or a local video file, call `media_upload`.
2. Pass the returned presigned HTTPS URL into `seedance_create_task` as a
   video reference.

### Speech-to-Text Transcription

Call `speech_to_text` with an audio URL, Base64, or local file path (stdio
only). The tool returns the complete `TranscriptionResult` in a single
synchronous call — no task ID, no polling, no object-storage upload required.

Use `TranscriptionResult.text` for the full transcript, or `utterances` /
`words` for timestamped segments and speaker labels.

### Generation Record Lifecycle

Use explicit manifest states so a generated take is never mistaken for an
approved take:

`ready → submitted → queued/running → review → approved/rejected`

Use `failed`, `cancelled`, or `expired` for terminal failures. While a take is
under review, record it under `outputs` or `generated_output`; reserve
`selected_variant` and `approved` for an explicit user choice.

If the provider returns null or incomplete settings, keep the submitted request
as the source of intended parameters and use media inspection as the source of
actual output properties.

### Post-generation Media QA

After downloading a Seedance result:

1. Use `ffprobe` to record actual resolution, duration, frame rate, codecs,
   pixel format, and audio streams.
2. Decode the full file with FFmpeg and fail QA on any decode error.
3. Generate contact sheets around the opening, major transitions, and ending.
4. Check story acceptance criteria such as subject order, travel direction,
   boundary behavior, forbidden elements, and final location.
5. When audio is enabled, verify the audio stream and inspect important dynamic
   segments rather than inferring sound quality from the request.
6. Set the manifest to `review`; only the user can provide creative approval.
7. For HEVC or other review-host-sensitive masters, optionally generate a
   lightweight H.264 proxy while preserving the original master.

### Parallel Variations

Use variation tools when you want to give the user multiple options:

- `seedream_generate_image_variations` — up to 10 distinct images in one call.
- `seed_audio_generate_variations` — up to 5 audio clips in one call.
- `seedance_create_task_variations` — up to 5 parallel video tasks.

Each variation is independent. Partial failures are captured — if 4 of 5
succeed, the tool returns 4 results and 1 error. The `VariationSummary` reports
`total`, `succeeded`, and `failed` counts.

### Deterministic Reproduction

For Seedream images, pass a `seed` to reproduce the same output with the same
prompt. For variation tools, pass `base_seed` to get a deterministic sequence
(e.g., `base_seed=100` with `variations=4` produces seeds [100, 101, 102,
103]).

### Image Editing

For interactive, coordinate-based editing, use `seedream_edit_image` with
structured `point` or `bbox` coordinates. The tool constructs the `<point>`
and `<bbox>` markup automatically. Do not force point or bbox logic into
`seedream_generate_image`.

For reference-based generation without spatial targeting, use
`seedream_generate_image` with the `images` parameter.

---

## Error Handling

### Provider Errors

Provider errors are normalized into `ProviderError` with a structured message.
The error includes the provider's HTTP status, error code, and a human-readable
description.

### Retry Policy

The server retries only explicitly retryable, non-ambiguous errors:
- Connection/transport errors are retried (up to 3 attempts with exponential
  backoff and jitter: 0.25s base, 4s max).
- Timeouts are NOT retried (the operation may have succeeded server-side).
- Provider errors with `retryable=true` are retried.

For Seedance task polling, a local watcher timeout is not a generation failure.
Resume `seedance_get_task` with the existing task ID. Only create a new task
after the previous task reaches a terminal state and the user requests another
take.

For `speech_to_text`, the synchronous call blocks until transcription completes
or the `SEED_SPEECH_ASR_POLL_MAX_SECONDS` cap is reached. A timeout does not
produce a partial result.

### Budget Rejections

If `DAILY_BUDGET_USD` is configured (non-zero), the server tracks per-principal
daily spend. Requests exceeding the budget are rejected with a clear message.
Set to `0` (default) for record-only mode with no enforcement.

### Common Issues

| Symptom | Cause | Resolution |
|---|---|---|
| Tool not appearing | Missing API key | Set the corresponding `BYTEPLUS_*` or `SEED_SPEECH_ASR_*` env var |
| Model not found | Unbound custom model ID | Add to `*_MODEL_BINDINGS` JSON |
| URL expired | Provider URL TTL elapsed | Use `persist=true` and reference `ArtifactRef.uri` |
| Auth error (JWT mode) | Missing or invalid token | Check JWT configuration and scopes |
| Budget rejected | Daily limit exceeded | Wait for UTC day rollover or increase budget |
| `speech_to_text` timeout | ASR poll cap reached | Increase `SEED_SPEECH_ASR_POLL_MAX_SECONDS` or provide shorter audio |
| `media_upload` not available | Missing TOS/S3 credentials | Set `TOS_*` or `S3_*` env vars and `OBJECT_STORAGE_BACKEND` |

---

## Best Practices

1. **Always persist.** Set `persist=true` (the default) so generated media
   survives provider URL expiry. Reference the returned `ArtifactRef.uri` for
   durable access.

2. **Poll with backoff for Seedance.** Use the `recommended_poll_after_ms`
   from `seedance_create_task` output. Don't poll faster than the interval — it
   wastes quota and can hit rate limits.

3. **Make polling resumable.** Save the task ID and request metadata before the
   first poll. A process timeout must continue the existing task, not create a
   duplicate.

4. **Use variation tools for choice.** When the user needs options (e.g., "show
   me a few versions"), use a variation tool rather than calling the single
   generate tool multiple times. Variations run in parallel and handle partial
   failures gracefully.

5. **Set seeds for reproducibility.** When the user wants consistent or
   reproducible output, pass a fixed `seed` to `seedream_generate_image` or a
   `base_seed` to `seedream_generate_image_variations`.

6. **Check health first.** Call `seed-health://status` to verify which products
   are configured before attempting generation.

7. **Respect model capabilities.** Different models support different features
   (batch generation, resolutions, reference counts). Check the capability
   registry before passing unsupported parameters.

8. **Clean up Seedance tasks.** Use `seedance_cancel_or_delete_task` to clean up
   completed or queued tasks when they are no longer needed.

9. **Validate input sizes.** Audio and image references are limited to 10 MiB
   each; video references are limited to 200 MiB. Base64 inputs are validated
   before submission.

10. **Treat cost estimates as estimates.** Record estimated cost separately
    from confirmed billing and usage. Do not infer actual cost solely from a
    preflight estimate when resolution or token usage differs.

11. **Verify the saved media.** Provider task success proves generation
    completed, not that resolution, audio, narrative continuity, or playback
    compatibility satisfy the production brief.

12. **Use `media_upload` for URL-only workflows.** Seedance video references
    are URL-only. When starting with a local or Base64 video, upload it first
    and pass the presigned URL into `seedance_create_task`.

13. **`speech_to_text` is synchronous.** It blocks until transcription completes
    or the poll cap is reached. Provide appropriately sized audio and plan for
    the blocking duration.

---

## Environment Essentials

### Provider Credentials

- `BYTEPLUS_MODELARK_API_KEY` — enables Seedream and Seedance
- `BYTEPLUS_SEED_AUDIO_API_KEY` — enables Seed Audio (TTS)
- `SEED_SPEECH_ASR_API_KEY` — enables Speech-to-Text (ASR)
- `BYTEPLUS_MODELARK_BASE_URL` — override ModelArk data-plane host
- `BYTEPLUS_SEED_AUDIO_BASE_URL` — override Seed Audio host
- `SEED_SPEECH_ASR_BASE_URL` — override ASR host
- `SEED_SPEECH_ASR_POLL_INTERVAL_SECONDS` — seconds between ASR query polls (default 3)
- `SEED_SPEECH_ASR_POLL_MAX_SECONDS` — maximum total seconds to wait for ASR result (default 600)

### Model Selection

- `SEEDREAM_DEFAULT_MODEL`
- `SEEDANCE_DEFAULT_MODEL`
- `SEEDREAM_MODEL_FAMILY`
- `SEEDANCE_MODEL_FAMILY`
- `SEEDREAM_MODEL_BINDINGS`
- `SEEDANCE_MODEL_BINDINGS`

Use bindings when a custom model ID is not one of the built-in defaults.

### Transport and Auth

- `MCP_TRANSPORT` or `FASTMCP_TRANSPORT`
- `MCP_HOST` or `FASTMCP_HOST`
- `MCP_PORT` or `FASTMCP_PORT`
- `MCP_AUTH_MODE`
- `MCP_JWT_JWKS_URI`
- `MCP_JWT_ISSUER`
- `MCP_JWT_AUDIENCE`
- `MCP_TENANT_CLAIM`

### Persistence and Runtime

- `ARTIFACT_BACKEND`
- `ARTIFACT_DIR`
- `ARTIFACT_TTL_SECONDS`
- `MCP_INLINE_MEDIA_MAX_BYTES`
- `MCP_HTTP_MAX_BODY_BYTES`
- `PROVIDER_MAX_CONCURRENCY`
- `PRINCIPAL_MAX_CONCURRENCY`
- `DAILY_BUDGET_USD`
- `MODELARK_LOG_LEVEL`

### Object Storage

- `TOS_ACCESS_KEY`
- `TOS_SECRET_KEY`
- `TOS_SECURITY_TOKEN`
- `TOS_BUCKET`
- `TOS_REGION`
- `TOS_ENDPOINT`
- `TOS_PRESIGN_TTL_SECONDS`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET`
- `S3_REGION`
- `S3_ENDPOINT`
- `S3_PRESIGN_TTL_SECONDS`
- `OBJECT_STORAGE_BACKEND`
