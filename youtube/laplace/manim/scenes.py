# 회로이론 15장 라플라스 변환 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
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


class Hook(Scene):
    """미분방정식 → (라플라스) → 곱셈 한 줄."""
    def construct(self):
        a = tex(r"RC\,\frac{dv}{dt} + v = V", 80)
        lab1 = kr("미분방정식", 34, RED).next_to(a, UP, .4)
        self.play(Write(a), FadeIn(lab1), run_time=1.2)
        self.wait(.4)
        b = tex(r"(sRC + 1)\,V(s) = \frac{V}{s}", 80, YEL)
        lab2 = kr("곱셈 · 나눗셈만", 34, GRN).next_to(b, DOWN, .4)
        g = VGroup(a, lab1)
        self.play(g.animate.shift(UP * 1.6).scale(.75), run_time=.7)
        arr = Arrow(UP * .9, DOWN * .1, color=BLU, stroke_width=8)
        al = kr("라플라스 변환", 32, BLU).next_to(arr, RIGHT, .3)
        self.play(GrowArrow(arr), FadeIn(al), run_time=.6)
        VGroup(b, lab2).shift(DOWN * 1.6)
        self.play(TransformFromCopy(a, b), FadeIn(lab2), run_time=1.2)
        self.play(Circumscribe(b, color=YEL, buff=.2), run_time=1.0)
        self.wait(2)


def rc_circuit(closed=False):
    """전원 · 스위치 · R · C 직렬 회로 (단순 그림)."""
    W, Hh = 4.0, 2.4
    tl, tr, br, bl = np.array([-W/2, Hh/2, 0]), np.array([W/2, Hh/2, 0]), np.array([W/2, -Hh/2, 0]), np.array([-W/2, -Hh/2, 0])
    g = VGroup()
    # 전원(왼쪽 세로)
    g.add(Line(bl, bl + UP * .85, color=INK), Line(bl + UP * 1.55, tl, color=INK))
    g.add(Line(bl + UP * .85 + LEFT * .35, bl + UP * .85 + RIGHT * .35, color=INK, stroke_width=6))
    g.add(Line(bl + UP * 1.55 + LEFT * .55, bl + UP * 1.55 + RIGHT * .55, color=INK, stroke_width=6))
    g.add(kr("V", 30, YEL).next_to(bl + UP * 1.2, LEFT, .5))
    # 스위치(위)
    s0 = tl + RIGHT * .7; s1 = s0 + RIGHT * .8
    g.add(Line(tl, s0, color=INK), Dot(s0, .06, color=INK), Dot(s1, .06, color=INK))
    sw = Line(s0, s1 if closed else s0 + np.array([.65, .45, 0]), color=YEL, stroke_width=5)
    g.add(sw)
    # 저항(위 오른쪽)
    r0 = s1 + RIGHT * .2; pts = [s1, r0]
    for k in range(6):
        pts.append(r0 + RIGHT * (.15 + .3 * k) + UP * (.18 if k % 2 == 0 else -.18))
    r1 = r0 + RIGHT * 1.9; pts += [r1]
    g.add(VMobject(color=INK).set_points_as_corners(pts), Line(r1, tr, color=INK))
    g.add(kr("R", 30, ORG).next_to(r0 + RIGHT * .95, UP, .3))
    # 커패시터(오른쪽 세로)
    g.add(Line(tr, tr + DOWN * 1.0, color=INK), Line(br + UP * 1.0, br, color=INK))
    g.add(Line(tr + DOWN * 1.0 + LEFT * .45, tr + DOWN * 1.0 + RIGHT * .45, color=INK, stroke_width=6))
    g.add(Line(br + UP * 1.0 + LEFT * .45, br + UP * 1.0 + RIGHT * .45, color=INK, stroke_width=6))
    g.add(kr("C", 30, BLU).next_to(tr + DOWN * 1.2, RIGHT, .55))
    g.add(Line(br, bl, color=INK))
    return g, sw


