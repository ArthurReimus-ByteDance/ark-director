# Artifact Access

#### `seed_media_get_artifact`

Retrieve a persisted media artifact by its UUID as inline Base64 content. Use
when the client needs the artifact data directly rather than reading the
resource URI. Read-only, idempotent, ownership-checked. Requires
`artifacts:read` scope in JWT mode.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `artifact_id` | `str` | Yes | Artifact UUID from a previous generation call |

Returns `SeedMediaGetArtifactOutput` with `artifact_id`, `media_type`,
`mime_type`, `sha256`, `bytes`, optional `expires_at`, and Base64 `data`.

---
