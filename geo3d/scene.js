// 장면 JSON → Three.js 렌더링 (z축이 위쪽)
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";

const v = (a) => new THREE.Vector3(a[0], a[1], a[2]);

// 법선 n에 수직인 정규직교 기저 (u, w)
function planeBasis(n) {
  const nn = n.clone().normalize();
  const helper = Math.abs(nn.z) < 0.9 ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0);
  const u = new THREE.Vector3().crossVectors(helper, nn).normalize();
  const w = new THREE.Vector3().crossVectors(nn, u).normalize();
  return { n: nn, u, w };
}

function circlePoints(center, normal, r, seg = 160) {
  const { u, w } = planeBasis(normal);
  const pts = [];
  for (let i = 0; i <= seg; i++) {
    const t = (i / seg) * Math.PI * 2;
    pts.push(center.clone().addScaledVector(u, r * Math.cos(t)).addScaledVector(w, r * Math.sin(t)));
  }
  return pts;
}

export class GeoViewer {
  constructor(container) {
    this.container = container;
    this.items = new Map(); // id → { objs: Object3D[], mats: Material[] }
    this.labels = [];
    this.lineMats = [];
    this.ortho = false;

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(this.renderer.domElement);

    this.labelRenderer = new CSS2DRenderer();
    this.labelRenderer.domElement.className = "label-layer";
    container.appendChild(this.labelRenderer.domElement);

    this.scene = new THREE.Scene();
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.75));
    const dl = new THREE.DirectionalLight(0xffffff, 0.9);
    dl.position.set(5, -8, 12);
    this.scene.add(dl);

    this.root = new THREE.Group();
    this.scene.add(this.root);
    this.axes = this.makeAxes(8);
    this.scene.add(this.axes);
    this.setAxes(false);

    this.persp = new THREE.PerspectiveCamera(40, 1, 0.1, 2000);
    this.orthoCam = new THREE.OrthographicCamera(-1, 1, 1, -1, -2000, 2000);
    for (const c of [this.persp, this.orthoCam]) c.up.set(0, 0, 1);
    this.camera = this.persp;
    this.controls = new OrbitControls(this.camera, this.labelRenderer.domElement);
    this.controls.enableDamping = true;

    this.center = new THREE.Vector3();
    this.radius = 10;
    this.anim = null;

    new ResizeObserver(() => this.resize()).observe(container);
    this.resize();
    this.renderer.setAnimationLoop(() => this.tick());
  }

  makeAxes(len) {
    const g = new THREE.Group();
    const defs = [
      ["x", [len, 0, 0], 0xd9534f],
      ["y", [0, len, 0], 0x3fa34d],
      ["z", [0, 0, len], 0x4c7bd9],
    ];
    for (const [name, end, color] of defs) {
      const geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), v(end)]);
      g.add(new THREE.Line(geo, new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.5 })));
      const lab = this.makeLabel(name, "axis");
      lab.position.copy(v(end).multiplyScalar(1.05));
      g.add(lab);
    }
    g.visible = false;
    return g;
  }

  makeLabel(text, cls = "") {
    const el = document.createElement("div");
    el.className = "lbl " + cls;
    el.textContent = text;
    const o = new CSS2DObject(el);
    o.center.set(-0.15, 1.1);
    return o;
  }

  lineMat(color, dashed, width = 2.5) {
    const m = new LineMaterial({
      color: new THREE.Color(color),
      linewidth: width,
      dashed,
      dashSize: 0.35,
      gapSize: 0.22,
      transparent: true,
      opacity: 1,
      worldUnits: false,
    });
    m.userData.baseOpacity = 1;
    m.userData.baseWidth = width;
    m.resolution.set(this.w || 1, this.h || 1);
    this.lineMats.push(m);
    return m;
  }

  polyline(pts, color, dashed = false, width = 2.5) {
    const geo = new LineGeometry();
    geo.setPositions(pts.flatMap((p) => [p.x, p.y, p.z]));
    const line = new Line2(geo, this.lineMat(color, dashed, width));
    if (dashed) line.computeLineDistances();
    return line;
  }

  fillMat(color, opacity) {
    const m = new THREE.MeshPhongMaterial({
      color: new THREE.Color(color),
      transparent: true,
      opacity,
      side: THREE.DoubleSide,
      depthWrite: false,
      shininess: 20,
    });
    m.userData.baseOpacity = opacity;
    return m;
  }

  register(id, objs, kind, label) {
    for (const o of objs) this.root.add(o);
    const mats = [];
    for (const o of objs)
      o.traverse((c) => {
        if (c.material) mats.push(c.material);
      });
    this.items.set(id, { objs, mats, kind, label: label || id, visible: true });
  }

  clear() {
    this.root.traverse((o) => {
      o.geometry?.dispose?.();
      o.material?.dispose?.();
      if (o.isCSS2DObject) o.element.remove();
    });
    this.root.clear();
    this.items.clear();
    this.lineMats = [];
  }

  load(data) {
    this.clear();
    this.data = data;
    const P = new Map(data.points.map((p) => [p.name, v(p.coord)]));
    this.pointMap = P;
    const planeById = new Map(data.planes.map((p) => [p.id, p]));

    // 평면
    for (const pl of data.planes) {
      const { n, u, w } = planeBasis(v(pl.normal));
      const c = v(pl.point);
      const half = pl.size / 2;
      const geo = new THREE.PlaneGeometry(pl.size, pl.size);
      const mesh = new THREE.Mesh(geo, this.fillMat(pl.color, 0.16));
      mesh.position.copy(c);
      mesh.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(u, w, n));
      const corners = [
        [-1, -1],
        [1, -1],
        [1, 1],
        [-1, 1],
        [-1, -1],
      ].map(([a, b]) => c.clone().addScaledVector(u, a * half).addScaledVector(w, b * half));
      const edge = this.polyline(corners, pl.color, false, 1.2);
      const lab = this.makeLabel(pl.label, "plane");
      lab.position.copy(corners[2]);
      this.register(pl.id, [mesh, edge, lab], "평면", pl.label);
    }

    // 구
    for (const s of data.spheres) {
      const c = v(s.center);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(s.radius, 64, 48), this.fillMat(s.color, 0.1));
      mesh.position.copy(c);
      const rings = [];
      for (let k = -2; k <= 2; k++) {
        const h = (k / 3) * s.radius;
        const r = Math.sqrt(s.radius ** 2 - h * h);
        rings.push(this.polyline(circlePoints(c.clone().add(new THREE.Vector3(0, 0, h)), new THREE.Vector3(0, 0, 1), r), s.color, false, 0.8));
      }
      for (let k = 0; k < 3; k++) {
        const a = (k / 3) * Math.PI;
        rings.push(this.polyline(circlePoints(c, new THREE.Vector3(Math.cos(a), Math.sin(a), 0), s.radius), s.color, false, 0.8));
      }
      for (const r of rings) {
        r.material.opacity = r.material.userData.baseOpacity = 0.35;
      }
      const lab = this.makeLabel(s.label, "obj");
      lab.position.copy(c).add(new THREE.Vector3(s.radius * 0.72, -s.radius * 0.2, s.radius * 0.72));
      this.register(s.id, [mesh, ...rings, lab], "구", s.label);
    }

    // 원
    for (const ci of data.circles) {
      const pts = circlePoints(v(ci.center), v(ci.normal), ci.radius);
      const line = this.polyline(pts, ci.color, ci.style === "dashed", 3);
      const lab = this.makeLabel(ci.label, "obj");
      lab.position.copy(pts[Math.floor(pts.length * 0.62)]);
      this.register(ci.id, [line, lab], "원", ci.label);
    }

    // 다각형
    for (const pg of data.polygons) {
      const pts = pg.vertices.map((n) => P.get(n)).filter(Boolean);
      if (pts.length < 3) continue;
      const pos = [];
      for (let i = 1; i < pts.length - 1; i++) for (const p of [pts[0], pts[i], pts[i + 1]]) pos.push(p.x, p.y, p.z);
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
      geo.computeVertexNormals();
      const mesh = new THREE.Mesh(geo, this.fillMat(pg.color, pg.opacity || 0.2));
      this.register(pg.id, [mesh], "다각형", pg.vertices.join(""));
    }

    // 선분
    for (const sg of data.segments) {
      const a = P.get(sg.from),
        b = P.get(sg.to);
      if (!a || !b) continue;
      this.register(sg.id, [this.polyline([a, b], sg.color, sg.style === "dashed", sg.style === "dashed" ? 2 : 3)], "선분", sg.from + sg.to);
    }

    // 직선
    const span = this.estimateSpan(data);
    for (const ln of data.lines) {
      const p = v(ln.point);
      const d = v(ln.direction).normalize();
      const a = p.clone().addScaledVector(d, -span * 0.6);
      const b = p.clone().addScaledVector(d, span * 0.6);
      const lab = this.makeLabel(ln.label, "obj");
      lab.position.copy(b);
      this.register(ln.id, [this.polyline([a, b], ln.color, false, 2.5), lab], "직선", ln.label);
    }

    // 정사영
    for (const pr of data.projections) {
      const pl = planeById.get(pr.planeId);
      if (!pl) continue;
      const src = this.sourcePoints(pr.sourceId, P);
      if (!src) continue;
      const n = v(pl.normal).normalize();
      const p0 = v(pl.point);
      const proj = src.pts.map((p) => p.clone().addScaledVector(n, -p.clone().sub(p0).dot(n)));
      const objs = [this.polyline(proj, pr.color, false, 3)];
      if (src.closed && proj.length > 3) {
        const c = proj.reduce((s, p) => s.add(p), new THREE.Vector3()).multiplyScalar(1 / proj.length);
        const pos = [];
        for (let i = 0; i < proj.length - 1; i++) for (const p of [c, proj[i], proj[i + 1]]) pos.push(p.x, p.y, p.z);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
        objs.push(new THREE.Mesh(geo, this.fillMat(pr.color, 0.25)));
      }
      // 사영 방향을 보여주는 점선 몇 개
      const step = Math.max(1, Math.floor(src.pts.length / 8));
      for (let i = 0; i < src.pts.length - (src.closed ? 1 : 0); i += step) {
        const l = this.polyline([src.pts[i], proj[i]], pr.color, true, 1);
        l.material.opacity = l.material.userData.baseOpacity = 0.55;
        objs.push(l);
      }
      const lab = this.makeLabel(pr.label, "obj proj");
      lab.position.copy(proj[Math.floor(proj.length * 0.3)]);
      objs.push(lab);
      this.register(pr.id, objs, "정사영", pr.label);
    }

    // 점
    const ptR = Math.max(0.06, span * 0.008);
    for (const p of data.points) {
      const pos = P.get(p.name);
      const dot = new THREE.Mesh(new THREE.SphereGeometry(ptR, 16, 12), new THREE.MeshBasicMaterial({ color: 0x1b1f27, transparent: true }));
      dot.material.userData.baseOpacity = 1;
      dot.userData.isPoint = true;
      dot.position.copy(pos);
      const objs = [dot];
      if (p.showLabel) {
        const lab = this.makeLabel(p.name, "pt");
        lab.position.copy(pos);
        objs.push(lab);
      }
      this.register(p.name, objs, "점", p.name);
    }

    this.fit();
    this.setView("iso", false);
    this.applyHighlight([]);
  }

  sourcePoints(id, P) {
    const ci = this.data.circles.find((c) => c.id === id);
    if (ci) return { pts: circlePoints(v(ci.center), v(ci.normal), ci.radius), closed: true };
    const sg = this.data.segments.find((s) => s.id === id);
    if (sg && P.get(sg.from) && P.get(sg.to)) return { pts: [P.get(sg.from), P.get(sg.to)], closed: false };
    const pg = this.data.polygons.find((s) => s.id === id);
    if (pg) {
      const pts = pg.vertices.map((n) => P.get(n)).filter(Boolean);
      return { pts: [...pts, pts[0]], closed: true };
    }
    return null;
  }

  estimateSpan(data) {
    const box = new THREE.Box3();
    data.points.forEach((p) => box.expandByPoint(v(p.coord)));
    const addBall = (c, r) => box.union(new THREE.Sphere(v(c), r).getBoundingBox(new THREE.Box3()));
    data.spheres.forEach((s) => addBall(s.center, s.radius));
    data.circles.forEach((c) => addBall(c.center, c.radius));
    if (box.isEmpty()) return 10;
    return Math.max(4, box.getSize(new THREE.Vector3()).length());
  }

  fit() {
    const box = new THREE.Box3();
    for (const [, it] of this.items) if (it.kind !== "평면" && it.kind !== "직선") for (const o of it.objs) box.expandByObject(o);
    if (box.isEmpty()) box.setFromCenterAndSize(new THREE.Vector3(), new THREE.Vector3(10, 10, 10));
    const s = box.getBoundingSphere(new THREE.Sphere());
    this.center.copy(s.center);
    this.radius = Math.max(2, s.radius);
    this.axes.scale.setScalar(this.radius / 8);
  }

  viewDir(name) {
    if (name === "top") return new THREE.Vector3(0, -0.0001, 1);
    if (name === "front") return new THREE.Vector3(0, -1, 0.0001);
    if (name === "side") return new THREE.Vector3(1, 0, 0.0001);
    if (name?.startsWith("normal:")) {
      const pl = this.data?.planes.find((p) => p.id === name.slice(7));
      if (pl) {
        const n = v(pl.normal).normalize();
        // 현재 카메라 쪽에 있는 면에서 바라본다
        const cur = this.camera.position.clone().sub(this.center);
        if (n.dot(cur) < 0) n.negate();
        if (Math.abs(n.z) > 0.999) n.y -= 0.0001;
        return n.normalize();
      }
    }
    return new THREE.Vector3(1.1, -1.6, 0.95);
  }

  setView(name, animate = true) {
    const dir = this.viewDir(name).normalize();
    const dist = this.radius * 2.9;
    const to = this.center.clone().addScaledVector(dir, dist);
    if (!animate) {
      this.camera.position.copy(to);
      this.controls.target.copy(this.center);
      this.updateOrtho();
      return;
    }
    this.anim = {
      t0: performance.now(),
      fromPos: this.camera.position.clone(),
      fromTarget: this.controls.target.clone(),
      toPos: to,
      toTarget: this.center.clone(),
    };
  }

  setOrtho(on) {
    const pos = this.camera.position.clone();
    const target = this.controls.target.clone();
    this.ortho = on;
    this.camera = on ? this.orthoCam : this.persp;
    this.camera.position.copy(pos);
    this.controls.object = this.camera;
    this.controls.target.copy(target);
    this.updateOrtho();
    this.resize();
  }

  updateOrtho() {
    if (!this.ortho) return;
    const d = this.camera.position.distanceTo(this.controls.target);
    const h = d * Math.tan(THREE.MathUtils.degToRad(20));
    const a = (this.w || 1) / (this.h || 1);
    Object.assign(this.orthoCam, { left: -h * a, right: h * a, top: h, bottom: -h });
    this.orthoCam.updateProjectionMatrix();
  }

  setAxes(on) {
    this.axes.visible = on;
    this.axes.traverse((o) => o.isCSS2DObject && (o.visible = on));
  }

  setLabels(on) {
    this.labelRenderer.domElement.style.display = on ? "" : "none";
  }

  setVisible(id, on) {
    const it = this.items.get(id);
    if (!it) return;
    it.visible = on;
    for (const o of it.objs) o.traverse((c) => (c.visible = on));
  }

  applyHighlight(ids) {
    const set = new Set(ids);
    const any = set.size > 0;
    for (const [id, it] of this.items) {
      const state = !any ? "normal" : set.has(id) ? "hi" : "dim";
      for (const m of it.mats) {
        const base = m.userData.baseOpacity ?? 1;
        m.opacity = state === "dim" ? base * 0.22 : state === "hi" ? Math.min(1, base * (m.isLineMaterial ? 1 : 1.6)) : base;
        if (m.isLineMaterial) m.linewidth = m.userData.baseWidth * (state === "hi" ? 1.7 : 1);
      }
      for (const o of it.objs) {
        if (o.isCSS2DObject) o.element.classList.toggle("dim", state === "dim");
        if (o.isCSS2DObject) o.element.classList.toggle("hi", state === "hi");
        if (o.userData.isPoint) o.scale.setScalar(state === "hi" ? 1.6 : 1);
      }
    }
  }

  resize() {
    const r = this.container.getBoundingClientRect();
    this.w = Math.max(1, r.width);
    this.h = Math.max(1, r.height);
    this.renderer.setSize(this.w, this.h);
    this.labelRenderer.setSize(this.w, this.h);
    this.persp.aspect = this.w / this.h;
    this.persp.updateProjectionMatrix();
    this.updateOrtho();
    for (const m of this.lineMats) m.resolution.set(this.w, this.h);
  }

  tick() {
    if (this.anim) {
      const k = Math.min(1, (performance.now() - this.anim.t0) / 650);
      const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
      // 중심 기준 구면 보간으로 회전하듯 이동
      const a = this.anim.fromPos.clone().sub(this.anim.fromTarget);
      const b = this.anim.toPos.clone().sub(this.anim.toTarget);
      const len = THREE.MathUtils.lerp(a.length(), b.length(), e);
      const q = new THREE.Quaternion().setFromUnitVectors(a.clone().normalize(), b.clone().normalize());
      const dir = a.clone().normalize().applyQuaternion(new THREE.Quaternion().slerp(q, e));
      this.controls.target.lerpVectors(this.anim.fromTarget, this.anim.toTarget, e);
      this.camera.position.copy(this.controls.target).addScaledVector(dir, len);
      if (k >= 1) this.anim = null;
    }
    this.controls.update();
    this.updateOrtho();
    this.renderer.render(this.scene, this.camera);
    this.labelRenderer.render(this.scene, this.camera);
  }
}
