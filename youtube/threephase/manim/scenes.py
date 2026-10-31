# 3상 회로 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(long.json 에서 그 문장 시작에 붙임). 교류 전력 편(acpower/manim/scenes.py) 형식을 따른다.
# 끝까지 보게 만드는 4원칙: 1.5~2.5초마다 화면에 새 요소(내용으로 변화, 전환·반복 확대 없음), 4초 넘게 멈춘 화면 없음.
# 검산: 220·√3 = 381 ≈ 380V, P = √3·380·10·0.8 = 5266W ≈ 5.3kW, Y-Δ 기동 선전류 1/3.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
from manim import *
import numpy as np, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
PH = [RED, GRN, BLU]            # a, b, c 상
PN = ["a", "b", "c"]
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
    return kr(s, 44, c).to_edge(UP, buff=.4)


def step_tag(n, c=YEL):
    """오른쪽 위 STEP 진행 표시: ●●●○○. 쇼츠용 렌더(NOSTEP=1)에선 뺀다."""
    if os.environ.get("NOSTEP"):
        return VGroup()
    dots = VGroup(*[Circle(.11, color=c if k < n else MUTE, fill_color=c if k < n else BG, fill_opacity=1, stroke_width=3)
                    for k in range(5)]).arrange(RIGHT, buff=.14)
    return VGroup(kr(f"STEP {n}/5", 28, c), dots).arrange(RIGHT, buff=.25).to_corner(UR, buff=.35)


def beat(sc, *anims, t=1.8, rt=.6):
    """요소 하나 띄우고 t 초를 채운다 (새 요소 간격)."""
    if anims:
        sc.play(*anims, run_time=rt)
    sc.wait(max(.05, t - (rt if anims else 0)))


def pulse(sc, m, t=3.0, c=YEL):
    """마지막 몇 초: 테두리를 그렸다 지우며 강조 (확대 없이)."""
    sc.play(Circumscribe(m, color=c, buff=.18, fade_out=True, run_time=t * .45))
    sc.play(Circumscribe(m, color=c, buff=.18, fade_out=True, run_time=t * .45))
    sc.wait(t * .1)


def P3(p): return np.array([p[0], p[1], 0.0])
def U(deg): return np.array([np.cos(deg * DEGREES), np.sin(deg * DEGREES), 0.0])
def wire(a, b, c=INK, w=4): return Line(P3(a), P3(b), color=c, stroke_width=w)


# ---------- 파형 ----------
def wax(ymax=1.3, xl=10.5, yl=3.6, x1=2.05):
    return Axes(x_range=[0, x1, .5], y_range=[-ymax, ymax, 1], x_length=xl, y_length=yl, tips=False,
                axis_config={"color": MUTE, "stroke_width": 3}, x_axis_config={"include_ticks": False}, y_axis_config={"include_ticks": False})


def ph_v(k): return lambda x: np.sin(2 * PI * x - k * 2 * PI / 3)
def ph_p(k): return lambda x: .5 * (np.sin(2 * PI * x - k * 2 * PI / 3)) ** 2 * 2     # 저항 부하 한 상의 순시전력 (0~1)


def roam(sc, ax, f, c=YEL, t=3.0, x0=0, x1=2):
    k = ValueTracker(x0)
    d = always_redraw(lambda: Dot(ax.c2p(k.get_value(), f(k.get_value())), .1, color=c))
    sc.add(d); sc.play(k.animate.set_value(x1), run_time=t, rate_func=linear)
    return d


# ---------- 페이저 ----------
ANG = [90, -30, 210]            # a, b, c 페이저 방향 (a 기준 120° 씩 늦음)


def pha(k, L=2.0, o=ORIGIN, c=None, sw=7):
    return Arrow(o, o + U(ANG[k]) * L, buff=0, color=c or PH[k], stroke_width=sw, max_tip_length_to_length_ratio=.16)


def plab(k, arr, s=None, size=44):
    return tex(s or rf"V_{PN[k]}", size, PH[k]).move_to(arr.get_end() + U(ANG[k]) * .45)


# ---------- 회로 부품 ----------
def coil(a, b, c=INK, n=4, sw=4):
    """a→b 사이 코일 (반원 n 개)."""
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L
    seg = L * .6; r = seg / n / 2; s0 = a + u * (L - seg) / 2
    g = VGroup(Line(a, s0, color=c, stroke_width=sw))
    ang = np.arctan2(u[1], u[0])
    for i in range(n):
        ctr = s0 + u * (r * (2 * i + 1))
        g.add(Arc(radius=r, start_angle=ang + PI, angle=-PI, color=c, stroke_width=sw).move_arc_center_to(ctr))
    g.add(Line(s0 + u * seg, b, color=c, stroke_width=sw))
    return g


def motor(p, c=INK, r=.55):
    return VGroup(Circle(r, color=c, stroke_width=4), kr("M", int(80 * r), c)).move_to(P3(p))


def ystar(R=2.0, o=ORIGIN, ext=.9, cols=True):
    """Y결선: 중성점 o, 코일 3개, 단자에서 선이 바깥으로."""
    G = VGroup(); C = VGroup(); Ls = VGroup(); T = []
    for k in range(3):
        u = U(ANG[k]); c = PH[k] if cols else INK
        C.add(coil(o, o + u * R, c))
        Ls.add(Line(o + u * R, o + u * (R + ext), color=c, stroke_width=4))
        T.append(o + u * (R + ext))
    n = Dot(o, .12, color=YEL)
    G.add(C, Ls, n)
    return G, C, Ls, n, T


def delta(R=2.2, o=ORIGIN, ext=.9):
    """Δ결선: 꼭짓점 a(위), b(오른쪽 아래), c(왼쪽 아래). 변마다 코일, 꼭짓점에서 선이 바깥으로."""
    V = [o + U(ANG[k]) * R for k in range(3)]
    C = VGroup(coil(V[0], V[1], PH[0]), coil(V[1], V[2], PH[1]), coil(V[2], V[0], PH[2]))
    Ls = VGroup(*[Line(V[k], V[k] + U(ANG[k]) * ext, color=INK, stroke_width=4) for k in range(3)])
    D = VGroup(*[Dot(V[k], .09, color=INK) for k in range(3)])
    return VGroup(C, Ls, D), C, Ls, V


def house(c=INK):
    b = Square(1.6, color=c, stroke_width=5); roof = Polygon(b.get_corner(UL) + LEFT * .25, b.get_corner(UR) + RIGHT * .25, b.get_top() + UP * .9, color=c, stroke_width=5)
    door = Rectangle(width=.45, height=.8, color=c, stroke_width=4).align_to(b, DOWN)
    return VGroup(b, roof, door)


def factory(c=INK):
    b = Rectangle(width=2.6, height=1.4, color=c, stroke_width=5)
    tl = b.get_corner(UL)
    saw = VMobject(color=c, stroke_width=5).set_points_as_corners([tl, tl + UP * .7 + RIGHT * .1, tl + RIGHT * .87, tl + RIGHT * .87 + UP * .7, tl + RIGHT * 1.73,
                                                                   tl + RIGHT * 1.73 + UP * .7, tl + RIGHT * 2.6])
    ch = Rectangle(width=.35, height=1.0, color=c, stroke_width=5).next_to(b, UP, 0).align_to(b, RIGHT).shift(LEFT * .2 + UP * .3)
    win = VGroup(*[Square(.35, color=c, stroke_width=3).move_to(b.get_center() + RIGHT * x) for x in (-.8, 0, .8)])
    return VGroup(b, saw, ch, win)


def tower(c=INK):
    """송전탑 (선 3가닥)."""
    body = VMobject(color=c, stroke_width=5).set_points_as_corners([P3((-.8, -2.2)), P3((-.25, 1.6)), P3((.25, 1.6)), P3((.8, -2.2))])
    arms = VGroup(Line(P3((-1.4, 1.1)), P3((1.4, 1.1)), color=c, stroke_width=5), Line(P3((-1.0, .3)), P3((1.0, .3)), color=c, stroke_width=5))
    x = VGroup(Line(P3((-.6, -1.0)), P3((.4, .3)), color=c, stroke_width=3), Line(P3((.6, -1.0)), P3((-.4, .3)), color=c, stroke_width=3))
    return VGroup(body, arms, x)


