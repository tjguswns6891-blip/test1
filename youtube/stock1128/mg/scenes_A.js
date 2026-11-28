// A · 이번 주 정리: 하루 6%씩 출렁, 한 주 +0.94%  (숫자 출처: ../script.json "_출처")
const KOSPI = [['11/20', '금', 4869.96, null], ['11/23', '월', 4708.54, -3.31], ['11/24', '화', 5006.03, 6.32],
  ['11/25', '수', 4697.51, -6.16], ['11/26', '목', 4711.21, 0.29], ['11/27', '금', 4915.68, 4.34]];
const NV = [['11/18', 150.96], ['11/19', 145.98], ['11/20', 125.53], ['11/23', 165.05], ['11/24', 155.38], ['11/25', 149.30], ['11/27', 150.49]];

function A0(t) {   // 0: 지그재그 → +0.94%
  kicker('코스피 · 이번 주 (11/23 ~ 11/27)', t);
  const x0 = 110, x1 = 970, yT = 150, yB = 520, sy = scaler(KOSPI.map(d => d[2]), yT, yB, .16);
  const X = i => lerp(x0, x1, i / 5), pts = KOSPI.map((d, i) => [X(i), sy(d[2])]);
  line(x0 - 30, sy(4869.96), x1 + 30, sy(4869.96), { color: C.dim, lw: 2, dash: [8, 8] });
  text('지난주 종가 4,870', x1 + 30, sy(4869.96) + 24, { size: 22, color: C.mute, align: 'right', weight: 500 });
  const prog = .22 + .78 * eio(P(t, .05, 1.5));
  // 구간마다 색 (오르면 빨강, 내리면 파랑)
  const segN = prog * 5;
  for (let i = 1; i <= 5; i++) {
    const k = clamp(segN - (i - 1)); if (k <= 0) break;
    const a = pts[i - 1], b = [lerp(a[0], pts[i][0], k), lerp(a[1], pts[i][1], k)];
    line(a[0], a[1], b[0], b[1], { color: colOf(KOSPI[i][3]), lw: 9, glow: 16 });
  }
  KOSPI.forEach((d, i) => {
    const shown = segN >= i - .02;
    text(d[1], pts[i][0], 572, { size: 30, color: i && shown ? C.ink : C.dim, weight: 700 });
    text(d[0], pts[i][0], 606, { size: 20, color: shown ? C.mute : C.dim, weight: 500 });
    if (!shown) return;
    dot(pts[i][0], pts[i][1], 11, i ? colOf(d[3]) : C.mute, { ring: C.bg });
    if (i) {
      const big = Math.abs(d[3]) > 4, k6 = big ? P(t, K(0, '6%', .22), .4) : 0, sc = 1 + .22 * Math.sin(Math.PI * k6);
      const up = d[3] > 0, ly = pts[i][1] + (up ? -44 : 46);
      ctx.save(); ctx.translate(pts[i][0], ly); ctx.scale(sc, sc);
      text(sgn(d[3]), 0, 0, { size: big ? 40 : 28, color: colOf(d[3]), weight: 900, glow: big ? 14 * Math.sin(Math.PI * k6) : 0 }); ctx.restore();
    }
  });
  // 결과 카드
  const tr = K(0, '0.94', .72);
  appear(t, tr - .25, () => {
    box(150, 650, 780, 150, { fill: '#1b1a12', stroke: C.yel, lw: 3, glow: 26 });
    text('한 주 성적', 200, 725, { size: 34, color: C.mute, align: 'left' });
    const v = .94 * eo(P(t, tr - .2, .6));
    text('+' + v.toFixed(2) + '%', 890, 727, { size: 96, color: C.yel, weight: 900, align: 'right', glow: 18 });
  });
}

