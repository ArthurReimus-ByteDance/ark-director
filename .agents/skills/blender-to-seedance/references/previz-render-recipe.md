# Previz render recipe (Blender → Seedance master)

Build a flat-gray, viewport-like previz and render it to a 24fps MPEG-4 clip
that Seedance 2.5 will treat as the motion master.

Blender 5.x removed `bpy.ops.render.opengl`; render with a lightweight **EEVEE**
setup and flat materials instead.

## Target contract

| Property | Value |
|---|---|
| Resolution | 1920 x 1080 |
| FPS | 24 |
| Frame range | `1 .. int(24 * duration)` |
| Format | FFMPEG / MPEG4, codec H264 |
| Look | Flat mid-gray materials, neutral world, AO + one soft light |

## Render snippet

```python
import bpy

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'      # Blender 4.2+ / 5.x
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 24
scene.render.frame_start = 1
scene.render.frame_end = int(scene.render.fps * DURATION)  # DURATION in seconds
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.filepath = '//previz_<shot>_v01.mp4'

# One shared flat-gray material system
for mat in bpy.data.materials:
    bsdf = mat.node_tree.nodes.get('Principled BSDF') if mat.node_tree else None
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)
        bsdf.inputs['Roughness'].default_value = 1.0

# Neutral gray world
if bpy.context.scene.world:
    bpy.context.scene.world.color = (0.5, 0.5, 0.5)

bpy.ops.render.render(animation=True)
```

## Blockout conventions

- **Primitives = subjects.** Cube = person; monolith = hero; cylinder = can;
  spheres = fruit; boxes = props; checkerboard plane = "to replace".
- **Color = identity.** Distinct flat color per subject. Never rely on texture.
- **Monolith facing.** Paint a character proxy's faces: RED = the direction it
  faces, BLACK = its back, GREEN = sides/top. The prompt then reads facing
  direction as text.
- **Camera on splines.** Camera targets a null; cuts change only on frame
  boundaries. Handheld = slow sway + micro-tremor, never fast jitter.
- **Black gaps.** Leave empty frames where a later effect (liquid sim, etc.)
  will be generated separately.

## Minimal scene example (one hero, orbit camera)

```python
import bpy, math

def box(name, loc, scale, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    ob.data.materials.append(mat)
    return ob

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))     # floor
box('hero', (0, 0, 1), (0.6, 0.6, 1.8), (0.8, 0.1, 0.1))         # red hero monolith

# Camera + target on an orbit
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
target = bpy.context.active_object
bpy.ops.object.camera_add(location=(6, 0, 2))
cam = bpy.context.active_object
cam.constraints.new('TRACK_TO').target = target

scene = bpy.context.scene
scene.camera = cam
scene.frame_start, scene.frame_end = 1, 120          # 5s @ 24fps

cam.rotation_euler = (0, 0, 0)
for f in range(scene.frame_start, scene.frame_end + 1):
    a = (f - 1) / 24 * 2 * math.pi / 5               # one orbit over 5s
    cam.location = (6 * math.cos(a), 6 * math.sin(a), 2)
    cam.keyframe_insert('location', frame=f)
```

## Notes

- Verify the render in the viewport before the full pass (one test frame).
- Keep the `.blend` as the editable source; the MP4 is the submission master.
- If EEVEE Next is unavailable, fall back to `'BLENDER_EEVEE'`.
