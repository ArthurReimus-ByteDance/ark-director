---
name: ugc-ad-modes
description: >
  Write production-grade Seedance 2.5 video prompts for 9 ad modes: UGC,
  UGC How-To, UGC Unboxing, Product Showcase, Product Review, TV Spot,
  Wild Card, UGC Virtual Try-On, and Pro Virtual Try-On. Each mode
  encodes its own visual texture, narrative beat structure, hook formula,
  camera style, audio direction, and CTA pattern. Use whenever the user
  asks to create a UGC video ad, unboxing ad, product tutorial ad,
  product showcase, product review ad, TV commercial, virtual try-on,
  or any branded video ad. Partners with seedance-prompt-25 (six-part
  formula) and seed-audio-prompt (dialogue audio). Does not call the API
  itself.
---

# UGC Ad Modes

Write ready-to-use Seedance 2.5 prompts for distinct ad modes. Make the
chosen mode govern not only the visual texture but also the narrative
structure, hook formula, creator performance, camera discipline, audio
direction, and CTA pattern throughout the entire prompt.

## Source basis

The mode taxonomy is adapted from [Higgsfield's Marketing Studio](https://higgsfield.ai/skills/ugc)
mode system, accessed 2026-08-16. The recipes are rebuilt from
independent research into UGC, unboxing, tutorial, product showcase,
product review, TV spot, and virtual try-on best practices (100+ sources,
2025-2026). The creative principles are research-backed, not copied from
Higgsfield's implementation.

## Mode bank

Read `references/mode-recipes.md` after identifying the requested mode.
Use only the matching recipe or the custom-mode template.

- `ugc`
- `ugc-how-to`
- `ugc-unboxing`
- `product-showcase`
- `product-review`
- `tv-spot`
- `wild-card`
- `ugc-virtual-try-on`
- `virtual-try-on`

## Core principle

The mode governs the entire world. A UGC ad shot with TV-spot lighting
and polished transitions stops reading as UGC. A product showcase with a
talking head stops reading as a product showcase. The mode is the
physical law of the ad, just as the medium is the physical law of an
animation scene.

**Do not burn in captions, on-screen text overlays, or lower-thirds in
Seedance video prompts.** Seedance cannot reliably render readable text
in generated video. Platforms (TikTok, Reels, YouTube Shorts) generate
captions natively from the audio track. For broadcast/CTV delivery
(TV Spot mode), closed captions are added in post-production as
sidecar files (SRT/TTML/CEA-608/708), not embedded in the video by
Seedance.

For every prompt, define:

```text
mode                 the ad format that governs visual texture and structure
visual texture       what the footage looks like (phone-shot, studio, broadcast)
narrative beats      the timed structure (hook, problem, demo, payoff, CTA)
hook formula         the opening 0-3s pattern that stops the scroll
creator performance  how the presenter acts, speaks, and engages
camera style         angles, movement, framing discipline
audio direction      voice style, ambience, SFX, music approach
CTA pattern          how the ad closes (soft, hard, visual, spoken)
failure modes        what kills authenticity or conversion for this mode
```

## Prompting workflow

### 1. Resolve the requested mode

Map the user's language to the closest recipe. Keep modes materially
separate:

- phone-shot organic content reads as `ugc`;
- broadcast-quality multi-shot reads as `tv-spot`;
- product-as-hero with no presenter reads as `product-showcase`;
- presenter giving an opinion reads as `product-review`;
- trying on clothing casually reads as `ugc-virtual-try-on`;
- trying on clothing editorially reads as `virtual-try-on`.

If the user asks for a hybrid, choose one dominant visual texture and
state how the secondary influence appears. Do not combine incompatible
textures without explaining which mode governs each visible element.

**Default when the user doesn't specify:** `ugc`.

### 2. Establish the mode before the story

Open with one sentence that names:

- the ad mode and its visual texture;
- the camera style;
- the dominant authenticity or production signal;
- the narrative beat structure.

Example pattern:

```text
A casual UGC creator-style video shot on a phone in vertical 9:16, with
handheld micro-shake, natural window lighting, a real-environment
background, and a 5-beat structure: hook, problem, demo, payoff, soft CTA.
```

### 3. Translate the entire scene into the mode

Apply the mode's visual texture to every visible category:

- camera style (handheld phone vs tripod vs gimbal vs studio rig);
- lighting (natural window vs 3-point studio vs broadcast-grade);
- framing (medium-close selfie vs full-body vs product-hero macro);
- background (real environment vs minimalist sweep vs styled set);
- editing (jump cuts vs clean transitions vs dynamic multi-shot cutting);
- imperfections (refocus hunting, slight overexposure, verbal fillers
  for UGC; controlled precision for polished modes).

### 4. Structure the narrative beats

Every mode has a beat structure with timestamps. Use numbered shots or
stages, each with one primary event and a visible end state.

The universal 5-beat spine (applies to most UGC and review modes):

```text
Beat 1 — Hook (0-2s):     Pattern-interrupt + pre-qualify the viewer
Beat 2 — Problem (2-7s):  Name the pain in the viewer's language
Beat 3 — Demo (7-22s):    Show the product working — proof, not claim
Beat 4 — Payoff (22-27s): Specific, measurable outcome
Beat 5 — CTA (27-30s):    One clear action, spoken and on-screen
```

**Only the demo beat scales with duration.** For 15s, compress demo to
8s and combine payoff + CTA into 3-4s. Do not add a second hook, second
problem, or extra CTAs.

Not all modes use the 5-beat spine. Product Showcase uses 1-2-1 or
4-beat. TV Spot uses 0-5-22-30. The recipe defines the structure; the
skill enforces it.

Treat time ranges as a readable pacing plan:

- hook or reaction: roughly 2-3 seconds;
- simple action or beat: roughly 3-5 seconds;
- complex action, demonstration, or multi-step: roughly 5-10 seconds.

If the requested actions do not fit, split the concept into multiple
prompts. Do not compress many steps, locations, and reactions into an
unreadable sequence.

### 5. Write the hook

The hook is the single highest-leverage element. Write 3-5 hook variants
per concept. The first frame matters as much as the first line — brief
the AI to open mid-action, already using the product, mid-sentence, in a
real environment.

Hook formula bank (10 patterns):

1. **Contrarian claim** — "Stop buying [category] until you've seen this."
2. **Specific number** — "I replaced 14 products with one."
3. **Cost compare** — "Why I stopped paying $180 for this."
4. **Identity call-out** — "If you're a [role] over 30, watch this."
5. **Mistake confession** — "I wasted two years doing X the wrong way."
6. **Problem callout** — "I stopped buying X because..."
7. **Curiosity / open loop** — "I almost returned this until day four."
8. **Visual surprise** — Show the product doing something unexpected in frame one.
9. **Social proof** — "I didn't believe the reviews until..."
10. **Native mimicry** — Open like an organic post (GRWM, haul, reaction).

Pattern-interrupt and curiosity-gap hooks have the highest 3-second hold
rate. Social-proof opens have the highest CTR-to-click conversion among
viewers who hold.

### 6. Direct the creator performance

The presenter's behavior must match the mode:

- **UGC modes**: conversational, like a friend recommending. Contractions,
  filler words ("um", "like"), casual numbers ("after like two weeks").
  Lock hook and CTA verbatim; leave the middle as beats. Mention one
  honest drawback or learning curve.
- **Product Review**: skeptic-to-convert structure ("I was skeptical
  but...") outperforms straight praise. One honest con makes every pro
  more believable.
- **Product Showcase**: no presenter. The product speaks through motion,
  material, and light.
- **TV Spot**: professional delivery. Testimonial format outperforms
  announcer-voice. The viewer is the protagonist; the brand is the guide.

Avoid relying only on words such as `authentic`, `casual`, or
`professional`. Make the mode visible through observable behavior,
timing, and framing.

### 7. Specify camera style per mode

Each mode has a camera discipline. Encode the camera style explicitly:

| Mode | Camera style | Key discipline |
|---|---|---|
| UGC family | Handheld phone, 9:16, eye-level, slight micro-shake | Lock exposure and focus; no digital zoom; rear camera |
| UGC Unboxing | 3 angles: overhead, 45-degree, close-up macro | Product visible by 0:03; reveal in layers |
| UGC How-To | Medium shot showing hand + product in real context | Cut every 2-4s; product fills 50%+ of frame |
| Product Showcase | Tripod or gimbal, 16:9 or 1:1, low-angle hero | One camera move per beat; cap rotation 10-15°; protect text/logos |
| Product Review | Handheld phone or casual tripod, 9:16 | Show product in use, not on shelf |
| TV Spot | Professional cinematography, 16:9, multi-shot | 4-8 scenes for 30s; title-safe framing |
| UGC Virtual Try-On | Phone, waist-level, 9:16, 2-2.5m distance | Full-body multi-angle; always include movement |
| Pro Virtual Try-On | Tripod or gimbal, 85-135mm equivalent | 3-point studio lighting; editorial framing |
| Wild Card | User-defined | State the camera discipline explicitly |

Load `seedance-camera-presets` when the user names a specific camera
move ("dolly in", "bullet-time orbit"). For ordinary ad mode prompts
without such direction, this skill's camera table is sufficient.

### 8. Direct audio

Audio direction depends on the mode and whether the user requests
lip-synced dialogue:

- **UGC modes**: natural voice with room echo, ambient background noise
  mixed in, no background music during speech. Do not burn in captions or
  on-screen text overlays — Seedance cannot reliably render readable text.
  Platforms (TikTok, Reels, YouTube Shorts) generate captions natively;
  rely on the platform's caption system instead of embedding text in the
  video itself.
- **Product Showcase**: typically no voiceover. Product speaks through
  motion and material. When audio is requested, use Seed Audio for
  sensory SFX (pour, click, sparkle) + subtle music bed.
- **TV Spot**: professional voiceover or testimonial-style delivery.
  Licensed music bed. Sound design with SFX. Broadcast loudness spec
  (-24 LKFS for TV, -14 LUFS for streaming).
- **Product Review**: voice is mandatory — silent videos engage at 0.90x
  vs 1.09x with voice. Voice won in every category tested.

When the user requests lip-synced dialogue audio, use the audio-first
pipeline: generate Seed Audio dialogue first, then pass it as
`reference_audio` to Seedance. See [Audio-video alignment](#audio-video-alignment-dialogue-scenes)
below. Load `seed-audio-prompt` for the audio prompt structure.

### 9. Close with the CTA

Each mode has a CTA pattern:

- **UGC family**: soft CTA — permission, not pressure. One action, one
  destination. Never bolt on a second CTA.
- **Product Review**: single action, single destination. Soft not pushy.
- **Product Showcase**: no spoken CTA. End on the product, not the logo.
- **TV Spot**: brand lock-in in final 3-5 seconds. Spoken + on-screen.
- **UGC How-To**: harder CTA — viewers have been educated. Include
  brand name.

### 10. End with a mode seal

Close with one compact sentence that reinforces:

- the ad mode;
- the visual texture;
- the camera style;
- the audio direction;
- relevant exclusions (positive phrasing only).

Do not repeat the entire prompt. The seal exists to prevent the mode
from drifting during later shots.

## Hook variant generation

By default, when the user asks for a UGC ad mode prompt, generate
**3-5 hook variants** for the first 0-3 seconds. This is the single
highest-leverage element. Present each variant as labeled alternatives
within the Shot 1 section:

```text
Shot 1 — Hook (0-2s) [Variant A]: <contrarian claim hook>
Shot 1 — Hook (0-2s) [Variant B]: <specific number hook>
Shot 1 — Hook (0-2s) [Variant C]: <curiosity gap hook>
```

Treat hooks as separate ads — test 4 hooks × 1 mode before testing 1
hook × 4 modes. Creative fatigue is fast (5-14 days on TikTok); plan for
15-30 distinct variations per month.

## Output formats

### Mode block

Use when the user only wants ad-mode wording:

```text
[Ad Mode]
<Mode-first sentence naming visual texture, camera style, and beat structure.>

[Narrative Beats]
Beat 1 (<time range>): <hook event and visible end state>.
Beat 2 (<time range>): <problem/demo event and visible end state>.
...
Beat N (<time range>): <CTA event and visible end state>.

[Mode Seal]
<Compact closing mode sentence and relevant exclusions.>
```

### Full ad prompt

Use when the user asks for a complete Seedance 2.5 prompt:

```text
[Ad Mode]
<Mode-first sentence naming visual texture, camera style, and beat structure.>

[Subject]
<Presenter definition, product definition, or both. Reference @Image N / @Audio N
as needed. Define each reference's role explicitly.>

[Scene and Environment]
<Location, lighting, background, surface, and observable tone.>

[Visual Style]
<Mode-specific visual texture: handheld vs studio, natural vs controlled
lighting, real environment vs minimalist sweep, editing style.>

[Shot Plan]
Shot 1 (<time range>): <beat name — one event and visible end state>.
Shot 2 (<time range>): <beat name — one event and visible end state>.
Shot 3 (<time range>): <beat name — one event and visible end state>.
Shot 4 (<time range>): <beat name — one event and visible end state>.
Final Shot (<time range>): <closing event and final visible state>.

Shot labels and count adapt to the mode's beat structure — see the
recipe in references/mode-recipes.md. UGC modes use 5 beats; Product
Showcase uses 1-2-1 or 4-beat; TV Spot uses 0-5-22-30.

[Camera]
<Camera style, angles, movement discipline, framing, safe zones.>

[Audio]
<Voice style, ambience, SFX, music approach. Dialogue in {curly braces}
for lip-sync when audio is requested.>

[Mode Seal]
<Compact mode, texture, camera, audio, tone, and exclusions.>
```

Return the prompt directly. Do not add production workflow, tool
selection, asset management, approval gates, or generation instructions
unless the user explicitly asks for them.

## Audio-video alignment (dialogue scenes)

When the user explicitly requests lip-synced dialogue audio for any UGC
or review mode, follow the audio-first pipeline:

1. **Generate Seed Audio dialogue first** — use `seed-audio-prompt` to
   write the audio prompt, then generate via `seed_audio_generate`.
2. **Verify audio duration ≤ video duration.** If audio exceeds video
   duration, trim the audio prompt (shorter ambience tails, fewer
   pauses) and regenerate.
3. **Pass the audio as `reference_audio`** to the Seedance 2.5 task
   (`seedance_2_5_create_task`).
4. **Use `{curly brace}` syntax** in the Seedance prompt for dialogue
   lines that should be lip-synced.
5. **Adjust shot timestamps** in the prompt to match actual audio timing
   after generating the audio.

This is opt-in. When the user does not request lip-synced audio,
generate video directly and let Seedance's native audio handle dialogue.

## Integration with existing skills

| Partner skill | What it owns | What this skill provides |
|---|---|---|
| `seedance-prompt-25` | Six-part formula, reference syntax, audio brackets, scene staging, timestamps | Mode-specific phrasing that drops into the formula's slots |
| `seed-audio-prompt` | Seed Audio 1.0 prompt structure (dialogue, music, SFX, ambience) | Mode-specific audio direction (voice style, ambience, music) |
| `seedance-camera-presets` | Camera moves and MoveSet styles | Mode-specific camera discipline (handheld phone vs gimbal vs studio rig) |
| `seedance-lighting-presets` | Lighting recipes (causal lighting for elements and video) | Mode-specific lighting approach (natural window vs 3-point studio vs broadcast) |
| `seedance-acting-console` | Per-character emotion cues | Mode-specific creator performance direction (conversational vs professional vs testimonial) |
| `seedance-pacing-presets` | Speed ramps and montage pacing | Mode-specific beat timing (5-beat spine, 1-2-1, 0-5-22-30) |

Load a partner skill only when the user names a specific axis ("dolly
in on her face", "golden hour lighting", "rage at medium intensity").
For ordinary ad mode prompts without such direction, this skill alone
is sufficient. Do not let two skills fight: exactly one dominant visual
texture and 1-2 camera moves per clip.

## Custom-mode procedure

For an unlisted mode:

1. Identify the dominant visual texture (phone-shot, studio, broadcast,
   or hybrid).
2. Define the camera style and framing discipline.
3. Name the narrative beat structure with timing.
4. Choose 3-5 hook formulas that fit the mode.
5. Define creator performance and product interaction.
6. Specify audio direction (voice, ambience, SFX, music).
7. Choose a CTA pattern (soft, hard, visual, spoken).
8. Write a mode-first opening and a compact mode seal.
9. Add only exclusions that prevent likely mode drift.
10. Name common failure modes for the custom mode.

## Exclusion rules

- Use positive phrasing throughout. Instead of "no cluttered
  background," write "clean, minimal background with product as sole
  focal point."
- Instead of "no logo deformation," write "preserve all printed text
  and logo integrity: rigid, sharp, undeformed."
- Exclude only likely contradictions: studio lighting in a UGC mode,
  handheld shake in a product showcase, talking head in a product-as-hero
  shot.
- Do not use exclusions as a substitute for positive mode direction.

## Self-check

Before returning the prompt, verify:

1. The mode appears before the story action.
2. Visual texture, camera style, and lighting are mode-appropriate.
3. The narrative beat structure matches the mode's recipe.
4. The hook formula is specific, not generic ("Check this out" is
   invisible).
5. Creator performance direction matches the mode (conversational for
   UGC, no presenter for showcase, professional for TV spot).
6. Product interaction is visible and mode-appropriate (in use, not on
   shelf).
7. Audio direction matches the mode and the user's audio preference.
8. The CTA pattern matches the mode (soft for UGC, brand lock-in for TV
   spot, no CTA for showcase).
9. The duration is right-sized for the mode and platform.
10. The mode seal is compact and does not contradict the mode.
11. Text and logo protection directives are included when the product
   has visible branding or text.
12. The response contains the prompt, not an unrelated production
    workflow.
