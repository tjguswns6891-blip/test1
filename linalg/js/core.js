/* 선형대수 실험실 — 공용 엔진: 분수, 행렬 계산, 행렬 렌더링, 평면/공간 캔버스, 단계 재생기 */
(function () {
'use strict';
const LA = window.LA = { sections: [], chapters: [] };
const MINUS = '−';

/* ------------------------------------------------------------------ 분수 */
function gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { const t = a % b; a = b; b = t; } return a || 1; }
class F {
  constructor(n, d = 1) {
    if (d < 0) { n = -n; d = -d; }
    const g = gcd(n, d); this.n = n / g; this.d = d / g;
    if (Object.is(this.n, -0)) this.n = 0;
  }
  static of(x) {
    if (x instanceof F) return x;
    if (typeof x === 'number') {
      if (Number.isInteger(x)) return new F(x, 1);
      for (let d = 1; d <= 1000; d++) { const n = Math.round(x * d); if (Math.abs(n / d - x) < 1e-9) return new F(n, d); }
      return new F(Math.round(x * 1e6), 1e6);
    }
    return F.parse(x);
  }
  static parse(s) {
    s = String(s).trim().replace(/−/g, '-');
    if (s === '' || s === '-') return null;
    if (s.includes('/')) {
      const [a, b] = s.split('/'); const fa = F.parse(a), fb = F.parse(b);
      if (!fa || !fb || fb.n === 0) return null; return fa.div(fb);
    }
    if (!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(s)) return null;
    return F.of(Number(s));
  }
  add(o) { o = F.of(o); return new F(this.n * o.d + o.n * this.d, this.d * o.d); }
  sub(o) { o = F.of(o); return new F(this.n * o.d - o.n * this.d, this.d * o.d); }
  mul(o) { o = F.of(o); return new F(this.n * o.n, this.d * o.d); }
  div(o) { o = F.of(o); return new F(this.n * o.d, this.d * o.n); }
  neg() { return new F(-this.n, this.d); }
  inv() { return new F(this.d, this.n); }
  isZero() { return this.n === 0; }
  isOne() { return this.n === 1 && this.d === 1; }
  eq(o) { o = F.of(o); return this.n === o.n && this.d === o.d; }
  sign() { return Math.sign(this.n); }
  abs() { return new F(Math.abs(this.n), this.d); }
  val() { return this.n / this.d; }
  toString() { return this.d === 1 ? String(this.n) : this.n + '/' + this.d; }
  html() {
    if (this.d === 1) return this.n < 0 ? MINUS + (-this.n) : String(this.n);
    return (this.n < 0 ? MINUS : '') + `<span class="fr"><span>${Math.abs(this.n)}</span><span>${this.d}</span></span>`;
  }
}
LA.F = F;
const f = (x) => F.of(x);
LA.f = f;

/* ------------------------------------------------------------------ 숫자 표기 */
function fmt(x, d = 3) {
  if (x instanceof F) return x.toString().replace('-', MINUS);
  if (typeof x === 'string') return x;
  if (!isFinite(x)) return '∞';
  if (Math.abs(x) < 1e-10) x = 0;
  let s = String(+x.toFixed(d));
  if (s === '-0') s = '0';
  return s.replace('-', MINUS);
}
function fh(x, d) { return x instanceof F ? x.html() : (typeof x === 'string' ? x : fmt(x, d)); }
/* 음수면 괄호를 씌운다: 곱셈 전개에서 a·(−3) 처럼 */
function par(x, d) { const neg = x instanceof F ? x.n < 0 : (typeof x === 'number' && x < -1e-10); return neg ? `(${fh(x, d)})` : fh(x, d); }
/* 덧셈 항: 첫 항이 아니면 부호를 연산자로 */
function term(x, first, d) {
  const neg = x instanceof F ? x.n < 0 : x < -1e-10;
  const a = x instanceof F ? x.abs() : Math.abs(x);
  if (first) return neg ? MINUS + fh(a, d) : fh(a, d);
  return (neg ? ` ${MINUS} ` : ' + ') + fh(a, d);
}
Object.assign(LA, { fmt, fh, par, term, MINUS });

/* 인덱스 붙은 기호: v('a','12') → a₁₂ */
LA.v = (s, sub, sup) => `<i class="var">${s}</i>${sub != null && sub !== '' ? `<sub>${sub}</sub>` : ''}${sup ? `<sup>${sup}</sup>` : ''}`;
LA.bold = (s, sub) => `<b class="vec">${s}</b>${sub != null ? `<sub>${sub}</sub>` : ''}`;

/* ------------------------------------------------------------------ 실수 행렬 계산 */
const N = {
  zeros: (m, n) => Array.from({ length: m }, () => Array(n).fill(0)),
  eye: (n) => Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))),
  clone: (A) => A.map((r) => r.slice()),
  T: (A) => A[0].map((_, j) => A.map((r) => r[j])),
  mul: (A, B) => A.map((r) => B[0].map((_, j) => r.reduce((s, a, k) => s + a * B[k][j], 0))),
  mv: (A, v) => A.map((r) => r.reduce((s, a, k) => s + a * v[k], 0)),
  add: (A, B) => A.map((r, i) => r.map((a, j) => a + B[i][j])),
  sub: (A, B) => A.map((r, i) => r.map((a, j) => a - B[i][j])),
  scale: (A, k) => A.map((r) => r.map((a) => a * k)),
  dot: (u, v) => u.reduce((s, a, i) => s + a * v[i], 0),
  norm: (u) => Math.hypot(...u),
  vadd: (u, v) => u.map((a, i) => a + v[i]),
  vsub: (u, v) => u.map((a, i) => a - v[i]),
  vs: (u, k) => u.map((a) => a * k),
  cross: (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]],
  det(A) {
    const n = A.length, M = N.clone(A); let d = 1;
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      if (Math.abs(M[p][c]) < 1e-12) return 0;
      if (p !== c) { [M[p], M[c]] = [M[c], M[p]]; d = -d; }
      d *= M[c][c];
      for (let r = c + 1; r < n; r++) { const k = M[r][c] / M[c][c]; for (let j = c; j < n; j++) M[r][j] -= k * M[c][j]; }
    }
    return d;
  },
  inv(A) {
    const n = A.length, M = A.map((r, i) => [...r, ...N.eye(n)[i]]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      if (Math.abs(M[p][c]) < 1e-12) return null;
      [M[p], M[c]] = [M[c], M[p]];
      const k = M[c][c]; for (let j = 0; j < 2 * n; j++) M[c][j] /= k;
      for (let r = 0; r < n; r++) if (r !== c) { const t = M[r][c]; for (let j = 0; j < 2 * n; j++) M[r][j] -= t * M[c][j]; }
    }
    return M.map((r) => r.slice(n));
  },
  /* 대칭행렬 야코비 고윳값 분해: 내림차순 {vals, vecs(열)} */
  symEig(S) {
    const n = S.length, A = N.clone(S), V = N.eye(n);
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += A[i][j] ** 2;
      if (off < 1e-22) break;
      for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
        if (Math.abs(A[p][q]) < 1e-15) continue;
        const th = (A[q][q] - A[p][p]) / (2 * A[p][q]);
        const t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1));
        const c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (let k = 0; k < n; k++) { const akp = A[k][p], akq = A[k][q]; A[k][p] = c * akp - s * akq; A[k][q] = s * akp + c * akq; }
        for (let k = 0; k < n; k++) { const apk = A[p][k], aqk = A[q][k]; A[p][k] = c * apk - s * aqk; A[q][k] = s * apk + c * aqk; }
        for (let k = 0; k < n; k++) { const vkp = V[k][p], vkq = V[k][q]; V[k][p] = c * vkp - s * vkq; V[k][q] = s * vkp + c * vkq; }
      }
    }
    const idx = [...Array(n).keys()].sort((a, b) => A[b][b] - A[a][a]);
    return { vals: idx.map((i) => A[i][i]), vecs: V.map((r) => idx.map((i) => r[i])) };
  },
  /* 단측 야코비 SVD: A = U Σ Vᵀ (m×n 아무 모양) */
  svd(A) {
    const m = A.length, n = A[0].length;
    if (m < n) { const r = N.svd(N.T(A)); return { U: r.V, S: r.S, V: r.U }; }
    const U = N.clone(A), V = N.eye(n);
    for (let sweep = 0; sweep < 40; sweep++) {
      let rot = false;
      for (let p = 0; p < n - 1; p++) for (let q = p + 1; q < n; q++) {
        let a = 0, b = 0, g = 0;
        for (let i = 0; i < m; i++) { a += U[i][p] ** 2; b += U[i][q] ** 2; g += U[i][p] * U[i][q]; }
        if (Math.abs(g) <= 1e-13 * Math.sqrt(a * b) || Math.abs(g) < 1e-300) continue;
        rot = true;
        const z = (b - a) / (2 * g), t = Math.sign(z || 1) / (Math.abs(z) + Math.sqrt(1 + z * z));
        const c = 1 / Math.sqrt(1 + t * t), s = c * t;
        for (let i = 0; i < m; i++) { const x = U[i][p], y = U[i][q]; U[i][p] = c * x - s * y; U[i][q] = s * x + c * y; }
        for (let i = 0; i < n; i++) { const x = V[i][p], y = V[i][q]; V[i][p] = c * x - s * y; V[i][q] = s * x + c * y; }
      }
      if (!rot) break;
    }
    const S = []; for (let j = 0; j < n; j++) { let s = 0; for (let i = 0; i < m; i++) s += U[i][j] ** 2; S.push(Math.sqrt(s)); }
    const idx = [...Array(n).keys()].sort((a, b) => S[b] - S[a]);
    const Uo = U.map((r) => idx.map((j) => (S[j] > 1e-12 ? r[j] / S[j] : 0)));
    return { U: Uo, S: idx.map((j) => S[j]), V: V.map((r) => idx.map((j) => r[j])) };
  },
  /* 2×2 고윳값 (실수/복소) */
  eig2(A) {
    const [[a, b], [c, d]] = A, tr = a + d, det = a * d - b * c, disc = tr * tr - 4 * det;
    if (disc < -1e-12) return { real: false, tr, det, disc, re: tr / 2, im: Math.sqrt(-disc) / 2 };
    const s = Math.sqrt(Math.max(0, disc)), l1 = (tr + s) / 2, l2 = (tr - s) / 2;
    const vec = (l) => {
      let v = Math.abs(b) > 1e-12 || Math.abs(a - l) > 1e-12 ? [b, l - a] : [l - d, c];
      if (Math.hypot(...v) < 1e-12) v = Math.abs(l - d) + Math.abs(c) > 1e-12 ? [l - d, c] : [1, 0];
      const nn = Math.hypot(...v); return [v[0] / nn, v[1] / nn];
    };
    return { real: true, tr, det, disc, l1, l2, v1: vec(l1), v2: vec(l2) };
  },
};
LA.N = N;

