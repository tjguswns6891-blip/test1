// 모션그래픽 렌더: node render.js <A|B|C> <timing.json> <out.mp4>  |  미리보기: node render.js A timing.json sheet.png --sheet 0.5,2,4,...
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs'); const path = require('path');
const [,, clip, tmf, out, mode, arg] = process.argv;
(async () => {
  const tm = JSON.parse(fs.readFileSync(tmf, 'utf8'))[clip];
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 840 }, deviceScaleFactor: 1 });
  pg.on('pageerror', e => console.error('PAGE', e.message));
  await pg.goto('file://' + path.join(__dirname, 'index.html')); await pg.evaluate(() => window.ready); await pg.evaluate(t => window.setTiming(t), tm);
  if (mode === '--sheet') {
    const dir = out.replace(/\.png$/, '_f'); fs.mkdirSync(dir, { recursive: true }); const ts = arg.split(',').map(Number);
    for (let i = 0; i < ts.length; i++) { await pg.evaluate(([c, t]) => window.draw(c, t), [clip, ts[i]]); await pg.screenshot({ path: `${dir}/${String(i).padStart(3, '0')}.png` }); }
    await b.close(); return;
  }
  const fps = 30, n = Math.ceil((tm.end + .6) * fps);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    await pg.evaluate(([c, t]) => window.draw(c, t), [clip, i / fps]);
    const buf = await pg.screenshot({ type: 'png' }); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log(out, n, 'frames');
})();
