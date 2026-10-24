# 교류 전력 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(long.json 에서 그 문장 시작에 붙임).
# 끝까지 보게 만드는 4원칙: 1.5~2.5초마다 화면에 새 요소(내용으로 변화, 전환·반복 확대 없음), 4초 넘게 멈춘 화면 없음.
#   → 장면마다 beat() 로 요소를 차례로 띄우고, 끝에는 파형 위를 도는 점처럼 계속 움직이는 요소를 둔다.
# 예제(검산): 220V·60Hz·25A·역률 0.8 → S 5.5kVA, P 4.4kW, Q 3.3kVAR, C = 3300/(377·220²) ≈ 181μF → I 20A, 손실 36%↓
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
from manim import *
import numpy as np

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
TexTemplateLibrary.default.add_to_preamble(r"\usepackage{amsmath}")
TH = 40 * DEGREES        # 파형 장면의 위상차 (보기 좋게 크게). 예제는 36.87°(역률 0.8)


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def tex(s, size=56, color=INK):
    return MathTex(s, font_size=size, color=color)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK):
    return kr(s, 44, c).to_edge(UP, buff=.4)


def step_tag(n, c=YEL):
    """오른쪽 위 STEP 진행 표시: ●●●○○."""
    dots = VGroup(*[Circle(.11, color=c if k < n else MUTE, fill_color=c if k < n else BG, fill_opacity=1, stroke_width=3)
                    for k in range(5)]).arrange(RIGHT, buff=.14)
    return VGroup(kr(f"STEP {n}/5", 28, c), dots).arrange(RIGHT, buff=.25).to_corner(UR, buff=.35)


def beat(sc, *anims, t=1.8, rt=.6):
    """요소 하나 띄우고 t 초를 채운다 (새 요소 간격)."""
    if anims:
        sc.play(*anims, run_time=rt)
    sc.wait(max(.05, t - (rt if anims else 0)))


def roam(sc, ax, f, c=YEL, t=3.0, x0=0, x1=2):
    """파형 위를 도는 점 (마지막에 화면이 멈추지 않게)."""
    k = ValueTracker(x0)
    d = always_redraw(lambda: Dot(ax.c2p(k.get_value(), f(k.get_value())), .1, color=c))
    sc.add(d); sc.play(k.animate.set_value(x1), run_time=t, rate_func=linear)
    return d


def pulse(sc, m, t=3.0, c=YEL):
    """마지막 몇 초: 테두리를 한 바퀴 돌며 강조 (확대 없이)."""
    sc.play(ShowPassingFlash(SurroundingRectangle(m, color=c, buff=.18, corner_radius=.15), time_width=.5), run_time=t * .5)
    sc.play(ShowPassingFlash(SurroundingRectangle(m, color=c, buff=.18, corner_radius=.15), time_width=.5), run_time=t * .5)


# ---------- 파형 ----------
def wax(ymax=1.3, xl=10.5, yl=3.6, ylab=None):
    ax = Axes(x_range=[0, 2.05, .5], y_range=[-ymax, ymax, 1], x_length=xl, y_length=yl, tips=False,
              axis_config={"color": MUTE, "stroke_width": 3}, x_axis_config={"include_ticks": False}, y_axis_config={"include_ticks": False})
    g = VGroup(ax)
    if ylab:
        g.add(tex(ylab, 34, MUTE).next_to(ax.y_axis, UP, .1))
    return g


def v_(x): return np.sin(2 * PI * x)
def i_(x, th=0): return .7 * np.sin(2 * PI * x - th)
def p_(x, th=0): return v_(x) * i_(x, th)


def shade_neg(ax, f, color=RED):
    """f<0 인 구간을 빨갛게 칠한다."""
    xs = np.linspace(0, 2, 801); g = VGroup(); seg = []
    for x in xs:
        if f(x) < 0:
            seg.append(x)
        elif seg:
            g.add(ax.get_area(ax.plot(f, x_range=[seg[0], seg[-1]]), x_range=[seg[0], seg[-1]], color=color, opacity=.55)); seg = []
    if seg:
        g.add(ax.get_area(ax.plot(f, x_range=[seg[0], seg[-1]]), x_range=[seg[0], seg[-1]], color=color, opacity=.55))
    return g


# ---------- 회로 부품 ----------
def P3(p): return np.array([p[0], p[1], 0.0])
def wire(a, b, c=INK, w=4): return Line(P3(a), P3(b), color=c, stroke_width=w)


def cap(a, b, c=INK):
    a, b = P3(a), P3(b); d = b - a; u = d / np.linalg.norm(d); n = np.array([-u[1], u[0], 0]); m = (a + b) / 2
    return VGroup(Line(a, m - u * .13, color=c, stroke_width=4), Line(m + u * .13, b, color=c, stroke_width=4),
                  Line(m - u * .13 - n * .4, m - u * .13 + n * .4, color=c, stroke_width=6),
                  Line(m + u * .13 - n * .4, m + u * .13 + n * .4, color=c, stroke_width=6))


def acsrc(bot, top, c=INK):
    bot, top = P3(bot), P3(top); m = (bot + top) / 2
    wv = FunctionGraph(lambda x: .18 * np.sin(2 * PI * x / .5), x_range=[-.25, .25], color=c, stroke_width=4).move_to(m)
    return VGroup(wire(bot, m + DOWN * .45, c), wire(m + UP * .45, top, c), Circle(.45, color=c, stroke_width=4).move_to(m), wv)


def motor(p, c=INK):
    return VGroup(Circle(.55, color=c, stroke_width=4), kr("M", 44, c)).move_to(P3(p))


def load_ckt(with_c=False, I="25\\,\\mathrm{A}"):
    """220V 교류 전원 — 전류계 — 모터 (+ 병렬 콘덴서)."""
    G = {}
    G["src"] = acsrc((-4.2, -1.4), (-4.2, 1.4)); G["lV"] = tex(r"220\,\mathrm{V}\ 60\,\mathrm{Hz}", 36, YEL).next_to(P3((-4.7, 0)), LEFT, .1)
    G["top"] = wire((-4.2, 1.4), (2.0, 1.4)); G["bot"] = wire((-4.2, -1.4), (2.0, -1.4))
    G["mw1"] = wire((.4, 1.4), (.4, .55)); G["mw2"] = wire((.4, -.55), (.4, -1.4)); G["M"] = motor((.4, 0))
    G["lM"] = kr("모터", 30, MUTE).next_to(P3((.4, 0)), LEFT, .7)
    G["arr"] = Arrow(P3((-3.6, 1.85)), P3((-1.8, 1.85)), buff=0, color=GRN, stroke_width=6)
    G["lI"] = tex(I, 52, GRN).next_to(G["arr"], UP, .1)
    if with_c:
        G["cw1"] = wire((2.0, 1.4), (2.6, 1.4)); G["cw2"] = wire((2.0, -1.4), (2.6, -1.4))
        G["C"] = cap((2.6, 1.4), (2.6, -1.4), BLU); G["lC"] = kr("콘덴서", 30, BLU).next_to(P3((2.6, 0)), RIGHT, .5)
    return G


