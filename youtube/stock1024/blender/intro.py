# 증시 2026-10-24 롱폼 인트로 3D: 이번 주 코스피 5분봉(10/19~10/23)을 롤러코스터 레일로 깔고, 구슬이 그 위를 달린다.
# 오른 날은 초록, 빠진 날은 빨강. 레일 아래에 요일·등락률 3D 글자, 지난주 종가(5668) 높이에 반투명 판.
# blender -b --python intro.py -- 출력폴더   (PNG 연속 프레임)
import bpy, sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../reels2/blender'))
from common import *
from mathutils import Vector

F = int(os.environ.get('FRAMES', 300))
s = reset(F, res=(1600, 900))
R = os.path.join(os.path.dirname(__file__), '../../raw/stock1024/')
rows = json.load(open(R + 'intra_KS11.json'))            # [["10-19 09:00", 값], ...] Yahoo 5분봉
PREV = 5668.05                                           # 10/16(금) 종가
DAYS = [("10-19", "월", "+1.8%", '#3ddc97'), ("10-20", "화", "−3.7%", '#ff5d73'), ("10-21", "수", "+3.3%", '#3ddc97'),
        ("10-22", "목", "−3.5%", '#ff5d73'), ("10-23", "금", "+0.3%", '#3ddc97')]
FONT = os.path.expanduser('~/.fonts/NotoSansCJKkr-Black.otf')
fnt = bpy.data.fonts.load(FONT)
L, K = 16.0, 6.5 / 500                                    # 레일 길이, 지수 1포인트 → 높이
def z(v): return (v - 5300) * K
seg = []                                                  # 날마다 점 목록 (x, z)
n_all = len(rows); i = 0
for key, *_ in DAYS:
    pts = [r for r in rows if r[0].startswith(key)]
    seg.append([(-L / 2 + L * (i + j) / (n_all - 1), z(v)) for j, (_, v) in enumerate(pts)]); i += len(pts)
for a, b in zip(seg, seg[1:]):                             # 날 사이 이음
    a.append(b[0])

def tube(name, pts, color, start, dur):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .07; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for k, (x, zz) in enumerate(pts):
        sp.points[k].co = (x, 0, zz, 1)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(name + 'm', color, emit=3.2))
    cu.bevel_factor_end = 0; cu.keyframe_insert('bevel_factor_end', frame=start)
    cu.bevel_factor_end = 1; cu.keyframe_insert('bevel_factor_end', frame=start + dur)
    # 레일 아래 반투명 벽 (바닥까지)
    verts, faces = [], []
    for k, (x, zz) in enumerate(pts):
        verts += [(x, 0, 0), (x, 0, zz)]
        if k: faces.append((2 * k - 2, 2 * k, 2 * k + 1, 2 * k - 1))
    me = bpy.data.meshes.new(name + 'w'); me.from_pydata(verts, [], faces); me.update()
    w = bpy.data.objects.new(name + 'w', me); bpy.context.collection.objects.link(w)
    assign(w, mat(name + 'wm', color, emit=.4, alpha=.22, rough=.3))
    b = w.modifiers.new('b', 'BUILD'); b.frame_start = start; b.frame_duration = dur
    return o

def text(body, loc, size, color, start, emit=4.0, rot=(math.radians(90), 0, 0)):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body; cu.font = fnt; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .04
    o = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    o.data.materials.append(mat('tm' + body, color, emit=emit))
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=start); o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=start + 8)
    return o

T0, PER = 20, 34                                          # 하루 그리는 데 34프레임
for d, ((key, wd, pct, c), pts) in enumerate(zip(DAYS, seg)):
    st = T0 + d * PER
    tube('d' + key, pts, c, st, PER)
    xm = (pts[0][0] + pts[-1][0]) / 2
    text(wd + '요일', (xm, -0.6, -1.25), .55, '#c9ced8', st + 4, emit=2.5)
    text(pct, (xm, -0.6, -0.45), .85, c, st + PER - 6)
# 지난주 종가 판
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, z(PREV)))
p = bpy.context.object; p.scale = (L + 1.2, 3.2, 1); assign(p, mat('prev', '#ffc53d', emit=.5, alpha=.12))
text("지난주 종가 5,668", (-L / 2 + 1.6, -0.3, z(PREV) + 2.3), .5, '#ffc53d', 8, emit=2.2)
# 구슬: 레일을 따라 달린다 (그리는 끝을 따라감)
allp = [q for sgm in seg for q in sgm]
bpy.ops.mesh.primitive_uv_sphere_add(radius=.22, location=(allp[0][0], 0, allp[0][1] + .2)); ball = bpy.context.object
assign(ball, mat('ball', '#ffffff', emit=6))
tot = T0 + 5 * PER
for f in range(T0, tot + 1, 2):
    u = (f - T0) / (tot - T0); x, zz = allp[min(len(allp) - 1, int(u * (len(allp) - 1)))]
    ball.location = (x, 0, zz + .24); ball.keyframe_insert('location', frame=f)
# 끝 라벨
text("5,550", (allp[-1][0] + .9, 0, allp[-1][1] + .55), .7, '#ffffff', tot + 2, emit=5)
# 바닥 격자
bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=10, size=24, location=(0, 0, -1.4))
g = bpy.context.object; g.scale = (1, .4, 1); gm = g.modifiers.new('w', 'WIREFRAME'); gm.thickness = .012
assign(g, mat('grid', '#232a38', emit=.6))
# 카메라: 레일을 비스듬히 따라가다가 마지막에 뒤로 빠져 전체를 본다
cam, tgt = camera((-12, -9, 4.5), (-6, 0, 3), lens=30)
keys = [(1, (-12, -13, 4.0), (-6.5, 0, 2.3))]
for d in range(5):
    f = T0 + d * PER + PER // 2; xm = -L / 2 + L * (d + .5) / 5
    keys.append((f, (xm - 3.5, -14.0 + (d % 2) * .8, 4.2), (xm + .6, 0, 2.3)))
keys.append((F, (0.5, -17.5, 6.0), (0.5, 0, 2.6)))
for f, loc, t in keys:
    cam.location = loc; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
light('AREA', (0, -6, 10), 900, size=12); light('AREA', (-9, 6, 5), 300, '#8d9bff', size=6)
smooth_keys()
render(out_arg())
