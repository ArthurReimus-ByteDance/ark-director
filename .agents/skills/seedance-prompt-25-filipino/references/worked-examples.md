# Worked Examples

Read [the entrypoint](../SKILL.md). **All examples below are HYPOTHETICAL.**
They demonstrate prompt structure, not prior approvals, language validation,
or successful model generations. Exact example wording is illustrative; a
project's locked line always takes precedence.

## Native audio — private check-in

Assumed brief: two close friends, a private phone conversation, contemporary
conversational Filipino; the line below was selected for this hypothetical case.

```text
Dialogue language: conversational Filipino, matching the established speaker.
Mara is checking whether her friend arrived safely. She waits for the answer,
then asks quietly: {Nakarating ka na?}
Keep the selected words intact; the question is a private check-in.
```

Review target: a short private question with the exact words. Do not add a
phonetic table or turn the line into a formal announcement by default.

## Native audio — formal wording deliberately preserved

Assumed brief: a formal public statement; the user wants the supplied wording
unchanged. The register itself is not a defect.

```text
Dialogue language: Filipino, the approved formal register.
The speaker delivers the supplied statement to the assembly with measured
phrasing and a firm close: {<exact approved formal statement>}
```

Review target: preserve words and intent. A preference for everyday vocabulary
is not a reason to modernize the line.

## Native audio — Taglish with a locked language mix

```text
Dialogue language: the approved conversational Taglish register.
Jay addresses his colleague privately, seeking a concrete answer about the
handoff. He says: {Ready na ba yung report?}
He emphasizes the handoff question and waits for the colleague to answer.
```

Review target: the selected code-switching and exact words survive. Do not
invent a pronunciation issue or force all English words into one accent rule.

## Audio-first — only with explicit separate-track scope

Assumed brief: the user specifically requested a separate dialogue track and
selected the line below. Its performance still needs listening review.

Audio prompt:

```text
Characters and dialogue
Mara, with the approved voice and conversational register, asks a private
check-in question: "Nakarating ka na?"
Ending
The voice ends cleanly, leaving space for an answer.
```

Video prompt after the track is selected and verified:

```text
@Audio 1 defines Mara's selected voice and dialogue performance.
Mara holds the phone and listens before asking: {Nakarating ka na?}
Direct speaking rhythm and lip motion to @Audio 1, preserving the scene's
approved identity, camera, and timing.
```

Review target: identical dialogue, actual duration fit, selected audio evidence,
and observed lip alignment. This example does not claim a successful generation.
