# 상호 인덕턴스·변압기 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(long.json 에서 그 문장 시작에 붙임). 3상 편(threephase/manim/scenes.py) 형식을 따른다.
# 끝까지 보게 만드는 4원칙: 1.5~2.5초마다 화면에 새 요소(내용으로 변화, 전환·반복 확대 없음), 4초 넘게 멈춘 화면 없음.
# 검산: 10:1 → 2200V→220V, 1A→10A, 22Ω→2200Ω(×100). 송전 V×10 → I/10 → 손실 1/100.
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


# ---------- 변압기 부품 ----------
STEPC = [BLU, PUR, GRN, ORG, RED]
IRON, IRON_IN = "#4a505c", BG


def solenoid(c=ORIGIN, n=5, w=2.0, h=1.6, col=INK, sw=5):
    """옆에서 본 코일: 세로 타원 n 개 + 위아래 연결선."""
    c = P3(c) if len(c) == 2 else c
    g = VGroup()
    for i in range(n):
        x = c[0] - w / 2 + w * (i + .5) / n
        g.add(Ellipse(width=.42, height=h, color=col, stroke_width=sw).move_to([x, c[1], 0]))
    return g


def core(o=ORIGIN, W=6.0, H=3.6, t=.6):
    """철심(사각 고리). 반환: 그룹, 왼쪽 다리 x, 오른쪽 다리 x, 자속 경로(가운데 선)."""
    o = P3(o) if len(o) == 2 else o
    out = Rectangle(width=W, height=H, color=IRON, fill_color=IRON, fill_opacity=1, stroke_width=0).move_to(o)
    inn = Rectangle(width=W - 2 * t, height=H - 2 * t, color=BG, fill_color=IRON_IN, fill_opacity=1, stroke_width=0).move_to(o)
    path = Rectangle(width=W - t, height=H - t).move_to(o)
    return VGroup(out, inn), o[0] - W / 2 + t / 2, o[0] + W / 2 - t / 2, path


def winding(x, y0, y1, n, col, t=.6, sw=6):
    """철심 다리(x)에 감은 n 바퀴 (비스듬한 선)."""
    g = VGroup()
    for i in range(n):
        y = y0 + (y1 - y0) * (i + .5) / n
        g.add(Line([x - t / 2 - .22, y - .1, 0], [x + t / 2 + .22, y + .1, 0], color=col, stroke_width=sw))
    return g


def xfmr(o=ORIGIN, n1=6, n2=3, W=6.0, H=3.6, c1=BLU, c2=ORG):
    """철심 변압기: core + 1차(왼쪽) + 2차(오른쪽)."""
    cg, xl, xr, path = core(o, W, H)
    cy = (P3(o) if len(o) == 2 else o)[1]; span = (H / 2 - .6) * .9
    y0, y1 = cy - span, cy + span
    w1 = winding(xl, y0, y1, n1, c1); w2 = winding(xr, y0, y1, n2, c2)
    return VGroup(cg, w1, w2), cg, w1, w2, path


def sym(o=ORIGIN, h=2.4, gap=1.0, c1=BLU, c2=ORG, iron=True, lead=1.0):
    """결합 코일 회로 기호: 왼쪽 1차(아래로), 오른쪽 2차(위로), 가운데 철심 두 줄."""
    o = P3(o) if len(o) == 2 else o
    xl, xr, yt, yb = o[0] - gap, o[0] + gap, o[1] + h / 2, o[1] - h / 2
    L1 = coil((xl, yt), (xl, yb), c1, n=4, sw=5); L2 = coil((xr, yb), (xr, yt), c2, n=4, sw=5)
    g = VGroup(L1, L2)
    if iron:
        g.add(Line([o[0] - .12, yt - .2, 0], [o[0] - .12, yb + .2, 0], color=MUTE, stroke_width=4),
              Line([o[0] + .12, yt - .2, 0], [o[0] + .12, yb + .2, 0], color=MUTE, stroke_width=4))
    T = VGroup(Line([xl, yt, 0], [xl - lead, yt, 0], color=c1, stroke_width=4), Line([xl, yb, 0], [xl - lead, yb, 0], color=c1, stroke_width=4),
               Line([xr, yt, 0], [xr + lead, yt, 0], color=c2, stroke_width=4), Line([xr, yb, 0], [xr + lead, yb, 0], color=c2, stroke_width=4))
    g.add(T)
    d1 = Dot([xl - .38, yt - .45, 0], .13, color=YEL); d2 = Dot([xr + .38, yt - .45, 0], .13, color=YEL)
    return g, L1, L2, d1, d2, (xl, xr, yt, yb)


def battery(p, c=INK, s=1.0):
    p = P3(p)
    return VGroup(Line(p + LEFT * .18 * s + UP * .55 * s, p + LEFT * .18 * s + DOWN * .55 * s, color=c, stroke_width=6),
                  Line(p + RIGHT * .18 * s + UP * .3 * s, p + RIGHT * .18 * s + DOWN * .3 * s, color=c, stroke_width=10))


def acsrc(p, c=INK, r=.55):
    p = P3(p); ax = np.linspace(-.35, .35, 30)
    s = VMobject(color=c, stroke_width=5).set_points_smoothly([p + np.array([x, .22 * np.sin(x / .35 * PI), 0]) for x in ax])
    return VGroup(Circle(r, color=c, stroke_width=5).move_to(p), s)


def resistor(a, b, c=INK, sw=5):
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    s0 = a + u * L * .25; seg = L * .5; pts = [a, s0]
    for i in range(6):
        pts.append(s0 + u * seg * (i + .5) / 6 + n * (.22 if i % 2 == 0 else -.22))
    pts += [s0 + u * seg, b]
    return VMobject(color=c, stroke_width=sw).set_points_as_corners(pts)


def bar(h, w, col, base, lab=None, size=32):
    r = Rectangle(width=w, height=max(h, .02), color=col, fill_color=col, fill_opacity=.85, stroke_width=0).move_to(base, aligned_edge=DOWN)
    g = VGroup(r)
    if lab:
        g.add(kr(lab, size, col).next_to(r, DOWN, .2))
    return g


def heat(p, c=ORG, n=3):
    p = P3(p)
    g = VGroup()
    for i in range(n):
        x0 = p + RIGHT * (i - (n - 1) / 2) * .4
        g.add(VMobject(color=c, stroke_width=4).set_points_smoothly([x0 + np.array([.1 * np.sin(k * PI / 2), k * .15, 0]) for k in range(6)]))
    return g


# ================= 인트로 =================
class Hook(Scene):
    """송전선 345,000V vs 집 220V → 바꾸는 건 코일 두 개."""
    def construct(self):
        t = tower().scale(.8).shift(LEFT * 4.3 + UP * .5); h = house().shift(RIGHT * 4.3 + UP * .5)
        beat(self, Create(t), t=.6, rt=.5)
        l1 = tex(r"345{,}000\,\mathrm{V}", 64, RED).next_to(t, DOWN, .35)
        beat(self, FadeIn(l1, shift=UP * .2), t=1.0, rt=.4)
        beat(self, Create(h), t=.6, rt=.5)
        l2 = tex(r"220\,\mathrm{V}", 64, GRN).next_to(h, DOWN, .35).align_to(l1, DOWN)
        beat(self, FadeIn(l2, shift=UP * .2), t=1.0, rt=.4)
        X = xfmr(UP * .5, 6, 2, W=2.6, H=2.2)[0]
        a1 = Arrow(LEFT * 3.0 + UP * .5, LEFT * 1.5 + UP * .5, buff=0, color=MUTE); a2 = Arrow(RIGHT * 1.5 + UP * .5, RIGHT * 3.0 + UP * .5, buff=0, color=MUTE)
        q = kr("?", 80, YEL).move_to(UP * .5)
        beat(self, GrowArrow(a1), GrowArrow(a2), FadeIn(q, scale=1.4), t=1.2, rt=.5)
        lab = kr("코일 두 개", 48, YEL).to_edge(DOWN, buff=.6)
        beat(self, FadeOut(q), FadeIn(X), Write(lab), t=1.2, rt=.8)
        pulse(self, X, t=1.6)


