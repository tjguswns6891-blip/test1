# 릴스 2차(선형대수 3·4장, 회로 4·12·13장) 설명 애니메이션.
# 렌더: ~/.venvs/manim/bin/manim -r 1920,1080 --fps 30 scenes.py <Scene>
from manim import *
import numpy as np

BG = "#111318"
INK = "#eef0f3"
MUTE = "#8d94a1"
YEL = "#ffc53d"
E1, E2, E3 = "#ff8f57", "#3fd5bd", "#d391ff"    # 선형대수 사이트 색
ACC, WARN, OK = "#8d9bff", "#ff6b9a", "#6bd982"
VOLT, AMP = "#7aa2ff", "#ff9f43"                 # 회로 사이트 색
KR = "Noto Sans CJK KR"
config.background_color = BG


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def plane(**kw):
    return NumberPlane(
        x_range=[-8, 8, 1], y_range=[-5, 5, 1],
        background_line_style={"stroke_color": "#2a3346", "stroke_width": 1.5},
        axis_config={"stroke_color": "#4d5a73"}, **kw)


class Kernel(Scene):
    """L-B: 커널 방향 벡터가 0으로 사라지고, 평면이 상공간 직선으로 눌린다."""
    def construct(self):
        A = np.array([[1, 2], [0.5, 1]])
        grid = plane()
        title = kr("A = [ 1  2 ; 0.5  1 ]   det A = 0", 34, MUTE).to_corner(UL).add_background_rectangle(color=BG, opacity=.8)
        kdir = np.array([-2, 1, 0]) / np.sqrt(5)
        kline = Line(-7 * kdir, 7 * kdir, color=WARN, stroke_width=6)
        kvecs = VGroup(*[Arrow(ORIGIN, t * kdir, buff=0, color=WARN, stroke_width=5) for t in (-3, -1.6, 1.6, 3)])
        klab = kr("커널 ker A", 36, WARN).next_to(3.2 * kdir, UP).add_background_rectangle(color=BG, opacity=.7)
        self.play(Create(grid, lag_ratio=.05), run_time=1.2)
        self.play(FadeIn(title), Create(kline), *[GrowArrow(v) for v in kvecs], FadeIn(klab), run_time=1.2)
        self.wait(.6)
        others = VGroup(Arrow(ORIGIN, [1.5, 1, 0], buff=0, color=E1, stroke_width=6), Arrow(ORIGIN, [0.5, 2, 0], buff=0, color=E2, stroke_width=6))
        self.play(*[GrowArrow(o) for o in others], run_time=.6)
        moving = VGroup(grid, kline, kvecs, others)
        self.play(FadeOut(klab), ApplyMatrix(A, moving), run_time=2.6, rate_func=smooth)
        rdir = np.array([1, .5, 0]) / np.linalg.norm([1, .5])
        rline = Line(-8 * rdir, 8 * rdir, color=OK, stroke_width=8)
        rlab = kr("상공간 range A", 36, OK).next_to(3.5 * rdir, DOWN + RIGHT * .2).add_background_rectangle(color=BG, opacity=.7)
        dot = Dot(ORIGIN, radius=.14, color=WARN)
        zero = kr("커널은 전부 0으로", 32, WARN).next_to(dot, DL).add_background_rectangle(color=BG, opacity=.7)
        self.play(Create(rline), FadeIn(rlab), FadeIn(dot, scale=3), FadeIn(zero), run_time=1)
        self.wait(.6)
        eq = VGroup(kr("dim ker", 46, WARN), kr("+", 46), kr("dim range", 46, OK), kr("=", 46), kr("2", 46, YEL)).arrange(RIGHT, buff=.3)
        nums = VGroup(kr("1", 60, WARN), kr("+", 60), kr("1", 60, OK), kr("=", 60), kr("2", 60, YEL)).arrange(RIGHT, buff=.45)
        box = VGroup(eq, nums).arrange(DOWN, buff=.35).to_edge(DOWN, buff=.5)
        bg = SurroundingRectangle(box, color="#2a2e37", fill_color="#181b21", fill_opacity=.95, buff=.35, corner_radius=.2)
        self.play(FadeIn(bg), Write(eq), run_time=1)
        self.play(LaggedStart(*[FadeIn(n, shift=UP * .3) for n in nums], lag_ratio=.15), run_time=1)
        self.play(Indicate(nums[-1], color=YEL, scale_factor=1.3))
        self.wait(1.2)


