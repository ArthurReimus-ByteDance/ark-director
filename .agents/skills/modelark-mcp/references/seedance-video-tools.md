# Seedance (Video) Tools

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
| `images` | `list[SeedanceImageInput]` | No | Up to 9 images with roles: `first_frame`, `last_frame`, `reference_image`. Each entry may be a plain URL string or `{"url": ...}` (coerced to `role=reference_image`) |
| `videos` | `list[SeedanceVideoInput]` | No | Up to 3 videos with role: `reference_video`. Each entry may be a plain URL string or `{"url": ...}` |
| `audios` | `list[SeedanceAudioInput]` | No | Up to 3 audios with role: `reference_audio`. Each entry may be a plain URL string or `{"url": ...}` |
| `model` | `str` | No | Model ID. Default: `dreamina-seedance-2-0-260128` (Standard). Fast and Mini IDs are configured via `SEEDANCE_MODEL_BINDINGS`. |
| `resolution` | `"480p"` \| `"720p"` \| `"1080p"` \| `"4k"` | No | |
| `ratio` | `str` | No | Aspect ratio. For `extend_video`, stripped (auto-locks to source) to prevent `InvalidParameter.TaskTypeConstraint`. For `edit_video`, auto-derived from input video. For first/last-frame, locks to first image. |
| `duration` | `int` | No | -1 (auto) to 15 seconds. Ignored for edit tasks (auto-derived from input video) |
| `omni_reference_task_type` | `str` | No | Task type hint (e.g. `edit_video`, `extend_video`). Default: `auto`. Note: 2.0 `edit_video` output caps at ~5s in practice. |
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

#### Auto-locked parameters by task type

When the provider detects (or is hinted via `omni_reference_task_type`)
that the task is video editing, extension, or first/last-frame generation,
certain parameters are auto-derived from the input media and cannot be
overridden:

| Task type | Aspect ratio | Duration |
|---|---|---|
| Video editing | Locked to input video's ratio | Locked to input video's duration (±0.3s) |
| Video extension | Locked to input video's ratio | Set freely |
| First/last-frame generation | Locked to first image's ratio | Set freely |
| Text-to-video / standard reference | Set freely | Set freely (or `-1` for auto) |

For `extend_video`, any explicit `ratio` is client-stripped (logged as
`seedance_ratio_stripped_for_extension`) to prevent the provider from
rejecting the task with `InvalidParameter.TaskTypeConstraint`.

Use `omni_reference_task_type` to force a specific task type when
auto-detection is ambiguous (e.g. set to `"edit_video"` or
`"extend_video"`). When omitted, the provider defaults to `"auto"` which
infers the task type from the prompt and media inputs.

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