class RcProblem(Scene):
    """RC 회로 → KVL → 미분방정식 → 2차·연립으로 불어난다."""
    def construct(self):
        h = head("스위치를 닫는 순간의 RC 회로")
        c, sw = rc_circuit(False); c.scale(.9).shift(LEFT * 3.3 + DOWN * .3)
        self.play(FadeIn(h), Create(c), run_time=1.4)
        s0 = sw.get_start(); sw2 = Line(s0, s0 + RIGHT * .72, color=YEL, stroke_width=5)
        self.play(Transform(sw, sw2), run_time=.5)
        e1 = tex(r"RC\,\frac{dv}{dt} + v = V", 60).shift(RIGHT * 3 + UP * 1.2)
        l1 = kr("KVL → 1차 미분방정식", 28, MUTE).next_to(e1, UP, .3)
        self.play(FadeIn(l1), Write(e1), run_time=1.0)
        e2 = tex(r"LC\,\frac{d^2v}{dt^2} + RC\,\frac{dv}{dt} + v = V", 46, ORG).next_to(e1, DOWN, .7)
        e3 = tex(r"\begin{cases} \dot x_1 = \cdots \\ \dot x_2 = \cdots \\ \dot x_3 = \cdots \end{cases}", 46, RED).next_to(e2, DOWN, .5)
        self.play(FadeIn(e2, shift=UP * .2)); self.play(FadeIn(e3, shift=UP * .2))
        ic = card(kr("+ 초기 조건 v(0)", 30, YEL), color=YEL).next_to(e3, DOWN, .4)
        self.play(FadeIn(ic), Wiggle(VGroup(e2, e3)), run_time=1.2)
        self.wait(2)


class LogAnalogy(Scene):
    """로그: 곱셈 → 덧셈 → 되돌리기 / 라플라스: 미분방정식 → 대수 → 되돌리기."""
    def construct(self):
        h = head("어려운 세계 → 쉬운 세계 → 다시 돌아오기")
        self.play(FadeIn(h))
        def row(a, b, c, f, g, col, y):
            A = card(kr(a, 32), color="#2a2e37"); B = card(kr(b, 32, col), color=col); C = card(kr(c, 32, GRN), color=GRN)
            VGroup(A, B, C).arrange(RIGHT, buff=1.3).shift(UP * y)
            a1 = Arrow(A.get_right(), B.get_left(), buff=.1, color=col); a2 = Arrow(B.get_right(), C.get_left(), buff=.1, color=col)
            t1 = kr(f, 24, col).next_to(a1, UP, .1); t2 = kr(g, 24, col).next_to(a2, UP, .1)
            return VGroup(A, B, C, a1, a2, t1, t2)
        r1 = row("큰 곱셈", "덧셈", "답", "로그", "되돌리기", BLU, 1.2)
        r2 = row("미분방정식", "곱셈·분수", "답 v(t)", "라플라스", "역변환", YEL, -1.3)
        l1 = kr("옛날 계산법", 26, MUTE).next_to(r1, UP, .25).align_to(r1, LEFT)
        l2 = kr("라플라스 변환", 26, YEL).next_to(r2, UP, .25).align_to(r2, LEFT)
        self.play(FadeIn(l1), LaggedStart(*[FadeIn(m) for m in r1], lag_ratio=.15), run_time=1.6)
        self.wait(.5)
        self.play(FadeIn(l2), LaggedStart(*[FadeIn(m) for m in r2], lag_ratio=.15), run_time=1.6)
        hl = kr("미분 → 곱셈", 40, YEL).to_edge(DOWN, buff=.45)
        self.play(Write(hl)); self.wait(2)


class Definition(Scene):
    """F(s)=∫ f(t) e^{-st} dt, e^{-st} = 저울, s = σ + jω."""
    def construct(self):
        h = head("라플라스 변환의 정의")
        self.play(FadeIn(h))
        d = MathTex(r"F(s)", r"=", r"\int_0^{\infty}", r"f(t)", r"\,e^{-st}", r"\,dt", font_size=78).shift(UP * .9)
        self.play(Write(d), run_time=1.6)
        b = SurroundingRectangle(d[4], color=YEL, buff=.12)
        bl = kr("저울: s 성분이 얼마나 들어 있나", 30, YEL).next_to(b, DOWN, .35)
        self.play(Create(b), FadeIn(bl, shift=UP * .2)); self.wait(1.0)
        s = MathTex(r"s", r"=", r"\sigma", r"+", r"j\omega", font_size=70).shift(DOWN * 1.6 + LEFT * 2.6)
        self.play(FadeOut(bl), Write(s))
        b1 = Brace(s[2], DOWN, color=ORG); t1 = kr("감쇠·증가", 26, ORG).next_to(b1, DOWN, .1)
        b2 = Brace(s[4], DOWN, color=BLU); t2 = kr("진동", 26, BLU).next_to(b2, DOWN, .1)
        self.play(GrowFromCenter(b1), FadeIn(t1), GrowFromCenter(b2), FadeIn(t2))
        ax = Axes(x_range=[0, 6, 1], y_range=[-1.1, 1.1, 1], x_length=4.6, y_length=2.2, axis_config={"stroke_color": MUTE, "include_ticks": False}).shift(RIGHT * 3.4 + DOWN * 1.7)
        env = ax.plot(lambda t: np.exp(-.5 * t), color=ORG, stroke_width=3).set_stroke(opacity=.6)
        cur = ax.plot(lambda t: np.exp(-.5 * t) * np.cos(4 * t), color=BLU, stroke_width=5)
        lab = MathTex(r"e^{\sigma t}\cos\omega t", font_size=34, color=INK).next_to(ax, UP, .1)
        self.play(Create(ax), FadeIn(lab)); self.play(Create(env), Create(cur), run_time=1.6)
        self.wait(2)


