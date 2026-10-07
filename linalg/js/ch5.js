/* 5장 고윳값과 고유벡터 */
(function () {
'use strict';
const { F, f, X, N, mat, fh, par, term, v, editor, stepper, Plane, MINUS, fmt } = LA;
LA.chapter(5, '고윳값과 고유벡터', 'Eigenvalues and Eigenvectors');
const vec2 = (p) => `(${fmt(p[0])}, ${fmt(p[1])})`;
const ff = (M, d) => M.map((r) => r.map((t) => fmt(t, d)));

/* 3×3 특성다항식 λ³ − c₂λ² + c₁λ − c₀ 의 계수 (분수) */
function charPoly3(A) {
  const tr = A[0][0].add(A[1][1]).add(A[2][2]);
  const m = (i, j) => A[i][i].mul(A[j][j]).sub(A[i][j].mul(A[j][i]));
  const s2 = m(0, 1).add(m(0, 2)).add(m(1, 2));
  return { tr, s2, det: X.det(A), m };
}
/* 정수 근 찾기 (계수가 정수일 때) — 중복도 포함 */
function intRoots3(cp) {
  const c = [f(1), cp.tr.neg(), cp.s2, cp.det.neg()]; // λ³ + c1 λ² + c2 λ + c3
  if (c.some((x) => x.d !== 1)) return null;
  const ev = (l) => c.reduce((s, a) => s.mul(l).add(a), f(0));
  const c3 = Math.abs(c[3].n), cands = new Set([0]);
  for (let d = 1; d <= Math.max(1, c3); d++) if (c3 % d === 0) { cands.add(d); cands.add(-d); }
  let roots = [];
  for (const r of cands) if (ev(f(r)).isZero()) roots.push(r);
  if (!roots.length) return null;
  // 중복도: 나눗셈으로 낮춰 가며
  const out = []; let poly = c.slice();
  const div = (p, r) => { const q = [p[0]]; for (let i = 1; i < p.length; i++) q.push(p[i].add(q[i - 1].mul(r))); return { q: q.slice(0, -1), rem: q[q.length - 1] }; };
  for (let k = 0; k < 3; k++) {
    const r = roots.find((r0) => div(poly, f(r0)).rem.isZero());
    if (r == null) break; out.push(r); poly = div(poly, f(r)).q;
  }
  return out.length === 3 ? out : null;
}
function cubicRoots(a, b, c) { // λ³ + aλ² + bλ + c
  const Q = (a * a - 3 * b) / 9, R = (2 * a ** 3 - 9 * a * b + 27 * c) / 54;
  if (R * R <= Q ** 3 + 1e-12) {
    const th = Math.acos(Math.max(-1, Math.min(1, R / Math.sqrt(Math.max(Q, 1e-300) ** 3)))), s = -2 * Math.sqrt(Math.max(Q, 0));
    return { real: [s * Math.cos(th / 3) - a / 3, s * Math.cos((th + 2 * Math.PI) / 3) - a / 3, s * Math.cos((th - 2 * Math.PI) / 3) - a / 3].sort((x, y) => y - x) };
  }
  const A = -Math.sign(R) * Math.cbrt(Math.abs(R) + Math.sqrt(R * R - Q ** 3)), B = A ? Q / A : 0;
  return { real: [A + B - a / 3], cx: { re: -(A + B) / 2 - a / 3, im: (Math.sqrt(3) / 2) * Math.abs(A - B) } };
}
LA.charPoly3 = charPoly3; LA.intRoots3 = intRoots3; LA.cubicRoots = cubicRoots;

/* 2×2 특성방정식 전개 HTML */
function char2HTML(A) {
  const [[a, b], [c, d]] = A, tr = a + d, det = a * d - b * c, disc = tr * tr - 4 * det;
  const lines = [
    `det(A − λI) = | ${fmt(a)}−λ   ${fmt(b)} ; ${fmt(c)}   ${fmt(d)}−λ |`,
    `            = (${fmt(a)} − λ)(${fmt(d)} − λ) − (${fmt(b)})(${fmt(c)})`,
    `            = λ² − (${fmt(a)} + ${par(d)})λ + (${fmt(a)}·${par(d)}) − ${par(b * c)}`,
    `            = λ² − <b>${fmt(tr)}</b>λ + <b>${fmt(det)}</b>     ← λ² − (trace)λ + det`,
    `판별식 D = ${par(tr)}² − 4·${par(det)} = <b>${fmt(disc)}</b>`,
  ];
  if (disc >= -1e-12) { const s = Math.sqrt(Math.max(0, disc)); lines.push(`λ = (${fmt(tr)} ± √${fmt(Math.max(0, disc))}) / 2 = (${fmt(tr)} ± ${fmt(s)}) / 2   →   λ₁ = <b>${fmt((tr + s) / 2)}</b>, λ₂ = <b>${fmt((tr - s) / 2)}</b>`); }
  else lines.push(`D < 0 → 실수 고윳값 없음: λ = ${fmt(tr / 2)} ± ${fmt(Math.sqrt(-disc) / 2)}i  (회전 성분이 있어 방향이 보존되는 직선이 없음)`);
  return lines.map((l) => `<span class="ln">${l.replace(/ {2,}/g, (s) => '&nbsp;'.repeat(s.length))}</span>`).join('');
}

/* ======================================================= 5.1 특성방정식 */
LA.section({
  id: 'eigen', ch: 5, title: '특성방정식과 고유벡터', en: 'The Characteristic Equation',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">대부분의 벡터는 변환되면 방향이 바뀝니다. 그런데 어떤 특별한 방향의 벡터는 <b>방향은 그대로 두고 길이만 λ배</b> 됩니다. 그 벡터가 <b>고유벡터</b>, 배율 λ가 <b>고윳값</b>입니다.</p>
      <div class="keyline"><span class="lbl">정의 → 특성방정식</span><i>A</i><b>v</b> = λ<b>v</b>  (<b>v</b> ≠ <b>0</b>)  ⟺  (<i>A</i> − λ<i>I</i>)<b>v</b> = <b>0</b>이 0 아닌 해를 가짐  ⟺  det(<i>A</i> − λ<i>I</i>) = 0</div>
      <p class="small muted">(<i>A</i> − λ<i>I</i>)가 0이 아닌 벡터를 0으로 보내려면 공간을 납작하게 눌러야 하고, 그것이 곧 행렬식 0입니다. 왼쪽 그림에서 <b>x</b>를 돌려 보세요. <b>x</b>와 <i>A</i><b>x</b>가 한 직선에 겹치는 순간이 고유벡터입니다.</p>
    </div>
    <div id="eg-tabs"></div><div id="eg-body" class="page" style="gap:20px"></div>`;
    const body = root.querySelector('#eg-body');
    LA.tabs(root.querySelector('#eg-tabs'), ['2×2 (그림)', '3×3 (전개)'], (t) => { LA.cleanup(); (t ? eig3 : eig2)(body); });
  },
});
function eig2(body) {
  body.innerHTML = `<div class="lab">
    <div class="card"><div class="viz" id="e2-viz"></div>
      <div class="row"><label class="small"><input type="checkbox" id="e2-all"> 모든 방향 한꺼번에 보기</label><button type="button" class="btn" id="e2-spin">x 한 바퀴 돌리기</button></div>
      <div class="legend"><span><i style="background:var(--accent)"></i>x (끌기)</span><span><i style="background:var(--warn)"></i>Ax</span><span><i style="background:var(--e1)"></i>고유 직선 1</span><span><i style="background:var(--e2)"></i>고유 직선 2</span></div></div>
    <div class="card"><h3>행렬 A</h3><div id="e2-ctl"></div><div id="e2-now"></div></div></div>
    <details class="expand" open><summary>특성방정식 전개</summary><div class="body"><div class="calc" id="e2-char"></div></div></details>
    <details class="expand" open><summary>고유벡터 구하기: (A − λI)v = 0 풀기</summary><div class="body" id="e2-vec"></div></details>`;
  const A = [[2, 1], [1, 2]]; let x = [1.6, 0.6];
  const plane = new Plane(body.querySelector('#e2-viz'), { range: 5, aspect: 0.9, snap: 0 });
  plane.handle({ get: () => x, set: (p) => { const n = N.norm(p) || 1; x = N.vs(p, 2 / n); }, color: 'accent' });
  plane.draw = (p) => {
    const e = N.eig2(A);
    p.path((t) => [2 * Math.cos(t * 6.2832), 2 * Math.sin(t * 6.2832)], 90, 'grid', { w: 1 });
    if (e.real) { p.infLine([0, 0], e.v1, 'e1', 2, true); if (Math.abs(e.l1 - e.l2) > 1e-9 || Math.abs(N.dot(e.v1, e.v2)) < 0.999) p.infLine([0, 0], e.v2, 'e2', 2, true); }
    if (body.querySelector('#e2-all').checked) {
      for (let k = 0; k < 32; k++) {
        const th = (k / 32) * 2 * Math.PI, u = [2 * Math.cos(th), 2 * Math.sin(th)], Au = N.mv(A, u);
        const par = Math.abs(u[0] * Au[1] - u[1] * Au[0]) / (N.norm(u) * (N.norm(Au) || 1)) < 0.06;
        p.arrow(u, N.vadd(u, N.vs(Au, 0.35)), par ? 'ok' : 'muted', { w: par ? 2.5 : 1.2, alpha: par ? 1 : 0.6 });
      }
    }
    const Ax = N.mv(A, x), cross = (x[0] * Ax[1] - x[1] * Ax[0]) / (N.norm(x) * (N.norm(Ax) || 1));
    const hit = Math.abs(cross) < 0.03;
    p.arrow([0, 0], Ax, hit ? 'ok' : 'warn', { label: 'Ax', w: 3 }); p.arrow([0, 0], x, 'accent', { label: 'x' });
  };
  plane.onchange = now;
  function now() {
    const Ax = N.mv(A, x), cross = (x[0] * Ax[1] - x[1] * Ax[0]) / (N.norm(x) * (N.norm(Ax) || 1));
    const hit = Math.abs(cross) < 0.03, lam = N.dot(Ax, x) / N.dot(x, x);
    body.querySelector('#e2-now').innerHTML = `<div class="calc"><span class="ln">x = ${vec2(x)}</span><span class="ln">Ax = ${vec2(Ax)}</span><span class="ln">${hit ? `<b class="tok">평행! Ax ≈ ${fmt(lam)}·x → 고유벡터, λ ≈ ${fmt(lam)}</b>` : `x와 Ax 사이 각 ≈ ${fmt(Math.asin(Math.min(1, Math.abs(cross))) * 180 / Math.PI, 1)}°`}</span></div>`;
  }
  function solve() {
    body.querySelector('#e2-char').innerHTML = char2HTML(A);
    const e = N.eig2(A);
    if (!e.real) { body.querySelector('#e2-vec').innerHTML = '<p>실수 고윳값이 없으므로 실수 고유벡터도 없습니다.</p>'; return; }
    const ls = Math.abs(e.l1 - e.l2) < 1e-9 ? [e.l1] : [e.l1, e.l2];
    body.querySelector('#e2-vec').innerHTML = ls.map((l, k) => {
      const M = [[A[0][0] - l, A[0][1]], [A[1][0], A[1][1] - l]];
      const vv = k ? e.v2 : e.v1; const s = Math.abs(vv[0]) > 1e-9 ? vv[0] : vv[1]; const vn = N.vs(vv, 1 / s);
      const zero = M.every((r) => r.every((t) => Math.abs(t) < 1e-9));
      return `<div class="mxrow"><span class="math">λ<sub>${k + 1}</sub> = ${fmt(l)}:</span>${mat(ff(M), { name: `A − ${fmt(l)}I` })}</div>
        <div class="calc">${zero ? '<span class="ln">A − λI = 0 → 모든 벡터가 고유벡터 (고유공간 = ℝ²)</span>' : `<span class="ln">${fmt(M[0][0])}·v₁ + ${par(M[0][1])}·v₂ = 0</span><span class="ln">${fmt(M[1][0])}·v₁ + ${par(M[1][1])}·v₂ = 0   ← 행렬식이 0이라 두 식은 같은 직선</span><span class="ln">→ v = t·<b>${vec2(vn)}</b>  (t ≠ 0)</span><span class="ln">검산: A·${vec2(vn)} = ${vec2(N.mv(A, vn))} = ${fmt(l)}·${vec2(vn)} ✓</span>`}</div>`;
    }).join('<div class="sep"></div>');
  }
  LA.matSliders(body.querySelector('#e2-ctl'), A, () => { solve(); plane.changed(); }, 'e2');
  body.querySelector('#e2-all').addEventListener('change', () => plane.render());
  body.querySelector('#e2-spin').addEventListener('click', () => { const a0 = Math.atan2(x[1], x[0]); LA.tween(5000, (u) => { const a = a0 + u * 2 * Math.PI; x = [2 * Math.cos(a), 2 * Math.sin(a)]; plane.changed(); }); });
  solve(); now();
}
function eig3(body) {
  body.innerHTML = `<div class="lab"><div class="card"><h3>3×3 행렬</h3><div id="e3-ed"></div></div>
    <div class="card"><h3>특성다항식 계수 공식</h3><p class="small">det(A − λI)를 전개하면 계수에 규칙이 있습니다.</p>
      <div class="keyline">det(<i>A</i> − λ<i>I</i>) = −(λ³ − (tr <i>A</i>)λ² + <i>S</i><sub>2</sub>λ − det <i>A</i>)</div>
      <p class="small muted"><i>S</i><sub>2</sub> = 대각선 위 2×2 소행렬식(주소행렬식) 3개의 합. 아래에서 각각 펼쳐 계산합니다.</p></div></div>
    <details class="expand" open><summary>계수 전개</summary><div class="body"><div class="calc" id="e3-c"></div></div></details>
    <details class="expand" open><summary>고윳값과 고유벡터</summary><div class="body" id="e3-v"></div></details>`;
  editor(body.querySelector('#e3-ed'), X.fromN([[2, 0, 0], [1, 3, 0], [4, -1, 1]]), (A) => {
    if (A.length !== 3) return;
    const cp = charPoly3(A), a = (i, j) => par(A[i][j]);
    body.querySelector('#e3-c').innerHTML = [
      `tr A = a₁₁ + a₂₂ + a₃₃ = ${A[0][0].html()} + ${a(1, 1)} + ${a(2, 2)} = <b>${cp.tr.html()}</b>`,
      `S₂ = (a₁₁a₂₂ − a₁₂a₂₁) + (a₁₁a₃₃ − a₁₃a₃₁) + (a₂₂a₃₃ − a₂₃a₃₂)`,
      `   = (${a(0, 0)}·${a(1, 1)} − ${a(0, 1)}·${a(1, 0)}) + (${a(0, 0)}·${a(2, 2)} − ${a(0, 2)}·${a(2, 0)}) + (${a(1, 1)}·${a(2, 2)} − ${a(1, 2)}·${a(2, 1)})`,
      `   = ${cp.m(0, 1).html()} + ${par(cp.m(0, 2))} + ${par(cp.m(1, 2))} = <b>${cp.s2.html()}</b>`,
      ...LA.detLines(A, 'det A'),
      `특성방정식: λ³ ${term(cp.tr.neg(), false).trim()}λ² ${term(cp.s2, false).trim()}λ ${term(cp.det.neg(), false).trim()} = 0`,
    ].map((l) => `<span class="ln">${l.replace(/ {2,}/g, (s) => '&nbsp;'.repeat(s.length))}</span>`).join('');
    const ir = intRoots3(cp);
    let h = '';
    if (ir) {
      h += `<p>정수 근을 찾았습니다 (상수항 ${cp.det.neg().html()}의 약수를 대입): <b>λ = ${ir.join(', ')}</b></p>`;
      const uniq = [...new Set(ir)];
      h += uniq.map((l) => {
        const M = A.map((r, i) => r.map((x, j) => (i === j ? x.sub(l) : x))); const res = X.rref(M, 3); const nb = X.nullBasis(res.R, res.pivots, 3);
        const alg = ir.filter((x) => x === l).length;
        return `<div class="sep"></div><div class="mxrow"><span class="math">λ = ${l}</span>${mat(M, { name: `A − (${l})I` })}<span class="op">→</span>${mat(res.R, { name: 'RREF', cell: (i, j) => (res.pivots.some((p) => p[0] === i && p[1] === j) ? 'pv' : '') })}</div>
          <div class="mxrow">${nb.map((b, k) => LA.col(b.v, { name: `v<sub>${k + 1}</sub>`, noeq: true })).join('')}<span class="small">대수적 중복도 ${alg}, 기하적 중복도(고유공간 차원) ${nb.length}${nb.length < alg ? ' <span class="tw">← 부족: 대각화 불가</span>' : ''}</span></div>`;
      }).join('');
    } else {
      const r = cubicRoots(cp.tr.neg().val(), cp.s2.val(), cp.det.neg().val());
      h += `<p>정수 근이 없어 수치적으로 풉니다: λ ≈ ${r.real.map((t) => fmt(t)).join(', ')}${r.cx ? `, ${fmt(r.cx.re)} ± ${fmt(r.cx.im)}i` : ''}</p>`;
      const An = X.toN(A);
      h += r.real.map((l) => { const M = An.map((row, i) => row.map((t, j) => (i === j ? t - l : t))); const cs = [N.cross(M[0], M[1]), N.cross(M[0], M[2]), N.cross(M[1], M[2])].sort((p, q) => N.norm(q) - N.norm(p)); const w = cs[0], nn = N.norm(w) || 1; return `<div class="calc"><span class="ln">λ ≈ ${fmt(l)} → v ≈ (${w.map((t) => fmt(t / nn)).join(', ')})  (A − λI의 두 행에 동시에 수직인 방향 = 외적)</span></div>`; }).join('');
    }
    body.querySelector('#e3-v').innerHTML = h;
  }, { resize: false, presets: [{ name: '삼각행렬', A: [[2, 0, 0], [1, 3, 0], [4, -1, 1]] }, { name: '대칭', A: [[2, 1, 0], [1, 2, 0], [0, 0, 3]] }, { name: '중복 고윳값', A: [[2, 1, 0], [0, 2, 0], [0, 0, 3]] }, { name: '정수 아님', A: [[1, 2, 0], [2, 1, 1], [0, 1, 1]] }] });
  body.querySelector('#e3-ed input').dispatchEvent(new Event('input', { bubbles: true }));
}

/* ======================================================= 5.2 대각화 */
LA.section({
  id: 'diag', ch: 5, title: '행렬의 대각화', en: 'Diagonalization',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">고유벡터들로 기저를 잡으면 변환은 각 축 방향으로 늘이기만 하는 대각행렬이 됩니다. 이 기저 변환을 식으로 쓴 것이 대각화입니다.</p>
      <div class="keyline"><span class="lbl">P의 열 = 고유벡터, D의 대각 = 고윳값 (같은 순서)</span><i>A</i> = <i>P</i> <i>D</i> <i>P</i><sup>−1</sup>   ⟹   <i>A</i><sup><i>k</i></sup> = <i>P</i> <i>D</i><sup><i>k</i></sup> <i>P</i><sup>−1</sup></div>
      <ul><li><b>대각화 가능 조건</b>: 일차독립인 고유벡터가 <i>n</i>개 있을 것. 고윳값이 모두 다르면 자동으로 성립합니다.</li>
        <li>안 되는 예: 층밀림 [1 1; 0 1]은 λ = 1(중복도 2)인데 고유벡터 방향이 하나뿐입니다. 회전은 실수 고윳값이 없습니다.</li>
        <li><i>A</i><sup><i>k</i></sup>를 직접 <i>k</i>번 곱하는 대신 대각성분만 <i>k</i>제곱하면 됩니다.</li></ul>
    </div>
    <div class="lab">
      <div class="card"><h3>A = P D P⁻¹를 세 단계로 <small id="dg-stage"></small></h3><div class="viz" id="dg-viz"></div><div id="dg-step"></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>고유벡터 1</span><span><i style="background:var(--e2)"></i>고유벡터 2</span><span><i style="background:var(--accent)"></i>도형</span></div></div>
      <div class="card"><h3>행렬 A</h3><div id="dg-ctl"></div><div id="dg-pdp"></div></div>
    </div>
    <details class="expand" open><summary>Aᵏ = P Dᵏ P⁻¹ 전개</summary><div class="body"><div class="row">${LA.slider('dg-k', '지수 k', 1, 10, 1, 5)}</div><div id="dg-pow"></div></div></details>`;
    const A = [[1, 2], [2, 1]]; let stage = 0, cur = N.eye(2), dec = null;
    const viz = root.querySelector('#dg-viz'); const plane = new Plane(viz, { range: 5, aspect: 0.85 });
    const shape = [[0, 0], [1, 0], [1, 0.3], [0.3, 0.3], [0.3, 0.7], [0.8, 0.7], [0.8, 1], [0.3, 1], [0.3, 1.6], [0, 1.6]].map((p) => [p[0] * 1.3 + 0.4, p[1] * 1.3 + 0.2]);
    plane.draw = (p) => {
      p.tgrid(cur, 'accent', 0.22);
      if (dec) { const P0 = dec.P; const v1 = N.mv(cur, [P0[0][0], P0[1][0]]), v2 = N.mv(cur, [P0[0][1], P0[1][1]]); p.arrow([0, 0], v1, 'e1', { label: 'v₁' }); p.arrow([0, 0], v2, 'e2', { label: 'v₂' }); }
      p.poly(shape.map((q) => N.mv(cur, q)), 'accent', 'accent', { a: 0.25, w: 2 });
    };
    function decomp() {
      const e = N.eig2(A);
      if (!e.real) return { why: '실수 고윳값이 없습니다 (회전 성분).' };
      const P = [[e.v1[0], e.v2[0]], [e.v1[1], e.v2[1]]];
      if (Math.abs(N.det(P)) < 1e-6) return { why: `λ = ${fmt(e.l1)}이 중복인데 고유벡터 방향이 하나뿐입니다. 독립인 고유벡터 2개를 못 구해 P가 역행렬을 갖지 못합니다.` };
      // 보기 좋게: 각 고유벡터를 첫 0 아닌 성분이 1이 되도록 (정수에 가깝게)
      const nice = (u) => { const s = Math.abs(u[0]) > 1e-9 ? u[0] : u[1]; return N.vs(u, 1 / s); };
      const a = nice(e.v1), b = nice(e.v2); const Pn = [[a[0], b[0]], [a[1], b[1]]];
      return { P: Pn, D: [[e.l1, 0], [0, e.l2]], Pi: N.inv(Pn) };
    }
    const mats = () => dec && dec.P ? [N.eye(2), dec.Pi, N.mul(dec.D, dec.Pi), N.mul(dec.P, N.mul(dec.D, dec.Pi))] : [N.eye(2), A, A, A];
    const labels = ['시작: 표준 격자', '① P⁻¹ 적용 — 고유벡터를 좌표축으로 돌려놓기', '② D 적용 — 축 방향으로 λ배씩 늘이기', '③ P 적용 — 원래 방향으로 되돌리기 = A'];
    let from = N.eye(2);
    const sp = stepper(root.querySelector('#dg-step'), 4, (k) => {
      stage = k; const to = mats()[k]; const a0 = cur.map((r) => r.slice());
      root.querySelector('#dg-stage').textContent = labels[k];
      LA.tween(800, (u) => { cur = N.add(N.scale(a0, 1 - u), N.scale(to, u)); plane.render(); });
      from = to;
    }, { ms: 1700 });
    function info() {
      dec = decomp();
      if (!dec.P) { root.querySelector('#dg-pdp').innerHTML = `<span class="pill bad">대각화 불가</span><p class="small">${dec.why}</p>`; root.querySelector('#dg-pow').innerHTML = '<p class="small">대각화가 안 되면 이 지름길을 쓸 수 없습니다.</p>'; cur = mats()[stage]; plane.render(); return; }
      root.querySelector('#dg-pdp').innerHTML = `<span class="pill ok">대각화 가능</span><div class="mxrow">${mat(ff(A), { name: 'A' })}${mat(ff(dec.P), { cell: (i, j) => (j ? 'k2' : 'k1') })}${mat(ff(dec.D), { cell: (i, j) => (i === j ? 'h1' : 'dim') })}${mat(ff(dec.Pi))}</div>
        <div class="calc"><span class="ln">P의 1열 = λ₁ = ${fmt(dec.D[0][0])}의 고유벡터, 2열 = λ₂ = ${fmt(dec.D[1][1])}의 고유벡터</span><span class="ln">검산 PDP⁻¹ = ${JSON.stringify(ff(N.mul(dec.P, N.mul(dec.D, dec.Pi)))).replace(/"/g, '')}</span></div>`;
      pow(); cur = mats()[stage]; plane.render();
    }
    const getK = LA.bindSliders(root, ['dg-k'], () => pow());
    function pow() {
      if (!dec || !dec.P) return; const k = getK()['dg-k'], Dk = [[dec.D[0][0] ** k, 0], [0, dec.D[1][1] ** k]], Ak = N.mul(dec.P, N.mul(Dk, dec.Pi));
      let direct = N.eye(2); for (let i = 0; i < k; i++) direct = N.mul(direct, A);
      root.querySelector('#dg-pow').innerHTML = `<div class="mxrow">${mat(ff(Dk), { name: `D<sup>${k}</sup>`, cell: (i, j) => (i === j ? 'h1' : 'dim') })}<span class="small">= diag(${fmt(dec.D[0][0])}<sup>${k}</sup>, ${fmt(dec.D[1][1])}<sup>${k}</sup>)</span></div>
        <div class="mxrow">${mat(ff(Ak), { name: `A<sup>${k}</sup> = PD<sup>${k}</sup>P<sup>−1</sup>` })}<span class="op">vs</span>${mat(ff(direct), { name: `A·A⋯A (${k}번)` })}</div>
        <div class="calc">${[0, 1].map((i) => [0, 1].map((j) => `<span class="ln">(A<sup>${k}</sup>)<sub>${i + 1}${j + 1}</sub> = Σ p<sub>${i + 1}m</sub>·λ<sub>m</sub><sup>${k}</sup>·(P⁻¹)<sub>m${j + 1}</sub> = ${[0, 1].map((m) => `${par(dec.P[i][m])}·${par(Dk[m][m])}·${par(dec.Pi[m][j])}`).join(' + ')} = <b>${fmt(Ak[i][j])}</b></span>`).join('')).join('')}</div>`;
    }
    LA.matSliders(root.querySelector('#dg-ctl'), A, () => info(), 'dg');
    info();
  },
});
})();
