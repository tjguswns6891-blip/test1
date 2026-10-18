# 회로이론 8장 2차 RLC 과도 응답 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
from manim import *
import numpy as np

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
TexTemplateLibrary.default.add_to_preamble(r"\usepackage{amsmath}")
COL = {"over": ORG, "crit": GRN, "under": BLU}
NAME = {"over": "과감쇠", "crit": "임계 감쇠", "under": "부족 감쇠"}


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def tex(s, size=56, color=INK):
    return MathTex(s, font_size=size, color=color)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)


def step(z, t, w0=1.0):
    """감쇠비 z, 고유 각주파수 w0 인 2차 계단 응답 (최종값 1)."""
    a = z * w0
    if abs(z - 1) < 1e-3:
        return 1 - (1 + a * t) * np.exp(-a * t)
    if z > 1:
        d = w0 * np.sqrt(z * z - 1); s1, s2 = -a + d, -a - d
        return 1 + (s2 * np.exp(s1 * t) - s1 * np.exp(s2 * t)) / (s1 - s2)
    wd = w0 * np.sqrt(1 - z * z)
    return 1 - np.exp(-a * t) * (np.cos(wd * t) + a / wd * np.sin(wd * t))


def poles(z, w0=1.0):
    a = z * w0
    if z >= 1:
        d = w0 * np.sqrt(max(z * z - 1, 0)); return [(-a + d, 0), (-a - d, 0)]
    wd = w0 * np.sqrt(1 - z * z); return [(-a, wd), (-a, -wd)]


def resp_axes(w=5.6, h=3.0, T=12):
    ax = Axes(x_range=[0, T, 2], y_range=[0, 1.9, .5], x_length=w, y_length=h,
              axis_config={"stroke_color": MUTE, "include_ticks": False})
    one = DashedLine(ax.c2p(0, 1), ax.c2p(T, 1), color=MUTE, dash_length=.08)
    lt = kr("t", 24, MUTE).next_to(ax.x_axis, RIGHT, .1); lv = MathTex(r"v_C", font_size=30, color=MUTE).next_to(ax.y_axis, UP, .1)
    return VGroup(ax, one, lt, lv), ax


def splane(r=1.4, R=2.6):
    """s-평면: 실수축·허수축, 반지름 r(=ω0) 점선 원."""
    pl = NumberPlane(x_range=[-R, .8, 1], y_range=[-1.6, 1.6, 1], x_length=(R + .8) * r, y_length=3.2 * r,
                     background_line_style={"stroke_color": "#262a33", "stroke_width": 1}, axis_config={"stroke_color": MUTE})
    circ = DashedVMobject(Circle(radius=r, color=MUTE).move_to(pl.c2p(0, 0)), num_dashes=40)
    ls = MathTex(r"\sigma", font_size=28, color=MUTE).next_to(pl.c2p(.8, 0), DOWN, .1)
    lj = MathTex(r"j\omega", font_size=28, color=MUTE).next_to(pl.c2p(0, 1.6), RIGHT, .1)
    lw = MathTex(r"\omega_0", font_size=26, color=MUTE).move_to(pl.c2p(.45, 1.05))
    return VGroup(pl, circ, ls, lj, lw), pl


def xmark(p, pt, c=PUR, s=.16):
    q = p.c2p(*pt)
    return VGroup(Line(q + [-s, -s, 0], q + [s, s, 0], color=c, stroke_width=7), Line(q + [-s, s, 0], q + [s, -s, 0], color=c, stroke_width=7))


class Hook(Scene):
    """같은 회로, 저항만 다르게: 과감쇠 · 임계 · 부족 세 곡선."""
    def construct(self):
        h = head("같은 RLC 회로, 저항만 바꾸면")
        g, ax = resp_axes(9.6, 4.6, 12); g.shift(DOWN * .4)
        self.play(FadeIn(h), Create(g), run_time=1.0)
        labs = []
        for k, z, y in (("under", .2, 1.62), ("crit", 1.0, 1.25), ("over", 3.0, .85)):
            c = ax.plot(lambda t: step(z, t), x_range=[0, 12, .02], color=COL[k], stroke_width=6)
            l = kr(NAME[k], 30, COL[k]).move_to(ax.c2p(9.6, y + .22)) if k != "over" else kr(NAME[k], 30, COL[k]).move_to(ax.c2p(7.0, .42))
            self.play(Create(c), FadeIn(l), run_time=1.3); labs.append(l); self.wait(.3)
        self.wait(2)


