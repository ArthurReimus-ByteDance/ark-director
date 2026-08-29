---
name: prompt-review
description: >
  Review and fix prompts written for BytePlus generative models (Seedance, Seed Audio,
  Seedream) against the repo's skill best practices using a sub-agent review pipeline.
  After the main agent writes or updates any prompt, a sub-agent reviews each prompt
  against the applicable skill's validation checklist and returns structured findings;
  the main agent then fixes any issues before the prompt is finalized or submitted for
  generation. Invoke after creating or updating prompts for Seedance 2.5, Seedance 2.0,
  Seed Audio, Seedream image generation, character sheets, location assets, storyboards,
  VFX shots, or Filipino dialogue prompts. Also invoke when the user asks to "review
  prompts", "check prompts", "QA prompts", "validate prompts", "lint prompts", or when
  the agent has finished writing prompts for a scene and is about to submit generation
  tasks. Do not use for non-prompt assets (manifests, scene definitions) or for
  reviewing generated media output (use media-review instead).
---

# Prompt Review

A quality gate for prompts. The main agent writes prompts, a sub-agent reviews them
against the repo's skill best practices, and the main agent fixes any issues found.

## Core concept

```
Main agent writes/updates prompts
  → identify each prompt's type (Seedance 2.5, Seed Audio, Seedream, etc.)
  → load the matching review checklist from references/review-checklists.md
  → spawn a sub-agent: give it the prompt text + the checklist
  → sub-agent returns structured findings (issues by severity with suggested fixes)
  → main agent applies fixes to the prompt files
  → re-review only the changed prompts if any fixes were applied
```

## When to trigger

- After writing or updating any prompt for a BytePlus generative model.
- Before submitting a generation task (Seedance, Seed Audio, Seedream).
- When the user asks to review, check, QA, validate, or lint prompts.
- After revising a prompt based on generated output feedback.

Do not trigger for:
- Media review (use `media-review` skill).
- Manifest or scene definition edits (those are production metadata, not prompts).
- Prompts that have already been frozen as prompt snapshots unless the user explicitly
  asks to re-review a frozen snapshot.

## Prompt type detection

Match each prompt to its checklist source by file naming convention and content:

| Prompt type | File prefix | Checklist source |
|---|---|---|
| Seedance 2.5 video | `prompt_sNN_shNNN_tNN_vNN.md` | `seedance-prompt-25` |
| Seedance 2.0 video (4K/Fast/Mini) | `prompt_sNN_shNNN_tNN_vNN.md` | `seedance-prompt-20` |
| Seedance VFX (video-to-video edit) | `prompt_sNN_shNNN_tNN_vNN.md` | `seedance-vfx-prompt` |
| Seedance Filipino dialogue | `prompt_sNN_shNNN_tNN_vNN.md` | `seedance-prompt-25` + `seedance-prompt-25-filipino` |
| Seed Audio (dialogue/music/SFX/ambience) | `prompt_dlg_*`, `prompt_mus_*`, `prompt_amb_*`, `prompt_mix_*` | `seed-audio-prompt` |
| Seedream image generation | `prompt_concept_*`, `prompt_sNN_kf*` | `seedream-prompt` |
| Seedream character sheet | `prompt_char_*` | `seedream-character-sheet` |
| Seedream location asset | `prompt_loc_*` | `seedream-location-asset` |
| Seedream prop sheet | `prompt_prop_*` | `seedream-prompt` (general image rules apply) |
| Seedream screen UI reference | `prompt_screen_*` | `seedream-prompt` (general image rules apply) |
| Seedream brand/title card | `prompt_card_*` | `seedream-prompt` (general image rules apply) |
| Seedream storyboard | `prompt_sNN_kf*` (multi-panel) | `seedream-storyboard` |
| Seedance music video | `prompt_sNN_shNNN_tNN_vNN.md` (song-driven) | `seedance-music-video` |

The "Checklist source" column is a provenance label only — this skill never loads
a sibling; the applicable checklist is always read from this skill's own bundled
`references/review-checklists.md`.

When a prompt could match multiple types (e.g., a Seedance 2.5 prompt with Filipino
dialogue), stack the checklists — the sub-agent checks against all applicable skills.

