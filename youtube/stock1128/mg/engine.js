// 증시 2026-11-28 모션그래픽 엔진 (Canvas 2D, 1080×840 = faceless.py 그래픽 칸 크기 그대로).
// 모든 그림은 시각 t 의 순수 함수라서, 프레임마다 draw(clip, t) → 스크린샷으로 정확히 렌더한다 (render.js).
const W = 1080, H = 840;
const C = { bg: '#111318', ink: '#eef0f3', mute: '#8d94a1', dim: '#5b616d', yel: '#ffc53d', up: '#ff5d73', dn: '#6ea8ff',
  grn: '#3ddc97', org: '#ff9f43', pur: '#c792ff', card: '#181b21', card2: '#1e222a', line: '#2a2e37' };
let ctx;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const back = x => { x = clamp(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const P = (t, s, d = .45) => clamp((t - s) / d);
const lerp = (a, b, k) => a + (b - a) * k;
const FONT = '"Noto Sans CJK KR"';
function setFont(size, weight = 700) { ctx.font = `${weight} ${size}px ${FONT}`; }
function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
function text(str, x, y, o = {}) {
  const { size = 40, color = C.ink, weight = 700, align = 'center', alpha = 1, base = 'middle', glow = 0, ls = 0 } = o;
  if (alpha <= 0) return 0;
  ctx.save(); ctx.globalAlpha *= alpha; setFont(size, weight); ctx.textAlign = align; ctx.textBaseline = base; ctx.fillStyle = color;
  if (ls) ctx.letterSpacing = ls + 'px';
  if (glow) { ctx.shadowColor = hexA(color.startsWith('#') ? color : '#ffffff', .75); ctx.shadowBlur = glow; }
  ctx.fillText(str, x, y); const w = ctx.measureText(str).width; ctx.restore(); return w;
}
function measure(str, size, weight = 700) { ctx.save(); setFont(size, weight); const w = ctx.measureText(str).width; ctx.restore(); return w; }
// 색이 섞인 한 줄: parts = [[글, 색, 크기?, 굵기?], ...]
function rich(parts, x, y, o = {}) {
  const { size = 40, weight = 700, align = 'center', alpha = 1, gap = 0 } = o;
  const ws = parts.map(p => measure(p[0], p[2] || size, p[3] || weight));
  const total = ws.reduce((a, b) => a + b, 0) + gap * (parts.length - 1);
  let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
  parts.forEach((p, i) => { text(p[0], cx, y, { size: p[2] || size, weight: p[3] || weight, color: p[1] || C.ink, align: 'left', alpha, base: o.base || 'middle' }); cx += ws[i] + gap; });
  return total;
}
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function box(x, y, w, h, o = {}) {
  const { r = 22, fill = C.card, stroke = C.line, lw = 2, alpha = 1, glow = 0, glowColor } = o;
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  if (glow) { ctx.shadowColor = hexA(glowColor || stroke, .55); ctx.shadowBlur = glow; }
  rr(x, y, w, h, r); if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  ctx.shadowBlur = 0; if (stroke && lw) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
  ctx.restore();
}
function chip(str, x, y, o = {}) {      // 가운데 정렬 알약
  const { size = 28, fg = '#111318', bg = C.yel, padX = 18, h = size * 1.7, alpha = 1, weight = 800, stroke = null, align = 'center' } = o;
  const w = measure(str, size, weight) + padX * 2; const x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  box(x0, y - h / 2, w, h, { r: h / 2, fill: bg, stroke, lw: stroke ? 2 : 0, alpha });
  text(str, x0 + w / 2, y + 1, { size, color: fg, weight, alpha }); return w;
}
// 나타나기: 아래에서 살짝 올라오며 또렷해진다
function appear(t, s, fn, o = {}) {
  const { dy = 26, d = .42, scale = 0, ox = W / 2, oy = H / 2 } = o; const k = P(t, s, d); if (k <= 0) return;
  const e = eo(k); ctx.save(); ctx.globalAlpha *= e; ctx.translate(0, (1 - e) * dy);
  if (scale) { const sc = lerp(scale, 1, back(k)); ctx.translate(ox, oy); ctx.scale(sc, sc); ctx.translate(-ox, -oy); }
  fn(e); ctx.restore();
}
function pop(t, s, ox, oy, fn, d = .5) {  // 튀어나오기 (숫자 도장)
  const k = P(t, s, d); if (k <= 0) return; const sc = lerp(.55, 1, back(k));
  ctx.save(); ctx.globalAlpha *= eo(k * 2.2); ctx.translate(ox, oy); ctx.scale(sc, sc); ctx.translate(-ox, -oy); fn(k); ctx.restore();
}
function fade(a, fn) { if (a <= 0) return; ctx.save(); ctx.globalAlpha *= clamp(a); fn(); ctx.restore(); }
const sgn = (v, d = 1) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(d) + '%';
const comma = v => Math.round(v).toLocaleString('en-US');
const colOf = v => v >= 0 ? C.up : C.dn;      // 한국식: 오르면 빨강, 내리면 파랑
function line(x1, y1, x2, y2, o = {}) {
  const { color = C.mute, lw = 2, dash = null, alpha = 1, glow = 0, cap = 'round' } = o; if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = cap; if (dash) ctx.setLineDash(dash);
  if (glow) { ctx.shadowColor = hexA(color, .8); ctx.shadowBlur = glow; }
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); ctx.restore();
}
function arrow(x1, y1, x2, y2, o = {}) {
  const { color = C.ink, lw = 5, head = 16, alpha = 1 } = o; if (alpha <= 0) return;
  const a = Math.atan2(y2 - y1, x2 - x1); line(x1, y1, x2 - Math.cos(a) * head * .6, y2 - Math.sin(a) * head * .6, { color, lw, alpha });
  ctx.save(); ctx.globalAlpha *= alpha; ctx.fillStyle = color; ctx.beginPath(); ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - Math.cos(a - .45) * head, y2 - Math.sin(a - .45) * head); ctx.lineTo(x2 - Math.cos(a + .45) * head, y2 - Math.sin(a + .45) * head); ctx.closePath(); ctx.fill(); ctx.restore();
}
function dot(x, y, r, color, o = {}) {
  const { alpha = 1, glow = 0, ring = null } = o; if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha; if (glow) { ctx.shadowColor = hexA(color, .9); ctx.shadowBlur = glow; }
  ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); ctx.shadowBlur = 0;
  if (ring) { ctx.strokeStyle = ring; ctx.lineWidth = 3; ctx.stroke(); } ctx.restore();
}
// 꺾은선: pts=[[x,y],...] 를 진행도 prog(0~1, 길이 기준)까지 그린다. 끝점 좌표를 돌려준다.
function path(pts, prog, o = {}) {
  const { color = C.ink, lw = 5, glow = 0, alpha = 1, fillTo = null, fillColor = null, dash = null } = o;
  if (prog <= 0 || pts.length < 2) return pts[0];
  const segs = []; let L = 0; for (let i = 1; i < pts.length; i++) { const l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); segs.push(l); L += l; }
  let remain = L * clamp(prog); const out = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    if (remain >= segs[i - 1]) { out.push(pts[i]); remain -= segs[i - 1]; }
    else { const k = remain / segs[i - 1]; out.push([lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k)]); break; }
  }
  ctx.save(); ctx.globalAlpha *= alpha;
  if (fillTo != null) {
    const g = ctx.createLinearGradient(0, Math.min(...pts.map(p => p[1])), 0, fillTo); g.addColorStop(0, hexA(fillColor || color, .32)); g.addColorStop(1, hexA(fillColor || color, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(out[0][0], fillTo); out.forEach(p => ctx.lineTo(p[0], p[1])); ctx.lineTo(out[out.length - 1][0], fillTo); ctx.closePath(); ctx.fill();
  }
  ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; if (dash) ctx.setLineDash(dash);
  if (glow) { ctx.shadowColor = hexA(color, .8); ctx.shadowBlur = glow; }
  ctx.beginPath(); out.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke(); ctx.restore();
  return out[out.length - 1];
}
function scaler(vals, y0, y1, pad = .08) { const mn = Math.min(...vals), mx = Math.max(...vals), p = (mx - mn) * pad; return v => lerp(y1, y0, (v - (mn - p)) / ((mx + p) - (mn - p))); }
function kicker(str, t, s = 0, color = C.mute) {   // 장면 머리말 (왼쪽 위 작은 글씨 + 점)
  const a = eo(P(t, s, .3)); dot(60, 58, 7, C.yel, { alpha: a, glow: 10 }); text(str, 80, 60, { size: 30, color, weight: 700, align: 'left', alpha: a });
}
function bg() {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, 260, 60, W / 2, 260, 760); g.addColorStop(0, 'rgba(110,168,255,.07)'); g.addColorStop(1, 'rgba(110,168,255,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalAlpha = .05; ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1;
  for (let x = 60; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 60; y < H; y += 60) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();
}
// ── 타이밍: TM = {S:[문장 시작초...], end, K:{"문장번호:키워드": 초}} ──
let TM = null;
const S = i => TM.S[Math.min(i, TM.S.length - 1)];
const K = (i, w, f = .5) => (TM.K && TM.K[i + ':' + w] != null) ? TM.K[i + ':' + w] : lerp(S(i), i + 1 < TM.S.length ? TM.S[i + 1] : TM.end, f);
// 장면 목록 [{from: 문장번호, to: 문장번호(포함 안 함), draw(t)}] 을 0.22초 겹쳐 넘긴다
function play(scenes, t) {
  bg();
  for (const sc of scenes) {
    const a = S(sc.from), b = sc.to >= TM.S.length ? TM.end + 9 : S(sc.to);
    const fin = sc.from === 0 ? 1 : P(t, a - .12, .24), fout = 1 - P(t, b - .12, .24);
    const al = Math.min(fin, fout); if (al <= 0) continue;
    ctx.save(); ctx.globalAlpha = al; sc.draw(t); ctx.restore();
  }
}
