# Seed 2.1 Multimodal Understanding

Requires `BYTEPLUS_MODELARK_API_KEY`. Auth scope: `understanding:read`.

The default model is `dola-seed-2-1-turbo-260628` (Seed 2.1 Turbo).
`dola-seed-evolving` (the latest Seed-series Pro-tier model) is also a
recognized built-in ID — set `SEED_UNDERSTANDING_DEFAULT_MODEL=dola-seed-evolving`
to opt in; its family auto-resolves to `pro` so no explicit
`SEED_UNDERSTANDING_MODEL_FAMILY` is required. Other custom model IDs can be
registered via `SEED_UNDERSTANDING_MODEL_BINDINGS`.

#### `seed_understand`

Understand images and videos, or reason about a task, through the Seed 2.1
multimodal model via ModelArk Chat Completions. Supports deep-thinking
(chain-of-thought) reasoning when `thinking=true`. Use this for:

- **Video understanding** — describe, summarize, or answer questions about video content
- **Image understanding / OCR** — extract text, describe scenes, analyze visual content
- **Multimodal reasoning** — combine text + images + videos for complex analysis
- **As a reasoning sub-agent** — delegate analysis tasks that need visual context

Video inputs must be HTTPS URLs (Base64 not supported by the chat endpoint).
Upload local videos via `media_upload` first.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | `str` | Yes | 1–32,000 characters. The question or task for the model. |
| `images` | `list[UnderstandingImageInput]` | No | Up to 32 images (URL or Base64) |
| `videos` | `list[UnderstandingVideoInput]` | No | Up to 32 videos (URL only, no Base64) |
| `system` | `str` | No | Optional system instruction (max 32,000 chars) |
| `model` | `str` | No | Override the configured Seed 2.1 model ID |
| `thinking` | `bool` | No (default `false`) | Enable deep-thinking chain-of-thought reasoning |
| `reasoning_effort` | `"low"` \| `"medium"` \| `"high"` | No | Only when `thinking=true` |
| `temperature` | `float` | No | 0.0–2.0. Lower = more deterministic |
| `max_tokens` | `int` | No | 1–32768 |
| `top_p` | `float` | No | 0.0–1.0 nucleus sampling |
| `repetition_penalty` | `float` | No | 0.0–2.0 (Ark-only parameter) |

Returns `SeedUnderstandOutput` with `model`, `completion_id`, `choices`
(each with `content` and optional `reasoning_content`), `usage`
(prompt_tokens, completion_tokens, total_tokens), and `request_id`.

**Example — image OCR / understanding:**

```json
{
  "prompt": "Extract all text visible in this image and describe the scene.",
  "images": [
    { "kind": "url", "url": "https://cdn.example.com/document.png" }
  ]
}
```

**Example — video understanding with deep thinking:**

```json
{
  "prompt": "Analyze this product demo video. What are the key features shown? Are there any UI issues or bugs visible? Rate the overall production quality.",
  "videos": [
    { "kind": "url", "url": "https://cdn.example.com/demo.mp4" }
  ],
  "thinking": true,
  "reasoning_effort": "high",
  "max_tokens": 4096
}
```

**Example — multimodal reasoning as a sub-agent:**

```json
{
  "prompt": "Compare the UI in screenshot 1 with the design spec in screenshot 2. List all differences in spacing, color, and typography.",
  "images": [
    { "kind": "url", "url": "https://cdn.example.com/screenshot.png" },
    { "kind": "url", "url": "https://cdn.example.com/design-spec.png" }
  ],
  "system": "You are a meticulous UI/UX reviewer. Be specific about pixel-level differences."
}
```

**Deep-thinking mode:** When `thinking=true`, the model produces
chain-of-thought reasoning visible in `choices[].reasoning_content`. Use
`reasoning_effort` to control depth:

| Level | When to Use | Latency |
|---|---|---|
| `low` | Quick checks, simple OCR, basic descriptions | Fastest |
| `medium` | Balanced analysis, moderate comparisons | Moderate |
| `high` | Deep analysis, complex reasoning, detailed reviews | Slowest |

Keep `thinking=false` for simple extraction, description, or lookup tasks
where speed matters more than reasoning depth.

**Prompt engineering tips:**

- **Specify output format** — ask for JSON, markdown tables, or numbered lists
  to get structured results
- **Use system instructions** for role and constraints (e.g., "You are a
  senior data analyst. Be thorough and systematic.")
- **Break complex tasks into steps** — make focused calls (extract, then
  analyze, then summarize) instead of one massive prompt
- **Ask for timestamps** when referencing specific video moments
- **For multi-language OCR**, mention expected languages in the prompt

**Limitations:**

- Video Base64 is not supported — upload via `media_upload` first
- 32 media parts max (images + videos combined)
- Synchronous call — blocks until the model responds (long videos with
  deep-thinking can take 30+ seconds)
- No streaming — the full response is returned at once
- No artifact persistence — understanding returns text, not media

---
