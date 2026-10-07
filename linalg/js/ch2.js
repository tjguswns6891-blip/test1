/* 2장 행렬식 */
(function () {
'use strict';
const { F, f, X, N, mat, fh, par, term, v, editor, stepper, Plane, View3D, MINUS } = LA;
LA.chapter(2, '행렬식', 'Determinants');

/* 첫 행 전개를 끝까지 펼친 계산 줄들 */
function detLines(A, label = 'det') {
  const n = A.length;
  if (n === 1) return [`${label} = ${A[0][0].html()}`];
  if (n === 2) {
    const [[a, b], [c, d]] = A;
    return [`${label} = ${par(a)}·${par(d)} − ${par(b)}·${par(c)} = ${a.mul(d).html()} − ${par(b.mul(c))} = <b>${X.det(A).html()}</b>`];
  }
  const parts = [], vals = [];
  A[0].forEach((a, j) => {
    const Mj = X.minor(A, 0, j), d = X.det(Mj);
    parts.push(`${j ? (j % 2 ? ' − ' : ' + ') : ''}${par(a)}·|M<sub>1${j + 1}</sub>|`);
    vals.push(`${j ? (j % 2 ? ' − ' : ' + ') : ''}${par(a)}·${par(d)}`);
  });
  const out = [`${label} = ${parts.join('')}`, `${' '.repeat(label.length)} = ${vals.join('')} = <b>${X.det(A).html()}</b>`];
  A[0].forEach((_, j) => {
    const Mj = X.minor(A, 0, j);
    detLines(Mj, `|M<sub>1${j + 1}</sub>|`).forEach((l) => out.push('    ' + l));
  });
  return out;
}
LA.detLines = detLines;

function perms(n) {
  if (n === 1) return [[0]];
  const out = []; perms(n - 1).forEach((p) => { for (let k = 0; k <= p.length; k++) out.push([...p.slice(0, k), n - 1, ...p.slice(k)]); });
  return out;
}
function permSign(p) { let s = 1; for (let i = 0; i < p.length; i++) for (let j = i + 1; j < p.length; j++) if (p[i] > p[j]) s = -s; return s; }

/* ======================================================= 2.1 정의: 소행렬식과 여인수 전개 */
LA.section({
  id: 'det-def', ch: 2, title: '행렬식의 정의: 소행렬식과 여인수 전개', en: 'Minors and Cofactor Expansion',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">행렬식은 정사각행렬 하나를 수 하나로 바꾸는 규칙입니다. 그 수의 절댓값은 열벡터들이 만드는 <b>평행사변형의 넓이(3차원이면 평행육면체의 부피)</b>이고, 부호는 방향이 뒤집혔는지를 알려 줍니다.</p>
      <div class="keyline"><span class="lbl">i행을 따라 여인수 전개</span>det <i>A</i> = <span class="sum">Σ</span><sub><i>j</i>=1</sub><sup><i>n</i></sup> <i>a</i><sub><i>ij</i></sub> <i>C</i><sub><i>ij</i></sub> ,   <i>C</i><sub><i>ij</i></sub> = (−1)<sup><i>i</i>+<i>j</i></sup> <i>M</i><sub><i>ij</i></sub></div>
      <ul>
        <li><b>소행렬식</b> <i class="var">M<sub>ij</sub></i>: <i class="var">i</i>행과 <i class="var">j</i>열을 지우고 남은 행렬의 행렬식.</li>
        <li><b>여인수</b> <i class="var">C<sub>ij</sub></i>: 소행렬식에 부호 (−1)<sup><i>i</i>+<i>j</i></sup>를 붙인 것. 부호는 체스판처럼 +, −가 번갈아 나옵니다.</li>
        <li>어느 행, 어느 열을 골라 전개해도 답은 같습니다. 0이 많은 줄을 고르면 계산이 줄어듭니다.</li>
      </ul>
    </div>
    <div class="lab">
      <div class="card"><h3><i class="var">A</i> 입력</h3><div id="dd-ed"></div>
        <div><div class="small muted" style="margin-bottom:6px">전개할 줄 고르기</div><div class="row" id="dd-pick"></div></div>
        <div class="row"><span class="small muted">부호판 (−1)<sup>i+j</sup></span><span id="dd-sign"></span></div></div>
      <div class="card"><h3>기하학적 의미 <small>2×2: 두 열벡터의 평행사변형</small></h3><div class="viz" id="dd-viz"></div><div id="dd-geo" class="small"></div></div>
    </div>
    <div class="card"><h3 id="dd-h"></h3><div class="terms" id="dd-terms"></div><div class="calc" id="dd-sum"></div></div>
    <details class="expand"><summary>끝까지 전개 (모든 소행렬식을 2×2까지)</summary><div class="body"><div class="calc" id="dd-full"></div></div></details>
    <details class="expand"><summary>순열로 전부 펼치기: det <i class="var">A</i> = Σ sgn(σ) <i class="var">a</i><sub>1σ(1)</sub><i class="var">a</i><sub>2σ(2)</sub>⋯</summary><div class="body"><p class="small">각 행에서 하나씩, 서로 다른 열에서 고른 성분들의 곱을 모두 더합니다. 열 번호의 순서(순열)를 바꾸는 데 필요한 맞바꿈 횟수가 짝수면 +, 홀수면 −입니다.</p><div class="scroll" id="dd-perm"></div></div></details>`;
    let A, along = { t: 'r', k: 0 };
    const plane = new Plane(root.querySelector('#dd-viz'), { range: 5, aspect: 0.75 });
    let U = [3, 1], V = [1, 2];
    plane.handle({ get: () => U, set: (p) => (U = p), color: 'e1' }).handle({ get: () => V, set: (p) => (V = p), color: 'e2' });
    plane.draw = (p) => {
      const d = U[0] * V[1] - U[1] * V[0];
      p.poly([[0, 0], U, N.vadd(U, V), V], d >= 0 ? 'accent' : 'warn', d >= 0 ? 'accent' : 'warn', { a: 0.2 });
      p.arrow([0, 0], U, 'e1', { label: 'a₁' }); p.arrow([0, 0], V, 'e2', { label: 'a₂' });
      p.text(N.vs(N.vadd(U, V), 0.5), `det = ${LA.fmt(d)}`, d >= 0 ? 'accent' : 'warn', 0, 0);
    };
    plane.onchange = () => geo();
    function geo() {
      const d = U[0] * V[1] - U[1] * V[0];
      root.querySelector('#dd-geo').innerHTML = `<div class="calc">det [a₁ a₂] = ${LA.fmt(U[0])}·${LA.fmt(V[1])} − ${LA.fmt(V[0])}·${LA.fmt(U[1])} = <b>${LA.fmt(d)}</b></div>
        ${d > 0 ? 'a₁에서 a₂로 <b>반시계</b> 방향 → 양수.' : d < 0 ? 'a₁에서 a₂로 <b>시계</b> 방향 → 음수 (방향이 뒤집힘).' : '두 벡터가 한 직선 위 → 넓이 0, 역행렬 없음.'} 점을 끌어 보세요.`;
    }
    geo();
    function draw() {
      const n = A.length; if (along.k >= n) along.k = 0;
      root.querySelector('#dd-pick').innerHTML = [...Array(n).keys()].map((k) => `<button type="button" class="chip${along.t === 'r' && along.k === k ? ' on' : ''}" data-t="r" data-k="${k}">${k + 1}행</button>`).join('') +
        [...Array(n).keys()].map((k) => `<button type="button" class="chip${along.t === 'c' && along.k === k ? ' on' : ''}" data-t="c" data-k="${k}">${k + 1}열</button>`).join('');
      root.querySelector('#dd-sign').innerHTML = mat(A.map((r, i) => r.map((_, j) => ((i + j) % 2 ? '−' : '+'))), { cls: 'sm', cell: (i, j) => ((along.t === 'r' ? i : j) === along.k ? 'h1' : '') });
      const idx = [...Array(n).keys()]; const det = X.det(A);
      root.querySelector('#dd-h').innerHTML = `${along.k + 1}${along.t === 'r' ? '행' : '열'}을 따라 전개 <small>항 ${n}개 — 카드에 마우스를 올리면 지운 줄이 보입니다</small>`;
      const cards = idx.map((t) => {
        const [i, j] = along.t === 'r' ? [along.k, t] : [t, along.k];
        const Mij = X.minor(A, i, j), m = X.det(Mij), s = (i + j) % 2 ? -1 : 1, a = A[i][j];
        const contrib = a.mul(m).mul(s);
        return `<div class="term" data-i="${i}" data-j="${j}">
          <div class="tt">${v('a', `${i + 1}${j + 1}`)} · (−1)<sup>${i + 1}+${j + 1}</sup> · ${v('M', `${i + 1}${j + 1}`)}</div>
          <div class="mxrow">${mat(A, { cls: 'sm', cell: (r, c) => (r === i && c === j ? 'pv' : r === i || c === j ? 'x' : 'h2') })}<span class="op">→</span>${mat(Mij, { cls: 'sm', det: true })}</div>
          <div class="val">${v('M', `${i + 1}${j + 1}`)} = ${m.html()}<br>${par(a)} · (${s > 0 ? '+1' : '−1'}) · ${par(m)} = <b>${contrib.html()}</b>${a.isZero() ? ' <span class="tok">(0이라 계산 생략 가능)</span>' : ''}</div></div>`;
      });
      root.querySelector('#dd-terms').innerHTML = cards.join('');
      const contribs = idx.map((t) => { const [i, j] = along.t === 'r' ? [along.k, t] : [t, along.k]; return A[i][j].mul(X.det(X.minor(A, i, j))).mul((i + j) % 2 ? -1 : 1); });
      root.querySelector('#dd-sum').innerHTML = `<span class="ln">det A = ${contribs.map((c, k) => term(c, k === 0)).join('')} = <b>${det.html()}</b></span>`;
      root.querySelector('#dd-full').innerHTML = detLines(A, 'det A').map((l) => `<span class="ln">${l.replace(/ /g, '&nbsp;')}</span>`).join('');
      const P = perms(n);
      root.querySelector('#dd-perm').innerHTML = `<table class="t"><thead><tr><th>σ (각 행이 고른 열)</th><th>부호</th><th>곱</th><th>값</th></tr></thead><tbody>${P.map((p) => {
        const s = permSign(p); const prod = p.reduce((acc, c, r) => acc.mul(A[r][c]), f(s));
        return `<tr><td class="num">(${p.map((c) => c + 1).join(', ')})</td><td class="num ${s > 0 ? 'tok' : 'tw'}">${s > 0 ? '+' : '−'}</td><td>${p.map((c, r) => v('a', `${r + 1}${c + 1}`)).join('')} = ${p.map((c, r) => par(A[r][c])).join('·')}</td><td class="num">${prod.html()}</td></tr>`;
      }).join('')}<tr><td colspan="3"><b>합계 (${P.length}개 항)</b></td><td class="num"><b>${det.html()}</b></td></tr></tbody></table>`;
    }
    root.querySelector('#dd-pick').addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; along = { t: b.dataset.t, k: +b.dataset.k }; draw(); });
    root.querySelector('#dd-terms').addEventListener('mouseover', (e) => { root.querySelectorAll('#dd-terms .term').forEach((t) => t.classList.toggle('on', t.contains(e.target))); });
    editor(root.querySelector('#dd-ed'), X.fromN([[2, 0, 1], [1, 3, 2], [1, 1, 1]]), (M) => { A = M; draw(); }, {
      resize: { square: true, min: 2, max: 4 },
      presets: [{ name: '3×3', A: [[2, 0, 1], [1, 3, 2], [1, 1, 1]] }, { name: '0 많은 4×4', A: [[1, 0, 2, 0], [3, 0, 1, 4], [0, 2, 0, 0], [1, 0, 0, 1]] }, { name: '삼각행렬', A: [[2, 5, -1], [0, 3, 4], [0, 0, -1]] }],
    });
    A = X.fromN([[2, 0, 1], [1, 3, 2], [1, 1, 1]]); draw();
  },
});

/* ======================================================= 2.2 성질 */
LA.section({
  id: 'det-prop', ch: 2, title: '행렬식의 성질: 행 연산에 따른 변화', en: 'Properties of Determinants',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">기본 행 연산을 하면 행렬식이 정해진 방식으로 바뀝니다. 그래서 소거법으로 삼각행렬을 만든 뒤 대각선만 곱하면 큰 행렬의 행렬식도 빨리 구할 수 있습니다.</p>
      <table class="t"><thead><tr><th>연산</th><th>행렬식</th><th>그림으로 보면</th></tr></thead><tbody>
        <tr><td><i class="var">R<sub>i</sub></i> ↔ <i class="var">R<sub>j</sub></i></td><td><b>−1배</b></td><td>방향이 뒤집힘 (거울상)</td></tr>
        <tr><td><i class="var">R<sub>i</sub></i> ← <i class="var">k</i><i class="var">R<sub>i</sub></i></td><td><b><i>k</i>배</b></td><td>한 변만 <i>k</i>배로 늘어남</td></tr>
        <tr><td><i class="var">R<sub>i</sub></i> ← <i class="var">R<sub>i</sub></i> + <i class="var">k</i><i class="var">R<sub>j</sub></i></td><td><b>변하지 않음</b></td><td>밑변을 따라 미는 층밀림(shear). 밑변과 높이가 그대로라 넓이도 그대로</td></tr>
      </tbody></table>
      <p class="small muted">그 밖에: det(<i>A</i><sup>T</sup>) = det <i>A</i>, det(<i>AB</i>) = det <i>A</i> · det <i>B</i>, det(<i>kA</i>) = <i>k</i><sup><i>n</i></sup> det <i>A</i>, 삼각행렬의 행렬식 = 대각성분의 곱. 아래 그림은 <b>행벡터</b>가 만드는 도형입니다 (det <i>A</i> = det <i>A</i><sup>T</sup>이므로 넓이는 같습니다).</p>
    </div>
    <div class="lab">
      <div class="card"><h3>행 연산 적용하기</h3>
        <div class="row"><span class="small muted">크기</span><button type="button" class="chip on" data-n="2">2×2</button><button type="button" class="chip" data-n="3">3×3</button><button type="button" class="chip ghost" id="dp-reset">처음으로</button></div>
        <div class="scroll"><div class="mxrow" id="dp-m"></div></div>
        <div class="row"><label class="small" for="dp-i">대상 행 i</label><select id="dp-i"></select><label class="small" for="dp-j">다른 행 j</label><select id="dp-j"></select><label class="small" for="dp-k">k</label><select id="dp-k">${[-3, -2, -1, -0.5, 0.5, 2, 3].map((k) => `<option${k === 2 ? ' selected' : ''}>${LA.fmt(k)}</option>`).join('')}</select></div>
        <div class="row"><button type="button" class="btn" data-op="swap">Rᵢ ↔ Rⱼ</button><button type="button" class="btn" data-op="scale">Rᵢ ← k·Rᵢ</button><button type="button" class="btn primary" data-op="add">Rᵢ ← Rᵢ + k·Rⱼ</button></div>
        <ol class="steplist" id="dp-log" style="max-height:260px"></ol></div>
      <div class="card"><h3>넓이 / 부피 <small id="dp-val"></small></h3><div class="viz" id="dp-viz"></div><div class="legend"><span><i style="background:var(--e1)"></i>R₁</span><span><i style="background:var(--e2)"></i>R₂</span><span><i style="background:var(--e3)"></i>R₃</span></div></div>
    </div>
    <details class="expand" open><summary>소거로 행렬식 구하기 (대각선 곱 × 부호)</summary><div class="body" id="dp-elim"></div></details>`;
    let n = 2, A, A0, log = [], shown = null, view;
    const viz = root.querySelector('#dp-viz');
    function init(k) {
      n = k; A = k === 2 ? X.fromN([[3, 1], [1, 2]]) : X.fromN([[2, 1, 0], [0, 2, 1], [1, 0, 2]]); A0 = X.clone(A); log = []; shown = X.toN(A);
      LA.live.planes.forEach((p) => { if (p.host === viz) { p.destroy(); LA.live.planes.delete(p); } });
      viz.innerHTML = '';
      view = n === 2 ? new Plane(viz, { range: 6, aspect: 0.8 }) : new View3D(viz, { range: 3 });
      view.draw = paint; fill(); draw();
    }
    function paint(p) {
      const R = shown;
      if (n === 2) {
        const d = R[0][0] * R[1][1] - R[0][1] * R[1][0];
        p.poly([[0, 0], R[0], N.vadd(R[0], R[1]), R[1]], d >= 0 ? 'accent' : 'warn', d >= 0 ? 'accent' : 'warn', { a: 0.2 });
        p.arrow([0, 0], R[0], 'e1', { label: 'R₁' }); p.arrow([0, 0], R[1], 'e2', { label: 'R₂' });
      } else {
        const [a, b, c] = R, O = [0, 0, 0];
        const V = [O, a, b, c, N.vadd(a, b), N.vadd(a, c), N.vadd(b, c), N.vadd(N.vadd(a, b), c)];
        const d = N.det(R); const cc = d >= 0 ? 'accent' : 'warn';
        [[0, 1, 4, 2], [0, 1, 5, 3], [0, 2, 6, 3], [7, 4, 1, 5], [7, 4, 2, 6], [7, 5, 3, 6]].forEach((fc) => p.poly(fc.map((i) => V[i]), cc, cc, { a: 0.08, w: 0.8 }));
        p.arrow(O, a, 'e1', { label: 'R₁' }); p.arrow(O, b, 'e2', { label: 'R₂' }); p.arrow(O, c, 'e3', { label: 'R₃' });
      }
    }
    function fill() {
      const opts = [...Array(n).keys()].map((i) => `<option value="${i}">${i + 1}</option>`).join('');
      root.querySelector('#dp-i').innerHTML = opts; root.querySelector('#dp-j').innerHTML = opts; root.querySelector('#dp-j').value = '1';
    }
    function draw() {
      const d = X.det(A);
      root.querySelector('#dp-m').innerHTML = mat(A, { name: 'A', sub: 'a', cell: (i) => ['k1', 'k2', 'k3'][i] }) + `<span class="op">det = <b class="ta">${d.html()}</b></span>`;
      root.querySelector('#dp-val').innerHTML = `det = ${d.html()}`;
      root.querySelector('#dp-log').innerHTML = `<li class="cur"><span class="n">0</span><span>처음 det = ${X.det(A0).html()}</span></li>` + log.map((l, k) => `<li><span class="n">${k + 1}</span><span>${l}</span></li>`).join('');
      view.render(); elim();
    }
    function elim() {
      const res = X.rref(A, n, { normalizeFirst: false, full: false });
      const U = res.R; const swaps = res.steps.filter((s) => s.op && s.op.type === 'swap').length;
      const diag = U.map((r, i) => r[i]); const prod = diag.reduce((a, b) => a.mul(b), f(1)).mul(swaps % 2 ? -1 : 1);
      root.querySelector('#dp-elim').innerHTML = `<p class="small">더하기 연산(행렬식 불변)과 교환(부호만 바뀜)만 써서 위삼각행렬 <i>U</i>를 만듭니다.</p>
        <div class="calc">${res.steps.slice(1).map((s) => `<span class="ln">${s.desc} ${s.op.type === 'swap' ? '<span class="tw">→ 부호 × (−1)</span>' : '→ det 그대로'}</span>`).join('') || '<span class="ln">이미 위삼각행렬입니다.</span>'}</div>
        <div class="mxrow">${mat(U, { name: 'U', cell: (i, j) => (i === j ? 'h1' : i > j ? 'dim' : '') })}</div>
        <div class="calc"><span class="ln">det A = (−1)<sup>${swaps}</sup> × ${diag.map((x) => par(x)).join(' × ')} = <b>${prod.html()}</b></span></div>`;
    }
    root.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.n) { root.querySelectorAll('[data-n]').forEach((x) => x.classList.toggle('on', x === b)); init(+b.dataset.n); return; }
      if (b.id === 'dp-reset') { init(n); return; }
      const op = b.dataset.op; if (!op) return;
      const i = +root.querySelector('#dp-i').value, j = +root.querySelector('#dp-j').value, k = F.parse(root.querySelector('#dp-k').value);
      const before = X.det(A), from = X.toN(A); let rule;
      if (op === 'swap') { if (i === j) return; [A[i], A[j]] = [A[j], A[i]]; rule = `R${i + 1} ↔ R${j + 1}: det × (−1)`; }
      else if (op === 'scale') { A[i] = A[i].map((x) => x.mul(k)); rule = `R${i + 1} ← ${k.toString()}·R${i + 1}: det × ${k.toString()}`; }
      else { if (i === j) return; A[i] = A[i].map((x, c) => x.add(k.mul(A[j][c]))); rule = `R${i + 1} ← R${i + 1} + ${k.toString()}·R${j + 1}: det 불변`; }
      log.push(`${rule} &nbsp; <span class="muted">${before.toString()} → ${X.det(A).toString()}</span>`);
      const to = X.toN(A);
      LA.tween(700, (u) => { shown = from.map((r, a) => r.map((x, c) => x + (to[a][c] - x) * u)); view.render(); });
      draw();
    });
    init(2);
  },
});

