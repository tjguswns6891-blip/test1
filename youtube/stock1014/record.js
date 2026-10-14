// 증시 롱폼(2026-10-14): 내 증시 사이트 /invest /themes 를 16:9 로 조작하며 녹화한다.
// 사용: (raw/stock1014 에서 python3 -m http.server 8765) → NODE_PATH=<pw>/node_modules node record.js <출력 폴더> [클립,...]
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
async function scrollTo(p, sel, off = 20) { await p.evaluate(([s, o]) => { const el = document.querySelector(s); window.scrollTo({ top: window.scrollY + el.getBoundingClientRect().top - o, behavior: 'smooth' }); }, [sel, off]); await p.waitForTimeout(1200); }
(async () => {
  const b = await chromium.launch();
  await clip(b, 'inv_top', 'invest/', async (p) => {
    await p.waitForTimeout(800);
    for (const t of ['S&P 500', '10년물 금리', '유가 (WTI)', 'VIX']) { const l = p.getByText(t, { exact: true }).first(); await moveTo(p, l).catch(() => {}); await p.waitForTimeout(1500); }
    await moveTo(p, p.locator('#todaySig')); await p.waitForTimeout(2000);
  });
  await clip(b, 'inv_kospi', 'invest/', async (p) => {
    await click(p, '#t-chart'); await p.waitForTimeout(1200);
    await scrollTo(p, '#t-chart', 10);
    await click(p, 'button[data-id="kospi"]'); await p.waitForTimeout(1200);
    await click(p, 'button[data-from="last1"]'); await p.waitForTimeout(1200);
    await scrollTo(p, '#mainChart', 40); await p.waitForTimeout(2500);
    const bb = await p.locator('#mainChart').boundingBox();
    await p.mouse.move(bb.x + bb.width * .3, bb.y + 300, { steps: 20 }); await p.waitForTimeout(1500);
    await p.mouse.move(bb.x + bb.width * .85, bb.y + 360, { steps: 60 }); await p.waitForTimeout(3000);
  });
  await clip(b, 'inv_rates', 'invest/', async (p) => {
    await click(p, '#t-chart'); await p.waitForTimeout(1200);
    await scrollTo(p, '#t-chart', 10);
    await click(p, 'button[data-id="rates"]'); await p.waitForTimeout(1000);
    await click(p, 'button[data-from="1975-12"]'); await p.waitForTimeout(1200);
    await scrollTo(p, '#mainChart', 40); await p.waitForTimeout(2500);
    const bb = await p.locator('#mainChart').boundingBox();
    await p.mouse.move(bb.x + bb.width * .2, bb.y + 300, { steps: 20 }); await p.waitForTimeout(1000);
    await p.mouse.move(bb.x + bb.width * .95, bb.y + 300, { steps: 70 }); await p.waitForTimeout(3000);
  });
  await clip(b, 'th_week', 'themes/', async (p) => {
    await p.waitForTimeout(800);
    await click(p, 'button[data-p="w1"]'); await p.waitForTimeout(2500);
    await scrollTo(p, 'h2:nth-of-type(1)', 30); await p.waitForTimeout(2500);
    for (const t of ['양자', '광통신', '데이터센터']) { const l = p.locator(`.tile[data-t="${t}"]`).first(); await moveTo(p, l).catch(() => {}); await p.waitForTimeout(1300); }
    const o = p.locator('.tile[data-t="석유,가스"]').first(); await moveTo(p, o).catch(() => {}); await p.waitForTimeout(2000);
  });
  await clip(b, 'th_rank', 'themes/', async (p) => {
    await click(p, 'button[data-p="w1"]'); await p.waitForTimeout(1500);
    await p.evaluate(() => { const h = [...document.querySelectorAll('h2')].find(x => x.textContent.includes('테마 순위')); window.scrollTo({ top: window.scrollY + h.getBoundingClientRect().top - 20, behavior: 'smooth' }); });
    await p.waitForTimeout(2500);
    await p.mouse.wheel(0, 900); await p.waitForTimeout(3000); await p.mouse.wheel(0, 900); await p.waitForTimeout(3000);
  });
  await b.close();
  fs.writeFileSync(`${OUT}/starts.json`, JSON.stringify(STARTS, null, 1));
})();
