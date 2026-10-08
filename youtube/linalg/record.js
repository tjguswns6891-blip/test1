// 선형대수 실험실 화면을 자동으로 조작하며 녹화한다 (영상 B롤용).
// 사용: NODE_PATH=<playwright>/node_modules node record.js <사이트 주소> <출력 폴더>
const { chromium } = require('playwright');
const [,, BASE, OUT] = process.argv;
const VW = 1600, VH = 900;

const CURSOR = `(() => { const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:rgba(255,197,61,.85);border:3px solid #111;z-index:99999;pointer-events:none;transition:transform .08s';
  const add = () => document.body && document.body.appendChild(d); if (document.body) add(); else addEventListener('DOMContentLoaded', add);
  addEventListener('pointermove', (e) => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true);
  addEventListener('pointerdown', () => d.style.transform = 'scale(.7)', true);
  addEventListener('pointerup', () => d.style.transform = '', true); })();`;

const FOCUS = {
  home2d: '.card:has(#h-viz)', home3d: '.card:has(#h3-viz)', gauss: '#sec .lab', detdef: '#sec .lab', eigen: '#sec .lab',
  lsq: '.lab:has(#ls-viz)', svdgeo: '#sec .lab', svdimg: '.lab:has(#si-appr)', glossary: '#main', entoggle: '#main', toc: '#main', fraction: '#sec .lab',
};
const BOXES = {};
const ONLY = (process.argv[4] || '').split(',').filter(Boolean);
async function clip(browser, name, hash, act) {
  if (ONLY.length && !ONLY.includes(name)) return;
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, recordVideo: { dir: OUT, size: { width: VW, height: VH } } });
  await ctx.addInitScript(CURSOR);
  const page = await ctx.newPage();
  await page.goto(BASE + '#' + hash, { waitUntil: 'load' });
  await page.waitForTimeout(900);
  await page.mouse.move(VW / 2, VH / 2);
  try { await act(page); } catch (e) { console.error(name, '실패:', e.message.split('\n')[0]); }
  await page.waitForTimeout(600);
  // 편집 때 확대할 영역: 이 클립에서 조작한 카드(또는 실험 묶음)의 화면 위치
  const sel = FOCUS[name];
  if (sel) { const bb = await page.locator(sel).first().boundingBox().catch(() => null); if (bb) BOXES[name] = bb; }
  const v = page.video(); await ctx.close();
  const fs = require('fs'); fs.renameSync(await v.path(), `${OUT}/${name}.webm`); console.log(name);
}

// 좌표평면(캔버스) 위 점 끌기: range 는 그 평면의 반폭(세계 좌표)
async function canvasPt(page, sel, range, p) {
  const r = await page.locator(sel).boundingBox(); const s = r.width / (2 * range);
  return [r.x + r.width / 2 + p[0] * s, r.y + r.height / 2 - p[1] * s];
}
async function drag(page, sel, range, path, ms = 900) {
  let [x, y] = await canvasPt(page, sel, range, path[0]);
  await page.mouse.move(x, y, { steps: 12 }); await page.waitForTimeout(200); await page.mouse.down();
  for (const p of path.slice(1)) { const [nx, ny] = await canvasPt(page, sel, range, p); await page.mouse.move(nx, ny, { steps: Math.round(ms / 16) }); await page.waitForTimeout(150); }
  await page.mouse.up();
}
async function clickText(page, text) {
  let b = page.getByRole('button', { name: text, exact: true }).first();
  if (!(await b.count())) b = page.getByRole('tab', { name: text, exact: true }).first();
  if (!(await b.count())) b = page.getByText(text, { exact: true }).first(); await b.scrollIntoViewIfNeeded(); const bb = await b.boundingBox(); await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2, { steps: 15 }); await b.click(); }
async function clickSel(page, sel) { const b = page.locator(sel).first(); await b.scrollIntoViewIfNeeded(); const bb = await b.boundingBox(); await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2, { steps: 15 }); await b.click(); }

