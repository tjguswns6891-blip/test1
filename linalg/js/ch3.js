/* 3장 벡터 공간 */
(function () {
'use strict';
const { F, f, X, N, mat, fh, par, term, v, bold, editor, Plane, View3D, MINUS, fmt } = LA;
LA.chapter(3, '벡터 공간', 'Vector Spaces');
const vec2 = (p) => `(${fmt(p[0])}, ${fmt(p[1])})`;

/* ======================================================= 3.1 Rⁿ 벡터와 내적 */
LA.section({
  id: 'rn', ch: 3, title: 'ℝⁿ의 벡터와 내적', en: 'Vectors in ℝⁿ and the Dot Product',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">ℝ<sup><i>n</i></sup>의 벡터 <b class="vec">u</b> = (<i>u</i><sub>1</sub>, …, <i>u</i><sub><i>n</i></sub>)는 <i>n</i>개의 수를 순서대로 늘어놓은 것이고, 2·3차원에서는 원점에서 출발하는 화살표로 그릴 수 있습니다. 성분 <i>u</i><sub><i>i</i></sub>는 <i>i</i>번째 축 방향으로 얼마나 가는지를 뜻합니다.</p>
      <div class="keyline"><span class="lbl">내적 — 같은 번호 성분끼리 곱해서 더한다</span><b>u</b>·<b>v</b> = <span class="sum">Σ</span><sub><i>i</i>=1</sub><sup><i>n</i></sup> <i>u</i><sub><i>i</i></sub><i>v</i><sub><i>i</i></sub> = ‖<b>u</b>‖ ‖<b>v</b>‖ cos θ</div>
      <ul><li>‖<b class="vec">u</b>‖ = √(<b class="vec">u</b>·<b class="vec">u</b>): 길이. <b class="vec">u</b>·<b class="vec">v</b> = 0이면 수직.</li>
        <li><b class="vec">v</b> 위로의 정사영: proj<sub><b>v</b></sub><b class="vec">u</b> = (<b class="vec">u</b>·<b class="vec">v</b> / <b class="vec">v</b>·<b class="vec">v</b>) <b class="vec">v</b>. 내적은 “<b class="vec">u</b>의 그림자 길이 × ‖<b class="vec">v</b>‖”입니다.</li></ul>
    </div>
    <div class="lab">
      <div class="card"><h3>끌어서 바꾸기 <small>점을 드래그</small></h3><div class="viz" id="rn-viz"></div>
        <div class="row" id="rn-show"><label class="small"><input type="checkbox" id="rn-sum" checked> u + v</label><label class="small"><input type="checkbox" id="rn-proj" checked> 정사영</label></div>
        ${LA.slider('rn-k', '스칼라 k', -2, 2, 0.25, 1.5)}</div>
      <div class="card"><h3>계산 전개</h3><div class="calc" id="rn-calc"></div></div>
    </div>
    <div class="card"><h3>ℝⁿ 계산기 <small>1행 = <b>u</b>, 2행 = <b>v</b>. 열을 늘려 차원을 바꿔 보세요</small></h3><div id="rn-ed"></div><div class="calc" id="rn-n"></div></div>`;
    let U = [3, 1], V = [1, 2.5];
    const plane = new Plane(root.querySelector('#rn-viz'), { range: 5, aspect: 0.85 });
    plane.handle({ get: () => U, set: (p) => (U = p), color: 'e1' }).handle({ get: () => V, set: (p) => (V = p), color: 'e2' });
    const get = LA.bindSliders(root, ['rn-k'], () => plane.changed());
    root.querySelectorAll('#rn-show input').forEach((i) => i.addEventListener('change', () => plane.changed()));
    plane.draw = (p) => {
      const k = get()['rn-k'];
      if (root.querySelector('#rn-sum').checked) {
        p.seg(U, N.vadd(U, V), 'e2', { dash: true, alpha: 0.6 }); p.seg(V, N.vadd(U, V), 'e1', { dash: true, alpha: 0.6 });
        p.arrow([0, 0], N.vadd(U, V), 'accent', { label: 'u+v' });
      }
      if (root.querySelector('#rn-proj').checked) {
        const vv = N.dot(V, V); if (vv > 1e-9) { const pr = N.vs(V, N.dot(U, V) / vv); p.seg(U, pr, 'muted', { dash: true }); p.arrow([0, 0], pr, 'e3', { w: 4, alpha: 0.7, label: 'proj' }); }
      }
      p.arrow([0, 0], N.vs(U, k), 'e1', { w: 1.5, alpha: 0.45, dash: true });
      p.text(N.vs(U, k), `${fmt(k)}u`, 'e1', 0, 14);
      const a1 = Math.atan2(U[1], U[0]), a2 = Math.atan2(V[1], V[0]);
      const [ox, oy] = p.toS([0, 0]); const c = p.ctx; c.save(); c.strokeStyle = LA.color('muted'); c.lineWidth = 1.5; c.beginPath();
      let d = a2 - a1; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI;
      c.arc(ox, oy, 26, -a1, -(a1 + d), d > 0); c.stroke(); c.restore();
      p.arrow([0, 0], U, 'e1', { label: 'u' }); p.arrow([0, 0], V, 'e2', { label: 'v' });
    };
    plane.onchange = calc;
    function calc() {
      const k = get()['rn-k'], d = N.dot(U, V), nu = N.norm(U), nv = N.norm(V);
      const cos = nu && nv ? d / (nu * nv) : NaN, th = Math.acos(Math.max(-1, Math.min(1, cos))) * 180 / Math.PI;
      const vv = N.dot(V, V);
      root.querySelector('#rn-calc').innerHTML = [
        `<b class="t1">u</b> = ${vec2(U)},  <b class="t2">v</b> = ${vec2(V)}`,
        `u + v = (${fmt(U[0])} + ${fmt(V[0])}, ${fmt(U[1])} + ${fmt(V[1])}) = <b>${vec2(N.vadd(U, V))}</b>`,
        `${fmt(k)}u = (${fmt(k)}·${par(U[0])}, ${fmt(k)}·${par(U[1])}) = <b>${vec2(N.vs(U, k))}</b>`,
        `‖u‖ = √(${par(U[0])}² + ${par(U[1])}²) = √${fmt(N.dot(U, U))} = <b>${fmt(nu)}</b>`,
        `‖v‖ = √(${par(V[0])}² + ${par(V[1])}²) = √${fmt(vv)} = <b>${fmt(nv)}</b>`,
        `u·v = u₁v₁ + u₂v₂ = ${par(U[0])}·${par(V[0])} + ${par(U[1])}·${par(V[1])} = <b>${fmt(d)}</b>`,
        `cos θ = u·v / (‖u‖‖v‖) = ${fmt(d)} / (${fmt(nu)}·${fmt(nv)}) = <b>${fmt(cos)}</b>`,
        `θ = <b>${fmt(th, 1)}°</b> ${Math.abs(d) < 1e-9 ? '<span class="tok">→ 수직!</span>' : d > 0 ? '(예각: 내적 > 0)' : '(둔각: 내적 < 0)'}`,
        vv > 1e-9 ? `proj_v u = (${fmt(d)} / ${fmt(vv)}) v = <b>${vec2(N.vs(V, d / vv))}</b>` : '',
      ].map((l) => `<span class="ln">${l}</span>`).join('');
    }
    calc();
    editor(root.querySelector('#rn-ed'), X.fromN([[1, 2, 0, -1], [3, -1, 4, 2]]), (M) => {
      if (M.length !== 2) return; const n = M[0].length, [u, w] = M;
      const d = u.reduce((s, a, i) => s.add(a.mul(w[i])), f(0));
      root.querySelector('#rn-n').innerHTML = [
        `n = ${n}  (ℝ<sup>${n}</sup>의 벡터)`,
        `u·v = ${u.map((_, i) => `u<sub>${i + 1}</sub>v<sub>${i + 1}</sub>`).join(' + ')}`,
        `    = ${u.map((a, i) => `${par(a)}·${par(w[i])}`).join(' + ')}`,
        `    = ${u.map((a, i) => term(a.mul(w[i]), i === 0)).join('')} = <b>${d.html()}</b>`,
        `‖u‖² = ${u.map((a) => `${par(a)}²`).join(' + ')} = <b>${u.reduce((s, a) => s.add(a.mul(a)), f(0)).html()}</b>`,
        `u + v = (${u.map((a, i) => a.add(w[i]).toString()).join(', ')})`,
      ].map((l) => `<span class="ln">${l.replace(/^ +/, (s) => '&nbsp;'.repeat(s.length))}</span>`).join('');
    }, { sym: 'u/v', resize: { rows: false, minC: 2, maxC: 6 } });
    root.querySelector('#rn-ed input').dispatchEvent(new Event('input', { bubbles: true }));
  },
});

/* ======================================================= 3.2 일반 벡터 공간과 공리 */
const R = (a) => Math.round(a * 1e9) / 1e9;
const near = (a, b) => (Array.isArray(a) ? a.every((x, i) => Math.abs(x - b[i]) < 1e-7) : Math.abs(a - b) < 1e-7);
const ri = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));
const SPACES = [
  { name: 'ℝ² (보통 연산)', desc: '(x₁, y₁) + (x₂, y₂) = (x₁+x₂, y₁+y₂),  k(x, y) = (kx, ky)', ok: true,
    rand: () => [ri(-4, 4), ri(-4, 4)], add: (a, b) => [a[0] + b[0], a[1] + b[1]], smul: (k, a) => [k * a[0], k * a[1]], zero: () => [0, 0], neg: (a) => [-a[0], -a[1]], mem: () => true, show: (a) => `(${fmt(a[0])}, ${fmt(a[1])})` },
  { name: '2차 이하 다항식 P₂', desc: '계수끼리 더하고 곱함. p(x) = a + bx + cx²', ok: true,
    rand: () => [ri(-3, 3), ri(-3, 3), ri(-3, 3)], add: (a, b) => a.map((x, i) => x + b[i]), smul: (k, a) => a.map((x) => k * x), zero: () => [0, 0, 0], neg: (a) => a.map((x) => -x), mem: () => true,
    show: (a) => { const t = [[a[0], ''], [a[1], 'x'], [a[2], 'x²']].filter(([c]) => Math.abs(c) > 1e-12); if (!t.length) return '0'; return t.map(([c, s], i) => (i ? (c < 0 ? ' − ' : ' + ') : c < 0 ? '−' : '') + (Math.abs(c) === 1 && s ? '' : fmt(Math.abs(c))) + s).join(''); } },
  { name: '2×2 행렬 M₂ₓ₂', desc: '성분끼리 더하고 곱함', ok: true,
    rand: () => [ri(-3, 3), ri(-3, 3), ri(-3, 3), ri(-3, 3)], add: (a, b) => a.map((x, i) => x + b[i]), smul: (k, a) => a.map((x) => k * x), zero: () => [0, 0, 0, 0], neg: (a) => a.map((x) => -x), mem: () => true,
    show: (a) => `[${fmt(a[0])} ${fmt(a[1])}; ${fmt(a[2])} ${fmt(a[3])}]` },
  { name: '양의 실수 ℝ⁺ (곱을 덧셈으로)', desc: 'x ⊕ y = xy,  k ⊙ x = xᵏ.  영벡터는 1, −x는 1/x', ok: true,
    rand: () => ri(1, 5), add: (a, b) => a * b, smul: (k, a) => a ** k, zero: () => 1, neg: (a) => 1 / a, mem: (a) => a > 0, show: (a) => fmt(a, 4) },
  { name: '1사분면 {(x, y) | x ≥ 0, y ≥ 0}', desc: 'ℝ²의 보통 연산을 그대로 사용', ok: false,
    rand: () => [ri(0, 4), ri(0, 4)], add: (a, b) => [a[0] + b[0], a[1] + b[1]], smul: (k, a) => [k * a[0], k * a[1]], zero: () => [0, 0], neg: (a) => [-a[0], -a[1]], mem: (a) => a[0] >= 0 && a[1] >= 0, show: (a) => `(${fmt(a[0])}, ${fmt(a[1])})` },
  { name: 'ℝ², 이상한 스칼라배', desc: '덧셈은 보통, 스칼라배만 k ⊙ (x, y) = (kx, 0)', ok: false,
    rand: () => [ri(-4, 4), ri(-4, 4)], add: (a, b) => [a[0] + b[0], a[1] + b[1]], smul: (k, a) => [k * a[0], 0], zero: () => [0, 0], neg: (a) => [-a[0], -a[1]], mem: () => true, show: (a) => `(${fmt(a[0])}, ${fmt(a[1])})` },
  { name: 'ℝ², 이상한 덧셈', desc: '(x₁, y₁) ⊕ (x₂, y₂) = (x₁+x₂+1, y₁+y₂+1), 스칼라배는 보통', ok: false,
    rand: () => [ri(-3, 3), ri(-3, 3)], add: (a, b) => [a[0] + b[0] + 1, a[1] + b[1] + 1], smul: (k, a) => [k * a[0], k * a[1]], zero: () => [-1, -1], neg: (a) => [-a[0] - 2, -a[1] - 2], mem: () => true, show: (a) => `(${fmt(a[0])}, ${fmt(a[1])})` },
];
const AXIOMS = [
  { t: '덧셈에 닫힘', f: 'u ⊕ v ∈ V', run: (S, u, w) => { const s = S.add(u, w); return { ok: S.mem(s), l: `u ⊕ v = ${S.show(u)} ⊕ ${S.show(w)} = ${S.show(s)}`, r: S.mem(s) ? 'V 안에 있음' : '<span class="tw">V 밖으로 나감</span>' }; } },
  { t: '스칼라배에 닫힘', f: 'k ⊙ u ∈ V', run: (S, u, w, z, k) => { const s = S.smul(k, u); return { ok: S.mem(s), l: `${fmt(k)} ⊙ ${S.show(u)} = ${S.show(s)}`, r: S.mem(s) ? 'V 안에 있음' : '<span class="tw">V 밖으로 나감</span>' }; } },
  { t: '교환법칙', f: 'u ⊕ v = v ⊕ u', run: (S, u, w) => { const a = S.add(u, w), b = S.add(w, u); return { ok: near(a, b), l: `u ⊕ v = ${S.show(a)}`, r: `v ⊕ u = ${S.show(b)}` }; } },
  { t: '결합법칙', f: '(u ⊕ v) ⊕ w = u ⊕ (v ⊕ w)', run: (S, u, w, z) => { const a = S.add(S.add(u, w), z), b = S.add(u, S.add(w, z)); return { ok: near(a, b), l: `(u ⊕ v) ⊕ w = ${S.show(a)}`, r: `u ⊕ (v ⊕ w) = ${S.show(b)}` }; } },
  { t: '영벡터 존재', f: 'u ⊕ 0 = u', run: (S, u) => { const a = S.add(u, S.zero()); return { ok: near(a, u), l: `0 = ${S.show(S.zero())},  u ⊕ 0 = ${S.show(a)}`, r: `u = ${S.show(u)}` }; } },
  { t: '역원 존재', f: 'u ⊕ (−u) = 0', run: (S, u) => { const n = S.neg(u), a = S.add(u, n); return { ok: near(a, S.zero()) && S.mem(n), l: `−u = ${S.show(n)},  u ⊕ (−u) = ${S.show(a)}`, r: `0 = ${S.show(S.zero())}${S.mem(n) ? '' : ' <span class="tw">(−u가 V 밖)</span>'}` }; } },
  { t: '분배법칙 ①', f: 'k ⊙ (u ⊕ v) = k⊙u ⊕ k⊙v', run: (S, u, w, z, k) => { const a = S.smul(k, S.add(u, w)), b = S.add(S.smul(k, u), S.smul(k, w)); return { ok: near(a, b), l: `${fmt(k)} ⊙ (u ⊕ v) = ${S.show(a)}`, r: `${fmt(k)}⊙u ⊕ ${fmt(k)}⊙v = ${S.show(b)}` }; } },
  { t: '분배법칙 ②', f: '(k + m) ⊙ u = k⊙u ⊕ m⊙u', run: (S, u, w, z, k, m) => { const a = S.smul(k + m, u), b = S.add(S.smul(k, u), S.smul(m, u)); return { ok: near(a, b), l: `(${fmt(k)} + ${fmt(m)}) ⊙ u = ${S.show(a)}`, r: `${fmt(k)}⊙u ⊕ ${fmt(m)}⊙u = ${S.show(b)}` }; } },
  { t: '스칼라 결합', f: 'k ⊙ (m ⊙ u) = (km) ⊙ u', run: (S, u, w, z, k, m) => { const a = S.smul(k, S.smul(m, u)), b = S.smul(k * m, u); return { ok: near(a, b), l: `${fmt(k)} ⊙ (${fmt(m)} ⊙ u) = ${S.show(a)}`, r: `${fmt(k * m)} ⊙ u = ${S.show(b)}` }; } },
  { t: '항등원 1', f: '1 ⊙ u = u', run: (S, u) => { const a = S.smul(1, u); return { ok: near(a, u), l: `1 ⊙ u = ${S.show(a)}`, r: `u = ${S.show(u)}` }; } },
];
LA.section({
  id: 'axioms', ch: 3, title: '일반 벡터 공간과 8가지 공리', en: 'General Vector Spaces',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">“벡터”는 화살표만이 아닙니다. 덧셈 ⊕와 스칼라배 ⊙가 정의된 집합 <i>V</i>가 아래 규칙을 모두 지키면 <i>V</i>를 <b>벡터 공간</b>이라 부르고, 그 원소는 모두 벡터입니다. 다항식, 행렬, 함수도 벡터가 됩니다.</p>
      <p class="small muted">먼저 두 연산의 결과가 <i>V</i> 안에 머물러야 하고(닫힘), 그다음 8가지 공리가 성립해야 합니다. 하나라도 깨지면 벡터 공간이 아닙니다. 아래에서 후보를 고르고 공리를 눌러 실제 숫자로 양변을 비교해 보세요. 반례가 하나만 나와도 탈락입니다.</p>
    </div>
    <div class="card"><h3>후보 집합 고르기</h3><div class="row" id="ax-pick"></div><div id="ax-desc" class="calc"></div></div>
    <div class="lab">
      <div class="card"><h3>닫힘 + 공리 10개 <small>✓ 성립 · ✗ 반례 발견</small></h3><div class="ax" id="ax-list"></div>
        <button type="button" class="btn" id="ax-re">새 표본으로 다시 확인</button></div>
      <div class="card"><h3 id="ax-h">계산</h3><div id="ax-detail" class="page" style="gap:12px"></div></div>
    </div>`;
    let S = SPACES[0], sel = 2, samples;
    root.querySelector('#ax-pick').innerHTML = SPACES.map((s, i) => `<button type="button" class="chip${i ? '' : ' on'}" data-s="${i}">${s.name}</button>`).join('');
    const resample = () => { samples = Array.from({ length: 6 }, () => [S.rand(), S.rand(), S.rand(), [-2, -1, 2, 3, 0.5][ri(0, 4)], [-1, 2, 3, -2][ri(0, 3)]]); };
    function draw() {
      root.querySelector('#ax-desc').innerHTML = `<span class="ln">${S.desc}</span>`;
      const st = AXIOMS.map((ax) => { const rs = samples.map((s) => ax.run(S, ...s)); const bad = rs.find((r) => !r.ok); return { rs, bad }; });
      root.querySelector('#ax-list').innerHTML = AXIOMS.map((ax, i) => `<button type="button" data-a="${i}" class="${i === sel ? 'on' : ''}"><span class="no">${i < 2 ? '닫힘' : i - 1}</span><span><b>${ax.t}</b> <span class="muted small">${ax.f}</span></span><span class="st ${st[i].bad ? 'tw' : 'tok'}">${st[i].bad ? '✗ 반례' : '✓'}</span></button>`).join('');
      const fails = st.filter((x) => x.bad).length;
      const ax = AXIOMS[sel], cur = st[sel];
      root.querySelector('#ax-h').innerHTML = `${ax.t}: ${ax.f}`;
      const show = cur.bad ? [cur.bad, ...cur.rs.filter((r) => r !== cur.bad).slice(0, 2)] : cur.rs.slice(0, 3);
      root.querySelector('#ax-detail').innerHTML = `<div class="row">${fails ? `<span class="pill bad">벡터 공간 아님 — ${fails}개 규칙 위반</span>` : '<span class="pill ok">모든 표본에서 성립 → 벡터 공간</span>'}</div>` +
        show.map((r, k) => `<div class="calc"><span class="ln">${k === 0 && cur.bad ? '<b class="tw">반례</b>  ' : `표본 ${k + 1}  `}u = ${S.show(samples[cur.rs.indexOf(r)][0])}, v = ${S.show(samples[cur.rs.indexOf(r)][1])}, w = ${S.show(samples[cur.rs.indexOf(r)][2])}, k = ${fmt(samples[cur.rs.indexOf(r)][3])}, m = ${fmt(samples[cur.rs.indexOf(r)][4])}</span><span class="ln">왼쪽: ${r.l}</span><span class="ln">오른쪽: ${r.r}</span><span class="ln">${r.ok ? '<b class="tok">같음 ✓</b>' : '<b class="tw">다름 ✗</b>'}</span></div>`).join('') +
        `<p class="small muted">표본 몇 개로 확인한 것은 증명이 아니지만, 반례 하나는 공리가 깨졌다는 확실한 증거입니다.</p>`;
    }
    root.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.s) { S = SPACES[+b.dataset.s]; root.querySelectorAll('[data-s]').forEach((x) => x.classList.toggle('on', x === b)); resample(); draw(); }
      else if (b.dataset.a) { sel = +b.dataset.a; draw(); }
      else if (b.id === 'ax-re') { resample(); draw(); }
    });
    resample(); draw();
  },
});

