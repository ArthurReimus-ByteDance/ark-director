# VOD AI MediaKit audio separation

Requires `BYTEPLUS_VOD_MEDIAKIT_API_KEY` (same Bearer key as enhancement and
transcoding). Auth scopes: `vod:extract` (submit) and `vod:read` (poll).

#### `vod_separate_audio`

Submit an asynchronous voice and background audio separation task
(`POST /api/v1/tools/separate-voice`). Mutating, non-idempotent, open-world —
do not retry the POST automatically (timeout/5xx means ambiguous completion).
The source is a public HTTPS URL (audio or video), exactly one of the two.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `audio_url` | URL | Exactly one of `audio_url`/`video_url` | Public HTTPS audio URL (mp3, m4a, wav) |
| `video_url` | URL | Exactly one of `audio_url`/`video_url` | Public HTTPS video URL (mp4, flv, ts, avi, mov, wmv, mkv) |
| `scene` | `"Audio"` \| `"Music"` \| `"Drama"` \| `"Narrate"` | No | Default `Audio`. `Audio`/`Music` = 2-track; `Drama`/`Narrate` = 3-track |
| `output_format` | `"aac"` \| `"mp3"` \| `"wav"` \| `"m4a"` \| `"flac"` | No | Default `aac` |

Returns `status="accepted"` plus `task_id`, `request_id`, and
`provider_log_id`. Poll with `vod_get_audio_separation`.

**Source URL liveness.** The provider downloads `audio_url`/`video_url`
asynchronously after submission, so the URL must stay fetchable until the
provider has downloaded it. A presigned URL (default 1800s / 30 min,
configurable 60–604800s via `TOS_PRESIGN_TTL_SECONDS`/`S3_PRESIGN_TTL_SECONDS`)
may expire before the provider fetches it, causing the task to fail. For VOD
inputs, upload via `media_upload` with `expires_in_seconds` (e.g. 3600) or use
a stable public URL.

#### `vod_get_audio_separation`

Read-only poll of a separation task (`vod:read`). Requires the `task_id`
returned by `vod_separate_audio`. Maps provider `running`→`processing`,
`completed`→`succeeded`, `failed`→`failed`. On success, `voice`, `background`,
`music`, and `sfx` each carry the track's expiring `source_url` (24-hour
lifetime) and, with `persist_output=true` (default), a durable `artifact`
reference copied once and cached by task ID. A persistence failure never erases
provider success. On failure, `error` carries the safe provider detail.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | Yes | Task ID returned by `vod_separate_audio` |
| `persist_output` | boolean | No | Best-effort durable copy on first successful poll; default `true` |

**Latency and transient failures.** A completed separation typically takes
tens of seconds but can take minutes; keep polling until a terminal state
rather than giving up after the first `processing` response. A provider
`failed` result with `error.code` `AbilityProcessingError` /
`InternalError` is usually transient — re-submit the same source rather than
treating the input as invalid.

---
