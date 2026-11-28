// 릴스 커버 PNG: node render.js  (A.png·B.png·C.png = 모션그래픽 대표 프레임, ../mg/render.js --sheet 로 뽑아 둔다)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 3400, height: 1960 } });
  await p.goto('file://' + __dirname + '/covers.html'); await p.waitForTimeout(800);
  for (const id of ['A', 'B', 'C']) await p.locator('#' + id).screenshot({ path: __dirname + '/cover_' + id + '.png' });
  await b.close(); })();