/* ------------------------------------------------------------------ 분수 행렬 계산 */
const X = {
  fromN: (A) => A.map((r) => r.map((x) => f(x))),
  toN: (A) => A.map((r) => r.map((x) => x.val())),
  clone: (A) => A.map((r) => r.slice()),
  zeros: (m, n) => Array.from({ length: m }, () => Array.from({ length: n }, () => f(0))),
  eye: (n) => Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => f(i === j ? 1 : 0))),
  T: (A) => A[0].map((_, j) => A.map((r) => r[j])),
  mul: (A, B) => A.map((r) => B[0].map((_, j) => r.reduce((s, a, k) => s.add(a.mul(B[k][j])), f(0)))),
  minor: (A, i, j) => A.filter((_, r) => r !== i).map((r) => r.filter((_, c) => c !== j)),
  det(A) {
    const n = A.length; if (n === 1) return A[0][0];
    if (n === 2) return A[0][0].mul(A[1][1]).sub(A[0][1].mul(A[1][0]));
    let s = f(0); for (let j = 0; j < n; j++) { if (A[0][j].isZero()) continue; const t = A[0][j].mul(X.det(X.minor(A, 0, j))); s = j % 2 ? s.sub(t) : s.add(t); }
    return s;
  },
  /* 가우스-조르당 소거를 단계별로 기록. nc = 계수 열의 개수(첨가 행렬이면 마지막 열 제외) */
  rref(A0, nc, o = {}) {
    const A = X.clone(A0), m = A.length, n = A[0].length; nc = nc ?? n;
    const steps = [{ M: X.clone(A), op: null, phase: '시작' }];
    const pivots = []; let row = 0;
    const R = (i) => `<i class="var">R</i><sub>${i + 1}</sub>`;
    const rec = (op, desc, detail, phase, piv) => steps.push({ M: X.clone(A), op, desc, detail, phase, piv });
    for (let c = 0; c < nc && row < m; c++) {
      let p = -1; for (let r = row; r < m; r++) if (!A[r][c].isZero()) { p = r; break; }
      if (p < 0) continue;
      if (p !== row) {
        [A[p], A[row]] = [A[row], A[p]];
        rec({ type: 'swap', i: row, j: p }, `${R(row)} ↔ ${R(p)}`, `${c + 1}열의 ${row + 1}행 자리가 0이라서, 아래쪽에서 0이 아닌 행(${p + 1}행)과 자리를 바꿉니다.`, '전진 소거', [row, c]);
      }
      const piv = A[row][c];
      if (!piv.isOne() && o.normalizeFirst !== false) {
        const before = A[row].slice(); const k = piv.inv();
        A[row] = A[row].map((x) => x.mul(k));
        const det = before.map((x, j) => `<span class="ln">${LA.v('a', `${row + 1}${j + 1}`)} : ${par(x)} × ${par(k)} = <b>${A[row][j].html()}</b></span>`).join('');
        rec({ type: 'scale', i: row, k }, `${R(row)} ← ${k.html()} · ${R(row)}`, `피벗 ${piv.html()}을(를) 1로 만들기 위해 ${row + 1}행 전체에 ${k.html()}을(를) 곱합니다.<div class="lines">${det}</div>`, '전진 소거', [row, c]);
      }
      for (let r = row + 1; r < m; r++) {
        if (A[r][c].isZero()) continue;
        const k = A[r][c].div(A[row][c]).neg(); const before = A[r].slice();
        A[r] = A[r].map((x, j) => x.add(k.mul(A[row][j])));
        const det = before.map((x, j) => `<span class="ln">${LA.v('a', `${r + 1}${j + 1}`)} : ${fh(x)} + ${par(k)}·${par(A[row][j])} = <b>${A[r][j].html()}</b></span>`).join('');
        rec({ type: 'add', i: r, j: row, k }, `${R(r)} ← ${R(r)} ${k.sign() < 0 ? MINUS : '+'} ${k.abs().isOne() ? '' : k.abs().html() + '·'}${R(row)}`, `${r + 1}행 ${c + 1}열을 0으로 만들기: 배수 = −(${fh(before[c])})/(${fh(A[row][c])}) = ${k.html()}<div class="lines">${det}</div>`, '전진 소거', [row, c]);
      }
      pivots.push([row, c]); row++;
    }
    if (o.full !== false) {
      for (let t = pivots.length - 1; t >= 0; t--) {
        const [pr, pc] = pivots[t];
        if (!A[pr][pc].isOne()) {
          const k = A[pr][pc].inv(); const before = A[pr].slice();
          A[pr] = A[pr].map((x) => x.mul(k));
          const det = before.map((x, j) => `<span class="ln">${LA.v('a', `${pr + 1}${j + 1}`)} : ${par(x)} × ${par(k)} = <b>${A[pr][j].html()}</b></span>`).join('');
          rec({ type: 'scale', i: pr, k }, `${R(pr)} ← ${k.html()} · ${R(pr)}`, `피벗을 1로 만듭니다.<div class="lines">${det}</div>`, '후진 소거', [pr, pc]);
        }
        for (let r = pr - 1; r >= 0; r--) {
          if (A[r][pc].isZero()) continue;
          const k = A[r][pc].neg(); const before = A[r].slice();
          A[r] = A[r].map((x, j) => x.add(k.mul(A[pr][j])));
          const det = before.map((x, j) => `<span class="ln">${LA.v('a', `${r + 1}${j + 1}`)} : ${fh(x)} + ${par(k)}·${par(A[pr][j])} = <b>${A[r][j].html()}</b></span>`).join('');
          rec({ type: 'add', i: r, j: pr, k }, `${R(r)} ← ${R(r)} ${k.sign() < 0 ? MINUS : '+'} ${k.abs().isOne() ? '' : k.abs().html() + '·'}${R(pr)}`, `피벗 위쪽(${r + 1}행 ${pc + 1}열)을 0으로 만듭니다. 배수 = ${k.html()}<div class="lines">${det}</div>`, '후진 소거', [pr, pc]);
        }
      }
    }
    return { steps, R: A, pivots, rank: pivots.length };
  },
  /* 영공간 기저 (RREF에서 자유변수로) */
  nullBasis(Rm, pivots, n) {
    const pc = pivots.map((p) => p[1]); const free = [...Array(n).keys()].filter((j) => !pc.includes(j));
    return free.map((fj) => {
      const v = Array.from({ length: n }, () => f(0)); v[fj] = f(1);
      pivots.forEach(([r, c]) => { v[c] = Rm[r][fj].neg(); });
      return { free: fj, v };
    });
  },
};
LA.X = X;