# ---------- 전력 삼각형 ----------
def tri(P=4.4, Q=3.3, sc=.95, org=LEFT * 2.6 + DOWN * 1.7, labels=True, nums=True):
    o = P3(org); a = o + RIGHT * P * sc; b = a + UP * Q * sc
    g = VGroup(Line(o, a, color=GRN, stroke_width=8), Line(a, b, color=RED, stroke_width=8), Line(o, b, color=BLU, stroke_width=8))
    if labels:
        g.add(tex(r"P" + (rf"={P:g}\,\mathrm{{kW}}" if nums else ""), 42, GRN).next_to(g[0], DOWN, .2))
        if Q > .05:
            g.add(tex(r"Q" + (rf"={Q:g}\,\mathrm{{kVAR}}" if nums else ""), 42, RED).next_to(g[1], RIGHT, .2))
        S = (P * P + Q * Q) ** .5
        g.add(tex(r"S" + (rf"={S:.2g}\,\mathrm{{kVA}}" if nums else ""), 42, BLU).move_to((o + b) / 2 + np.array([-.55, .5, 0]) * (1 if Q > .05 else 0) + (UP * .45 if Q <= .05 else 0)))
    return g


def bars(vals, labs, cols, unit="", maxv=None, h=3.2, w=1.1):
    maxv = maxv or max(vals); g = VGroup()
    for v, l, c in zip(vals, labs, cols):
        r = Rectangle(width=w, height=h * v / maxv, color=c, fill_color=c, fill_opacity=.85, stroke_width=0)
        g.add(VGroup(r, tex(f"{v:g}" + unit, 44, c).next_to(r, UP, .15), kr(l, 30, MUTE).next_to(r, DOWN, .2)))
    g.arrange(RIGHT, buff=1.0, aligned_edge=DOWN)
    return g


# ================= 인트로 =================
class Hook(Scene):
    """콘덴서 하나로 25A → 20A (같은 4.4kW)."""
    def construct(self):
        G = load_ckt(with_c=True); base = VGroup(*[G[k] for k in ("src", "lV", "top", "bot", "mw1", "mw2", "M", "lM")])
        allg = VGroup(*G.values()).scale(.8).shift(DOWN * .3)
        self.add(base)
        beat(self, GrowArrow(G["arr"]), FadeIn(G["lI"]), t=1.6, rt=.5)
        kw = kr("일은 4.4kW 그대로", 34, MUTE).to_edge(UP, buff=.5); beat(self, FadeIn(kw), t=1.0, rt=.4)
        beat(self, Create(VGroup(G["cw1"], G["cw2"], G["C"])), FadeIn(G["lC"]), t=1.6, rt=.7)
        n = DecimalNumber(25, num_decimal_places=0, font_size=52, color=YEL).move_to(G["lI"]).shift(LEFT * .25)
        u = tex(r"\mathrm{A}", 52, YEL).next_to(n, RIGHT, .08)
        self.remove(G["lI"]); self.add(n, u)
        self.play(ChangeDecimalToValue(n, 20), G["arr"].animate.set_color(YEL), run_time=1.4)
        lab = kr("25A → 20A", 46, YEL).to_edge(DOWN, buff=.4); beat(self, FadeIn(lab, shift=UP * .2), t=1.4, rt=.4)


class Goal(Scene):
    """오늘의 목표: 역률 cosθ 를 이해하고 25A→20A 직접 계산 + STEP 5칸."""
    def construct(self):
        f = VGroup(kr("역률", 80, YEL), tex(r"=\cos\theta", 88, YEL)).arrange(RIGHT, buff=.3)
        f.shift(UP * 1.2)
        beat(self, FadeIn(f), t=1.5, rt=.5)
        g = kr("목표: 25A → 20A 직접 계산하기", 40, INK).next_to(f, DOWN, .6); beat(self, FadeIn(g, shift=UP * .2), t=1.4, rt=.4)
        dots = VGroup(*[VGroup(Circle(.32, color=YEL, stroke_width=4), kr(str(k + 1), 32, YEL)) for k in range(5)]).arrange(RIGHT, buff=.6)
        dots.next_to(g, DOWN, .8)
        self.play(LaggedStart(*[FadeIn(d, scale=.8) for d in dots], lag_ratio=.25), run_time=1.4)
        self.play(dots[0][0].animate.set_fill(YEL, .35), run_time=.8)
        self.wait(.8)


class Roadmap(Scene):
    """다섯 단계를 말하는 순서대로."""
    def construct(self):
        items = [("1", "순시전력", BLU), ("2", "실횻값", GRN), ("3", "유효·무효·피상", ORG), ("4", "전력 삼각형", RED), ("5", "역률 개선", YEL)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for i, k in enumerate(cards):
            beat(self, FadeIn(k, shift=UP * .3), t=1.0 if i < 4 else 1.2, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.6, rt=1.0)


# ================= STEP 1 순시전력 =================
class P1(Scene):
    """p(t) = v(t)·i(t)."""
    def construct(self):
        self.add(step_tag(1))
        f = tex(r"p(t) = v(t)\times i(t)", 84, INK).shift(UP * 1.6)
        beat(self, Write(f), t=1.6, rt=.9)
        g = wax(yl=3.0).shift(DOWN * 1.3); ax = g[0]
        v = ax.plot(v_, x_range=[0, 2], color=BLU, stroke_width=5); i = ax.plot(lambda x: i_(x), x_range=[0, 2], color=GRN, stroke_width=5)
        beat(self, Create(g), Create(v), t=1.4, rt=.9)
        beat(self, Create(i), t=1.2, rt=.8)
        roam(self, ax, v_, BLU, t=2.0, x0=0, x1=1)


class P2(Scene):
    """저항: v, i 같이 → p ≥ 0."""
    def construct(self):
        self.add(step_tag(1), head("저항만 있을 때", GRN))
        g = wax(ymax=1.3, yl=4.2).shift(DOWN * .4); ax = g[0]; self.add(g)
        v = ax.plot(v_, x_range=[0, 2], color=BLU, stroke_width=4); i = ax.plot(lambda x: i_(x), x_range=[0, 2], color=GRN, stroke_width=4)
        lv = tex("v", 40, BLU).next_to(ax.c2p(.25, 1), UP, .05); li = tex("i", 40, GRN).next_to(ax.c2p(.3, .6), RIGHT, .3)
        beat(self, Create(v), Create(i), FadeIn(lv), FadeIn(li), t=1.6, rt=1.0)
        p = ax.plot(lambda x: 1.15 * p_(x), x_range=[0, 2], color=YEL, stroke_width=7)
        area = ax.get_area(p, x_range=[0, 2], color=YEL, opacity=.25)
        beat(self, Create(p), FadeIn(area), t=1.8, rt=1.2)
        lab = kr("p ≥ 0 항상 양수", 40, YEL).to_edge(DOWN, buff=.35); beat(self, FadeIn(lab), t=1.0, rt=.4)
        roam(self, ax, lambda x: 1.15 * p_(x), YEL, t=2.0, x0=0, x1=1)


class P3f(Scene):
    """전력은 두 배 주파수: 60Hz → 120Hz."""
    def construct(self):
        self.add(step_tag(1))
        g = wax(ymax=1.3, yl=4.2).shift(DOWN * .3); ax = g[0]; self.add(g)
        v = ax.plot(v_, x_range=[0, 2], color=BLU, stroke_width=4)
        p = ax.plot(lambda x: 1.15 * p_(x), x_range=[0, 2], color=YEL, stroke_width=6)
        self.add(v, p)
        vt = tex(r"v:\ 60\,\mathrm{Hz}", 46, BLU).to_corner(UL, buff=.45)
        beat(self, FadeIn(vt), t=1.2, rt=.4)
        peaks = VGroup(*[Dot(ax.c2p(x, 1.15 * p_(x)), .12, color=YEL) for x in (.25, .75, 1.25, 1.75)])
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in peaks], lag_ratio=.4), run_time=1.6)
        cyc = VGroup(*[Dot(ax.c2p(x, 1), .12, color=BLU) for x in (.25, 1.25)])
        beat(self, FadeIn(cyc), t=1.0, rt=.4)
        pt = tex(r"p:\ 120\,\mathrm{Hz}", 52, YEL).next_to(vt, DOWN, .25, aligned_edge=LEFT)
        beat(self, Write(pt), t=1.4, rt=.6)
        roam(self, ax, lambda x: 1.15 * p_(x), YEL, t=2.0, x0=0, x1=.5)


