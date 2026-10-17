# C-C: 이상 변압기. 1차 코일(촘촘) → 철심을 도는 자속 입자 → 2차 코일(성김)
# blender -b --python transformer.py -- out.mp4
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from common import *

N = int(os.environ.get('FRAMES', 180))
s = reset(N)
s.eevee.taa_render_samples = 8
VOLT, AMP, FLUX = '#7aa2ff', '#ff9f43', '#3ddc97'
W, H, T = 4.0, 3.0, 0.7                       # 철심 바깥 폭·높이, 두께

# 철심: 사각 틀 4개
core = mat('core', '#4a5162', metal=0.85, rough=0.38)
for (x, y, sx, sy) in ((-(W - T) / 2, 0, T, H), ((W - T) / 2, 0, T, H), (0, (H - T) / 2, W, T), (0, -(H - T) / 2, W, T)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, y)); c = bpy.context.object
    c.dimensions = (sx, T, sy); assign(c, core)
    bev = c.modifiers.new('b', 'BEVEL'); bev.width = 0.04; bev.segments = 3


def coil(name, xc, turns, color, height):
    """철심 다리를 감는 나선 (곡선 + 베벨)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.045; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); n = turns * 48
    sp.points.add(n - 1)
    r = T * 0.78
    for i in range(n):
        a = 2 * math.pi * i / 48
        sp.points[i].co = (xc + r * math.cos(a), r * math.sin(a), -height / 2 + height * i / (n - 1), 1)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    m = mat(name, color, emit=1.0, metal=0.6, rough=0.3)
    em = m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    d = em.driver_add('default_value').driver; d.type = 'SCRIPTED'
    d.expression = '0.35 + 1.5*abs(sin(frame/30*pi))'          # 교류: 1초에 한 주기 반짝임
    o.data.materials.append(m)
    return o

coil('primary', -(W - T) / 2, 12, VOLT, 2.0)      # 200회를 12감김으로
coil('secondary', (W - T) / 2, 3, AMP, 1.4)       # 50회를 3감김으로 (4:1)

# 자속 입자: 철심 중심선(앞면)을 따라 돈다. 위치를 프레임마다 직접 키로 넣는다
hw, hh = (W - T) / 2, (H - T) / 2
per = 2 * (2 * hw + 2 * hh)
def on_loop(u):                      # u: 둘레 위 거리 → (x, z), 왼쪽 아래에서 시계 방향(위로)
    u %= per
    for (x0, z0, dx, dz, L) in ((-hw, -hh, 0, 1, 2 * hh), (-hw, hh, 1, 0, 2 * hw), (hw, hh, 0, -1, 2 * hh), (hw, -hh, -1, 0, 2 * hw)):
        if u <= L: return x0 + dx * u, z0 + dz * u
        u -= L
    return -hw, -hh
fm = mat('flux', FLUX, emit=6)
speed = per / 60                      # 2초에 한 바퀴
for i in range(16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, segments=16, ring_count=8)
    b = bpy.context.object; assign(b, fm)
    for f in range(1, N + 1, 2):
        x, z = on_loop(i * per / 16 + speed * f)
        b.location = (x, -T / 2 - 0.08, z); b.keyframe_insert('location', frame=f)
    for fc in b.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'

camera((1.2, -8.6, 2.2), (0, 0, 0), lens=44)
light('AREA', (3, -5, 5), 700, size=6); light('AREA', (-5, -2, 2), 250, '#8d9bff', size=4)
render(out_arg())