class Table4(Scene):
    """외울 변환 4개: u(t)→1/s, e^{-at}→1/(s+a), df/dt→sF−f(0), ∫f→F/s."""
    def construct(self):
        h = head("외울 건 딱 4개")
        self.play(FadeIn(h))
        rows = [(r"u(t)", r"\dfrac{1}{s}", "계단", BLU), (r"e^{-at}", r"\dfrac{1}{s+a}", "지수 감쇠", BLU),
                (r"\dfrac{df}{dt}", r"sF(s) - f(0)", "미분 → 곱셈", YEL), (r"\int_0^t f\,d\tau", r"\dfrac{F(s)}{s}", "적분 → 나눗셈", GRN)]
        g = VGroup()
        for i, (a, b, n, c) in enumerate(rows):
            y = 2.0 - i * 1.45
            A = tex(a, 50).move_to([-3.6, y, 0]); ar = Arrow([-2.3, y, 0], [-1.0, y, 0], color=MUTE, buff=0, stroke_width=5)
            B = tex(b, 50, c).move_to([1.2, y, 0]); N = kr(n, 28, c).move_to([4.6, y, 0])
            g.add(VGroup(A, ar, B, N))
        for r in g:
            self.play(FadeIn(r[0]), GrowArrow(r[1]), FadeIn(r[2], shift=LEFT * .2), FadeIn(r[3]), run_time=.6)
            self.wait(.25)
        f0 = SurroundingRectangle(g[2][2][0][-4:], color=RED, buff=.08)
        note = kr("초기값이 자동으로 들어온다", 28, RED).next_to(g, DOWN, .25)
        self.play(Create(f0), FadeIn(note)); self.wait(2)


class SDomain(Scene):
    """R→R, L→sL, C→1/sC, 그리고 s=jω → jωL, 1/jωC (페이저 임피던스)."""
    def construct(self):
        h = head("s-영역의 회로 소자")
        self.play(FadeIn(h))
        names = [("저항", ORG), ("인덕터", PUR), ("커패시터", BLU)]
        s_ex = [r"R", r"sL", r"\dfrac{1}{sC}"]; j_ex = [r"R", r"j\omega L", r"\dfrac{1}{j\omega C}"]
        cols = VGroup()
        for i, ((n, c), a, b) in enumerate(zip(names, s_ex, j_ex)):
            x = -4 + i * 4
            N = kr(n, 34, c).move_to([x, 1.8, 0]); A = tex(a, 72, c).move_to([x, .5, 0]); B = tex(b, 64, INK).move_to([x, -1.9, 0])
            cols.add(VGroup(N, A, B))
        for col in cols:
            self.play(FadeIn(col[0]), Write(col[1]), run_time=.7)
        sub = card(tex(r"s \;\to\; j\omega", 54, YEL), color=YEL).move_to([0, -.7, 0])
        self.play(FadeIn(sub, scale=1.2))
        self.play(*[TransformFromCopy(c[1], c[2]) for c in cols], run_time=1.2)
        lab = kr("= 교류 회로의 임피던스 (페이저)", 34, GRN).to_edge(DOWN, buff=.45)
        self.play(FadeIn(lab, shift=UP * .2)); self.wait(2.5)


