# Seedance 2.5 (Video) Tools

Requires `BYTEPLUS_MODELARK_API_KEY`. Same auth scopes as 2.0.

Seedance 2.5 (`dreamina-seedance-2-5-260628`) is the newer, higher-capability model. Key differences from 2.0:

| Capability | Seedance 2.0 | Seedance 2.5 |
|---|---|---|
| Max duration | 15s | 30s |
| Max images | 9 | 30 |
| Max videos | 3 | 10 |
| Max audios | 3 | 10 |
| Resolution | 480p, 720p, 1080p, 4K | 480p, 720p, 1080p |
| Fast/Mini variants | Yes | No |
| Structured editing | No | Subject replacement, background replacement, audio editing |
| Forward/backward extension | No (manual `return_last_frame` chaining) | Yes (native) |
| Keyframe sequences | No | Yes |

**When to choose 2.5:** longer single-pass videos (up to 30s), richer multimodal references (30/10/10), structured editing, native extension, 1080p output.

**When to choose 2.0:** 4K output resolution, Fast/Mini speed variants, lower cost per generation.

#### `seedance_2_5_create_task`

Create an asynchronous Seedance 2.5 video generation task.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | `str` | No | Text prompt (up to 32,000 chars). Optional when media inputs are provided. |
| `images` | `list[SeedanceImageInput]` | No | Up to 30 images with roles: `first_frame`, `last_frame`, `reference_image`. Each entry may be a plain URL string or `{"url": ...}` |
| `videos` | `list[SeedanceVideoInput]` | No | Up to 10 videos with role: `reference_video`. Each entry may be a plain URL string or `{"url": ...}` |
| `audios` | `list[SeedanceAudioInput]` | No | Up to 10 audios with role: `reference_audio`. Audio-only input is supported (unique to 2.5). Each entry may be a plain URL string or `{"url": ...}` |
| `model` | `str` | No | Default: `dreamina-seedance-2-5-260628`. No Fast/Mini variants. |
| `resolution` | `"480p"` \| `"720p"` \| `"1080p"` | No | 2.5 supports 480p, 720p, and 1080p. 4k is not supported. |
| `ratio` | `str` | No | Aspect ratio (e.g. `16:9`, `9:16`). For `extend_video`, stripped (auto-locks to source) to prevent `InvalidParameter.TaskTypeConstraint`. For `edit`, auto-derived from input video. For first/last-frame, locks to first image. |
| `duration` | `int` | No | -1 (auto) to 30 seconds. Ignored for edit tasks (auto-derived from input video). |
| `omni_reference_task_type` | `str` | No | Task type hint. 2.5 values: `auto | reference | edit | extend` — `edit_video` is 2.0-only and is rejected. Default: `auto`. |
| `generate_audio` | `bool` | No | Whether to generate an audio track. |
| `watermark` | `bool` | No | Apply AIGC watermark. |
| `return_last_frame` | `bool` | No | Return the last frame as a separate image. |
| `execution_expires_after` | `int` | No | Max execution time in seconds (3600–259200). |
| `priority` | `int` | No | Task priority (0–9). |
| `safety_identifier` | `str` | No | Content safety tracking ID (max 64 chars). |

Returns `Seedance25CreateTaskOutput` with `task_id`, `status="queued"`, and `recommended_poll_after_ms`.

> **Audio-only input:** Unlike Seedance 2.0, 2.5 supports audio as the sole
> media input — a single BGM, voice, or sound-effect track can drive visual
> pacing, beat matching, and lip-sync without any image or video reference.

**Example — 30s text-to-video with native audio:**

```json
{
  "prompt": "A cinematic 30-second scene...",
  "model": "dreamina-seedance-2-5-260628",
  "resolution": "720p",
  "ratio": "16:9",
  "duration": 30,
  "generate_audio": true
}
```

#### `seedance_2_5_create_task_variations`

Create multiple Seedance 2.5 video tasks in parallel. Inherits all parameters from `seedance_2_5_create_task` and adds `variations` (1–5) and `variation_prompts`.

> **Shared lifecycle tools:** `seedance_get_task`, `seedance_list_tasks`, and
> `seedance_cancel_or_delete_task` work with both 2.0 and 2.5 task IDs. Use
> them the same way regardless of which create tool produced the task.

---
