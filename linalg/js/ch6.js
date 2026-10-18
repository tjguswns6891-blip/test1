/* 6장 내적 공간과 직교성 */
(function () {
'use strict';
const { F, f, X, N, mat, fh, par, term, v, editor, stepper, Plane, View3D, MINUS, fmt } = LA;
LA.chapter(6, '내적 공간과 직교성', 'Inner Product Spaces and Orthogonality');
const vec2 = (p) => `(${fmt(p[0])}, ${fmt(p[1])})`;
const vecF = (u) => `(${u.map((x) => x.html()).join(', ')})`;
const dotF = (a, b) => a.reduce((s, x, i) => s.add(x.mul(b[i])), f(0));
/* √(p/q)를 보기 좋게 */
function sqrtTxt(q) { const r = Math.sqrt(q.val()); return Number.isInteger(Math.round(r * 1e9) / 1e9) ? fmt(r) : `√${q.toString()}`; }

/* ======================================================= 6.1 직교 기저 */
LA.section({
  id: 'ortho', ch: 6, title: '직교 기저와 정규직교 기저', en: 'Orthogonal and Orthonormal Bases',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">기저 벡터끼리 모두 수직(내적 0)이면 <b>직교 기저</b>, 거기에 길이까지 모두 1이면 <b>정규직교 기저</b>입니다. 정규직교 기저의 가장 큰 장점은 <b>좌표를 내적 한 번으로</b> 구한다는 것입니다.</p>
      <div class="keyline"><span class="lbl">정규직교 기저 {q₁, …, qₙ}에서의 좌표</span><b>x</b> = (<b>x</b>·<b>q</b><sub>1</sub>)<b>q</b><sub>1</sub> + (<b>x</b>·<b>q</b><sub>2</sub>)<b>q</b><sub>2</sub> + ⋯ + (<b>x</b>·<b>q</b><sub><i>n</i></sub>)<b>q</b><sub><i>n</i></sub></div>
      <p class="small muted">일반 기저라면 연립방정식을 풀어야 하지만(3장 기저), 정규직교면 각 축에 수선을 내린 그림자 길이가 곧 좌표입니다. 이 벡터들을 열로 세운 <b>직교행렬</b> <i>Q</i>는 <i>Q</i><sup>T</sup><i>Q</i> = <i>I</i>, 즉 <i>Q</i><sup>−1</sup> = <i>Q</i><sup>T</sup>입니다. (<i>Q</i><sup>T</sup><i>Q</i>)<sub><i>ij</i></sub> = <b>q</b><sub><i>i</i></sub>·<b>q</b><sub><i>j</i></sub>이기 때문입니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>회전한 정규직교 기저 <small>x를 끌기</small></h3><div class="viz" id="or-viz"></div>${LA.slider('or-th', '회전각 θ°', 0, 180, 5, 30)}</div>
      <div class="card"><h3>좌표 = 내적</h3><div id="or-out"></div></div>
    </div>
    <div class="card"><h3>직교성 검사기 <small>벡터를 열로 입력 → (QᵀQ)ᵢⱼ = qᵢ·qⱼ 표</small></h3>
      <div class="lab"><div id="or-ed"></div><div id="or-g"></div></div></div>`;
    let x = [3, 1.5];
    const plane = new Plane(root.querySelector('#or-viz'), { range: 4.5, aspect: 0.9, snap: 0.25 });
    plane.handle({ get: () => x, set: (p) => (x = p), color: 'accent' });
    const get = LA.bindSliders(root, ['or-th'], () => plane.changed());
    const Q = () => { const t = get()['or-th'] * Math.PI / 180; return [[Math.cos(t), Math.sin(t)], [-Math.sin(t), Math.cos(t)]]; };
    plane.draw = (p) => {
      const [q1, q2] = Q(); const c1 = N.dot(x, q1), c2 = N.dot(x, q2);
      p.tgrid([[q1[0], q2[0]], [q1[1], q2[1]]], 'muted', 0.3);
      p.infLine([0, 0], q1, 'e1', 1, true); p.infLine([0, 0], q2, 'e2', 1, true);
      const f1 = N.vs(q1, c1), f2 = N.vs(q2, c2);
      p.seg(x, f1, 'e1', { dash: true }); p.seg(x, f2, 'e2', { dash: true });
      p.arrow([0, 0], f1, 'e1', { w: 5, alpha: 0.35 }); p.arrow([0, 0], f2, 'e2', { w: 5, alpha: 0.35 });
      p.arrow([0, 0], q1, 'e1', { label: 'q₁' }); p.arrow([0, 0], q2, 'e2', { label: 'q₂' }); p.arrow([0, 0], x, 'accent', { label: 'x' });
    };
    plane.onchange = out;
    function out() {
      const [q1, q2] = Q(), c1 = N.dot(x, q1), c2 = N.dot(x, q2);
      root.querySelector('#or-out').innerHTML = `<div class="calc">
        <span class="ln">q₁ = ${vec2(q1)},  q₂ = ${vec2(q2)}</span>
        <span class="ln">q₁·q₂ = ${par(q1[0])}·${par(q2[0])} + ${par(q1[1])}·${par(q2[1])} = <b>${fmt(N.dot(q1, q2))}</b>  (수직)</span>
        <span class="ln">‖q₁‖² = ${fmt(N.dot(q1, q1))},  ‖q₂‖² = ${fmt(N.dot(q2, q2))}  (길이 1)</span>
        <span class="ln">c₁ = x·q₁ = ${par(x[0])}·${par(q1[0])} + ${par(x[1])}·${par(q1[1])} = <b>${fmt(c1)}</b></span>
        <span class="ln">c₂ = x·q₂ = ${par(x[0])}·${par(q2[0])} + ${par(x[1])}·${par(q2[1])} = <b>${fmt(c2)}</b></span>
        <span class="ln">검산: ${fmt(c1)}·q₁ + ${par(c2)}·q₂ = ${vec2(N.vadd(N.vs(q1, c1), N.vs(q2, c2)))} = x ✓</span>
        <span class="ln">피타고라스: c₁² + c₂² = ${fmt(c1 * c1 + c2 * c2)} = ‖x‖² = ${fmt(N.dot(x, x))}</span></div>
        <p class="small">연립방정식 없이 내적 두 번으로 끝났습니다. 점선은 x에서 각 축으로 내린 수선입니다.</p>`;
    }
    out();
    editor(root.querySelector('#or-ed'), X.fromN([[1, 2, 2], [2, 1, -2], [2, -2, 1]]), (A) => {
      const n = A[0].length, cols = [...Array(n).keys()].map((j) => A.map((r) => r[j]));
      const G = cols.map((a) => cols.map((b) => dotF(a, b)));
      const orth = G.every((r, i) => r.every((x, j) => i === j || x.isZero()));
      const unit = G.every((r, i) => r[i].isOne()); const same = orth && G.every((r, i) => r[i].eq(G[0][0]));
      root.querySelector('#or-g').innerHTML = `<div class="mxrow">${mat(G, { name: 'Q<sup>T</sup>Q', cell: (i, j) => (i === j ? 'h1' : G[i][j].isZero() ? 'h2' : 'pv') })}</div>
        <div class="calc">${G.map((r, i) => r.map((g, j) => (j < i ? '' : `<span class="ln">q${i + 1}·q${j + 1} = ${cols[i].map((a, k) => `${par(a)}·${par(cols[j][k])}`).join(' + ')} = <b>${g.html()}</b></span>`)).join('')).join('')}</div>
        <div class="row">${orth ? '<span class="pill ok">직교</span>' : '<span class="pill bad">직교 아님 (비대각 성분 ≠ 0)</span>'}${unit ? '<span class="pill ok">정규직교 (대각 = 1)</span>' : orth ? `<span class="pill info">각 벡터를 길이로 나누면 정규직교${same ? ` (모두 길이 ${sqrtTxt(G[0][0])})` : ''}</span>` : ''}</div>`;
    }, { sym: 'q', resize: { minR: 2, maxR: 4, minC: 1, maxC: 4 }, presets: [{ name: '직교 (길이 3)', A: [[1, 2, 2], [2, 1, -2], [2, -2, 1]] }, { name: '직교 아님', A: [[1, 1], [0, 1], [1, 0]] }, { name: '표준 기저', A: [[1, 0, 0], [0, 1, 0], [0, 0, 1]] }] });
    root.querySelector('#or-ed input').dispatchEvent(new Event('input', { bubbles: true }));
  },
});

/* ======================================================= 6.2 그람-슈미트 */
LA.section({
  id: 'gs', ch: 6, title: '그람-슈미트 과정', en: 'The Gram–Schmidt Process',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">아무 기저 {<b class="vec">v</b><sub>1</sub>, <b class="vec">v</b><sub>2</sub>, …}이나 받아서 같은 공간을 생성하는 정규직교 기저로 바꾸는 알고리즘입니다. 아이디어는 하나뿐입니다. <b>이미 만든 방향의 성분(그림자)을 빼서 수직인 부분만 남긴다.</b></p>
      <div class="keyline"><span class="lbl">k번째 단계</span><b>u</b><sub><i>k</i></sub> = <b>v</b><sub><i>k</i></sub> − <span class="sum">Σ</span><sub><i>j</i>&lt;<i>k</i></sub> <span class="fr"><span><b>v</b><sub><i>k</i></sub>·<b>u</b><sub><i>j</i></sub></span><span><b>u</b><sub><i>j</i></sub>·<b>u</b><sub><i>j</i></sub></span></span> <b>u</b><sub><i>j</i></sub> ,     <b>q</b><sub><i>k</i></sub> = <b>u</b><sub><i>k</i></sub> / ‖<b>u</b><sub><i>k</i></sub>‖</div>
      <p class="small muted">정규화(길이로 나누기)를 맨 끝에 하면 중간 계산이 모두 분수로 깔끔하게 유지됩니다. 아래 계산은 그 방식을 따릅니다. 그림은 끌어서 회전할 수 있습니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>v₁, v₂, v₃ (열) 입력</h3><div id="gs-ed"></div><div id="gs-step"></div></div>
      <div class="card"><h3 id="gs-cap">ℝ³</h3><div class="viz" id="gs-viz"></div>
        <div class="legend"><span><i style="background:var(--muted)"></i>원래 v</span><span><i style="background:var(--e1)"></i>u₁/q₁</span><span><i style="background:var(--e2)"></i>u₂/q₂</span><span><i style="background:var(--e3)"></i>u₃/q₃</span><span><i style="background:var(--warn)"></i>빼는 그림자</span></div></div>
    </div>
    <div class="card"><div class="stepbox" id="gs-desc"></div></div>
    <details class="expand"><summary>보너스: QR 분해 (A = QR, R = QᵀA는 위삼각)</summary><div class="body" id="gs-qr"></div></details>`;
    let V, U, sp, k = 0;
    const view = new View3D(root.querySelector('#gs-viz'), { range: 2 });
    const C = ['e1', 'e2', 'e3'];
    const plan = () => { const n = V.length; const st = [{ t: 'start' }]; for (let i = 0; i < n; i++) { if (i) st.push({ t: 'proj', i }); st.push({ t: 'u', i }); } st.push({ t: 'norm' }); return st; };
    let steps = [];
    function compute() {
      U = []; const info = [];
      V.forEach((vk, i) => {
        let u = vk.slice(); const terms = [];
        U.forEach((uj, j) => { if (!uj) return; const num = dotF(vk, uj), den = dotF(uj, uj), c = num.div(den); terms.push({ j, num, den, c, p: uj.map((x) => x.mul(c)) }); u = u.map((x, t) => x.sub(uj[t].mul(c))); });
        const zero = u.every((x) => x.isZero());
        U.push(zero ? null : u); info.push({ terms, zero, u });
      });
      return info;
    }
    let info;
    view.draw = (p) => {
      const s = steps[k] || { t: 'start' }; const Vn = V.map((x) => x.map((t) => t.val()));
      const doneU = s.t === 'start' ? 0 : s.t === 'proj' ? s.i : s.t === 'u' ? s.i + 1 : V.length;
      const norm = s.t === 'norm';
      if (doneU >= 2 && U[0] && U[1]) p.planePatch(U[0].map((x) => x.val()), U[1].map((x) => x.val()), 'accent');
      Vn.forEach((x, i) => p.arrow([0, 0, 0], x, 'muted', { w: 1.5, alpha: 0.6, label: `v${'₁₂₃'[i]}` }));
      for (let i = 0; i < doneU; i++) { if (!U[i]) continue; let u = U[i].map((x) => x.val()); if (norm) u = N.vs(u, 1 / N.norm(u)); p.arrow([0, 0, 0], u, C[i], { label: `${norm ? 'q' : 'u'}${'₁₂₃'[i]}`, w: 3 }); }
      if (s.t === 'proj' || (s.t === 'u' && s.i > 0)) {
        const i = s.i, vi = Vn[i]; let acc = [0, 0, 0];
        info[i].terms.forEach((tm) => { const pv = tm.p.map((x) => x.val()); p.arrow(acc, N.vadd(acc, pv), 'warn', { w: 2.5 }); acc = N.vadd(acc, pv); });
        p.seg(acc, vi, s.t === 'u' ? C[i] : 'muted', { dash: true, w: 2 });
        if (s.t === 'u' && U[i]) p.arrow(acc, vi, C[i], { w: 1.5, alpha: 0.5 });
      }
    };
    function desc() {
      const s = steps[k]; let h = '';
      const lineU = (i) => {
        const I = info[i]; const sub = i + 1;
        let t = `<span class="ph">u${'₁₂₃'[i]} 만들기</span>`;
        if (!I.terms.length) t += `<div class="math"><b>u</b><sub>1</sub> = <b>v</b><sub>1</sub> = ${vecF(V[0])}</div><p class="small">첫 벡터는 뺄 것이 없으니 그대로 씁니다.</p>`;
        else {
          t += `<div class="math"><b>u</b><sub>${sub}</sub> = <b>v</b><sub>${sub}</sub> ${I.terms.map((tm) => `− <span class="fr"><span><b>v</b><sub>${sub}</sub>·<b>u</b><sub>${tm.j + 1}</sub></span><span><b>u</b><sub>${tm.j + 1}</sub>·<b>u</b><sub>${tm.j + 1}</sub></span></span><b>u</b><sub>${tm.j + 1}</sub>`).join(' ')}</div><div class="calc">`;
          I.terms.forEach((tm) => {
            t += `<span class="ln">v${sub}·u${tm.j + 1} = ${V[i].map((a, q) => `${par(a)}·${par(U[tm.j][q])}`).join(' + ')} = <b>${tm.num.html()}</b></span>`;
            t += `<span class="ln">u${tm.j + 1}·u${tm.j + 1} = ${U[tm.j].map((a) => `${par(a)}²`).join(' + ')} = <b>${tm.den.html()}</b></span>`;
            t += `<span class="ln">그림자 = (${tm.num.toString()} / ${tm.den.toString()})·u${tm.j + 1} = ${tm.c.html()}·${vecF(U[tm.j])} = <b>${vecF(tm.p)}</b></span>`;
          });
          t += `<span class="ln">u${sub} = ${vecF(V[i])} ${I.terms.map((tm) => `− ${vecF(tm.p)}`).join(' ')} = <b>${vecF(I.u)}</b></span>`;
          t += I.terms.map((tm) => `<span class="ln">검산 u${sub}·u${tm.j + 1} = ${dotF(I.u, U[tm.j]).html()} ✓ 수직</span>`).join('');
          t += '</div>';
          if (I.zero) t += `<p class="tw small">u${sub} = 0: v${sub}가 앞의 벡터들의 조합(종속)이라 새 방향이 없습니다. 이 벡터는 버립니다.</p>`;
        }
        return t;
      };
      if (s.t === 'start') h = `<span class="ph">시작</span><p>회색 화살표가 원래 벡터입니다. <b>다음</b>을 눌러 한 단계씩 진행하세요.</p>`;
      else if (s.t === 'proj') h = `<span class="ph">v${'₁₂₃'[s.i]}에서 뺄 그림자 보기</span><p>빨간 화살표가 v${'₁₂₃'[s.i]}의 그림자(앞서 만든 u들 방향 성분)입니다. 그 끝에서 v${'₁₂₃'[s.i]} 끝까지가 남길 수직 부분입니다.</p>`;
      else if (s.t === 'u') h = lineU(s.i);
      else {
        h = `<span class="ph">정규화: 길이로 나누기</span><div class="calc">${U.map((u, i) => (u ? `<span class="ln">‖u${i + 1}‖ = √(${dotF(u, u).toString()}) = ${sqrtTxt(dotF(u, u))}  →  q${i + 1} = u${i + 1} / ${sqrtTxt(dotF(u, u))} = (${u.map((x) => fmt(x.val() / Math.sqrt(dotF(u, u).val()))).join(', ')})</span>` : '')).join('')}</div><p class="small">이제 {q} 는 서로 수직이고 길이가 1인 정규직교 기저입니다.</p>`;
      }
      root.querySelector('#gs-desc').innerHTML = h;
      view.render();
    }
    function run(A) {
      V = A[0].map((_, j) => A.map((r) => r[j])); info = compute(); steps = plan();
      root.querySelector('#gs-cap').textContent = `ℝ³ · 벡터 ${V.length}개`;
      if (sp) sp.reset(steps.length); else sp = stepper(root.querySelector('#gs-step'), steps.length, (kk) => { k = kk; desc(); }, { ms: 1800 });
      const Qc = U.filter(Boolean).map((u) => { const n = Math.sqrt(dotF(u, u).val()); return u.map((x) => x.val() / n); });
      if (Qc.length === V.length) {
        const Q = N.T(Qc), Rm = N.mul(Qc, X.toN(A));
        root.querySelector('#gs-qr').innerHTML = `<div class="mxrow">${mat(A, { name: 'A' })}${mat(Q.map((r) => r.map((t) => fmt(t))), { name: 'Q', noeq: true })}${mat(Rm.map((r) => r.map((t) => fmt(t))), { name: 'R', noeq: true, cell: (i, j) => (i > j ? 'dim' : '') })}</div><p class="small">r<sub>ij</sub> = q<sub>i</sub>·v<sub>j</sub>. q<sub>i</sub>는 v<sub>1</sub>…v<sub>i</sub>만으로 만들어졌으므로 i &gt; j이면 r<sub>ij</sub> = 0입니다.</p>`;
      } else root.querySelector('#gs-qr').innerHTML = '<p class="small">벡터가 종속이라 QR 분해를 보여 주지 않습니다.</p>';
    }
    editor(root.querySelector('#gs-ed'), X.fromN([[1, 1, 0], [1, 0, 1], [0, 1, 1]]), run, { sym: 'v', resize: { rows: false, minC: 2, maxC: 3 }, presets: [{ name: '3개', A: [[1, 1, 0], [1, 0, 1], [0, 1, 1]] }, { name: '2개 (평면)', A: [[3, 1], [0, 2], [0, 2]] }, { name: '종속 포함', A: [[1, 2, 0], [0, 0, 1], [1, 2, 1]] }] });
    run(X.fromN([[1, 1, 0], [1, 0, 1], [0, 1, 1]]));
  },
});

/* ======================================================= 6.3 최소제곱법 */
LA.section({
  id: 'lsq', ch: 6, title: '최소제곱법', en: 'Least Squares Approximation',
  render(root) {
    root.innerHTML = `
    <div class="concept">
      <p class="lead">점이 3개 이상이면 모든 점을 지나는 직선은 보통 없습니다. <i>A</i><b class="vec">x</b> = <b class="vec">b</b>의 해가 없는 것이죠. 그럴 때 <b>오차의 제곱합 ‖<b class="vec">b</b> − <i>A</i><b class="vec">x</b>‖²가 가장 작은</b> <b class="vec">x̂</b>을 찾는 것이 최소제곱법입니다.</p>
      <div class="keyline"><span class="lbl">정규방정식</span><i>A</i><sup>T</sup><i>A</i> <b>x̂</b> = <i>A</i><sup>T</sup><b>b</b>     ⟸   오차 <b>b</b> − <i>A</i><b>x̂</b>가 Col <i>A</i>에 수직: <i>A</i><sup>T</sup>(<b>b</b> − <i>A</i><b>x̂</b>) = <b>0</b></div>
      <p class="small muted">기하학적으로 <i>A</i><b>x̂</b>는 <b>b</b>를 열공간에 정사영한 것입니다. 열공간 안에서 <b>b</b>에 가장 가까운 점은 수선의 발이기 때문입니다. 점이 3개일 때는 오른쪽 아래에 ℝ³ 그림이 나타납니다.</p>
    </div>
    <div class="lab">
      <div class="card"><h3>데이터 점 끌기 <small id="ls-sse"></small></h3><div class="viz" id="ls-viz"></div>
        <div class="row"><button type="button" class="chip" id="ls-add">점 추가</button><button type="button" class="chip" id="ls-del">점 빼기</button><span class="small muted">모형</span><button type="button" class="chip on" data-deg="1">직선 y = c₀ + c₁x</button><button type="button" class="chip" data-deg="2">포물선 + c₂x²</button><label class="small"><input type="checkbox" id="ls-sq" checked> 오차 제곱 넓이</label></div></div>
      <div class="card"><h3>행렬로 쓰기</h3><div id="ls-ab"></div></div>
    </div>
    <details class="expand" open><summary>정규방정식 전부 전개</summary><div class="body" id="ls-ne"></div></details>
    <div class="card" id="ls-3d-card"><h3>ℝ³에서 본 정사영 <small>점 3개: b ∈ ℝ³, Col A = 평면</small></h3><div class="viz" id="ls-3d" style="max-width:560px"></div>
      <div class="legend"><span><i style="background:var(--accent)"></i>b (관측값)</span><span><i style="background:var(--ok)"></i>Ax̂ (정사영)</span><span><i style="background:var(--warn)"></i>오차 b − Ax̂ (평면에 수직)</span></div></div>`;
    let pts = [[-3, -1.5], [-1.5, -1], [0, 0.5], [1, 0.5], [2.5, 2.5]], deg = 1, sol = null;
    const plane = new Plane(root.querySelector('#ls-viz'), { range: 4.5, aspect: 0.8, snap: 0.25 });
    const v3 = new View3D(root.querySelector('#ls-3d'), { range: 4 });
    function handles() { plane.handles = []; pts.forEach((p0, i) => plane.handle({ get: () => pts[i], set: (q) => (pts[i] = q), color: 'accent' })); }
    const model = (x) => (sol ? sol.reduce((s, c, k) => s + c * x ** k, 0) : 0);
    plane.draw = (p) => {
      if (!sol) return;
      const sq = root.querySelector('#ls-sq').checked;
      pts.forEach(([x, y]) => { const yh = model(x), r = y - yh; if (sq) { const s = x > 0 ? -Math.abs(r) : Math.abs(r); p.poly([[x, yh], [x, y], [x + s, y], [x + s, yh]], 'warn', null, { a: 0.12 }); } p.seg([x, y], [x, yh], 'warn', { w: 2 }); });
      p.path((t) => { const x = -6 + 12 * t; return [x, model(x)]; }, 120, 'ok', { w: 2.5 });
    };
    plane.onchange = solve;
    function solve() {
      const n = pts.length, cols = deg + 1;
      const A = pts.map(([x]) => [...Array(cols).keys()].map((k) => x ** k)), b = pts.map((p) => p[1]);
      const AtA = N.mul(N.T(A), A), Atb = N.mv(N.T(A), b), inv = N.inv(AtA);
      if (!inv) { sol = null; root.querySelector('#ls-ne').innerHTML = '<p class="tw">AᵀA가 비가역입니다 (x값이 너무 적게 겹침). 점을 다른 x 위치로 옮기세요.</p>'; plane.render(); return; }
      sol = N.mv(inv, Atb); const yh = N.mv(A, sol), r = N.vsub(b, yh), sse = N.dot(r, r);
      root.querySelector('#ls-sse').textContent = `오차제곱합 = ${fmt(sse)}`;
      const ffm = (M) => M.map((row) => row.map((t) => fmt(t)));
      root.querySelector('#ls-ab').innerHTML = `<p class="small">점 (x<sub>i</sub>, y<sub>i</sub>)마다 식 하나: c₀ + c₁x<sub>i</sub>${deg > 1 ? ' + c₂x<sub>i</sub>²' : ''} = y<sub>i</sub></p>
        <div class="scroll"><div class="mxrow">${mat(ffm(A), { name: 'A', noeq: true, cell: (i, j) => ['', 'k1', 'k2'][j] })}${LA.col((deg > 1 ? ['c₀', 'c₁', 'c₂'] : ['c₀', 'c₁']))}<span class="op">≈</span>${LA.col(b.map((t) => fmt(t)), { name: '<b>b</b>', noeq: true })}</div></div>
        <p class="small">A의 1열은 모두 1(절편), 2열은 x값${deg > 1 ? ', 3열은 x²' : ''}입니다. 식이 ${n}개, 미지수가 ${cols}개라 정확한 해가 없습니다.</p>`;
      const xs = pts.map((p) => p[0]), ys = b; const S = (fn) => pts.reduce((s, p, i) => s + fn(xs[i], ys[i]), 0);
      const sumTxt = (lbl, fn, txt) => `<span class="ln">${lbl} = ${pts.map((p, i) => txt(xs[i], ys[i])).join(' + ')} = <b>${fmt(S(fn))}</b></span>`;
      let ne = `<p class="small">(AᵀA)<sub>jk</sub> = (A의 j열)·(A의 k열) = Σ x<sub>i</sub><sup>j+k</sup>,  (Aᵀb)<sub>j</sub> = Σ x<sub>i</sub><sup>j</sup>y<sub>i</sub> (j, k = 0부터)</p><div class="calc">`;
      ne += `<span class="ln">Σ1 = n = <b>${n}</b></span>`;
      ne += sumTxt('Σx', (x) => x, (x) => par(x));
      ne += sumTxt('Σx²', (x) => x * x, (x) => `${par(x)}²`);
      if (deg > 1) { ne += sumTxt('Σx³', (x) => x ** 3, (x) => `${par(x)}³`); ne += sumTxt('Σx⁴', (x) => x ** 4, (x) => `${par(x)}⁴`); }
      ne += sumTxt('Σy', (x, y) => y, (x, y) => par(y));
      ne += sumTxt('Σxy', (x, y) => x * y, (x, y) => `${par(x)}·${par(y)}`);
      if (deg > 1) ne += sumTxt('Σx²y', (x, y) => x * x * y, (x, y) => `${par(x)}²·${par(y)}`);
      ne += '</div>';
      ne += `<div class="mxrow">${mat(ffm(AtA), { name: 'A<sup>T</sup>A', noeq: true })}${LA.col(deg > 1 ? ['c₀', 'c₁', 'c₂'] : ['c₀', 'c₁'])}<span class="op">=</span>${LA.col(Atb.map((t) => fmt(t)), { name: 'A<sup>T</sup><b>b</b>', noeq: true })}<span class="op">⟹</span>${LA.col(sol.map((t) => fmt(t)), { name: '<b>x̂</b>' })}</div>`;
      if (deg === 1) {
        const d = AtA[0][0] * AtA[1][1] - AtA[0][1] * AtA[1][0];
        ne += `<div class="calc"><span class="ln">det(AᵀA) = ${fmt(AtA[0][0])}·${fmt(AtA[1][1])} − ${par(AtA[0][1])}² = ${fmt(d)}</span><span class="ln">c₀ = (${fmt(AtA[1][1])}·${par(Atb[0])} − ${par(AtA[0][1])}·${par(Atb[1])}) / ${fmt(d)} = <b>${fmt(sol[0])}</b></span><span class="ln">c₁ = (${fmt(AtA[0][0])}·${par(Atb[1])} − ${par(AtA[1][0])}·${par(Atb[0])}) / ${fmt(d)} = <b>${fmt(sol[1])}</b></span></div>`;
      }
      ne += `<div class="math">최적 ${deg > 1 ? '포물선' : '직선'}: y = ${fmt(sol[0])} ${sol.slice(1).map((c, k) => `${c < 0 ? '−' : '+'} ${fmt(Math.abs(c))}x${k ? '²' : ''}`).join(' ')}</div>`;
      ne += `<div class="calc"><span class="ln">오차 r = b − Ax̂ = (${r.map((t) => fmt(t)).join(', ')})</span>${[...Array(cols).keys()].map((j) => `<span class="ln">(A의 ${j + 1}열)·r = ${fmt(A.reduce((s, row, i) => s + row[j] * r[i], 0))}  ✓ 수직</span>`).join('')}</div>`;
      root.querySelector('#ls-ne').innerHTML = ne;
      root.querySelector('#ls-3d-card').hidden = !(n === 3 && deg === 1);
      v3.render();
    }
    v3.draw = (p) => {
      if (pts.length !== 3 || deg !== 1 || !sol) return;
      const a1 = [1, 1, 1], a2 = pts.map((q) => q[0]), b = pts.map((q) => q[1]), Ax = N.vadd(N.vs(a1, sol[0]), N.vs(a2, sol[1]));
      p.planePatch(a1, a2, 'ok');
      p.arrow([0, 0, 0], a1, 'e1', { label: '1열', w: 1.5 }); p.arrow([0, 0, 0], a2, 'e2', { label: '2열(x)', w: 1.5 });
      p.arrow([0, 0, 0], b, 'accent', { label: 'b' }); p.arrow([0, 0, 0], Ax, 'ok', { label: 'Ax̂' }); p.seg(Ax, b, 'warn', { w: 2.5, dash: true });
    };
    root.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.id === 'ls-add' && pts.length < 10) pts.push([Math.round((Math.random() * 7 - 3.5) * 4) / 4, Math.round((Math.random() * 5 - 2.5) * 4) / 4]);
      else if (b.id === 'ls-del' && pts.length > 2) pts.pop();
      else if (b.dataset.deg) { deg = +b.dataset.deg; root.querySelectorAll('[data-deg]').forEach((x) => x.classList.toggle('on', x === b)); }
      else return;
      handles(); solve(); plane.render();
    });
    root.querySelector('#ls-sq').addEventListener('change', () => plane.render());
    handles(); solve();
  },
});
})();
