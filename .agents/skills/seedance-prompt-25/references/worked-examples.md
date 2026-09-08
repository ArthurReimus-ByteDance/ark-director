# Worked Examples

Focused reference for `seedance-prompt-25`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [Full example: T2V 30-second one-take](#full-example-t2v-30-second-one-take)
- [Full example: R2V multi-reference concert](#full-example-r2v-multi-reference-concert)
- [Full example: Video editing — subject replacement](#full-example-video-editing--subject-replacement)

## Full example: T2V 30-second one-take

```
One-take handheld gimbal tracking shot. The camera slowly pushes in through a gap in a heavy red
curtain and enters a warm-toned backstage dressing room. A young female singer, with her back to
the camera, is adjusting her earpiece as a staff member reminds her it's time to go on. She turns
toward the camera and starts singing citypop. The camera pulls back and tracks her as she passes
through the curtain into a dim backstage corridor, interacting naturally with her dancers along
the way; one staff member hands her a microphone. She and the dancers then step onto the stage,
and the camera arcs around to the back, gradually revealing the red-and-black stage design, LED
screens, spotlights, haze, and reflective floor. The camera finally pulls out to a wide shot of
the arena, showing the packed audience, light boards, glow sticks, and cheering crowd.
```

## Full example: R2V multi-reference concert

```
A 30-second concert sequence in 16:9 landscape, with cinematic realism, authentic concert hall
lighting and shadows, warm golden stage lighting, and the atmosphere of a formal classical concert.

Use @Image 1 for the venue.
Reference @Image 2 for the pianist.
Reference @Image 3 for the cello.
Reference @Image 4 for the violin.
The lead vocalist must strictly follow @Image 5.
Reference @Images 6 to 10 for the rest of the orchestra.
Reference @Images 11 to 14 for the choir.
Reference @Images 15 to 18 for the audience seating.

The lead vocalist walks from center stage toward the front edge. The pianist is positioned by the
piano. The orchestra is arranged on both sides and toward the rear. The choir stands at the back
of the stage.

Open with a high-angle wide shot of the full concert hall. The pianist strikes the keys, and the
lead vocalist steps into the spotlight and begins singing. The camera naturally moves across the
violin, cello, and orchestra as they perform together, with the violin feeling bright and the
cello warm. In the latter part, the choir joins in. The lead vocalist briefly makes eye contact
with front-row audience members, who respond with a smile and a slight nod. In the closing shot,
the camera pulls back. The singing ends, and the audience joins in the applause.
```

## Full example: Video editing — subject replacement

```
[Edit Goal]
Edit @Video 1. Replace only the yellow folding desk lamp with the white folding desk lamp in @Image 1.

[Source Video Role]
@Video 1 is the sole editing master. It defines the desk, books, hand movements, camera position,
camera movement, occlusion relationships, and event order.

[Target Reference Role]
@Image 1 defines only the white folding desk lamp's appearance, structure, and material. Do not use
the image's background, composition, or other objects.

[Edit Scope]
Keep exactly one white folding desk lamp throughout the video. Replace only the original yellow
folding desk lamp. Do not modify the books, desk, hands, or background.

[Timeline Inheritance]
The white folding desk lamp inherits every appearance, lamp-arm rotation, hand occlusion, and exit
of the original yellow folding desk lamp, including timing, path, and speed changes.
Except for the object or area explicitly modified above, keep all other people, props, scene
content, camera movements, cuts, and event order from @Video 1 unchanged.
```
