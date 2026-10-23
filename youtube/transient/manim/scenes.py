# RC·RL 과도응답 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(롱폼 long.json 에서 그 문장 시작에 붙임). 처음 1~2초에 움직이고 나머지는 멈춘 화면.
# 예제: 10V·10kΩ·100μF (τ 1초), RL 10V·10Ω·10H, 스위치 문제 12V·2kΩ·2kΩ·1mF (12V → 6V, τ 1초).
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
from manim import *
import numpy as np

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
TexTemplateLibrary.default.add_to_preamble(r"\usepackage{amsmath}")
E1 = 1 - np.exp(-1)


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def tex(s, size=56, color=INK):
    return MathTex(s, font_size=size, color=color)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)


# ---------- 부품 ----------
def P3(p):
    return np.array([p[0], p[1], 0.0])


def wire(a, b, c=INK, w=4):
    return Line(P3(a), P3(b), color=c, stroke_width=w)


def res(a, b, c=INK, n=6, amp=.17):
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L; nrm = np.array([-u[1], u[0], 0])
    m0, m1 = .5 * L - .55, .5 * L + .55
    pts = [a, a + u * m0]
    for k in range(n):
        pts.append(a + u * (m0 + (k + .5) * (m1 - m0) / n) + nrm * (amp if k % 2 == 0 else -amp))
    pts += [a + u * m1, b]
    return VMobject(color=c, stroke_width=4).set_points_as_corners(pts)


def cap(a, b, c=INK):
    """a→b 커패시터 (판 두 장)."""
    a, b = P3(a), P3(b); d = b - a; u = d / np.linalg.norm(d); nrm = np.array([-u[1], u[0], 0]); m = (a + b) / 2
    return VGroup(Line(a, m - u * .13, color=c, stroke_width=4), Line(m + u * .13, b, color=c, stroke_width=4),
                  Line(m - u * .13 - nrm * .4, m - u * .13 + nrm * .4, color=c, stroke_width=6),
                  Line(m + u * .13 - nrm * .4, m + u * .13 + nrm * .4, color=c, stroke_width=6))


def coil(a, b, c=INK, n=4):
    """a→b 인덕터 (반원 n개)."""
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L
    m0 = .5 * L - .6; seg = 1.2 / n; g = VGroup(Line(a, a + u * m0, color=c, stroke_width=4))
    for k in range(n):
        p, q = a + u * (m0 + k * seg), a + u * (m0 + (k + 1) * seg)
        g.add(ArcBetweenPoints(p, q, angle=-PI, color=c, stroke_width=4))
    g.add(Line(a + u * (m0 + 1.2), b, color=c, stroke_width=4))
    return g


def vsrc(bot, top, c=INK):
    bot, top = P3(bot), P3(top); m = (bot + top) / 2
    g = VGroup(wire(bot, m + DOWN * .45, c), wire(m + UP * .45, top, c), Circle(.45, color=c, stroke_width=4).move_to(m))
    g.add(tex("+", 34, c).move_to(m + UP * .2), tex("-", 34, c).move_to(m + DOWN * .2))
    return g


def switch(a, b, closed=False, c=INK):
    """a→b 스위치. [0]=a 점, [1]=b 점, [2]=날(a 를 축으로 돈다)."""
    a, b = P3(a), P3(b)
    da = Dot(a, .07, color=c); db = Dot(b, .07, color=c)
    lev = Line(a, b, color=c, stroke_width=5)
    if not closed:
        lev.rotate(35 * DEGREES * (1 if (b - a)[0] >= 0 else -1), about_point=a)
    return VGroup(da, db, lev)


def close_sw(sw):
    a = sw[0].get_center(); b = sw[1].get_center()
    return sw[2].animate.put_start_and_end_on(a, b)


def term(p, s):
    d = Circle(.09, color=INK, fill_color=BG, fill_opacity=1, stroke_width=4).move_to(P3(p))
    return VGroup(d, kr(s, 30, INK).next_to(d, RIGHT, .15))


# ---------- RC / RL 직렬 회로 ----------
XV, XC, Y1, Y0 = -3.9, 2.9, 1.5, -1.5