class Goal(Scene):
    """오늘의 목표: 변압기 + STEP 5칸."""
    def construct(self):
        X, cg, w1, w2, path = xfmr(UP * 1.3, 6, 3, W=4.4, H=2.6)
        beat(self, FadeIn(cg), t=.6, rt=.4)
        beat(self, Create(w1), Create(w2), t=1.0, rt=.6)
        g = kr("변압기", 48, INK).next_to(X, DOWN, .35); beat(self, FadeIn(g, shift=UP * .2), t=.8, rt=.4)
        dots = VGroup(*[VGroup(Circle(.32, color=STEPC[k], stroke_width=4), kr(str(k + 1), 32, STEPC[k])) for k in range(5)]).arrange(RIGHT, buff=.6)
        dots.next_to(g, DOWN, .6)
        self.play(LaggedStart(*[FadeIn(d, scale=.8) for d in dots], lag_ratio=.25), run_time=1.4)
        self.play(dots[0][0].animate.set_fill(BLU, .35), run_time=.8)
        self.wait(.8)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "상호 인덕턴스", BLU), ("2", "점 규칙", PUR), ("3", "전압비", GRN), ("4", "전류비", ORG), ("5", "송전", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for i, k in enumerate(cards):
            beat(self, FadeIn(k, shift=UP * .3), t=1.1, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.8, rt=1.0)


# ================= STEP 1 상호 인덕턴스 =================
def two_coils():
    a = solenoid(LEFT * 2.4 + DOWN * .2, 5, 2.2, 1.8, BLU); b = solenoid(RIGHT * 2.4 + DOWN * .2, 5, 2.2, 1.8, ORG)
    la = kr("1차", 38, BLU).move_to(LEFT * 2.4 + DOWN * 2.75); lb = kr("2차", 38, ORG).move_to(RIGHT * 2.4 + DOWN * 2.75)
    return a, b, la, lb


def flux_loops(n=3, col=YEL):
    g = VGroup()
    for k in range(n):
        e = Ellipse(width=8.4 - k * .9, height=2.6 + k * .9, color=col, stroke_width=3).move_to(DOWN * .2)
        g.add(DashedVMobject(e, num_dashes=40))
    return g


class M1(Scene):
    """코일 두 개를 가까이, 서로 안 닿음."""
    def construct(self):
        self.add(step_tag(1, BLU))
        a, b, la, lb = two_coils()
        beat(self, Create(a), FadeIn(la), t=1.2, rt=.8)
        beat(self, Create(b), FadeIn(lb), t=1.2, rt=.8)
        gap = DoubleArrow(LEFT * 1.1 + DOWN * .2, RIGHT * 1.1 + DOWN * .2, buff=0, color=YEL, stroke_width=4, tip_length=.2)
        no = kr("안 닿음", 36, YEL).next_to(gap, UP, .25)
        beat(self, GrowFromCenter(gap), FadeIn(no), t=1.4, rt=.5)
        cross = Cross(Square(.7), stroke_color=RED, stroke_width=8).next_to(gap, DOWN, .3)
        beat(self, Create(cross), t=1.2, rt=.4)
        self.play(Indicate(no, color=YEL, scale_factor=1.0), run_time=1.0)


class M2(Scene):
    """1차에 전류 → 코일 안 자속."""
    def construct(self):
        self.add(step_tag(1, BLU))
        a, b, la, lb = two_coils(); self.add(a, b, la, lb)
        src = acsrc(LEFT * 5.6 + DOWN * .2, BLU)
        w = VGroup(Line(a[0].get_top(), [-5.6, a[0].get_top()[1], 0], color=BLU, stroke_width=4),
                   Line([-5.6, a[0].get_top()[1], 0], [-5.6, -.2 + .55, 0], color=BLU, stroke_width=4))
        beat(self, FadeIn(src), Create(w), t=1.0, rt=.6)
        i1 = tex("i_1", 50, BLU).next_to(w[0], UP, .15)
        beat(self, FadeIn(i1), t=.8, rt=.3)
        arrs = VGroup(*[Arrow(LEFT * 3.7 + DOWN * .2 + UP * y, LEFT * 1.1 + DOWN * .2 + UP * y, buff=0, color=YEL, stroke_width=5) for y in (-.4, 0, .4)])
        self.play(LaggedStart(*[GrowArrow(x) for x in arrs], lag_ratio=.3), run_time=1.2)
        phi = tex(r"\Phi", 64, YEL).next_to(a, UP, .4)
        beat(self, Write(phi), t=1.2, rt=.5)
        self.play(*[Indicate(x, color=YEL, scale_factor=1.0) for x in arrs], run_time=1.2)
        self.wait(.6)


class M3(Scene):
    """자속이 2차 코일까지."""
    def construct(self):
        self.add(step_tag(1, BLU))
        a, b, la, lb = two_coils(); self.add(a, b, la, lb)
        F = flux_loops(3)
        for f in F:
            beat(self, Create(f), t=.9, rt=.8)
        phi = tex(r"\Phi", 64, YEL).move_to(UP * 2.2)
        beat(self, Write(phi), t=.8, rt=.4)
        beat(self, b.animate.set_color(YEL), t=1.0, rt=.6)
        k = ValueTracker(0)
        e = Ellipse(width=7.5, height=3.5).move_to(DOWN * .2)
        d = always_redraw(lambda: Dot(e.point_from_proportion(k.get_value() % 1), .14, color=YEL))
        self.add(d); self.play(k.animate.set_value(1), run_time=2.0, rate_func=linear)


def iv_axes():
    a1 = wax(ymax=1.3, xl=10, yl=2.2, x1=2.05).shift(UP * 1.2)
    a2 = wax(ymax=1.3, xl=10, yl=2.2, x1=2.05).shift(DOWN * 1.9)
    return a1, a2


class M4(Scene):
    """전류가 변하면 2차 전압."""
    def construct(self):
        self.add(step_tag(1, BLU))
        a1, a2 = iv_axes(); self.add(a1, a2)
        l1 = tex("i_1", 48, BLU).next_to(a1, LEFT, .2); l2 = tex("v_2", 48, ORG).next_to(a2, LEFT, .2)
        c1 = a1.plot(lambda x: np.sin(2 * PI * x), x_range=[0, 2], color=BLU, stroke_width=5)
        beat(self, Create(c1), FadeIn(l1), t=1.4, rt=1.0)
        c2 = a2.plot(lambda x: np.cos(2 * PI * x), x_range=[0, 2], color=ORG, stroke_width=5)
        beat(self, Create(c2), FadeIn(l2), t=1.4, rt=1.0)
        lab = card(kr("변할 때 전압", 34, YEL), YEL, .15).move_to(UP * 3.25 + LEFT * 1.5)
        beat(self, FadeIn(lab, shift=DOWN * .2), t=.8, rt=.4)
        k = ValueTracker(0)
        d1 = always_redraw(lambda: Dot(a1.c2p(k.get_value(), np.sin(2 * PI * k.get_value())), .11, color=YEL))
        d2 = always_redraw(lambda: Dot(a2.c2p(k.get_value(), np.cos(2 * PI * k.get_value())), .11, color=YEL))
        ln = always_redraw(lambda: DashedLine(a1.c2p(k.get_value(), 1.3), a2.c2p(k.get_value(), -1.3), color=MUTE, stroke_width=2))
        self.add(ln, d1, d2); self.play(k.animate.set_value(2), run_time=3.0, rate_func=linear)


class M5(Scene):
    """v2 = M di1/dt."""
    def construct(self):
        self.add(step_tag(1, BLU))
        f = tex(r"v_2 = M\,\frac{di_1}{dt}", 110, INK).shift(UP * .6)
        beat(self, Write(f), t=1.6, rt=1.2)
        m = f[0][3]
        box = SurroundingRectangle(m, color=YEL, buff=.12)
        lab = kr("상호 인덕턴스", 40, YEL).next_to(f, DOWN, .7).shift(LEFT * 1.6)
        ar = Arrow(lab.get_top(), box.get_bottom(), buff=.1, color=YEL)
        beat(self, Create(box), m.animate.set_color(YEL), t=1.2, rt=.5)
        beat(self, FadeIn(lab), GrowArrow(ar), t=1.2, rt=.5)
        rt = SurroundingRectangle(f[0][4:], color=BLU, buff=.12)
        lab2 = kr("전류의 변화율", 40, BLU).next_to(f, DOWN, .7).shift(RIGHT * 2.2)
        beat(self, Create(rt), FadeIn(lab2), t=1.4, rt=.5)
        pulse(self, VGroup(box, m), t=1.6)


class M6(Scene):
    """직류 → 2차 전압 0."""
    def construct(self):
        self.add(step_tag(1, BLU))
        a1, a2 = iv_axes(); self.add(a1, a2)
        bt = battery(LEFT * 6.2 + UP * 1.2, BLU, .8)
        beat(self, FadeIn(bt), t=.6, rt=.3)
        l1 = tex("i_1", 48, BLU).move_to(a1.c2p(0, .9) + LEFT * .45); l2 = tex("v_2", 48, ORG).next_to(a2, LEFT, .2)
        c1 = a1.plot(lambda x: .9, x_range=[0, 2], color=BLU, stroke_width=6)
        beat(self, Create(c1), FadeIn(l1), t=1.4, rt=1.0)
        c2 = a2.plot(lambda x: 0, x_range=[0, 2], color=ORG, stroke_width=7)
        beat(self, Create(c2), FadeIn(l2), t=1.4, rt=1.0)
        z = tex(r"v_2 = 0", 84, YEL).move_to(a2.c2p(1.5, .9))
        beat(self, Write(z), t=1.2, rt=.6)
        pulse(self, z, t=1.8)


# ================= STEP 2 점 규칙 =================
class Dot1(Scene):
    """감은 방향에 따라 부호가 바뀐다."""
    def construct(self):
        self.add(step_tag(2, PUR))
        A = xfmr(LEFT * 3.3 + DOWN * .2, 4, 3, W=4.2, H=3.0, c1=BLU, c2=ORG)
        B = xfmr(RIGHT * 3.3 + DOWN * .2, 4, 3, W=4.2, H=3.0, c1=BLU, c2=ORG)
        for w in B[3]:
            w.flip(UP)
        beat(self, FadeIn(A[0]), t=1.0, rt=.6)
        beat(self, FadeIn(B[0]), t=1.0, rt=.6)
        ra = A[3].get_right(); rb = B[3].get_right()
        pa = VGroup(tex("+", 60, GRN).move_to(ra + RIGHT * .6 + UP * .8), tex("-", 60, RED).move_to(ra + RIGHT * .6 + DOWN * .8))
        pb = VGroup(tex("-", 60, RED).move_to(rb + RIGHT * .6 + UP * .8), tex("+", 60, GRN).move_to(rb + RIGHT * .6 + DOWN * .8))
        beat(self, FadeIn(pa, scale=1.4), t=1.2, rt=.4)
        beat(self, FadeIn(pb, scale=1.4), t=1.2, rt=.4)
        q = kr("감은 방향 → 부호", 40, PUR).to_edge(DOWN, buff=.5)
        beat(self, Write(q), t=1.2, rt=.6)
        self.play(Indicate(pb, color=YEL, scale_factor=1.0), run_time=1.0)


class Dot2(Scene):
    """회로도: 코일마다 점 하나."""
    def construct(self):
        self.add(step_tag(2, PUR))
        g, L1, L2, d1, d2, _ = sym(DOWN * .2, 3.0, 1.1)
        beat(self, Create(g), t=1.6, rt=1.2)
        beat(self, FadeIn(d1, scale=3), t=1.0, rt=.4)
        beat(self, FadeIn(d2, scale=3), t=1.0, rt=.4)
        c1 = Circle(.4, color=YEL, stroke_width=4).move_to(d1); c2 = Circle(.4, color=YEL, stroke_width=4).move_to(d2)
        lab = kr("감은 방향 = 점", 40, YEL).to_edge(UP, buff=.9)
        beat(self, Create(c1), Create(c2), FadeIn(lab), t=1.4, rt=.6)
        self.play(Indicate(d1, color=YEL), Indicate(d2, color=YEL), run_time=1.2)


class Dot3(Scene):
    """1차 전류가 점으로 → 2차 점 쪽 +."""
    def construct(self):
        self.add(step_tag(2, PUR))
        g, L1, L2, d1, d2, (xl, xr, yt, yb) = sym(DOWN * .2, 3.0, 1.1); self.add(g, d1, d2)
        ia = Arrow([xl - 1.9, yt, 0], [xl - .3, yt, 0], buff=0, color=BLU, stroke_width=7)
        i1 = tex("i_1", 50, BLU).next_to(ia, UP, .15)
        beat(self, GrowArrow(ia), FadeIn(i1), t=1.4, rt=.6)
        pl = tex("+", 72, GRN).move_to([xr + 1.6, yt - .2, 0]); mi = tex("-", 72, RED).move_to([xr + 1.6, yb + .2, 0])
        beat(self, FadeIn(pl, scale=1.5), t=1.0, rt=.4)
        beat(self, FadeIn(mi, scale=1.5), FadeIn(tex("v_2", 52, ORG).move_to([xr + 1.6, (yt + yb) / 2, 0])), t=1.0, rt=.4)
        rule = card(kr("점으로 들어가면 → 점 쪽이 +", 38, YEL), YEL, .2).to_edge(UP, buff=.5).shift(LEFT * 1)
        beat(self, FadeIn(rule, shift=DOWN * .2), t=1.2, rt=.5)
        k = ValueTracker(0)
        dt = always_redraw(lambda: Dot([xl - 1.9 + 1.6 * (k.get_value() % 1), yt, 0], .1, color=YEL))
        self.add(dt); self.play(k.animate.set_value(2), run_time=2.0, rate_func=linear)


class Dot4(Scene):
    """직렬 연결: 전체 인덕턴스는?"""
    def construct(self):
        self.add(step_tag(2, PUR))
        c1 = coil((-4.0, .3), (-1.0, .3), BLU, n=4, sw=5); c2 = coil((1.0, .3), (4.0, .3), ORG, n=4, sw=5)
        w = Line([-1.0, .3, 0], [1.0, .3, 0], color=INK, stroke_width=4)
        beat(self, Create(c1), FadeIn(tex("L_1", 50, BLU).next_to(c1, UP, .3)), t=1.2, rt=.7)
        beat(self, Create(c2), FadeIn(tex("L_2", 50, ORG).next_to(c2, UP, .3)), t=1.2, rt=.7)
        beat(self, Create(w), t=.6, rt=.4)
        br = BraceBetweenPoints([-4.0, -.3, 0], [4.0, -.3, 0], DOWN, color=MUTE)
        q = VGroup(tex("L =", 72, YEL), kr("?", 72, YEL)).arrange(RIGHT, buff=.2).next_to(br, DOWN, .3)
        beat(self, GrowFromCenter(br), Write(q), t=1.4, rt=.7)
        mm = tex("M", 56, PUR).move_to(UP * 2.9)
        a = CurvedDoubleArrow(c1.get_top() + UP * 1.1, c2.get_top() + UP * 1.1, color=PUR, angle=-PI / 4)
        beat(self, Create(a), FadeIn(mm), t=1.6, rt=.7)


class Dot5(Scene):
    """L1+L2+2M / L1+L2−2M."""
    def construct(self):
        self.add(step_tag(2, PUR))
        def row(y, same):
            c1 = coil((-6.2, y), (-4.4, y), BLU, n=3, sw=5); c2 = coil((-3.6, y), (-1.8, y), ORG, n=3, sw=5)
            w = Line([-4.4, y, 0], [-3.6, y, 0], color=INK, stroke_width=4)
            d1 = Dot([-6.0, y + .45, 0], .12, color=YEL); d2 = Dot([-3.4 if same else -2.0, y + .45, 0], .12, color=YEL)
            f = tex(r"L_1 + L_2 + 2M" if same else r"L_1 + L_2 - 2M", 72, GRN if same else RED).move_to([2.6, y, 0])
            return VGroup(c1, c2, w), VGroup(d1, d2), f
        r1 = row(1.3, True); r2 = row(-1.5, False)
        beat(self, FadeIn(r1[0]), FadeIn(r1[1], scale=2), t=1.0, rt=.5)
        beat(self, Write(r1[2]), t=1.2, rt=.7)
        beat(self, FadeIn(r2[0]), FadeIn(r2[1], scale=2), t=1.0, rt=.5)
        beat(self, Write(r2[2]), t=1.2, rt=.7)
        beat(self, Indicate(r1[2][0][-2:], color=YEL, scale_factor=1.0), t=1.0, rt=.8)
        self.play(Indicate(r2[2][0][-2:], color=YEL, scale_factor=1.0), run_time=1.0)


def sum_rows(items):
    g = VGroup(*[VGroup(kr(a, 34, MUTE), b).arrange(RIGHT, buff=.5) for a, b in items]).arrange(DOWN, buff=.55, aligned_edge=LEFT)
    return g.shift(DOWN * .2)


class Sum1(Scene):
    """중간 정리 (STEP 1~2)."""
    def construct(self):
        self.add(head("여기까지 정리", YEL))
        rows = sum_rows([("직류", tex(r"v_2 = 0", 52, BLU)),
                         ("변화", tex(r"v_2 = M\,\frac{di_1}{dt}", 52, GRN)),
                         ("부호", kr("점 규칙", 42, PUR))])
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.5, rt=.5)
        pulse(self, rows[2], t=1.8)