class BasisChange(Scene):
    """L-C: 같은 점 x 가 표준 좌표 (2,1), B 좌표 (1,1)."""
    def construct(self):
        std = plane()
        P = np.array([[1, 1], [0, 1]])
        x = np.array([2, 1, 0])
        dot = Dot(x, radius=.13, color=ACC)
        lab = always_redraw(lambda: kr("x", 40, ACC).next_to(dot, UR, buff=.1))
        c1 = kr("표준 좌표  (2, 1)", 44, INK).to_corner(UL).add_background_rectangle(color=BG, opacity=.85)
        e1 = Arrow(ORIGIN, RIGHT, buff=0, color=E1, stroke_width=7); e2 = Arrow(ORIGIN, UP, buff=0, color=E2, stroke_width=7)
        self.play(Create(std, lag_ratio=.05), run_time=1.2)
        self.play(GrowArrow(e1), GrowArrow(e2), FadeIn(dot, scale=2), FadeIn(lab), run_time=.8)
        path = VGroup(DashedLine(ORIGIN, [2, 0, 0], color=E1), DashedLine([2, 0, 0], x, color=E2))
        self.play(Create(path), FadeIn(c1), run_time=1)
        self.wait(.8)
        skew = NumberPlane(x_range=[-10, 10, 1], y_range=[-6, 6, 1],
                           background_line_style={"stroke_color": YEL, "stroke_width": 2, "stroke_opacity": .55},
                           axis_config={"stroke_color": YEL, "stroke_opacity": .8})
        b1 = Arrow(ORIGIN, RIGHT, buff=0, color=E1, stroke_width=7); b2 = Arrow(ORIGIN, UP, buff=0, color=E2, stroke_width=7)
        self.play(FadeOut(path), FadeIn(skew), ReplacementTransform(e1, b1), ReplacementTransform(e2, b2), run_time=.6)
        self.play(ApplyMatrix(P, VGroup(skew, b2)), run_time=2.2)
        bl = VGroup(kr("b₁", 34, E1).next_to(b1, DOWN, buff=.1), kr("b₂", 34, E2).next_to([.5, .5, 0], UL, buff=.12))
        self.play(FadeIn(bl))
        pathB = VGroup(DashedLine(ORIGIN, [1, 0, 0], color=E1, stroke_width=5), DashedLine([1, 0, 0], x, color=E2, stroke_width=5))
        c2 = kr("B 좌표  (1, 1)", 44, YEL).next_to(c1, DOWN, aligned_edge=LEFT).add_background_rectangle(color=BG, opacity=.85)
        self.play(Create(pathB), FadeIn(c2, shift=DOWN * .2), run_time=1.2)
        self.play(Indicate(dot, color=YEL, scale_factor=1.6))
        eq = kr("점은 그대로, 자만 바뀐다   x = P [x]B", 40, INK)
        bar = VGroup(SurroundingRectangle(eq, color="#2a2e37", fill_color="#181b21", fill_opacity=.95, buff=.3, corner_radius=.2), eq).to_edge(DOWN, buff=.5)
        self.play(FadeIn(bar, shift=UP * .3))
        self.wait(1.5)


