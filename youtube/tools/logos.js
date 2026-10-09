// simple-icons(npm, CC0 아이콘 모음)의 회사 로고 SVG 를 썸네일용 PNG 로 만든다.
// 글자 부분만 딱 맞게 자르고, 브랜드 색(<slug>.png)과 흰색(<slug>_white.png) 두 벌을 youtube/logos/ 에 둔다.
// 사용: npm pack simple-icons && tar xzf simple-icons-*.tgz
//       SI_DIR=package NODE_PATH=<playwright>/node_modules node logos.js samsung openai nvidia
// 로고는 각 회사의 상표다. 뉴스·시황 영상에서 해당 회사를 가리키는 용도로만 쓴다.
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const H = 300;

(async () => {
  const si = process.env.SI_DIR || 'package';
  const data = JSON.parse(fs.readFileSync(path.join(si, '_data', 'simple-icons.json'), 'utf8'));
  const list = Array.isArray(data) ? data : data.icons;
  const slugOf = t => t.toLowerCase().replace(/\+/g, 'plus').replace(/\./g, 'dot').replace(/&/g, 'and')
    .normalize('NFD').replace(/[^a-z0-9]/g, '');
  const out = path.join(__dirname, '..', 'logos');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 600 } });
  for (const slug of process.argv.slice(2)) {
    const icon = list.find(i => (i.slug || slugOf(i.title)) === slug);
    const svg = fs.readFileSync(path.join(si, 'icons', slug + '.svg'), 'utf8');
    const d = svg.match(/ d="([^"]+)"/)[1];
    for (const [suffix, color] of [['', '#' + icon.hex], ['_white', '#ffffff']]) {
      await page.setContent(`<body style="margin:0;background:transparent">
        <svg id="s" xmlns="http://www.w3.org/2000/svg"><path id="p" d="${d}" fill="${color}"/></svg></body>`);
      const box = await page.evaluate(h => {
        const p = document.getElementById('p'), b = p.getBBox(), k = h / b.height, s = document.getElementById('s');
        s.setAttribute('viewBox', `${b.x} ${b.y} ${b.width} ${b.height}`);
        s.setAttribute('width', b.width * k); s.setAttribute('height', h);
        return { w: Math.ceil(b.width * k), h };
      }, H);
      await page.locator('#s').screenshot({ path: path.join(out, slug + suffix + '.png'), omitBackground: true });
      console.log(`${slug}${suffix}.png ${box.w}×${box.h}`);
    }
  }
  await browser.close();
})();
