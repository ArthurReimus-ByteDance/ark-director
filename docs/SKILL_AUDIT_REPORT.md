# Skill Audit Report — Standalone-ness & Separation of Concerns

> Audited 38 project-local skills in `.agents/skills/` across 5 parallel sub-agent analyses.
> Date: 2026-08-14

## Executive Summary

| Severity | Count | Summary |
|---|---|---|
| **Critical** | 0 | All resolved |
| **Moderate** | 3 | Content duplication, artificial thin skills |
| **Low** | 6 | Minor implicit coupling, stale links, back-reference anti-pattern |
| **Clean** | 26 | Standalone or intentionally coupled with sharp boundaries |

---

## Critical Findings

### ~~C1: `seedance-footage-vfx` and `seedance-vfx-prompt` are ~60% near-duplicate~~ — RESOLVED

Merged `seedance-footage-vfx` into `seedance-vfx-prompt`. Ported the compact `@source`/`@creature` declaration format, compact specs line, plain-text output rules, structure patterns quick-reference, and Seedance 2.0 input limits table. Deleted `seedance-footage-vfx`. Updated `film-production` routing table, `SEEDANCE_25_LIMITATIONS.md`, `PLAN_SEEDANCE_25_ANIMATION_STYLES_SKILL.md`, and `PLAN_SKILL_VERSION_AUDIT.md` to remove references.

Also fixed M1 (convention misattribution): `seedance-vfx-prompt` was referencing `seedance-prompt-25` for heading conventions but actually uses `seedance-prompt-20` conventions. All four references corrected to `seedance-prompt-20`.

### ~~C2: `tig-acting-task` / `seedance-acting-console` overlap~~ — RESOLVED

Merged `tig-acting-task` into `seedance-acting-console`. The combined skill has two layers: (1) Tig's analysis ladder (scene direction → motive → goal → obstacle → tactic with eye-work) as the always-on front-end, and (2) the emotion bank + cue encoding as the translation layer — cues are derived from the tactic, not the emotion label. The audio-first pipeline is now an optional section that pairs with `seed-audio-prompt` instead of duplicating the contract. Deleted `tig-acting-task`. Registered `tig-scene-engine` and `tig-blocking-map` in AGENTS.md's axis routing table.

### ~~C3: `seedance-animation-styles` references missing `references/style-recipes.md`~~ — FALSE POSITIVE

The file exists (194 lines, all 10 recipes). The sub-agent that audited this group ran in a fresh context and could not see the file. No fix needed.

---

## Moderate Findings

### ~~M1: `seedance-vfx-prompt` misattributes conventions to `seedance-prompt-25`~~ — RESOLVED

Fixed all convention attributions from `seedance-prompt-25` to `seedance-prompt-20` (four references in the Asset preparation, Subject definitions, and prompt structure sections).

### ~~M2: `seed-audio-commercial` duplicates `seed-audio-prompt` content while declaring it "mandatory"~~ — RESOLVED