def series(kind="C", closed=False, src=True, R="10\\,\\mathrm{k}\\Omega", X="100\\,\\mu\\mathrm{F}", V="10\\,\\mathrm{V}"):
    """전원 — 스위치 — 저항 — C 또는 L. dict 로 부품을 돌려준다."""
    P = {}
    if src:
        P["VS"] = vsrc((XV, Y0), (XV, Y1)); P["lV"] = tex(V, 46, YEL).next_to(P3((XV - .45, 0)), LEFT, .15)
    else:
        P["VS"] = wire((XV, Y0), (XV, Y1))
    P["w1"] = wire((XV, Y1), (-3.0, Y1))
    P["SW"] = switch((-3.0, Y1), (-2.0, Y1), closed)
    P["w2"] = wire((-2.0, Y1), (-1.3, Y1))
    P["R"] = res((-1.3, Y1), (1.3, Y1)); P["lR"] = tex(R, 46, ORG).next_to(P3((0, Y1 + .2)), UP, .1)
    P["w3"] = wire((1.3, Y1), (XC, Y1))
    P["X"] = cap((XC, Y1), (XC, Y0)) if kind == "C" else coil((XC, Y1), (XC, Y0))
    P["lX"] = tex(X, 46, BLU if kind == "C" else PUR).next_to(P3((XC + .45, 0)), RIGHT, .15)
    P["bot"] = wire((XV, Y0), (XC, Y0))
    P["lSW"] = tex(r"t=0", 34, MUTE).next_to(P3((-2.5, Y1 + .55)), UP, .05)
    return P


def grp(P):
    return VGroup(*P.values())


# ---------- 그래프 ----------
def axes(ymax=10, ystep=2, ylab=r"v_C\,(\mathrm{V})", xl=8.8, yl=5.0):
    ax = Axes(x_range=[0, 5.4, 1], y_range=[0, ymax * 1.08, ystep], x_length=xl, y_length=yl, tips=False,
              axis_config={"color": MUTE, "stroke_width": 3},
              y_axis_config={"include_numbers": True, "font_size": 36, "numbers_to_exclude": [0]})
    xs = VGroup(*[tex(("" if k == 1 else str(k)) + r"\tau", 38, MUTE).next_to(ax.c2p(k, 0), DOWN, .2) for k in range(1, 6)])
    lab = tex(ylab, 38, MUTE).next_to(ax.y_axis, UP, .15)
    return VGroup(ax, xs, lab).shift(DOWN * .2)


def mark(ax, x, y, txt, c=YEL, side=RIGHT):
    p = ax.c2p(x, y)
    g = VGroup(DashedLine(ax.c2p(x, 0), p, color=c, stroke_width=3), DashedLine(ax.c2p(0, y), p, color=c, stroke_width=3),
               Dot(p, .1, color=c))
    g.add(tex(txt, 46, c).next_to(p, side + UP * .3, .15))
    return g


# ================= 장면 =================
class Hook(Scene):
    """스위치를 켜도 v_C 는 0 에서 천천히: 회로 + 그래프."""
    def construct(self):
        P = series()
        c = grp(P).scale(.62).to_edge(LEFT, buff=.3).shift(UP * .3)
        g = axes(xl=5.8, yl=4.0).to_edge(RIGHT, buff=.4).shift(UP * .5); ax = g[0]
        self.add(c, g)
        self.play(close_sw(P["SW"]), run_time=.4)
        cur = ax.plot(lambda t: 10 * (1 - np.exp(-t)), x_range=[0, 5], color=BLU, stroke_width=6)
        jump = DashedLine(ax.c2p(0, 0), ax.c2p(0, 10), color=RED, stroke_width=4)
        x = kr("✕", 46, RED).next_to(ax.c2p(0, 10), RIGHT, .15)
        self.play(Create(jump), FadeIn(x), run_time=.5)
        self.play(Create(cur), run_time=2.4, rate_func=linear)
        lab = kr("바로 안 올라감", 42, YEL).to_edge(DOWN, buff=.6)
        self.play(FadeIn(lab, shift=UP * .2), run_time=.4)
        self.wait(1)


class Roadmap(Scene):
    """오늘 다룰 것 4칸."""
    def construct(self):
        items = [("시정수", GRN), ("충전·방전", BLU), ("RL 회로", PUR), ("스위치 문제", YEL)]
        cards = VGroup(*[card(kr(t, 40, c), c, .35) for t, c in items]).arrange(RIGHT, buff=.35).shift(UP * .3)
        self.play(LaggedStart(*[FadeIn(k, shift=UP * .3) for k in cards], lag_ratio=.3), run_time=1.4)
        self.wait(1)


class OneFormula(Scene):
    """공식은 하나: 만능 공식 미리보기."""
    def construct(self):
        f = tex(r"x(t) = x(\infty) + \big[\,x(0^+) - x(\infty)\,\big]\,e^{-t/\tau}", 60, INK)
        lab = kr("공식은 하나", 44, YEL).next_to(f, UP, .7)
        self.play(FadeIn(lab), Write(f), run_time=1.3)
        self.play(Circumscribe(f, color=YEL), run_time=.8)
        self.wait(1)


class Cont1(Scene):
    """i_C = C dv/dt."""
    def construct(self):
        self.add(head("커패시터 전류", BLU))
        f = tex(r"i_C = C\,\frac{dv_C}{dt}", 96, INK)
        b = Brace(f[0][4:], DOWN, color=MUTE); bl = kr("전압이 변하는 속도", 34, MUTE).next_to(b, DOWN, .2)
        self.play(Write(f), run_time=1.0)
        self.play(GrowFromCenter(b), FadeIn(bl), run_time=.6)
        self.wait(1)