/* ------------------------------------------------------------------ DOM 헬퍼 */
LA.$ = (s, r = document) => r.querySelector(s);
LA.$$ = (s, r = document) => [...r.querySelectorAll(s)];
LA.html = (host, h) => { host.innerHTML = h; return host; };

/* 행렬 렌더링. A의 원소는 F | number | string(이미 HTML) */
function mat(A, o = {}) {
  const m = A.length, n = m ? A[0].length : 0;
  let cells = '';
  for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) {
    const v = A[i][j]; const cls = ['c'];
    if (o.aug != null && j === o.aug) cls.push('aug');
    if (o.cell) { const c = o.cell(i, j); if (c) cls.push(c); }
    const sep = (m > 9 || n > 9) ? ',' : '';
    const sub = o.sub ? `<span class="ix">${o.sub}<sub>${i + 1}${sep}${j + 1}</sub></span>` : '';
    const val = typeof v === 'string' ? v : fh(v, o.digits ?? 2);
    cells += `<span class="${cls.join(' ')}" data-i="${i}" data-j="${j}">${sub}<span class="v">${val}</span></span>`;
  }
  const name = o.name ? `<span class="mxname">${o.name}</span>${o.noeq ? '' : '<span class="mxeq">=</span>'}` : '';
  return `<span class="mxw ${o.cls || ''}"${o.id ? ` id="${o.id}"` : ''}>${name}<span class="mx${o.sub ? ' has-ix' : ''}${o.det ? ' det' : ''}" style="grid-template-columns:repeat(${n},auto)">${cells}</span>${o.after || ''}</span>`;
}
LA.mat = mat;
LA.col = (v, o) => mat(v.map((x) => [x]), o);

