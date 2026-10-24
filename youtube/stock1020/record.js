// 증시 2026-10-20: 내 테마 사이트 /themes 를 16:9 로 조작하며 녹화한다.
// 사용: (raw/stock1020 에서 python3 -m http.server 8765) → NODE_PATH=<pw>/node_modules node record.js <출력 폴더> [클립,...]
const { chromium } = require('playwright');
const fs = require('fs');
const [,, OUT, ONLY_ARG] = process.argv;
const BASE = 'http://localhost:8765/';
const VW = 1920, VH = 1080;                // CSS zoom 1.3 으로 글자를 크게
const ONLY = (ONLY_ARG || '').split(',').filter(Boolean);
const CURSOR = `(() => { const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:rgba(255,197,61,.9);border:3px solid #111;z-index:99999;pointer-events:none;transition:transform .08s';
  const add = () => document.body && document.body.appendChild(d); if (document.body) add(); else addEventListener('DOMContentLoaded', add);
  addEventListener('pointermove', (e) => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true);
  addEventListener('pointerdown', () => d.style.transform = 'scale(.7)', true);
  addEventListener('pointerup', () => d.style.transform = '', true); })();`;
const STARTS = {};
async function clip(browser, name, path, act) {
  if (ONLY.length && !ONLY.includes(name)) return;
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, colorScheme: 'dark',
    recordVideo: { dir: OUT, size: { width: 1920, height: 1080 } } });
  await ctx.addInitScript(CURSOR);
  const page = await ctx.newPage(); const t0 = Date.now();
  await page.goto(BASE + path, { waitUntil: 'load' }); await page.evaluate(() => document.documentElement.style.zoom = '1.3'); await page.waitForTimeout(3500);
  await page.mouse.move(VW / 2, VH / 2);
  STARTS[name] = (Date.now() - t0) / 1000;
  try { await act(page); } catch (e) { console.error(name, '실패:', e.message.split('\n')[0]); }
  await page.waitForTimeout(500);
  const v = page.video(); await ctx.close(); fs.renameSync(await v.path(), `${OUT}/${name}.webm`); console.log(name);
}
async function moveTo(p, loc) { const bb = await loc.boundingBox(); await p.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2, { steps: 20 }); return bb; }
async function click(p, sel) { const l = p.locator(sel).first(); await moveTo(p, l); await l.click(); }
(async () => {
  const b = await chromium.launch();
  // 1주: 데이터센터 꼴찌 → 광통신 → 반도체
  await clip(b, 'th_week', 'themes/', async (p) => {
    await p.waitForTimeout(800);
    await click(p, 'button[data-p="w1"]'); await p.waitForTimeout(2500);
    for (const t of ['데이터센터', '광통신', '반도체']) { const l = p.locator(`.tile[data-t="${t}"]`).first(); await moveTo(p, l).catch(() => {}); await p.waitForTimeout(1500); }
    const l = p.locator('.tile[data-t="데이터센터"]').first(); await moveTo(p, l).catch(() => {}); await p.waitForTimeout(2500);
  });
  // 어제(1일): 반도체·데이터센터 반등
  await clip(b, 'th_day', 'themes/', async (p) => {
    await p.waitForTimeout(800);
    await click(p, 'button[data-p="d1"]'); await p.waitForTimeout(2500);
    for (const t of ['반도체', '데이터센터', '광통신', '방산,항공']) { const l = p.locator(`.tile[data-t="${t}"]`).first(); await moveTo(p, l).catch(() => {}); await p.waitForTimeout(1400); }
    await p.waitForTimeout(1500);
  });
  await b.close();
  fs.writeFileSync(`${OUT}/starts.json`, JSON.stringify(STARTS, null, 1));
})();
