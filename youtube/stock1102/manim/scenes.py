# 증시 2026-11-02(월) 오늘 + 지난주(10/26~30) + 이번 주 정리 모션그래픽. 16:9, 핵심 내용은 가운데(가로 ±5.5)에 두어 세로 쇼츠에서도 잘라 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>   (1920×1080)
# 숫자: 기사(stock1102/script.json "_출처") + 내 테마 사이트 데이터(themes/data.json 10/30). 오늘 숫자는 ../today.json.
from manim import *
import json, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
TD = json.load(open(os.path.join(os.path.dirname(__file__), "../today.json"), encoding="utf-8"))
DAYS = [("월", "10/26", 5469.47, -1.46), ("화", "10/27", 5638.34, 3.09), ("수", "10/28", 6012.44, 6.63),
        ("목", "10/29", 5937.66, -1.24), ("금", "10/30", 5730.74, -3.48)]
PREV_W = 5550.30   # 10/23(금)


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
        h = head("오늘 정리할 네 가지")
        self.play(FadeIn(h, shift=DOWN * .2), run_time=.5)
        items = [("①", "오늘 한국장", "11/2(월) 마감", RED), ("②", "금요일 밤 미국", "10/30(금) 현지", BLU),
                 ("③", "지난주 전체", "10/26 ~ 10/30", YEL), ("④", "이번 주 일정", "중간선거 · 고용", GRN)]
        g = VGroup()
        for n, t, s, c in items:
            body = VGroup(kr(n, 54, c), kr(t, 34), kr(s, 24, MUTE)).arrange(DOWN, buff=.22)
            g.add(card(body, color=c, buff=.35))
        g.arrange_in_grid(2, 2, buff=(.5, .4)).shift(DOWN * .35)
        for x in g:
            self.play(FadeIn(x, shift=UP * .3, scale=.92), run_time=.5)
            self.wait(.6)
        for x in g:
            self.play(Indicate(x, color=x[1][0].get_color(), scale_factor=1.04), run_time=.5)
        self.wait(2)


class TodayKospi(Scene):
    """오늘(11/2) 코스피: 금요일 5730.74 → 시가 5637.77(−1.62%) → 저점 5616.50 → 고점 5910.83 → 종가 5859.08(+2.24%) (today.json)."""
    def construct(self):
        t = TD["kospi"]
        P = 5730.74
        h = head("오늘 코스피 · 11월 2일(월)")
        self.play(FadeIn(h), run_time=.5)
        pts = [("금요일 종가", P, MUTE, UP), ("시작", t["open"], RED, DL), ("장중 저점", t["low"], RED, DR),
               ("장중 고점", t["high"], GRN, UP), ("마감", t["close"], YEL, DOWN)]
        ax = Axes(x_range=[0, 4.4, 1], y_range=[5560, 5960, 100], x_length=9.6, y_length=3.6,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False}).shift(UP * .35)
        self.play(Create(ax), run_time=.4)
        pv = DashedLine(ax.c2p(0, P), ax.c2p(4.4, P), color=MUTE, dash_length=.12, stroke_width=3)
        self.play(Create(pv), run_time=.3)
        prev = None
        for i, (lab, v, c, side) in enumerate(pts):
            p = ax.c2p(i + .2, v)
            dot = Dot(p, .13, color=c)
            pct = 100 * (v / P - 1)
            txt = VGroup(kr(lab, 24, MUTE), kr(f"{v:,.0f}" + ("" if i == 0 else f"  {sgn(pct, 2)}"), 30, c)).arrange(DOWN, buff=.06)
            txt.next_to(p, side, .2)
            anims = [FadeIn(dot, scale=1.4), FadeIn(txt, shift=side * .15)]
            if prev is not None:
                anims.append(Create(Line(prev, p, color=GRN if v > prev_v else RED, stroke_width=6)))
            self.play(*anims, run_time=.6)
            self.wait(1.1)
            prev, prev_v = p, v
        self.play(Flash(prev, color=YEL), run_time=.5)
        flow = card(VGroup(kr(t["flow1"], 32, PUR), kr(t["flow2"], 24, MUTE)).arrange(DOWN, buff=.1), color=PUR, buff=.22)
        kq = card(VGroup(kr(t["side1"], 30, INK), kr(t["side2"], 24, MUTE)).arrange(DOWN, buff=.1), color=YEL, buff=.22)
        VGroup(flow, kq).arrange(RIGHT, buff=.4).to_edge(DOWN, buff=.3)
        self.play(FadeIn(flow, shift=UP * .2)); self.wait(2.5)
        self.play(FadeIn(kq, shift=UP * .2)); self.wait(5)


