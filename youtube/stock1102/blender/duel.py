# 증시 2026-11-02 '107조 vs 83조' 3D: 두 영업이익 탑이 자라고, 그 위에 다음 날 주가 화살표(하이닉스 +10.9% ↑, 삼성 −4.1% ↓).
# 숫자: SK하이닉스 3분기 영업이익 83조3338억 · 10/28 +10.89% / 삼성전자 107조4405억 · 10/29 −4.13% (stock1102/script.json _출처)
# blender -b --python duel.py -- 출력폴더
import bpy, sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../reels2/blender'))
from common import *

F = int(os.environ.get('FRAMES', 300))
s = reset(F, res=(1600, 900))
fnt = bpy.data.fonts.load(os.path.expanduser('~/.fonts/NotoSansCJKkr-Black.otf'))
K = 6.0 / 110

def text(body, loc, size, color, start, emit=3.5, rot=80):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body; cu.font = fnt; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .04
    o = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (math.radians(rot), 0, 0)
    o.data.materials.append(mat('m' + body, color, emit=emit))
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=start); o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=start + 8)
    return o

def tower(x, v, color, start, name):
    h = v * K
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0)); b = bpy.context.object
    assign(b, mat('b' + name, color, emit=.55, rough=.2))
    b.scale = (2.0, 2.0, .001); b.keyframe_insert('scale', frame=start); b.keyframe_insert('location', frame=start)
    b.scale = (2.0, 2.0, h); b.location.z = h / 2; b.keyframe_insert('scale', frame=start + 40); b.keyframe_insert('location', frame=start + 40)
    text(name, (x, -1.2, h + 1.45), .8, color, start + 38, emit=3.0)
    text(f"{v:g}조", (x, -1.2, h + .35), 1.1, '#ffffff', start + 38, emit=4.5)
    return h

def arrow3d(x, z0, up, color, start, label):
    bpy.ops.mesh.primitive_cone_add(radius1=.6, depth=1.0, location=(x, 0, z0)); c = bpy.context.object
    assign(c, mat('a' + label, color, emit=5))
    if not up: c.rotation_euler = (math.pi, 0, 0)
    c.scale = (0, 0, 0); c.keyframe_insert('scale', frame=start)
    c.scale = (1, 1, 1); c.keyframe_insert('scale', frame=start + 8)
    dz = 1.0 if up else -0.6
    c.location.z = z0; c.keyframe_insert('location', frame=start + 8)
    c.location.z = z0 + dz; c.keyframe_insert('location', frame=start + 30)
    text(label, (x + 2.3, -1.0, z0 + dz - .3), 1.1, color, start + 12, emit=5)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.03)); fl = bpy.context.object
fl.scale = (12, 5, .06); assign(fl, mat('floor', '#8d94a1', emit=.2, alpha=.2, rough=.1))
hs = tower(2.6, 107.4, '#6ea8ff', 15, "삼성전자")
hh = tower(-2.6, 83.3, '#c792ff', 45, "SK하이닉스")
text("3분기 영업이익", (0, 1.5, 11.2), .9, '#8d94a1', 10, emit=2)
arrow3d(-2.6, hh + 2.7, True, '#3ddc97', 130, "+10.9%")
arrow3d(2.6, hs + 3.6, False, '#ff5d73', 175, "−4.1%")
cam, tgt = camera((-9, -14, 2.0), (0, 0, 3.0), lens=32)
for f, loc, t in ((1, (-8.5, -15.5, 2.6), (0, 0, 3.4)), (120, (-2.0, -18.5, 5.0), (0, 0, 4.6)), (F, (3.0, -19.0, 6.0), (0, 0, 5.0))):
    cam.location = loc; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
light('AREA', (0, -7, 11), 1000, size=12); light('AREA', (8, 5, 5), 300, '#8d9bff', size=6)
smooth_keys()
render(out_arg())
