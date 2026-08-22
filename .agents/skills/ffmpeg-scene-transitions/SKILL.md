---
name: ffmpeg-scene-transitions
description: >
  Assemble multiple video clips into one film with crossfade scene transitions and
  correct audio/video sync using FFmpeg. Use whenever the user wants to combine
  scenes into a single video, stitch clips with dissolves, crossfade between shots,
  add fade in/out, join AI-generated video scenes into one file, or fix audio/video
  drift in an assembled film. Also trigger on phrases like "assemble the scenes",
  "combine the clips into one video", "add transitions between scenes", "the audio
  is out of sync after combining", or "crossfade the takes together".
---

# FFmpeg Scene Transitions

Assemble an ordered set of video clips into a single film with crossfade
transitions, fades, and locked audio/video sync. This is the assembly step for
multi-scene videos (including AI-generated scenes whose audio stream is often a
little shorter than the video).

## When to use

- Combine several scene/clip files into one deliverable film.
- Add crossfades (dissolves) between shots, or a hard cut at a chosen boundary.
- Add a fade-in at the open and a fade-out at the close.
- Diagnose or fix audio drifting out of sync after clips were joined.

For single-clip operations (trim, resize, speed, extract audio), use the
`ffmpeg` skill instead. This skill is for the multi-clip assembly.

## Why sync drifts (read this first)

AI-generated clips frequently carry an audio stream that is slightly shorter
than the video stream (e.g. ~90 ms per 30 s at 32 kHz AAC padding). When you
crossfade, the video chain advances by each clip's *video* duration while the
audio chain advances by each clip's *audio* duration. The mismatch accumulates
at every boundary — a 0.3 s/0.5 s lip-sync drift by the last scene after four
joins. The fix is to pad each clip's audio to its exact video duration before
crossfading, so both chains walk the same timeline.

## Step 1 — Preflight the clips

Check every input before assembling:

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,duration -of csv=p=0 clip.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration -of csv=p=0 clip.mp4
```

Confirm:

- same video codec, resolution, and frame rate across all clips (else re-encode
  them to a common spec first);
- each clip's **video duration** and **audio duration** (they may differ);
- the audio sample rate (all clips should match, or `acrossfade` will resample).

Record the video duration `D` of each clip (for the offset math) and note any
clip whose audio is shorter than its video.

## Step 2 — Choose the transition plan

Decide per boundary:

- **Crossfade (dissolve)**: smooth, standard between scenes. Duration 0.3–1 s.
- **Hard cut**: no transition. Use where a cut reads better (e.g. a deliberate
  time/location jump), or per the user's direction.
- **Open/close fades**: typically 0.5 s fade-in at the start and fade-out at the
  end of the whole film.

Write the plan as an ordered list of boundaries with their transition type and
duration, e.g. `cut, 0.5s, 0.5s, 0.5s` for four boundaries.

## Step 3 — Compute xfade offsets

For N clips of equal video duration `D`, transition durations `d1..d(N-1)`
(d1 is between clip 1 and clip 2, etc.), the `xfade` offset for transition `i`
is:

```
offset_i = i * D - (d1 + d2 + ... + di)
```

Final duration = `N * D - sum(d)`.

Example: `D = 30.041667`, transitions `[0.3, 0.5, 0.5, 0.5]`:

| Boundary | offset | Combined so far |
|---|---|---|
| 1 | 29.74 | 59.78 |
| 2 | 59.28 | 89.33 |
| 3 | 88.83 | 118.87 |
| 4 | 118.37 | 148.41 |

Use these exact offsets in the `xfade` chain below. If the clips have *different*
durations, compute each offset cumulatively instead (offset_i = time in the
combined stream where clip i+1 starts appearing = combined_duration_so_far - d_i).

## Step 4 — Build the command

Template for 5 clips (0=first … 4=last). Adjust the number of `-i` inputs, the
`xfade`/`acrossfade` links, and the offsets to your plan. The key details:

- `settb=AVTB` on every video branch prevents an `xfade` timebase mismatch.
- `apad=whole_dur=<D>` on every audio branch pads each clip's audio to the video
  duration, keeping the audio timeline locked to the video.
- `afade`/`fade` handle the open and close.

```bash
D=30.041667   # per-clip VIDEO duration in seconds (from Step 1)

ffmpeg -y -v error \
 -i clip0.mp4 -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 -i clip4.mp4 \
 -filter_complex "\
[0:v]fade=t=in:st=0:d=0.5,settb=AVTB[v0];\
[1:v]settb=AVTB[v1];[2:v]settb=AVTB[v2];[3:v]settb=AVTB[v3];[4:v]settb=AVTB[v4];\
[v0][v1]xfade=transition=fade:duration=0.3:offset=29.74[v01];\
[v01][v2]xfade=transition=fade:duration=0.5:offset=59.28[v02];\
[v02][v3]xfade=transition=fade:duration=0.5:offset=88.83[v03];\
[v03][v4]xfade=transition=fade:duration=0.5:offset=118.37[v04];\
[v04]fade=t=out:st=147.9:d=0.5[vout];\
[0:a]apad=whole_dur=$D,afade=t=in:st=0:d=0.5[a0];\
[1:a]apad=whole_dur=$D[a1];[2:a]apad=whole_dur=$D[a2];\
[3:a]apad=whole_dur=$D[a3];[4:a]apad=whole_dur=$D[a4];\
[a0][a1]acrossfade=d=0.3[a01];\
[a01][a2]acrossfade=d=0.5[a02];\
[a02][a3]acrossfade=d=0.5[a03];\
[a03][a4]acrossfade=d=0.5[a04];\
[a04]afade=t=out:st=147.9:d=0.5[aout]" \
 -map "[vout]" -map "[aout]" \
 -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p \
 -c:a aac -b:a 192k -ar 48000 -movflags +faststart \
 film_v01.mp4
```

Notes:

- The fade-out `st` = final_duration - fade_duration (148.41 - 0.5 ≈ 147.9).
- `apad=whole_dur` pads; if a clip's audio is *longer* than its video, trim it
  first with `atrim=0:$D`.
- For a hard cut at a boundary, use `concat` (or `concat` the pair first) instead
  of `xfade` for that join — the `settb=AVTB` on the `concat` output keeps the
  timebase uniform for the following `xfade`.

## Step 5 — Verify the result

```bash
# Total duration and streams
ffprobe -v error -show_entries format=duration,size -of csv=p=0 film_v01.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 film_v01.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 film_v01.mp4

# Full decode (any output = error)
ffmpeg -v error -i film_v01.mp4 -f null -
```

Pass criteria:

- video duration ≈ expected final duration (from Step 3);
- audio duration within ~10 ms of the video duration (this proves the drift fix
  held through the whole chain);
- decode reports no errors.

Optionally build a boundary contact sheet (one frame just before/after each
transition) and open the film to eyeball the cuts.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `xfade` fails: "main timebase … do not match" | mixed timebases (e.g. a `concat` output feeding `xfade`) | add `settb=AVTB` to every video branch |
| audio leads/lags video, worse in later scenes | audio shorter than video per clip; `acrossfade` walked a shorter timeline | `apad=whole_dur=$D` on each audio branch |
| jump/cut where a crossfade was wanted | wrong offset or a missing `xfade` link | recompute offsets from Step 3 |
| audio resampled unexpectedly | clips have different sample rates | re-encode all clips to one sample rate first |
| last scene audio ends early | fade-out `st` too large | set `st = final_duration - fade_duration` |

## Reference

- `ffmpeg` skill — general single-clip operations and the same crossfade recipe
  in its "Crossfade assembly — A/V sync pitfall" section.
