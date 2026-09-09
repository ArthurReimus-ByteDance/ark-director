---
name: seedance-restoration
description: >
  Write Seedance 2.5 video-to-video restoration prompts that remove film grain,
  video noise, black and white scratch lines, vertical and horizontal scratches,
  hairlines, streaks, dust, dirt, flicker, and compression artifacts from aged,
  damaged, or archival footage while preserving every person, object, action,
  composition, camera movement, and timing. Use whenever the user asks to
  restore, clean, denoise, or repair old, aged, or archival footage, remove
  grain or noise, erase scratch lines or film damage, or "clean up" damaged
  film through the Seedance generative-edit route. Prompt-composition only; the
  caller owns submission and the generation lifecycle.
---

# Seedance Restoration

Write production-grade **Seedance 2.5 video-to-video restoration prompts** that
clean aged, damaged, or archival footage. This is a generative re-render: the
source clip is the sole editing master, and the prompt directs the model to
erase surface damage while locking everything the shot actually contains.

Use this skill when the user wants to:

- **restore / clean / repair** old, aged, or archival footage
- **denoise** — remove film grain and video noise
- **remove scratch lines** — black lines, white lines, vertical/horizontal
  scratches, hairlines, streaks from aged film prints
- **clean up** dust, dirt, flicker, and compression artifacts

Do **not** use for deterministic VOD AI enhancement (`vod_enhance_video`) or
FFmpeg denoisers — this skill is the Seedance generative-edit route. For the
general edit grammar and the full six-part formula, compose with
`seedance-prompt-25`; for the submission lifecycle, use the modelark MCP tools.

> **Known ceiling.** Seedance re-renders the picture; aggressive cleanup trades
> fine-detail fidelity for smoothness, and there is a real limit to how far a
> generative model cleans before it starts re-interpreting the image. If
> residual grain or lines remain after escalation, surface the deterministic
> alternative (temporal denoiser + scratch-removal filters in FFmpeg) rather
> than promising a generative fix.

## Input and output contract

Input: an inspected source clip, the requested cleanup targets, and the
may-change / must-preserve contract.

Output: a Seedance 2.5 structured-edit prompt with the source bound as `@Video 1`.

## Procedure

1. **Inspect the source.** Probe duration, fps, resolution, and aspect. Read the
   actual defect mix from the footage — is it grain, scratch lines, flicker, or
   all of the above? This drives which defect to name as dominant.
2. **Trim to the 30s ceiling.** Seedance 2.5 caps edits at 30s. If the source is
   longer, trim to ≤29s before upload; the edit auto-locks duration to the input.
3. **Choose an escalation level** (below) based on how much cleanup is wanted and
   what the last take under-delivered on.
4. **Write the prompt** using the canonical template. Make the dominant defect
   explicit and dominant; never bury it in a mixed list.
5. **Run `prompt-review`** against the Seedance 2.5 edit checklist before
   submission.
6. **Re-mux original audio** afterward. Seedance regenerates native audio; for
   "keep everything the same," mux the source audio back onto the restored video.

## Escalation ladder

Field-tested levels, least → most aggressive. Escalate one step when the
previous take leaves residual damage; change only the wording and defect
emphasis, keep the preserve-locks stable.

| Level | Dominant target | Key phrasing |
|---|---|---|
| **1 — gentle cleanup** | scratches, dust, grain as a mixed list | "restore and clean the archival footage" |
| **2 — aggressive denoise** | grain / noise | "grain removal is the dominant task — push it hard, frame by frame, until no visible noise or shimmer remains" |
| **3 — scratch lines + grain** | black/white scratch lines **and** grain | "black lines and scratches … are a dominant defect — eliminate every one of them, frame by frame, until no line or scratch remains" |

## Canonical prompt template (Seedance 2.5 edit)