(async () => {
  const browser = await chromium.launch();
  await clip(browser, 'home2d', 'home', async (p) => {
    await drag(p, '#h-viz canvas', 4, [[2, 1], [3, 0.5], [2.5, 2.5], [2, 1]]);
    await drag(p, '#h-viz canvas', 4, [[-1, 1.5], [0.5, 2.5], [-2.5, 0.5], [-1, 1.5]]);
    await drag(p, '#h-viz canvas', 4, [[-1, 1.5], [2, 1]], 1400);   // 두 열이 같아지면 넓이 0
    await p.waitForTimeout(800);
  });
  await clip(browser, 'home3d', 'home', async (p) => {
    const c = p.locator('#h3-viz canvas'); await c.scrollIntoViewIfNeeded(); await p.waitForTimeout(500);
    const b = await c.boundingBox(); const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
    await p.mouse.move(cx, cy, { steps: 10 }); await p.mouse.down(); await p.mouse.move(cx + 220, cy + 40, { steps: 60 }); await p.mouse.up();
    await p.waitForTimeout(500); await clickText(p, '층밀림'); await p.waitForTimeout(1500);
    await clickText(p, '납작 (det 0)'); await p.waitForTimeout(2200);
  });
  await clip(browser, 'gauss', 'gauss', async (p) => {
    for (let i = 0; i < 3; i++) { await clickSel(p, '[data-s="next"]'); await p.waitForTimeout(1300); }
    await clickSel(p, '[data-s="play"]'); await p.waitForTimeout(6000);
  });
  await clip(browser, 'detdef', 'det-def', async (p) => {
    const btns = p.locator('#dd-pick button'); const n = await btns.count();
    for (let i = 0; i < Math.min(n, 4); i++) { const bb = await btns.nth(i).boundingBox(); await p.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2, { steps: 15 }); await btns.nth(i).click(); await p.waitForTimeout(1500); }
  });
  await clip(browser, 'eigen', 'eigen', async (p) => { await clickSel(p, '#e2-spin'); await p.waitForTimeout(7000); });
  await clip(browser, 'lsq', 'lsq', async (p) => {
    const s = '#ls-viz canvas'; await p.locator(s).scrollIntoViewIfNeeded();
    await drag(p, s, 4.5, [[2.5, 2.5], [2.5, -1], [2.5, 3.5]]);
    await drag(p, s, 4.5, [[-3, -1.5], [-3, 1.5]]);
    await p.waitForTimeout(800);
  });
  await clip(browser, 'svdgeo', 'svd', async (p) => {
    const play = p.locator('[data-s="play"]'); if (await play.count()) await clickSel(p, '[data-s="play"]');
    else { const anim = p.getByRole('button', { name: /애니메이션|재생/ }).first(); if (await anim.count()) await anim.click(); }
    await p.waitForTimeout(6000);
  });
  await clip(browser, 'svdimg', 'svd', async (p) => {
    await clickText(p, '이미지 압축'); await p.waitForTimeout(1200);
    const sl = p.locator('#si-k'); await sl.scrollIntoViewIfNeeded();
    for (const k of [1, 2, 3, 5, 8, 12, 20, 30, 40]) { await sl.evaluate((el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); }, k); await p.waitForTimeout(650); }
    await p.waitForTimeout(800);
  });
  await clip(browser, 'glossary', 'glossary', async (p) => {
    await clickSel(p, '#gl-q'); await p.keyboard.type('고유', { delay: 250 }); await p.waitForTimeout(1800);
    await p.locator('#gl-q').fill(''); await p.keyboard.type('eigen', { delay: 150 }); await p.waitForTimeout(1500);
  });
  await clip(browser, 'entoggle', 'gauss', async (p) => {
    await p.waitForTimeout(800); await clickSel(p, '#en-tog'); await p.waitForTimeout(1600); await clickSel(p, '#en-tog'); await p.waitForTimeout(1200);
  });
  await clip(browser, 'toc', 'home', async (p) => {
    await p.mouse.move(VW / 2, VH / 2); for (let i = 0; i < 12; i++) { await p.mouse.wheel(0, 120); await p.waitForTimeout(120); }
    await p.waitForTimeout(1200);
  });
  await clip(browser, 'fraction', 'inverse', async (p) => {
    const cell = p.locator('input.c').first(); await cell.scrollIntoViewIfNeeded(); const bb = await cell.boundingBox();
    await p.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2, { steps: 15 }); await cell.click({ clickCount: 3 });
    await p.keyboard.type('3/4', { delay: 300 }); await p.keyboard.press('Tab'); await p.waitForTimeout(2000);
  });
  await browser.close();
  const fs = require('fs'), bf = `${OUT}/boxes.json`;
  const old = fs.existsSync(bf) ? JSON.parse(fs.readFileSync(bf, 'utf8')) : {};
  fs.writeFileSync(bf, JSON.stringify(Object.assign(old, BOXES, { _viewport: [VW, VH] }), null, 1));
})();