class Energy(Scene):
    """에너지 저장소 두 개: C(전기장) ↔ L(자기장), 그네 비유 → 2차 미분방정식."""
    def construct(self):
        h = head("에너지를 담는 곳이 두 군데")
        self.play(FadeIn(h))
        t = ValueTracker(0)
        def bar(x, col, lab, f):
            base = Rectangle(width=1.2, height=3.0, color=MUTE).shift(RIGHT * x + DOWN * .3)
            fill = always_redraw(lambda: Rectangle(width=1.2, height=max(.02, 3.0 * f(t.get_value())), fill_color=col,
                                 fill_opacity=.85, stroke_width=0).align_to(base, DOWN).shift(RIGHT * x))
            return VGroup(base, fill, kr(lab, 28, col).next_to(base, DOWN, .25))
        wc = lambda u: np.cos(u) ** 2 * np.exp(-.08 * u); wl = lambda u: np.sin(u) ** 2 * np.exp(-.08 * u)
        bc = bar(-4.2, YEL, "C · 전기장", wc); bl = bar(-1.8, BLU, "L · 자기장", wl)
        arr = DoubleArrow(LEFT * 3.4 + UP * .2, LEFT * 2.6 + UP * .2, color=INK, buff=0)
        piv = UP * 2.0 + RIGHT * 3.4
        swing = always_redraw(lambda: VGroup(
            Line(piv, piv + 2.6 * np.array([np.sin(.7 * np.cos(t.get_value())), -np.cos(.7 * np.cos(t.get_value())), 0]), color=MUTE, stroke_width=4),
            Dot(piv + 2.6 * np.array([np.sin(.7 * np.cos(t.get_value())), -np.cos(.7 * np.cos(t.get_value())), 0]), radius=.22, color=ORG)))
        sl = kr("그네: 위치 ↔ 운동 에너지", 26, ORG).move_to(RIGHT * 3.4 + DOWN * 1.4)
        self.play(FadeIn(bc), FadeIn(bl), GrowArrow(arr), FadeIn(swing), FadeIn(sl))
        self.play(t.animate.set_value(4 * PI), run_time=6, rate_func=linear)
        eq = tex(r"LC\,\frac{d^2v_C}{dt^2} + RC\,\frac{dv_C}{dt} + v_C = V", 46, YEL).to_edge(DOWN, buff=.35)
        lb = kr("2차 미분방정식", 28, YEL).next_to(eq, LEFT, .3); VGroup(lb, eq).arrange(RIGHT, buff=.35).to_edge(DOWN, buff=.35)
        self.play(FadeOut(sl), Write(eq), FadeIn(lb), t.animate.set_value(5 * PI), run_time=2)
        self.wait(1.5)


def rlc_circuit(sdom=False):
    """직렬 RLC: 전원 - R - L - C. sdom 이면 소자 이름을 s-영역으로."""
    W, H = 6.0, 2.6; o = LEFT * W / 2 + DOWN * H / 2
    P = lambda x, y: o + RIGHT * x + UP * y
    src = VGroup(Circle(radius=.36, color=INK).move_to(P(0, H / 2)), kr("+", 22).move_to(P(0, H / 2 + .14)), kr("−", 22).move_to(P(0, H / 2 - .16)))
    res = Rectangle(width=1.0, height=.36, color=ORG).move_to(P(1.5, H))
    coil = VGroup(*[Arc(radius=.16, start_angle=PI, angle=-PI, color=BLU).move_to(P(3.0 + .32 * i, H + .08)) for i in range(4)])
    cap = VGroup(Line(P(W - .35, H / 2 + .1), P(W + .35, H / 2 + .1), color=YEL, stroke_width=6),
                 Line(P(W - .35, H / 2 - .1), P(W + .35, H / 2 - .1), color=YEL, stroke_width=6))
    wires = VGroup(Line(P(0, H / 2 + .36), P(0, H)), Line(P(0, H), P(1.0, H)), Line(P(2.0, H), P(2.84, H)), Line(P(4.12, H), P(W, H)),
                   Line(P(W, H), P(W, H / 2 + .1)), Line(P(W, H / 2 - .1), P(W, 0)), Line(P(W, 0), P(0, 0)), Line(P(0, 0), P(0, H / 2 - .36)))
    wires.set_color(MUTE)
    n = (["R", "sL", r"\tfrac{1}{sC}", r"\tfrac{V}{s}"] if sdom else ["R", "L", "C", "V"])
    labs = VGroup(MathTex(n[0], font_size=40, color=ORG).next_to(res, UP, .15), MathTex(n[1], font_size=40, color=BLU).next_to(coil, UP, .15),
                  MathTex(n[2], font_size=40, color=YEL).next_to(cap, RIGHT, .2), MathTex(n[3], font_size=40, color=INK).next_to(src, LEFT, .2))
    return VGroup(wires, src, res, coil, cap), labs


