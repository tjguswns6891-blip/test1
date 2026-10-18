// 푸리에 롱폼: 보이는 회로이론 16장(고조파 하나씩 더하기)을 다크 모드로 조작하며 녹화한다.
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
async function setN(page, n) {
  const el = page.locator('[id$="-N-n"]').first(); await moveTo(page, el); await el.click({ clickCount: 3 });
  await page.keyboard.type(String(n), { delay: 200 }); await page.keyboard.press('Enter'); await el.dispatchEvent('change');
}
(async () => {
  const browser = await chromium.launch({ args: ['--ignore-certificate-errors'] });
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, colorScheme: 'dark', recordVideo: { dir: OUT, size: { width: VW, height: VH } } });
  await ctx.addInitScript(CURSOR);
  const p = await ctx.newPage(); const t0 = Date.now(), M = {}, mark = (k) => { M[k] = (Date.now() - t0) / 1000; console.log(k, M[k]); };
  await p.goto(BASE + '#ch16', { waitUntil: 'load' }); await p.waitForTimeout(4500);
  const focus = () => p.evaluate(() => { const el = document.querySelector('#lab-fs'); window.scrollBy(0, el.getBoundingClientRect().top - 16); });
  await focus(); await p.waitForTimeout(700); await focus(); await p.waitForTimeout(500);
  await p.mouse.move(VW / 2, VH / 2);
  mark('start');
  await clickSel(p, '#lab-fs [data-wave="sq"]'); await p.waitForTimeout(800);
  await clickSel(p, '#lab-fs [data-act="build"]'); mark('sq_build'); await p.waitForTimeout(17000);   // N=1 → 49 (홀수만, 0.6초마다)
  mark('gibbs'); await p.waitForTimeout(5000);                                                         // N=49: 모서리 9% 뿔
  await clickSel(p, '#lab-fs [data-wave="saw"]'); mark('saw'); await setN(p, 15); await p.waitForTimeout(6000);  // 톱니파: 모든 차수
  await clickSel(p, '#lab-fs [data-wave="tri"]'); await p.waitForTimeout(400);
  await clickSel(p, '#lab-fs [data-act="build"]'); mark('tri_build'); await p.waitForTimeout(10000); // 삼각파: 금방 똑같아짐
  mark('end');
  const bb = await p.locator('#lab-fs').boundingBox();
  const v = p.video(); await ctx.close(); fs.renameSync(await v.path(), `${OUT}/fs_build.webm`);
  fs.writeFileSync(`${OUT}/boxes.json`, JSON.stringify({ fs_build: bb, _viewport: [VW, VH], _marks: M }, null, 1));
  await browser.close(); console.log('fs_build');
})();
