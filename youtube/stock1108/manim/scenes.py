# 증시 2026-11-08(일) 지난주(11/2~6) + 이번 주 정리 모션그래픽. 16:9, 핵심 내용은 가운데(가로 ±5.5)에 두어 세로 쇼츠에서도 잘라 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>   (1920×1080)
# 숫자: 기사(stock1108/script.json "_출처") + 내 테마 사이트 데이터(themes/data.json 11/6).
from manim import *

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
DAYS = [("월", "11/2", 5859.08, 2.24), ("화", "11/3", 5648.79, -3.59), ("수", "11/4", 5683.80, 0.62),
        ("목", "11/5", 5383.80, -5.28), ("금", "11/6", 5059.69, -6.02)]
PREV_W = 5730.74   # 10/30(금)


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK, sub=None):
    h = kr(s, 46, c).to_edge(UP, buff=.45)
    if sub:
        return VGroup(h, kr(sub, 26, MUTE).next_to(h, DOWN, .18))
    return h


def sgn(v, d=1):
    return ("+" if v > 0 else ("−" if v < 0 else "")) + f"{abs(v):.{d}f}%"


class Agenda(Scene):
    """오늘 볼 네 가지."""
    def construct(self):
        h = head("지난주 증시, 네 가지로 정리")
        self.play(FadeIn(h, shift=DOWN * .2), run_time=.5)
        items = [("①", "코스피 하루하루", "11/2 ~ 11/6", RED), ("②", "방아쇠: 미국 선거", "데이터센터 규제 공포", BLU),
                 ("③", "금요일 밤 미국", "반등 · 고용 서프라이즈", GRN), ("④", "이번 주 일정", "물가 · 코어위브", YEL)]
        g = VGroup()
        for n, t, s, c in items:
            body = VGroup(kr(n, 54, c), kr(t, 34), kr(s, 24, MUTE)).arrange(DOWN, buff=.22)
            g.add(card(body, color=c, buff=.35))
        g.arrange_in_grid(2, 2, buff=(.5, .4)).shift(DOWN * .35)
        for x in g:
            self.play(FadeIn(x, shift=UP * .3, scale=.92), run_time=.5)
            self.wait(.5)
        for x in g:
            self.play(Indicate(x, color=x[1][0].get_color(), scale_factor=1.04), run_time=.5)
        self.wait(2)


class Breaker(Scene):
    """11/6(금) 코스피: 전날 5383.80 → 장 초반 8% 넘게 하락, 서킷브레이커 20분 → 장중 저점 4911.28 → 종가 5059.69(−6.02%).
    수급: 외국인 −2조7690억 · 기관 +1조6998억."""
    def construct(self):
        h = head("금요일 코스피 · 11월 6일")
        self.play(FadeIn(h), run_time=.5)
        P = 5383.80
        ax = Axes(x_range=[0, 4.4, 1], y_range=[4850, 5450, 100], x_length=9.6, y_length=3.9,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False, "include_tip": False}).shift(UP * .5)
        self.play(Create(ax), run_time=.4)
        five = DashedLine(ax.c2p(0, 5000), ax.c2p(4.4, 5000), color=YEL, dash_length=.12, stroke_width=3)
        fl = kr("5,000", 24, YEL).next_to(five, LEFT, .1)
        self.play(Create(five), FadeIn(fl), run_time=.4)
        pts = [("목요일 종가", P, MUTE, RIGHT), ("장 초반 −8%↓", P * .92, RED, UR), ("장중 저점", 4911.28, RED, DOWN), ("마감", 5059.69, YEL, UP)]
        prev = None
        for i, (lab, v, c, side) in enumerate(pts):
            x = [.3, 1.1, 2.6, 4.0][i]
            p = ax.c2p(x, v)
            dot = Dot(p, .13, color=c)
            pct = 100 * (v / P - 1)
            txt = VGroup(kr(lab, 24, MUTE), kr(f"{v:,.0f}" + ("" if i == 0 else f"  {sgn(pct, 1)}"), 30, c)).arrange(DOWN, buff=.06)
            txt.next_to(p, side, .32 if i == 1 else .2)
            anims = [FadeIn(dot, scale=1.4), FadeIn(txt, shift=side * .15)]
            if prev is not None:
                anims.append(Create(Line(prev, p, color=GRN if v > prev_v else RED, stroke_width=6)))
            self.play(*anims, run_time=.6)
            if i == 1:
                cb = card(VGroup(kr("서킷브레이커", 40, RED), kr("거래 20분 정지", 26, INK)).arrange(DOWN, buff=.08), color=RED, buff=.22)
                cb.move_to(ax.c2p(2.6, 5300))
                self.play(FadeIn(cb, scale=1.2), Flash(dot, color=RED), run_time=.6)
                self.wait(1.6)
                self.play(FadeOut(cb), run_time=.3)
            else:
                self.wait(1.4)
            prev, prev_v = p, v
        self.play(Flash(prev, color=YEL), run_time=.5)
        f1 = card(VGroup(kr("기관 +1조 7천억", 32, GRN), kr("5,000을 지킨 매수", 24, MUTE)).arrange(DOWN, buff=.1), color=GRN, buff=.22)
        f2 = card(VGroup(kr("외국인 −2조 7천억", 32, BLU), kr("6거래일 연속 매도", 24, MUTE)).arrange(DOWN, buff=.1), color=BLU, buff=.22)
        VGroup(f1, f2).arrange(RIGHT, buff=.4).to_edge(DOWN, buff=.3)
        self.play(FadeIn(f1, shift=UP * .2)); self.wait(2.5)
        self.play(FadeIn(f2, shift=UP * .2)); self.wait(4)


