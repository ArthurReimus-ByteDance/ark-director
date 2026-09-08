# Photographic Detail

Use for a requested photographic look or a reported photographic defect. These
are **optional artistic techniques**, not API requirements or guarantees of
realism. Read the image or supplied review before diagnosing it. When no output
is available, state a hypothesis rather than claiming an observed failure.

## Diagnose the visible mismatch

Identify the region and observable symptom: erased skin texture, implausible
light direction, repeated fabric texture, inconsistent scale, or unwanted lens
artifacts. Possible causes include the reference, requested aesthetic, lighting,
edit scope, and generation variation. Insufficient prompt detail is only one
hypothesis; more detail is not a universal remedy.

Preserve approved identity, age, skin features, wardrobe, framing and copy.
Do not invent freckles, scars, asymmetry or wear to make a person or product
look real. Describe existing reference texture when it is relevant and visible.
A clean beauty photograph or evenly lit catalog image can be intentional.

## Choose only the relevant photographic controls

| Requested result | Optional direction | Avoid adding automatically |
| --- | --- | --- |
| Soft catalog image | Broad diffuse source, readable contours, controlled contact shadow | Neon spill, grain, hard dramatic shadows |
| Documentary portrait | Existing skin texture, available light and context | New identity marks, forced age or exaggerated pores |
| Product material study | Visible grain/finish, reflections that explain the form | Scratches or dirt absent from the approved product |
| Cinematic atmosphere | A motivated source and one compatible lens/grade treatment | Multiple film stocks and contradictory lens signatures |

Name direction, softness, color and falloff when they help communicate the
image. Flat or shadowless lighting is not intrinsically a defect. Lens, camera
body and film-stock names are creative shorthand; pair them with the desired
visible result and omit them when they add nothing. They do not prove physical
camera simulation.

## Write a focused edit

Lead with the main subject or requested change so a reader understands the
intent. This is a clarity convention, not a measured positional weighting law.
Use positive visible detail; include a narrow exclusion only when needed to
protect an edit boundary or prevent a demonstrated reference leak. Do not append
a generic list of unwanted artifacts to every image prompt.

Keep actual output size and optimization settings in request metadata. Treat
any parameter or quality/latency claim as a source-guide snapshot until checked
against the selected live model/tool. Do not invent an optimization field or
force a mode merely because the image is photographic.

## Repair example: texture without changing identity

**Hypothetical teaching example. No image was generated or measured.**

- **Brief:** Edit an approved portrait to restore texture while retaining its
  soft studio lighting and the person's exact appearance.
- **Initial prompt:** “Make this realistic with freckles, wrinkles, film grain,
  hard sunlight and cinematic lens flare.”
- **Simulated failure:** The result adds age/identity marks and changes lighting.
- **Hypothesis:** The requested additions exceed the texture-only edit scope.
- **Smallest repair:** “Restore the fine skin texture visible in @Image 1 on
  the cheeks and forehead. Preserve the person's existing skin markings, age,
  facial geometry, expression, framing and broad soft studio light.”
- **Tradeoff:** Less stylization; fidelity to the approved portrait takes priority.
- **Acceptance:** Compare the same facial regions at the intended viewing size;
  texture is visible without added markings or a lighting redesign.

If the input does not contain recoverable texture evidence, describe that gap
and propose a conservative treatment rather than inventing canonical details.