```text
[Edit Goal]
Edit @Video 1 to <aggressively/completely> remove <dominant defect(s) — name them
explicitly: film grain, video noise, black lines, white lines, vertical scratches,
horizontal scratches, hairlines, streaks>, so the final image is clean, temporally
stable, and free of <grain and line> artifacts, while every person, object, action,
composition, camera movement, and timing stays exactly as it is.

[Source Video Role]
@Video 1 is the sole editing master. It defines the people, their faces, clothing,
and body language, the scene and background, the actions and event order, the camera
position and movement, and the lighting and color.

[Edit Scope]
Aggressively remove all old-film damage across the entire video: film grain, video
noise, black lines, white lines, vertical scratches, horizontal scratches, hairlines,
streaks, dust, dirt, flicker, and compression artifacts. <Name the dominant defect
and push it hard: "…are a dominant defect — eliminate every one of them, frame by
frame, until no … remains."> Denoise temporally so grain does not flicker between
frames, without introducing motion blur, ghosting, or trailing on moving subjects
or the camera. Remove only the film-print grain, noise, and scratch artifacts —
retain the real surface texture of skin, fabric, and objects. Keep edges crisp —
do not soften the image into a blurry or mushy picture. Do not modify any person's
face, body, clothing, or gestures; do not modify the background objects, set, or
props; do not modify the camera movement, framing, or cuts; do not modify the
lighting direction, color grade, contrast, or exposure. Exactly one of each person
remains in frame — never a second or duplicated copy.

[Content to Preserve]
Keep every person's identity, face, expression, body, clothing, and motion from
@Video 1 unchanged. Keep the scene, background, set, props, camera position, camera
movement, framing, cuts, event order, and timing from @Video 1 unchanged. Keep the
lighting direction, color, contrast, and exposure from @Video 1 unchanged. Faces
stay real and natural — never waxy, plastic, or warped; faces stay naturally
grounded in the scene with no cut-out edge, no halo; rim light matches the key
direction.
```

## Guardrails

- **Name the dominant defect, don't hedge.** A mixed list with "keep everything
  exactly the same" makes the model timid and under-cleans. Make the target
  defect explicit and dominant.
- **The discriminator line is mandatory.** Always include "remove only the
  film-print grain, noise, and scratch artifacts — retain the real surface
  texture of skin, fabric, and objects." This is what prevents the model from
  over-smoothing into waxy/plastic skin when you push grain removal hard.
- **Never demand contradictory absolutes.** "Completely remove all grain" plus
  "keep every pore and fine hair" is physically unresolvable and invites
  over-smoothing. Rank the outcome: cleanup first, detail second.
- **Single source reference.** Only `@Video 1` is bound; no image/audio
  references. `[Target Material Role]` is omitted.
- **Preservation locks.** Quantity ("exactly one … never a second or duplicated
  copy"), grounding ("no cut-out edge, no halo; rim light matches the key
  direction"), and face protection ("never waxy, plastic, or warped") belong in
  every prompt that preserves people.
- **Submission.** `omni_reference_task_type="edit"`, `resolution` 480p/720p/1080p
  (2.5 has no 4K), `watermark: false`. Duration auto-locks to the input — do not
  set it.
- **Temporal denoising with a no-ghosting guard.** Always pair the temporal
  instruction with "without introducing motion blur, ghosting, or trailing."

## Self-check checklist

1. `[Edit Goal]` is one sentence, begins "Edit @Video 1 to …", and names the
   dominant defect explicitly.
2. `[Source Video Role]` declares `@Video 1` the sole editing master.
3. `[Edit Scope]` names the change, pushes the dominant defect hard, and carries
   the "exactly one … never a second" quantity guard.
4. The discriminator line ("remove only the film-print … retain real surface
   texture") is present.
5. Temporal denoising is paired with the no-blur/ghosting/trailing guard.
6. `[Content to Preserve]` locks identity, motion, timing, camera, and lighting.
7. Grounding and face-protection locks are present when people are in frame.
8. No `[Target Material Role]` section (single `@Video 1` source only).
9. Source trimmed to ≤29s before submission; no duration embedded in the prompt.
10. Prompt-review gate passed before submission; original audio re-muxed after.
