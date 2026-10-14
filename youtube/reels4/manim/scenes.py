# 선형대수 쇼츠 4편(최소제곱법 · 그람-슈미트 · 대각화 · 역행렬) 설명 그래픽. 세로 영상 가운데 칸(1080×840)용.
# 렌더: ~/.venvs/manim/bin/manim -r 1080,840 --fps 30 scenes.py <Scene>
from manim import *
import numpy as np

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, ORG, GRN, PUR, RED = "#7aa2ff", "#ff9f43", "#3ddc97", "#c792ff", "#ff6b9a"
KR = "Noto Sans CJK KR"
config.background_color = BG
config.frame_height = 8.0
config.frame_width = 8.0 * 1080 / 840


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def mat(rows, color=INK, size=40, hl=None, hb=1.0):
    """정수 행렬 (Text 로 그려서 LaTeX 없이). hl: {(i,j): 색}"""
    m = MobjectMatrix([[kr(str(x), size, (hl or {}).get((i, j), color), weight=BOLD) for j, x in enumerate(r)] for i, r in enumerate(rows)],
                      h_buff=hb, v_buff=.75, bracket_h_buff=.15)
    m.get_brackets().set_color(MUTE)
    return m


def plane(r=6):
    return NumberPlane(x_range=[-r * 2, r * 2], y_range=[-r * 2, r * 2], x_length=r * 4 * .62, y_length=r * 4 * .62,
                       background_line_style={"stroke_color": BLU, "stroke_width": 2, "stroke_opacity": .45},
                       faded_line_ratio=1, axis_config={"stroke_color": MUTE, "stroke_width": 3})


class LeastSq(Scene):
    """점 5개 → 다 지나는 직선 없음 → 오차 제곱합 최소 직선 → 정규방정식."""
    def construct(self):
        P = np.array([[-3, -1.5], [-1.5, -1], [0, .5], [1, .5], [2.5, 2.5]])
        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3.5, 1], x_length=8.6, y_length=5.4,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .2)
        head = kr("점 5개, 직선 하나?", 44).to_edge(UP, buff=.35)
        dots = VGroup(*[Dot(ax.c2p(*p), .12, color=BLU) for p in P])
        self.play(FadeIn(head), Create(ax), LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=.15), run_time=1.6)
        # 아무렇게나 두 점을 이은 직선: 나머지는 빗나간다
        tr = ax.plot(lambda x: (x + 3) * (2.5 + 1.5) / 5.5 - 1.5, x_range=[-4, 4], color=MUTE, stroke_width=5)
        miss = kr("✕ 전부 지나는 직선은 없다", 34, RED).next_to(head, DOWN, .2)
        self.play(Create(tr), run_time=.8); self.play(FadeIn(miss), Wiggle(tr), run_time=1)
        A = np.c_[np.ones(5), P[:, 0]]; c = np.linalg.solve(A.T @ A, A.T @ P[:, 1])
        f = lambda x: c[0] + c[1] * x
        best = ax.plot(f, x_range=[-4, 4], color=GRN, stroke_width=7)
        res = VGroup(); sq = VGroup()
        for x, y in P:
            p0, p1 = ax.c2p(x, f(x)), ax.c2p(x, y)
            res.add(Line(p0, p1, color=RED, stroke_width=6))
            s = abs(p1[1] - p0[1]); sgn = -1 if x > 0 else 1
            sq.add(Polygon(p0, p1, p1 + RIGHT * s * sgn, p0 + RIGHT * s * sgn, stroke_width=0, fill_color=RED, fill_opacity=.22))
        head2 = kr("오차² 합이 가장 작은 직선", 44, GRN).to_edge(UP, buff=.35)
        self.play(ReplacementTransform(tr, best), FadeOut(miss), ReplacementTransform(head, head2), run_time=1.2)
        self.play(LaggedStart(*[Create(r) for r in res], lag_ratio=.12), FadeIn(sq), run_time=1.2)
        sse = float(((A @ c - P[:, 1]) ** 2).sum())
        tag = kr(f"오차제곱합 = {sse:.2f} (최소)", 32, RED).next_to(head2, DOWN, .2)
        self.play(FadeIn(tag)); self.wait(1.4)
        eq = VGroup(kr("정규방정식", 30, MUTE), kr("AᵀA x̂ = Aᵀb", 56, YEL)).arrange(DOWN, buff=.18)
        self.play(FadeIn(card(eq).to_edge(DOWN, buff=.3), shift=UP * .3), run_time=.8)
        self.play(Indicate(eq[1], color=YEL, scale_factor=1.08)); self.wait(2.5)