class MaxPower(Scene):
    """C-A: P_L(R_L) 곡선, R_L = R_Th = 75Ω 에서 최대 270 mW."""
    def construct(self):
        V, Rth = 9.0, 75.0
        Pf = lambda R: V * V * R / (R + Rth) ** 2 * 1000
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 300, 100], x_length=11.4, y_length=5.4,
                  axis_config={"stroke_color": "#4d5a73", "include_ticks": True}, tips=False).shift(RIGHT * .7 + UP * .15)
        xl = VGroup(*[kr(t, 26, MUTE, NORMAL).next_to(ax.c2p(i, 0), DOWN) for i, t in enumerate(["1Ω", "10Ω", "100Ω", "1kΩ", "10kΩ"])])
        yl = VGroup(*[kr(f"{v} mW", 24, MUTE, NORMAL).next_to(ax.c2p(0, v), LEFT) for v in (100, 200, 300)])
        curve = ax.plot(lambda u: Pf(10 ** u), x_range=[0, 4], color=AMP, stroke_width=7)
        area = ax.get_area(curve, x_range=[0, 4], color=AMP, opacity=.15)
        title = kr("부하 전력  P = V²·R / (R + R_Th)²", 38, INK).to_edge(UP, buff=.45)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(title), run_time=1)
        self.play(Create(curve), FadeIn(area), run_time=1.6)
        t = ValueTracker(0.3)
        dot = always_redraw(lambda: Dot(ax.c2p(t.get_value(), Pf(10 ** t.get_value())), radius=.14, color=YEL))
        read = always_redraw(lambda: kr(f"R = {10 ** t.get_value():.0f}Ω   P = {Pf(10 ** t.get_value()):.0f} mW", 32, YEL)
                             .next_to(ax.c2p(t.get_value(), Pf(10 ** t.get_value())), UP, buff=.3))
        self.add(dot, read)
        self.play(t.animate.set_value(3.4), run_time=2.4, rate_func=there_and_back_with_pause)
        self.play(t.animate.set_value(np.log10(75)), run_time=1.2)
        x0 = np.log10(75)
        vl = DashedLine(ax.c2p(x0, 0), ax.c2p(x0, 285), color=INK, stroke_width=3)
        tag = kr("R_L = R_Th = 75Ω  →  최대 270 mW", 42, YEL)
        tagbg = VGroup(SurroundingRectangle(tag, color=YEL, fill_color="#181b21", fill_opacity=.95, buff=.25, corner_radius=.15), tag).move_to(ax.c2p(2.0, 45))
        self.play(Create(vl), Flash(dot.get_center(), color=YEL, line_length=.4, num_lines=14), run_time=.8)
        self.play(FadeIn(tagbg, shift=UP * .3))
        self.wait(1.5)


class ThreePhase(Scene):
    """C-B: 120° 어긋난 세 페이저, 머리-꼬리 이으면 원점으로 닫힌다 = 합 0."""
    def construct(self):
        cols = [VOLT, "#3ddc97", "#c792ff"]
        names = ["Va", "Vb", "Vc"]
        R = 2.6
        th = ValueTracker(PI / 2)
        O = LEFT * 3.4 + DOWN * .35
        circle = Circle(radius=R, color="#2a3346", stroke_width=2).move_to(O)
        def ph(k):
            return lambda: Arrow(O, O + R * np.array([np.cos(th.get_value() - k * 2 * PI / 3), np.sin(th.get_value() - k * 2 * PI / 3), 0]),
                                 buff=0, color=cols[k], stroke_width=8, max_tip_length_to_length_ratio=.12)
        arrows = [always_redraw(ph(k)) for k in range(3)]
        labs = [always_redraw(lambda k=k: kr(names[k], 32, cols[k]).move_to(O + (R + .45) * np.array([np.cos(th.get_value() - k * 2 * PI / 3), np.sin(th.get_value() - k * 2 * PI / 3), 0]))) for k in range(3)]
        ang = kr("120°씩 어긋난 세 전압", 40, INK).to_edge(UP, buff=.4)
        self.play(Create(circle), FadeIn(ang), run_time=.6)
        self.play(*[GrowArrow(a) for a in arrows], *[FadeIn(l) for l in labs], run_time=1)
        # 오른쪽: 세 사인파 + 합(0)
        ax = Axes(x_range=[0, 4 * PI, PI], y_range=[-1.3, 1.3, 1], x_length=6.6, y_length=3.6, tips=False,
                  axis_config={"stroke_color": "#4d5a73"}).shift(RIGHT * 3.4 + DOWN * .35)
        waves = VGroup(*[ax.plot(lambda x, k=k: np.cos(x - k * 2 * PI / 3), color=cols[k], stroke_width=4) for k in range(3)])
        self.play(Create(ax), LaggedStart(*[Create(w) for w in waves], lag_ratio=.3), th.animate.increment_value(2 * PI), run_time=3, rate_func=linear)
        # 머리-꼬리 잇기 (정지 스냅샷)
        self.remove(*arrows, *labs)
        t0 = th.get_value()
        vecs = [R * np.array([np.cos(t0 - k * 2 * PI / 3), np.sin(t0 - k * 2 * PI / 3), 0]) for k in range(3)]
        still = [Arrow(O, O + vecs[k], buff=0, color=cols[k], stroke_width=8, max_tip_length_to_length_ratio=.12) for k in range(3)]
        self.add(*still)
        p1 = O + vecs[0]; p2 = p1 + vecs[1]
        self.play(still[1].animate.shift(p1 - O), run_time=.9)
        self.play(still[2].animate.shift(p2 - O), run_time=.9)
        hit = Dot(O, radius=.16, color=YEL)
        s = kr("합 = 0", 54, YEL).next_to(O, DOWN, buff=.5).add_background_rectangle(color=BG, opacity=.8)
        sumw = ax.plot(lambda x: 0, color=YEL, stroke_width=7)
        sl = kr("Va + Vb + Vc = 0", 30, YEL).next_to(ax, UP, buff=.15)
        self.play(Flash(O, color=YEL, num_lines=16, line_length=.45), FadeIn(hit, scale=3), FadeIn(s), Create(sumw), FadeIn(sl), run_time=1)
        bar = kr("평형이면 중성선 전류 = 0", 42, INK)
        bar = VGroup(SurroundingRectangle(bar, color="#2a2e37", fill_color="#181b21", fill_opacity=.95, buff=.28, corner_radius=.2), bar).to_edge(DOWN, buff=.35)
        self.play(FadeIn(bar, shift=UP * .3))
        self.wait(1.5)


