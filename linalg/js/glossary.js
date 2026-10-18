/* 용어집: [한국어, English, 장] — 본문의 첫 등장 위치에 영어를 붙이고, 용어집 페이지를 만든다 */
(function () {
'use strict';
LA.GLOSS = [
  ['선형연립방정식', 'system of linear equations', 1], ['연립방정식', 'system of equations', 1], ['첨가행렬', 'augmented matrix', 1],
  ['기본 행 연산', 'elementary row operations', 1], ['가우스 소거법', 'Gaussian elimination', 1], ['가우스-조르당 소거', 'Gauss–Jordan elimination', 1],
  ['계단 모양', 'row echelon form', 1], ['RREF', 'reduced row echelon form', 1], ['피벗', 'pivot', 1], ['자유변수', 'free variable', 1],
  ['전진 소거', 'forward elimination', 1], ['후진 소거', 'backward elimination', 1], ['행렬', 'matrix', 1], ['성분', 'entry', 1],
  ['전치행렬', 'transpose', 1], ['전치', 'transpose', 1], ['단위행렬', 'identity matrix', 1], ['역행렬', 'inverse matrix', 1],
  ['비가역', 'noninvertible', 1], ['가역', 'invertible', 1], ['특이행렬', 'singular matrix', 1], ['스칼라배', 'scalar multiplication', 1], ['스칼라', 'scalar', 1],
  ['행렬식', 'determinant', 2], ['소행렬식', 'minor', 2], ['여인수 전개', 'cofactor expansion', 2], ['여인수', 'cofactor', 2],
  ['크래머 공식', "Cramer's rule", 2], ['층밀림', 'shear', 2], ['위삼각행렬', 'upper triangular matrix', 2], ['삼각행렬', 'triangular matrix', 2],
  ['대각행렬', 'diagonal matrix', 2], ['대각성분', 'diagonal entries', 2], ['평행사변형', 'parallelogram', 2], ['평행육면체', 'parallelepiped', 2], ['순열', 'permutation', 2],
  ['벡터 공간', 'vector space', 3], ['부분공간', 'subspace', 3], ['공리', 'axiom', 3], ['영벡터', 'zero vector', 3], ['일차결합', 'linear combination', 3],
  ['일차독립', 'linearly independent', 3], ['일차종속', 'linearly dependent', 3], ['생성', 'span', 3], ['표준 기저', 'standard basis', 3], ['기저', 'basis', 3],
  ['차원', 'dimension', 3], ['좌표', 'coordinates', 3], ['행공간', 'row space', 3], ['열공간', 'column space', 3], ['영공간', 'null space', 3],
  ['랭크-널리티 정리', 'rank–nullity theorem', 3], ['랭크', 'rank', 3], ['널리티', 'nullity', 3], ['내적 공간', 'inner product space', 6], ['내적', 'dot product (inner product)', 3],
  ['정사영', 'orthogonal projection', 3], ['외적', 'cross product', 3], ['닫힘', 'closure', 3], ['교환법칙', 'commutative law', 3], ['결합법칙', 'associative law', 3], ['분배법칙', 'distributive law', 3],
  ['선형 변환', 'linear transformation', 4], ['선형성', 'linearity', 4], ['커널', 'kernel', 4], ['상공간', 'range (image)', 4], ['치역', 'range', 4],
  ['표준 행렬', 'standard matrix', 4], ['행렬 표현', 'matrix representation', 4], ['기저 변환', 'change of basis', 4], ['전이행렬', 'transition matrix', 4],
  ['닮음 행렬', 'similar matrices', 4], ['닮음', 'similarity', 4], ['대각합', 'trace', 4], ['불변량', 'invariant', 4], ['평행이동', 'translation', 4],
  ['고윳값', 'eigenvalue', 5], ['고유벡터', 'eigenvector', 5], ['고유공간', 'eigenspace', 5], ['특성방정식', 'characteristic equation', 5], ['특성다항식', 'characteristic polynomial', 5],
  ['대각화', 'diagonalization', 5], ['대수적 중복도', 'algebraic multiplicity', 5], ['기하적 중복도', 'geometric multiplicity', 5], ['판별식', 'discriminant', 5], ['주소행렬식', 'principal minor', 5],
  ['직교 기저', 'orthogonal basis', 6], ['정규직교 기저', 'orthonormal basis', 6], ['정규직교', 'orthonormal', 6], ['직교행렬', 'orthogonal matrix', 6], ['직교', 'orthogonal', 6],
  ['수직', 'perpendicular', 6], ['정규화', 'normalization', 6], ['그람-슈미트 과정', 'Gram–Schmidt process', 6], ['QR 분해', 'QR decomposition', 6],
  ['최소제곱법', 'least squares', 6], ['정규방정식', 'normal equations', 6], ['오차제곱합', 'sum of squared errors', 6], ['오차의 제곱합', 'sum of squared errors', 6], ['피타고라스', 'Pythagorean theorem', 6],
  ['대칭행렬', 'symmetric matrix', 7], ['직교 대각화', 'orthogonal diagonalization', 7], ['주축 정리', 'principal axes theorem', 7], ['주축', 'principal axes', 7],
  ['스펙트럼 정리', 'spectral theorem', 7], ['스펙트럼 분해', 'spectral decomposition', 7], ['특이값 분해', 'singular value decomposition', 7], ['특이값', 'singular value', 7],
  ['저랭크 근사', 'low-rank approximation', 7], ['이차 형식', 'quadratic form', 7], ['양의 정부호', 'positive definite', 7], ['음의 정부호', 'negative definite', 7],
  ['부정부호', 'indefinite', 7], ['준정부호', 'semidefinite', 7], ['교차항', 'cross term', 7], ['단위원', 'unit circle', 7], ['등고선', 'contour (level curve)', 7],
];
const MAP = new Map(LA.GLOSS.map(([k, e]) => [k, e]));
const terms = [...MAP.keys()].sort((a, b) => b.length - a.length);
const RE = new RegExp(terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'g');
const RT = new RegExp(RE.source);
const SKIP = 'script,style,button,input,select,option,textarea,canvas,h1,.eyebrow,.pager,.tabs,.calc,.math,.mx,.mxw,.en-term,.sl,.legend,.lines,.chip,code';
let used = new Set();
LA.resetGloss = () => { used = new Set(); };
/* root 안의 텍스트에서 아직 안 붙인 용어의 첫 등장 뒤에 (English)를 붙인다 */
LA.annotate = (root) => {
  if (!root) return;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => (n.parentElement && !n.parentElement.closest(SKIP) && RT.test(n.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT) });
  const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
  nodes.forEach((node) => {
    const s = node.nodeValue; let last = 0, out = null; RE.lastIndex = 0; let m;
    while ((m = RE.exec(s))) {
      const t = m[0]; if (used.has(t)) continue; used.add(t);
      out = out || document.createDocumentFragment();
      out.appendChild(document.createTextNode(s.slice(last, m.index + t.length)));
      const sp = document.createElement('span'); sp.className = 'en-term'; sp.lang = 'en'; sp.textContent = `(${MAP.get(t)})`; out.appendChild(sp);
      last = m.index + t.length;
    }
    if (out) { out.appendChild(document.createTextNode(s.slice(last))); node.parentNode.replaceChild(out, node); }
  });
};
/* 용어집 페이지 */
LA.glossaryPage = (main) => {
  const secs = LA.sections, src = (s) => s.title + s.render.toString(), first = (ko, ch) => secs.find((s) => s.title.includes(ko)) || secs.find((s) => s.ch === ch && src(s).includes(ko)) || secs.find((s) => src(s).includes(ko));
  const rows = LA.GLOSS.filter(([k], i, a) => !(k === '전치' || k === '오차의 제곱합'));
  main.innerHTML = `<article class="page"><header><div class="eyebrow"><span class="chno">A</span>부록</div><h1>용어집<span class="en">Glossary of Terms</span></h1></header>
    <div class="concept"><p class="lead">이 사이트에 나오는 선형대수 용어를 한국어와 영어로 정리했습니다. 원서나 영어 강의를 볼 때 찾아보세요. 각 단원 본문에서도 용어가 처음 나올 때 괄호 안에 영어를 붙여 두었습니다.</p>
      <label class="small" for="gl-q">찾기</label> <input id="gl-q" type="search" placeholder="예: 고윳값, eigen" style="border:1px solid var(--line);border-radius:6px;padding:6px 10px;background:var(--canvas);width:min(320px,100%)"></div>
    ${LA.chapters.map((c) => `<section class="card" data-ch="${c.no}"><h3><span>${c.no}. ${c.title}</span><small>${c.en}</small></h3><div class="scroll"><table class="t"><thead><tr><th>한국어</th><th>English</th><th>관련 단원</th></tr></thead><tbody>
      ${rows.filter((r) => r[2] === c.no).map(([k, e]) => { const s = first(k, c.no) || secs.find((x) => x.ch === c.no); return `<tr data-q="${(k + ' ' + e).toLowerCase()}"><td><b>${k}</b></td><td lang="en">${e}</td><td><a href="#${s.id}">${s.title}</a></td></tr>`; }).join('')}
    </tbody></table></div></section>`).join('')}</article>`;
  main.querySelector('#gl-q').addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    main.querySelectorAll('tr[data-q]').forEach((tr) => (tr.hidden = q && !tr.dataset.q.includes(q)));
    main.querySelectorAll('section[data-ch]').forEach((sc) => (sc.hidden = !sc.querySelector('tr[data-q]:not([hidden])')));
  });
};
})();
