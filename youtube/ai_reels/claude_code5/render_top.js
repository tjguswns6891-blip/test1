// 위쪽 애니메이션 장면을 장면별 mp4 로 뽑는다.
// node render_top.js <출력폴더> [초=5] [fps=30]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const out = process.argv[2] || 'out';
const secs = Number(process.argv[3] || 5), fps = Number(process.argv[4] || 30);

(async () => {
  require('fs').mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 880 } });
  await page.goto('file://' + path.resolve(__dirname, 'top.html'));
  await page.evaluate(() => document.fonts.ready);
  for (let s = 0; s < 6; s++) {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', path.join(out, `top_${s}.mp4`)]);
    for (let f = 0; f < secs * fps; f++) {
      await page.evaluate(([s, t]) => render(s, t), [s, f / fps]);
      ff.stdin.write(await page.screenshot({ type: 'png' }));
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('scene', s, 'done');
  }
  await browser.close();
})();
