# 블렌더 3D 오프닝: 코스피 5거래일 하락 그래프가 바닥에서 솟아오르고 카메라가 마지막 점으로 다가간다.
# 실행: blender -b -P b01_kospi.py -- 출력폴더 [--test]
#   --test : 1프레임만 (렌더 시간 확인용)
# GPU 없음 → Cycles CPU. 1920×1080 · 30fps · 5초
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else '/tmp/b01'
TEST = '--test' in argv
FONT = os.path.expanduser('~/.fonts/NotoSansCJKkr-Black.otf')
FPS, SEC = 30, 4

DATA = [('10/2', 7003.74), ('10/6', 6941.39), ('10/7', 6803.90), ('10/8', 6625.93), ('10/12', 6384.24)]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 8
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.05
sc.cycles.use_denoising = True
sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.max_bounces = 4
sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 2
sc.cycles.transmission_bounces = 0
sc.cycles.volume_bounces = 0
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.render.use_persistent_data = True
sc.cycles.threads = 4
sc.render.threads_mode = 'FIXED'
sc.render.threads = 4
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, FPS * SEC
sc.render.film_transparent = False
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'Medium High Contrast'

world = bpy.data.worlds.new('w'); sc.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.007, 0.010, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0


def mat(name, color, emit=0.0, rough=0.35, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*color, 1)
        b.inputs['Emission Strength'].default_value = emit
    return m


BLUE = (0.10, 0.28, 1.0)
M_LINE = mat('line', BLUE, emit=2.2)
M_DOT = mat('dot', (0.55, 0.72, 1.0), emit=4)
M_BAR = mat('bar', (0.10, 0.16, 0.30), rough=0.25, metal=0.4)
M_FLOOR = mat('floor', (0.02, 0.022, 0.03), rough=0.18, metal=0.6)
M_TXT = mat('txt', (0.93, 0.94, 0.96), emit=0.6)
M_RED = mat('red', BLUE, emit=1.6)
M_GRID = mat('grid', (0.16, 0.18, 0.24), emit=0.8)

# 바닥 (반사)
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); bpy.context.object.data.materials.append(M_FLOOR)
# 바닥 격자
for i in range(-12, 13):
    for axis in (0, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 1.5 if axis == 0 else 0, 0 if axis == 0 else i * 1.5, 0.003))
        o = bpy.context.object
        o.scale = (0.012, 40, 0.004) if axis == 0 else (40, 0.012, 0.004)
        o.data.materials.append(M_GRID)

# 점 위치: x 간격 2.4, 높이는 값 범위를 0.6~4.6 으로
lo, hi = 6300, 7050
pts = [Vector(((i - 2) * 2.4, 0, 0.6 + (v - lo) / (hi - lo) * 4.0)) for i, (_, v) in enumerate(DATA)]

# 기둥 (값 높이까지, 프레임마다 자람)
for i, p in enumerate(pts):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p.x, 0, p.z / 2))
    b = bpy.context.object; b.scale = (0.9, 0.9, p.z); b.data.materials.append(M_BAR)
    start = 4 + i * 5
    b.scale.z = 0.001; b.location.z = 0; b.keyframe_insert('scale', frame=start); b.keyframe_insert('location', frame=start)
    b.scale.z = p.z; b.location.z = p.z / 2; b.keyframe_insert('scale', frame=start + 18); b.keyframe_insert('location', frame=start + 18)

# 선 (곡선 + 굵기, bevel_factor_end 로 그려지는 효과)
cu = bpy.data.curves.new('kline', 'CURVE'); cu.dimensions = '3D'
sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
for i, p in enumerate(pts):
    sp.points[i].co = (p.x, -0.55, p.z + 0.05, 1)
cu.bevel_depth = 0.07; cu.bevel_resolution = 6
cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=24)
cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=66)
line = bpy.data.objects.new('kline', cu); sc.collection.objects.link(line); cu.materials.append(M_LINE)

# 점과 날짜 라벨
def text(body, loc, size, m, rot=(math.radians(90), 0, 0), align='CENTER', extrude=0.02):
    td = bpy.data.curves.new(body, 'FONT'); td.body = body; td.font = bpy.data.fonts.load(FONT)
    td.size = size; td.align_x = align; td.extrude = extrude
    o = bpy.data.objects.new(body, td); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot; td.materials.append(m)
    return o

for i, ((d, v), p) in enumerate(zip(DATA, pts)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(p.x, -0.55, p.z + 0.05))
    s = bpy.context.object; s.data.materials.append(M_DOT)
    f = 24 + int(i * 10.5)
    s.scale = (0, 0, 0); s.keyframe_insert('scale', frame=f)
    s.scale = (1, 1, 1); s.keyframe_insert('scale', frame=f + 6)
    text(d, (p.x, -0.6, 0.05), 0.42, M_TXT, rot=(math.radians(90), 0, 0))
    lab = text(f'{v:,.0f}', (p.x, -0.6, p.z + 0.45), 0.36, M_TXT)
    lab.scale = (0, 0, 0); lab.keyframe_insert('scale', frame=f)
    lab.scale = (1, 1, 1); lab.keyframe_insert('scale', frame=f + 6)

# 큰 글씨: −3.65%  (마지막 점 위)
big = text('−3.65%', (pts[-1].x - 0.6, -1.6, pts[-1].z + 1.7), 1.6, M_RED, extrude=0.16)
big.scale = (0, 0, 0); big.keyframe_insert('scale', frame=72)
big.scale = (1.08, 1.08, 1.08); big.keyframe_insert('scale', frame=80)
big.scale = (1, 1, 1); big.keyframe_insert('scale', frame=84)
title = text('코스피 4일 연속 하락', (0, -0.6, 6.1), 0.62, M_TXT, extrude=0.04)

# 조명
bpy.ops.object.light_add(type='AREA', location=(0, -7, 9)); l = bpy.context.object; l.data.energy = 2200; l.data.size = 10
l.rotation_euler = (math.radians(35), 0, 0)
bpy.ops.object.light_add(type='AREA', location=(7, 3, 4)); l = bpy.context.object; l.data.energy = 600; l.data.color = (0.4, 0.55, 1.0)
l.rotation_euler = (math.radians(70), 0, math.radians(115))

# 카메라: 왼쪽 위에서 전체 → 마지막 점 쪽으로 다가감
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
cam.data.lens = 35; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0
target = bpy.data.objects.new('target', None); sc.collection.objects.link(target)
con = cam.constraints.new('TRACK_TO'); con.target = target; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
cam.data.dof.focus_object = target
for f, cl, tl in [(1, (-7.5, -15, 7.5), (-0.5, 0, 3.0)), (60, (-1.5, -12.5, 5.6), (1.6, 0, 2.8)), (120, (3.4, -8.6, 4.6), (4.2, 0, 2.6))]:
    cam.location = cl; cam.keyframe_insert('location', frame=f)
    target.location = tl; target.keyframe_insert('location', frame=f)
for o in (cam, target):
    if o.animation_data:
        for fc in o.animation_data.action.fcurves:
            for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.easing = 'EASE_IN_OUT'

os.makedirs(OUT, exist_ok=True)
if TEST:
    sc.frame_set(110); sc.render.filepath = os.path.join(OUT, 'test.png')
    bpy.ops.render.render(write_still=True)
else:
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, 'f_')
    bpy.ops.render.render(animation=True)
