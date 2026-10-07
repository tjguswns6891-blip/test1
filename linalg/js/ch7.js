/* 7장 행렬의 분해 및 고급 주제 */
(function () {
'use strict';
const { F, f, X, N, mat, fh, par, term, v, editor, stepper, Plane, View3D, MINUS, fmt } = LA;
LA.chapter(7, '행렬의 분해와 고급 주제', 'Matrix Decompositions');
const vec2 = (p) => `(${fmt(p[0])}, ${fmt(p[1])})`;
const ff = (M, d) => M.map((r) => r.map((t) => fmt(t, d)));
const symSliders = (id, a, b, c) => `<div class="sliders">${LA.slider(id + '-a', '<i class="var">a</i> (a₁₁)', -3, 3, 0.25, a)}${LA.slider(id + '-b', '<i class="var">b</i> (a₁₂=a₂₁)', -3, 3, 0.25, b)}${LA.slider(id + '-c', '<i class="var">c</i> (a₂₂)', -3, 3, 0.25, c)}</div>`;
/* 대칭 2×2 고유분해 (정규직교) */
function sym2(a, b, c) {
  const r = N.symEig([[a, b], [b, c]]); let q1 = [r.vecs[0][0], r.vecs[1][0]], q2 = [r.vecs[0][1], r.vecs[1][1]];
  if (q1[0] < -1e-9 || (Math.abs(q1[0]) < 1e-9 && q1[1] < 0)) q1 = N.vs(q1, -1);
  q2 = [-q1[1], q1[0]];
  return { l1: r.vals[0], l2: r.vals[1], q1, q2 };
}

/* ======================================================= 7.1 대칭행렬과 직교 대각화 */
LA.section({
  id: 'spectral', ch: 7, title: '대칭행렬과 직교 대각화', en: 'Symmetric Matrices and the Spectral Theorem',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">대칭행렬(<i>A</i><sup>T</sup> = <i>A</i>, 즉 <i>a<sub>ij</sub></i> = <i>a<sub>ji</sub></i>)은 특별합니다. 고윳값이 모두 실수이고, 서로 다른 고윳값의 고유벡터끼리 <b>반드시 수직</b>입니다. 그래서 <i>P</i>를 직교행렬 <i>Q</i>로 잡을 수 있습니다.</p>
      <div class="keyline"><span class="lbl">주축 정리 (스펙트럼 정리)</span><i>A</i> = <i>Q</i>Λ<i>Q</i><sup>T</sup> = λ<sub>1</sub><b>q</b><sub>1</sub><b>q</b><sub>1</sub><sup>T</sup> + λ<sub>2</sub><b>q</b><sub>2</sub><b>q</b><sub>2</sub><sup>T</sup> + ⋯ + λ<sub><i>n</i></sub><b>q</b><sub><i>n</i></sub><b>q</b><sub><i>n</i></sub><sup>T</sup></div>
      <p class="small muted">역행렬 대신 전치만 하면 되고(<i>Q</i><sup>−1</sup> = <i>Q</i><sup>T</sup>), 행렬이 “서로 수직인 축 방향으로 늘이기의 합”으로 쪼개집니다. 그림에서 단위원이 타원이 되는데, 타원의 두 축이 고유벡터(주축), 반지름이 |λ|입니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>대칭행렬 A = [a b; b c]</h3>${symSliders('sp', 2, 1, 2)}<div class="viz" id="sp-viz"></div>
        <div class="legend"><span><i style="background:var(--muted)"></i>단위원</span><span><i style="background:var(--accent)"></i>A·(단위원)</span><span><i style="background:var(--e1)"></i>λ₁q₁</span><span><i style="background:var(--e2)"></i>λ₂q₂</span></div></div>
      <div class="card"><h3>A = QΛQᵀ</h3><div id="sp-out"></div></div>
    </div>
    <details class="expand" open><summary>스펙트럼 분해 전개: λ₁q₁q₁ᵀ + λ₂q₂q₂ᵀ</summary><div class="body" id="sp-sum"></div></details>`;
    const plane = new Plane(root.querySelector('#sp-viz'), { range: 4.5, aspect: 0.85 });
    const get = LA.bindSliders(root, ['sp-a', 'sp-b', 'sp-c'], () => { plane.render(); out(); });
    const cur = () => { const g = get(); return [g['sp-a'], g['sp-b'], g['sp-c']]; };
    plane.draw = (p) => {
      const [a, b, c] = cur(), A = [[a, b], [b, c]], e = sym2(a, b, c);
      p.path((t) => [Math.cos(t * 6.2832), Math.sin(t * 6.2832)], 80, 'muted', { w: 1.5, dash: true });
      p.ellipse(A, 'accent', { fill: 'accent', a: 0.12, w: 2.5 });
      p.infLine([0, 0], e.q1, 'e1', 1, true); p.infLine([0, 0], e.q2, 'e2', 1, true);
      p.arrow([0, 0], N.vs(e.q1, e.l1), 'e1', { label: 'λ₁q₁' }); p.arrow([0, 0], N.vs(e.q2, e.l2), 'e2', { label: 'λ₂q₂' });
      p.arrow([0, 0], e.q1, 'e1', { w: 1.5, alpha: 0.5 }); p.arrow([0, 0], e.q2, 'e2', { w: 1.5, alpha: 0.5 });
    };
    function out() {
      const [a, b, c] = cur(), e = sym2(a, b, c), Q = [[e.q1[0], e.q2[0]], [e.q1[1], e.q2[1]]];
      root.querySelector('#sp-out').innerHTML = `<div class="mxrow">${mat(ff([[a, b], [b, c]]), { name: 'A', cell: (i, j) => (i !== j ? 'h2' : '') })}${mat(ff(Q), { cell: (i, j) => (j ? 'k2' : 'k1') })}${mat(ff([[e.l1, 0], [0, e.l2]]), { cell: (i, j) => (i === j ? 'h1' : 'dim') })}${mat(ff(N.T(Q)))}</div>
        <div class="calc"><span class="ln">λ = (tr ± √(tr² − 4det))/2 = (${fmt(a + c)} ± √(${fmt((a + c) ** 2)} − 4·${par(a * c - b * b)}))/2</span><span class="ln">λ₁ = <b>${fmt(e.l1)}</b>, λ₂ = <b>${fmt(e.l2)}</b>  (판별식 = (a−c)² + 4b² ≥ 0 → 항상 실수)</span>
          <span class="ln">q₁ = ${vec2(e.q1)},  q₂ = ${vec2(e.q2)}</span><span class="ln">q₁·q₂ = ${par(e.q1[0])}·${par(e.q2[0])} + ${par(e.q1[1])}·${par(e.q2[1])} = <b>${fmt(N.dot(e.q1, e.q2))}</b>  ← 수직</span>
          <span class="ln">QᵀQ = ${JSON.stringify(ff(N.mul(N.T(Q), Q))).replace(/"/g, '')} = I</span></div>`;
      const P1 = [[e.q1[0] * e.q1[0], e.q1[0] * e.q1[1]], [e.q1[1] * e.q1[0], e.q1[1] * e.q1[1]]], P2 = [[e.q2[0] * e.q2[0], e.q2[0] * e.q2[1]], [e.q2[1] * e.q2[0], e.q2[1] * e.q2[1]]];
      const S = N.add(N.scale(P1, e.l1), N.scale(P2, e.l2));
      root.querySelector('#sp-sum').innerHTML = `<p class="small">(q q<sup>T</sup>)<sub>jk</sub> = q<sub>j</sub>·q<sub>k</sub> — 열벡터 × 행벡터 = 랭크 1 행렬. 각각은 그 축 위로의 정사영 행렬입니다.</p>
        <div class="scroll"><div class="mxrow"><span class="math">${fmt(e.l1)}</span>${mat(ff(P1), { cell: () => 'h1' })}<span class="op">+</span><span class="math">${par(e.l2)}</span>${mat(ff(P2), { cell: () => 'h2' })}<span class="op">=</span>${mat(ff(S))}</div></div>
        <div class="calc">${[0, 1].map((j) => [0, 1].map((k) => `<span class="ln">a<sub>${j + 1}${k + 1}</sub> = λ₁·q₁${'₁₂'[j]}·q₁${'₁₂'[k]} + λ₂·q₂${'₁₂'[j]}·q₂${'₁₂'[k]} = ${fmt(e.l1)}·${par(e.q1[j])}·${par(e.q1[k])} + ${par(e.l2)}·${par(e.q2[j])}·${par(e.q2[k])} = <b>${fmt(S[j][k])}</b></span>`).join('')).join('')}</div>`;
    }
    out();
  },
});

/* ======================================================= 7.2 SVD */
LA.section({
  id: 'svd', ch: 7, title: '특이값 분해 (SVD)', en: 'Singular Value Decomposition',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">고윳값 분해는 정사각행렬, 그것도 일부에만 됩니다. SVD는 <b>모든</b> <i>m</i>×<i>n</i> 행렬을 회전·늘이기·회전으로 쪼갭니다.</p>
      <div class="keyline"><span class="lbl">A (m×n) = U (m×m, 직교) · Σ (m×n, 대각) · Vᵀ (n×n, 직교)</span><i>A</i> = <i>U</i>Σ<i>V</i><sup>T</sup> = σ<sub>1</sub><b>u</b><sub>1</sub><b>v</b><sub>1</sub><sup>T</sup> + σ<sub>2</sub><b>u</b><sub>2</sub><b>v</b><sub>2</sub><sup>T</sup> + ⋯ ,   σ<sub>1</sub> ≥ σ<sub>2</sub> ≥ ⋯ ≥ 0</div>
      <ul><li><b class="vec">v</b><sub><i>i</i></sub>: <i>A</i><sup>T</sup><i>A</i>의 고유벡터 (입력 공간의 서로 수직인 방향). σ<sub><i>i</i></sub> = √(<i>A</i><sup>T</sup><i>A</i>의 고윳값).</li>
        <li><b class="vec">u</b><sub><i>i</i></sub> = <i>A</i><b class="vec">v</b><sub><i>i</i></sub> / σ<sub><i>i</i></sub>: 출력 공간의 서로 수직인 방향. “수직인 방향들이 수직인 방향들로 간다.”</li>
        <li>앞쪽 몇 개의 항만 남기면 원래 행렬의 가장 좋은 저랭크 근사가 됩니다(에카르트-영 정리). 이미지 압축, 추천 시스템, PCA가 모두 이 원리입니다.</li></ul>
    </div>
    <div id="sv-tabs"></div><div id="sv-body" class="page" style="gap:20px"></div>`;
    const body = root.querySelector('#sv-body');
    LA.tabs(root.querySelector('#sv-tabs'), ['2×2 기하: 회전-늘이기-회전', '계산 전개 (직사각 행렬)', '이미지 압축'], (t) => { LA.cleanup(); [svdGeo, svdCalc, svdImg][t](body); });
  },
});
function svdGeo(body) {
  body.innerHTML = `<div class="lab">
    <div class="card"><h3 id="sg-cap">단위원에서 시작</h3><div class="viz" id="sg-viz"></div><div id="sg-step"></div>
      <div class="legend"><span><i style="background:var(--e1)"></i>v₁ → σ₁u₁</span><span><i style="background:var(--e2)"></i>v₂ → σ₂u₂</span></div></div>
    <div class="card"><h3>A</h3><div id="sg-ctl"></div><div id="sg-out"></div></div></div>`;
  const A = [[2, 1], [0.5, 1.5]]; let cur = N.eye(2), stage = 0, d;
  const plane = new Plane(body.querySelector('#sg-viz'), { range: 4, aspect: 0.85 });
  const dec = () => { const r = N.svd(A); let { U, S, V } = r; if (N.det(V) < 0) { V = V.map((row) => [row[0], -row[1]]); U = U.map((row) => [row[0], -row[1]]); } return { U, S, V }; };
  const stages = () => { const { U, S, V } = d, Sg = [[S[0], 0], [0, S[1]]], Vt = N.T(V); return [N.eye(2), Vt, N.mul(Sg, Vt), N.mul(U, N.mul(Sg, Vt))]; };
  plane.draw = (p) => {
    p.tgrid(cur, 'accent', 0.18);
    p.path((t) => N.mv(cur, [Math.cos(t * 6.2832), Math.sin(t * 6.2832)]), 90, 'accent', { fill: 'accent', a: 0.12, w: 2.5 });
    const v1 = [d.V[0][0], d.V[1][0]], v2 = [d.V[0][1], d.V[1][1]];
    p.arrow([0, 0], N.mv(cur, v1), 'e1', { label: stage === 3 ? 'σ₁u₁' : stage ? '' : 'v₁' }); p.arrow([0, 0], N.mv(cur, v2), 'e2', { label: stage === 3 ? 'σ₂u₂' : stage ? '' : 'v₂' });
  };
  d = dec();
  const caps = ['시작: 단위원과 v₁, v₂', '① Vᵀ: v₁, v₂를 좌표축으로 회전', '② Σ: 축 방향으로 σ₁, σ₂배', '③ U: u₁, u₂ 방향으로 회전 = A'];
  const sp = stepper(body.querySelector('#sg-step'), 4, (k) => {
    stage = k; body.querySelector('#sg-cap').textContent = caps[k]; const to = stages()[k], a0 = cur.map((r) => r.slice());
    LA.tween(800, (u) => { cur = N.add(N.scale(a0, 1 - u), N.scale(to, u)); plane.render(); });
  }, { ms: 1700 });
  function out() {
    d = dec(); cur = stages()[stage]; plane.render(); const { U, S, V } = d;
    body.querySelector('#sg-out').innerHTML = `<div class="mxrow">${mat(ff(A), { name: 'A' })}${mat(ff(U))}${mat(ff([[S[0], 0], [0, S[1]]]), { cell: (i, j) => (i === j ? 'h1' : 'dim') })}${mat(ff(N.T(V)))}</div>
      <div class="calc"><span class="ln">σ₁ = ${fmt(S[0])} = 타원의 긴 반지름 (A가 가장 많이 늘이는 배율)</span><span class="ln">σ₂ = ${fmt(S[1])} = 짧은 반지름</span><span class="ln">|det A| = σ₁σ₂ = ${fmt(S[0] * S[1])}</span></div>`;
  }
  LA.matSliders(body.querySelector('#sg-ctl'), A, out, 'sg');
  out();
}
function svdCalc(body) {
  body.innerHTML = `<div class="card"><h3>A (m×n)</h3><div id="sc-ed"></div></div>
    <details class="expand" open><summary>① AᵀA 만들기 (성분 = 열끼리의 내적)</summary><div class="body" id="sc-1"></div></details>
    <details class="expand" open><summary>② AᵀA의 고윳값 → 특이값, 고유벡터 → V</summary><div class="body" id="sc-2"></div></details>
    <details class="expand" open><summary>③ uᵢ = Avᵢ / σᵢ → U, 그리고 검산</summary><div class="body" id="sc-3"></div></details>`;
  editor(body.querySelector('#sc-ed'), X.fromN([[3, 1, 1], [-1, 3, 1]]), (Af) => {
    const A = X.toN(Af), m = A.length, n = A[0].length, AtA = X.mul(X.T(Af), Af);
    const cols = [...Array(n).keys()].map((j) => A.map((r) => r[j]));
    body.querySelector('#sc-1').innerHTML = `<div class="mxrow">${mat(X.T(Af), { name: 'A<sup>T</sup>', noeq: true })}${mat(Af)}<span class="op">=</span>${mat(AtA, { name: '', noeq: true })}<span class="small muted">${n}×${n} 대칭행렬</span></div>
      <div class="calc">${AtA.map((r, i) => r.map((x, j) => (j < i ? '' : `<span class="ln">(AᵀA)<sub>${i + 1}${j + 1}</sub> = a${i + 1}·a${j + 1} = ${cols[i].map((a, k) => `${par(a)}·${par(cols[j][k])}`).join(' + ')} = <b>${x.html()}</b></span>`)).join('')).join('')}</div>`;
    const eg = N.symEig(X.toN(AtA)); const r = eg.vals.filter((l) => l > 1e-9).length;
    const sig = eg.vals.map((l) => Math.sqrt(Math.max(0, l)));
    body.querySelector('#sc-2').innerHTML = `<p class="small">AᵀA는 대칭이고 고윳값이 모두 0 이상입니다 (xᵀAᵀAx = ‖Ax‖² ≥ 0). 고윳값을 큰 순서로:</p>
      <div class="calc">${eg.vals.map((l, i) => `<span class="ln">λ${i + 1} = ${fmt(l)}  →  σ${i + 1} = √${fmt(Math.max(0, l))} = <b>${fmt(sig[i])}</b>   v${i + 1} = (${eg.vecs.map((row) => fmt(row[i])).join(', ')})</span>`).join('')}</div>
      <p class="small">0이 아닌 특이값 ${r}개 = rank A = ${r}.</p><div class="mxrow">${mat(ff(eg.vecs), { name: 'V', cell: (i, j) => ['k1', 'k2', 'k3', ''][j] || '' })}</div>`;
    const Us = []; let lines = '';
    for (let i = 0; i < Math.min(r, m); i++) {
      const vi = eg.vecs.map((row) => row[i]), Av = N.mv(A, vi), u = N.vs(Av, 1 / sig[i]); Us.push(u);
      lines += `<span class="ln">u${i + 1} = A·v${i + 1} / σ${i + 1} = (${Av.map((t) => fmt(t)).join(', ')}) / ${fmt(sig[i])} = <b>(${u.map((t) => fmt(t)).join(', ')})</b></span>`;
    }
    if (Us.length < m) lines += `<span class="ln muted">남은 u는 앞의 u들에 수직인 단위벡터로 채웁니다 (Σ의 그 행이 0이라 결과에 영향 없음).</span>`;
    while (Us.length < m) { // 그람-슈미트로 채우기
      for (let e = 0; e < m && Us.length < m; e++) { let w = Array.from({ length: m }, (_, k) => (k === e ? 1 : 0)); Us.forEach((u) => (w = N.vsub(w, N.vs(u, N.dot(w, u))))); if (N.norm(w) > 1e-6) Us.push(N.vs(w, 1 / N.norm(w))); }
    }
    const U = N.T(Us), Sg = Array.from({ length: m }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? sig[i] : 0)));
    const back = N.mul(U, N.mul(Sg, N.T(eg.vecs)));
    body.querySelector('#sc-3').innerHTML = `<div class="calc">${lines}</div><div class="scroll"><div class="mxrow">${mat(ff(U), { name: 'U', noeq: true })}${mat(ff(Sg), { name: 'Σ', noeq: true, cell: (i, j) => (i === j ? 'h1' : 'dim') })}${mat(ff(N.T(eg.vecs)), { name: 'V<sup>T</sup>', noeq: true })}<span class="op">=</span>${mat(ff(back))}</div></div>
      <p class="small">σ₁u₁v₁ᵀ + σ₂u₂v₂ᵀ + … 로 원래 A가 정확히 복원됩니다. 크기: U ${m}×${m}, Σ ${m}×${n}, Vᵀ ${n}×${n}.</p>`;
  }, { resize: { minR: 1, maxR: 4, minC: 1, maxC: 4 }, presets: [{ name: '2×3', A: [[3, 1, 1], [-1, 3, 1]] }, { name: '3×2', A: [[1, 1], [0, 1], [1, 0]] }, { name: '랭크 1', A: [[1, 2], [2, 4], [3, 6]] }] });
  body.querySelector('#sc-ed input').dispatchEvent(new Event('input', { bubbles: true }));
}
function svdImg(body) {
  body.innerHTML = `<div class="lab">
    <div class="card"><h3>원본 <small id="si-dim"></small></h3><canvas id="si-orig" class="plane" style="image-rendering:pixelated;border-radius:6px"></canvas>
      <div class="row"><label class="btn" for="si-file">내 이미지로 바꾸기</label><input type="file" id="si-file" accept="image/*" hidden><span class="small muted">흑백으로 바꾸고 96픽셀 이하로 줄입니다. 이미지는 이 브라우저 밖으로 나가지 않습니다.</span></div></div>
    <div class="card"><h3>랭크 k 근사 <small id="si-k-cap"></small></h3><canvas id="si-appr" class="plane" style="image-rendering:pixelated;border-radius:6px"></canvas>${LA.slider('si-k', '남길 항 k', 1, 40, 1, 5)}</div></div>
    <div class="card"><h3>특이값 σᵢ <small>앞쪽 몇 개가 거의 모든 정보를 담습니다</small></h3><canvas id="si-bars" class="plane"></canvas><div id="si-stat" class="calc"></div></div>`;
  let G, dec;
  function sample() {
    const S = 72, c = document.createElement('canvas'); c.width = c.height = S; const x = c.getContext('2d');
    const g = x.createLinearGradient(0, 0, S, S); g.addColorStop(0, '#202838'); g.addColorStop(1, '#8a9bb8'); x.fillStyle = g; x.fillRect(0, 0, S, S);
    x.fillStyle = '#f2f2f2'; x.beginPath(); x.arc(50, 22, 12, 0, 7); x.fill();
    x.fillStyle = '#0e1320'; x.beginPath(); x.moveTo(0, 60); x.lineTo(22, 34); x.lineTo(38, 50); x.lineTo(52, 38); x.lineTo(72, 58); x.lineTo(72, 72); x.lineTo(0, 72); x.fill();
    x.strokeStyle = '#ffffff'; x.lineWidth = 2; for (let i = 0; i < 5; i++) { x.beginPath(); x.moveTo(6, 8 + i * 5); x.lineTo(28, 8 + i * 5); x.stroke(); }
    x.fillStyle = '#d0d0d0'; x.font = 'bold 15px sans-serif'; x.fillText('Aᵀ', 8, 68);
    return toGray(c);
  }
  function toGray(c) { const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; return Array.from({ length: c.height }, (_, i) => Array.from({ length: c.width }, (_, j) => { const k = 4 * (i * c.width + j); return (0.299 * d[k] + 0.587 * d[k + 1] + 0.114 * d[k + 2]) / 255; })); }
  function paint(cv, M) {
    const h = M.length, w = M[0].length; const host = cv.parentElement; const W = Math.min(host.clientWidth - 36, 360) || 300; const H = Math.round(W * h / w);
    cv.width = w; cv.height = h; cv.style.width = W + 'px'; cv.style.height = H + 'px';
    const x = cv.getContext('2d'), im = x.createImageData(w, h);
    M.forEach((r, i) => r.forEach((val, j) => { const g = Math.max(0, Math.min(255, Math.round(val * 255))), k = 4 * (i * w + j); im.data[k] = im.data[k + 1] = im.data[k + 2] = g; im.data[k + 3] = 255; }));
    x.putImageData(im, 0, 0);
  }
  function load(M) {
    G = M; dec = N.svd(G); const m = G.length, n = G[0].length;
    body.querySelector('#si-dim').textContent = `${m}×${n} = ${m * n}개 수`;
    const sl = body.querySelector('#si-k'); sl.max = Math.min(m, n); if (+sl.value > +sl.max) sl.value = sl.max;
    paint(body.querySelector('#si-orig'), G); approx(); bars();
  }
  function approx() {
    const k = +body.querySelector('#si-k').value, m = G.length, n = G[0].length;
    body.querySelector('#si-k-o').textContent = k;
    const M = Array.from({ length: m }, () => Array(n).fill(0));
    for (let t = 0; t < k; t++) { const s = dec.S[t]; for (let i = 0; i < m; i++) { const a = s * dec.U[i][t]; if (!a) continue; for (let j = 0; j < n; j++) M[i][j] += a * dec.V[j][t]; } }
    paint(body.querySelector('#si-appr'), M);
    const tot = dec.S.reduce((s, x) => s + x * x, 0), kept = dec.S.slice(0, k).reduce((s, x) => s + x * x, 0);
    body.querySelector('#si-k-cap').textContent = `σ₁u₁v₁ᵀ + … + σ${k}u${k}v${k}ᵀ`;
    body.querySelector('#si-stat').innerHTML = `<span class="ln">저장할 수: k(m + n + 1) = ${k}·(${m} + ${n} + 1) = <b>${k * (m + n + 1)}</b>  vs 원본 m·n = ${m * n}  → ${fmt((100 * k * (m + n + 1)) / (m * n), 1)}%</span><span class="ln">보존된 에너지 Σσᵢ²(i ≤ k) / Σσᵢ² = <b>${fmt((100 * kept) / tot, 2)}%</b></span>`;
    bars(k);
  }
  function bars(k = +body.querySelector('#si-k').value) {
    const cv = body.querySelector('#si-bars'), W = cv.parentElement.clientWidth - 36, H = 140, d = devicePixelRatio || 1;
    cv.width = W * d; cv.height = H * d; cv.style.height = H + 'px'; const x = cv.getContext('2d'); x.setTransform(d, 0, 0, d, 0, 0);
    x.fillStyle = LA.color('canvas'); x.fillRect(0, 0, W, H);
    const S = dec.S.slice(0, 40), mx = S[0] || 1, bw = (W - 40) / S.length;
    x.strokeStyle = LA.color('grid'); x.beginPath(); for (let t = 0; t <= 4; t++) { const y = 10 + (H - 30) * t / 4; x.moveTo(30, y); x.lineTo(W, y); } x.stroke();
    S.forEach((s, i) => { const h = (H - 30) * s / mx; x.fillStyle = LA.color(i < k ? 'accent' : 'axis'); x.fillRect(32 + i * bw, H - 20 - h, Math.max(1, bw - 2), h); });
    x.fillStyle = LA.color('muted'); x.font = '10px "JetBrains Mono", monospace'; x.textAlign = 'right'; x.fillText(fmt(mx, 1), 28, 14); x.fillText('0', 28, H - 20);
    x.textAlign = 'center'; [1, 10, 20, 30, 40].filter((t) => t <= S.length).forEach((t) => x.fillText(t, 32 + (t - 0.5) * bw, H - 6));
  }
  LA.bindSliders(body, ['si-k'], approx);
  body.querySelector('#si-file').addEventListener('change', (e) => {
    const file = e.target.files[0]; if (!file) return; const r = new FileReader();
    r.onload = () => { const img = new Image(); img.onload = () => { const s = 96 / Math.max(img.width, img.height), c = document.createElement('canvas'); c.width = Math.max(8, Math.round(img.width * Math.min(1, s))); c.height = Math.max(8, Math.round(img.height * Math.min(1, s))); c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); load(toGray(c)); }; img.src = r.result; };
    r.readAsDataURL(file);
  });
  load(sample());
}

/* ======================================================= 7.3 이차 형식 */
LA.section({
  id: 'quadform', ch: 7, title: '이차 형식', en: 'Quadratic Forms',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">모든 항이 2차인 다변수 다항식 <i>Q</i>(<i>x</i>, <i>y</i>) = <i>ax</i>² + 2<i>bxy</i> + <i>cy</i>²는 대칭행렬 하나로 씁니다. 교차항 2<i>bxy</i>는 <i>a</i><sub>12</sub><i>xy</i>와 <i>a</i><sub>21</sub><i>yx</i>로 반씩 나뉘어 들어갑니다.</p>
      <div class="keyline"><span class="lbl">행렬 표현</span><i>Q</i>(<b>x</b>) = <b>x</b><sup>T</sup><i>A</i><b>x</b> = <span class="sum">Σ</span><sub><i>i</i></sub><span class="sum">Σ</span><sub><i>j</i></sub> <i>a</i><sub><i>ij</i></sub><i>x</i><sub><i>i</i></sub><i>x</i><sub><i>j</i></sub>   →   주축 변환 <b>x</b> = <i>Q</i><b>y</b> 후   λ<sub>1</sub><i>y</i><sub>1</sub>² + λ<sub>2</sub><i>y</i><sub>2</sub>²</div>
      <p class="small muted">주축(고유벡터) 방향으로 좌표를 돌리면 교차항이 사라집니다. 그러면 고윳값의 부호만 보고 모양을 판정할 수 있습니다: 둘 다 양수면 <b>양의 정부호</b>(그릇 모양, 등고선은 타원), 부호가 다르면 <b>부정부호</b>(말안장, 쌍곡선), 하나가 0이면 <b>준정부호</b>.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>등고선 지도 <small>점을 끌어 값 확인</small></h3><div class="viz" id="qf-viz"></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>Q &gt; 0</span><span><i style="background:var(--e2)"></i>Q &lt; 0</span><span><i style="background:var(--ink)"></i>Q = 1 곡선</span><span><i style="background:var(--accent)"></i>주축</span></div></div>
      <div class="card"><h3>Q(x, y) = ax² + 2bxy + cy²</h3>${symSliders('qf', 2, 1, 1)}<div class="row" id="qf-pre"></div><div id="qf-cls"></div><div class="viz" id="qf-3d"></div><p class="small muted">곡면 z = Q(x, y) — 끌어서 회전</p></div>
    </div>
    <details class="expand" open><summary>xᵀAx 전부 전개 + 주축 변환</summary><div class="body" id="qf-exp"></div></details>`;
    let P = [1, 0.5];
    const plane = new Plane(root.querySelector('#qf-viz'), { range: 3, aspect: 0.9, snap: 0.25, labels: true });
    plane.handle({ get: () => P, set: (p) => (P = p), color: 'ink' });
    const surf = new View3D(root.querySelector('#qf-3d'), { range: 2.5, aspect: 0.6, pitch: 0.5 });
    const get = LA.bindSliders(root, ['qf-a', 'qf-b', 'qf-c'], () => upd());
    const cur = () => { const g = get(); return [g['qf-a'], g['qf-b'], g['qf-c']]; };
    const Qf = (a, b, c, x, y) => a * x * x + 2 * b * x * y + c * y * y;
    plane.draw = (p) => {
      const [a, b, c] = cur(), ctx = p.ctx, step = 6; let mx = 0;
      for (let sx = 0; sx < p.W; sx += step) for (let sy = 0; sy < p.H; sy += step) { const [x, y] = p.toW(sx + step / 2, sy + step / 2); mx = Math.max(mx, Math.abs(Qf(a, b, c, x, y))); }
      const c1 = LA.color('e1'), c2 = LA.color('e2');
      for (let sx = 0; sx < p.W; sx += step) for (let sy = 0; sy < p.H; sy += step) {
        const [x, y] = p.toW(sx + step / 2, sy + step / 2), q = Qf(a, b, c, x, y);
        ctx.fillStyle = LA.alpha(q >= 0 ? c1 : c2, Math.min(0.55, (Math.abs(q) / (mx || 1)) ** 0.6 * 0.55)); ctx.fillRect(sx, sy, step, step);
      }
      p.baseGrid();
      // 등고선: 레벨마다 극좌표로 r(θ) = sqrt(L / Q(cos, sin))
      [0.5, 1, 2, 4, -0.5, -1, -2, -4].forEach((L) => {
        ctx.save(); ctx.strokeStyle = LA.color(L === 1 ? 'ink' : 'muted'); ctx.lineWidth = L === 1 ? 2.5 : 1; ctx.beginPath(); let pen = false;
        for (let i = 0; i <= 720; i++) { const t = (i / 720) * 2 * Math.PI, q = Qf(a, b, c, Math.cos(t), Math.sin(t)); if (q * L <= 1e-9) { pen = false; continue; } const r = Math.sqrt(L / q); if (r > 10) { pen = false; continue; } const [sx, sy] = p.toS([r * Math.cos(t), r * Math.sin(t)]); if (pen) ctx.lineTo(sx, sy); else ctx.moveTo(sx, sy); pen = true; }
        ctx.stroke(); ctx.restore();
      });
      const e = sym2(a, b, c); p.infLine([0, 0], e.q1, 'accent', 1.5, true); p.infLine([0, 0], e.q2, 'accent', 1.5, true);
      p.text(N.vs(e.q1, 2.6), `y₁ (λ=${fmt(e.l1, 2)})`, 'accent', 0, 0); p.text(N.vs(e.q2, 2.6), `y₂ (λ=${fmt(e.l2, 2)})`, 'accent', 0, 0);
      p.text(P, `Q = ${fmt(Qf(a, b, c, P[0], P[1]), 2)}`, 'ink', 0, -16);
    };
    surf.draw = (p) => {
      const [a, b, c] = cur(), R = 2, n = 16, s = 0.35;
      const z = (x, y) => Math.max(-2.2, Math.min(2.2, Qf(a, b, c, x, y) * s));
      for (let i = 0; i <= n; i++) {
        const t = -R + (2 * R * i) / n; const l1 = [], l2 = [];
        for (let j = 0; j <= n; j++) { const u = -R + (2 * R * j) / n; l1.push([t, u, z(t, u)]); l2.push([u, t, z(u, t)]); }
        [l1, l2].forEach((L) => { for (let k = 1; k < L.length; k++) { const zz = (L[k][2] + L[k - 1][2]) / 2; p.seg(L[k - 1], L[k], zz >= 0 ? 'e1' : 'e2', { w: 1, alpha: 0.75 }); } });
      }
    };
    plane.onchange = exp;
    root.querySelector('#qf-pre').innerHTML = [['타원 (양의 정부호)', 2, 1, 1], ['쌍곡선 (부정부호)', 1, 2, -1], ['평행선 (준정부호)', 1, 1, 1], ['원', 1, 0, 1]].map(([n, a, b, c]) => `<button type="button" class="chip" data-v="${a},${b},${c}">${n}</button>`).join('');
    root.querySelector('#qf-pre').addEventListener('click', (e) => {
      const btn = e.target.closest('[data-v]'); if (!btn) return; const vals = btn.dataset.v.split(',').map(Number);
      ['qf-a', 'qf-b', 'qf-c'].forEach((id, k) => { root.querySelector('#' + id).value = vals[k]; root.querySelector('#' + id + '-o').textContent = fmt(vals[k]); }); upd();
    });
    function upd() { plane.render(); surf.render(); exp(); }
    function exp() {
      const [a, b, c] = cur(), e = sym2(a, b, c), [x, y] = P, y1 = N.dot(P, e.q1), y2 = N.dot(P, e.q2);
      const kind = e.l2 > 1e-9 ? ['양의 정부호', 'ok', '모든 x ≠ 0에서 Q > 0 · 최솟값을 갖는 그릇'] : e.l1 < -1e-9 ? ['음의 정부호', 'bad', '모든 x ≠ 0에서 Q < 0 · 뒤집힌 그릇'] : (e.l1 > 1e-9 && e.l2 < -1e-9) ? ['부정부호', 'info', 'Q가 양수도 음수도 됨 · 말안장'] : ['준정부호', 'info', '한 방향으로는 평평 · 골짜기'];
      root.querySelector('#qf-cls').innerHTML = `<div class="row"><span class="pill ${kind[1]}">${kind[0]}</span><span class="small">λ₁ = ${fmt(e.l1)}, λ₂ = ${fmt(e.l2)} — ${kind[2]}</span></div>`;
      const A = [[a, b], [b, c]];
      root.querySelector('#qf-exp').innerHTML = `<div class="mxrow"><span class="math">Q(<b>x</b>) =</span>${mat([['x', 'y']])}${mat(ff(A), { sub: 'a', cell: (i, j) => (i !== j ? 'h2' : 'h1') })}${LA.col(['x', 'y'])}</div>
        <div class="calc"><span class="ln">= Σᵢ Σⱼ aᵢⱼ xᵢ xⱼ = a₁₁·x·x + a₁₂·x·y + a₂₁·y·x + a₂₂·y·y</span>
        <span class="ln">= ${fmt(a)}x² + ${fmt(b)}xy + ${fmt(b)}yx + ${fmt(c)}y² = ${fmt(a)}x² + <b>${fmt(2 * b)}</b>xy + ${fmt(c)}y²   ← 교차항 계수 = 2b</span>
        <span class="ln">끈 점 (${fmt(x)}, ${fmt(y)}):  ${fmt(a)}·${par(x)}² + ${fmt(2 * b)}·${par(x)}·${par(y)} + ${fmt(c)}·${par(y)}² = <b>${fmt(Qf(a, b, c, x, y))}</b></span></div>
        <p class="small">주축 좌표: y₁ = <b>x</b>·q₁, y₂ = <b>x</b>·q₂ (q₁ = ${vec2(e.q1)}, q₂ = ${vec2(e.q2)})</p>
        <div class="calc"><span class="ln">y₁ = ${fmt(y1)},  y₂ = ${fmt(y2)}</span><span class="ln">λ₁y₁² + λ₂y₂² = ${fmt(e.l1)}·${par(y1)}² + ${par(e.l2)}·${par(y2)}² = <b>${fmt(e.l1 * y1 * y1 + e.l2 * y2 * y2)}</b>  ← 같은 값, 교차항 없음</span></div>`;
    }
    upd();
  },
});
})();
