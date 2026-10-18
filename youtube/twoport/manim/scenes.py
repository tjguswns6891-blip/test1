# 회로이론 17장 2포트 회로 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
# 숫자 예제는 사이트 시각화 17-1 기본값: Ra 100 · Rb 220 · Rc 330 Ω, 넣는 전류 10 mA
from manim import *
import numpy as np

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
TexTemplateLibrary.default.add_to_preamble(r"\usepackage{amsmath}")

RA, RB, RC, I0 = 100, 220, 330, 0.01
Z = [[RA + RC, RC], [RC, RB + RC]]
DZ = Z[0][0] * Z[1][1] - Z[0][1] * Z[1][0]


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def tex(s, size=56, color=INK):
    return MathTex(s, font_size=size, color=color)


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)


def resistor(a, b, color=INK, n=6, amp=.14):
    """a→b 지그재그 저항 (양 끝 1/5 은 도선)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a; L = np.linalg.norm(d); u = d / L; v = np.array([-u[1], u[0], 0])
    p0, p1 = a + u * L * .2, a + u * L * .8
    pts = [a, p0] + [p0 + (p1 - p0) * (k + .5) / n + v * amp * (1 if k % 2 == 0 else -1) for k in range(n)] + [p1, b]
    return VMobject(color=color, stroke_width=4).set_points_as_corners(pts)


def wire(*pts, color=INK):
    return VMobject(color=color, stroke_width=4).set_points_as_corners([np.array(p, float) for p in pts])


def terminal(p, color=INK):
    return Circle(.09, color=color, fill_color=BG, fill_opacity=1, stroke_width=3).move_to(p)


def box2(label="?", w=3.2, h=2.2, color=BLU, inner=None):
    """2포트 상자: 왼쪽 포트 1, 오른쪽 포트 2, 단자 4개."""
    r = RoundedRectangle(width=w, height=h, corner_radius=.2, color=color, fill_color="#181b21", fill_opacity=1, stroke_width=4)
    t = inner if inner is not None else kr(label, 60, color)
    t.move_to(r)
    y = h * .3
    lead = VGroup(*[Line(r.get_left() + UP * s * y, r.get_left() + UP * s * y + LEFT * .7, color=INK, stroke_width=4) for s in (1, -1)],
                  *[Line(r.get_right() + UP * s * y, r.get_right() + UP * s * y + RIGHT * .7, color=INK, stroke_width=4) for s in (1, -1)])
    terms = VGroup(*[terminal(l.get_end()) for l in lead])
    return VGroup(r, t, lead, terms)


def t_net(scale=1.0, open_side=2, show_src=True):
    """T형 회로 (Ra 직렬 · Rc 병렬 · Rb 직렬). open_side 쪽은 개방, 반대쪽에 전류원."""
    xl, xr, xm, yt, yb = -3.2, 3.2, 0, 1.0, -1.2
    g = VGroup(
        resistor([xl, yt, 0], [xm, yt, 0]), resistor([xm, yt, 0], [xr, yt, 0]),
        resistor([xm, yt, 0], [xm, yb, 0]), wire([xl, yb, 0], [xr, yb, 0]),
    )
    labs = VGroup(MathTex(r"R_a=100\,\Omega", font_size=36).move_to([-1.6, yt + .45, 0]),
                  MathTex(r"R_b=220\,\Omega", font_size=36).move_to([1.6, yt + .45, 0]),
                  MathTex(r"R_c=330\,\Omega", font_size=36).move_to([xm + 1.3, (yt + yb) / 2, 0]))
    terms = VGroup(*[terminal([x, y, 0]) for x in (xl, xr) for y in (yt, yb)])
    src = VGroup()
    if show_src:
        xs = xl - 1.3 if open_side == 2 else xr + 1.3
        xe = xl if open_side == 2 else xr
        c = Circle(.38, color=ORG, stroke_width=4).move_to([xs, (yt + yb) / 2, 0])
        arr = Arrow(c.get_bottom() + UP * .12, c.get_top() + DOWN * .12, buff=0, color=ORG, stroke_width=5, max_tip_length_to_length_ratio=.35)
        src = VGroup(wire([xe, yt, 0], [xs, yt, 0], [xs, (yt + yb) / 2 + .38, 0]), wire([xe, yb, 0], [xs, yb, 0], [xs, (yt + yb) / 2 - .38, 0]), c, arr,
                     MathTex(r"10\,\mathrm{mA}", font_size=36, color=ORG).next_to(c, LEFT if open_side == 2 else RIGHT, .15))
    return VGroup(g, labs, terms, src).scale(scale)


class Hook(Scene):
    """안을 몰라도 숫자 네 개면 끝."""
    def construct(self):
        h = head("안을 몰라도, 숫자 네 개")
        b = box2("?").shift(UP * .2)
        self.play(FadeIn(h), FadeIn(b, scale=.9), run_time=1.0)
        stuff = VGroup(resistor([-1, .5, 0], [0, .5, 0], MUTE), resistor([0, -.4, 0], [1, -.4, 0], MUTE),
                       kr("트랜지스터?", 24, MUTE).move_to([0, .05, 0])).scale(.8).move_to(b[0])
        self.play(FadeOut(b[1]), FadeIn(stuff), run_time=.7); self.wait(.5)
        m = tex(r"\begin{bmatrix}430&330\\330&550\end{bmatrix}\,\Omega", 52, YEL).move_to(b[0])
        self.play(FadeOut(stuff), FadeIn(m, scale=1.2), run_time=.8)
        t = kr("이 네 숫자가 회로 전부", 32, YEL).to_edge(DOWN, buff=.5)
        self.play(FadeIn(t)); self.wait(2)


class BlackBox(Scene):
    """증폭기·필터·변압기 → 포트 두 개짜리 상자, 전류는 둘 다 들어가는 방향."""
    def construct(self):
        h = head("회로를 상자 하나로")
        names = VGroup(*[kr(s, 32, c) for s, c in (("증폭기", BLU), ("필터", GRN), ("변압기", ORG))]).arrange(RIGHT, buff=1.2).shift(UP * 1.6)
        self.play(FadeIn(h), LaggedStart(*[FadeIn(n, shift=DOWN * .2) for n in names], lag_ratio=.3), run_time=1.4)
        b = box2("2포트", inner=kr("2포트", 44, BLU)).shift(DOWN * .6)
        self.play(ReplacementTransform(names, b[0]), FadeIn(b[1:]), run_time=1.0)
        p1 = kr("포트 1", 28, MUTE).next_to(b[0], LEFT, 1.0).shift(DOWN * 1.1)
        p2 = kr("포트 2", 28, MUTE).next_to(b[0], RIGHT, 1.0).shift(DOWN * 1.1)
        self.play(FadeIn(p1), FadeIn(p2)); self.wait(.4)
        y = b[0].get_top()[1] - b[0].height * .2
        a1 = Arrow(b[0].get_left() + LEFT * 1.1 + UP * (y - b[0].get_center()[1]), b[0].get_left() + LEFT * .15 + UP * (y - b[0].get_center()[1]), buff=0, color=ORG, stroke_width=6)
        a2 = Arrow(b[0].get_right() + RIGHT * 1.1 + UP * (y - b[0].get_center()[1]), b[0].get_right() + RIGHT * .15 + UP * (y - b[0].get_center()[1]), buff=0, color=ORG, stroke_width=6)
        l1 = MathTex("I_1", font_size=40, color=ORG).next_to(a1, UP, .1)
        l2 = MathTex("I_2", font_size=40, color=ORG).next_to(a2, UP, .1)
        self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(l1), FadeIn(l2))
        t = kr("전류는 둘 다 상자로 들어가는 방향", 30, YEL).to_edge(DOWN, buff=.4)
        self.play(FadeIn(t)); self.wait(2)


class ZParams(Scene):
    """V = z I, 숫자 네 개, 단위 Ω."""
    def construct(self):
        h = head("z 파라미터: 숫자 네 개")
        e1 = tex(r"V_1 = z_{11} I_1 + z_{12} I_2", 54).shift(UP * 1.1)
        e2 = tex(r"V_2 = z_{21} I_1 + z_{22} I_2", 54).next_to(e1, DOWN, .4)
        self.play(FadeIn(h), Write(e1), Write(e2), run_time=1.8); self.wait(.6)
        m = tex(r"\begin{bmatrix}V_1\\V_2\end{bmatrix}=\begin{bmatrix}z_{11}&z_{12}\\z_{21}&z_{22}\end{bmatrix}\begin{bmatrix}I_1\\I_2\end{bmatrix}", 54).shift(DOWN * 1.6)
        self.play(TransformFromCopy(VGroup(e1, e2), m), run_time=1.2)
        br = SurroundingRectangle(m[0][7:20], color=YEL, buff=.12)
        t = kr("단위 Ω → 임피던스 파라미터", 28, YEL).next_to(m, DOWN, .35)
        self.play(Create(br), FadeIn(t)); self.wait(2)


class MeasureOpen(Scene):
    """포트 2 개방, 포트 1에 10 mA → V₁ 4.3 V, V₂ 3.3 V → z₁₁ 430 Ω, z₂₁ 330 Ω."""
    def construct(self):
        h = head("포트 2를 열고 재기")
        n = t_net(1.0, 2).shift(UP * .2 + RIGHT * .4)
        self.play(FadeIn(h), Create(n[0]), FadeIn(n[1]), FadeIn(n[2]), run_time=1.4)
        op = kr("개방  I₂ = 0", 26, MUTE).next_to(n[2][3], RIGHT, .25).shift(UP * .9)
        self.play(FadeIn(n[3]), FadeIn(op)); self.wait(.4)
        v1 = tex(r"V_1 = 4.3\,\mathrm{V}", 42, GRN).to_edge(LEFT, buff=.6).shift(DOWN * 2.1)
        v2 = tex(r"V_2 = 3.3\,\mathrm{V}", 42, GRN).to_edge(RIGHT, buff=.6).shift(DOWN * 2.1)
        self.play(FadeIn(v1, shift=UP * .2), FadeIn(v2, shift=UP * .2)); self.wait(.5)
        z = VGroup(tex(r"z_{11} = \frac{4.3}{0.01} = 430\,\Omega", 40, YEL), tex(r"z_{21} = \frac{3.3}{0.01} = 330\,\Omega", 40, YEL)).arrange(RIGHT, buff=1.0).to_edge(DOWN, buff=.3)
        self.play(FadeOut(v1), FadeOut(v2), Write(z), run_time=1.4); self.wait(.6)
        note = kr("Rb엔 전류 0 → V₂ = Rc 전압", 28, MUTE).next_to(z, UP, .35)
        self.play(Indicate(n[0][2], color=YEL), FadeIn(note)); self.wait(2)


class Reciprocity(Scene):
    """반대로 재면 z₂₂ 550, z₁₂ 330 → z₁₂ = z₂₁ (상반성), 재야 할 숫자 3개."""
    def construct(self):
        h = head("반대로 재면: 상반성")
        mat = Matrix([["430", "330"], ["330", "550"]], element_to_mobject_config={"font_size": 70}, h_buff=1.6)
        m = VGroup(tex(r"\mathbf z =", 70), mat, tex(r"\Omega", 70)).arrange(RIGHT, buff=.3).shift(UP * .5)
        self.play(FadeIn(h), Write(m), run_time=1.4); self.wait(.4)
        ent = mat.get_entries()
        c12 = SurroundingRectangle(ent[1], color=YEL, buff=.1)
        c21 = SurroundingRectangle(ent[2], color=YEL, buff=.1)
        eq = tex(r"z_{12} = z_{21}", 54, YEL).shift(DOWN * 1.3)
        self.play(Create(c12), Create(c21), Write(eq)); self.wait(.6)
        tf = MathTex(r"\begin{bmatrix}R_a+R_c&R_c\\R_c&R_b+R_c\end{bmatrix}", font_size=40, color=MUTE).shift(DOWN * 2.6 + LEFT * 2.6)
        t = kr("R·L·C만 → 숫자 3개만 재면 끝", 30, GRN).next_to(tf, RIGHT, .6)
        self.play(FadeIn(tf), FadeIn(t)); self.wait(2)


class YTrap(Scene):
    """y는 단락해서 잰다. y₁₁ ≠ 1/z₁₁ : 2.33 mS vs 4.31 mS."""
    def construct(self):
        h = head("y₁₁ ≠ 1/z₁₁")
        self.play(FadeIn(h))
        cols = []
        for x, title, rin, val, col in ((-3.4, "포트 2 개방", r"R_{in} = 100 + 330 = 430\,\Omega", r"\frac{1}{430} = 2.33\,\mathrm{mS}", RED),
                                         (3.4, "포트 2 단락", r"R_{in} = 100 + 330\parallel 220 = 232\,\Omega", r"y_{11} = \frac{1}{232} = 4.31\,\mathrm{mS}", GRN)):
            g = VGroup(kr(title, 32, col), MathTex(rin, font_size=38), MathTex(val, font_size=44, color=col)).arrange(DOWN, buff=.45).move_to([x, 0, 0])
            cols.append(g)
        self.play(FadeIn(cols[0], shift=UP * .2), run_time=1.0); self.wait(.5)
        self.play(FadeIn(cols[1], shift=UP * .2), run_time=1.0)
        x = kr("✗", 60, RED).next_to(cols[0][2], RIGHT, .2)
        t = kr("y는 반대쪽을 막고(단락) 잰다", 30, YEL).to_edge(DOWN, buff=.4)
        self.play(FadeIn(x), FadeIn(t)); self.wait(2)


class HParam(Scene):
    """h 파라미터: 입력 전압·출력 전류. h₂₁ = I₂/I₁ |V₂=0 = 전류 이득 = hFE."""
    def construct(self):
        h = head("h 파라미터 = 트랜지스터의 숫자")
        b = box2(inner=kr("트랜지스터", 34, PUR), color=PUR).scale(.85).shift(UP * .9)
        self.play(FadeIn(h), FadeIn(b), run_time=1.0)
        e = VGroup(tex(r"V_1 = h_{11} I_1 + h_{12} V_2", 40), tex(r"I_2 = h_{21} I_1 + h_{22} V_2", 40)).arrange(DOWN, buff=.25).shift(DOWN * 1.2)
        self.play(Write(e), run_time=1.4); self.wait(.4)
        k = tex(r"h_{21} = \left.\frac{I_2}{I_1}\right|_{V_2=0}", 48, YEL).move_to(DOWN * 1.3 + LEFT * 3.0)
        self.play(e.animate.scale(.85).move_to(RIGHT * 3.3 + DOWN * 1.6), FadeIn(k)); self.wait(.4)
        g = VGroup(kr("전류 이득", 32, YEL), tex(r"= h_{FE}", 48, YEL)).arrange(RIGHT, buff=.2).next_to(k, DOWN, .4)
        self.play(FadeIn(g, shift=UP * .2)); self.wait(2)


class Cascade(Scene):
    """ABCD: −I₂, 줄줄이 이으면 행렬 곱."""
    def construct(self):
        h = head("ABCD: 이으면 곱하기")
        e = tex(r"\begin{bmatrix}V_1\\I_1\end{bmatrix}=\begin{bmatrix}A&B\\C&D\end{bmatrix}\begin{bmatrix}V_2\\-I_2\end{bmatrix}", 50).shift(UP * 1.4)
        self.play(FadeIn(h), Write(e), run_time=1.6)
        mi = SurroundingRectangle(e[0][-6:-2], color=RED, buff=.08)
        ml = kr("나가는 방향으로", 26, RED).next_to(mi, RIGHT, .2)
        self.play(Create(mi), FadeIn(ml)); self.wait(.6)
        b1 = box2(inner=tex(r"\mathbf T_1", 80, BLU)).scale(.6)
        b2 = box2(inner=tex(r"\mathbf T_2", 80, GRN), color=GRN).scale(.6)
        row = VGroup(b1, b2).arrange(RIGHT, buff=-.42).shift(DOWN * 1.0)
        self.play(FadeOut(mi), FadeOut(ml), FadeIn(row, shift=UP * .2), run_time=1.0)
        t = tex(r"\mathbf T = \mathbf T_1 \, \mathbf T_2", 56, YEL).shift(DOWN * 2.7)
        self.play(Write(t)); self.wait(2)


class Connections(Scene):
    """직렬 z 더하기 · 병렬 y 더하기 · 종속 ABCD 곱하기."""
    def construct(self):
        h = head("연결 규칙 세 줄")
        rows = VGroup(*[VGroup(kr(a, 38, c), kr("→", 38, MUTE), tex(b, 48, c)).arrange(RIGHT, buff=.5)
                        for a, b, c in (("직렬", r"\mathbf z_1 + \mathbf z_2", BLU), ("병렬", r"\mathbf y_1 + \mathbf y_2", GRN), ("종속", r"\mathbf T_1\,\mathbf T_2", ORG))]
                      ).arrange(DOWN, buff=.7, aligned_edge=LEFT).shift(DOWN * .3)
        self.play(FadeIn(h))
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * .3), run_time=.8); self.wait(.5)
        self.wait(1.5)


class Summary(Scene):
    def construct(self):
        h = head("정리")
        items = VGroup(*[kr(s, 34, c) for s, c in (
            ("2포트 = 안을 몰라도 숫자 네 개로 쓰는 상자", INK),
            ("z: 반대쪽 개방 · y: 반대쪽 단락", BLU),
            ("h: 트랜지스터 (h₂₁ = 전류 이득)", PUR),
            ("ABCD: 줄줄이 이으면 곱하기", ORG))]).arrange(DOWN, buff=.5, aligned_edge=LEFT)
        self.play(FadeIn(h))
        for it in items:
            self.play(FadeIn(it, shift=UP * .15), run_time=.6); self.wait(.3)
        self.wait(2)
