# PLAN — Higgsfield Cinema Studio Features → ai-director Agent Skills

> Deep research + implementation plan for porting copyable Cinema Studio features from Higgsfield into ai-director agent skills on the BytePlus MCP stack (Seedance 2.5 / Seedream 5.0 / Seed Audio 1.0).

**Status:** research complete, verified; **skills implemented (S1–S6) and sub-agent reviewed**. **Created:** 2026-08-13. **Research method:** deep-research orchestrator + 5 parallel researcher sub-agents, each finding independently re-verified against official sources.

> **Implementation note (2026-08-13):** All six skills S1–S6 were created under `.agents/skills/` (each with `SKILL.md`, `evals/evals.json`, `agents/openai.yaml`). Two independent reviewer sub-agents audited the set against the canonical `seedance-prompt-25`/`seedream-prompt`/`seed-audio-prompt` grammar, `AGENTS.md`, and this plan; all flagged issues were fixed (Sadness routing, canonical timestamp syntax, mislabeled lens source citation, lighting worked-example/bank contradiction, eval assertion mismatches, trigger disambiguation across skills, plus eval coverage for MoveSet/static-lock/post-grade/sensor/relight/flash). S7 was intentionally **not** built (user decision).

---

## 1. Research summary (verified)

Cinema Studio is Higgsfield's "director console" for AI video — nearly all its controls are **UI presets applied at generation time** while the text prompt carries the scene description. It drives Seedance-family models under the hood, which is the strongest evidence that its console semantics degrade cleanly into ai-director **prompt-composition skills**.

### 1.1 Verified Higgsfield feature catalog (from official sources)

| Panel / axis | Documented options (official) | Source |
|---|---|---|
| **Genre** (global) | General, Action, Epic, Drama, Comedy, Horror, Noir (7) | help center + 3.5 tutorial |
| **Color Palette** (global) | Auto, Naturalistic Clean, Bleached Warm, Hyper Neon, Teal & Orange Epic, Sodium Decay, Cold Steel, Bleach Bypass, Classic B&W (9) | 3.5 tutorial (verified) |
| **Camera MoveSet Style** (global) | Auto, Classic Static, Silent Machine, One Take, Epic Scale, Intimate Observer, Impossible Camera, Documentary Snap, Raw Chaos, Dreamy Flow (10) | 3.5 tutorial (verified) |
| **Lighting** (global) | Auto, Soft Cross, Overhead Fall, Contre-jour, Window, Practicals, Silhouette (7) — documented as *causal* (defines light-source physics) | 3.5 tutorial (verified) |
| **Camera body** (per shot) | Raw 16mm, Fine Film, Clean Digital; 2.0 sensor profiles: VHS / Film / Digital Cinema | 3.5 tutorial, help center |
| **Lens** (per shot) | Auto, Clinical Sharp, Extreme Macro, Anamorphic, Warm Halation, Vintage Haze (3.5); 11 lenses incl. Cooke, 8–50mm (2.0) | 3.5 tutorial, PR Newswire |
| **Focal Length** (per shot) | 8 / 14 / 35 / 50 / 75mm (3.5); full range 12–135mm (2.0) | 3.5 tutorial, help center (verified) |
| **Aperture** (per shot) | f/1.4 Wide Open, f/4 Moderate, f/11 Deep Focus (3.5); continuous f/1.4–f/16 (2.0) | 3.5 tutorial, help center |
| **Camera movement** (per shot) | 15+ director moves (Pan, Tilt, Dolly, Truck, Orbit, Zoom, Drone, Static, Handheld, Jib); **stack up to 3 moves/shot**; platform gallery of **50+ named motion presets** (Hero Cam, Crash Zoom, Dolly Zoom, FPV Drone, Bullet Time, Aerial Pullback, Handheld, Whip Pan, Dutch Angle, Object POV, Snorricam…) | help center (verified), camera-controls gallery (verified) |
| **Speed ramp** | Linear, Auto, Flash In, Flash Out, Slow-mo, Bullet Time, Impact, Ramp Up (3.0) | help center (verified) |
| **Montage Pacing** (4.0) | Chaotic, Dynamic, Calm, Single Shot | product page |
| **Emotions** (per character) | per-character emotion dropdown + **continuous intensity slider**; documented 6-emotion set (hands-on): **Serenity, Joy, Terror, Rage, Fear, Vigilance** | moderncreator.app tutorial; 2.0-era reviews list 5 (Happy/Sad/Angry/Surprised/Focused) |
| **Colorgrade suite** (post-gen, 2.5) | Color Temperature, Contrast, Saturation, Sharpness, Film Grain, Highlights, Exposure (+bloom) | help center (verified) |
| **Relight app** | 6 direction presets (Top/Front/Right/Left/Back/Bottom), interactive light-direction pad, Soft/Hard quality, brightness %, color/gel hex | higgsfield.ai/apps/relight |
| **Color Grading app** | presets Natural, Split Tone, Soft Skin, Old Lens, 16mm; fine-tune sliders; DaVinci plugin **AI LUT Creator → .cube** | higgsfield.ai/apps/color-grading |
| **Elements** | reusable Characters/Locations/Props, project-scoped, referenced via **@tags**, auto-injected every shot | help center (verified) |
| **Soul Cast / SOUL ID** | consistent AI actors; SOUL ID = trained persistent identity from 20+ photos, works cross-model (Kling 3.0, Veo 3.1, Seedance 2.0, WAN 2.6) | official blogs |
| **AI Cast** (4.0) | structured casting (genre, era, archetype, physique, outfit) | product page |
| **AI Director chat (Claude Chat)** | chat beside prompt box; adjusts Genre/Style/Camera; breaks script into shots; never auto-generates (populates prompt for review) | help center (verified) |