class Week(Scene):
    """지난주 코스피 일별 + 주간 5730.74 → 5059.69 −11.71%, 코스닥 724.38 → 644.27 −11.06%, 외국인 5일 합 약 −10.5조(계산)."""
    def construct(self):
        h = head("지난주 코스피 · 하루하루")
        self.play(FadeIn(h), run_time=.5)
        ax = NumberLine(x_range=[-.5, 4.5, 1], length=10, include_ticks=False, color=MUTE).shift(UP * 1.2)
        self.play(Create(ax), run_time=.4)
        bars, tags = VGroup(), VGroup()
        for i, (wd, dt, v, p) in enumerate(DAYS):
            c = GRN if p > 0 else RED
            r = Rectangle(width=1.2, height=max(abs(p) * .42, .06), stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to(ax.n2p(i), aligned_edge=DOWN if p > 0 else UP)
            t = kr(sgn(p), 34, c).next_to(r, UP if p > 0 else DOWN, .12)
            d = kr(wd, 30, MUTE).next_to(ax.n2p(i), DOWN if p > 0 else UP, .2)
            bars.add(r); tags.add(VGroup(t, d))
        for i, (r, t, (_, _, _, p)) in enumerate(zip(bars, tags, DAYS)):
            self.play(GrowFromEdge(r, DOWN if p > 0 else UP), FadeIn(t), run_time=.5)
            self.wait(1.3 if i < 3 else .8)
        two = card(VGroup(kr("이틀 연속 −5% 넘게", 32, RED), kr("목 사이드카 · 금 서킷브레이커", 24, MUTE)).arrange(DOWN, buff=.1), color=RED)
        two.next_to(bars[3:], LEFT, .3).shift(DOWN * .3)
        self.play(Indicate(bars[3:], color=RED, scale_factor=1.06), FadeIn(two, shift=RIGHT * .2), run_time=.7)
        self.wait(3)
        self.play(FadeOut(two), VGroup(ax, bars, tags).animate.scale(.62).shift(UP * .75), run_time=.6)
        wk = card(VGroup(kr("코스피 주간", 26, MUTE), kr("5,731 → 5,060", 34), kr("−11.7%", 50, RED)).arrange(DOWN, buff=.1), color=RED)
        kq = card(VGroup(kr("코스닥 주간", 26, MUTE), kr("724 → 644", 34), kr("−11.1%", 50, RED)).arrange(DOWN, buff=.1), color=RED)
        fo = card(VGroup(kr("외국인 5일 합계", 26, MUTE), kr("6거래일 연속 매도", 30), kr("−10조+", 50, BLU)).arrange(DOWN, buff=.1), color=BLU)
        VGroup(wk, kq, fo).arrange(RIGHT, buff=.45).to_edge(DOWN, buff=.35)
        for x in (wk, kq, fo):
            self.play(FadeIn(x, shift=UP * .3), run_time=.5)
            self.wait(2.4)
        self.wait(2)


class Election(Scene):
    """중간선거: 민주당 상·하원 장악 · 10개 주 데이터센터 주민투표 41건 중 40건 제한/규제 통과 · 골드만: 증설 계획 45%가 규제 강화 예상 주(텍사스 25%)."""
    def construct(self):
        h = head("방아쇠 · 미국 중간선거")
        self.play(FadeIn(h), run_time=.5)
        sen = card(VGroup(kr("상원", 30, MUTE), kr("민주당", 44, BLU)).arrange(DOWN, buff=.1), color=BLU, buff=.3)
        hou = card(VGroup(kr("하원", 30, MUTE), kr("민주당", 44, BLU)).arrange(DOWN, buff=.1), color=BLU, buff=.3)
        top = VGroup(sen, hou).arrange(RIGHT, buff=.6).shift(UP * 1.5)
        self.play(FadeIn(sen, shift=DOWN * .2)); self.wait(.9)
        self.play(FadeIn(hou, shift=DOWN * .2)); self.wait(.9)
        both = kr("둘 다", 40, YEL).next_to(top, RIGHT, .4)
        self.play(FadeIn(both, scale=1.3)); self.wait(1.5)
        # 41칸 중 40칸 빨강
        grid = VGroup(*[Square(.34, stroke_width=0, fill_color=RED if i < 40 else MUTE, fill_opacity=1) for i in range(41)])
        grid.arrange_in_grid(3, 14, buff=.1).shift(DOWN * .55 + LEFT * 1.2)
        gl = kr("데이터센터 주민투표 41건", 28, MUTE).next_to(grid, UP, .18).align_to(grid, LEFT)
        self.play(FadeIn(gl), run_time=.3)
        self.play(LaggedStart(*[FadeIn(s, scale=.4) for s in grid], lag_ratio=.05), run_time=2.2)
        g40 = VGroup(kr("40건", 64, RED), kr("제한 · 규제 쪽 통과", 26, INK)).arrange(DOWN, buff=.08).next_to(grid, RIGHT, .5)
        self.play(FadeIn(g40, shift=LEFT * .2)); self.wait(2.5)
        gs = card(VGroup(kr("골드만삭스", 26, MUTE), kr("증설 계획의 45%가", 34), kr("규제 세질 주에", 34, RED)).arrange(DOWN, buff=.08), color=ORG, buff=.22)
        gs.to_edge(DOWN, buff=.25)
        self.play(FadeIn(gs, shift=UP * .2)); self.wait(3)
        chain = VGroup(kr("데이터센터 ↓", 34, ORG), kr("→", 34, MUTE), kr("AI 칩 수요 ↓ ?", 34, RED)).arrange(RIGHT, buff=.3)
        chain.move_to(gs)
        self.play(FadeOut(gs, shift=UP * .2), FadeIn(chain, shift=UP * .2)); self.wait(5)


class UsCrash(Scene):
    """11/5(현지): 나스닥 −5.52% · S&P −4.36% · 다우 −3.44% · 반도체지수 −12%대 / 엔비디아 −9.3 · 브로드컴 −10.6 · AMD −17.3."""
    def construct(self):
        h = head("목요일 밤 미국 · 하루 낙폭")
        self.play(FadeIn(h), run_time=.5)
        rows = [("나스닥", 5.52, "−5.5%", RED), ("S&P 500", 4.36, "−4.4%", ORG), ("다우", 3.44, "−3.4%", ORG), ("반도체지수", 12.3, "−12%대", RED)]
        base = Line(UP * 2.0, DOWN * 2.2, color=MUTE, stroke_width=3).shift(RIGHT * 2.6)
        self.play(Create(base), run_time=.3)
        grp = VGroup(base)
        for i, (nm, v, s, c) in enumerate(rows):
            y = 1.45 - i * 1.0
            r = Rectangle(width=v * .48, height=.66, stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to([base.get_x(), y, 0], aligned_edge=RIGHT)
            lab = kr(nm, 30).next_to(r, LEFT, .25)
            val = kr(s, 32, c).next_to(base, RIGHT, .25).set_y(y)
            self.play(GrowFromEdge(r, RIGHT), FadeIn(lab), FadeIn(val), run_time=.55)
            grp.add(r, lab, val)
            self.wait(1.0)
        self.wait(1.2)
        self.play(grp.animate.scale(.75).to_edge(UP, buff=1.25), run_time=.5)
        chips = [("엔비디아", "−9.3%"), ("브로드컴", "−10.6%"), ("AMD", "−17.3%")]
        cg = VGroup(*[card(VGroup(kr(n, 28, MUTE), kr(v, 46, RED)).arrange(DOWN, buff=.08), color=RED, buff=.25) for n, v in chips])
        cg.arrange(RIGHT, buff=.4).to_edge(DOWN, buff=.45)
        for c in cg:
            self.play(FadeIn(c, shift=UP * .25), run_time=.45)
            self.wait(1.3)
        self.play(Indicate(cg[2], color=RED, scale_factor=1.08)); self.wait(4)


class Chips(Scene):
    """이틀(11/5~6): SK하이닉스 약 139.6만 → 126.4만(−9.46%) → 113.2만(−10.44%), 이틀 −18.9% / 삼성전자 약 21.8만 → 20.15만(−7.57%) → 18.87만(−6.35%), 이틀 −13.4%.
    11/5 외국인 −3.4조 중 하이닉스 −1.52조 · 삼성 −1.16조 ≈ 70%."""
    def construct(self):
        h = head("이틀 동안 반도체 두 종목")
        self.play(FadeIn(h), run_time=.5)
        def col(name, vals, tot, c):
            nm = kr(name, 36, c)
            bars = VGroup()
            for v in vals:
                bars.add(Rectangle(width=1.0, height=v / vals[0] * 3.6, stroke_width=0, fill_color=c, fill_opacity=.9))
            bars.arrange(RIGHT, buff=.25, aligned_edge=DOWN)
            return nm, bars, kr(tot, 56, RED)
        hy = col("SK하이닉스", [139.6, 126.4, 113.2], "−18.9%", ORG)
        ss = col("삼성전자", [21.8, 20.15, 18.87], "−13.4%", BLU)
        out = VGroup()
        for i, (nm, bars, tot) in enumerate((hy, ss)):
            x = -3.0 if i == 0 else 3.0
            bars.move_to([x, -2.6, 0], aligned_edge=DOWN)
            nm.next_to(bars, UP, 1.25)
            labs = VGroup(*[kr(s, 22, MUTE).next_to(b, DOWN, .12) for s, b in zip(["수", "목", "금"], bars)])
            vals = (["139.6만", "126.4만", "113.2만"] if i == 0 else ["21.8만", "20.2만", "18.9만"])
            vl = VGroup(*[kr(s, 22, INK).next_to(b, UP, .1) for s, b in zip(vals, bars)])
            self.play(FadeIn(nm), run_time=.4)
            for b, l, v in zip(bars, labs, vl):
                self.play(GrowFromEdge(b, DOWN), FadeIn(l), FadeIn(v), run_time=.45)
                self.wait(.5)
            tot.next_to(nm, DOWN, .15)
            self.play(FadeIn(tot, scale=1.3), run_time=.5)
            self.wait(1.5)
            out.add(nm, bars, labs, vl, tot)
        self.wait(1)
        self.play(out.animate.scale(.72).shift(UP * .55), run_time=.5)
        pie = card(VGroup(kr("목요일 외국인 순매도 3조 4천억", 28, MUTE), kr("그중 70%가 이 두 종목", 38, YEL)).arrange(DOWN, buff=.1), color=YEL, buff=.25)
        pie.to_edge(DOWN, buff=.35)
        self.play(FadeIn(pie, shift=UP * .2)); self.wait(5)


class Recap(Scene):
    """여기까지 정리: 미국 선거 → 데이터센터 규제 공포 → AI 반도체 → 코스피."""
    def construct(self):
        h = head("여기까지 정리", YEL)
        self.play(FadeIn(h), run_time=.4)
        steps = [("미국 중간선거", "민주당 상·하원", BLU), ("데이터센터 규제 공포", "41건 중 40건", ORG),
                 ("AI 반도체 급락", "나스닥 −5.5%", RED), ("코스피 −11.7%", "서킷브레이커", RED)]
        g = VGroup(*[card(VGroup(kr(t, 32, c), kr(s, 24, MUTE)).arrange(DOWN, buff=.08), color=c, buff=.22) for t, s, c in steps])
        g.arrange(DOWN, buff=.45).shift(DOWN * .3 + LEFT * 2.2)
        arrows = VGroup(*[Arrow(g[i].get_bottom(), g[i + 1].get_top(), buff=.05, color=MUTE, stroke_width=5) for i in range(3)])
        self.play(FadeIn(g[0], shift=DOWN * .2), run_time=.4); self.wait(1.4)
        for i in range(3):
            self.play(GrowArrow(arrows[i]), FadeIn(g[i + 1], shift=DOWN * .2), run_time=.5)
            self.wait(1.6)
        note = VGroup(kr("반도체 비중 큰 코스피가", 30, YEL), kr("미국보다 더 크게", 30, YEL)).arrange(DOWN, buff=.08).next_to(g[3], RIGHT, .4)
        self.play(Indicate(g[3], color=RED), FadeIn(note, shift=LEFT * .2)); self.wait(5)


class UsFri(Scene):
    """11/6(현지): 나스닥 +1.1% 24,579 · AMD +11.0 · 엔비디아 +2.8 · 반도체지수 +4.2 / 10월 비농업 +16.5만(예상 6.5만), 실업률 4.1%, 10년물 4.86%.
    다우 −0.5%. 주간 나스닥 −3.4%(4주 연속)."""
    def construct(self):
        h = head("금요일 밤 미국 · 반등, 그런데")
        self.play(FadeIn(h), run_time=.5)
        up = [("나스닥", "+1.1%"), ("AMD", "+11%"), ("엔비디아", "+2.8%"), ("반도체지수", "+4.2%")]
        ug = VGroup(*[card(VGroup(kr(n, 26, MUTE), kr(v, 42, GRN)).arrange(DOWN, buff=.06), color=GRN, buff=.2) for n, v in up])
        ug.arrange(RIGHT, buff=.3).shift(UP * 1.7)
        for c in ug:
            self.play(FadeIn(c, shift=UP * .2), run_time=.4)
            self.wait(.8)
        self.wait(.8)
        ax = NumberLine(x_range=[0, 18, 3], length=7, include_ticks=False, color=MUTE).shift(DOWN * .9 + RIGHT * .6)
        k = 7 / 18
        e = Rectangle(width=6.5 * k, height=.6, stroke_width=0, fill_color=MUTE, fill_opacity=.9).move_to(ax.n2p(0), aligned_edge=LEFT).shift(UP * 1.2)
        a = Rectangle(width=16.5 * k, height=.6, stroke_width=0, fill_color=YEL, fill_opacity=.95).move_to(ax.n2p(0), aligned_edge=LEFT).shift(UP * .35)
        el = kr("예상 6.5만", 26, MUTE).next_to(e, RIGHT, .15)
        al = kr("실제 16.5만", 30, YEL).next_to(a, RIGHT, .15)
        tl = kr("10월 일자리", 30).next_to(VGroup(e, a), LEFT, .3)
        self.play(FadeIn(tl), GrowFromEdge(e, LEFT), FadeIn(el), run_time=.6); self.wait(1.4)
        self.play(GrowFromEdge(a, LEFT), FadeIn(al), run_time=.7); self.wait(2)
        info = VGroup(kr("실업률 4.1%", 30, INK), kr("10년물 금리 4.86%", 30, RED), kr("→ 금리 인상 걱정", 30, ORG)).arrange(RIGHT, buff=.5)
        info.to_edge(DOWN, buff=1.1)
        for x in info:
            self.play(FadeIn(x, shift=UP * .2), run_time=.4)
            self.wait(1.4)
        wk = kr("나스닥 주간 −3.4% · 4주 연속 하락", 32, RED).to_edge(DOWN, buff=.3)
        self.play(FadeIn(wk, shift=UP * .2)); self.wait(4)


class NextWeek(Scene):
    """이번 주(11/9~13): 9일 신용융자 담보비율 140% 유지 의무 3개월 면제 · 10일 미국 10월 CPI(예상 +0.3%) · 10일 코어위브 실적 · 12일 MSCI 정기 리뷰·옵션 만기 · 13일 미국 PPI. 밴드 5000~6000."""
    def construct(self):
        h = head("이번 주 꼭 볼 일정", YEL)
        self.play(FadeIn(h), run_time=.5)
        items = [("11/10(화) 밤", "미국 10월 소비자물가", "예상 +0.3% · 고용 뜨거웠는데?", RED),
                 ("11/10(화) 밤", "코어위브 3분기 실적", "AI 데이터센터 투자 분위기", BLU),
                 ("11/12(목)", "MSCI 정기 리뷰 · 옵션 만기", "11/13(금) 미국 생산자물가", PUR),
                 ("11/9(월)부터", "신용융자 담보비율 의무 면제", "석 달 · 반대매매 부담 완화", GRN)]
        g = VGroup()
        for d, t, s, c in items:
            g.add(card(VGroup(kr(d, 26, c), VGroup(kr(t, 32), kr(s, 22, MUTE)).arrange(DOWN, buff=.06, aligned_edge=LEFT)).arrange(RIGHT, buff=.4), color=c, buff=.2))
        g.arrange(DOWN, buff=.2, aligned_edge=LEFT).shift(UP * .35)
        for x in g:
            self.play(FadeIn(x, shift=RIGHT * .4), run_time=.5)
            self.wait(2.6)
        self.play(g.animate.scale(.85).shift(UP * .3), run_time=.4)
        bar = NumberLine(x_range=[4800, 6200, 100], length=8, include_ticks=False, color=MUTE).to_edge(DOWN, buff=.7)
        rng = Line(bar.n2p(5000), bar.n2p(6000), color=YEL, stroke_width=14)
        l1, l2 = kr("5,000", 24, YEL).next_to(bar.n2p(5000), DOWN, .15), kr("6,000", 24, YEL).next_to(bar.n2p(6000), DOWN, .15)
        me = VGroup(Triangle(color=RED, fill_opacity=1).scale(.13).rotate(PI).next_to(bar.n2p(5059.69), UP, .02), kr("5,060", 24, RED))
        me[1].next_to(me[0], UP, .05)
        self.play(Create(bar), Create(rng), FadeIn(l1), FadeIn(l2), run_time=.6)
        self.play(FadeIn(me, shift=DOWN * .2)); self.wait(1)
        self.play(Indicate(l1, color=YEL, scale_factor=1.5)); self.wait(4)


class Summary(Scene):
    def construct(self):
        h = head("세 줄 요약", YEL)
        ls = [("1", "코스피 주간 −11.7% · 서킷브레이커 뒤 5,060", RED), ("2", "중간선거 → 데이터센터 규제 공포 → 나스닥 −5.5%", BLU),
              ("3", "이번 주: 화요일 밤 물가 · 코어위브 · 5,000선", GRN)]
        g = VGroup()
        for n, t, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), kr(t, 34)).arrange(RIGHT, buff=.4))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.6).shift(DOWN * .1)
        self.play(FadeIn(h))
        for r in g:
            self.play(FadeIn(r, shift=RIGHT * .3), run_time=.5)
            self.wait(3.2)
        foot = kr("금리·주가 50년 /invest   ·   미국 테마 강도 /themes", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(4)
