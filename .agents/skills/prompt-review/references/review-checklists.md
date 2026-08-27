# Review Checklists

Consolidated, actionable validation checklists for every prompt-writing skill in the
repo. Each section is self-contained — pass the relevant section to the review
sub-agent along with the prompt text.

## Table of contents

- [Universal — all prompts](#universal--all-prompts)
- [Seedance 2.5](#seedance-25)
- [Seedance 2.0](#seedance-20)
- [Seedance VFX (video-to-video)](#seedance-vfx-video-to-video)
- [Seedance 2.5 edit (video-to-video)](#seedance-25-edit-video-to-video)
- [Seedance Filipino dialogue](#seedance-filipino-dialogue)
- [Seed Audio](#seed-audio)
- [Seedream image generation](#seedream-image-generation)
- [Seedream character sheet](#seedream-character-sheet)
- [Seedream location asset](#seedream-location-asset)
- [Seedream storyboard](#seedream-storyboard)
- [Seedance music video](#seedance-music-video)

---

## Universal — all prompts

These apply to every prompt regardless of model or skill. Check every prompt against
these before checking the type-specific checklist.

1. **Assets first.** Every character, location, and prop referenced in the prompt is
   named, versioned, and locked. Descriptors are copied word for word — never
   summarized, shortened, or implied.

2. **Say what you want, not what you avoid.** Prohibitions name and summon the thing
   they forbid. The prompt uses positive, specific instructions instead of
   negative-only constraints.

3. **Direct, don't describe.** The prompt contains scene events, motives, goals,
   obstacles, and tactics — not just static visual descriptions. If it reads like a
   description with no event or intent, it fails this check.

4. **Watermark.** If the prompt specifies watermark behavior, it must be `false`
   unless the user explicitly requested the AIGC watermark.

5. **Duration right-sizing.** The prompt does not pad a scene to fill a maximum
   duration. Each scene is set to its natural length (4-30s for Seedance 2.5, up to
   15s for Seedance 2.0).

6. **Parameters in the API, not the prompt.** Generation parameters (duration,
   resolution, aspect ratio) are not embedded in the prompt text unless the skill's
   structure explicitly includes them. They belong in the API call.

7. **Prompt snapshot location.** The prompt is saved beside the media asset it
   produced, using the `prompt_` prefix convention. It is not duplicated in shot
   folders, scene folders, or any other location.

8. **No duplicate action descriptions.** The same action is not described twice in
   the same prompt. Each beat appears once.

9. **No generic adjectives.** The prompt avoids "beautiful," "stunning," "amazing,"
   "cinematic" as standalone descriptors. It uses concrete, specific, observable
   language instead.

10. **@tag references.** All project Elements (characters, locations, props) are
    referenced by their locked `@tag` and bound to the correct `@Image N` / `@Video N`
    / `@Audio N` index.

---

## Seedance 2.5

Source skill: `seedance-prompt-25`

### Formula check

1. **Subject + Action present.** The prompt contains at minimum a clear subject and a
   primary action or event. These are the only required parts.

2. **Six-part formula.** The prompt follows: Subject + Action/Event + Scene/Environment
   (optional) + Visual Style (optional) + Camera Movement/Cut (optional) + Audio
   (optional). Parts are in this order.

3. **No double-description.** The same action is not described in multiple sections.

4. **Action granularity.** The Action slot describes motion at the body-part
   level (hands, arms, legs, head, shoulders, back, hips, feet) with range,
   speed, and force, grounded in weight, balance, momentum, and contact — not
   as bare verbs. High-burst, large-dynamic actions are avoided unless the
   shot requires them.

### Reference materials

5. **Material mapping in prompt.** Every reference material is mapped directly in the
   prompt text — the model never has to guess which asset belongs to which
   person/prop/scene.

6. **Individual naming.** Each subject is named and bound individually. The prompt
   does not use lazy groupings like "@Images 1 through 4 define four characters."

7. **Grouped by type.** References are organized as [Characters], [Props], [Scenes],
   [Motion and Audio] sections.

8. **Centralized profiles.** Important subjects have a centralized profile block with
   stable attributes that is referenced in each scene.

9. **Per-scene selection.** Each scene names only the references it uses — not all
   materials at once.

10. **Exclusion phrasing.** "Do not use..." exclusions appear only when leakage is
   genuinely possible. Not as a generic negative-prompt dump.

11. **Multiple views.** If multiple images define one subject, the prompt explicitly
    states "The output must contain only one [subject] throughout."

12. **Video reference inheritance.** If inheriting from a reference video, only the
    attributes to inherit are stated. The prompt does not restate every action from
    the reference (which can conflict).

13. **Control-only references.** Control-only images are preferably translated to text
    and omitted. If kept, they are labeled as control-only with explicit extraction
    instructions.

14. **Reference count limits.** ≤ 30 images, ≤ 10 videos, ≤ 10 audio. Recommended:
    1-8 image subjects, 1-5 video subjects (5-10s each), only directly relevant audio.

### Scene staging

15. **Stage structure.** The story is divided into consecutive stages. Each stage has
    ONE primary state change and a clear end state.

16. **Natural duration.** Each scene is generated at its natural duration (4-30s),
    not padded to 30s. 30s single-pass or extension is the exception, not the default.

17. **Timestamp ranges.** Time ranges are consecutive and non-overlapping. They are
    treated as a time budget, not precise edit points.

18. **No impossible frequencies.** The prompt does not demand impossible action
    densities (e.g., "complete three actions in one second").

### Audio syntax

19. **Audio bracket syntax.** Dialogue in `{}`, music in `()`, SFX in `<>`, subtitles
    in `【】`. All audio content uses the correct bracket type.

20. **Dialogue language reinforcement.** Non-Chinese dialogue includes: Dialogue
    Language + Regional Variety/Accent + Delivery Style + Speaker + `{dialogue}`.

21. **Same dialogue in both prompts.** If audio-first pipeline is used, the exact
    dialogue text in the Seed Audio prompt matches the `{curly brace}` text in the
    Seedance prompt. No paraphrasing, reordering, or omitted lines.

### Emotional direction

22. **Visible/audible cues.** Abstract emotions are paired with directly visible or
    audible cues (eye movement, brow tension, mouth movement, breathing, gaze, hand
    movement). 2-4 clear cues per emotional transition.

23. **No bare emotion words.** The prompt does not rely solely on emotion labels like
    "very sad" or "extremely angry" without physical externalization.

### Camera language

24. **One camera movement per clip.** The prompt specifies one camera movement and
    states which subject the camera follows, where it begins, and where it ends.

25. **Uncommon cinematography terms.** If used, they follow the format:
    Term + Target Subject + Visual Change + Foreground/Background Relationship +
    Direction or Speed.

### Spatial continuity

26. **Spatial map present.** Movement-heavy scenes include: Start positions,
    Travel axis, Subject order, Boundary behavior, End state, Forbidden transitions.

27. **Physical locations.** Uses physical locations and ordered states, not relative
    verbs alone.

28. **Invariants repeated.** Critical spatial invariants are repeated in every
    shot/stage since every cut can reset relationships.

### Parameter auto-lock

29. **Editing task.** Aspect ratio and duration are not set (locked to input). Edit
    scope, target quantity, and content to preserve are defined.

30. **First/last-frame task.** Aspect ratio locks to first image. First and last
    frames share the same aspect ratio.

31. **Extension task.** Aspect ratio is not set (locked to input). Duration can be
    set. Boundary image, motion trend, and audio continuity are checked.

### Preflight review (15-point)

32. **Subject & action** clearly stated.
33. **Reference roles**: every reference states what to use and what not to use.
34. **Subject binding**: every distinct character/product/prop named and bound to a
    reference.
35. **Scene selection**: references selected by scene, not forced to appear all at once.
36. **Stage structure**: each stage has only one primary change and a clear end state.
37. **Consistency**: character count, clothing, prop ownership, spatial relationships
    stay consistent.
38. **Editing master**: for editing, sole editing master, edit scope, target quantity,
    content to preserve defined.
39. **Emotion & camera**: abstract emotions and cinematography terms paired with
    visible/audible cues.
40. **First/last frames**: one role per image; first and last share aspect ratio.
41. **Storyboards & blockouts**: storyboard states which structure to inherit;
    blockouts identify coarse vs fine.
42. **Auto-lock rules**: editing, first/last-frame, and extension follow locked
    aspect-ratio and duration rules.
43. **Extension boundary**: boundary image, motion trend, and audio continuity checked.
44. **One-click video**: material roles, image order, motion amount, editing style,
    and audio defined.
45. **Seamless transitions**: two videos' roles, trigger action, transition process,
    and arrival state defined.

46. **Speech fits duration.** For dialogue-driven shots, estimate speech length
    ≈ spoken words / 2.2 (conversational) to seconds. If the `{}` script reads
    far shorter than the API `duration`, the prompt must explicitly direct the
    gap (pauses, hesitations, action beats); otherwise right-size the duration.

---

## Seedance 2.5 edit (video-to-video)

Source skills: `seedance-prompt-25` (editing) + `seedance-vfx-prompt` (2.5 section).

Apply "Universal — all prompts" first, then this section. Mark N/A any item
whose feature is absent (no references → skip material mapping).

### Editing task

1. `[Edit Goal] Edit @Video 1 …` present and one-sentence; submit with
   `omni_reference_task_type="edit"` (2.5 values: `auto | reference | edit |
   extend` — `edit_video` is 2.0-only and is rejected).
2. `[Source Video Role]` declares `@Video 1` as the sole editing master and
   lists what it defines (subjects, scene, actions, camera, event order).
3. `[Target Material Role]` present iff references are used: each `@Image N`
   mapped to one target; "Do not use its background/people" present;
   single-person sheets directed to use the close-up panel only.
4. `[Edit Scope]` states what changes and, for what must not change, a positive
   "exactly one <subject> — never a second or duplicated copy" guard.
5. `[Content to Preserve]` lists identity/motion/timing/camera/lighting to keep.

### Preservation locks (only where MUST PRESERVE says so)

6. Quantity: "Exactly one <subject> in frame — never a second or duplicated copy."
7. Non-reaction (when the subject must not react): "…facial expression, gaze,
   and gestures remain exactly as in @Video 1; only <the changed thing>
   re-animates."
8. Grounding: "…naturally grounded — no cut-out edge, no halo; rim light
   matches the key direction."
9. Face protection (any preserved face): "real human skin with pores and
   catchlights — never waxy, smoothed, or warped."

### Audio / lip-sync

10. New dialogue in `{}` with language + regional variety + delivery style +
    speaker; lips directed to the NEW words. CJK punctuation: `……` not `——`.
11. Same-content contract (language swap): target `{}` line is the source line
    translated, no paraphrase/omission.
12. Diegetic audio only; SFX in `<>`, music in `()`; no non-diegetic score.

### Camera (only when the edit intentionally re-stages the camera)

13. ≤ 2 camera moves in one take; each move numeric-anchored ("At about 0:02…")
    plus a semantic cue; uncommon terms expanded (orbit: direction + parallax).
    See also general Seedance 2.5 item 24 ("One camera movement per clip") —
    two moves apply only when re-staging is intentional.
14. Camera-move items are N/A when the edit must preserve the source camera.

### Change contract

15. Flag only breakage of MUST PRESERVE or a quality defect in the change
    description — never an item the user explicitly asked to change.

---

## Seedance 2.0

Source skill: `seedance-prompt-20`

### Structure

1. **Section order.** Prompt assembles in this order: Asset preparation → Subject
   definitions → Prompt (with task type) → Shot 1/2/3 → Quality and constraints.

2. **Asset preparation first.** References are labeled with `@Image N`, `@Video N`,
   `@Audio N` (sequential, space separator) before any prompt body.

3. **Reference limits.** ≤ 9 images, ≤ 3 videos, ≤ 3 audio (15 total). Audio cannot
   be sent alone. Combined video duration ≤ 15s, combined audio duration ≤ 15s.

### Subject definitions

4. **Define keyword.** Uses `Define` keyword with 2-3 stable static features
   (clothing, hairstyle, appearance, category). Static only — no mutable attributes
   like expression or pose.

5. **Label reuse.** The same `@Image N` / `@Video N` label is reused in every shot.

6. **No Asset IDs.** Uses `@Image 1` / `@Video 1` format, not Asset IDs.

### Reference classification

7. **Classification.** Each reference is classified as: Visible identity, Visible
   environment, Motion/camera reference, or Control-only reference.

8. **Control-only handling.** Control-only images are preferably translated to text.
   If kept, labeled as control-only with extraction instructions and visual
   reproduction prohibition.

9. **Face restriction.** No direct uploads of real human faces. Uses model outputs,
   preset digital characters, or authorized real-person assets.

### Task type declaration

10. **Task type declared.** One of: Multimodal Reference | Video Editing | Video
    Extension | Combined Tasks.

11. **Edit/extend phrasing.** For edit/extend: uses `@Video 1` directly ("Strictly
    edit @Video 1..."). Does NOT write "Reference @Video 1" (which triggers
    multimodal reference mode).

### Shots

12. **Timeline storyboard.** Uses `Shot 1 / Shot 2 / Shot 3` format. Each shot
    covers one coherent unit of action.

13. **Per-shot references repeated.** Every shot repeats applicable `@Image N`,
    `@Video N`, `@Audio N` references inline.

14. **Per-shot description order.** (1) Camera movement/transition, (2) Subject
    actions/expressions, (3) Position/spatial changes, (4) Lighting & color tone,
    (5) Audio.

15. **One camera movement per shot.** Does not combine push, pull, pan, tilt in one
    shot.

16. **Complexity budget.** At most 3 major action beats or 4 tightly related shots
    for 15s generation.

17. **Action detail.** Body-part level detail (hands, legs, head, shoulders, back)
    with range, speed, force.

18. **Motion preference.** Prefers slow, gentle, continuous motion. Avoids
    high-burst, large-dynamic actions.

19. **Emotion externalization.** Emotions are externalized as physical details,
    never bare labels.

20. **Dialogue format.** Spoken text in `{curly braces}` or quotes for lip-sync.
    Multi-speaker format with speaker labels.

### Timing

21. **Duration via API.** Total video length set with API `duration` parameter, not
    timecodes in text.

22. **Natural pacing.** The model paces multi-shot generation naturally. Second-level
    timing only when user explicitly requests it.

23. **Timestamp format.** If used: concise ranges (`Shot 1 (0-4s):`), contiguous,
    non-overlapping, consistent with API duration.

### Spatial continuity

24. **Spatial map present.** Same 6-field format as Seedance 2.5 (Start, Travel axis,
    Subject order, Boundary behavior, End, Forbidden transitions).

25. **Physical locations.** Uses physical locations and ordered states, not relative
    verbs alone.

### Quality and constraints

26. **Inline constraints.** All constraints go inline in the text prompt (no separate
    negative_prompt field).

27. **Prioritized constraints.** Prioritizes constraints instead of accumulating a
    long blacklist.

28. **Positive phrasing.** States required physical behavior positively. Repeats only
    the few exclusions that prevent expensive failure.

### Preflight review (6-point)

29. **Parameter agreement.** Prompt and API resolution, duration, ratio, and audio
    setting agree.

30. **Reference indexing.** Every reference is indexed, classified, and bound only
    where intended.

31. **Spatial fields.** Start, travel axis, subject order, boundary behavior, and end
    state are explicit.

32. **No contradictions.** No contradictory instructions (e.g., "single continuous
    shot" plus several cuts; "no powers" plus an emitting aura reference).

33. **Focus.** Prompt is focused; repetition compressed before removing critical
    spatial state.

34. **Beats fit duration.** Requested beats fit the duration or the scene is split.

### Revision contract (if revising)

35. **Locked decisions carried.** Approved identity, action, camera, environment,
    audio, boundary behavior carried into revised prompt.

36. **One delta.** Only one of {prompt wording, reference bundle, motion design}
    changed per retry.

37. **Acceptance criteria.** Observable conditions for the next take to pass are
    stated.

38. **Known rejections.** Behaviors from earlier takes that must not return are listed.

---

## Seedance VFX (video-to-video)

Source skill: `seedance-vfx-prompt`

### Core principle

1. **Source clip is the lock.** The prompt preserves what to keep (subject identity,
   performance, camera motion) and describes only what should change. It does not
   re-describe the entire scene from scratch.

### Asset preparation

2. **@Video 1 is source.** Source clip is always `@Video 1`. Uses "Strictly edit
   @Video 1" (NOT "Reference @Video 1").

3. **Source described.** Subject, action, camera motion, and duration of source clip
   are described in asset preparation.

4. **Source inspected.** The source clip was inspected before writing (duration, fps,
   aspect ratio probed). Prompt is built from footage, not user's one-line summary.

5. **Texture references labeled.** Texture references say "texture only" — "appearance
   and fur/skin texture reference only; ignore the photo's background and lighting."

### Subject definitions

6. **Define keyword.** Uses `Define` with 2-3 core static features. Bound as
   `<Label>@Video 1`.

### Locks (preservation)

7. **Locks declared.** Identity (face, body, costume, props), Performance (gait,
   gestures, expressions, timing), Camera (motion type, framing, lens, bob),
   Continuity are locked with `<Label>@Video 1`.

### Change

8. **Change named with timestamp.** The exact change and when it happens are stated
   (`At 0:NN` for localized changes). Global changes at `0:00`.

9. **Subject reaction.** Whether the subject reacts or does not react is stated.

### New world

10. **Full description.** Replacement/added environment/element is fully described.

### Lighting (embedded)

11. **Lighting lives in the world.** Light sources are physically present in the new
    world. Not described as a layer pasted on top.

12. **No generic lighting terms.** Does not say "cinematic lighting" or "dramatic
    lighting" alone — names the source.

13. **Light on subject.** Where light falls on subject (direction, color, intensity)
    is described.

14. **Light-environment interaction.** How light interacts with environment
    (volumetric mist, reflections, shadows) is described.

15. **Integration fork decided.** Either "preserve subject's lighting; grade only new
    elements" (default) OR "relight the whole frame under one look" is explicitly
    chosen.

16. **"Looks pasted in" recipe applied.** Light (direction, softness, shadow density),
    environmental bounce, optics & atmosphere (lens, micro-contrast, haze, DOF, grain),
    edges & grounding (no hard cut-out, no halos, matched rims) are addressed.

### Space

17. **Layered space.** Foreground (parallax elements), Midground (subject + primary
    environment), Background (atmosphere and scale) are described.

### Timing

18. **Sequential timestamps.** When each event triggers and how it progresses.

19. **Timed camera moves dual-anchored.** Semantic anchor ("At the line '<exact
    words>,' the camera <move>") AND numeric anchor ("At about <T> seconds...").

20. **Zoom type specified.** Crash zoom = fast hard punch-in. Smooth push-in = slow
    steady glide.

21. **Tail after trigger.** Enough tail (~2-3s) after trigger for payoff. If clip is
    short, zoom fires on first word.

22. **Reveal pull-back.** If used: opens tight on added element, moves outward to land
    on real plate, demands 100% match of source composition at landing.

23. **Lip-sync window checked.** If lip-sync preservation: line quoted verbatim,
    anchored twice (in change/action and in audio), `SFX and source dialogue only`
    requested, "lips matching the source exactly" in Locks, line fits surviving
    dialogue window.

### Audio

24. **Diegetic only.** Only sound that physically exists in the new world. Preserves
    source-clip diegetic sounds that still make sense.

25. **No non-diegetic audio.** Does not request background music, score, or voiceover
    unless part of source footage.

### Quality and constraints

26. **NON-IP.** No recognizable real persons, no copyrighted characters, no brand logos.

27. **Face protection.** "Real human skin with pores, stubble, and catchlights — never
    waxy, smoothed, or warped."

28. **4K for faces.** 4K resolution is default for any VFX shot involving faces,
    lip-sync, or fine detail.

### Creature/element integration (if applicable)

29. **Photoreal demanded.** "Fully photoreal, real fur with depth and individual
    strands, true anatomy, never CG, plastic, or cartoonish."

30. **Tied into plate.** Same sun direction, real soft-edged contact shadow, same hazy
    atmosphere.

31. **Scale explicit.** Scale is explicit for giant creatures.

32. **Texture fallback.** If still reads CG: second input — reference photo of real
    animal as texture-only `@Image N`.

33. **Species behavior.** Behavior matches the species (sloth slow, chimp twitchy,
    snake coils and forked tongue, snakes don't blink).

34. **Living micro-movements.** For static creature holds: slow blink, jaw shift,
    steady breath.

### Duration discipline

35. **Source runtime default.** Defaults to source clip's exact runtime.

36. **Recomputed timing.** If runtime changed, numeric zoom timing is recomputed.

37. **Prepended-intro budget.** `total runtime − intro length = surviving window for
    source performance`. If source take longer than surviving window, one of three
    resolutions offered (extend total, start source earlier, accept truncation).

### Iteration discipline

38. **Only named change.** Only the named thing changes; rest of prompt stays stable.

39. **Refine via edit.** When refining a generated still/frame, edits the chosen result
    (passes it back as base) and fixes only what is off.

### Voice

40. **No generic adjectives.** No "beautiful," "stunning," "amazing," "cinematic."

41. **Concrete language.** Names exact materials, behaviors, scale, lenses, angles,
    moves. Uses texture words. Does not inflate, soften, or explain what things
    "represent."

---

## Seedance Filipino dialogue

Source skill: `seedance-prompt-25-filipino`

Use as an additional checklist alongside Seedance 2.5 when the scene contains Tagalog,
Filipino, or Taglish dialogue.

### Vocabulary simplification

1. **Tier 1-2 words.** Dialogue uses Tier 1 (easy: 1-3 syllables, penultimate stress,
   common) and Tier 2 (moderate: 3-4 syllables, penultimate stress, common) words
   predominantly.

2. **Short sentences.** Sentences are 5-8 words; split if >10.

3. **Contractions used.** `di`, `pwede`, `ganun`, `ayos` used where natural.

4. **No literary Filipino.** Deep/literary words replaced with modern equivalents.

5. **Modern Manila Taglish.** Preferred for urban/contemporary settings.

6. **Natural, not dumbed-down.** Simplification keeps it natural.

### Phonetic annotation (if used)

7. **Stress markers correct.** Penultimate stress = default (unwritten). Final
   syllable stressed = **bold**. Penultimate + glottal stop = trailing `'`. Final
   stressed + glottal stop = both.

8. **Glottal stops marked.** Word-final (trailing apostrophe `gala'`), morpheme-boundary
   (hyphen `mag-uwî`).

9. **Notation format.** UPPERCASE+hyphen in standalone pronunciation blocks and Seed
   Audio prompts (plain text). Bold+middle-dot for inline annotations in Seedance
   prompts (markdown).

### Intonation direction

10. **Baseline pitch.** Very slight pitch variation; level 2 baseline, slight rise to
    level 3 on stressed syllables, return to level 2.

11. **Sentence-type contours.** Declarative (fall), yes/no question (rise), tag question
    (rise on tag), command (level/flat, NOT falling like English), non-final phrase
    (slight rise/suspended).

12. **Plain-language arc.** Intonation arc described in plain language in the prompt.

### Taglish code-switching

13. **English words with Filipino phonology.** No schwa, full vowel articulation,
    penultimate stress default, unreleased final consonants or glottal stop.

14. **F/V and TH substitution.** "F"/"V" often bilabial "p"/"b". "TH" often "d"/"t".

15. **Discourse markers.** `po`, `opo`, `ba`, `eh`, `na`, `na lang`, `ha?`, `naman`,
    `kasi`, `daw`/`raw` included where natural.

### Speech register

16. **Register consistent.** Formal (marangal: `po`, `opo`, full words), Casual
    (pang-araw-araw: no `po`/`opo`, contractions), or Taglish (informal: English words
    with Filipino phonology, optional `po`). Not mixed inconsistently.

17. **Register pitfalls avoided.** `opo` replaces `oo` (don't say `oo po`). `po`
    placement after modified word. Contractions signal casualness.

### Common pronunciation pitfalls

18. **Mabuhay** — stress on second syllable (ma-**BU**-hay), not first.
19. **Salamat** — stress on second syllable (sa-**LA**-mat).
20. **Hindi** — stress on second syllable (hi-**NDI**), glottal stop on final.
21. **Oo** — two syllables with glottal stop, stress on first syllable (**O**-'o).
22. **Bababa** — stress on second syllable (ba-**BA**-ba).
23. **Maynila** — stress on second syllable (Ma-**NI**-la).
24. **Ng at word start** — single velar nasal [ŋ], not "n-g".
25. **Ts cluster** — affricate [tʃ], like English "ch".

### Audio-first pipeline (if used)

26. **Vocabulary simplified first.** Before generating Seed Audio.
27. **Dialogue language set.** "Manila Tagalog" or "Taglish" stated.
28. **Audio verified.** Stress, glottal stops, intonation, duration, Taglish phonology
    checked after generation.
29. **Same dialogue in both prompts.** Seed Audio prompt and Seedance `{}` dialogue
    match verbatim.
30. **Timestamps aligned.** Shot timestamps in Seedance prompt match actual audio
    timing.
31. **Audio as reference_audio.** Passed as `@Audio N` in Seedance task.
32. **Manifest updated.** Audio path, hash, duration, timestamp mapping recorded in
    `shot.md`.

---

## Seed Audio

Source skill: `seed-audio-prompt`

### Full-soundscape ingredients

1. **Environment.** Location, weather, context, acoustic space described.
2. **Background music and SFX.** Dramatic role, style, instruments, rhythm, mood,
   volume, opening intensity described.
3. **Character actions/appearance.** Included when they affect performance.
4. **Character voice profile.** Age, gender, accent, emotion, tone, speed, timbre for
   each character.
5. **Exact dialogue.** In double quotes, with delivery note before the quote.

### Arrangement order

6. **Input references** (only when reference audio included).
7. **Opening environment, ambience, music.**
8. **Dialogue, actions, SFX** in chronological order.
9. **Ending behavior.** Resolve, fade, sustain, or cut.
10. **Creative/quality constraints** (only when user supplies them).

### Input references

11. **Reference count.** ≤ 3 reference audio (TA2A) OR exactly 1 reference image
    (reference-image mode). Mutually exclusive.

12. **Per-clip limits.** ≤ 30s, ≤ 10 MB. Formats: WAV, MP3, PCM, OGG_OPUS.

13. **Single purpose per clip.** Each clip serves exactly one purpose: voice timbre
    cloning, emotion reference, or SFX reference.

14. **TA2A mapping.** `<<TGT_SPK1>>`, `<<TGT_SPK2>>`, `<<TGT_SPK3>>` mapped to ordered
    entries in `references[]`, labeled `@Audio1`, `@Audio2`, `@Audio3`.

15. **No references section.** When no references, the input references section is
    omitted entirely.

### Environment

16. **Acoustic quality specific.** "Hallway reverb," "stone corridor echo" — not just
    "echoey room."

17. **Layers described.** Foreground, midground, background.

18. **Evolution.** How environment evolves over time.

### Background music

19. **Dramatic role.** Underscore, tension bed, transition, reveal, celebration, outro.

20. **Style/genre/instruments.** Concrete musical language, not generic phrases.

21. **Dynamic arc.** How it begins, swells, thins, changes instrumentation, stops.

22. **Relationship to speech/effects.** When music ducks, effects dominate, ambience
    remains distant.

23. **Ending.** Clean stop, held unresolved note, crossfade, gradual fade.

### Ambience

24. **Persistent bed.** Separate from one-off effects.

25. **Distance/direction/room tone.** Echo, reverb, gradual evolution described.

26. **Subordinate to dialogue.** Unless scene requires otherwise.

### Sound effects

27. **Source/action/material/acoustic character.** Spatial position described.

28. **Positioned relative to actions/dialogue.**

29. **Evolution/decay.** Described when important.

30. **Onomatopoeia in quotes.** "ring-a-ling," "zzzip," "clack" — used to clarify
    texture, not as a substitute for describing the sound.

31. **Foreground/midground/background.** Identified when mix could be ambiguous.

### Character voice profiles

32. **T2A format.** `Name (age, gender, accent, voice timbre, emotional tone, delivery
    style) says: "dialogue text"`

33. **TA2A format.** `Name (voice description, voiced by <<TGT_SPKN>>) says [delivery
    note]: "dialogue text"`

34. **Voice contrast.** Each voice contrasts through pitch, timbre, accent, pacing,
    emotional baseline, or performance style.

### Dialogue

35. **Double quotes.** Spoken text in double quotes.

36. **Delivery note before quote.**

37. **Physical actions included.** When they affect delivery or generate sound.

38. **Multi-character chronological.** Alternates chronologically; actions/music/SFX
    between lines where listeners should hear them.

39. **Explicit attribution.** No unlabeled blocks of alternating quotes.

40. **Non-speech in brackets.** Ambient descriptions and non-speech sounds wrapped in
    square brackets.

41. **Prompt language = script language.** The prompt and the dialogue script are in
    the same language.

### Scene transitions

42. **Transition block format.** Audio state A → Transition trigger → Transition
    behavior → Audio state B → Forbidden carryover. All five fields present.

### Timestamp control

43. **Format.** `[start_time:end_time]` immediately before dialogue, in seconds with
    decimal precision.

44. **Used only when precision matters.** Omitted when event-relative cues suffice.

### Validation

45. **Character limit.** `text_prompt` ≤ 3000 characters.

46. **Duration limit.** Generated audio ≤ 120 seconds per call.

47. **No API concerns in prompt.** Does not insert "Max duration: 120 seconds" into the
    prompt — that is an API concern.

48. **Long requests split.** If requested generation > 120s, split before sending.

### Audio-video alignment (when used with Seedance)

49. **Same dialogue text in both prompts.** Exact lines match between Seed Audio
    `text_prompt` and Seedance `{curly braces}`.

50. **Audio duration ≤ video duration.**

51. **Shot timestamps align to audio.** Seedance shot time ranges match actual audio
    timing.

52. **Audio as reference_audio.** Passed to Seedance task as `reference_audio`.

---

## Seedream image generation

Source skill: `seedream-prompt`

### Structure

1. **Section order.** Subject > Setting > Style > Lighting > Composition > Technical.
   Order matters — earlier concepts carry more weight.

2. **Most important subject first.** The primary subject appears before secondary
   subjects.

3. **Reference labeling.** `@Image 1`, `@Image 2`, ... sequential numbering with `@`.

4. **Reference list is inventory.** Each reference is also bound again where it affects
   output — not just listed in the reference section.

5. **Exact tokens.** Uses exact `@Image N` token every time. Does not drop `@` or
   replace with ambiguous phrase.

### Reference limits

6. **Seedream 5.0 Pro.** ≤ 10 input images.
7. **Lite.** Refs + outputs ≤ 15.

### Task type

8. **Correct task type.** T2I, I2I, Image Editing, Sequential Generation, or
   Infographic/Information Visualization.

9. **Sequential generation.** NOT supported on 5.0 Pro. Requires Lite/4.5/4.0.

### Subject

10. **2-3 stable attributes.** Each subject defined with 2-3 stable attributes.

11. **Multi-subject priority order.** Listed in order of visual priority.

### Avoiding the AI look

12. **Concrete photorealism signals.** Not just "realistic" — uses film stocks, lens
    characteristics, camera bodies, photographic genres.

13. **Lighting direction specified.** Direction, quality, color temperature, falloff,
    environmental contamination described. No flat/shadowless lighting.

14. **Skin and texture imperfections.** Visible pores, flyaway hair, slight asymmetry,
    fabric texture included for photorealistic output.

15. **Prompt order carries weight.** Subject > Setting > Style > Lighting >
    Composition > Constraints. Most important visual directives placed high.

16. **Negative constraints aggressive.** No plastic skin, no over-smoothing, no waxy
    textures, no CG render look, no unnatural symmetry.

17. **No over-description.** Observed detail over value judgment. "Windswept dark hair"
    not "beautiful stunning gorgeous hair."

18. **prompt_optimization.** Uses `standard` for photorealistic final output. `fast`
    only for drafts.

### Text in image

19. **Exact text in double quotes.** Text to render is in double quotes.

20. **Surface described.** The surface the text is on is described.

21. **14 languages supported.** Small text may still be unstable — noted if used.

### Constraints

22. **Inline only.** All constraints in the text prompt. No separate `negative_prompt`.

23. **Quality directives and negative constraints.** Only those that materially affect
    output.

### Prompt length

24. **30-100 words.** For standard images. Infographics and complex scenes can go
    longer but stay focused.

---

## Seedream character sheet

Source skill: `seedream-character-sheet`

### Layout

1. **Three-panel default.** Back full-body, front full-body, face close-up. Unless user
   explicitly asks for more panels.

2. **Neutral gray background.** Default studio background — neutral gray, never
   scene-specific. Deviates only if user explicitly wants stylized/filmic sheet
   background.

3. **Panel order.** Back full-body first, front full-body second, frontal close-up
   third.

### Subject

4. **Reference binding.** Each reference is bound inline.

5. **Required elements.** Age, ethnicity/cultural identity, 2-4 stable facial traits,
   hair and headwear, costume, key accessories.

6. **Same person statement.** Explicitly states it is the same person in all panels.

7. **No held props.** Nothing held, carried, aimed, or operated appears in the sheet;
   those are authored as separate `prop_` sheets. Scene-variant wearables (e.g.
   sunglasses worn only in some scenes) are also excluded and made props instead.
   Only always-worn outfit elements (hat, helmet, eyewear, jewelry) may appear.

### Setting

8. **Default background.** Neutral gray seamless, no props, no held objects, no
   furniture, no environmental clutter.

### Lighting

9. **Neutral, not scene-specific.** Soft, even studio light, flat fill, neutral
   white balance, no mood, no dramatic shadows, no hotspots, no blown highlights.
   Lighting never changes to match the character's scene or story mood.

10. **Consistent across panels.** Lighting is identical across all three panels.

### Composition

11. **Three panels only.** No extra panels.

12. **Same identity.** Same character identity across all panels.

13. **Readable silhouette.** Costume silhouette readable in body panels.

14. **Face authority.** Close-up panel is the face authority.

### Constraints

15. **Common negatives.** No extra panels, no profile panel, no 3/4 panel, no props in
    hands, no held objects/weapons, no background variation, no scene lighting or
    color cast, no distorted hands, no extra fingers, no watermark.

### Workflow

16. **Cleanup check.** Body panels inspected for extra readable faces after generation.
    If found, `seedream-character-sheet-cleanup` invoked.

17. **Element saved.** Saved under `elements/<character-id>/`.

18. **Selected variant.** Approved filename recorded as `selected_variant` in
    `character.md`.

---

## Seedream location asset

Source skill: `seedream-location-asset`

### Location

1. **Place described.** Interior/exterior, function, scale, spatial mood, core
   architectural identity.

### Era and world rules

2. **Historical period.** Stated if relevant.

3. **Geography/climate.** Stated if relevant.

4. **Technology limitations.** Stated if relevant.

5. **Realism constraints.** Explicitly excludes modern intrusions if realism matters.

### Set dressing and objects

6. **1-3 hero set pieces.** Key defining objects.

7. **Practical objects.** Objects that imply use.

8. **Material realism and wear.** Surfaces show wear and use.

9. **Depth cues.** Foreground/midground/background.

10. **Lived in.** Not empty — feels inhabited.

### Style

11. **2-4 strong anchors.** From: photorealistic, cinematic, naturalistic editorial
    reference, grounded realism, film still, period-authentic.

### Lighting and atmosphere

12. **Practical key source.** Where the light comes from physically.

13. **Time of day / weather.**

14. **Shadow falloff.**

15. **Haze / dust / smoke / moisture.** Atmospheric particles.

16. **Brightness.** How bright or restrained the scene is.

### Composition and lens

17. **Establishing vs detail vs reference sheet.** Type stated.

18. **Camera angle.** Eye level / high angle / low angle.

19. **Lens length.**

20. **Aspect ratio.**

21. **Depth of field.**

### Ordering rules

22. **Place before mood.** What the place is comes before how it feels.

23. **Era/world rules before lens/style polish.**

### Constraints

24. **Common negatives.** No characters, no modern props, no plastic CGI surfaces,
    no bright white cyc background unless explicitly requested, no text overlays, no
    watermark.

### Three prompt patterns

25. **Pattern A — Reusable asset.** Stable architecture, clear material language,
    minimal action, readable space, reusable identity.

26. **Pattern B — Cinematic establishing still.** Emotional lighting, camera language,
    atmosphere, foreground/background layering.

27. **Pattern C — Reference-preserving iteration.** I2I for every reference-guided
    location prompt.

---

## Seedream storyboard

Source skill: `seedream-storyboard`

### Core rules

1. **One frozen, decisive moment per panel.** Not a collage or multi-panel grid.

2. **Panel budget honored.** When user requests one panel, the strongest representative
   moment is selected — not silently expanded.

3. **Explicit canon.** Recurring identities, locations, props, and style are in an
   explicit canon section.

4. **Canonical Element sheets attached.** When matching Element sheets exist, they are
   attached to the generation request — not substituted with text descriptions.

5. **Screen direction and geography.** Treated as sequence-level constraints.

6. **Natural language.** Coherent natural language, not comma-heavy keyword piles.

7. **References bound by role and target.** Every reference bound with exact `@Image N`
   tokens.

8. **Production notes outside image.** Arrows, labels, dialogue, timing, and production
   notes are outside the generated image unless visible story-world text is required.

### Panel prompt structure

9. **References.** Each reference labeled with role (character identity, location
   geometry, prop identity, composition control, approved style).

10. **Panel purpose.** The new story information or emotion this panel communicates.

11. **Subject and decisive moment.** One frozen moment. Every visible subject, pose,
    expression, action, and prop named. Identity and prop references bound inline.

12. **Setting and state.** Location, time, weather, persistent landmarks, visible
    object state. Location reference bound inline.

13. **Staging and continuity.** Screen-left/right positions, foreground/midground/
    background, eyelines, distances, overlaps, travel direction, entrances/exits, and
    what must match the previous panel.

14. **Style.** Medium, realism level, palette, stable treatment. Style reference bound
    inline when provided.

15. **Lighting.** Source, direction, quality, color, and atmosphere.

16. **Composition.** Aspect ratio, shot size, camera height/angle, lens intent,
    framing, depth, and focus priority. Composition guide bound inline when provided.

17. **Constraints.** Appropriate quality (draft or final), preservation (approved
    identity, geometry, pose, state, style), exclusion (only material faults — no text
    overlays, labels, storyboard borders, watermarks, unintended subjects, duplicated
    faces, control-guide marks).

### Sequential generation

18. **Sequence contract.** Cohesive ordered set of N separate images, one per panel.
    Recurring identity, wardrobe, location geometry, prop design, palette, and
    rendering style kept consistent.

19. **Each image is one moment.** Not a collage or multi-panel grid.

20. **Global visual canon.** Stable identity, location, prop, style, aspect ratio, and
    lighting rules stated before individual panels.

### Revisions

21. **Local edits preferred.** After a composition is approved, prefer local edits over
    full re-generation.

22. **Seeds for tracking.** Used for experiment tracking, not as the identity system.

### Status

23. **Review on generation.** Technically successful generation enters `review`.

24. **Explicit user choice.** Only explicit user choice sets `selected_variant` or
    `approved`.

---

## Seedance music video

Source skill: `seedance-music-video`

### Format and genre

1. **Format declared.** Performance, narrative, conceptual, lyric, visualizer,
   or hybrid — with address mode (direct / indirect / none).

2. **Genre lock is a single recipe.** Not a mixture of two genres. The prompt
   names one genre and follows its palette, lighting, camera grammar, and motion
   cadence consistently.

### Song map

3. **One event per section.** Each song section has one primary visual
   assignment and a visible end state.

4. **Chorus repeats escalate.** A second chorus has rising visual energy —
   not identical to the first.

5. **Bridge departs.** The bridge introduces a new angle, location, wardrobe,
   or image not yet shown.

### Audio contract

6. **Audio treatment explicit.** Native audio brackets, `@Audio N` timing
   authority, or hybrid (reference + native generation) — never ambiguous.

7. **Lip-sync lines verbatim in `{...}`.** Match the audio master exactly —
   no paraphrasing, no reordering, no omitted lines.

8. **Timestamped lyric timeline used when coverage is critical.** Each lyric
   line is bound to its own `[X-Ys] { line }` beat slot — not grouped into
   large blocks. Applies to rap, fast vocal delivery, and any verse where
   complete lyric coverage is a hard requirement.

9. **"No line skipped" mandate present.** When the timestamped timeline is
   used, the prompt includes an explicit instruction that no line may be
   skipped, shortened, mumbled, or reordered.

10. **Native audio caveat acknowledged.** If `generate_audio` is true, the
    prompt accounts for re-performance risk (the model re-performs, not copies,
    the reference).

### Beat contract

11. **Audio events named.** Which beats trigger cuts and camera moves —
    not just "cuts on the beat."

12. **Cut density matches section energy.** Low for verses, high for chorus;
    the prompt states the relationship.

### Structure

13. **Right-sized (4–30s).** One song section per pass, or an explicit
    continuous one-take. Not padded to fill 30s.

14. **Style seal present.** Compact closing sentence with genre, palette,
    motion cadence, beat contract, and tone — does not contradict the format
    or genre.

### Rap-specific (when applicable)

15. **Rap uses timestamped timeline.** Rap and fast vocal delivery always
    use the timestamped lyric timeline (never large `{...}` blocks).

16. **Delivery cue present.** The prompt includes a physical delivery cue
    (e.g., "jaw opening fully on vowels, lips stay in frame throughout").
