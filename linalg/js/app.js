/* 목차, 라우팅, 홈 화면 */
(function () {
'use strict';
const { mat, Plane, N, fmt } = LA;
const main = document.getElementById('main'), toc = document.getElementById('toc'), nav = document.getElementById('nav');
const secs = LA.sections;
const secNo = (s) => `${s.ch}.${secs.filter((x) => x.ch === s.ch).indexOf(s) + 1}`;

toc.innerHTML = `<div class="toc-ch"><a href="#glossary" data-id="glossary"><b>용어집</b> · Glossary (한↔영)</a><button type="button" class="chip ghost" id="en-tog" aria-pressed="true" style="justify-self:start;margin-top:6px">영어 용어 표시: 켜짐</button></div>` + LA.chapters.map((c) => `<div class="toc-ch"><h3><span class="no">${c.no}</span>${c.title}</h3>${secs.filter((s) => s.ch === c.no).map((s) => `<a href="#${s.id}" data-id="${s.id}">${secNo(s)} ${s.title}</a>`).join('')}</div>`).join('');
const enTog = () => document.getElementById('en-tog');
const setEn = (on) => { document.documentElement.classList.toggle('hide-en', !on); enTog().setAttribute('aria-pressed', on); enTog().textContent = `영어 용어 표시: ${on ? '켜짐' : '꺼짐'}`; try { localStorage.setItem('la-en', on ? '1' : '0'); } catch (e) {} };
let enOn = true; try { enOn = localStorage.getItem('la-en') !== '0'; } catch (e) {}
setEn(enOn);
enTog().addEventListener('click', () => { enOn = !enOn; setEn(enOn); });
document.getElementById('navtoggle').addEventListener('click', () => { const o = nav.classList.toggle('open'); document.getElementById('navtoggle').setAttribute('aria-expanded', o); });

function home() {
  main.innerHTML = `<div class="page">
    <section class="hero">
      <div>
        <div class="eyebrow">선형대수학 · 7개 장 · ${secs.length}개 실험</div>
        <h1>인덱스가 많아 막힐 때, <em>숫자를 다 펼쳐서</em> 봅니다</h1>
        <p class="lead"><i class="var">a<sub>ij</sub></i>, Σ<sub><i>k</i></sub>, (−1)<sup><i>i</i>+<i>j</i></sup> 같은 기호를 실제 숫자로 하나하나 전개하고, 행렬이 공간을 어떻게 바꾸는지 그림으로 움직여 봅니다. 모든 행렬은 직접 고칠 수 있고 계산은 분수 그대로 정확하게 따라갑니다.</p>
        <div class="legendbox" style="margin-top:16px">
          <div><span class="sw" style="background:var(--e1)"></span><span>주황 = 첫째 열 / 첫째 기저 벡터 (<b>e</b>₁이 가는 곳)</span></div>
          <div><span class="sw" style="background:var(--e2)"></span><span>초록 = 둘째 열 / 둘째 기저 벡터 (<b>e</b>₂가 가는 곳)</span></div>
          <div><span class="sw" style="background:var(--accent)"></span><span>파랑 = 결과, 피벗, 지금 보고 있는 칸</span></div>
        </div>
      </div>
      <div class="card"><h3>행렬 = 격자를 바꾸는 규칙 <small>주황·초록 점을 끌어 보세요</small></h3><div class="viz" id="h-viz"></div><div class="mxrow" id="h-m"></div></div>
    </section>
    <section class="card"><h3>3×3 행렬 = 공간을 바꾸는 규칙 <small>숫자를 바꾸고 그림을 끌어 회전해 보세요</small></h3>
      <div class="lab"><div><div id="h3-ed"></div><p class="small">1열 → <span class="t1">Ae₁</span>, 2열 → <span class="t2">Ae₂</span>, 3열 → <span class="t3">Ae₃</span>. 단위정육면체가 이 세 벡터로 만든 평행육면체가 되고, 그 부피가 |det A|입니다.</p><div id="h3-det" class="calc"></div></div><div id="h3-viz"></div></div></section>
    <section class="chgrid">${LA.chapters.map((c) => `<div class="chcard"><h3><span class="no">${c.no}</span><span>${c.title}</span></h3><p class="small muted" style="margin:0">${c.en}</p><ul>${secs.filter((s) => s.ch === c.no).map((s) => `<li><a href="#${s.id}"><span class="t-ko">${s.title}<small lang="en" class="en-term">${s.en}</small></span><span>${secNo(s)}</span></a></li>`).join('')}</ul></div>`).join('')}</section>
    <section class="concept"><h2>읽는 법</h2>
      <ul><li><i class="var">a<sub>ij</sub></i>는 언제나 <b><i>i</i>행 <i>j</i>열</b>입니다. 행렬의 각 칸 위에 작게 붙은 글자가 그 칸의 이름입니다.</li>
        <li>회색 계산 상자는 기호식에 실제 숫자를 대입한 줄입니다. 굵은 파란 숫자가 그 줄의 결과입니다.</li>
        <li>“다음 →” 버튼이 있는 곳은 한 단계씩 진행됩니다. “자동 재생”으로 연속해서 볼 수도 있습니다.</li>
        <li>본문에서 용어가 처음 나오면 괄호 안에 영어 용어가 붙습니다. 왼쪽 목차의 <a href="#glossary">용어집</a>에서 전체 목록을 한↔영으로 찾아볼 수 있고, 영어 표시는 끌 수도 있습니다.</li>
        <li>분수는 <code>3/4</code>처럼 입력합니다. 그림의 동그란 점은 마우스나 손가락으로 끌 수 있습니다.</li></ul></section>
  </div>`;
  let c1 = [2, 1], c2 = [-1, 1.5];
  const plane = new Plane(main.querySelector('#h-viz'), { range: 4, aspect: 0.85 });
  plane.handle({ get: () => c1, set: (p) => (c1 = p), color: 'e1' }).handle({ get: () => c2, set: (p) => (c2 = p), color: 'e2' });
  plane.draw = (p) => {
    const A = [[c1[0], c2[0]], [c1[1], c2[1]]]; p.tgrid(A, 'accent', 0.3);
    p.poly([[0, 0], c1, N.vadd(c1, c2), c2], 'accent', null, { a: 0.15 });
    p.arrow([0, 0], c1, 'e1', { label: 'Ae₁' }); p.arrow([0, 0], c2, 'e2', { label: 'Ae₂' });
  };
  const upd = () => { main.querySelector('#h-m').innerHTML = mat([[`<span class="t1">${fmt(c1[0])}</span>`, `<span class="t2">${fmt(c2[0])}</span>`], [`<span class="t1">${fmt(c1[1])}</span>`, `<span class="t2">${fmt(c2[1])}</span>`]], { name: 'A', sub: 'a' }) + `<span class="small muted">det A = ${fmt(c1[0] * c2[1] - c2[0] * c1[1])} = 파란 평행사변형의 넓이</span>`; };
  plane.onchange = upd; upd();
  const T = LA.transform3D(main.querySelector('#h3-viz'), { range: 3, aspect: 0.85 });
  LA.editor(main.querySelector('#h3-ed'), LA.X.fromN([[1, 0.5, 0], [0, 1, 0], [0.5, 0, 1.5]]), (A) => {
    T.set(LA.X.toN(A), N.eye(3)); T.setT(1);
    main.querySelector('#h3-det').innerHTML = `<span class="ln">det A = <b>${LA.X.det(A).html()}</b> → 부피 ${LA.X.det(A).abs().html()}배</span>`;
  }, { name: 'A', resize: false, presets: [{ name: '층밀림', A: [[1, 1, 0], [0, 1, 0], [0, 0, 1]] }, { name: 'z축 회전', A: [[0, -1, 0], [1, 0, 0], [0, 0, 1]] }, { name: '납작 (det 0)', A: [[1, 0, 1], [0, 1, 1], [0, 0, 0]] }] });
  main.querySelector('#h3-ed input').dispatchEvent(new Event('input', { bubbles: true }));
}

function show() {
  LA.cleanup();
  const id = location.hash.replace('#', '');
  const i = secs.findIndex((s) => s.id === id);
  toc.querySelectorAll('a').forEach((a) => { if (a.dataset.id === id) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
  nav.classList.remove('open');
  if (id === 'glossary') { LA.glossaryPage(main); document.title = '용어집 · 선형대수 실험실'; window.scrollTo(0, 0); return; }
  if (i < 0) { home(); document.title = '선형대수 실험실'; window.scrollTo(0, 0); return; }
  const s = secs[i], ch = LA.chapters.find((c) => c.no === s.ch), prev = secs[i - 1], next = secs[i + 1];
  main.innerHTML = `<article class="page"><header><div class="eyebrow"><span class="chno">${s.ch}</span>${ch.title}<span>·</span><span>${secNo(s)}</span></div><h1>${s.title}<span class="en">${s.en}</span></h1></header><div id="sec" class="page" style="gap:22px"></div>
    <nav class="pager">${prev ? `<a href="#${prev.id}"><small>← 이전 ${secNo(prev)}</small>${prev.title}</a>` : '<a href="#home"><small>←</small>처음 화면</a>'}${next ? `<a class="next" href="#${next.id}"><small>다음 ${secNo(next)} →</small>${next.title}</a>` : ''}</nav></article>`;
  document.title = `${s.title} · 선형대수 실험실`;
  LA.resetGloss();
  try { s.render(main.querySelector('#sec')); LA.annotate(main.querySelector('#sec')); } catch (e) { console.error(e); main.querySelector('#sec').innerHTML = `<p class="tw">이 실험을 그리는 중 오류가 났습니다: ${e.message}</p>`; }
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', show);
show();
})();