**Corrections to the brief:** there is **no feature literally named "acting console"** and **no officially published "6 × 3" grid**. The real controls are a per-character emotion dropdown + a continuous intensity slider; "6 emotions" is corroborated (Serenity/Joy/Terror/Rage/Fear/Vigilance) but "3 intensity levels" is **not** — that's an invention we can still adopt as a design choice (see S3).

### 1.2 Copyability assessment (per feature category)

| Feature category | Tier | Rationale (model-capability-grounded) |
|---|---|---|
| Camera movement presets | **HIGH** | Seedance 2.5 prompt grammar natively covers push in/out, pan, lateral/track, follow, orbit, dolly out, tilt, crane, aerial, FPV, bullet time, dolly zoom, handheld, one-take, whip pan (`seedance-prompt-25` SKILL.md §camera). Higgsfield runs Seedance underneath → proven expressible. |
| Color grading palettes | **HIGH** | Grade maps cleanly to the Seedance visual-style slot + Seedream Style section (teal-and-orange, bleach bypass, film stock, warm/cool, low-sat, B&W). Pure prompt-composition. |
| Static lock / camera-fixed | **HIGH** | "locked-off shot, static camera, only subject moves" is a documented cross-tool + Seedance pattern; `camera_fixed` exists as param in 2.5 (skill line 1044). |
| Keyframes / first-last frame / chaining | **HIGH** | Native first/last-frame + `return_last_frame` on the MCP surface — already built in the workspace. |
| Character identity / Elements consistency | **HIGH** | Workspace already mirrors Higgsfield Elements (`elements/`, manifests, `@tags`, shared reference bundle). **Caveat:** trained persistent identity (SOUL ID) is NOT prompt-expressible → that subset is LOW; reference-bundle consistency is HIGH and largely built. |
| Storyboard / multi-shot planning | **HIGH** | `seedream-storyboard` already exists; Seedance storyboard-grid + scene staging. |
| Native audio + lip-sync | **HIGH** | Already built: audio-first pipeline (Seed Audio → `reference_audio`), `{}` dialogue syntax. |
| Lens / aperture options | **MEDIUM** | No numeric optics control on Seedance; official guide: values "can be included but the intended **visible result** is clearer". Skill must translate lens/aperture presets into visible-result phrasing (bokeh, compression, anamorphic flare, deep focus). |
| Lighting control | **MEDIUM** | Prompt-expressible (direction, soft/hard, time of day, golden hour, vignette, rim) with a dedicated Seedream `Lighting:` section; but emergent per-shot — no per-light rig, no relight-API. |
| Acting console (emotion × intensity) | **MEDIUM** | Seedance 2.5 documents abstract-emotion → observable-cue externalization; intensity only via graduated cues + delivery style, **not** numerically controllable; performance is reinforced audio-first via Seed Audio `reference_audio`. |
| Speed ramp / pacing | **MEDIUM** | "bounce speed ramp", slow-mo, timestamp pacing exist in prompt grammar; timestamps are a time budget, not frame-accurate. |
| AI co-director (script → shots) | **MEDIUM** | Agentic LLM feature — feasible as a Seed-LLM layer on `film-production`, not model grammar. |
| Negative prompts / anti-slop | **LOW** | No `negative_prompt` field on Seedance/Seedream; use positive exclusion phrasing + clean references. |
| Motion brush (regional animation) | **LOW** | No pixel-region motion control on Seedance → needs new MCP support. |
| Trained persistent identity (SOUL ID) | **LOW** | No likeness-training API; nearest is reference-bundle consistency. |

