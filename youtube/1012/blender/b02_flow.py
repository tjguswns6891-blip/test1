# 블렌더 3D: 10/12 코스피 투자자별 순매매 — 외국인 −2.02조(파랑) · 기관 −1,107억(회색) · 개인 +1.47조(빨강)
# 막대가 차례로 솟고, 외국인 막대 위에서 동전이 튀어 개인 막대 위로 쌓인다.
# 실행: blender -b -P b02_flow.py -- 출력폴더 [--test]
import bpy, math, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUT, TEST = args()
sc = setup(sec=4)
floor(); lights()
random.seed(7)

M_F = mat('for', BLUE, emit=1.4, rough=0.2, metal=0.3)
M_P = mat('per', RED, emit=1.4, rough=0.2, metal=0.3)
M_I = mat('ins', (0.45, 0.48, 0.55), emit=0.4, rough=0.3)
M_T = mat('txt', WHITE, emit=0.6)
M_C = mat('coin', YEL, emit=0.9, rough=0.25, metal=0.8)

UNIT = 2.2   # 1조 = 높이 2.2
cols = [('외국인', -2.0186, M_F, -3.6), ('기관', -0.1107, M_I, 0.0), ('개인', 1.4674, M_P, 3.6)]
for i, (name, v, m, x) in enumerate(cols):
    h = max(abs(v) * UNIT, 0.05)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0))
    b = bpy.context.object; b.data.materials.append(m)
    bev = b.modifiers.new('bev', 'BEVEL'); bev.width = 0.06; bev.segments = 3
    f0 = 10 + i * 8
    b.scale = (1.6, 1.6, 0.001); b.location.z = 0
    b.keyframe_insert('scale', frame=f0); b.keyframe_insert('location', frame=f0)
    b.scale = (1.6, 1.6, h); b.location.z = h / 2
    b.keyframe_insert('scale', frame=f0 + 26); b.keyframe_insert('location', frame=f0 + 26)
    lab = text(name, (x, -2.3, 0.42), 0.62, M_T, extrude=0.03)
    pop(lab, f0 + 4)
    val = ('+' if v > 0 else '−') + (f'{abs(v):.2f}조' if abs(v) >= 1 else f'{abs(v) * 10000:,.0f}억')
    vt = text(val, (x, -0.2, h + 0.75), 0.82, m, extrude=0.08)
    pop(vt, f0 + 24)

# 동전: 외국인 막대 위 → 가운데 높이 → 개인 막대 위
for k in range(14):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.06, vertices=32, location=(-3.6, 0, 4.0))
    c = bpy.context.object; c.data.materials.append(M_C)
    f = 34 + k * 3
    end_z = 1.4674 * UNIT + 0.1 + (k % 5) * 0.07
    c.location = (-3.6 + random.uniform(-.4, .4), random.uniform(-.3, .3), 2.0186 * UNIT - 0.2); c.keyframe_insert('location', frame=f)
    c.rotation_euler = (0, 0, 0); c.keyframe_insert('rotation_euler', frame=f)
    c.location = (0, 0.4, 6.0 + random.uniform(0, .6)); c.keyframe_insert('location', frame=f + 9)
    c.location = (3.6 + random.uniform(-.45, .45), 0.3 + random.uniform(-.3, .3), end_z); c.keyframe_insert('location', frame=f + 18)
    c.rotation_euler = (random.uniform(3, 7), random.uniform(1, 4), 0); c.keyframe_insert('rotation_euler', frame=f + 18)
    c.scale = (0, 0, 0); c.keyframe_insert('scale', frame=f - 1)
    c.scale = (1, 1, 1); c.keyframe_insert('scale', frame=f)

text('10/12 코스피 투자자별 순매매', (0, 0.6, 7.0), 0.6, M_T, extrude=0.03)

camera([(1, (-7.5, -14.0, 2.6), (-3.0, 0, 2.2)),
        (60, (-2.0, -15.0, 4.0), (-0.5, 0, 2.8)),
        (120, (0.8, -15.5, 4.6), (0.2, 0, 3.0))])
render(OUT, TEST, 105)