class Project(ThreeDScene):
    """b 를 열공간(평면)에 정사영 → Ax̂, 오차는 평면에 수직."""
    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES, zoom=1.15)
        pl = Surface(lambda u, v: np.array([u, v, 0]), u_range=[-2.6, 2.6], v_range=[-2.6, 2.6], resolution=(8, 8),
                     fill_color=GRN, fill_opacity=.18, stroke_color=GRN, stroke_width=1, stroke_opacity=.4)
        b = np.array([1.6, 1.2, 2.2]); p = np.array([1.6, 1.2, 0])
        vb = Arrow3D(ORIGIN, b, color=BLU, thickness=.03); vp = Arrow3D(ORIGIN, p, color=GRN, thickness=.03)
        err = DashedLine(p, b, color=RED, stroke_width=7, dash_length=.15)
        ra = VGroup(Line(p + UP * .0 + np.array([0, 0, .3]), p + np.array([-.25, -.19, .3]), color=INK, stroke_width=4),
                    Line(p + np.array([-.25, -.19, .3]), p + np.array([-.25, -.19, 0]), color=INK, stroke_width=4))
        lb = kr("b", 46, BLU); lp = kr("Ax̂", 46, GRN); lc = kr("열공간 Col A", 32, GRN); le = kr("오차 ⟂ 평면", 36, RED)
        self.add_fixed_in_frame_mobjects(lb, lp, lc, le)
        for m in (lb, lp, lc, le): m.set_opacity(0)
        lb.move_to([1.2, 2.6, 0]); lp.move_to([2.6, -.6, 0]); lc.move_to([-3.2, -2.6, 0]); le.move_to([3.4, 1.3, 0])
        self.play(Create(pl), lc.animate.set_opacity(1), run_time=1)
        self.play(Create(vb), lb.animate.set_opacity(1), run_time=.9)
        self.play(Create(err), Create(vp), lp.animate.set_opacity(1), run_time=1.2)
        self.play(Create(ra), le.animate.set_opacity(1), run_time=.6)
        self.begin_ambient_camera_rotation(rate=.12); self.wait(3.2)


class GramSchmidt(ThreeDScene):
    """v₁=(1,1,0), v₂=(1,0,1), v₃=(0,1,1) → 그림자 빼기로 u₁,u₂,u₃ → 정규화 q."""
    def construct(self):
        self.set_camera_orientation(phi=66 * DEGREES, theta=-40 * DEGREES, zoom=.9, frame_center=[.9, .9, 1.4])
        S = 2.6
        V = [np.array(v, float) for v in ((1, 1, 0), (1, 0, 1), (0, 1, 1))]
        u1 = V[0]; p21 = V[1] @ u1 / (u1 @ u1) * u1; u2 = V[1] - p21
        p31 = V[2] @ u1 / (u1 @ u1) * u1; p32 = V[2] @ u2 / (u2 @ u2) * u2; u3 = V[2] - p31 - p32
        A = lambda a, b, c, t=.045: Arrow3D(a * S, b * S, color=c, thickness=t)
        ax = ThreeDAxes(x_range=[-.5, 2], y_range=[-.5, 2], z_range=[-.5, 2], x_length=6.5, y_length=6.5, z_length=6.5, tips=False,
                        axis_config={"stroke_color": "#3a404c", "stroke_width": 2, "include_ticks": False})
        head = kr("삐딱한 벡터 3개", 42); self.add_fixed_in_frame_mobjects(head); head.to_edge(UP, buff=.35)
        gv = [A(ORIGIN, v, MUTE, .02) for v in V]
        self.add(ax); self.play(*[Create(g) for g in gv], FadeIn(head), run_time=1.2)
        self.begin_ambient_camera_rotation(rate=.10)
        def title(s, c=INK):
            t = kr(s, 42, c); self.add_fixed_in_frame_mobjects(t); t.to_edge(UP, buff=.35); return t
        a1 = A(ORIGIN, u1, ORG); t1 = title("① 첫 번째는 그대로", ORG)
        self.play(FadeOut(head), FadeIn(t1), Create(a1), run_time=.9); self.wait(.4)
        sh = A(ORIGIN, p21, RED, .04); t2 = title("② 그림자를 빼면 → 수직", GRN)
        self.play(FadeOut(t1), FadeIn(t2), Create(sh), run_time=.9)
        a2 = A(p21, V[1], GRN)
        self.play(Create(a2), run_time=.8)
        a2b = A(ORIGIN, u2, GRN); self.play(ReplacementTransform(a2, a2b), FadeOut(sh), run_time=.8); self.wait(.4)
        t3 = title("③ 두 방향 그림자를 둘 다 빼기", BLU)
        sh1 = A(ORIGIN, p31, RED, .04); sh2 = A(p31, p31 + p32, RED, .04)
        self.play(FadeOut(t2), FadeIn(t3), Create(sh1), Create(sh2), run_time=1)
        a3 = A(p31 + p32, V[2], BLU); self.play(Create(a3), run_time=.7)
        a3b = A(ORIGIN, u3, BLU); self.play(ReplacementTransform(a3, a3b), FadeOut(sh1), FadeOut(sh2), run_time=.8)
        t4 = title("④ 길이로 나누면 정규직교 기저", YEL)
        q = [u / np.linalg.norm(u) for u in (u1, u2, u3)]
        self.play(FadeOut(t3), FadeIn(t4), *[FadeOut(g) for g in gv],
                  ReplacementTransform(a1, A(ORIGIN, q[0], ORG)), ReplacementTransform(a2b, A(ORIGIN, q[1], GRN)),
                  ReplacementTransform(a3b, A(ORIGIN, q[2], BLU)), run_time=1.2)
        self.wait(3)


