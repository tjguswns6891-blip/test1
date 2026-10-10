/* 조회수: 오늘(한국 시간 기준) / 누적. 공개 카운터 abacus.jasoncameron.dev 사용.
   GitHub Pages 주소에서만 동작하고, 같은 탭 세션에서는 한 번만 셉니다. */
(function () {
'use strict';
const box = document.getElementById('views'); if (!box) return;
if (!/github\.io$/.test(location.hostname)) return; // 로컬·미리보기에서는 세지 않음
const API = 'https://abacus.jasoncameron.dev', NS = 'tjguswns-test1-linalg';
const day = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10).replace(/-/g, '');
let first = true;
try { first = sessionStorage.getItem('la-viewed') !== day; } catch (e) {}
const call = (key) => fetch(`${API}/${first ? 'hit' : 'get'}/${NS}/${key}`, { cache: 'no-store' })
  .then((r) => (r.status === 404 ? { value: 0 } : r.ok ? r.json() : Promise.reject(r.status)))
  .then((j) => Number(j.value) || 0);
const n = (x) => x.toLocaleString('ko-KR');
Promise.all([call('d' + day), call('total')]).then(([today, total]) => {
  try { sessionStorage.setItem('la-viewed', day); } catch (e) {}
  box.innerHTML = `<span>오늘 <b>${n(today)}</b></span><span>누적 <b>${n(total)}</b></span>`;
  box.hidden = false;
}).catch(() => { /* 카운터에 닿지 못하면 표시하지 않음 */ });
})();
