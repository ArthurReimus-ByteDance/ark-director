---
name: seed-audio-prompt
description: Write structured Seed Audio 1.0 prompts for full-soundscape audio generation including dialogue, music, SFX, and ambience. Supports text-to-audio (T2A) and text-plus-audio-to-audio (TA2A) with voice cloning. Invoke when the user asks to generate Seed Audio 1.0 prompts, write audio prompts for BytePlus audio generation, create audiobook/dialogue/soundscape scripts, or design multi-character audio scenes.
---

# Seed Audio Prompt

Write production-grade prompts for BytePlus Seed Audio 1.0 (model ID `seed-audio-1.0`), a multimodal full-soundscape generator that produces dialogue, background music, sound effects, and ambience in a single pass. Unlike traditional TTS, Seed Audio 1.0 is an "audio director" that interprets scene descriptions, character voice profiles, and script content simultaneously.

## Source authority

The public API reference is the authoritative source of truth for request fields and limits. Prompt-writing conventions originate from the internal Seed Audio 1.0 prompting guide and are labeled where they are not defined in the public API.
- [Seed Audio 1.0 API Reference](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01) — authoritative
- [Seed Audio 1.0 Prompting Guide](https://bytedance.larkoffice.com/wiki/WgU4wFVQ8iZgvjkHHdbcDmhCnug) — T2A/TA2A prompting conventions and examples, modified July 23, 2026
- [Seed Audio 1.0 Pricing](https://docs.byteplus.com/en/docs/byteplusvoice/audiopricing) — authoritative

Seed Audio 1.0 is in early access. Applications for early access are open via a whitelist form; confirm current access status before building.

When the official API reference is updated, prefer the live page over this skill where they conflict.

## Prompt assembly

Build the shortest prompt that clearly communicates the requested result. Use plain-language headings only when they improve readability, and omit sections that do not apply.

For full-soundscape generation, cover the five ingredients recommended by the prompting guide:

1. The environment: location, weather, context, and acoustic space
2. Background music and sound effects
3. Character actions or appearance when they affect the performance
4. Each character's voice: age, gender, accent, emotion, tone, speed, and timbre as relevant
5. The exact dialogue

Arrange those ingredients as one chronological audio scene, not as unrelated inventories. A typical prompt follows this order:

1. Input references, only when the request includes reference audio
2. Opening environment, ambience, and music
3. Dialogue, actions, and sound effects in the order they occur
4. Ending behavior: resolve, fade, sustain, or cut
5. Creative or quality constraints, only when the user supplies them

Generation mode and request limits belong in request metadata or validation, not in model-facing prompt boilerplate.

### Input references

The API contract is the request's `references[]` array. For each supplied audio reference, add one `references[]` entry and identify its intended role. When the prompting guide's inline conventions are useful, map those entries sequentially to `@Audio1`, `@Audio2`, and `@Audio3` (no space or underscore) and describe each role for the model and human reader.

```text
Input references
@Audio1: Female protagonist voice timbre — Lux
@Audio2: Male antagonist voice timbre — Sylas
@Audio3: Male heroic voice timbre — Garen
```

Rules for references:
- Up to 3 reference audio clips per request (reference-audio mode), OR exactly 1 reference image (reference-image mode). Audio and image references are mutually exclusive.
- Per-clip duration: up to 30 seconds.
- Per-clip size: up to 10 MB.
- Audio formats: WAV, MP3, PCM, OGG_OPUS.
- Image format: 1 image, ≤10 MB, JPEG/PNG/WebP. In image mode, `text_prompt` contains ONLY the text to be synthesized (no scene/voice description).
- Each clip serves exactly one purpose: voice timbre cloning, emotion reference, or SFX reference.
- Per reference, provide exactly one of: `speaker` (a TTS 2.0 or cloned voice ID), `audio_data` (base64), or `audio_url`. For image mode, provide exactly one of: `image_data` (base64) or `image_url`.
- `@AudioN` labels and `<<TGT_SPKN>>` speaker tags are prompting-guide conventions, not fields or tokens defined by the public API. The source-backed reference contract is `references[]`.
- When using the prompting-guide convention for voice cloning, map `<<TGT_SPK1>>`, `<<TGT_SPK2>>`, and `<<TGT_SPK3>>` to the corresponding first, second, and third audio entries in `references[]`, labeled `@Audio1`, `@Audio2`, and `@Audio3` in the prompt.
- When no references are provided (text-only / T2A mode), omit the input references section.

### Generation mode

Determine which generation mode applies so the request is constructed correctly. Do not add a task-type heading to `text_prompt` unless the user asks for one.

**T2A — Text-only generation**: Pure text prompt describing everything — environment, music, SFX, character voices, and dialogue. No reference audio clips. Best for one-off scenes, ambience beds, and standalone content where voice cloning is not needed.

**TA2A — Reference-audio generation**: Uses up to 3 reference audio clips for voice cloning and emotion reference. Reference clips are tagged in the prompt with `<<TGT_SPK1>>`, `<<TGT_SPK2>>`, `<<TGT_SPK3>>`. Best for multi-character dialogue, audiobooks, and scenes requiring consistent character voices across multiple generations. (Speaker ID mode is also supported: pass a `speaker` voice ID instead of a clip.)

**Reference-image generation**: Exactly 1 image (≤10 MB, JPEG/PNG/WebP). The model describes the scene in the image and generates appropriate sound. `text_prompt` contains ONLY the text to be synthesized. Image and audio references are mutually exclusive — cannot mix `image_data`/`image_url` with `audio_data`/`audio_url`/`speaker`.

### Full-soundscape composition workflow

When the user wants dialogue, music, SFX, and ambience together, compose the prompt in this order:

1. **Establish the acoustic world.** State the place, time, weather, room or outdoor acoustics, and persistent ambience.
2. **Start the score.** Describe the background music's dramatic purpose, style, instruments, rhythm, mood, volume, and opening intensity.
3. **Introduce characters.** Give each character a stable name and a distinct voice profile before or at their first line. Include a reference-speaker tag in TA2A.
4. **Interleave events chronologically.** Write dialogue, physical actions, music changes, and discrete SFX in the order the listener should hear them.
5. **Control the mix narratively.** Say when music ducks beneath speech, an effect dominates the foreground, ambience remains distant, or silence replaces the score.
6. **Specify the ending.** Describe what fades, sustains, stops abruptly, or carries into silence.

Use event-relative cues such as "as she opens the door," "under his line," and "after the impact" by default. Add exact second-level timestamps only when the user explicitly requests them.

### Scene transitions and dynamic arcs

When the scene changes mood or location, describe the transition as an audible
state change rather than listing two sound palettes independently:

```text
Audio state A: [music, ambience, effects, intensity, and spatial character]
Transition trigger: [visible action or story event]
Transition behavior: [cut, resolve, crossfade, decay, or brief silence]
Audio state B: [new music, ambience, effects, intensity, and spatial character]
Forbidden carryover: [sounds from state A that must not continue]
```

Tie the transition to an observable event such as crossing a doorway, landing,
reaching safety, or a pursuer stopping. State what ends as well as what begins.
For example, when an intense chase reaches a calm beach, let drums and threat
sounds resolve at the boundary, then crossfade to surf, wind, birds, and a
gentler score. Do not allow roars, impacts, or chase percussion to leak into the
safe-location soundscape unless the story requires lingering threat.

For native video audio, keep this arc inside the Seedance prompt so sound and
picture share the same trigger. Use standalone Seed Audio when producing or
replacing a separate soundtrack, dialogue stem, ambience bed, or mix element.
When the audio is destined for a Seedance video, route the prompt to
`seedance-prompt-25` (2.5, up to 10 audio refs, 30s) or `seedance-prompt-20`
(2.0, up to 3 audio refs, 15s), and follow the audio-first pipeline in
`AGENTS.md` (audio duration ≤ video duration, same dialogue text in both
prompts, pass as `reference_audio`).

### Scene and atmosphere

Describe only the acoustic layers that matter to the request. This section can set the sonic world before any character speaks.

```text
Scene and atmosphere
Environment: [location, weather, context, foreground/background layers, and acoustic space]
Background music: [dramatic role, genre, instruments, tempo, mood, dynamics, relation to dialogue, and ending]
Ambience: [persistent environmental bed and how it evolves]
Sound effects: [source or action, acoustic character, distance or direction, relative cue, and decay]
```

Omit this heading and any unused layers for simple speech-only requests.

Rules for environment:
- Be specific about acoustic quality: "hallway reverb," "stone corridor echo," "open field with distant wind."
- Describe layers of sound: foreground, midground, background.
- Mention how the environment evolves: "the rain gradually intensifies," "footsteps fade from near to far."

Rules for background music:
- State its dramatic role: underscore, tension bed, transition, reveal, celebration, or outro.
- Describe style or genre, instruments and timbre, tempo or rhythmic feel, and mood.
- Specify its dynamic arc: how it begins, swells, thins out, changes instrumentation, or stops.
- Describe its relationship to speech and important effects: "softly under the dialogue," "ducks beneath her whisper," "drops out before the alarm," or "swells after the final line."
- State how it ends: clean stop, held unresolved note, crossfade, or gradual fade into silence.
- Prefer concrete musical language such as "low somber strings with distant war drums" over generic phrases such as "cinematic music."

Background music template:

```text
Background music: A [dramatic role] in a [style/genre], led by [instruments/timbres] at a [tempo/rhythmic feel]. It begins [dynamic], stays [mix relationship] beneath the dialogue, then [change tied to an event], and ends by [ending behavior].
```

Rules for ambience:
- Treat ambience as the persistent environmental bed, separate from one-off effects.
- Name foreground, midground, and background layers only when they help establish space.
- Describe distance, direction, room tone, echo, reverb, and gradual evolution.
- Keep ambience subordinate to intelligible dialogue unless the scene requires otherwise.

Rules for sound effects:
- Describe the source or action, material, acoustic character, and spatial position: "a heavy iron chain scrapes harshly across stone from the rear left."
- Position effects relative to actions or dialogue: "as the locker shuts," "under the last word," or "immediately after the impact."
- Describe evolution or decay when important: approaches, recedes, rings out, echoes, rattles, or fades.
- Use onomatopoeia in quotes when it clarifies the desired texture: "ring-a-ling," "zzzip," "clack," "shhhk," "BOOM," or "CLANG." Do not use it as a substitute for describing the sound.
- Identify whether an effect sits in the foreground, midground, or background when the mix could otherwise be ambiguous.

Sound effect template:

```text
As [triggering action], [sound source] produces a [acoustic character] "[optional onomatopoeia]" from [distance/direction or mix layer], then [decay/evolution].
```

### Characters and dialogue

Define each character with the voice attributes needed to distinguish them, then script their dialogue in scene order. Use the same character name on every line. Give the complete voice profile on first mention; later lines may shorten the description but must preserve the name and, in TA2A, the same `<<TGT_SPKN>>` mapping.

```text
Characters and dialogue
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

**Character voice profile format (TA2A)** with voice cloning tags (`<<TGT_SPKN>>` and `@AudioN` are prompting-guide conventions for mapping in-prompt speakers to the ordered entries in `references[]`):

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
- Include physical actions or appearance when they affect delivery or generate sound: "gasping then bursting out laughing," "slapping his knee with an audible clap."
- For multi-character scenes, alternate characters chronologically and place actions, music changes, and SFX between the lines where listeners should hear them.
- Make each voice contrast with the others through useful traits such as pitch, timbre, accent, pacing, emotional baseline, or performance style.
- For voices heard through a device or space, describe the filter or acoustics: television reverb, walkie-talkie compression, telephone band-limit, public-address echo, or whispered proximity.
- Keep dialogue attribution explicit. Do not write an unlabeled block of alternating quotes.
- Wrap ambient descriptions and non-speech sounds in square brackets: `[Ambient street sounds: passing cars, distant chatter.]`
- Prompt language and script language should be the same language.

Multi-character dialogue template:

```text
Characters and dialogue
[Name A] ([full voice profile, and voiced by <<TGT_SPK1>> in TA2A]) [action], then says [delivery]: "[dialogue]"

[Music/SFX/ambience change triggered by the line or action.]

[Name B] ([contrasting full voice profile, and voiced by <<TGT_SPK2>> in TA2A]) replies [delivery]: "[dialogue]"

[Name A] (voiced by <<TGT_SPK1>> in TA2A) [brief delivery update]: "[next dialogue]"
```

For TA2A, make the reference plan unambiguous:

1. State what audio scene will be generated.
2. Identify each reference as `@Audio1`, `@Audio2`, or `@Audio3`.
3. State the purpose of each reference, such as a character's voice timbre or emotional performance.
4. Map each character to the matching ordered speaker tag, `<<TGT_SPK1>>` through `<<TGT_SPK3>>`, and never change that mapping within the prompt.

**Timestamp control** (only when the user explicitly asks for second-level timing; T2A and TA2A prompting-guide convention, not defined in the public API reference):

Do not add per-line timestamps by default. If the user explicitly requests second-level timing, use the `[start_time:end_time]` bracket notation immediately before the dialogue:

```
Ryan (young adult male, warm voice) calls out anxiously: "[5.5s:8.0s] Maya! Wait—you're really leaving tonight?"
Maya (young adult female, soft voice) answers softly: "[8.5s:11.5s] I have to. I've spent years chasing this… I can't walk away now."
```

Timestamps are in seconds with decimal precision. Treat them as prompting guidance rather than an API guarantee, and ensure the requested windows fit within the validated output duration.

### Reusable full-soundscape template

Use only the sections and fields the request needs.

```text
Input references
@Audio1: [character name] voice timbre — [purpose]
@Audio2: [character name] voice timbre — [purpose]

Scene and atmosphere
Environment: [place, time, weather/context, acoustic space]
Background music: [role, style, instruments, tempo, mood, dynamic arc, mix behavior, ending]
Ambience: [persistent foreground/midground/background environmental bed]

Characters and dialogue
[Character A] ([full voice profile], voiced by <<TGT_SPK1>>) [action] and says [delivery]: "[dialogue]"

[As the action occurs, describe the discrete SFX, position, acoustic quality, and decay. State any music or ambience change.]

[Character B] ([contrasting full voice profile], voiced by <<TGT_SPK2>>) replies [delivery]: "[dialogue]"

[Continue dialogue, actions, SFX, and score changes in chronological order.]

Ending
[Describe the final sound, music resolution or fade, ambience tail, and transition to silence.]
```

For T2A, omit `Input references` and all `<<TGT_SPKN>>` tags, but retain complete text-based voice profiles.

### Creative and quality constraints

Add only constraints that affect the generated content and are supplied or clearly implied by the user's request.

```text
Creative and quality constraints
Language: [the prompt and dialogue language]
Quality notes: [any specific output requirements]
```

Do not insert `Max duration: 120 seconds` into every prompt. Duration is a request and API validation concern: reject or split a requested generation longer than 120 seconds before sending it.

Key request limits (see Quick reference card for the authoritative table):
- `text_prompt` max 3000 characters.
- Generated audio max 120 seconds per call (billing is based on `original_duration`).
- Max 3 reference audio clips OR 1 reference image.
- Cross-lingual synthesis is supported; consult the [BytePlus voice list](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01) for current supported languages.
- Pricing: 0.15 USD per minute of generated audio (0.0025 USD/second), billed per second.

## Full example: T2A — Sci-fi news broadcast

```text
Scene and atmosphere
A deep synthesizer pad and sparse synth drums form a tense, uneasy underscore. A low electrical hum and sealed underground-room tone remain in the background. The score stays beneath speech and grows more urgent as the crisis escalates.

Characters and dialogue
The narrator (female, slightly lower pitch, mechanical quality) says in a grave tone: "...with the rapid population growth and the problem of global warming, Earth will no longer be suitable for human habitation. Predictions show that Earth's lifespan is now facing a crisis."

[The synthesizer holds a low unresolved note. A television relay clicks on in the midground.]

The television narrator (adult female, filtered through a television speaker with slight reverberation) continues gravely: "Humanity has begun searching for a new habitable place."

[A fingertip taps a glass screen with a crisp electronic chime; a short ascending data-loading sequence follows.]

The announcer (young female, English accent, slightly lower pitch, gentle temperament) reports steadily: "The surface temperature today is seventy…"

The technician (young adult female, bright energetic voice now tightened by worry) exhales sharply and says: "Ugh! If this keeps up, even down here underground won't be livable anymore."

[A walkie-talkie crackles in the foreground with narrow-band compression.]

The field operator (adult male, clipped delivery through the walkie-talkie) says urgently: "Looks like the Eden Project needs to speed up."

[A harsh alarm bursts across the facility. The music cuts out immediately, leaving only the alarm and room hum.]

The broadcaster (middle-aged male, deep resonant voice, heard through a public-address system with metallic echo) announces seriously: "Emergency notice, emergency notice. All technical personnel, please assemble in the command pod immediately."

The broadcaster continues in a professional tone: "This planet, code-named 'New Eden,' has undergone preliminary exploration, which shows it possesses abundant water resources, a suitable atmospheric composition, and potential signs of life, making it one of the best candidate locations in the Eden Project."

Ending
[The alarm stops. A spacecraft engine ignites with a deep mechanical roar that grows from the background to fill the soundstage; the low synthesizer returns beneath it and fades on an unresolved note.]
```

## Full example: TA2A — Multi-character fantasy battle dialogue

```text
Input references
@Audio1: female protagonist voice timbre — Lux (clear, bright, crystalline)
@Audio2: male antagonist voice timbre — Sylas (raspy, low, gravelly)
@Audio3: male heroic voice timbre — Garen (deep, powerful, booming)

Scene and atmosphere
Low, somber strings and distant war drums underscore a ruined stone courtyard. Cold wind moans through broken arches. The music remains restrained beneath dialogue and swells only during attacks.

Characters and dialogue
[Heavy iron chains scrape harshly across stone in the foreground, then shackles strike with a sharp, echoing "CLANG."]

Sylas (raspy, low, gravelly male voice, rough and menacing, like sand grinding over rusted iron, voiced by <<TGT_SPK2>>) speaks in a cold, taunting tone: "Lux. Did your brother send you to finish the job?"

Lux (clear, bright young female voice, resonant with a crystalline timbre, voiced by <<TGT_SPK1>>) says firmly yet pleadingly: "Sylas, it's not too late to stop."

[A bright chime of gathering light energy rings like crystal near breaking. The strings rise as the energy builds.]

[A beam fires with a sharp "shhhk!" and strikes the chains in a dazzling "CLANG!!", followed immediately by a thunderous "BOOM!" Debris scatters and the shockwave briefly overwhelms the music.]

Garen (deep, powerful, booming male voice, heroic and resolute, voiced by <<TGT_SPK3>>) roars: "DEMACIA!!"

[A massive spinning blade rushes forward with repeated "whoom, whoom, whoom" passes across the foreground.]

Sylas (voiced by <<TGT_SPK2>>) snarls through gritted teeth: "Demacia's dog—"

Lux (voiced by <<TGT_SPK1>>) shouts urgently, throwing herself between them: "Stop! Both of you, STOP!"

[A golden shield blooms with a resonant, sustained "diiing—". All music and battle noise cut out, leaving only cold wind and three characters breathing heavily.]

Lux (voiced by <<TGT_SPK1>>) speaks softly, almost carried off by the wind: "He's our brother… he once was."

Ending
[A sword slides into its sheath; loose chains settle against stone. A solitary clarinet enters over the wind and slowly fades into silence.]
```

## Full example: T2A — User-requested timestamp control

Use this format only when the user explicitly asks for second-level timing.

```text
Scene and atmosphere
A quiet evening room. Soft ambient room tone. Occasional distant traffic. The air is still and heavy with unspoken tension.

Characters and dialogue
Ryan (young adult male, warm voice) calls out anxiously, slightly out of breath: "[5.5s:8.0s] Maya! Wait—you're really leaving tonight?"

Maya (young adult female, soft voice) answers softly, forcing herself to stay composed: "[8.5s:11.5s] I have to. I've spent years chasing this… I can't walk away now."
```

## Ideal use cases

- **Audiobooks**: T2A and TA2A eliminate the need for human recording or manual SFX. Supports science fiction, daily talk, adventure, and inner monologue at roughly 1/10 the cost of human recording.
- **Video dubbing**: Generate character voices from text descriptions or reference audio. Human voice + SFX + background music in a single pass.
- **Gaming**: Generate character voices and environmental sound effects for immersive player experiences.
- **Podcast and radio drama**: Multi-character dialogue with full sound design from a single prompt.
- **Language learning content**: Generate audio in multiple languages, with per-sentence timestamp guidance when the user explicitly requests second-level timing.

## What makes Seed Audio 1.0 different from normal TTS

| Feature | Audio 1.0 | Normal TTS |
|---|---|---|
| Text-to-Speech | ✅ | ✅ |
| Voice Cloning | ✅ | ✅ |
| Text Prompt to Audio (T2A) — describe voice, atmosphere, BGM, SFX in free text | ✅ | ❌ |
| Text Prompt + Audio to Audio (TA2A) — reference audio + text prompt for voice/emotion reference | ✅ | ❌ |
| Multimodal soundscape (dialogue + music + SFX + ambience in one pass) | ✅ | ❌ |
| Optional prompting-guide time control per sentence | ✅ | ❌ |
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
