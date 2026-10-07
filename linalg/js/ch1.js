/* 1장 선형연립방정식과 행렬 */
(function () {
'use strict';
const { F, f, X, N, mat, fh, par, term, v, editor, stepper, Plane, MINUS } = LA;
LA.chapter(1, '선형연립방정식과 행렬', 'Systems of Linear Equations and Matrices');

/* 첨가행렬 → 방정식 문자열 */
function eqHTML(M, names = ['x', 'y', 'z', 'w', 'u']) {
  const n = M[0].length - 1;
  return M.map((r) => {
    let s = '', first = true;
    for (let j = 0; j < n; j++) {
      if (r[j].isZero()) continue;
      const a = r[j].abs(); const coef = a.isOne() ? '' : a.html();
      s += (first ? (r[j].sign() < 0 ? MINUS : '') : (r[j].sign() < 0 ? ` ${MINUS} ` : ' + ')) + coef + v(names[j]);
      first = false;
    }
    if (first) s = '0';
    return `<span class="ln">${s} = ${r[n].html()}</span>`;
  }).join('');
}
LA.eqHTML = eqHTML;

/* 해 판정 */
function verdict(Rm, pivots, nc) {
  const incons = Rm.some((r) => r.slice(0, nc).every((x) => x.isZero()) && !r[nc].isZero());
  if (incons) return { kind: 'none', html: `<span class="pill bad">해 없음</span> <span class="small">0 = (0이 아닌 수) 꼴의 행이 생겼습니다. 모순입니다.</span>` };
  if (pivots.length === nc) return { kind: 'one', html: `<span class="pill ok">해가 하나</span> <span class="small">모든 변수 열에 피벗이 있습니다.</span>` };
  return { kind: 'many', html: `<span class="pill info">해가 무수히 많음</span> <span class="small">피벗이 없는 열(자유변수)이 ${nc - pivots.length}개 있습니다.</span>` };
}

/* ======================================================= 1.1 가우스 소거법 */
LA.section({
  id: 'gauss', ch: 1, title: '가우스 소거법과 기본 행 연산', en: 'Gaussian Elimination',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">연립방정식은 계수만 모아 <b>첨가행렬</b> [<i class="var">A</i> | <b class="vec">b</b>]로 씁니다. 그다음 해를 바꾸지 않는 세 가지 <b>기본 행 연산</b>만으로 행렬을 계단 모양으로 정리합니다.</p>
      <ul>
        <li><b>교환</b> <i class="var">R<sub>i</sub></i> ↔ <i class="var">R<sub>j</sub></i>: 두 방정식의 순서를 바꿉니다.</li>
        <li><b>스칼라배</b> <i class="var">R<sub>i</sub></i> ← <i class="var">k</i><i class="var">R<sub>i</sub></i> (<i class="var">k</i> ≠ 0): 방정식 양변에 같은 수를 곱합니다.</li>
        <li><b>더하기</b> <i class="var">R<sub>i</sub></i> ← <i class="var">R<sub>i</sub></i> + <i class="var">k</i><i class="var">R<sub>j</sub></i>: 다른 방정식의 배수를 더합니다. 소거의 핵심입니다.</li>
      </ul>
      <p class="small muted">아래 각 단계는 바뀐 행의 모든 성분 계산을 <i class="var">a<sub>ij</sub></i> 하나하나 펼쳐서 보여 줍니다. 2변수 연립방정식이면 오른쪽 그림에서 두 직선이 단계마다 기울어지지만 교점(해)은 그대로라는 점을 확인할 수 있습니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>첨가행렬 입력 <small>마지막 열 = 우변</small></h3><div id="g-ed"></div><div id="g-eq" class="calc"></div></div>
      <div class="card"><h3>그림 <small id="g-vtitle"></small></h3><div class="viz" id="g-viz"></div><div class="viz" id="g-viz3"></div><div class="legend" id="g-leg"></div></div>
    </div>
    <div class="card">
      <div id="g-step"></div>
      <div class="row top" style="gap:24px">
        <div class="scroll" id="g-mat"></div>
        <div class="stepbox" id="g-desc" style="flex:1 1 300px"></div>
      </div>
      <div id="g-verdict"></div>
      <details class="expand"><summary>전체 단계 목록</summary><div class="body"><ol class="steplist" id="g-list"></ol></div></details>
    </div>`;
    let res, sp;
    const viz = root.querySelector('#g-viz');
    const plane = new Plane(viz, { range: 6, aspect: 0.8 });
    let cur = null;
    plane.draw = (p) => {
      if (!cur || cur[0].length !== 3) return;
      const cols = ['e1', 'e2', 'e3', 'accent', 'warn'];
      cur.forEach((r, i) => {
        const [a, b, c] = r.map((x) => x.val());
        if (Math.abs(a) < 1e-12 && Math.abs(b) < 1e-12) return;
        const pt = Math.abs(b) > Math.abs(a) ? [0, c / b] : [c / a, 0];
        p.infLine(pt, [b, -a], cols[i % 5], 2.5);
        p.text([pt[0] + b * 0.0, pt[1]], `R${i + 1}`, cols[i % 5], 14, -10);
      });
      if (res && res.pivots.length === 2) {
        const R = res.R; const s = [R[0][2].val(), R[1][2].val()];
        if (!R.some((r) => r[0].isZero() && r[1].isZero() && !r[2].isZero())) { p.dot(s, 'ink', 5); p.text(s, `(${LA.fmt(s[0])}, ${LA.fmt(s[1])})`, 'ink', 0, 18); }
      }
    };
    const viz3 = root.querySelector('#g-viz3');
    const v3 = new LA.View3D(viz3, { range: 4, aspect: 0.85 });
    v3.draw = (p) => {
      if (!cur || cur[0].length !== 4) return;
      const cols = ['e1', 'e2', 'e3', 'accent', 'warn'];
      let center = [0, 0, 0], uniq = false;
      if (res && res.pivots.length === 3) { const R = res.R; if (!R.some((r) => r.slice(0, 3).every((x) => x.isZero()) && !r[3].isZero())) { center = [0, 1, 2].map((i) => R[i][3].val()); uniq = true; } }
      cur.forEach((r, i) => { const [a, b, c, d] = r.map((x) => x.val()); LA.plane3(p, [a, b, c], d, cols[i % 5], { center, size: 2.4, label: `R${i + 1}` }); });
      if (uniq) { p.dot(center, 'ink', 6); p.text(center, `(${center.map((t) => LA.fmt(t)).join(', ')})`, 'ink', 0, -16); }
    };
    function show(k) {
      const st = res.steps[k], prev = res.steps[k - 1];
      const changed = st.op ? (st.op.type === 'swap' ? [st.op.i, st.op.j] : [st.op.i]) : [];
      root.querySelector('#g-mat').innerHTML = `<div class="mxrow">${prev ? mat(prev.M, { aug: prev.M[0].length - 1, cls: '', cell: (i) => (changed.includes(i) ? 'dim' : '') }) + '<span class="op">→</span>' : ''}${mat(st.M, { aug: st.M[0].length - 1, sub: 'a', cell: (i, j) => (st.piv && st.piv[0] === i && st.piv[1] === j ? 'pv' : changed.includes(i) ? 'changed h1' : '') })}</div>`;
      root.querySelector('#g-desc').innerHTML = st.op
        ? `<span class="ph">${st.phase}</span><div class="op-t">${st.desc}</div><div class="small">${st.detail}</div><div class="calc">${eqHTML(st.M)}</div>`
        : `<span class="ph">시작</span><div class="small">주어진 첨가행렬입니다. <b>다음</b>을 눌러 한 단계씩 진행하세요. 파란 칸은 그 단계의 피벗입니다.</div><div class="calc">${eqHTML(st.M)}</div>`;
      root.querySelectorAll('#g-list li').forEach((li, i) => li.classList.toggle('cur', i === k));
      cur = st.M; plane.render(); v3.render();
      root.querySelector('#g-verdict').innerHTML = k === res.steps.length - 1 ? verdictBox() : '';
    }
    function verdictBox() {
      const nc = res.R[0].length - 1; const vd = verdict(res.R, res.pivots, nc);
      let h = `<div class="row">${vd.html}</div>`;
      if (vd.kind === 'one') h += `<div class="calc">${res.R.slice(0, nc).map((r, i) => `<span class="ln">${v(['x', 'y', 'z', 'w', 'u'][i])} = <b>${r[nc].html()}</b></span>`).join('')}</div>`;
      if (vd.kind === 'many') {
        const names = ['x', 'y', 'z', 'w', 'u']; const pc = res.pivots.map((p) => p[1]);
        const free = [...Array(nc).keys()].filter((j) => !pc.includes(j)); const params = ['s', 't', 'r', 'q'];
        const lines = res.pivots.map(([r, c]) => {
          let s = res.R[r][nc].html();
          free.forEach((fj, t) => { const k = res.R[r][fj].neg(); if (!k.isZero()) s += `${k.sign() < 0 ? ` ${MINUS} ` : ' + '}${k.abs().isOne() ? '' : k.abs().html()}${v(params[t])}`; });
          return `<span class="ln">${v(names[c])} = ${s}</span>`;
        }).concat(free.map((fj, t) => `<span class="ln">${v(names[fj])} = ${v(params[t])} <span class="muted">(자유변수)</span></span>`));
        h += `<div class="calc">${lines.join('')}</div>`;
      }
      return h;
    }
    function run(A) {
      res = X.rref(A, A[0].length - 1);
      root.querySelector('#g-list').innerHTML = res.steps.map((s, i) => `<li data-k="${i}"><span class="n">${i}</span><span>${s.op ? s.desc : '시작 행렬'}</span></li>`).join('');
      root.querySelector('#g-eq').innerHTML = eqHTML(A);
      const two = A[0].length === 3, three = A[0].length === 4;
      root.querySelector('#g-vtitle').textContent = two ? '각 행 = 직선 하나' : three ? '각 행 = 평면 하나 · 끌어서 회전' : '';
      root.querySelector('#g-leg').innerHTML = two ? '행 연산을 해도 직선들의 공통점(해)은 움직이지 않습니다.' : three ? '각 방정식 ax + by + cz = d는 3차원 공간의 평면입니다. 행 연산을 하면 평면이 기울어지지만 세 평면이 만나는 점(해)은 그대로입니다. 마지막 단계에서는 세 평면이 각각 x = …, y = …, z = … 꼴로 축에 수직하게 섭니다.' : '변수가 2개(열 3개)면 직선, 3개(열 4개)면 평면 그림이 나타납니다. 지금은 행렬 단계만 보여 줍니다.';
      viz.hidden = !two; viz3.hidden = !three;
      if (sp) sp.reset(res.steps.length); else sp = stepper(root.querySelector('#g-step'), res.steps.length, show);
    }
    root.querySelector('#g-list').addEventListener('click', (e) => { const li = e.target.closest('li'); if (li) sp.go(+li.dataset.k); });
    editor(root.querySelector('#g-ed'), X.fromN([[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]]), run, {
      aug: true, resize: { rows: true, cols: true, minR: 2, maxR: 4, minC: 3, maxC: 5 },
      presets: [
        { name: '3변수 (해 1개)', A: [[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]] },
        { name: '2변수 직선', A: [[1, 2, 4], [3, -1, 5]] },
        { name: '해 없음', A: [[1, 1, 2], [2, 2, 5]] },
        { name: '해 무수히', A: [[1, 2, -1, 3], [2, 4, 1, 3], [3, 6, 0, 6]] },
      ],
    });
    run(X.fromN([[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]]));
  },
});

/* ======================================================= 1.2 행렬 연산 */
LA.section({
  id: 'matops', ch: 1, title: '행렬의 덧셈 · 곱셈 · 전치', en: 'Matrix Operations',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead"><i class="var">A</i>의 (<i class="var">i</i>, <i class="var">j</i>) 성분 <i class="var">a<sub>ij</sub></i>는 <b><i class="var">i</i>행 <i class="var">j</i>열</b>에 있는 수입니다. 행렬 연산은 결국 “어느 인덱스끼리 짝지어 계산하는가”의 규칙입니다.</p>
      <div class="keyline"><span class="lbl">곱셈의 정의 — 같은 k끼리 곱해서 모두 더한다</span>(<i>AB</i>)<sub><i>ij</i></sub> = <span class="sum">Σ</span><sub><i>k</i>=1</sub><sup><i>n</i></sup> <i>a</i><sub><i>ik</i></sub> <i>b</i><sub><i>kj</i></sub> = <i>a</i><sub><i>i</i>1</sub><i>b</i><sub>1<i>j</i></sub> + <i>a</i><sub><i>i</i>2</sub><i>b</i><sub>2<i>j</i></sub> + ⋯ + <i>a</i><sub><i>in</i></sub><i>b</i><sub><i>nj</i></sub></div>
      <p class="small muted">시그마 안의 <i class="var">k</i>는 <i class="var">A</i>에서는 <b>열</b> 번호, <i class="var">B</i>에서는 <b>행</b> 번호입니다. 그래서 “<i class="var">A</i>의 <i class="var">i</i>행”과 “<i class="var">B</i>의 <i class="var">j</i>열”을 나란히 놓고 곱하게 됩니다. 아래에서 결과 칸에 마우스를 올리거나 눌러 보세요.</p>
    </div>
    <div id="mo-tabs"></div>
    <div id="mo-body" class="page" style="gap:20px"></div>`;
    const body = root.querySelector('#mo-body');
    LA.tabs(root.querySelector('#mo-tabs'), ['곱셈 AB', '덧셈 · 스칼라배', '전치 Aᵀ'], (t) => [mulTab, addTab, tTab][t](body));
  },
});

function mulTab(body) {
  body.innerHTML = `
    <div class="lab">
      <div class="card"><h3><span><i class="var">A</i> <small>(m×n)</small></span></h3><div id="mu-a"></div></div>
      <div class="card"><h3><span><i class="var">B</i> <small>(n×p)</small></span></h3><div id="mu-b"></div></div>
    </div>
    <div class="card">
      <h3>결과 <i class="var">C</i> = <i class="var">AB</i> <small id="mu-dim"></small></h3>
      <div class="scroll"><div class="mxrow" id="mu-show"></div></div>
      <div class="stepbox" id="mu-exp"></div>
    </div>
    <details class="expand" open><summary>모든 성분 전개 (<i class="var">c<sub>ij</sub></i> 전부)</summary><div class="body"><div class="calc" id="mu-all"></div></div></details>`;
  let A = X.fromN([[1, 2, 0], [-1, 3, 2]]), B = X.fromN([[2, 1], [0, -1], [4, 3]]), sel = [0, 0];
  const edA = editor(body.querySelector('#mu-a'), A, (M) => { A = M; sync('A'); }, { sym: 'a', resize: { minR: 1, maxR: 4, minC: 1, maxC: 4 } });
  const edB = editor(body.querySelector('#mu-b'), B, (M) => { B = M; sync('B'); }, { sym: 'b', resize: { minR: 1, maxR: 4, minC: 1, maxC: 4 } });
  let lock = false;
  function sync(who) {
    if (lock) return;
    const n = A[0].length;
    if (B.length !== n) {
      lock = true;
      if (who === 'A') { while (B.length < n) B.push(B[0].map(() => f(0))); while (B.length > n) B.pop(); edB.set(B); }
      else { A.forEach((r) => { while (r.length < B.length) r.push(f(0)); while (r.length > B.length) r.pop(); }); edA.set(A); }
      lock = false;
    }
    draw();
  }
  function draw() {
    const C = X.mul(A, B), m = A.length, n = A[0].length, p = B[0].length;
    if (sel[0] >= m || sel[1] >= p) sel = [0, 0];
    const [i, j] = sel;
    body.querySelector('#mu-dim').textContent = `(${m}×${n})·(${n}×${p}) = ${m}×${p} — 가운데 ${n}이 같아야 곱할 수 있음`;
    body.querySelector('#mu-show').innerHTML =
      mat(A, { name: 'A', noeq: true, sub: 'a', cell: (r, c) => (r === i ? 'h1' : 'dim') }) + '<span class="op">·</span>' +
      mat(B, { name: 'B', noeq: true, sub: 'b', cell: (r, c) => (c === j ? 'h2' : 'dim') }) + '<span class="op">=</span>' +
      `<span id="mu-c">${mat(C, { name: 'C', noeq: true, sub: 'c', cell: (r, c) => (r === i && c === j ? 'pv' : '') })}</span>`;
    const terms = A[i].map((a, k) => `<span class="t1">${v('a', `${i + 1}${k + 1}`)}</span><span class="t2">${v('b', `${k + 1}${j + 1}`)}</span>`).join(' + ');
    const nums = A[i].map((a, k) => `<span class="t1">${par(a)}</span>·<span class="t2">${par(B[k][j])}</span>`).join(' + ');
    const prods = A[i].map((a, k) => a.mul(B[k][j])).map((x, k) => term(x, k === 0)).join('');
    body.querySelector('#mu-exp').innerHTML = `<span class="ph">${v('c', `${i + 1}${j + 1}`)} 계산 — A의 ${i + 1}행 × B의 ${j + 1}열</span>
      <div class="math">${v('c', `${i + 1}${j + 1}`)} = <span class="sum">Σ</span><sub><i>k</i>=1</sub><sup>${n}</sup> ${v('a', `${i + 1}<i>k</i>`)}${v('b', `<i>k</i>${j + 1}`)} = ${terms}</div>
      <div class="math">= ${nums} = ${prods} = <b class="ta">${C[i][j].html()}</b></div>`;
    body.querySelector('#mu-all').innerHTML = C.map((r, ii) => r.map((c, jj) =>
      `<span class="ln">${v('c', `${ii + 1}${jj + 1}`)} = ${A[ii].map((a, k) => `${par(a)}·${par(B[k][jj])}`).join(' + ')} = <b>${c.html()}</b></span>`).join('')).join('');
  }
  const pick = (e) => { const c = e.target.closest('#mu-c .c'); if (c) { const ns = [+c.dataset.i, +c.dataset.j]; if (ns[0] !== sel[0] || ns[1] !== sel[1]) { sel = ns; draw(); } } };
  body.querySelector('#mu-show').addEventListener('mouseover', pick);
  body.querySelector('#mu-show').addEventListener('click', pick);
  draw();
}

function addTab(body) {
  body.innerHTML = `
    <div class="lab">
      <div class="card"><h3><i class="var">A</i></h3><div id="ad-a"></div></div>
      <div class="card"><h3><i class="var">B</i> <small>A와 같은 크기</small></h3><div id="ad-b"></div></div>
    </div>
    <div class="card"><h3>성분끼리 계산 <small>같은 (i, j) 자리끼리만 짝지음</small></h3>
      <div class="row">${LA.slider('ad-k', '스칼라 k', -3, 3, 0.5, 2)}</div>
      <div class="scroll"><div class="mxrow" id="ad-show"></div></div>
      <div class="calc" id="ad-calc"></div></div>`;
  let A = X.fromN([[1, -2], [3, 0]]), B = X.fromN([[4, 1], [-1, 2]]);
  let lock = false;
  const edA = editor(body.querySelector('#ad-a'), A, (M) => { A = M; fit('A'); }, { resize: { maxR: 3, maxC: 3 } });
  const edB = editor(body.querySelector('#ad-b'), B, (M) => { B = M; fit('B'); }, { sym: 'b', resize: { maxR: 3, maxC: 3 } });
  function fit(who) {
    if (lock) return; const [S, D, ed] = who === 'A' ? [A, B, edB] : [B, A, edA];
    if (S.length !== D.length || S[0].length !== D[0].length) { lock = true; const M = S.map((r, i) => r.map((_, j) => (D[i] && D[i][j]) || f(0))); if (who === 'A') B = M; else A = M; ed.set(M); lock = false; }
    draw();
  }
  const get = LA.bindSliders(body, ['ad-k'], () => draw());
  function draw() {
    const k = f(get()['ad-k']);
    const S = A.map((r, i) => r.map((a, j) => a.add(B[i][j])));
    const K = A.map((r) => r.map((a) => a.mul(k)));
    body.querySelector('#ad-show').innerHTML = mat(A, { sub: 'a' }) + '<span class="op">+</span>' + mat(B, { sub: 'b' }) + '<span class="op">=</span>' + mat(S, { sub: 's' }) +
      `<span class="op" style="margin-left:24px">${k.html()} ·</span>` + mat(A, { sub: 'a' }) + '<span class="op">=</span>' + mat(K);
    body.querySelector('#ad-calc').innerHTML = S.map((r, i) => r.map((s, j) => `<span class="ln">(A+B)<sub>${i + 1}${j + 1}</sub> = ${v('a', `${i + 1}${j + 1}`)} + ${v('b', `${i + 1}${j + 1}`)} = ${fh(A[i][j])} + ${par(B[i][j])} = <b>${s.html()}</b>    (${k.html()}A)<sub>${i + 1}${j + 1}</sub> = ${k.html()}·${par(A[i][j])} = <b>${K[i][j].html()}</b></span>`).join('')).join('');
  }
  draw();
}

function tTab(body) {
  body.innerHTML = `
    <div class="lab">
      <div class="card"><h3><i class="var">A</i> <small>m×n</small></h3><div id="tr-a"></div>
        <p class="small">전치는 <b>(<i>i</i>, <i>j</i>) 자리의 수를 (<i>j</i>, <i>i</i>) 자리로</b> 옮기는 것입니다. 행이 열이 되고, 대각선(<i>i</i> = <i>j</i>)은 움직이지 않습니다.</p>
        <div class="keyline"><span class="lbl">정의와 성질</span>(<i>A</i><sup>T</sup>)<sub><i>ij</i></sub> = <i>a</i><sub><i>ji</i></sub> ,  (<i>AB</i>)<sup>T</sup> = <i>B</i><sup>T</sup><i>A</i><sup>T</sup> ,  (<i>A</i><sup>T</sup>)<sup>T</sup> = <i>A</i></div></div>
      <div class="card"><h3>칸에 마우스를 올려 짝 찾기</h3><div class="scroll"><div class="mxrow" id="tr-show"></div></div><div class="stepbox" id="tr-exp"></div>
        <div class="row"><button type="button" class="btn primary" id="tr-anim">대각선을 축으로 뒤집기 애니메이션</button></div>
        <div class="viz" id="tr-viz" style="max-width:420px"></div></div>
    </div>`;
  let A = X.fromN([[1, 2, 3], [4, 5, 6]]), sel = [0, 1];
  editor(body.querySelector('#tr-a'), A, (M) => { A = M; draw(); }, { resize: { maxR: 4, maxC: 4 } });
  const viz = body.querySelector('#tr-viz');
  const cv = document.createElement('canvas'); cv.className = 'plane'; viz.appendChild(cv);
  let t = 0;
  function paint() {
    const w = viz.clientWidth; if (!w) return; const m = A.length, n = A[0].length, S = Math.max(m, n);
    const cell = Math.min(56, (w - 40) / S), H = cell * S + 40, d = devicePixelRatio || 1;
    cv.width = w * d; cv.height = H * d; cv.style.height = H + 'px'; const c = cv.getContext('2d'); c.setTransform(d, 0, 0, d, 0, 0);
    c.fillStyle = LA.color('canvas'); c.fillRect(0, 0, w, H);
    const ox = 20, oy = 20;
    c.strokeStyle = LA.color('warn'); c.setLineDash([4, 4]); c.beginPath(); c.moveTo(ox, oy); c.lineTo(ox + S * cell, oy + S * cell); c.stroke(); c.setLineDash([]);
    for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) {
      const x = ox + (j + (i - j) * t) * cell, y = oy + (i + (j - i) * t) * cell;
      const hot = (i === sel[0] && j === sel[1]);
      c.fillStyle = LA.alpha(LA.color(hot ? 'e1' : i === j ? 'warn' : 'accent'), hot ? 0.35 : 0.13); c.fillRect(x + 2, y + 2, cell - 4, cell - 4);
      c.fillStyle = LA.color('ink'); c.font = '500 14px "JetBrains Mono", monospace'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(A[i][j].toString(), x + cell / 2, y + cell / 2 + 3);
      c.fillStyle = LA.color('muted'); c.font = 'italic 10px "STIX Two Text", serif'; c.fillText(`a${i + 1}${j + 1}`, x + cell / 2, y + 11);
    }
  }
  new ResizeObserver(paint).observe(viz);
  body.querySelector('#tr-anim').addEventListener('click', () => { const from = t > 0.5 ? 1 : 0; LA.tween(1300, (u) => { t = from ? 1 - u : u; paint(); }); });
  function draw() {
    const T = X.T(A); if (sel[0] >= A.length || sel[1] >= A[0].length) sel = [0, 0];
    const [i, j] = sel;
    body.querySelector('#tr-show').innerHTML = `<span id="tr-A">${mat(A, { name: 'A', sub: 'a', cell: (r, c) => (r === i && c === j ? 'h1' : r === c ? 'h2' : '') })}</span>` +
      mat(T, { name: 'A<sup>T</sup>', sub: 'a', cell: (r, c) => (r === j && c === i ? 'h1' : r === c ? 'h2' : '') }).replace(/a<sub>(\d)(\d)<\/sub>/g, 'a<sub>$2$1</sub>');
    body.querySelector('#tr-exp').innerHTML = `<div class="math">(<i>A</i><sup>T</sup>)<sub>${j + 1}${i + 1}</sub> = ${v('a', `${i + 1}${j + 1}`)} = <b class="t1">${A[i][j].html()}</b></div><span class="small muted">A의 ${i + 1}행 ${j + 1}열 → Aᵀ의 ${j + 1}행 ${i + 1}열. 초록 칸은 대각선(제자리).</span>`;
    paint();
  }
  body.querySelector('#tr-show').addEventListener('mouseover', (e) => { const c = e.target.closest('#tr-A .c'); if (c) { sel = [+c.dataset.i, +c.dataset.j]; draw(); } });
  draw();
}