UGC intermediate outputs (hooks, scripts) are reviewed at **Stage 1** (before
composition into a final Seedance prompt). The final composed Seedance prompt is
reviewed at **Stage 2** against the Seedance 2.5 + Universal checklists. UGC
compliance audit runs **before Stage 1** — if it returns CRITICAL, stop the pipeline.

## Workflow

### Step 1 — Collect prompts to review

Gather all prompt files that were written or updated in the current session. These are
the files with the `prompt_` prefix that sit beside their media asset. Read each file
to get its full text.

If reviewing prompts that have not yet been saved to files (drafted inline in
`shot.md` or `scene.md`), extract the prompt text from the manifest's `prompt:` field
or inline working copy.

### Step 2 — Detect prompt type and load checklist

For each prompt:
1. Match it to a reviewing skill using the table above.
2. Read the corresponding section from `references/review-checklists.md`.
3. Also load the **universal directing principles** section (applies to all prompts).

### Step 3 — Spawn the review sub-agent

Delegate the review to a sub-agent. The sub-agent receives:
- The full text of each prompt being reviewed.
- The applicable checklist section(s) from `references/review-checklists.md`.
- The universal directing principles.
- Clear instructions on what to check and how to report.

**Batching strategy:**
- All prompts of the same type → one sub-agent reviews them all in one pass.
- Prompts of different types → spawn one sub-agent per type, run in parallel.
- Maximum 5 sub-agents concurrent.

**Delegation mechanisms (host-agnostic):**

Use whichever mechanism the current host provides:

- **OpenCode CLI (non-interactive):**
  `opencode run -m <review-model> "<worker prompt>"`
  Pass the prompt text and checklist inline. Capture stdout for findings.
  (`<review-model>` is the host's configured sub-agent model, not a hard-coded ID.)

- **Host Task / sub-agent tool:**
  Delegate each review batch as a separate task with the prompt text and checklist
  embedded in the task prompt.

- **Fallback (no sub-agent mechanism):**
  The main agent runs the review itself using the same checklist and findings format.
  Do not skip the review — just run it inline.

### Step 4 — Sub-agent prompt template

Use this template when constructing the sub-agent's task prompt. Replace the bracketed
placeholders with actual content.

```text
You are a prompt quality reviewer for BytePlus generative AI models.
Your job is to review prompt(s) against a specific checklist of best practices
and return structured findings. You do NOT fix the prompts — you only identify
issues and suggest fixes.

## Prompt type
<e.g., Seedance 2.5 video prompt>

## Change contract (may change / must preserve)

- MAY CHANGE: <list from the user's request, e.g. "spoken language + lip sync">
- MUST PRESERVE: <list, e.g. "character identity, environment, timing, camera">

## Prompts to review

### Prompt 1: <filename or identifier>
<full prompt text>

### Prompt 2: <filename or identifier>
<full prompt text>

## Review checklist

<paste the applicable checklist section from references/review-checklists.md here>

## Universal directing principles (apply to ALL prompts)

<these are always included — see Universal Directing Principles section below>

## Your task

For each prompt, go through every item in the checklist. For each item:
1. Determine if the prompt satisfies the requirement.
2. If it does not, record a finding.

Report your findings in this exact format:

### Review Findings

#### Prompt: <filename or identifier>

**PASS** — no issues found.

OR

**ISSUES FOUND:**

1. [CRITICAL] <Checklist item name>
   - Problem: <what is wrong>
   - Evidence: <quote the relevant part of the prompt>
   - Suggested fix: <specific, actionable fix>

2. [MAJOR] <Checklist item name>
   - Problem: <what is wrong>
   - Evidence: <quote the relevant part of the prompt>
   - Suggested fix: <specific, actionable fix>

3. [MINOR] <Checklist item name>
   - Problem: <what is wrong>
   - Evidence: <quote the relevant part of the prompt>
   - Suggested fix: <specific, actionable fix>

### Severity definitions
- CRITICAL: Will cause generation failure, safety rejection, identity drift,
  or fundamentally broken output. Must fix before submission.
- MAJOR: Will degrade output quality, cause inconsistency, or violate a core
  directing principle. Should fix before submission.
- MINOR: Could improve quality or clarity but won't break the generation.
  Fix if time allows.

## Rules
- Check every item in the checklist. Do not skip items.
- Quote the exact text from the prompt as evidence.
- Suggested fixes must be specific and actionable — not "improve the prompt".
- If a checklist item does not apply to this prompt type, note "N/A" and move on.
- Do not rewrite the prompt. Only identify issues and suggest fixes.
- Be precise and honest. Do not invent problems that don't exist.
- If the prompt passes all items, say so clearly.
- An item listed under MAY CHANGE is a deliberate instruction — do NOT flag it
  as "modifying the subject" or "not preserving the source". Only flag:
  (a) a breakage of something under MUST PRESERVE, or (b) a real quality defect
  in how the changed thing is described (missing guards, missing numeric
  anchors, missing language reinforcement, ambiguity).
```

### Step 5 — Receive and triage findings

If a sub-agent returns an empty, truncated, or content-free result (or findings
without explicit PASS/FAIL per prompt), retry the same batch once (max 1 retry).
If the retry is still unusable, run the review inline against the same
checklists — never treat an empty sub-agent result as "passed".

When the sub-agent returns findings:

1. **Read all findings** for each prompt.
2. **Triage by severity:**
   - CRITICAL issues — must fix before any generation task is submitted.
   - MAJOR issues — should fix unless the user explicitly waives them.
   - MINOR issues — fix opportunistically; surface to the user.
3. **Deduplicate** — if multiple sub-agents found the same issue (e.g., a universal
   principle violation), merge into one finding.
4. **Cross-check** — if the sub-agent flagged something that you believe is actually
   correct, verify against the skill file before dismissing.

### Step 6 — Apply fixes

The main agent applies fixes directly to the prompt files:

1. For each finding to be fixed, edit the prompt file with the suggested fix.
2. Preserve the prompt's structure and formatting conventions.
3. Do not rewrite the entire prompt — apply only the targeted fix.
4. After applying fixes, note what was changed.

### Step 7 — Re-review changed prompts (if any fixes were applied)

If any CRITICAL or MAJOR fixes were applied, re-review the changed prompts:
- Spawn a new sub-agent (or run inline) with the updated prompt text and the same
  checklist.
- Confirm the fixed issues are resolved and no new issues were introduced.
- If new issues appear, fix and re-review again (maximum 2 re-review rounds).
- If issues persist after 2 rounds, surface to the user for a decision.

### Step 8 — Report to the user

Summarize the review results:

```text
## Prompt Review Complete

### Reviewed
- <prompt file> — <prompt type> — <PASS | N issues fixed>

### Findings summary
- CRITICAL: <count> (all fixed)
- MAJOR: <count> (all fixed)
- MINOR: <count> (<fixed count> fixed, <remaining count> remaining)

### Changes made
- <prompt file>: <what was changed and why>

### Remaining issues (if any)
- <prompt file>: <issue> — <reason not fixed>

### Ready for generation
- <prompt file> — READY
- <prompt file> — BLOCKED (<reason>)
```

## Multi-prompt review

When reviewing multiple prompts (e.g., all prompts for a scene's shots):

1. Group prompts by type.
2. Spawn one sub-agent per type (parallel, max 5 concurrent).
3. Each sub-agent reviews all prompts of its assigned type in one pass.
4. Collect all findings, deduplicate, and apply fixes.
5. Re-review only the prompts that had CRITICAL or MAJOR fixes applied.

This is efficient because:
- Same-type prompts share the same checklist — one sub-agent loads it once.
- Different-type prompts run in parallel without blocking each other.
- The main agent only re-reviews prompts that actually changed.

## Universal directing principles

The canonical universal checklist lives in
`references/review-checklists.md` (§Universal, 10 items). The sub-agent must
check all prompts against that full list plus the type-specific checklist. The
three core rules below summarize the workspace's non-negotiable principles:

1. **Assets first.** Not one shot until every character, location, and prop is named,
   versioned, and locked. The model has no memory — describe everything, every time.
   Locked descriptors go into every prompt word for word; never summarize, shorten,
   or imply a locked descriptor.

2. **Say what you want, not what you avoid.** The words you write are the words you
   summon — including the ones inside a "no". A prohibition still names and summons
   the thing it forbids. Write the positive, specific instruction that produces the
   intended result.

3. **Direct, don't describe.** Write the scene event, motive, goal, obstacle, and
   tactic — not just what things look like. If a prompt reads like a static
   description with no event or intent, it is not yet a shot.

Also check all prompts against the workspace-level conventions in AGENTS.md:
- Watermark should be false by default (if specified in the prompt, it must be false).
- Per-scene duration should be right-sized (4-30s), not padded to fill time.
- Prompt snapshots must be saved beside the media asset, not duplicated elsewhere.
- Generation parameters (duration, resolution, ratio) belong in the API, not the
  prompt text (except where a skill explicitly includes them in the prompt structure).

## Element completeness review

In addition to checking prompt quality, the sub-agent **must** review the
complete set of prompts for a scene or project against the **Element
identification checklist** in AGENTS.md. This is a separate pass from the
per-prompt quality review — it checks whether the plan or prompt set is
*missing* elements that should exist, not whether existing prompts are
well-written.

### How to run the element completeness pass

When the sub-agent receives a set of prompts for review, it also receives:

1. The beat structure / scene description for each shot.
2. The full Elements table from the project's `project.md` or plan (if
   available).

The sub-agent walks every beat of every scene/shot and checks whether every
visible element has a corresponding Element defined and referenced:

| Check | What to look for |
|---|---|
| On-camera characters | Does every person who appears on screen — including people visible *through* a phone/laptop screen during a video call, and any character with dialogue — have a `char_` sheet or reference? |
| Locations / settings | Does every distinct physical space — including transitional spaces and screen-within-screen locations — have a `loc_` sheet? |
| Props (held/operated) | Does every object a character holds, carries, aims, or operates have a `prop_` sheet? Is product packaging a separate prop from the product itself? |
| Screen / UI surfaces | Does every phone screen, laptop screen, tablet, monitor, signage, or text-heavy surface that shows specific content have a `screen_` reference? |
| Brand / title cards | Does every ad/scene that needs a brand end card, lower third, or logo plate have a `card_` image defined? |
| Audio assets | Does every scene that needs a music bed, ambient bed, or recurring SFX have a `library/` asset defined? |
| Costume variants | If a character wears a different outfit in different scenes, is the variant noted or generated as a separate prop sheet? |

### Reporting element findings

The sub-agent reports element completeness findings in a separate section:

```text
### Element Completeness Review

#### Missing elements
1. [CRITICAL] <Element description> — appears in <ad/scene> beat <timestamp>
   but no Element is defined. The model will hallucinate this element.
   Suggested action: Generate a <char_/loc_/prop_/screen_/card_> reference.

2. [MAJOR] <Element description> — referenced in <ad/scene> but not in the
   Elements table. May need a dedicated sheet.

#### Element coverage
- Characters: <count> defined, <count> referenced, <list any gaps>
- Locations: <count> defined, <count> referenced, <list any gaps>
- Props: <count> defined, <count> referenced, <list any gaps>
- Screen UIs: <count> defined, <count> referenced, <list any gaps>
- Title cards: <count> defined, <count> referenced, <list any gaps>
- Audio assets: <count> defined, <count> referenced, <list any gaps>
```

### Severity for element findings

- **CRITICAL:** A visible element with no reference will cause identity drift,
  product inaccuracy, or garbled text/UI. Must generate before video
  submission.
- **MAJOR:** A missing element will degrade quality (e.g. undefined background
  character, missing music bed) but won't break the generation.
- **MINOR:** An element could enhance the production but isn't strictly
  required (e.g. ambient SFX library for a quiet scene).

## Reference file

The consolidated review checklists for all prompt types live in:
`references/review-checklists.md`

Load the relevant section(s) when constructing the sub-agent prompt. The reference is
organized by prompt type with a table of contents at the top for quick navigation.

## Compose with other skills

- After prompts pass review and generation tasks are submitted, consider composing
  with `media-review` to review the generated media output.
- For end-to-end production coordination, `film-production` is the production manager.
- This skill is called by the main agent during prompt-writing work; it does not call
  generation tools itself.