# ================= STEP 3 전압비 =================
class V1(Scene):
    """철심에 두 코일."""
    def construct(self):
        self.add(step_tag(3, GRN))
        X, cg, w1, w2, path = xfmr(DOWN * .2, 6, 3, W=7, H=4.2)
        beat(self, FadeIn(cg), FadeIn(kr("철심", 38, MUTE).move_to(DOWN * .2)), t=1.4, rt=.8)
        beat(self, LaggedStart(*[Create(x) for x in w1], lag_ratio=.15), t=1.4, rt=1.0)
        beat(self, LaggedStart(*[Create(x) for x in w2], lag_ratio=.15), t=1.4, rt=.8)
        l1 = kr("1차", 38, BLU).next_to(w1, LEFT, .4); l2 = kr("2차", 38, ORG).next_to(w2, RIGHT, .4)
        beat(self, FadeIn(l1), FadeIn(l2), t=1.0, rt=.4)
        self.play(Indicate(cg, color=MUTE, scale_factor=1.0), run_time=1.2)


def flow(sc, path, t=2.5, n=4, col=YEL):
    k = ValueTracker(0)
    ds = always_redraw(lambda: VGroup(*[Dot(path.point_from_proportion((k.get_value() + i / n) % 1), .13, color=col) for i in range(n)]))
    sc.add(ds); sc.play(k.animate.set_value(1), run_time=t, rate_func=linear)
    return ds