function A1(t) {   // 1: 요일별 막대 → 4870 → 4916 제자리
  kicker('코스피 · 하루 등락률', t, S(1));
  const days = KOSPI.slice(1), zero = 370, unit = 36, bw = 120, x0 = 130, gap = 205;
  line(70, zero, 1010, zero, { color: C.dim, lw: 2 });
  const hi = [null, K(1, '화요일', .02), K(1, '수요일', .2), null, K(1, '금요일', .4)];
  const last = Math.max(...hi.filter(Boolean).map(h => t >= h ? h : -1));
  days.forEach((d, i) => {
    const k = eo(P(t, S(1) + .05 + i * .09, .45)), h = d[3] * unit * k, x = x0 + i * gap - bw / 2 + 40;
    const on = hi[i] != null && t >= hi[i], cur = hi[i] === last, dimmed = last > 0 && !on;
    ctx.save(); ctx.globalAlpha *= dimmed ? .38 : 1;
    const col = colOf(d[3]); const g = ctx.createLinearGradient(0, zero - h, 0, zero); g.addColorStop(0, col); g.addColorStop(1, hexA(col, .45));
    if (cur) { ctx.shadowColor = hexA(col, .8); ctx.shadowBlur = 30; }
    ctx.fillStyle = g; rr(x, Math.min(zero, zero - h), bw, Math.max(4, Math.abs(h)), 12); ctx.fill(); ctx.shadowBlur = 0;
    const pk = on ? back(P(t, hi[i], .4)) : 0, size = lerp(30, 46, pk);
    text(sgn(d[3] * k), x + bw / 2, d[3] > 0 ? zero - h - 34 : zero - h + 36, { size, color: col, weight: 900 });
    text(d[1] + '요일', x + bw / 2, d[3] > 0 ? zero + 30 : zero - 30, { size: 26, color: C.ink });
    ctx.restore();
  });
  const t1 = K(1, '4870', .62), t2 = K(1, '4916', .76), t3 = K(1, '제자리', .9);
  appear(t, t1 - .15, () => {
    box(110, 665, 860, 150, { fill: C.card });
    text('지난주 금요일', 250, 700, { size: 24, color: C.mute, weight: 500 }); text('4,870', 250, 758, { size: 66, weight: 900 });
  });
  const ak = eo(P(t, t2 - .2, .5));
  if (ak > 0) { arrow(400, 750, lerp(400, 590, ak), 750, { color: C.yel, lw: 6, head: 20 });
    fade(P(t, t2 - .05, .3), () => { text('이번 주 금요일', 740, 700, { size: 24, color: C.mute, weight: 500 }); text('4,916', 740, 758, { size: 66, weight: 900, color: C.yel }); }); }
  pop(t, t3 - .1, 900, 665, () => chip('결국 제자리', 900, 665, { size: 30, bg: C.yel }));
}

