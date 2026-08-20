---
name: audio-split
description: Splits an audio file into segments for Seed Audio reference preparation. Supports explicit cut points, a max-duration mode (e.g. -m 30 to honor the 30s reference clip limit), and a target segment count. Use when the user needs to divide source audio into multiple reference clips for dubbing, break a long audio file into ≤30s segments, split at dialogue boundaries, or prepare reference audio for Seed Audio voice cloning.
---

# Audio Split

Split a source audio file into segments for Seed Audio reference preparation and
dubbing assembly. Produces segment files plus a `manifest.txt` recording each
segment's absolute offset and duration.

## When to use

- Preparing reference audio clips for Seed Audio (each must be ≤30s, ≤10MB)
- Splitting source audio at dialogue/scene boundaries for dubbing
- Trimming a silent tail or dividing a long track into chunks
- Verifying segment offsets for the offset-mix assembly step

## When NOT to use

- Reassembling generated segments (use `audio-dubbing` offset-mix or `scripts/mix_segments.sh`)
- Generating or composing Seed Audio prompts (use `seed-audio-prompt` or `audio-dubbing`)

## Core limits

| Constraint | Value |
|---|---|
| Max reference clips per request | 3 |
| Max duration per clip | 30 seconds |
| Max size per clip | 10 MB |

- Max 3 reference audio files per Seed Audio request.
- Each clip must be ≤30s. For a 68s file this means **3 clips minimum** (68/30 → 3).
- Splitting at a point like 60s yields a 60s segment that **still exceeds** the 30s
  reference limit — use `-m 30` when preparing actual upload clips.

## Script usage

```bash
scripts/split_segments.sh <input_audio> <output_dir> [cut_points...]
scripts/split_segments.sh -i <input_audio> -o <output_dir> [options]
```

| Option | Description |
|---|---|
| `-b, --boundary SEC` | Add a cut point at `SEC` seconds (repeatable) |
| `-s, --srt FILE` | Snap cut points to subtitle gaps so no dialogue line is cut mid-sentence |
| `-m, --max-duration SEC` | Split so every segment is ≤ `SEC` seconds (e.g. `-m 30`) |
| `-n, --count N` | Split into N equal segments |
| `--overlap SEC` | Overlap each boundary by `SEC` seconds (voice-identity continuity) |
| `--wav` | Output WAV 44.1kHz instead of MP3 320kbps |

Positional `cut_points` are the simplest form: each number starts a new segment.

## SRT-aware splitting

Pass the target-language `.srt` with `-s` to snap each cut point to the nearest
subtitle boundary (start or end). A cut that would land mid-line is moved to the
nearer cue edge, so no sentence is split across reference clips.

```bash
# 30s cut lands inside a cue (29.66-33.07s) → snapped to 29.66s
scripts/split_segments.sh -i source.wav -o segs -s script.srt 30 58.31
```

The same SRT can be used to generate per-segment **relative** timestamps ready
for prompt authoring (timestamps are relative to each segment's start, per the
`audio-dubbing` convention):

```bash
python3 scripts/srt_timestamps.py table script.srt 30 58.31
```

```
=== Segment 1 (abs 0.00s - 29.66s) ===
[1.2s:3.7s] Ms. Ford, alam mong peke ang kasal na ito.
[4.6s:7.7s] Gusto ni Mr. Dawson na wakasan na ang kasal na ito ngayon.
...
```

## Examples

Split the ABS CBN 68s source at 60s into 2 segments (seg2 = silent tail, no dialogue):

```bash
scripts/split_segments.sh original-en-audio.mp3 segs 60
```

Prepare upload-ready reference clips honoring the 30s limit:

```bash
scripts/split_segments.sh -i original-en-audio.mp3 -o segs -m 30
```

Split at natural dialogue boundaries with 2s overlap:

```bash
scripts/split_segments.sh original-en-audio.mp3 segs 22 38 47.5 --overlap 2
```

Split snapped to SRT gaps (never mid-line) and print prompt-ready relative timestamps:

```bash
scripts/split_segments.sh -i original-en-audio.mp3 -o segs -s original-tagalog-script.srt 30 58.31
python3 scripts/srt_timestamps.py table original-tagalog-script.srt 30 58.31
```

## Output

```
segs/
  seg1.mp3
  seg2.mp3
  manifest.txt   # per-segment offset + duration + warnings
```

`manifest.txt` lines:

```
seg1.mp3 offset=0s duration=60s
seg2.mp3 offset=60s duration=8.07s
```

Use these offsets as the `adelay` values in the `audio-dubbing` offset-mix assembly.

## Requirements

- ffmpeg, ffprobe, bc (checked at runtime)
- `-s/--srt` snapping requires Python 3 (uses `scripts/srt_timestamps.py`)
- Only splits files — it does not upload or generate. Pair with `modelark-mcp`
  `media_upload` (upload clips) and `seed_audio_generate` (generate per clip).

## Related skills

- `audio-dubbing` — full dubbing pipeline (reference prep is its Stage 4; use this skill's `-s` snapping and `table` helper there)
- `seed-audio-prompt` — Seed Audio prompt composition
