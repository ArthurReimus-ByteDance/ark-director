# Prompt Templates

Use these structures as authoring examples, then measure the final prompt against the live character limit. Preserve approved voice descriptors verbatim in every segment. Template windows are illustrative; replace them with the actual manifest-relative dialogue timing before review and submission.

---

## Template 1: Single-speaker reference segment (up to 30s)

```
@Audio1: [source description — e.g. "Original English narration audio"].
Clone the voice timbre, cadence, emotion, pacing, and pauses exactly.
Only change the language from [source_lang] to [target_lang].
Preserve room tone and acoustic character.

Speaker — [role, age/gender, voice quality] — voice in @Audio1.
Match every pause and rhythm of @Audio1 exactly. Pure dialogue with the source room tone.

[0.5s:2.5s] "[line 1]"
[2.6s:5.2s] "[line 2]"
[5.3s:8.0s] "[line 3]"
[8.1s:11.0s] "[line 4]"
[11.1s:14.0s] "[line 5]"
[14.1s:17.0s] "[line 6]"
[17.1s:20.0s] "[line 7]"
[20.1s:23.0s] "[line 8]"
[23.1s:26.0s] "[line 9]"

Pronunciation: [target_lang] [key pronunciation rules, 3-5 bullet max].

Ending: Clean ending matching @Audio1, same tail silence.
```

Estimated size: ~1,000–1,500 chars for 8-10 lines.

---

## Template 2: Multi-speaker reference segment (up to 30s)

```
@Audio1: [source description]. Clone all voice timbres, cadence, emotion,
pacing, pauses, speaker order, and timing exactly. Same [N] characters in
same order. Only change dialogue from [source_lang] to [target_lang].
Preserve room tone and acoustics of @Audio1.

[N] speakers from @Audio1:
A — [role] (age/gender, quality) — first [male/female] voice
B — [role] (age/gender, quality) — [second voice description]
C — [role] (age/gender, quality) — [third voice description]

Match every pause and gap in @Audio1 exactly. Pure dialogue with the source room tone.

A says [delivery]: "[0.5s:2.5s] [line]"
A continues: "[2.6s:5.2s] [line]"

B replies [delivery]: "[5.3s:8.0s] [line]"

C speaks up [delivery]: "[8.1s:11.0s] [line]"
C continues: "[11.1s:14.0s] [line]"

A pushes back [delivery]: "[14.1s:17.0s] [line]"

B says [delivery]: "[17.1s:20.0s] [line]"
B continues: "[20.1s:23.0s] [line]"

[Room tone beat matching gap in @Audio1 between two segments.]

A advises [delivery]: "[23.1s:26.0s] [line]"
A finishes: "[26.1s:28.5s] [line]"

Pronunciation: [target_lang]. [key rules, 5-8 bullet max].
Key words: [5-8 most important words with stress marks].

Ending: Clean ending matching @Audio1 exactly, same tail silence.
```

Estimated size: ~1,800–2,800 chars for 15-20 lines across 3 speakers.

---

## Template 3: Long-form segment (>120s or >30s, split into parts)

Each segment gets its own prompt. Use relative timestamps starting from 0 (not the original absolute timestamps). Each reference clip must be ≤30s — split the source at natural boundaries with 2–3s overlaps. Use `@Audio1` for the segment's reference clip.

```
@Audio1: [source description]. Clone all voices, cadence, emotion, pacing,
pauses, and speaker order. Use the approved speaker identities listed below. Only change
dialogue from [source_lang] to [target_lang]. Preserve room tone of @Audio1.

This is segment [M] of [TOTAL] (lines [START]-[END]).
List every relevant speaker with their exact approved voice descriptor in every segment. The model has no memory of another request.

Speaker A — [role] — voice from @Audio1
Speaker B — [role] — voice from @Audio1
Speaker C — [role] — voice from @Audio1

Match pauses and rhythm exactly. Pure dialogue with the source room tone.

[Opening: ~Xs of room tone matching gap before segment M in original.]

A says [delivery]: "[0.0s:Y1] [line]"
B replies [delivery]: "[Y2:Y3] [line]"
...

Pronunciation: [target_lang]. [key rules].
Key words: [critical words].

Ending: Clean ending matching the end of segment M in @Audio1.
```

Estimated size: ~1,500–2,500 chars per segment.

After generating all segments, reassemble using offset-mix (not concat):
```bash
# Place each segment at its absolute offset and mix
scripts/mix_segments.sh 68.074671 output.wav \
  'seg1.wav:0' 'seg2.wav:20000' 'seg3.wav:36000' 'seg4.wav:47500'
```
This preserves original gaps and room tone. See [generation and assembly](generation-assembly.md) for technical checks and recovery.

---

## Template 4: Reference-segmented dub (source >30s, ≤120s)

When the source exceeds the 30s reference clip limit but fits within the 120s generation limit, split into reference segments. Each segment gets its own ≤30s reference clip and its own prompt with relative timestamps. Reassemble with offset-mix.

```
@Audio1: [source description — segment N of M]. Clone all voice timbres,
cadence, emotion, pacing, pauses, and speaker order. Same [N] characters.
Only change dialogue from [source_lang] to [target_lang]. Preserve room
tone of @Audio1.

[Full relevant speaker list and exact approved voice descriptors in every segment]

Match every pause and gap in @Audio1 exactly. Pure dialogue with the source room tone.

[Room tone — match gap in @Audio1 from 0s to Xs before first line.]

A says [delivery]: "[Xs:Ys] [line]"
B replies [delivery]: "[Ys:Zs] [line]"
...

Pronunciation: [target_lang]. [key rules].
Key words: [critical words].

Ending: Clean ending matching @Audio1 exactly, same tail silence.
```

**Splitting rules:**
- Split at natural boundaries: dialogue pauses (2s+), speaker handoffs, scene transitions
- Each actual encoded clip ≤30s and ≤10,000,000 bytes, including overlap and codec padding
- Overlap by 2–3 seconds between clips for voice identity continuity
- Record absolute offset of each clip (e.g., seg1=0ms, seg2=20000ms, seg3=36000ms)
- Timestamps within each prompt are relative to that segment's start

**Reassembly:**
```bash
scripts/mix_segments.sh 68.074671 output.wav \
  'seg1.wav:0' 'seg2.wav:20000' 'seg3.wav:36000' 'seg4.wav:47500'
```

---

## Prompt size budget

Keep these approximate limits in mind:

| Component | Char budget |
|---|---|
| Reference intro + speaker list | 300–500 |
| Per line of dialogue | ~50–100 (speaker label + line + timestamps) |
| Pronunciation guide | 200–400 |
| Ending + misc | 50–100 |
| **Total budget** | **3,000** |

Rule of thumb: ~20 lines of dialogue = ~2,500 chars including setup.
If you have more than ~25 lines, you probably need to split into segments.
