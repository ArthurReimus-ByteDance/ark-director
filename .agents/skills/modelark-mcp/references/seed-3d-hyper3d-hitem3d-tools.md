# Seed 3D (Hyper3D + Hitem3d) Tools

Requires `BYTEPLUS_MODELARK_3D_ENABLED=true` (and `BYTEPLUS_MODELARK_API_KEY`).
Auth scopes: `hyper3d:create`, `hyper3d:read`, `hyper3d:delete`, `hitem3d:create`,
`hitem3d:read`, `hitem3d:delete`.

3D generation is **asynchronous**. You create a task, then poll for completion.
Tasks use the same lifecycle states as Seedance:
`queued → running → succeeded | failed | cancelled | expired`.

Two model families are supported:

- **Hyper3D** (`hyper3d-gen2-260112`) — text-to-3D and image-to-3D. Accepts a
  text prompt and/or up to 5 reference images. Supports seeds, PBR/Shaded/All/None
  materials, Raw/Quad mesh modes, custom polygon counts, HD textures, bounding-box
  conditioning, T-Pose, and subdivision levels. Output formats: GLB, OBJ, USDZ,
  FBX, STL.
- **Hitem3d** (`hitem3d-2-0-251223`) — image-to-3D only. Requires 1–4 reference
  images. Supports resolution selection (1536/1536pro), custom face counts
  (100K–2M), geometry-only or geometry+texture modes, and multi-view bitmap
  marking. Output formats: OBJ, GLB, STL, FBX, USDZ.

#### `hyper3d_create_task`

Create an asynchronous Hyper3D 3D generation task. Supports text-to-3D (prompt
required) and image-to-3D (1–5 images).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | `str` | No* | Text prompt (English, max 400 chars). *Required for text-to-3D when no images are provided. |
| `images` | `list[Seed3DImageInput]` | No | Reference images for image-to-3D. Max 5. |
| `model` | `str` | No | Model ID. Omit for the configured Hyper3D default. |
| `seed` | `int` | No | Random seed for reproducible generation (0–65535). |
| `callback_url` | `str` | No | Optional callback URL notified on status changes. |
| `material` | `"PBR"` \| `"Shaded"` \| `"All"` \| `"None"` | No | Material type. PBR (default). |
| `mesh_mode` | `"Raw"` \| `"Quad"` | No | Mesh shape. Raw (triangles) or Quad (default). |
| `quality_override` | `int` | No | Custom polygon count (Raw: 500–1M, Quad: 1000–200K). |
| `addons` | `"HighPack"` | No | Texture enhancement. HighPack provides 4K textures. |
| `use_original_alpha` | `bool` | No | Preserve transparent areas of the input image. |
| `bbox_condition` | `list[int]` | No | Bounding box `[width, height, length]` (3 ints). |
| `ta_pose` | `bool` | No | Force T-Pose/A-Pose for humanoid models. |
| `subdivision_level` | `"high"` \| `"medium"` \| `"low"` | No | Polygon count level. Ignored when `quality_override` is set. |
| `file_format` | `"glb"` \| `"obj"` \| `"usdz"` \| `"fbx"` \| `"stl"` | No | Output 3D file format. Defaults to `glb`. |
| `hd_texture` | `bool` | No | Enable HD textures. |

Returns `Seed3DCreateTaskOutput` with `task_id`, `status="queued"`, and
`recommended_poll_after_ms` (5000ms).

**Example — text-to-3D:**

```json
{
  "prompt": "A medieval castle with tall towers and a drawbridge",
  "file_format": "glb",
  "material": "PBR"
}
```

**Example — image-to-3D with PBR materials:**

```json
{
  "images": [
    { "kind": "url", "url": "https://cdn.example.com/character.png" }
  ],
  "material": "PBR",
  "mesh_mode": "Quad",
  "file_format": "glb"
}
```

#### `hitem3d_create_task`

Create an asynchronous Hitem3d 3D generation task. Image-to-3D only; requires
1–4 reference images.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `images` | `list[Seed3DImageInput]` | Yes | Reference images for image-to-3D. 1–4 required. |
| `model` | `str` | No | Model ID. Omit for the configured Hitem3d default. |
| `callback_url` | `str` | No | Optional callback URL notified on status changes. |
| `resolution` | `"1536"` \| `"1536pro"` | No | Model resolution. 1536 (default) or 1536pro. |
| `face` | `int` | No | Custom model face count (100000–2000000). |
| `file_format` | `"obj"` \| `"glb"` \| `"stl"` \| `"fbx"` \| `"usdz"` | No | Output 3D file format. Defaults to `obj`. |
| `request_type` | `1` \| `3` | No | 1 = geometry only, 3 = geometry + texture (default). |
| `multi_images_bit` | `str` | No | Bitmap marking which views are present, in order front/back/left/right (e.g. `"1010"` = front + left). Max 4 chars. |

Returns `Seed3DCreateTaskOutput` with `task_id`, `status="queued"`, and
`recommended_poll_after_ms` (5000ms).

**Example — image-to-3D with multiple views:**

```json
{
  "images": [
    { "kind": "url", "url": "https://cdn.example.com/front.png" },
    { "kind": "url", "url": "https://cdn.example.com/left.png" }
  ],
  "multi_images_bit": "1010",
  "resolution": "1536pro",
  "file_format": "glb"
}
```

#### `hyper3d_get_task` / `hitem3d_get_task`

Retrieve the status and output of a 3D generation task. On first successful
retrieval with `persist_output=true` (default), copies the provider's 24-hour
file URL (zip package of the 3D file) into durable artifact storage so the
`seed-media://` resource remains available after expiry.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | `str` | Yes | Task ID from the create tool |
| `persist_output` | `bool` | No (default `true`) | Persist the 3D file to artifact store on first success |

Returns `Seed3DTaskOutput` with `task_id`, `model`, `created_at`, `updated_at`,
`status`, optional `error`, optional `file: ArtifactRef` (on success), and
optional `usage`.

#### `hyper3d_list_tasks` / `hitem3d_list_tasks`

List recent 3D generation tasks (previous 7 days, provider limitation). Supports
filtering by status, task IDs, and model.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `page` | `int` | No | 1–500 |
| `page_size` | `int` | No | 1–100 |
| `status` | `Seed3DTaskStatus` | No | Filter by status |
| `task_ids` | `list[str]` | No | Filter by specific task IDs |
| `model` | `str` | No | Filter by model ID |

Returns `Seed3DTaskPage` with paginated task summaries.

#### `hyper3d_cancel_or_delete_task` / `hitem3d_cancel_or_delete_task`

Cancel a queued task or delete a terminal task. **Destructive** — requires
explicit confirmation.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | `str` | Yes | Task to act on |
| `mode` | `"cancel"` \| `"delete"` | Yes | Action to perform |
| `expected_status` | `Seed3DTaskStatus` | Yes | Must match current status |
| `confirm` | `Literal[true]` | Yes | Must be `true` |

- `mode=cancel` + `expected_status=queued`: Cancel a pending task.
- `mode=delete` + `expected_status=succeeded|failed|expired`: Delete a completed task.

Returns `Seed3DCancelOrDeleteOutput`.

---