/* ======================================================= 3.3 부분공간 */
const SETS = [
  { name: '원점을 지나는 직선 y = 2x', sub: true, proj: (p) => { const d = [1, 2], t = N.dot(p, d) / 5; return N.vs(d, t); }, mem: (p) => Math.abs(p[1] - 2 * p[0]) < 1e-6, draw: (pl) => pl.infLine([0, 0], [1, 2], 'accent', 3),
    why: '두 벡터 모두 (t, 2t) 꼴이라 합도 (t+s, 2(t+s)), 상수배도 (kt, 2kt)로 직선 위에 있습니다.' },
  { name: '원점을 지나지 않는 직선 y = 2x + 1', sub: false, proj: (p) => { const d = [1, 2], q = N.vsub(p, [0, 1]), t = N.dot(q, d) / 5; return N.vadd([0, 1], N.vs(d, t)); }, mem: (p) => Math.abs(p[1] - 2 * p[0] - 1) < 1e-6, draw: (pl) => pl.infLine([0, 1], [1, 2], 'accent', 3),
    why: '영벡터 (0, 0)이 들어 있지 않습니다. 합 u + v는 y절편이 2인 직선 위로 가 버립니다.' },
  { name: '1사분면', sub: false, proj: (p) => [Math.max(0, p[0]), Math.max(0, p[1])], mem: (p) => p[0] >= -1e-9 && p[1] >= -1e-9, draw: (pl) => pl.poly([[0, 0], [20, 0], [20, 20], [0, 20]], 'accent', null, { a: 0.12 }),
    why: '덧셈에는 닫혀 있지만 음수를 곱하면(k < 0) 3사분면으로 나갑니다.' },
  { name: '두 좌표축의 합집합', sub: false, proj: (p) => (Math.abs(p[0]) > Math.abs(p[1]) ? [p[0], 0] : [0, p[1]]), mem: (p) => Math.abs(p[0]) < 1e-9 || Math.abs(p[1]) < 1e-9, draw: (pl) => { pl.infLine([0, 0], [1, 0], 'accent', 3); pl.infLine([0, 0], [0, 1], 'accent', 3); },
    why: '스칼라배에는 닫혀 있지만 (1, 0) + (0, 1) = (1, 1)은 어느 축에도 없습니다.' },
  { name: '영벡터만 {0}', sub: true, proj: () => [0, 0], mem: (p) => Math.abs(p[0]) + Math.abs(p[1]) < 1e-9, draw: (pl) => pl.dot([0, 0], 'accent', 6),
    why: '0 + 0 = 0, k·0 = 0. 가장 작은 부분공간입니다.' },
  { name: '원판 x² + y² ≤ 4', sub: false, proj: (p) => { const n = N.norm(p); return n > 2 ? N.vs(p, 2 / n) : p; }, mem: (p) => N.dot(p, p) <= 4 + 1e-6, draw: (pl) => pl.path((t) => [2 * Math.cos(t * 6.3), 2 * Math.sin(t * 6.3)], 80, 'accent', { fill: 'accent' }),
    why: '큰 수를 곱하면 원판 밖으로 나갑니다. 경계가 있는 집합은 (영벡터만 빼고) 부분공간이 될 수 없습니다.' },
];
LA.section({
  id: 'subspace', ch: 3, title: '부분공간의 조건', en: 'Subspaces',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">벡터 공간 <i>V</i>의 부분집합 <i>W</i>가 같은 연산으로 그 자체로 벡터 공간이 되면 <b>부분공간</b>입니다. 공리를 다시 다 확인할 필요 없이 세 가지만 보면 됩니다.</p>
      <div class="keyline"><span class="lbl">부분공간 판정</span>① <b>0</b> ∈ <i>W</i>   ② <b>u</b>, <b>v</b> ∈ <i>W</i> ⇒ <b>u</b> + <b>v</b> ∈ <i>W</i>   ③ <b>u</b> ∈ <i>W</i> ⇒ <i>k</i><b>u</b> ∈ <i>W</i></div>
      <p class="small muted">ℝ²의 부분공간은 {<b>0</b>}, 원점을 지나는 직선, ℝ² 전체뿐입니다. 아래에서 집합을 고르고 <b class="vec">u</b>, <b class="vec">v</b>를 집합 안에서 끌며 합과 상수배가 밖으로 나가는지 보세요.</p>
    </div>
    <div class="card"><div class="row" id="ss-pick"></div></div>
    <div class="lab">
      <div class="card"><div class="viz" id="ss-viz"></div>${LA.slider('ss-k', '스칼라 k', -3, 3, 0.25, -1.5)}
        <div class="legend"><span><i style="background:var(--e1)"></i>u</span><span><i style="background:var(--e2)"></i>v</span><span><i style="background:var(--ok)"></i>W 안</span><span><i style="background:var(--warn)"></i>W 밖</span></div></div>
      <div class="card"><h3 id="ss-h"></h3><div id="ss-out"></div></div>
    </div>`;
    let S = SETS[0], U = [1, 2], V = [-0.5, -1];
    const plane = new Plane(root.querySelector('#ss-viz'), { range: 5, aspect: 0.85, snap: 0.25 });
    plane.handle({ get: () => U, set: (p) => (U = S.proj(p)), color: 'e1' }).handle({ get: () => V, set: (p) => (V = S.proj(p)), color: 'e2' });
    const get = LA.bindSliders(root, ['ss-k'], () => plane.changed());
    plane.draw = (p) => {
      S.draw(p); const k = get()['ss-k'], s = N.vadd(U, V), ku = N.vs(U, k);
      p.arrow([0, 0], s, S.mem(s) ? 'ok' : 'warn', { label: 'u+v', w: 2 }); p.arrow([0, 0], ku, S.mem(ku) ? 'ok' : 'warn', { label: 'ku', w: 2, dash: true });
      p.arrow([0, 0], U, 'e1', { label: 'u' }); p.arrow([0, 0], V, 'e2', { label: 'v' });
      p.dot([0, 0], S.mem([0, 0]) ? 'ok' : 'warn', 5, { hollow: true });
    };
    plane.onchange = out;
    function out() {
      const k = get()['ss-k'], s = N.vadd(U, V), ku = N.vs(U, k);
      const c = [S.mem([0, 0]), S.mem(s), S.mem(ku)];
      const ok = (b) => (b ? '<span class="pill ok">✓</span>' : '<span class="pill bad">✗</span>');
      root.querySelector('#ss-h').textContent = S.name;
      root.querySelector('#ss-out').innerHTML = `<table class="t"><tbody>
        <tr><td>① 0 ∈ W</td><td>${ok(c[0])}</td></tr>
        <tr><td>② u + v = ${vec2(U)} + ${vec2(V)} = ${vec2(s)}</td><td>${ok(c[1])}</td></tr>
        <tr><td>③ ${fmt(k)}·u = ${vec2(ku)}</td><td>${ok(c[2])}</td></tr></tbody></table>
        <p style="margin-top:12px">${S.sub ? '<span class="pill ok">부분공간</span>' : '<span class="pill bad">부분공간 아님</span>'}</p><p class="small">${S.why}</p>
        <p class="small muted">지금 위치에서 ✓가 떠도, 다른 위치에서 하나라도 ✗가 나오면 부분공간이 아닙니다. 점을 여러 곳으로 옮겨 보세요.</p>`;
    }
    root.querySelector('#ss-pick').innerHTML = SETS.map((s, i) => `<button type="button" class="chip${i ? '' : ' on'}" data-s="${i}">${s.name}</button>`).join('');
    root.querySelector('#ss-pick').addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; S = SETS[+b.dataset.s]; root.querySelectorAll('[data-s]').forEach((x) => x.classList.toggle('on', x === b)); U = S.proj([1.5, 2.5]); V = S.proj([-1, 0.5]); plane.changed(); });
    out();
  },
});

/* ======================================================= 3.4 일차독립과 일차종속 */
LA.section({
  id: 'indep', ch: 3, title: '일차독립과 일차종속', en: 'Linear Independence',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">벡터들 <b class="vec">v</b><sub>1</sub>, …, <b class="vec">v</b><sub><i>k</i></sub>가 <b>일차독립</b>이라는 것은 “어느 하나도 나머지의 조합으로 만들 수 없다”는 뜻입니다. 식으로 쓰면 다음 방정식의 해가 모두 0인 것뿐이어야 합니다.</p>
      <div class="keyline"><span class="lbl">판정식</span><i>c</i><sub>1</sub><b>v</b><sub>1</sub> + <i>c</i><sub>2</sub><b>v</b><sub>2</sub> + ⋯ + <i>c</i><sub><i>k</i></sub><b>v</b><sub><i>k</i></sub> = <b>0</b>  ⟹  <i>c</i><sub>1</sub> = <i>c</i><sub>2</sub> = ⋯ = <i>c</i><sub><i>k</i></sub> = 0 ?</div>
      <p class="small muted">벡터들을 <b>열</b>로 세운 행렬 [<b>v</b><sub>1</sub> ⋯ <b>v</b><sub><i>k</i></sub>]의 랭크가 <i>k</i>이면 독립, 작으면 종속입니다. 종속이면 0이 아닌 해 (<i>c</i><sub>1</sub>, …)가 바로 “어떤 벡터가 나머지로 만들어지는지”를 알려 줍니다. 그림의 색칠은 벡터들의 <b>생성(span)</b>입니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>벡터를 열로 입력 <small>행 수 = 차원 (2 또는 3)</small></h3><div id="li-ed"></div><div id="li-verdict"></div></div>
      <div class="card"><h3>span 그림 <small id="li-cap"></small></h3><div class="viz" id="li-viz"></div></div>
    </div>
    <details class="expand" open><summary>판정식 전부 전개</summary><div class="body" id="li-exp"></div></details>`;
    let M, view, dim = 0;
    const viz = root.querySelector('#li-viz'); const cols = ['e1', 'e2', 'e3', 'accent'];
    function mkView(d) {
      if (dim === d) return; dim = d;
      LA.live.planes.forEach((p) => { if (p.host === viz) { p.destroy(); LA.live.planes.delete(p); } }); viz.innerHTML = '';
      view = d === 2 ? new Plane(viz, { range: 5, aspect: 0.85 }) : new View3D(viz, { range: 4 });
      view.draw = paint;
    }
    function paint(p) {
      const V = N.T(X.toN(M)), r = X.rref(M, M[0].length).rank;
      if (dim === 2) {
        if (r === 2) p.poly([[-9, -9], [9, -9], [9, 9], [-9, 9]], 'accent', null, { a: 0.1 });
        if (r === 1) { const d = V.find((x) => N.norm(x) > 1e-9); p.infLine([0, 0], d, 'accent', 6, null); }
      } else {
        const nz = V.filter((x) => N.norm(x) > 1e-9);
        if (r === 1) { const d = N.vs(nz[0], 6 / N.norm(nz[0])); p.seg(N.vs(d, -1), d, 'accent', { w: 5, alpha: 0.3 }); }
        if (r === 2) { const a = nz[0]; const b = nz.find((x) => N.norm(N.cross(a, x)) > 1e-9); p.planePatch(a, b, 'accent'); }
        if (r === 3) { const [a, b, c] = V; const O = [0, 0, 0]; const P = [O, a, b, c, N.vadd(a, b), N.vadd(a, c), N.vadd(b, c), N.vadd(N.vadd(a, b), c)]; [[0, 1, 4, 2], [0, 1, 5, 3], [0, 2, 6, 3], [7, 4, 1, 5], [7, 4, 2, 6], [7, 5, 3, 6]].forEach((fc) => p.poly(fc.map((i) => P[i]), 'accent', 'accent', { a: 0.07, w: 0.6 })); }
      }
      V.forEach((x, i) => p.arrow(dim === 2 ? [0, 0] : [0, 0, 0], x, cols[i % 4], { label: `v${'₁₂₃₄₅'[i]}` }));
    }
    function run(m) {
      M = m; const d = M.length, k = M[0].length; mkView(d);
      const res = X.rref(M, k), r = res.rank, indep = r === k;
      const spanTxt = r === 0 ? '원점 하나' : r === 1 ? '직선' : r === 2 ? (d === 2 ? 'ℝ² 전체' : '평면') : 'ℝ³ 전체';
      root.querySelector('#li-cap').textContent = `span = ${spanTxt} (${r}차원)`;
      let h = `<div class="row" style="margin-top:6px"><span class="pill ${indep ? 'ok' : 'bad'}">${indep ? '일차독립' : '일차종속'}</span><span class="small">랭크 ${r} ${indep ? '=' : '<'} 벡터 수 ${k}</span></div>`;
      if (k > d) h += `<p class="small">ℝ<sup>${d}</sup>에서 ${k}개의 벡터는 언제나 종속입니다. 차원보다 많은 벡터는 독립일 수 없습니다.</p>`;
      root.querySelector('#li-verdict').innerHTML = h;
      const names = 'c₁,c₂,c₃,c₄,c₅'.split(',');
      const eqs = M.map((row) => row.map((a, j) => `${j ? ' + ' : ''}${par(a)}·${v('c', j + 1)}`).join('') + ' = 0');
      const zero = M.map((r0) => [...r0, f(0)]);
      const nb = X.nullBasis(res.R, res.pivots, k);
      let ex = `<div class="math">${M[0].map((_, j) => `${v('c', j + 1)}${LA.col(M.map((r0) => r0[j]), { cls: '' })}`).join(' + ')} = ${LA.col(M.map(() => f(0)))}</div>
        <p class="small">성분(행)마다 하나씩 방정식이 나옵니다:</p><div class="calc">${eqs.map((e) => `<span class="ln">${e}</span>`).join('')}</div>
        <p class="small">계수행렬을 RREF로 줄이면:</p><div class="mxrow">${mat(zero, { aug: k })}<span class="op">→</span>${mat(res.R.map((r0) => [...r0, f(0)]), { aug: k, cell: (i, j) => (res.pivots.some((p) => p[0] === i && p[1] === j) ? 'pv' : '') })}</div>`;
      if (indep) ex += `<p>모든 열에 피벗이 있어 자유변수가 없습니다. 따라서 <b>${names.slice(0, k).join(' = ')} = 0</b>뿐이고, 벡터들은 독립입니다.</p>`;
      else {
        const c = nb[0].v;
        const rel = c.map((x, j) => (x.isZero() ? '' : `${x.sign() < 0 ? ' − ' : ' + '}${x.abs().isOne() ? '' : x.abs().html()}<b class="vec">v</b><sub>${j + 1}</sub>`)).join('').replace(/^ \+ /, '').replace(/^ − /, '−');
        const fj = nb[0].free;
        const others = c.map((x, j) => (j === fj || x.isZero() ? '' : `${x.neg().sign() < 0 ? ' − ' : ' + '}${x.abs().isOne() ? '' : x.abs().html()}<b class="vec">v</b><sub>${j + 1}</sub>`)).join('').replace(/^ \+ /, '').replace(/^ − /, '−');
        ex += `<p>피벗이 없는 열 ${nb.map((b) => b.free + 1).join(', ')}번 → 자유변수가 있습니다. ${v('c', fj + 1)} = 1로 두면 0이 아닌 해 (${c.map((x) => x.html()).join(', ')})이 나옵니다.</p>
          <div class="math">${rel || '0'} = <b>0</b>   ⇒   <b class="vec">v</b><sub>${fj + 1}</sub> = ${others || '<b>0</b>'}</div>
          <p class="small muted">즉 ${fj + 1}번째 벡터는 앞의 벡터들로 만들 수 있어서 span을 넓히지 못합니다.</p>`;
      }
      root.querySelector('#li-exp').innerHTML = ex;
      view.render();
    }
    editor(root.querySelector('#li-ed'), X.fromN([[1, 0, 2], [2, 1, 5], [0, 1, 1]]), run, {
      sym: 'v', resize: { minR: 2, maxR: 3, minC: 1, maxC: 4 },
      presets: [{ name: 'ℝ³ 종속 3개', A: [[1, 0, 2], [2, 1, 5], [0, 1, 1]] }, { name: 'ℝ³ 독립 3개', A: [[1, 0, 1], [0, 1, 1], [0, 0, 2]] }, { name: 'ℝ² 2개', A: [[2, 1], [1, 3]] }, { name: 'ℝ² 3개', A: [[1, 0, 2], [0, 1, 1]] }],
    });
    run(X.fromN([[1, 0, 2], [2, 1, 5], [0, 1, 1]]));
  },
});

