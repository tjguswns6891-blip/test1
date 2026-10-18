# 블렌더 장면 공통: 렌더 설정(Cycles CPU, 빠른 설정), 재질, 3D 글씨, 바닥, 카메라 키프레임
import bpy, math, os, sys

FONT = os.path.expanduser('~/.fonts/NotoSansCJKkr-Black.otf')
BLUE = (0.10, 0.28, 1.0)     # 하락 #4c8dff 계열
RED = (1.0, 0.12, 0.14)      # 상승 #ff5a5f 계열
YEL = (1.0, 0.62, 0.05)      # 강조 #ffc53d 계열
WHITE = (0.93, 0.94, 0.96)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a[0] if a else '/tmp/bl'), ('--test' in a)


def setup(fps=30, sec=4, samples=8):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    c = sc.cycles
    c.device = 'CPU'; c.samples = samples
    c.use_adaptive_sampling = True; c.adaptive_threshold = 0.05
    c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'
    c.max_bounces = 4; c.diffuse_bounces = 2; c.glossy_bounces = 2
    c.transmission_bounces = 0; c.volume_bounces = 0
    c.caustics_reflective = False; c.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = fps
    sc.frame_start, sc.frame_end = 1, int(fps * sec)
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'Medium High Contrast'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.007, 0.010, 1)
    return sc


def mat(name, color, emit=0.0, rough=0.35, metal=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*color, 1)
        b.inputs['Emission Strength'].default_value = emit
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
    return m


def text(body, loc, size, m, rot=(math.radians(90), 0, 0), align='CENTER', extrude=0.02):
    td = bpy.data.curves.new(body, 'FONT'); td.body = body; td.font = bpy.data.fonts.load(FONT)
    td.size = size; td.align_x = align; td.align_y = 'CENTER'; td.extrude = extrude
    o = bpy.data.objects.new(body, td); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot; td.materials.append(m)
    return o


def floor(grid=True):
    m = mat('floor', (0.02, 0.022, 0.03), rough=0.18, metal=0.6)
    bpy.ops.mesh.primitive_plane_add(size=400); bpy.context.object.data.materials.append(m)
    if grid:
        g = mat('grid', (0.16, 0.18, 0.24), emit=0.8)
        for i in range(-14, 15):
            for ax in (0, 1):
                bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 1.5 if ax == 0 else 0, 0 if ax == 0 else i * 1.5, 0.003))
                o = bpy.context.object
                o.scale = (0.012, 44, 0.004) if ax == 0 else (44, 0.012, 0.004)
                o.data.materials.append(g)


def lights():
    bpy.ops.object.light_add(type='AREA', location=(0, -7, 9)); l = bpy.context.object
    l.data.energy = 2200; l.data.size = 10; l.rotation_euler = (math.radians(35), 0, 0)
    bpy.ops.object.light_add(type='AREA', location=(7, 3, 4)); l = bpy.context.object
    l.data.energy = 600; l.data.color = (0.4, 0.55, 1.0); l.rotation_euler = (math.radians(70), 0, math.radians(115))


def pop(o, f, dur=6, overshoot=1.08):
    s = tuple(o.scale)
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f)
    o.scale = tuple(v * overshoot for v in s); o.keyframe_insert('scale', frame=f + dur)
    o.scale = s; o.keyframe_insert('scale', frame=f + dur + 4)


def camera(keys, lens=35, fstop=4.0):
    """keys: [(frame, cam_loc, target_loc), ...]"""
    sc = bpy.context.scene
    bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
    cam.data.lens = lens; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = fstop
    tgt = bpy.data.objects.new('target', None); sc.collection.objects.link(tgt)
    con = cam.constraints.new('TRACK_TO'); con.target = tgt; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
    cam.data.dof.focus_object = tgt
    for f, cl, tl in keys:
        cam.location = cl; cam.keyframe_insert('location', frame=f)
        tgt.location = tl; tgt.keyframe_insert('location', frame=f)
    for o in (cam, tgt):
        for fc in o.animation_data.action.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = 'BEZIER'; k.easing = 'EASE_IN_OUT'
    return cam


def render(out, test, test_frame):
    sc = bpy.context.scene
    os.makedirs(out, exist_ok=True)
    if test:
        sc.frame_set(test_frame); sc.render.filepath = os.path.join(out, 'test.png')
        bpy.ops.render.render(write_still=True)
    else:
        sc.render.image_settings.file_format = 'PNG'
        sc.render.filepath = os.path.join(out, 'f_')
        bpy.ops.render.render(animation=True)
