# Quick Reference

Focused reference for `seedream-prompt`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [Quick reference card](#quick-reference-card)

## Quick reference card

### Model IDs
| Model | Model ID |
|---|---|
| Seedream 5.0 Pro | `dola-seedream-5-0-pro-260628` |
| Seedream 5.0 Lite | `seedream-5-0-260128` (alias: `seedream-5-0-lite-260128`; override via `SEEDREAM_MODEL_BINDINGS`) |

### Pricing (Seedream 5.0 Pro)
| Tier | Price |
|---|---|
| Output ≤ ~2.36M pixels (1K tier) | $0.045 / image |
| Output > ~2.36M pixels (2K tier) | $0.09 / image |
| First reference image | Free |
| Each additional reference image | $0.003 |

The 2.36M-pixel threshold is the practical 1K/2K billing boundary. Only the $0.045 base is shown on the public pricing page.

### Resolution and size (Seedream 5.0 Pro)
The `size` parameter accepts either a resolution tier (`1K` / `2K`, set via natural-language aspect-ratio/shape description; default `2K`) or explicit `widthxheight`.
- Pixel range: [921600, 4624220] (~0.92M–4.6M)
- Aspect-ratio range: [1/16, 16]
- 1K examples: 1024×1024, 1424×800 (16:9)
- 2K examples: 2048×2048, 2816×1584 (16:9, 2K tier)

Input per image: ≤ 36,000,000 pixels, ≤ 30 MB (per API reference).

### Prompt optimization mode (Pro)
`optimize_prompt_options.mode`:
- `standard` (default) — higher quality, slower.
- `fast` — lower latency, slightly lower quality. Recommended when latency-sensitive.

### Output parameters
- `response_format`, `output_format`: png / jpeg (default jpeg).
- `watermark`: bool.
- Layer separation: PNG with alpha (transparency) channel, 2-20 images.

### Supported prompt languages (Seedream 5.0 Pro)
Native support for 14 languages: Arabic, Filipino, French, German, Indonesian, Japanese, Korean, Malay, Portuguese, Russian, Spanish, Thai, Turkish, Vietnamese. English is the base language. Other languages also work but with weaker in-image text rendering and cultural understanding.

### Throughput and streaming
- Rate limit: 500 images/minute.
- Streaming output: not supported on Pro (supported on Lite/4.5/4.0).
- Sequential/batch output: not supported on Pro (supported on Lite/4.5/4.0).

### Regions
Supported in `ap-southeast-1` and `eu-west-1`.

### Trust ecosystem with Seedance
- Images from Seedream 5.0 Pro and Lite are trusted inputs across all Seedance models (2.5 `dreamina-seedance-2-5-260628`, 2.0 `dreamina-seedance-2-0-260128`, Fast/Mini via `SEEDANCE_MODEL_BINDINGS`).
- Text-to-Image outputs are trusted automatically for all customers.
- Image-to-Image outputs become trusted after the account passes KYC verification.
- Trust exempts input moderation only, not output moderation.