class SDomain(Scene):
    """회로 → s-영역 → 전압 분배 → 분모의 2차식."""
    def construct(self):
        h = head("라플라스로 옮기기")
        c, l = rlc_circuit(False); g = VGroup(c, l).scale(.85).shift(UP * .9)
        self.play(FadeIn(h), Create(c), FadeIn(l), run_time=1.4); self.wait(.6)
        _, l2 = rlc_circuit(True); l2.scale(.85).shift(UP * .9)
        self.play(*[Transform(a, b) for a, b in zip(l, l2)], run_time=1.2); self.wait(.8)
        e1 = tex(r"V_C(s) = \frac{V}{s}\cdot\frac{\tfrac{1}{sC}}{R + sL + \tfrac{1}{sC}}", 50).shift(DOWN * 1.5)
        self.play(Write(e1), run_time=1.6); self.wait(.8)
        e2 = MathTex(r"V_C(s) = \frac{V}{s}\cdot\frac{1/LC}{", r"s^2 + \frac{R}{L}s + \frac{1}{LC}", r"}", font_size=50).move_to(e1)
        self.play(TransformMatchingTex(e1, e2), run_time=1.2)
        b = SurroundingRectangle(e2[1], color=YEL, buff=.1); bl = kr("2차식 → 근만 찾으면 끝", 30, YEL).next_to(b, DOWN, .25)
        self.play(Create(b), FadeIn(bl, shift=UP * .2)); self.wait(2)


class CharEq(Scene):
    """α, ω0 → 특성 방정식 → 극점, 루트 안의 부호."""
    def construct(self):
        h = head("특성 방정식과 두 극점")
        self.play(FadeIn(h))
        d = tex(r"\alpha = \frac{R}{2L}, \qquad \omega_0 = \frac{1}{\sqrt{LC}}", 50).shift(UP * 1.6)
        self.play(Write(d)); self.wait(.5)
        e = tex(r"s^2 + 2\alpha s + \omega_0^2 = 0", 64, YEL).shift(UP * .2)
        self.play(Write(e)); self.wait(.6)
        p = MathTex(r"s_{1,2} = -\alpha \pm", r"\sqrt{\alpha^2 - \omega_0^2}", font_size=64).shift(DOWN * 1.3)
        self.play(Write(p), run_time=1.3)
        b = SurroundingRectangle(p[1], color=RED, buff=.12); bl = kr("이 안의 부호가 모양을 정한다", 30, RED).next_to(b, DOWN, .25)
        la = kr("α: 저항이 에너지를 태우는 빠르기", 24, ORG).to_corner(DL, buff=.5).shift(UP * .1)
        lw = kr("ω₀: L·C가 주고받는 빠르기", 24, BLU).to_corner(DR, buff=.5).shift(UP * .1)
        self.play(FadeIn(la), FadeIn(lw)); self.wait(1.2)
        self.play(Create(b), FadeIn(bl, shift=UP * .2)); self.wait(2)


def case_scene(self, kind, z, title, cond, note, extra=None):
    h = head(title, COL[kind])
    sp, pl = splane(); sp.scale(.85).shift(LEFT * 3.6 + DOWN * .2)
    g, ax = resp_axes(5.4, 2.9, 12); g.shift(RIGHT * 3.0 + DOWN * .2)
    c = VGroup(tex(cond, 46, COL[kind]), kr(note, 32, COL[kind])).arrange(RIGHT, buff=.4).next_to(h, DOWN, .35)
    self.play(FadeIn(h), FadeIn(c), Create(sp), Create(g), run_time=1.2)
    xs = VGroup(*[xmark(pl, q, COL[kind]) for q in poles(z)])
    self.play(LaggedStart(*[GrowFromCenter(x) for x in xs], lag_ratio=.3), run_time=.9)
    cur = ax.plot(lambda t: step(z, t), x_range=[0, 12, .02], color=COL[kind], stroke_width=6)
    self.play(Create(cur), run_time=2.4)
    if extra:
        extra(self, pl, ax)
    self.wait(2)


