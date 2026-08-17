---
name: lark-showcase-aigc
description: Creates enterprise-facing Lark documents to showcase AIGC (AI-generated content) with prompts, results, and inline media. Invoke when the user wants a standalone customer guide or showcase article in Lark.
---

# Showcase AIGC

Create a polished external-facing Lark Document that combines two goals at once:

1. **Showcase** what was produced and why it matters.
2. **Teach** the reader how the workflow works step by step.

Use this skill when the user wants a customer-ready Lark document that feels like a strong product article or breakdown page similar in spirit to a Higgsfield workflow post, but adapted for enterprise readers and delivered as a Lark Document.

## Primary outcome

Produce a **standalone external guide** that a client can read without any access to the local workspace, repository, or project folder. The document must stand on its own.

The final document should:

- open with the strongest result or business outcome before the detailed walkthrough;
- explain the business scenario and outcome clearly;
- walk through the workflow in a logical tutorial sequence;
- show the exact prompts, references, settings, and outputs that matter;
- embed images, audio, and video inline when available;
- read like a polished customer showcase, not an internal engineering note.

## Mandatory routing

When executing this skill, use these skills and tools as needed:

- `lark-demo-doc-builder` for the main document-building workflow and prompt/result table patterns.
- `lark-doc` for document creation and block-level editing.
- `lark-wiki` when the target is a wiki URL and the underlying doc token must be resolved.
- `lark-drive` when folder placement, permissions, or document organization is requested.
- `design-doc-mermaid` when a workflow diagram materially improves clarity.

Before writing to Lark, follow the upstream Lark instructions required by `lark-demo-doc-builder`.

## External-guide rules

This skill is for **client-facing artifacts**, so enforce these rules strictly unless the user explicitly asks otherwise:

- Do **not** mention local files, local paths, repo paths, folder names, asset filenames, shell commands, or workspace structure.
- Do **not** say things like "stored in", "saved at", "located in", or reference internal directories.
- Do **not** expose internal-only notes, debugging context, temporary constraints, or implementation caveats irrelevant to the customer.
- Do **not** present the workflow as dependent on this specific machine or repository.
- Do **not** include raw MCP, API, or CLI details unless the user explicitly wants a technical appendix.

Translate internal provenance into customer-safe wording:

- "reference image supplied to the model"
- "generated storyboard frame"
- "generated video result"
- "voice prompt"
- "workflow step"
- "model configuration"

Never surface filesystem-oriented phrasing in the Lark document.

## Narrative style

Write in a way that feels:

- polished;
- enterprise-appropriate;
- concrete and evidence-based;
- tutorial-like without sounding academic;
- confident but not hype-heavy.

The reader should be able to understand:

- what problem is being solved;
- what inputs were used;
- what steps were taken;
- what outputs were produced;
- how they can adapt the workflow to their own use case.

## Higgsfield article patterns to emulate

The reference article is effective because it behaves like a guided production breakdown rather than a generic case study. Reproduce these strengths in the Lark document when appropriate:

- lead with the finished outcome and why it is impressive before diving into process;
- explain the workflow as a sequence of clearly separated steps;
- show the exact prompt or setup for each step, not just a paraphrase;
- explain what each prompt or step does in plain language;
- make it obvious where each step belongs in the overall workflow;
- keep the narrative skimmable even when the source prompts are long and technical.

Do not copy the article's creator-marketing tone. Preserve the article's clarity and structure, then rewrite it for enterprise readers.

## Table-first layout (default)

Two layout principles govern the entire document. Apply them unless the user explicitly asks for a different arrangement.

### 1. Prompts as columns inside asset tables

When a table already exists to showcase assets (reference images, character sheets, location sheets, prop sheets, storyboard panels), **add the generation prompt as a column in that same table** — do not create a separate "Prompt and result evidence" section or scatter prompts across standalone paragraphs.

The prompt sits directly beside the asset it produced. The reader scans one row per asset: name, type, role, image, and the exact prompt that generated it. This eliminates the need to cross-reference between a media table and a separate prompt section.

Typical columns for an asset table:

| Element | Type | Role | Reference image | Prompt |

Use a `<pre lang="text"><code>` block inside the prompt cell for long prompts — the cell expands, and the prompt stays scannable alongside its result.

### 2. Consolidate parallel items into one table

When multiple items share the same structure — per-scene audio, per-scene video, per-character sheets — **put them as rows in a single consolidated table**, not as repeated h2 + paragraph + table sections.

An item qualifies for consolidation when:

