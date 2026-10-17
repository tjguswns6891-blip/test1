# 회로 쇼츠 2탄(실효값 · 푸리에 · RC 필터 · 공진) 설명 그래픽. 세로 영상 가운데 칸(1080×840)용.
# 렌더: ~/.venvs/manim/bin/manim -qm -r 1080,840 --fps 30 scenes.py <Scene>
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




def axes(xr, yr, w=9.2, h=4.6, **kw):
    return Axes(x_range=xr, y_range=yr, x_length=w, y_length=h,
                axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False, **kw})


class Rms(Scene):
    """220V 의 정체: 최대 311V 사인파 → 제곱 평균 → 루트 = 220V."""
    def construct(self):
        ax = axes([0, 2, 1], [-360, 360, 100]).shift(DOWN * .3)
        head = kr("우리 집 전압 v(t)", 42).to_edge(UP, buff=.35)
        wave = ax.plot(lambda t: 311 * np.sin(2 * PI * t), x_range=[0, 2], color=VOLT, stroke_width=7)
        self.play(FadeIn(head), Create(ax), run_time=.7); self.play(Create(wave), run_time=1.4)
        pk = DashedLine(ax.c2p(0, 311), ax.c2p(2, 311), color=RED, stroke_width=4)
        pl = kr("최댓값 311V", 36, RED).next_to(ax.c2p(1.25, 311), UP, .1)
        self.play(Create(pk), FadeIn(pl), Flash(ax.c2p(.25, 311), color=RED), run_time=.9); self.wait(.8)
        # 제곱 → 평균
        sq = ax.plot(lambda t: (311 * np.sin(2 * PI * t)) ** 2 / 311, x_range=[0, 2], color=AMP, stroke_width=5)
        area = ax.get_area(sq, x_range=[0, 2], color=AMP, opacity=.25)
        h2 = kr("같은 열을 내는 직류 = 실효값", 40, YEL).to_edge(UP, buff=.35)
        self.play(ReplacementTransform(head, h2), TransformFromCopy(wave, sq), FadeIn(area), run_time=1.2)
        rms = DashedLine(ax.c2p(0, 220), ax.c2p(2, 220), color=YEL, stroke_width=6)
        rl = kr("실효값 220V", 38, YEL).next_to(ax.c2p(1.25, 220), DOWN, .12)
        self.play(FadeOut(sq), FadeOut(area), Create(rms), FadeIn(rl), run_time=1)
        self.wait(.6)
        eq = VGroup(kr("311V ÷ √2", 50, INK), kr("= 220V", 58, YEL)).arrange(RIGHT, buff=.3)
        self.play(FadeIn(card(eq).to_edge(DOWN, buff=.3), shift=UP * .3), run_time=.8)
        self.play(Indicate(eq[1], color=YEL, scale_factor=1.1)); self.wait(2.5)


class Fourier(Scene):
    """구형파 = sin + sin3x/3 + sin5x/5 + … 부분합이 쌓이고, 모서리엔 9% 뿔(깁스)."""
    def construct(self):
        ax = axes([0, 2, 1], [-1.5, 1.5, .5]).shift(DOWN * .4)
        sqw = ax.plot(lambda t: 1 if (t % 1) < .5 else -1, x_range=[0.001, 1.999], color="#5a606c", stroke_width=4,
                      use_smoothing=False, discontinuities=[.5, 1, 1.5])
        head = kr("목표: 네모난 파형", 42).to_edge(UP, buff=.35)
        self.play(FadeIn(head), Create(ax), Create(sqw), run_time=1)
        f = lambda N: (lambda t: 4 / PI * sum(np.sin(2 * PI * n * t) / n for n in range(1, N + 1, 2)))
        part = ax.plot(f(1), x_range=[0, 2], color=VOLT, stroke_width=6)
        tag = kr("sin x", 40, VOLT).to_edge(UP, buff=.35)
        self.play(ReplacementTransform(head, tag), Create(part), run_time=1)
        labels = {3: "+ sin3x / 3", 5: "+ sin5x / 5", 7: "+ sin7x / 7"}
        for N in (3, 5, 7):
            h = ax.plot(lambda t, N=N: 4 / PI * np.sin(2 * PI * N * t) / N, x_range=[0, 2], color=AMP, stroke_width=4)
            t2 = kr(labels[N], 40, AMP).to_edge(UP, buff=.35)
            self.play(Create(h), ReplacementTransform(tag, t2), run_time=.6)
            self.play(Transform(part, ax.plot(f(N), x_range=[0, 2], color=VOLT, stroke_width=6)), FadeOut(h), run_time=.7)
            tag = t2
        t3 = kr("홀수 배만 계속 더하면…", 40, YEL).to_edge(UP, buff=.35)
        self.play(ReplacementTransform(tag, t3), run_time=.4)
        for N in (15, 31, 61):
            self.play(Transform(part, ax.plot(f(N), x_range=[0, 2, .0015], color=VOLT, stroke_width=6)), run_time=.6)
        # 깁스: 모서리 뿔
        pk = ax.c2p(1.006, 1.179)
        ring = Circle(.42, color=RED, stroke_width=6).move_to(pk + RIGHT * .1)
        gl = kr("끝까지 남는 9% 뿔", 38, RED).next_to(ring, UP, .1)
        t4 = kr("푸리에 급수 · 깁스 현상", 40, YEL).to_edge(UP, buff=.35)
        self.play(ReplacementTransform(t3, t4), Create(ring), FadeIn(gl), run_time=.9)
        self.wait(2.5)


