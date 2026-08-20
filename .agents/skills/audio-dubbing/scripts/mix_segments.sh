#!/usr/bin/env bash
# Usage: mix_segments.sh <source_duration> <output_wav> <seg1.wav>:<offset_ms> [<seg2.wav>:<offset_ms> ...]
# Places each segment at its absolute time offset (in milliseconds) and mixes
# them into a single track, then pads/trim to match the source duration exactly.
#
# Example:
#   mix_segments.sh 68.074671 final.wav seg1.wav:0 seg2.wav:20000 seg3.wav:36000 seg4.wav:47500
#
# Uses adelay + amix normalize=0 to preserve volume across overlapping regions.

set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <source_duration> <output_wav> <seg1.wav>:<offset_ms> [<seg2.wav>:<offset_ms> ...]"
  exit 1
fi

SOURCE_DURATION="$1"
OUTPUT_WAV="$2"
shift 2

command -v ffmpeg >/dev/null 2>&1 || { echo "ERROR: ffmpeg is required"; exit 1; }

INPUT_ARGS=""
FILTER_CHAIN=""
MIX_INPUTS=""
SEG_COUNT=0

for entry in "$@"; do
  FILE="${entry%%:*}"
  OFFSET="${entry##*:}"

  if [ ! -f "$FILE" ]; then
    echo "ERROR: segment file not found: $FILE"
    exit 1
  fi

  IDX=$SEG_COUNT
  INPUT_ARGS="$INPUT_ARGS -i \"$FILE\""
  FILTER_CHAIN="$FILTER_CHAIN[${IDX}:a]adelay=${OFFSET}|${OFFSET}[a$((IDX+1))];"
  MIX_INPUTS="${MIX_INPUTS}[a$((IDX+1))]"
  SEG_COUNT=$((SEG_COUNT+1))
done

MIX_INPUTS="${MIX_INPUTS}amix=inputs=${SEG_COUNT}:duration=longest:dropout_transition=0:normalize=0,apad=whole_dur=${SOURCE_DURATION}[out]"

echo "=== Mixing ${SEG_COUNT} segments ==="
for entry in "$@"; do
  FILE="${entry%%:*}"
  OFFSET="${entry##*:}"
  DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FILE")
  echo "  $(basename $FILE): offset=${OFFSET}ms, duration=${DUR}s"
done

CMD="ffmpeg -y ${INPUT_ARGS} -filter_complex \"${FILTER_CHAIN}${MIX_INPUTS}\" -map \"[out]\" -ac 2 -ar 44100 -t ${SOURCE_DURATION} \"${OUTPUT_WAV}\" -loglevel warning"

echo "=== Running ffmpeg ==="
eval "$CMD"

OUT_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_WAV")
OUT_SIZE=$(ls -lh "$OUTPUT_WAV" | awk '{print $5}')

echo
echo "=== Summary ==="
echo "Output: ${OUTPUT_WAV}"
echo "Duration: ${OUT_DUR}s"
echo "Size: ${OUT_SIZE}"
echo "Segments: ${SEG_COUNT}"
echo "Done."