/* ======================================================= 2.3 크래머 공식 */
LA.section({
  id: 'cramer', ch: 2, title: '크래머 공식', en: "Cramer's Rule",
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead"><i class="var">A</i><b class="vec">x</b> = <b class="vec">b</b>에서 det <i class="var">A</i> ≠ 0이면, 각 미지수를 행렬식 두 개의 비로 바로 쓸 수 있습니다.</p>
      <div class="keyline"><span class="lbl">i번째 열을 b로 바꾼 행렬 Aᵢ</span><i>x</i><sub><i>i</i></sub> = <span class="fr"><span>det <i>A</i><sub><i>i</i></sub></span><span>det <i>A</i></span></span></div>
      <p class="small muted">왜 성립할까: <b class="vec">b</b> = <i>x</i><sub>1</sub><b class="vec">a</b><sub>1</sub> + <i>x</i><sub>2</sub><b class="vec">a</b><sub>2</sub>이므로 det[<b class="vec">b</b> <b class="vec">a</b><sub>2</sub>] = det[<i>x</i><sub>1</sub><b class="vec">a</b><sub>1</sub> + <i>x</i><sub>2</sub><b class="vec">a</b><sub>2</sub>  <b class="vec">a</b><sub>2</sub>] = <i>x</i><sub>1</sub> det[<b class="vec">a</b><sub>1</sub> <b class="vec">a</b><sub>2</sub>]. (<b class="vec">a</b><sub>2</sub>의 배수를 더한 부분은 층밀림이라 넓이가 그대로입니다.) 오른쪽 그림에서 두 평행사변형의 넓이 비가 곧 <i>x</i><sub>1</sub>입니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>[A | b] 입력</h3><div id="cr-ed"></div></div>
      <div class="card"><h3>2×2: 넓이의 비 <small id="cr-which"></small></h3><div id="cr-tabs"></div><div class="viz" id="cr-viz"></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>a₁</span><span><i style="background:var(--e2)"></i>a₂</span><span><i style="background:var(--accent)"></i>b</span></div></div>
    </div>
    <div class="card"><h3>모든 항 전개</h3><div id="cr-out" class="page" style="gap:16px"></div></div>`;
    let M, which = 0;
    const viz = root.querySelector('#cr-viz'); const plane = new Plane(viz, { range: 7, aspect: 0.8 });
    LA.tabs(root.querySelector('#cr-tabs'), ['x₁ = det A₁ / det A', 'x₂ = det A₂ / det A'], (t) => { which = t; plane.render(); });
    plane.draw = (p) => {
      if (!M || M.length !== 2) return;
      const a1 = [M[0][0].val(), M[1][0].val()], a2 = [M[0][1].val(), M[1][1].val()], b = [M[0][2].val(), M[1][2].val()];
      const keep = which === 0 ? a2 : a1, rep = which === 0 ? a1 : a2;
      p.poly([[0, 0], rep, N.vadd(rep, keep), keep], 'muted', 'muted', { a: 0.12, dash: true });
      p.poly([[0, 0], b, N.vadd(b, keep), keep], 'accent', 'accent', { a: 0.18 });
      p.arrow([0, 0], a1, 'e1', { label: 'a₁' }); p.arrow([0, 0], a2, 'e2', { label: 'a₂' }); p.arrow([0, 0], b, 'accent', { label: 'b' });
    };
    function out() {
      const n = M.length, A = M.map((r) => r.slice(0, n)), b = M.map((r) => r[n]); const dA = X.det(A);
      const blocks = [`<div class="mxrow">${mat(A, { name: 'A', cell: (i, j) => ['k1', 'k2', 'k3', 'k1'][j] })}${LA.col(b, { name: '<b>b</b>' })}</div><div class="calc">${detLines(A, 'det A').map((l) => `<span class="ln">${l.replace(/ /g, '&nbsp;')}</span>`).join('')}</div>`];
      if (dA.isZero()) blocks.push(`<div class="row"><span class="pill bad">det A = 0</span><span class="small">분모가 0이라 크래머 공식을 쓸 수 없습니다. 해가 없거나 무수히 많습니다.</span></div>`);
      else for (let i = 0; i < n; i++) {
        const Ai = A.map((r, rr) => r.map((x, c) => (c === i ? b[rr] : x))); const d = X.det(Ai);
        blocks.push(`<div class="sep"></div><div class="mxrow">${mat(Ai, { name: `A<sub>${i + 1}</sub>`, cell: (r, c) => (c === i ? 'pv' : '') })}<span class="small muted">${i + 1}열을 <b>b</b>로 교체</span></div>
          <div class="calc">${detLines(Ai, `det A${i + 1}`).map((l) => `<span class="ln">${l.replace(/ /g, '&nbsp;')}</span>`).join('')}</div>
          <div class="math">${v('x', i + 1)} = <span class="fr"><span>det <i>A</i><sub>${i + 1}</sub></span><span>det <i>A</i></span></span> = <span class="fr"><span>${d.toString()}</span><span>${dA.toString()}</span></span> = <b class="ta">${d.div(dA).html()}</b></div>`);
      }
      root.querySelector('#cr-out').innerHTML = blocks.join('');
      viz.parentElement.hidden = n !== 2; plane.render();
    }
    editor(root.querySelector('#cr-ed'), X.fromN([[2, 1, 5], [1, 3, 5]]), (m) => {
      const n = m.length;
      if (m[0].length !== n + 1) return; // 정사각 계수 + 우변 1열일 때만
      M = m; out();
    }, { aug: true, resize: { rows: false, cols: false }, presets: [{ name: '2×2', A: [[2, 1, 5], [1, 3, 5]] }, { name: '3×3', A: [[1, 2, -1, 2], [2, -1, 1, 3], [1, 1, 1, 6]] }, { name: 'det 0', A: [[1, 2, 3], [2, 4, 5]] }] });
    M = X.fromN([[2, 1, 5], [1, 3, 5]]); out();
  },
});
})();