class P4(Scene):
    """코일: 전류가 늦다, 위상차 θ."""
    def construct(self):
        self.add(step_tag(1), head("코일이 끼면", PUR))
        g = wax(ymax=1.3, yl=4.2).shift(DOWN * .4); ax = g[0]; self.add(g)
        v = ax.plot(v_, x_range=[0, 2], color=BLU, stroke_width=5); self.add(v)
        i0 = ax.plot(lambda x: i_(x), x_range=[0, 2], color=GRN, stroke_width=5)
        k = ValueTracker(0)
        i = always_redraw(lambda: ax.plot(lambda x: i_(x, k.get_value()), x_range=[0, 2], color=GRN, stroke_width=5))
        beat(self, Create(i0), t=1.2, rt=.7)
        self.remove(i0); self.add(i)
        self.play(k.animate.set_value(TH), run_time=1.6)
        x1 = TH / (2 * PI)
        br = VGroup(DashedLine(ax.c2p(0, 0), ax.c2p(0, 1.15), color=MUTE), DashedLine(ax.c2p(x1, 0), ax.c2p(x1, 1.15), color=MUTE))
        th = tex(r"\theta", 64, YEL).move_to(ax.c2p(x1 / 2, 1.35))
        beat(self, FadeIn(br), Write(th), t=1.4, rt=.5)
        lab = kr("전류가 θ 만큼 늦다", 40, GRN).to_edge(DOWN, buff=.35); beat(self, FadeIn(lab), t=1.0, rt=.4)
        roam(self, ax, lambda x: i_(x, TH), GRN, t=1.8, x0=0, x1=1)


class P5(Scene):
    """부호가 다른 구간 → p < 0 (빨강)."""
    def construct(self):
        self.add(step_tag(1))
        g = wax(ymax=1.3, yl=4.6).shift(DOWN * .2); ax = g[0]; self.add(g)
        v = ax.plot(v_, x_range=[0, 2], color=BLU, stroke_width=3, stroke_opacity=.6)
        i = ax.plot(lambda x: i_(x, TH * 1.6), x_range=[0, 2], color=GRN, stroke_width=3, stroke_opacity=.6)
        self.add(v, i)
        f = lambda x: 1.15 * p_(x, TH * 1.6)
        p = ax.plot(f, x_range=[0, 2], color=YEL, stroke_width=6)
        beat(self, Create(p), t=1.6, rt=1.2)
        neg = shade_neg(ax, f)
        beat(self, FadeIn(neg), t=1.4, rt=.6)
        lab = kr("p < 0", 46, RED).to_corner(UL, buff=.5); beat(self, Write(lab), t=1.2, rt=.4)
        roam(self, ax, f, RED, t=2.0, x0=0, x1=.6)


class P6(Scene):
    """에너지가 전원으로 되돌아간다."""
    def construct(self):
        self.add(step_tag(1))
        src = VGroup(Circle(.8, color=BLU, stroke_width=5), kr("전원", 34, BLU)).shift(LEFT * 3.5)
        ld = VGroup(RoundedRectangle(width=2, height=1.6, corner_radius=.2, color=PUR, stroke_width=5), kr("코일", 34, PUR)).shift(RIGHT * 3.5)
        self.add(src, ld)
        go = Arrow(LEFT * 2.5 + UP * .5, RIGHT * 2.3 + UP * .5, buff=0, color=YEL, stroke_width=7)
        bk = Arrow(RIGHT * 2.3 + DOWN * .5, LEFT * 2.5 + DOWN * .5, buff=0, color=RED, stroke_width=7)
        l1 = kr("p > 0  받음", 32, YEL).next_to(go, UP, .15); l2 = kr("p < 0  돌려줌", 32, RED).next_to(bk, DOWN, .15)
        beat(self, GrowArrow(go), FadeIn(l1), t=1.6, rt=.6)
        beat(self, GrowArrow(bk), FadeIn(l2), t=1.6, rt=.6)
        e = Dot(color=YEL, radius=.16)
        for _ in range(2):
            self.play(MoveAlongPath(e, Line(go.get_start(), go.get_end())), run_time=.8)
            self.play(MoveAlongPath(e.set_color(RED), Line(bk.get_start(), bk.get_end())), run_time=.8); e.set_color(YEL)


# ================= STEP 2 실횻값 =================
class R1(Scene):
    """콘센트 220V — 최댓값이 아니다."""
    def construct(self):
        self.add(step_tag(2, GRN))
        plug = VGroup(RoundedRectangle(width=3, height=3, corner_radius=.5, color=INK, stroke_width=5),
                      Circle(.28, color=INK, stroke_width=5).shift(LEFT * .65), Circle(.28, color=INK, stroke_width=5).shift(RIGHT * .65)).shift(LEFT * 3)
        beat(self, Create(plug), t=1.4, rt=.8)
        v = tex(r"220\,\mathrm{V}", 110, YEL).shift(RIGHT * 2.3 + UP * .4); beat(self, Write(v), t=1.4, rt=.6)
        q = VGroup(kr("최댓값?", 50, INK), kr("✕", 60, RED)).arrange(RIGHT, buff=.3).next_to(v, DOWN, .5)
        beat(self, FadeIn(q[0]), t=1.0, rt=.4); beat(self, FadeIn(q[1], scale=1.5), t=1.5, rt=.3)


class R2(Scene):
    """사인파 꼭대기 311V."""
    def construct(self):
        self.add(step_tag(2, GRN))
        g = wax(ymax=1.25, yl=4.8, ylab=r"v\,(\mathrm{V})").shift(DOWN * .2); ax = g[0]; self.add(g)
        v = ax.plot(v_, x_range=[0, 2], color=BLU, stroke_width=6)
        beat(self, Create(v), t=1.6, rt=1.4)
        top = VGroup(DashedLine(ax.c2p(0, 1), ax.c2p(2, 1), color=YEL), tex(r"+311\,\mathrm{V}", 46, YEL).next_to(ax.c2p(.25, 1), UP, .1))
        bot = VGroup(DashedLine(ax.c2p(0, -1), ax.c2p(2, -1), color=YEL), tex(r"-311\,\mathrm{V}", 46, YEL).next_to(ax.c2p(.75, -1), DOWN, .1))
        beat(self, FadeIn(top), t=1.3, rt=.5); beat(self, FadeIn(bot), t=1.0, rt=.5)
        roam(self, ax, v_, YEL, t=2.2, x0=0, x1=1)


