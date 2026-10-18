// 2포트 롱폼: 보이는 회로이론 17장(T형 회로 z 파라미터 측정)을 다크 모드로 조작하며 녹화한다.
// 사용: NODE_PATH=<playwright>/node_modules node record.js <회로 사이트 html> <출력 폴더>
// 장면마다 녹화 시작부터의 시각(초)을 boxes.json 의 _marks 에 남긴다 (편집 때 그 시각부터 잘라 쓴다).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [,, SRC, OUT] = process.argv;
const BASE = /^https?:/.test(SRC) ? SRC : 'file://' + path.resolve(SRC);
const VW = 1600, VH = 900;
const CURSOR = `(() => { const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:rgba(255,197,61,.9);border:3px solid #111;z-index:99999;pointer-events:none;transition:transform .08s';
  const add = () => document.body && document.body.appendChild(d); if (document.body) add(); else addEventListener('DOMContentLoaded', add);
  addEventListener('pointermove', (e) => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true);
  addEventListener('pointerdown', () => d.style.transform = 'scale(.7)', true);
  addEventListener('pointerup', () => d.style.transform = '', true); })();`;

async function moveTo(page, loc) { const bb = await loc.boundingBox(); await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2, { steps: 18 }); return bb; }
async function clickSel(page, sel) { const b = page.locator(sel).first(); await moveTo(page, b); await b.click(); }
async function setVal(page, key, val) {
  const el = page.locator(`#tp-ctl-${key}-n`); await moveTo(page, el); await el.click({ clickCount: 3 });
  await page.keyboard.type(String(val), { delay: 200 }); await page.keyboard.press('Enter'); await el.dispatchEvent('change');
}
(async () => {
  const browser = await chromium.launch({ args: ['--ignore-certificate-errors'] });
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, colorScheme: 'dark', recordVideo: { dir: OUT, size: { width: VW, height: VH } } });
  await ctx.addInitScript(CURSOR);
  const p = await ctx.newPage(); const t0 = Date.now(), M = {}, mark = (k) => { M[k] = (Date.now() - t0) / 1000; console.log(k, M[k]); };
  await p.goto(BASE + '#ch17', { waitUntil: 'load' }); await p.waitForTimeout(4500);
  const focus = () => p.evaluate(() => { const el = document.querySelector('#lab-2p'); window.scrollBy(0, el.getBoundingClientRect().top - 16); });
  await focus(); await p.waitForTimeout(700); await focus(); await p.waitForTimeout(500);
  await p.mouse.move(VW / 2, VH / 2);
  mark('start');
  await clickSel(p, '#lab-2p [data-mode="p1"]'); mark('p1'); await p.waitForTimeout(9000);     // 포트 2 개방: V₁ 4.3 V, V₂ 3.3 V → z₁₁ 430, z₂₁ 330
  await clickSel(p, '#lab-2p [data-mode="p2"]'); mark('p2'); await p.waitForTimeout(9000);     // 포트 1 개방: z₁₂ 330, z₂₂ 550
  await setVal(p, 'Rc', 500); mark('recip'); await p.waitForTimeout(5000);                      // Rc 를 바꿔도 z₁₂ = z₂₁
  await setVal(p, 'Rc', 330); await p.waitForTimeout(1500);
  await clickSel(p, '#lab-2p [data-mode="p1"]'); mark('p1_again'); await p.waitForTimeout(5000);
  mark('end');
  const bb = await p.locator('#lab-2p').boundingBox();
  const v = p.video(); await ctx.close(); fs.renameSync(await v.path(), `${OUT}/tp_measure.webm`);
  fs.writeFileSync(`${OUT}/boxes.json`, JSON.stringify({ tp_measure: bb, _viewport: [VW, VH], _marks: M }, null, 1));
  await browser.close(); console.log('tp_measure');
})();