/* 편집 가능한 행렬 */
let edSeq = 0;
function editor(host, A, onChange, o = {}) {
  const key = o.key || 'ed' + (++edSeq);
  const st = { A };
  function draw() {
    const m = st.A.length, n = st.A[0].length;
    let h = `<div class="ed">${o.name ? `<span class="mxname">${o.name}</span><span class="mxeq">=</span>` : ''}<span class="mx edmx" style="grid-template-columns:repeat(${n},auto)">`;
    for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) {
      h += `<input class="c${o.aug != null && j === n - 1 ? ' aug' : ''}" id="${key}-${i}-${j}" data-i="${i}" data-j="${j}" value="${st.A[i][j].toString().replace('-', '−')}" inputmode="text" autocomplete="off" spellcheck="false" aria-label="${o.sym || 'a'} ${i + 1}행 ${j + 1}열">`;
    }
    h += '</span></div>';
    let tools = '';
    if (o.resize) {
      const z = o.resize;
      if (z.square) tools += `<span class="sz">크기 <button type="button" data-a="n-" aria-label="작게">−</button><b>${m}×${n}</b><button type="button" data-a="n+" aria-label="크게">+</button></span>`;
      else {
        if (z.rows !== false) tools += `<span class="sz">행 <button type="button" data-a="r-" aria-label="행 줄이기">−</button><b>${m}</b><button type="button" data-a="r+" aria-label="행 늘리기">+</button></span>`;
        if (z.cols !== false) tools += `<span class="sz">열 <button type="button" data-a="c-" aria-label="열 줄이기">−</button><b>${n}</b><button type="button" data-a="c+" aria-label="열 늘리기">+</button></span>`;
      }
    }
    if (o.presets) tools += `<span class="presets">${o.presets.map((p, k) => `<button type="button" class="chip" data-p="${k}">${p.name}</button>`).join('')}</span>`;
    tools += `<button type="button" class="chip ghost" data-a="rand">무작위</button>`;
    host.innerHTML = `<div class="edwrap">${h}<div class="edtools">${tools}</div><p class="hint">칸을 눌러 숫자를 바꾸세요. 분수는 <code>3/4</code>처럼.</p></div>`;
  }
  host.addEventListener('input', (e) => {
    const t = e.target; if (!t.dataset || t.dataset.i == null) return;
    const v = F.parse(t.value);
    if (!v) { t.classList.add('bad'); return; }
    t.classList.remove('bad'); st.A[+t.dataset.i][+t.dataset.j] = v; onChange(st.A);
  });
  host.addEventListener('focusin', (e) => { if (e.target.tagName === 'INPUT') e.target.select(); });
  host.addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return;
    const z = o.resize || {}; let A = st.A; const m = A.length, n = A[0].length;
    const a = b.dataset.a;
    if (b.dataset.p != null) A = X.clone(o.presets[+b.dataset.p].A.map((r) => r.map((x) => f(x))));
    else if (a === 'rand') { const lo = o.randRange || 4; A = A.map((r, i) => r.map(() => f(Math.floor(Math.random() * (2 * lo + 1)) - lo))); if (o.randFix) A = o.randFix(A); }
    else if (a === 'n+' && m < (z.max || 4)) { A = A.map((r) => [...r, f(0)]); A.push(Array.from({ length: n + 1 }, (_, j) => f(j === n ? 1 : 0))); }
    else if (a === 'n-' && m > (z.min || 2)) { A = A.slice(0, -1).map((r) => r.slice(0, -1)); }
    else if (a === 'r+' && m < (z.maxR || 5)) A.push(Array.from({ length: n }, () => f(0)));
    else if (a === 'r-' && m > (z.minR || 1)) A.pop();
    else if (a === 'c+' && n < (z.maxC || 5)) A.forEach((r) => (o.aug ? r.splice(n - 1, 0, f(0)) : r.push(f(0))));
    else if (a === 'c-' && n > (z.minC || 1)) A.forEach((r) => (o.aug ? r.splice(n - 2, 1) : r.pop()));
    else return;
    st.A = A; draw(); onChange(st.A);
  });
  draw();
  return { get A() { return st.A; }, set(B) { st.A = B; draw(); onChange(B); }, redraw: draw };
}
LA.editor = editor;

