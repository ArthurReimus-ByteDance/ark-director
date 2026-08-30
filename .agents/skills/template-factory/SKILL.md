---
name: template-factory
description: Pinterest-inspired template factory that reverse-engineers a reference video (a "pin") into reproducible AIGC output. Orchestrates pin intake, seed_understand breakdown, keyframe extraction, a deep motion review, a dynamic sketch storyboard, optional Seedream element sheets, and a Seedance 2.5 video — each generated prompt passing the mandatory prompt-review gate. Explicitly-marked orchestrator: composes modelark-mcp, seedream-storyboard, seedance-prompt-25, prompt-review, media-review, and the ffmpeg skills; it does not call the Ark REST API itself. Use when the user wants to replicate a reference video's style/composition/grammar, build a reusable visual template, or turn a downloaded Pinterest pin into generated elements and video.
---

# Template Factory

Turn a reference video ("pin") into reproducible AIGC output through a reusable
"template" (the recipe). One run produces: a `VideoBreakdown` analysis, a sketch
storyboard, optional element sheets, and a Seedance 2.5 video take — all
manifested for later reproduction.

This skill is an **explicitly-marked orchestrator** (precedent: `film-production`).
It composes MCP tools + specialist skills; it never calls the Ark REST API
directly.

## Core operating model

- Act as the single manager communicating with the user.
- Treat `project.md`, `task_ids.json`, `ref_cache.json`, and shot manifests as
  production memory.
- Never infer approval. Technical success places an output in `review`; only the
  user sets `approved`.
- **Every prompt this factory submits — Seedream storyboard, Seedream element
  sheet, or Seedance video — must pass the `prompt-review` gate first.**
- Replicate style, composition, and grammar. Do not clone copyrighted footage or
  reproduce identifiable real people (de-identify in analysis).
- `watermark: false` on all generations unless the user requests otherwise.

## Pipeline (one stage at a time)

```text
pin_uploaded → breakdown_draft → breakdown_approved → motion_reviewed
  → storyboard_draft → storyboard_approved → elements_draft
  → elements_approved → video_draft → video_review → approved
```

1. **Pin intake** — resolve the pin (local file or URL); upload via
   `media_upload`; record `object_key` in `ref_cache.json` (never re-upload;
   presign on demand).
2. **Analysis** — `seed_understand` with the template's analysis prompt
   (`references/analysis-prompt.md`) → validate `VideoBreakdown` against
   `references/breakdown-schema.json` → write `analysis.json` + `breakdown.md`.
   Gate A: user reviews the breakdown.
3. **Keyframes** — `ffmpeg` extracts a frame per shot (mid-shot, or the flagged
   element keyframe) into `keyframes/`.
4. **Deep motion review** — second `seed_understand` pass (`thinking=true`) per
   `references/motion-review-prompt.md` → merge `shots[].motion` into
   `analysis.json`. This is the primary fix for "ours looks static".
5. **Storyboard** — write a monochrome-sketch single-image grid with a **dynamic
   panel count** (one panel per `shots[]` entry), via `seedream-storyboard`.
   Run `prompt-review`, generate **3 variants** (same prompt, distinct seeds),
   then apply the **selection gate** (§ Selection gate). The chosen board is
   passed to Seedance as `@Image 1`.
6. **Elements (optional)** — for each approved element, write Seedream sheet
   prompts via the mapped skill, run `prompt-review`, generate 3 variants,
   cleanup where applicable, persist `selected_variant` after user choice.
7. **Video** — compose the Seedance 2.5 six-part prompt from breakdown + board +
   motion review + element sheets (via `seedance-prompt-25`), run
   `prompt-review`, submit via `seedance_2_5_create_task`, persist the task id,
   poll, download, QA (`ffprobe` + decode + contact sheet).
8. **Review** — set `review`; user approves.

## Route specialist work

| Need | Primary skill |
| --- | --- |
| Upload / presign references | `modelark-mcp` (`media_upload`, `media_presign`) |
| Video analysis + motion review | `modelark-mcp` (`seed_understand`) |
| Keyframe extraction | `ffmpeg` |
| Storyboard grid prompt | `seedream-storyboard` |
| Element sheets | `seedream-character-sheet`, `seedream-location-asset`, `seedream-prompt` |
| Seedance 2.5 video prompt | `seedance-prompt-25` |
| Prompt quality gate (mandatory) | `prompt-review` |
| Visual review of outputs | `media-review` |

## Storyboard rules

- **Dynamic panel count** — one panel per identified scene/shot; never a fixed
  budget. Grid = smallest grid that fits (1×3, 2×2, 2×3, 3×3, …).
- **Monochrome sketch only** — colorless pencil/ink; the board is a
  composition/order anchor, never a color source.
- **3 variants** — identical prompt + references + params, distinct seeds.
- **Passed to Seedance** as `@Image 1` (`reference_image`) with the
  storyboard-grid role contract.

## Selection gate (human review by default)

Storyboard variant selection requires **human review by default** (template
`storyboard.review: true`). When a template sets `review: false`, auto-select
and record `selected_variant: auto` — never `approved`.

## Prompt review gates (mandatory)

Before any generation call, run `prompt-review`:

- Seedream storyboard grid prompt (before `seedream_generate_image`)
- Seedream element sheet prompts (before each sheet generation)
- Seedance video prompt, including the motion-review wording merged into it
  (before `seedance_2_5_create_task`)

CRITICAL/MAJOR findings must be fixed before submission.

## Revisions

Write every revision as: locked decisions, requested delta, acceptance criteria,
known rejections, invalidation scope. Change one of prompt wording, reference
bundle, or motion design at a time.

## File layout

Skill (committed):

```text
.agents/skills/template-factory/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── analysis-prompt.md
│   ├── motion-review-prompt.md
│   ├── breakdown-schema.json
│   ├── slot-mapping.md
│   └── templates/
│       ├── index.json
│       └── <template-id>/template.md + template.json
└── evals/evals.json
```

Run (local-only, project-scoped):

```text
projects/<project>/
├── pins/                     # downloaded reference videos
├── project.md, task_ids.json, ref_cache.json
├── templates/<template-id>/
│   ├── analysis.json, breakdown.md, motion-review.md
│   └── keyframes/
├── elements/<id>/
└── scenes/scene-01/...
```
