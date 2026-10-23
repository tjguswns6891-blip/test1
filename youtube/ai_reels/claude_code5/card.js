// cta_card.html 을 투명 PNG 로 굽는다: node card.js <출력 png>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'cta_card.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: process.argv[2] || 'cta_card.png', omitBackground: true });
  await b.close();
})();
