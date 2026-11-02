# 증시 2026-11-02 롱폼 인트로 3D: 지난주 코스피 종가(10/23 → 10/30)와 오늘(11/2) 마감을 롤러코스터 레일로 깔고, 구슬이 그 위를 달린다.
# 오른 날은 초록, 빠진 날은 빨강, 오늘은 노랑. 6000 높이에 반투명 판.
# blender -b --python intro.py -- 출력폴더   (PNG 연속 프레임)
import bpy, sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../reels2/blender'))
from common import *

F = int(os.environ.get('FRAMES', 300))
s = reset(F, res=(1600, 900))
TD = json.load(open(os.path.join(os.path.dirname(__file__), '../today.json'), encoding='utf-8'))
tc = TD['kospi']['close']; tp = 100 * (tc / 5730.74 - 1)
DAYS = [("월", 5469.47, -1.46), ("화", 5638.34, 3.09), ("수", 6012.44, 6.63), ("목", 5937.66, -1.24), ("금", 5730.74, -3.48),
        ("오늘", tc, tp)]
fnt = bpy.data.fonts.load(os.path.expanduser('~/.fonts/NotoSansCJKkr-Black.otf'))
L, K = 16.0, 6.0 / 600
def z(v): return (v - 5400) * K
xs = [-L / 2 + L * i / len(DAYS) for i in range(len(DAYS) + 1)]
vals = [5550.30] + [d[1] for d in DAYS]
seg = []
for i in range(len(DAYS)):
    a, b = vals[i], vals[i + 1]
    seg.append([(xs[i] + (xs[i + 1] - xs[i]) * t / 24, z(a + (b - a) * (1 - math.cos(math.pi * t / 24)) / 2)) for t in range(25)])

def tube(name, pts, color, start, dur):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .08; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for k, (x, zz) in enumerate(pts):
        sp.points[k].co = (x, 0, zz, 1)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(name + 'm', color, emit=3.2))
    cu.bevel_factor_end = 0; cu.keyframe_insert('bevel_factor_end', frame=start)
    cu.bevel_factor_end = 1; cu.keyframe_insert('bevel_factor_end', frame=start + dur)
    verts, faces = [], []
    for k, (x, zz) in enumerate(pts):
        verts += [(x, 0, 0), (x, 0, zz)]
        if k: faces.append((2 * k - 2, 2 * k, 2 * k + 1, 2 * k - 1))
    me = bpy.data.meshes.new(name + 'w'); me.from_pydata(verts, [], faces); me.update()
    w = bpy.data.objects.new(name + 'w', me); bpy.context.collection.objects.link(w)
    assign(w, mat(name + 'wm', color, emit=.4, alpha=.22, rough=.3))
    b = w.modifiers.new('b', 'BUILD'); b.frame_start = start; b.frame_duration = dur

def text(body, loc, size, color, start, emit=4.0):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body; cu.font = fnt; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .04
    o = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(mat('tm' + body, color, emit=emit))
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=start); o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=start + 8)

T0, PER = 20, 32
for d, ((wd, v, p), pts) in enumerate(zip(DAYS, seg)):
    st = T0 + d * PER
    c = '#ffc53d' if wd == "오늘" else ('#3ddc97' if p > 0 else '#ff5d73')
    tube('d%d' % d, pts, c, st, PER)
    xm = (pts[0][0] + pts[-1][0]) / 2
    text(wd if wd == "오늘" else wd + '요일', (xm, -0.6, -1.35), .75, '#c9ced8', st + 4, emit=2.5)
    text(("+" if p > 0 else "−") + f"{abs(p):.1f}%", (xm, -0.6, -0.45), .8, c, st + PER - 6)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, z(6000)))
p = bpy.context.object; p.scale = (L + 1.2, 3.2, 1); assign(p, mat('six', '#ffc53d', emit=.5, alpha=.12))
text("6,000", (-L / 2 + .9, -0.3, z(6000) + .3), .6, '#ffc53d', 8, emit=2.4)
allp = [q for sgm in seg for q in sgm]
bpy.ops.mesh.primitive_uv_sphere_add(radius=.24, location=(allp[0][0], 0, allp[0][1] + .2)); ball = bpy.context.object
assign(ball, mat('ball', '#ffffff', emit=6))
tot = T0 + len(DAYS) * PER
for f in range(T0, tot + 1, 2):
    u = (f - T0) / (tot - T0); x, zz = allp[min(len(allp) - 1, int(u * (len(allp) - 1)))]
    ball.location = (x, 0, zz + .26); ball.keyframe_insert('location', frame=f)
text(f"{tc:,.0f}", (allp[-1][0] + 1.0, 0, allp[-1][1] + .6), .7, '#ffffff', tot + 2, emit=5)
text("6,012", (xs[3], 0, z(6012.44) + .55), .6, '#3ddc97', T0 + 3 * PER, emit=4)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=10, size=24, location=(0, 0, -1.4))
g = bpy.context.object; g.scale = (1, .4, 1); gm = g.modifiers.new('w', 'WIREFRAME'); gm.thickness = .012
assign(g, mat('grid', '#232a38', emit=.6))
cam, tgt = camera((-12, -9, 4.5), (-6, 0, 3), lens=30)
keys = [(1, (-12, -13, 4.0), (-6.5, 0, 2.3))]
for d in range(len(DAYS)):
    f = T0 + d * PER + PER // 2; xm = (xs[d] + xs[d + 1]) / 2
    keys.append((f, (xm - 3.5, -14.0 + (d % 2) * .8, 4.4), (xm + .6, 0, 2.6)))
keys.append((F, (0.5, -18.0, 6.2), (0.5, 0, 2.8)))
for f, loc, t in keys:
    cam.location = loc; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
light('AREA', (0, -6, 10), 900, size=12); light('AREA', (-9, 6, 5), 300, '#8d9bff', size=6)
smooth_keys()
render(out_arg())
