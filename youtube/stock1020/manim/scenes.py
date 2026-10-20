# 증시 2026-10-20(화) 마감 분석 모션그래픽. 16:9, 핵심 내용은 가운데(가로 ±5.5)에 두어 세로 쇼츠에서도 잘라 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>   (1920×1080)
# 숫자: Yahoo 종가(raw/stock1020/yf.json · kospi_intra.json) + 기사(stock1020/script.json "_출처").
from manim import *
import numpy as np, json, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
DIM = "#3a3f4b"
KR = "Noto Sans CJK KR"
config.background_color = BG
R = os.path.join(os.path.dirname(__file__), "../../raw/stock1020/")
Y = json.load(open(R + "yf.json"))
INTRA = json.load(open(R + "kospi_intra.json"))
T = json.load(open(R + "themes/data.json"))
KOSPI = [x for x in Y["^KS11"]]
PREV, CLOSE, OPEN, LOW = 5768.01, 5552.74, 5733.57, 5493.24      # 10/19 종가 · 10/20 시가·저가·종가 (기사·Yahoo)


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK, sub=None):
    h = kr(s, 46, c).to_edge(UP, buff=.45)
    if sub:
        return VGroup(h, kr(sub, 26, MUTE).next_to(h, DOWN, .18))
    return h


def glow(m, c, n=4):
    """선·막대 뒤에 번지는 빛 (같은 모양을 굵고 옅게 몇 겹)."""
    return VGroup(*[m.copy().set_stroke(c, width=m.get_stroke_width() + 6 * i, opacity=.12 / i) for i in range(1, n + 1)])


def counter(v0, v1, fmt, size, color, **kw):
    t = ValueTracker(v0)
    m = always_redraw(lambda: kr(fmt(t.get_value()), size, color).move_to(kw.get("at", ORIGIN)))
    return t, m


class KospiDay(Scene):
    """오늘 코스피 하루: 전일 종가 5768 점선 · 시가 5733 · 장중 저점 5493(기사) · 종가 5552.74 (−3.73%)."""
    def construct(self):
        h = head("오늘 코스피 · 10월 20일(화)")
        self.play(FadeIn(h, shift=DOWN * .2), run_time=.5)
        pts = [[OPEN]] + [[x[1]] for x in INTRA]
        vals = [OPEN] + [x[1] for x in INTRA]
        vals[-1] = CLOSE
        n = len(vals)
        ax = Axes(x_range=[0, n - 1, 12], y_range=[5450, 5800, 50], x_length=9.0, y_length=5.0,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False}).shift(DOWN * .55 + LEFT * 1.9)
        self.play(Create(ax), run_time=.5)
        pv = DashedLine(ax.c2p(0, PREV), ax.c2p(n - 1, PREV), color=MUTE, dash_length=.12, stroke_width=3)
        pl = kr("어제 종가 5,768", 26, MUTE).next_to(pv, UP, .1).align_to(pv, LEFT).shift(RIGHT * .35)
        c5 = DashedLine(ax.c2p(0, 5554.22), ax.c2p(n - 1, 5554.22), color=ORG, dash_length=.1, stroke_width=2, stroke_opacity=.7)
        self.play(Create(pv), FadeIn(pl), run_time=.6)
        line = ax.plot_line_graph(list(range(n)), vals, line_color=RED, add_vertex_dots=False, stroke_width=6)["line_graph"]
        area = ax.get_area(ax.plot(lambda x: np.interp(x, range(n), vals), x_range=[0, n - 1]), bounded_graph=ax.plot(lambda x: PREV, x_range=[0, n - 1]), color=RED, opacity=.18)
        tr = ValueTracker(0)
        num = always_redraw(lambda: kr(f"{np.interp(tr.get_value(), range(n), vals):,.2f}", 60, RED).move_to(RIGHT * 4.6 + UP * 1.6))
        self.add(num)
        self.play(Create(line), tr.animate.set_value(n - 1), run_time=3.2, rate_func=linear)
        self.play(FadeIn(area), Create(c5), run_time=.6)
        il = int(np.argmin(vals))
        lo = VGroup(Dot(ax.c2p(il, vals[il]), .11, color=YEL), kr("장중 5,493 · 5500선 붕괴", 28, YEL).next_to(ax.c2p(il, vals[il]), DOWN, .18))
        cl = VGroup(Dot(ax.c2p(n - 1, CLOSE), .13, color=RED), kr("종가", 28, RED).next_to(ax.c2p(n - 1, CLOSE), DOWN, .2))
        self.play(FadeIn(lo, scale=1.2), Flash(ax.c2p(il, vals[il]), color=YEL), run_time=.7)
        self.play(FadeIn(cl, scale=1.2), run_time=.5)
        lab5 = VGroup(DashedLine(LEFT * .3, RIGHT * .3, color=ORG, dash_length=.08), kr("지난주 서킷 날 종가 5,554", 22, ORG)).arrange(RIGHT, buff=.15)
        chip = card(VGroup(kr("−215.27", 40, RED), kr("−3.73%", 52, RED)).arrange(DOWN, buff=.12), color=RED).next_to(num, DOWN, .35)
        lab5.next_to(chip, DOWN, .35)
        self.play(FadeIn(lab5), FadeIn(chip, shift=UP * .2), run_time=.6)
        self.play(Indicate(chip, color=RED, scale_factor=1.06)); self.wait(3)