class V2(Scene):
    """같은 자속이 두 코일을 지난다."""
    def construct(self):
        self.add(step_tag(3, GRN))
        X, cg, w1, w2, path = xfmr(DOWN * .2, 6, 3, W=7, H=4.2); self.add(X)
        ln = path.copy().set_stroke(YEL, 4); dl = DashedVMobject(ln, num_dashes=50)
        beat(self, Create(dl), t=1.2, rt=1.0)
        phi = tex(r"\Phi", 72, YEL).move_to(UP * 2.6)
        beat(self, Write(phi), t=.8, rt=.4)
        s = kr("같은 자속", 44, YEL).move_to(DOWN * .2)
        beat(self, FadeIn(s), t=.8, rt=.4)
        flow(self, path, t=3.0)


class V3(Scene):
    """한 바퀴마다 같은 전압 → 감은 수에 비례."""
    def construct(self):
        self.add(step_tag(3, GRN))
        X, cg, w1, w2, path = xfmr(DOWN * .2, 6, 3, W=7, H=4.2); self.add(X)
        e1 = VGroup(*[tex("e", 34, BLU).next_to(w, LEFT, .15) for w in w1])
        e2 = VGroup(*[tex("e", 34, ORG).next_to(w, RIGHT, .15) for w in w2])
        self.play(LaggedStart(*[FadeIn(x, scale=1.5) for x in e1], lag_ratio=.3), run_time=1.6)
        self.play(LaggedStart(*[FadeIn(x, scale=1.5) for x in e2], lag_ratio=.3), run_time=1.0)
        s1 = tex(r"6e", 72, BLU).move_to(LEFT * 5.4 + DOWN * .2); s2 = tex(r"3e", 72, ORG).move_to(RIGHT * 5.4 + DOWN * .2)
        beat(self, ReplacementTransform(e1, s1), t=1.2, rt=.8)
        beat(self, ReplacementTransform(e2, s2), t=1.2, rt=.8)
        lab = kr("전압 ∝ 감은 수", 44, YEL).to_edge(UP, buff=.6).shift(LEFT * 1)
        beat(self, Write(lab), t=1.2, rt=.6)


class V4(Scene):
    """V2/V1 = N2/N1."""
    def construct(self):
        self.add(step_tag(3, GRN))
        f = tex(r"\frac{V_2}{V_1} = \frac{N_2}{N_1}", 130, INK)
        beat(self, Write(f[0][:5]), t=1.4, rt=.9)
        beat(self, Write(f[0][5:]), t=1.4, rt=.9)
        b = SurroundingRectangle(f, color=GRN, buff=.3, corner_radius=.15)
        beat(self, Create(b), t=1.2, rt=.6)
        lab = kr("감은 수 비 = 전압 비", 40, GRN).next_to(b, DOWN, .4)
        beat(self, FadeIn(lab, shift=UP * .2), t=1.2, rt=.4)
        pulse(self, f, t=1.6, c=GRN)


