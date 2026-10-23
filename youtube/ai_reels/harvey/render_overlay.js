// 장면 계획대로 overlay.html 을 프레임마다 찍어 투명 영상(mov, png 코덱)으로 만든다.
// node render_overlay.js plan.json out.mov [fps]   plan = [[장면 이름 또는 null, 초], ...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [planPath, out, fpsArg] = process.argv.slice(2);
  const plan = JSON.parse(fs.readFileSync(planPath)), fps = +(fpsArg || 30);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'overlay.html'));
  await p.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'png', '-pix_fmt', 'rgba', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  let blank = null, acc = 0, done = 0;
  for (const [name, sec] of plan) {
    acc += sec;
    const n = Math.round(acc * fps) - done;   // 누적 반올림으로 길이 오차가 쌓이지 않게
    for (let i = 0; i < n; i++) {
      if (!name) {
        if (!blank) { await p.evaluate(() => render(null, 0, 1)); blank = await p.screenshot({ omitBackground: true }); }
        if (!ff.stdin.write(blank)) await new Promise(r => ff.stdin.once('drain', r));
        continue;
      }
      await p.evaluate(([nm, t, d]) => render(nm, t, d), [name, i / fps, sec]);
      const png = await p.screenshot({ omitBackground: true });
      if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
    }
    done += n;
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log('frames', done);
})();
