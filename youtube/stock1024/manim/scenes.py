# 증시 2026-10-24(토) 어제·오늘 + 이번 주 정리 모션그래픽. 16:9, 핵심 내용은 가운데(가로 ±5.5)에 두어 세로 쇼츠에서도 잘라 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>   (1920×1080)
# 숫자: Yahoo 종가(raw/stock1024/yf.json · intra_KS11.json) + 기사(stock1024/script.json "_출처").
from manim import *
import numpy as np, json, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
DIM = "#3a3f4b"
KR = "Noto Sans CJK KR"
config.background_color = BG
R = os.path.join(os.path.dirname(__file__), "../../raw/stock1024/")
Y = json.load(open(R + "yf.json"))
INTRA = json.load(open(R + "intra_KS11.json"))
PREV, OPEN, LOW, CLOSE = 5533.77, 5403.17, 5305.98, 5550.30       # 10/22 종가 · 10/23 시가·저가·종가
WEEK = ["2026-10-16", "2026-10-19", "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23"]


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK, sub=None):
    h = kr(s, 46, c).to_edge(UP, buff=.45)
    if sub:
        return VGroup(h, kr(sub, 26, MUTE).next_to(h, DOWN, .18))
    return h


def close(sym, day):
    v = dict((r[0], r[4]) for r in Y[sym] if r[4] is not None)
    return v.get(day)


def sgn(v, d=1):
    return ("+" if v > 0 else ("−" if v < 0 else "")) + f"{abs(v):.{d}f}%"


class Agenda(Scene):
    """오늘 볼 세 가지: 어제 한국장 · 오늘 새벽 미국장 · 이번 주 전체."""
    def construct(self):
        h = head("오늘 정리할 세 가지")
        self.play(FadeIn(h, shift=DOWN * .2), run_time=.5)
        items = [("①", "어제 한국장", "10/23(금) 마감", RED), ("②", "오늘 새벽 미국장", "10/23(금) 현지 마감", BLU), ("③", "이번 주 전체", "10/19 ~ 10/23", YEL)]
        g = VGroup()
        for n, t, s, c in items:
            body = VGroup(kr(n, 60, c), kr(t, 40), kr(s, 26, MUTE)).arrange(DOWN, buff=.25)
            g.add(card(body, color=c, buff=.45))
        g.arrange(RIGHT, buff=.5).shift(DOWN * .3)
        self.play(LaggedStart(*[FadeIn(x, shift=UP * .4, scale=.9) for x in g], lag_ratio=.35), run_time=1.8)
        for x in g:
            self.play(Indicate(x, color=x[0].get_color(), scale_factor=1.04), run_time=.6)
        self.wait(3)


class FriKospi(Scene):
    """10/23(금) 코스피 5분봉: 전일 5533.77 점선 · 시가 −2.36% · 장중 5305.98(−4.1%) · 종가 5550.30(+0.30%)."""
    def construct(self):
        h = head("어제 코스피 · 10월 23일(금)")
        self.play(FadeIn(h, shift=DOWN * .2), run_time=.5)
        vals = [v for d, v in INTRA if d.startswith("10-23")]
        vals[0] = OPEN; vals[-1] = CLOSE
        n = len(vals)
        ax = Axes(x_range=[0, n - 1, 12], y_range=[5240, 5580, 50], x_length=9.0, y_length=5.0,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False}).shift(DOWN * .55 + LEFT * 1.9)
        self.play(Create(ax), run_time=.5)
        pv = DashedLine(ax.c2p(0, PREV), ax.c2p(n - 1, PREV), color=MUTE, dash_length=.12, stroke_width=3)
        pl = kr("그제 종가 5,534", 26, MUTE).next_to(pv, UP, .1).align_to(pv, LEFT).shift(RIGHT * .3)
        self.play(Create(pv), FadeIn(pl), run_time=.6)
        line = ax.plot_line_graph(list(range(n)), vals, line_color=GRN, add_vertex_dots=False, stroke_width=6)["line_graph"]
        tr = ValueTracker(0)
        def num():
            v = np.interp(tr.get_value(), range(n), vals); p = 100 * (v / PREV - 1)
            c = GRN if p > 0 else RED
            return VGroup(kr(f"{v:,.2f}", 60, c), kr(sgn(p, 2), 44, c)).arrange(DOWN, buff=.1).move_to(RIGHT * 4.6 + UP * 1.4)
        nm = always_redraw(num)
        self.add(nm)
        o = VGroup(Dot(ax.c2p(0, OPEN), .11, color=RED), kr("시작 −2.4%", 26, RED).next_to(ax.c2p(0, OPEN), UP, .9).shift(RIGHT * .6))
        self.play(FadeIn(o), run_time=.4)
        self.play(Create(line), tr.animate.set_value(n - 1), run_time=4.0, rate_func=linear)
        il = int(np.argmin(vals))
        lo = VGroup(Dot(ax.c2p(il, vals[il]), .12, color=YEL), kr("장중 5,306 · −4.1%", 28, YEL).next_to(ax.c2p(il, vals[il]), DR, .12))
        self.play(FadeIn(lo, scale=1.2), Flash(ax.c2p(il, vals[il]), color=YEL), run_time=.7)
        chip = card(kr("+244포인트 반등", 34, GRN), color=GRN).next_to(nm, DOWN, .45)
        self.play(FadeIn(chip, shift=UP * .2)); self.wait(4)