class TenDays(Scene):
    """10/2 7003 → 10/15 5554(서킷) → 10/16 5668 → 10/19 5768 → 10/20 5552: 이틀 반등분 하루 만에 반납."""
    def construct(self):
        h = head("코스피 최근 13거래일", sub="이틀 반등 → 하루 만에 반납")
        self.play(FadeIn(h), run_time=.5)
        k = [x for x in KOSPI if x[0] >= "2026-10-01"]
        n = len(k)
        ax = Axes(x_range=[-.6, n - .4, 1], y_range=[5000, 7300, 500], x_length=11, y_length=5.0,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False}).shift(DOWN * .75)
        self.add(ax)
        bars, labs = VGroup(), VGroup()
        for i, (d, v) in enumerate(k):
            c = RED if d == "2026-10-20" else (GRN if d in ("2026-10-16", "2026-10-19") else (ORG if d == "2026-10-15" else DIM))
            top, bot = ax.c2p(i, v), ax.c2p(i, 5000)
            r = Rectangle(width=.62, height=top[1] - bot[1], stroke_width=0, fill_color=c, fill_opacity=1).move_to(bot, aligned_edge=DOWN)
            bars.add(r)
            labs.add(kr(f"{int(d[5:7])}/{int(d[8:])}", 20, MUTE).next_to(bot, DOWN, .12))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=.07), FadeIn(labs), run_time=2.0)
        def tag(i, s, c, up=True):
            return kr(s, 24, c).next_to(bars[i], UP, .1)
        i0 = 0 if k[0][0] == "2026-10-01" else 0
        i2 = [x[0] for x in k].index("2026-10-02"); i15 = [x[0] for x in k].index("2026-10-15")
        t = VGroup(tag(i2, "7,003", INK), tag(i15, "5,554 서킷", ORG), tag(n - 2, "5,768", GRN), tag(n - 1, "5,552", RED))
        self.play(FadeIn(t, shift=DOWN * .15), run_time=.6)
        ln = DashedLine(ax.c2p(i15, 5554.22), ax.c2p(n - .4, 5554.22), color=ORG, dash_length=.1, stroke_width=3)
        self.play(Create(ln), run_time=.5)
        arc = CurvedArrow(bars[n - 2].get_top() + UP * .55, bars[n - 1].get_top() + UP * .55 + RIGHT * .1, angle=-TAU / 4, color=RED, stroke_width=6)
        self.play(Create(arc), Flash(bars[-1].get_top(), color=RED), run_time=.7)
        box = card(VGroup(kr("10/2 대비", 26, MUTE), kr("−20.7%", 48, RED)).arrange(DOWN, buff=.12), color=RED).to_corner(UR, buff=.5).shift(DOWN * 1.3)
        self.play(FadeIn(box, shift=LEFT * .2)); self.wait(3)


