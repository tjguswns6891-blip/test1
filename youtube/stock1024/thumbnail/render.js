// 썸네일·커버 PNG 만들기: node render.js
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 1920 } });
  await p.goto('file://' + __dirname + '/thumbs.html'); await p.waitForTimeout(800);
  for (const id of ['V1', 'V2', 'V3']) await p.locator('#' + id).screenshot({ path: __dirname + '/thumb_' + id + '.png' });
  for (const id of ['A', 'B', 'C', 'D', 'E']) await p.locator('#' + id).screenshot({ path: __dirname + '/cover_' + id + '.png' });
  await b.close(); })();
