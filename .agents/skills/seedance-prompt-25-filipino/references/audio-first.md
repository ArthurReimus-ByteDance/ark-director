# Audio First

Read [the entrypoint](../SKILL.md). This is an **optional** route for an
explicitly requested separate dialogue track that will drive video lip-sync.
Filipino language, scene complexity, or a pronunciation concern alone does not
select this route. The caller coordinates generation; this leaf supplies the
wording and alignment contract.

## Before audio preparation

- Confirm that separate lip-sync audio is within the user's requested scope.
- Preserve exact approved dialogue, speaker voice, register, and scene timing.
- Use an agreed wording revision only after its approval or within explicit
  rewrite authority. Simplification is not a required first step.
- Resolve current tool/model support for the audio reference and video mode.
- Record the intended speaking window and source of pronunciation guidance.

## Audio prompt form

```text
Scene and atmosphere
<Acoustic space and relevant sound layers.>

Characters and dialogue
<Speaker with approved voice/register> says with <playable intent/delivery>:
"<exact approved dialogue>"

Pronunciation direction, only where needed
<Verified reading or explicitly identified hypothesis outside spoken text.>

Ending
<Sound tail or finish appropriate to the scene.>
```

## Verify actual audio

Listen for word fidelity, intended pronunciation, speaker/register continuity,
and the line's dramatic delivery. Record issues with timestamps when available.
A transcript supports word checking but cannot certify stress or vowel quality.
Measure actual duration against the video speaking window. If verification is
unavailable, the track remains unresolved and cannot be claimed as verified.

A failed delivery hypothesis calls for a bounded proposed repair, not automatic
regeneration. Preserve the provider task and prepared request; the caller
reconciles an uncertain submission instead of repeating it.

## Video prompt form

```text
@Audio 1 defines <speaker>'s selected dialogue and voice reference.
<Speaker> performs <the scene action> and says: {<the same exact approved words>}
Direct lip motion and speaking rhythm to the selected @Audio 1 performance.
<Preserved scene, identity, and camera direction.>
```

The requested synchronization is an acceptance target, not a guarantee.
Do not assert that a reference has correct pronunciation until it was checked.

## Alignment and handoff

1. Keep exact dialogue identical in audio and video prompts.
2. Ensure actual audio duration fits the planned video and speaking window.
3. Use measured dialogue timestamps only where shot alignment needs them.
4. Pass the supported audio file as the ordered `reference_audio` binding.
5. Record local path, SHA-256, duration, reference selection, and any mapping.
6. Review generated lip motion and sound continuity; a correct audio track does
   not establish correct video alignment.

Preserve native audio as the default for future scenes unless the user's
separate-audio instruction explicitly covers them too.
