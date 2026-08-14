---
project: ube-commercial
title: Seedance 2.5 adoption — current limitations
status: open
created: 2026-08-04
---

# Seedance 2.5 adoption — current limitations

> The prompt skills (`seedance-prompt` for 2.5, `seedance-prompt-20` for 2.0)
> are correctly split. The blockers are in the infrastructure layer and the
> model catalog.

## 1. AGENTS.md model catalog — no Seedance 2.5

`AGENTS.md:29` only lists Seedance 2.0:

```
| Seedance | Seedance 2.0 Standard (`dreamina-seedance-2-0-260128`); configured Fast/Mini bindings | ...
```

No 2.5 row, no 2.5 model ID, no 30-second duration, no 50-reference limit. An
agent reading AGENTS.md first defaults to 2.0 assumptions (15s cap, 9 images,
clip splitting).

**Fix:** add a Seedance 2.5 row to the model catalog table.

## 2. MCP server hardcoded for 2.0

`modelark-mcp/SKILL.md:411-419` — the `seedance_create_task` tool parameters
reflect 2.0 limits:

| Parameter | Documented limit (2.0) | 2.5 actual |
|---|---|---|
| `duration` | -1 to 15 seconds | 4–30 seconds |
| `images` | up to 9 | up to 30 |
| `videos` | up to 3 | up to 10 |
| `audios` | up to 3 | up to 10 |
| `model` default | `dreamina-seedance-2-0-260128` | TBD (2.5 ID not registered) |

**Fix:** update `seedance_create_task` parameter docs and the model capability
registry to add a Seedance 2.5 family with the correct limits.

## 3. MCP model capability registry — no 2.5 family

`modelark-mcp/SKILL.md:671-678` — the registry has `Seedance 2 Standard`,
`Seedance 2 Fast`, `Seedance 2 Mini` but **no Seedance 2.5 entry**. Even if a
2.5 model ID were passed, the server's input validation would reject it as
unknown or silently fall back to the 2.0 default.

**Fix:** add a `Seedance 2.5` row to the capability registry. This requires
changes to the MCP server code, not just the SKILL.md docs.

## 4. Seedance 2.5 model ID — not yet on ModelArk

The `seedance-prompt` skill notes at line 946:

```
| Seedance 2.5 | TBD — check the Model list when API access launches |
```

> Seedance 2.5 API access is "coming soon" on BytePlus ModelArk as of
> 2026-07-31. It is live on Jimeng AI and Doubao Pro.

Without a registered model ID, the MCP server cannot submit 2.5 tasks even if
the capability registry were updated.

**Fix:** check the [ModelArk model list](https://docs.byteplus.com/en/docs/ModelArk/1330310)
for the 2.5 model ID when it launches. Register it in the MCP server's
`SEEDANCE_MODEL_BINDINGS` or as a new default.

## 5. MCP server code — validation needs relaxing

Even with docs updated, the actual MCP server implementation enforces 2.0 limits
at runtime. The server code needs to:

- accept the 2.5 model ID as valid
- relax image count validation (9 → 30)
- relax video count validation (3 → 10)
- relax audio count validation (3 → 10)
- relax total reference count (implicitly 15 → 50)
- relax duration validation (15 → 30)
- pass through 2.5-specific parameters (50 refs, structured editing, extension
  duration)

This is a code change to the MCP server, not a documentation fix.

## 6. Audio-only reference constraint

The MCP tool documentation states
(`modelark-mcp/SKILL.md:405-406`):

> Audio references cannot be the sole media input; at least one image or video
> must accompany audio.

The v02 prompt (`seedance_25_prompt_v02.md`) works around the KYC issue by
using audio-only references with no images. If the MCP server enforces this
constraint at runtime, the v02 prompt will be rejected.

**Fix:** verify whether the 2.5 API and MCP server allow audio-only references.
If not, the KYC workaround needs a different approach (e.g., a non-face image
such as the kitchen location sheet as a minimal image reference).

## What is already correct

- **`seedance-prompt` skill** — correctly targets 2.5 (flexible formula, stages,
  30s, 50 refs, audio brackets, dialogue language reinforcement)
- **`seedance-prompt-20` skill** — correctly targets 2.0 with a "use
  seedance-prompt for 2.5" pointer
- **Cross-references** in `seedance-vfx-prompt`,
  `seedance-vfx-shot` all correctly route to `seedance-prompt` for 2.5
- **`SEEDANCE_25_PROMPT_GUIDE.md`** — full reference guide is up to date
- **Jollibee commercial** — already has a working 2.5 visual package
  (`SEEDANCE_25_VISUAL_PACKAGE.md`) with 4 connected 2.5 generations

## Summary

| Layer | 2.5-ready? | Action needed |
|---|---|---|
| Prompt skills | Yes | None |
| AGENTS.md model catalog | No | Add 2.5 row |
| MCP SKILL.md docs | No | Update limits + registry |
| MCP server code | No | Accept 2.5 ID, relax validation |
| ModelArk API | No | 2.5 model ID "coming soon" |
| Audio-only constraint | Unknown | Verify at runtime |