class Lowpass(Scene):
    """RC 저역 통과: 회로 → 보드 선도(-3dB @1.59kHz, -20dB/dec) → 섞인 신호에서 고음만 사라짐."""
    def construct(self):
        # 회로
        a, b = np.array([-4.3, 2.3, 0]), np.array([-.2, 2.3, 0])
        circ = VGroup(wire(a, [-3.5, 2.3, 0], color=INK), resistor([-3.5, 2.3, 0], [-1.9, 2.3, 0], AMP),
                      wire([-1.9, 2.3, 0], b, color=INK),
                      wire([-1.2, 2.3, 0], [-1.2, 1.95, 0], color=INK),
                      Line([-1.6, 1.95, 0], [-.8, 1.95, 0], color=VOLT, stroke_width=7), Line([-1.6, 1.75, 0], [-.8, 1.75, 0], color=VOLT, stroke_width=7),
                      wire([-1.2, 1.75, 0], [-1.2, 1.35, 0], color=INK), Line([-1.5, 1.35, 0], [-.9, 1.35, 0], color=INK, stroke_width=5))
        cl = VGroup(kr("1kΩ", 30, AMP).next_to([-2.7, 2.3, 0], UP, .15), kr("100nF", 30, VOLT).next_to([-.8, 1.85, 0], RIGHT, .15),
                    kr("입력", 28, MUTE).next_to(a, LEFT, .1), kr("출력", 28, MUTE).next_to(b, RIGHT, .1))
        self.play(Create(circ), FadeIn(cl), run_time=1.2)
        # 보드 선도 (x: log10 f, 1~5 = 10Hz~100kHz)
        ax = Axes(x_range=[1, 5, 1], y_range=[-45, 5, 10], x_length=8.6, y_length=3.6,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * 1.6)
        fc = 1 / (2 * PI * 1e3 * 100e-9)
        mag = ax.plot(lambda x: -10 * np.log10(1 + (10 ** x / fc) ** 2), x_range=[1, 5], color=GRN, stroke_width=7)
        xl = VGroup(*[kr(t, 24, MUTE).next_to(ax.c2p(x, -45), DOWN, .1) for x, t in ((1, "10Hz"), (2, "100Hz"), (3, "1k"), (4, "10k"), (5, "100k"))])
        self.play(Create(ax), FadeIn(xl), Create(mag), run_time=1.4)
        x0 = np.log10(fc)
        dot = Dot(ax.c2p(x0, -3), .12, color=YEL)
        fl = kr("−3dB · 1.59kHz", 32, YEL).next_to(dot, UP + RIGHT, .1)
        self.play(GrowFromCenter(dot), FadeIn(fl), Flash(dot, color=YEL), run_time=.8); self.wait(.6)
        slope = VGroup(Arrow(ax.c2p(4, -20), ax.c2p(5, -40), buff=0, color=RED, stroke_width=6),
                       kr("10배마다 −20dB", 32, RED).next_to(ax.c2p(3.55, -32), LEFT, .1))
        self.play(GrowArrow(slope[0]), FadeIn(slope[1]), run_time=.8); self.wait(.6)
        # 섞인 신호 → 출력
        self.play(FadeOut(VGroup(ax, mag, xl, dot, fl, slope)), run_time=.5)
        ax2 = axes([0, 2, 1], [-2, 2, 1], h=3.2).shift(DOWN * 1.6)
        mix = ax2.plot(lambda t: np.sin(2 * PI * t) + .6 * np.sin(2 * PI * 12 * t), x_range=[0, 2], color=MUTE, stroke_width=4)
        out = ax2.plot(lambda t: .99 * np.sin(2 * PI * t - .06) + .6 * .13 * np.sin(2 * PI * 12 * t - 1.4), x_range=[0, 2], color=GRN, stroke_width=7)
        t1 = kr("낮은 소리 + 높은 소리", 34, MUTE).next_to(ax2, UP, .1)
        t2 = kr("→ 높은 소리만 사라짐", 34, GRN).next_to(ax2, UP, .1)
        self.play(Create(ax2), Create(mix), FadeIn(t1), run_time=1)
        self.play(Transform(mix, out), ReplacementTransform(t1, t2), run_time=1.4)
        self.wait(2.5)


