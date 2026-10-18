// cards.html 의 카드(section.card[data-file])를 1920×1080 PNG로 저장한다.
// 사용: NODE_PATH=<playwright 설치 폴더>/node_modules node render.js
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'cards.html'));
  await page.evaluate(() => document.fonts.ready);
  const outDir = path.join(__dirname, '..', 'img');
  const names = await page.$$eval('section.card', els => els.map(e => e.dataset.file));
  for (const name of names) {
    await page.locator(`section.card[data-file="${name}"]`).screenshot({ path: path.join(outDir, name + '.png') });
    console.log(name + '.png');
  }
  await browser.close();
})();
