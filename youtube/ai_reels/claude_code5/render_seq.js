// 장면 순서와 길이대로 위쪽 애니메이션을 한 파일로 뽑는다.
// node render_seq.js <plan.json: [[장면, 초], ...]> <출력.mp4> [fps=30]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const plan = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const out = process.argv[3], fps = Number(process.argv[4] || 30);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 880 } });
  await page.goto('file://' + path.resolve(__dirname, 'top.html'));
  await page.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', out]);
  let frame = 0, start = 0;
  for (const [scene, dur] of plan) {
    const end = start + dur;
    // 누적 시간 기준으로 프레임을 나눠 반올림 오차가 쌓이지 않게 한다
    for (; frame < Math.round(end * fps); frame++) {
      await page.evaluate(([s, t]) => render(s, t), [scene, frame / fps - start]);
      ff.stdin.write(await page.screenshot({ type: 'png' }));
    }
    start = end;
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('frames', frame);
})();