function A2(t) {   // 2~3: 엔비디아 +31% → 이틀 −9.5% → S&P 등급 경고
  kicker('엔비디아 (NVDA) · 종가', t, S(2));
  const x0 = 120, x1 = 960, yT = 170, yB = 540, sy = scaler(NV.map(d => d[1]), yT, yB, .12), X = i => lerp(x0, x1, i / 6);
  const pts = NV.map((d, i) => [X(i), sy(d[1])]);
  NV.forEach((d, i) => text(d[0], X(i), 590, { size: 22, color: C.mute, weight: 500 }));
  const tJump = K(2, '31%', .42), tDown = K(2, '이틀', .66), tLast = S(3) + .2;
  const p1 = eo(P(t, S(2) + .05, .7)) * 2;                 // 11/18 → 11/20
  const p2 = eio(P(t, tJump - .35, .5));                    // → 11/23
  const p3 = eio(P(t, tDown - .1, .8)) * 2;                 // → 11/25
  const p4 = eo(P(t, tLast, .5));                           // → 11/27
  const n = p1 + p2 + p3 + p4;
  for (let i = 1; i <= 6; i++) {
    const k = clamp(n - (i - 1)); if (k <= 0) break; const a = pts[i - 1], b = [lerp(a[0], pts[i][0], k), lerp(a[1], pts[i][1], k)];
    line(a[0], a[1], b[0], b[1], { color: colOf(NV[i][1] - NV[i - 1][1]), lw: i === 3 ? 11 : 8, glow: i === 3 ? 26 : 12 });
  }
  NV.forEach((d, i) => { if (n >= i - .02) { dot(pts[i][0], pts[i][1], 9, i ? colOf(d[1] - NV[i - 1][1]) : C.mute, { ring: C.bg });
    if ([2, 3, 5].includes(i)) text('$' + d[1].toFixed(0), pts[i][0] + (i === 3 ? 0 : 0), pts[i][1] + (i === 3 ? -34 : 38), { size: 26, color: C.ink, weight: 700 }); } });
  appear(t, K(2, '복귀', .22) - .2, () => chip('젠슨 황 CEO 복귀 소식', 330, 150, { size: 30, bg: '#2a2410', fg: C.yel, stroke: C.yel }));
  pop(t, tJump - .05, 770, 450, () => { text('하루 만에', 770, 385, { size: 30, color: C.mute }); text('+31%', 770, 455, { size: 110, color: C.up, weight: 900, glow: 26 }); });
  appear(t, tDown + .25, () => {
    line(pts[3][0] + 26, pts[3][1], pts[5][0] + 40, pts[3][1], { color: C.dn, lw: 3, dash: [6, 6] }); line(pts[5][0] + 40, pts[3][1], pts[5][0] + 40, pts[5][1], { color: C.dn, lw: 3 });
    chip('이틀 −9.5%', pts[5][0] + 20, pts[3][1] - 34, { size: 30, bg: C.dn, fg: '#0c1322' });
  });
  appear(t, S(3) - .05, () => {
    box(90, 640, 900, 160, { fill: '#1d1620', stroke: C.up, lw: 3, glow: 22 });
    ctx.save(); ctx.translate(170, 720); ctx.fillStyle = C.yel; ctx.beginPath(); ctx.moveTo(0, -42); ctx.lineTo(46, 36); ctx.lineTo(-46, 36); ctx.closePath(); ctx.fill(); ctx.restore();
    text('!', 170, 728, { size: 50, color: '#111318', weight: 900 });
    text('신용평가사 S&P 글로벌', 250, 690, { size: 28, color: C.mute, align: 'left', weight: 500 });
    rich([['엔비디아 → ', C.ink], ['부정적 관찰 대상', C.up]], 250, 745, { size: 44, align: 'left', weight: 900 });
  }, { dy: 40 });
}

function A4(t) {   // 4: 미국 주간
  kicker('미국 증시 · 이번 주', t, S(4));
  const rows = [['다우', 5.5], ['S&P 500', 5.6], ['나스닥', 6.7]], th = K(4, '5.6', .5), tb = K(4, '작년', .72);
  rows.forEach((r, i) => {
    const y = 190 + i * 140, k = eo(P(t, S(4) + .08 + i * .12, .6)), w = r[1] * 82 * k, hl = i === 1 && t >= th - .1;
    text(r[0], 300, y, { size: 44, align: 'right', weight: 900, color: hl ? C.yel : C.ink });
    const g = ctx.createLinearGradient(330, 0, 330 + w, 0); g.addColorStop(0, hexA(C.up, .5)); g.addColorStop(1, C.up);
    ctx.save(); if (hl) { ctx.shadowColor = hexA(C.up, .9); ctx.shadowBlur = 34; } ctx.globalAlpha *= (t >= th - .1 && !hl) ? .5 : 1;
    ctx.fillStyle = g; rr(330, y - 38, Math.max(6, w), 76, 16); ctx.fill(); ctx.restore();
    const sc = hl ? 1 + .25 * Math.sin(Math.PI * P(t, th - .1, .45)) : 1;
    ctx.save(); ctx.translate(350 + w, y); ctx.scale(sc, sc); text('+' + (r[1] * k).toFixed(1) + '%', 0, 2, { size: hl ? 58 : 46, color: C.up, weight: 900, align: 'left' }); ctx.restore();
  });
  pop(t, tb - .05, W / 2, 690, () => {
    box(130, 620, 820, 150, { fill: '#1b1a12', stroke: C.yel, lw: 3, glow: 26 });
    text('S&P 500 주간 상승률', W / 2, 665, { size: 28, color: C.mute, weight: 500 });
    rich([['2025년 4월', C.yel], [' 이후 최대', C.ink]], W / 2, 722, { size: 52, weight: 900 });
  });
}