# ================= 인트로 =================
class Hook(Scene):
    """집 220V vs 공장 380V → 220 × √3 ≈ 380."""
    def construct(self):
        h = house().shift(LEFT * 3.4 + UP * .7); f = factory().shift(RIGHT * 3.4 + UP * .5)
        beat(self, Create(h), t=.6, rt=.5)
        l1 = tex(r"220\,\mathrm{V}", 72, GRN).next_to(h, DOWN, .45)
        beat(self, FadeIn(l1, shift=UP * .2), t=1.0, rt=.4)
        beat(self, Create(f), t=.6, rt=.5)
        l2 = tex(r"380\,\mathrm{V}", 72, ORG).next_to(f, DOWN, .45).align_to(l1, DOWN)
        q = kr("?", 72, YEL).next_to(l2, RIGHT, .25)
        beat(self, FadeIn(l2, shift=UP * .2), FadeIn(q), t=1.6, rt=.4)
        eq = tex(r"220 \times \sqrt{3} \approx 380", 84, YEL).to_edge(DOWN, buff=.5)
        beat(self, Write(eq), FadeOut(q), t=1.6, rt=1.0)
        pulse(self, eq, t=1.8)


class Goal(Scene):
    """오늘의 목표: √3 의 정체 + STEP 5칸."""
    def construct(self):
        f = tex(r"\sqrt{3}", 150, YEL).shift(UP * 1.3)
        beat(self, FadeIn(f), t=1.2, rt=.5)
        g = kr("같은 3상 전기", 44, INK).next_to(f, DOWN, .5); beat(self, FadeIn(g, shift=UP * .2), t=1.2, rt=.4)
        dots = VGroup(*[VGroup(Circle(.32, color=YEL, stroke_width=4), kr(str(k + 1), 32, YEL)) for k in range(5)]).arrange(RIGHT, buff=.6)
        dots.next_to(g, DOWN, .8)
        self.play(LaggedStart(*[FadeIn(d, scale=.8) for d in dots], lag_ratio=.25), run_time=1.4)
        self.play(dots[0][0].animate.set_fill(YEL, .35), run_time=.8)
        self.wait(.6)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "3상이란", RED), ("2", "중성선", GRN), ("3", "Y결선", BLU), ("4", "델타 결선", ORG), ("5", "3상 전력", YEL)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for i, k in enumerate(cards):
            beat(self, FadeIn(k, shift=UP * .3), t=1.1, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.8, rt=1.0)


# ================= STEP 1 3상이란 =================
class A1(Scene):
    """발전기: 코일 3개 120° 간격, 가운데 자석이 돈다."""
    def construct(self):
        self.add(step_tag(1, RED))
        ring = Circle(2.6, color=MUTE, stroke_width=4); self.add(ring)
        coils = VGroup()
        for k in range(3):
            u = U(ANG[k]); n = U(ANG[k] + 90)
            coils.add(coil(u * 2.6 - n * .7, u * 2.6 + n * .7, PH[k], n=3, sw=6))
        for k in range(3):
            lab = tex(PN[k], 48, PH[k]).move_to(U(ANG[k]) * 3.25)
            beat(self, Create(coils[k]), FadeIn(lab), t=1.0, rt=.5)
        arcs = VGroup(Arc(1.9, 90 * DEGREES, -120 * DEGREES, color=YEL, stroke_width=4))
        t120 = tex(r"120^\circ", 46, YEL).move_to(U(30) * 1.35)
        beat(self, Create(arcs), FadeIn(t120), t=1.2, rt=.6)
        mag = VGroup(Rectangle(width=.5, height=.95, color=RED, fill_color=RED, fill_opacity=.9, stroke_width=0).shift(UP * .475),
                     Rectangle(width=.5, height=.95, color=BLU, fill_color=BLU, fill_opacity=.9, stroke_width=0).shift(DOWN * .475))
        self.play(FadeIn(mag), run_time=.4)
        self.play(Rotate(mag, -2 * PI, about_point=ORIGIN), run_time=2.4, rate_func=linear)


class A2(Scene):
    """세 사인파가 120° 씩 늦게."""
    def construct(self):
        self.add(step_tag(1, RED))
        ax = wax(yl=4.2).shift(DOWN * .3); self.add(ax)
        for k in range(3):
            w = ax.plot(ph_v(k), x_range=[0, 2], color=PH[k], stroke_width=5)
            lab = tex(rf"v_{PN[k]}", 44, PH[k]).next_to(ax.c2p(.25 + k / 3, 1), UP, .1)
            beat(self, Create(w), FadeIn(lab), t=1.4, rt=.9)
        br = DoubleArrow(ax.c2p(.75, -1.2), ax.c2p(.75 + 1 / 3, -1.2), buff=0, color=YEL, stroke_width=4, tip_length=.2)
        beat(self, GrowFromCenter(br), t=.4, rt=.4)
        roam(self, ax, ph_v(0), RED, t=1.6, x0=0, x1=.75)


class A3(Scene):
    """a → b → c 차례로 꼭대기."""
    def construct(self):
        self.add(step_tag(1, RED))
        ax = wax(yl=4.2).shift(DOWN * .3); self.add(ax)
        for k in range(3):
            self.add(ax.plot(ph_v(k), x_range=[0, 2], color=PH[k], stroke_width=4, stroke_opacity=.55))
        x = ValueTracker(0)
        cur = always_redraw(lambda: DashedLine(ax.c2p(x.get_value(), -1.3), ax.c2p(x.get_value(), 1.3), color=INK, stroke_width=2))
        dots = always_redraw(lambda: VGroup(*[Dot(ax.c2p(x.get_value(), ph_v(k)(x.get_value())), .11, color=PH[k]) for k in range(3)]))
        self.add(cur, dots)
        tops = VGroup()
        for k in range(3):
            xp = .25 + k / 3
            self.play(x.animate.set_value(xp), run_time=1.0 if k == 0 else 1.0, rate_func=linear)
            t = card(tex(PN[k], 44, PH[k]), PH[k], .15).next_to(ax.c2p(xp, 1), UP, .2)
            tops.add(t); self.play(FadeIn(t, scale=.8), run_time=.4)
        self.play(x.animate.set_value(1.6), run_time=2.0, rate_func=linear)


class A4(Scene):
    """페이저: 같은 길이 화살표 3개, 120° 간격 (돌아간다)."""
    def construct(self):
        self.add(step_tag(1, RED))
        o = LEFT * .2
        arrs = VGroup(*[pha(k, 2.3, o) for k in range(3)])
        labs = VGroup(*[plab(k, arrs[k]) for k in range(3)])
        for k in range(3):
            beat(self, GrowArrow(arrs[k]), FadeIn(labs[k]), t=1.0, rt=.5)
        arcs = VGroup(*[Arc(.8, ANG[k] * DEGREES, -120 * DEGREES, arc_center=o, color=YEL, stroke_width=3) for k in range(2)])
        t = tex(r"120^\circ", 42, YEL).move_to(o + U(30) * 1.25)
        beat(self, Create(arcs), FadeIn(t), t=1.0, rt=.5)
        grp = VGroup(arrs, labs, arcs, t)
        self.play(FadeOut(labs), FadeOut(t), FadeOut(arcs), run_time=.3)
        self.play(Rotate(arrs, 2 * PI * .6, about_point=o), run_time=2.6, rate_func=linear)