class Cont2(Scene):
    """전압이 순간에 툭 → 기울기 무한대 → 전류 무한대."""
    def construct(self):
        ax = Axes(x_range=[-1, 2, 1], y_range=[0, 11, 5], x_length=4.6, y_length=3.4, tips=False,
                  axis_config={"color": MUTE, "stroke_width": 3}).shift(LEFT * 2.6 + DOWN * .2)
        st = VMobject(color=RED, stroke_width=6).set_points_as_corners([ax.c2p(-1, 0), ax.c2p(0, 0), ax.c2p(0, 10), ax.c2p(2, 10)])
        lab = tex(r"v_C", 34, MUTE).next_to(ax.y_axis, UP, .1)
        t0 = tex(r"t=0", 30, MUTE).next_to(ax.c2p(0, 0), DOWN, .15)
        self.play(Create(ax), FadeIn(lab), FadeIn(t0), run_time=.5)
        self.play(Create(st), run_time=.8)
        f = VGroup(tex(r"\frac{dv_C}{dt} = \infty", 64, RED), tex(r"i_C = \infty", 64, RED), kr("불가능", 40, RED)).arrange(DOWN, buff=.35)
        f.shift(RIGHT * 2.8)
        self.play(Write(f[0]), run_time=.7)
        self.play(Write(f[1]), FadeIn(f[2]), run_time=.7)
        self.wait(1)


class Cont3(Scene):
    """v_C(0⁻) = v_C(0⁺)."""
    def construct(self):
        self.add(head("커패시터 전압은 연속", BLU))
        f = tex(r"v_C(0^-) = v_C(0^+)", 96, YEL)
        s = kr("스위치 직전 = 직후", 40, MUTE).next_to(f, DOWN, .6)
        self.play(Write(f), run_time=1.0); self.play(FadeIn(s), run_time=.4)
        self.wait(1)


class Dual(Scene):
    """C: 전압 연속 / L: 전류 연속."""
    def construct(self):
        l = card(VGroup(kr("커패시터 C", 40, BLU), tex(r"i = C\,\frac{dv}{dt}", 56), kr("전압이 연속", 40, YEL)).arrange(DOWN, buff=.35), BLU, .4)
        r = card(VGroup(kr("인덕터 L", 40, PUR), tex(r"v = L\,\frac{di}{dt}", 56), kr("전류가 연속", 40, YEL)).arrange(DOWN, buff=.35), PUR, .4)
        VGroup(l, r).arrange(RIGHT, buff=.8)
        self.add(l); self.play(FadeIn(r, shift=LEFT * .3), run_time=.8)
        self.wait(1)


class RCckt(Scene):
    """RC 충전 회로를 그리고 스위치를 닫는다."""
    def construct(self):
        self.add(head("RC 충전", BLU))
        P = series(); c = grp(P).shift(DOWN * .3)
        self.play(Create(VGroup(P["VS"], P["w1"], P["SW"], P["w2"], P["R"], P["w3"], P["X"], P["bot"])), run_time=1.6)
        self.play(FadeIn(P["lV"]), run_time=.3); self.wait(.6)
        self.play(FadeIn(P["lR"]), run_time=.3); self.wait(.7)
        self.play(FadeIn(P["lX"]), FadeIn(P["lSW"]), run_time=.3); self.wait(1.4)
        self.play(close_sw(P["SW"]), run_time=.4)
        self.wait(1)


def rc_closed(sh=DOWN * .3):
    P = series(closed=True); return P, grp(P).shift(sh)


class RCstart(Scene):
    """t=0⁺: v_C = 0, 전류 1mA."""
    def construct(self):
        self.add(head("RC 충전", BLU))
        P, c = rc_closed(); self.add(c)
        a = Arrow(P3((-.9, Y1 - .55)) + DOWN * .3, P3((.7, Y1 - .55)) + DOWN * .3, color=GRN, buff=0, stroke_width=6)
        v0 = tex(r"v_C = 0", 40, BLU).next_to(P["lX"], DOWN, .3)
        f = tex(r"i(0^+) = \frac{10\,\mathrm{V}}{10\,\mathrm{k}\Omega} = 1\,\mathrm{mA}", 50, GRN).to_edge(DOWN, buff=.45)
        self.play(GrowArrow(a), FadeIn(v0), run_time=.6)
        self.play(Write(f), run_time=1.0)
        self.wait(1)