function A5(t) {   // 5: 추세 전환? → 아직은 되돌림
  kicker('제 관점', t, S(5), C.yel);
  const tx = K(5, '안 봐요', .22), tn = K(5, '엔비디아', .36), ts = K(5, '사이드카', .68);
  text('추세 전환?', 330, 160, { size: 76, weight: 900, alpha: eo(P(t, S(5), .3)) });
  const xk = eo(P(t, tx - .2, .3));
  if (xk > 0) { line(110, 160, lerp(110, 560, xk), 160, { color: C.up, lw: 10, glow: 14 }); }
  pop(t, tx + .05, 800, 160, () => chip('아직은 되돌림', 800, 160, { size: 44, bg: C.yel, padX: 28 }));
  appear(t, tn - .15, () => {
    box(70, 270, 450, 500, { fill: C.card });
    text('엔비디아', 295, 325, { size: 36, weight: 900 }); text('고점 대비', 295, 368, { size: 24, color: C.mute, weight: 500 });
    const k = eo(P(t, tn, .9)), top = 420, bot = 690, yNow = lerp(top, top + (bot - top) * .371, k);
    box(150, top, 110, bot - top, { r: 14, fill: '#22262e', stroke: null, lw: 0 }); text('$239', 205, top - 0 + 24, { size: 24, color: C.mute });
    ctx.fillStyle = C.dn; rr(150, yNow, 110, bot - yNow, 14); ctx.fill(); text('$150', 205, bot - 26, { size: 26, color: '#0c1322', weight: 900 });
    text('−' + Math.round(37 * k) + '%', 395, 560, { size: 84, color: C.dn, weight: 900, glow: 16 });
  });
  appear(t, ts - .15, () => {
    box(560, 270, 450, 500, { fill: C.card });
    text('사이드카', 785, 325, { size: 36, weight: 900 }); text('올해 코스피·코스닥 합계', 785, 368, { size: 24, color: C.mute, weight: 500 });
    const k = eo(P(t, ts, 1.0)), n = Math.round(102 * k);
    text(n + (k >= 1 ? '+' : ''), 785, 520, { size: 150, color: C.yel, weight: 900, glow: 22 }); text('회', 785, 628, { size: 44, color: C.ink });
    for (let i = 0; i < 34; i++) { const on = i < n / 3; ctx.fillStyle = on ? (i % 2 ? C.up : C.dn) : '#262a33'; rr(596 + (i % 17) * 22.5, 690 + Math.floor(i / 17) * 26, 15, 18, 4); ctx.fill(); }
  });
}

function A6(t) {   // 6~끝: 다음 주 달력 (아래 240px 은 마지막에 배너가 덮는다)
  kicker('다음 주 일정', t, S(6));
  const days = [['11/30', '월'], ['12/1', '화'], ['12/2', '수'], ['12/3', '목'], ['12/4', '금']], th = K(6, '목요일', .3), tq = K(6, '청문회', .7);
  days.forEach((d, i) => {
    const x = 70 + i * 192, hl = i === 3 && t >= th - .1, k = eo(P(t, S(6) + .05 + i * .06, .35));
    ctx.save(); ctx.globalAlpha *= k * (t >= th - .1 && !hl ? .45 : 1);
    box(x, 130, 172, 150, { fill: hl ? '#2a2410' : C.card, stroke: hl ? C.yel : C.line, lw: hl ? 4 : 2, glow: hl ? 30 : 0 });
    text(d[1], x + 86, 180, { size: 44, weight: 900, color: hl ? C.yel : C.ink }); text(d[0], x + 86, 238, { size: 28, color: C.mute, weight: 500 }); ctx.restore();
  });
  appear(t, tq - .45, () => {
    box(110, 330, 860, 220, { fill: '#1b1a12', stroke: C.yel, lw: 3, glow: 26 });
    line(732, 280, 732, 330, { color: C.yel, lw: 4 });
    text('젠슨 황 · 미국 상원 청문회', W / 2, 395, { size: 50, weight: 900 });
    rich([['한국 시간 ', C.mute], ['목요일 밤 12시', C.yel]], W / 2, 478, { size: 42, weight: 900 });
  }, { dy: 40 });
}

const SCENES_A = [{ from: 0, to: 1, draw: A0 }, { from: 1, to: 2, draw: A1 }, { from: 2, to: 4, draw: A2 }, { from: 4, to: 5, draw: A4 },
  { from: 5, to: 6, draw: A5 }, { from: 6, to: 99, draw: A6 }];
