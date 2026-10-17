// 회로 쇼츠 2탄(실효값·푸리에·RC 필터·공진): 보이는 회로이론 9·11·14·16장을 다크 모드로 조작하며 녹화한다.
// 사용: NODE_PATH=<playwright>/node_modules node record.js <회로 사이트 html> <출력 폴더> [클립,...]
// 선형대수는 LINALG 환경변수(기본: ../raw/linalg_site/index.html, 사이트 파일을 받아 둔 곳)
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
const pos = (sel) => (page) => page.locator(sel).first().evaluate(el => el.value / 1000);

async function setNum(p, id, v) {                       // 슬라이더 옆 숫자 칸에 값을 직접 입력
  const n = p.locator(`[id="${id}-n"]`); await moveTo(p, n); await n.click({ clickCount: 3 });
  await p.keyboard.type(String(v), { delay: 220 }); await p.keyboard.press('Enter'); await n.dispatchEvent('change');
}
(async () => {
  const browser = await chromium.launch({ args: ['--ignore-certificate-errors'] });
  await clip(browser, 'v_pw', 'ch11', '#lab-pw', async (p) => {
    await p.waitForTimeout(1200);
    await setNum(p, 'pw-ctl-Vm', 20); await p.waitForTimeout(2500);
    await setNum(p, 'pw-ctl-th', 0); await p.waitForTimeout(2500);
    const r = p.locator('#lab-pw .readout').getByText('실효값').first(); await moveTo(p, r).catch(() => {}); await p.waitForTimeout(3500);
  });
  await clip(browser, 'f_fs', 'ch16', '#lab-fs', async (p) => {
    await p.waitForTimeout(1000);
    await setNum(p, 'fs-ctl-N', 1); await p.waitForTimeout(1500);
    for (const n of [3, 5, 7, 9]) { await setNum(p, 'fs-ctl-N', n); await p.waitForTimeout(1300); }
    await setNum(p, 'fs-ctl-N', 49); await p.waitForTimeout(3500);
  });
  await clip(browser, 'h_bode', 'ch14', '#lab-bode', async (p) => {
    await p.waitForTimeout(1200);
    await setNum(p, 'bode-ctl-f', 100); await p.waitForTimeout(2500);
    await setNum(p, 'bode-ctl-f', 1590); await p.waitForTimeout(2500);
    await setNum(p, 'bode-ctl-f', 10000); await p.waitForTimeout(3000);
  });
  await clip(browser, 'q_imp', 'ch9', '#lab-imp', async (p) => {
    await p.waitForTimeout(1200);
    await setNum(p, 'imp-ctl-R', 20); await p.waitForTimeout(1800);
    await clickSel(p, '#lab-imp [data-act="res"]'); await p.waitForTimeout(4500);
    const r = p.locator('#lab-imp .readout').getByText('소자 전압').first(); await moveTo(p, r).catch(() => {}); await p.waitForTimeout(3000);
  });
  await browser.close();
  const bf = `${OUT}/boxes.json`, old = fs.existsSync(bf) ? JSON.parse(fs.readFileSync(bf, 'utf8')) : {};
  fs.writeFileSync(bf, JSON.stringify(Object.assign(old, BOXES, { _viewport: [VW, VH], _start: Object.assign(old._start || {}, STARTS) }), null, 1));
})();