/* 슬라이더 묶음 */
LA.slider = (id, label, min, max, step, val) =>
  `<label class="sl" for="${id}"><span class="sl-l">${label}</span><input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${val}"><output id="${id}-o">${fmt(val)}</output></label>`;
LA.bindSliders = (root, ids, cb) => {
  ids.forEach((id) => {
    const inp = root.querySelector('#' + id); const out = root.querySelector('#' + id + '-o');
    inp.addEventListener('input', () => { if (out) out.textContent = fmt(+inp.value); cb(); });
  });
  return () => Object.fromEntries(ids.map((id) => [id, +root.querySelector('#' + id).value]));
};

/* ------------------------------------------------------------------ 생명주기 */
const live = { planes: new Set(), timers: new Set(), rafs: new Set() };
LA.live = live;
LA.cleanup = () => {
  live.planes.forEach((p) => p.destroy()); live.planes.clear();
  live.timers.forEach((t) => clearInterval(t)); live.timers.clear();
  live.rafs.forEach((r) => (r.stop = true)); live.rafs.clear();
};
LA.every = (ms, fn) => { const t = setInterval(fn, ms); live.timers.add(t); return () => { clearInterval(t); live.timers.delete(t); }; };
const reduceMotion = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
LA.reduceMotion = reduceMotion;
/* 0→1 트윈 */
LA.tween = (ms, fn, done) => {
  const h = { stop: false }; live.rafs.add(h);
  if (reduceMotion()) { fn(1); done && done(); return h; }
  const t0 = performance.now();
  const step = (t) => {
    if (h.stop) return;
    const u = Math.min(1, (t - t0) / ms); fn(u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2);
    if (u < 1) requestAnimationFrame(step); else { live.rafs.delete(h); done && done(); }
  };
  requestAnimationFrame(step); return h;
};
LA.loop = (fn) => {
  const h = { stop: false }; live.rafs.add(h); let t0 = null;
  const step = (t) => { if (h.stop) return; if (t0 == null) t0 = t; fn((t - t0) / 1000); requestAnimationFrame(step); };
  requestAnimationFrame(step); return h;
};

/* ------------------------------------------------------------------ 색 */
let colorCache = null;
function col(name) {
  if (!colorCache) colorCache = {};
  if (!(name in colorCache)) colorCache[name] = getComputedStyle(document.documentElement).getPropertyValue('--' + name).trim() || '#888';
  return colorCache[name];
}
LA.color = col;
function rerenderAll() { colorCache = null; live.planes.forEach((p) => p.render()); }
if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rerenderAll);
new MutationObserver(rerenderAll).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class'] });
function alpha(c, a) {
  if (c.startsWith('#')) {
    let h = c.slice(1); if (h.length === 3) h = h.split('').map((x) => x + x).join('');
    const n = parseInt(h, 16); return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }
  return c;
}
LA.alpha = alpha;