class Slow(Scene):
    """차오를수록 느려진다: 곡선 + 기울기 접선."""
    def construct(self):
        g = axes(); ax = g[0]; self.add(g)
        cur = ax.plot(lambda t: 10 * (1 - np.exp(-t)), x_range=[0, 5], color=BLU, stroke_width=6)
        self.play(Create(cur), run_time=1.8, rate_func=linear)
        tans = VGroup()
        for t0 in (0.45, 1.4, 3.2):
            y0 = 10 * (1 - np.exp(-t0)); s = 10 * np.exp(-t0)
            tans.add(Line(ax.c2p(t0 - .4, y0 - .4 * s), ax.c2p(t0 + .4, y0 + .4 * s), color=ORG, stroke_width=5))
        lab = kr("점점 느려짐", 40, ORG).next_to(ax.c2p(3.2, 4), RIGHT, .1)
        self.play(LaggedStart(*[Create(t) for t in tans], lag_ratio=.5), FadeIn(lab), run_time=1.0)
        self.wait(1)


class Tau(Scene):
    """τ = RC."""
    def construct(self):
        self.add(head("시정수 τ", GRN))
        f = tex(r"\tau = R\,C", 140, YEL)
        self.play(Write(f), run_time=.9); self.play(Circumscribe(f, color=YEL), run_time=.7)
        self.wait(1)


class TauCalc(Scene):
    """10kΩ × 100μF = 1초."""
    def construct(self):
        self.add(head("시정수 τ", GRN))
        f = VGroup(tex(r"\tau = R\,C", 80, YEL), tex(r"= 10\,\mathrm{k}\Omega \times 100\,\mu\mathrm{F}", 64),
                   tex(r"= 1\,\mathrm{s}", 96, YEL)).arrange(DOWN, buff=.35)
        self.add(f[0]); self.play(Write(f[1]), run_time=.9); self.play(FadeIn(f[2], scale=1.3), run_time=.5)
        self.wait(1)


def charge_base():
    g = axes(); ax = g[0]
    cur = ax.plot(lambda t: 10 * (1 - np.exp(-t)), x_range=[0, 5], color=BLU, stroke_width=6)
    fin = DashedLine(ax.c2p(0, 10), ax.c2p(5.3, 10), color=MUTE, stroke_width=2)
    return g, ax, cur, fin


class Ch1(Scene):
    """1τ → 63.2%, 6.3V."""
    def construct(self):
        g, ax, cur, fin = charge_base(); self.add(g, fin)
        self.play(Create(cur), run_time=1.2, rate_func=linear)
        m = mark(ax, 1, 10 * E1, r"63.2\%\ (6.3\,\mathrm{V})")
        self.play(Create(m[:3]), FadeIn(m[3]), run_time=.7)
        self.wait(1)


class Ch2(Scene):
    """2τ 86%, 3τ 95%."""
    def construct(self):
        g, ax, cur, fin = charge_base(); m1 = mark(ax, 1, 10 * E1, r"63.2\%\ (6.3\,\mathrm{V})")
        self.add(g, fin, cur, m1)
        m2 = mark(ax, 2, 8.65, r"86\%", GRN); m3 = mark(ax, 3, 9.5, r"95\%", GRN)
        m2[3].move_to(ax.c2p(2.45, 4.6)); m3[3].move_to(ax.c2p(3.45, 6.0))
        self.play(Create(m2[0]), Create(m2[2]), FadeIn(m2[3]), run_time=.5); self.wait(.8)
        self.play(Create(m3[0]), Create(m3[2]), FadeIn(m3[3]), run_time=.5)
        self.wait(1)


class Ch5(Scene):
    """5τ 99% → 다 찼다."""
    def construct(self):
        g, ax, cur, fin = charge_base(); m1 = mark(ax, 1, 10 * E1, r"63.2\%\ (6.3\,\mathrm{V})")
        self.add(g, fin, cur, m1)
        d = Dot(ax.c2p(5, 9.93), .12, color=YEL)
        lab = VGroup(tex(r"5\tau:\ 99\%", 44, YEL), kr("다 찼다", 36, YEL)).arrange(DOWN, buff=.15).next_to(ax.c2p(4.6, 9.9), DOWN, .45)
        self.play(FadeIn(d, scale=2), FadeIn(lab), run_time=.6)
        self.wait(1)


class Dis1(Scene):
    """방전 회로: 전원을 빼고 R-C 고리."""
    def construct(self):
        self.add(head("RC 방전", RED))
        P = series(src=False, closed=True); c = grp(P).shift(DOWN * .3)
        lx = tex(r"v_C(0) = 10\,\mathrm{V}", 40, BLU).next_to(P3((XC + .45, -.3)), RIGHT, .15)
        body = VGroup(P["VS"], P["w1"], P["SW"], P["w2"], P["R"], P["lR"], P["w3"], P["X"], P["bot"])
        self.play(Create(body), FadeIn(lx), run_time=1.2)
        a = Arrow(P3((.7, Y1 - .55)) + DOWN * .3, P3((-.9, Y1 - .55)) + DOWN * .3, color=RED, buff=0, stroke_width=6)
        self.play(GrowArrow(a), run_time=.5)
        self.wait(1)


