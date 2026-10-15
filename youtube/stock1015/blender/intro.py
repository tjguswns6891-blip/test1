# 증시 롱폼 인트로 3D: 지난 1년 미국(S&P 500, 파랑) vs 한국(코스피, 빨강) 리본 차트.
# 미국은 꾸준히 올라 꼭대기, 코스피는 산처럼 솟았다가 절벽처럼 떨어진다. 카메라가 옆으로 돌며 보여 준다.
# blender -b --python intro.py -- 출력폴더   (PNG 연속 프레임)
import bpy, sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../reels2/blender'))
from common import *
from mathutils import Vector

F = int(os.environ.get('FRAMES', 210))
s = reset(F, res=(1600, 900))
D = json.load(open(os.path.join(os.path.dirname(__file__), '../../raw/stock1015/invest/data.json')))
KT = json.load(open(os.path.join(os.path.dirname(__file__), '../../raw/stock1015/kospi_today.json')))
kos = D['daily']['kospi'] + [['2026-10-14', 6008.81], ['2026-10-15', KT['close']]]   # 10/15 은 오전 장중 값
spy = D['daily']['spx']
start = '2025-10-15'
def series(v):
    v = [x for x in v if x[0] >= start]
    step = max(1, len(v) // 70)
    v = v[::step] + ([v[-1]] if (len(v) - 1) % step else [])
    return [x[1] / v[0][1] for x in v]
L = 11.0
def ribbon(name, vals, y, color, k=1.6, delay=0):
    """선 아래를 채운 반투명 벽 + 빛나는 윗선(굵은 곡선). 왼쪽부터 자라난다."""
    n = len(vals); xs = [-L / 2 + L * i / (n - 1) for i in range(n)]; zs = [(v - 1) * k * 1.45 for v in vals]
    verts, faces = [], []
    for i, (x, z) in enumerate(zip(xs, zs)):
        verts += [(x, y, 0), (x, y, z)]
        if i: faces.append((2 * i - 2, 2 * i, 2 * i + 1, 2 * i - 1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    wall = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(wall)
    assign(wall, mat(name + 'm', color, emit=.35, alpha=.28, rough=.3))
    b = wall.modifiers.new('b', 'BUILD'); b.frame_start = 15 + delay; b.frame_duration = 110
    cu = bpy.data.curves.new(name + 'c', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .055; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(n - 1)
    for i, (x, z) in enumerate(zip(xs, zs)):
        sp.points[i].co = (x, y, z, 1)
    line = bpy.data.objects.new(name + 'L', cu); bpy.context.collection.objects.link(line)
    line.data.materials.append(mat(name + 'lm', color, emit=3.0))
    cu.bevel_factor_end = 0; cu.keyframe_insert('bevel_factor_end', frame=15 + delay)
    cu.bevel_factor_end = 1; cu.keyframe_insert('bevel_factor_end', frame=125 + delay)
    # 끝점 구슬
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.16, location=(xs[-1], y, zs[-1])); o = bpy.context.object
    assign(o, mat(name + 'dot', color, emit=6))
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=124 + delay); o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=132 + delay)
    return xs, zs

us = series(spy); kr = series(kos)
xu, zu = ribbon('us', us, -1.2, '#6ea8ff')
xk, zk = ribbon('kr', kr, 1.2, '#ff5d73', delay=6)
# 바닥 격자
bpy.ops.mesh.primitive_grid_add(x_subdivisions=30, y_subdivisions=12, size=16, location=(0, 0, -0.01))
g = bpy.context.object; g.scale = (1, .45, 1); gm = g.modifiers.new('w', 'WIREFRAME'); gm.thickness = .01
assign(g, mat('grid', '#232a38', emit=.6))
# 카메라: 앞쪽 낮게 → 옆으로 돌며 → 끝점 쪽
cam, tgt = camera((-9.5, -11.5, 3.2), (-1.5, 0, 1.5), lens=34)
for f, loc, t in ((1, (-9.5, -11.5, 3.2), (-2.5, 0, 1.2)), (110, (-2.0, -14.0, 5.2), (0.5, 0, 1.6)), (F, (6.5, -11.5, 4.4), (3.0, 0, 1.4))):
    cam.location = loc; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
light('AREA', (0, -6, 9), 900, size=10); light('AREA', (-8, 6, 5), 300, '#8d9bff', size=6)
smooth_keys()
print('US end', round(us[-1], 3), 'KR max', round(max(kr), 3), 'KR end', round(kr[-1], 3))
render(out_arg())