class Hynix(Scene):
    """SK하이닉스 10/23: 전일 122.3만 → 장중 117.1만(−4.3%) → 종가 127.7만(+4.42%). 솔리다임 미국 상장 추진 중단(기사)."""
    def construct(self):
        h = head("반전의 주인공 · SK하이닉스")
        self.play(FadeIn(h), run_time=.5)
        news = card(VGroup(kr("자회사 솔리다임", 30, MUTE), kr("미국 상장 추진 중단", 44, YEL), kr("→ 중복상장 걱정 해소", 28, INK)).arrange(DOWN, buff=.18), color=YEL)
        news.shift(LEFT * 3.6 + UP * .2)
        self.play(FadeIn(news, shift=RIGHT * .3), run_time=.7)
        ax = NumberLine(x_range=[115, 130, 5], length=5.2, rotation=PI / 2, color=MUTE, include_numbers=False).shift(RIGHT * 2.6 + DOWN * .4)
        self.play(Create(ax), run_time=.4)
        lab = lambda v, s, c, side: VGroup(Dot(ax.n2p(v), .1, color=c), kr(s, 28, c).next_to(ax.n2p(v), side, .25))
        pv = lab(122.3, "그제 122.3만", MUTE, LEFT)
        self.play(FadeIn(pv), run_time=.4)
        dot = Dot(ax.n2p(122.3), .2, color=WHITE)
        self.play(FadeIn(dot), run_time=.2)
        self.play(dot.animate.move_to(ax.n2p(117.1)).set_color(RED), run_time=1.0)
        self.play(FadeIn(lab(117.1, "장중 117.1만 · −4.3%", RED, RIGHT)), run_time=.4)
        tr = Line(ax.n2p(117.1), ax.n2p(127.7), color=GRN, stroke_width=12)
        self.play(Create(tr), dot.animate.move_to(ax.n2p(127.7)).set_color(GRN), run_time=1.4)
        top = lab(127.7, "종가 127.7만", GRN, RIGHT)
        big = kr("+4.42%", 64, GRN).next_to(top, DOWN, .3).align_to(top[1], LEFT)
        self.play(FadeIn(top), FadeIn(big, scale=1.3), Flash(dot, color=GRN), run_time=.7)
        self.wait(5)


