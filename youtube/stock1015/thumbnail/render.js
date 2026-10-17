const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 1920 } });
  await p.goto('file://' + __dirname + '/covers.html'); await p.waitForTimeout(800);
  await p.locator('#L').screenshot({ path: __dirname + '/thumb_long.png' });
  for (const id of ['A','B','C']) await p.locator('#' + id).screenshot({ path: __dirname + '/cover_' + id + '.png' });
  await b.close(); })();
