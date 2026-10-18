# 회로이론 16장 푸리에 급수 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
from manim import *
import numpy as np

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
TexTemplateLibrary.default.add_to_preamble(r"\usepackage{amsmath}")


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def tex(s, size=56, color=INK):
    return MathTex(s, font_size=size, color=color)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)



def sq(x):
    return np.where(np.mod(x, TAU) < PI, 1.0, -1.0)


def sq_line(ax, x0, x1, color, sw=4, opacity=1.0):
    """구형파(주기 2π, 처음 반 주기 +1)를 꺾은선으로: 모서리가 수직으로 정확히 그려진다."""
    pts, x = [], x0
    while x < x1 - 1e-9:
        y = 1.0 if np.mod(x + 1e-9, TAU) < PI else -1.0
        nx = min(x1, (np.floor((x + 1e-9) / PI) + 1) * PI)
        pts += [ax.c2p(x, y), ax.c2p(nx, y)]; x = nx
    return VMobject(color=color, stroke_width=sw, stroke_opacity=opacity).set_points_as_corners(pts)


def coef(kind, n):
    """sin(n x) 계수: 구형파 4/(nπ) 홀수, 삼각파 ±8/(π²n²) 홀수, 톱니파 2(−1)^(n+1)/(nπ)."""
    if kind == "sq":
        return 4 / (n * PI) if n % 2 else 0.0
    if kind == "tri":
        return (8 / (PI * PI * n * n)) * (-1 if (n - 1) // 2 % 2 else 1) if n % 2 else 0.0
    return 2 / PI * (1 if n % 2 else -1) / n


def partial(kind, N):
    return lambda x: sum(coef(kind, n) * np.sin(n * x) for n in range(1, N + 1))


def wave_axes(w=10, h=3.6, X=2 * TAU, Y=1.5):
    ax = Axes(x_range=[0, X, PI], y_range=[-Y, Y, 1], x_length=w, y_length=h,
              axis_config={"stroke_color": MUTE, "include_ticks": False})
    return ax


def bars(kind, N, n_max=25, w=8, h=1.6, col=BLU, gain=None):
    """|bₙ| 막대 (1 … n_max), N 까지 색칠."""
    g = VGroup(); bw = w / n_max; m = abs(coef(kind, 1))
    for n in range(1, n_max + 1):
        b = abs(coef(kind, n)) * (gain(n) if gain else 1)
        if b < 1e-9:
            continue
        r = Rectangle(width=bw * .7, height=max(.02, h * b / m), stroke_width=0, fill_color=col if n <= N else "#2a2e37", fill_opacity=1)
        r.move_to([(n - .5) * bw - w / 2, 0, 0], aligned_edge=DOWN); g.add(r)
    base = Line([-w / 2, 0, 0], [w / 2, 0, 0], color=MUTE, stroke_width=2)
    return VGroup(base, g)


class Hook(Scene):
    """사인파만 더했는데 네모가 된다."""
    def construct(self):
        h = head("사인파만 더했는데, 네모?")
        ax = wave_axes(11, 4.2).shift(DOWN * .3)
        tgt = sq_line(ax, 0, 2 * TAU, MUTE, 3, .5)
        self.play(FadeIn(h), Create(ax), Create(tgt), run_time=1.0)
        N = ValueTracker(1)
        cur = always_redraw(lambda: ax.plot(partial("sq", int(N.get_value())), x_range=[0, 2 * TAU, .01], color=BLU, stroke_width=5))
        lab = always_redraw(lambda: MathTex(r"N = %d" % int(N.get_value()), font_size=40, color=YEL).to_corner(DR, buff=.5))
        self.play(Create(cur), FadeIn(lab), run_time=1.2)
        for n in (3, 5, 7, 9, 15, 25, 49):
            self.play(N.animate.set_value(n), run_time=.7, rate_func=lambda t: 1 if t > .5 else 0)
            self.wait(.25)
        self.wait(1.5)


class PhasorLimit(Scene):
    """페이저는 사인파 하나만 → 쪼개서 따로 풀고 더하기."""
    def construct(self):
        h = head("페이저는 사인파 하나만")
        a1 = wave_axes(4.2, 1.6, TAU, 1.3).shift(LEFT * 3.5 + UP * 1.0)
        s1 = a1.plot(np.sin, x_range=[0, TAU, .02], color=GRN, stroke_width=5)
        ok = kr("페이저 OK", 30, GRN).next_to(a1, DOWN, .2)
        a2 = wave_axes(4.2, 1.6, TAU, 1.3).shift(RIGHT * 3.5 + UP * 1.0)
        s2 = sq_line(a2, 0, TAU, RED, 5)
        no = kr("페이저 ✗", 30, RED).next_to(a2, DOWN, .2)
        self.play(FadeIn(h), Create(a1), Create(s1), FadeIn(ok), run_time=1.2)
        self.play(Create(a2), Create(s2), FadeIn(no), run_time=1.2); self.wait(.6)
        row = VGroup()
        for n, c in ((1, BLU), (3, ORG), (5, PUR)):
            a = wave_axes(2.6, 1.0, TAU, 1.3); w = a.plot(lambda x, n=n: coef("sq", n) * np.sin(n * x), x_range=[0, TAU, .01], color=c, stroke_width=4)
            row.add(VGroup(a, w))
        plus = [MathTex("+", font_size=48, color=MUTE) for _ in range(2)]
        seq = VGroup(row[0], plus[0], row[1], plus[1], row[2], MathTex(r"+\cdots", font_size=48, color=MUTE)).arrange(RIGHT, buff=.25).shift(DOWN * 1.7)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * .2) for m in seq], lag_ratio=.2), run_time=1.6)
        t = kr("사인파마다 페이저 → 다 더하기 (중첩)", 30, YEL).to_edge(DOWN, buff=.3)
        self.play(FadeIn(t)); self.wait(2)


