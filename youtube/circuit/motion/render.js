// motion.html 의 카드(section.card[data-file])를 시간대로 한 프레임씩 찍어 1920×1080 mp4 로 만든다.
// 마지막 화면은 PNG 로도 남긴다 (compose.py 정지 카드용).
// 사용: NODE_PATH=<playwright 설치 폴더>/node_modules FFMPEG=<ffmpeg 경로> node render.js [카드이름,...]
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');
const FPS = 30;

(async () => {
  const only = process.argv[2] ? new Set(process.argv[2].split(',')) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'motion.html'));
  await page.evaluate(() => document.fonts.ready);
  const outDir = path.join(__dirname, '..', 'img');
  const cards = await page.$$eval('section.card', els => els.map(e => [e.dataset.file, +e.dataset.dur]));
  for (const [name, dur] of cards) {
    if (only && !only.has(name)) continue;
    const loc = page.locator(`section.card[data-file="${name}"]`);
    await loc.scrollIntoViewIfNeeded();
    const ff = spawn(process.env.FFMPEG || 'ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y',
      '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
      path.join(outDir, name + '.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise(r => ff.on('close', r));
    const n = Math.round(dur * FPS);
    for (let f = 0; f < n; f++) {
      await page.evaluate(([n, t]) => setT(document.querySelector(`section.card[data-file="${n}"]`), t), [name, f / FPS]);
      const buf = await loc.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await done;
    await loc.screenshot({ path: path.join(outDir, name + '.png') });
    console.log(`${name}.mp4 (${dur}s) + .png`);
  }
  await browser.close();
})();