class A5(Scene):
    """어느 순간이든 세 전압의 합 = 0."""
    def construct(self):
        self.add(step_tag(1, RED))
        ax = wax(yl=3.4).shift(DOWN * .6); self.add(ax)
        for k in range(3):
            self.add(ax.plot(ph_v(k), x_range=[0, 2], color=PH[k], stroke_width=4, stroke_opacity=.6))
        f = tex(r"v_a + v_b + v_c = 0", 72, YEL).to_edge(UP, buff=.5)
        beat(self, Write(f), t=1.3, rt=.8)
        s = ax.plot(lambda x: 0, x_range=[0, 2], color=YEL, stroke_width=9)
        beat(self, Create(s), t=1.0, rt=.8)
        x = ValueTracker(.1)
        cur = always_redraw(lambda: DashedLine(ax.c2p(x.get_value(), -1.3), ax.c2p(x.get_value(), 1.3), color=INK, stroke_width=2))
        dots = always_redraw(lambda: VGroup(*[Dot(ax.c2p(x.get_value(), ph_v(k)(x.get_value())), .11, color=PH[k]) for k in range(3)],
                                            Dot(ax.c2p(x.get_value(), 0), .14, color=YEL)))
        self.add(cur, dots)
        self.play(x.animate.set_value(1.9), run_time=3.4, rate_func=linear)


class A6(Scene):
    """화살표 3개를 이어 붙이면 정삼각형이 닫힌다."""
    def construct(self):
        self.add(step_tag(1, RED))
        o = LEFT * 3.4 + DOWN * .2
        arrs = VGroup(*[pha(k, 1.8, o) for k in range(3)]); self.add(arrs)
        beat(self, t=.6)
        # 머리-꼬리: a 끝 → b → c
        p0 = RIGHT * .8 + DOWN * 1.6
        tgt = []; p = p0
        for k in (0, 1, 2):        # b, c, a 순서로 이으면 위로 닫히는 삼각형
            q = p + U(ANG[k]) * 2.8; tgt.append((k, p, q)); p = q
        for k, a, b in tgt:
            new = Arrow(a, b, buff=0, color=PH[k], stroke_width=8, max_tip_length_to_length_ratio=.12)
            beat(self, Transform(arrs[k], new), t=1.1, rt=.8)
        tri = Polygon(*[a for _, a, _ in tgt], color=YEL, fill_color=YEL, fill_opacity=.15, stroke_width=0)
        z = tex(r"= 0", 80, YEL).next_to(tri, RIGHT, .6)
        beat(self, FadeIn(tri), Write(z), t=1.2, rt=.6)
        dot = Dot(p0, .14, color=YEL); self.add(dot)
        path = VMobject().set_points_as_corners([a for _, a, _ in tgt] + [p0])
        self.play(MoveAlongPath(dot, path), run_time=2.0, rate_func=linear)


# ================= STEP 2 중성선 =================
def three_loads(neutral=False, y0=0):
    """왼쪽 전원 3개 — 오른쪽 부하 3개. neutral=True 면 돌아오는 선을 하나로."""
    G = VGroup(); go = VGroup(); back = VGroup(); srcs = VGroup(); loads = VGroup()
    for k in range(3):
        y = y0 + 1.8 - k * 1.8
        s = VGroup(Circle(.35, color=PH[k], stroke_width=4), tex("\\sim", 40, PH[k])).move_to(P3((-4.5, y)))
        r = coil((3.6, y + .5), (3.6, y - .5), PH[k], n=3)
        srcs.add(s); loads.add(r)
        go.add(VGroup(Line(P3((-4.5, y + .35)), P3((-4.5, y + .55)), color=PH[k], stroke_width=4),
                      Line(P3((-4.5, y + .55)), P3((3.6, y + .55)), color=PH[k], stroke_width=4),
                      Line(P3((3.6, y + .55)), P3((3.6, y + .5)), color=PH[k], stroke_width=4)))
        back.add(VGroup(Line(P3((-4.5, y - .35)), P3((-4.5, y - .55)), color=MUTE, stroke_width=4),
                        Line(P3((-4.5, y - .55)), P3((3.6, y - .55)), color=MUTE, stroke_width=4),
                        Line(P3((3.6, y - .55)), P3((3.6, y - .5)), color=MUTE, stroke_width=4)))
    return srcs, loads, go, back


class N1(Scene):
    """단상 3개 = 전선 6가닥."""
    def construct(self):
        self.add(step_tag(2, GRN))
        srcs, loads, go, back = three_loads()
        beat(self, FadeIn(srcs), FadeIn(loads), t=.9, rt=.5)
        nums = VGroup()
        for k in range(3):
            self.play(Create(go[k]), Create(back[k]), run_time=.5)
            for j, ln in enumerate((go[k], back[k])):
                n = card(kr(str(2 * k + j + 1), 30, YEL), YEL, .1).move_to(ln[1].get_center())
                nums.add(n)
            self.play(FadeIn(nums[-2]), FadeIn(nums[-1]), run_time=.35)
        t = kr("6가닥", 56, YEL).to_edge(DOWN, buff=.25)
        beat(self, FadeIn(t, shift=UP * .2), t=1.4, rt=.4)
        dots = VGroup(*[Dot(go[k][1].get_start(), .09, color=YEL) for k in range(3)])
        self.add(dots); self.play(*[d.animate.move_to(go[k][1].get_end()) for k, d in enumerate(dots)], run_time=1.6, rate_func=linear)


class N2(Scene):
    """돌아오는 선 3개 → 중성선 하나."""
    def construct(self):
        self.add(step_tag(2, GRN))
        srcs, loads, go, back = three_loads(); self.add(srcs, loads, go, back)
        beat(self, back.animate.set_color(YEL), t=1.0, rt=.5)
        nl = Line(P3((-5.3, -3.2)), P3((4.4, -3.2)), color=YEL, stroke_width=8)
        stubs = VGroup()
        for k in range(3):
            y = 1.8 - k * 1.8
            stubs.add(Line(P3((-4.5, y - .35)), P3((-4.5, -3.2)), color=YEL, stroke_width=4),
                      Line(P3((3.6, y - .5)), P3((3.6, -3.2)), color=YEL, stroke_width=4))
        self.play(FadeOut(back), Create(stubs), Create(nl), run_time=1.4)
        lab = kr("중성선 N", 40, YEL).next_to(nl, UP, .12).shift(RIGHT * 1.2)
        beat(self, FadeIn(lab), t=1.2, rt=.4)
        t = kr("6 → 4가닥", 44, YEL).to_corner(UL, buff=.4)
        beat(self, FadeIn(t), t=1.2, rt=.4)
        d = Dot(nl.get_end(), .12, color=YEL); self.add(d)
        self.play(d.animate.move_to(nl.get_start()), run_time=1.6, rate_func=linear)


def y_feed(I_lab=True):
    """선 3개 → 부하 코일 3개 → 아래 중성 모선 → 중성선."""
    lines = VGroup(); arrows = VGroup(); labs = VGroup(); loads = VGroup()
    xs = [1.4, 2.7, 4.0]; ys = [1.8, 1.0, .2]; yb = -1.7
    for k in range(3):
        lines.add(VGroup(Line(P3((-5.0, ys[k])), P3((xs[k], ys[k])), color=PH[k], stroke_width=4)))
        loads.add(VGroup(coil((xs[k], ys[k]), (xs[k], -1.0), PH[k], n=3), Line(P3((xs[k], -1.0)), P3((xs[k], yb)), color=YEL, stroke_width=4)))
        if I_lab:
            ar = Arrow(P3((-4.2, ys[k] + .22)), P3((-2.8, ys[k] + .22)), buff=0, color=PH[k], stroke_width=5, max_tip_length_to_length_ratio=.25)
            arrows.add(ar); labs.add(tex(r"10\,\mathrm{A}", 34, PH[k]).next_to(ar, RIGHT, .15))
    nl = VGroup(Line(P3((xs[2], yb)), P3((xs[0], yb)), color=YEL, stroke_width=5), Line(P3((xs[0], yb)), P3((-5.0, yb)), color=YEL, stroke_width=5))
    return VGroup(lines, loads), nl, arrows, labs


