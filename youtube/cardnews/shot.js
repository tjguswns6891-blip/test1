// node shot.js <폴더> <장수> : 폴더/N.html → 폴더/card_N.png (1080x1350)
const path = require('path');
let pw; try { pw = require('playwright'); } catch { pw = require('/root/.cache/pw/node_modules/playwright'); }
(async () => {
  const [dir, n] = [path.resolve(process.argv[2]), +process.argv[3]];
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  for (let i = 1; i <= n; i++) {
    await p.goto('file://' + dir + '/' + i + '.html');
    await p.waitForTimeout(150);
    await p.screenshot({ path: dir + '/card_' + i + '.png' });
  }
  await b.close();
})();
