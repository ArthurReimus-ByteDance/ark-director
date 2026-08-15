# Cross-Modality Handoff Contracts

## Canon to storyboard

Pass selected element paths, roles, approval states, hashes, and stable prompt
tokens. If an element is not approved, keep the dependent board in `draft` or
`review` and make video handoff ineligible.

## Storyboard to video

Treat elements as identity sources and storyboard panels as derivative
composition anchors. Require explicit panel selection, verify source hashes,
and choose exactly one supported image mode: I2V, FLF2V, R2V, or T2V. Never
promote a multi-panel contact sheet as a clean video keyframe.

## Audio to video (when user requests lip-synced dialogue)

Use the exact same dialogue text in both prompts. Verify audio duration does not
exceed video duration, map dialogue to observed audio timing, pass the file as
`reference_audio`, and record its path and hash in the shot manifest. Skip this
handoff when the user has not requested lip-synced audio.

## Shot to assembly

Accept only user-approved takes. Pass local paths, hashes, actual duration,
resolution, frame rate, audio properties, intended order, transition notes, and
known defects. Do not treat `succeeded` as creative approval.

## Dependency invalidation

When a selected element, audio file, storyboard anchor, or exact prompt changes,
identify every dependent artifact. Return affected downstream artifacts to
`review`; preserve their files, prompts, task IDs, hashes, and rejection history.