class N3(Scene):
    """질문: 세 부하가 10A씩이면 중성선엔 몇 A?"""
    def construct(self):
        self.add(step_tag(2, GRN))
        ck, nl, arrows, labs = y_feed(); self.add(ck, nl)
        for k in range(3):
            beat(self, GrowArrow(arrows[k]), FadeIn(labs[k]), t=.7, rt=.4)
        q = card(VGroup(kr("중성선", 36, YEL), tex(r"I_N = \ ?", 56, YEL)).arrange(RIGHT, buff=.2), YEL, .2).next_to(nl[1], DOWN, .25).shift(LEFT * 1.0)
        beat(self, FadeIn(q, shift=UP * .2), t=1.4, rt=.4)
        d = Dot(nl[1].get_end(), .1, color=YEL); self.add(d)
        self.play(d.animate.move_to(nl[1].get_start()), run_time=1.6, rate_func=linear)
        self.play(Wiggle(q[1], scale_value=1.1), run_time=1.0)


class N4(Scene):
    """전류 페이저 3개 합 → 0A."""
    def construct(self):
        self.add(step_tag(2, GRN))
        o = LEFT * 4.0
        arrs = VGroup(*[pha(k, 1.7, o) for k in range(3)])
        labs = VGroup(*[tex(rf"I_{PN[k]}", 40, PH[k]).move_to(o + U(ANG[k]) * 2.15) for k in range(3)])
        beat(self, LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=.3), FadeIn(labs), t=1.4, rt=1.0)
        p0 = LEFT * .6 + DOWN * 1.4; p = p0; pts = []
        for k in (0, 1, 2):
            q = p + U(ANG[k]) * 2.6; pts.append(p)
            new = Arrow(p, q, buff=0, color=PH[k], stroke_width=8, max_tip_length_to_length_ratio=.12)
            self.play(TransformFromCopy(arrs[k], new), run_time=.7); p = q
        self.wait(.3)
        z = card(VGroup(tex(r"I_N", 60, YEL), tex(r"= 0\,\mathrm{A}", 60, YEL)).arrange(RIGHT, buff=.15), YEL, .25).move_to(RIGHT * 4.3 + DOWN * .1)
        beat(self, FadeIn(z, shift=LEFT * .2), t=1.4, rt=.5)
        pulse(self, z, t=1.6)


class N5(Scene):
    """평형 3상 → 송전선 3가닥."""
    def construct(self):
        self.add(step_tag(2, GRN))
        t = card(kr("평형 3상", 52, YEL), YEL, .25).to_corner(UL, buff=.5).shift(DOWN * .3)
        beat(self, FadeIn(t), t=1.2, rt=.4)
        tw = VGroup(tower().shift(LEFT * .8), tower().shift(RIGHT * 3.8)).shift(DOWN * .5)
        beat(self, Create(tw), t=1.0, rt=.8)
        wires = VGroup(Line(P3((-6.5, .25)), P3((6.5, .25)), color=PH[0], stroke_width=5),
                       Line(P3((-6.5, -.05)), P3((6.5, -.05)), color=PH[1], stroke_width=5),
                       Line(P3((-6.5, -.75)), P3((6.5, -.75)), color=PH[2], stroke_width=5))
        beat(self, LaggedStart(*[Create(w) for w in wires], lag_ratio=.3), t=1.4, rt=1.0)
        n = kr("3가닥", 56, YEL).to_edge(DOWN, buff=.5)
        beat(self, FadeIn(n, shift=UP * .2), t=1.0, rt=.4)
        dots = VGroup(*[Dot(w.get_start(), .1, color=YEL) for w in wires]); self.add(dots)
        self.play(*[d.animate.move_to(w.get_end()) for d, w in zip(dots, wires)], run_time=1.8, rate_func=linear)


def sum_rows(items):
    g = VGroup(*[VGroup(kr(a, 34, MUTE), b).arrange(RIGHT, buff=.5) for a, b in items]).arrange(DOWN, buff=.55, aligned_edge=LEFT)
    return g.shift(DOWN * .2)


class Sum1(Scene):
    """중간 정리 (STEP 1~2)."""
    def construct(self):
        self.add(head("여기까지 정리", YEL))
        rows = sum_rows([("세 전압", kr("120°씩 어긋남", 42, RED)),
                         ("합", tex(r"v_a+v_b+v_c = 0", 52, GRN)),
                         ("평형이면", VGroup(kr("중성선 전류", 42, YEL), tex(r"= 0", 56, YEL)).arrange(RIGHT, buff=.2))])
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.5, rt=.5)
        pulse(self, rows[2], t=1.8)


# ================= STEP 3 Y결선 =================
class Y1(Scene):
    """Y결선: 코일 끝을 한 점(중성점)에."""
    def construct(self):
        self.add(step_tag(3, BLU))
        G, C, Ls, n, T = ystar(2.0, DOWN * .2)
        for k in range(3):
            beat(self, Create(C[k]), Create(Ls[k]), t=.9, rt=.6)
        beat(self, FadeIn(n, scale=3), t=.8, rt=.4)
        lab = kr("중성점 N", 38, YEL).next_to(n, LEFT, .5).shift(DOWN * .9)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        y = kr("Y결선", 52, BLU).to_corner(UL, buff=.5).shift(DOWN * .3)
        beat(self, FadeIn(y), t=1.0, rt=.4)
        self.play(Flash(n, color=YEL, line_length=.35, num_lines=10, flash_radius=.35), run_time=1.0)
        self.play(Flash(n, color=YEL, line_length=.35, num_lines=10, flash_radius=.35), run_time=1.0)


class Y2(Scene):
    """상전압(코일 하나) vs 선간전압(선과 선 사이)."""
    def construct(self):
        self.add(step_tag(3, BLU))
        o = LEFT * 2.2 + DOWN * .3
        G, C, Ls, n, T = ystar(1.7, o, ext=.7); self.add(G)
        ta = [Dot(T[k], .1, color=PH[k]) for k in range(3)]; self.add(*ta)
        for k in range(3):
            self.add(tex(PN[k], 40, PH[k]).move_to(T[k] + U(ANG[k]) * .35))
        # 상전압: N ~ a
        pa = Brace(Line(o, o + U(90) * 1.7), LEFT, color=RED)
        pl = VGroup(kr("상전압", 36, RED), tex(r"V_P", 44, RED)).arrange(DOWN, buff=.1).next_to(pa, LEFT, .15)
        beat(self, GrowFromCenter(pa), FadeIn(pl), t=1.6, rt=.5)
        # 선간전압: a ~ b
        lab_line = DashedLine(T[0], T[1], color=YEL, stroke_width=5)
        ll = VGroup(kr("선간전압", 36, YEL), tex(r"V_L", 44, YEL)).arrange(DOWN, buff=.1).next_to(lab_line.get_center(), UR, .2)
        beat(self, Create(lab_line), FadeIn(ll), t=1.6, rt=.6)
        cmp = card(VGroup(tex(r"V_P", 52, RED), kr("코일 하나", 32, MUTE), tex(r"V_L", 52, YEL), kr("선과 선 사이", 32, MUTE)).arrange_in_grid(2, 2, buff=(.4, .3)), "#2a2e37", .3).shift(RIGHT * 4.0 + DOWN * .2)
        beat(self, FadeIn(cmp, shift=LEFT * .2), t=1.4, rt=.4)
        pulse(self, lab_line, t=1.4)


class Y3(Scene):
    """V_ab = V_a − V_b: 화살표 빼기."""
    def construct(self):
        self.add(step_tag(3, BLU))
        o = LEFT * 3.0 + DOWN * .6
        f = tex(r"V_{ab} = V_a - V_b", 64, YEL).to_corner(UR, buff=.6).shift(DOWN * .5)
        beat(self, Write(f), t=1.2, rt=.7)
        va = pha(0, 2.2, o); vb = pha(1, 2.2, o)
        la = plab(0, va, r"V_a"); lb = plab(1, vb, r"V_b")
        beat(self, GrowArrow(va), FadeIn(la), t=.9, rt=.5)
        beat(self, GrowArrow(vb), FadeIn(lb), t=.9, rt=.5)
        nb = Arrow(o, o - U(ANG[1]) * 2.2, buff=0, color=GRN, stroke_width=7, max_tip_length_to_length_ratio=.16).set_opacity(.6)
        lnb = tex(r"-V_b", 44, GRN).move_to(o - U(ANG[1]) * 2.65)
        beat(self, TransformFromCopy(vb, nb), FadeIn(lnb), t=1.2, rt=.8)
        shifted = Arrow(va.get_end(), va.get_end() - U(ANG[1]) * 2.2, buff=0, color=GRN, stroke_width=7, max_tip_length_to_length_ratio=.16)
        beat(self, TransformFromCopy(nb, shifted), t=1.0, rt=.8)
        vab = Arrow(o, shifted.get_end(), buff=0, color=YEL, stroke_width=9, max_tip_length_to_length_ratio=.1)
        beat(self, GrowArrow(vab), t=1.2, rt=.8)


