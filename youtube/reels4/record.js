// 선형대수 쇼츠 4편(최소제곱법·그람-슈미트·대각화·역행렬): 선형대수 실험실을 다크 모드로 조작하며 녹화한다.
// 사용: NODE_PATH=<playwright>/node_modules node record.js <선형대수 사이트 index.html> <출력 폴더> [클립,...]
const { chromium } = require('playwright');
const fs = require('fs');
const [,, SRC, OUT, ONLY_ARG] = process.argv;
const url = (s) => /^https?:/.test(s) ? s : 'file://' + require('path').resolve(s);
const CIRCUIT = url(SRC), LINALG = url(process.env.LINALG || require('path').join(__dirname, '../raw/linalg_site/index.html'));
let BASE = CIRCUIT;
const VW = 1600, VH = 900;
const ONLY = (ONLY_ARG || '').split(',').filter(Boolean);

const CURSOR = `(() => { const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:rgba(255,197,61,.9);border:3px solid #111;z-index:99999;pointer-events:none;transition:transform .08s';
  const add = () => document.body && document.body.appendChild(d); if (document.body) add(); else addEventListener('DOMContentLoaded', add);
  addEventListener('pointermove', (e) => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true);
  addEventListener('pointerdown', () => d.style.transform = 'scale(.7)', true);
  addEventListener('pointerup', () => d.style.transform = '', true); })();`;