class Diag(Scene):
    """A=[1 2;2 1] = P D P⁻¹ (격자 3단계) → A¹⁰ = P D¹⁰ P⁻¹."""
    def construct(self):
        Pm = np.array([[1, 1], [1, -1]], float); Dm = np.diag([3., -1.]); Pi = np.linalg.inv(Pm)
        pl = plane(4); self.add(pl)
        e1 = Vector([1 * pl.x_length / 16, 1 * pl.y_length / 16 * 0 + 0], color=ORG)
        u = pl.x_length / 16      # 한 칸 길이
        v1 = Arrow(ORIGIN, np.array([u, u, 0]), buff=0, color=ORG, stroke_width=8)
        v2 = Arrow(ORIGIN, np.array([u, -u, 0]), buff=0, color=GRN, stroke_width=8)
        g = VGroup(pl, v1, v2)
        head = card(VGroup(kr("A =", 40), mat([[1, 2], [2, 1]], size=36)).arrange(RIGHT, buff=.2), buff=.2).to_edge(UP, buff=.25)
        lab = kr("고유벡터: λ=3, λ=−1", 30, MUTE).next_to(head, DOWN, .15)
        self.play(FadeIn(head), GrowArrow(v1), GrowArrow(v2), FadeIn(lab), run_time=1)
        steps = [(Pi, "① P⁻¹: 고유벡터를 축으로", INK), (Dm, "② D: 축 방향으로 3배, −1배", YEL), (Pm, "③ P: 제자리로 = A", GRN)]
        cap = None
        for M, s, c in steps:
            t = card(kr(s, 36, c), buff=.18).to_edge(DOWN, buff=.3)
            self.play(FadeIn(t) if cap is None else ReplacementTransform(cap, t), run_time=.4)
            self.play(ApplyMatrix(np.array(M), g), run_time=1.2); cap = t; self.wait(.3)
        self.wait(.4)
        self.play(FadeOut(g), FadeOut(cap), FadeOut(lab), run_time=.6)
        r1 = VGroup(kr("A¹⁰ = P", 40), mat([[59049, 0], [0, 1]], size=34, hb=1.7, hl={(0, 0): YEL, (1, 1): YEL}), kr("P⁻¹", 40)).arrange(RIGHT, buff=.2)
        r2 = kr("3¹⁰ = 59049   (−1)¹⁰ = 1", 38, YEL)
        r3 = VGroup(kr("=", 44), mat([[29525, 29524], [29524, 29525]], size=36, color=GRN, hb=1.9)).arrange(RIGHT, buff=.25)
        grp = VGroup(r1, r2, r3).arrange(DOWN, buff=.35).next_to(head, DOWN, .35)
        self.play(FadeIn(r1, shift=UP * .2), run_time=.8); self.play(FadeIn(r2), run_time=.6)
        self.play(FadeIn(r3, shift=UP * .2), run_time=.8)
        ok = kr("✓ 직접 10번 곱한 값과 같다", 34, GRN).next_to(r3, DOWN, .3)
        self.play(FadeIn(ok)); self.wait(2.5)