class Y4(Scene):
    """두 화살표 차 = √3 배, 30° 앞섬 (꼭짓각 120° 이등변삼각형)."""
    def construct(self):
        self.add(step_tag(3, BLU))
        o = LEFT * 3.6 + DOWN * 2.0
        L = 2.4
        A = o + U(90) * L; B = o + U(-30) * L
        va = Arrow(o, A, buff=0, color=RED, stroke_width=7, max_tip_length_to_length_ratio=.14)
        vb = Arrow(o, B, buff=0, color=GRN, stroke_width=7, max_tip_length_to_length_ratio=.14)
        self.add(va, vb, tex("V_a", 42, RED).next_to(A, UP, .1), tex("V_b", 42, GRN).next_to(B, RIGHT, .1))
        d = Arrow(B, A, buff=0, color=YEL, stroke_width=9, max_tip_length_to_length_ratio=.1)
        beat(self, GrowArrow(d), t=1.0, rt=.6)
        a120 = Arc(.6, -30 * DEGREES, 120 * DEGREES, arc_center=o, color=INK, stroke_width=3)
        t120 = tex(r"120^\circ", 36, INK).move_to(o + U(30) * 1.0)
        beat(self, Create(a120), FadeIn(t120), t=1.0, rt=.4)
        r = tex(r"|V_a - V_b| = 2\cos 30^\circ \, V_P = \sqrt{3}\, V_P", 54, YEL).to_edge(UP, buff=1.0).shift(RIGHT * .6)
        beat(self, Write(r), t=1.6, rt=1.0)
        dd = Arrow(o, o + (A - B), buff=0, color=YEL, stroke_width=7, max_tip_length_to_length_ratio=.1).set_opacity(.6)
        a30 = Arc(1.1, 90 * DEGREES, 30 * DEGREES, arc_center=o, color=YEL, stroke_width=4)
        t30 = kr("30° 앞섬", 34, YEL).next_to(o + U(120) * 2.6, LEFT, .2)
        beat(self, TransformFromCopy(d, dd), Create(a30), FadeIn(t30), t=1.4, rt=.8)
        big = card(VGroup(tex(r"V_L = \sqrt{3}\,V_P", 70, YEL)), YEL, .3).shift(RIGHT * 3.2 + DOWN * 1.4)
        beat(self, FadeIn(big, shift=UP * .2), t=1.4, rt=.4)


class Y5(Scene):
    """220 × 1.732 ≈ 380V."""
    def construct(self):
        self.add(step_tag(3, BLU))
        a = VGroup(kr("상전압", 40, RED), tex(r"220\,\mathrm{V}", 72, RED)).arrange(DOWN, buff=.2).shift(LEFT * 4 + UP * .6)
        beat(self, FadeIn(a), t=1.0, rt=.4)
        m = tex(r"\times 1.732", 72, YEL).shift(UP * .2 + LEFT * .6)
        beat(self, Write(m), t=1.0, rt=.6)
        n = DecimalNumber(220, num_decimal_places=0, font_size=96, color=ORG).shift(RIGHT * 3.2 + UP * .2)
        u = tex(r"\mathrm{V}", 96, ORG).next_to(n, RIGHT, .1)
        lab = kr("선간전압", 40, ORG).next_to(VGroup(n, u), UP, .3)
        self.add(n, u, lab)
        self.play(ChangeDecimalToValue(n, 381), UpdateFromFunc(u, lambda x: x.next_to(n, RIGHT, .1)), run_time=1.6)
        ap = tex(r"\approx 380\,\mathrm{V}", 64, ORG).next_to(VGroup(n, u), DOWN, .3)
        beat(self, FadeIn(ap, shift=UP * .2), t=.9, rt=.4)
        f = factory(ORG).scale(.7).to_edge(DOWN, buff=.35).shift(RIGHT * 3.2)
        t = kr("공장 380V의 정체", 40, YEL).to_edge(DOWN, buff=.6).shift(LEFT * 2.6)
        beat(self, Create(f), FadeIn(t), t=1.2, rt=.6)
        pulse(self, ap, t=1.6, c=ORG)


class Y6(Scene):
    """Y: 선전류 = 상전류 (같은 길 하나)."""
    def construct(self):
        self.add(step_tag(3, BLU))
        o = RIGHT * 2.0 + DOWN * .3
        G, C, Ls, n, T = ystar(1.6, o, ext=0); self.add(G)
        a = T[0]; line = Line(P3((-5.0, a[1])), a, color=RED, stroke_width=5); self.add(line)
        f = tex(r"I_L = I_P", 80, YEL).to_corner(UL, buff=.6).shift(DOWN * .4)
        beat(self, Write(f), t=1.2, rt=.7)
        l1 = tex(r"I_L", 44, RED).next_to(line, UP, .15); l2 = tex(r"I_P", 44, RED).next_to(C[0], RIGHT, .2)
        beat(self, FadeIn(l1), FadeIn(l2), t=1.0, rt=.4)
        path = VMobject().set_points_as_corners([line.get_start(), a, o])
        for _ in range(3):
            ds = VGroup(*[Dot(line.get_start(), .1, color=YEL) for _ in range(1)])
            self.play(MoveAlongPath(ds[0], path), run_time=1.3, rate_func=linear); self.remove(ds)
        s = kr("같은 길 하나", 36, MUTE).next_to(f, DOWN, .3)
        beat(self, FadeIn(s), t=.6, rt=.3)


# ================= STEP 4 델타 =================
class D1(Scene):
    """델타: 세 코일을 삼각형으로."""
    def construct(self):
        self.add(step_tag(4, ORG))
        G, C, Ls, V = delta(2.2, DOWN * .4)
        for k in range(3):
            beat(self, Create(C[k]), t=.9, rt=.6)
        beat(self, Create(Ls), FadeIn(G[2]), t=1.0, rt=.5)
        for k in range(3):
            self.add(tex(PN[k], 40, INK).move_to(V[k] + U(ANG[k]) * 1.25))
        y = VGroup(kr("델타", 52, ORG), tex(r"\Delta", 64, ORG)).arrange(RIGHT, buff=.2).to_corner(UL, buff=.5).shift(DOWN * .3)
        beat(self, FadeIn(y), t=1.0, rt=.4)
        tri = Polygon(*V, color=ORG, stroke_width=0, fill_color=ORG, fill_opacity=.08)
        self.play(FadeIn(tri), run_time=.6); self.bring_to_back(tri)
        d = Dot(V[0], .12, color=YEL); self.add(d)
        self.play(MoveAlongPath(d, VMobject().set_points_as_corners(V + [V[0]])), run_time=2.0, rate_func=linear)


class D2(Scene):
    """델타: 코일 하나 = 두 선 사이 → V_L = V_P."""
    def construct(self):
        self.add(step_tag(4, ORG))
        G, C, Ls, V = delta(2.0, LEFT * 2.2 + DOWN * .4); self.add(G)
        hl = C[0].copy().set_stroke(YEL, 9)
        beat(self, Create(hl), t=1.0, rt=.6)
        dl = DashedLine(Ls[0].get_end(), Ls[1].get_end(), color=YEL, stroke_width=4)
        beat(self, Create(dl), t=1.0, rt=.6)
        f = tex(r"V_L = V_P", 84, ORG).shift(RIGHT * 3.8 + UP * .6)
        beat(self, Write(f), t=1.4, rt=.7)
        s = kr("코일이 선 사이에 바로", 34, MUTE).next_to(f, DOWN, .35)
        beat(self, FadeIn(s), t=1.0, rt=.4)
        pulse(self, f, t=1.6, c=ORG)


