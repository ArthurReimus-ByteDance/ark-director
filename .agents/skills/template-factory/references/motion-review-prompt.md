# Motion Review Prompt — deep frame-by-frame pass

A static "action" description is not enough to reproduce how a template moves.
Run this as a **second** `seed_understand` pass (`thinking=true`,
`reasoning_effort=high`). Feed the pin as `@Video 1`; when comparing against a
previous take, feed the generated take as `@Video 2`.

```text
You are a senior motion designer and video analyst. Analyze the attached video
frame by frame and report, exhaustively, how it MOVES.

Break the video into every shot/cut. For EACH shot report:
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

Then list the TOP concrete imperative prompt wording (positive only — say what
moves and how, never negative phrasing) to reproduce the same movement in a
Seedance 2.5 prompt.

Return JSON only.
```

When comparing template vs generated take, add per-shot `missing_or_wrong` and a
`concrete_fix_prompt_text`, plus `global_diffs` (pace/cut timing, energy level,
glitch aesthetic).

## Merge contract

- Write the output to `templates/<template-id>/motion-review.md`.
- Merge per-shot motion into `analysis.json` as `shots[].motion` (fields:
  `camera_motion`, `moving_elements[]`, `light_motion`, `strongest_cue`).
- The imperative wording fills the Seedance Action slot; it is **prompt text**
  and must follow positive-only directing principles and pass the Seedance
  `prompt-review` gate before submission.