def dis_base():
    g = axes(); ax = g[0]
    cur = ax.plot(lambda t: 10 * np.exp(-t), x_range=[0, 5], color=RED, stroke_width=6)
    return g, ax, cur


class Dis2(Scene):
    """v = 10 e^{-t/τ}."""
    def construct(self):
        g, ax, cur = dis_base(); self.add(g)
        f = tex(r"v_C = 10\,e^{-t/\tau}", 56, RED).next_to(ax.c2p(2.2, 8), RIGHT, 0)
        self.play(Create(cur), Write(f), run_time=1.4)
        self.wait(1)


class Dis3(Scene):
    """1τ → 36.8%, 3.7V."""
    def construct(self):
        g, ax, cur = dis_base(); f = tex(r"v_C = 10\,e^{-t/\tau}", 56, RED).next_to(ax.c2p(2.2, 8), RIGHT, 0)
        self.add(g, cur, f)
        m = mark(ax, 1, 10 * np.exp(-1), r"36.8\%\ (3.7\,\mathrm{V})")
        self.play(Create(m[:3]), FadeIn(m[3]), run_time=.7)
        self.wait(1)


class Dis4(Scene):
    """충전 63.2% + 방전 36.8% = 100%."""
    def construct(self):
        g = axes(); ax = g[0]
        up = ax.plot(lambda t: 10 * (1 - np.exp(-t)), x_range=[0, 5], color=BLU, stroke_width=6)
        dn = ax.plot(lambda t: 10 * np.exp(-t), x_range=[0, 5], color=RED, stroke_width=6)
        self.add(g); self.play(Create(up), Create(dn), run_time=1.0)
        a = mark(ax, 1, 10 * E1, r"63.2\%", BLU); b = mark(ax, 1, 10 * np.exp(-1), r"36.8\%", RED, DOWN + RIGHT)
        self.play(Create(a[0]), Create(a[2]), Create(b[2]), FadeIn(a[3]), FadeIn(b[3]), run_time=.6)
        s = tex(r"63.2 + 36.8 = 100\%", 52, YEL).next_to(ax.c2p(2.3, 5.5), RIGHT, 0)
        self.play(Write(s), run_time=.8)
        self.wait(1)


class RL1(Scene):
    """RL 회로: 커패시터 자리에 인덕터."""
    def construct(self):
        self.add(head("RL 회로", PUR))
        Pc = series(); Pl = series("L", R=r"10\,\Omega", X=r"10\,\mathrm{H}")
        c = grp(Pc).shift(DOWN * .3); l = grp(Pl).shift(DOWN * .3)
        self.add(c)
        self.play(ReplacementTransform(Pc["X"], Pl["X"]), ReplacementTransform(Pc["lX"], Pl["lX"]),
                  ReplacementTransform(Pc["lR"], Pl["lR"]), Indicate(Pl["X"], color=PUR), run_time=1.0)
        self.wait(1)


class RL2(Scene):
    """인덕터는 전류를 붙잡는다: 전류가 0 에서 천천히."""
    def construct(self):
        g = axes(ymax=1, ystep=.5, ylab=r"i_L\,(\mathrm{A})"); ax = g[0]; self.add(g)
        jump = DashedLine(ax.c2p(0, 0), ax.c2p(0, 1), color=RED, stroke_width=4)
        x = kr("✕", 46, RED).next_to(ax.c2p(0, 1), RIGHT, .15)
        cur = ax.plot(lambda t: 1 - np.exp(-t), x_range=[0, 5], color=PUR, stroke_width=6)
        self.play(Create(jump), FadeIn(x), run_time=.4)
        self.play(Create(cur), run_time=1.6, rate_func=linear)
        lab = kr("전류를 붙잡음", 40, PUR).next_to(ax.c2p(2.0, .45), RIGHT, 0)
        self.play(FadeIn(lab), run_time=.4)
        self.wait(1)


class RL3(Scene):
    """RC 는 곱하기, RL 은 나누기."""
    def construct(self):
        self.add(head("시정수", GRN))
        l = card(VGroup(kr("RC", 44, BLU), tex(r"\tau = R\,C", 72), kr("곱하기", 38, YEL)).arrange(DOWN, buff=.3), BLU, .45)
        r = card(VGroup(kr("RL", 44, PUR), tex(r"\tau = \frac{L}{R}", 72), kr("나누기", 38, YEL)).arrange(DOWN, buff=.3), PUR, .45)
        VGroup(l, r).arrange(RIGHT, buff=1.0).shift(DOWN * .2)
        self.play(FadeIn(r, shift=UP * .2), run_time=.6); self.wait(1.0)
        self.play(FadeIn(l, shift=UP * .2), run_time=.6)
        self.wait(1)