def xex(sc, out="?", col=YEL, draw=True):
    """2200V → [10:1] → ? 예제 그림."""
    X = xfmr(DOWN * .3, 10, 1, W=4.4, H=3.4)[0]
    vin = tex(r"2200\,\mathrm{V}", 64, BLU).move_to(LEFT * 4.8 + DOWN * .3)
    r = tex(r"10 : 1", 60, GRN).next_to(X, UP, .35)
    vo = (tex(out, 72, col) if out != "?" else kr("? V", 64, col)).move_to(RIGHT * 4.8 + DOWN * .3)
    return X, vin, r, vo


class V5(Scene):
    """예제: 2200V, 10:1 → ?"""
    def construct(self):
        self.add(step_tag(3, GRN))
        X, vin, r, vo = xex(self)
        beat(self, FadeIn(X), t=1.0, rt=.6)
        beat(self, FadeIn(vin, shift=RIGHT * .3), t=1.2, rt=.4)
        beat(self, Write(r), t=1.2, rt=.5)
        beat(self, FadeIn(vo, scale=1.4), t=1.2, rt=.4)
        self.play(Indicate(vo, color=YEL), run_time=1.0)
        self.play(Indicate(r, color=GRN, scale_factor=1.0), run_time=1.0)


class V6(Scene):
    """2200 ÷ 10 = 220V."""
    def construct(self):
        self.add(step_tag(3, GRN))
        X, vin, r, vo = xex(self, r"220\,\mathrm{V}", GRN); self.add(X, vin, r)
        q = kr("? V", 64, YEL).move_to(vo); self.add(q)
        calc = tex(r"2200 \div 10 = 220", 72, YEL).to_edge(DOWN, buff=.5)
        beat(self, Write(calc), t=1.6, rt=1.0)
        beat(self, ReplacementTransform(q, vo), t=1.4, rt=.6)
        flow(self, xfmr(DOWN * .3, 10, 1, W=4.4, H=3.4)[4], t=2.0, n=3)
        pulse(self, vo, t=1.6, c=GRN)


# ================= STEP 4 전류비와 임피던스 =================
class C1(Scene):
    """전압을 낮추면 전류는?"""
    def construct(self):
        self.add(step_tag(4, ORG))
        X = xfmr(DOWN * .2, 10, 1, W=4.4, H=3.4)[0]
        beat(self, FadeIn(X), t=.8, rt=.5)
        v1 = tex(r"V \downarrow", 80, GRN).move_to(RIGHT * 4.6 + UP * .8)
        beat(self, FadeIn(v1, shift=DOWN * .3), t=1.4, rt=.5)
        i1 = VGroup(tex("I", 80, ORG), kr("?", 80, YEL)).arrange(RIGHT, buff=.2).move_to(RIGHT * 4.6 + DOWN * 1.2)
        beat(self, FadeIn(i1, scale=1.3), t=1.4, rt=.5)
        a = Arrow(LEFT * 6 + DOWN * .2, LEFT * 2.6 + DOWN * .2, buff=0, color=BLU, stroke_width=6)
        beat(self, GrowArrow(a), t=1.0, rt=.5)
        self.play(Indicate(i1[1], color=YEL), run_time=1.0)


class C2(Scene):
    """손실 없음: 들어간 전력 = 나온 전력."""
    def construct(self):
        self.add(step_tag(4, ORG))
        base = DOWN * 2.0
        X = xfmr(UP * 1.9, 6, 3, W=3.2, H=2.4)[0]; self.add(X)
        b1 = bar(3.0, 1.6, BLU, base + LEFT * 3.2, "들어간 전력", 32)
        b2 = bar(3.0, 1.6, ORG, base + RIGHT * 3.2, "나온 전력", 32)
        beat(self, GrowFromEdge(b1[0], DOWN), FadeIn(b1[1]), t=1.4, rt=.8)
        beat(self, GrowFromEdge(b2[0], DOWN), FadeIn(b2[1]), t=1.4, rt=.8)
        eq = tex("=", 110, YEL).move_to(base + UP * 1.2)
        beat(self, FadeIn(eq, scale=1.5), t=1.0, rt=.4)
        lab = kr("손실 0", 40, YEL).next_to(eq, DOWN, .3)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(Indicate(eq, color=YEL), run_time=1.0)


class C3(Scene):
    """V1 I1 = V2 I2 → I2/I1 = N1/N2."""
    def construct(self):
        self.add(step_tag(4, ORG))
        f1 = tex(r"V_1 I_1 = V_2 I_2", 100, INK).shift(UP * 1.3)
        beat(self, Write(f1), t=1.6, rt=1.0)
        f2 = tex(r"\frac{I_2}{I_1} = \frac{N_1}{N_2}", 110, ORG).shift(DOWN * 1.3)
        a = Arrow(f1.get_bottom(), f2.get_top(), buff=.15, color=MUTE)
        beat(self, GrowArrow(a), t=.6, rt=.4)
        beat(self, Write(f2), t=1.4, rt=1.0)
        lab = kr("반대!", 52, YEL).next_to(f2, RIGHT, .6)
        beat(self, FadeIn(lab, scale=1.4), t=1.2, rt=.4)
        sw = SurroundingRectangle(f2[0][-5:], color=YEL, buff=.12)
        beat(self, Create(sw), t=1.0, rt=.5)


class C4(Scene):
    """같은 넓이: 2200V×1A = 220V×10A."""
    def construct(self):
        self.add(step_tag(4, ORG))
        s = .12
        r1 = Rectangle(width=1 * .55, height=22 * s * 1.6, color=BLU, fill_color=BLU, fill_opacity=.8, stroke_width=0).move_to(LEFT * 3.8 + DOWN * 2.4, aligned_edge=DOWN)
        r2 = Rectangle(width=10 * .55, height=2.2 * s * 1.6, color=ORG, fill_color=ORG, fill_opacity=.8, stroke_width=0).move_to(RIGHT * 2.0 + DOWN * 2.4, aligned_edge=DOWN)
        beat(self, GrowFromEdge(r1, DOWN), t=1.0, rt=.6)
        t1 = VGroup(tex(r"2200\,\mathrm{V}", 60, BLU), tex(r"1\,\mathrm{A}", 60, BLU)).arrange(DOWN, buff=.15).next_to(r1, RIGHT, .3)
        beat(self, FadeIn(t1), t=1.0, rt=.4)
        beat(self, GrowFromEdge(r2, LEFT), t=1.0, rt=.6)
        t2 = VGroup(tex(r"220\,\mathrm{V}", 60, ORG), tex(r"10\,\mathrm{A}", 72, YEL)).arrange(RIGHT, buff=.4).next_to(r2, UP, .3)
        beat(self, FadeIn(t2), t=1.2, rt=.4)
        eq = kr("넓이(전력) 같음", 40, YEL).to_edge(UP, buff=.7).shift(LEFT * 1)
        beat(self, Write(eq), t=1.2, rt=.6)
        self.play(Indicate(t2[1], color=YEL), run_time=1.0)