class Overdamped(Scene):
    def construct(self):
        case_scene(self, "over", 1.4, "과감쇠: 느릿느릿", r"\alpha > \omega_0 \;\Rightarrow", "두 실수 극점")


class Critical(Scene):
    def construct(self):
        def ex(self, pl, ax):
            f = tex(r"R = 2\sqrt{\tfrac{L}{C}}", 52, GRN); n = tex(r"10\,\text{mH},\ 10\,\mu\text{F} \Rightarrow 2\sqrt{1000} \approx 63\,\Omega", 38)
            v = VGroup(f, n).arrange(RIGHT, buff=.6).to_edge(DOWN, buff=.35)
            self.play(Write(f)); self.play(FadeIn(n, shift=UP * .2)); self.wait(1)
        case_scene(self, "crit", 1.0, "임계 감쇠: 가장 빨리", r"\alpha = \omega_0 \;\Rightarrow\; -\alpha", "중근", ex)


class Underdamped(Scene):
    def construct(self):
        def ex(self, pl, ax):
            env = VGroup(ax.plot(lambda t: 1 + np.exp(-.2 * t) / np.sqrt(1 - .04), x_range=[1.8, 12], color=MUTE, stroke_width=2),
                         ax.plot(lambda t: 1 - np.exp(-.2 * t) / np.sqrt(1 - .04), x_range=[1.8, 12], color=MUTE, stroke_width=2))
            f = tex(r"s = -\alpha \pm j\omega_d, \quad \omega_d = \sqrt{\omega_0^2 - \alpha^2}", 42).to_edge(DOWN, buff=.4)
            self.play(Create(env[0].set_stroke(opacity=.6)), Create(env[1].set_stroke(opacity=.6)), Write(f), run_time=1.4)
        case_scene(self, "under", .2, "부족 감쇠: 출렁출렁", r"\alpha < \omega_0 \;\Rightarrow", "켤레 복소 극점", ex)


class PoleSweep(Scene):
    """저항을 줄이면: 실수축의 두 극점이 만나(임계) 원을 따라 갈라진다(부족). 응답이 함께 바뀐다."""
    def construct(self):
        h = head("저항을 줄이면 극점이 움직인다")
        sp, pl = splane(); sp.scale(.85).shift(LEFT * 3.6 + DOWN * .3)
        g, ax = resp_axes(5.4, 2.9, 12); g.shift(RIGHT * 3.0 + DOWN * .3)
        z = ValueTracker(2.4)
        kind = lambda: "over" if z.get_value() > 1.005 else "crit" if z.get_value() > .995 else "under"
        xs = always_redraw(lambda: VGroup(*[xmark(pl, q, COL[kind()]) for q in poles(z.get_value())]))
        cur = always_redraw(lambda: ax.plot(lambda t: step(z.get_value(), t), x_range=[0, 12, .03], color=COL[kind()], stroke_width=6))
        lab = always_redraw(lambda: kr(NAME[kind()], 34, COL[kind()]).next_to(h, DOWN, .3))
        zl = always_redraw(lambda: MathTex(r"\zeta = \alpha/\omega_0 = %.2f" % z.get_value(), font_size=34, color=MUTE).to_edge(DOWN, buff=.35))
        self.play(FadeIn(h), Create(sp), Create(g), FadeIn(xs), FadeIn(cur), FadeIn(lab), FadeIn(zl), run_time=1.2)
        self.wait(1.5)
        self.play(z.animate.set_value(1.0), run_time=4, rate_func=smooth); self.wait(1.5)
        self.play(z.animate.set_value(.3), run_time=3.5, rate_func=smooth); self.wait(1.2)
        self.play(z.animate.set_value(.12), run_time=2.5, rate_func=smooth); self.wait(2)