class Flows(Scene):
    """수급: 외국인 −5,348억 · 기관 −9,975억 · 개인 +8,971억 (기사)."""
    def construct(self):
        h = head("누가 팔고, 누가 샀나")
        self.play(FadeIn(h), run_time=.5)
        rows = [("외국인", -5348, BLU), ("기관", -9975, PUR), ("개인", 8971, GRN)]
        mid = Line(UP * 2.0, DOWN * 2.2, color=MUTE, stroke_width=3).shift(RIGHT * .6)
        self.play(Create(mid), run_time=.4)
        g = VGroup()
        sc = 4.6 / 10000
        for i, (nm, v, c) in enumerate(rows):
            y = 1.25 - i * 1.55
            r = Rectangle(width=abs(v) * sc, height=.9, stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to(mid.get_center() + UP * (y - mid.get_center()[1]) * 0 + UP * y, aligned_edge=RIGHT if v < 0 else LEFT).set_x(mid.get_x() + (-1 if v < 0 else 1) * abs(v) * sc / 2)
            lab = kr(nm, 36).next_to(mid, LEFT if v > 0 else RIGHT, .3).set_y(y)
            amt = kr(("−" if v < 0 else "+") + f"{abs(v):,}억", 38, c).next_to(r, LEFT if v < 0 else RIGHT, .25)
            g.add(VGroup(r, lab, amt))
        for row in g:
            self.play(GrowFromEdge(row[0], RIGHT if row[0].get_x() < mid.get_x() else LEFT), FadeIn(row[1]), FadeIn(row[2], shift=UP * .1), run_time=.6)
        tot = card(kr("외국인 + 기관 = 약 1조 5천억 원 순매도", 32, YEL), color=YEL).to_edge(DOWN, buff=.45)
        self.play(FadeIn(tot, shift=UP * .2)); self.play(Indicate(g[1][2], color=PUR)); self.wait(2.5)


class BigTwo(Scene):
    """삼성전자 211,500 (−2.98%) · SK하이닉스 1,223,000 (−4.23%) + 지난 5거래일 미니 차트."""
    def construct(self):
        h = head("반도체 두 형님")
        self.play(FadeIn(h), run_time=.5)
        def one(name, sym, color):
            v = [x[1] for x in Y[sym] if x[0] >= "2026-10-08"]
            last, prev = v[-1], v[-2]
            ax = Axes(x_range=[0, len(v) - 1, 1], y_range=[min(v) * .97, max(v) * 1.02, (max(v) - min(v)) / 4 or 1], x_length=4.2, y_length=2.0,
                      axis_config={"stroke_opacity": 0, "include_ticks": False})
            ln = ax.plot_line_graph(list(range(len(v))), v, line_color=color, add_vertex_dots=False, stroke_width=5)["line_graph"]
            top = VGroup(kr(name, 38), kr(f"{last:,.0f}원", 52, INK), kr(f"{100 * (last / prev - 1):+.2f}%".replace("-", "−"), 44, RED)).arrange(DOWN, buff=.18)
            body = VGroup(top, VGroup(ax, ln)).arrange(DOWN, buff=.35)
            return card(body, color=RED), ln
        a, la = one("삼성전자", "005930.KS", BLU)
        b, lb = one("SK하이닉스", "000660.KS", ORG)
        VGroup(a, b).arrange(RIGHT, buff=.9).shift(DOWN * .35)
        self.play(FadeIn(a[0]), FadeIn(a[1][0], shift=UP * .2), run_time=.6); self.play(Create(la), run_time=.9)
        self.play(FadeIn(b[0]), FadeIn(b[1][0], shift=UP * .2), run_time=.6); self.play(Create(lb), run_time=.9)
        self.wait(3)


class KospiYear(Scene):
    """코스피 1년: 꼭대기 9,114(6/22) → 오늘 5,552 (−39%)."""
    def construct(self):
        v = [x[1] for x in KOSPI]; n = len(v)
        ax = Axes(x_range=[0, n - 1, 50], y_range=[3000, 10000, 1000], x_length=10.6, y_length=5.4,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False}).shift(DOWN * .4)
        h = head("코스피 1년")
        self.play(FadeIn(h), Create(ax), run_time=.6)
        line = ax.plot_line_graph(list(range(n)), v, line_color=ORG, add_vertex_dots=False, stroke_width=6)["line_graph"]
        self.play(Create(line), run_time=2.6, rate_func=linear)
        ip = int(np.argmax(v))
        pk = VGroup(Dot(ax.c2p(ip, v[ip]), .13, color=YEL), kr("꼭대기 9,114 (6/22)", 30, YEL).next_to(ax.c2p(ip, v[ip]), UP, .15))
        nw = VGroup(Dot(ax.c2p(n - 1, v[-1]), .13, color=RED), kr("오늘 5,552", 30, RED).next_to(ax.c2p(n - 1, v[-1]), DOWN, .2))
        self.play(FadeIn(pk, scale=1.2)); self.play(FadeIn(nw, scale=1.2))
        drop = Arrow(ax.c2p(ip + 3, v[ip]), ax.c2p(n - 1, v[-1]) + UP * .2, color=RED, stroke_width=6, buff=.15)
        pct = kr(f"{100 * (v[-1] / v[ip] - 1):.0f}%".replace("-", "−"), 60, RED).next_to(drop.get_center(), RIGHT, .3)
        self.play(GrowArrow(drop), FadeIn(pct, scale=1.3)); self.wait(3)


