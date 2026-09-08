---
name: template-factory
description: >-
  Pinterest-inspired template factory that reverse-engineers a reference video (a "pin") into reproducible AIGC output. Orchestrates pin intake, seed_understand breakdown, keyframe extraction, a deep motion review, a dynamic sketch storyboard, optional Seedream element sheets, and a Seedance 2.5 video — each generated prompt passing the mandatory prompt-review gate. Explicitly-marked orchestrator: composes modelark-mcp, seedream-storyboard, seedance-prompt-25, prompt-review, media-review, and the ffmpeg skills; it does not call the Ark REST API itself. Use when the user wants to replicate a reference video's style/composition/grammar, build a reusable visual template, or turn a downloaded Pinterest pin into generated elements and video.
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
- Default `watermark: false` only where the selected live tool supports the
  parameter, unless the user requests otherwise.

## Pipeline (one stage at a time)

```text
pin_uploaded → breakdown_draft → breakdown_approved → motion_reviewed
  → elements_draft → elements_approved → storyboard_draft
  → storyboard_approved → video_draft → video_review → approved
```

1. **Pin intake** — resolve the pin (local file or URL); upload via
   `media_upload`; record `object_key`, content SHA-256, and storage scope in
   `ref_cache.json`. Re-presign unchanged cached objects on demand; re-upload
   only if content changed or the recorded remote object is missing.
2. **Analysis** — `seed_understand` with the template's analysis prompt
   (`references/analysis-prompt.md`) → validate `VideoBreakdown` against
   `references/breakdown-schema.json` → write `analysis.json` + `breakdown.md`.
   Gate A: user reviews the breakdown.
3. **Keyframes** — `ffmpeg` extracts a frame per shot (mid-shot, or the flagged
   element keyframe) into `keyframes/`.
4. **Deep motion review** — second `seed_understand` pass (`thinking=true`) per
   `references/motion-review-prompt.md` → merge `shots[].motion` into
   `analysis.json`. This is the primary fix for "ours looks static".
5. **Elements** — identify required canonical inputs from the draft breakdown.
   Use the workspace prop threshold: branded, recurring, story-critical, or
   scene-variant wearables need a separate prop reference; incidental objects
   may be described in text. Generate required sheets in 3 variants after
   prompt review; persist `selected_variant` only after explicit user choice.
6. **Storyboard** — after relevant Elements are approved, write a dynamic
   production board via `seedream-storyboard`, one panel per shot. Review the
   prompt and generate 3 variants with distinct seeds. A monochrome analysis
   sketch is control-only: translate its blocking into text and omit it from
   video inputs by default. A production panel can be promoted only after
   explicit selection, source-hash validation, and a supported image mode.

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
- **Video eligibility** — production panels need explicit user selection and
  current canonical source hashes. Control sketches are omitted by default;
  an intentional conditioning exception requires explicit selection, supported
  tool inputs, and artifact-specific QA. Bind only eligible inputs.

## Selection gate (human review by default)

Storyboard variant selection requires explicit user choice. `storyboard.review:
false` disables the review UI only. Store an automatic suggestion under
`recommended_variant`, keep `status: review`, and wait for explicit selection
before video promotion. Neither a recommendation nor technical success writes
`selected_variant` or `approved`.

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

## Submission recovery

Persist each exact prompt snapshot and reviewed prepared request in the project
registry before submitting. Record the provider task ID as soon as available.
An ambiguous timeout leaves `submission_unknown`: reconcile that operation or
resume its known task; never repeat submission automatically or switch transport
to submit a duplicate. Any new authorized take gets a new operation record.

## Intentional conditioning representation

A sketch or blockout stays `control_only: true` while it is analysis-only. To
use intentional conditioning, first obtain explicit selection of a derived
composition or motion reference. Record its exact selected manifest, current
SHA-256, `reference_image` or `reference_video` role, and `control_only: false`.
Confirm live model/mode support. Flipping the flag alone never grants approval;
the caller applies the [production policy](../../contracts/production-policy.md).