class R3(Scene):
    """같은 저항, 같은 열: 교류 220V(실효) = 직류 220V."""
    def construct(self):
        self.add(step_tag(2, GRN))
        def heater(lab, c, sh):
            r = VGroup(*[Line(UP * .9 + RIGHT * x, DOWN * .9 + RIGHT * x, color=ORG, stroke_width=6) for x in np.linspace(-.6, .6, 5)])
            return VGroup(RoundedRectangle(width=2.4, height=2.4, corner_radius=.2, color=c, stroke_width=5), r, kr(lab, 34, c).shift(UP * 1.6)).shift(sh)
        a = heater("교류 실효 220V", BLU, LEFT * 3.2); b = heater("직류 220V", GRN, RIGHT * 3.2)
        beat(self, FadeIn(a), t=1.2, rt=.4); beat(self, FadeIn(b), t=1.2, rt=.4)
        eq = tex("=", 120, YEL); beat(self, Write(eq), t=1.0, rt=.4)
        lab = kr("같은 열", 46, YEL).to_edge(DOWN, buff=.6); beat(self, FadeIn(lab), t=.8, rt=.3)
        waves = VGroup(*[FunctionGraph(lambda x: .12 * np.sin(6 * x), x_range=[-.5, .5], color=ORG, stroke_width=4).shift(s + UP * (1.5 + .0))
                         for s in (LEFT * 3.2, RIGHT * 3.2)])
        self.play(*[w.animate.shift(UP * .5).set_opacity(0) for w in waves], run_time=1.6)


class R4(Scene):
    """제곱 → 평균 → 루트 (RMS)."""
    def construct(self):
        self.add(step_tag(2, GRN))
        g = wax(ymax=1.25, yl=3.4).shift(UP * .4); ax = g[0]; self.add(g)
        v = ax.plot(v_, x_range=[0, 2], color=BLU, stroke_width=4); self.add(v)
        v2 = ax.plot(lambda x: v_(x) ** 2, x_range=[0, 2], color=ORG, stroke_width=6)
        steps = VGroup(kr("① 제곱", 40, ORG), kr("② 평균", 40, YEL), kr("③ 루트", 40, GRN)).arrange(RIGHT, buff=1.2).to_edge(DOWN, buff=.5)
        beat(self, Create(v2), FadeIn(steps[0]), t=1.6, rt=.9)
        mean = DashedLine(ax.c2p(0, .5), ax.c2p(2, .5), color=YEL, stroke_width=5)
        beat(self, Create(mean), FadeIn(steps[1]), t=1.6, rt=.7)
        f = tex(r"V_{rms}=\sqrt{\overline{v^2}}", 52, GRN).to_corner(UR, buff=.4).shift(DOWN * .6)
        beat(self, FadeIn(steps[2]), Write(f), t=1.6, rt=.7)


class R5(Scene):
    """평균 = Vm²/2 → Vrms = Vm/√2."""
    def construct(self):
        self.add(step_tag(2, GRN))
        f1 = tex(r"\overline{v^2} = \frac{V_m^2}{2}", 76, ORG).shift(UP * 1.3)
        beat(self, Write(f1), t=1.8, rt=.8)
        b = kr("최댓값 제곱의 절반", 34, MUTE).next_to(f1, DOWN, .3); beat(self, FadeIn(b), t=1.2, rt=.4)
        f2 = tex(r"V_{rms} = \frac{V_m}{\sqrt{2}}", 96, YEL).shift(DOWN * 1.3)
        beat(self, Write(f2), t=1.6, rt=.8)
        pulse(self, f2, t=1.8)


class R6(Scene):
    """311 ÷ 1.414 = 220V, 앞으로 V·I 는 실횻값."""
    def construct(self):
        self.add(step_tag(2, GRN))
        f = VGroup(tex(r"\frac{311\,\mathrm{V}}{\sqrt{2}}", 84), tex(r"=", 84), tex(r"220\,\mathrm{V}", 96, YEL)).arrange(RIGHT, buff=.4).shift(UP * .9)
        beat(self, Write(f[0]), t=1.4, rt=.7)
        beat(self, FadeIn(f[1]), FadeIn(f[2], shift=LEFT * .3), t=1.4, rt=.5)
        n = card(VGroup(tex(r"V,\ I", 60, GRN), kr("= 실횻값", 44, GRN)).arrange(RIGHT, buff=.3), GRN, .35).shift(DOWN * 1.5)
        beat(self, FadeIn(n, shift=UP * .2), t=1.4, rt=.5)
        pulse(self, n, t=1.6, c=GRN)


# ================= STEP 3 유효전력 =================
class A1(Scene):
    """p(t) 의 한 주기 평균 = P (수평선)."""
    def construct(self):
        self.add(step_tag(3, ORG))
        g = wax(ymax=1.3, yl=4.4).shift(DOWN * .3); ax = g[0]; self.add(g)
        f = lambda x: 1.3 * p_(x, TH)
        p = ax.plot(f, x_range=[0, 2], color=YEL, stroke_width=6)
        beat(self, Create(p), t=1.6, rt=1.2)
        avg = 1.3 * .7 * .5 * np.cos(TH)
        m = DashedLine(ax.c2p(0, avg), ax.c2p(2, avg), color=GRN, stroke_width=6)
        lab = VGroup(kr("평균", 36, GRN), tex("= P", 50, GRN)).arrange(RIGHT, buff=.15).next_to(ax.c2p(2, avg), UP, .2).shift(LEFT * .8)
        beat(self, Create(m), t=1.2, rt=.8); beat(self, FadeIn(lab), t=1.0, rt=.4)
        roam(self, ax, f, YEL, t=2.0, x0=0, x1=1)


class A2(Scene):
    """P = V I cosθ."""
    def construct(self):
        self.add(step_tag(3, ORG), head("유효전력", GRN))
        f = tex(r"P = V\,I\,\cos\theta", 120, GRN)
        beat(self, Write(f), t=1.8, rt=1.0)
        b = Brace(f[0][4:], DOWN, color=YEL); bl = kr("위상차만큼 깎인다", 34, YEL).next_to(b, DOWN, .2)
        beat(self, GrowFromCenter(b), FadeIn(bl), t=1.4, rt=.5)
        pulse(self, f, t=1.4, c=GRN)


class A3(Scene):
    """진짜 일: 열·모터, 단위 W."""
    def construct(self):
        self.add(step_tag(3, ORG))
        heat = VGroup(*[FunctionGraph(lambda x: .15 * np.sin(5 * x), x_range=[-.6, .6], color=ORG, stroke_width=6).shift(UP * y) for y in (-.4, .1, .6)])
        h = VGroup(heat, kr("열", 40, ORG).shift(DOWN * 1.2)).shift(LEFT * 3.5)
        m = VGroup(motor((0, 0), GRN), kr("회전", 40, GRN).shift(DOWN * 1.2))
        u = VGroup(tex(r"\mathrm{W}", 120, YEL), kr("와트", 40, YEL)).arrange(DOWN, buff=.2).shift(RIGHT * 3.5)
        beat(self, FadeIn(h), t=1.2, rt=.4); beat(self, FadeIn(m), t=1.2, rt=.4)
        self.play(Rotate(m[0], PI, about_point=m[0].get_center()), run_time=1.0)
        beat(self, Write(u), t=1.4, rt=.6)
        self.play(Rotate(m[0], 2 * PI, about_point=m[0].get_center()), *[w.animate.shift(UP * .2) for w in heat], run_time=1.6)