class Intel(Scene):
    """인텔 10/30(현지) −28.58%: 4분기 매출 전망 150~160억달러 vs 시장 예상 171억달러. 1970년대 이후 최대 하루 낙폭."""
    def construct(self):
        h = head("금요일 밤 미국 · 인텔")
        self.play(FadeIn(h), run_time=.5)
        ax = NumberLine(x_range=[0, 180, 30], length=6.4, include_numbers=False, color=MUTE).shift(DOWN * 2.2 + LEFT * 1.2)
        self.play(Create(ax), run_time=.3)
        k = 6.4 / 180
        exp = Rectangle(width=171 * k, height=.8, stroke_width=0, fill_color=MUTE, fill_opacity=.9).move_to(ax.n2p(0), aligned_edge=LEFT).shift(UP * 2.6)
        gl = Rectangle(width=160 * k, height=.8, stroke_width=0, fill_color=RED, fill_opacity=.9).move_to(ax.n2p(0), aligned_edge=LEFT).shift(UP * 1.1)
        gl2 = Rectangle(width=10 * k, height=.8, stroke_width=0, fill_color=RED, fill_opacity=.4).move_to(ax.n2p(150), aligned_edge=LEFT).shift(UP * 1.1)
        el = kr("시장 기대  171억 달러", 30, INK).next_to(exp, UP, .12).align_to(exp, LEFT)
        gll = kr("인텔 4분기 전망  150~160억 달러", 30, RED).next_to(gl, UP, .12).align_to(gl, LEFT)
        self.play(GrowFromEdge(exp, LEFT), FadeIn(el), run_time=.8)
        self.wait(1.2)
        self.play(GrowFromEdge(gl, LEFT), FadeIn(gl2), FadeIn(gll), run_time=.8)
        self.wait(1.5)
        big = VGroup(kr("인텔 하루", 30, MUTE), kr("−28.6%", 84, RED), kr("1970년대 이후 최대 낙폭", 28, YEL)).arrange(DOWN, buff=.15)
        big.move_to(RIGHT * 3.0 + UP * .3)
        self.play(VGroup(ax, exp, gl, gl2, el, gll).animate.scale(.72).move_to(LEFT * 3.2 + UP * .2), run_time=.5)
        self.play(FadeIn(big[0]), FadeIn(big[1], scale=1.4), run_time=.6)
        self.play(Flash(big[1], color=RED, line_length=.4), FadeIn(big[2], shift=UP * .15), run_time=.6)
        self.wait(5)