class Inverse(Scene):
    """A 로 비틀기 → A⁻¹ 로 되감기 → [A|I] → [I|A⁻¹] → det 0 이면 직선으로 눌려 못 되돌림."""
    def construct(self):
        A = np.array([[2, 1], [1, 1]], float); Ai = np.linalg.inv(A)
        pl = plane(4); u = pl.x_length / 16
        sq = Polygon(ORIGIN, [u, 0, 0], [u, u, 0], [0, u, 0], stroke_width=0, fill_color=YEL, fill_opacity=.45)
        g = VGroup(pl, sq); self.add(g)
        def cap(s, c=INK):
            return card(kr(s, 38, c), buff=.18).to_edge(UP, buff=.3)
        c1 = cap("A = [2 1; 1 1] 로 비틀기", ORG)
        self.play(FadeIn(c1)); self.play(ApplyMatrix(A, g), run_time=1.3); self.wait(.3)
        c2 = cap("A⁻¹ = 되감기 ⏪", GRN)
        self.play(ReplacementTransform(c1, c2)); self.play(ApplyMatrix(Ai, g), run_time=1.3); self.wait(.4)
        self.play(FadeOut(g), FadeOut(c2), run_time=.5)
        # [A | I] → [I | A⁻¹]
        L = mat([[2, 1, 1, 0], [1, 1, 0, 1]], size=40, hl={(0, 2): MUTE, (0, 3): MUTE, (1, 2): MUTE, (1, 3): MUTE})
        R = mat([[1, 0, 1, -1], [0, 1, -1, 2]], size=40, hl={(0, 2): GRN, (0, 3): GRN, (1, 2): GRN, (1, 3): GRN})
        for m in (L, R):
            ent = m.get_entries(); x = (ent[1].get_right()[0] + ent[2].get_left()[0]) / 2
            m.add(DashedLine([x, m.get_top()[1] - .1, 0], [x, m.get_bottom()[1] + .1, 0], color=MUTE, stroke_width=3))
        tl = kr("[ A | I ]", 40, MUTE); tr = kr("[ I | A⁻¹ ]", 40, GRN)
        top = VGroup(tl, L).arrange(DOWN, buff=.25).move_to(UP * 1.9)
        arr = VGroup(Arrow(UP * .45, DOWN * .45, color=YEL, stroke_width=8), kr("행 소거", 32, YEL)).arrange(RIGHT, buff=.2).move_to(DOWN * .05)
        bot = VGroup(tr, R).arrange(DOWN, buff=.25).move_to(DOWN * 2.1)
        self.play(FadeIn(top), run_time=.7); self.play(GrowArrow(arr[0]), FadeIn(arr[1]), run_time=.6)
        self.play(TransformFromCopy(L, R), FadeIn(tr), run_time=1.2)
        self.play(Indicate(VGroup(*R.get_entries()[2:4], *R.get_entries()[6:8]), color=GRN)); self.wait(1.2)
        self.play(FadeOut(VGroup(top, arr, bot)), run_time=.5)
        # det = 0
        B = np.array([[2, 1], [4, 2]], float)
        pl2 = plane(4); sq2 = sq.copy().move_to(ORIGIN).align_to(ORIGIN, DL); g2 = VGroup(pl2, sq2)
        sq2.become(Polygon(ORIGIN, [u, 0, 0], [u, u, 0], [0, u, 0], stroke_width=0, fill_color=YEL, fill_opacity=.45))
        c3 = cap("det = 0 → 평면이 직선으로", RED)
        self.play(FadeIn(g2), FadeIn(c3), run_time=.5); self.play(ApplyMatrix(B, g2), run_time=1.3)
        x = kr("✕ 되돌릴 수 없음", 48, RED); self.play(FadeIn(card(x).to_edge(DOWN, buff=.4), scale=1.1)); self.wait(2.5)