class A4(Scene):
    """저항만: θ=0 → P = VI."""
    def construct(self):
        self.add(step_tag(3, ORG), head("저항만", GRN))
        a = tex(r"\theta = 0^\circ", 70, INK).shift(UP * .9 + LEFT * 3)
        b = tex(r"\cos\theta = 1", 70, INK).shift(UP * .9 + RIGHT * 2.6)
        c = tex(r"P = V\,I", 100, GRN).shift(DOWN * 1.2)
        beat(self, Write(a), t=1.4, rt=.6); beat(self, Write(b), t=1.4, rt=.6); beat(self, Write(c), t=1.2, rt=.6)
        pulse(self, c, t=1.4, c=GRN)


class A5(Scene):
    """코일만: θ=90° → 평균 0."""
    def construct(self):
        self.add(step_tag(3, ORG), head("코일만", PUR))
        g = wax(ymax=1.3, yl=3.4).shift(DOWN * .8); ax = g[0]; self.add(g)
        f = lambda x: 1.3 * p_(x, PI / 2)
        a = tex(r"\theta = 90^\circ,\ \cos\theta = 0", 56).shift(UP * 1.9)
        beat(self, Write(a), t=1.4, rt=.7)
        p = ax.plot(f, x_range=[0, 2], color=YEL, stroke_width=6)
        beat(self, Create(p), t=1.4, rt=1.0)
        neg = shade_neg(ax, f); pos = shade_neg(ax, lambda x: -f(x), GRN)
        beat(self, FadeIn(neg), FadeIn(pos), t=1.2, rt=.5)
        z = VGroup(kr("평균", 40, YEL), tex("P = 0", 56, YEL)).arrange(RIGHT, buff=.2).to_corner(UR, buff=.4).shift(DOWN * .9)
        beat(self, FadeIn(z), t=.8, rt=.4)
        roam(self, ax, f, YEL, t=1.6, x0=0, x1=.5)


def sum_rows(items):
    g = VGroup(*[VGroup(kr(a, 34, MUTE), b).arrange(RIGHT, buff=.5) for a, b in items]).arrange(DOWN, buff=.55, aligned_edge=LEFT)
    return g.shift(DOWN * .2)


class Sum1(Scene):
    """중간 정리 ① (STEP 1~3)."""
    def construct(self):
        self.add(head("여기까지 정리", YEL))
        rows = sum_rows([("순시전력", VGroup(tex(r"p = v\,i", 50, BLU), kr("두 배 주파수", 36, BLU)).arrange(RIGHT, buff=.4)),
                         ("실횻값", tex(r"220\,\mathrm{V} = 311/\sqrt{2}", 50, GRN)),
                         ("평균 전력", tex(r"P = V\,I\,\cos\theta", 56, YEL))])
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.6, rt=.5)
        pulse(self, rows[2], t=1.6)


# ================= STEP 4 무효·피상 =================
class Q1(Scene):
    """코일: 평균 0 인데 주고받기."""
    def construct(self):
        self.add(step_tag(4, RED))
        g = wax(ymax=1.3, yl=3.6).shift(DOWN * .6); ax = g[0]; self.add(g)
        f = lambda x: 1.3 * p_(x, PI / 2)
        p = ax.plot(f, x_range=[0, 2], color=YEL, stroke_width=6); self.add(p)
        pos = shade_neg(ax, lambda x: -f(x), GRN); neg = shade_neg(ax, f)
        beat(self, FadeIn(pos), t=1.2, rt=.5)
        beat(self, FadeIn(neg), t=1.2, rt=.5)
        lab = VGroup(kr("받고", 40, GRN), tex(r"\leftrightarrow", 56, YEL), kr("돌려주고", 40, RED)).arrange(RIGHT, buff=.3).shift(UP * 2.2)
        beat(self, FadeIn(lab), t=1.2, rt=.5)
        roam(self, ax, f, YEL, t=2.4, x0=0, x1=1)


class Q2(Scene):
    """Q = V I sinθ."""
    def construct(self):
        self.add(step_tag(4, RED), head("무효전력", RED))
        f = tex(r"Q = V\,I\,\sin\theta", 120, RED)
        beat(self, Write(f), t=1.8, rt=1.0)
        cmp = tex(r"P = V\,I\,\cos\theta", 56, GRN).next_to(f, DOWN, .6)
        beat(self, FadeIn(cmp, shift=UP * .2), t=1.6, rt=.5)
        pulse(self, f, t=1.6, c=RED)


class Q3(Scene):
    """단위 VAR, 모터·변압기 자기장."""
    def construct(self):
        self.add(step_tag(4, RED))
        u = VGroup(tex(r"\mathrm{VAR}", 100, RED), kr("바", 44, RED)).arrange(DOWN, buff=.2).shift(LEFT * 3.6)
        beat(self, Write(u), t=1.6, rt=.6)
        core = VGroup(*[Ellipse(width=1.4 + .7 * k, height=.8 + .45 * k, color=PUR, stroke_width=4, stroke_opacity=1 - .22 * k) for k in range(4)]).shift(RIGHT * 2.4)
        m = motor((2.4, 0), INK)
        beat(self, FadeIn(m), t=1.2, rt=.4)
        beat(self, LaggedStart(*[Create(c) for c in core], lag_ratio=.3), t=1.6, rt=1.2)
        lab = kr("자기장 만들기에 필요", 38, PUR).to_edge(DOWN, buff=.6); beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(Rotate(m, 2 * PI, about_point=m.get_center()), run_time=2.0)


class Q4(Scene):
    """코일 +Q (받음) / 콘덴서 −Q (내줌)."""
    def construct(self):
        self.add(step_tag(4, RED))
        l = card(VGroup(kr("코일 L", 40, PUR), tex(r"+Q", 80, PUR), kr("받아 감", 34, MUTE)).arrange(DOWN, buff=.3), PUR, .4).shift(LEFT * 3)
        r = card(VGroup(kr("콘덴서 C", 40, BLU), tex(r"-Q", 80, BLU), kr("내줌", 34, MUTE)).arrange(DOWN, buff=.3), BLU, .4).shift(RIGHT * 3)
        beat(self, FadeIn(l, shift=RIGHT * .3), t=1.6, rt=.5)
        beat(self, FadeIn(r, shift=LEFT * .3), t=1.6, rt=.5)
        a = DoubleArrow(l.get_right(), r.get_left(), buff=.15, color=YEL, stroke_width=6)
        beat(self, GrowFromCenter(a), t=1.0, rt=.5)
        s = kr("부호 반대", 40, YEL).next_to(a, UP, .3); beat(self, FadeIn(s), t=1.2, rt=.4)


class Q5(Scene):
    """S = V I, 단위 VA."""
    def construct(self):
        self.add(step_tag(4, RED), head("피상전력", BLU))
        f = tex(r"S = V\,I", 130, BLU)
        beat(self, Write(f), t=1.6, rt=.9)
        u = VGroup(tex(r"\mathrm{VA}", 80, BLU), kr("볼트암페어", 38, BLU)).arrange(RIGHT, buff=.3).next_to(f, DOWN, .6)
        beat(self, FadeIn(u), t=1.6, rt=.5)
        pulse(self, f, t=1.6, c=BLU)


