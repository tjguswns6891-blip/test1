# 증시 2026-10-24 '이번 주 성적표' 3D: 유리 바닥 위로 주간 등락률 막대가 위(초록)·아래(빨강)로 자란다.
# 숫자는 Yahoo 종가 10/16 → 10/23 (stock1024/script.json S6 와 같음).
# blender -b --python scorecard.py -- 출력폴더
import bpy, sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../reels2/blender'))
from common import *

F = int(os.environ.get('FRAMES', 270))
s = reset(F, res=(1600, 900))
fnt = bpy.data.fonts.load(os.path.expanduser('~/.fonts/NotoSansCJKkr-Black.otf'))
ROWS = [("나스닥", -0.71), ("S&P 500", -0.47), ("다우", 0.41), ("미국 반도체", -3.21),
        ("코스피", -2.08), ("코스닥", -5.42), ("삼성전자", 0.0), ("SK하이닉스", 0.39)]
K, GAP = 0.85, 1.65                                     # 1% → 높이, 막대 간격
x0 = -GAP * (len(ROWS) - 1) / 2

def text(body, loc, size, color, start, emit=3.5):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body; cu.font = fnt; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .03
    o = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (math.radians(80), 0, 0)
    o.data.materials.append(mat('m' + body, color, emit=emit))
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=start); o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=start + 8)
    return o

# 유리 바닥(0% 선)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.03)); fl = bpy.context.object
fl.scale = (GAP * len(ROWS) + .8, 2.6, .06); assign(fl, mat('floor', '#8d94a1', emit=.25, alpha=.18, rough=.1))
# 한국 / 미국 구역 띠
for xs, label, c in ((x0 + GAP * 1.5, "미국", '#6ea8ff'), (x0 + GAP * 5.5, "한국", '#ff9f43')):
    text(label, (xs, 1.4, 1.6), .8, c, 6, emit=2.5)
for i, (name, v) in enumerate(ROWS):
    x = x0 + GAP * i; st = 20 + i * 14
    c = '#3ddc97' if v > 0.05 else ('#ff5d73' if v < -0.05 else '#ffc53d')
    h = max(abs(v) * K, .08)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0)); b = bpy.context.object
    assign(b, mat('b' + name, c, emit=1.6, rough=.25))
    b.scale = (.9, .9, .001); b.location.z = 0; b.keyframe_insert('scale', frame=st); b.keyframe_insert('location', frame=st)
    b.scale = (.9, .9, h); b.location.z = h / 2 if v >= 0 else -h / 2
    b.keyframe_insert('scale', frame=st + 22); b.keyframe_insert('location', frame=st + 22)
    pct = ("+" if v > 0.05 else ("" if abs(v) < 0.05 else "−")) + f"{abs(v):.1f}%"
    zt = (h + .35) if v >= 0 else (-h - .75)
    text(pct, (x, -0.55, zt), .62, c, st + 20, emit=4)
    text(name, (x, -0.55, 0.3 if v < -0.05 else -0.85), .5, '#eef0f3', st + 4, emit=2.2)
# 카메라: 아래에서 올려다보다가 앞으로 이동
cam, tgt = camera((-9, -12, 1.0), (-3, 0, -0.5), lens=32)
for f, loc, t in ((1, (-9.5, -12.5, 0.8), (-3, 0, -0.6)), (130, (-2.5, -15.0, 2.6), (-0.5, 0, -1.2)), (F, (2.0, -15.5, 1.6), (0.8, 0, -1.4))):
    cam.location = loc; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
light('AREA', (0, -7, 9), 900, size=12); light('AREA', (8, 5, 4), 250, '#8d9bff', size=6)
smooth_keys()
render(out_arg())
