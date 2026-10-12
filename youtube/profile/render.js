const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.goto('file://' + __dirname + '/profile.html'); await p.waitForTimeout(400);
  for (const id of ['A','B','C']) await p.locator('#' + id).screenshot({ path: __dirname + '/profile_' + id + '.png' });
  await b.close(); })();
