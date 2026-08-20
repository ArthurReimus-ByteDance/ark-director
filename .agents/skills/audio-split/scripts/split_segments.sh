#!/usr/bin/env bash
# split_segments.sh - Split an audio file into segments for Seed Audio reference prep.
# Usage:
#   split_segments.sh <input_audio> <output_dir> [cut_points...]
#   split_segments.sh -i <input_audio> -o <output_dir> [options]
#
# Examples:
#   split_segments.sh original-en-audio.mp3 segs 60
#     -> seg1 (0-60s), seg2 (60s-end)
#   split_segments.sh -i original-en-audio.mp3 -o segs -m 30
#     -> segments, each <= 30s (Seed Audio reference limit)

set -euo pipefail

INPUT=""
OUTDIR=""
CUTS=()
MAX_DUR=""
COUNT=""
OVERLAP=0
FMT="mp3"
SRT=""

print_help() {
  cat <<'EOF'
Usage:
  split_segments.sh <input_audio> <output_dir> [cut_points...]
  split_segments.sh -i <input_audio> -o <output_dir> [options]

Splits an audio file into segments for Seed Audio reference preparation.

Positional arguments:
  input_audio       source audio file (anything ffmpeg can read)
  output_dir        directory where segment files + manifest are written
  cut_points...     explicit cut times in seconds; each starts a new segment

Options:
  -i, --input FILE        source audio file
  -o, --outdir DIR        output directory
  -b, --boundary SEC      add a cut point at SEC seconds (repeatable)
  -m, --max-duration SEC  split so every segment is at most SEC seconds
  -n, --count N           split into N equal segments
  -s, --srt FILE          snap cut points to subtitle gaps (never mid-line)
      --overlap SEC       overlap each boundary by SEC seconds
      --wav               output WAV 44.1kHz instead of MP3 320kbps
  -h, --help              show this help

Seed Audio 1.0 reference limit: each clip must be <= 30 seconds and <= 10 MB.
Use `-m 30` when preparing reference clips for upload.
EOF
}

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) print_help; exit 0 ;;
    -i|--input) INPUT="$2"; shift 2 ;;
    -o|--outdir) OUTDIR="$2"; shift 2 ;;
    -b|--boundary) CUTS+=("$2"); shift 2 ;;
    -m|--max-duration) MAX_DUR="$2"; shift 2 ;;
    -n|--count) COUNT="$2"; shift 2 ;;
    -s|--srt) SRT="$2"; shift 2 ;;
    --overlap) OVERLAP="$2"; shift 2 ;;
    --wav) FMT="wav"; shift ;;
    --) shift; while [[ $# -gt 0 ]]; do POSITIONAL+=("$1"); shift; done ;;
    -*) echo "ERROR: unknown option: $1" >&2; print_help >&2; exit 1 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [[ -z "$INPUT" && ${#POSITIONAL[@]} -ge 1 ]]; then INPUT="${POSITIONAL[0]}"; POSITIONAL=("${POSITIONAL[@]:1}"); fi
if [[ -z "$OUTDIR" && ${#POSITIONAL[@]} -ge 1 ]]; then OUTDIR="${POSITIONAL[0]}"; POSITIONAL=("${POSITIONAL[@]:1}"); fi
if [[ ${#POSITIONAL[@]} -gt 0 ]]; then CUTS+=("${POSITIONAL[@]}"); fi

command -v ffmpeg  >/dev/null 2>&1 || { echo "ERROR: ffmpeg is required"  >&2; exit 1; }
command -v ffprobe >/dev/null 2>&1 || { echo "ERROR: ffprobe is required" >&2; exit 1; }
command -v bc      >/dev/null 2>&1 || { echo "ERROR: bc is required"      >&2; exit 1; }

[[ -n "$INPUT" ]]  || { echo "ERROR: input audio file is required" >&2; exit 1; }
[[ -f "$INPUT" ]]  || { echo "ERROR: file not found: $INPUT"       >&2; exit 1; }
[[ -n "$OUTDIR" ]] || { echo "ERROR: output directory is required" >&2; exit 1; }
mkdir -p "$OUTDIR"

TOTAL=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT")
[[ -n "$TOTAL" && "$TOTAL" != "N/A" ]] || { echo "ERROR: could not read duration of $INPUT" >&2; exit 1; }

if [[ -n "$MAX_DUR" && ${#CUTS[@]} -gt 0 ]]; then echo "ERROR: -m cannot combine with cut points" >&2; exit 1; fi
if [[ -n "$COUNT" && ${#CUTS[@]} -gt 0 ]]; then echo "ERROR: -n cannot combine with cut points" >&2; exit 1; fi

if [[ -n "$MAX_DUR" ]]; then
  N=$(echo "scale=0; (${TOTAL} + ${MAX_DUR} - 1) / ${MAX_DUR}" | bc)
  for k in $(seq 1 $((N - 1))); do
    CUTS+=("$(echo "scale=3; ${k} * ${MAX_DUR}" | bc)")
  done
elif [[ -n "$COUNT" ]]; then
  STEP=$(echo "scale=3; ${TOTAL} / ${COUNT}" | bc)
  for k in $(seq 1 $((COUNT - 1))); do
    CUTS+=("$(echo "scale=3; ${k} * ${STEP}" | bc)")
  done
fi

for c in "${CUTS[@]}"; do
  if [[ $(echo "$c <= 0" | bc) -eq 1 || $(echo "$c >= $TOTAL" | bc) -eq 1 ]]; then
    echo "ERROR: cut point out of range (0 < $c < $TOTAL)" >&2; exit 1
  fi
done

if [[ -n "$SRT" ]]; then
  if [[ ! -f "$SRT" ]]; then
    echo "ERROR: SRT file not found: $SRT" >&2; exit 1
  fi
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  SNAPPED=$(python3 "$SCRIPT_DIR/srt_timestamps.py" snap "$SRT" "${CUTS[@]}") || {
    echo "ERROR: failed to snap cut points against $SRT" >&2; exit 1;
  }
  CUTS=()
  while IFS= read -r line; do
    [[ -n "$line" ]] && CUTS+=("$line")
  done <<< "$SNAPPED"
  echo "=== Snap to subtitle gaps ==="
  echo "Cut points: ${CUTS[*]}"
fi

MANIFEST="$OUTDIR/manifest.txt"
: > "$MANIFEST"

emit_segment() {
  local n="$1" start="$2" dur="$3"
  local out="$OUTDIR/seg${n}.${FMT}"
  if [[ "$FMT" == "mp3" ]]; then
    ffmpeg -y -ss "$start" -i "$INPUT" -t "$dur" -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 "$out" -loglevel warning
  else
    ffmpeg -y -ss "$start" -i "$INPUT" -t "$dur" -ac 2 -ar 44100 "$out" -loglevel warning
  fi
  local durs
  durs=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$out")
  local end
  end=$(echo "scale=3; ${start} + ${dur}" | bc)
  echo "seg${n}.${FMT} offset=${start}s duration=${durs}s" | tee -a "$MANIFEST"
  if [[ $(echo "$dur > 30.01" | bc) -eq 1 ]]; then
    echo "  WARNING: seg${n} is ${dur}s > 30s Seed Audio reference limit — split further (e.g. -m 30)" | tee -a "$MANIFEST"
  fi
}

echo "=== Splitting $INPUT (${TOTAL}s) ==="
PREV=0
IDX=1
for CUT in "${CUTS[@]}"; do
  START=$(echo "scale=3; ${PREV} - ${OVERLAP}" | bc)
  if [[ $(echo "$START < 0" | bc) -eq 1 ]]; then START=0; fi
  DUR=$(echo "scale=3; ${CUT} - ${START}" | bc)
  emit_segment "$IDX" "$START" "$DUR"
  PREV="$CUT"
  IDX=$((IDX + 1))
done
START=$(echo "scale=3; ${PREV} - ${OVERLAP}" | bc)
if [[ $(echo "$START < 0" | bc) -eq 1 ]]; then START=0; fi
DUR=$(echo "scale=3; ${TOTAL} - ${START}" | bc)
emit_segment "$IDX" "$START" "$DUR"

echo
echo "=== Summary ==="
echo "Input:    $INPUT (${TOTAL}s)"
echo "Segments: $IDX"
echo "Manifest: $MANIFEST"
echo "Done."
