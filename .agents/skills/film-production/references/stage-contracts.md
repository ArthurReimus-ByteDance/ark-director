# Production Stage Contracts

Use these contracts to determine the next safe stage. A later stage may begin
only when its entry evidence exists. Keep unavailable future departments as
explicit gaps rather than fabricating their outputs.

## 1. Brief and development

Entry: user intent or an existing `project.md`.

Required output: audience, format, runtime, aspect ratio, story objective, tone,
creative constraints, known rights constraints, budget posture, and unresolved
questions recorded in `project.md`. Confirmed directorial defaults (structure,
camera, lens, lighting, grade, pacing, acting, staging, medium, audio) from
`brief-intake` persisted as a `locked` block in `project.md` frontmatter.

Exit: the production objective, constraints, and directorial defaults are clear
enough to break down.

## 2. Scene and production breakdown

Entry: an accepted brief and available story or script material. Draft scene
and shot breakdown may precede canonical asset generation; it identifies which
assets are required and does not make a prompt ready for production submission.

Required output: scene list, cast, locations, props, dialogue, sound needs,
continuity states, delivery assumptions, and scene-level acceptance criteria.

Exit: every planned scene has observable action and an inventory of required
production inputs, with missing approvals recorded as unresolved.

## 3. Canon and elements

Entry: breakdown identifies recurring characters, locations, or props.

Required output: one flat `elements/<element-id>/` folder per reusable element,
manifest, reference files, prompt snapshots, hashes, variants, and lifecycle
states. **Before locking the element list**, walk every beat of every
scene/shot against the Element identification checklist in AGENTS.md — verify
that visible characters, settings, props, screen/UI surfaces, brand/title cards,
and recurring audio have been identified and assigned the appropriate treatment
under the tracked element-identification contract. Recurring/identity-critical
on-camera characters and recurring/geography-critical spaces need canonical
references; incidental people/settings may use descriptors or scene direction.
Screen-only callers use a locked UI with text-directed movement/dialogue, not
character sheets as static screen content. Apply the prop threshold rather than
turning every visible object into a generation requirement. Record missing
required references before dependent tasks are submitted.

Exit: every required canonical element has an approved selected variant, or the
dependent scene is explicitly marked unresolved. The element list has been
cross-checked against the Element identification checklist and no gaps remain.

## 4. Storyboard and visual plan

Entry: scene objective, geography, continuity state, and approved relevant canon
exist before dependent panel generation. A text-only visual plan may be drafted
earlier and stays draft until its input requirements are satisfied.

Required output: beat/panel plan, bound references, prompts, generated panels or
prompt package, continuity review, provenance, and video-handoff eligibility.

Exit: required panels are approved and all source element hashes remain current,
or the scene has an explicitly approved direct-to-video path.

## 5. Audio preparation (optional — when user requests lip-synced dialogue)

Entry: exact dialogue and planned scene duration exist, and the user has
explicitly requested lip-synced dialogue audio.

Required output: exact audio prompt, local audio file, duration, transcript or
dialogue timing, media inspection, SHA-256, and manifest linkage.

Exit: audio duration fits the planned video and dialogue mappings are verified.

When the user has not requested lip-synced audio, skip this stage and proceed
directly to shot generation. Seedance's native audio handles dialogue by
default.

## 6. Shot generation

Entry: shot objective, selected video mode, approved inputs, reference roles,
prompt snapshot target, duration, and any requested audio (if Stage 5 was
completed) exist. Before submission the `prompt-review` gate has passed for
every prompt being submitted; the ordered `references:` array is verified 1:1
against `shot.md` (same files, same order, same `@Image N` / `@Video N` /
`@Audio N` bindings); and the pass uses the lowest suitable resolution for the
current prototype.

Required output: task registry entry, local media, exact prompt snapshot,
provider metadata, actual media properties, cost fields, SHA-256, semantic QA,
and `review` status. Resolution is raised only after the current pass is
approved (final-candidate gate).

Exit: the user approves a take or requests a bounded revision.

## 7. Assembly and review

Entry: approved takes and any requested audio assets exist.

Required output: ordered edit, review render, transition and continuity review,
audio presence check, technical decode QA, and outstanding notes.

Exit: explicit picture and audio approval. Full editorial, color, and sound-post
department contracts are future work tracked in the lifecycle specification.

## 8. Delivery

Entry: approved picture and audio plus a known delivery target.

Required output: inspected master, review proxy if needed, caption or localization
status, delivery metadata, hashes, and archive pointers.

Exit: explicit user approval of the final deliverable.