class RcSolve(Scene):
    """RC 계단 응답을 3단계로: s-영역 → 전압 분배·부분분수 → 역변환 → 충전 곡선."""
    def construct(self):
        h = head("RC 회로, 3단계로 풀기")
        self.play(FadeIn(h))
        st1 = kr("① s-영역으로", 30, BLU); e1 = tex(r"\frac{V}{s},\quad R,\quad \frac{1}{sC}", 50)
        st2 = kr("② 전압 분배 · 부분분수", 30, YEL)
        e2 = tex(r"V_C(s) = \frac{V}{s}\cdot\frac{1/sC}{R + 1/sC} = \frac{V}{s} - \frac{V}{s + 1/RC}", 46)
        st3 = kr("③ 표를 거꾸로", 30, GRN); e3 = tex(r"v_C(t) = V\left(1 - e^{-t/RC}\right)", 58, GRN)
        rows = VGroup(*[VGroup(a, b).arrange(RIGHT, buff=.5) for a, b in ((st1, e1), (st2, e2), (st3, e3))]).arrange(DOWN, buff=.5, aligned_edge=LEFT)
        rows.scale_to_fit_width(12.4).next_to(h, DOWN, .45)
        for r in rows:
            self.play(FadeIn(r[0]), Write(r[1]), run_time=1.1); self.wait(.4)
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 1.1, .5], x_length=5.5, y_length=1.7, axis_config={"stroke_color": MUTE, "include_ticks": False}).to_edge(DOWN, buff=.3)
        cur = ax.plot(lambda t: 1 - np.exp(-t), color=GRN, stroke_width=6)
        vl = DashedLine(ax.c2p(0, 1), ax.c2p(5, 1), color=MUTE)
        tl = kr("τ = RC", 24, MUTE).next_to(ax.c2p(1, 0), DOWN, .1)
        self.play(Create(ax), Create(vl), FadeIn(tl)); self.play(Create(cur), run_time=1.6)
        self.wait(2)


class PoleSurface(ThreeDScene):
    """|H(s)| 를 s-평면 위 지형으로: 극점에서 기둥처럼 솟는다. H(s)=1/((s+0.6)^2+16)."""
    def construct(self):
        self.set_camera_orientation(phi=64 * DEGREES, theta=-50 * DEGREES, zoom=1.05, frame_center=[0, 0, 1.0])
        ax = ThreeDAxes(x_range=[-3, 1.5, 1], y_range=[-6, 6, 2], z_range=[0, 4, 1], x_length=6, y_length=7, z_length=3.2)
        def H(u, v):
            s = complex(u, v); val = abs(1 / ((s + .6) ** 2 + 16))
            return ax.c2p(u, v, float(np.clip(1.7 * (np.log10(val + 1e-9) + 1.9), 0, 4.0)))
        surf = Surface(lambda u, v: H(u, v), u_range=[-3, 1.5], v_range=[-6, 6], resolution=(50, 70), fill_opacity=.95, checkerboard_colors=False)
        surf.set_fill_by_value(axes=ax, colorscale=[("#1d3b7a", 0), (BLU, .8), (PUR, 2.0), (YEL, 3.6)], axis=2)
        stab = Polygon(ax.c2p(-3, -6, 0), ax.c2p(0, -6, 0), ax.c2p(0, 6, 0), ax.c2p(-3, 6, 0), fill_color=GRN, fill_opacity=.12, stroke_width=0)
        lx = MathTex(r"\sigma", color=MUTE).move_to(ax.c2p(1.8, 0, 0)); ly = MathTex(r"j\omega", color=MUTE).move_to(ax.c2p(0, 6.6, 0))
        title = kr("s-평면 위의 |H(s)| · 극점에서 솟는다", 36).to_corner(UL, buff=.4)
        self.add_fixed_in_frame_mobjects(title); self.play(FadeIn(title))
        self.play(Create(ax), FadeIn(stab), FadeIn(lx), FadeIn(ly), run_time=1.2)
        self.play(Create(surf), run_time=2.4)
        self.begin_ambient_camera_rotation(rate=.18)
        self.wait(5)
        self.stop_ambient_camera_rotation()


