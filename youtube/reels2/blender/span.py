# L-A: 벡터 세 개가 만드는 상자 → 셋째 벡터가 평면으로 들어가며 상자가 납작해진다 (일차종속)
# blender -b --python span.py -- out.mp4
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from mathutils import Vector

s = reset(int(os.environ.get("FRAMES", 180)))
v1, v2, v3 = Vector((2.2, 0, 0)), Vector((0.5, 2.0, 0)), Vector((0.4, 0.6, 2.0))
v3f = 0.5 * v1 + 0.5 * v2                                       # 납작해진 셋째 벡터

E1, E2, E3 = mat('e1', '#ff8f57', emit=1.6), mat('e2', '#3fd5bd', emit=1.6), mat('e3', '#d391ff', emit=1.8)
arrow('v1', (0, 0, 0), v1, E1); arrow('v2', (0, 0, 0), v2, E2)
a3 = arrow('v3', (0, 0, 0), v3, E3)
point(a3, (0, 0, 0), v3, frame=75); point(a3, (0, 0, 0), v3f, frame=135)

# 평행육면체: 꼭짓점 = 세 벡터의 0/1 조합. shape key 로 납작한 모양을 만든다
def corners(c):
    return [a * v1 + b * v2 + d * c for d in (0, 1) for b in (0, 1) for a in (0, 1)]
faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
me = bpy.data.meshes.new('box'); me.from_pydata([tuple(p) for p in corners(v3)], [], faces); me.update()
box = bpy.data.objects.new('box', me); bpy.context.collection.objects.link(box)
assign(box, mat('glass', '#8d9bff', emit=0.25, alpha=0.22, rough=0.2))
box.shape_key_add(name='base'); k = box.shape_key_add(name='flat')
for i, p in enumerate(corners(v3f)): k.data[i].co = p
k.value = 0; k.keyframe_insert('value', frame=75); k.value = 1; k.keyframe_insert('value', frame=135)
# 상자 모서리 (와이어)
wire = box.copy(); wire.data = box.data; bpy.context.collection.objects.link(wire)
wm = wire.modifiers.new('w', 'WIREFRAME'); wm.thickness = 0.025
mw = mat('edge', '#b7c0ff', emit=2.2)                    # 메시를 공유하므로 재질은 오브젝트 쪽에 건다
wire.material_slots[0].link = 'OBJECT'; wire.material_slots[0].material = mw

# 바닥 격자
bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=24, size=12, location=(0.8, 0.8, -0.002))
g = bpy.context.object; gm = g.modifiers.new('w', 'WIREFRAME'); gm.thickness = 0.008
assign(g, mat('grid', '#2a3346', emit=0.6))
# 원점
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(0, 0, 0)); assign(bpy.context.object, mat('o', '#eef0f3', emit=1))

cam, tgt = camera((7.5, -6.2, 4.6), (1.1, 1.0, 0.6), lens=42)
tgt.location = (1.1, 1.0, 0.6)
# 천천히 공전
cam.location = (7.5, -6.2, 4.6); cam.keyframe_insert('location', frame=1)
cam.location = (8.6, -3.6, 4.0); cam.keyframe_insert('location', frame=180)
light('AREA', (4, -4, 7), 600, size=6); light('AREA', (-5, 3, 4), 250, '#8d9bff', size=5)
smooth_keys()
render(out_arg())
