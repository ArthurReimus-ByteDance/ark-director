---
name: audio-dubbing
description: "Dubs video or audio from one language to another using Seed Audio 1.0 voice cloning (TA2A). Takes a source audio/video file and a target-language script, clones all speaker voices from the original, preserves timing and pauses, and overlays the new audio onto the original video. Use this skill whenever the user asks to dub audio/video, translate audio with voice cloning, create a language dub, replace dialogue in a video with another language while keeping the same voices, do voice-over localization, or produce a multi-language version of a video using the original actors' voices. Also trigger when the user mentions dubbing, voice cloning for translation, audio localization, or replacing spoken dialogue in a clip. Works with any language pair supported by Seed Audio cross-lingual synthesis."
---

# Audio Dubbing

End-to-end dubbing pipeline: take source audio/video + target-language script → clone all original voices → generate target-language audio with matching timing → overlay onto original video.

Built on BytePlus Seed Audio 1.0 TA2A (Text + Audio-to-Audio) with cross-lingual synthesis and the `modelark-mcp` MCP server.

## When to use

- User has a video or audio clip and wants it dubbed into another language
- User wants to preserve the original speakers' voices in the new language
- User asks for "voice cloning translation," "dub this video," "make a [language] version," "localize audio," or "replace dialogue"
- User has a script/SRT in the target language and wants it spoken by the original cast
- User provides source media + translated script and expects output audio and/or dubbed video

## When NOT to use

- User just wants a single TTS voice reading text (use `seed-audio-prompt` skill)
- User wants a full soundscape with music + SFX (use `seed-audio-commercial` or `seed-audio-prompt`)
- User wants to edit video visuals (use `seedance-vfx-pipeline` or `seedance-prompt-25`)
- User wants the video's **lip movement to re-sync** to the new language (this skill overlays cloned audio on unchanged frames; for re-rendered lip-sync use the Seedance 2.5 audio edit in `seedance-vfx-prompt`)
- User wants to transcribe/translate without audio output (use Seed 2.1 understand + translation)

## Core concepts

**TA2A** — Text + Audio-to-Audio. Seed Audio 1.0 can take reference audio and generate new audio that clones the voice timbre, cadence, emotion, and pacing from the reference, but with different text content in a (potentially different) language.

**@Audio1 reference convention** — The source audio is always labeled `@Audio1` in the prompt. If there are multiple reference clips (separated per speaker), label them `@Audio1`, `@Audio2`, etc.

**Single-reference multi-speaker cloning** — When the source audio contains multiple speakers, a single reference clip is sufficient. Seed Audio can extract distinct speaker identities from a single clip and clone each one. The prompt must clearly identify each speaker by role and map them to their dialogue lines.

**Timestamp-based pacing** — The `[start_s:end_s]` bracket notation controls per-line timing. This is how you preserve pauses, pacing, and scene rhythm from the original.

## Source authority

- Seed Audio 1.0 API Reference — https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01
- Seed Audio 1.0 Prompting Guide (internal) — https://bytedance.larkoffice.com/wiki/WgU4wFVQ8iZgvjkHHdbcDmhCnug
- Seed Audio 1.0 Pricing — https://docs.byteplus.com/en/docs/byteplusvoice/audiopricing

## Quick limits

| Parameter | Limit |
|---|---|
| `text_prompt` max characters | 3,000 |
| Max generated audio per call | 120 seconds (2 min) |
| Max reference audio clips | 3 |
| Per reference clip max size | 10 MB |
| Per reference clip max duration | 30 seconds |
| Timestamp precision | ~100 ms |
| Reference formats | WAV, MP3, PCM, OGG_OPUS |
| Pricing | $0.15 / minute of generated audio |

**Two segmentation triggers — know the difference:**

- **Reference segmentation** (source >30s): The 30s per-clip limit means sources longer than 30s must be split into multiple reference clips. Each clip gets its own generation, and outputs are mixed at absolute time offsets. This applies even when the source is well under the 120s generation limit.
- **Generation segmentation** (source >120s): The 120s generation cap requires splitting the prompt AND reference into multiple generation passes, then concatenating.

**Supported languages (20):** English, Chinese, Japanese, Korean, Mexican Spanish, Castilian Spanish, Indonesian, German, Brazilian Portuguese, French, Thai, Vietnamese, Malay, Filipino, Italian, Russian, Dutch, Polish, Turkish, Swedish.

