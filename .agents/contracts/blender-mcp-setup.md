# Blender MCP Setup

Reference for the eight `blender-*` skills vendored from
`ra100/blender-claude-plugin` (see `skills-lock.json`). The skills were written
against the upstream "Blender Lab" MCP server whose tools are unprefixed
(`execute_blender_code`, `get_objects_summary`, `search_api_docs`, …). This
workspace connects to a different Blender MCP surface whose tools carry a
`blender_` prefix. Treat this mapping as adapter guidance; resolve actual callable names from the connected tool inventory before use.

## Tool-name mapping

| Vendored (upstream) tool | Connected (`blender_`) tool |
|---|---|
| `execute_blender_code` | `blender_execute_blender_code` |
| `get_objects_summary` | `blender_get_scene_info` |
| `get_object_detail_summary` | `blender_get_object_info` |
| `get_screenshot_of_window_as_image` / `get_screenshot_of_area_as_image` | `blender_get_viewport_screenshot` |
| `render_thumbnail_to_path` / `render_viewport_to_path` | `blender_get_viewport_screenshot` |
| `get_blendfile_summary_*`, `jump_to_*`, `search_api_docs`, `get_python_api_docs`, `search_manual_docs` | No connected equivalent — use `blender_execute_blender_code` to inspect data, and confirm API/doc details via a docs lookup tool such as Context7. |

## Detection

The connected Blender MCP server is available when tools prefixed `blender_`
are present (e.g. `blender_execute_blender_code`, `blender_get_scene_info`,
`blender_get_object_info`, `blender_get_viewport_screenshot`). When those tools
are absent, fall back to emitting self-contained `bpy` scripts.

## Workflow

1. Inspect with `blender_get_scene_info` / `blender_get_object_info`.
2. Mutate via `blender_execute_blender_code`.
3. Verify with `blender_get_viewport_screenshot`.

## Notes

- These skills are out of domain for the core ai-director AIGC pipeline
  (Seedance/Seedream/Seed Audio). They are kept for Blender-based modeling,
  previz, and post work; keep them project-local; cross-project installation is a separate explicit task.
- The skills document Blender 5.0/5.1 API; the local install may be a newer
  minor (e.g. 5.2). Verify version-gated API claims against the installed
  `bpy` before relying on them.
