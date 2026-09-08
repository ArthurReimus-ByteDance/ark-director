## Registration Model

Do not assume a fixed tool count. Registration is conditional on environment
variables. Tools for a product appear only when its API key is set; the server
gracefully degrades to whatever is configured.

### Always registered

- `seed_media_get_artifact`
- `seed-health://status` resource

### Requires `BYTEPLUS_SEED_SPEECH_API_KEY`

- `seed_audio_generate`
- `seed_audio_generate_variations`
- `speech_to_text`

### Requires `BYTEPLUS_VOD_MEDIAKIT_API_KEY`

- `vod_enhance_video`
- `vod_transcode_video`
- `vod_get_transcode_task`
- `vod_separate_audio`
- `vod_get_audio_separation`

### Requires `BYTEPLUS_MODELARK_API_KEY`

- `seedream_generate_image`
- `seedream_edit_image`
- `seedream_generate_image_variations`
- `seedance_create_task`
- `seedance_create_task_variations`
- `seedance_get_task`               # shared: retrieves both 2.0 and 2.5 tasks
- `seedance_list_tasks`             # shared: lists both 2.0 and 2.5 tasks
- `seedance_cancel_or_delete_task`  # shared: acts on both 2.0 and 2.5 tasks
- `seedance_2_5_create_task`
- `seedance_2_5_create_task_variations`
- `seed_understand`

### Requires `BYTEPLUS_MODELARK_3D_ENABLED=true` (and `BYTEPLUS_MODELARK_API_KEY`)

- `hyper3d_create_task`
- `hyper3d_get_task`
- `hyper3d_list_tasks`
- `hyper3d_cancel_or_delete_task`
- `hitem3d_create_task`
- `hitem3d_get_task`
- `hitem3d_list_tasks`
- `hitem3d_cancel_or_delete_task`

3D generation is **disabled by default**; it reuses the ModelArk API key and
base URL but is gated by its own feature flag so it stays off unless
explicitly enabled.

### Requires object storage credentials (TOS or S3)

- `media_upload`
- `media_presign`
- `media_presign_batch`

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
BYTEPLUS_SEED_SPEECH_API_KEY=your-speech-key  # required for Seed Audio + Speech-to-Text
BYTEPLUS_VOD_MEDIAKIT_API_KEY=your-mediakit-key # required for VOD enhancement, transcoding, and audio separation
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