class C5(Scene):
    """2차 저항이 1차에선 제곱배."""
    def construct(self):
        self.add(step_tag(4, ORG))
        g, L1, L2, d1, d2, (xl, xr, yt, yb) = sym(DOWN * .4 + RIGHT * .6, 2.6, .9, lead=.9)
        beat(self, Create(g), t=1.0, rt=.8)
        R = resistor([xr + .9, yt, 0], [xr + .9, yb, 0], ORG)
        rl = tex("R_L", 50, ORG).next_to(R, RIGHT, .3)
        beat(self, Create(R), FadeIn(rl), t=1.0, rt=.6)
        eye = VGroup(Arrow([xl - 2.8, (yt + yb) / 2, 0], [xl - 1.0, (yt + yb) / 2, 0], buff=0, color=BLU, stroke_width=6))
        beat(self, GrowArrow(eye[0]), t=.8, rt=.4)
        f = tex(r"R_{in} = \left(\frac{N_1}{N_2}\right)^{2} R_L", 80, YEL).to_edge(UP, buff=.5)
        beat(self, Write(f), t=1.6, rt=1.1)
        sq = SurroundingRectangle(f[0][4:12], color=ORG, buff=.1)
        beat(self, Create(sq), FadeIn(kr("제곱배", 38, ORG).next_to(sq, DOWN, .2).shift(RIGHT * 3.4)), t=1.4, rt=.5)


class C6(Scene):
    """10:1 → ×100: 22Ω → 2200Ω."""
    def construct(self):
        self.add(step_tag(4, ORG))
        a = tex(r"22\,\Omega", 96, ORG).shift(RIGHT * 4 + DOWN * .2)
        beat(self, FadeIn(a), t=1.0, rt=.4)
        X = xfmr(DOWN * .2, 10, 1, W=3.2, H=2.6)[0]
        r = tex(r"10:1", 52, GRN).next_to(X, UP, .3)
        beat(self, FadeIn(X), FadeIn(r), t=1.0, rt=.5)
        m = tex(r"\times 10^2 = \times 100", 64, YEL).next_to(X, DOWN, .5)
        beat(self, Write(m), t=1.4, rt=.9)
        b = tex(r"2200\,\Omega", 96, YEL).shift(LEFT * 4.8 + DOWN * .2)
        ar = Arrow(X.get_left() + LEFT * .6, b.get_right() + RIGHT * .1, buff=0, color=YEL)
        beat(self, GrowArrow(ar), t=.6, rt=.4)
        beat(self, Write(b), t=1.2, rt=.7)
        pulse(self, b, t=1.6)


# ================= STEP 5 높은 전압 송전 =================
def plant(c=INK):
    b = Rectangle(width=1.8, height=1.2, color=c, stroke_width=5)
    s1 = Rectangle(width=.35, height=1.1, color=c, stroke_width=5).next_to(b, UP, 0).shift(LEFT * .45)
    s2 = Rectangle(width=.35, height=.8, color=c, stroke_width=5).next_to(b, UP, 0).shift(RIGHT * .2)
    bolt = kr("⚡", 44, YEL).move_to(b)
    return VGroup(b, s1, s2, bolt)


class T1(Scene):
    """발전소 → 송전선 → 동네, 왜 수십만 V?"""
    def construct(self):
        self.add(step_tag(5, RED))
        p = plant().move_to(LEFT * 5.4 + DOWN * .6); h = house().scale(.8).move_to(RIGHT * 5.4 + DOWN * .5)
        beat(self, Create(p), t=.9, rt=.6)
        beat(self, Create(h), t=.9, rt=.6)
        ln = VGroup(*[Line(LEFT * 4.3 + UP * (.5 + k * .3), RIGHT * 4.4 + UP * (.5 + k * .3), color=MUTE, stroke_width=3) for k in range(3)])
        beat(self, Create(ln), t=1.0, rt=.7)
        v = tex(r"345{,}000\,\mathrm{V}", 64, RED).next_to(ln, UP, .4)
        beat(self, FadeIn(v, shift=DOWN * .2), t=1.2, rt=.4)
        q = kr("왜?", 72, YEL).next_to(ln, DOWN, .8)
        beat(self, FadeIn(q, scale=1.5), t=1.0, rt=.4)
        k = ValueTracker(0)
        ds = always_redraw(lambda: VGroup(*[Dot(LEFT * 4.3 + RIGHT * 8.7 * ((k.get_value() + i / 6) % 1) + UP * .8, .09, color=YEL) for i in range(6)]))
        self.add(ds); self.play(k.animate.set_value(1), run_time=1.6, rate_func=linear)


class T2(Scene):
    """전선 저항 → I²R 열."""
    def construct(self):
        self.add(step_tag(5, RED))
        w1 = Line(LEFT * 6 + UP * .3, LEFT * 1.6 + UP * .3, color=INK, stroke_width=5)
        R = resistor(LEFT * 1.6 + UP * .3, RIGHT * 1.6 + UP * .3, RED)
        w2 = Line(RIGHT * 1.6 + UP * .3, RIGHT * 6 + UP * .3, color=INK, stroke_width=5)
        beat(self, Create(w1), Create(R), Create(w2), t=1.2, rt=.8)
        rl = kr("전선 저항 R", 36, RED).next_to(R, DOWN, .4)
        beat(self, FadeIn(rl), t=.8, rt=.3)
        k = ValueTracker(0)
        ds = always_redraw(lambda: VGroup(*[Dot(LEFT * 6 + RIGHT * 12 * ((k.get_value() + i / 8) % 1) + UP * .3, .1, color=BLU) for i in range(8)]))
        self.add(ds); self.play(k.animate.set_value(.5), run_time=1.2, rate_func=linear)
        ht = heat(UP * 1.2, ORG, 4)
        self.play(Create(ht), k.animate.set_value(.8), run_time=.8, rate_func=linear)
        f = tex(r"P_{loss} = I^2 R", 84, ORG).to_edge(DOWN, buff=.7)
        self.play(Write(f), k.animate.set_value(1.4), run_time=1.2, rate_func=linear)
        self.play(Circumscribe(f[0][-3:-1], color=YEL, fade_out=True), k.animate.set_value(2.2), run_time=1.6, rate_func=linear)


class T3(Scene):
    """같은 전력, V×10 → I÷10."""
    def construct(self):
        self.add(step_tag(5, RED))
        base = DOWN * 2.3
        v1 = bar(.4, 1.3, BLU, base + LEFT * 4.6, "전압", 30); v2 = bar(4.0, 1.3, BLU, base + LEFT * 2.6, "×10", 30)
        i1 = bar(4.0, 1.3, ORG, base + RIGHT * 2.6, "전류", 30); i2 = bar(.4, 1.3, ORG, base + RIGHT * 4.6, "÷10", 30)
        beat(self, FadeIn(v1), FadeIn(i1), t=1.0, rt=.5)
        beat(self, GrowFromEdge(v2[0], DOWN), FadeIn(v2[1]), t=1.4, rt=.8)
        beat(self, GrowFromEdge(i2[0], DOWN), FadeIn(i2[1]), t=1.4, rt=.8)
        p = tex(r"P = V I", 72, YEL).to_edge(UP, buff=.8)
        beat(self, Write(p), FadeIn(kr("그대로", 36, YEL).next_to(p, DOWN, .2)), t=1.4, rt=.6)
        f = tex(r"\tfrac{1}{10}", 96, ORG).next_to(i2, UP, .3)
        beat(self, Write(f), t=1.0, rt=.5)


