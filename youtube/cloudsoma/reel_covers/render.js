const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + __dirname + '/covers.html'); await p.waitForTimeout(800);
  for (const id of ['A','B','C','D']) await p.locator('#' + id).screenshot({ path: __dirname + '/paf_cover_' + id + '.png' });
  await b.close(); })();
