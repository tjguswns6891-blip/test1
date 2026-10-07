/* 4장 선형 변환 */
(function () {
'use strict';
const { F, f, X, N, mat, fh, par, term, v, editor, Plane, MINUS, fmt } = LA;
LA.chapter(4, '선형 변환', 'Linear Transformations');
const vec2 = (p) => `(${fmt(p[0])}, ${fmt(p[1])})`;
const m2 = (A) => mat(A.map((r) => r.map((x) => fmt(x))));

const PRESETS = [
  { name: '층밀림', A: [[1, 1], [0, 1]] },
  { name: '90° 회전', A: [[0, -1], [1, 0]] },
  { name: '늘이기', A: [[2, 0], [0, 0.5]] },
  { name: 'y = x 대칭', A: [[0, 1], [1, 0]] },
  { name: 'x축 정사영', A: [[1, 0], [0, 0]] },
  { name: '납작 (랭크 1)', A: [[1, 2], [0.5, 1]] },
  { name: '일반', A: [[2, 1], [1, 1.5]] },
];
/* 2×2 행렬 입력: 4개 슬라이더 + 프리셋 */
function matSliders(host, A, cb, idp) {
  host.innerHTML = `<div class="row">${PRESETS.map((p, i) => `<button type="button" class="chip" data-p="${i}">${p.name}</button>`).join('')}</div>
    <div class="sliders">${[['a', 0, 0], ['b', 0, 1], ['c', 1, 0], ['d', 1, 1]].map(([n, i, j]) => LA.slider(`${idp}-${i}${j}`, `<i class="var">a</i><sub>${i + 1}${j + 1}</sub>`, -3, 3, 0.25, A[i][j])).join('')}</div>`;
  const ids = ['00', '01', '10', '11'].map((s) => `${idp}-${s}`);
  const get = LA.bindSliders(host, ids, () => { const g = get(); A[0][0] = g[ids[0]]; A[0][1] = g[ids[1]]; A[1][0] = g[ids[2]]; A[1][1] = g[ids[3]]; cb(); });
  host.addEventListener('click', (e) => {
    const b = e.target.closest('[data-p]'); if (!b) return; const P = PRESETS[+b.dataset.p].A;
    ids.forEach((id, k) => { const el = host.querySelector('#' + id); el.value = P[k >> 1][k & 1]; host.querySelector('#' + id + '-o').textContent = fmt(+el.value); A[k >> 1][k & 1] = P[k >> 1][k & 1]; });
    cb(true);
  });
}
LA.matSliders = matSliders;

/* ======================================================= 4.1 선형 변환, 커널과 치역 */
LA.section({
  id: 'lintrans', ch: 4, title: '선형 변환: 커널과 상공간', en: 'Kernel and Range',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">함수 <i>T</i> : <i>V</i> → <i>W</i>가 <b>선형</b>이라는 것은 덧셈과 상수배를 그대로 보존한다는 뜻입니다. 그림으로는 <b>격자선이 평행하고 고르게 남고, 원점이 고정</b>되는 변환입니다.</p>
      <div class="keyline"><span class="lbl">선형성</span><i>T</i>(<b>u</b> + <b>v</b>) = <i>T</i>(<b>u</b>) + <i>T</i>(<b>v</b>) ,   <i>T</i>(<i>k</i><b>u</b>) = <i>k</i> <i>T</i>(<b>u</b>)</div>
      <ul><li><b>커널</b> ker <i>T</i> = {<b class="vec">x</b> | <i>T</i>(<b class="vec">x</b>) = <b class="vec">0</b>}: 원점으로 뭉개지는 벡터들. 행렬로는 영공간.</li>
        <li><b>상공간(치역)</b> range <i>T</i> = {<i>T</i>(<b class="vec">x</b>)}: 도달할 수 있는 결과 전체. 행렬로는 열공간.</li>
        <li>dim ker <i>T</i> + dim range <i>T</i> = dim <i>V</i>. 커널이 커질수록(많이 뭉갤수록) 상공간은 작아집니다.</li></ul>
    </div>
    <div class="lab">
      <div class="card"><h3>변환 <i>T</i>(<b>x</b>) = <i>A</i><b>x</b></h3><div id="lt-ctl"></div>${LA.slider('lt-t', '진행 t', 0, 1, 0.01, 1)}
        <div class="row"><button type="button" class="btn primary" id="lt-play">변환 애니메이션</button></div><div id="lt-info"></div></div>
      <div class="card"><div class="viz" id="lt-viz"></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>T(e₁) = 1열</span><span><i style="background:var(--e2)"></i>T(e₂) = 2열</span><span><i style="background:var(--warn)"></i>커널</span><span><i style="background:var(--ok)"></i>상공간</span><span><i style="background:var(--accent)"></i>x와 T(x) (x는 끌기)</span></div></div>
    </div>
    <details class="expand" open><summary>선형성 확인 전개</summary><div class="body" id="lt-lin"></div></details>`;
    const A = [[1, 1], [0, 1]]; let x = [1.5, 1], u = [1, -1];
    const plane = new Plane(root.querySelector('#lt-viz'), { range: 5, aspect: 0.9, snap: 0.25 });
    plane.handle({ get: () => x, set: (p) => (x = p), color: 'accent' });
    const getT = LA.bindSliders(root, ['lt-t'], () => plane.changed());
    const M = () => { const t = getT()['lt-t']; return [[1 + (A[0][0] - 1) * t, A[0][1] * t], [A[1][0] * t, 1 + (A[1][1] - 1) * t]]; };
    plane.draw = (p) => {
      const Mt = M(), d = N.det(A);
      p.tgrid(Mt, 'accent', 0.32);
      p.poly([[0, 0], [Mt[0][0], Mt[1][0]], [Mt[0][0] + Mt[0][1], Mt[1][0] + Mt[1][1]], [Mt[0][1], Mt[1][1]]], 'accent', null, { a: 0.12 });
      if (Math.abs(d) < 1e-9) {
        const e = N.eig2(A); // 커널 방향: A의 영공간
        const k = Math.abs(A[0][0]) + Math.abs(A[0][1]) > 1e-9 ? [-A[0][1], A[0][0]] : [-A[1][1], A[1][0]];
        if (N.norm(k) > 1e-9) p.infLine([0, 0], k, 'warn', 3, true);
        const cR = N.norm([A[0][0], A[1][0]]) > 1e-9 ? [A[0][0], A[1][0]] : [A[0][1], A[1][1]];
        if (N.norm(cR) > 1e-9 && getT()['lt-t'] > 0.99) p.infLine([0, 0], cR, 'ok', 3);
        void e;
      }
      p.arrow([0, 0], [Mt[0][0], Mt[1][0]], 'e1', { label: 'T(e₁)' }); p.arrow([0, 0], [Mt[0][1], Mt[1][1]], 'e2', { label: 'T(e₂)' });
      const Tx = N.mv(Mt, x); p.arrow([0, 0], x, 'accent', { w: 1.5, dash: true, alpha: 0.6 }); p.arrow([0, 0], Tx, 'accent', { label: 'T(x)' });
      if (N.norm(N.vsub(Tx, x)) > 0.05) p.seg(x, Tx, 'muted', { dash: [2, 4], w: 1 });
    };
    plane.onchange = info;
    function info() {
      const d = N.det(A), Tx = N.mv(A, x), rank = Math.abs(d) > 1e-9 ? 2 : (A.flat().some((a) => Math.abs(a) > 1e-9) ? 1 : 0);
      const ker = 2 - rank;
      root.querySelector('#lt-info').innerHTML = `<div class="mxrow">${m2(A)}${LA.col(x.map((t) => fmt(t)))}<span class="op">=</span>${LA.col(Tx.map((t) => fmt(t)))}</div>
        <div class="calc"><span class="ln">T(x) = x₁·(1열) + x₂·(2열) = ${fmt(x[0])}·${vec2([A[0][0], A[1][0]])} + ${par(x[1])}·${vec2([A[0][1], A[1][1]])} = <b>${vec2(Tx)}</b></span><span class="ln">det A = ${fmt(d)}</span></div>
        <table class="t"><tbody><tr><td>ker T</td><td>${ker === 0 ? '{0} (원점만) — 0차원' : ker === 1 ? '<span class="tw">직선 (빨간 점선)</span> — 1차원' : 'ℝ² 전체 — 2차원'}</td></tr>
        <tr><td>range T</td><td>${rank === 2 ? 'ℝ² 전체 — 2차원' : rank === 1 ? '<span class="tok">직선 (초록)</span> — 1차원' : '{0} — 0차원'}</td></tr>
        <tr><td>합</td><td>${ker} + ${rank} = 2 = dim ℝ² ✓</td></tr></tbody></table>`;
      const s = N.vadd(x, u), k = 2;
      root.querySelector('#lt-lin').innerHTML = `<p class="small">x = ${vec2(x)} (그림에서 끌기), u = ${vec2(u)}, k = ${k}</p><div class="calc">
        <span class="ln">T(x + u) = A${vec2(s)} = (${fmt(A[0][0])}·${par(s[0])} + ${par(A[0][1])}·${par(s[1])}, ${fmt(A[1][0])}·${par(s[0])} + ${par(A[1][1])}·${par(s[1])}) = <b>${vec2(N.mv(A, s))}</b></span>
        <span class="ln">T(x) + T(u) = ${vec2(N.mv(A, x))} + ${vec2(N.mv(A, u))} = <b>${vec2(N.vadd(N.mv(A, x), N.mv(A, u)))}</b>  ✓ 같음</span>
        <span class="ln">T(${k}x) = A${vec2(N.vs(x, k))} = <b>${vec2(N.mv(A, N.vs(x, k)))}</b>,   ${k}·T(x) = ${k}·${vec2(N.mv(A, x))} = <b>${vec2(N.vs(N.mv(A, x), k))}</b>  ✓</span></div>
        <p class="small muted">반례: 평행이동 S(x) = x + (1, 0)은 S(0) = (1, 0) ≠ 0이라 선형이 아닙니다. 선형 변환은 반드시 원점을 원점으로 보냅니다.</p>`;
    }
    matSliders(root.querySelector('#lt-ctl'), A, () => plane.changed(), 'lt');
    root.querySelector('#lt-play').addEventListener('click', () => {
      const el = root.querySelector('#lt-t'), o = root.querySelector('#lt-t-o');
      LA.tween(1600, (t) => { el.value = t; o.textContent = fmt(t, 2); plane.changed(); });
    });
    info();
  },
});

/* ======================================================= 4.2 행렬 표현 */
LA.section({
  id: 'matrep', ch: 4, title: '선형 변환의 행렬 표현', en: 'Matrix of a Linear Transformation',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">선형 변환은 <b>기저 벡터가 어디로 가는지</b>만 알면 전부 결정됩니다. <b class="vec">x</b> = <i>x</i><sub>1</sub><b class="vec">e</b><sub>1</sub> + <i>x</i><sub>2</sub><b class="vec">e</b><sub>2</sub>이면 선형성 때문에 <i>T</i>(<b class="vec">x</b>) = <i>x</i><sub>1</sub><i>T</i>(<b class="vec">e</b><sub>1</sub>) + <i>x</i><sub>2</sub><i>T</i>(<b class="vec">e</b><sub>2</sub>)이기 때문입니다.</p>
      <div class="keyline"><span class="lbl">표준 행렬: j번째 열 = T(eⱼ)</span><i>A</i> = [ <i>T</i>(<b>e</b><sub>1</sub>)  <i>T</i>(<b>e</b><sub>2</sub>)  ⋯  <i>T</i>(<b>e</b><sub><i>n</i></sub>) ]</div>
      <div class="keyline"><span class="lbl">기저 B = {b₁, …, bₙ}에 대한 행렬: j번째 열 = T(bⱼ)의 B-좌표</span>[<i>T</i>]<sub><i>B</i></sub> = [ [<i>T</i>(<b>b</b><sub>1</sub>)]<sub><i>B</i></sub>  ⋯  [<i>T</i>(<b>b</b><sub><i>n</i></sub>)]<sub><i>B</i></sub> ] = <i>P</i><sup>−1</sup><i>AP</i>,  <i>P</i> = [<b>b</b><sub>1</sub> ⋯ <b>b</b><sub><i>n</i></sub>]</div>
    </div>
    <div id="mr-tabs"></div><div id="mr-body" class="page" style="gap:20px"></div>`;
    const body = root.querySelector('#mr-body');
    LA.tabs(root.querySelector('#mr-tabs'), ['표준 기저', '일반 기저 B'], (t) => { LA.cleanup(); (t ? general : standard)(body); });
  },
});
function standard(body) {
  body.innerHTML = `<div class="lab">
    <div class="card"><h3>T(e₁), T(e₂)의 끝점을 끌어 변환 정하기</h3><div class="viz" id="ms-viz"></div>
      <div class="legend"><span><i style="background:var(--e1)"></i>T(e₁)</span><span><i style="background:var(--e2)"></i>T(e₂)</span><span><i style="background:var(--accent)"></i>x → T(x)</span></div></div>
    <div class="card"><h3>행렬이 만들어지는 과정</h3><div id="ms-out"></div></div></div>`;
  let c1 = [2, 0.5], c2 = [-0.5, 1.5]; const x = [1, 2];
  const plane = new Plane(body.querySelector('#ms-viz'), { range: 5, aspect: 0.9 });
  plane.handle({ get: () => c1, set: (p) => (c1 = p), color: 'e1' }).handle({ get: () => c2, set: (p) => (c2 = p), color: 'e2' });
  plane.draw = (p) => {
    const A = [[c1[0], c2[0]], [c1[1], c2[1]]]; p.tgrid(A, 'accent', 0.25);
    p.arrow([0, 0], [1, 0], 'e1', { w: 1.5, alpha: 0.4, label: 'e₁' }); p.arrow([0, 0], [0, 1], 'e2', { w: 1.5, alpha: 0.4, label: 'e₂' });
    const a = N.vs(c1, x[0]), Tx = N.mv(A, x);
    p.arrow([0, 0], a, 'e1', { w: 4, alpha: 0.35 }); p.arrow(a, Tx, 'e2', { w: 4, alpha: 0.35 });
    p.arrow([0, 0], c1, 'e1', { label: 'T(e₁)' }); p.arrow([0, 0], c2, 'e2', { label: 'T(e₂)' });
    p.arrow([0, 0], x, 'accent', { w: 1.5, dash: true, alpha: 0.6, label: 'x' }); p.arrow([0, 0], Tx, 'accent', { label: 'T(x)' });
  };
  plane.onchange = out;
  function out() {
    const A = [[c1[0], c2[0]], [c1[1], c2[1]]], Tx = N.mv(A, x);
    body.querySelector('#ms-out').innerHTML = `<div class="mxrow">${mat([[`<span class="t1">${fmt(c1[0])}</span>`, `<span class="t2">${fmt(c2[0])}</span>`], [`<span class="t1">${fmt(c1[1])}</span>`, `<span class="t2">${fmt(c2[1])}</span>`]], { name: 'A', sub: 'a' })}</div>
      <p class="small"><span class="t1">주황 열</span> = T(e₁) = ${vec2(c1)}, <span class="t2">초록 열</span> = T(e₂) = ${vec2(c2)}. 화살표 끝 좌표가 그대로 열이 됩니다.</p>
      <div class="calc"><span class="ln">x = ${vec2(x)} = ${fmt(x[0])}·e₁ + ${fmt(x[1])}·e₂</span>
      <span class="ln">T(x) = ${fmt(x[0])}·T(e₁) + ${fmt(x[1])}·T(e₂)       ← 선형성</span>
      <span class="ln">     = ${fmt(x[0])}·${vec2(c1)} + ${fmt(x[1])}·${vec2(c2)}</span>
      <span class="ln">     = (${fmt(x[0])}·${par(c1[0])} + ${fmt(x[1])}·${par(c2[0])}, ${fmt(x[0])}·${par(c1[1])} + ${fmt(x[1])}·${par(c2[1])}) = <b>${vec2(Tx)}</b></span>
      <span class="ln">이것이 바로 행렬 곱 A·x의 계산 규칙입니다.</span></div>`.replace(/ {2,}/g, (s) => '&nbsp;'.repeat(s.length));
  }
  out();
}
function general(body) {
  body.innerHTML = `<div class="lab">
    <div class="card"><h3>변환 A와 기저 B</h3><div id="mg-ctl"></div><p class="small muted">그림에서 b₁, b₂를 끌어 기저를 바꾸세요. 고유벡터 쪽으로 맞추면 [T]<sub>B</sub>가 대각행렬이 됩니다.</p></div>
    <div class="card"><div class="viz" id="mg-viz"></div><div class="legend"><span><i style="background:var(--e1)"></i>b₁ → T(b₁)</span><span><i style="background:var(--e2)"></i>b₂ → T(b₂)</span></div></div></div>
    <details class="expand" open><summary>[T]<sub>B</sub>를 열마다 구하는 전개</summary><div class="body" id="mg-out"></div></details>`;
  const A = [[2, 1], [1, 2]]; let b1 = [1, 1], b2 = [-1, 2];
  const plane = new Plane(body.querySelector('#mg-viz'), { range: 5, aspect: 0.9 });
  plane.handle({ get: () => b1, set: (p) => (b1 = p), color: 'e1' }).handle({ get: () => b2, set: (p) => (b2 = p), color: 'e2' });
  plane.draw = (p) => {
    const P = [[b1[0], b2[0]], [b1[1], b2[1]]]; if (Math.abs(N.det(P)) > 1e-9) p.tgrid(P, 'muted', 0.35);
    p.arrow([0, 0], N.mv(A, b1), 'e1', { label: 'T(b₁)', dash: true }); p.arrow([0, 0], N.mv(A, b2), 'e2', { label: 'T(b₂)', dash: true });
    p.arrow([0, 0], b1, 'e1', { label: 'b₁' }); p.arrow([0, 0], b2, 'e2', { label: 'b₂' });
  };
  plane.onchange = out;
  function out() {
    const P = [[b1[0], b2[0]], [b1[1], b2[1]]], d = N.det(P);
    if (Math.abs(d) < 1e-9) { body.querySelector('#mg-out').innerHTML = '<span class="pill bad">b₁, b₂가 평행해서 기저가 아닙니다.</span>'; return; }
    const Pi = N.inv(P), T1 = N.mv(A, b1), T2 = N.mv(A, b2), k1 = N.mv(Pi, T1), k2 = N.mv(Pi, T2), TB = N.mul(Pi, N.mul(A, P));
    const row = (Tb, k, j) => `<span class="ln"><b>${j}열</b>: T(b${j}) = A·b${j} = ${vec2(Tb)}</span><span class="ln">   ${vec2(Tb)} = c₁·b₁ + c₂·b₂ 를 풀면 → c₁ = <b>${fmt(k[0])}</b>, c₂ = <b>${fmt(k[1])}</b></span><span class="ln">   검산: ${fmt(k[0])}·${vec2(b1)} + ${par(k[1])}·${vec2(b2)} = ${vec2(N.vadd(N.vs(b1, k[0]), N.vs(b2, k[1])))}</span>`;
    body.querySelector('#mg-out').innerHTML = `<div class="calc">${row(T1, k1, 1)}${row(T2, k2, 2)}</div>`.replace(/ {2,}/g, (s) => '&nbsp;'.repeat(s.length)) +
      `<div class="mxrow">${mat([[fmt(TB[0][0]), fmt(TB[0][1])], [fmt(TB[1][0]), fmt(TB[1][1])]], { name: '[T]<sub>B</sub>', cell: (i, j) => (j ? 'h2' : 'h1') })}<span class="op">=</span>${mat(Pi.map((r) => r.map((t) => fmt(t))), { name: 'P<sup>−1</sup>', noeq: true })}${m2(A)}${mat(P.map((r) => r.map((t) => fmt(t))), { name: 'P', noeq: true })}</div>
      <p class="small">${Math.abs(TB[0][1]) < 1e-6 && Math.abs(TB[1][0]) < 1e-6 ? '<span class="pill ok">대각행렬!</span> b₁, b₂가 고유벡터라서 T가 각 기저 방향으로 늘이기만 합니다.' : '같은 변환 T지만 기저 B로 재면 행렬 숫자가 달라집니다. b₁ = (1, 1), b₂ = (−1, 1)로 끌어 보세요.'}</p>`;
  }
  LA.matSliders(body.querySelector('#mg-ctl'), A, () => plane.changed(), 'mg');
  out();
}

/* ======================================================= 4.3 기저 변환과 닮음 */
LA.section({
  id: 'cob', ch: 4, title: '기저 변환과 닮음 행렬', en: 'Change of Basis and Similarity',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">같은 벡터, 같은 변환이라도 <b>어떤 기저로 재느냐</b>에 따라 숫자가 바뀝니다. 기저를 바꾸는 번역기가 전이행렬 <i>P</i>입니다.</p>
      <div class="keyline"><span class="lbl">좌표 번역 (P의 열 = B의 기저 벡터를 표준 좌표로 쓴 것)</span><b>x</b> = <i>P</i> [<b>x</b>]<sub><i>B</i></sub>   ⟺   [<b>x</b>]<sub><i>B</i></sub> = <i>P</i><sup>−1</sup><b>x</b></div>
      <div class="keyline"><span class="lbl">닮음 — 같은 변환의 다른 표현</span>[<i>T</i>]<sub><i>B</i></sub> = <i>P</i><sup>−1</sup> <i>A</i> <i>P</i>   :   B좌표 → (<i>P</i>) 표준좌표 → (<i>A</i>) 변환 → (<i>P</i><sup>−1</sup>) B좌표</div>
      <p class="small muted">닮은 행렬은 같은 변환이므로 행렬식, 대각합(trace), 고윳값, 랭크가 모두 같습니다. 아래 두 그림은 같은 일을 표준 좌표(왼쪽)와 B 좌표(오른쪽)에서 본 것입니다. 오른쪽에서는 B의 격자가 바둑판으로 펴져 보입니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>표준 좌표 <small>x, b₁, b₂를 끌기</small></h3><div class="viz" id="cb-l"></div></div>
      <div class="card"><h3>B 좌표 <small>[x]<sub>B</sub> → [T]<sub>B</sub>[x]<sub>B</sub></small></h3><div class="viz" id="cb-r"></div></div>
    </div>
    <div class="lab">
      <div class="card"><h3>변환 A</h3><div id="cb-ctl"></div></div>
      <div class="card"><h3>번역 전개</h3><div id="cb-out"></div></div>
    </div>`;
    const A = [[1, 1], [0, 2]]; let b1 = [1, 0], b2 = [1, 1], x = [2, 1];
    const L = new Plane(root.querySelector('#cb-l'), { range: 5, aspect: 0.9 }), Rr = new Plane(root.querySelector('#cb-r'), { range: 5, aspect: 0.9, snap: 0 });
    L.handle({ get: () => x, set: (p) => (x = p), color: 'accent' }).handle({ get: () => b1, set: (p) => (b1 = p), color: 'e1' }).handle({ get: () => b2, set: (p) => (b2 = p), color: 'e2' });
    const P = () => [[b1[0], b2[0]], [b1[1], b2[1]]];
    L.draw = (p) => {
      const Pm = P(); if (Math.abs(N.det(Pm)) > 1e-9) p.tgrid(Pm, 'muted', 0.35);
      p.arrow([0, 0], b1, 'e1', { label: 'b₁' }); p.arrow([0, 0], b2, 'e2', { label: 'b₂' });
      p.arrow([0, 0], x, 'accent', { label: 'x' }); p.arrow([0, 0], N.mv(A, x), 'warn', { label: 'Ax', dash: true });
    };
    Rr.draw = (p) => {
      const Pm = P(); if (Math.abs(N.det(Pm)) < 1e-9) { p.text([0, 0], 'B가 기저가 아닙니다', 'warn', 0, 0); return; }
      const Pi = N.inv(Pm), xb = N.mv(Pi, x), TB = N.mul(Pi, N.mul(A, Pm));
      p.arrow([0, 0], [1, 0], 'e1', { label: '[b₁]' }); p.arrow([0, 0], [0, 1], 'e2', { label: '[b₂]' });
      p.arrow([0, 0], xb, 'accent', { label: '[x]B' }); p.arrow([0, 0], N.mv(TB, xb), 'warn', { label: '[Ax]B', dash: true });
    };
    L.onchange = () => { Rr.render(); out(); };
    function out() {
      const Pm = P(), d = N.det(Pm); if (Math.abs(d) < 1e-9) { root.querySelector('#cb-out').innerHTML = '<span class="pill bad">P가 비가역 — b₁, b₂를 평행하지 않게 놓으세요.</span>'; return; }
      const Pi = N.inv(Pm), xb = N.mv(Pi, x), TB = N.mul(Pi, N.mul(A, Pm)), ff = (M) => M.map((r) => r.map((t) => fmt(t)));
      const tr = (M) => M[0][0] + M[1][1];
      root.querySelector('#cb-out').innerHTML = `<div class="mxrow">${mat(ff(Pm), { name: 'P', cell: (i, j) => (j ? 'k2' : 'k1') })}${mat(ff(Pi), { name: 'P<sup>−1</sup>' })}</div>
        <div class="calc"><span class="ln">[x]_B = P⁻¹x = ${vec2(xb)}   ← x = ${fmt(xb[0])}·b₁ + ${fmt(xb[1])}·b₂</span><span class="ln">검산 P[x]_B = ${vec2(N.mv(Pm, xb))} = x ✓</span></div>
        <div class="mxrow">${mat(ff(TB), { name: '[T]<sub>B</sub>' })}<span class="op">=</span>${mat(ff(Pi), { name: '', noeq: true })}${mat(ff(A))}${mat(ff(Pm))}</div>
        <table class="t"><thead><tr><th>불변량</th><th>A</th><th>[T]<sub>B</sub></th></tr></thead><tbody>
          <tr><td>det</td><td class="num">${fmt(N.det(A))}</td><td class="num">${fmt(N.det(TB))}</td></tr>
          <tr><td>trace (대각합)</td><td class="num">${fmt(tr(A))}</td><td class="num">${fmt(tr(TB))}</td></tr>
          <tr><td>고윳값</td><td class="num">${eigTxt(A)}</td><td class="num">${eigTxt(TB)}</td></tr></tbody></table>
        <p class="small muted">b₁ = (1, 0), b₂ = (1, 1)은 이 A의 고유벡터라서 [T]<sub>B</sub>가 대각행렬 diag(1, 2)입니다.</p>`;
    }
    const eigTxt = (M) => { const e = N.eig2(M); return e.real ? `${fmt(e.l1)}, ${fmt(e.l2)}` : `${fmt(e.re)} ± ${fmt(e.im)}i`; };
    LA.matSliders(root.querySelector('#cb-ctl'), A, () => { L.render(); Rr.render(); out(); }, 'cb');
    out();
  },
});
})();