/* ------------------------------------------------------------------ 2D 평면 */
class Plane {
  constructor(host, o = {}) {
    this.o = Object.assign({ range: 5, aspect: 1, snap: 0.5, grid: true, labels: true, center: [0, 0] }, o);
    this.host = host;
    this.cv = document.createElement('canvas'); this.cv.className = 'plane';
    this.cv.setAttribute('role', 'img'); this.cv.setAttribute('aria-label', o.aria || '좌표평면 그림');
    host.appendChild(this.cv);
    this.ctx = this.cv.getContext('2d'); this.handles = []; this.draw = () => {}; this.onchange = null;
    this.drag = null;
    this.ro = new ResizeObserver(() => this.resize()); this.ro.observe(host);
    const pos = (e) => { const r = this.cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    this.cv.addEventListener('pointerdown', (e) => {
      const [x, y] = pos(e); const h = this.pick(x, y, e.pointerType === 'touch' ? 26 : 14);
      if (h) { this.drag = h; this.cv.setPointerCapture(e.pointerId); e.preventDefault(); }
    });
    this.cv.addEventListener('pointermove', (e) => {
      const [x, y] = pos(e);
      if (this.drag) {
        let w = this.toW(x, y); const s = this.drag.snap ?? this.o.snap;
        if (s) w = w.map((t) => Math.round(t / s) * s);
        const R = this.o.range * 1.4; w = w.map((t) => Math.max(-R, Math.min(R, t)));
        this.drag.set(w); this.changed();
      } else this.cv.style.cursor = this.pick(x, y, 14) ? 'grab' : '';
    });
    const end = () => { this.drag = null; };
    this.cv.addEventListener('pointerup', end); this.cv.addEventListener('pointercancel', end);
    live.planes.add(this);
  }
  destroy() { this.ro.disconnect(); }
  pick(x, y, r) {
    let best = null, bd = r;
    for (const h of this.handles) { if (h.hidden && h.hidden()) continue; const [sx, sy] = this.toS(h.get()); const d = Math.hypot(sx - x, sy - y); if (d < bd) { bd = d; best = h; } }
    return best;
  }
  handle(h) { this.handles.push(h); this.cv.style.touchAction = 'none'; return this; }
  changed() { this.onchange && this.onchange(); this.render(); }
  resize() {
    const w = this.host.clientWidth; if (!w) return;
    const h = Math.round(w * this.o.aspect), d = window.devicePixelRatio || 1;
    this.cv.width = Math.round(w * d); this.cv.height = Math.round(h * d); this.cv.style.height = h + 'px';
    this.W = w; this.H = h; this.ctx.setTransform(d, 0, 0, d, 0, 0);
    this.s = w / (2 * this.o.range); this.render();
  }
  toS(p) { return [this.W / 2 + (p[0] - this.o.center[0]) * this.s, this.H / 2 - (p[1] - this.o.center[1]) * this.s]; }
  toW(x, y) { return [(x - this.W / 2) / this.s + this.o.center[0], -(y - this.H / 2) / this.s + this.o.center[1]]; }
  render() {
    if (!this.W) return; const c = this.ctx;
    c.clearRect(0, 0, this.W, this.H); c.fillStyle = col('canvas'); c.fillRect(0, 0, this.W, this.H);
    if (this.o.grid) this.baseGrid();
    c.save(); this.draw(this); c.restore();
    for (const h of this.handles) {
      if (h.hidden && h.hidden()) continue;
      const [x, y] = this.toS(h.get());
      c.beginPath(); c.arc(x, y, 7, 0, 7); c.fillStyle = col('canvas'); c.fill();
      c.lineWidth = 2.5; c.strokeStyle = h.color ? col(h.color) : col('ink'); c.stroke();
    }
  }
  baseGrid() {
    const c = this.ctx, R = this.o.range, cy = this.o.center[1], cx = this.o.center[0];
    const yr = R * this.o.aspect;
    c.lineWidth = 1; c.strokeStyle = col('grid');
    c.beginPath();
    for (let x = Math.ceil(cx - R); x <= cx + R; x++) { const [sx] = this.toS([x, 0]); c.moveTo(Math.round(sx) + 0.5, 0); c.lineTo(Math.round(sx) + 0.5, this.H); }
    for (let y = Math.ceil(cy - yr); y <= cy + yr; y++) { const [, sy] = this.toS([0, y]); c.moveTo(0, Math.round(sy) + 0.5); c.lineTo(this.W, Math.round(sy) + 0.5); }
    c.stroke();
    c.strokeStyle = col('axis'); c.lineWidth = 1.25; c.beginPath();
    const [ox, oy] = this.toS([0, 0]); c.moveTo(0, oy); c.lineTo(this.W, oy); c.moveTo(ox, 0); c.lineTo(ox, this.H); c.stroke();
    if (this.o.labels) {
      c.fillStyle = col('muted'); c.font = '10px "JetBrains Mono", monospace'; c.textAlign = 'center'; c.textBaseline = 'top';
      const stepL = R > 7 ? 2 : 1;
      for (let x = Math.ceil(cx - R); x <= cx + R; x++) if (x && x % stepL === 0) { const [sx] = this.toS([x, 0]); c.fillText(fmt(x), sx, oy + 3); }
      c.textAlign = 'right'; c.textBaseline = 'middle';
      for (let y = Math.ceil(cy - yr); y <= cy + yr; y++) if (y && y % stepL === 0) { const [, sy] = this.toS([0, y]); c.fillText(fmt(y), ox - 4, sy); }
    }
  }
  /* 변환된 격자: A의 열벡터로 만든 격자선 */
  tgrid(A, color = 'accent', a = 0.35, extent) {
    const c1 = [A[0][0], A[1][0]], c2 = [A[0][1], A[1][1]], K = extent || Math.ceil(this.o.range * 2.5);
    const c = this.ctx; c.save(); c.globalAlpha = a;
    for (let k = -K; k <= K; k++) {
      this.infLine(N.vs(c1, k), c2, color, k === 0 ? 2 : 1);
      this.infLine(N.vs(c2, k), c1, color, k === 0 ? 2 : 1);
    }
    c.restore();
  }
  infLine(p, d, color, w = 1.5, dash) {
    const L = Math.hypot(...d); if (L < 1e-9) return;
    const t = (this.o.range * 4) / L;
    this.seg([p[0] - d[0] * t, p[1] - d[1] * t], [p[0] + d[0] * t, p[1] + d[1] * t], color, { w, dash });
  }
  seg(a, b, color = 'ink', o = {}) {
    const c = this.ctx, [x1, y1] = this.toS(a), [x2, y2] = this.toS(b);
    c.save(); c.strokeStyle = col(color); c.lineWidth = o.w || 1.5; if (o.alpha != null) c.globalAlpha = o.alpha;
    if (o.dash) c.setLineDash(o.dash === true ? [5, 4] : o.dash);
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke(); c.restore();
  }
  arrow(a, b, color = 'ink', o = {}) {
    const c = this.ctx, [x1, y1] = this.toS(a), [x2, y2] = this.toS(b);
    const L = Math.hypot(x2 - x1, y2 - y1);
    c.save(); c.strokeStyle = c.fillStyle = col(color); c.lineWidth = o.w || 2.5; if (o.alpha != null) c.globalAlpha = o.alpha;
    if (o.dash) c.setLineDash([6, 4]);
    if (L < 1) { c.beginPath(); c.arc(x1, y1, 3, 0, 7); c.fill(); c.restore(); return; }
    const ux = (x2 - x1) / L, uy = (y2 - y1) / L, hs = Math.min(11, L * 0.4);
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2 - ux * hs * 0.8, y2 - uy * hs * 0.8); c.stroke(); c.setLineDash([]);
    c.beginPath(); c.moveTo(x2, y2); c.lineTo(x2 - ux * hs - uy * hs * 0.45, y2 - uy * hs + ux * hs * 0.45); c.lineTo(x2 - ux * hs + uy * hs * 0.45, y2 - uy * hs - ux * hs * 0.45); c.closePath(); c.fill();
    if (o.label) this.textS(x2 + ux * 10 + (o.dx || 0), y2 + uy * 10 + (o.dy || 0), o.label, color, o.font);
    c.restore();
  }
  poly(pts, fill, stroke, o = {}) {
    const c = this.ctx; c.save(); c.beginPath();
    pts.forEach((p, i) => { const [x, y] = this.toS(p); i ? c.lineTo(x, y) : c.moveTo(x, y); }); c.closePath();
    if (fill) { c.fillStyle = alpha(col(fill), o.a ?? 0.18); c.fill(); }
    if (stroke) { c.strokeStyle = col(stroke); c.lineWidth = o.w || 1.5; if (o.dash) c.setLineDash([5, 4]); c.stroke(); }
    c.restore();
  }
  dot(p, color = 'ink', r = 4, o = {}) {
    const c = this.ctx, [x, y] = this.toS(p); c.save(); c.beginPath(); c.arc(x, y, r, 0, 7);
    if (o.hollow) { c.lineWidth = 2; c.strokeStyle = col(color); c.fillStyle = col('canvas'); c.fill(); c.stroke(); }
    else { c.fillStyle = col(color); c.fill(); }
    c.restore();
  }
  text(p, s, color = 'ink', dx = 8, dy = -8, font) { const [x, y] = this.toS(p); this.textS(x + dx, y + dy, s, color, font); }
  textS(x, y, s, color = 'ink', font) {
    const c = this.ctx; c.save(); c.font = font || '600 13px "IBM Plex Sans KR", sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.lineWidth = 3.5; c.strokeStyle = col('canvas'); c.strokeText(s, x, y); c.fillStyle = col(color); c.fillText(s, x, y); c.restore();
  }
  path(fn, n, color, o = {}) {
    const c = this.ctx; c.save(); c.beginPath();
    for (let i = 0; i <= n; i++) { const [x, y] = this.toS(fn(i / n)); i ? c.lineTo(x, y) : c.moveTo(x, y); }
    if (o.fill) { c.fillStyle = alpha(col(o.fill), o.a ?? 0.15); c.fill(); }
    c.strokeStyle = col(color); c.lineWidth = o.w || 2; if (o.dash) c.setLineDash([5, 4]); c.stroke(); c.restore();
  }
  /* 단위원의 A 상 */
  ellipse(A, color, o) { this.path((t) => N.mv(A, [Math.cos(t * 2 * Math.PI), Math.sin(t * 2 * Math.PI)]), 96, color, o); }
}
LA.Plane = Plane;