class TurnsRatio(Scene):
    """C-C: N₁:N₂ = 200:50 → 100V:25V, 전류는 625mA:2.5A, 전력 그대로."""
    def construct(self):
        head = kr("감은 횟수 비율 = 전압 비율", 48, INK).to_edge(UP, buff=.6)
        self.play(FadeIn(head, shift=DOWN * .2))
        def col(title, n, v, i, c):
            g = VGroup(kr(title, 34, MUTE), kr(f"{n}회", 72, c), kr(f"{v}", 64, VOLT), kr(f"{i}", 52, AMP)).arrange(DOWN, buff=.45)
            return g
        L = col("1차 코일", 200, "100 V", "625 mA", INK).shift(LEFT * 3.6 + DOWN * .3)
        Rg = col("2차 코일", 50, "25 V", "2.5 A", INK).shift(RIGHT * 3.6 + DOWN * .3)
        mid = VGroup(kr("÷4", 56, YEL), kr("÷4", 56, VOLT), kr("×4", 52, AMP)).arrange(DOWN, buff=.75).move_to(DOWN * .55)
        for a, b in zip(L, Rg): b.align_to(a, UP)
        mid[0].match_y(L[1]); mid[1].match_y(L[2]); mid[2].match_y(L[3])
        rowl = VGroup(kr("감은 횟수", 26, MUTE, NORMAL).next_to(L[1], LEFT, buff=.6), kr("전압", 26, VOLT, NORMAL).next_to(L[2], LEFT, buff=.6), kr("전류", 26, AMP, NORMAL).next_to(L[3], LEFT, buff=.6))
        self.play(FadeIn(L[0]), FadeIn(Rg[0]), FadeIn(L[1], shift=UP * .2), FadeIn(Rg[1], shift=UP * .2), FadeIn(rowl[0]), run_time=.9)
        self.play(GrowFromCenter(mid[0]), run_time=.5)
        self.play(FadeIn(L[2]), FadeIn(rowl[1]), run_time=.5)
        self.play(TransformFromCopy(L[2], Rg[2]), GrowFromCenter(mid[1]), run_time=.9)
        self.play(FadeIn(L[3]), FadeIn(rowl[2]), run_time=.5)
        self.play(TransformFromCopy(L[3], Rg[3]), GrowFromCenter(mid[2]), run_time=.9)
        pw = kr("전력  100 V × 625 mA  =  25 V × 2.5 A", 40, YEL)
        pwb = VGroup(SurroundingRectangle(pw, color=YEL, fill_color="#181b21", fill_opacity=.95, buff=.28, corner_radius=.18), pw).to_edge(DOWN, buff=.4)
        self.play(FadeIn(pwb, shift=UP * .3))
        self.play(Indicate(pw, color=YEL, scale_factor=1.06))
        self.wait(1.5)
