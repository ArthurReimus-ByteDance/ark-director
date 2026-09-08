# Reusing uploaded references across shots (presign pattern)

Presigned URLs expire after 30 minutes by default (1800s, configurable
60–604800s via `TOS_PRESIGN_TTL_SECONDS`/`S3_PRESIGN_TTL_SECONDS`). When the
same reference images or audio are used across multiple shots (e.g., character
sheets reused across every scene), do **not** re-upload the same file each time.
Instead:

1. **Upload once** — call `media_upload` for each reference file and store
   the returned `object_key` (e.g., in a project-level reference registry
   like `task_ids.json` or a dedicated `ref_cache.json`).
2. **Presign on demand** — before each new shot submission, call
   `media_presign` with the stored `object_key` to get a fresh presigned
   URL in seconds. No file re-upload, no duplicate storage cost.
3. **Batch presign** — presign all needed references for a shot in one call
   with `media_presign_batch` (pass the list of `object_keys`), then
   immediately submit the Seedance task while the URLs are still valid.

This reduces upload time from minutes (re-uploading 9–10 files per shot)
to seconds (presigning 9–10 keys per shot) and avoids filling object
storage with duplicate copies of the same reference images.

---