**Key constraint:** 3,000 char prompt limit. Long scripts require splitting the prompt AND/OR the audio into segments. The 120s generation limit is also a hard cap.

## Workflow

The dubbing pipeline has 7 stages. Do them in order.

```
1. Preflight → 2. Character identification → 3. Prompt authoring
   → 4. Reference preparation → 5. Generation → 6. Assembly → 7. Video overlay
```

### Stage 1: Preflight

Gather and verify all inputs before generating anything.

**Required inputs:**
- Source audio or video file (the original)
- Target-language script (text, SRT, VTT, or plain text per line)
- Target language name

**Verification checklist:**
- [ ] Source file exists and is readable
- [ ] Source audio duration (use `ffprobe`)
- [ ] Source audio is ≤ 120s (single pass) or needs generation segmentation
- [ ] Source audio is ≤ 30s (single reference clip) or needs reference segmentation
- [ ] Target script has the same number of lines as the original has spoken segments
- [ ] Target script is in the correct language (verify by reading it)
- [ ] Target language is supported by Seed Audio cross-lingual synthesis (see supported languages above)
- [ ] If source is video, extract audio track first

**Common preflight issues and fixes:**

| Issue | Fix |
|---|---|
| Source audio >10MB (reference upload limit) | Compress to MP3 (see Stage 4 for recipe) — voice cloning quality is preserved at compressed bitrates |
| Source audio >30s (reference clip limit) | Split into reference segments at natural scene boundaries; each clip must be ≤30s; generate separately and mix at absolute offsets (see Reference segmentation below) |
| Source audio >120s (generation limit) | Split into generation segments at natural scene boundaries; generate each separately; concatenate after |
| Prompt >3,000 chars | Shorten pronunciation guides, remove verbose descriptions, use abbreviated character profiles |
| Source is video (not audio) | Extract audio with `ffmpeg -i input.mp4 -vn -acodec libmp3lame -b:a 320k -ac 2 audio_ref.mp3` |
| No target script provided | Transcribe first with speech-to-text, then translate; do NOT proceed without an approved script |
| Target script is SRT/VTT | Parse timestamps and line text from the subtitle file; use the timestamps directly in the Seed Audio prompt |

### Stage 2: Character identification

Before writing the prompt, identify every speaker and assign them to dialogue lines. This is critical — getting a speaker wrong creates a jarring dub.

**How to identify speakers:**
1. Read the target script and note who is being addressed, who is referenced, who uses first-person pronouns
2. Look for proper noun references (names, titles, "your client," "my grandson")
3. Map each line to a speaker
4. Verify the count matches the audible number of distinct voices in the source
5. If uncertain, use Seed 2.1 multimodal understanding (the `seed_understand` MCP tool, model `dola-seed-2-1-turbo-260628`) to analyze the script context

**Character mapping template:**
```
Speaker A — [role description], [voice quality], [emotional baseline] — speaker number X in @Audio1
Speaker B — [role description], [voice quality], [emotional baseline] — speaker number Y in @Audio1
Speaker C — [role description], [voice quality], [emotional baseline] — speaker number Z in @Audio1
```