class PoleMove(Scene):
    """극점을 왼쪽 → 허수축 → 오른쪽으로 옮기면 시간 응답이 감쇠 → 진동 → 발산."""
    def construct(self):
        sg = ValueTracker(-1.2); om = 4.0
        pl = NumberPlane(x_range=[-3, 1.5, 1], y_range=[-6, 6, 2], x_length=4.6, y_length=5.4, background_line_style={"stroke_color": "#2a2e37", "stroke_width": 1},
                         axis_config={"stroke_color": MUTE}).shift(LEFT * 4.0 + DOWN * .3)
        stab = Rectangle(width=pl.c2p(0, 0)[0] - pl.c2p(-3, 0)[0], height=5.4, fill_color=GRN, fill_opacity=.12, stroke_width=0).move_to(pl.c2p(-1.5, 0))
        unst = Rectangle(width=pl.c2p(1.5, 0)[0] - pl.c2p(0, 0)[0], height=5.4, fill_color=RED, fill_opacity=.10, stroke_width=0).move_to(pl.c2p(.75, 0))
        lab_s = kr("안정", 26, GRN).next_to(stab, DOWN, .1); lab_u = kr("불안정", 26, RED).next_to(unst, DOWN, .1)
        ax = Axes(x_range=[0, 6, 1], y_range=[-3, 3, 1], x_length=6.6, y_length=4.6, axis_config={"stroke_color": MUTE, "include_ticks": False}).shift(RIGHT * 2.9 + DOWN * .3)
        title = kr("극점 위치 → 시간 응답", 44).to_edge(UP, buff=.4)
        self.play(FadeIn(title), Create(pl), FadeIn(stab), FadeIn(unst), FadeIn(lab_s), FadeIn(lab_u), Create(ax), run_time=1.2)
        def poles():
            g = VGroup()
            for y in (om, -om):
                p = pl.c2p(sg.get_value(), y)
                g.add(VGroup(Line(p + UL * .16, p + DR * .16, color=YEL, stroke_width=7), Line(p + DL * .16, p + UR * .16, color=YEL, stroke_width=7)))
            return g
        def resp():
            s = sg.get_value(); c = GRN if s < -0.02 else (YEL if s < 0.02 else RED)
            return ax.plot(lambda t: np.clip(np.exp(s * t) * np.cos(om * t), -3, 3), x_range=[0, 6, .01], color=c, stroke_width=5)
        P = always_redraw(poles); R = always_redraw(resp)
        txt = always_redraw(lambda: MathTex(r"\sigma = %.1f" % sg.get_value(), font_size=40, color=YEL).next_to(pl, UP, .15))
        self.play(FadeIn(P), Create(R), FadeIn(txt), run_time=1.0)
        state = kr("감쇠 · 안정", 34, GRN).next_to(ax, UP, .2)
        self.play(FadeIn(state)); self.wait(1.2)
        self.play(sg.animate.set_value(0.0), run_time=2.2)
        self.play(Transform(state, kr("계속 진동", 34, YEL).next_to(ax, UP, .2))); self.wait(1.2)
        self.play(sg.animate.set_value(0.25), run_time=1.8)
        self.play(Transform(state, kr("발산 · 불안정", 34, RED).next_to(ax, UP, .2))); self.wait(1.5)
        self.play(sg.animate.set_value(-1.2), run_time=1.6)
        self.play(Transform(state, kr("왼쪽 반평면 = 안정", 34, GRN).next_to(ax, UP, .2))); self.wait(2)


class Apps(Scene):
    """라플라스로 설계하는 것들."""
    def construct(self):
        h = head("극점을 왼쪽에 두도록 설계한다")
        self.play(FadeIn(h))
        items = [("드론 자세 제어", BLU), ("크루즈 컨트롤", GRN), ("오디오 필터", PUR), ("전력망 안정도", ORG), ("로봇 팔", YEL)]
        cs = VGroup(*[card(kr(t, 36, c), color=c) for t, c in items])
        top = VGroup(*cs[:3]).arrange(RIGHT, buff=.4); bot = VGroup(*cs[3:]).arrange(RIGHT, buff=.4)
        VGroup(top, bot).arrange(DOWN, buff=.55).shift(DOWN * .1)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cs], lag_ratio=.25), run_time=1.8)
        self.wait(2.5)


class Summary(Scene):
    def construct(self):
        h = head("정리", YEL)
        ls = [("1", r"\frac{d}{dt} \to s", "미분방정식 → 대수 문제", RED), ("2", r"R,\; sL,\; \tfrac{1}{sC}", "옴의 법칙만으로 회로 해석", BLU), ("3", r"\mathrm{Re}(p) < 0", "극점이 왼쪽이면 안정", GRN)]
        g = VGroup()
        for n, t, d, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), tex(t, 46, c), kr(d, 36)).arrange(RIGHT, buff=.45))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.55).shift(DOWN * .1)
        self.play(FadeIn(h))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * .3) for r in g], lag_ratio=.5), run_time=2)
        foot = kr("보이는 회로이론 15장 · 극점 직접 옮겨 보기", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(3)