class KoreaVsUs(Scene):
    """어젯밤 나스닥 +1.11% · 반도체지수 +1.6%  vs  오늘 코스피 −3.73% · 코스닥 −3.33%."""
    def construct(self):
        L = VGroup(kr("어젯밤 미국", 34, MUTE), kr("나스닥", 40), kr("+1.11%", 80, GRN), kr("반도체지수 +1.6%", 32, GRN)).arrange(DOWN, buff=.25)
        Rr = VGroup(kr("오늘 한국", 34, MUTE), kr("코스피", 40), kr("−3.73%", 80, RED), kr("코스닥 −3.33%", 32, RED)).arrange(DOWN, buff=.25)
        a, b = card(L, color=GRN, buff=.45), card(Rr, color=RED, buff=.45)
        VGroup(a, b).arrange(RIGHT, buff=2.0).shift(DOWN * .1)
        up = Arrow(DOWN, UP, color=GRN, stroke_width=10).scale(.7).next_to(a, UP, .15)
        dn = Arrow(UP, DOWN, color=RED, stroke_width=10).scale(.7).next_to(b, UP, .15)
        self.play(FadeIn(a, shift=RIGHT * .4), GrowArrow(up), run_time=.7)
        vs = kr("그런데", 40, YEL).move_to((a.get_right() + b.get_left()) / 2)
        self.play(FadeIn(vs, scale=1.4), run_time=.4)
        self.play(FadeIn(b, shift=LEFT * .4), GrowArrow(dn), run_time=.7)
        self.play(Indicate(b[1][2], color=RED, scale_factor=1.1)); self.wait(3)