class RL4(Scene):
    """10V, 10Ω, 10H → τ 1초, 최종 1A."""
    def construct(self):
        self.add(head("RL 회로", PUR))
        f = VGroup(tex(r"\tau = \frac{L}{R} = \frac{10\,\mathrm{H}}{10\,\Omega} = 1\,\mathrm{s}", 64, INK),
                   tex(r"i(\infty) = \frac{10\,\mathrm{V}}{10\,\Omega} = 1\,\mathrm{A}", 64, INK)).arrange(DOWN, buff=.6)
        self.play(Write(f[0]), run_time=1.0); self.wait(.8); self.play(Write(f[1]), run_time=.9)
        self.wait(1)


class RL5(Scene):
    """1τ → 0.632A, 모양은 RC 충전과 같음."""
    def construct(self):
        g = axes(ymax=1, ystep=.5, ylab=r"i_L\,(\mathrm{A})"); ax = g[0]
        cur = ax.plot(lambda t: 1 - np.exp(-t), x_range=[0, 5], color=PUR, stroke_width=6)
        self.add(g, cur)
        m = mark(ax, 1, E1, r"63.2\%\ (0.632\,\mathrm{A})", PUR)
        self.play(Create(m[:3]), FadeIn(m[3]), run_time=.7)
        same = kr("RC 충전과 같은 모양", 36, MUTE).next_to(ax.c2p(2.3, .35), RIGHT, 0)
        self.play(FadeIn(same), run_time=.4)
        self.wait(1)


def uni(size=64):
    return MathTex(r"x(t)", "=", r"x(\infty)", "+", r"\big[\,", r"x(0^+)", "-", r"x(\infty)", r"\,\big]", r"\,e^{-t/", r"\tau", "}",
                   font_size=size, color=INK)


class Uni1(Scene):
    """만능 공식."""
    def construct(self):
        self.add(head("만능 공식", YEL))
        f = uni(72)
        self.play(Write(f), run_time=1.3); self.play(Circumscribe(f, color=YEL), run_time=.7)
        self.wait(1)


class Uni2(Scene):
    """공식의 세 부분을 색칠."""
    def construct(self):
        self.add(head("만능 공식", YEL))
        f = uni(72); self.add(f)
        b1 = Brace(f[2], DOWN, color=GRN); t1 = kr("최종값", 32, GRN).next_to(b1, DOWN, .15)
        b2 = Brace(f[5], DOWN, color=BLU); t2 = kr("처음값", 32, BLU).next_to(b2, DOWN, .15)
        b3 = Brace(f[10], DOWN, color=ORG); t3 = kr("시정수", 32, ORG).next_to(b3, DOWN, .15)
        self.play(f[2].animate.set_color(GRN), f[7].animate.set_color(GRN), GrowFromCenter(b1), FadeIn(t1), run_time=.5); self.wait(.6)
        self.play(f[5].animate.set_color(BLU), GrowFromCenter(b2), FadeIn(t2), run_time=.5); self.wait(1.2)
        self.play(f[10].animate.set_color(ORG), GrowFromCenter(b3), FadeIn(t3), run_time=.5)
        self.wait(1)


class Uni3(Scene):
    """충전·방전·RC·RL 네 그래프가 같은 식."""
    def construct(self):
        items = [("RC 충전", lambda t: 1 - np.exp(-t), BLU), ("RC 방전", lambda t: np.exp(-t), RED),
                 ("RL 전류", lambda t: 1 - np.exp(-t), PUR), ("RL 차단", lambda t: np.exp(-t), ORG)]
        gs = VGroup()
        for name, fn, c in items:
            ax = Axes(x_range=[0, 5, 1], y_range=[0, 1.1, 1], x_length=2.4, y_length=1.6, tips=False, axis_config={"color": MUTE, "stroke_width": 2})
            gs.add(VGroup(ax, ax.plot(fn, x_range=[0, 5], color=c, stroke_width=5), kr(name, 28, c).next_to(ax, DOWN, .2)))
        gs.arrange(RIGHT, buff=.45).shift(UP * .6)
        f = uni(48).to_edge(DOWN, buff=.8)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * .2) for g in gs], lag_ratio=.25), run_time=1.2)
        self.play(FadeIn(f), run_time=.5)
        self.wait(1)


class Uni4(Scene):
    """구할 건 세 개."""
    def construct(self):
        items = [(r"x(0^+)", "처음값", BLU), (r"x(\infty)", "최종값", GRN), (r"\tau", "시정수", ORG)]
        cards = VGroup(*[card(VGroup(tex(a, 64, c), kr(b, 36, c)).arrange(DOWN, buff=.3), c, .45) for a, b, c in items]).arrange(RIGHT, buff=.6)
        h = kr("구할 건 세 개", 46, YEL).next_to(cards, UP, .7)
        self.play(FadeIn(h), run_time=.4)
        self.play(LaggedStart(*[FadeIn(k, shift=UP * .3) for k in cards], lag_ratio=.4), run_time=1.4)
        self.wait(1)