**Always confirm with the user if speaker identity is ambiguous.** Never guess. But if the script context makes it clear (e.g., "my grandson" = grandmother, "your client" = lawyer addressing client's representative), proceed and note the reasoning.

### Stage 3: Prompt authoring

Write the Seed Audio TA2A prompt. Keep it under 3,000 characters.

**Prompt structure (compact form):**

```
@Audio1: [source reference description — what to clone]. Clone all voice timbres,
cadence, emotion, pacing, pauses, speaker order, and scene timing exactly.
Same [N] characters speaking in same order. Only change dialogue from
[source language] to [target language] using the script below.
Preserve room tone and acoustic character of @Audio1.

[N] speakers from @Audio1:
A — [role] (age/gender, voice quality) — [which voice in the source]
B — [role] (age/gender, voice quality) — [which voice in the source]
...

Match every pause, rhythm, and gap in @Audio1 exactly.
No music, no SFX — pure dialogue dub.

[Speaker X] says [delivery]: "[start_s:end_s] [target dialogue line]"
[Speaker Y] says [delivery]: "[start_s:end_s] [target dialogue line]"
...

Pronunciation: [target language pronunciation notes, stress patterns,
intonation guidance. Keep concise — only the essential patterns.]

Ending: Clean ending matching @Audio1 exactly, same tail silence and room tone.
```

**Prompt length budget (≈3,000 chars):**
- Reference + speaker setup: ~400 chars
- Dialogue lines: ~1,500–2,000 chars (varies by script length)
- Pronunciation guide: ~300–500 chars
- Ending + other: ~100 chars

**If the prompt is too long:**
1. Cut pronunciation guide to only the most critical words (10–15 key terms)
2. Shorten character descriptions to 5–10 words each
3. Reduce stage directions to a single word per line ("calmly," "firmly")
4. Remove any redundant phrases
5. If still too long, split into segments (see "Long-form dubbing" below)

**Timestamp conventions:**
- Use the original SRT/VTT timestamps directly if available
- If no SRT, estimate timestamps based on line count and total duration
- Timestamps use seconds with one decimal: `[1.2s:3.7s]`
- Gaps between lines = room tone / silence matching the original

**Timestamp behavior and limitations:**
- Precision is approximately 100ms — the model fits delivery into the timestamp window but not to frame-exact precision
- The model **fits each line's delivery into the window** — it speeds up, slows down, and places pauses to make the line land within `[start:end]`
- Lines without timestamps are paced naturally by the model
- Long gaps between lines (2s+) are difficult for the model to preserve as silence — it tends to compress or fill them. For critical gaps, split into separate segments at the gap boundary and handle silence in assembly
- Timestamps are most effective when each line's window matches the original speech duration closely

### Stage 4: Reference preparation

Prepare the source audio for upload as a Seed Audio reference. The **30-second per-clip limit** is the primary constraint — not file size.

**Use the `audio-split` skill to do this.** It splits sources into ≤30s reference clips at cut points you choose, snaps cuts to subtitle gaps when given the target `.srt` (`-s` flag, never cuts mid-line), outputs MP3 320kbps clips + a `manifest.txt` with offsets, and can print per-segment relative timestamps for prompt authoring:

```bash
# Split source at scene boundaries, snapped to SRT gaps (never mid-line)
.agents/skills/audio-split/scripts/split_segments.sh -i source.wav -o segs -s script.srt 22 40
# Show per-segment relative [start:end] timestamps for the prompts
python3 .agents/skills/audio-split/scripts/srt_timestamps.py table script.srt 22 40
```

**Single reference clip (source ≤30s):**
When the source is under 30s and under 10MB, compress to MP3 and upload one clip labeled `@Audio1`. This is the simplest case — one generation covers the full source.

**Reference segmentation (source >30s, ≤120s):**
When the source exceeds 30s but fits within the 120s generation limit, split into multiple reference clips at natural boundaries (scene gaps, dialogue pauses, speaker handoffs). Each clip must be ≤30s. Overlap clips by 2–3 seconds at boundaries to preserve voice identity continuity. Each clip gets its own generation with timestamps **relative to that clip's start** (not absolute timeline time). After generation, mix segments at their absolute offsets using `adelay` + `amix` (see Stage 6).

**Splitting recipe:**
```bash
# Split a 68s source into 4 clips at natural boundaries
# Clip 1: 0s–22s, Clip 2: 20s–38s (2s overlap), Clip 3: 36s–49.5s, Clip 4: 47.5s–68s
ffmpeg -ss 0 -t 22 -i source.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg1_ref.mp3
ffmpeg -ss 20 -t 18 -i source.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg2_ref.mp3
ffmpeg -ss 36 -t 13.5 -i source.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg3_ref.mp3
ffmpeg -ss 47.5 -t 20.5 -i source.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg4_ref.mp3
```

**Splitting rules:**
- Split at natural boundaries: scene transitions, dialogue pauses (2s+), speaker handoffs — never mid-line
- Each clip ≤30s, under 10MB after compression
- Overlap by 2–3 seconds between clips (preserves voice identity across boundaries)
- Record the absolute offset of each clip for assembly (e.g., seg1=0s, seg2=20s, seg3=36s, seg4=47.5s)
- Timestamps within each segment's prompt are relative to that segment's start, not the original timeline

**Compression recipe (if a segment is over 10MB):**

For segments under ~60s (stereo, higher quality):
```bash
ffmpeg -i source.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 source_ref.mp3
```
- 320kbps stereo MP3 at 44.1kHz — ~2.6MB for 60s of audio
- Preserves full frequency range and stereo imaging for voice cloning

For longer segments (>60s, or still over 10MB at 320k):
```bash
ffmpeg -i source.wav -acodec libmp3lame -b:a 128k -ac 1 -ar 22050 source_ref.mp3
```
- 128kbps mono MP3 at 22.05kHz — ~1.0MB for 60s of audio
- Quality loss is negligible for cloning purposes; timbre and cadence are preserved

**Upload via MCP:**
Use `media_upload` with `media_type: "audio"` and the compressed file.
Save the returned `object_key` and URL — the URL expires in 2 hours, so generate immediately after upload.

### Stage 5: Generation

Call `seed_audio_generate` with the prompt and reference.

**Request structure:**
```
text_prompt: the composed prompt string
audio_references: [{kind: "url", url: "...", mime_type: "audio/mpeg"}]
output: {format: "wav", sample_rate: 44100}
persist: true
```

**Generation tips:**
- Use WAV 44.1kHz output for highest quality (video-ready)
- Set `persist: true` to get a durable artifact ID
- Save the `request_id` and `artifact.id` for retrieval

**Expected output:**
- Duration should be close to the source audio duration (±5% is normal)
- If output is significantly shorter than expected, the model may have skipped lines — check the prompt for any truncated content or ambiguous instructions
- If output is significantly longer, check for runaway speech or added content

### Stage 6: Assembly

Download the generated audio and adjust timing to match the original exactly.

**Downloading generated audio:**
The generation response contains a durable artifact (e.g. `seed-media://artifacts/<id>`) and an expiring `source_url` (provider CDN, ~2h). Prefer downloading the `source_url` directly — it avoids base64 round-trips:

```bash
curl -L -o seg1.wav "<source_url>"
```

Fallback: if only the artifact ID is available, fetch it via `seed_media_get_artifact` (`artifact_id`), which returns base64 data. Note the payload can exceed MCP output limits (~5MB truncates in chat), so decode it with a script rather than pasting it directly:

```bash
# Extract base64 payload from the tool result and decode to WAV
python3 - <<'EOF'
import json, base64
data = open("artifact_result.txt").read()
obj = json.loads(data[data.find("{"):])
def find_b64(o):
    if isinstance(o, dict):
        for v in o.values():
            if isinstance(v, str) and len(v) > 10000:
                return v
            r = find_b64(v)
            if r: return r
    elif isinstance(o, list):
        for it in o:
            r = find_b64(it)
            if r: return r
    return None
open("seg1.wav","wb").write(base64.b64decode(find_b64(obj)))
EOF
```

**Single-segment assembly:**
1. Download generated audio from the artifact URL
2. Compare duration with source (use `ffprobe`)
3. If shorter, append silence to match source duration exactly (this ensures frame-perfect video sync)
4. If longer (rare), trim or investigate — a longer output usually means the model added filler

**Duration matching recipe:**
```bash
# Append silence to match target duration
ffmpeg -i generated.wav -af "apad=pad_dur=X" -ac 2 final.wav
# where X = target_duration - generated_duration
```

**Multi-segment assembly (offset-mix):**

When using reference segmentation, each segment is generated independently with its own timestamps relative to the segment start. To reassemble, place each segment at its **absolute time offset** in the original timeline and mix together. This preserves the original gaps, room tone, and inter-segment timing — unlike concat, which assumes segments are contiguous.

```bash
# Place 4 segments at their absolute offsets and mix
# seg1 at 0ms, seg2 at 20000ms, seg3 at 36000ms, seg4 at 47500ms
ffmpeg -y \
  -i seg1.wav \
  -i seg2.wav \
  -i seg3.wav \
  -i seg4.wav \
  -filter_complex "[0:a]adelay=0|0[a1]; \
                   [1:a]adelay=20000|20000[a2]; \
                   [2:a]adelay=36000|36000[a3]; \
                   [3:a]adelay=47500|47500[a4]; \
                   [a1][a2][a3][a4]amix=inputs=4:duration=longest:dropout_transition=0:normalize=0,apad=pad_dur=X[out]" \
  -map "[out]" -ac 2 -ar 44100 -t <SOURCE_DURATION> final.wav
```

**Critical amix parameters:**
- `normalize=0` — prevents amix from attenuating volume when inputs overlap (overlap regions from the 2–3s reference splits would otherwise be quieter)
- `dropout_transition=0` — prevents volume ramping when an input ends
- `duration=longest` — extends to the longest input including delays
- `apad=whole_dur=X` — pad the final output to match the exact source duration (the bundled `mix_segments.sh` does this automatically now; it also trims to `-t` if a segment ever runs long)

**Why not concat:**
`ffmpeg concat` assumes segments are contiguous end-to-end. When segments have 2–3s reference overlaps, the overlap regions would be duplicated or trimmed. `adelay` + `amix` places each segment at its exact absolute position, preserving original gaps and handling overlaps gracefully.

### Stage 7: Video overlay (optional)

If the source is video, overlay the dubbed audio track.

**Recipe:**
```bash
ffmpeg -i original_video.mp4 -i dubbed_audio.wav \
  -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 \
  -shortest \
  video_dubbed.mp4
```

- `-c:v copy` — copy video stream without re-encoding (fast, no quality loss)
- `-map 0:v:0 -map 1:a:0` — take video from input 0, audio from input 1
- `-shortest` — cut to the shorter of the two streams

## Long-form dubbing (>120s)

When the source exceeds Seed Audio's 120s generation limit, split into generation segments. This is separate from reference segmentation (>30s) — a long-form source needs both: reference clips ≤30s AND generation passes ≤120s.

**Segmentation strategy:**
1. Split at natural scene boundaries, not at arbitrary time points
2. Each segment should contain complete lines of dialogue
3. Each reference clip must be ≤30s (apply reference segmentation rules within each generation segment)
4. Overlap reference audio by 2–3 seconds between segments (to preserve voice identity continuity)
5. Generate each segment with timestamps relative to the segment start (not the original absolute time)
6. Reassemble using offset-mix (see Stage 6), not concat

**Segment planning template:**
```
Generation segment 1: lines 1-10 (0.0s - 45.0s) → ref clips: 0-22s, 20-45s
Generation segment 2: lines 11-20 (45.0s - 90.0s) → ref clips: 45-67s, 65-90s
Generation segment 3: lines 21-28 (90.0s - 115.0s) → ref clips: 90-115s
```

**Important:** Each generation segment gets its own prompt. The reference audio for each segment is a ≤30s clip from the corresponding portion of the source. Timestamps within each segment's prompt are relative to that segment's start, not the original timeline. Reassemble all outputs at their absolute offsets using `adelay` + `amix`.

## Multi-speaker dubbing

When the source has multiple speakers, follow these rules:

1. **One reference clip is sufficient** — Seed Audio can extract multiple voice identities from a single clip
2. **Identify every speaker before writing** — map all lines to speakers
3. **Use consistent speaker labels** — Speaker A, B, C throughout the prompt
4. **Each line must have a clear speaker attribution** — never have an unattributed line
5. **Describe each speaker's role** — "male lawyer," "female lead," "elderly grandmother" — so the model knows which voice to clone for which line
6. **Emotional arc per speaker** — note if a speaker's tone changes across the scene (e.g., "calm at first, then angry")

**Common pitfall:** Mixing up who speaks a line. If Speaker A's line is spoken in Speaker B's voice, the dub is ruined. Double-check speaker assignments before generating.

## Prompt-too-long strategies

The 3,000 character limit is the most common constraint you'll hit. Try these fixes in order:

1. **Trim the pronunciation guide** — keep only 10–15 most critical words; remove all explanatory text
2. **Shorten character descriptions** — "male lawyer, calm" instead of "mature adult male, calm, firm, professional delivery"
3. **Remove stage directions** — keep only the speaker label and the dialogue line
4. **Shrink the reference intro** — one sentence instead of two
5. **Abbreviate the ending instruction** — "Ending: match @Audio1"
6. **Split into segments** — if still over 3,000, split the script in half and do two passes

## Language-specific guidance

For languages with special phonetic considerations, include targeted guidance:

**Tagalog/Filipino:**
- Penultimate stress default (note key words with non-default stress)
- Flat intonation, not English-style rising-falling
- Glottal stops are phonemic (mark with trailing apostrophe: `gala'`)
- "Ng" at word start is a single velar nasal [ŋ]
- See `seedance-prompt-25-filipino` skill for full Filipino phonetic guide

**Chinese:**
- Tones are critical — mark tone numbers on key words (e.g., `ni3 hao3`)
- Pinyin romanization in pronunciation guides

**Japanese:**
- Pitch accent patterns on key words
- Long vowel markers (e.g., `obāsan` vs `obasan`)

**For unsupported languages:** Check the Seed Audio API reference for current supported languages. If the target language isn't supported, tell the user and suggest alternatives (e.g., English narration with the original voice, or a different service).

## Output files and naming

Save outputs alongside source assets in the project directory:

```
projects/<project>/
  original/                              # source assets and outputs
    original-en-audio.wav               # source audio (uncompressed)
    original-en-audio.mp3               # reference audio (compressed for upload)
    original-en-video.mp4               # source video
    original-<lang>-script.srt          # target script
    dub_<lang>_v01.wav                   # dubbed audio
    video_<lang>_v01.mp4                 # dubbed video
    prompt_dub_<lang>_v01.md            # prompt snapshot
```

- `<lang>` = full language name (e.g., `tagalog`, `spanish`, `japanese`, `chinese`)
- For single-pass dubs, use `dub_<lang>_v01.wav`. For multi-segment dubs, use `dub_<lang>_full_v01.wav` to distinguish from split approaches
- Version increment for regenerations: `v02`, `v03`, etc.
- Prompt snapshots live beside the output they produced

## Quality checklist

Before delivering a dub, verify:

- [ ] Generated audio exists and is playable
- [ ] Duration matches source (±0.1s after padding)
- [ ] All dialogue lines are present (count them)
- [ ] Correct speaker voices for each line (listen and spot-check)
- [ ] Target language pronunciation is intelligible (listen to key words)
- [ ] Pacing matches original (no rushed or stretched lines)
- [ ] No background artifacts, clicks, or glitches
- [ ] If video overlay: video plays, audio syncs with lip movement (visually spot-check at 2-3 points)
- [ ] File saved in correct project directory
- [ ] Prompt snapshot saved beside the output

## Full example: Tagalog dub of a 68s drama scene

**Inputs:**
- Source: `original-en-audio.wav` (68.07s, 11.4MB) + `original-en-video.mp4`
- Script: 22 lines in Tagalog (SRT format)
- Target language: Manila Tagalog

**Stage 1 — Preflight:**
- Source is 68.07s (under 120s generation limit) ✓
- Source is 68.07s (over 30s reference clip limit) → needs reference segmentation into 4 clips ✓
- Source audio is 11.4MB (over 10MB) → compress each segment to MP3 320kbps ✓
- 22 lines of Tagalog dialogue ✓
- Tagalog is in the supported languages list ✓

**Stage 2 — Character identification:**
Analysis of the script (contract marriage drama scene). Verified using Seed 2.1 (`seed_understand` with `thinking: true`) to confirm speaker assignments:
- Speaker A: Male lawyer (10 lines) — formal "Mr. Dawson" references, professional tone
- Speaker B: Lucy / Ms. Ford (3 lines) — "your client," "I'll wait for him"
- Speaker C: Older woman / Grandma (9 lines) — "Vincent" (first name), "apo ko" (my grandson)

Key insight: Lines 5-6 ("Mamuhay ka bilang asawa ni Vincent sa papel") were initially misassigned to the male lawyer, but context analysis confirmed they belong to the grandma (she argues for keeping the marriage on paper, then the lawyer pushes back in lines 7-8 urging annulment). Always verify speaker assignments when characters debate opposing positions.

**Stage 3 — Prompt authoring:**
4 prompts written, one per reference segment. Each uses relative timestamps (starting from 0 within that segment). Pronunciation guide includes "wakasan" = wa-ka-SAN (stress on final syllable). See prompt files: `prompt_dub_tagalog_v03_seg{1-4}.md`.

**Stage 4 — Reference segmentation:**
Split the 68s source into 4 clips at natural boundaries (dialogue gaps, speaker handoffs), with 2s overlaps:
```bash
ffmpeg -ss 0 -t 22 -i original-en-audio.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg1_ref.mp3
ffmpeg -ss 20 -t 18 -i original-en-audio.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg2_ref.mp3
ffmpeg -ss 36 -t 13.5 -i original-en-audio.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg3_ref.mp3
ffmpeg -ss 47.5 -t 20.5 -i original-en-audio.wav -acodec libmp3lame -b:a 320k -ac 2 -ar 44100 seg4_ref.mp3
```
Offsets: seg1=0s, seg2=20s, seg3=36s, seg4=47.5s. All clips ≤30s, all under 10MB.

**Stage 5 — Generation:**
4 `seed_audio_generate` calls, one per segment with its own reference clip. Each prompt has relative timestamps matching the segment's portion of the SRT. Output: seg1=20.83s, seg2=15.82s, seg3=12.60s, seg4=10.80s.

**Stage 6 — Assembly (offset-mix):**
```bash
# Place each segment at its absolute offset and mix
ffmpeg -y \
  -i seg1.wav -i seg2.wav -i seg3.wav -i seg4.wav \
  -filter_complex "[0:a]adelay=0|0[a1]; \
                   [1:a]adelay=20000|20000[a2]; \
                   [2:a]adelay=36000|36000[a3]; \
                   [3:a]adelay=47500|47500[a4]; \
                   [a1][a2][a3][a4]amix=inputs=4:duration=longest:dropout_transition=0:normalize=0,apad=pad_dur=9.77[out]" \
  -map "[out]" -ac 2 -ar 44100 -t 68.074671 dub_tagalog_v03.wav
# Result: 68.07s, matches source exactly, preserves all gaps and room tone
```

**Stage 7 — Video overlay:**
```bash
ffmpeg -i original-en-video.mp4 -i dub_tagalog_v03.wav \
  -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 -shortest \
  video_tagalog_v03.mp4
# Result: 68.07s, original video with Tagalog audio
```

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Generated audio is much shorter than expected | Model skipped lines or prompt was truncated | Check prompt character count; split into shorter segments |
| Voice cloning doesn't match | Reference quality too low | Use higher bitrate reference (128kbps+); ensure reference contains clear speech from the target speaker |
| Wrong speaker voice for a line | Speaker misidentification | Re-analyze the script; regenerate with corrected speaker assignments |
| Pronunciation is off | Missing language-specific guidance | Add targeted pronunciation guide with key words and stress patterns |
| Pacing is too fast / too slow | Timestamps misaligned | Adjust `[start:end]` timestamps; use `speech_rate` in `audio_config` |
| Audio has clicks or artifacts | Generation glitch | Regenerate; if persistent, simplify the prompt |
| Video sync is off | Duration mismatch | Always pad/trim generated audio to match source exactly before muxing |
| Reference upload fails (too big) | Over 10MB limit | Compress to MP3 (see Stage 4 recipe); use 320k stereo for <60s, 128k mono for >60s |
| Timing drift across long scenes | Reference clip >30s | Split into ≤30s reference segments at natural boundaries; use offset-mix assembly (Stage 6) |
| Gaps between lines compressed | Model struggles with 2s+ silence | Split into separate segments at the gap boundary; let assembly insert the silence |
| Multi-segment output has timing seams | Used concat instead of offset-mix | Use `adelay` + `amix normalize=0` to place segments at absolute offsets (Stage 6) |

## Bundled scripts

### scripts/mix_segments.sh

Mixes multiple generated segments at their absolute time offsets using `adelay` + `amix normalize=0`. Use after multi-segment generation (reference or generation segmentation) to reassemble the full track with correct timing and gaps preserved. Pads the output to the exact source duration automatically (no manual `apad` needed).

Usage:
```bash
scripts/mix_segments.sh <source_duration> <output_wav> <seg1.wav>:<offset_ms> [<seg2.wav>:<offset_ms> ...]
# Example:
scripts/mix_segments.sh 68.074671 final.wav seg1.wav:0 seg2.wav:20000 seg3.wav:36000 seg4.wav:47500
```

Steps performed:
1. Parse each `file:offset` pair
2. Build an ffmpeg filter_complex chain placing each segment at its absolute offset
3. Mix with `normalize=0` (no volume attenuation on overlaps) and `dropout_transition=0`
4. Pad to exact source duration
5. Print summary with per-segment offsets

### scripts/verify_and_mux.sh

Combines duration verification and video muxing into one command. Use after assembly (single-segment pad or multi-segment mix) to overlay the final audio onto the source video.

Usage:
```bash
scripts/verify_and_mux.sh <source_audio> <generated_audio> <source_video> <output_video>
```

Steps performed:
1. Check both durations with ffprobe
2. Calculate needed padding
3. Pad generated audio to match source duration
4. Mux padded audio with source video (video stream copy, audio AAC 192k)
5. Verify output duration
6. Print summary

## Related skills

- `seed-audio-prompt` — general Seed Audio prompt composition (T2A and TA2A)
- `seed-audio-commercial` — full-soundscape audio commercial generation
- `seedance-prompt-25-filipino` — Filipino/Tagalog phonetic guidance for video
- `ffmpeg` — all audio/video processing operations
- `film-production` — full film production orchestration
