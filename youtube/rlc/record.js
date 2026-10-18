// RLC 롱폼: 보이는 회로이론 8장(직렬 RLC 극점·계단 응답)을 다크 모드로 조작하며 녹화한다.
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
// 로그 슬라이더(1~2000 Ω)의 손잡이를 R1 → R2 로 실제로 끈다
const RPOS = (r) => Math.log(r) / Math.log(2000);
async function slideR(page, r1, r2, ms) {
  const b = await page.locator('#rlc2-ctl-R').boundingBox(); const y = b.y + b.height / 2, x = r => b.x + 8 + (b.width - 16) * RPOS(r);
  await page.mouse.move(x(r1), y, { steps: 15 }); await page.mouse.down();
  await page.mouse.move(x(r2), y, { steps: Math.round(ms / 16) }); await page.mouse.up();
}
async function setR(page, r) {
  const n = page.locator('[id="rlc2-ctl-R-n"]'); await moveTo(page, n); await n.click({ clickCount: 3 });
  await page.keyboard.type(String(r), { delay: 200 }); await page.keyboard.press('Enter'); await n.dispatchEvent('change');
}
(async () => {
  const browser = await chromium.launch({ args: ['--ignore-certificate-errors'] });
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, colorScheme: 'dark', recordVideo: { dir: OUT, size: { width: VW, height: VH } } });
  await ctx.addInitScript(CURSOR);
  const p = await ctx.newPage(); const t0 = Date.now(), M = {}, mark = (k) => { M[k] = (Date.now() - t0) / 1000; console.log(k, M[k]); };
  await p.goto(BASE + '#ch8', { waitUntil: 'load' }); await p.waitForTimeout(4500);
  const focus = () => p.evaluate(() => { const el = document.querySelector('#lab-rlc2'); window.scrollBy(0, el.getBoundingClientRect().top - 16); });
  await focus(); await p.waitForTimeout(700); await focus(); await p.waitForTimeout(500);
  await p.mouse.move(VW / 2, VH / 2);
  mark('start');
  await setR(p, 1000); mark('over'); await p.waitForTimeout(6500);                 // 과감쇠: 실수축 두 극점, 느린 상승
  mark('sweep'); await slideR(p, 1000, 120, 3000); await p.waitForTimeout(5500);   // 두 극점이 다가감
  await moveTo(p, p.locator('#lab-rlc2 [data-act="crit"]')); mark('crit');
  await p.locator('#lab-rlc2 [data-act="crit"]').click(); await p.waitForTimeout(6500); // 임계: 중근
  mark('under'); await slideR(p, 63, 15, 2500); await p.waitForTimeout(6500);      // 부족: 위아래로 갈라짐
  mark('low'); await slideR(p, 15, 4, 2000); await p.waitForTimeout(7000);         // 허수축 가까이: 오래 출렁
  mark('end');
  const bb = await p.locator('#lab-rlc2').boundingBox();
  const v = p.video(); await ctx.close(); fs.renameSync(await v.path(), `${OUT}/rlc_sweep.webm`);
  fs.writeFileSync(`${OUT}/boxes.json`, JSON.stringify({ rlc_sweep: bb, _viewport: [VW, VH], _marks: M }, null, 1));
  await browser.close(); console.log('rlc_sweep');
})();