/* ------------------------------------------------------------------ 3D 뷰 */
class View3D {
  constructor(host, o = {}) {
    this.o = Object.assign({ range: 4, aspect: 0.85 }, o);
    this.host = host; this.yaw = o.yaw ?? 0.6; this.pitch = o.pitch ?? 0.38;
    this.cv = document.createElement('canvas'); this.cv.className = 'plane view3d';
    this.cv.setAttribute('role', 'img'); this.cv.setAttribute('aria-label', o.aria || '3차원 공간 그림 — 끌어서 회전');
    host.appendChild(this.cv); this.ctx = this.cv.getContext('2d'); this.draw = () => {};
    this.ro = new ResizeObserver(() => this.resize()); this.ro.observe(host);
    let last = null;
    this.cv.style.touchAction = 'none';
    this.cv.addEventListener('pointerdown', (e) => { last = [e.clientX, e.clientY]; this.cv.setPointerCapture(e.pointerId); });
    this.cv.addEventListener('pointermove', (e) => {
      if (!last) return; this.yaw -= (e.clientX - last[0]) * 0.008; this.pitch = Math.max(-1.45, Math.min(1.45, this.pitch + (e.clientY - last[1]) * 0.008));
      last = [e.clientX, e.clientY]; this.render();
    });
    const end = () => (last = null); this.cv.addEventListener('pointerup', end); this.cv.addEventListener('pointercancel', end);
    live.planes.add(this);
  }
  destroy() { this.ro.disconnect(); }
  resize() {
    const w = this.host.clientWidth; if (!w) return; const h = Math.round(w * this.o.aspect), d = devicePixelRatio || 1;
    this.cv.width = Math.round(w * d); this.cv.height = Math.round(h * d); this.cv.style.height = h + 'px';
    this.W = w; this.H = h; this.ctx.setTransform(d, 0, 0, d, 0, 0); this.s = Math.min(w, h * 1.2) / (2.3 * this.o.range); this.render();
  }
  P(p) {
    const [x, y, z] = p, cy = Math.cos(this.yaw), sy = Math.sin(this.yaw);
    const x1 = x * cy - y * sy, y1 = x * sy + y * cy, cp = Math.cos(this.pitch), sp = Math.sin(this.pitch);
    const up = z * cp + y1 * sp;
    return [this.W / 2 + x1 * this.s, this.H / 2 - up * this.s];
  }
  render() {
    if (!this.W) return; const c = this.ctx;
    c.clearRect(0, 0, this.W, this.H); c.fillStyle = col('canvas'); c.fillRect(0, 0, this.W, this.H);
    this.floor(); c.save(); this.draw(this); c.restore();
  }
  floor() {
    const R = this.o.range; for (let k = -R; k <= R; k++) { this.seg([k, -R, 0], [k, R, 0], 'grid', { w: 1 }); this.seg([-R, k, 0], [R, k, 0], 'grid', { w: 1 }); }
    const L = R + 0.6;
    [['x', [L, 0, 0]], ['y', [0, L, 0]], ['z', [0, 0, L]]].forEach(([n, e]) => { this.seg(N.vs(e, -1), e, 'axis', { w: 1.25 }); this.text(e, n, 'muted', 0, 0, '500 12px "JetBrains Mono", monospace'); });
  }
  seg(a, b, color = 'ink', o = {}) {
    const c = this.ctx, [x1, y1] = this.P(a), [x2, y2] = this.P(b); c.save(); c.strokeStyle = col(color); c.lineWidth = o.w || 1.5;
    if (o.alpha != null) c.globalAlpha = o.alpha; if (o.dash) c.setLineDash([5, 4]);
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke(); c.restore();
  }
  arrow(a, b, color = 'ink', o = {}) {
    const c = this.ctx, [x1, y1] = this.P(a), [x2, y2] = this.P(b), L = Math.hypot(x2 - x1, y2 - y1);
    c.save(); c.strokeStyle = c.fillStyle = col(color); c.lineWidth = o.w || 2.5; if (o.alpha != null) c.globalAlpha = o.alpha; if (o.dash) c.setLineDash([6, 4]);
    if (L < 1) { c.beginPath(); c.arc(x1, y1, 3, 0, 7); c.fill(); c.restore(); return; }
    const ux = (x2 - x1) / L, uy = (y2 - y1) / L, hs = Math.min(11, L * 0.4);
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2 - ux * hs * 0.8, y2 - uy * hs * 0.8); c.stroke(); c.setLineDash([]);
    c.beginPath(); c.moveTo(x2, y2); c.lineTo(x2 - ux * hs - uy * hs * 0.45, y2 - uy * hs + ux * hs * 0.45); c.lineTo(x2 - ux * hs + uy * hs * 0.45, y2 - uy * hs - ux * hs * 0.45); c.closePath(); c.fill();
    c.restore();
    if (o.label) this.textS(x2 + ux * 12, y2 + uy * 12, o.label, color);
  }
  poly(pts, fill, stroke, o = {}) {
    const c = this.ctx; c.save(); c.beginPath(); pts.forEach((p, i) => { const [x, y] = this.P(p); i ? c.lineTo(x, y) : c.moveTo(x, y); }); c.closePath();
    if (fill) { c.fillStyle = alpha(col(fill), o.a ?? 0.15); c.fill(); }
    if (stroke) { c.strokeStyle = col(stroke); c.lineWidth = o.w || 1; if (o.dash) c.setLineDash([4, 4]); c.stroke(); }
    c.restore();
  }
  /* 원점을 지나는 두 벡터 u,v가 만드는 평면 조각 */
  planePatch(u, v, color, ext = 1.6) {
    const nu = N.norm(u) || 1, nv = N.norm(v) || 1, R = this.o.range * 0.8;
    const a = N.vs(u, R / nu * ext * 0.6), b = N.vs(v, R / nv * ext * 0.6);
    this.poly([N.vadd(a, b), N.vsub(a, b), N.vs(N.vadd(a, b), -1), N.vsub(b, a)], color, color, { a: 0.12, w: 0.8 });
  }
  dot(p, color = 'ink', r = 4) { const c = this.ctx, [x, y] = this.P(p); c.save(); c.beginPath(); c.arc(x, y, r, 0, 7); c.fillStyle = col(color); c.fill(); c.restore(); }
  text(p, s, color = 'ink', dx = 8, dy = -8, font) { const [x, y] = this.P(p); this.textS(x + dx, y + dy, s, color, font); }
  textS(x, y, s, color, font) { Plane.prototype.textS.call(this, x, y, s, color, font); }
}
LA.View3D = View3D;