class D3(Scene):
    """델타: 꼭짓점에서 두 코일 전류가 만남 → I_L = √3 I_P."""
    def construct(self):
        self.add(step_tag(4, ORG))
        G, C, Ls, V = delta(2.0, LEFT * 3.0 + DOWN * .4); self.add(G)
        a = V[0]
        i1 = Arrow(a + U(-60) * 1.4 + U(30) * .25, a + U(-60) * .25 + U(30) * .25, buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=.3)
        i2 = Arrow(a + U(240) * .25 + U(150) * .25, a + U(240) * 1.4 + U(150) * .25, buff=0, color=BLU, stroke_width=6, max_tip_length_to_length_ratio=.3)
        il = Arrow(a + U(90) * 1.4, a + U(90) * .1, buff=0, color=YEL, stroke_width=7, max_tip_length_to_length_ratio=.3)
        beat(self, GrowArrow(i1), GrowArrow(i2), t=1.2, rt=.6)
        beat(self, GrowArrow(il), FadeIn(tex(r"I_L", 44, YEL).next_to(il, RIGHT, .15)), t=1.0, rt=.5)
        # 오른쪽: 페이저 차
        o = RIGHT * 2.4 + DOWN * 1.6
        p1 = Arrow(o, o + U(90) * 1.9, buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=.14)
        p2 = Arrow(o, o + U(-30) * 1.9, buff=0, color=BLU, stroke_width=6, max_tip_length_to_length_ratio=.14)
        beat(self, GrowArrow(p1), GrowArrow(p2), FadeIn(tex(r"I_P", 40, RED).next_to(p1, LEFT, .1)), t=1.0, rt=.6)
        d = Arrow(p2.get_end(), p1.get_end(), buff=0, color=YEL, stroke_width=8, max_tip_length_to_length_ratio=.1)
        beat(self, GrowArrow(d), t=.8, rt=.6)
        f = card(tex(r"I_L = \sqrt{3}\, I_P", 64, YEL), YEL, .25).to_corner(UR, buff=.5).shift(DOWN * .4)
        beat(self, FadeIn(f, shift=DOWN * .2), t=1.2, rt=.4)
        pulse(self, f, t=1.4)


class D4(Scene):
    """Y vs 델타 표: 서로 거꾸로."""
    def construct(self):
        self.add(step_tag(4, ORG))
        Gy = ystar(.8, ORIGIN, ext=.35)[0]; Gd = delta(.9, ORIGIN, ext=.35)[0]
        ly = card(VGroup(VGroup(kr("Y", 52, BLU)), Gy, tex(r"V_L = \sqrt{3}\,V_P", 50, YEL), tex(r"I_L = I_P", 46, MUTE)).arrange(DOWN, buff=.3), BLU, .35)
        ld = card(VGroup(VGroup(kr("델타", 48, ORG)), Gd, tex(r"V_L = V_P", 46, MUTE), tex(r"I_L = \sqrt{3}\,I_P", 50, YEL)).arrange(DOWN, buff=.3), ORG, .35)
        VGroup(ly, ld).arrange(RIGHT, buff=1.4).shift(UP * .2)
        beat(self, FadeIn(ly, shift=RIGHT * .3), t=1.4, rt=.5)
        beat(self, FadeIn(ld, shift=LEFT * .3), t=1.4, rt=.5)
        t = kr("Y는 전압, 델타는 전류 · 서로 거꾸로", 38, YEL).to_edge(DOWN, buff=.3)
        beat(self, FadeIn(t, shift=UP * .2), t=1.4, rt=.6)
        self.play(Indicate(ly[1][2], color=YEL, scale_factor=1.0), run_time=.9)
        self.play(Indicate(ld[1][3], color=YEL, scale_factor=1.0), run_time=.9)


class D5(Scene):
    """같은 부하: Y → 델타, 부하 전압 √3배 → 전력 3배."""
    def construct(self):
        self.add(step_tag(4, ORG))
        f = tex(r"P \propto V^2:\ (\sqrt{3})^2 = 3", 64, YEL).to_edge(UP, buff=1.1)
        beat(self, Write(f), t=1.4, rt=.8)
        base = DOWN * 2.4
        r1 = Rectangle(width=1.4, height=1.0, color=BLU, fill_color=BLU, fill_opacity=.85, stroke_width=0).move_to(base + LEFT * 2.2, aligned_edge=DOWN)
        r3 = Rectangle(width=1.4, height=3.0, color=ORG, fill_color=ORG, fill_opacity=.85, stroke_width=0).move_to(base + RIGHT * 2.2, aligned_edge=DOWN)
        l1 = VGroup(kr("Y", 40, BLU)).next_to(r1, DOWN, .2); l3 = kr("델타", 36, ORG).next_to(r3, DOWN, .2).align_to(l1, DOWN)
        beat(self, GrowFromEdge(r1, DOWN), FadeIn(l1), FadeIn(tex("1", 52, BLU).next_to(r1, UP, .15)), t=1.2, rt=.6)
        beat(self, GrowFromEdge(r3, DOWN), FadeIn(l3), t=1.0, rt=.8)
        x3 = tex(r"\times 3", 64, ORG).next_to(r3, UP, .15)
        beat(self, FadeIn(x3, shift=UP * .2), t=1.2, rt=.4)
        pulse(self, x3, t=1.4, c=ORG)


class D6(Scene):
    """Y-델타 기동: Y로 켜고(전류 1/3) → 델타로."""
    def construct(self):
        self.add(step_tag(4, ORG))
        m = motor((-4.3, .4), INK, .8); self.add(m)
        lab = kr("Y-델타 기동", 44, YEL).to_edge(UP, buff=.5)
        beat(self, FadeIn(lab), t=.8, rt=.4)
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 7, 1], x_length=6.2, y_length=3.6, tips=False, axis_config={"color": MUTE, "stroke_width": 3},
                  x_axis_config={"include_ticks": False}, y_axis_config={"include_ticks": False}).shift(RIGHT * 2.0 + DOWN * .5)
        self.add(ax, kr("전류", 30, MUTE).next_to(ax.y_axis, UP, .1), kr("시간", 30, MUTE).next_to(ax.x_axis, RIGHT, .1).shift(DOWN * .3))
        fd = lambda t: 1 + 5 * np.exp(-2.2 * t)
        fy = lambda t: (1 + 5 * np.exp(-2.2 * t)) / 3 if t < 1.6 else 1 + 1.4 * np.exp(-6 * (t - 1.6))
        cd = ax.plot(fd, x_range=[0.02, 4], color=RED, stroke_width=4, stroke_opacity=.6)
        ld = kr("바로 델타", 30, RED).next_to(ax.c2p(.1, 6), RIGHT, .3)
        beat(self, Create(cd), FadeIn(ld), t=1.2, rt=.8)
        cy = ax.plot(fy, x_range=[0.02, 4], color=YEL, stroke_width=6, discontinuities=[1.6], use_smoothing=False)
        sw1 = kr("Y로 시작", 32, BLU).next_to(ax.c2p(.5, 1.2), RIGHT, .1)
        self.play(Rotate(m, -PI, about_point=m.get_center()), Create(cy), FadeIn(sw1), run_time=1.8, rate_func=linear)
        third = tex(r"\tfrac{1}{3}", 56, YEL).next_to(ax.c2p(.05, 2), LEFT, .15)
        sw2 = kr("→ 델타", 32, ORG).next_to(ax.c2p(1.7, 2.4), UP, .1)
        self.play(FadeIn(third), FadeIn(sw2), Rotate(m, -PI, about_point=m.get_center()), run_time=1.0, rate_func=linear)
        self.play(Rotate(m, -4 * PI, about_point=m.get_center()), run_time=1.6, rate_func=linear)


