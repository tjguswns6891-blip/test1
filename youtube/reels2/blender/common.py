# 릴스 2차 Blender 장면 공통 도구 (blender 4.0, EEVEE, 화면 없이 렌더)
import bpy, math, sys, os
from mathutils import Vector

BG = (0.066, 0.074, 0.094)


def hexrgb(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x ** 2.2 for x in c) + (a,)          # sRGB → linear


def reset(frames, fps=30, res=(1280, 720)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'BLENDER_EEVEE'
    s.render.resolution_x, s.render.resolution_y = res
    s.render.fps = fps
    s.frame_start, s.frame_end = 1, frames
    s.eevee.use_bloom = True
    s.eevee.bloom_intensity = 0.04
    s.eevee.bloom_threshold = 0.9
    s.eevee.taa_render_samples = 8
    s.eevee.use_gtao = True
    s.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = hexrgb('#111318')
    w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
    s.render.image_settings.file_format = 'FFMPEG'
    s.render.ffmpeg.format = 'MPEG4'
    s.render.ffmpeg.codec = 'H264'
    s.render.ffmpeg.constant_rate_factor = 'HIGH'
    return s


def mat(name, color, emit=0.0, metal=0.0, rough=0.4, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexrgb(color)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = hexrgb(color)
        b.inputs['Emission Strength'].default_value = emit
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'; m.shadow_method = 'NONE'; m.show_transparent_back = True
    return m


def assign(o, m):
    o.data.materials.clear(); o.data.materials.append(m)
    return o


def arrow(name, tail, head, m, r=0.045):
    """tail→head 화살표 (원기둥 + 원뿔). 부모 빈 객체를 돌리고 늘려서 애니메이션한다."""
    root = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(root)
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=0.86, location=(0, 0, 0.43), vertices=24)
    shaft = bpy.context.object; assign(shaft, m); shaft.parent = root
    bpy.ops.mesh.primitive_cone_add(radius1=r * 3, depth=0.14, location=(0, 0, 0.93), vertices=24)
    tip = bpy.context.object; assign(tip, m); tip.parent = root
    point(root, tail, head)
    return root


def point(root, tail, head, frame=None):
    d = Vector(head) - Vector(tail)
    root.location = tail
    root.rotation_mode = 'QUATERNION'
    root.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    root.scale = (1, 1, d.length)
    if frame is not None:
        for p in ('location', 'rotation_quaternion', 'scale'):
            root.keyframe_insert(p, frame=frame)


def camera(loc, target, lens=50):
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam)
    cam.location = loc; cam.data.lens = lens
    t = bpy.data.objects.new('target', None); bpy.context.collection.objects.link(t); t.location = target
    c = cam.constraints.new('TRACK_TO'); c.target = t; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam, t


def light(kind, loc, energy, color='#ffffff', size=3):
    l = bpy.data.objects.new(kind, bpy.data.lights.new(kind, kind)); bpy.context.collection.objects.link(l)
    l.location = loc; l.data.energy = energy; l.data.color = hexrgb(color)[:3]
    if kind == 'AREA': l.data.size = size
    l.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return l


def smooth_keys():
    for a in bpy.data.actions:
        for fc in a.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = 'BEZIER'; k.easing = 'AUTO'


def render(out):
    s = bpy.context.scene
    still = os.environ.get('STILL')                 # STILL=프레임 → 그 프레임만 png 로 확인
    if still:
        s.frame_set(int(still)); s.render.image_settings.file_format = 'PNG'
        s.render.filepath = out; bpy.ops.render.render(write_still=True); return
    # PNG 연속 프레임으로 렌더 → ffmpeg 로 묶는다 (중간에 끊겨도 이어서 가능)
    s.render.image_settings.file_format = 'PNG'
    s.render.use_overwrite = False; s.render.use_placeholder = True
    s.render.filepath = out.rstrip('/') + '/f_'
    bpy.ops.render.render(animation=True)


def out_arg():
    return sys.argv[sys.argv.index('--') + 1]
