---
project: jollibee-chickenjoy-commercial
type: commercial-spot
title: "Jollibee Chickenjoy — Home Is Just One Bite Away"
status: draft
brand: Jollibee
product: Chickenjoy
language: Taglish (Tagalog-English mix)
duration_target_seconds: 110
created: 2026-07-28
---

# jollibee-chickenjoy-commercial

A dramatic, story-involved audio commercial for **Jollibee Chickenjoy**. A
homesick Filipino worker abroad calls home on a rainy night; his mother tells
him to get Chickenjoy. One bite transports him back to family joy, resolving
with the brand tagline: "Because no matter how far you go — home is just one
bite away."

## Brief

- **Brand**: Jollibee
- **Product**: Chickenjoy (crispy fried chicken)
- **Tone**: dramatic, emotional, nostalgic, heartwarming
- **Format**: ~110-second single-mix audio spot (dialogue + BGM + SFX + ambience)
- **Language**: Taglish (Tagalog-English mix), natural Filipino speech patterns
- **Story arc**: loneliness → phone call home → journey to store → first bite → joyful memory flashback → emotional resolution → brand tagline

- Marco speaks in Taglish throughout, mixing Tagalog and English naturally.

## Cast

- **Marco** — late 20s male, Filipino English accent, warm but tired voice.
  Homesick OFW (Overseas Filipino Worker) in Singapore. Speaks Taglish.
- **Nanay** — late 50s female, warm gentle Filipino accent, nurturing and
  motherly. Marco's mother, heard through a phone call. Speaks Tagalog-heavy
  Taglish.
- **Crew member** — young adult female, cheerful, bright and energetic. Jollibee
  store crew.
- **Announcer** — deep, warm, confident male. Professional broadcaster tone for
  the brand tagline.

## Locations

- **singapore-apartment-night** — cold rainy night, small apartment, lonely
  room tone, rain on window, distant traffic.
- **jollibee-store** — warm, busy store ambience, chatter, welcoming hum.
- **family-memory** — joyful Filipino family dinner table (flashback soundscape).

## Production notes

- Audio generated via BytePlus Seed Audio 1.0 (`seed-audio-1.0`) in T2A
  (text-only) mode — no voice cloning references.
- Full soundscape (dialogue + music + SFX + ambience) generated in a single
  pass.
- See [scenes/scene-01/scene.md](scenes/scene-01/scene.md) for the full
  prompt, model, params, artifact reference, and cost.

## Model & credit defaults

| Setting | Value |
|---|---|
| Model | `seed-audio-1.0` |
| Mode | T2A (text-only) |
| Actual duration | 110.640s (t03, preferred) |
| Pricing | $0.15/min ($0.0025/s) |
| Est. cost (t03) | ~$0.28 (110.6s × $0.0025/s) |
| Total cost (3 takes) | ~$0.79 |
| Output format | mp3, 24kHz stereo, 64 kbps |

## Status

- [x] Prompt authored (`seed-audio-prompt` skill, T2A structure)
- [x] Audio generated t01 v01 — 101s, English-only version (content filter
  forced Taglish removal)
- [x] Audio generated t02 v01 — 103s, Taglish version (Tagalog + English mix)
- [x] Audio generated t03 v01 — 110.6s, Taglish fresh take (preferred)
- [ ] Voice cloning / TA2A pass for consistent character voices
- [ ] Video / storyboard (Seedream keyframes + Seedance shot)
- [ ] Final mix/master