# ================= STEP 5 3상 전력 =================
class W1(Scene):
    """3상 전력 = 한 상 × 3."""
    def construct(self):
        self.add(step_tag(5, YEL))
        boxes = VGroup(*[card(VGroup(tex(rf"P_{PN[k]}", 56, PH[k])), PH[k], .3) for k in range(3)]).arrange(RIGHT, buff=.9).shift(UP * .8)
        pl = VGroup(*[tex("+", 56, INK).move_to((boxes[k].get_right() + boxes[k + 1].get_left()) / 2) for k in range(2)])
        for k in range(3):
            beat(self, FadeIn(boxes[k], shift=UP * .2), *( [FadeIn(pl[k - 1])] if k else []), t=.8, rt=.4)
        f = tex(r"P = 3\, V_P\, I_P \cos\theta", 76, YEL).shift(DOWN * 1.4)
        beat(self, Write(f), t=1.6, rt=.9)
        pulse(self, f, t=1.6)


class W2(Scene):
    """P = √3 V_L I_L cosθ (Y·델타 같음)."""
    def construct(self):
        self.add(step_tag(5, YEL))
        f = tex(r"P = \sqrt{3}\, V_L\, I_L\, \cos\theta", 90, YEL).shift(UP * .9)
        beat(self, Write(f), t=1.6, rt=1.0)
        sub = VGroup(kr("선간전압", 34, ORG), tex(r"V_L", 44, ORG), kr("선전류", 34, BLU), tex(r"I_L", 44, BLU), kr("역률", 34, GRN), tex(r"\cos\theta", 44, GRN)).arrange(RIGHT, buff=.25).next_to(f, DOWN, .6)
        beat(self, FadeIn(sub), t=1.4, rt=.5)
        tags = VGroup(card(kr("Y", 40, BLU), BLU, .2), card(kr("델타", 36, ORG), ORG, .2)).arrange(RIGHT, buff=.4)
        ok = kr("둘 다 같은 식", 38, INK); row = VGroup(tags, ok).arrange(RIGHT, buff=.5).to_edge(DOWN, buff=.8)
        beat(self, FadeIn(row, shift=UP * .2), t=1.4, rt=.5)
        pulse(self, f, t=1.6)


class W3(Scene):
    """예제: 380V, 10A, 역률 0.8 모터."""
    def construct(self):
        self.add(step_tag(5, YEL), head("예제", YEL))
        m = motor((2.6, -.3), INK, .9)
        lines = VGroup(*[Line(P3((-5.2, -.3 + .7 * (1 - k))), P3((1.7, -.3 + .7 * (1 - k))), color=PH[k], stroke_width=5) for k in range(3)])
        beat(self, Create(lines), FadeIn(m), t=1.2, rt=.7)
        v = tex(r"V_L = 380\,\mathrm{V}", 52, ORG).next_to(lines, UP, .35).shift(LEFT * 1.2)
        beat(self, FadeIn(v), t=1.0, rt=.4)
        i = tex(r"I_L = 10\,\mathrm{A}", 52, BLU).next_to(lines, DOWN, .35).shift(LEFT * 1.2)
        beat(self, FadeIn(i), t=1.0, rt=.4)
        pf = tex(r"\cos\theta = 0.8", 52, GRN).next_to(m, DOWN, .35)
        beat(self, FadeIn(pf), t=1.0, rt=.4)
        dots = VGroup(*[Dot(l.get_start(), .09, color=YEL) for l in lines]); self.add(dots)
        self.play(*[d.animate.move_to(l.get_end()) for d, l in zip(dots, lines)], Rotate(m[1], 0), run_time=1.8, rate_func=linear)


class W4(Scene):
    """1.732 × 380 × 10 × 0.8 ≈ 5.3kW."""
    def construct(self):
        self.add(step_tag(5, YEL))
        e = tex(r"1.732 \times 380 \times 10 \times 0.8", 70, INK).shift(UP * 1.0)
        beat(self, Write(e), t=1.6, rt=1.0)
        n = DecimalNumber(0, num_decimal_places=1, font_size=110, color=YEL).shift(DOWN * .9 + LEFT * .6)
        u = tex(r"\mathrm{kW}", 100, YEL).next_to(n, RIGHT, .15)
        ap = tex(r"\approx", 100, YEL).next_to(n, LEFT, .3)
        self.add(ap, n, u)
        self.play(ChangeDecimalToValue(n, 5.3), run_time=1.6)
        b = SurroundingRectangle(VGroup(ap, n, u), color=YEL, buff=.25, corner_radius=.15)
        beat(self, Create(b), t=1.0, rt=.5)
        pulse(self, VGroup(ap, n, u), t=1.6)


class W5(Scene):
    """단상 전력: 두 배 주파수로 출렁."""
    def construct(self):
        self.add(step_tag(5, YEL))
        t = kr("단상 전력", 44, RED).to_corner(UL, buff=.5).shift(DOWN * .3)
        beat(self, FadeIn(t), t=.8, rt=.4)
        ax = wax(ymax=1.3, yl=3.8, x1=2.05).shift(DOWN * .4); self.add(ax)
        v = ax.plot(ph_v(0), x_range=[0, 2], color=MUTE, stroke_width=3)
        beat(self, Create(v), t=.8, rt=.6)
        p = ax.plot(ph_p(0), x_range=[0, 2], color=RED, stroke_width=6)
        beat(self, Create(p), t=1.2, rt=1.0)
        peaks = VGroup(*[Dot(ax.c2p(x, 1), .12, color=RED) for x in (.25, .75, 1.25, 1.75)])
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in peaks], lag_ratio=.4), run_time=1.2)
        f = tex(r"60\,\mathrm{Hz} \rightarrow 120\,\mathrm{Hz}", 52, RED).to_corner(UR, buff=.5).shift(DOWN * .8)
        beat(self, Write(f), t=.8, rt=.6)
        roam(self, ax, ph_p(0), YEL, t=2.0, x0=0, x1=1)


class W6(Scene):
    """3상: 세 상 전력 합 = 일정."""
    def construct(self):
        self.add(step_tag(5, YEL))
        ax = Axes(x_range=[0, 2.05, .5], y_range=[0, 1.8, 1], x_length=10.5, y_length=4.6, tips=False, axis_config={"color": MUTE, "stroke_width": 3},
                  x_axis_config={"include_ticks": False}, y_axis_config={"include_ticks": False}).shift(DOWN * .6); self.add(ax)
        for k in range(3):
            beat(self, Create(ax.plot(lambda x, k=k: ph_p(k)(x), x_range=[0, 2], color=PH[k], stroke_width=4)), t=.6, rt=.5)
        tot = ax.plot(lambda x: 1.5, x_range=[0, 2], color=YEL, stroke_width=9)
        beat(self, Create(tot), t=1.0, rt=.8)
        lab = card(kr("합 = 일정", 44, YEL), YEL, .2).next_to(ax.c2p(1.0, 1.5), UP, .25)
        beat(self, FadeIn(lab, shift=DOWN * .2), t=.8, rt=.4)
        x = ValueTracker(0)
        cur = always_redraw(lambda: DashedLine(ax.c2p(x.get_value(), 0), ax.c2p(x.get_value(), 1.6), color=INK, stroke_width=2))
        dts = always_redraw(lambda: VGroup(*[Dot(ax.c2p(x.get_value(), ph_p(k)(x.get_value())), .1, color=PH[k]) for k in range(3)],
                                           Dot(ax.c2p(x.get_value(), 1.5), .14, color=YEL)))
        self.add(cur, dts)
        self.play(x.animate.set_value(2.0), run_time=3.0, rate_func=linear)


# ================= 정리 =================
def final_rows():
    return sum_rows([("3상", VGroup(kr("120° 세 전압 · 평형이면", 38, RED), tex(r"I_N = 0", 46, RED)).arrange(RIGHT, buff=.25)),
                     ("Y결선", VGroup(tex(r"V_L = \sqrt{3}\,V_P", 46, BLU), kr("220V → 380V", 38, BLU)).arrange(RIGHT, buff=.35)),
                     ("델타", tex(r"I_L = \sqrt{3}\,I_P", 46, ORG)),
                     ("3상 전력", VGroup(tex(r"\sqrt{3}\,V_L I_L \cos\theta", 46, YEL), kr("· 순간 전력 일정", 38, YEL)).arrange(RIGHT, buff=.25))])