class Suspension(Scene):
    """질량-스프링-댐퍼 ↔ L-C-R, 방지턱 뒤 출렁임."""
    def construct(self):
        h = head("자동차 서스펜션 = RLC 회로")
        self.play(FadeIn(h))
        y = ValueTracker(0)
        ground = Line(LEFT * 6 + DOWN * 2.6, LEFT * 1.0 + DOWN * 2.6, color=MUTE)
        def body():
            yy = y.get_value(); top = DOWN * .1 + UP * yy + LEFT * 3.5
            m = Rectangle(width=2.2, height=1.0, fill_color=BLU, fill_opacity=.85, color=BLU).move_to(top)
            bot = DOWN * 2.6 + LEFT * 3.5; a, b = bot + LEFT * .55, top + DOWN * .5 + LEFT * .55
            pts = [a + (b - a) * k / 12 + (RIGHT * .22 if k % 2 else LEFT * .22) * (0 < k < 12) for k in range(13)]
            spr = VMobject(color=YEL, stroke_width=5).set_points_as_corners(pts)
            c0, c1 = bot + RIGHT * .55, top + DOWN * .5 + RIGHT * .55; mid = (c0 + c1) / 2
            dmp = VGroup(Line(c0, mid + DOWN * .15, color=ORG, stroke_width=5), Rectangle(width=.42, height=.55, color=ORG).move_to(mid + DOWN * .1),
                         Line(mid + UP * .05, c1, color=ORG, stroke_width=5))
            return VGroup(spr, dmp, m)
        sys_ = always_redraw(body)
        lm = kr("질량", 26, BLU).move_to(LEFT * 3.5 + UP * 1.0); ls = kr("스프링", 24, YEL).move_to(LEFT * 5.4 + DOWN * 1.6); ld = kr("댐퍼", 24, ORG).move_to(LEFT * 1.6 + DOWN * 1.6)
        self.play(Create(ground), FadeIn(sys_), FadeIn(lm), FadeIn(ls), FadeIn(ld))
        rows = VGroup(*[VGroup(kr(a, 30, c), kr("↔", 30, MUTE), kr(b, 30, c)).arrange(RIGHT, buff=.35)
                        for a, b, c in (("질량", "인덕터 L", BLU), ("스프링", "커패시터 C", YEL), ("댐퍼", "저항 R", ORG))]).arrange(DOWN, buff=.5, aligned_edge=LEFT).shift(RIGHT * 3 + UP * .6)
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * .3) for r in rows], lag_ratio=.4), run_time=1.6)
        note = kr("댐퍼 약함 → 출렁 · 너무 셈 → 딱딱", 28, INK).shift(RIGHT * 3 + DOWN * 1.7)
        self.play(FadeIn(note))
        for _ in range(1):
            self.play(y.animate.set_value(.8), run_time=.25)
            self.play(UpdateFromAlphaFunc(y, lambda m, a: m.set_value(.8 * np.exp(-1.2 * a * 4) * np.cos(2 * PI * 2.2 * a))), run_time=4, rate_func=linear)
        self.wait(1.5)


class Summary(Scene):
    """정리: 루트 안 부호 → 이름 → 극점 → 모양, 임계 저항."""
    def construct(self):
        h = head("정리")
        self.play(FadeIn(h))
        rows = [(r"\alpha^2-\omega_0^2 > 0", "과감쇠", "두 실수 극점", "느릿느릿", ORG),
                (r"\alpha^2-\omega_0^2 = 0", "임계 감쇠", "중근", "가장 빨리", GRN),
                (r"\alpha^2-\omega_0^2 < 0", "부족 감쇠", "켤레 복소", "출렁출렁", BLU)]
        tb = VGroup(*[VGroup(tex(a, 40, c), kr(b, 32, c), kr(p, 28), kr(s, 28, MUTE)).arrange(RIGHT, buff=.7) for a, b, p, s, c in rows])
        for r in tb:
            for i, m in enumerate(r):
                m.move_to([[-4.2, -1.0, 1.9, 4.6][i], 0, 0])
        tb.arrange(DOWN, buff=.55).shift(UP * .4)
        for r in tb:
            for i, m in enumerate(r):
                m.set_x([-4.2, -1.0, 1.9, 4.6][i])
        self.play(LaggedStart(*[FadeIn(r, shift=UP * .2) for r in tb], lag_ratio=.35), run_time=2)
        f = card(VGroup(kr("임계 감쇠 저항", 32, YEL), tex(r"R = 2\sqrt{L/C}", 50, YEL)).arrange(RIGHT, buff=.4), color=YEL).to_edge(DOWN, buff=.5)
        self.play(FadeIn(f, shift=UP * .2)); self.wait(2.5)
