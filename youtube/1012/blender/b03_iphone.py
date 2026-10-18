# 블렌더 3D: 아이폰18 프로 부품 주문 −15% → 메모리 칩 값↑ → LG이노텍 −16.2%
# 휴대폰이 돌며 들어오고, 뒤판에서 메모리 칩이 빠져나와 떠오른 뒤, 오른쪽에 큰 숫자가 찍힌다.
# 실행: blender -b -P b03_iphone.py -- 출력폴더 [--test]
import bpy, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUT, TEST = args()
sc = setup(sec=4)
floor(grid=True); lights()

M_BODY = mat('body', (0.55, 0.57, 0.62), rough=0.22, metal=1.0)
M_GLASS = mat('glass', (0.01, 0.012, 0.02), rough=0.05, metal=0.0)
M_SCR = mat('screen', (0.05, 0.12, 0.35), emit=1.2)
M_CAM = mat('cam', (0.02, 0.02, 0.025), rough=0.1, metal=0.5)
M_CHIP = mat('chip', (0.03, 0.035, 0.04), rough=0.4, metal=0.2)
M_PIN = mat('pin', (0.9, 0.7, 0.3), rough=0.25, metal=1.0)
M_T = mat('txt', WHITE, emit=0.6)
M_B = mat('blue', BLUE, emit=1.6)
M_R = mat('red', RED, emit=1.6)
M_Y = mat('yel', YEL, emit=1.4)

def part(kind, loc, scale, m, rot=(0, 0, 0), bevel=0.0, seg=3, **kw):
    if kind == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, location=loc, rotation=rot, **kw)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bev', 'BEVEL'); bv.width = bevel; bv.segments = seg
        bpy.ops.object.modifier_apply(modifier='bev')
    return o


def join(objs, origin):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.object
    bpy.context.scene.cursor.location = origin
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return o


# 휴대폰: 몸체 + 앞 화면(-y) + 뒤 카메라 섬과 렌즈 3개(+y)
P0 = (-2.6, 0, 3.0)
parts = [part('cube', P0, (3.1, 0.32, 6.3), M_BODY, bevel=0.35, seg=8),
         part('cube', (P0[0], -0.17, P0[2]), (2.8, 0.02, 6.0), M_SCR),
         part('cube', (P0[0] - 0.55, 0.19, P0[2] + 2.2), (1.4, 0.08, 1.4), M_GLASS, bevel=0.25, seg=6)]
for dx, dz in [(-0.85, 2.55), (-0.25, 2.55), (-0.55, 1.9)]:
    parts.append(part('cyl', (P0[0] + dx, 0.26, P0[2] + dz), (1, 1, 1), M_CAM, rot=(math.radians(90), 0, 0), radius=0.24, depth=0.1))
ph = join(parts, P0)
ph.rotation_euler = (0, 0, math.radians(-150)); ph.location = (-2.6, 2.5, 3.0)
ph.keyframe_insert('rotation_euler', frame=1); ph.keyframe_insert('location', frame=1)
ph.rotation_euler = (0, 0, math.radians(195)); ph.location = (-2.6, 0, 3.0)
ph.keyframe_insert('rotation_euler', frame=40); ph.keyframe_insert('location', frame=40)
ph.rotation_euler = (math.radians(3), 0, math.radians(200)); ph.keyframe_insert('rotation_euler', frame=120)

# 메모리 칩: 검은 패키지 + 금색 핀 + MEMORY 글씨 (앞면 -y)
C0 = (0.4, -0.8, 4.4)
cparts = [part('cube', C0, (1.6, 0.14, 1.05), M_CHIP, bevel=0.05)]
for i in range(9):
    for side in (-1, 1):
        cparts.append(part('cube', (C0[0] - 0.64 + i * 0.16, C0[1], C0[2] + side * 0.6), (0.07, 0.06, 0.16), M_PIN))
chip = join(cparts, C0)
lab = text('MEMORY', (C0[0], C0[1] - 0.09, C0[2]), 0.3, M_Y, extrude=0.01)
for o in (chip, lab):
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=44)
    loc = tuple(o.location); o.location = (-2.6, 0, 3.0); o.keyframe_insert('location', frame=44)
    o.scale = (1.4, 1.4, 1.4); o.keyframe_insert('scale', frame=62)
    o.location = loc; o.keyframe_insert('location', frame=62)

up = text('메모리 값 ↑', (0.4, -1.4, 5.75), 0.6, M_R, extrude=0.06); pop(up, 62)

# 오른쪽 글씨
t1 = text('부품 주문 15%↓', (3.6, -1.0, 4.9), 0.62, M_B, extrude=0.05); pop(t1, 24)
t2 = text('LG이노텍', (3.6, -1.0, 3.6), 0.62, M_T, extrude=0.04); pop(t2, 72)
t3 = text('−16.2%', (3.6, -1.2, 2.35), 1.35, M_B, extrude=0.14); pop(t3, 78)
t0 = text('아이폰18 프로', (-2.6, -1.4, 0.55), 0.5, M_T, extrude=0.03); pop(t0, 10)

camera([(1, (-1.5, -16.5, 4.2), (-1.4, 0, 3.6)),
        (70, (0.0, -15.8, 4.4), (0.2, 0, 3.7)),
        (120, (0.6, -15.0, 4.5), (0.4, 0, 3.7))], lens=40, fstop=5.6)
render(OUT, TEST, 105)
