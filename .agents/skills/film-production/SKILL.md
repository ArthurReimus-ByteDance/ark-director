---
name: film-production
description: Orchestrate an AI-assisted film, commercial, music video, or narrative production across brief, development, canon, storyboard, audio, shot generation, review, assembly, and delivery. Use when a request spans multiple scenes or modalities, asks to create or continue a film project, requires coordination between Seedream, Seed Audio, Seedance, Remotion, or FFmpeg, or needs the next safe production step rather than a single prompt. Do not use for an isolated image, audio, video, or editing request that one specialist skill can complete independently.
---

# Film Production

Manage one coherent production run while keeping specialist skills modular. Read
`AGENTS.md` first, inspect the existing project before creating anything, and
advance only as far as the available evidence and approvals permit.

## Core operating model

- Act as the single manager communicating with the user.
- Treat project files and manifests as production memory; do not rely on chat
  history alone.
- Delegate modality work by invoking the narrowest applicable project skill.
- Prefer a deterministic workflow when the next action is known. Use agentic
  judgment for creative choices, contradiction resolution, and review.
- Never infer approval. Technical success places an output in `review`.
- Never submit a replacement generation because local polling timed out. Resume
  the provider task recorded in `task_ids.json`.
- Never silently replace user writing, approved canon, selected variants, or
  unrelated project state.

## Start or resume a run

1. Resolve the project directory. Search before creating a project, scene,
   element, shot, or same-purpose artifact.
2. Read `project.md`, `task_ids.json`, relevant element manifests, scene and shot
   manifests, prompt snapshots, and the latest review decisions.
3. Determine the current stage from recorded artifacts and lifecycle states.
   Do not infer completion from filenames alone.
4. Identify contradictions, missing inputs, stale dependencies, pending provider
   tasks, and approval gates.
5. State the current stage, the next safe objective, required specialist skills,
   and any user decision needed before spending credits.

Read [stage-contracts.md](references/stage-contracts.md) for entry evidence,
required outputs, and exit conditions. Read
[handoff-contracts.md](references/handoff-contracts.md) before moving an artifact
between modalities.

## Route specialist work

<!-- markdownlint-disable MD013 -->

| Production need | Primary skill |
| --- | --- |
| Character identity asset | `seedream-character-sheet` |
| Character sheet cleanup | `seedream-character-sheet-cleanup` |
| Location identity asset | `seedream-location-asset` |
| General image generation or edit | `seedream-prompt` or `seedream-edit` |
| Storyboard and visual continuity | `seedream-storyboard` |
| Seed Audio prompt | `seed-audio-prompt` |
| Narrative audio commercial | `seed-audio-commercial` |
| Seedance 2.5 video prompt | `seedance-prompt-25` |
| Filipino or Taglish video dialogue | `seedance-prompt-25-filipino` with `seedance-prompt-25` |
| Seedance 2.0 video prompt | `seedance-prompt-20` |
| Footage-driven VFX prompt | `seedance-footage-vfx` or `seedance-vfx-prompt` |
| End-to-end Seedance 2.0 VFX shot | `seedance-vfx-shot` |
| Model submission, polling, or artifact access | `modelark-mcp` |
| Assembly, media transforms, captions, render | appropriate Remotion, FFmpeg, or Mediabunny skill |

<!-- markdownlint-enable MD013 -->

If the needed lifecycle role does not exist, keep the work at its current stage
and record the gap. Do not disguise a generic prompt as a completed production
department workflow. See `specs/SPEC_FILMMAKING_LIFECYCLE_SKILLS.md` for planned
coverage.

## Run one stage at a time

For the active stage:

1. Record the stage objective and observable acceptance criteria.
2. Confirm every input path, selected variant, lifecycle state, and SHA-256.
3. Invoke only the specialists needed for that stage.
4. Persist exact prompts beside generated media and update the owning manifest.
5. Inspect actual outputs, not only provider response metadata.
6. Set outputs to `review` and present material differences, known defects, and
   the recommended next decision.
7. Advance only when the stage exit contract is satisfied.

## Approval and spending gates

Require explicit user approval before:

- promoting a generated identity or location asset into approved canon;
- using a storyboard panel as a video input;
- submitting a high-cost or multi-variant final generation;
- invalidating or replacing an approved take;
- declaring picture, audio, or final delivery lock.

Ordinary low-cost work explicitly requested by the user may proceed within the
repository guardrails. Approval to generate does not approve the result.

## Handle revisions

Write every revision as:

- **Locked decisions:** properties that must remain unchanged;
- **Requested delta:** the single intended change where practical;
- **Acceptance criteria:** observable evidence of success;
- **Known rejections:** previously rejected outcomes that must not return;
- **Invalidation scope:** dependent artifacts that return to `review` if inputs
  change.

Prefer a bounded edit over full regeneration after composition or performance is
approved. Preserve rejected history and never overwrite source media.

## Finish the run

Report the stage reached, artifacts created or changed, review status, provider
tasks still running, costs when known, unresolved risks, and the next production
decision. A production run is complete only when its active stage exit contract
is satisfied; the whole film is complete only after explicit final-delivery
approval.
