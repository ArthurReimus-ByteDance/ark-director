---
project: ube-commercial
type: commercial-spot
title: "Lola Maria's Ube Halaya — Merienda"
status: draft
brand: Lola Maria's
product: Ube Halaya
language: Taglish (Tagalog-English mix)
duration_target_seconds: 30
created: 2026-07-24
---

# ube-commercial

A 30-second Filipino food commercial spot for **Lola Maria's Ube Halaya**.
Single-scene, single-mix audio spot produced with BytePlus Seed Audio 1.0.

## Brief

A warm, nostalgic merienda-time scene in a Filipino home kitchen. Lola Maria
cooks ube halaya for her granddaughter Bianca. The spot ends with a brand
voiceover tagline.

- **Brand**: Lola Maria's
- **Product**: Ube Halaya
- **Tone**: warm, nostalgic, family, natural/artisanal
- **Format**: 30-second single-mix audio spot (dialogue + BGM + SFX + ambience)
- **Language**: Taglish

## Cast

- **Bianca** — 7-year-old girl, bright/curious voice, Filipino child accent.
- **Lola Maria** — 65-year-old grandmother, warm/soft voice, provincial lola
  accent.
- **Announcer / Voiceover** — middle-aged woman, warm/professional, Filipino
  commercial announcer accent.

## Locations

- **filipino-home-kitchen** — afternoon merienda time, electric fan hum, kawa
  on the kalan, distant street sounds.

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
| Default duration | 30s |
| Pricing | $0.15/min ($0.0025/s) |
| Output format | wav (provider default) |

## Status

- [x] Prompt authored (`seed-audio-prompt` skill, T2A structure)
- [x] Audio generated (t01 v01)
- [ ] Voice cloning / TA2A pass for consistent Bianca & Lola Maria voices
- [ ] Video / storyboard (Seedream keyframes + Seedance shot)
- [ ] Final mix/master

## Seedream product-insert storyboard

On 2026-07-28, three brand-neutral product-insert panels were generated for the
existing merienda commercial:

1. real ube ingredient origin;
2. handmade halaya transformation;
3. finished product hero serving.

The panels are saved under
`assets/image/storyboard/scene-01/` and remain in `review`. They complement the
approved Lola Maria and Bianca narrative but do not replace its character or
location references.
