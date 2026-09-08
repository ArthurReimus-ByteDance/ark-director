# Worked Examples

Focused reference for `seedream-prompt`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [Full example: T2I — Cinematic scene](#full-example-t2i--cinematic-scene)
- [Full example: Infographic](#full-example-infographic)
- [Full example: Image Editing — Color & Material Replacement](#full-example-image-editing--color--material-replacement)
- [Full example: Multi-image fusion](#full-example-multi-image-fusion)

## Full example: T2I — Cinematic scene

```
Task:
Text-to-Image (T2I)

Subject:
A young woman in a flowing red dress, windswept dark hair, standing at the edge of a cliff, arms slightly raised, face turned toward the horizon with a serene expression.

Setting:
A dramatic coastal cliff at golden hour. The ocean stretches endlessly below, waves crashing against rocks. Distant seabirds circle. A lighthouse is visible on a far promontory.

Style:
Cinematic, photorealistic, widescreen anamorphic look. Kodak Portra 400 film stock aesthetic.

Lighting:
Golden hour backlight, warm amber and rose tones, soft rim light on the subject's hair and dress, gentle fill from the ocean reflection. God rays breaking through scattered clouds.

Composition:
Wide shot, eye level, rule of thirds — subject positioned on the left third line, horizon on the lower third, negative space to the right filled by the ocean and sky.

Constraints:
Quality: 4K, rich textures, cinematic depth of field
Negative: no watermarks, no text overlays, no distorted anatomy, natural skin texture
```

## Full example: Infographic

```
Task:
Infographic / Information Visualization

Subject:
A visual infographic chronicling scientific research at Antarctica's Qinling Station. Place the main Qinling Station building at the center. Surround it with a timeline of research station development, a bar chart comparing the sizes of five research stations, a pie chart of the station's energy sources, and a line chart of monthly sunshine. Supplement with realistic photos of research equipment, a summer weather panel, a seven-step fieldwork flowchart, and on-site sampling photography.

Setting:
Clean, academic presentation layout. Antarctic landscape references in the background — ice shelves, penguin colonies, aurora.

Style:
Scientific infographic, National Geographic editorial style, clean data visualization, modern sans-serif typography.

Lighting:
Even, bright studio lighting for charts and diagrams. Dramatic natural lighting for the landscape elements.

Composition:
Central anchor (research station) with radial layout. Timeline along the top, charts on the left, flowchart on the right, photos in the bottom section.

Text in image:
"Qinling Station" — main title
Chart labels and data values as appropriate

Constraints:
Quality: 2K, crisp text rendering, professional color palette
Negative: no distorted charts, no misaligned text, consistent font sizes
```

## Full example: Image Editing — Color & Material Replacement

```
References:
@Image 1: velvet fabric swatch (material reference)
@Image 2: color palette card — teal and gold
@Image 3: living room photo — brown leather sofa to modify

Task:
Image Editing

Editing mode:
Color & Material Replacement

Edit instructions:
Using the velvet material from @Image 1 and the teal color from @Image 2, modify the sofa in @Image 3. Replace the brown leather with teal velvet. Keep the wood frame, surrounding decor, and room lighting unchanged. The new material should catch light naturally with the same highlights and shadows as the original.

Constraints:
Quality: 2K, photorealistic material rendering
Negative: do not change the room background, do not alter the sofa's shape or proportions
```

## Full example: Multi-image fusion

```
References:
@Image 1: wooden desk on white background
@Image 2: leather-bound journal on white background
@Image 3: brass desk lamp on white background
@Image 4: porcelain teacup on white background
@Image 5: fountain pen on white background
@Image 6: composition layout sketch
@Image 7: window light reference photo

Task:
Image Editing

Editing mode:
Multi-Image Fusion

Edit instructions:
Precisely cut out the objects from @Image 1 through @Image 5 and compose them according to the layout in @Image 6 into a real still-life photograph on the desk. Use the window lighting from @Image 7 as the scene lighting reference. Ensure correct perspective, light-and-shadow, and spatial relationships. Faithfully reproduce material details — wood grain, leather texture, polished brass, glazed ceramic.

Constraints:
Quality: 2K, photorealistic, natural shadow casting
Negative: no floating objects, no mismatched lighting directions
```