class UsFri(Scene):
    """10/30(현지) 마감: 반도체지수 −7%대 · 나스닥 −2.86% 25,437 · S&P −1.82% 7,580 · 다우 −1.09% 51,770 · 내 사이트 데이터센터 테마 −8.55%."""
    def construct(self):
        h = head("금요일 밤 미국 · 하루 낙폭")
        self.play(FadeIn(h), run_time=.5)
        rows = [("반도체지수", 7.2, "−7%대", RED), ("나스닥", 2.86, "−2.86%", RED), ("S&P 500", 1.82, "−1.82%", ORG), ("다우", 1.09, "−1.09%", ORG)]
        base = Line(UP * 2.0, DOWN * 2.2, color=MUTE, stroke_width=3).shift(RIGHT * 2.0)
        self.play(Create(base), run_time=.3)
        for i, (nm, v, s, c) in enumerate(rows):
            y = 1.45 - i * 1.0
            r = Rectangle(width=v * .62, height=.66, stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to([base.get_x(), y, 0], aligned_edge=RIGHT)
            lab = kr(nm, 32).next_to(r, LEFT, .25)
            val = kr(s, 32, c).next_to(base, RIGHT, .25).set_y(y)
            self.play(GrowFromEdge(r, RIGHT), FadeIn(lab), FadeIn(val), run_time=.55)
            self.wait(.6)
        self.wait(1.5)
        site = card(VGroup(kr("내 테마 사이트 · 그날 꼴찌", 26, MUTE), kr("데이터센터 −8.6%", 38, RED)).arrange(DOWN, buff=.12), color=RED)
        site.to_edge(DOWN, buff=.3)
        self.play(FadeIn(site, shift=UP * .3)); self.wait(5)


class Week(Scene):
    """지난주 코스피 일별: 5469.47(−1.46) 5638.34(+3.09) 6012.44(+6.63) 5937.66(−1.24) 5730.74(−3.48). 10/23 5550.30 → +3.25%."""
    def construct(self):
        h = head("지난주 코스피 · 하루하루")
        self.play(FadeIn(h), run_time=.5)
        ax = NumberLine(x_range=[-.5, 4.5, 1], length=10, include_ticks=False, color=MUTE).shift(DOWN * .3)
        self.play(Create(ax), run_time=.4)
        bars, tags = VGroup(), VGroup()
        for i, (wd, dt, v, p) in enumerate(DAYS):
            c = GRN if p > 0 else RED
            r = Rectangle(width=1.2, height=max(abs(p) * .3, .06), stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to(ax.n2p(i), aligned_edge=DOWN if p > 0 else UP)
            t = kr(sgn(p), 34, c).next_to(r, UP if p > 0 else DOWN, .12)
            d = kr(wd, 30, MUTE).next_to(ax.n2p(i), DOWN if p > 0 else UP, .2)
            bars.add(r); tags.add(VGroup(t, d))
        for r, t, (_, _, _, p) in zip(bars, tags, DAYS):
            self.play(GrowFromEdge(r, DOWN if p > 0 else UP), FadeIn(t), run_time=.5)
            self.wait(.35)
        six = card(VGroup(kr("수요일 6,012", 34, GRN), kr("10거래일 만에 6000 회복", 24, MUTE)).arrange(DOWN, buff=.1), color=GRN)
        six.next_to(bars[2], RIGHT, .3).shift(UP * .3)
        self.play(Indicate(bars[2], scale_factor=1.08), FadeIn(six, shift=LEFT * .2), run_time=.7)
        self.wait(2.5)
        side = card(VGroup(kr("금요일 외국인 −1조 6천억", 32, BLU), kr("매도 사이드카 발동", 26, RED)).arrange(DOWN, buff=.1), color=BLU)
        side.next_to(bars[4], DOWN, .2).shift(LEFT * 1.4 + DOWN * .5)
        self.play(Indicate(bars[4], color=RED, scale_factor=1.08), FadeIn(side, shift=UP * .2), run_time=.7)
        self.wait(3)
        self.play(FadeOut(six), FadeOut(side), VGroup(ax, bars, tags).animate.scale(.7).shift(UP * 1.0), run_time=.6)
        wk = card(VGroup(kr("코스피 주간", 26, MUTE), kr("5,550 → 5,731", 34), kr("+3.3%", 50, GRN)).arrange(DOWN, buff=.1), color=GRN)
        kq = card(VGroup(kr("코스닥 주간", 26, MUTE), kr("752 → 724", 34), kr("−3.6%", 50, RED)).arrange(DOWN, buff=.1), color=RED)
        mo = card(VGroup(kr("10월 한 달", 26, MUTE), kr("9월 말 대비", 34), kr("−16.2%", 50, RED)).arrange(DOWN, buff=.1), color=YEL)
        VGroup(wk, kq, mo).arrange(RIGHT, buff=.45).to_edge(DOWN, buff=.3)
        for x in (wk, kq, mo):
            self.play(FadeIn(x, shift=UP * .3), run_time=.5)
            self.wait(2.2)
        self.wait(2)


class Duel(Scene):
    """3분기 영업이익: SK하이닉스 83조3338억(주주환원 약 100조, 배당 주당 2만원) vs 삼성전자 107조4405억(추가 주주환원 구체화 없음).
    주가: 하이닉스 10/28 +10.89% 148.7만 · 10/29 +2.62% 152.6만 / 삼성 10/29 −4.13% 23.2만."""
    def construct(self):
        h = head("지난주 핵심 ① · 3분기 실적", sub="영업이익과 다음 날 주가")
        self.play(FadeIn(h), run_time=.5)
        base = Line(LEFT * 5, RIGHT * 5, color=MUTE, stroke_width=3).shift(DOWN * 2.6)
        self.play(Create(base), run_time=.3)
        k = 2.7 / 110
        def col(x, name, v, c, sub):
            r = Rectangle(width=2.0, height=v * k, stroke_width=0, fill_color=c, fill_opacity=.95).move_to([x, -2.6, 0], aligned_edge=DOWN)
            n = kr(name, 34, c).next_to(base, DOWN, .2).set_x(x)
            val = kr(f"{v:g}조", 44, INK).next_to(r, UP, .12)
            return r, n, val, kr(sub, 26, MUTE)
        hx = col(-2.3, "SK하이닉스", 83.3, PUR, "")
        ss = col(2.3, "삼성전자", 107.4, BLU, "")
        for r, n, val, _ in (hx, ss):
            self.play(GrowFromEdge(r, DOWN), FadeIn(n), run_time=.7)
            self.play(FadeIn(val, scale=1.2), run_time=.4)
            self.wait(1.4)
        ret = card(VGroup(kr("주주환원", 26, YEL), kr("약 100조", 30, YEL)).arrange(DOWN, buff=.06), color=YEL, buff=.15)
        ret.move_to(hx[0])
        self.play(FadeIn(ret, shift=RIGHT * .2), run_time=.5)
        self.wait(2)
        a1 = VGroup(Arrow(DOWN * .4, UP * .4, color=GRN, stroke_width=10, buff=0), kr("+10.9%", 52, GRN)).arrange(RIGHT, buff=.15).next_to(hx[2], UP, .2)
        self.play(FadeIn(a1, shift=UP * .4), run_time=.6)
        self.wait(2.5)
        no = card(VGroup(kr("추가 주주환원", 26, RED), kr("구체안 ✕", 30, RED)).arrange(DOWN, buff=.06), color=RED, buff=.15).move_to(ss[0])
        self.play(FadeIn(no, shift=LEFT * .2), run_time=.5)
        self.wait(1.2)
        a2 = VGroup(Arrow(UP * .4, DOWN * .4, color=RED, stroke_width=10, buff=0), kr("−4.1%", 52, RED)).arrange(RIGHT, buff=.15).next_to(ss[2], UP, .2)
        self.play(FadeIn(a2, shift=DOWN * .4), run_time=.6)
        self.wait(5)


class AiDoubt(Scene):
    """지난주 미국 AI 의심: 목 알파벳 −12.6%(상장 이후 최대) · 메타 975억달러 조달 · MS 250억달러 회사채 · 금 인텔 −28.6%."""
    def construct(self):
        h = head("지난주 핵심 ② · AI 의심", sub="버는 돈보다 쓰는 돈이 빠르다?")
        self.play(FadeIn(h), run_time=.5)
        tl = Line(LEFT * 5.2, RIGHT * 5.2, color=MUTE, stroke_width=4).shift(UP * .5)
        self.play(Create(tl), run_time=.4)
        ev = [(-3.75, "목요일", card(VGroup(kr("알파벳", 32, RED), kr("−12.6%", 46, RED), kr("상장 이후 최대 하락", 22, MUTE)).arrange(DOWN, buff=.08), color=RED)),
              (0, "같은 주", card(VGroup(kr("메타", 26, ORG), kr("975억 달러 조달", 26, ORG), kr("MS 250억 달러 회사채", 22, MUTE)).arrange(DOWN, buff=.1), color=ORG, buff=.22)),
              (3.75, "금요일", card(VGroup(kr("인텔", 32, RED), kr("−28.6%", 46, RED), kr("4분기 전망 미달", 22, MUTE)).arrange(DOWN, buff=.08), color=RED))]
        for x, d, c in ev:
            dot = Dot([x, .5, 0], .15, color=c[0].get_color())
            lab = kr(d, 26, MUTE).move_to([x, 1.05, 0])
            c.move_to([x, -1.1, 0])
            self.play(FadeIn(dot, scale=1.5), FadeIn(lab), FadeIn(c, shift=UP * .2), run_time=.6)
            self.wait(2.4)
        self.wait(4)


class Fomc(Scene):
    """10/28 FOMC: 기준금리 3.75~4.00% 동결, 10 대 2 (2명 0.25%p 인상). 9월엔 0.25%p 인상."""
    def construct(self):
        h = head("FOMC · 10월 28일(현지)")
        self.play(FadeIn(h), run_time=.5)
        band = card(VGroup(kr("기준금리", 30, MUTE), kr("3.75 ~ 4.00%", 64, BLU), kr("동결", 44, YEL)).arrange(DOWN, buff=.15), color=BLU, buff=.4)
        band.shift(LEFT * 2.8 + DOWN * .3)
        self.play(FadeIn(band, scale=.9), run_time=.7)
        self.wait(1.5)
        dots = VGroup(*[Circle(.26, color=GRN if i < 10 else RED, fill_opacity=1, stroke_width=0) for i in range(12)]).arrange_in_grid(3, 4, buff=.22)
        dots.shift(RIGHT * 3.0 + UP * .1)
        self.play(LaggedStart(*[FadeIn(x, scale=.5) for x in dots[:10]], lag_ratio=.08), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(x, scale=1.6) for x in dots[10:]], lag_ratio=.3), run_time=.6)
        lg = VGroup(kr("● 동결 10", 28, GRN), kr("● 인상 2", 28, RED)).arrange(RIGHT, buff=.5).next_to(dots, DOWN, .35)
        self.play(FadeIn(lg), run_time=.4)
        self.wait(5)