class UsNight(Scene):
    """10/19(월) 미국장: 나스닥 +1.11% · S&P 500 +0.41% · 다우 −0.07% · 반도체지수 +1.61% / 아마존 +4.95% 테슬라 +3.74% 마이크론 +2.95% / WTI $103.66 (+2.2%)."""
    def construct(self):
        h = head("10월 19일(월) 미국장")
        self.play(FadeIn(h), run_time=.5)
        def pct(s):
            v = Y[s]; return 100 * (v[-1][1] / v[-2][1] - 1)
        rows = [("나스닥", pct("^IXIC")), ("S&P 500", pct("^GSPC")), ("다우", pct("^DJI")), ("반도체지수", pct("^SOX"))]
        base = Line(UP * 1.6, DOWN * 2.6, color=MUTE, stroke_width=3).shift(LEFT * 3.0)
        self.play(Create(base), run_time=.3)
        g = VGroup()
        for i, (nm, v) in enumerate(rows):
            y = 1.2 - i * 1.05
            c = GRN if v > 0 else RED
            r = Rectangle(width=max(abs(v) * 1.5, .06), height=.7, stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to([base.get_x(), y, 0], aligned_edge=LEFT if v > 0 else RIGHT)
            lab = kr(nm, 32).move_to([base.get_x() - .35, y, 0], aligned_edge=RIGHT)
            if v < 0:
                lab.shift(LEFT * r.width)
            g.add(VGroup(r, lab, kr(f"{v:+.2f}%".replace("-", "−"), 32, c).next_to(base, RIGHT, .2 + (r.width if v > 0 else 0)).set_y(y)))
        for row in g:
            self.play(GrowFromEdge(row[0], LEFT), FadeIn(row[1]), FadeIn(row[2]), run_time=.45)
        st = VGroup(*[kr(t, 30, GRN) for t in ("아마존 +4.95%", "테슬라 +3.74%", "마이크론 +2.95%")]).arrange(DOWN, aligned_edge=LEFT, buff=.2)
        oil = VGroup(kr("WTI 유가", 28, MUTE), kr("$103.66", 46, ORG), kr("+2.2% · 후티, 사우디 공격", 24, ORG)).arrange(DOWN, buff=.12)
        side = VGroup(card(st, color=GRN), card(oil, color=ORG)).arrange(DOWN, buff=.35).to_edge(RIGHT, buff=.5).shift(DOWN * .4)
        self.play(FadeIn(side[0], shift=LEFT * .2)); self.play(FadeIn(side[1], shift=LEFT * .2)); self.wait(3)


class Elice(Scene):
    """엘리스 상장 첫날: 수요예측 388.84 : 1 · 공모가 90,500 → 종가 61,500 (−32.04%) · 장중 58,000."""
    def construct(self):
        h = head("엘리스 · 상장 첫날", sub="AI 데이터센터 회사 · 10월 20일 코스닥")
        self.play(FadeIn(h), run_time=.5)
        tr = ValueTracker(0)
        cnt = always_redraw(lambda: kr(f"{tr.get_value():.0f} : 1", 72, YEL).move_to(LEFT * 3.4 + UP * .5))
        cap = kr("기관 수요예측 경쟁률", 28, MUTE).move_to(LEFT * 3.4 + UP * 1.5)
        self.add(cap, cnt)
        self.play(tr.animate.set_value(388), run_time=1.4, rate_func=rush_from)
        ok = kr("인기 폭발 ✓", 30, GRN).next_to(cnt, DOWN, .3)
        self.play(FadeIn(ok, shift=UP * .1), run_time=.4)
        sc = 3.6 / 90500; bx = RIGHT * .2 + DOWN * 2.4
        a = Rectangle(width=1.3, height=90500 * sc, stroke_width=0, fill_color=DIM, fill_opacity=1).move_to(bx, aligned_edge=DOWN)
        b = Rectangle(width=1.3, height=61500 * sc, stroke_width=0, fill_color=RED, fill_opacity=1).move_to(bx + RIGHT * 2.2, aligned_edge=DOWN)
        la = VGroup(kr("공모가", 26, MUTE).next_to(a, DOWN, .15), kr("90,500", 32).next_to(a, UP, .12))
        lb = VGroup(kr("첫날 종가", 26, MUTE).next_to(b, DOWN, .15), kr("61,500", 32, RED).next_to(b, UP, .12))
        self.play(GrowFromEdge(a, DOWN), FadeIn(la), run_time=.6)
        ghost = a.copy().move_to(b, aligned_edge=DOWN).set_fill(RED, .25)
        self.play(FadeIn(ghost), run_time=.3)
        self.play(Transform(ghost, b), FadeIn(lb), run_time=.9)
        big = kr("−32%", 84, RED).next_to(VGroup(a, b), RIGHT, .6).shift(UP * .3)
        self.play(FadeIn(big, scale=1.5), Flash(big, color=RED), run_time=.6)
        self.play(FadeOut(ok), FadeIn(kr("그런데…", 30, RED).next_to(cnt, DOWN, .3)), run_time=.4)
        foot = kr("장중 한때 58,000원 (−38%)", 26, MUTE).to_edge(DOWN, buff=.35)
        self.play(FadeIn(foot)); self.wait(2.5)


class DcDoubt(Scene):
    """데이터센터 의심의 고리: GPU 구매 → 감가상각비 · 전기료 ↑ → 언제 벌어서 갚나?  + 내 사이트 1주 꼴찌 데이터센터 −17.6%."""
    def construct(self):
        h = head("시장이 의심하는 것")
        self.play(FadeIn(h), run_time=.5)
        steps = [("GPU · 데이터센터에 돈을 쏟는다", BLU), ("감가상각비 + 전기료 ↑", ORG), ("언제 벌어서 갚나?", RED)]
        boxes = VGroup(*[card(kr(t, 36, c), color=c) for t, c in steps]).arrange(DOWN, buff=.55).scale(.78).to_edge(LEFT, buff=.4).shift(DOWN * .3)
        arrows = VGroup(*[Arrow(boxes[i].get_bottom(), boxes[i + 1].get_top(), buff=.05, color=MUTE, stroke_width=5) for i in range(2)])
        for i, b in enumerate(boxes):
            self.play(FadeIn(b, shift=RIGHT * .2), *([GrowArrow(arrows[i - 1])] if i else []), run_time=.55)
        self.play(Indicate(boxes[2], color=RED, scale_factor=1.06))
        rows = sorted([(100 * x["path"]["w1"][-1], x["name"]) for x in T["themes"]])[:4]
        g = VGroup()
        for i, (v, nm) in enumerate(rows):
            r = Rectangle(width=abs(v) * .17, height=.5, stroke_width=0, fill_color=RED if i == 0 else DIM, fill_opacity=1)
            g.add(VGroup(kr(nm.replace(",", "·"), 26, INK if i == 0 else MUTE), r, kr(f"{v:.1f}%".replace("-", "−"), 28, RED if i == 0 else MUTE)).arrange(RIGHT, buff=.2))
        for row in g:
            row[0].set_width(min(row[0].width, 2.1))
        g.arrange(DOWN, aligned_edge=LEFT, buff=.3)
        panel = card(VGroup(kr("내 테마 사이트 · 1주 꼴찌 4개", 26, YEL), g).arrange(DOWN, buff=.3, aligned_edge=LEFT), color=YEL).scale(.9).to_edge(RIGHT, buff=.4).shift(DOWN * .3)
        self.play(FadeIn(panel[0]), FadeIn(panel[1][0]), run_time=.4)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(r[0]), GrowFromEdge(r[1], LEFT), FadeIn(r[2])) for r in g], lag_ratio=.25), run_time=1.4)
        self.wait(2.5)


