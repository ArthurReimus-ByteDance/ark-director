---
description: Review and fix prompts (Seedance, Seed Audio, Seedream) against skill best practices using a sub-agent review pipeline.
agent: build
---

Load the `prompt-review` skill and run its full review workflow.

$ARGUMENTS

If the user specified prompt file paths above, review only those files. If no arguments were given, find all `prompt_*.md` files that were written or updated in the current session (check git diff and recently modified files under `projects/`) and review those.

Follow the 8-step workflow in the skill's SKILL.md:
1. Collect prompts to review
2. Detect each prompt's type and load the matching checklist from `references/review-checklists.md`
3. Spawn a review sub-agent for each prompt type (parallel, max 5 concurrent)
4. Sub-agent returns structured findings (CRITICAL / MAJOR / MINOR with suggested fixes)
5. Triage findings by severity
6. Apply fixes to the prompt files
7. Re-review changed prompts if any CRITICAL or MAJOR fixes were applied (max 2 rounds)
8. Report results to the user with the summary format from the skill

Do not skip the review or rush it. Every checklist item must be checked. The sub-agent quotes exact text from each prompt as evidence and provides specific, actionable suggested fixes — not "improve the prompt".
