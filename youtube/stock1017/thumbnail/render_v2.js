const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 2200 } });
  await p.goto('file://' + __dirname + '/thumbs_v2.html'); await p.waitForTimeout(800);
  for (const id of ['V1','V2','V3']) await p.locator('#' + id).screenshot({ path: __dirname + '/thumb_' + id + '.png' });
  await b.close(); })();