/* ======================================================= 3.5 기저와 차원 */
LA.section({
  id: 'basis', ch: 3, title: '기저와 차원', en: 'Basis and Dimension',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead"><b>기저</b>는 공간 전체를 생성하면서(span) 서로 일차독립인 벡터 집합입니다. 기저가 정해지면 공간의 모든 벡터는 <b>단 한 가지 방법</b>으로 기저의 일차결합이 되고, 그 계수를 좌표 [<b class="vec">x</b>]<sub><i>B</i></sub>라 부릅니다.</p>
      <div class="keyline"><span class="lbl">좌표의 뜻</span><b>x</b> = <i>c</i><sub>1</sub><b>b</b><sub>1</sub> + <i>c</i><sub>2</sub><b>b</b><sub>2</sub>   ⟺   [<b>x</b>]<sub><i>B</i></sub> = (<i>c</i><sub>1</sub>, <i>c</i><sub>2</sub>)</div>
      <ul><li><b>차원</b> = 기저에 들어 있는 벡터의 개수. 어떤 기저를 골라도 개수는 같습니다. dim ℝ<sup><i>n</i></sup> = <i>n</i>, dim P<sub>2</sub> = 3 ({1, <i>x</i>, <i>x</i>²}), dim M<sub>2×2</sub> = 4.</li>
        <li>벡터가 너무 적으면 공간을 다 못 덮고(생성 실패), 너무 많으면 종속이 됩니다. 기저는 그 사이의 “딱 맞는” 개수입니다.</li></ul>
    </div>
    <div class="lab">
      <div class="card"><h3>기저 B의 격자 <small>b₁, b₂, x를 끌어 보세요</small></h3><div class="viz" id="bs-viz"></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>b₁</span><span><i style="background:var(--e2)"></i>b₂</span><span><i style="background:var(--accent)"></i>x</span></div></div>
      <div class="card"><h3>좌표 구하기 전개</h3><div id="bs-out"></div></div>
    </div>`;
    let B1 = [2, 1], B2 = [-1, 1.5], Xv = [3, 3.5];
    const plane = new Plane(root.querySelector('#bs-viz'), { range: 5, aspect: 0.9 });
    plane.handle({ get: () => B1, set: (p) => (B1 = p), color: 'e1' }).handle({ get: () => B2, set: (p) => (B2 = p), color: 'e2' }).handle({ get: () => Xv, set: (p) => (Xv = p), color: 'accent' });
    plane.draw = (p) => {
      const P = [[B1[0], B2[0]], [B1[1], B2[1]]], d = N.det(P);
      if (Math.abs(d) > 1e-9) {
        p.tgrid(P, 'accent', 0.28);
        const c = N.mv(N.inv(P), Xv), a = N.vs(B1, c[0]);
        p.arrow([0, 0], a, 'e1', { w: 4, alpha: 0.45 }); p.arrow(a, Xv, 'e2', { w: 4, alpha: 0.45 });
        p.text(N.vs(a, 0.5), `${fmt(c[0], 2)}b₁`, 'e1', 0, 14); p.text(N.vadd(a, N.vs(N.vsub(Xv, a), 0.5)), `${fmt(c[1], 2)}b₂`, 'e2', 18, 0);
      } else p.infLine([0, 0], N.norm(B1) > 1e-9 ? B1 : B2, 'warn', 4);
      p.arrow([0, 0], B1, 'e1', { label: 'b₁' }); p.arrow([0, 0], B2, 'e2', { label: 'b₂' }); p.arrow([0, 0], Xv, 'accent', { label: 'x', w: 3 });
    };
    plane.onchange = out;
    function out() {
      const P = [[B1[0], B2[0]], [B1[1], B2[1]]], d = N.det(P);
      if (Math.abs(d) < 1e-9) { root.querySelector('#bs-out').innerHTML = `<span class="pill bad">기저 아님</span><p>b₁과 b₂가 한 직선 위에 있습니다(종속). 빨간 직선 밖의 벡터는 만들 수 없어서 ℝ²를 생성하지 못합니다.</p>`; return; }
      const c1 = (Xv[0] * B2[1] - B2[0] * Xv[1]) / d, c2 = (B1[0] * Xv[1] - Xv[0] * B1[1]) / d;
      root.querySelector('#bs-out').innerHTML = `<span class="pill ok">기저 (det = ${fmt(d)} ≠ 0)</span>
        <div class="math">${v('c', 1)}${LA.col([B1[0], B1[1]].map((x) => fmt(x)), {})} + ${v('c', 2)}${LA.col([B2[0], B2[1]].map((x) => fmt(x)))} = ${LA.col(Xv.map((x) => fmt(x)))}</div>
        <div class="calc"><span class="ln">성분별 방정식:</span><span class="ln">  ${fmt(B1[0])}·c₁ + ${par(B2[0])}·c₂ = ${fmt(Xv[0])}</span><span class="ln">  ${fmt(B1[1])}·c₁ + ${par(B2[1])}·c₂ = ${fmt(Xv[1])}</span>
        <span class="ln">크래머 공식으로:</span><span class="ln">  c₁ = (${fmt(Xv[0])}·${par(B2[1])} − ${par(B2[0])}·${par(Xv[1])}) / ${fmt(d)} = <b>${fmt(c1)}</b></span><span class="ln">  c₂ = (${fmt(B1[0])}·${par(Xv[1])} − ${par(Xv[0])}·${par(B1[1])}) / ${fmt(d)} = <b>${fmt(c2)}</b></span></div>
        <div class="math">[<b>x</b>]<sub><i>B</i></sub> = (${fmt(c1)}, ${fmt(c2)})   <span class="small muted">vs 표준 좌표 (${fmt(Xv[0])}, ${fmt(Xv[1])})</span></div>
        <p class="small">같은 화살표 <b>x</b>라도 어떤 자(기저)로 재느냐에 따라 좌표 숫자가 달라집니다. 파란 격자의 칸 수를 세면 [<b>x</b>]<sub>B</sub>가 됩니다.</p>`;
    }
    out();
  },
});

/* ======================================================= 3.6 행공간, 열공간, 영공간 */
LA.section({
  id: 'fourspaces', ch: 3, title: '행공간 · 열공간 · 영공간과 랭크', en: 'Row, Column and Null Spaces; Rank–Nullity',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead"><i>m</i>×<i>n</i> 행렬 <i>A</i>에는 중요한 부분공간이 세 개 붙어 있습니다. 셋 다 RREF 하나로 기저를 읽어 낼 수 있습니다.</p>
      <table class="t"><thead><tr><th>공간</th><th>뜻</th><th>기저 읽는 법</th><th>차원</th></tr></thead><tbody>
        <tr><td><b>열공간</b> Col <i>A</i> ⊆ ℝ<sup><i>m</i></sup></td><td><i>A</i><b>x</b>로 만들 수 있는 모든 결과 (열들의 span)</td><td>RREF의 피벗 열 위치 → <b>원래 <i>A</i></b>의 그 열들</td><td>rank</td></tr>
        <tr><td><b>행공간</b> Row <i>A</i> ⊆ ℝ<sup><i>n</i></sup></td><td>행들의 span</td><td>RREF의 0이 아닌 행들</td><td>rank</td></tr>
        <tr><td><b>영공간</b> Null <i>A</i> ⊆ ℝ<sup><i>n</i></sup></td><td><i>A</i><b>x</b> = <b>0</b>의 모든 해</td><td>자유변수마다 1을 넣어 얻은 해 벡터</td><td>nullity</td></tr>
      </tbody></table>
      <div class="keyline"><span class="lbl">랭크-널리티 정리</span>rank <i>A</i> + nullity <i>A</i> = <i>n</i> (열의 개수)  —  피벗 변수 + 자유변수 = 전체 변수</div>
    </div>
    <div class="lab">
      <div class="card"><h3><i>A</i> 입력</h3><div id="fs-ed"></div><div id="fs-bar"></div></div>
      <div class="card"><h3>ℝ³ 그림 <small>n = 3일 때: 행공간 ⟂ 영공간</small></h3><div class="viz" id="fs-viz"></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>행공간</span><span><i style="background:var(--e2)"></i>영공간</span></div><p class="small muted" id="fs-cap"></p></div>
    </div>
    <div class="card"><h3>RREF와 피벗</h3><div class="scroll"><div class="mxrow" id="fs-r"></div></div></div>
    <div class="lab">
      <div class="card"><h3>열공간 · 행공간 기저</h3><div id="fs-cr"></div></div>
      <div class="card"><h3>영공간: 해를 벡터 꼴로 전개</h3><div id="fs-null"></div></div>
    </div>`;
    let A, res;
    const viz = root.querySelector('#fs-viz'); const view = new View3D(viz, { range: 3.5 });
    view.draw = (p) => {
      if (!A || A[0].length !== 3) return;
      const rows = res.R.filter((r) => r.some((x) => !x.isZero())).map((r) => r.map((x) => x.val()));
      const nb = X.nullBasis(res.R, res.pivots, 3).map((b) => b.v.map((x) => x.val()));
      const drawSpan = (V, c) => {
        if (V.length === 1) { const d = N.vs(V[0], 5 / N.norm(V[0])); p.seg(N.vs(d, -1), d, c, { w: 5, alpha: 0.35 }); }
        if (V.length === 2) p.planePatch(V[0], V[1], c);
        V.forEach((x) => p.arrow([0, 0, 0], x, c));
      };
      drawSpan(rows, 'e1'); drawSpan(nb, 'e2');
    };
    function run(M) {
      A = M; const m = A.length, n = A[0].length; res = X.rref(A, n); const r = res.rank, pc = res.pivots.map((p) => p[1]);
      const free = [...Array(n).keys()].filter((j) => !pc.includes(j)); const nb = X.nullBasis(res.R, res.pivots, n);
      root.querySelector('#fs-bar').innerHTML = `<div class="small muted">열 ${n}개 = 피벗 ${r}개 + 자유 ${n - r}개</div><div class="bar">${r ? `<span style="flex-grow:${r};background:var(--e1)">rank ${r}</span>` : ''}${n - r ? `<span style="flex-grow:${n - r};background:var(--e2)">nullity ${n - r}</span>` : ''}</div>`;
      root.querySelector('#fs-r').innerHTML = mat(A, { name: 'A', sub: 'a', cell: (i, j) => (pc.includes(j) ? 'h1' : 'h2') }) + '<span class="op">RREF →</span>' + mat(res.R, { name: 'R', cell: (i, j) => (res.pivots.some((p) => p[0] === i && p[1] === j) ? 'pv' : pc.includes(j) ? '' : 'h2') });
      root.querySelector('#fs-cr').innerHTML = `<p class="small">피벗 열: <b>${pc.map((j) => j + 1).join(', ') || '없음'}</b>번째 → <b>원래 A</b>에서 이 열들을 가져옵니다. (RREF의 열이 아닙니다! 행 연산은 열공간을 바꾸기 때문입니다.)</p>
        <div class="mxrow">${pc.map((j) => LA.col(A.map((row) => row[j]), { name: `a<sub>${j + 1}</sub>`, noeq: true })).join('<span class="op">,</span>') || '{0}'}</div>
        <p class="small muted">Col A = span{${pc.map((j) => `a${j + 1}`).join(', ')}} ⊆ ℝ<sup>${m}</sup>, dim = ${r}</p><div class="sep"></div>
        <p class="small">행공간 기저: RREF의 0이 아닌 행 (행 연산은 행공간을 바꾸지 않습니다)</p>
        <div class="calc">${res.R.slice(0, r).map((row, i) => `<span class="ln">r${i + 1} = (${row.map((x) => x.toString()).join(', ')})</span>`).join('') || '<span class="ln">{0}</span>'}</div>`;
      const names = (j) => `x<sub>${j + 1}</sub>`; const params = ['s', 't', 'u', 'w'];
      let h = `<p class="small">R<b>x</b> = <b>0</b>을 피벗 변수에 대해 풀면 (자유변수: ${free.map((j) => `x${j + 1}`).join(', ') || '없음'})</p><div class="calc">`;
      res.pivots.forEach(([i, c]) => { h += `<span class="ln">${names(c)} = ${free.map((fj) => { const k = res.R[i][fj].neg(); return k.isZero() ? '' : `${k.sign() < 0 ? ' − ' : ' + '}${k.abs().isOne() ? '' : k.abs().html()}${names(fj)}`; }).join('').replace(/^ \+ /, '').replace(/^ − /, '−') || '0'}</span>`; });
      free.forEach((fj, t) => { h += `<span class="ln">${names(fj)} = ${params[t]}  <span class="muted">(자유)</span></span>`; });
      h += '</div>';
      if (nb.length) {
        h += `<div class="math">${LA.col([...Array(n).keys()].map((j) => names(j)))} = ${nb.map((b, t) => `${params[t]}${LA.col(b.v)}`).join(' + ')}</div>`;
        h += `<p class="small">검산 (A·v = 0):</p><div class="calc">${nb.map((b, t) => A.map((row, i) => `<span class="ln">v${t + 1}, ${i + 1}행: ${row.map((a, j) => `${par(a)}·${par(b.v[j])}`).join(' + ')} = <b>${row.reduce((s, a, j) => s.add(a.mul(b.v[j])), f(0)).html()}</b></span>`).join('')).join('')}</div>`;
      } else h += `<p>자유변수가 없으므로 Null A = {<b>0</b>}, nullity = 0.</p>`;
      root.querySelector('#fs-null').innerHTML = h;
      viz.parentElement.hidden = n !== 3;
      if (n === 3) {
        const rows = res.R.slice(0, r).map((row) => row.map((x) => x.val()));
        root.querySelector('#fs-cap').textContent = `행공간 ${r}차원 + 영공간 ${3 - r}차원 = 3. 행공간의 모든 벡터는 영공간의 모든 벡터와 수직입니다 (Ax = 0은 "모든 행과 x의 내적이 0"이라는 뜻이기 때문).` + (nb.length && rows.length ? ` 예: r1·v1 = ${fmt(N.dot(rows[0], nb[0].v.map((x) => x.val())))}` : '');
      }
      view.render();
    }
    editor(root.querySelector('#fs-ed'), X.fromN([[1, 2, 1], [2, 4, 0], [3, 6, 1]]), run, {
      resize: { minR: 1, maxR: 4, minC: 2, maxC: 5 },
      presets: [{ name: '3×3 랭크 2', A: [[1, 2, 1], [2, 4, 0], [3, 6, 1]] }, { name: '3×3 랭크 1', A: [[1, -1, 2], [2, -2, 4], [-1, 1, -2]] }, { name: '3×4', A: [[1, 2, 0, 3], [2, 4, 1, 8], [-1, -2, 1, -1]] }, { name: '3×5', A: [[1, 3, 0, 2, -1], [0, 0, 1, 4, 2], [1, 3, 1, 6, 1]] }],
    });
    run(X.fromN([[1, 2, 1], [2, 4, 0], [3, 6, 1]]));
  },
});
})();