class Q6(Scene):
    """전선·변압기는 S 로 크기를 정한다."""
    def construct(self):
        self.add(step_tag(4, RED))
        tr = VGroup(Rectangle(width=1.2, height=2.2, color=INK, stroke_width=5), Rectangle(width=1.2, height=2.2, color=INK, stroke_width=5).shift(RIGHT * 1.6),
                    *[Arc(.25, -PI / 2, PI, color=ORG, stroke_width=4).shift(UP * y + RIGHT * .35) for y in (-.6, -.1, .4)],
                    *[Arc(.25, PI / 2, PI, color=ORG, stroke_width=4).shift(UP * y + RIGHT * 1.25) for y in (-.6, -.1, .4)]).shift(LEFT * 4)
        lab1 = kr("변압기", 34, MUTE).next_to(tr, DOWN, .3)
        beat(self, FadeIn(tr), FadeIn(lab1), t=1.4, rt=.5)
        w = Line(LEFT * 1.2, RIGHT * 2.2, color=ORG, stroke_width=26)
        lab2 = kr("전선", 34, MUTE).next_to(w, DOWN, .35)
        beat(self, Create(w), FadeIn(lab2), t=1.4, rt=.6)
        dots = VGroup(*[Dot(LEFT * 1.2 + RIGHT * .5 * k, .1, color=YEL) for k in range(7)])
        self.add(dots); self.play(dots.animate.shift(RIGHT * .5), run_time=1.0, rate_func=linear)
        s = card(VGroup(kr("크기 =", 40, INK), tex("S", 70, BLU)).arrange(RIGHT, buff=.25), BLU, .35).shift(RIGHT * 4.6)
        beat(self, FadeIn(s), t=1.4, rt=.5)
        self.play(dots.animate.shift(RIGHT * .5), run_time=1.0, rate_func=linear)


# ================= STEP 5 전력 삼각형 =================
class T1(Scene):
    """삼각형 하나로 묶기 (P 밑변 → Q 높이 → S 빗변)."""
    def construct(self):
        self.add(step_tag(5, YEL))
        t = tri(labels=False).move_to(ORIGIN)
        beat(self, Create(t[0]), t=1.0, rt=.6); beat(self, Create(t[1]), t=1.0, rt=.6); beat(self, Create(t[2]), t=1.2, rt=.6)
        pulse(self, t, t=1.6)


class T2(Scene):
    """밑변 P, 높이 Q, 빗변 S."""
    def construct(self):
        self.add(step_tag(5, YEL))
        t = tri(nums=False).move_to(ORIGIN); self.add(t[:3])
        for k in (3, 4, 5):
            beat(self, Write(t[k]), Indicate(t[k - 3], color=YEL, scale_factor=1.0), t=1.5, rt=.6)
        nm = VGroup(kr("유효", 30, GRN), kr("무효", 30, RED), kr("피상", 30, BLU))
        nm[0].next_to(t[3], DOWN, .1); nm[1].next_to(t[4], DOWN, .1); nm[2].next_to(t[5], UP, .1)
        beat(self, FadeIn(nm), t=1.2, rt=.4)


class T3(Scene):
    """S² = P² + Q²."""
    def construct(self):
        self.add(step_tag(5, YEL))
        t = tri(nums=False).scale(.8).to_edge(LEFT, buff=.6).shift(DOWN * .2); self.add(t)
        f = tex(r"S^2 = P^2 + Q^2", 84, YEL).shift(RIGHT * 2.6 + UP * .5)
        beat(self, Write(f), t=1.8, rt=.9)
        s = kr("피타고라스", 40, MUTE).next_to(f, DOWN, .5); beat(self, FadeIn(s), t=1.4, rt=.4)
        sq = Square(.5, color=YEL, stroke_width=3).move_to(t[0].get_end() + np.array([-.25, .25, 0]))
        beat(self, Create(sq), t=1.4, rt=.5)


class T4(Scene):
    """각 θ, 역률 = P/S = cosθ."""
    def construct(self):
        self.add(step_tag(5, YEL))
        t = tri(nums=False).scale(.8).to_edge(LEFT, buff=.6).shift(DOWN * .2); self.add(t)
        o = t[0].get_start()
        arc = Arc(.9, 0, np.arctan2(3.3, 4.4), arc_center=o, color=YEL, stroke_width=5)
        th = tex(r"\theta", 50, YEL).move_to(o + np.array([1.2, .38, 0]))
        beat(self, Create(arc), Write(th), t=1.4, rt=.6)
        f = VGroup(kr("역률", 56, YEL), tex(r"= \frac{P}{S} = \cos\theta", 76, YEL)).arrange(RIGHT, buff=.25).shift(RIGHT * 2.8 + UP * .3)
        beat(self, FadeIn(f[0]), t=1.2, rt=.4); beat(self, Write(f[1]), t=1.4, rt=.8)
        pulse(self, f, t=1.6)


class T5(Scene):
    """역률 = 일을 하는 비율 (막대). 1 에 가까울수록 좋다."""
    def construct(self):
        self.add(step_tag(5, YEL))
        full = Rectangle(width=9, height=1.0, color=BLU, stroke_width=4).shift(UP * .6)
        lab = kr("받은 전력 S", 34, BLU).next_to(full, UP, .2)
        beat(self, Create(full), FadeIn(lab), t=1.4, rt=.6)
        k = ValueTracker(.0)
        fill = always_redraw(lambda: Rectangle(width=max(.01, 9 * k.get_value()), height=1.0, color=GRN, fill_color=GRN, fill_opacity=.85,
                                               stroke_width=0).align_to(full, LEFT).align_to(full, DOWN))
        pct = always_redraw(lambda: tex(rf"{k.get_value():.2f}", 60, GRN).next_to(full, DOWN, .4))
        self.add(fill, pct)
        self.play(k.animate.set_value(.6), run_time=1.4)
        w = kr("진짜 일 P", 34, GRN).to_edge(LEFT, buff=1).shift(DOWN * 1.8); beat(self, FadeIn(w), t=1.0, rt=.4)
        self.play(k.animate.set_value(.95), run_time=1.6)
        g = kr("1에 가까울수록 좋다", 40, YEL).to_edge(DOWN, buff=.5); beat(self, FadeIn(g), t=1.0, rt=.4)


class T6(Scene):
    """역률 낮으면 전류 ↑ → 손실 I²R ↑."""
    def construct(self):
        self.add(step_tag(5, YEL))
        f = tex(r"I = \frac{P}{V\cos\theta}", 80, INK).shift(UP * 1.6 + LEFT * 3)
        beat(self, Write(f), t=1.6, rt=.8)
        a = VGroup(kr("역률 ↓", 44, RED), tex(r"\Rightarrow", 60, MUTE), kr("전류 ↑", 44, ORG)).arrange(RIGHT, buff=.4).shift(RIGHT * 2.6 + UP * 1.6)
        beat(self, FadeIn(a), t=1.4, rt=.5)
        loss = VGroup(kr("전선 손실", 46, ORG), tex(r"= I^2 R", 80, ORG)).arrange(RIGHT, buff=.3).shift(DOWN * .8)
        beat(self, Write(loss), t=1.6, rt=.8)
        w = Line(LEFT * 4, RIGHT * 4, color=ORG, stroke_width=18).shift(DOWN * 2.6)
        self.play(Create(w), run_time=.6)
        self.play(w.animate.set_color(RED), run_time=1.2)