class NextWeek(Scene):
    """이번 주(11/2~6): 3일 미국 중간선거 · 6일 미국 10월 고용보고서 · 애플·AMD·LG에너지솔루션 실적 · 증권가 코스피 밴드 5700~6500."""
    def construct(self):
        h = head("이번 주 꼭 볼 일정", YEL)
        self.play(FadeIn(h), run_time=.5)
        items = [("11/3(화)", "미국 중간선거", "상원 · 하원 누가 가져가나", RED),
                 ("11/6(금)", "미국 10월 고용보고서", "금리 더 올릴까?", BLU),
                 ("이번 주", "실적 발표", "애플 · AMD · LG에너지솔루션", PUR)]
        g = VGroup()
        for d, t, s, c in items:
            g.add(card(VGroup(kr(d, 30, c), VGroup(kr(t, 36), kr(s, 24, MUTE)).arrange(DOWN, buff=.08, aligned_edge=LEFT)).arrange(RIGHT, buff=.5), color=c, buff=.28))
        g.arrange(DOWN, buff=.3, aligned_edge=LEFT).shift(UP * .1)
        for x in g:
            self.play(FadeIn(x, shift=RIGHT * .4), run_time=.55)
            self.wait(2.2)
        bar = NumberLine(x_range=[5600, 6600, 100], length=8, include_ticks=False, color=MUTE).to_edge(DOWN, buff=.75)
        rng = Line(bar.n2p(5700), bar.n2p(6500), color=YEL, stroke_width=14)
        l1, l2 = kr("5,700", 24, YEL).next_to(bar.n2p(5700), DOWN, .15), kr("6,500", 24, YEL).next_to(bar.n2p(6500), DOWN, .15)
        me = VGroup(Triangle(color=RED, fill_opacity=1).scale(.13).rotate(PI).next_to(bar.n2p(5730.74), UP, .02), kr("5,731", 24, RED))
        me[1].next_to(me[0], UP, .05)
        self.play(Create(bar), Create(rng), FadeIn(l1), FadeIn(l2), run_time=.6)
        self.play(FadeIn(me, shift=DOWN * .2)); self.wait(5)


class Summary(Scene):
    def construct(self):
        h = head("세 줄 요약", YEL)
        ls = [("1", TD["sum1"], RED), ("2", "지난주 코스피 +3.3% · 6000 찍고 5731", GRN), ("3", "알파벳 · 인텔발 AI 의심 → 중간선거 · 고용", BLU)]
        g = VGroup()
        for n, t, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), kr(t, 34)).arrange(RIGHT, buff=.4))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.6).shift(DOWN * .1)
        self.play(FadeIn(h))
        for r in g:
            self.play(FadeIn(r, shift=RIGHT * .3), run_time=.5)
            self.wait(2.2)
        foot = kr("금리·주가 50년 /invest   ·   미국 테마 강도 /themes", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(4)