class Flows(Scene):
    """10/23 코스피 수급(뉴스핌): 외국인 −1조 938억 · 기관 +7,995억 · 개인 +2,336억. 코스닥 751.69 −1.62%, 에코프로 −5.83%."""
    def construct(self):
        h = head("누가 팔고, 누가 샀나 · 10/23")
        self.play(FadeIn(h), run_time=.5)
        rows = [("외국인", -10938, BLU, "−1조 938억"), ("기관", 7995, PUR, "+7,995억"), ("개인", 2336, GRN, "+2,336억")]
        mid = Line(UP * 1.9, DOWN * 1.4, color=MUTE, stroke_width=3).shift(RIGHT * .3)
        self.play(Create(mid), run_time=.4)
        for i, (nm, v, c, s) in enumerate(rows):
            y = 1.3 - i * 1.15
            w = abs(v) / 2400
            r = Rectangle(width=w, height=.75, stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to([mid.get_x(), y, 0], aligned_edge=RIGHT if v < 0 else LEFT)
            name = kr(nm, 34).move_to([mid.get_x() + (.9 if v < 0 else -.9), y, 0])
            val = kr(s, 34, c).next_to(r, LEFT if v < 0 else RIGHT, .2)
            self.play(GrowFromEdge(r, RIGHT if v < 0 else LEFT), FadeIn(name), run_time=.6)
            self.play(FadeIn(val, shift=(LEFT if v < 0 else RIGHT) * .2), run_time=.3)
        self.wait(2.5)
        kq = card(VGroup(kr("코스닥 751.69  −1.62%", 34, RED), kr("에코프로 −5.8% · 2차전지 약세", 28, MUTE)).arrange(DOWN, buff=.15), color=RED)
        kq.to_edge(DOWN, buff=.45)
        self.play(FadeIn(kq, shift=UP * .3)); self.wait(4)


class UsNight(Scene):
    """10/23(현지) 뉴욕: 다우 52215.16 −1.23% · S&P 500 7623.68 −0.52% · 나스닥 25955.34 −0.21% (Yahoo·뉴스1)."""
    def construct(self):
        h = head("오늘 새벽 미국장", sub="10월 23일(금) 현지 마감")
        self.play(FadeIn(h), run_time=.5)
        rows = [("다우", "^DJI"), ("S&P 500", "^GSPC"), ("나스닥", "^IXIC")]
        g = VGroup()
        for nm, s in rows:
            a, b = close(s, "2026-10-22"), close(s, "2026-10-23")
            p = 100 * (b / a - 1)
            t = ValueTracker(0)
            body = VGroup(kr(nm, 36, MUTE), kr(f"{b:,.0f}", 52), kr(sgn(p, 2), 48, RED)).arrange(DOWN, buff=.2)
            g.add(card(body, color=RED, buff=.4))
        g.arrange(RIGHT, buff=.45).shift(DOWN * .2)
        self.play(LaggedStart(*[FadeIn(x, shift=DOWN * .3) for x in g], lag_ratio=.3), run_time=1.4)
        self.play(Indicate(g[0], color=RED, scale_factor=1.06), run_time=.8)
        foot = kr("다우 −652포인트 · 기술주보다 넓게 팔렸다", 32, YEL).to_edge(DOWN, buff=.6)
        self.play(FadeIn(foot, shift=UP * .2)); self.wait(5)


class Oil(Scene):
    """WTI 12월물 일봉(Yahoo) 10/16~10/23 + 10/20 장중 110.48. 기사: 10/23 WTI +3.8% 103.27, 브렌트 116.72(4/29 이후 최고), 이란 공습 재개 검토 보도."""
    def construct(self):
        h = head("기름값이 다시 오른다", sub="WTI 원유 · 달러/배럴")
        self.play(FadeIn(h), run_time=.5)
        days = WEEK; vals = [close("CL=F", d) for d in days]
        hi = max(r[2] for r in Y["CL=F"] if r[0] == "2026-10-20")
        ax = Axes(x_range=[-.5, len(days) - .5, 1], y_range=[94, 112, 4], x_length=8.2, y_length=4.6,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False}).shift(LEFT * 2.0 + DOWN * .6)
        self.play(Create(ax), run_time=.4)
        labs = VGroup(*[kr(t, 24, MUTE).next_to(ax.c2p(i, 94), DOWN, .15) for i, t in enumerate(["지난 금", "월", "화", "수", "목", "금"])])
        self.play(FadeIn(labs), run_time=.3)
        wick = Line(ax.c2p(2, vals[2]), ax.c2p(2, hi), color=ORG, stroke_width=4)
        line = ax.plot_line_graph(list(range(len(days))), vals, line_color=ORG, vertex_dot_radius=.09, stroke_width=6)
        self.play(Create(line), run_time=2.0)
        self.play(Create(wick), run_time=.4)
        hl = kr(f"화 장중 {hi:.1f}", 26, ORG).next_to(ax.c2p(2, hi), UP, .12)
        self.play(FadeIn(hl), run_time=.4)
        last = kr("103달러 · 하루 +3.8%", 30, YEL).next_to(ax.c2p(5, vals[5]), UP, .35).shift(LEFT * 1.3)
        self.play(FadeIn(last, shift=UP * .2), Flash(ax.c2p(5, vals[5]), color=YEL), run_time=.6)
        news = card(VGroup(kr("美·이스라엘", 28, MUTE), kr("이란 공습 재개 검토", 34, RED), kr("보도", 26, MUTE)).arrange(DOWN, buff=.12), color=RED)
        br = card(VGroup(kr("브렌트유", 28, MUTE), kr("116.72달러", 40, YEL), kr("4월 말 이후 최고", 24, MUTE)).arrange(DOWN, buff=.12), color=YEL)
        VGroup(news, br).arrange(DOWN, buff=.4).to_edge(RIGHT, buff=.5).shift(DOWN * .3)
        self.play(FadeIn(news, shift=LEFT * .3), run_time=.5)
        self.play(FadeIn(br, shift=LEFT * .3), run_time=.5)
        self.wait(5)