- every item has the same columns (e.g., prompt + playable track);
- the only differentiator is which scene/character/step it belongs to;
- the per-item narrative is short enough that a "Scene" or "Stage" column carries it.

When a per-item section needs a long narrative explanation that does not fit a table cell, break only that item into its own section — keep the rest in the consolidated table.

Typical columns for a consolidated evidence table:

| Scene | Prompt | Generated Result |

or:

| Scene | Audio prompt | Full track (playable) |

Replace what would have been 7 h2 + table sections with one h1 + intro paragraph + single table. This keeps the document skimmable: the reader sees the full inventory at a glance instead of scrolling through near-identical sections.

### When NOT to consolidate

Break into separate sections only when:

- items have genuinely different structures (different columns, different media types);
- one item needs substantial narrative context the others do not;
- the user explicitly asks for one section per item.

## Recommended document structure

Use this structure by default, trimming or expanding only when the user asks.

1. **Title**
2. **Audience and purpose**
3. **Hero outcome**
4. **Executive summary**
5. **What this workflow demonstrates**
6. **Workflow overview**
7. **Input assets** — one consolidated table with reference images **and their prompts as a column** (see Table-first layout, principle 1)
8. **Audio assets** (if applicable) — one consolidated table per modality (see Table-first layout, principle 2)
9. **Scene-by-scene breakdown** — one table per scene showing video prompt + generated clip; use a "Scene" column if scenes share the same structure
10. **Enterprise adaptation guidance**
11. **Limitations and review notes**
12. **Next steps**

## Section blueprint

### 1. Title

Use a customer-readable title that signals both the use case and the outcome.

Examples:

- `How to Create a Cinematic Product Showcase with BytePlus AI`
- `Enterprise Workflow: From Prompt to Polished AI Video Demo`
- `Showcase + Tutorial: Building a Brand Storytelling Asset with BytePlus Models`

### 2. Audience and purpose

Open with 2-4 sentences that explain:

- who this document is for;
- what business scenario it addresses;
- what the reader will learn from the guide.

### 3. Hero outcome

Before the summary, show the strongest customer-facing result first:

- a hero video, image, audio sample, or composite before/after;
- a one-paragraph explanation of what the reader is about to learn;
- a short statement of business relevance.

This mirrors the article's strongest pattern: outcome first, explanation second.

### 4. Executive summary

Add a short summary block covering:

- models or capabilities used;
- the final output type;
- the main value for enterprise teams.

If helpful, include a compact capability table.

### 5. What this workflow demonstrates

State the specific capabilities being showcased, such as:

- concept development;
- image generation;
- character consistency;
- video generation;
- audio generation;
- multi-step creative orchestration;
- prompt engineering;
- campaign adaptation.

### 6. Workflow overview

When the workflow has three or more linked stages, add a Mermaid diagram or a compact flow table.

Keep the diagram customer-readable. Use business-oriented labels such as:

- `Creative Brief`
- `Visual Reference Creation`
- `Video Generation`
- `Audio Layer`
- `Final Deliverable`

Avoid internal storage or system topology diagrams unless explicitly requested.

If useful, add a compact workflow table with these columns:

- `Step`
- `Goal`
- `What happens here`
- `Primary output`

### 7. Input assets — reference images and their prompts

Present all approved reference images (characters, locations, props) in a **single consolidated table** with the generation prompt as a column inside the table (see Table-first layout, principle 1).

One table, one row per asset. The prompt column uses a `<pre lang="text"><code>` block so long prompts stay readable inside the cell.

If the same element has multiple variants (e.g., a hero sheet and a rollout sheet), show both images in the same cell and note the variant in the prompt text.

### 8. Audio assets (if applicable)

When the workflow includes generated audio (dialogue, ambience, music), present all audio assets in a **single consolidated table** with a "Scene" column as the first column (see Table-first layout, principle 2).

Do not create one h2 + table per scene. One table, one row per scene, three columns: Scene, Audio prompt, Full track (playable).

If one scene needs extra narrative (e.g., "this track spans both shots of scene 3"), put that note in the Scene cell, not in a separate paragraph above the table.

### 9. Scene-by-scene breakdown

Create one section per scene. Each scene section should explain:

- the goal of the shot;
- the references used;
- the prompt and the generated result in a table row;
- why this step matters.

For each scene, use a short intro paragraph followed by a prompt/result table with these columns:

- `Stage`
- `Prompt / Input`
- `Generated Result`

If multiple scenes share the same table structure and the per-scene narrative is short, consider consolidating them into a single table with a "Scene" column (see Table-first layout, principle 2).