class T4(Scene):
    """손실 1/100."""
    def construct(self):
        self.add(step_tag(5, RED))
        base = DOWN * 2.2
        b1 = bar(4.2, 1.8, RED, base + LEFT * 2.6, "그냥 보내면", 32)
        b2 = bar(.042 * 1.0 + .03, 1.8, GRN, base + RIGHT * 2.6, "10배 올리면", 32)
        beat(self, GrowFromEdge(b1[0], DOWN), FadeIn(b1[1]), t=1.4, rt=.8)
        f0 = tex(r"\left(\tfrac{1}{10}\right)^2", 80, INK).move_to(UP * 2.5 + RIGHT * 2.6)
        beat(self, Write(f0), t=1.2, rt=.7)
        beat(self, GrowFromEdge(b2[0], DOWN), FadeIn(b2[1]), t=1.0, rt=.6)
        f = tex(r"= \tfrac{1}{100}", 96, YEL).next_to(f0, DOWN, .3)
        beat(self, Write(f), t=1.2, rt=.6)
        pulse(self, f, t=1.6)


class T5(Scene):
    """발전소 → 승압 → 송전 → 강압 → 집."""
    def construct(self):
        self.add(step_tag(5, RED))
        p = plant().scale(.75).move_to(LEFT * 6 + DOWN * .3)
        X1 = xfmr(ORIGIN, 2, 6, W=1.6, H=1.5)[0].move_to(LEFT * 3.3 + DOWN * .3)
        X2 = xfmr(ORIGIN, 6, 2, W=1.6, H=1.5)[0].move_to(RIGHT * 3.3 + DOWN * .3)
        h = house().scale(.6).move_to(RIGHT * 6 + DOWN * .2)
        seq = [p, X1, X2, h]
        lines = [Line(LEFT * 5.1 + DOWN * .3, LEFT * 4.2 + DOWN * .3, color=MUTE, stroke_width=4),
                 Line(LEFT * 2.4 + DOWN * .3, RIGHT * 2.4 + DOWN * .3, color=RED, stroke_width=6),
                 Line(RIGHT * 4.2 + DOWN * .3, RIGHT * 5.3 + DOWN * .3, color=MUTE, stroke_width=4)]
        beat(self, FadeIn(p), t=.6, rt=.4)
        beat(self, Create(lines[0]), FadeIn(X1), FadeIn(kr("올려서 ↑", 34, RED).next_to(X1, UP, .3)), t=1.2, rt=.6)
        beat(self, Create(lines[1]), FadeIn(tex(r"345{,}000\,\mathrm{V}", 44, RED).next_to(lines[1], UP, .25)), t=1.2, rt=.6)
        beat(self, FadeIn(X2), FadeIn(kr("내려서 ↓", 34, GRN).next_to(X2, UP, .3)), t=1.2, rt=.6)
        beat(self, Create(lines[2]), FadeIn(h), FadeIn(tex(r"220\,\mathrm{V}", 44, GRN).next_to(h, DOWN, .3)), t=1.2, rt=.6)
        k = ValueTracker(0)
        ds = always_redraw(lambda: VGroup(*[Dot(LEFT * 2.4 + RIGHT * 4.8 * ((k.get_value() + i / 5) % 1) + DOWN * .3, .09, color=YEL) for i in range(5)]))
        self.add(ds); self.play(k.animate.set_value(1), run_time=1.6, rate_func=linear)


class T6(Scene):
    """교류라서 가능, 직류는 안 됨."""
    def construct(self):
        self.add(step_tag(5, RED))
        a = acsrc(LEFT * 5.2 + UP * 1.3, GRN, .6); b = battery(LEFT * 5.2 + DOWN * 1.6, RED, 1.1)
        X1 = xfmr(ORIGIN, 4, 2, W=2.0, H=1.7)[0].move_to(LEFT * 1.6 + UP * 1.3)
        X2 = xfmr(ORIGIN, 4, 2, W=2.0, H=1.7)[0].move_to(LEFT * 1.6 + DOWN * 1.6)
        beat(self, FadeIn(a), FadeIn(X1), FadeIn(kr("교류", 38, GRN).next_to(a, DOWN, .2)), t=1.2, rt=.5)
        ok = kr("✓  바뀜", 52, GRN).move_to(RIGHT * 3.6 + UP * 1.3)
        beat(self, FadeIn(ok, scale=1.3), t=1.2, rt=.4)
        beat(self, FadeIn(b), FadeIn(X2), FadeIn(kr("직류", 38, RED).next_to(b, DOWN, .3)), t=1.2, rt=.5)
        no = kr("✕  0 V", 52, RED).move_to(RIGHT * 3.6 + DOWN * 1.6)
        beat(self, FadeIn(no, scale=1.3), t=1.2, rt=.4)
        self.play(Indicate(ok, color=GRN, scale_factor=1.0), run_time=1.0)
        self.play(Indicate(no, color=RED, scale_factor=1.0), run_time=1.0)


# ================= 정리 =================
def final_rows():
    return sum_rows([("상호 인덕턴스", VGroup(tex(r"v_2 = M\,\frac{di_1}{dt}", 50, BLU), kr("· 부호는 점 규칙", 36, PUR)).arrange(RIGHT, buff=.25)),
                     ("변압기", VGroup(tex(r"\frac{V_2}{V_1} = \frac{N_2}{N_1}", 50, GRN), tex(r"\frac{I_2}{I_1} = \frac{N_1}{N_2}", 50, ORG),
                                       tex(r"R \times \left(\frac{N_1}{N_2}\right)^2", 50, ORG)).arrange(RIGHT, buff=.45)),
                     ("송전", VGroup(kr("전압 ×10 →", 36, RED), kr("손실 1/100", 40, YEL)).arrange(RIGHT, buff=.25))])


class F1(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows()
        beat(self, FadeIn(rows[0], shift=RIGHT * .3), t=2.0, rt=.5)
        pulse(self, rows[0], t=2.4, c=BLU)


class F2(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows(); self.add(rows[0])
        r = rows[1]; self.add(r[0])
        for m in r[1]:
            beat(self, FadeIn(m, shift=RIGHT * .3), t=1.5, rt=.5)
        pulse(self, r[1], t=1.8, c=GRN)


class F3(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows(); self.add(rows[0], rows[1])
        beat(self, FadeIn(rows[2], shift=RIGHT * .3), t=2.0, rt=.6)
        pulse(self, rows[2], t=2.8)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("변압기 · 상호 인덕턴스", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        beat(self, FadeIn(t[0]), t=.8, rt=.3)
        for m in t[1]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.4, rt=.4)
        pulse(self, t, t=2.0)


class Next(Scene):
    def construct(self):
        items = ["교류 전력", "3상", "변압기", "주파수 응답"]
        cards = VGroup(*[card(kr(s, 36, YEL if s == "변압기" else MUTE), YEL if s == "변압기" else "#2a2e37", .3) for s in items]).arrange(RIGHT, buff=.35)
        lab = kr("재생목록 · 회로이론 한눈에", 40, INK).next_to(cards, UP, .6)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cards], lag_ratio=.3), run_time=1.6)
        arr = Arrow(cards[2].get_bottom() + DOWN * .2, cards[3].get_bottom() + DOWN * .2, buff=0, color=YEL, path_arc=PI / 2)
        beat(self, Create(arr), t=1.6, rt=.8)


# ================= 쇼츠 전용 =================
class BQ(Scene):
    """변압기에 직류를 넣으면?"""
    def construct(self):
        X = xfmr(ORIGIN, 6, 3, W=4.4, H=3.4)[0]
        beat(self, FadeIn(X), t=.8, rt=.5)
        b = battery(LEFT * 4.6, RED, 1.3)
        beat(self, FadeIn(b), FadeIn(kr("직류", 44, RED).next_to(b, DOWN, .4)), t=1.2, rt=.5)
        q = kr("? V", 80, YEL).move_to(RIGHT * 4.6)
        beat(self, FadeIn(q, scale=1.4), t=1.2, rt=.4)
        self.play(Indicate(q, color=YEL), run_time=1.0)
        self.play(Indicate(b, color=RED, scale_factor=1.0), run_time=1.0)