**Bottom line:** ~80% of the console is copyable as prompt-composition skills; the non-copyable parts are the **optical layer** (true aperture/exposure simulation, lens-specific bokeh), **trained identity**, **relight/pixel-brush**, and **negative prompts**.

### 1.3 Sources (verified by orchestrator)

- [Higgsfield Help Center — How do I use Cinema Studio](https://higgsfield.ai/creator-hub/help-center/tools-and-workflows/how-do-i-use-cinema-studio) — official, updated 2026-08-03 (verified)
- [Cinema Studio 3.5 Full Tutorial](https://higgsfield.ai/blog/cinema-studio-3.5-full-tutorial) — official blog (settings tables verified)
- [Higgsfield Camera Controls gallery (50+ presets)](https://higgsfield.ai/camera-controls) — official (preset list verified)
- [Higgsfield Cinema Studio 3.0](https://higgsfield.ai/blog/cinema-studio-3), [2.5](https://higgsfield.ai/blog/cinema-studio-2-5-ai-video-generator), [2.0 guide](https://higgsfield.ai/blog/cinema-studio-guide), [Cinematic Video Generator](https://higgsfield.ai/cinematic-video-generator) — official blogs/product
- [Higgsfield Relight](https://higgsfield.ai/apps/relight), [Color Grading](https://higgsfield.ai/apps/color-grading), [DaVinci plugin](https://higgsfield.ai/plugins/davinci) — official
- [Seedance 2.5 Prompt Guide (Lark)](https://bytedance.larkoffice.com/docx/A88jd0B47oAd8zxWp5ycZFMfnxh), [ModelArk](https://docs.byteplus.com/en/docs/ModelArk/2607689), [launch blog](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) — official (camera vocab, emotion externalization, aperture caveat)
- Local: `.agents/skills/seedance-prompt-25/SKILL.md` (§camera lines 782–843, §emotional direction 743–780, `camera_fixed` line 1044), `.agents/skills/seedream-prompt/SKILL.md` (Lighting + Style keywords), `.agents/skills/seed-audio-prompt/SKILL.md` (voice emotion profile)
- Competitor: Veo 3.1 (deepmind.google/models/veo), Kling (kling.ai quickstarts), Hailuo (minimax I2V API, hailuoai.video), Luma (lumalabs.ai changelog/docs), Runway (help.runwayml.com), Sora 2 (developers.openai.com cookbook), LTX (ltx.io) — all official, accessed 2026-08-13
- Hands-on: [Modern Creator tutorial](https://moderncreator.app/2026-05-27-creating-with-conor-the-only-ai-filmmaking-workflow-you-ll-ever-need) (6-emotion set), [justoborn CS 2.0 guide](https://justoborn.com/studio-2-0/), [PRNewswire CS 2.0](https://www.prnewswire.com/news-releases/higgsfield-advances-its-creator-first-platform-with-cinema-studio-2-0--302698249.html)

---

## 2. Skills to create (implementation plan)

Architecture decision: **six modular preset-bank skills** layered on the existing prompt skills, plus an optional **umbrella `seedance-director-console`** that composes them — mirroring the Higgsfield panel one-for-one. Each preset-bank skill is **prompt-composition only** (no new MCP tools needed), deterministic, parameterized, and emits a drop-in block for the Seedance six-part formula (`Subject + Action + Scene + Visual Style + Camera + Audio`) or the Seedream prompt structure. All follow existing skill conventions (`name` + `description` frontmatter, `## Source authority`, project `AGENTS.md` naming/manifest rules, watermark `false`, ≥3 variants for images, seed-controlled variations).

### S1. `seedance-camera-presets` — camera movement presets + MoveSet styles  [Tier HIGH]

- **Trigger:** user wants a named camera move / shot with specific camera treatment ("dolly in on her face", "FPV drone shot", "one-take gimbal tracking").
- **Preset bank:** map the Higgsfield/industry move vocabulary to canonical Seedance phrases (official vocabulary from `seedance-prompt-25` lines 789–843):
  - *Basic:* pan L/R, tilt U/D, dolly in/out/L/R, truck L/R, track/follow, orbit, crane/jib up/down, static.
  - *Technique presets:* dolly zoom, crash/rapid zoom, whip pan, aerial reveal, FPV path, bullet time, handheld, one-take, rack focus, slow-mo.
  - *MoveSet styles (10):* One Take, Intimate Observer, Documentary Snap, Raw Chaos, Epic Scale, Silent Machine, Impossible Camera, Dreamy Flow, Classic Static — each → a paragraph-level camera-treatment block.
- **Parameter schema:** `move` (preset name), `subject` (what the camera follows), `shot_size` (extreme wide→ECU), `angle` (low/high/overhead/FPV), `duration_or_timestamps` (e.g. `At 3s, ...`), `stack` (≤2 moves/clip — official guidance; Higgsfield allows 3 but Seedance recommends ≤2), `speed`.
- **Output:** a `Camera` block to drop into the formula, e.g.:
  `Slow dolly in toward @gloria's face, medium close-up, low angle, ending on a static lock.`
- **Edge cases:** optical zoom ≠ dolly zoom (specify "purely optical zoom on a locked-off tripod" vs "camera physically dollies"); timestamps are a time budget not frame-accurate; one-take needs explicit subject/space/event order; `camera_fixed: true` for locked-off.
- **MCP wiring:** none. Compose with `seedance-prompt-25`; on generation, snapshot prompt to `prompt_<...>.md` beside the asset + record in `shot.md`.

### S2. `color-grade-palettes` — named color grading palettes  [Tier HIGH]

- **Trigger:** user wants a look/grade ("teal and orange", "bleach bypass", "warm vintage film look") applied to a scene or project.
- **Palette bank:** Higgsfield 9 (Naturalistic Clean, Bleached Warm, Hyper Neon, Teal & Orange Epic, Sodium Decay, Cold Steel, Bleach Bypass, Classic B&W) + film stocks (Kodak Portra 400, Fujifilm Superia 400, Ilford HP5, CineStill 800T) + standard looks (golden hour, low-key noir, high-key, desaturated, Morandi). Each entry = **canonical grade sentence** for the prompt + optional matching **FFmpeg filter graph** (equalizer/colorbalance/curves/vignette/noise) used only for cross-shot matching in the mix step.
- **Parameter schema:** `palette` (named), `target_model` (seedance | seedream), `reference` (optional style-ref image), `post_grade` (bool: also emit FFmpeg graph).
- **Output (Seedance visual-style slot):**
  `Visual style: teal-and-orange cinematic grade — deep teal shadows, rich orange highlights, skin glows, gentle halation.`
- **Output (Seedream Style section):** same phrase + optional film-stock keyword.
- **Edge cases:** **prompt grade is the source of truth** — never stack a conflicting FFmpeg re-grade (only matching/refinement); enforce one project-wide palette for cross-shot consistency; B&W needs explicit contrast/silvers language; avoid mixing conflicting color words.
- **MCP wiring:** none (+ optional `ffmpeg` skill for the post graph).

### S3. `seedance-acting-console` — emotions × intensity with audio-first reinforcement  [Tier MEDIUM]

- **Trigger:** user wants to direct a character's performance/emotion ("make Gloria rageful but restrained, then break into tears").
- **Emotion set (adopt Higgsfield's documented 6):** Serenity, Joy, Terror, Rage, Fear, Vigilance. Extend with the official Seedance 5-emotion externalization table (Sadness, Joy, Nervousness, Anger, Relief) using the same cue vocabulary — Terror/Vigilance are built from gaze/brow/stillness cues.
- **Intensity (design choice: 3 levels):** low = "a flicker in the eyes, a slight raise of the brow"; medium = "brows draw down, mouth tightens, weight shifts"; high = "tears streaming, shoulders shaking, voice cracking". Official guidance forbids degree adjectives ("very sad") → encode intensity as **graduated observable cues** (count, amplitude, delivery style), not degree words.
- **Two-layer architecture (mirrors the console):**
  1. **Prompt layer** — Seedance emotional-direction block using the official single-transition / multi-stage templates: trigger → observable reaction → gradual change → final expression, with `{}` dialogue + delivery style (`urgent`, `softly`).
  2. **Audio-first layer** — Seed Audio voice profile from the same grid (emotional baseline + tone + delivery style), generate dialogue track, verify `audio_duration ≤ video_duration`, keep **identical `{dialogue}` text** in both prompts, pass WAV as `reference_audio` (`@Audio 1`), align shot timestamps to actual audio timing. This is the stronger "acting" lever — lip-sync constrains on-screen performance to the voice emotion.
- **Parameter schema:** `character`, `emotion` (6), `intensity` (1–3), `arc` (optional list of emotion×intensity beats + timestamps), `dialogue` (exact lines), `reinforce_with_audio` (bool → audio-first pipeline).
- **Edge cases:** intensity not numerically controllable — validate each level (A/B same seed); don't overload cues (2–4 per transition); dialogue text must be verbatim across Seed Audio + Seedance prompts; if audio exceeds video duration, trim audio prompt, never pad video.
- **MCP wiring:** `seed_audio_*` (T2A/TA2A) → `seedance_2_5_create_task` with `reference_audio` + `duration`. Record audio path/hash/duration + dialogue-to-shot mapping in `shot.md` and `scene.md` per AGENTS.md alignment contract.

### S4. `seedance-lighting-presets` — lighting presets for Seedream + Seedance  [Tier MEDIUM]

- **Trigger:** user wants a lighting setup ("soft cross light interrogation room", "contre-jour sunset", "practicals only candlelit").
- **Preset bank:** Higgsfield 7 (Soft Cross, Overhead Fall, Contre-jour, Window, Practicals, Silhouette) with the **causal intent** from the 3.5 tutorial (what the light does to the physical scene) + Relight concepts (direction: front/back/top/side; quality soft/hard; gel color; brightness) + standard (three-point, Rembrandt, golden hour, rim, low-key, high-key).
- **Parameter schema:** `preset`, `direction`, `quality`, `color_temp_or_gel`, `target_model` (seedream | seedance), `subject`.
- **Output (Seedream `Lighting:` recipe):**
  `Lighting: soft key light at 45 degrees left, warm 3200K, gentle fill from right, rim light on hair.`
- **Output (Seedance visual-style):**
  `Lighting: contre-jour — warm backlight halo along head and shoulders, face readable, field catches the glow.`
- **Edge cases:** lighting is **emergent** (prompt-level, not rig-level) — validate per shot; "relight existing asset" is NOT available prompt-side (must re-gen or use `seedream-edit`); match preset to scene intent (the tutorial's failure examples show mismatches).
- **MCP wiring:** none. Compose with `seedream-prompt` / `seedance-prompt-25`.

### S5. `seedance-lens-presets` — lens, focal length, aperture → visible result  [Tier MEDIUM]

- **Trigger:** user wants optics ("anamorphic widescreen look", "portrait compression 85mm", "deep focus wide shot").
- **Preset bank:** focal lengths (8/14/24 → wide/distortion; 35/50 → natural perspective; 75/85/135 → portrait compression + background compression); apertures (f/1.4 → shallow DOF + circular/oval bokeh; f/4 → moderate; f/11 → deep focus); lens character (Anamorphic → oval bokeh + horizontal flare; Fisheye → barrel distortion; Macro → extreme close; Warm Halation / Vintage Haze; Clinical Sharp); sensor (VHS / Film / Digital Cinema → grain/texture language).
- **Rule (official):** always pair any numeric value with the **visible result** — numbers are advisory on Seedance:
  `Camera: 85mm, shallow depth of field — face sharp, background soft with compressed, creamy bokeh.`
- **Parameter schema:** `lens`, `focal_length`, `aperture`, `sensor`, `subject`.
- **Edge cases:** no true optical simulation — never promise exact bokeh/aberration; anamorphic flare may need explicit "horizontal lens flare"; 2.5 caps at 720p so "4K anamorphic" is a 2.0/Fast/Mini concern → route to `seedance-prompt-20` per AGENTS.md.
- **MCP wiring:** none.

### S6. `seedance-pacing-presets` — speed ramp + montage pacing  [Tier MEDIUM]

- **Trigger:** user wants pacing control ("slow-mo on impact", "chaotic montage", "single continuous take").
- **Preset bank:** speed ramps (Linear, Auto, Slow-mo, Bullet Time, Flash In, Flash Out, Impact, Ramp Up) + Montage Pacing (Chaotic, Dynamic, Calm, Single Shot) → timestamped motion/cut/pacing blocks (e.g. `At 4s the action snaps into slow motion, bullet-time orbit...`).
- **Parameter schema:** `ramp`, `pacing`, `duration`, `cut_list` (optional shot timings), `audio_sync` (align to Seed Audio master).
- **Edge cases:** timestamps are a time budget, not frame-accurate; pacing needs a shot list (compose with storyboard/film-production); 30s single-pass or extension only for continuous-seamless-motion needs (AGENTS.md exception).
- **MCP wiring:** none. Composes with `seedance-prompt-25` + `film-production`.

### S7 (optional umbrella). `seedance-director-console` — full "Cinema Studio" brief  [Tier MEDIUM]

- **Trigger:** user gives a full directorial brief ("genre: horror; lighting: practicals; grade: sodium decay; camera: intimate observer; lens: 35mm f/1.4; Gloria: Rage × 2, dialogue...") and wants one complete Seedance prompt.
- **Behavior:** parameterized front-end that resolves each axis through S1–S6 banks and assembles the six-part formula into a single prompt + optional audio-first layer. Mirrors the Higgsfield panel exactly; also records the whole brief + per-axis resolutions in `shot.md`.
- **Relationship to `film-production`:** stays a leaf-level prompt generator; `film-production` remains the stage manager (per AGENTS.md).
- **Edge cases:** avoid conflicting axes (e.g. palette Cold Steel + golden-hour lighting); validate resolved prompt with the `seedance-prompt-25` self-check list (line ~903).

---

## 3. Sequencing & effort

| Phase | Work | Priority |
|---|---|---|
| 1 | S1 camera-presets + S2 color-grade-palettes (both HIGH, pure prompt banks) | Do first |
| 2 | S3 acting-console (highest novelty; needs audio-first pipeline validation) | Next |
| 3 | S4 lighting + S5 lens + S6 pacing (share bank structure with S1/S2) | Then |
| 4 | S7 director-console umbrella (compose S1–S6) | Last |
| – | Optionally: probe `camera_fixed`/optics params live on MCP; add `camera_preset` MCP param to upgrade S4/S5 fidelity | Stretch |

Each skill needs: `SKILL.md` (frontmatter + source authority + preset bank + parameter schema + output grammar + edge cases + self-check), an `evals/` folder (mirror `seedance-prompt-25/evals`), and a smoke test that produces one asset and verifies prompt snapshot + `shot.md` linkage + hash.

## 4. Open questions / follow-ups

- **Exact emotion taxonomy:** Higgsfield never publishes a fixed emotion list — the 6 (Serenity/Joy/Terror/Rage/Fear/Vigilance) rest on one strong hands-on source; verify against a live account or pin ours as a documented design decision.
- **"3 intensity levels":** not a Higgsfield control (it's a continuous slider). We adopt 3 levels as a skill design; validate each level's fidelity via same-seed A/B.
- **Audio emotion forcing:** does `reference_audio` reliably make Seedance *act* the emotion vs only lip-sync? Needs an empirical A/B (neutral vs angry voice, same prompt).
- **Numeric-lens ceiling:** cheap live probe "50mm f/2.8" vs "shallow DOF, compressed background" to calibrate S5.
- **MCP surface:** confirm there's no `camera_fixed`/`motion_strength`/`negative_prompt`/`preset` param on the modelark MCP server; if a `camera_preset`/`lighting_preset` param is added, tiers for S1/S4/S5 upgrade.
- **Prompt-grade vs post-grade:** no LUT stage exists; prompt grade is the source of truth, FFmpeg only for cross-shot matching — decide whether to add Remotion/FFmpeg grade nodes later.