# ---------- 스위치 문제 ----------
SXV, SXN, SXC, SY1, SY0 = -4.0, .4, 3.3, 1.7, -1.7


def sw_ckt(closed=False, c_open=False, labels=True):
    """12V — 2kΩ — 마디 — (스위치 + 2kΩ) ∥ 1mF."""
    P = {}
    P["VS"] = vsrc((SXV, SY0), (SXV, SY1))
    P["R1"] = res((SXV, SY1), (SXN, SY1))
    P["top"] = wire((SXN, SY1), (SXC, SY1))
    P["bot"] = wire((SXV, SY0), (SXC, SY0))
    P["wS"] = wire((SXN, SY1), (SXN, 1.15))
    P["SW"] = switch((SXN, 1.15), (SXN, .3), closed)
    P["R2"] = res((SXN, .3), (SXN, SY0))
    if c_open:
        P["C"] = VGroup(wire((SXC, SY1), (SXC, .35), MUTE), wire((SXC, -.35), (SXC, SY0), MUTE))
    else:
        P["C"] = cap((SXC, SY1), (SXC, SY0))
    if labels:
        P["lV"] = tex(r"12\,\mathrm{V}", 46, YEL).next_to(P3((SXV - .45, 0)), LEFT, .15)
        P["lR1"] = tex(r"2\,\mathrm{k}\Omega", 44, ORG).next_to(P3(((SXV + SXN) / 2, SY1 + .2)), UP, .1)
        P["lR2"] = tex(r"2\,\mathrm{k}\Omega", 44, ORG).next_to(P3((SXN + .25, -.7)), RIGHT, .1)
        P["lSW"] = tex(r"t=0", 34, MUTE).next_to(P3((SXN + .4, .95)), RIGHT, .05)
        P["lC"] = (kr("개방", 36, YEL) if c_open else tex(r"1\,\mathrm{mF}", 44, BLU)).next_to(P3((SXC + .45, 0)), RIGHT, .15)
    return P


class Sw1(Scene):
    """스위치 문제 제목."""
    def construct(self):
        t = kr("스위치 문제", 72, YEL); s = tex(r"t=0^- \ \rightarrow\ t=0^+ \ \rightarrow\ t=\infty", 56, INK).next_to(t, DOWN, .6)
        self.play(FadeIn(t, scale=1.1), run_time=.6); self.play(Write(s), run_time=.9)
        self.wait(1)


class Sw2(Scene):
    """회로 그리기 → 스위치 닫힘."""
    def construct(self):
        P = sw_ckt(); c = grp(P).shift(DOWN * .1)
        self.play(Create(VGroup(P["VS"], P["R1"], P["top"], P["bot"], P["C"])), FadeIn(P["lV"]), FadeIn(P["lR1"]), FadeIn(P["lC"]), run_time=1.6)
        self.wait(2.2)
        self.play(Create(VGroup(P["wS"], P["SW"], P["R2"])), FadeIn(P["lR2"]), FadeIn(P["lSW"]), run_time=.8)
        self.play(close_sw(P["SW"]), run_time=.4)
        self.wait(1)


def step_tag(s, c=YEL):
    return kr(s, 40, c).to_corner(UL, buff=.45)


class Sw3(Scene):
    """1단계 0⁻: 스위치 열림, C 개방."""
    def construct(self):
        self.add(step_tag("1단계  t = 0⁻"))
        P0 = sw_ckt(); P = sw_ckt(c_open=True)
        c0 = grp(P0).shift(DOWN * .1); c = grp(P).shift(DOWN * .1)
        self.add(c0)
        self.play(ReplacementTransform(P0["C"], P["C"]), ReplacementTransform(P0["lC"], P["lC"]), run_time=.7)
        self.wait(1)


class Sw4(Scene):
    """전류 0 → v_C = 12V."""
    def construct(self):
        self.add(step_tag("1단계  t = 0⁻"))
        P = sw_ckt(c_open=True); c = grp(P).shift(DOWN * .1); self.add(c)
        i0 = tex(r"i = 0", 40, GRN).next_to(P3(((SXV + SXN) / 2, SY1 - .5)), DOWN, 0)
        v = tex(r"v_C(0^-) = 12\,\mathrm{V}", 52, YEL).to_edge(DOWN, buff=.35)
        self.play(FadeIn(i0), run_time=.4); self.play(Write(v), run_time=.8)
        self.wait(1)


def steps_row(n):
    items = [(r"t=0^-", r"12\,\mathrm{V}", "개방"), (r"t=0^+", r"12\,\mathrm{V}", "그대로"), (r"t=\infty", r"6\,\mathrm{V}", "분압")]
    cards = VGroup(*[card(VGroup(tex(a, 50, MUTE), tex(b, 72, YEL), kr(s, 32, INK)).arrange(DOWN, buff=.3), c, .4)
                     for (a, b, s), c in zip(items, (BLU, GRN, ORG))]).arrange(RIGHT, buff=.9)
    return cards