class Series(Scene):
    """f(t) = 평균값 + 기본파 + 고조파, ω₀ = 2π/T, 계수 aₙ bₙ."""
    def construct(self):
        h = head("푸리에 급수")
        f = MathTex(r"f(t) =", r"a_0", r"+", r"\sum_{n=1}^{\infty}\left(a_n\cos n\omega_0 t + b_n\sin n\omega_0 t\right)", font_size=56).shift(UP * 1.3)
        self.play(FadeIn(h), Write(f), run_time=1.8)
        b0 = Brace(f[1], DOWN, color=GRN); t0 = kr("평균값", 26, GRN).next_to(b0, DOWN, .1)
        b1 = Brace(f[3], DOWN, color=BLU); t1 = kr("기본파(n=1) + 고조파(n=2, 3, 4 …)", 26, BLU).next_to(b1, DOWN, .1)
        self.play(GrowFromCenter(b0), FadeIn(t0), GrowFromCenter(b1), FadeIn(t1)); self.wait(.8)
        w0 = tex(r"\omega_0 = \frac{2\pi}{T}", 48, YEL).shift(DOWN * 1.2 + LEFT * 3.6)
        sp = bars("saw", 12, 12, 5.4, 1.5, BLU).shift(DOWN * 2.6 + RIGHT * 2.4)
        sl = kr("계수 aₙ, bₙ = 고조파마다 섞인 양", 24, MUTE).next_to(sp, UP, .15)
        nl = VGroup(*[MathTex(str(n), font_size=22, color=MUTE).move_to(sp[0].get_left() + RIGHT * (n - .5) * 5.4 / 12 + DOWN * .25) for n in (1, 2, 3, 4)])
        self.play(Write(w0), FadeIn(sp), FadeIn(sl), FadeIn(nl), run_time=1.4); self.wait(2)


