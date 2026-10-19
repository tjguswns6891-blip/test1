# 회로이론 3분 정리(테브난·노턴·중첩) 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 예제 회로: 12V — 6Ω — 마디 a — (3Ω ∥ 2A 전류원) — 단자 a·b. 답: Vth 8V, Rth 2Ω, In 4A, Pmax 8W.
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


# ---------- 회로 부품 ----------
def wire(a, b, c=INK, w=4):
    return Line(np.array(a, float), np.array(b, float), color=c, stroke_width=w)


def res(a, b, c=INK, n=6, amp=.17):
    """a→b 지그재그 저항 (가로·세로 모두)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a; L = np.linalg.norm(d); u = d / L; nrm = np.array([-u[1], u[0], 0])
    m0, m1 = .5 * L - .55, .5 * L + .55
    pts = [a, a + u * m0]
    for k in range(n):
        pts.append(a + u * (m0 + (k + .5) * (m1 - m0) / n) + nrm * (amp if k % 2 == 0 else -amp))
    pts += [a + u * m1, b]
    return VMobject(color=c, stroke_width=4).set_points_as_corners(pts)


def vsrc(bot, top, c=INK):
    """세로 전압원 (원 + +/−)."""
    bot, top = np.array(bot, float), np.array(top, float); m = (bot + top) / 2
    g = VGroup(wire(bot, m + DOWN * .45, c), wire(m + UP * .45, top, c), Circle(.45, color=c, stroke_width=4).move_to(m))
    g.add(tex("+", 34, c).move_to(m + UP * .2), tex("-", 34, c).move_to(m + DOWN * .2))
    return g


def isrc(bot, top, c=INK):
    """세로 전류원 (원 + 위 화살표)."""
    bot, top = np.array(bot, float), np.array(top, float); m = (bot + top) / 2
    g = VGroup(wire(bot, m + DOWN * .45, c), wire(m + UP * .45, top, c), Circle(.45, color=c, stroke_width=4).move_to(m))
    g.add(Arrow(m + DOWN * .3, m + UP * .3, buff=0, color=c, stroke_width=5, max_tip_length_to_length_ratio=.4))
    return g


def term(p, s):
    d = Circle(.09, color=INK, fill_color=BG, fill_opacity=1, stroke_width=4).move_to(p)
    return VGroup(d, kr(s, 30, INK).next_to(d, RIGHT, .15))


# 좌표: 아래 줄 y=-1.3, 위 줄 y=1.3
Y0, Y1 = -1.3, 1.3
XV, XN, XI, XT = -4.0, -1.2, 1.0, 3.2


def circuit(vs="on", cs="on", load=False, labels=True):
    """예제 회로. vs/cs: 'on'·'short'·'open'·'off'(없음). 부품마다 이름으로 꺼낼 수 있게 dict 로 돌려준다."""
    P = {}
    P["top1"] = wire((XV, Y1, 0), (XV + .5, Y1, 0))
    P["R1"] = res((XV + .5, Y1, 0), (XN, Y1, 0))
    P["top2"] = wire((XN, Y1, 0), (XT, Y1, 0))
    P["bot"] = wire((XV, Y0, 0), (XT, Y0, 0))
    P["R2"] = res((XN, Y1, 0), (XN, Y0, 0))
    if vs == "on":
        P["VS"] = vsrc((XV, Y0, 0), (XV, Y1, 0))
    elif vs == "short":
        P["VS"] = wire((XV, Y0, 0), (XV, Y1, 0), YEL, 6)
    elif vs == "open":
        P["VS"] = VGroup(wire((XV, Y0, 0), (XV, -.35, 0)), wire((XV, .35, 0), (XV, Y1, 0)))
    if cs == "on":
        P["IS"] = isrc((XI, Y0, 0), (XI, Y1, 0))
    elif cs == "short":
        P["IS"] = wire((XI, Y0, 0), (XI, Y1, 0), YEL, 6)
    elif cs == "open":
        P["IS"] = VGroup(wire((XI, Y0, 0), (XI, -.35, 0), MUTE), wire((XI, .35, 0), (XI, Y1, 0), MUTE),
                         kr("개방", 24, YEL).move_to((XI + .5, 0, 0)))
    P["a"] = term((XT, Y1, 0), "a"); P["b"] = term((XT, Y0, 0), "b")
    if labels:
        if vs == "on":
            P["lVS"] = tex(r"12\,\mathrm{V}", 40, YEL).next_to((XV - .45, 0, 0), LEFT, .15)
        elif vs == "short":
            P["lVS"] = kr("단락", 26, YEL).next_to((XV, 0, 0), LEFT, .2)
        P["lR1"] = tex(r"6\,\Omega", 40, ORG).next_to((XV / 2 + XN / 2 + .25, Y1 + .2, 0), UP, .1)
        P["lR2"] = tex(r"3\,\Omega", 40, ORG).next_to((XN + .25, 0, 0), RIGHT, .1)
        if cs == "on":
            P["lIS"] = tex(r"2\,\mathrm{A}", 40, BLU).next_to((XI + .45, 0, 0), RIGHT, .15)
    if load:
        P["L1"] = wire((XT, Y1, 0), (XT + 1.3, Y1, 0), MUTE); P["L2"] = wire((XT, Y0, 0), (XT + 1.3, Y0, 0), MUTE)
        P["RL"] = res((XT + 1.3, Y1, 0), (XT + 1.3, Y0, 0), GRN)
        P["lRL"] = tex(r"R_L", 40, GRN).next_to((XT + 1.5, 0, 0), RIGHT, .1)
    return P


def grp(P, order=None):
    return VGroup(*[P[k] for k in (order or P)])


def thev_eq(V="8", R="2", x0=-1.6):
    """테브난 등가: 전압원 + 직렬 저항 + 단자."""
    g = VGroup(vsrc((x0, Y0, 0), (x0, Y1, 0), YEL), wire((x0, Y1, 0), (x0 + .5, Y1, 0)),
               res((x0 + .5, Y1, 0), (x0 + 2.6, Y1, 0), ORG), wire((x0 + 2.6, Y1, 0), (x0 + 3.2, Y1, 0)),
               wire((x0, Y0, 0), (x0 + 3.2, Y0, 0)), term((x0 + 3.2, Y1, 0), "a"), term((x0 + 3.2, Y0, 0), "b"))
    u = lambda v, unit: v + (r"\," + unit if v[0].isdigit() else "")
    g.add(tex(u(V, r"\mathrm{V}"), 44, YEL).next_to((x0 - .45, 0, 0), LEFT, .15),
          tex(u(R, r"\Omega"), 44, ORG).next_to((x0 + 1.55, Y1 + .2, 0), UP, .1))
    return g


def norton_eq(I="4", R="2", x0=-1.4):
    g = VGroup(isrc((x0, Y0, 0), (x0, Y1, 0), BLU), wire((x0, Y1, 0), (x0 + 3.2, Y1, 0)),
               res((x0 + 1.6, Y1, 0), (x0 + 1.6, Y0, 0), ORG), wire((x0, Y0, 0), (x0 + 3.2, Y0, 0)),
               term((x0 + 3.2, Y1, 0), "a"), term((x0 + 3.2, Y0, 0), "b"))
    u = lambda v, unit: v + (r"\," + unit if v[0].isdigit() else "")
    g.add(tex(u(I, r"\mathrm{A}"), 44, BLU).next_to((x0 - .45, 0, 0), LEFT, .15),
          tex(u(R, r"\Omega"), 44, ORG).next_to((x0 + 1.85, 0, 0), RIGHT, .1))
    return g


class Hook(Scene):
    """복잡한 회로 → 박스 → 전압원 하나 + 저항 하나."""
    def construct(self):
        P = circuit()
        c = grp(P).shift(UP * .2)
        self.play(Create(c), run_time=1.3)
        box = SurroundingRectangle(VGroup(*[P[k] for k in P if k not in ("a", "b")]), color=BLU, buff=.25, corner_radius=.15)
        self.play(Create(box), run_time=.5)
        eq = thev_eq().shift(UP * .2)
        lab = kr("저항 하나로 끝", 44, YEL).to_edge(DOWN, buff=.6)
        self.play(ReplacementTransform(VGroup(c, box), eq), run_time=1.0)
        self.play(FadeIn(lab, shift=UP * .2), Circumscribe(eq[2], color=YEL), run_time=.9)
        self.wait(3)


class Three(Scene):
    """세 가지 카드: 중첩 · 테브난 · 노턴."""
    def construct(self):
        items = [("중첩", "전원 하나씩", GRN), ("테브난", "전압원 + 저항", YEL), ("노턴", "전류원 + 저항", BLU)]
        cards = VGroup()
        for t, s, c in items:
            cards.add(card(VGroup(kr(t, 54, c), kr(s, 30, MUTE)).arrange(DOWN, buff=.35), c, .45))
        cards.arrange(RIGHT, buff=.5)
        self.play(LaggedStart(*[FadeIn(k, shift=UP * .3) for k in cards], lag_ratio=.35), run_time=1.5)
        self.wait(1.5)
        one = kr("회로 하나로 전부", 44, INK).to_edge(DOWN, buff=.7)
        self.play(FadeIn(one), run_time=.5)
        self.wait(4)


class Circuit(Scene):
    """오늘의 회로: 부품을 하나씩 그리고, 부하 R_L 을 단다."""
    def construct(self):
        P = circuit(load=True)
        sh = UP * .1 + LEFT * .5
        for k in P: P[k].shift(sh)
        steps = [(["VS", "lVS", "top1", "R1", "lR1"], 1.2), (["R2", "lR2", "top2", "bot"], 1.0),
                 (["IS", "lIS"], .8), (["a", "b"], .5)]
        waits = [2.6, 2.2, 2.4, .3]
        for (ks, rt), w in zip(steps, waits):
            self.play(*[Create(P[k]) if k[0] != "l" else FadeIn(P[k]) for k in ks], run_time=rt)
            self.wait(w)
        self.play(Create(P["L1"]), Create(P["L2"]), Create(P["RL"]), FadeIn(P["lRL"]), run_time=.9)
        q = tex(r"I_L = \,?", 50, GRN).move_to(P["RL"].get_center() + DOWN * 2.0)
        self.play(FadeIn(q), Indicate(P["RL"], color=GRN), run_time=.8)
        self.wait(3)
        for v in ["1", "4", "6"]:
            t = tex(r"R_L=" + v + r"\,\Omega", 36, MUTE).next_to(q, DOWN, .3)
            self.play(FadeIn(t, shift=UP * .1), run_time=.3); self.wait(.5); self.play(FadeOut(t), run_time=.2)
        self.wait(2)


class KillRule(Scene):
    """전원 끄는 법: 전압원 → 단락, 전류원 → 개방."""
    def construct(self):
        self.add(head("전원 끄는 법", GRN))
        def pair(x, src, after, name, unit, how):
            a = src((x - 1.3, -1.0, 0), (x - 1.3, 1.2, 0)); b = after(x + 1.3)
            t = VGroup(kr(name, 36), tex(unit, 38, MUTE)).arrange(RIGHT, buff=.25).next_to(a, DOWN, .4)
            ar = Arrow((x - .6, .1, 0), (x + .6, .1, 0), color=MUTE)
            h = kr(how, 36, YEL).next_to(b, DOWN, .4)
            return a, t, ar, b, h
        L = pair(-3.4, vsrc, lambda x: wire((x, -1.0, 0), (x, 1.2, 0), YEL, 7), "전압원", r"0\,\mathrm{V}", "단락 (전선)")
        R = pair(3.4, isrc, lambda x: VGroup(wire((x, -1.0, 0), (x, -.3, 0)), wire((x, .5, 0), (x, 1.2, 0))), "전류원", r"0\,\mathrm{A}", "개방 (떼기)")
        self.play(Create(L[0]), FadeIn(L[1]), run_time=.8); self.wait(1.0)
        self.play(GrowArrow(L[2]), Create(L[3]), FadeIn(L[4]), run_time=.9); self.wait(2.6)
        self.play(Create(R[0]), FadeIn(R[1]), run_time=.8)
        self.play(GrowArrow(R[2]), Create(R[3]), FadeIn(R[4]), run_time=.9)
        self.wait(5)


class Sup1(Scene):
    """중첩 1: 전류원 개방 → 12V 만, 분압 4V."""
    def construct(self):
        self.add(head("① 12V만 남기기", GRN))
        P = circuit(cs="open")
        c = grp(P).shift(UP * .1 + LEFT * 1.4)
        self.play(Create(c), run_time=1.2)
        f = VGroup(tex(r"V_1 = 12 \times \frac{3}{6+3}", 48), tex(r"= 4\,\mathrm{V}", 60, YEL)).arrange(DOWN, buff=.3, aligned_edge=LEFT)
        f.to_edge(RIGHT, buff=.4).shift(UP * .1)
        self.play(Indicate(P["R1"], color=ORG), Indicate(P["R2"], color=ORG), run_time=1.0)
        self.play(Write(f[0]), run_time=1.0); self.wait(1.2)
        self.play(FadeIn(f[1], shift=UP * .2), run_time=.6)
        self.wait(4)


class Sup2(Scene):
    """중첩 2: 전압원 단락 → 2A 만, 6∥3 = 2Ω, 4V."""
    def construct(self):
        self.add(head("② 2A만 남기기", GRN))
        P = circuit(vs="short")
        c = grp(P).shift(UP * .1 + LEFT * 1.4)
        self.play(Create(c), run_time=1.2)
        self.play(Indicate(P["VS"], color=YEL, scale_factor=1.05), run_time=.8)
        self.wait(.8)
        f = VGroup(tex(r"6 \parallel 3 = 2\,\Omega", 48), tex(r"V_2 = 2 \times 2", 48), tex(r"= 4\,\mathrm{V}", 60, YEL)).arrange(DOWN, buff=.3, aligned_edge=LEFT)
        f.to_edge(RIGHT, buff=.4).shift(UP * .1)
        self.play(Write(f[0]), run_time=.8); self.wait(1.4)
        self.play(Write(f[1]), run_time=.7)
        self.play(FadeIn(f[2], shift=UP * .2), run_time=.6)
        self.wait(4)


class SupSum(Scene):
    """중첩 합: 4 + 4 = 8V. 전력은 중첩 안 됨."""
    def construct(self):
        s = tex(r"V_{ab} = 4 + 4 = 8\,\mathrm{V}", 84, YEL).shift(UP * 1.2)
        self.play(Write(s), run_time=1.2)
        self.play(Circumscribe(s, color=YEL), run_time=.8)
        self.wait(2.2)
        w = VGroup(kr("전력은 더하면 틀림", 40, RED),
                   tex(r"P \neq P_1 + P_2", 60, RED),
                   tex(r"P \propto I^2:\ (I_1+I_2)^2 \neq I_1^2 + I_2^2", 44, MUTE)).arrange(DOWN, buff=.35).shift(DOWN * 1.4)
        self.play(FadeIn(w[0]), Write(w[1]), run_time=1.0)
        self.wait(1.8)
        self.play(FadeIn(w[2]), run_time=.6)
        self.wait(5)


class Thev(Scene):
    """테브난: 두 단자에서 본 회로 = Vth + Rth. Vth = 개방 전압 8V."""
    def construct(self):
        self.add(head("테브난 정리", YEL))
        P = circuit()
        c = grp(P).scale(.7).shift(LEFT * 2.9 + DOWN * .2)
        eq = VGroup(*thev_eq("V_{th}", "R_{th}", 0).submobjects).scale(.8).shift(RIGHT * 2.6 + DOWN * .2)
        arr = Arrow(LEFT * .2 + DOWN * .2, RIGHT * 1.1 + DOWN * .2, color=MUTE)
        self.play(Create(c), run_time=1.0)
        self.play(GrowArrow(arr), FadeIn(eq), run_time=1.0)
        self.wait(3.5)
        self.play(FadeOut(VGroup(arr, eq)), c.animate.scale(.95).move_to(LEFT * 1.9 + DOWN * .2), run_time=.8)
        v = tex(r"V_{th} = V_{oc} = 8\,\mathrm{V}", 54, YEL).to_edge(RIGHT, buff=.4).shift(UP * .4)
        oc = kr("개방 전압 (부하 뗌)", 30, MUTE).next_to(v, DOWN, .3)
        brace = DoubleArrow(P["a"][0].get_center() + RIGHT * .2, P["b"][0].get_center() + RIGHT * .2, color=YEL, buff=.15)
        self.play(GrowFromCenter(brace), Write(v), FadeIn(oc), run_time=1.0)
        self.wait(6)


class Rth(Scene):
    """Rth: 전원 끄기 → 6∥3 = 2Ω."""
    def construct(self):
        self.add(head("테브난 저항: 전원 끄고 들여다보기", YEL))
        P = circuit(vs="short", cs="open")
        c = grp(P).shift(LEFT * 1.4 + DOWN * .1)
        self.play(Create(c), run_time=1.2)
        eye = Arrow(RIGHT * 3.6 + DOWN * .1, RIGHT * 2.2 + DOWN * .1, color=GRN, stroke_width=8).shift(LEFT * 0)
        self.play(GrowArrow(eye), run_time=.5)
        self.wait(2.0)
        f = VGroup(tex(r"R_{th} = 6 \parallel 3", 50), tex(r"= \frac{6 \times 3}{6+3} = 2\,\Omega", 54, YEL)).arrange(DOWN, buff=.3, aligned_edge=LEFT)
        f.to_corner(DR, buff=.5)
        self.play(Write(f[0]), run_time=.8); self.wait(.6)
        self.play(Write(f[1]), run_time=1.0)
        self.wait(4)


class ThevDone(Scene):
    """완성: 8V + 2Ω, 부하 전류 공식과 표."""
    def construct(self):
        eq = VGroup(*thev_eq().submobjects)
        L = VGroup(wire((1.6, Y1, 0), (2.8, Y1, 0), MUTE), wire((1.6, Y0, 0), (2.8, Y0, 0), MUTE), res((2.8, Y1, 0), (2.8, Y0, 0), GRN),
                   tex(r"R_L", 40, GRN).next_to((3.0, 0, 0), RIGHT, .1))
        g = VGroup(eq, L).shift(LEFT * 2.6 + UP * .3)
        self.play(FadeIn(eq), run_time=.8)
        self.play(Circumscribe(eq, color=YEL), run_time=1.0)
        self.wait(2.5)
        self.play(Create(L), run_time=.8)
        f = tex(r"I_L = \frac{8}{2 + R_L}", 60, GRN).to_edge(RIGHT, buff=.6).shift(UP * 1.4)
        self.play(Write(f), run_time=1.0)
        self.wait(2.5)
        rows = VGroup()
        for r, i in [("2", "2"), ("6", "1")]:
            rows.add(tex(r"R_L = " + r + r"\,\Omega \ \Rightarrow\ I_L = " + i + r"\,\mathrm{A}", 44, INK))
        rows.arrange(DOWN, buff=.35).next_to(f, DOWN, .7)
        for k in rows:
            self.play(FadeIn(k, shift=UP * .15), run_time=.5); self.wait(1.3)
        self.wait(4)


class Norton(Scene):
    """노턴 등가, 단락 전류 2A + 2A = 4A."""
    def construct(self):
        self.add(head("노턴 정리", BLU))
        n = norton_eq("I_N", "R_N")
        self.play(FadeIn(n), run_time=.8)
        self.wait(4.0)
        self.play(FadeOut(n), run_time=.4)
        P = circuit()
        c = grp(P).shift(LEFT * 1.6 + DOWN * .1)
        sc = wire((XT - 1.6, Y1 - .1, 0), (XT - 1.6, Y0 - .1, 0), YEL, 7)
        self.play(Create(c), run_time=.9)
        self.play(Create(sc), FadeIn(kr("단락", 28, YEL).next_to(sc, RIGHT, .2)), run_time=.6)
        self.wait(2.0)
        x = Cross(P["R2"], stroke_color=RED, stroke_width=6).scale(.6)
        z = kr("3Ω: 전압 0 → 전류 0", 30, RED).to_edge(DOWN, buff=.6).shift(LEFT * 1.6)
        self.play(Create(x), FadeIn(z), run_time=.6)
        self.wait(3.0)
        f = VGroup(tex(r"\frac{12}{6} = 2\,\mathrm{A}", 46), tex(r"+\ 2\,\mathrm{A}", 46, BLU), tex(r"I_N = 4\,\mathrm{A}", 58, YEL)).arrange(DOWN, buff=.25, aligned_edge=LEFT)
        f.to_corner(UR, buff=.5).shift(DOWN * 1.0)
        self.play(Write(f[0]), run_time=.8); self.play(Write(f[1]), run_time=.6)
        self.play(FadeIn(f[2], shift=UP * .2), run_time=.6)
        self.wait(5)


class NortonCheck(Scene):
    """테브난 ⇄ 노턴: 4A × 2Ω = 8V, 전원 변환."""
    def construct(self):
        t = VGroup(*thev_eq().submobjects).scale(.8).shift(LEFT * 3.4 + UP * .4)
        n = VGroup(*norton_eq().submobjects).scale(.8).shift(RIGHT * 3.0 + UP * .4)
        arr = DoubleArrow(LEFT * .8 + UP * .4, RIGHT * .8 + UP * .4, color=MUTE)
        self.play(FadeIn(t), FadeIn(n), GrowFromCenter(arr), run_time=1.0)
        self.wait(1.0)
        f = tex(r"4\,\mathrm{A} \times 2\,\Omega = 8\,\mathrm{V}", 64, YEL).shift(DOWN * 2.0)
        self.play(Write(f), run_time=1.0)
        ok = kr("딱 맞음", 40, GRN).next_to(f, RIGHT, .4)
        self.play(FadeIn(ok, scale=1.3), run_time=.5)
        self.wait(3.0)
        tri = VGroup(tex(r"V_{oc}", 50, YEL), tex(r"I_{sc}", 50, BLU), tex(r"R_{th}", 50, ORG)).arrange(RIGHT, buff=1.0)
        rel = tex(r"V_{oc} = I_{sc}\,R_{th}", 56).next_to(tri, DOWN, .35)
        g = VGroup(tri, rel).shift(DOWN * 2.0)
        self.play(FadeOut(VGroup(f, ok)), FadeIn(g), run_time=.8)
        self.wait(4.0)
        st = kr("전원 변환", 44, INK).next_to(arr, UP, .4)
        self.play(FadeIn(st), Indicate(arr), run_time=.8)
        self.wait(4)


class When(Scene):
    """언제 무엇을: 3줄 표 + 종속 전원 주의."""
    def construct(self):
        self.add(head("시험에선 뭘 먼저?"))
        rows = [("전원이 여러 개", "중첩", GRN), ("부하만 바뀜 · 최대 전력", "테브난", YEL), ("전류원 · 병렬이 많음", "노턴 · 전원 변환", BLU)]
        g = VGroup()
        for a, b, c in rows:
            g.add(VGroup(kr(a, 36, INK), kr("→", 36, MUTE), kr(b, 40, c)).arrange(RIGHT, buff=.4))
        g.arrange(DOWN, buff=.55, aligned_edge=LEFT).shift(UP * .3)
        self.wait(1.5)
        for k, w in zip(g, [2.0, 3.0, 3.0]):
            self.play(FadeIn(k, shift=RIGHT * .3), run_time=.5); self.wait(w)
        warn = card(VGroup(kr("종속 전원은 끄지 않기", 36, RED), tex(r"R_{th} = \frac{1\,\mathrm{V}}{I_{test}}", 48)).arrange(RIGHT, buff=.6), RED)
        warn.to_edge(DOWN, buff=.5)
        self.play(FadeIn(warn, shift=UP * .2), run_time=.6)
        self.wait(7)


class MaxPower(Scene):
    """P(R_L) 곡선, R_L = 2Ω 에서 8W 최대, 효율 50%."""
    def construct(self):
        self.add(head("최대 전력 전달", YEL))
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 9, 2], x_length=7.5, y_length=4.2, tips=False,
                  axis_config={"color": MUTE, "include_numbers": True, "font_size": 28}).shift(LEFT * 1.8 + DOWN * .5)
        xl = tex(r"R_L\,(\Omega)", 34, MUTE).next_to(ax.x_axis, DOWN, .3).shift(RIGHT * 3)
        yl = tex(r"P\,(\mathrm{W})", 34, MUTE).next_to(ax.y_axis, UP, .2)
        cur = ax.plot(lambda r: 64 * r / (2 + r) ** 2, x_range=[0, 10], color=GRN, stroke_width=6)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        self.play(Create(cur), run_time=1.5)
        self.wait(1.0)
        p = ax.c2p(2, 8); d = Dot(p, .12, color=YEL)
        vl = DashedLine(ax.c2p(2, 0), p, color=YEL)
        self.play(FadeIn(d, scale=2), Create(vl), run_time=.6)
        f = VGroup(tex(r"R_L = R_{th} = 2\,\Omega", 46, YEL), tex(r"P_{max} = \frac{V_{th}^2}{4R_{th}} = \frac{64}{8}", 44),
                   tex(r"= 8\,\mathrm{W}", 58, YEL)).arrange(DOWN, buff=.3, aligned_edge=LEFT).to_edge(RIGHT, buff=.3).shift(UP * .5)
        self.play(Write(f[0]), run_time=.8); self.wait(2.2)
        self.play(Write(f[1]), run_time=1.0); self.wait(1.0)
        self.play(FadeIn(f[2]), run_time=.5); self.wait(2.0)
        e = kr("효율 50% (절반은 열)", 34, RED).next_to(f, DOWN, .5)
        self.play(FadeIn(e), run_time=.5)
        self.wait(5)


class Mistakes(Scene):
    """자주 틀리는 3가지."""
    def construct(self):
        self.add(head("자주 틀리는 3가지", RED))
        items = [("전압원을 떼어 버림", "→ 단락"), ("전력을 중첩으로 더함", "→ V·I 먼저 더하기"), ("종속 전원까지 끔", "→ 그대로 두기")]
        g = VGroup()
        for i, (a, b) in enumerate(items):
            g.add(VGroup(kr("✕", 40, RED), kr(a, 38, INK), kr(b, 34, GRN)).arrange(RIGHT, buff=.4))
        g.arrange(DOWN, buff=.6, aligned_edge=LEFT)
        self.wait(1.8)
        for k, w in zip(g, [3.0, 3.6, 3.0]):
            self.play(FadeIn(k, shift=RIGHT * .3), run_time=.5); self.wait(w)
        self.wait(3)


class Summary(Scene):
    """정리: 세 카드 + V = IR."""
    def construct(self):
        items = [("중첩", "하나씩 켜서 더하기", GRN), ("테브난", "개방 전압 + 저항", YEL), ("노턴", "단락 전류 + 저항", BLU)]
        cards = VGroup(*[card(VGroup(kr(t, 50, c), kr(s, 28, MUTE)).arrange(DOWN, buff=.3), c, .4) for t, s, c in items]).arrange(RIGHT, buff=.45).shift(UP * .9)
        self.play(FadeIn(cards[0], shift=UP * .2), run_time=.6); self.wait(2.2)
        self.play(FadeIn(cards[1], shift=UP * .2), FadeIn(cards[2], shift=UP * .2), run_time=.8); self.wait(3.0)
        rel = tex(r"V_{oc} = I_{sc} \times R_{th}", 70, YEL).shift(DOWN * 1.6)
        self.play(Write(rel), run_time=1.0)
        self.wait(8)