/* ------------------------------------------------------------------ 단계 재생기 */
LA.stepper = (host, n, on, o = {}) => {
  host.innerHTML = `<div class="stepper" role="group" aria-label="단계 이동">
    <button type="button" data-s="first" aria-label="처음 단계로">⇤</button>
    <button type="button" data-s="prev">← 이전</button>
    <span class="stepcount" aria-live="polite"></span>
    <button type="button" data-s="next" class="primary">다음 →</button>
    <button type="button" data-s="play" class="ghost">▶ 자동 재생</button></div>`;
  let k = 0, stop = null;
  const cnt = host.querySelector('.stepcount'), playB = host.querySelector('[data-s=play]');
  const go = (x) => { k = Math.max(0, Math.min(n - 1, x)); cnt.textContent = `${k} / ${n - 1}단계`; on(k); };
  const halt = () => { if (stop) { stop(); stop = null; playB.textContent = '▶ 자동 재생'; } };
  host.addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return;
    const s = b.dataset.s;
    if (s === 'first') { halt(); go(0); } else if (s === 'prev') { halt(); go(k - 1); } else if (s === 'next') { halt(); go(k + 1); }
    else if (s === 'play') {
      if (stop) return halt();
      if (k >= n - 1) go(0);
      playB.textContent = '❚❚ 멈춤';
      stop = LA.every(o.ms || 1500, () => { if (k >= n - 1) halt(); else go(k + 1); });
    }
  });
  go(o.start || 0);
  return { go, get k() { return k; }, reset(m) { halt(); n = m; go(0); } };
};

/* 탭 */
LA.tabs = (host, names, on) => {
  host.innerHTML = `<div class="tabs" role="tablist">${names.map((n, i) => `<button type="button" role="tab" data-t="${i}" aria-selected="${i === 0}">${n}</button>`).join('')}</div>`;
  host.addEventListener('click', (e) => {
    const b = e.target.closest('[data-t]'); if (!b) return;
    host.querySelectorAll('[data-t]').forEach((x) => x.setAttribute('aria-selected', x === b)); on(+b.dataset.t);
  });
  on(0);
};

/* 섹션 등록 */
LA.chapter = (no, title, en) => LA.chapters.push({ no, title, en });
LA.section = (s) => LA.sections.push(s);
})();