For Higgsfield-style breakdowns, each scene should usually follow this micro-structure:

1. `What we are trying to achieve`
2. `What this step does`
3. `Prompt / setup`
4. `Generated result`
5. `Why it matters`
6. `How to adapt it`

This is the preferred default for long-form showcase tutorials.

For each row:

- show the exact prompt or a faithfully cleaned version of it;
- describe references in external-facing language;
- place the matching image/audio/video inline in the result cell;
- add a concise explanation of what the prompt is intended to control;
- add a brief note on what the result proves.

When speech or dialogue is relevant, include the exact transcript beside the generated media.

When the source prompt is very long, use this presentation pattern:

- first show a short reader-facing explanation of the prompt's purpose;
- then include the full prompt in a clearly labeled code block inside the table cell;
- keep the matching result immediately adjacent to that prompt.

Never bury the prompt far away from the result it produced.

## Per-step breakdown block

For each major workflow step, prefer this section recipe:

1. **Step title**: short, action-oriented, and customer-readable.
2. **Goal**: one sentence on the step's purpose.
3. **What this step does**: plain-language explanation of the prompt or setup.
4. **Table row with prompt + result**: the exact prompt and the generated result appear side by side in a table cell, not in separate paragraphs or sections (see Table-first layout).
5. **Why this matters for enterprise teams**: stakeholder value, repeatability, or reuse.
6. **How to adapt it**: what a customer should swap for their own brand, product, or campaign.

This is the closest Lark-document equivalent of the article's "prompt + what it does + where to run it" rhythm.

## Higgsfield-inspired writing pattern

When the user wants a breakdown similar to a strong AI filmmaking article, structure each major stage like this:

1. **What we are trying to achieve**
2. **Why this step matters**
3. **Prompt / setup**
4. **Generated output**
5. **What to reuse or customize**

This keeps the document readable as both a showcase and a tutorial.

For cinematic or narrative workflows, prefer preserving the prompt's internal logic in a customer-readable way. Typical prompt segments may include:

- scene context;
- active references;
- location or spatial map;
- first frame or blocking;
- optics or shot framing;
- action beats;
- performance direction;
- lighting;
- audio;
- consistency or lock constraints.

Do not force these headings into every customer document. Use them when they help explain why the generation is controllable and repeatable.

## Enterprise framing guidance

Adapt the narrative toward enterprise readers. Emphasize:

- repeatability;
- controllability;
- brand alignment;
- creative iteration speed;
- cross-team collaboration;
- traceable inputs and outputs;
- where human review still matters.

Good framing examples:

- "This step establishes a reusable visual identity that can be carried across multiple campaign assets."
- "The workflow keeps prompt intent and generated evidence side by side for easier stakeholder review."
- "This pattern can be adapted for retail, entertainment, travel, and product marketing scenarios."

Avoid consumer-creator phrasing like:

- "go viral"
- "crazy results"
- "insane output"
- "magic"

unless the user explicitly wants that tone.

## Prompt cleanup rules

When the source material comes from internal prompting or generation workflows:

- preserve the exact business-relevant prompt wording when possible;
- remove internal-only labels, scratch notes, and local storage references;
- rewrite path-like references into readable descriptions;
- keep technical precision where it helps the customer understand controllability;
- shorten only when the full prompt would harm readability, and clearly label any shortened excerpt.

If a prompt includes named references, convert them into external-facing labels such as:

- `Character Reference`
- `Location Reference`
- `Product Reference`
- `Voice Reference`
- `Scene Reference`

If the source prompt uses many internal reference labels, add a short "Reference legend" near the prompt so external readers understand the role of each reference without seeing internal asset names or storage details.

### Scene-by-scene label cleanup

The per-scene breakdown tables are the second most common source of jargon.
When writing scene labels, clip descriptions, and reference lists:

| Forbidden pattern | Use instead |
|---|---|
| "Clip used: s01_sh010_t01_v01 — full (12.1s)" | "Full clip (12.1s)" |
| "Clip used: s03_sh020_t01_v02 — 1–9s only (8s)" | "Trimmed clip (8s)" |
| "Input references: Bianca, Lola Maria..." | "References used: Bianca, Lola Maria..." |
| "Asset: dlg_s01_kiko_t01.wav (9.2s)" | "Scene 1 — audio track" |
| "s04a — The Eruption (shot 1)" | "Scene 4a — The Eruption" |
| "shot 2, part 1" | "first part" / "second part" |
| "`@Audio 1` reference" | "audio reference" |