class Spread(Scene):
    """10/23 매도 확산: 기술주 → 금융 · 필수소비재 등 방어 업종까지 (블록미디어·MTN)."""
    def construct(self):
        h = head("매도가 번졌다")
        self.play(FadeIn(h), run_time=.5)
        src = card(kr("기술주", 44, RED), color=RED).shift(LEFT * 4 + DOWN * .3)
        dst = VGroup(card(kr("금융", 40, ORG), color=ORG), card(kr("필수소비재", 40, ORG), color=ORG), card(kr("방어 업종", 40, ORG), color=ORG)).arrange(DOWN, buff=.45).shift(RIGHT * 3.2 + DOWN * .3)
        self.play(FadeIn(src, scale=.9), run_time=.5)
        arrs = VGroup(*[Arrow(src.get_right(), d.get_left(), color=MUTE, stroke_width=6, buff=.2) for d in dst])
        for a, d in zip(arrs, dst):
            self.play(GrowArrow(a), FadeIn(d, shift=RIGHT * .2), run_time=.5)
        note = kr("“안전하다던 곳까지 같이 팔렸다”", 32, YEL).to_edge(DOWN, buff=.6)
        self.play(FadeIn(note)); self.wait(5)


class Zigzag(Scene):
    """이번 주 코스피 일별 등락: +1.76 −3.73 +3.29 −3.52 +0.30 → 주간 5668.05 → 5550.30 (−2.08%), 코스닥 794.78 → 751.69 (−5.42%)."""
    def construct(self):
        h = head("이번 주 코스피 · 하루하루")
        self.play(FadeIn(h), run_time=.5)
        cl = [close("^KS11", d) for d in WEEK[:-1]] + [CLOSE]
        ch = [100 * (b / a - 1) for a, b in zip(cl, cl[1:])]
        ax = NumberLine(x_range=[-.5, 4.5, 1], length=10, include_ticks=False, color=MUTE).shift(UP * .4)
        self.play(Create(ax), run_time=.4)
        bars, tags = VGroup(), VGroup()
        for i, (p, wd) in enumerate(zip(ch, "월화수목금")):
            c = GRN if p > 0 else RED
            r = Rectangle(width=1.2, height=max(abs(p) * .62, .06), stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to(ax.n2p(i), aligned_edge=DOWN if p > 0 else UP)
            t = kr(sgn(p), 36, c).next_to(r, UP if p > 0 else DOWN, .15)
            d = kr(wd, 30, MUTE).next_to(ax.n2p(i), DOWN if p > 0 else UP, .2)
            bars.add(r); tags.add(VGroup(t, d))
        for r, t, p in zip(bars, tags, ch):
            self.play(GrowFromEdge(r, DOWN if p > 0 else UP), FadeIn(t), run_time=.55)
        for i in (1, 2, 3):
            self.play(Indicate(bars[i], scale_factor=1.06), run_time=.35)
        self.wait(5)
        week = card(VGroup(kr("코스피 주간", 28, MUTE), kr("5,668 → 5,550", 36), kr("−2.1%", 54, RED)).arrange(DOWN, buff=.12), color=RED)
        kq = card(VGroup(kr("코스닥 주간", 28, MUTE), kr("795 → 752", 36), kr("−5.4%", 54, RED)).arrange(DOWN, buff=.12), color=RED)
        VGroup(week, kq).arrange(RIGHT, buff=.6).to_edge(DOWN, buff=.25)
        self.play(VGroup(ax, bars, tags).animate.scale(.72).shift(UP * .7), run_time=.6)
        self.play(FadeIn(week, shift=UP * .3), run_time=.6)
        self.wait(4)
        self.play(FadeIn(kq, shift=UP * .3), run_time=.6)
        self.wait(4)


class AiTimeline(Scene):
    """이번 주 AI 투자 의심: 화 코어위브 빚 걱정(코스피 −3.7%) → 목 밤 메타 의결권 없는 신주 발행(실적은 예상 상회)."""
    def construct(self):
        h = head("이번 주 질문 ①", sub="AI에 쏟은 돈, 언제 회수하나?")
        self.play(FadeIn(h), run_time=.5)
        tl = Line(LEFT * 5.2, RIGHT * 5.2, color=MUTE, stroke_width=4).shift(UP * .2)
        self.play(Create(tl), run_time=.4)
        a = VGroup(Dot([-3, .2, 0], .16, color=ORG), kr("화요일", 28, MUTE).move_to([-3, .8, 0]),
                   card(VGroup(kr("코어위브 빚 걱정", 32, ORG), kr("코스피 −3.7%", 28, RED)).arrange(DOWN, buff=.12), color=ORG).move_to([-3, -1.1, 0]))
        b = VGroup(Dot([3, .2, 0], .16, color=RED), kr("목요일 밤", 28, MUTE).move_to([3, .8, 0]),
                   card(VGroup(kr("메타 실적  예상 상회 ✓", 30, GRN), kr("의결권 없는 새 주식 발행", 30, RED)).arrange(DOWN, buff=.14), color=RED).move_to([3, -1.25, 0]))
        self.play(FadeIn(a, shift=UP * .2), run_time=.7)
        self.wait(2.5)
        self.play(FadeIn(b, shift=UP * .2), run_time=.7)
        self.play(Indicate(b[2], color=RED, scale_factor=1.05))
        self.wait(5)


class AiBars(Scene):
    """10/22(현지) 하루: 메타 −6.98% · 코어위브 −10.06% · 엔비디아 −4.40% · 반도체지수 −6.72% · 나스닥 −2.60% (Yahoo)."""
    def construct(self):
        h = head("목요일 밤 미국 · 하루 낙폭")
        self.play(FadeIn(h), run_time=.5)
        rows = [("코어위브", "CRWV"), ("메타", "META"), ("반도체지수", "^SOX"), ("엔비디아", "NVDA"), ("나스닥", "^IXIC")]
        base = Line(UP * 2.0, DOWN * 2.8, color=MUTE, stroke_width=3).shift(RIGHT * 3.2)
        self.play(Create(base), run_time=.3)
        for i, (nm, s) in enumerate(rows):
            p = 100 * (close(s, "2026-10-22") / close(s, "2026-10-21") - 1)
            y = 1.55 - i * 1.0
            r = Rectangle(width=abs(p) * .62, height=.66, stroke_width=0, fill_color=RED if nm != "나스닥" else ORG, fill_opacity=1)
            r.move_to([base.get_x(), y, 0], aligned_edge=RIGHT)
            lab = kr(nm, 32).next_to(r, LEFT, .25)
            val = kr(sgn(p), 32, RED if nm != "나스닥" else ORG).next_to(base, RIGHT, .25).set_y(y)
            self.play(GrowFromEdge(r, RIGHT), FadeIn(lab), FadeIn(val), run_time=.5)
        note = kr("나스닥 6월 이후 최대 낙폭", 30, YEL).to_corner(DL, buff=.5)
        self.play(FadeIn(note)); self.wait(5)


class Macro(Scene):
    """이번 주 거시: 원/달러 1340.95 → 1324.6(연중 최저) · 미 10년물 5.10 → 4.99 · 금 4181 → 4010(−4.1%) · 한은 기준금리 동결(10/22)."""
    def construct(self):
        h = head("이번 주 질문 ② · 유가 · 금리 · 원화")
        self.play(FadeIn(h), run_time=.5)
        g10a, g10b = close("^TNX", "2026-10-16"), close("^TNX", "2026-10-23")
        ga, gb = close("GC=F", "2026-10-16"), close("GC=F", "2026-10-23")
        tiles = [("한국은행", "기준금리 동결", "10/22(목)", MUTE),
                 ("원·달러 환율", "1,341 → 1,324원", "원화 강세 · 연중 최저", GRN),
                 ("미국 10년물 금리", f"{g10a:.2f} → {g10b:.2f}%", "조금 내려옴", BLU),
                 ("금값", f"{ga:,.0f} → {gb:,.0f}달러", sgn(100 * (gb / ga - 1)), RED)]
        g = VGroup()
        for t, v, s, c in tiles:
            g.add(card(VGroup(kr(t, 28, MUTE), kr(v, 38, c if c != MUTE else INK), kr(s, 26, c)).arrange(DOWN, buff=.14), color=c if c != MUTE else "#2a2e37", buff=.35))
        g.arrange_in_grid(2, 2, buff=(.5, .45)).shift(DOWN * .35)
        for x in g:
            self.play(FadeIn(x, shift=UP * .25, scale=.95), run_time=.55)
            self.wait(1.6)
        self.wait(3)


class BigTwoFlat(Scene):
    """삼성전자 10/16 215,500 → 10/23 215,500 (0.0%) · SK하이닉스 1,272,000 → 1,277,000 (+0.39%). 사이 하루 ±5% 넘게 출렁임(Yahoo)."""
    def construct(self):
        h = head("대장주는 제자리", sub="지난주 금요일 → 이번 주 금요일")
        self.play(FadeIn(h), run_time=.5)
        def one(name, sym, color, shift):
            vals = [close(sym, d) for d in WEEK]
            base = vals[0]; pct = [100 * (v / base - 1) for v in vals]
            ax = Axes(x_range=[0, 5, 1], y_range=[-6, 6, 3], x_length=5.0, y_length=3.6,
                      axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False}).shift(shift)
            zero = DashedLine(ax.c2p(0, 0), ax.c2p(5, 0), color=YEL, dash_length=.1, stroke_width=3)
            ln = ax.plot_line_graph(list(range(6)), pct, line_color=color, vertex_dot_radius=.08, stroke_width=6)
            t = kr(name, 34, color).next_to(ax, UP, .2)
            end = kr(sgn(pct[-1]) if abs(pct[-1]) > .05 else "0.0%", 44, YEL).next_to(ax.c2p(5, pct[-1]), UP, .35)
            return ax, zero, ln, t, end, vals
        L = one("삼성전자", "005930.KS", BLU, LEFT * 3.3 + DOWN * .6)
        Rr = one("SK하이닉스", "000660.KS", PUR, RIGHT * 3.0 + DOWN * .6)
        for ax, zero, ln, t, end, vals in (L, Rr):
            self.play(Create(ax), FadeIn(t), Create(zero), run_time=.5)
            self.play(Create(ln), run_time=1.6)
            self.play(FadeIn(end, scale=1.3), run_time=.4)
        s1 = kr("21만 5,500원 → 21만 5,500원", 30, INK).next_to(L[0], DOWN, .35)
        s2 = kr("127만 2천 → 127만 7천", 30, INK).next_to(Rr[0], DOWN, .35)
        self.play(FadeIn(s1), FadeIn(s2)); self.wait(6)


