---
name: seed-audio-prompt
description: Write structured Seed Audio 1.0 prompts for full-soundscape audio generation including dialogue, music, SFX, and ambience. Supports text-to-audio (T2A) and text-plus-audio-to-audio (TA2A) with voice cloning. Invoke when the user asks to generate Seed Audio 1.0 prompts, write audio prompts for BytePlus audio generation, create audiobook/dialogue/soundscape scripts, or design multi-character audio scenes.
---

# Seed Audio Prompt

Write production-grade prompts for BytePlus Seed Audio 1.0 (model ID `seed-audio-1.0`), a multimodal full-soundscape generator that produces dialogue, background music, sound effects, and ambience in a single pass. Unlike traditional TTS, Seed Audio 1.0 is an "audio director" that interprets scene descriptions, character voice profiles, and script content simultaneously.

## Source authority

The public API reference is the authoritative source of truth for this skill. Prompting conventions (in-prompt speaker tags, timestamp syntax) originate from the BytePlus prompting guide (Lark wiki, updated July 20th 2026) and are labeled as such where they are not defined in the public API.
- [Seed Audio 1.0 API Reference](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01) — authoritative
- [Seed Audio 1.0 Pricing](https://docs.byteplus.com/en/docs/byteplusvoice/audiopricing) — authoritative

Seed Audio 1.0 is in early access. Applications for early access are open via a whitelist form; confirm current access status before building.

When the official API reference is updated, prefer the live page over this skill where they conflict.

## Mandatory prompt structure

Every Seed Audio 1.0 prompt must be assembled in this order. Do not skip sections that apply to the user's task.

```
=== INPUT REFERENCES ===
=== TASK TYPE ===
=== SCENE & ATMOSPHERE ===
=== CHARACTERS & DIALOGUE ===
=== CONSTRAINTS ===
```

### 1. INPUT REFERENCES (always first)

List every reference audio clip the user provides. Label them with `@Audio1`, `@Audio2`, `@Audio3` using sequential numbering starting from 1 (no space, no underscore). Include a short role or description for each reference so the model and the human reader know what each clip is for.

```
=== INPUT REFERENCES ===
@Audio1: [role, e.g. "female protagonist voice timbre — Lux"]
@Audio2: [role, e.g. "male antagonist voice timbre — Sylas"]
@Audio3: [role, e.g. "male heroic voice timbre — Garen"]
```

Rules for references:
- Up to 3 reference audio clips per request (reference-audio mode), OR exactly 1 reference image (reference-image mode). Audio and image references are mutually exclusive.
- Per-clip duration: up to 30 seconds.
- Per-clip size: up to 10 MB.
- Audio formats: WAV, MP3, PCM, OGG_OPUS.
- Image format: 1 image, ≤10 MB, JPEG/PNG/WebP. In image mode, `text_prompt` contains ONLY the text to be synthesized (no scene/voice description).
- Each clip serves exactly one purpose: voice timbre cloning, emotion reference, or SFX reference.
- Per reference, provide exactly one of: `speaker` (a TTS 2.0 or cloned voice ID), `audio_data` (base64), or `audio_url`. For image mode, provide exactly one of: `image_data` (base64) or `image_url`.
- Voice cloning uses `<<TGT_SPK1>>`, `<<TGT_SPK2>>`, `<<TGT_SPK3>>` in-prompt speaker tags mapped to `@Audio1`, `@Audio2`, `@Audio3` respectively. (Prompting-guide convention; the API-level reference token is `@AudioN`. Not documented in the public API reference.)
- When no references are provided (text-only / T2A mode), skip this section or write "None."

### 2. TASK TYPE

Declare which generation mode applies. Pick exactly one.

```
=== TASK TYPE ===
T2A (Text-only)  |  TA2A (Reference-audio)  |  Reference-image
```

**T2A — Text-only generation**: Pure text prompt describing everything — environment, music, SFX, character voices, and dialogue. No reference audio clips. Best for one-off scenes, ambience beds, and standalone content where voice cloning is not needed.

**TA2A — Reference-audio generation**: Uses up to 3 reference audio clips for voice cloning and emotion reference. Reference clips are tagged in the prompt with `<<TGT_SPK1>>`, `<<TGT_SPK2>>`, `<<TGT_SPK3>>`. Best for multi-character dialogue, audiobooks, and scenes requiring consistent character voices across multiple generations. (Speaker ID mode is also supported: pass a `speaker` voice ID instead of a clip.)

**Reference-image generation**: Exactly 1 image (≤10 MB, JPEG/PNG/WebP). The model describes the scene in the image and generates appropriate sound. `text_prompt` contains ONLY the text to be synthesized. Image and audio references are mutually exclusive — cannot mix `image_data`/`image_url` with `audio_data`/`audio_url`/`speaker`.

### 3. SCENE & ATMOSPHERE

Describe the acoustic environment, background music, and sound effects in rich detail. This section sets the sonic world before any character speaks.

```
=== SCENE & ATMOSPHERE ===
[Environment description: location, weather, time of day, ambient sounds, reverb characteristics]
[Background music: genre, instruments, tempo, mood, dynamics, how it evolves over the scene]
[Sound effects: specific sounds, their timing, distance, and acoustic quality]
```

Rules for environment:
- Be specific about acoustic quality: "hallway reverb," "stone corridor echo," "open field with distant wind."
- Describe layers of sound: foreground, midground, background.
- Mention how the environment evolves: "the rain gradually intensifies," "footsteps fade from near to far."

Rules for background music:
- Describe genre, instruments, tempo, and mood.
- Specify dynamics and when the music changes: "drums quicken," "choir swells," "music suddenly cuts out."
- Use cinematic terminology: "deep war drums," "low brass," "mournful choir," "soaring strings."

Rules for sound effects:
- Write onomatopoeia in quotes: "ring-a-ling," "zzzip," "clack," "shhhk," "BOOM," "CLANG."
- Describe the acoustic quality of each effect: "distant," "sharp," "muffled," "echoing."
- Position effects in time relative to dialogue: "before speaking," "after the line," "underneath the conversation."

### 4. CHARACTERS & DIALOGUE

Define each character with a full voice profile, then script their dialogue in scene order. Use the character label format consistently across every line spoken by that character.

```
=== CHARACTERS & DIALOGUE ===
[Character Name] ([age/gender], [accent], [voice quality description], [emotional baseline], [delivery style]) says [delivery note]: "[dialogue]"
```

**Character voice profile format (T2A)**:

```
Name (age, gender, accent, voice timbre, emotional tone, delivery style) says: "dialogue text"
```

Examples:
```
Aric (young prince, breathless but brave, fantasy war film style) says: "There are too many. The valley is full of them."

The commentator (middle-aged male, British accent, rich and penetrating voice, classic sports commentary, extremely exhilarated) shouts in a rapid, soaring tone: "OH, HE SCORES!!! WHAT A GOAL!"
```

**Character voice profile format (TA2A)** with voice cloning tags (`<<TGT_SPKN>>` is a prompting-guide convention for in-prompt speaker assignment; the API-level reference token is `@AudioN`):

```
Name (voice description, voiced by <<TGT_SPKN>>) says [delivery note]: "dialogue text"
```

Examples:
```
Marcus (male voice, smooth and confident, warm playful broadcaster tone, clear articulation, voiced by <<TGT_SPK1>>), upbeat and inviting, says: "Hey there! Quick question—what's the most embarrassing thing that's ever happened to you?"

Lux (clear, bright young female voice, resonant with a crystalline timbre, voiced by <<TGT_SPK1>>) says firmly yet pleadingly: "Sylas, it's not too late to stop."
```

**Voice profile components** (describe as many as apply):
- **Age**: young, teenage, young adult, middle-aged, old
- **Gender**: male, female
- **Accent**: American, British, Australian, etc.
- **Timbre**: bright, dark, warm, cold, breathy, rich, thin, gravelly, smooth, crystalline, resonant, deep, airy
- **Emotional baseline**: calm, anxious, angry, joyful, sad, determined, fearful, playful, serious
- **Tone**: soft, loud, gentle, fierce, steady, shaky, confident, hesitant
- **Speed**: slow, rapid, measured, speeding up, drawing out words
- **Delivery style**: fantasy war film, classic sports commentary, broadcaster, conversational, theatrical, whispered, shouted

**Dialogue rules**:
- Put spoken text in double quotes.
- Describe delivery before the quote: "says playfully and teasingly," "shouts in a rapid, soaring tone," "whispers, voice cracking."
- Include physical actions and sounds inline: "gasping then bursting out laughing," "slapping his knee with an audible clap."
- For multi-character scenes, alternate characters naturally with stage-direction-like descriptions between lines.
- Wrap ambient descriptions and non-speech sounds in square brackets: `[Ambient street sounds: passing cars, distant chatter.]`
- Prompt language and script language should be the same language.

**Timestamp control** (optional, T2A and TA2A — prompting-guide convention; not defined in the public API reference):

For precise timing of individual lines, use the `[start_time:end_time]` bracket notation immediately before the dialogue:

```
Ryan (young adult male, warm voice) calls out anxiously: "[5.5s:8.0s] Maya! Wait—you're really leaving tonight?"
Maya (young adult female, soft voice) answers softly: "[8.5s:11.5s] I have to. I've spent years chasing this… I can't walk away now."
```

Timestamps are in seconds with decimal precision. The model will fit each character's spoken line within the specified time window.

### 5. CONSTRAINTS

Close with any negative constraints or quality directives.

```
=== CONSTRAINTS ===
Max duration: [up to 120 seconds]
Languages: [the prompt and dialogue language]
Quality notes: [any specific output requirements]
```

Key limits (see Quick reference card for the authoritative table):
- `text_prompt` max 3000 characters.
- Generated audio max 120 seconds per call (billing is based on `original_duration`).
- Max 3 reference audio clips OR 1 reference image.
- Cross-lingual synthesis is supported; consult the [BytePlus voice list](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01) for current supported languages.
- Pricing: 0.15 USD per minute of generated audio (0.0025 USD/second), billed per second.

## Full example: T2A — Sci-fi news broadcast

```
=== INPUT REFERENCES ===
None

=== TASK TYPE ===
T2A

=== SCENE & ATMOSPHERE ===
A deep synthesizer pad underpins the entire scene with synth drum beats, creating a tense and uneasy mood. A low humming sound accompanies various electronic sound effects, evoking technology and crisis. An electronic chime signals a screen tap, followed by a data-loading chime. Later, alarm sounds burst in, the music stops, and a spacecraft engine roars in flight.

=== CHARACTERS & DIALOGUE ===
The narrator (female, slightly lower pitch, mechanical quality) says in a grave tone: "...with the rapid population growth and the problem of global warming, Earth will no longer be suitable for human habitation. Predictions show that Earth's lifespan is now facing a crisis."

Then a voice comes as if from a television, with a slight reverberation: "Humanity has begun searching for a new habitable place."

The announcer (young female, English, slightly lower pitch, gentle temperament) reports in a steady tone: "The surface temperature today is seventy…"

A woman (young female, bright voice, energetic) says in a worried tone: "Ugh! If this keeps up, even down here underground won't be livable anymore."

A voice comes as if from a walkie-talkie: "Looks like the Eden Project needs to speed up."

The broadcaster (middle-aged male, deep resonant voice) announces in a serious tone: "Emergency notice, emergency notice. All technical personnel, please assemble in the command pod immediately."

The broadcaster continues in a professional tone: "This planet, code-named 'New Eden,' has undergone preliminary exploration, which shows it possesses abundant water resources, a suitable atmospheric composition, and potential signs of life, making it one of the best candidate locations in the Eden Project."

=== CONSTRAINTS ===
Max duration: 120 seconds
Languages: English
```

## Full example: TA2A — Multi-character fantasy battle dialogue

```
=== INPUT REFERENCES ===
@Audio1: female protagonist voice timbre — Lux (clear, bright, crystalline)
@Audio2: male antagonist voice timbre — Sylas (raspy, low, gravelly)
@Audio3: male heroic voice timbre — Garen (deep, powerful, booming)

=== TASK TYPE ===
TA2A

=== SCENE & ATMOSPHERE ===
Low, somber strings swell beneath the distant roar of war drums. A harsh, grinding metallic scraping of heavy chains dragging across stone fills the air, followed by a sharp clang of iron shackles striking together. A bright, ringing chime of gathering light energy resonates, clear like wind chimes and crystal on the verge of shattering. A whooshing surge of energy builds, then a beam of light fires with a sharp "shhhk!" — it explodes against the chains with a dazzling, ringing "CLANG!!", followed by a thunderous "BOOM!" as a shockwave scatters debris. The rushing "whoom, whoom, whoom" of a massive spinning blade slices through the air. A golden shield blooms with a resonant, sustained "diiing—". All sound suddenly cuts out, leaving only the moan of wind and heavy breathing. The music shifts into a long, lingering clarinet solo that slowly fades into silence.

=== CHARACTERS & DIALOGUE ===
Sylas (raspy, low, gravelly male voice, rough and menacing, like sand grinding over rusted iron, voiced by <<TGT_SPK2>>) speaks in a cold, taunting tone: "Lux. Did your brother send you to finish the job?"

Lux (clear, bright young female voice, resonant with a crystalline timbre, voiced by <<TGT_SPK1>>) says firmly yet pleadingly: "Sylas, it's not too late to stop."

Garen (deep, powerful, booming male voice, heroic and resolute, voiced by <<TGT_SPK3>>) roars: "DEMACIA!!"

Sylas (voiced by <<TGT_SPK2>>) snarls through gritted teeth: "Demacia's dog—"

Lux (voiced by <<TGT_SPK1>>) shouts urgently, throwing herself between them: "Stop! Both of you, STOP!"

Lux (voiced by <<TGT_SPK1>>) speaks softly, almost carried off by the wind: "He's our brother… he once was."

=== CONSTRAINTS ===
Max duration: 120 seconds
Languages: English
```

## Full example: T2A — Timestamp-controlled emotional dialogue

```
=== INPUT REFERENCES ===
None

=== TASK TYPE ===
T2A

=== SCENE & ATMOSPHERE ===
A quiet evening room. Soft ambient room tone. Occasional distant traffic. The air is still and heavy with unspoken tension.

=== CHARACTERS & DIALOGUE ===
Ryan (young adult male, warm voice) calls out anxiously, slightly out of breath: "[5.5s:8.0s] Maya! Wait—you're really leaving tonight?"

Maya (young adult female, soft voice) answers softly, forcing herself to stay composed: "[8.5s:11.5s] I have to. I've spent years chasing this… I can't walk away now."

=== CONSTRAINTS ===
Max duration: 15 seconds
Languages: English
```

## Ideal use cases

- **Audiobooks**: T2A and TA2A eliminate the need for human recording or manual SFX. Supports science fiction, daily talk, adventure, and inner monologue at roughly 1/10 the cost of human recording.
- **Video dubbing**: Generate character voices from text descriptions or reference audio. Human voice + SFX + background music in a single pass.
- **Gaming**: Generate character voices and environmental sound effects for immersive player experiences.
- **Podcast and radio drama**: Multi-character dialogue with full sound design from a single prompt.
- **Language learning content**: Generate audio in multiple languages with precise timestamp control per sentence.

## What makes Seed Audio 1.0 different from normal TTS

| Feature | Audio 1.0 | Normal TTS |
|---|---|---|
| Text-to-Speech | ✅ | ✅ |
| Voice Cloning | ✅ | ✅ |
| Text Prompt to Audio (T2A) — describe voice, atmosphere, BGM, SFX in free text | ✅ | ❌ |
| Text Prompt + Audio to Audio (TA2A) — reference audio + text prompt for voice/emotion reference | ✅ | ❌ |
| Multimodal soundscape (dialogue + music + SFX + ambience in one pass) | ✅ | ❌ |
| Accurate time control per sentence | ✅ | ❌ |
| Multilingual generation | ✅ | Varies |

## Quick reference card

### Model identity
- Model ID: `seed-audio-1.0`
- Endpoint: `POST https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/create`
- Auth: `X-Api-Key` header (required). Optional: `X-Api-Request-Id` (client-generated UUID for tracing).
- Output: non-streaming HTTP only.

### Request body
| Field | Description |
|---|---|
| `model` (required) | `seed-audio-1.0` |
| `text_prompt` (required) | Up to 3000 characters. In image mode, contains only text to synthesize. |
| `references[]` | Array of references. Per reference: exactly one of `speaker` (TTS 2.0 / cloned voice ID), `audio_data` (base64), `audio_url`; OR `image_data` / `image_url` for image mode. Max 3 audio OR 1 image. |
| `audio_config` | Object containing `format`, `sample_rate`, `speech_rate`, `loudness_rate`, `pitch_rate`. |
| `watermark` | Object (see below). |

### Response fields
| Field | Description |
|---|---|
| `code` / `message` | Status code and message. |
| `audio` | Base64-encoded generated audio. |
| `duration` | Post-processed audio duration (seconds). |
| `original_duration` | Pre-processed duration — **basis for billing**, capped at 120s. |
| `url` | Temporary download URL — **expires in 2 hours**. |

### Limits
| Parameter | Limit |
|---|---|
| `text_prompt` max characters | 3000 |
| Max generated audio duration | 120 seconds (2 minutes) |
| Max reference audio clips | 3 (reference-audio mode) |
| Max reference images | 1 (reference-image mode) |
| Reference clip max duration | 30 seconds each |
| Reference clip max size | 10 MB each |
| Reference clip formats | WAV, MP3, PCM, OGG_OPUS |
| Reference image formats | JPEG, PNG, WebP (≤10 MB) |

### Output configuration (`audio_config`)
| Parameter | Range / Values |
|---|---|
| `format` | wav / mp3 / pcm / ogg_opus |
| `sample_rate` | one of [8000, 16000, 24000, 32000, 44100, 48000]; default 40000 (wav/pcm), 44100 (mp3) |
| `speech_rate` | -50 to 100 (-50 = 0.5x, 0 = default, 100 = 2.0x) |
| `loudness_rate` | -50 to 100 (-50 = 0.5x, 0 = default, 100 = 2.0x) |
| `pitch_rate` | -12 to 12 semitones (0 = default) |

### Watermark (`watermark` object)
| Sub-field | Type | Description |
|---|---|---|
| `aigc_watermark` | bool | Explicit rhythm marker appended to end of audio. Default `false`. |
| `aigc_metadata` | object | Implicit header metadata. Sub-fields: `enable` (bool), `content_producer`, `produce_id`, `content_propagator`, `propagate_id`. Default disabled. |

### Pricing
- **0.15 USD per minute** of generated audio (0.0025 USD/second), billed per second based on `original_duration`.
- 60-minute free trial provided on service activation.
- Prepaid packages available (e.g. 200 min / $28.50 up to 2,000,000 min / $240,000).

### Long-form pattern
For content longer than 2 minutes, chain generations: take the output of one call, use it as a reference audio clip in the next call, and continue the scene. Voice identity carries through if you re-pass the original voice reference clips.

### Prompt language
Prompt language and dialogue/script language should be the same language. Seed Audio 1.0 supports cross-lingual synthesis; consult the [API reference](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01) for the current voice and language list.
