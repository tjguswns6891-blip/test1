const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 2400 } });
  await p.goto('file://' + __dirname + '/thumbs.html'); await p.waitForTimeout(800);
  await p.locator('#V1').screenshot({ path: __dirname + '/thumb_V1.png' });
  const ids = ['A', 'B', 'C', 'D', 'E'];
  for (let i = 0; i < ids.length; i++) await p.locator('#' + ids[i]).screenshot({ path: __dirname + '/cover_' + (i + 1) + '.png' });
  await b.close(); })();