class Orthogonality(Scene):
    """곱해서 평균: 같은 주파수만 남는다."""
    def construct(self):
        h = head("계수 구하기: 곱해서 평균")
        self.play(FadeIn(h))
        def panel(n, y, col):
            ax = wave_axes(7.0, 1.7, TAU, 1.4).shift(UP * y + LEFT * 1.2)
            prod = lambda x: sq(x) * np.sin(n * x)
            area = ax.get_area(ax.plot(prod, x_range=[0, TAU, .005], use_smoothing=False), x_range=[0, TAU], color=col, opacity=.35)
            cur = ax.plot(prod, x_range=[0, TAU, .005], color=col, stroke_width=4, use_smoothing=False)
            lab = MathTex(r"f(t)\cdot\sin %s\omega_0 t" % ("" if n == 1 else str(n)), font_size=34, color=col).next_to(ax, UP, .1).align_to(ax, LEFT)
            avg = np.mean(prod(np.linspace(0, TAU, 4000)))
            res = VGroup(kr("평균", 26, MUTE), MathTex(r"%.2f" % avg if abs(avg) > 1e-3 else "0", font_size=44, color=col)).arrange(RIGHT, buff=.2).next_to(ax, RIGHT, .4)
            return ax, area, cur, lab, res
        for n, y, col in ((1, 1.0, GRN), (2, -1.6, RED)):
            ax, area, cur, lab, res = panel(n, y, col)
            self.play(Create(ax), FadeIn(lab), Create(cur), run_time=1.2)
            self.play(FadeIn(area), FadeIn(res, shift=LEFT * .2)); self.wait(.6)
        t = kr("다른 주파수끼리 곱하면 평균 0 → 직교성", 30, YEL).to_edge(DOWN, buff=.3)
        self.play(FadeIn(t)); self.wait(2)


class SquareBuild(Scene):
    """구형파: 1 + 1/3 + 1/5 … 홀수 차수만, 크기 1/n."""
    def construct(self):
        h = head("구형파 = 홀수 차수, 크기 1/n")
        ax = wave_axes(10, 2.6).shift(UP * 1.25)
        tgt = sq_line(ax, 0, 2 * TAU, MUTE, 3, .5)
        self.play(FadeIn(h), Create(ax), Create(tgt))
        N = ValueTracker(1)
        cur = always_redraw(lambda: ax.plot(partial("sq", int(N.get_value())), x_range=[0, 2 * TAU, .01], color=BLU, stroke_width=5))
        sp = always_redraw(lambda: bars("sq", int(N.get_value()), 15, 6, 1.1).shift(DOWN * 3.0))
        terms = [r"\sin t", r"+\tfrac{1}{3}\sin 3t", r"+\tfrac{1}{5}\sin 5t", r"+\tfrac{1}{7}\sin 7t", r"+\cdots"]
        eq = MathTex(r"\tfrac{4}{\pi}\Big(", *terms, r"\Big)", font_size=40).to_edge(DOWN, buff=.15).shift(UP * .05)
        eq.move_to(DOWN * .95)
        self.play(Create(cur), FadeIn(sp), FadeIn(eq[0]), FadeIn(eq[1]), FadeIn(eq[-1]))
        for i, n in enumerate((3, 5, 7)):
            self.play(N.animate.set_value(n), FadeIn(eq[i + 2], shift=LEFT * .2), run_time=.9, rate_func=lambda t: 1 if t > .5 else 0); self.wait(.8)
        self.play(N.animate.set_value(15), FadeIn(eq[5]), run_time=1.2, rate_func=linear); self.wait(2)


class Gibbs(Scene):
    """N 을 늘려도 모서리 약 9% 뿔은 그대로."""
    def construct(self):
        h = head("깁스 현상: 9%가 남는다")
        ax = Axes(x_range=[0, 1.2, .2], y_range=[0, 1.35, .25], x_length=9, y_length=4.6, axis_config={"stroke_color": MUTE, "include_ticks": False}).shift(DOWN * .4)
        one = DashedLine(ax.c2p(0, 1), ax.c2p(1.2, 1), color=MUTE)
        top = DashedLine(ax.c2p(0, 1.0895), ax.c2p(1.2, 1.0895), color=RED)
        tl = kr("약 9%", 32, RED).next_to(ax.c2p(1.2, 1.0895), RIGHT, .1)
        self.play(FadeIn(h), Create(ax), Create(one))
        prev = None
        for N, c in ((9, ORG), (25, PUR), (49, BLU), (99, GRN)):
            cur = ax.plot(partial("sq", N), x_range=[0.001, 1.2, .002], color=c, stroke_width=4)
            l = MathTex(r"N=%d" % N, font_size=34, color=c).move_to(ax.c2p(.95, .55 - .1 * [9, 25, 49, 99].index(N)))
            self.play(Create(cur), FadeIn(l), run_time=1.0); self.wait(.3)
        self.play(Create(top), FadeIn(tl)); self.wait(1)
        n = kr("좁아질 뿐, 높이는 그대로", 30, YEL).to_edge(DOWN, buff=.3)
        self.play(FadeIn(n)); self.wait(2)


