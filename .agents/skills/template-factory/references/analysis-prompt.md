# Analysis Prompt — `seed_understand` breakdown

The canonical prompt for the first `seed_understand` pass. It turns "understand
the video" into a reproducible, slot-complete `VideoBreakdown`.

```text
You are a film-analysis expert. Analyze the attached video and produce a JSON
object that fully describes how to REPRODUCE its style, composition, and grammar.

RULES
- Output valid JSON only. No prose outside the JSON.
- De-identify: describe a person's appearance (age, build, hair, clothing) but
  NEVER name them, infer a real identity, or reproduce text/logos that identify
  real brands or people. Replace brand text with a placeholder description.
- Say what you want positively; describe what IS shown, not what to avoid.
- Break the video into consecutive shots at every cut. Each shot needs:
  index, start_s, end_s, duration_s, composition, camera, action, lighting,
  audio, and end_state (observable state at the shot's end).
- Identify every distinct character, location, and prop that appears. Assign each
  a short kebab-case id and an exhaustive visual descriptor (the exact phrasing
  a generator can use word-for-word). Mark the shot index of the clearest
  keyframe for each element.
- Extract visual_style (grade, lighting_direction, lens, film_look), camera
  (shot_sizes, moves, framing, transitions), and audio (mode, music, sfx,
  dialogue — transcribe any dialogue verbatim inside {braces}).

Return this schema:
{
  "schema_version": "1.0",
  "title": string,
  "genre": string,
  "visual_style": {...},
  "camera": {...},
  "audio": {...},
  "elements": [{ "type": "character|location|prop|screen", "id", "tag",
                 "descriptor", "keyframe_index": [int], "in_shots": [int] }],
  "shots": [{ "index", "start_s", "end_s", "duration_s", "composition",
              "camera", "action", "lighting", "audio", "end_state" }]
}
```

## Call parameters

```json
{
  "videos": [{ "kind": "url", "url": "<presigned pin url>" }],
  "prompt": "<analysis prompt above>",
  "temperature": 0.2,
  "thinking": false,
  "max_tokens": 8192
}
```

Notes:
- Video inputs must be HTTPS URLs (Base64 unsupported) — upload via
  `media_upload` first and pass the presigned URL.
- `thinking=false` for extraction speed; the JSON contract keeps it deterministic.
- Validate the response against `breakdown-schema.json`; on schema failure,
  retry once with an explicit "return JSON only, no markdown fences" correction.
  Never proceed with a malformed breakdown.
