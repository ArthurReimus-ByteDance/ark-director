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

Exception: `vod_enhance_video`, `vod_transcode_video`, and `vod_separate_audio`
are never automatically retried. Their POSTs are non-idempotent and a transport
failure may have ambiguous completion. `vod_get_transcode_task` and
`vod_get_audio_separation` (read-only GET polls) ARE retried on provider-marked
retryable errors such as HTTP 429.

For Seedance task polling, a local watcher timeout is not a generation failure.
Resume `seedance_get_task` with the existing task ID. Only create a new task
after the previous task reaches a terminal state and the user requests another
take.

For Seed 3D task polling, the same principle applies — resume
`hyper3d_get_task` or `hitem3d_get_task` with the existing task ID after a
local timeout. Do not submit a replacement task.

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
| Tool not appearing | Missing API key | Set the corresponding `BYTEPLUS_*` env var |
| Model not found | Unbound custom model ID | Add to `*_MODEL_BINDINGS` JSON |
| URL expired | Provider URL TTL elapsed | Use `persist=true` and reference `ArtifactRef.uri` |
| Auth error (JWT mode) | Missing or invalid token | Check JWT configuration and scopes |
| Budget rejected | Daily limit exceeded | Wait for UTC day rollover or increase budget |
| `speech_to_text` timeout | ASR poll cap reached | Increase `SEED_SPEECH_ASR_POLL_MAX_SECONDS` or provide shorter audio |
| `speech_to_text` error code `20000003` | Silent audio — no speech detected, or a format mismatch (e.g. non-16 kHz/16-bit/mono WAV) decoded to silence | Verify the audio contains speech and matches the declared `audio_format`; re-submit with corrected audio |
| `media_upload` / `media_presign` / `media_presign_batch` not available | Missing TOS/S3 credentials | Set `TOS_*` or `S3_*` env vars and `OBJECT_STORAGE_BACKEND` |
| Presigned URL expired | TTL elapsed (default 30 min) | Call `media_presign` (single key) or `media_presign_batch` (many keys) with the `object_key` to generate a fresh URL |
| 3D tools not appearing | `BYTEPLUS_MODELARK_3D_ENABLED` not set or ModelArk key missing | Set `BYTEPLUS_MODELARK_3D_ENABLED=true` and ensure `BYTEPLUS_MODELARK_API_KEY` is configured |
| 3D task failed with `AbilityProcessingError` | Transient provider error | Re-submit the same task; do not treat the input as invalid |

---