Scene subheadings should use plain scene names, not internal shot codes.

### Deliverable table cleanup

The executive summary capability table is the most common source of jargon
leakage. When filling the "Deliverable" column:

- **Remove variant counts** — "3 variants each, user-approved" → "Approved
  character and location designs"
- **Remove internal filenames** — "s01_sh010_t01_v01.mp4" → "41-second
  commercial video"
- **Remove API parameters** — "720p/24fps with native audio" → "with
  synchronized voice and sound"
- **Remove model IDs** — "dreamina-seedance-2-5-260628" → "Seedance 2.5"
- **Remove tool names** — "FFmpeg" → "Video assembly"
- **Remove shot codes and version suffixes** — "s01_sh010" → "Scene 1",
  "_v01" → (omit)

A reader should understand the deliverable without knowing what a "variant"
or "shot code" is.

## Media handling rules

Use playable inline media whenever Lark supports it.

- Images should appear **inside the same table cell** as the prompt that produced them — not in a separate media gallery or a detached section (see Table-first layout, principle 1).
- Audio and video should use Preview rendering when possible, also inside the table cell adjacent to their prompt.
- Captions should explain what the reader is looking at.
- Avoid detached media galleries when the evidence belongs inside a step table.

If multiple outputs exist for one step, present only the strongest reader-facing examples by default and summarize the selection logic briefly.

Prefer showing the result before or immediately beside dense technical text. The article works partly because the reader never has to hold a very long prompt in memory before seeing why it matters.

## Jargon blocklist

The following terms must **never** appear in reader-facing text (outside
`<pre><code>` prompt blocks). They are internal-only jargon that breaks the
"mom test" — a non-technical reader should understand every word outside the
prompt code blocks.

### Model IDs and API parameters

| Forbidden | Use instead |
|---|---|
| `dreamina-seedance-2-5-260628` | Seedance 2.5 |
| `dreamina-seedance-2-0-260128` | Seedance 2.0 |
| `dola-seedream-5-0-pro-260628` | Seedream 5.0 Pro |
| `seed-audio-1.0` (in prose) | Seed Audio 1.0 |
| `generate_audio: true` | (omit; describe the result instead) |
| `return_last_frame: true` | (omit; describe the result instead) |
| `reference_audio` | audio reference |
| `prompt_optimization` | (omit) |
| `persist: true` | (omit) |
| `watermark: false` | (omit) |
| `text-to-image` (T2I) | image generation |
| `text-to-audio` (T2A) | audio generation |
| `reference-to-video` (R2V) | video generation |

### Internal filenames and asset codes

| Forbidden pattern | Use instead |
|---|---|
| `dlg_s01_kiko_t01.wav` | Scene 1 — audio track |
| `s01_sh010_t01_v01.mp4` | Scene 1 — video clip |
| `char_bianca_sheet_v03.png` | Bianca |
| `loc_filipino-home-kitchen_wide_v03.png` | Filipino Home Kitchen |
| `.wav`, `.mp4`, `.png` (in visible labels) | (omit extension) |
| `_t01`, `_v01`, `_v02`, `_v03` version suffixes | (omit) |
| `s01_sh010`, `s01_sh020`, etc. | Scene 1, Scene 2, etc. |
| `sh010`, `sh020` shot codes | (omit; use scene names) |

### Tool and infrastructure names

| Forbidden | Use instead |
|---|---|
| FFmpeg, ffmpeg | video assembly |
| Remotion | video rendering |
| CLI, MCP | (omit entirely) |
| `lark-cli` | (omit entirely) |
| object storage, S3, TOS | (omit entirely) |
| presigned URL | (omit entirely) |
| `seed-media://` | (omit entirely) |
| artifact ID | (omit entirely) |
| token (as in file token) | (omit entirely) |

### Process jargon

| Forbidden | Use instead |
|---|---|
| native audio | synchronized voice and sound |
| forward extension | continuation |
| muxed, mux, post-mux | combined, assembled |
| canonical input assets | approved reference images |
| variants, 3 variants each | (omit; just say "approved") |
| timestamp constraints | (omit) |
| base scene, base generation | scene |
| Element sheet | reference image |
| reference sheet | reference image |
| KYC restriction | (omit; say "not yet available" if needed) |
| `@Audio 1`, `@Image N`, `@Video 1` (in prose) | audio reference, reference images, source video |
| `block_replace`, `str_replace`, `block_insert_after` | (omit entirely) |
| 720p/24fps, 4K, 2K (in deliverable descriptions) | high-resolution |
| seed (as in random seed) | (omit) |