class F1(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows()
        beat(self, FadeIn(rows[0], shift=RIGHT * .3), t=2.0, rt=.5)
        pulse(self, rows[0], t=2.4, c=RED)


class F2(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows(); self.add(rows[0])
        beat(self, FadeIn(rows[1], shift=RIGHT * .3), t=1.8, rt=.5); beat(self, FadeIn(rows[2], shift=RIGHT * .3), t=1.6, rt=.5)
        pulse(self, rows[1], t=1.8, c=BLU)


class F3(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows(); self.add(rows[0], rows[1], rows[2])
        beat(self, FadeIn(rows[3], shift=RIGHT * .3), t=2.0, rt=.6)
        pulse(self, rows[3], t=2.8)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("3상 회로 · Y·델타 · 3상 전력", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        beat(self, FadeIn(t[0]), t=.8, rt=.3)
        for m in t[1]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.4, rt=.4)
        pulse(self, t, t=2.0)


class Next(Scene):
    def construct(self):
        items = ["과도응답", "교류 전력", "3상", "변압기"]
        cards = VGroup(*[card(kr(s, 36, YEL if s == "3상" else MUTE), YEL if s == "3상" else "#2a2e37", .3) for s in items]).arrange(RIGHT, buff=.35)
        lab = kr("재생목록 · 회로이론 한눈에", 40, INK).next_to(cards, UP, .6)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cards], lag_ratio=.3), run_time=1.6)
        arr = Arrow(cards[2].get_bottom() + DOWN * .2, cards[3].get_bottom() + DOWN * .2, buff=0, color=YEL, path_arc=PI / 2)
        beat(self, Create(arr), t=1.6, rt=.8)


# ================= 쇼츠 전용 =================
class CQ(Scene):
    """Y vs 델타 두 모양."""
    def construct(self):
        Gy = ystar(1.3, LEFT * 3.0, ext=.5)[0]; Gd = delta(1.5, RIGHT * 3.0 + DOWN * .2, ext=.5)[0]
        beat(self, Create(Gy), FadeIn(kr("Y", 56, BLU).next_to(Gy, DOWN, .3)), t=1.4, rt=.8)
        beat(self, Create(Gd), FadeIn(kr("델타", 48, ORG).next_to(Gd, DOWN, .3)), t=1.4, rt=.8)
        vs = kr("vs", 52, YEL)
        beat(self, FadeIn(vs, scale=1.4), t=1.0, rt=.4)
        self.play(Rotate(Gy, PI / 3 * 2, about_point=Gy[2].get_center()), run_time=1.6)


class MS0(Scene):
    """큰 모터를 일부러 약하게."""
    def construct(self):
        m = motor((0, .5), INK, 1.4)
        beat(self, Create(m[0]), FadeIn(m[1]), t=1.0, rt=.6)
        bar_bg = RoundedRectangle(width=6, height=.5, corner_radius=.25, color=MUTE, stroke_width=3).shift(DOWN * 2.2)
        fill = RoundedRectangle(width=1.8, height=.5, corner_radius=.25, color=GRN, fill_color=GRN, fill_opacity=.9, stroke_width=0).align_to(bar_bg, LEFT).shift(DOWN * 2.2)
        lab = kr("약하게 시작", 36, GRN).next_to(bar_bg, UP, .2)
        beat(self, Create(bar_bg), GrowFromEdge(fill, LEFT), FadeIn(lab), t=1.2, rt=.6)
        self.play(Rotate(m, -PI, about_point=m.get_center()), run_time=1.6, rate_func=rate_functions.ease_in_quad)
        self.play(Rotate(m, -3 * PI, about_point=m.get_center()), run_time=1.4, rate_func=linear)


class MS1(Scene):
    """켜는 순간 전류가 몇 배로."""
    def construct(self):
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 7, 1], x_length=9, y_length=4.2, tips=False, axis_config={"color": MUTE, "stroke_width": 3},
                  x_axis_config={"include_ticks": False}, y_axis_config={"include_ticks": False}).shift(DOWN * .4)
        self.add(ax, kr("전류", 30, MUTE).next_to(ax.y_axis, UP, .1))
        fd = lambda t: 1 + 5 * np.exp(-2.2 * t)
        rated = DashedLine(ax.c2p(0, 1), ax.c2p(4, 1), color=GRN, stroke_width=3)
        beat(self, Create(rated), FadeIn(kr("평소", 30, GRN).next_to(ax.c2p(4, 1), UP, .1)), t=1.0, rt=.5)
        c = ax.plot(fd, x_range=[0.02, 4], color=RED, stroke_width=6)
        beat(self, Create(c), t=1.4, rt=1.2)
        x = kr("몇 배!", 52, RED)
        x.next_to(ax.c2p(.15, 6), RIGHT, .3)
        beat(self, FadeIn(x, scale=1.3), t=1.0, rt=.4)
        roam(self, ax, fd, YEL, t=2.0, x0=0.02, x1=2.0)


class MS2(Scene):
    """기동 전류 1/3."""
    def construct(self):
        base = DOWN * 2.3
        r1 = Rectangle(width=1.5, height=3.6, color=RED, fill_color=RED, fill_opacity=.85, stroke_width=0).move_to(base + LEFT * 2.2, aligned_edge=DOWN)
        r2 = Rectangle(width=1.5, height=1.2, color=BLU, fill_color=BLU, fill_opacity=.85, stroke_width=0).move_to(base + RIGHT * 2.2, aligned_edge=DOWN)
        beat(self, GrowFromEdge(r1, DOWN), FadeIn(kr("바로 델타", 32, RED).next_to(r1, DOWN, .2)), t=1.2, rt=.6)
        beat(self, GrowFromEdge(r2, DOWN), FadeIn(kr("Y로 시작", 32, BLU).next_to(r2, DOWN, .2)), t=1.2, rt=.6)
        t = tex(r"\tfrac{1}{3}", 110, YEL).next_to(r2, UP, .3)
        beat(self, Write(t), t=1.2, rt=.6)
        pulse(self, t, t=1.6)


class EQ(Scene):
    """단상 모터는 떨리고 3상은 매끈."""
    def construct(self):
        m1 = motor((-3.2, .3), RED, 1.2); m2 = motor((3.2, .3), GRN, 1.2)
        l1 = kr("단상", 44, RED).next_to(m1, DOWN, .4); l2 = kr("3상", 44, GRN).next_to(m2, DOWN, .4)
        beat(self, FadeIn(m1), FadeIn(l1), FadeIn(m2), FadeIn(l2), t=1.0, rt=.5)
        tr = ValueTracker(0)
        c1 = m1.get_center().copy()
        m1.add_updater(lambda m: m.move_to(c1 + RIGHT * .08 * np.sin(tr.get_value() * 40)))
        self.play(tr.animate.set_value(1), Rotate(m2, -4 * PI, about_point=m2.get_center()), run_time=2.4, rate_func=linear)
        w = VGroup(kr("부르르", 36, RED).next_to(l1, DOWN, .2), kr("매끈", 36, GRN).next_to(l2, DOWN, .2))
        self.play(FadeIn(w), tr.animate.set_value(1.6), Rotate(m2, -2 * PI, about_point=m2.get_center()), run_time=1.4, rate_func=linear)
        self.play(tr.animate.set_value(2.2), Rotate(m2, -2 * PI, about_point=m2.get_center()), run_time=1.4, rate_func=linear)


class ES1(Scene):
    """세 상의 전력이 서로 어긋나서 출렁."""
    def construct(self):
        ax = wax(ymax=1.3, yl=4.2).shift(DOWN * .3); self.add(ax)
        for k in range(3):
            beat(self, Create(ax.plot(ph_p(k), x_range=[0, 2], color=PH[k], stroke_width=5)),
                 FadeIn(tex(rf"p_{PN[k]}", 40, PH[k]).next_to(ax.c2p(.25 + k / 3, 1), UP, .05)), t=1.1, rt=.8)
        roam(self, ax, ph_p(1), YEL, t=2.0, x0=0, x1=1)
