const { chromium } = require('/root/.cache/pw/node_modules/playwright');
(async () => {
  const dir = __dirname;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  for (let i = 1; i <= 7; i++) {
    await p.goto('file://' + dir + '/html/' + i + '.html');
    await p.waitForTimeout(150);
    await p.screenshot({ path: dir + '/png/card_' + i + '.png' });
  }
  await b.close();
})();
