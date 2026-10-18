# C-B: 3상 발전기. 자석(회전자)이 돌면 120°씩 떨어진 세 코일이 차례로 빛난다
# blender -b --python generator.py -- out.mp4
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from common import *

N = int(os.environ.get('FRAMES', 180))
s = reset(N)
s.eevee.taa_render_samples = 8
COLS = ['#7aa2ff', '#3ddc97', '#c792ff']
TURN = 90                                           # 한 바퀴 프레임 수

# 고정자 링
bpy.ops.mesh.primitive_torus_add(major_radius=2.25, minor_radius=0.22, major_segments=96, minor_segments=24)
assign(bpy.context.object, mat('stator', '#3a4150', metal=0.9, rough=0.35))

# 코일 6개(상마다 마주 보는 두 개). 발광 세기 = cos² 로 회전자 각도를 따라간다
for k in range(3):
    m = mat(f'coil{k}', COLS[k], emit=0.0, metal=0.3, rough=0.3)
    em = m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    m.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = hexrgb(COLS[k])
    d = em.driver_add('default_value').driver
    d.type = 'SCRIPTED'
    d.expression = f'0.15 + 2.6*cos(frame/{TURN}*2*pi - {k}*2*pi/3)**2'
    for side in (0, 1):
        ang = math.radians(90 - 120 * k + 180 * side)
        x, y = 1.55 * math.cos(ang), 1.55 * math.sin(ang)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.09, location=(x, y, 0))
        c = bpy.context.object; c.rotation_euler = (math.pi / 2, 0, ang + math.pi / 2); assign(c, m)
        # 코일 감긴 느낌: 같은 고리를 여러 겹
        for j in (-1, 1):
            c2 = c.copy(); c2.data = c.data; bpy.context.collection.objects.link(c2)
            c2.location = (x * (1 + 0.07 * j), y * (1 + 0.07 * j), 0)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x * 1.22, y * 1.22, 0))
        p = bpy.context.object; p.scale = (0.5, 0.5, 0.5); p.rotation_euler = (0, 0, ang)
        p.dimensions = (0.6, 0.34, 0.5); assign(p, mat(f'pole{k}{side}', '#2b313d', metal=0.8, rough=0.4))

# 회전자: 막대자석 (N 빨강, S 파랑)
rotor = bpy.data.objects.new('rotor', None); bpy.context.collection.objects.link(rotor)
for col, sgn, nm in (('#ff5a5f', 1, 'N'), ('#4c8dff', -1, 'S')):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, sgn * 0.5, 0))
    b = bpy.context.object; b.dimensions = (0.42, 1.0, 0.42); assign(b, mat(nm, col, emit=0.6, rough=0.35)); b.parent = rotor
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.2, location=(0, 0, 0))
assign(bpy.context.object, mat('shaft', '#cfd5df', metal=1, rough=0.2))
rotor.rotation_euler = (0, 0, 0); rotor.keyframe_insert('rotation_euler', frame=1)
rotor.rotation_euler = (0, 0, -2 * math.pi * (N - 1) / TURN); rotor.keyframe_insert('rotation_euler', frame=N)
for fc in rotor.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'

# 120° 표시 호 (바닥에 얇게)
for k in range(3):
    ang = math.radians(90 - 120 * k)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=2.0, location=(1.0 * math.cos(ang), 1.0 * math.sin(ang), -0.45))
    l = bpy.context.object; l.rotation_euler = (math.pi / 2, 0, ang + math.pi / 2); assign(l, mat(f'ray{k}', COLS[k], emit=2))

camera((0, -5.4, 5.6), (0, 0.15, 0), lens=40)
light('AREA', (3, -4, 6), 500, size=6); light('AREA', (-4, 2, 3), 200, '#8d9bff', size=4)
render(out_arg())
