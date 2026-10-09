// 보이는 회로이론 화면을 다크 모드로 직접 조작하며 녹화한다 (영상 B롤용).
// 사용: NODE_PATH=<playwright>/node_modules node record.js <사이트 html 경로 또는 주소> <출력 폴더> [클립,...]
const { chromium } = require('playwright');
const fs = require('fs');
const [,, SRC, OUT, ONLY_ARG] = process.argv;
const BASE = /^https?:/.test(SRC) ? SRC : 'file://' + require('path').resolve(SRC);
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
const pos = (sel) => (page) => page.locator(sel).first().evaluate(el => el.value / 1000);

(async () => {
  const browser = await chromium.launch({ args: ['--ignore-certificate-errors'] });
  await clip(browser, 'home', 'home', null, async (p) => {
    await p.waitForTimeout(2500);
    for (let i = 0; i < 6; i++) { await p.mouse.wheel(0, 140); await p.waitForTimeout(220); }
    await p.waitForTimeout(1500);
  });
  await clip(browser, 'toc', 'home', null, async (p) => {       // 왼쪽 목차 1~17장 훑기
    const items = p.locator('.side a.ch'); const n = await items.count();
    for (let i = 0; i < n; i++) { await moveTo(p, items.nth(i)); await p.waitForTimeout(90); }
    await p.waitForTimeout(800);
  });
  await clip(browser, 'ch2', 'ch2', '#lab-ohm', async (p) => {
    const s = '#ohm-ctl-R1'; const f = await pos(s)(p);
    await slide(p, s, f, 0.95, 1800); await p.waitForTimeout(1500);
    await slide(p, s, 0.95, f, 1200); await p.waitForTimeout(800);
    await clickSel(p, '#lab-ohm [data-mode="parallel"]'); await p.waitForTimeout(3500);
  });
  await clip(browser, 'ch7', 'ch7', '#lab-tr', async (p) => {
    await clickSel(p, '#lab-tr [data-act="restart"]'); await p.waitForTimeout(5000);
    await clickSel(p, '#lab-tr [data-kind="RL"]'); await p.waitForTimeout(400);
    await clickSel(p, '#lab-tr [data-act="restart"]'); await p.waitForTimeout(4500);
  });
  await clip(browser, 'ch9wave', 'ch9', '#lab-wave', async (p) => { await p.waitForTimeout(7000); });
  await clip(browser, 'ch9res', 'ch9', '#lab-imp', async (p) => {
    await p.waitForTimeout(1800); await clickSel(p, '#lab-imp [data-act="res"]'); await p.waitForTimeout(5000);
  });
  await clip(browser, 'ch8', 'ch8', '#lab-rlc2', async (p) => {
    const s = '#rlc2-ctl-R'; await slide(p, s, await pos(s)(p), 0.62, 1500); await p.waitForTimeout(900);
    await slide(p, s, 0.62, 0.08, 2200); await p.waitForTimeout(1800);
    await clickSel(p, '#lab-rlc2 [data-act="crit"]'); await p.waitForTimeout(3500);
  });
  await clip(browser, 'ch16', 'ch16', '#lab-fs', async (p) => {
    await clickSel(p, '#lab-fs [data-act="build"]'); await p.waitForTimeout(9000);
  });
  await clip(browser, 'ch14num', 'ch14', '#lab-bode', async (p) => {
    const n = p.locator('#bode-ctl-f-n'); await moveTo(p, n); await n.click({ clickCount: 3 });
    await p.keyboard.type('200', { delay: 260 }); await p.keyboard.press('Enter'); await n.dispatchEvent('change'); await p.waitForTimeout(1800);
    await n.click({ clickCount: 3 }); await p.keyboard.type('20000', { delay: 220 }); await p.keyboard.press('Enter'); await n.dispatchEvent('change'); await p.waitForTimeout(2200);
  });
  await browser.close();
  const bf = `${OUT}/boxes.json`, old = fs.existsSync(bf) ? JSON.parse(fs.readFileSync(bf, 'utf8')) : {};
  fs.writeFileSync(bf, JSON.stringify(Object.assign(old, BOXES, { _viewport: [VW, VH], _start: Object.assign(old._start || {}, STARTS) }), null, 1));
})();
