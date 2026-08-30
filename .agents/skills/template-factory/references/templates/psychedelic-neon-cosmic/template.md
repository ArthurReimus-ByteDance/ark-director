# Template — Psychedelic Neon Cosmic Journey

Replicates the validated reference (see `projects/template-factory`, pin
`01.mp4`, approved take `t03`).

## Style

- **Grade:** high-saturation neon, strong chromatic aberration, retro
  vaporwave/synthwave palette, analog film grain + CRT scanlines
- **Lighting:** all emissive neon; self-illuminated subjects; no natural
  directional light; high contrast vs dark starfields
- **Lens:** wide-angle for cosmic/road shots, standard for figure shots, soft
  glow bloom on bright neon
- **Film look:** low-fi retro digital animation, film grain, color shifting,
  analog distortion

## Camera

Static framing for most shots (motion comes from elements + light, not the
camera). Only the rainbow-road shot has a real forward dolly. All transitions
are hard cuts.

## Motion grammar (from the deep motion review)

- Floating figure: slow sine bob (~0.5Hz), leaning pose
- Rainbow beams/heads/rings: continuous hue scroll (0.3–2s cycle)
- Palm fronds: out-of-phase slow sway (~0.4Hz)
- Ringed planets: counter-rotating, rings in sync (~3s cycle)
- Car: forward drive via scrolling lane markers + passing streetlights
- Rainbow road: fast first-person dolly, bands scroll toward viewer
- Walkers: outline-only figures, natural walk cycles, glitch distortion
  through light beams
- Global: subtle pulsing chromatic aberration (~1Hz) + soft edge distortion on
  all elements

## Audio

Source has a synthwave score; the factory generates **no audio** by default
(`generate_audio: false`). Set `generate_audio: true` and supply the `audio`
slot to generate native audio.

## Key parameters

| Setting | Value |
|---|---|
| Model | `dreamina-seedance-2-5-260628` |
| Resolution | 720p |
| Ratio | 1:1 |
| Duration | sum of shot durations (source ≈ 16s) |
| Storyboard | monochrome sketch, 8 panels (dynamic), 3 variants, human review |
| watermark | false |
