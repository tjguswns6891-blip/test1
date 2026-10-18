# 회로 해석 기본(L1) 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
# 예제 숫자: 분배 12V·2Ω·4Ω / 6A·3Ω·6Ω, 마디 12V·2Ω·6Ω·3Ω → V=6V, 망 12V·2Ω·4Ω·4Ω → 3A·1.5A, 변환 12V·3Ω ↔ 4A·3Ω (+6Ω → 8V)
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


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)


def P(x, y):
    return np.array([x, y, 0.0])


def resistor(a, b, color=INK, n=6, amp=.16):
    """a→b 지그재그 저항 (양 끝 1/4 은 도선)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a; L = np.linalg.norm(d); u = d / L; v = np.array([-u[1], u[0], 0])
    p0, p1 = a + u * L * .25, a + u * L * .75
    pts = [a, p0] + [p0 + (p1 - p0) * (k + .5) / n + v * amp * (1 if k % 2 == 0 else -1) for k in range(n)] + [p1, b]
    return VMobject(color=color, stroke_width=4).set_points_as_corners(pts)


def wire(*pts, color=INK):
    return VMobject(color=color, stroke_width=4).set_points_as_corners([np.array(p, float) for p in pts])


def dot(p, color=INK):
    return Dot(p, radius=.08, color=color)


def vsrc(a, b, label=None, color=ORG):
    """a(아래)→b(위) 사이 전압원: 원 + 위쪽 +."""
    a, b = np.array(a, float), np.array(b, float); c = (a + b) / 2; r = .4
    g = VGroup(wire(a, c + DOWN * r), wire(c + UP * r, b), Circle(r, color=color, stroke_width=4).move_to(c),
               MathTex("+", font_size=34, color=color).move_to(c + UP * .17), MathTex("-", font_size=34, color=color).move_to(c + DOWN * .19))
    if label:
        g.add(MathTex(label, font_size=38, color=color).next_to(c, LEFT, .55))
    return g


def isrc(a, b, label=None, color=ORG, side=LEFT):
    """a→b 방향 화살표 전류원."""
    a, b = np.array(a, float), np.array(b, float); c = (a + b) / 2; r = .4; u = (b - a) / np.linalg.norm(b - a)
    g = VGroup(wire(a, c - u * r), wire(c + u * r, b), Circle(r, color=color, stroke_width=4).move_to(c),
               Arrow(c - u * .28, c + u * .28, buff=0, color=color, stroke_width=5, max_tip_length_to_length_ratio=.4))
    if label:
        g.add(MathTex(label, font_size=38, color=color).next_to(c, side, .55))
    return g


def dsrc(a, b, label=None, color=PUR, side=RIGHT):
    """a→b 방향 종속 전류원 (다이아몬드)."""
    a, b = np.array(a, float), np.array(b, float); c = (a + b) / 2; r = .45; u = (b - a) / np.linalg.norm(b - a)
    dia = Square(r * 1.414, color=color, stroke_width=4).rotate(PI / 4).move_to(c)
    g = VGroup(wire(a, c - u * r), wire(c + u * r, b), dia,
               Arrow(c - u * .28, c + u * .28, buff=0, color=color, stroke_width=5, max_tip_length_to_length_ratio=.4))
    if label:
        g.add(MathTex(label, font_size=40, color=color).next_to(c, side, .5))
    return g


def rl(s, p, color=INK, size=36):
    return MathTex(s, font_size=size, color=color).move_to(p)


def nodal_net(third="R"):
    """12V — 2Ω — 마디 V — 6Ω ∥ (3Ω 또는 종속 전원 2Iₓ) — 땅."""
    xl, xm, xr, yt, yb = -3.6, 0.2, 3.0, 1.3, -1.6
    g = VGroup(vsrc(P(xl, yb), P(xl, yt), r"12\,\mathrm V"), resistor(P(xl, yt), P(xm, yt)),
               resistor(P(xm, yt), P(xm, yb)), wire(P(xm, yt), P(xr, yt)), wire(P(xl, yb), P(xr, yb)))
    labs = VGroup(rl(r"2\,\Omega", P((xl + xm) / 2, yt + .5)), rl(r"6\,\Omega", P(xm + .75, (yt + yb) / 2)))
    if third == "R":
        g.add(resistor(P(xr, yt), P(xr, yb))); labs.add(rl(r"3\,\Omega", P(xr + .75, (yt + yb) / 2)))
    else:
        g.add(dsrc(P(xr, yt), P(xr, yb), r"2I_x"))
    gnd = VGroup(*[Line(P((xl + xr) / 2 - w, yb - .25 - k * .14), P((xl + xr) / 2 + w, yb - .25 - k * .14), color=INK, stroke_width=4)
                   for k, w in enumerate((.35, .22, .09))], Line(P((xl + xr) / 2, yb), P((xl + xr) / 2, yb - .25), color=INK, stroke_width=4))
    node = VGroup(dot(P(xm, yt), YEL), MathTex("V", font_size=44, color=YEL).move_to(P(xm, yt + .5)))
    return VGroup(g, labs, gnd, node)


def mesh_net():
    """왼쪽 고리 12V·2Ω, 가운데 4Ω 공유, 오른쪽 고리 4Ω."""
    xl, xm, xr, yt, yb = -4.0, 0.0, 4.0, 1.3, -1.6
    g = VGroup(vsrc(P(xl, yb), P(xl, yt), r"12\,\mathrm V"), resistor(P(xl, yt), P(xm, yt)), resistor(P(xm, yt), P(xm, yb)),
               wire(P(xm, yt), P(xr, yt)), resistor(P(xr, yt), P(xr, yb)), wire(P(xl, yb), P(xr, yb)))
    labs = VGroup(rl(r"2\,\Omega", P(-2, yt + .5)), rl(r"4\,\Omega", P(xm - .75, (yt + yb) / 2)), rl(r"4\,\Omega", P(xr + .75, (yt + yb) / 2)))
    return VGroup(g, labs)


def loop_arrow(c, color, label):
    a = Arc(radius=.75, start_angle=PI * .75, angle=-PI * 1.5, color=color, stroke_width=5).move_arc_center_to(c)
    a.add_tip(tip_length=.25)
    return VGroup(a, MathTex(label, font_size=44, color=color).move_to(c))


class Hook(Scene):
    """방법 다섯 개면 회로 문제 거의 다."""
    def construct(self):
        h = head("회로 해석, 방법 다섯 개")
        items = [("분배", BLU), ("마디 해석", GRN), ("망 해석", ORG), ("전원 변환", PUR), ("종속 전원", RED)]
        cards = VGroup(*[VGroup(RoundedRectangle(width=2.3, height=1.5, corner_radius=.18, color=c, fill_color="#181b21", fill_opacity=1, stroke_width=4),
                                kr(s, 30, c)) for s, c in items]).arrange(RIGHT, buff=.25)
        for cd in cards:
            cd[1].move_to(cd[0])
        nums = VGroup(*[kr(str(i + 1), 26, MUTE).next_to(cd, UP, .15) for i, cd in enumerate(cards)])
        self.play(FadeIn(h), run_time=.6)
        self.play(LaggedStart(*[FadeIn(VGroup(c, n), shift=UP * .3) for c, n in zip(cards, nums)], lag_ratio=.25), run_time=2.0)
        t = kr("+ 옴의 법칙 · KCL · KVL", 32, YEL).next_to(cards, DOWN, .8)
        self.play(FadeIn(t)); self.wait(3)


class Basics(Scene):
    """옴 · KCL · KVL 세 칸."""
    def construct(self):
        h = head("기본 도구 세 개")
        self.play(FadeIn(h), run_time=.5)
        ohm = VGroup(kr("옴의 법칙", 32, BLU), tex(r"V = IR", 60)).arrange(DOWN, buff=.5).move_to(P(-4.3, .3))
        n0 = P(0, .3)
        arrs = VGroup(*[Arrow(n0 + d * 1.3, n0 + d * .12, buff=0, color=GRN, stroke_width=5) for d in (LEFT, UP)],
                      *[Arrow(n0 + d * .12, n0 + d * 1.3, buff=0, color=RED, stroke_width=5) for d in (RIGHT, DOWN)])
        kcl = VGroup(kr("KCL", 32, GRN).move_to(P(0, 2.2)), arrs, dot(n0), tex(r"\sum I_{in} = \sum I_{out}", 38).move_to(P(0, -1.6)))
        sq = Square(2.0, color=INK, stroke_width=4).move_to(P(4.3, .3))
        lp = Arc(radius=.6, start_angle=PI * .7, angle=-PI * 1.6, color=ORG, stroke_width=5).move_arc_center_to(P(4.3, .3)); lp.add_tip(tip_length=.22)
        kvl = VGroup(kr("KVL", 32, ORG).move_to(P(4.3, 2.2)), sq, lp, tex(r"\sum V = 0", 44).move_to(P(4.3, -1.6)))
        self.play(FadeIn(ohm, shift=UP * .2), run_time=.9); self.wait(2.2)
        self.play(FadeIn(kcl, shift=UP * .2), run_time=.9); self.wait(3.2)
        self.play(FadeIn(kvl, shift=UP * .2), run_time=.9); self.wait(3.0)
        r = resistor(P(-2, -3.0), P(2, -3.0), YEL)
        pm = VGroup(tex("+", 40, YEL).move_to(P(-2.3, -2.6)), tex("-", 40, YEL).move_to(P(2.3, -2.6)),
                    Arrow(P(-3.4, -3.0), P(-2.1, -3.0), buff=0, color=YEL, stroke_width=5), tex("I", 36, YEL).move_to(P(-2.8, -2.6)))
        self.play(FadeIn(r), FadeIn(pm)); self.wait(3)


class VDivider(Scene):
    """직렬: 12V, 2Ω, 4Ω → 4Ω에 8V."""
    def construct(self):
        h = head("전압 분배 (직렬)", BLU)
        xl, xr, yt, yb = -3.0, 1.0, 1.3, -1.6
        n = VGroup(vsrc(P(xl, yb), P(xl, yt), r"12\,\mathrm V"), resistor(P(xl, yt), P(xr, yt)), resistor(P(xr, yt), P(xr, yb)), wire(P(xl, yb), P(xr, yb)))
        labs = VGroup(rl(r"2\,\Omega", P(-1, yt + .5)), rl(r"4\,\Omega", P(xr + .75, 0)))
        self.play(FadeIn(h), Create(n), FadeIn(labs), run_time=1.6); self.wait(1.5)
        e = tex(r"V_{4\Omega} = 12 \times \frac{4}{2+4}", 52).move_to(P(4.3, .6))
        r = tex(r"= 8\,\mathrm V", 60, YEL).next_to(e, DOWN, .4)
        self.play(Write(e), Indicate(n[2], color=YEL), run_time=1.4); self.wait(1.2)
        self.play(FadeIn(r, scale=1.2)); self.wait(2.5)


class CDivider(Scene):
    """병렬: 6A → 3Ω 4A, 6Ω 2A. 분자는 반대편 저항."""
    def construct(self):
        h = head("전류 분배 (병렬)", GRN)
        xs, x1, x2, yt, yb = -4.2, -1.8, .6, 1.3, -1.6
        n = VGroup(isrc(P(xs, yb), P(xs, yt), r"6\,\mathrm A"), wire(P(xs, yt), P(x2, yt)), wire(P(xs, yb), P(x2, yb)),
                   resistor(P(x1, yt), P(x1, yb)), resistor(P(x2, yt), P(x2, yb)))
        labs = VGroup(rl(r"3\,\Omega", P(x1 + .7, 0)), rl(r"6\,\Omega", P(x2 + .7, 0)))
        self.play(FadeIn(h), Create(n), FadeIn(labs), run_time=1.6); self.wait(1.5)
        a1 = Arrow(P(x1 - .45, .9), P(x1 - .45, -.3), buff=0, color=YEL, stroke_width=9)
        a2 = Arrow(P(x2 - .45, .9), P(x2 - .45, .1), buff=0, color=MUTE, stroke_width=4)
        t = kr("작은 저항 쪽으로 더 많이", 30, YEL).move_to(P(-1.6, -2.4))
        self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(t)); self.wait(2.5)
        e = tex(r"I_{3\Omega} = 6 \times \frac{6}{3+6}", 50).move_to(P(4.3, .7))
        r = tex(r"= 4\,\mathrm A", 60, YEL).next_to(e, DOWN, .4)
        self.play(Write(e), run_time=1.3)
        box = SurroundingRectangle(e[0][6], color=RED, buff=.08)
        self.play(Create(box), FadeIn(r, scale=1.2)); self.wait(2.0)
        rule = VGroup(kr("직렬: 자기 저항", 32, BLU), kr("병렬: 반대편 저항", 32, GRN)).arrange(DOWN, buff=.3, aligned_edge=LEFT).move_to(P(4.3, -2.0))
        self.play(FadeIn(rule, shift=UP * .2)); self.wait(3)


class Nodal(Scene):
    """마디 해석: 기준 마디 0V → 마디 전압 V → KCL → V = 6V."""
    def construct(self):
        h = head("마디 해석", GRN)
        n = nodal_net().scale(.9).shift(LEFT * 2.6 + DOWN * .2)
        steps = VGroup(*[kr(s, 28, c) for s, c in (("① 기준 마디 = 0V", MUTE), ("② 마디 전압 V", YEL), ("③ KCL: 나가는 전류 합 = 0", GRN))]
                       ).arrange(DOWN, buff=.35, aligned_edge=LEFT).move_to(P(3.9, 1.3))
        self.play(FadeIn(h), Create(n[0]), FadeIn(n[1]), run_time=1.5)
        self.play(FadeIn(n[2]), FadeIn(steps[0])); self.wait(1.2)
        self.play(FadeIn(n[3], scale=1.4), FadeIn(steps[1])); self.wait(1.2)
        self.play(FadeIn(steps[2])); self.wait(4.0)
        e = tex(r"\frac{V-12}{2} + \frac{V}{6} + \frac{V}{3} = 0", 46).move_to(P(3.6, -.6))
        self.play(Write(e), run_time=1.8); self.wait(4.5)
        e2 = tex(r"3V - 36 + V + 2V = 0", 42, MUTE).next_to(e, DOWN, .4)
        r = tex(r"V = 6\,\mathrm V", 60, YEL).next_to(e2, DOWN, .4)
        self.play(FadeIn(e2, shift=UP * .2)); self.wait(1.0)
        self.play(FadeIn(r, scale=1.2)); self.wait(3)


class NodalMatrix(Scene):
    """n개 마디 → n−1개 식, 컨덕턴스 행렬 규칙."""
    def construct(self):
        h = head("마디 n개 → 식 n−1개", GRN)
        self.play(FadeIn(h)); self.wait(3.0)
        G = Matrix([["G_{11}", "-G_{12}"], ["-G_{21}", "G_{22}"]], element_to_mobject_config={"font_size": 60}, h_buff=1.9)
        m = VGroup(G, Matrix([["V_1"], ["V_2"]], element_to_mobject_config={"font_size": 60}), tex("=", 60),
                   Matrix([["I_1"], ["I_2"]], element_to_mobject_config={"font_size": 60})).arrange(RIGHT, buff=.3).shift(UP * .3)
        self.play(Write(m), run_time=1.8); self.wait(1.5)
        en = G.get_entries()
        d = VGroup(*[SurroundingRectangle(en[i], color=YEL, buff=.1) for i in (0, 3)])
        o = VGroup(*[SurroundingRectangle(en[i], color=RED, buff=.1) for i in (1, 2)])
        t1 = kr("대각선: 그 마디에 붙은 컨덕턴스 합", 30, YEL).move_to(P(0, -1.9))
        t2 = kr("옆자리: 사이 컨덕턴스에 빼기", 30, RED).move_to(P(0, -2.6))
        self.play(Create(d), FadeIn(t1)); self.wait(2.5)
        self.play(Create(o), FadeIn(t2)); self.wait(3)


class Mesh(Scene):
    """망 해석: I₁, I₂, 공유 4Ω엔 I₁−I₂ → 3A, 1.5A."""
    def construct(self):
        h = head("망 해석", ORG)
        n = mesh_net().scale(.85).shift(UP * .55)
        self.play(FadeIn(h), Create(n[0]), FadeIn(n[1]), run_time=1.6)
        l1 = loop_arrow(P(-1.7, .4), BLU, "I_1"); l2 = loop_arrow(P(1.7, .4), GRN, "I_2")
        self.play(Create(l1), Create(l2), run_time=1.2); self.wait(4.5)
        sh = n[0][2]
        d = tex(r"I_1 - I_2", 40, YEL).move_to(P(-.95, -1.3))
        self.play(Indicate(sh, color=YEL, scale_factor=1.15), FadeIn(d)); self.wait(4.0)
        e1 = tex(r"6I_1 - 4I_2 = 12", 46, BLU); e2 = tex(r"8I_2 - 4I_1 = 0", 46, GRN)
        eqs = VGroup(e1, e2).arrange(RIGHT, buff=1.2).move_to(P(0, -2.25))
        self.play(Write(e1), run_time=1.2); self.play(Write(e2), run_time=1.2); self.wait(3.0)
        r = tex(r"I_1 = 3\,\mathrm A,\quad I_2 = 1.5\,\mathrm A", 50, YEL).move_to(P(0, -3.25))
        self.play(FadeIn(r, scale=1.15)); self.wait(4)


class MeshMatrix(Scene):
    """망 행렬: 대각선 6, 8 · 옆자리 −4."""
    def construct(self):
        h = head("망 해석도 같은 규칙", ORG)
        G = Matrix([["6", "-4"], ["-4", "8"]], element_to_mobject_config={"font_size": 66}, h_buff=1.6)
        m = VGroup(G, Matrix([["I_1"], ["I_2"]], element_to_mobject_config={"font_size": 66}), tex("=", 66),
                   Matrix([["12"], ["0"]], element_to_mobject_config={"font_size": 66})).arrange(RIGHT, buff=.3).shift(UP * .4)
        self.play(FadeIn(h), Write(m), run_time=1.8)
        en = G.get_entries()
        d = VGroup(*[SurroundingRectangle(en[i], color=YEL, buff=.12) for i in (0, 3)])
        o = VGroup(*[SurroundingRectangle(en[i], color=RED, buff=.12) for i in (1, 2)])
        t1 = kr("대각선: 고리 안 저항 합", 30, YEL).move_to(P(0, -1.8)); t2 = kr("옆자리: 같이 쓰는 저항에 빼기", 30, RED).move_to(P(0, -2.5))
        self.play(Create(d), FadeIn(t1)); self.wait(1.6)
        self.play(Create(o), FadeIn(t2)); self.wait(3)


class SourceTransform(Scene):
    """12V+직렬 3Ω ↔ 4A+병렬 3Ω, 6Ω 달면 둘 다 8V."""
    def construct(self):
        h = head("전원 변환", PUR)
        yt, yb = 1.1, -1.4
        L0 = VGroup(vsrc(P(-5.2, yb), P(-5.2, yt), r"12\,\mathrm V"), resistor(P(-5.2, yt), P(-3.2, yt)), wire(P(-3.2, yt), P(-2.8, yt)), wire(P(-5.2, yb), P(-2.8, yb)),
                    rl(r"3\,\Omega", P(-4.2, yt + .45)))
        R0 = VGroup(isrc(P(.6, yb), P(.6, yt), r"4\,\mathrm A", side=RIGHT), wire(P(.6, yt), P(4.2, yt)), wire(P(.6, yb), P(4.2, yb)),
                    resistor(P(2.6, yt), P(2.6, yb)), rl(r"3\,\Omega", P(3.2, -.15)))
        self.play(FadeIn(h), Create(L0), run_time=1.4); self.wait(3.0)
        arr = DoubleArrow(P(-1.6, -.15), P(-.1, -.15), color=YEL, stroke_width=5)
        self.play(GrowFromCenter(arr), Create(R0), run_time=1.4); self.wait(1.5)
        f = tex(r"I = \frac{V}{R} = \frac{12}{3} = 4\,\mathrm A", 44, YEL).move_to(P(-1.2, -2.5))
        self.play(Write(f), run_time=1.2); self.wait(3.0)
        ld1 = VGroup(resistor(P(-2.8, yt), P(-2.8, yb), GRN), rl(r"6\,\Omega", P(-2.2, -.15), GRN))
        ld2 = VGroup(resistor(P(4.2, yt), P(4.2, yb), GRN), rl(r"6\,\Omega", P(4.8, -.15), GRN))
        v1 = tex(r"8\,\mathrm V", 46, YEL).move_to(P(-2.8, 1.75)); v2 = tex(r"8\,\mathrm V", 46, YEL).move_to(P(4.2, 1.75))
        self.play(FadeOut(f), FadeIn(ld1), FadeIn(ld2)); self.play(FadeIn(v1), FadeIn(v2)); self.wait(3.0)
        g = tex(r"3\parallel 6 = 2\,\Omega,\quad 4\,\mathrm A \times 2\,\Omega = 8\,\mathrm V", 44, GRN).move_to(P(0, -2.6))
        self.play(Write(g), run_time=1.4); self.wait(3.5)
        nx = kr("반복하면 → 테브난 · 노턴 등가 회로", 30, MUTE).move_to(P(0, -3.4))
        self.play(FadeIn(nx)); self.wait(3)


class Dependent(Scene):
    """종속 전원: 다이아몬드, 식 하나 더, 2Iₓ = V/3 → V = 6V, 끄지 않기."""
    def construct(self):
        h = head("종속 전원", RED)
        n = nodal_net("D").scale(.9).shift(LEFT * 2.6 + DOWN * .2)
        self.play(FadeIn(h), Create(n[0]), FadeIn(n[1]), FadeIn(n[2]), FadeIn(n[3]), run_time=1.6)
        dia = n[0][-1][2]
        self.play(Indicate(dia, color=YEL, scale_factor=1.3)); self.wait(1.2)
        ex = VGroup(kr("트랜지스터", 28, PUR), kr("연산 증폭기 모델", 28, PUR)).arrange(DOWN, buff=.3).move_to(P(4.0, 1.5))
        self.play(FadeIn(ex, shift=UP * .2)); self.wait(5.5)
        ix = VGroup(Arrow(P(-2.95, .5), P(-2.95, -.5), buff=0, color=BLU, stroke_width=5), tex("I_x", 36, BLU).move_to(P(-3.35, 0)))
        self.play(FadeOut(ex), FadeIn(ix))
        c = tex(r"I_x = \frac{V}{6}", 50, BLU).move_to(P(4.0, 1.9))
        tag = kr("+ 식 하나", 28, BLU).next_to(c, DOWN, .3)
        self.play(Write(c), FadeIn(tag)); self.wait(7.0)
        e = tex(r"2I_x = \frac{V}{3}", 50, PUR).move_to(P(4.0, -.5))
        r = tex(r"V = 6\,\mathrm V", 58, YEL).next_to(e, DOWN, .5)
        self.play(Write(e)); self.wait(2.0); self.play(FadeIn(r, scale=1.2)); self.wait(3.5)
        warn = kr("전원 끌 때도 종속 전원은 그대로!", 34, RED).to_edge(DOWN, buff=.35)
        self.play(FadeIn(warn, shift=UP * .2), Indicate(dia, color=RED)); self.wait(3)


class Choose(Scene):
    """마디냐 망이냐: 식 개수, 전류원/전압원, 슈퍼마디."""
    def construct(self):
        h = head("마디냐, 망이냐")
        self.play(FadeIn(h)); self.wait(2.0)
        hdr = VGroup(kr("", 30), kr("마디 해석", 34, GRN), kr("망 해석", 34, ORG))
        r1 = VGroup(kr("식 개수", 30, MUTE), kr("마디 수 − 1", 30), kr("망 개수", 30))
        r2 = VGroup(kr("편한 회로", 30, MUTE), kr("전류원 많을 때", 30), kr("전압원 많을 때", 30))
        r3 = VGroup(kr("까다로운 곳", 30, MUTE), kr("슈퍼마디", 30, YEL), kr("슈퍼망", 30, YEL))
        rows = [hdr, r1, r2, r3]
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                c.move_to(P(-4.0 + j * 4.0, 1.7 - i * 1.3))
        self.play(FadeIn(hdr)); self.play(FadeIn(r1)); self.wait(3.0)
        pick = kr("→ 적은 쪽", 28, YEL).move_to(P(4.0, r1[2].get_y() - .5))
        self.play(FadeIn(r2), FadeIn(pick)); self.wait(5.0)
        self.play(FadeIn(r3)); self.wait(5.0)
        s = VGroup(tex(r"V_a - V_b = V_s", 42, YEL), kr("+ 묶어서 KCL 하나", 30, YEL)).arrange(RIGHT, buff=.6).move_to(P(0, -2.9))
        self.play(FadeIn(s, shift=UP * .2)); self.wait(4)


class Check(Scene):
    """검산: 3A = 1A + 2A, 36W = 18 + 6 + 12."""
    def construct(self):
        h = head("검산하는 습관")
        n = nodal_net().scale(.8).shift(LEFT * 2.8 + DOWN * .2)
        self.play(FadeIn(h), FadeIn(n), run_time=1.2); self.wait(2.0)
        a = VGroup(Arrow(P(-5.4, 1.75), P(-3.5, 1.75), buff=0, color=GRN, stroke_width=5), tex(r"3\,\mathrm A", 38, GRN).move_to(P(-4.45, 2.15)))
        i = tex(r"\frac{12-6}{2} = 3\,\mathrm A", 44, GRN).move_to(P(3.6, 1.6))
        self.play(GrowArrow(a[0]), FadeIn(a[1]), Write(i)); self.wait(3.5)
        o = tex(r"1\,\mathrm A + 2\,\mathrm A = 3\,\mathrm A\ \checkmark", 44, GRN).move_to(P(3.6, .5))
        self.play(Write(o)); self.wait(3.0)
        p = tex(r"36\,\mathrm W = 18 + 6 + 12\,\mathrm W", 44, YEL).move_to(P(3.6, -.8))
        p2 = tex(r"P = 12\,\mathrm V \times 3\,\mathrm A", 36, MUTE).next_to(p, DOWN, .3)
        self.play(Write(p), FadeIn(p2)); self.wait(6)


class Summary(Scene):
    def construct(self):
        h = head("정리")
        items = VGroup(*[kr(s, 34, c) for s, c in (
            ("단순하면 → 분배 (직렬 자기 · 병렬 반대편)", BLU),
            ("복잡하면 → 마디 해석 또는 망 해석 (식 적은 쪽)", GRN),
            ("그 전에 → 전원 변환으로 회로 줄이기", PUR),
            ("종속 전원 → 식 하나 더, 절대 끄지 않기", RED),
            ("마지막 → KCL·전력으로 검산", YEL))]).arrange(DOWN, buff=.45, aligned_edge=LEFT)
        self.play(FadeIn(h))
        for it in items:
            self.play(FadeIn(it, shift=UP * .15), run_time=.6); self.wait(.5)
        self.wait(4)
