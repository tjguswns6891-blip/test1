// 증시 2026-11-28: 내 사이트 /invest 를 조작하며 녹화한다 (그래픽 칸 1080×840 에 꽉 차게, 글자가 또렷하도록 스크린샷을 이어 붙인다).
// 사용: (사이트 폴더에서 python3 -m http.server 8765) → node record.js <출력 폴더> [signal,chart]
const { chromium } = require('playwright'); const fs = require('fs'); const { execFileSync } = require('child_process');
const [,, OUT, ONLY_ARG] = process.argv; const ONLY = (ONLY_ARG || '').split(',').filter(Boolean);
const BASE = 'http://localhost:8765/';
const CURSOR = `(() => { const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:-50px;top:-50px;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;background:rgba(255,197,61,.95);border:2px solid #111;z-index:99999;pointer-events:none';
  const add = () => document.body && document.body.appendChild(d); if (document.body) add(); else addEventListener('DOMContentLoaded', add);
  addEventListener('pointermove', (e) => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true); })();`;
async function clip(browser, name, VW, VH, act) {
  const DSF = 1080 / VW;
  if (ONLY.length && !ONLY.includes(name)) return;
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, deviceScaleFactor: DSF, colorScheme: 'dark' });
  await ctx.addInitScript(CURSOR); const page = await ctx.newPage();
  await page.goto(BASE + 'invest/', { waitUntil: 'load' }); await page.waitForTimeout(2500);
  const dir = `${OUT}/${name}_f`; fs.mkdirSync(dir, { recursive: true }); const frames = []; let on = false, t0 = 0;
  const loop = (async () => { while (!on) await new Promise(r => setTimeout(r, 20)); let i = 0;
    while (on) { const f = `${dir}/${String(i++).padStart(5, '0')}.jpg`; const t = Date.now() - t0; await page.screenshot({ path: f, type: 'jpeg', quality: 93 }).catch(() => {}); frames.push([f, t]); } })();
  const start = () => { t0 = Date.now(); on = true; };
  try { await act(page, start); } catch (e) { console.error(name, '실패:', e.message.split('\n')[0]); }
  on = false; await loop; await ctx.close();
  let list = ''; frames.forEach(([f, t], i) => { const d = ((i + 1 < frames.length ? frames[i + 1][1] : t + 80) - t) / 1000; list += `file '${f.replace(/.*\//, '')}'\nduration ${d.toFixed(3)}\n`; });
  fs.writeFileSync(`${dir}/list.txt`, list);
  execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', `${dir}/list.txt`, '-vf', 'fps=30,scale=1080:840:flags=lanczos,setsar=1', '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', `${OUT}/${name}.mp4`]);
  console.log(name, frames.length, 'frames', (frames[frames.length - 1][1] / 1000).toFixed(1) + 's');
}
const sleep = (p, ms) => p.waitForTimeout(ms);
async function hl(p, loc) {   // 마우스를 옮기고 노란 테두리
  const bb = await loc.boundingBox(); await p.mouse.move(bb.x + bb.width * .62, bb.y + bb.height + 9, { steps: 12 });
  await loc.evaluate(e => { document.querySelectorAll('[data-hl]').forEach(x => { x.style.outline = ''; x.style.background = ''; x.removeAttribute('data-hl'); });
    e.setAttribute('data-hl', 1); e.style.outline = '3px solid #ffc53d'; e.style.outlineOffset = '3px'; e.style.borderRadius = '8px'; e.style.background = 'rgba(255,197,61,.12)'; });
}
(async () => {
  const b = await chromium.launch();
  // C 2번째 문장: 오늘의 매매 신호 — S&P 500(보유) 1년 뒤 오른 확률 75% → QQQ(비중 축소) 10% 넘게 빠진 확률 48%
  await clip(b, 'signal', 560, 436, async (p, start) => {
    await p.evaluate(() => { const g = document.getElementById('sigCards'), cs = g.querySelectorAll('.scard'); cs[0].style.display = 'none'; cs[2].style.display = 'none';   // 10년 국채·SCHD 카드는 가리고 두 장만 크게
      g.style.gridTemplateColumns = '1fr 1fr'; cs.forEach(c => { const pp = c.querySelector(':scope > p'); if (pp) pp.style.display = 'none'; });
      cs.forEach(c => { const w = c.querySelector('.won'); if (w) w.style.display = 'none'; }); const y = g.getBoundingClientRect().top + scrollY - 58; scrollTo(0, y); });
    await sleep(p, 400); start(); await sleep(p, 600);          // 아래 쉼은 C 릴스 음성의 단어 시각에 맞춘 값 (문장 시작 기준 3.6초 '1년 뒤', 6.0초 '그런데 QQQ는', 7.1초 '10% 넘게')
    const spx = p.locator('#sigCards .scard').nth(1), qqq = p.locator('#sigCards .scard').nth(3);
    await hl(p, spx.locator('.act')); await sleep(p, 2750);
    await hl(p, spx.locator('table.per tbody tr').nth(1)); await sleep(p, 2250);
    await hl(p, qqq.locator('.act')); await sleep(p, 900);
    await hl(p, qqq.locator('.ddline')); await sleep(p, 3800);
  });
  // B 5번째 문장: 50년 차트 — S&P 500 과 금리만 남기고, 금리가 방향을 바꾼 시기를 짚는다
  await clip(b, 'chart', 750, 583, async (p, start) => {
    await p.click('#t-chart'); await sleep(p, 600);
    for (const id of ['qqq', 'schd', 'bond', 'nikkei', 'kospi']) await p.click(`#legend button[data-id="${id}"]`);
    for (const id of ['bond', 'cpi', 'oil', 'vix']) await p.click(`#panelToggles button[data-id="${id}"]`);
    await p.selectOption('#srSel', 'none'); await sleep(p, 600);
    const r = await p.evaluate(() => { const e = document.getElementById('mainChart'), r = e.getBoundingClientRect(); scrollTo(0, r.top + scrollY - 3); return [r.left, r.width]; });
    const X = y => r[0] + 56 + (y - 1976) / 50.9 * (r[1] - 154);   // 그림 안쪽 여백: 왼쪽 56, 오른쪽 98 await sleep(p, 400);
    await p.mouse.move(X(1978), 330); await sleep(p, 300); start();
    for (const [y, ms] of [[1981.5, 950], [1987.8, 650], [2000.2, 900], [2007.9, 900], [2020.2, 600], [2022.1, 2400]]) { await p.mouse.move(X(y), 330, { steps: 14 }); await sleep(p, ms); }
  });
  await b.close();
})();