class NextWeek(Scene):
    """다음 주(10/26~30): FOMC 27~28일(현지) → 결과 한국 시간 29일 새벽 · MS·알파벳·아마존 실적 · 삼성전자·SK하이닉스 3분기 실적 (한국경제·SBS Biz)."""
    def construct(self):
        h = head("다음 주 꼭 볼 일정", YEL, sub="시장이 부르는 이름: 슈퍼위크")
        self.play(FadeIn(h), run_time=.5)
        items = [("FOMC", "27~28일(현지) · 결과 29일 새벽(한국)", BLU),
                 ("빅테크 실적", "마이크로소프트 · 알파벳 · 아마존", PUR),
                 ("한국 반도체", "삼성전자 · SK하이닉스 3분기 실적", GRN)]
        g = VGroup()
        for t, s, c in items:
            g.add(card(VGroup(kr(t, 38, c), kr(s, 28, INK)).arrange(RIGHT, buff=.5), color=c, buff=.32))
        g.arrange(DOWN, buff=.38, aligned_edge=LEFT).shift(DOWN * .2)
        for x in g:
            self.play(FadeIn(x, shift=RIGHT * .4), run_time=.6)
            self.wait(1.8)
        ln = kr("내 기준선 · 금요일 장중 저점 5,306", 30, YEL).to_edge(DOWN, buff=.45)
        self.play(FadeIn(ln, shift=UP * .2)); self.wait(5)


class Summary(Scene):
    def construct(self):
        h = head("세 줄 요약", YEL)
        ls = [("1", "어제 코스피 장중 −4% → +0.3% · 오늘 새벽 다우 −1.2%", RED),
              ("2", "이번 주 코스피 −2.1% · 코스닥 −5.4%", BLU),
              ("3", "다음 주 FOMC · 빅테크 · 삼성·하이닉스 실적", YEL)]
        g = VGroup()
        for n, t, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), kr(t, 36)).arrange(RIGHT, buff=.4))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.6).shift(DOWN * .1)
        self.play(FadeIn(h))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * .3) for r in g], lag_ratio=.5), run_time=2)
        foot = kr("금리·주가 50년 /invest   ·   미국 테마 강도 /themes", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(4)