Removed ~190 lines of duplicated content (prompt template, voice profile format, onomatopoeia guidance, timestamp control, Do/Don't best practices, quick reference card, verification commands). Replaced with a clear "Pairs with `seed-audio-prompt`" statement at the top. Kept only commercial-specific content: five-act story arc, production workflow, Taglish safety filter guidance, SFX/music patterns, cost management, and the two full commercial examples. Skill reduced from 717 to 525 lines.

### M3: Audio-first alignment contract duplicated across 3 skills + AGENTS.md

The full audio-first pipeline and alignment contract is restated in:
- `seedance-acting-console` (7-step pipeline + 5-point contract)
- `seedance-pacing-presets` (shorter version)
- `AGENTS.md` (canonical version)

If AGENTS.md updates the contract, both skills drift.

**Recommendation:** Define the contract once in AGENTS.md. Have both skills reference it by name instead of restating it.

### M4: `remotion-best-practices` is a pure router with full duplicate copies of spoke skills

Zero domain knowledge — just links to 8 other Remotion skills. Worse, it contains full byte-for-byte duplicate copies of each spoke skill under `remotion-best-practices/<spoke>/REFERENCE.md`. Dual maintenance burden.

**Recommendation:** Remove the duplicate subdirectories. Reduce to a lightweight index or eliminate entirely — the system prompt's skill list already handles routing.

### M5: `remotion-interactivity` (23 lines) is an artificial subset of `remotion-markup`

Core advice (avoid object spreads, `<Interactive.Div>`, inline values) is already in `remotion-markup`. The interactivity skill adds almost nothing. References a sub-file that lives in markup's directory.

**Recommendation:** Merge into `remotion-markup` as an "Interactivity" section. Delete the separate skill.

### ~~M6: `tig-acting-task` not registered in AGENTS.md routing table~~ — RESOLVED

Merged `tig-acting-task` into `seedance-acting-console` (see C2). Registered `tig-scene-engine` and `tig-blocking-map` in AGENTS.md's axis routing table.

---

## Low-Severity Findings

### L1: `remotion-render` is too thin (28 lines) to justify independence

Two CLI commands + one sub-file about transparent videos. Could be a section in `remotion-markup`.

**Recommendation:** Merge into `remotion-markup` or expand with real depth (Lambda, Cloud Run, batch rendering, codec control).

### L2: "Go back to best-practices" back-references in Remotion spoke skills

`remotion-create`, `remotion-docs`, and `remotion-markup` all open with "If this is not relevant, load best-practices." Creates bidirectional coupling and undermines standalone-ness.

**Recommendation:** Remove all back-references. Each skill should assume it was correctly routed.

### L3: `seedance-camera-presets` and `seedance-pacing-presets` overlap on bullet-time, slow-motion, one-take

Both include canonical templates for bullet time and slow motion. Camera calls it "one-take," pacing calls it "Single Shot." No composition rule for when both are loaded.

**Recommendation:** Make bullet-time canonical in `seedance-camera-presets` (it's primarily a camera technique). Remove duplicates from pacing. Standardize terminology.

### L4: No Visual Style slot composition order for preset skills

`seedance-lens-presets`, `seedance-lighting-presets`, and `color-grade-palettes` all produce text for the Visual Style slot with no merge rule.

**Recommendation:** Add an explicit slot composition order to `seedance-prompt-25` or AGENTS.md (e.g., lighting -> lens character -> grade -> sensor).

### L5: `seedance-acting-console` paradoxically restates `seedance-prompt-25` templates

Claims to defer to `seedance-prompt-25` for single-transition and multi-stage templates, then provides them inline. Maps its 6-emotion bank to `seedance-prompt-25`'s 5-emotion table.

**Recommendation:** Either own the templates (remove the "from prompt-25" claim) or truly defer (remove the template text and reference the other skill).

### L6: `ffmpeg` has stale external reference to `github.com/digitalsamba/claude-code-video-toolkit`

**Recommendation:** Update or remove the attribution/contribution section.

---

## Clean Skills (No Action Needed)

| Skill | Status |
|---|---|
| `seedance-prompt-25` | Standalone. Base skill with advisory routing. |
| `seedance-prompt-20` | Standalone. Clean version boundary. |
| `seedance-prompt-25-filipino` | Intentional partner skill. Explicit "do not use alone" + clear composition contract. |
| `seedance-vfx-shot` | Intentional pipeline skill. Sharp boundary with `seedance-vfx-prompt`. |
| `seedance-camera-presets` | Standalone. Produces Camera block fragments. |
| `seedance-lens-presets` | Standalone. Produces optics sub-phrases. |
| `seedance-lighting-presets` | Standalone. Dual-output (Seedream + Seedance). |
| `seedance-pacing-presets` | Standalone (except for duplicated audio-first contract). |
| `seedance-acting-console` | Standalone (except for paradoxical template coupling). |
| `seedream-prompt` | Standalone. Base skill with advisory routing. |
| `seedream-character-sheet` | Standalone. Minor convention re-derivation. |
| `seedream-character-sheet-cleanup` | Intentional post-processing skill. |
| `seedream-location-asset` | Standalone. Cleanest specialized skill. |
| `seedream-edit` | Standalone. Tool-operation layer. |
| `seedream-storyboard` | Standalone. Most comprehensive standalone skill. |
| `seed-audio-prompt` | Standalone. Base audio skill. |
| `audio-dubbing` | Standalone pipeline skill. |
| `film-production` | Orchestrator by design. References are a routing table, not imports. |
| `modelark-mcp` | Standalone. 1294-line API reference. |
| `media-review` | Standalone. Single-purpose. |
| `color-grade-palettes` | Standalone. Prompt-composition fragment skill. Correct layering pattern. |
| `ffmpeg` | Standalone. Command cookbook. |
| `mediabunny` | Standalone. Different runtime from ffmpeg (browser/Node vs CLI). |
| `lark-showcase-aigc` | Partial — hard dependency on `lark-demo-doc-builder` is defensible layering. |
| `remotion-captions` | Standalone. Zero coupling. |
| `remotion-docs` | Standalone (remove back-ref). |
| `remotion-saas` | Standalone. Clean separation. |
| `remotion-upgrade` | Standalone. |

---

## Full Dependency Matrix

```mermaid
graph TD
  subgraph "Base Prompt Skills (standalone)"
    P25[seedance-prompt-25]
    P20[seedance-prompt-20]
    SP[seedream-prompt]
    SAP[seed-audio-prompt]
  end

  subgraph "Partner/Extension Skills"
    FIL[seedance-prompt-25-filipino --> P25]
    VFX[seedance-vfx-prompt]
    VSHOT[seedance-vfx-shot --> VFX]
    CS[seedream-character-sheet]
    CSC[seedream-character-sheet-cleanup --> CS]
    SAC[seed-audio-commercial --> SAP]
  end

  subgraph "Preset/Fragment Skills"
    CAM[seedance-camera-presets]
    LENS[seedance-lens-presets]
    LIGHT[seedance-lighting-presets]
    PACE[seedance-pacing-presets]
    ACT[seedance-acting-console]
    ANIM[seedance-animation-styles]
    GRADE[color-grade-palettes]
  end

  subgraph "Orchestration & Infra"
    FILM[film-production]
    MCP[modelark-mcp]
    FFM[ffmpeg]
    MED[media-review]
    BUN[mediabunny]
    TIG[tig-acting-task]
    LARK[lark-showcase-aigc]
  end

  subgraph "Remotion Hub-and-Spoke"
    BP[remotion-best-practices]
    MK[remotion-markup]
    CRE[remotion-create]
    INT[remotion-interactivity]
    REN[remotion-render]
    CAP[remotion-captions]
    DOC[remotion-docs]
    SAAS[remotion-saas]
    UP[remotion-upgrade]
  end

  TIG -->|now resolved| TIGSE[tig-scene-engine]
  ANIM -.->|missing file| REC[??? style-recipes.md]
  BP -->|duplicates| MK
  BP -->|duplicates| CAP
  BP -->|duplicates| CRE
  INT -->|references file in| MK
```

---

## Recommended Action Plan

### Immediate (critical fixes)

1. ~~**Merge `seedance-footage-vfx` into `seedance-vfx-prompt`**~~ — DONE.
2. ~~**Create `references/style-recipes.md`** for `seedance-animation-styles`~~ — FALSE POSITIVE. File exists with all 10 recipes.

### Short-term (moderate fixes)

3. ~~**Register `tig-acting-task` in AGENTS.md** or merge into `seedance-acting-console`~~ — DONE. Merged into `seedance-acting-console` (two-layer: Tig analysis + cue encoding). Registered `tig-scene-engine` and `tig-blocking-map` in AGENTS.md. Deleted `tig-acting-task`.
4. ~~Fix convention attribution in `seedance-vfx-prompt`~~ — DONE. All references corrected from `seedance-prompt-25` to `seedance-prompt-20`.
5. ~~Remove duplicated content from `seed-audio-commercial`~~ — DONE. Removed ~190 lines of duplicated prompt structure, voice profile format, best practices, quick reference card, and verification commands. Now pairs with `seed-audio-prompt` instead of duplicating it. Reduced from 717 to 525 lines.
6. ~~Remove duplicated audio-first contract from `seedance-acting-console` and `seedance-pacing-presets`~~ — DONE. `seedance-acting-console` now has an optional, self-contained audio section that pairs with `seed-audio-prompt`. `seedance-pacing-presets` audio-first contract replaced with a concise pointer; clarified that audio-first is only for lip-sync-critical scenes, not all dialogue. Removed AGENTS.md reference.
7. Eliminate duplicate subdirectories in `remotion-best-practices`; reduce to index or remove
8. Merge `remotion-interactivity` into `remotion-markup`

### Long-term (low priority)

9. Merge `remotion-render` into `remotion-markup` or expand it
10. Remove "go back to best-practices" back-references from Remotion spoke skills
11. Resolve bullet-time/slow-motion duplication between camera-presets and pacing-presets
12. Add Visual Style slot composition order to `seedance-prompt-25` or AGENTS.md
13. ~~Fix paradoxical template ownership in `seedance-acting-console`~~ — DONE. The combined skill now owns both the analysis templates and the encoding templates; no paradox.
14. Clean up stale external reference in `ffmpeg`
