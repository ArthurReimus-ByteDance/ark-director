# Motion Review Prompt — deep frame-by-frame pass

A static "action" description is not enough to reproduce how a template moves.
Run this as a **second** `seed_understand` pass (`thinking=true`,
`reasoning_effort=high`). Feed the existing shot list and its analysis SHA-256
with the prompt. Feed the pin as `@Video 1`; when comparing against a previous
take, feed the generated take as `@Video 2`.

```text
You are a senior motion designer and video analyst. Analyze the attached video
frame by frame and report, exhaustively, how it MOVES.

Use the supplied shot boundaries without renumbering them. For EACH shot report:
1. time range
2. what is in the shot (subjects, background elements, effects)
3. every moving element with its motion type (translate/rotate/scale/parallax/
   drift/float-bob/pulse/flicker/color-cycle/twinkle/shimmer/sway/wave/slide/
   zoom/rotation), direction, speed, amplitude, easing, and loop period
4. camera motion (static/dolly/push/pan/tilt/rotate/shake) — be explicit when
   the camera is truly static and only elements move
5. light/color motion (pulse, strobe, flicker, hue cycle, blink, bloom, shimmer)
   and its rate
6. the single strongest motion cue that makes the shot feel alive

Separate direct observation from uncertain estimates. Give each shot a
low/medium/high confidence and list uncertainty whenever confidence is not high.
Then list the top concrete imperative prompt wording (positive only — say what
moves and how, never negative phrasing) to reproduce the same movement in a
Seedance 2.5 prompt.

Return JSON only, conforming to motion-review-schema.json. Key every result by
shot_index.
```

Use `mode: source` for source-only review. When comparing template vs generated
take, use `mode: comparison` and add per-shot `missing_or_wrong` and
`concrete_fix_prompt_text`, plus `global_diffs` for pace/cut timing, energy
level, and the relevant aesthetic.

## Merge contract

- Write the exact JSON output to `templates/<template-id>/motion-review.json`
  and a readable rendering to `motion-review.md`.
- Validate it with `scripts/validate_breakdown.py <analysis.json>
  --motion-review <motion-review.json>`.
- Merge per-shot motion by `shot_index`, never by array position, into
  `analysis.json` as `shots[].motion` (fields:
  `camera_motion`, `moving_elements[]`, `light_motion`, `strongest_cue`).
- The imperative wording fills the Seedance Action slot; it is **prompt text**
  and must follow positive-only directing principles and pass the Seedance
  `prompt-review` gate before submission.
- Preserve the approved `analysis.vNN.json` bytes and bind their hash as the
  motion review's `source_breakdown_sha256`. Merge valid motion into a new
  analysis revision. If motion review proposes changed timing or action, re-run
  affected gates rather than silently changing an approved decision.
