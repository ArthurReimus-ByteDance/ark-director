# Object Storage Upload

Requires object storage credentials (TOS or S3). No auth scope in stdio mode.
In JWT mode: `media:upload` for `media_upload`, `media:presign` for `media_presign`
and `media_presign_batch`.

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
| `expires_in_seconds` | `int` | No | Presigned URL validity in seconds (60–604800). Defaults to the configured presign TTL. Use a long value (e.g. 3600) for uploads destined for VOD tools, which fetch the source asynchronously. |

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

#### `media_presign`

Generate a fresh presigned HTTPS GET URL for an existing object in storage
(TOS or S3) without re-uploading. Use this when a previously uploaded
reference's presigned URL has expired or is about to expire.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `object_key` | `str` | Yes | Object key returned by a prior `media_upload` call |
| `expires_in_seconds` | `int` | No | Presigned URL validity in seconds (60–604800). Defaults to the configured presign TTL. Use a long value (e.g. 3600) when renewing for VOD tools, which fetch the source asynchronously. |

Returns `MediaPresignOutput` with `url`, `expires_at`, `object_key`.

**Example — renew an expired URL:**

```json
{
  "object_key": "references/video/abc-123-def"
}
```

JWT scope: `media:presign`.

#### `media_presign_batch`

Generate fresh presigned HTTPS GET URLs for many existing objects in a single
call (TOS or S3). Use this when preparing multiple references for one shot —
e.g. presigning 30 Seedance 2.5 reference images — instead of calling
`media_presign` once per key. Failures are reported per key: each failing key
returns `code` (`INVALID_KEY`, `NOT_OWNED`, `INTERNAL`, or a provider error
code) and `error` while the rest succeed.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `object_keys` | `list[str]` | Yes | Object keys returned by prior `media_upload` calls (1–100 entries) |
| `expires_in_seconds` | `int` | No | Presigned URL validity (60–604800) applied to every key. Defaults to the configured presign TTL. |

Returns `MediaPresignBatchOutput` with `items` (per-key `object_key`, `url`,
`expires_at`, `code`, `error`, `request_id`), `succeeded`, and `failed`.

**Example — presign a batch of references:**

```json
{
  "object_keys": [
    "references/image/char-sheet-1",
    "references/image/char-sheet-2",
    "references/audio/bgm-track"
  ]
}
```

JWT scope: `media:presign`.

---