/* ======================================================= 1.3 역행렬 */
LA.section({
  id: 'inverse', ch: 1, title: '역행렬', en: 'Inverse Matrices',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead"><i class="var">AB</i> = <i class="var">BA</i> = <i class="var">I</i>이면 <i class="var">B</i>를 <i class="var">A</i>의 역행렬 <i class="var">A</i><sup>−1</sup>이라 합니다. 변환으로 보면 <i class="var">A</i>가 한 일을 <b>정확히 되돌리는</b> 변환입니다.</p>
      <ul>
        <li>구하는 법: [<i class="var">A</i> | <i class="var">I</i>]에 가우스-조르당 소거를 해서 왼쪽이 <i class="var">I</i>가 되면 오른쪽이 <i class="var">A</i><sup>−1</sup>입니다.</li>
        <li>2×2 공식: <span class="math">[<i>a b</i>; <i>c d</i>]<sup>−1</sup> = <span class="fr"><span>1</span><span><i>ad</i> − <i>bc</i></span></span> [<i>d</i>  −<i>b</i>; −<i>c</i>  <i>a</i>]</span></li>
        <li>가역 ⇔ det <i class="var">A</i> ≠ 0 ⇔ 랭크 = <i class="var">n</i> ⇔ <i class="var">A</i><b class="vec">x</b> = <b class="vec">0</b>의 해는 <b class="vec">0</b>뿐 ⇔ RREF가 <i class="var">I</i>.</li>
        <li>성질: (<i class="var">AB</i>)<sup>−1</sup> = <i class="var">B</i><sup>−1</sup><i class="var">A</i><sup>−1</sup> (양말 신고 신발 신기 → 벗을 땐 신발 먼저), (<i class="var">A</i><sup>T</sup>)<sup>−1</sup> = (<i class="var">A</i><sup>−1</sup>)<sup>T</sup>.</li>
      </ul>
    </div>
    <div class="lab">
      <div class="card"><h3><i class="var">A</i> 입력</h3><div id="iv-ed"></div><div id="iv-st"></div></div>
      <div class="card"><h3>2×2일 때: 변환과 되돌리기 <small>A → A⁻¹</small></h3><div class="viz" id="iv-viz"></div>
        <div class="row"><button type="button" class="btn primary" id="iv-play">A 적용 후 A⁻¹로 되돌리기</button></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>첫째 열 (<b>e</b>₁의 행선지)</span><span><i style="background:var(--e2)"></i>둘째 열 (<b>e</b>₂의 행선지)</span></div></div>
      <div class="card" id="iv-3card" hidden><h3>3×3일 때: 공간 변환과 되돌리기 <small>끌어서 회전</small></h3><div id="iv-3d"></div>
        <div class="legend"><span><i style="background:var(--e1)"></i>Ae₁</span><span><i style="background:var(--e2)"></i>Ae₂</span><span><i style="background:var(--e3)"></i>Ae₃</span><span><i style="background:var(--accent)"></i>단위정육면체의 상</span></div>
        <p class="small muted" id="iv-3cap"></p></div>
    </div>
    <div class="card"><h3>[A | I] 가우스-조르당 소거</h3><div id="iv-step"></div>
      <div class="row top" style="gap:24px"><div class="scroll" id="iv-mat"></div><div class="stepbox" id="iv-desc" style="flex:1 1 280px"></div></div></div>
    <details class="expand" open><summary>검산: <i class="var">A</i><i class="var">A</i><sup>−1</sup> = <i class="var">I</i> 전개</summary><div class="body" id="iv-check"></div></details>`;
    const viz = root.querySelector('#iv-viz'); const plane = new Plane(viz, { range: 5, aspect: 0.8 });
    const I3 = N.eye(3);
    const T3 = LA.transform3D(root.querySelector('#iv-3d'), { playLabel: 'A 적용 후 A⁻¹로 되돌리기', onPlay: (T) => {
      const An = X.toN(A); T.set(An, I3); T.setT(0);
      LA.tween(1300, (u) => T.setT(u), () => setTimeout(() => {
        if (!Ainv) return; T.set(I3, An); T.setT(0);
        LA.tween(1300, (u) => T.setT(u), () => { T.set(An, I3); T.setT(1); });
      }, 500));
    } });
    let A, Ainv, t = 0, sp, showFn;
    plane.draw = (p) => {
      if (!A || A.length !== 2) return;
      const An = X.toN(A), I = N.eye(2);
      let M;
      if (t <= 1) M = N.add(N.scale(I, 1 - t), N.scale(An, t));
      else { const u = t - 1; M = N.add(N.scale(An, 1 - u), N.scale(I, u)); }
      p.tgrid(M, 'accent', 0.3);
      p.poly([[0, 0], [M[0][0], M[1][0]], [M[0][0] + M[0][1], M[1][0] + M[1][1]], [M[0][1], M[1][1]]], 'accent', null, { a: 0.15 });
      p.arrow([0, 0], [M[0][0], M[1][0]], 'e1', { label: 'Ae₁' });
      p.arrow([0, 0], [M[0][1], M[1][1]], 'e2', { label: 'Ae₂' });
    };
    root.querySelector('#iv-play').addEventListener('click', () => {
      if (!A || A.length !== 2) return; t = 0;
      LA.tween(1200, (u) => { t = u; plane.render(); }, () => setTimeout(() => LA.tween(1200, (u) => { t = 1 + u; plane.render(); }), 500));
    });
    function run(M) {
      A = M; const n = A.length;
      const aug = A.map((r, i) => [...r, ...X.eye(n)[i]]);
      const res = X.rref(aug, n);
      const ok = res.rank === n;
      Ainv = ok ? res.R.map((r) => r.slice(n)) : null;
      const d = X.det(A);
      let st = `<div class="row"><span class="pill ${ok ? 'ok' : 'bad'}">${ok ? '가역' : '비가역 (특이행렬)'}</span><span class="small">det A = <b>${d.html()}</b></span></div>`;
      if (n === 2) {
        const [[a, b], [c, dd]] = A;
        st += `<div class="calc"><span class="ln">ad − bc = ${par(a)}·${par(dd)} − ${par(b)}·${par(c)} = <b>${d.html()}</b></span>${ok ? `<span class="ln">A⁻¹ = (1/${d.toString()}) · [ ${dd.toString()}  ${b.neg().toString()} ; ${c.neg().toString()}  ${a.toString()} ]</span>` : '<span class="ln">ad − bc = 0 → 1/0 이 되어 공식이 성립하지 않습니다</span>'}</span></div>`;
      }
      if (ok) st += `<div class="mxrow">${mat(Ainv, { name: 'A<sup>−1</sup>' })}</div>`;
      else st += `<p class="small">정사각형이 한 직선(또는 점)으로 납작해지면 원래 위치를 되찾을 방법이 없습니다. 그래서 역행렬이 없습니다.</p>`;
      root.querySelector('#iv-st').innerHTML = st;
      viz.parentElement.hidden = n !== 2;
      root.querySelector('#iv-3card').hidden = n !== 3;
      if (n === 3) {
        T3.set(X.toN(A), I3); T3.setT(1);
        root.querySelector('#iv-3cap').textContent = ok ? `정육면체가 부피 ${LA.fmt(Math.abs(d.val()))}배인 평행육면체로 바뀝니다. 부피가 0이 아니라서 A⁻¹이 정확히 원래 정육면체로 되돌립니다.` : '평행육면체가 평면이나 직선으로 납작해집니다(부피 0). 납작해진 것을 다시 펼칠 방법이 없어서 역행렬이 없습니다.';
      }
      showFn = (k) => {
        const s = res.steps[k];
        root.querySelector('#iv-mat').innerHTML = mat(s.M, { aug: n, cell: (i, j) => (s.piv && s.piv[0] === i && s.piv[1] === j ? 'pv' : j >= n ? 'h2' : '') });
        root.querySelector('#iv-desc').innerHTML = s.op ? `<span class="ph">${s.phase}</span><div class="op-t">${s.desc}</div><div class="small">${s.detail}</div>` : `<span class="small">왼쪽은 A, 오른쪽(초록)은 단위행렬 I. 왼쪽을 I로 만드는 연산을 오른쪽에도 똑같이 적용합니다. 그 연산들을 모두 곱한 것이 곧 A⁻¹이기 때문입니다.</span>`;
      };
      if (sp) sp.reset(res.steps.length); else sp = stepper(root.querySelector('#iv-step'), res.steps.length, (k) => showFn(k));
      root.querySelector('#iv-check').innerHTML = ok ? (() => {
        const P = X.mul(A, Ainv);
        return `<div class="mxrow">${mat(A)}<span class="op">·</span>${mat(Ainv)}<span class="op">=</span>${mat(P)}</div><div class="calc">${P.map((r, i) => r.map((x, j) => `<span class="ln">(AA⁻¹)<sub>${i + 1}${j + 1}</sub> = ${A[i].map((a, k) => `${par(a)}·${par(Ainv[k][j])}`).join(' + ')} = <b>${x.html()}</b></span>`).join('')).join('')}</div>`;
      })() : '<p class="small">역행렬이 없으므로 검산할 것이 없습니다.</p>';
      plane.render();
    }
    editor(root.querySelector('#iv-ed'), X.fromN([[2, 1], [1, 1]]), run, {
      resize: { square: true, min: 2, max: 4 },
      presets: [{ name: '2×2 가역', A: [[2, 1], [1, 1]] }, { name: '2×2 특이', A: [[2, 4], [1, 2]] }, { name: '3×3', A: [[1, 2, 3], [0, 1, 4], [5, 6, 0]] }],
    });
    run(X.fromN([[2, 1], [1, 1]]));
  },
});
})();
