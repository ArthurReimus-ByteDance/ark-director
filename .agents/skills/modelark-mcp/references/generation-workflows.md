## Usage Patterns

### Standard Generation Workflow

1. Persist the exact prompt snapshot and prepared request record before calling
   the generate tool with `persist=true` (default).
2. The tool returns an `ArtifactRef` with `uri` (e.g.
   `seed-media://artifacts/abc123`).
3. Download the artifact to the project-local asset path, record its SHA-256
   and bytes, and retain the artifact URI as supplementary recovery evidence.

### Seedance Async Workflow

1. Call `seedance_create_task` (2.0) or `seedance_2_5_create_task` (2.5) to create a task.
2. Immediately persist the returned `task_id`, request parameters, prompt hash,
   and intended output path to the single project task registry before polling.
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

> **Choosing 2.0 vs 2.5:** Use `seedance_2_5_create_task` when you need
> 30-second generation, 50 multimodal references, structured editing, or
> native extension. Use `seedance_create_task` for 4K or lower
> cost per task. The get/list/cancel tools are shared — `seedance_get_task`,
> `seedance_list_tasks`, and `seedance_cancel_or_delete_task` work with
> task IDs from either version.

### Seed 3D Async Workflow

1. Ensure `BYTEPLUS_MODELARK_3D_ENABLED=true` is set, along with
   `BYTEPLUS_MODELARK_API_KEY`.
2. Call `hyper3d_create_task` (text-to-3D or image-to-3D) or
   `hitem3d_create_task` (image-to-3D only) to create a task.
3. Persist the returned `task_id` before polling.
4. Poll `hyper3d_get_task` or `hitem3d_get_task` with the `task_id` until the
   status is terminal (`succeeded`, `failed`, `cancelled`, `expired`).
   Respect the `recommended_poll_after_ms` (5000ms) from creation.
5. On success, the 3D file (zip package) is automatically persisted to the
   artifact store with a 24-hour source URL backup. The durable artifact
   survives provider URL expiry. Download the package to the project-local
   asset path and record SHA-256, bytes and the provider artifact ID.
6. Call `hyper3d_list_tasks` or `hitem3d_list_tasks` to browse recent tasks.
7. Call `hyper3d_cancel_or_delete_task` or `hitem3d_cancel_or_delete_task`
   only when cleanup is explicitly wanted.

> **Choosing Hyper3D vs Hitem3d:** Use `hyper3d_create_task` for text-to-3D
> or when you need seeds, PBR materials, or custom mesh modes. Use
> `hitem3d_create_task` for image-to-3D with multi-view inputs and resolution
> control. The get/list/cancel tools are family-specific — use the
> `hyper3d_*` tools for Hyper3D task IDs and `hitem3d_*` tools for Hitem3d
> task IDs.

### URL-only Video References

1. If the user has Base64 video or a local video file, call `media_upload`.
2. Pass the returned presigned HTTPS URL into `seedance_create_task` or
   `seedance_2_5_create_task` as a video reference.

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
- `seedance_create_task_variations` (2.0) / `seedance_2_5_create_task_variations` (2.5) — up to 5 parallel video tasks.

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