class TriSaw(Scene):
    """삼각파 1/n² (금방 수렴) vs 톱니파 1/n (모든 차수)."""
    def construct(self):
        h = head("매끈할수록 고조파가 빨리 사라진다")
        self.play(FadeIn(h))
        for kind, x, col, name, rule in (("tri", -3.5, GRN, "삼각파", r"1/n^2"), ("saw", 3.5, ORG, "톱니파", r"1/n")):
            ax = wave_axes(5.4, 2.4, 2 * TAU, 1.4).shift(RIGHT * x + UP * .7)
            cur = ax.plot(partial(kind, 5 if kind == "tri" else 15), x_range=[0, 2 * TAU, .01], color=col, stroke_width=4)
            t = VGroup(kr(name, 32, col), tex(rule, 40, col)).arrange(RIGHT, buff=.3).next_to(ax, UP, .2)
            sp = bars(kind, 15, 15, 4.6, 1.2, col).next_to(ax, DOWN, .55)
            self.play(Create(ax), FadeIn(t), Create(cur), FadeIn(sp), run_time=1.4)
        self.wait(2.5)


class Symmetry(Scene):
    """짝함수 → 코사인만, 홀함수 → 사인만, 반파 대칭 → 홀수 차수만."""
    def construct(self):
        h = head("대칭부터 보세요")
        self.play(FadeIn(h))
        items = [(lambda x: np.cos(x) + .3 * np.cos(3 * x), "짝함수 (y축 대칭)", "코사인 항만", BLU),
                 (lambda x: np.sin(x) + .3 * np.sin(2 * x), "홀함수 (원점 대칭)", "사인 항만", GRN),
                 (lambda x: sq(x), "반파 대칭", "홀수 차수만", ORG)]
        g = VGroup()
        for f, a, b, c in items:
            ax = Axes(x_range=[-PI, PI, PI], y_range=[-1.5, 1.5, 1], x_length=3.6, y_length=2.0, axis_config={"stroke_color": MUTE, "include_ticks": False})
            cur = sq_line(ax, -PI, PI, c, 4) if b == "홀수 차수만" else ax.plot(f, x_range=[-PI, PI, .005], color=c, stroke_width=4)
            g.add(VGroup(kr(a, 26, c), VGroup(ax, cur), kr("→ " + b, 30, c)).arrange(DOWN, buff=.3))
        g.arrange(RIGHT, buff=.6).shift(DOWN * .2)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * .2) for m in g], lag_ratio=.4), run_time=2.4); self.wait(2.5)


