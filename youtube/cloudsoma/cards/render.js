// cards.html 의 카드(section.card)를 1920×1080 PNG로 저장한다.
// 사용: NODE_PATH=<playwright 설치 폴더>/node_modules node render.js
const path = require('path');
const { chromium } = require('playwright');

const NAMES = {
  c01: 'card-01-hook', c02: 'card-02-paf', c03: 'card-03-timeline', c04: 'card-04-concept',
  c05: 'card-05-tech', c06: 'card-06-colors', c07: 'card-07-price', c08: 'card-08-lacing',
  c09: 'card-09-monument', c10: 'card-10-buy', c11: 'card-11-summary', c12: 'card-12-on', c13: 'card-13-student-price', c14: 'card-14-run-style',
};

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'cards.html'));
  await page.evaluate(() => document.fonts.ready);
  const outDir = path.join(__dirname, '..', 'img');
  for (const [id, name] of Object.entries(NAMES)) {
    await page.locator('#' + id).screenshot({ path: path.join(outDir, name + '.png') });
    console.log(name + '.png');
  }
  await browser.close();
})();