class Resonance(Scene):
    """XL·XC 곡선이 650Hz 에서 교차 → 둘이 상쇄 → 전압 페이저: VL 61V, VC 61V, VR 10V."""
    def construct(self):
        L, C, R = .03, 2e-6, 20
        ax = Axes(x_range=[100, 1400, 200], y_range=[0, 400, 100], x_length=8.8, y_length=4.4,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .3)
        xl = ax.plot(lambda f: 2 * PI * f * L, x_range=[100, 1400], color=AMP, stroke_width=6)
        xc = ax.plot(lambda f: min(400, 1 / (2 * PI * f * C)), x_range=[200, 1400], color=VOLT, stroke_width=6)
        lab = VGroup(kr("코일 XL", 32, AMP).next_to(ax.c2p(1300, 245), UP, .1), kr("커패시터 XC", 32, VOLT).next_to(ax.c2p(330, 240), RIGHT, .1))
        head = kr("주파수에 따른 리액턴스", 40).to_edge(UP, buff=.35)
        self.play(FadeIn(head), Create(ax), run_time=.6)
        self.play(Create(xl), Create(xc), FadeIn(lab), run_time=1.4)
        f0 = 1 / (2 * PI * np.sqrt(L * C))
        p = ax.c2p(f0, 2 * PI * f0 * L)
        dot = Dot(p, .14, color=YEL); vl = DashedLine(ax.c2p(f0, 0), p, color=YEL)
        fl = kr("650Hz: XL = XC = 122Ω", 34, YEL).next_to(p, UP, .25)
        h2 = kr("공진: 둘이 서로 상쇄", 40, YEL).to_edge(UP, buff=.35)
        self.play(GrowFromCenter(dot), Create(vl), FadeIn(fl), ReplacementTransform(head, h2), Flash(dot, color=YEL), run_time=1)
        self.wait(1)
        self.play(FadeOut(VGroup(ax, xl, xc, lab, dot, vl, fl)), run_time=.5)
        # 전압 페이저 (1단위 = 10V 를 0.36 칸으로)
        s = .03; o = np.array([-2.2, -1.25, 0])
        vr = Arrow(o, o + RIGHT * 10 * s * 6, buff=0, color=GRN, stroke_width=8)
        vL = Arrow(o + RIGHT * 10 * s * 6, o + RIGHT * 10 * s * 6 + UP * 61 * s * 2, buff=0, color=AMP, stroke_width=8)
        off = RIGHT * .45                                # 코일 화살표와 겹치지 않게 옆으로
        vC = Arrow(o + RIGHT * 10 * s * 6 + UP * 61 * s * 2 + off, o + RIGHT * 10 * s * 6 + off, buff=0, color=VOLT, stroke_width=8)
        tr = VGroup(kr("저항 10V = 전원", 32, GRN).next_to(vr, DOWN, .15),
                    kr("코일 61V ↑", 40, AMP).next_to(vL, LEFT, .25).shift(UP * .4),
                    kr("↓ 커패시터 61V", 34, VOLT).next_to(vC, RIGHT, .2).shift(UP * .4))
        h3 = kr("10V 넣었는데 코일엔 61V", 40, AMP).to_edge(UP, buff=.35)
        self.play(ReplacementTransform(h2, h3), GrowArrow(vr), FadeIn(tr[0]), run_time=.8)
        self.play(GrowArrow(vL), FadeIn(tr[1]), run_time=.8)
        self.play(GrowArrow(vC), FadeIn(tr[2]), run_time=.8)
        eq = VGroup(kr("I = 10V ÷ 20Ω = 0.5A", 36, INK), kr("VL = 0.5A × 122Ω = 61V", 40, YEL)).arrange(DOWN, buff=.15)
        self.play(FadeIn(card(eq).to_edge(DOWN, buff=.25), shift=UP * .3), run_time=.8)
        self.wait(2.5)