class RCFilter(Scene):
    """구형파 → RC 저역통과 → 고조파마다 깎임 → 모서리가 둥근 파형."""
    def construct(self):
        h = head("구형파를 RC 필터에 넣으면")
        wc = 3.0
        H = lambda n: 1 / np.sqrt(1 + (n / wc) ** 2)
        ph = lambda n: -np.arctan(n / wc)
        a1 = wave_axes(4.4, 1.8, 2 * TAU, 1.4).shift(LEFT * 4.1 + UP * 1.0)
        a2 = wave_axes(4.4, 1.8, 2 * TAU, 1.4).shift(RIGHT * 4.1 + UP * 1.0)
        box = card(VGroup(kr("RC", 36, YEL), kr("저역통과", 24, MUTE)).arrange(DOWN, buff=.1), color=YEL).move_to(UP * 1.0)
        inn = sq_line(a1, 0, 2 * TAU, BLU, 4)
        out = a2.plot(lambda x: sum(coef("sq", n) * H(n) * np.sin(n * x + ph(n)) for n in range(1, 80, 2)), x_range=[0, 2 * TAU, .01], color=GRN, stroke_width=4)
        ar1 = Arrow(a1.get_right(), box.get_left(), buff=.15, color=MUTE); ar2 = Arrow(box.get_right(), a2.get_left(), buff=.15, color=MUTE)
        self.play(FadeIn(h), Create(a1), Create(inn), FadeIn(box), GrowArrow(ar1), run_time=1.4)
        s1 = bars("sq", 15, 15, 4.4, 1.3, BLU).shift(LEFT * 4.1 + DOWN * 2.0); l1 = kr("입력 고조파", 24, BLU).next_to(s1, DOWN, .15)
        s2 = bars("sq", 15, 15, 4.4, 1.3, GRN, gain=H).shift(RIGHT * 4.1 + DOWN * 2.0); s2.align_to(s1, DOWN); l2 = kr("높은 차수일수록 깎임", 24, GRN).next_to(s2, DOWN, .15)
        self.play(FadeIn(s1), FadeIn(l1)); self.wait(.5)
        self.play(TransformFromCopy(s1, s2), FadeIn(l2), run_time=1.4)
        self.play(GrowArrow(ar2), Create(a2), Create(out), run_time=1.4)
        t = kr("모서리가 둥글어진다", 30, YEL).next_to(a2, UP, .2)
        self.play(FadeIn(t)); self.wait(2)


class Timbre(Scene):
    """같은 440 Hz, 고조파 비율이 달라서 소리가 다르다 (예시 비율)."""
    def construct(self):
        h = head("같은 '라' 440 Hz, 다른 소리")
        self.play(FadeIn(h))
        mix = {"악기 A": ([1, .55, .35, .2, .12, .07, .04, .02], BLU), "악기 B": ([1, .8, .7, .5, .45, .3, .25, .2], ORG)}
        for i, (name, (amp, c)) in enumerate(mix.items()):
            x = -3.4 if i == 0 else 3.4
            ax = wave_axes(5.2, 1.8, 2 * TAU, 2.6).shift(RIGHT * x + UP * .9)
            f = lambda t, amp=amp: sum(a * np.sin((k + 1) * t + .4 * k) for k, a in enumerate(amp))
            cur = ax.plot(f, x_range=[0, 2 * TAU, .01], color=c, stroke_width=4)
            bw = 4.4 / 8; bs = VGroup(*[Rectangle(width=bw * .7, height=1.5 * a, stroke_width=0, fill_color=c, fill_opacity=1).move_to([x - 2.2 + (k + .5) * bw, -2.4, 0], aligned_edge=DOWN) for k, a in enumerate(amp)])
            base = Line([x - 2.2, -2.4, 0], [x + 2.2, -2.4, 0], color=MUTE)
            nl = VGroup(*[MathTex(s, font_size=20, color=MUTE).move_to([x - 2.2 + (k + .5) * bw, -2.65, 0]) for k, s in enumerate(["440", "880", "1320", "", "", "", "", ""]) if s])
            self.play(FadeIn(kr(name, 30, c).next_to(ax, UP, .15)), Create(ax), Create(cur), FadeIn(base), FadeIn(bs), FadeIn(nl), run_time=1.4)
        t = kr("기본 주파수는 같고, 고조파 비율이 다르다", 28, YEL).to_edge(DOWN, buff=.15)
        n = kr("(비율은 설명용 예시)", 20, MUTE).to_corner(DR, buff=.2)
        self.play(FadeIn(t), FadeIn(n)); self.wait(2)


class Summary(Scene):
    def construct(self):
        h = head("정리")
        self.play(FadeIn(h))
        rows = [("주기 신호", "= 평균값 + 고조파의 합", BLU), ("계수", "= 곱해서 한 주기 평균", GRN),
                ("대칭", "짝 → cos만 · 홀 → sin만 · 반파 → 홀수 차수만", ORG), ("회로", "고조파마다 페이저 → 다시 더하기", YEL)]
        tb = VGroup(*[VGroup(kr(a, 34, c), kr(b, 30)).arrange(RIGHT, buff=.5) for a, b, c in rows]).arrange(DOWN, buff=.55, aligned_edge=LEFT).shift(DOWN * .2)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * .2) for r in tb], lag_ratio=.35), run_time=2.2); self.wait(2.5)
