---
description: Write a Seedance 2.5 video ad prompt for any of 9 UGC ad modes (UGC, UGC How-To, Unboxing, Product Showcase, Product Review, TV Spot, Try-On, Wild Card).
agent: build
---

Load the `ugc-ad-modes` skill (`.agents/skills/ugc-ad-modes/SKILL.md`) and use it
to write a production-grade Seedance 2.5 video ad prompt for the requested mode.

$ARGUMENTS

Follow the skill's full workflow:
1. Resolve the requested mode from the user's language (default: `ugc`)
2. Load the matching recipe from `references/mode-recipes.md`
3. Write the prompt using the skill's full ad prompt output format
4. Generate 3-5 hook variants for the opening 0-3s
5. Include mode-appropriate visual texture, camera style, lighting, narrative
   beats, creator performance, product interaction, audio direction, and CTA
6. End with a compact mode seal

If the user does not specify a mode, infer it from the product and brief:
- "casual phone-shot creator" → `ugc`
- "open the box, reveal" → `ugc-unboxing`
- "show how to use, tutorial" → `ugc-how-to`
- "product hero, no presenter" → `product-showcase`
- "honest opinion, review" → `product-review`
- "broadcast commercial" → `tv-spot`
- "try on clothes, casual" → `ugc-virtual-try-on`
- "try on clothes, editorial" → `virtual-try-on`
- "surprise me, experimental" → `wild-card`

If the user requests lip-synced dialogue audio, note the audio-first pipeline
(generate Seed Audio first, then pass as `reference_audio` to Seedance) and
recommend loading the `seed-audio-prompt` skill.

Return the prompt directly. Do not submit any generation tasks or call the API.