class T7(Scene):
    """한전 역률 요금제: 기준 90% — 낮으면 추가, 높으면 감액."""
    def construct(self):
        self.add(step_tag(5, YEL), head("산업용 역률 요금제 (한전)", INK))
        ax = NumberLine(x_range=[60, 100, 10], length=10, color=MUTE, include_numbers=True, font_size=36).shift(DOWN * .4)
        beat(self, Create(ax), t=1.2, rt=.7)
        mk = VGroup(DashedLine(ax.n2p(90) + DOWN * .4, ax.n2p(90) + UP * 1.6, color=YEL, stroke_width=5), kr("기준 90%", 36, YEL).next_to(ax.n2p(90) + UP * 1.6, UP, .1))
        beat(self, FadeIn(mk), t=1.4, rt=.5)
        lo = VGroup(Arrow(ax.n2p(88) + UP * .8, ax.n2p(64) + UP * .8, buff=0, color=RED, stroke_width=6), kr("낮으면 요금 추가", 34, RED))
        lo[1].next_to(lo[0], DOWN, .15)
        beat(self, GrowArrow(lo[0]), FadeIn(lo[1]), t=1.6, rt=.6)
        hi = VGroup(Arrow(ax.n2p(91) + UP * .8, ax.n2p(99) + UP * .8, buff=0, color=GRN, stroke_width=6), kr("높으면 감액", 34, GRN))
        hi[1].next_to(hi[0], DOWN, .15)
        beat(self, GrowArrow(hi[0]), FadeIn(hi[1]), t=1.6, rt=.6)
        n = kr("기본요금에 할인·할증 (한전 기본공급약관)", 26, MUTE).to_edge(DOWN, buff=.4); beat(self, FadeIn(n), t=1.0, rt=.4)


class Sum2(Scene):
    """중간 정리 ② P·Q·S."""
    def construct(self):
        self.add(head("중간 정리", YEL))
        items = [("P", "일", GRN), ("Q", "주고받기", RED), ("S", "설비", BLU)]
        cards = VGroup(*[card(VGroup(tex(a, 90, c), kr(b, 40, c)).arrange(DOWN, buff=.2), c, .4) for a, b, c in items]).arrange(RIGHT, buff=.7).shift(UP * .3)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.0, rt=.4)
        f = VGroup(kr("역률", 46, YEL), tex(r"= P / S", 64, YEL)).arrange(RIGHT, buff=.2).next_to(cards, DOWN, .6)
        beat(self, Write(f), t=1.4, rt=.6)
        pulse(self, f, t=1.4)


# ================= 예제 =================
class E1(Scene):
    """문제: 220V 60Hz, 25A, 역률 0.8 모터."""
    def construct(self):
        self.add(head("예제", YEL))
        G = load_ckt(); c = VGroup(*G.values()).scale(.75).shift(LEFT * 1.6 + DOWN * .3)
        beat(self, Create(VGroup(G["src"], G["top"], G["bot"], G["mw1"], G["mw2"], G["M"])), t=1.4, rt=1.0)
        beat(self, FadeIn(G["lV"]), t=1.0, rt=.4)
        beat(self, GrowArrow(G["arr"]), FadeIn(G["lI"]), FadeIn(G["lM"]), t=1.2, rt=.5)
        pf = card(VGroup(kr("역률", 36, ORG), tex("0.8", 64, ORG)).arrange(DOWN, buff=.2), ORG, .35).shift(RIGHT * 4.6)
        beat(self, FadeIn(pf, shift=LEFT * .3), t=1.6, rt=.5)


class E2(Scene):
    """S = 220 × 25 = 5.5kVA."""
    def construct(self):
        self.add(head("예제 ① 피상전력", BLU))
        f = VGroup(tex(r"S = V\,I", 72, BLU), tex(r"= 220 \times 25", 72), tex(r"= 5.5\,\mathrm{kVA}", 84, YEL)).arrange(DOWN, buff=.45)
        self.add(f[0]); beat(self, Write(f[1]), t=1.4, rt=.7); beat(self, FadeIn(f[2], shift=UP * .2), t=1.4, rt=.5)
        pulse(self, f[2], t=1.6)


class E3(Scene):
    """P = 5.5×0.8 = 4.4kW, Q = 5.5×0.6 = 3.3kVAR."""
    def construct(self):
        self.add(head("예제 ② 유효·무효", INK))
        a = tex(r"P = 5.5 \times 0.8 = 4.4\,\mathrm{kW}", 70, GRN).shift(UP * .8)
        b = tex(r"Q = 5.5 \times 0.6 = 3.3\,\mathrm{kVAR}", 70, RED).shift(DOWN * .8)
        beat(self, Write(a), t=2.2, rt=1.0); beat(self, Write(b), t=2.0, rt=1.0)
        pulse(self, VGroup(a, b), t=1.6)


class E4(Scene):
    """3·4·5 직각삼각형, sinθ = 0.6."""
    def construct(self):
        t = tri().move_to(LEFT * 1.6 + DOWN * .1)
        beat(self, Create(t[:3]), t=1.4, rt=1.0); beat(self, FadeIn(t[3:]), t=1.2, rt=.5)
        r = VGroup(tex(r"3 : 4 : 5", 70, YEL), tex(r"\cos\theta = 0.8", 56, GRN), tex(r"\sin\theta = 0.6", 56, RED)).arrange(DOWN, buff=.4).to_edge(RIGHT, buff=.6)
        beat(self, Write(r[0]), t=1.2, rt=.5); beat(self, FadeIn(r[1]), t=.9, rt=.3); beat(self, FadeIn(r[2]), t=1.2, rt=.3)


class E5(Scene):
    """콘덴서 병렬 연결, 4.4kW 그대로."""
    def construct(self):
        self.add(head("콘덴서를 병렬로", BLU))
        G = load_ckt(with_c=True); c = VGroup(*G.values()).scale(.75).shift(DOWN * .3)
        self.add(G["src"], G["top"], G["bot"], G["mw1"], G["mw2"], G["M"], G["lV"], G["lM"])
        beat(self, Create(VGroup(G["cw1"], G["cw2"], G["C"])), t=1.6, rt=1.0)
        beat(self, FadeIn(G["lC"]), t=1.0, rt=.4)
        k = card(VGroup(kr("모터 일", 32, GRN), tex(r"4.4\,\mathrm{kW}", 56, GRN), kr("그대로", 32, GRN)).arrange(DOWN, buff=.15), GRN, .3).to_edge(RIGHT, buff=.3).shift(UP * 1.5)
        beat(self, FadeIn(k), t=1.4, rt=.5)
        self.play(Rotate(G["M"], 2 * PI, about_point=G["M"].get_center()), run_time=2.0)


