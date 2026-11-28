// C · QQQ·S&P500 매수·매도 관점: 내 사이트 신호 + 200일선 + 지지선  (숫자 출처: ../script.json "_출처", data.js)
const disc = () => text('개인 의견이며 투자 권유가 아닙니다', W / 2, 818, { size: 20, color: C.dim, weight: 500 });
function sigCard(x, name, sub, badge, bcol, bfg, tb, t, rows, px, tp) {
  const on = t >= tb - .1;
  box(x, 150, 460, 610, { fill: C.card, stroke: on ? bcol : C.line, lw: on ? 4 : 2, glow: on ? 26 * eo(P(t, tb - .1, .5)) : 0, glowColor: bcol });
  text(name, x + 230, 225, { size: 60, weight: 900 }); text(sub, x + 230, 282, { size: 24, color: C.mute, weight: 500 });
  appear(t, tp, () => rich(px, x + 230, 330, { size: 30, weight: 700 }), { dy: 12 });
  if (!on) text('?', x + 230, 440, { size: 130, color: C.dim, weight: 900 });
  pop(t, tb - .1, x + 230, 440, () => chip(badge, x + 230, 440, { size: 62, bg: bcol, fg: bfg, padX: 36, h: 120 }));
  rows.forEach((r, i) => appear(t, tb + .25 + i * .18, () => { text(r[0], x + 40, 580 + i * 86, { size: 26, color: C.mute, align: 'left', weight: 500 }); text(r[1], x + 420, 582 + i * 86, { size: 48, color: r[2], align: 'right', weight: 900 }); line(x + 40, 622 + i * 86, x + 420, 622 + i * 86, { color: C.line, lw: 1.5 }); }, { dy: 14 }));
}
function C0(t) {   // 0: 내 사이트 신호 — S&P 500 보유 · QQQ 비중 축소
  kicker('내 사이트 · 오늘의 매매 신호 (11/27 종가 기준)', t);
  sigCard(60, 'S&P 500', '미국 대형주 500', '보유', '#e9ecf1', '#111318', K(0, '보유', .62), t, [['1년 뒤 오른 확률', '75%', C.up], ['10% 넘게 빠진 확률', '21%', C.ink]], [['7,297 ', C.ink], [' 고점 대비 −6.7%', C.dn]], .7);
  sigCard(560, 'QQQ', '나스닥 100', '비중 축소', C.dn, '#0c1322', K(0, '비중', .82), t, [['1년 뒤 오른 확률', '59%', C.up], ['10% 넘게 빠진 확률', '48%', C.dn]], [['$651 ', C.ink], [' 고점 대비 −14%', C.dn]], 1.5);
  pop(t, K(0, '사도', .3) - .1, W / 2, 106, () => chip('지금 사도 될까?', W / 2, 106, { size: 34, bg: C.yel, padX: 26 }));
  disc();
}
function priceChart(d, k, o) {   // 종가(선) + 200일 평균(점선). k = 그리기 진행도
  const { x0 = 90, x1 = 800, yT = 170, yB = 700, col = C.ink } = o;
  const vals = d.flatMap(v => [v[1], v[2], v[3]]), sy = scaler(vals, yT, yB, .06), X = i => lerp(x0, x1, i / (d.length - 1));
  path(d.map((v, i) => [X(i), sy(v[2])]), clamp(k * 1.4), { color: C.yel, lw: 4, dash: [12, 9] });
  const end = path(d.map((v, i) => [X(i), sy(v[1])]), k, { color: col, lw: 5, glow: 10, fillTo: yB + 20 });
  if (k > 0) dot(end[0], end[1], 10, col, { glow: 18, ring: C.bg });
  [0, 43, 86, 129].forEach(i => text(d[i][0].slice(5).replace('-', '/'), X(i), yB + 46, { size: 20, color: C.dim, weight: 500 }));
  return { sy, X, end };
}
function C2(t) {   // 2~3: S&P 500 은 200일선 바로 아래 · QQQ 는 5% 더 · 바닥 두 번
  const tq = K(2, 'QQQ는', .5), sA = 1 - P(t, tq - .3, .3), qA = P(t, tq - .15, .3);
  fade(sA, () => {
    kicker('S&P 500 · 최근 6개월', t, S(2));
    const d = DATA.spx, c = priceChart(d, eio(P(t, S(2) + .05, 1.4)), {}), tm = K(2, '200일선', .22), tv = K(2, '7354', .3);
    appear(t, tm - .2, () => { chip('200일선 7,354', 930, c.sy(7354.27) - 44, { size: 30, bg: C.yel }); line(810, c.sy(7354.27), 1020, c.sy(7354.27), { color: C.yel, lw: 4, dash: [12, 9] }); }, { dy: 10 });
    appear(t, tv + .2, () => { text('현재', 930, c.sy(7297.49) + 46, { size: 24, color: C.mute, weight: 500 }); text('7,297', 930, c.sy(7297.49) + 96, { size: 64, weight: 900 }); chip('바로 아래 −0.8%', 930, c.sy(7297.49) + 160, { size: 26, bg: '#262a33', fg: C.ink }); }, { dy: 10 });
  });
  fade(qA, () => {
    kicker('QQQ · 최근 6개월', t, tq - .15);
    const d = DATA.qqq, c = priceChart(d, eio(P(t, tq - .1, 1.1)), { col: C.dn }), t651 = K(2, '651달러', .58), t684 = K(2, '684달러', .74), t5 = K(2, '5%를', .86);
    const yM = c.sy(683.69), yN = c.sy(650.99);
    appear(t, t684 - .2, () => { line(810, yM, 1020, yM, { color: C.yel, lw: 4, dash: [12, 9] }); chip('200일선 $684', 925, yM - 40, { size: 30, bg: C.yel }); }, { dy: 10 });
    appear(t, t651 - .15, () => { line(810, yN, 1020, yN, { color: C.dn, lw: 4 }); text('현재 $651', 925, yN + 40, { size: 38, weight: 900, color: C.dn }); }, { dy: 10 });
    const bk = eo(P(t, t5 - .2, .5));
    if (bk > 0 && t < S(3) + .2) { arrow(925, yN - 8, 925, lerp(yN - 8, yM + 8, bk), { color: C.up, lw: 6, head: 18 }); }
    pop(t, t5, 925, (yM + yN) / 2, () => { if (t < S(3) + .2) chip('+5% 더', 990, (yM + yN) / 2, { size: 32, bg: C.up, fg: '#200a0e' }); });
    // 바닥 두 번
    const i1 = d.findIndex(v => v[0] === '2026-11-20'), i2 = d.findIndex(v => v[0] === '2026-11-25'), t1 = K(3, '606달러', .5), t2 = K(3, '608달러', .8), ts = K(3, '지켰어요', .25);
    const yS = c.sy(606.23), sk = eo(P(t, ts - .25, .5));
    if (sk > 0) { line(lerp(c.X(i1) - 180, c.X(i1) - 180, sk), yS, lerp(c.X(i1) - 180, 1020, sk), yS, { color: C.grn, lw: 4, glow: 12 }); text('지지선', 925, yS + 34, { size: 32, color: C.grn, weight: 900, alpha: sk }); }
    pop(t, t1 - .1, c.X(i1), yS, () => { dot(c.X(i1), c.sy(d[i1][3]), 14, C.grn, { glow: 22, ring: C.bg }); box(c.X(i1) - 250, yS - 150, 190, 110, { fill: '#122019', stroke: C.grn, lw: 3 }); text('11/20', c.X(i1) - 155, yS - 122, { size: 22, color: C.mute, weight: 500 }); text('$606', c.X(i1) - 155, yS - 80, { size: 46, color: C.grn, weight: 900 }); });
    pop(t, t2 - .1, c.X(i2), yS, () => { dot(c.X(i2), c.sy(d[i2][3]), 14, C.grn, { glow: 22, ring: C.bg }); box(c.X(i1) - 40, yS + 30, 190, 110, { fill: '#122019', stroke: C.grn, lw: 3 }); text('11/25', c.X(i1) + 55, yS + 58, { size: 22, color: C.mute, weight: 500 }); text('$608', c.X(i1) + 55, yS + 100, { size: 46, color: C.grn, weight: 900 }); });
  });
  disc();
}
function C4(t) {   // 4~5: QQQ 가격 사다리 — 세 번에 나눠 사기 → 606 이탈 · 200일선 근처
  const Y = v => lerp(730, 150, (v - 596) / (694 - 596)), y684 = Y(683.69), y651 = Y(650.99), y606 = Y(606.23), sell = t >= S(5) - .12;
  kicker(sell ? 'QQQ · 멈추는 자리, 덜어내는 자리' : 'QQQ · 매수는 세 번에 나눠서', t, S(4), C.yel);
  // 왼쪽 가격 기둥
  box(60, 120, 400, 650, { fill: C.card });
  [[y684, C.yel, '200일선', '$684', [12, 9]], [y651, C.ink, '현재', '$651', null], [y606, C.grn, '지지선', '$606', null]].forEach(([y, col, lab, v, dash], i) => {
    const k = eo(P(t, S(4) + .05 + i * .1, .4)); line(90, y, lerp(90, 430, k), y, { color: col, lw: 4, dash });
    text(lab, 100, y - 24, { size: 24, color: col, align: 'left', weight: 700, alpha: k }); text(v, 425, y - 28, { size: 40, color: col, align: 'right', weight: 900, alpha: k }); });
  dot(260, y651, 14, C.ink, { glow: 20, ring: C.bg });
  const ts = [K(4, '지금 조금', .5), K(4, '지나고', .62) - .45, K(4, '200일선을', .8)], t3 = K(4, '3번', .3);
  if (!sell || t < S(5) + .15) fade(1 - P(t, S(5) - .12, .25), () => {
    const rows = [['지금 조금', '현재가 근처에서 첫 매수', y651 + 40, C.ink], ['FOMC 지나고 한 번', '12/9 금리 결정 확인 뒤', (y651 + y684) / 2 + 20, C.dn], ['200일선 종가 돌파 때 마지막', '$684 위에서 마감하면', y684, C.yel]];
    const last = Math.max(...ts.map(x => t >= x - .15 ? x : -1));
    pop(t, t3 - .1, 760, 150, () => { [0, 1, 2].forEach(i => { ctx.fillStyle = t >= ts[i] - .15 ? rows[i][3] : '#2a2e37'; rr(620 + i * 96, 118, 86, 22, 11); ctx.fill(); }); });
    rows.forEach((r, i) => appear(t, ts[i] - .15, () => { const cur = ts[i] === last, y = r[2];
      box(500, y - 56, 520, 112, { fill: cur ? '#1b1d24' : C.card, stroke: cur ? r[3] : C.line, lw: cur ? 4 : 2, glow: cur ? 22 : 0 });
      dot(555, y, 30, r[3]); text(String(i + 1), 555, y + 2, { size: 36, weight: 900, color: '#111318' });
      text(r[0], 605, y - 18, { size: i === 2 ? 31 : 36, weight: 900, align: 'left' }); text(r[1], 605, y + 26, { size: 23, color: C.mute, align: 'left', weight: 500 });
      line(430, y, 500, y, { color: r[3], lw: 3, dash: [5, 5] }); }, { dy: 24 }));
  });
  if (sell) {
    const tb = K(5, '606달러', .16), tx = K(5, '멈춰요', .4), tm = K(5, '200일선', .58), td = K(5, '덜고요', .9);
    const zk = eo(P(t, tb - .2, .5));
    if (zk > 0) { ctx.save(); ctx.globalAlpha *= zk * .35; ctx.fillStyle = C.dn; rr(90, y606, 340, 760 - y606 - 6, 8); ctx.fill(); ctx.restore(); }
    appear(t, tb - .15, () => { box(500, y606 - 110, 520, 200, { fill: '#121a2a', stroke: C.dn, lw: 4, glow: 22 }); line(430, y606, 500, y606, { color: C.dn, lw: 3, dash: [5, 5] });
      text('$606 을 종가로 깨면', 760, y606 - 58, { size: 36, weight: 900 }); pop(t, tx - .1, 760, y606 + 22, () => chip('추가 매수 멈춤', 760, y606 + 22, { size: 44, bg: C.dn, fg: '#0c1322', padX: 30 })); }, { dy: 24 });
    const mk = eo(P(t, tm - .2, .5));
    if (mk > 0) { ctx.save(); ctx.globalAlpha *= mk * .3; ctx.fillStyle = C.yel; rr(90, y684 - 26, 340, 52, 8); ctx.fill(); ctx.restore(); }
    appear(t, tm - .15, () => { box(500, y684 - 70, 520, 200, { fill: '#1b1a12', stroke: C.yel, lw: 4, glow: 22 }); line(430, y684, 500, y684, { color: C.yel, lw: 3, dash: [5, 5] });
      text('200일선 근처에 오면', 760, y684 - 18, { size: 36, weight: 900 }); pop(t, td - .5, 760, y684 + 62, () => chip('단기 물량 조금 덜기', 760, y684 + 62, { size: 40, bg: C.yel, padX: 30 })); }, { dy: 24 });
  }
  disc();
}
function C6(t) {   // 6~끝: 장기 적립식은 일정 그대로 (아래 240px 은 배너가 덮는다)
  kicker('장기 적립식이라면', t, S(6));
  const tk = K(6, '일정', .62);
  text('매달 적립하는 장기 투자', W / 2, 170, { size: 56, weight: 900, alpha: eo(P(t, S(6), .3)) });
  ['12월', '1월', '2월', '3월', '4월', '5월'].forEach((m, i) => { const x = 105 + i * 150, k = eo(P(t, S(6) + .15 + i * .22, .35)); if (k <= 0) return;
    ctx.save(); ctx.globalAlpha *= k; box(x, 250, 120, 150, { fill: C.card, stroke: C.grn, lw: 3 }); text(m, x + 60, 295, { size: 30, weight: 700 });
    ctx.strokeStyle = C.grn; ctx.lineWidth = 8; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(x + 38, 352); ctx.lineTo(x + 54, 368); ctx.lineTo(x + 84, 334); ctx.stroke(); ctx.restore(); });
  pop(t, tk - .1, W / 2, 490, () => chip('저는 일정 그대로 갑니다', W / 2, 490, { size: 48, bg: C.yel, padX: 36, h: 96 }));
}
const SCENES_C = [{ from: 0, to: 1, draw: C0 }, { from: 2, to: 4, draw: C2 }, { from: 4, to: 6, draw: C4 }, { from: 6, to: 99, draw: C6 }];
