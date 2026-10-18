# 회로 쇼츠 4편(노턴 · 중첩 · 과도응답 · 연산증폭기) 설명 그래픽. 세로 영상 가운데 칸(1080×840)용.
# 렌더: ~/.venvs/manim/bin/manim -r 1080,840 --fps 30 scenes.py <Scene>
from manim import *
import numpy as np

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
VOLT, AMP, GRN, PUR, RED = "#7aa2ff", "#ff9f43", "#3ddc97", "#c792ff", "#ff6b9a"
KR = "Noto Sans CJK KR"
config.background_color = BG
config.frame_height = 8.0
config.frame_width = 8.0 * 1080 / 840


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def resistor(a, b, color=INK, n=6, amp=.16):
    """a→b 직선 위에 지그재그 저항."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a; L = np.linalg.norm(d); u = d / L; nrm = np.array([-u[1], u[0], 0])
    pts = [a]
    for k in range(1, 2 * n):
        pts.append(a + u * L * k / (2 * n) + nrm * amp * (1 if k % 2 else -1))
    pts.append(b)
    return VMobject(color=color, stroke_width=6).set_points_as_corners(pts)


def vsource(c, r=.42, color=INK):
    g = VGroup(Circle(r, color=color, stroke_width=6).move_to(c),
               kr("+", 30, color).move_to(c + UP * .18), kr("−", 30, color).move_to(c + DOWN * .2))
    return g


def isource(c, r=.42, color=AMP):
    return VGroup(Circle(r, color=color, stroke_width=6).move_to(c),
                  Arrow(c + DOWN * .26, c + UP * .3, buff=0, color=color, stroke_width=6, max_tip_length_to_length_ratio=.35))


def wire(*pts, color=VOLT):
    return VMobject(color=color, stroke_width=6).set_points_as_corners([np.array(p, float) for p in pts])


class Norton(Scene):
    """테브난(전압원 + 직렬 저항) → 노턴(전류원 ‖ 같은 저항), I_N = 9V / 75Ω = 120 mA."""
    def construct(self):
        top, bot, L, R = 1.4, -1.6, -3.8, 3.8
        a, b = np.array([R, top, 0]), np.array([R, bot, 0])
        term = VGroup(Dot(a, .1, color=INK), Dot(b, .1, color=INK), kr("a", 28, MUTE).next_to(a, RIGHT, .15), kr("b", 28, MUTE).next_to(b, RIGHT, .15))
        # 테브난
        vs = vsource([L, (top + bot) / 2, 0], color=YEL)
        th = VGroup(wire([L, (top + bot) / 2 + .42, 0], [L, top, 0], [-1.6, top, 0]), resistor([-1.6, top, 0], [.4, top, 0], YEL),
                    wire([.4, top, 0], a), wire([L, (top + bot) / 2 - .42, 0], [L, bot, 0], b), vs)
        thl = VGroup(kr("V_Th 9V", 34, YEL).next_to(vs, LEFT, .2), kr("R_Th 75Ω", 34, YEL).move_to([-.6, top + .55, 0]))
        head = kr("테브난 등가", 44, INK).to_edge(UP, buff=.5)
        self.play(FadeIn(head), Create(th), FadeIn(thl), FadeIn(term), run_time=1.6)
        self.wait(.8)
        # 노턴
        is_ = isource([L + 1.2, (top + bot) / 2, 0])
        no = VGroup(wire([L + 1.2, (top + bot) / 2 + .42, 0], [L + 1.2, top, 0], a), wire([L + 1.2, (top + bot) / 2 - .42, 0], [L + 1.2, bot, 0], b),
                    wire([.9, top, 0], [.9, .45, 0]), resistor([.9, .45, 0], [.9, -.65, 0], AMP), wire([.9, -.65, 0], [.9, bot, 0]), is_)
        nol = VGroup(kr("I_N", 34, AMP).next_to(is_, LEFT, .2), kr("R_N 75Ω", 34, AMP).next_to([.9, -.1, 0], RIGHT, .25))
        head2 = kr("노턴 등가", 44, AMP).to_edge(UP, buff=.5)
        self.play(FadeOut(th), FadeOut(thl), ReplacementTransform(head, head2), run_time=.7)
        self.play(Create(no), FadeIn(nol), run_time=1.4)
        eq = VGroup(kr("I_N = V_Th ÷ R_Th", 40, INK), kr("= 9V ÷ 75Ω = 120 mA", 46, YEL)).arrange(DOWN, buff=.25)
        self.play(FadeIn(card(eq).to_edge(DOWN, buff=.35), shift=UP * .3), run_time=.8)
        self.play(Indicate(eq[1], color=YEL, scale_factor=1.08))
        self.wait(2.5)


class Superpose(Scene):
    """가운데 저항 전류: 12V만 25.7 mA + 5V만 7.1 mA = 함께 32.9 mA (막대가 쌓인다)."""
    def construct(self):
        head = kr("가운데 저항 R₃ 의 전류", 42).to_edge(UP, buff=.5)
        self.play(FadeIn(head))
        unit = 4.0 / 32.9                      # mA → 화면 높이
        base = -2.2
        def bar(x, v, c, y0=base):
            return Rectangle(width=1.5, height=v * unit, fill_color=c, fill_opacity=.9, stroke_width=0).move_to([x, y0 + v * unit / 2, 0])
        b1 = bar(-3.0, 25.7, VOLT); b2 = bar(0.0, 7.14, GRN)
        l1 = VGroup(kr("12V만", 34, VOLT), kr("25.7 mA", 40, INK)).arrange(DOWN, buff=.1).next_to(b1, UP, .2)
        l2 = VGroup(kr("5V만", 34, GRN), kr("7.1 mA", 40, INK)).arrange(DOWN, buff=.1).next_to(b2, UP, .2)
        axis = Line([-4.4, base, 0], [4.4, base, 0], color="#4d5a73", stroke_width=4)
        self.add(axis)
        self.play(GrowFromEdge(b1, DOWN), FadeIn(l1), run_time=1.0)
        self.wait(1.2)
        self.play(GrowFromEdge(b2, DOWN), FadeIn(l2), run_time=.9)
        self.wait(1.0)
        plus = kr("+", 80, YEL).move_to([1.6, 0, 0])
        s1, s2 = b1.copy(), b2.copy()
        self.play(FadeIn(plus), s1.animate.move_to([3.2, base + 25.7 * unit / 2, 0]), run_time=.8)
        self.play(s2.animate.move_to([3.2, base + 25.7 * unit + 7.14 * unit / 2, 0]), run_time=.8)
        tot = card(VGroup(kr("= 32.9 mA", 50, YEL), kr("두 전원을 함께 켰을 때와 같아요", 30, MUTE)).arrange(DOWN, buff=.12), YEL, .2).to_edge(DOWN, buff=.25)
        self.play(FadeIn(tot, shift=UP * .2), Flash(s2.get_top(), color=YEL, num_lines=14))
        self.wait(2.5)


class Transient(Scene):
    """v_C(t) = Vs(1 − e^(−t/τ)), 1τ → 63.2%, 5τ → 99.3%."""
    def construct(self):
        ax = Axes(x_range=[0, 5.2, 1], y_range=[0, 105, 25], x_length=8.0, y_length=5.0, tips=False,
                  axis_config={"stroke_color": "#4d5a73"}).shift(DOWN * .4 + RIGHT * .45)
        xl = VGroup(*[kr(f"{k}τ" if k else "0", 28, MUTE, NORMAL).next_to(ax.c2p(k, 0), DOWN) for k in range(6)])
        yl = VGroup(*[kr(f"{v}%", 26, MUTE, NORMAL).next_to(ax.c2p(0, v), LEFT) for v in (50, 100)])
        head = kr("커패시터 전압 v_C(t)", 42).to_edge(UP, buff=.45)
        self.play(FadeIn(head), Create(ax), FadeIn(xl), FadeIn(yl), run_time=1)
        f = lambda t: 100 * (1 - np.exp(-t))
        t = ValueTracker(0)
        curve = always_redraw(lambda: ax.plot(f, x_range=[0, max(1e-3, t.get_value())], color=VOLT, stroke_width=8))
        dot = always_redraw(lambda: Dot(ax.c2p(t.get_value(), f(t.get_value())), .13, color=YEL))
        self.add(curve, dot)
        self.play(t.animate.set_value(1), run_time=1.6, rate_func=linear)
        m1 = VGroup(DashedLine(ax.c2p(1, 0), ax.c2p(1, 63.2), color=YEL), DashedLine(ax.c2p(0, 63.2), ax.c2p(1, 63.2), color=YEL))
        t1 = card(kr("1τ → 63.2%", 40, YEL), YEL, .18).next_to(ax.c2p(1, 63.2), RIGHT, .3).shift(DOWN * .6)
        self.play(Create(m1), FadeIn(t1), run_time=.7)
        self.wait(.8)
        self.play(t.animate.set_value(5), run_time=2.6, rate_func=linear)
        m5 = DashedLine(ax.c2p(5, 0), ax.c2p(5, 99.3), color=GRN)
        t5 = card(kr("5τ → 99.3%", 40, GRN), GRN, .18).next_to(ax.c2p(5, 99.3), DOWN, .25).shift(LEFT * 1.6)
        self.play(Create(m5), FadeIn(t5), run_time=.7)
        tau = card(kr("τ = RC = 1kΩ × 100μF = 0.1초", 34, INK)).to_edge(DOWN, buff=.15)
        self.play(FadeIn(tau, shift=UP * .2))
        self.wait(2.5)


class Opamp(Scene):
    """이상 연산증폭기 두 규칙 → 반전 증폭기 이득 −Rf/R1 = −4.7, 입력·출력 파형."""
    def construct(self):
        c = np.array([.4, 1.2, 0])
        tri = Polygon(c + [-1.1, 1.0, 0], c + [-1.1, -1.0, 0], c + [1.2, 0, 0], color=INK, stroke_width=6)
        minus, plus = c + [-1.1, .5, 0], c + [-1.1, -.5, 0]
        sg = VGroup(kr("−", 40).move_to(minus + RIGHT * .3), kr("+", 40).move_to(plus + RIGHT * .3))
        out = c + [1.2, 0, 0]
        ckt = VGroup(wire([-4.2, minus[1], 0], [-3.2, minus[1], 0]), resistor([-3.2, minus[1], 0], [-1.8, minus[1], 0], VOLT), wire([-1.8, minus[1], 0], minus),
                     wire([-1.5, minus[1], 0], [-1.5, 3.0, 0], [-.3, 3.0, 0]), resistor([-.3, 3.0, 0], [1.3, 3.0, 0], AMP), wire([1.3, 3.0, 0], [2.4, 3.0, 0], [2.4, out[1], 0]),
                     wire(out, [3.6, out[1], 0]), wire(plus, [-1.5, plus[1], 0], [-1.5, plus[1] - .5, 0]))
        gnd = VGroup(*[Line([-1.5 - w, plus[1] - .5 - k * .14, 0], [-1.5 + w, plus[1] - .5 - k * .14, 0], color=VOLT, stroke_width=5) for k, w in enumerate((.3, .2, .1))])
        lab = VGroup(kr("R1 10kΩ", 30, VOLT).next_to([-2.5, minus[1], 0], DOWN, .25), kr("Rf 47kΩ", 30, AMP).next_to([.5, 3.0, 0], UP, .2),
                     kr("vin", 30, MUTE).next_to([-4.2, minus[1], 0], UP, .1), kr("vout", 30, MUTE).next_to([3.6, out[1], 0], UP, .1))
        self.play(Create(tri), FadeIn(sg), Create(ckt), FadeIn(gnd), FadeIn(lab), run_time=1.6)
        r1 = card(kr("① v+ = v−", 40, YEL), YEL, .15).move_to([-2.0, -1.0, 0])
        r2 = card(kr("② 입력 전류 = 0", 40, YEL), YEL, .15).move_to([2.0, -1.0, 0])
        self.play(FadeIn(r1, shift=UP * .2), Indicate(sg, color=YEL), run_time=.9)
        self.play(FadeIn(r2, shift=UP * .2), run_time=.8)
        self.wait(1.4)
        gain = card(kr("이득 = −Rf ÷ R1 = −4.7", 44, YEL), YEL, .18).move_to([0, -1.0, 0])
        self.play(FadeOut(r1), FadeOut(r2), FadeIn(gain), run_time=.8)
        ax = Axes(x_range=[0, 4 * PI, PI], y_range=[-5, 5, 5], x_length=9.0, y_length=1.9, tips=False,
                  axis_config={"stroke_color": "#4d5a73"}).move_to([0, -3.0, 0])
        vin = ax.plot(lambda x: np.sin(x), color=VOLT, stroke_width=5)
        vout = ax.plot(lambda x: -4.7 * np.sin(x), color=AMP, stroke_width=6)
        lg = VGroup(kr("입력 1V", 26, VOLT), kr("출력 4.7V (뒤집힘)", 26, AMP)).arrange(RIGHT, buff=.5).next_to(ax, UP, .05).align_to(ax, RIGHT)
        self.play(Create(ax), Create(vin), FadeIn(lg[0]), run_time=1.0)
        self.play(Create(vout), FadeIn(lg[1]), run_time=1.4)
        self.wait(2.5)