class E6(Scene):
    """Q 3.3 → 0: 삼각형이 납작해져 역률 1."""
    def construct(self):
        k = ValueTracker(3.3)
        t = always_redraw(lambda: tri(Q=k.get_value(), nums=False).move_to(LEFT * 1.8 + DOWN * .2, aligned_edge=DOWN).shift(DOWN * .6))
        self.add(t)
        qc = VGroup(kr("콘덴서", 34, BLU), tex(r"-3.3\,\mathrm{kVAR}", 56, BLU)).arrange(DOWN, buff=.15).to_edge(RIGHT, buff=.6).shift(UP * 1.4)
        beat(self, FadeIn(qc, shift=LEFT * .3), t=1.2, rt=.5)
        self.play(k.animate.set_value(0), run_time=2.0)
        r = VGroup(tex(r"Q = 0", 60, RED), VGroup(kr("역률", 40, YEL), tex("= 1", 60, YEL)).arrange(RIGHT, buff=.2)).arrange(DOWN, buff=.35).to_edge(RIGHT, buff=.6).shift(DOWN * .8)
        beat(self, FadeIn(r[0]), t=1.0, rt=.4); beat(self, FadeIn(r[1]), t=1.4, rt=.4)


class E7(Scene):
    """C = Q/(ωV²) = 3300/(377·220²) ≈ 181μF."""
    def construct(self):
        self.add(head("콘덴서 용량", BLU))
        f = VGroup(tex(r"C = \frac{Q}{\omega V^2}", 76, BLU), tex(r"= \frac{3300}{377 \times 220^2}", 72),
                   tex(r"\approx 181\,\mu\mathrm{F}", 88, YEL)).arrange(DOWN, buff=.35)
        beat(self, Write(f[0]), t=1.6, rt=.8)
        w = tex(r"\omega = 2\pi \times 60 \approx 377", 40, MUTE).to_corner(UR, buff=.5).shift(DOWN * .7)
        beat(self, Write(f[1]), FadeIn(w), t=1.8, rt=.9)
        beat(self, FadeIn(f[2], shift=UP * .2), t=1.4, rt=.5)
        pulse(self, f[2], t=1.4)


class E8(Scene):
    """S = 4.4kVA, I = 4400/220 = 20A."""
    def construct(self):
        self.add(head("개선 뒤", GRN))
        a = tex(r"S = 4.4\,\mathrm{kVA}", 70, BLU).shift(UP * 1.2)
        b = tex(r"I = \frac{4400}{220} = 20\,\mathrm{A}", 84, YEL).shift(DOWN * .8)
        beat(self, Write(a), t=1.6, rt=.7); beat(self, Write(b), t=1.8, rt=1.0)
        pulse(self, b, t=1.6)


class E9(Scene):
    """전류 25 → 20A (−20%), 손실 100 → 64 (−36%)."""
    def construct(self):
        l = bars([25, 20], ["개선 전", "개선 뒤"], [RED, GRN], "A", 25).shift(LEFT * 3.2 + DOWN * .3)
        r = bars([100, 64], ["개선 전", "개선 뒤"], [RED, GRN], "\\%", 100).shift(RIGHT * 3.2 + DOWN * .3)
        tl = kr("전류", 38, INK).next_to(l, UP, .4); tr = kr("전선 손실", 38, INK).next_to(r, UP, .4)
        beat(self, FadeIn(tl), *[GrowFromEdge(b[0], DOWN) for b in l], *[FadeIn(b[1:]) for b in l], t=1.8, rt=.8)
        d1 = kr("−20%", 46, YEL).next_to(l, RIGHT, .1).shift(UP * 1); beat(self, FadeIn(d1), t=1.0, rt=.4)
        beat(self, FadeIn(tr), *[GrowFromEdge(b[0], DOWN) for b in r], *[FadeIn(b[1:]) for b in r], t=1.6, rt=.8)
        d2 = kr("−36%", 46, YEL).next_to(r, RIGHT, .1).shift(UP * 1); beat(self, FadeIn(d2), t=1.2, rt=.4)


# ================= 정리 =================
def final_rows():
    return sum_rows([("순시전력", kr("두 배 주파수로 출렁", 40, BLU)),
                     ("220V", kr("실횻값 (최댓값 311V)", 40, GRN)),
                     ("세 전력", tex(r"P=VI\cos\theta,\ Q=VI\sin\theta,\ S=VI", 46, YEL)),
                     ("역률", VGroup(tex(r"P/S", 50, ORG), kr("→ 병렬 콘덴서로 개선", 40, ORG)).arrange(RIGHT, buff=.3))])


class F1(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows()
        beat(self, FadeIn(rows[0], shift=RIGHT * .3), t=1.8, rt=.5); beat(self, FadeIn(rows[1], shift=RIGHT * .3), t=1.8, rt=.5)
        pulse(self, rows[1], t=1.4, c=GRN)


class F2(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows(); self.add(rows[0], rows[1])
        beat(self, FadeIn(rows[2], shift=RIGHT * .3), t=2.0, rt=.6)
        pulse(self, rows[2], t=2.4)


class F3(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows(); self.add(rows[0], rows[1], rows[2])
        beat(self, FadeIn(rows[3], shift=RIGHT * .3), t=2.0, rt=.6)
        pulse(self, rows[3], t=2.4, c=ORG)


class Site(Scene):
    """무료 사이트 안내."""
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("11장 교류 전력 · 역률 개선 문제", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        beat(self, FadeIn(t[0]), t=.8, rt=.3)
        for m in t[1]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.4, rt=.4)
        pulse(self, t, t=2.0)


class Next(Scene):
    """재생목록: 회로이론 한눈에."""
    def construct(self):
        items = ["과도응답", "교류 전력", "3상", "변압기"]
        cards = VGroup(*[card(kr(s, 36, YEL if s == "교류 전력" else MUTE), YEL if s == "교류 전력" else "#2a2e37", .3) for s in items]).arrange(RIGHT, buff=.35)
        lab = kr("재생목록 · 회로이론 한눈에", 40, INK).next_to(cards, UP, .6)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cards], lag_ratio=.3), run_time=1.6)
        arr = Arrow(cards[1].get_bottom() + DOWN * .2, cards[2].get_bottom() + DOWN * .2, buff=0, color=YEL, path_arc=PI / 2)
        beat(self, Create(arr), t=1.6, rt=.8)


# ================= 쇼츠 전용 =================
class D1(Scene):
    """같은 일, 역률 낮으면 전류 더 (막대 20 → 25A)."""
    def construct(self):
        l = bars([20, 25], ["역률 1", "역률 0.8"], [GRN, RED], "A", 25).shift(DOWN * .2)
        t = kr("같은 4.4kW", 40, INK).next_to(l, UP, .5)
        beat(self, FadeIn(t), t=1.0, rt=.4)
        beat(self, GrowFromEdge(l[0][0], DOWN), FadeIn(l[0][1:]), t=1.2, rt=.6)
        beat(self, GrowFromEdge(l[1][0], DOWN), FadeIn(l[1][1:]), t=1.4, rt=.6)
        d = kr("+25%", 50, RED).next_to(l, RIGHT, .4); beat(self, FadeIn(d), t=1.4, rt=.4)


class D2(Scene):
    """손실 ∝ I²: 1.25² = 1.56배."""
    def construct(self):
        f = tex(r"1.25^2 \approx 1.56", 100, ORG).shift(UP * .8)
        beat(self, Write(f), t=1.6, rt=.8)
        s = VGroup(kr("전선 손실", 44, ORG), tex(r"\propto I^2", 64, ORG)).arrange(RIGHT, buff=.3).shift(DOWN * 1.2)
        beat(self, FadeIn(s), t=1.4, rt=.4)
        pulse(self, f, t=1.8, c=ORG)
