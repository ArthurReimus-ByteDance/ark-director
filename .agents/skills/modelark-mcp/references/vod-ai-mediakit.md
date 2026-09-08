# VOD AI MediaKit

Requires `BYTEPLUS_VOD_MEDIAKIT_API_KEY`. Auth scopes: `vod:enhance`,
`vod:transcode`, `vod:read`.

#### `vod_enhance_video`

Enhance a public HTTPS video using the exact currently supported profile. The
operation is asynchronous, mutating, non-idempotent, and open-world. Do
not retry it automatically: a timeout may be ambiguous after provider work has
started, and there is no MediaKit polling tool in the current integration.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `video_url` | URL | Yes | Public HTTPS source; private/link-local targets rejected |
| `scene` | `"common"` | No | Fixed current scene profile |
| `tool_version` | `"professional"` | No | Fixed current enhancement profile |
| `resolution` | `"4k"` | No | Fixed current output resolution |
| `bitrate_level` | `"high"` | No | Fixed current bitrate profile |
| `fps` | `24` | No | Fixed current frame rate |
| `project` | string | No | Defaults to `default`; sent upstream as `Project` |
| `input_duration_seconds` | number | No | Reserved; no price estimate is currently produced |
| `persist` | boolean | No | Best-effort durable artifact copy; default `true` |

The verified response is `status="accepted"` with a task ID. No Bearer-surface
polling route is verified for enhancement, so do not substitute the transcode or
audio-separation tools (which do have polling routes) for enhancement results.
If a completed response supplies `source_url`, retain it even when the best-effort
copy fails. `persistence` is `not_applicable`, `persisted`, `failed`, or `not_requested`; durable
video copies are capped at 200 MiB. `estimated_cost_usd` remains null until
convenience-endpoint pricing and billing-unit mapping are confirmed.

#### `vod_transcode_video`

Submit an asynchronous video transcoding task. Mutating, non-idempotent,
open-world. Do not retry the POST automatically (a timeout may be ambiguous).
The request body and `video` object enums are verified from the official AI
MediaKit API reference. Defaults reproduce the verified portrait-to-720x720
letterbox profile (`scale_type=2`, `scale_width=720`, `scale_height=720`,
`scale_mode=2`).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `video_url` | URL | Yes | Public HTTPS source; private/link-local targets rejected |
| `container_format` | `"MP4"` \| `"FLV"` \| `"MPEGTS"` | No | Output container format; default `MP4` |
| `video` | object | No | See fields below |
| `persist` | boolean | No | Best-effort durable copy on later poll; default `true` |

`video` fields: `codec` (`h264`/`h265`, default `h264`); `scale_type` (`0`/`1`/`2`,
default `2`); `scale_mode` (`0`/`1`/`2`, default `2`); `scale_width`/`scale_height`
(px [0,4320], only when `scale_type=2`, default 720); `scale_short`/`scale_long`
(px [0,4320], only when `scale_type=1`); `bitrate_mode` (`crf`/`abr`/`cbr`, default
`crf`); `bitrate_crf` ([0,51], default 25); `bitrate_kbps` (kbps [10,50000],
default 2000); `fps_mode` (`vfr`/`cfr`, default `vfr`); `fps` ([1,240], unset keeps
source rate); `is_hdr_to_sdr` (default `true`).

Returns `status="accepted"` plus `task_id` and a heuristic
`recommended_poll_after_ms`. Poll with `vod_get_transcode_task`.

#### `vod_get_transcode_task`

Read-only poll of a transcode task (`vod:read`). Requires the `task_id` returned
by `vod_transcode_video`. Maps provider `running`→`processing`,
`completed`→`succeeded`, `failed`→`failed` (the provider documents no
queued/expired/cancelled statuses). On success, returns `source_url` (24-hour
lifetime) plus optional `duration_seconds`/`resolution`/`video_codec` and
normalized ISO-8601 `created_at`/`finished_at`/`source_expires_at`. With
`persist_output=true` (default), the completed output is copied once into the
durable artifact store (200 MiB cap) and cached by task ID so repeated polls do
not re-download; a persistence failure never erases provider success. On
failure, `error` carries the safe provider detail.

---