const BOXES = {}, STARTS = {};   // STARTS: 녹화 시작부터 조작이 시작되기까지(초) — 편집 때 그만큼 앞을 잘라 쓴다
async function clip(browser, name, hash, focus, act) {
  if (ONLY.length && !ONLY.includes(name)) return;
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, colorScheme: 'dark', ignoreHTTPSErrors: true,
    recordVideo: { dir: OUT, size: { width: VW, height: VH } } });
  await ctx.addInitScript(CURSOR);
  const page = await ctx.newPage();
  const t0 = Date.now();
  await page.goto(BASE + '#' + hash, { waitUntil: 'load' });
  await page.waitForTimeout(4500);                       // 수식(MathJax)이 다 그려져 높이가 바뀐 뒤에
  const toFocus = () => page.evaluate(s => { const el = document.querySelector(s); window.scrollBy(0, el.getBoundingClientRect().top - 16); }, focus);
  if (focus) { await toFocus(); await page.waitForTimeout(700); await toFocus(); }
  await page.waitForTimeout(500);
  await page.mouse.move(VW / 2, VH / 2);
  STARTS[name] = (Date.now() - t0) / 1000;
  try { await act(page); } catch (e) { console.error(name, '실패:', e.message.split('\n')[0]); }
  await page.waitForTimeout(600);
  if (focus) { const bb = await page.locator(focus).first().boundingBox().catch(() => null); if (bb) BOXES[name] = bb; }
  const v = page.video(); await ctx.close();
  fs.renameSync(await v.path(), `${OUT}/${name}.webm`); console.log(name);
}
async function moveTo(page, loc) { const bb = await loc.boundingBox(); await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2, { steps: 18 }); return bb; }
async function clickSel(page, sel) { const b = page.locator(sel).first(); await moveTo(page, b); await b.click(); }
// 슬라이더 손잡이를 실제로 끌어서 from→to (0~1 위치)
async function slide(page, sel, from, to, ms = 1400) {
  const r = await page.locator(sel).first().boundingBox(); const y = r.y + r.height / 2, x = f => r.x + 8 + (r.width - 16) * f;
  await page.mouse.move(x(from), y, { steps: 15 }); await page.mouse.down();
  await page.mouse.move(x(to), y, { steps: Math.round(ms / 16) }); await page.mouse.up();
}
// Plane 캔버스 위 좌표(world) → 화면 좌표 (range 는 섹션마다 다름)
async function planeXY(p, sel, range, w) {
  const bb = await p.locator(sel).first().boundingBox(); const s = bb.width / (2 * range);
  return [bb.x + bb.width / 2 + w[0] * s, bb.y + bb.height / 2 - w[1] * s];
}
async function drag(p, a, b, steps = 60) { await p.mouse.move(a[0], a[1], { steps: 20 }); await p.waitForTimeout(250); await p.mouse.down(); await p.mouse.move(b[0], b[1], { steps }); await p.mouse.up(); }
const nextBtn = (host) => `${host} [data-s="next"]`;
(async () => {
  const browser = await chromium.launch({ args: ['--ignore-certificate-errors'] });
  BASE = CIRCUIT;   // 첫 인자 = 선형대수 사이트
  await clip(browser, 'l_lsq', 'lsq', '.lab:has(#ls-viz)', async (p) => {
    const cv = '#ls-viz canvas', R = 4.5;
    await p.waitForTimeout(1200);
    await drag(p, await planeXY(p, cv, R, [2.5, 2.5]), await planeXY(p, cv, R, [2.5, -0.5]), 70); await p.waitForTimeout(1200);
    await drag(p, await planeXY(p, cv, R, [2.5, -0.5]), await planeXY(p, cv, R, [2.5, 2.5]), 70); await p.waitForTimeout(1200);
    await drag(p, await planeXY(p, cv, R, [-3, -1.5]), await planeXY(p, cv, R, [-3, 1]), 60); await p.waitForTimeout(1000);
    await drag(p, await planeXY(p, cv, R, [-3, 1]), await planeXY(p, cv, R, [-3, -1.5]), 60); await p.waitForTimeout(2000);
  });
  await clip(browser, 'l_3d', 'lsq', '#ls-3d-card', async (p) => {
    await p.evaluate(() => { document.querySelector('#ls-del').click(); document.querySelector('#ls-del').click(); });
    await p.waitForTimeout(800);
    await p.evaluate(() => { const el = document.querySelector('#ls-3d-card'); window.scrollBy(0, el.getBoundingClientRect().top - 16); });
    await p.waitForTimeout(800);
    const bb = await p.locator('#ls-3d canvas').first().boundingBox(); const cx = bb.x + bb.width / 2, cy = bb.y + bb.height / 2;
    await drag(p, [cx - 120, cy], [cx + 160, cy - 20], 120); await p.waitForTimeout(800);
    await drag(p, [cx + 160, cy - 20], [cx - 60, cy + 10], 120); await p.waitForTimeout(1500);
  });
  await clip(browser, 'g_gs', 'gs', '.lab:has(#gs-viz)', async (p) => {
    await p.waitForTimeout(1200);
    for (let i = 0; i < 6; i++) { await clickSel(p, nextBtn('#gs-step')); await p.waitForTimeout(1700); }
    const bb = await p.locator('#gs-viz canvas').first().boundingBox(); const cx = bb.x + bb.width / 2, cy = bb.y + bb.height / 2;
    await drag(p, [cx - 100, cy], [cx + 120, cy - 10], 110); await p.waitForTimeout(1500);
  });
  await clip(browser, 'd_diag', 'diag', '.lab:has(#dg-viz)', async (p) => {
    await p.waitForTimeout(1200);
    for (let i = 0; i < 3; i++) { await clickSel(p, nextBtn('#dg-step')); await p.waitForTimeout(2200); }
    await p.waitForTimeout(800);
  });
  await clip(browser, 'd_pow', 'diag', 'details:has(#dg-pow)', async (p) => {
    await p.waitForTimeout(1000);
    await slide(p, '#dg-k', 4 / 9, 1, 1800); await p.waitForTimeout(3500);
  });
  await clip(browser, 'i_inv', 'inverse', '.lab:has(#iv-viz)', async (p) => {
    await p.waitForTimeout(1000);
    await clickSel(p, '#iv-play'); await p.waitForTimeout(4500);
    await clickSel(p, '#iv-play'); await p.waitForTimeout(4500);
  });
  await clip(browser, 'i_gj', 'inverse', '.card:has(#iv-step)', async (p) => {
    await p.waitForTimeout(1000);
    for (let i = 0; i < 6; i++) { await clickSel(p, nextBtn('#iv-step')); await p.waitForTimeout(1500); }
    await p.waitForTimeout(1000);
  });
  await browser.close();
  const bf = `${OUT}/boxes.json`, old = fs.existsSync(bf) ? JSON.parse(fs.readFileSync(bf, 'utf8')) : {};
  fs.writeFileSync(bf, JSON.stringify(Object.assign(old, BOXES, { _viewport: [VW, VH], _start: Object.assign(old._start || {}, STARTS) }), null, 1));
})();