class Concentration(Scene):
    """MSCI 코리아에서 삼성전자 + SK하이닉스 비중 62.9% (9월 말, 증권사 분석) — 100칸 와플."""
    def construct(self):
        h = head("한국 지수 = 반도체 두 종목", sub="MSCI 코리아 비중 · 9월 말")
        self.play(FadeIn(h), run_time=.5)
        cells = VGroup(*[Square(.42, stroke_width=0, fill_color=DIM, fill_opacity=1) for _ in range(100)]).arrange_in_grid(10, 10, buff=.07).shift(LEFT * 2.6 + DOWN * .45)
        self.play(LaggedStart(*[FadeIn(c, scale=.4) for c in cells], lag_ratio=.006), run_time=1.0)
        order = sorted(range(100), key=lambda i: (9 - i // 10, i % 10))
        k = [cells[i] for i in sorted(range(100), key=lambda i: (-(i // 10), i % 10))][:63]
        self.play(LaggedStart(*[c.animate.set_fill(RED if j < 40 else ORG) for j, c in enumerate(k)], lag_ratio=.015), run_time=1.6)
        t = ValueTracker(0)
        num = always_redraw(lambda: kr(f"{t.get_value():.1f}%", 110, RED).move_to(RIGHT * 3.4 + UP * .4))
        self.add(num); self.play(t.animate.set_value(62.9), run_time=1.0)
        lg = VGroup(VGroup(Square(.3, fill_color=RED, fill_opacity=1, stroke_width=0), kr("삼성전자", 30)).arrange(RIGHT, buff=.2),
                    VGroup(Square(.3, fill_color=ORG, fill_opacity=1, stroke_width=0), kr("SK하이닉스", 30)).arrange(RIGHT, buff=.2),
                    VGroup(Square(.3, fill_color=DIM, fill_opacity=1, stroke_width=0), kr("나머지 전부", 30, MUTE)).arrange(RIGHT, buff=.2)).arrange(DOWN, aligned_edge=LEFT, buff=.2).next_to(num, DOWN, .5)
        self.play(FadeIn(lg, shift=UP * .2))
        nt = kr("※ 두 종목 합산 · 칸 나눔은 그림", 20, MUTE).to_edge(DOWN, buff=.25)
        self.play(FadeIn(nt)); self.wait(3)


class Rates(Scene):
    """금리: 프랑스 10년물 4.9%(시위 2,300명+ 체포 · 부채 GDP 119%) · 미국 10년물 5.14% · 원/달러 1,328원."""
    def construct(self):
        h = head("세 번째 이유 · 금리")
        self.play(FadeIn(h), run_time=.5)
        def gauge(title, val, lo, hi, color, note):
            arc_bg = Arc(radius=1.5, start_angle=PI, angle=-PI, stroke_width=22, color=DIM)
            frac = (val - lo) / (hi - lo)
            arc = Arc(radius=1.5, start_angle=PI, angle=-PI * frac, stroke_width=22, color=color)
            txt = kr(title, 30, MUTE).next_to(arc_bg, UP, .25)
            v = kr(f"{val:.2f}%" if val < 100 else f"{val:,.0f}원", 40, color).move_to(arc_bg.get_center() + DOWN * .25)
            nt = kr(note, 22, MUTE).next_to(arc_bg, DOWN, .55)
            return VGroup(arc_bg, txt, v, nt), arc
        a, aa = gauge("프랑스 10년물", 4.93, 3.0, 5.2, RED, "시위 2,300명+ 체포 · 부채 GDP 119%")
        b, ab = gauge("미국 10년물", Y["^TNX"][-1][1], 3.5, 5.5, ORG, "미래 이익에 기대는 AI주 부담")
        c, ac = gauge("원/달러", 1328.1, 1250, 1450, BLU, "원화 강세 → 수출주 이익 걱정")
        VGroup(VGroup(a, aa), VGroup(b, ab), VGroup(c, ac)).arrange(RIGHT, buff=.6).shift(DOWN * .3)
        for g, arc in ((a, aa), (b, ab), (c, ac)):
            self.play(FadeIn(g[0]), FadeIn(g[1]), run_time=.25)
            self.play(Create(arc), FadeIn(g[2], scale=1.2), FadeIn(g[3]), run_time=.8)
        self.wait(3)


class Defense(Scene):
    """방산: 한화에어로스페이스 −11.7% · 현대로템 −13.7% · 한화시스템 −13.9% · KODEX 방산TOP10레버리지 −19.1%."""
    def construct(self):
        h = head("오늘 제일 아팠던 업종 · 방산")
        self.play(FadeIn(h), run_time=.5)
        rows = [("한화에어로스페이스", -11.7, RED), ("현대로템", -13.7, RED), ("한화시스템", -13.9, RED), ("방산 레버리지 ETF", -19.1, PUR)]
        base = Line(UP * 1.7, DOWN * 2.6, color=MUTE, stroke_width=3).shift(LEFT * 1.3)
        self.play(Create(base), run_time=.3)
        g = VGroup()
        for i, (nm, v, c) in enumerate(rows):
            y = 1.25 - i * 1.1
            r = Rectangle(width=abs(v) * .3, height=.72, stroke_width=0, fill_color=c, fill_opacity=1).move_to([base.get_x(), y, 0], aligned_edge=LEFT)
            g.add(VGroup(r, kr(nm, 30).move_to([base.get_x() - .3, y, 0], aligned_edge=RIGHT), kr(f"{v:.1f}%".replace("-", "−"), 38, c).next_to(r, RIGHT, .2)))
        for row in g:
            self.play(GrowFromEdge(row[0], LEFT), FadeIn(row[1]), FadeIn(row[2], shift=RIGHT * .1), run_time=.5)
        self.play(Flash(g[3][2], color=PUR), Indicate(g[3][2], color=PUR, scale_factor=1.1), run_time=.7)
        nt = card(kr("어제 강했던 방산·조선·원전 → 차익실현 + 현대로템 실적 실망", 28, YEL), color=YEL).to_edge(DOWN, buff=.35)
        self.play(FadeIn(nt, shift=UP * .2)); self.wait(3)


class ThisWeek(Scene):
    """이번 주 실적 (한국 시간): 10/21(수) 아침 넷플릭스 · 10/22(목) 새벽 메타 · 테슬라 · 기준선: 오늘 장중 저점 5,493."""
    def construct(self):
        h = head("이번 주 꼭 볼 날짜", sub="한국 시간 기준")
        self.play(FadeIn(h), run_time=.5)
        tl = Line(LEFT * 5.2, RIGHT * 5.2, color=MUTE, stroke_width=4).shift(UP * .3)
        self.play(Create(tl), run_time=.5)
        items = [(-4.3, "10/20 (화)", "오늘 코스피 −3.7%", RED), (0, "10/21 (수) 아침", "넷플릭스 실적", INK), (4.3, "10/22 (목) 새벽", "메타 · 테슬라 실적", YEL)]
        g = VGroup()
        for x, d, t, c in items:
            dot = Dot([x, .3, 0], .16, color=c)
            g.add(VGroup(dot, kr(d, 28, MUTE).next_to(dot, UP, .3), card(kr(t, 32, c), color=c if c != INK else "#2a2e37").next_to(dot, DOWN, .35)))
        self.play(LaggedStart(*[FadeIn(x, shift=UP * .2) for x in g], lag_ratio=.4), run_time=1.6)
        self.play(Indicate(g[2][2], color=YEL, scale_factor=1.06))
        q = kr("메타: AI에 얼마나 더 쓰고, 그만큼 버나?", 32, YEL).to_edge(DOWN, buff=1.2)
        ln = kr("내 기준선 · 오늘 장중 저점 5,493", 28, MUTE).next_to(q, DOWN, .25)
        self.play(FadeIn(q, shift=UP * .2)); self.play(FadeIn(ln)); self.wait(3)


class Summary(Scene):
    def construct(self):
        h = head("세 줄 요약", YEL)
        ls = [("1", "미국은 올랐는데 코스피 −3.7% · 5,552", RED), ("2", "AI 데이터센터 의심 · 반도체 쏠림 · 금리", BLU), ("3", "22일 새벽 메타 · 테슬라 실적이 관건", YEL)]
        g = VGroup()
        for n, t, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), kr(t, 38)).arrange(RIGHT, buff=.4))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.6).shift(DOWN * .1)
        self.play(FadeIn(h))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * .3) for r in g], lag_ratio=.5), run_time=2)
        foot = kr("금리·주가 50년 /invest   ·   미국 테마 강도 /themes", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(3)