class CQ(Scene):
    """회로도의 점 두 개."""
    def construct(self):
        g, L1, L2, d1, d2, _ = sym(DOWN * .3, 3.0, 1.1)
        beat(self, Create(g), t=1.2, rt=1.0)
        beat(self, FadeIn(d1, scale=3), FadeIn(d2, scale=3), t=1.0, rt=.5)
        q = kr("?", 96, YEL).to_edge(UP, buff=.5)
        c1 = Circle(.45, color=YEL, stroke_width=5).move_to(d1); c2 = Circle(.45, color=YEL, stroke_width=5).move_to(d2)
        beat(self, Create(c1), Create(c2), FadeIn(q, scale=1.4), t=1.4, rt=.6)
        self.play(Indicate(d1, color=YEL, scale_factor=2), Indicate(d2, color=YEL, scale_factor=2), run_time=1.2)
        self.wait(.4)


class DQ(Scene):
    """전압 ÷10 → 전류 ×10."""
    def construct(self):
        X = xfmr(UP * 1.0, 10, 1, W=3.4, H=2.4)[0]
        beat(self, FadeIn(X), t=.7, rt=.4)
        v = tex(r"V \div 10", 96, GRN).move_to(LEFT * 3.2 + DOWN * 2.0)
        beat(self, Write(v), t=1.2, rt=.6)
        a = Arrow(LEFT * .9 + DOWN * 2.0, RIGHT * .9 + DOWN * 2.0, buff=0, color=MUTE)
        i = tex(r"I \times 10", 110, YEL).move_to(RIGHT * 3.4 + DOWN * 2.0)
        beat(self, GrowArrow(a), t=.5, rt=.4)
        beat(self, Write(i), t=1.2, rt=.6)
        pulse(self, i, t=1.6)


class DW(Scene):
    """용접기: 전압 낮고 전류 큼."""
    def construct(self):
        X = xfmr(ORIGIN, 10, 1, W=2.8, H=2.4)[0].move_to(LEFT * 3.6 + UP * .3)
        beat(self, FadeIn(X), FadeIn(kr("용접기", 44, INK).next_to(X, DOWN, .4)), t=1.0, rt=.5)
        rod = Line(RIGHT * 1.6 + UP * 2.0, RIGHT * 2.8 + UP * .1, color=MUTE, stroke_width=10)
        plate = Rectangle(width=4.2, height=.35, color=MUTE, fill_color=MUTE, fill_opacity=.6, stroke_width=0).move_to(RIGHT * 3.2 + DOWN * .35)
        beat(self, Create(rod), FadeIn(plate), t=.8, rt=.5)
        sp = VGroup(*[Line(RIGHT * 2.85 + DOWN * .05, RIGHT * 2.85 + DOWN * .05 + U(a) * .7, color=YEL, stroke_width=5) for a in (20, 50, 80, 110, 140, 160)])
        beat(self, Create(sp), t=.8, rt=.4)
        l1 = kr("전압 ↓", 44, GRN).move_to(LEFT * 1.2 + DOWN * 2.5); l2 = kr("전류 ↑↑", 52, YEL).move_to(RIGHT * 3.0 + DOWN * 2.5)
        beat(self, FadeIn(l1), t=1.0, rt=.4)
        beat(self, FadeIn(l2, scale=1.3), t=1.0, rt=.4)
        for _ in range(2):
            self.play(sp.animate.rotate(PI / 12, about_point=RIGHT * 2.85 + DOWN * .05), run_time=.4)
            self.play(sp.animate.rotate(-PI / 12, about_point=RIGHT * 2.85 + DOWN * .05), run_time=.4)


class EQ(Scene):
    """22Ω 이 변압기 너머에선 2200Ω."""
    def construct(self):
        X = xfmr(ORIGIN, 10, 1, W=3.0, H=2.6)[0]
        beat(self, FadeIn(X), t=.7, rt=.4)
        R = resistor(RIGHT * 3.4 + UP * 1.1, RIGHT * 3.4 + DOWN * 1.1, ORG)
        a = tex(r"22\,\Omega", 72, ORG).next_to(R, RIGHT, .3)
        beat(self, Create(R), FadeIn(a), t=1.2, rt=.6)
        eye = Arrow(LEFT * 6 + UP * 0, LEFT * 2.0, buff=0, color=BLU, stroke_width=6)
        beat(self, GrowArrow(eye), t=.8, rt=.4)
        b = tex(r"2200\,\Omega", 80, YEL).next_to(eye, UP, .4)
        q = kr("처럼 보임", 36, YEL).next_to(b, DOWN, .15).shift(DOWN * .9)
        beat(self, Write(b), FadeIn(q), t=1.4, rt=.7)
        pulse(self, b, t=1.6)


class EZ1(Scene):
    """R = V/I: V ×10, I ÷10 → ×100."""
    def construct(self):
        f = tex(r"R = \frac{V}{I}", 110, INK).shift(LEFT * 3.2)
        beat(self, Write(f), t=1.2, rt=.8)
        v = tex(r"V \times 10", 80, GRN).move_to(RIGHT * 2.6 + UP * 1.4)
        i = tex(r"I \div 10", 80, ORG).move_to(RIGHT * 2.6 + DOWN * .1)
        beat(self, FadeIn(v, shift=LEFT * .3), t=1.0, rt=.4)
        beat(self, FadeIn(i, shift=LEFT * .3), t=1.0, rt=.4)
        r = tex(r"R \times 100", 96, YEL).move_to(RIGHT * 2.6 + DOWN * 2.0)
        beat(self, Write(r), t=1.2, rt=.6)
        pulse(self, r, t=1.6)


class ESpk(Scene):
    """앰프 — 변압기 — 스피커."""
    def construct(self):
        amp = card(kr("앰프", 44, BLU), BLU, .4).move_to(LEFT * 4.8)
        beat(self, FadeIn(amp), t=.8, rt=.4)
        X = xfmr(ORIGIN, 8, 2, W=2.6, H=2.2)[0]
        w1 = Line(amp.get_right(), X.get_left(), color=INK, stroke_width=4)
        beat(self, Create(w1), FadeIn(X), t=1.0, rt=.5)
        spk = VGroup(Rectangle(width=.5, height=.9, color=ORG, stroke_width=5),
                     Polygon([.25, .45, 0], [1.0, 1.0, 0], [1.0, -1.0, 0], [.25, -.45, 0], color=ORG, stroke_width=5)).move_to(RIGHT * 4.6)
        w2 = Line(X.get_right(), spk.get_left(), color=INK, stroke_width=4)
        beat(self, Create(w2), FadeIn(spk), FadeIn(kr("스피커", 36, ORG).next_to(spk, DOWN, .3)), t=1.0, rt=.5)
        m = kr("저항 맞추기", 48, YEL).to_edge(UP, buff=.8)
        beat(self, Write(m), t=1.2, rt=.6)
        waves = VGroup(*[Arc(radius=.4 + .35 * k, start_angle=-PI / 4, angle=PI / 2, color=YEL, stroke_width=4).move_arc_center_to(spk.get_right() + LEFT * .1) for k in range(3)])
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=.3), run_time=1.0)
        self.play(FadeOut(waves), run_time=.4)
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=.3), run_time=1.0)
