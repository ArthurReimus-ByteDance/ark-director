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

## Recommended document structure

Use this structure by default, trimming or expanding only when the user asks.

1. **Title**
2. **Audience and purpose**
3. **Hero outcome**
4. **Executive summary**
5. **What this workflow demonstrates**
6. **Workflow overview**
7. **Step-by-step breakdown**
8. **Prompt and result evidence**
9. **Enterprise adaptation guidance**
10. **Limitations and review notes**
11. **Next steps**

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

### 7. Step-by-step breakdown

Create one section per major stage. Each stage should explain:

- the goal of the step;
- the inputs used;
- the prompt or instruction pattern;
- the generated output;
- why this step matters.

For each stage, use a short intro paragraph followed by a prompt/result table.

For Higgsfield-style breakdowns, each stage should usually follow this micro-structure:

1. `What we are trying to achieve`
2. `What this step does`
3. `Prompt / setup`
4. `Generated result`
5. `Why it matters`
6. `How to adapt it`

This is the preferred default for long-form showcase tutorials.

### 8. Prompt and result evidence

Use the three-column evidence format from `lark-demo-doc-builder` unless a different structure is clearly better:

- `Stage`
- `Prompt / Input`
- `Generated Result`

For each row:

- show the exact prompt or a faithfully cleaned version of it;
- describe references in external-facing language;
- place the matching image/audio/video inline in the result cell;
- add a concise explanation of what the prompt is intended to control;
- add a brief note on what the result proves.

When speech or dialogue is relevant, include the exact transcript beside the generated media.

When the source prompt is very long, use this presentation pattern:

- first show a short reader-facing explanation of the prompt's purpose;
- then include the full prompt in a clearly labeled code block, callout, or collapsible detail section when supported by the target document format;
- keep the matching result immediately adjacent to that prompt.

Never bury the prompt far away from the result it produced.

## Per-step breakdown block

For each major workflow step, prefer this section recipe:

1. **Step title**: short, action-oriented, and customer-readable.
2. **Goal**: one sentence on the step's purpose.
3. **What this step does**: plain-language explanation of the prompt or setup.
4. **Exact prompt / input**: full prompt or a faithful excerpt.
5. **Recommended workflow stage**: where this step fits in the end-to-end flow.
6. **Generated result**: inline media or a result description.
7. **Why this matters for enterprise teams**: stakeholder value, repeatability, or reuse.
8. **How to adapt it**: what a customer should swap for their own brand, product, or campaign.

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

## Media handling rules

Use playable inline media whenever Lark supports it.

- Images should appear adjacent to the prompt that produced them.
- Audio and video should use Preview rendering when possible.
- Captions should explain what the reader is looking at.
- Avoid detached media galleries when the evidence belongs inside a step table.

If multiple outputs exist for one step, present only the strongest reader-facing examples by default and summarize the selection logic briefly.

Prefer showing the result before or immediately beside dense technical text. The article works partly because the reader never has to hold a very long prompt in memory before seeing why it matters.

## Standalone-document checks

Before finalizing, verify that the document can be read on its own. The reader should not need:

- access to a code repository;
- knowledge of local folder structure;
- prior chat context;
- internal naming conventions;
- private attachments not included in the document.

Ask yourself:

- Would an external enterprise client understand this without additional context?
- Does every prompt/result pair have enough explanation?
- Are there any leftover internal references?
- Does the document tell a coherent story from business goal to final output?

## Default writing workflow

Unless the user specifies otherwise, follow this sequence:

1. Identify the target audience, use case, and desired business takeaway.
2. Gather the prompts, results, and any example structure the user wants to emulate.
3. Normalize the material into external-facing language.
4. Create the Lark document structure.
5. Add the hero outcome near the top.
6. Add a concise executive summary and workflow overview.
7. Build one scenario or stage section at a time using the per-step breakdown block.
8. Insert prompt/result tables with inline media.
9. Add adaptation guidance, limitations, and next steps.
10. Fetch the final structure and verify no internal path or local-file wording remains.

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