class Sw5(Scene):
    """2단계 0⁺: 그대로 12V."""
    def construct(self):
        cards = steps_row(3).shift(DOWN * .2)
        arr = VGroup(*[Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=.08, color=MUTE) for i in range(2)])
        self.add(cards[0])
        self.play(GrowArrow(arr[0]), FadeIn(cards[1], shift=RIGHT * .3), run_time=.7)
        self.wait(1)


class Sw6(Scene):
    """3단계 ∞: 스위치 닫힘, C 개방, 분압 6V."""
    def construct(self):
        self.add(step_tag("3단계  t = ∞", ORG))
        P = sw_ckt(closed=True, c_open=True); c = grp(P).shift(DOWN * .1)
        self.play(FadeIn(c), run_time=.5)
        v = tex(r"v_C(\infty) = 12 \times \frac{2}{2+2} = 6\,\mathrm{V}", 50, YEL).to_edge(DOWN, buff=.3)
        self.play(Indicate(P["R1"], color=ORG), Indicate(P["R2"], color=ORG), run_time=.8)
        self.play(Write(v), run_time=.9)
        self.wait(1)


class Sw7(Scene):
    """시정수: C 에서 본 저항 2k ∥ 2k = 1k, × 1mF = 1초."""
    def construct(self):
        self.add(head("시정수", GRN))
        f = VGroup(tex(r"R_{th} = 2\,\mathrm{k} \parallel 2\,\mathrm{k} = 1\,\mathrm{k}\Omega", 60),
                   tex(r"\tau = 1\,\mathrm{k}\Omega \times 1\,\mathrm{mF} = 1\,\mathrm{s}", 64, YEL)).arrange(DOWN, buff=.6)
        s = kr("전압원은 단락, 커패시터 자리에서 들여다본 저항", 30, MUTE).next_to(f, DOWN, .6)
        self.play(Write(f[0]), FadeIn(s), run_time=1.0); self.wait(1.4)
        self.play(Write(f[1]), run_time=.9)
        self.wait(1)


class Sw8(Scene):
    """답: v = 6 + 6e^{-t}, 12V → 6V 곡선."""
    def construct(self):
        g = axes(ymax=12, ystep=6); ax = g[0]; self.add(g)
        cur = ax.plot(lambda t: 6 + 6 * np.exp(-t), x_range=[0, 5], color=YEL, stroke_width=6)
        f = tex(r"v_C(t) = 6 + 6\,e^{-t}\ \mathrm{V}", 56, YEL).next_to(ax.c2p(1.6, 11.5), RIGHT, 0)
        fin = DashedLine(ax.c2p(0, 6), ax.c2p(5.3, 6), color=MUTE, stroke_width=2)
        self.play(Write(f), run_time=.8)
        self.play(Create(fin), Create(cur), run_time=1.4)
        self.wait(1)


class Sum1(Scene):
    """정리 ① 연속."""
    def construct(self):
        self.add(head("정리"))
        rows = sum_rows(); self.play(FadeIn(rows[0], shift=RIGHT * .3), run_time=.6)
        self.wait(1)


def sum_rows():
    rows = [(kr("연속", 36, MUTE), VGroup(kr("C → 전압", 40, BLU), kr("L → 전류", 40, PUR)).arrange(RIGHT, buff=.6)),
            (kr("직류 정상상태", 36, MUTE), VGroup(kr("C → 개방", 40, BLU), kr("L → 단락", 40, PUR)).arrange(RIGHT, buff=.6)),
            (kr("시정수", 36, MUTE), VGroup(tex(r"RC", 52, BLU), tex(r"L/R", 52, PUR), tex(r"1\tau = 63.2\%", 52, YEL)).arrange(RIGHT, buff=.6))]
    g = VGroup(*[VGroup(a, b).arrange(RIGHT, buff=.6) for a, b in rows]).arrange(DOWN, buff=.7, aligned_edge=LEFT).shift(DOWN * .2)
    return g


class Sum2(Scene):
    def construct(self):
        self.add(head("정리")); rows = sum_rows(); self.add(rows[0])
        self.play(FadeIn(rows[1], shift=RIGHT * .3), run_time=.6); self.wait(1)


class Sum3(Scene):
    def construct(self):
        self.add(head("정리")); rows = sum_rows(); self.add(rows[0], rows[1])
        self.play(FadeIn(rows[2], shift=RIGHT * .3), run_time=.6); self.wait(1)


class Site(Scene):
    """무료 사이트 안내."""
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("7장 과도 응답 · 값을 바꿔 가며 직접", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        self.play(FadeIn(t, scale=1.05), run_time=.7)
        self.wait(1)
