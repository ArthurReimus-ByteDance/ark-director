#!/usr/bin/env bash
# Usage: verify_and_mux.sh <source_audio> <generated_audio> <source_video> <output_video>
# Steps:
#   1. Verify inputs exist and ffprobe can read durations
#   2. Pad or trim generated audio to match source duration
#   3. Mux padded audio with source video (video stream copy, audio AAC 192k)
#   4. Verify output duration
#   5. Print summary

set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <source_audio> <generated_audio> <source_video> <output_video>"
  exit 1
fi

SOURCE_AUDIO="$1"
GENERATED_AUDIO="$2"
SOURCE_VIDEO="$3"
OUTPUT_VIDEO="$4"

PADDED_AUDIO="$(dirname "$GENERATED_AUDIO")/_padded_$(basename "$GENERATED_AUDIO")"
CLEANUP_NEEDED=false

cleanup() {
  if [ "$CLEANUP_NEEDED" = true ] && [ -f "$PADDED_AUDIO" ]; then
    rm -f "$PADDED_AUDIO"
  fi
}
trap cleanup EXIT

command -v ffprobe >/dev/null 2>&1 || { echo "ERROR: ffprobe is required"; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "ERROR: ffmpeg is required"; exit 1; }
command -v bc >/dev/null 2>&1 || { echo "ERROR: bc is required"; exit 1; }

for f in "$SOURCE_AUDIO" "$GENERATED_AUDIO" "$SOURCE_VIDEO"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: file not found: $f"
    exit 1
  fi
done

OUTPUT_DIR="$(dirname "$OUTPUT_VIDEO")"
if [ ! -d "$OUTPUT_DIR" ]; then
  mkdir -p "$OUTPUT_DIR"
fi

get_duration() {
  local file="$1"
  local dur
  dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file") || {
    echo "ERROR: ffprobe failed for $file" >&2
    exit 1
  }
  if [ -z "$dur" ] || [ "$dur" = "N/A" ]; then
    echo "ERROR: could not read duration for $file" >&2
    exit 1
  fi
  echo "$dur"
}

echo "=== Duration check ==="
SRC_DUR=$(get_duration "$SOURCE_AUDIO")
GEN_DUR=$(get_duration "$GENERATED_AUDIO")
echo "Source audio:    ${SRC_DUR}s"
echo "Generated audio: ${GEN_DUR}s"

DELTA=$(echo "$SRC_DUR - $GEN_DUR" | bc -l)
DELTA=$(printf "%.6f" "$DELTA")
echo "Difference:      ${DELTA}s"

if (( $(echo "$DELTA > 0.01" | bc -l) )); then
  echo "Padding generated audio by ${DELTA}s..."
  ffmpeg -y -i "$GENERATED_AUDIO" -af "apad=pad_dur=$DELTA" -ac 2 "$PADDED_AUDIO" -loglevel warning
  CLEANUP_NEEDED=true
elif (( $(echo "$DELTA < -0.01" | bc -l) )); then
  echo "WARNING: Generated audio is longer than source by $DELTA. Trimming to match..."
  echo "  (A longer output usually means the model added filler — investigate the prompt.)"
  ffmpeg -y -i "$GENERATED_AUDIO" -t "$SRC_DUR" -ac 2 "$PADDED_AUDIO" -loglevel warning
  CLEANUP_NEEDED=true
else
  echo "Durations match (within 10ms). Using generated audio as-is."
  PADDED_AUDIO="$GENERATED_AUDIO"
fi

PADDED_DUR=$(get_duration "$PADDED_AUDIO")

echo
echo "=== Muxing with video ==="
ffmpeg -y -i "$SOURCE_VIDEO" -i "$PADDED_AUDIO" \
  -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 \
  -shortest \
  "$OUTPUT_VIDEO" -loglevel warning

OUT_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_VIDEO")
OUT_SIZE=$(ls -lh "$OUTPUT_VIDEO" | awk '{print $5}')

echo
echo "=== Summary ==="
echo "Output video: $OUTPUT_VIDEO"
echo "Duration:     ${OUT_DUR}s"
echo "Size:         $OUT_SIZE"
echo "Video codec:  copied from source"
echo "Audio codec:  AAC 192kbps (dubbed)"
echo "Done."
