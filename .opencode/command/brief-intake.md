---
description: Run brief intake to propose genre-aware directorial defaults for a new project.
agent: build
---

Load and follow the `brief-intake` skill (`.agents/skills/brief-intake/SKILL.md`).

Read the brief below (or from the project's `project.md` if it exists), derive
genre-appropriate defaults per directorial axis, and confirm them with the user.

$ARGUMENTS

Run in **fast mode by default**: present the compact full-set line, then surface
only the four high-risk choices (audio mode, acting direction, grade palette,
medium) for confirmation. Switch to **full Q&A mode** only if the user explicitly
asks to walk through every axis.

Before finishing, write the confirmed `locked` block into `project.md`
frontmatter and record which axes were confirmed vs accepted by default. Do not
generate any media — this command proposes and confirms defaults only.