### Allowed inside `<pre><code>` prompt blocks only

The following are **only** acceptable inside the actual prompt code blocks
(captioned as "Seedance prompt" etc.), because they are the literal syntax the
model expects:

- `@Image N`, `@Audio N`, `@Video N` reference bindings
- `{dialogue}`, `<sound effect>`, `(music)` syntax
- `[Shot N (start–end)]` timestamp blocks
- Model-specific prompt structure (`@Image 1 defines...`, `Extend @Video 1
  forward...`)

Outside code blocks, translate all of these into plain English.

## Pre-publish verification gate

Before declaring the document complete, run this mandatory scan:

1. **Fetch every section** of the document using `lark-cli docs +fetch --scope
   section --detail with-ids`.
2. **Strip all `<pre>` blocks** from the fetched content — prompt code blocks
   are exempt from the jargon check.
3. **Scan the remaining text** for every term in the jargon blocklist above.
   A simple approach:
   ```bash
   # After fetching a section's JSON, strip code blocks and check for terms
   python3 -c "
   import re
   text = '<fetched content>'
   outside = re.sub(r'<pre[^>]*>.*?</pre>', '', text, flags=re.S)
   visible = re.sub(r'<[^>]+>', ' ', outside)
   terms = ['FFmpeg','dreamina-','dola-','generate_audio','reference_audio',
            'native audio','forward extension','720p','24fps','.wav','.mp4',
            's01_','sh0','_t01','_v0','text-to-image','text-to-audio',
            'variants','canonical','Element sheet','reference sheet',
            'muxed','CLI','MCP','@Audio','@Image','@Video']
   found = [t for t in terms if t.lower() in visible.lower()]
   print('JARGON FOUND:' if found else 'CLEAN', found)
   "
   ```
4. **Fix every hit** using `lark-cli docs +update --command str_replace` to
   replace the jargon with the reader-safe alternative from the blocklist.
5. **Re-fetch and re-scan** after fixes to confirm zero remaining hits.
6. **Only then** declare the document complete in the deliverable contract.

This gate is not optional. The "mom test" means: if you handed this document to
someone with no knowledge of AI tooling, API parameters, or internal project
structure, would they understand every word outside the prompt code blocks?

## Standalone-document checks

Before finalizing, verify that the document can be read on its own. The reader
should not need:

- access to a code repository;
- knowledge of local folder structure;
- prior chat context;
- internal naming conventions;
- private attachments not included in the document.

Ask yourself:

- Would an external enterprise client understand this without additional
  context?
- Does every prompt/result pair have enough explanation?
- Are there any leftover internal references? (Run the jargon blocklist scan.)
- Does the document tell a coherent story from business goal to final output?

## Default writing workflow

Unless the user specifies otherwise, follow this sequence:

1. Identify the target audience, use case, and desired business takeaway.
2. Gather the prompts, results, and any example structure the user wants to emulate.
3. Normalize the material into external-facing language.
4. Create the Lark document structure.
5. Add the hero outcome near the top.
6. Add a concise executive summary and workflow overview.
7. Build the **input assets table** with reference images and their prompts as a column (Table-first layout, principle 1).
8. Build **audio assets table** (if applicable) as a single consolidated table with a Scene column (Table-first layout, principle 2).
9. Build one **scene-by-scene table** per scene with prompt + generated result side by side; consolidate into a single table when scenes share the same structure.
10. Add adaptation guidance, limitations, and next steps.
11. Fetch the final structure and verify no internal path or local-file wording remains.

## When information is missing

If the user requests the document but has not yet provided enough detail, ask for the minimum set of inputs needed:

- target audience;
- target use case;
- whether the doc is a new document or an update;
- the artifacts or examples to showcase;
- the preferred tone;
- whether exact prompts should be included in full or summarized;
- whether the reader should see a business-friendly simplified view, a full technical prompt view, or both.

## Deliverable contract

At handoff, provide:

- the Lark document link;
- a short summary of what the document includes;
- the scenarios or workflow stages covered;
- any open review items or missing assets;
- confirmation that the document was checked for external-facing wording and absence of local file references.

## Example invocation cases

Use this skill when the user asks for requests like:

- "Create a client-facing Lark doc that showcases this workflow."
- "Turn this AI generation pipeline into a polished tutorial document for enterprise customers."
- "Make a Higgsfield-style breakdown as a Lark Document."
- "Build an external guide that explains the prompts and results without exposing local project details."
