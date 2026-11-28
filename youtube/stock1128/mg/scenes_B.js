// B · 거시 관점과 대처: 주가는 반등했는데 금리 인상 확률 90%+  (숫자 출처: ../script.json "_출처")
function gauge(cx, cy, r, k, color, lw = 30) {   // 반원 게이지 (0~1)
  ctx.save(); ctx.lineCap = 'round'; ctx.lineWidth = lw; ctx.strokeStyle = '#262a33'; ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI); ctx.stroke();
  if (k > 0) { ctx.strokeStyle = color; ctx.shadowColor = hexA(color, .8); ctx.shadowBlur = 24; ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, Math.PI * (1 + clamp(k))); ctx.stroke(); }
  ctx.restore();
}
function B0(t) {   // 0: 주가 +5.6% vs 금리 인상 확률 90%+
  kicker('주가는 반등 · 그런데 금리는?', t);
  box(60, 130, 440, 600, { fill: C.card });
  text('S&P 500', 280, 200, { size: 44, weight: 900 }); text('이번 주', 280, 250, { size: 26, color: C.mute, weight: 500 });
  const k0 = eo(P(t, 0, .9)), d = DATA.spx.slice(-6), sy = scaler(d.map(x => x[1]), 320, 500, .1);
  path(d.map((x, i) => [110 + i * 68, sy(x[1])]), .3 + .7 * k0, { color: C.up, lw: 8, glow: 16, fillTo: 520 });
  text('+' + (5.6 * (.3 + .7 * k0)).toFixed(1) + '%', 280, 620, { size: 96, color: C.up, weight: 900, glow: 14 });
  const tg = K(0, '인상', .42), tn = K(0, '90%', .68), tm = K(0, '시장은', .25);
  box(540, 130, 480, 600, { fill: '#1b1a12', stroke: t >= tg - .2 ? C.yel : C.line, lw: 3, glow: t >= tg - .2 ? 26 * eo(P(t, tg - .2, .5)) : 0 });
  text('12월 미국 금리', 780, 200, { size: 40, weight: 900 });
  rich([['인상', C.yel], [' 확률', C.ink]], 780, 256, { size: 40, weight: 900 });
  const gk = eio(P(t, tm, tn - tm + .25)) * .93; gauge(780, 520, 170, gk, C.yel, 34);
  text(t < tm ? '?' : Math.round(gk / .93 * 90) + '%', 780, 490, { size: 110, color: C.yel, weight: 900, glow: 16 });
  pop(t, tn + .1, 780, 610, () => chip('90% 넘음 · CME 페드워치', 780, 620, { size: 26, bg: C.yel }));
  text('0', 600, 560, { size: 22, color: C.mute }); text('100', 962, 560, { size: 22, color: C.mute });
}
function B1(t) {   // 1: 기준금리 3.75~4.00% · 물가 3.6 → 3.8 · 목표 2%
  kicker('미국 금리와 물가', t, S(1));
  appear(t, S(1), () => { box(60, 120, 960, 130, { fill: C.card }); text('미국 기준금리', 110, 185, { size: 36, color: C.mute, align: 'left' });
    text('3.75 ~ 4.00%', 970, 187, { size: 72, weight: 900, align: 'right' }); }, { dy: 16 });
  const base = 730, unit = 95, tb = K(1, '물가', .34), t38 = K(1, '3.8%', .46), t2 = K(1, '목표', .78), tx = K(1, '2배', .9);
  text('PCE 물가 (전년 대비)', 110, 292, { size: 26, color: C.mute, align: 'left', weight: 500, alpha: P(t, tb - .3, .3) });
  line(90, base, 990, base, { color: C.dim, lw: 2 });
  [['9월', 3.6, tb - .25, C.org, 330], ['10월', 3.8, t38 - .2, C.up, 600]].forEach(([lab, v, ts, col, x], i) => {
    const k = eo(P(t, ts, .6)); if (k <= 0) return; const h = v * unit * k, hl = i === 1;
    const g = ctx.createLinearGradient(0, base - h, 0, base); g.addColorStop(0, col); g.addColorStop(1, hexA(col, .35));
    ctx.save(); if (hl) { ctx.shadowColor = hexA(col, .8); ctx.shadowBlur = 30; } ctx.fillStyle = g; rr(x, base - h, 170, h, 16); ctx.fill(); ctx.restore();
    text(v.toFixed(1) + '%', x + 85, base - h - 40, { size: hl ? 66 : 48, color: col, weight: 900, alpha: k }); text(lab, x + 85, base + 36, { size: 30 });
  });
  const lk = eo(P(t, t2 - .2, .5));
  if (lk > 0) { line(90, base - 2 * unit, lerp(90, 990, lk), base - 2 * unit, { color: C.grn, lw: 4, dash: [14, 10] }); text('목표 2%', 100, base - 2 * unit - 26, { size: 30, color: C.grn, align: 'left', alpha: lk }); }
  pop(t, tx - .05, 890, 520, () => { box(790, 440, 210, 160, { fill: '#1d1620', stroke: C.up, lw: 3, glow: 20 }); text('목표의', 895, 485, { size: 28, color: C.mute }); text('약 2배', 895, 545, { size: 52, color: C.up, weight: 900 }); });
}
function B2(t) {   // 2: 인하 ✕ 인상 ○ · 10년물 4.9%
  kicker('연준과 국채 금리', t, S(2));
  const tx = K(2, '내리는', .18), to = K(2, '올리는', .36), ty = K(2, '10년물', .6), tv = K(2, '4.9%', .8);
  const cut = P(t, tx - .1, .35), hike = P(t, to - .1, .35);
  box(90, 130, 420, 130, { fill: C.card, alpha: 1 - .55 * cut }); text('금리 인하', 300, 196, { size: 54, weight: 900, color: C.mute, alpha: 1 - .5 * cut });
  if (cut > 0) line(140, 196, lerp(140, 460, eo(cut)), 196, { color: C.dn, lw: 8 });
  box(570, 130, 420, 130, { fill: hike > 0 ? '#2a1418' : C.card, stroke: hike > 0 ? C.up : C.line, lw: hike > 0 ? 4 : 2, glow: 28 * eo(hike) });
  text('금리 인상', 780, 196, { size: 54, weight: 900, color: hike > 0 ? C.up : C.ink });
  pop(t, to, 955, 140, () => chip('지금', 955, 140, { size: 26, bg: C.up, fg: '#200a0e' }));
  const d = DATA.tnx, x0 = 110, x1 = 770, sy = scaler(d.map(v => v[1]), 360, 740, .08), pts = d.map((v, i) => [lerp(x0, x1, i / (d.length - 1)), sy(v[1])]);
  fade(P(t, ty - .5, .3), () => { text('미국 10년물 국채 금리 · 최근 1년', 110, 320, { size: 26, color: C.mute, align: 'left', weight: 500 });
    [4, 4.5, 5].forEach(v => { line(x0, sy(v), x1 + 20, sy(v), { color: C.line, lw: 1.5 }); text(v.toFixed(1) + '%', x0 - 12, sy(v), { size: 20, color: C.dim, align: 'right', weight: 500 }); }); });
  const pk = eio(P(t, ty - .35, 1.3)), end = path(pts, pk, { color: C.yel, lw: 6, glow: 14, fillTo: 760 });
  if (pk > 0) dot(end[0], end[1], 11, C.yel, { glow: 20, ring: C.bg });
  pop(t, tv - .1, 910, sy(4.94), () => { text('4.9%', 805, sy(4.94) + 4, { size: 92, color: C.yel, weight: 900, align: 'left', glow: 18 }); text('11/27 기준', 810, sy(4.94) + 70, { size: 24, color: C.mute, align: 'left', weight: 500 }); });
}
function B3(t) {   // 3: 금리 ↑ → 먼 미래 이익의 현재 가치 ↓ · 뿌리는 금리
  kicker('금리가 오르면 왜 성장주가 먼저 빠질까', t, S(3));
  const tr = K(3, '오르면', .06), tf = K(3, '미래', .16), tc = K(3, '깎여요', .42), troot = K(3, '뿌리', .66), tnv = K(3, '엔비디아', .76), tg = K(3, '금리라고', .92);
  const rk = eio(P(t, tr - .2, 2.2)), rate = lerp(2, 5, rk);
  // 금리 눈금
  box(60, 130, 200, 470, { fill: C.card }); text('금리', 160, 175, { size: 34, weight: 900 });
  box(140, 220, 40, 300, { r: 20, fill: '#262a33', stroke: null, lw: 0 }); const fy = lerp(520, 240, rk * .85 + .1);
  ctx.fillStyle = C.up; rr(140, fy, 40, 520 - fy, 20); ctx.fill(); dot(160, fy, 22, C.up, { glow: 22 * rk, ring: C.bg });
  text(rate.toFixed(1) + '%', 160, 560, { size: 40, color: C.up, weight: 900 });
  // 미래 이익 막대 5개: 현재 가치 = 이익 / (1+r)^n, 먼 미래일수록 많이 깎인다
  box(290, 130, 730, 470, { fill: C.card }); text('AI 성장주 · 미래 이익의 현재 가치', 655, 175, { size: 30, weight: 900, alpha: P(t, tf - .4, .3) });
  const profits = [1, 1.5, 2.2, 3.1, 4.2], base = 540;
  profits.forEach((p, i) => {
    const k = eo(P(t, tf - .25 + i * .1, .45)); if (k <= 0) return; const x = 340 + i * 132, full = p * 68 * k, n = (i + 1) * 3;
    const pv = full * Math.pow(1.02, n) / Math.pow(1 + rate / 100, n);
    box(x, base - full, 96, full, { r: 10, fill: null, stroke: C.dim, lw: 2 });
    const g = ctx.createLinearGradient(0, base - pv, 0, base); g.addColorStop(0, C.dn); g.addColorStop(1, hexA(C.dn, .4)); ctx.fillStyle = g; rr(x, base - pv, 96, pv, 10); ctx.fill();
    text((i + 1) * 3 + '년 뒤', x + 48, base + 30, { size: 22, color: C.mute, weight: 500 });
    if (i === 0) text('예시 · 금리 2% → 5%', 990, 584, { size: 20, color: C.dim, align: 'right', weight: 500 });
    if (t >= tc - .3 && i >= 2) text('−' + Math.round((1 - pv / full) * 100) + '%', x + 48, base - full - 22, { size: 28, color: C.dn, weight: 900, alpha: P(t, tc - .3, .3) });
  });
  // 방아쇠 vs 뿌리
  appear(t, troot - .2, () => {
    const g = t >= tg - .15;
    box(60, 640, 440, 150, { fill: C.card, alpha: g ? .55 : 1 }); text('엔비디아 뉴스', 280, 690, { size: 40, weight: 900, color: g ? C.mute : C.ink }); text('방아쇠', 280, 748, { size: 28, color: C.mute, weight: 500 });
    box(540, 640, 480, 150, { fill: g ? '#1b1a12' : C.card, stroke: g ? C.yel : C.line, lw: g ? 4 : 2, glow: g ? 30 * eo(P(t, tg - .15, .4)) : 0 });
    text('금리', 780, 690, { size: 52, weight: 900, color: g ? C.yel : C.ink }); text('급락의 뿌리', 780, 748, { size: 28, color: g ? C.yel : C.mute, weight: 700 });
  }, { dy: 36 });
}
function icon(kind, x, y, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (kind === 'split') { [0, 1, 2].forEach(i => { rr(x - 34 + i * 26, y + 18 - i * 16, 18, 18 + i * 16, 4); ctx.fill(); }); }
  if (kind === 'cash') { ctx.beginPath(); ctx.arc(x, y, 30, 0, 7); ctx.stroke(); ctx.font = `900 34px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('₩', x, y + 2); }
  if (kind === 'cal') { rr(x - 30, y - 26, 60, 56, 8); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x - 30, y - 8); ctx.lineTo(x + 30, y - 8); ctx.moveTo(x - 14, y - 36); ctx.lineTo(x - 14, y - 22); ctx.moveTo(x + 14, y - 36); ctx.lineTo(x + 14, y - 22); ctx.stroke(); }
  ctx.restore();
}
function B5(t) {   // 5: 대처 세 가지
  text('개인 의견이며 투자 권유가 아닙니다', W / 2, 818, { size: 20, color: C.dim, weight: 500 });
  kicker('그래서, 제 대처 세 가지', t, S(5), C.yel);
  const rows = [['반등에 몰아서 사지 않기', '나눠서 산다', 'split', K(5, '반등에', .32)], ['현금 남겨 두기', '다음 기회를 위한 여유', 'cash', K(5, '현금', .58)], ['날짜 확인하기', '12/4 고용 · 12/9 FOMC', 'cal', K(5, '날짜', .8)]];
  const last = Math.max(...rows.map(r => t >= r[3] - .15 ? r[3] : -1));
  rows.forEach((r, i) => appear(t, r[3] - .15, () => {
    const y = 130 + i * 225, cur = r[3] === last;
    box(60, y, 960, 195, { fill: cur ? '#1b1a12' : C.card, stroke: cur ? C.yel : C.line, lw: cur ? 4 : 2, glow: cur ? 26 : 0 });
    dot(150, y + 98, 46, cur ? C.yel : '#2a2e37'); text(String(i + 1), 150, y + 100, { size: 52, weight: 900, color: cur ? '#111318' : C.mute });
    text(r[0], 230, y + 72, { size: 50, weight: 900, align: 'left' }); text(r[1], 230, y + 136, { size: 30, color: cur ? C.yel : C.mute, align: 'left', weight: 500 });
    icon(r[2], 940, y + 98, cur ? C.yel : C.dim);
  }, { dy: 40 }));
}
function B6(t) {   // 6~끝: 12/4 고용 · 12/9 FOMC (아래 240px 은 배너가 덮는다)
  kicker('확인할 날짜 두 개', t, S(6));
  const tj = K(6, '고용보고서', .08), tf = K(6, 'FOMC', .2), tw = K(6, '약하면', .5), tl = K(6, '덜 올릴', .66), tg = K(6, '호재', .88);
  appear(t, tj - .25, () => { box(60, 120, 465, 230, { fill: C.card, stroke: C.dn, lw: 3 }); chip('12/4 금', 160, 165, { size: 28, bg: C.dn, fg: '#0c1322' });
    text('미국 고용보고서', 292, 232, { size: 44, weight: 900 }); rich([['예상 ', C.mute], ['+9만 명', C.ink], ['  (10월 +16.5만)', C.mute, 24, 500]], 292, 298, { size: 32, weight: 700 }); });
  appear(t, tf - .25, () => { box(555, 120, 465, 230, { fill: C.card, stroke: C.yel, lw: 3 }); chip('12/9 수', 655, 165, { size: 28, bg: C.yel });
    text('FOMC 금리 결정', 787, 232, { size: 44, weight: 900 }); rich([['현재 ', C.mute], ['3.75~4.00%', C.ink]], 787, 298, { size: 32, weight: 700 }); });
  const steps = [['고용이 약하면', C.dn, tw], ['덜 올릴 기대', C.yel, tl], ['주가엔 호재 가능', C.up, tg]];
  steps.forEach((s, i) => { const x = 195 + i * 345;
    appear(t, s[2] - .2, () => { box(x - 150, 420, 300, 120, { fill: '#1b1d24', stroke: s[1], lw: 3, glow: 16 }); text(s[0], x, 482, { size: 34, weight: 900, color: s[1] }); }, { dy: 20 });
    if (i) { const k = eo(P(t, s[2] - .3, .3)); if (k > 0) arrow(x - 192, 480, x - 192 + 38 * k, 480, { color: C.mute, lw: 5, head: 14, alpha: k }); } });
}
const SCENES_B = [{ from: 0, to: 1, draw: B0 }, { from: 1, to: 2, draw: B1 }, { from: 2, to: 3, draw: B2 }, { from: 3, to: 4, draw: B3 },
  { from: 5, to: 6, draw: B5 }, { from: 6, to: 99, draw: B6 }];
