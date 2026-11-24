# 주파수 응답(전달함수·RC 필터·차단 주파수·보드선도·공진) 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(long.json 에서 그 문장 시작에 붙임). 변압기 편(transformer/manim/scenes.py) 형식을 따른다.
# 끝까지 보게 만드는 4원칙: 1.5~2.5초마다 화면에 새 요소(내용으로 변화, 전환·반복 확대 없음), 4초 넘게 멈춘 화면 없음.
# 검산: f_c = 1/(2π·1.6kΩ·0.1μF) ≈ 995Hz ≈ 1kHz, |H(ω_c)| = 0.707 = −3dB, ω≫ω_c 에서 −20dB/dec. 공진 ω0 = 1/√LC.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
from manim import *
import numpy as np, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
STEPC = [BLU, PUR, GRN, ORG, RED]
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


def P3(p): return np.array([p[0], p[1], 0.0]) if len(p) == 2 else np.array(p, dtype=float)
def wire(a, b, c=INK, w=4): return Line(P3(a), P3(b), color=c, stroke_width=w)


# ---------- 회로 부품 ----------
def coil(a, b, c=INK, n=4, sw=5):
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L
    seg = L * .6; r = seg / n / 2; s0 = a + u * (L - seg) / 2
    g = VGroup(Line(a, s0, color=c, stroke_width=sw))
    ang = np.arctan2(u[1], u[0])
    for i in range(n):
        ctr = s0 + u * (r * (2 * i + 1))
        g.add(Arc(radius=r, start_angle=ang + PI, angle=-PI, color=c, stroke_width=sw).move_arc_center_to(ctr))
    g.add(Line(s0 + u * seg, b, color=c, stroke_width=sw))
    return g


def resistor(a, b, c=INK, sw=5):
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    s0 = a + u * L * .25; seg = L * .5; pts = [a, s0]
    for i in range(6):
        pts.append(s0 + u * seg * (i + .5) / 6 + n * (.22 if i % 2 == 0 else -.22))
    pts += [s0 + u * seg, b]
    return VMobject(color=c, stroke_width=sw).set_points_as_corners(pts)


def capacitor(a, b, c=INK, sw=5, gap=.26, w=.9):
    """a→b 사이 커패시터: 가운데에 판 두 개. 반환 (그룹, 판1, 판2, 리드1, 리드2)."""
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    m = (a + b) / 2; p1 = m - u * gap / 2; p2 = m + u * gap / 2
    l1 = Line(a, p1, color=c, stroke_width=sw); l2 = Line(p2, b, color=c, stroke_width=sw)
    s1 = Line(p1 - n * w / 2, p1 + n * w / 2, color=c, stroke_width=sw + 3); s2 = Line(p2 - n * w / 2, p2 + n * w / 2, color=c, stroke_width=sw + 3)
    return VGroup(l1, s1, s2, l2), s1, s2, l1, l2


def acsrc(p, c=INK, r=.55):
    p = P3(p); ax = np.linspace(-.35, .35, 30)
    s = VMobject(color=c, stroke_width=5).set_points_smoothly([p + np.array([x, .22 * np.sin(x / .35 * PI), 0]) for x in ax])
    return VGroup(Circle(r, color=c, stroke_width=5).move_to(p), s)


def battery(p, c=INK, s=1.0):
    p = P3(p)
    return VGroup(Line(p + UP * .18 * s + LEFT * .55 * s, p + UP * .18 * s + RIGHT * .55 * s, color=c, stroke_width=6),
                  Line(p + DOWN * .18 * s + LEFT * .3 * s, p + DOWN * .18 * s + RIGHT * .3 * s, color=c, stroke_width=10))


def term(p, c=INK):
    return Circle(.1, color=c, fill_color=BG, fill_opacity=1, stroke_width=4).move_to(P3(p))


def rc_circuit(o=ORIGIN, hp=False, cR=BLU, cC=ORG, src=True, W=6.4, H=2.8):
    """RC 필터. hp=False: R 가로(위) + C 세로(출력) = 저역통과, hp=True: C 가로 + R 세로 = 고역통과.
    반환 dict: g(전체), ser(가로 소자), sh(세로 소자), out(출력 표시), pts."""
    o = P3(o); x0, x1, xm = o[0] - W / 2, o[0] + W / 2, o[0] + .6; yt, yb = o[1] + H / 2, o[1] - H / 2
    g = VGroup(); D = {}
    if src:
        s = acsrc((x0, o[1]), INK); g.add(s, wire((x0, o[1] + .55), (x0, yt)), wire((x0, o[1] - .55), (x0, yb))); D["src"] = s
    a, b = (x0, yt), (xm, yt)
    if hp:
        ser = capacitor(a, b, cC)[0]; sh = resistor((xm, yt), (xm, yb), cR)
    else:
        ser = resistor(a, b, cR); sh = capacitor((xm, yt), (xm, yb), cC)[0]
    g.add(ser, sh, wire((xm, yt), (x1, yt)), wire(P3((x0, yb)), P3((x1, yb))))
    t1, t2 = term((x1, yt)), term((x1, yb)); g.add(t1, t2)
    vo = VGroup(tex("+", 40, YEL).next_to(t1, DOWN, .15), tex("-", 40, YEL).next_to(t2, UP, .15), tex(r"V_{out}", 44, YEL).move_to((x1 + .1, o[1], 0)))
    vo[2].next_to(VGroup(vo[0], vo[1]), RIGHT, .15)
    D.update(g=g, ser=ser, sh=sh, out=vo, xm=xm, x0=x0, x1=x1, yt=yt, yb=yb)
    return D


def rlc_circuit(o=ORIGIN, W=8.0, H=2.6):
    o = P3(o); x0, x1 = o[0] - W / 2, o[0] + W / 2; yt, yb = o[1] + H / 2, o[1] - H / 2
    s = acsrc((x0, o[1]))
    xs = np.linspace(x0, x1, 4)
    R = resistor((xs[0], yt), (xs[1], yt), BLU); L = coil((xs[1], yt), (xs[2], yt), GRN); C = capacitor((xs[2], yt), (xs[3], yt), ORG)[0]
    g = VGroup(s, wire((x0, o[1] + .55), (x0, yt)), wire((x0, o[1] - .55), (x0, yb)), R, L, C, wire((x1, yt), (x1, yb)), wire((x0, yb), (x1, yb)))
    labs = VGroup(tex("R", 48, BLU).next_to(R, UP, .3), tex("L", 48, GRN).next_to(L, UP, .3), tex("C", 48, ORG).next_to(C, UP, .45))
    return g, R, L, C, labs


# ---------- 그래프 ----------
def lp(x):  # x = log10(ω/ω_c)
    return 1 / np.sqrt(1 + 10 ** (2 * x))


def hp_(x):
    w = 10 ** x; return w / np.sqrt(1 + w * w)


def db(v): return 20 * np.log10(max(v, 1e-9))


def bp(x, Q=3.0):
    w = 10 ** x; return 1 / np.sqrt(1 + Q * Q * (w - 1 / w) ** 2)


def mag_axes(xl=10, yl=3.8, o=DOWN * .3, xlab=True):
    ax = Axes(x_range=[-2, 2, 1], y_range=[0, 1.15, .5], x_length=xl, y_length=yl, tips=True,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False, "tip_length": .2}).move_to(o)
    g = VGroup(ax)
    if xlab:
        g.add(kr("주파수 →", 28, MUTE).next_to(ax.x_axis.get_end(), DOWN, .2).shift(LEFT * .6))
        g.add(tex(r"|H|", 40, MUTE).next_to(ax.y_axis.get_end(), LEFT, .15))
        g.add(tex("1", 34, MUTE).next_to(ax.c2p(-2, 1), LEFT, .15))
    return ax, g


def bode_axes(xl=10.4, yl=4.2, o=DOWN * .4, ymin=-45):
    ax = Axes(x_range=[-2, 2, 1], y_range=[ymin, 6, 10], x_length=xl, y_length=yl, tips=False,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False}).move_to(o)
    # x 축을 위(0dB)에 두지 않고 아래에 그림
    grid = VGroup(*[DashedLine(ax.c2p(k, ymin), ax.c2p(k, 6), color="#2a2e37", stroke_width=2) for k in (-1, 0, 1, 2)],
                  *[DashedLine(ax.c2p(-2, v), ax.c2p(2, v), color="#2a2e37", stroke_width=2) for v in (0, -20, -40)])
    yl_ = VGroup(*[tex(f"{v}", 30, MUTE).next_to(ax.c2p(-2, v), LEFT, .15) for v in (0, -20, -40)])
    ylab = kr("dB", 30, MUTE).next_to(ax.c2p(-2, 6), UP + LEFT, .1)
    return ax, VGroup(grid, ax, yl_, ylab)


def dec_labels(ax, ymin=-45, base=("10", "100", "1k", "10k", "100k")):
    return VGroup(*[kr(s, 26, MUTE).next_to(ax.c2p(k, ymin), DOWN, .15) for k, s in zip(range(-2, 3), base)])


def sine(ax_or_pt, amp, freq, length, col, phase=0, n=200, sw=5):
    """가운데 pt, 길이 length, 진폭 amp(단위), freq 주기 수."""
    p = P3(ax_or_pt); xs = np.linspace(-length / 2, length / 2, n)
    return VMobject(color=col, stroke_width=sw).set_points_smoothly([p + np.array([x, amp * np.sin(2 * PI * freq * (x + length / 2) / length - phase), 0]) for x in xs])


def boxio(lab="회로", w=2.6, h=1.6, c=MUTE):
    b = RoundedRectangle(width=w, height=h, corner_radius=.2, color=c, stroke_width=5, fill_color="#181b21", fill_opacity=1)
    return VGroup(b, kr(lab, 40, INK))


# ================= 인트로 =================
class Hook(Scene):
    """음악 파형(저음+고음) → R·C → 저음만."""
    def construct(self):
        f = lambda x: .55 * np.sin(2 * PI * x * 1.5) + .22 * np.sin(2 * PI * x * 14)
        g = lambda x: .55 * np.sin(2 * PI * x * 1.5)
        ax1 = Axes(x_range=[0, 1, 1], y_range=[-1, 1, 1], x_length=4.2, y_length=2.2, tips=False, axis_config={"stroke_opacity": 0}).move_to(LEFT * 4.3 + UP * .3)
        ax2 = ax1.copy().move_to(RIGHT * 4.3 + UP * .3)
        w1 = ax1.plot(f, x_range=[0, 1, .002], color=PUR, stroke_width=4)
        beat(self, Create(w1), FadeIn(kr("음악", 36, PUR).next_to(ax1, DOWN, .3)), t=1.0, rt=.8)
        r = resistor((-1.6, 1.0), (.4, 1.0), BLU); c = capacitor((.9, 1.0), (.9, -.9), ORG)[0]
        circ = VGroup(r, wire((.4, 1.0), (1.6, 1.0)), c, wire((-1.6, -.9), (1.6, -.9)))
        beat(self, Create(r), FadeIn(tex("R", 44, BLU).next_to(r, UP, .25)), t=1.0, rt=.6)
        beat(self, Create(VGroup(circ[1], c, circ[3])), FadeIn(tex("C", 44, ORG).next_to(c, RIGHT, .3)), t=1.0, rt=.6)
        a1 = Arrow(LEFT * 2.1 + UP * .3, LEFT * 1.6 + UP * .3, buff=0, color=MUTE); a2 = Arrow(RIGHT * 1.7 + UP * .3, RIGHT * 2.2 + UP * .3, buff=0, color=MUTE)
        w2 = ax2.plot(g, x_range=[0, 1, .002], color=GRN, stroke_width=5)
        beat(self, GrowArrow(a1), GrowArrow(a2), Create(w2), t=1.2, rt=1.0)
        lab = kr("고음 삭제", 44, YEL).next_to(ax2, DOWN, .3)
        beat(self, Write(lab), t=.8, rt=.5)
        pulse(self, w2, t=1.4, c=GRN)


class Goal(Scene):
    """같은 회로, 주파수에 따라 출력이 다름 → 그래프."""
    def construct(self):
        ax, g = mag_axes(9, 3.4, DOWN * .6)
        beat(self, FadeIn(g), t=.6, rt=.4)
        k = ValueTracker(-2)
        cur = ax.plot(lp, x_range=[-2, 2, .02], color=YEL, stroke_width=6)
        lo = sine(UP * 2.4 + LEFT * 3, .4, 2, 3, GRN); hi = sine(UP * 2.4 + RIGHT * 3, .06, 12, 3, RED, sw=4)
        beat(self, Create(lo), FadeIn(kr("낮은 주파수", 28, GRN).next_to(lo, DOWN, .15)), t=1.2, rt=.6)
        beat(self, Create(hi), FadeIn(kr("높은 주파수", 28, RED).next_to(hi, DOWN, .3)), t=1.2, rt=.6)
        beat(self, Create(cur), t=1.6, rt=1.4)
        t = kr("주파수 응답", 52, YEL).move_to(ax.c2p(.9, .75))
        beat(self, Write(t), t=1.0, rt=.6)
        pulse(self, t, t=1.4)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "전달함수", BLU), ("2", "저역통과", PUR), ("3", "차단 주파수", GRN), ("4", "보드선도", ORG), ("5", "공진", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.1, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.8, rt=1.0)


# ================= STEP 1 전달함수 =================
class H1(Scene):
    """V_in → [회로] → V_out, H = V_out / V_in."""
    def construct(self):
        self.add(step_tag(1, BLU))
        b = boxio("회로").shift(UP * .6)
        beat(self, FadeIn(b), t=.8, rt=.5)
        i = VGroup(Arrow(LEFT * 4 + UP * .6, LEFT * 1.4 + UP * .6, buff=0, color=BLU), tex(r"V_{in}", 52, BLU).move_to(LEFT * 4.9 + UP * .6))
        beat(self, GrowArrow(i[0]), FadeIn(i[1]), t=1.0, rt=.5)
        o = VGroup(Arrow(RIGHT * 1.4 + UP * .6, RIGHT * 4 + UP * .6, buff=0, color=ORG), tex(r"V_{out}", 52, ORG).move_to(RIGHT * 5.0 + UP * .6))
        beat(self, GrowArrow(o[0]), FadeIn(o[1]), t=1.0, rt=.5)
        H = tex(r"H = \frac{V_{out}}{V_{in}}", 72, YEL).shift(DOWN * 2)
        beat(self, Write(H), t=1.4, rt=.9)
        pulse(self, H, t=1.6)


class H2(Scene):
    """H(jω): ω 를 바꾸면 값이 바뀜."""
    def construct(self):
        self.add(step_tag(1, BLU))
        H = tex(r"H(j\omega)", 96, YEL).shift(UP * 1.6)
        beat(self, Write(H), t=1.2, rt=.8)
        w = tex(r"\omega = 2\pi f", 56, INK).next_to(H, DOWN, .5)
        beat(self, FadeIn(w, shift=UP * .2), t=1.2, rt=.4)
        k = ValueTracker(1)
        wav = always_redraw(lambda: sine(DOWN * 1.9, .55, k.get_value(), 9, BLU))
        self.add(wav); self.wait(.6)
        self.play(k.animate.set_value(8), run_time=2.2, rate_func=smooth)
        self.play(Indicate(H[0][2], color=BLU), run_time=.8)


class H3(Scene):
    """크기 = 몇 배, 각도 = 얼마나 늦게."""
    def construct(self):
        self.add(step_tag(1, BLU))
        ax = Axes(x_range=[0, 2, 1], y_range=[-1.2, 1.2, 1], x_length=10, y_length=3.4, tips=False,
                  axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .4)
        self.add(ax)
        vin = ax.plot(lambda x: np.sin(2 * PI * x), x_range=[0, 2, .01], color=BLU, stroke_width=5)
        beat(self, Create(vin), FadeIn(tex(r"V_{in}", 44, BLU).next_to(ax, LEFT, .15).shift(UP * .9)), t=1.0, rt=.8)
        vo = ax.plot(lambda x: .55 * np.sin(2 * PI * x - PI / 3), x_range=[0, 2, .01], color=ORG, stroke_width=5)
        beat(self, Create(vo), FadeIn(tex(r"V_{out}", 44, ORG).next_to(ax, LEFT, .15).shift(DOWN * .5)), t=1.0, rt=.8)
        m = VGroup(DoubleArrow(ax.c2p(1.25, 0), ax.c2p(1.25, 1), buff=0, color=YEL, tip_length=.18),
                   DoubleArrow(ax.c2p(1.35, 0), ax.c2p(1.35, .55), buff=0, color=YEL, tip_length=.18))
        lm = kr("크기 = 몇 배", 36, YEL).move_to(UP * 2.6 + LEFT * 2.6)
        beat(self, GrowFromCenter(m), FadeIn(lm), t=1.4, rt=.5)
        d = DoubleArrow(ax.c2p(.25, -1.05), ax.c2p(.25 + 1 / 6, -1.05), buff=0, color=GRN, tip_length=.15)
        ld = kr("각도 = 얼마나 늦게", 36, GRN).move_to(UP * 2.6 + RIGHT * 2.6)
        beat(self, GrowFromCenter(d), FadeIn(ld), t=1.4, rt=.5)
        self.play(Indicate(lm, color=YEL, scale_factor=1.0), Indicate(ld, color=GRN, scale_factor=1.0), run_time=1.0)


class H4(Scene):
    """Z_C = 1/(jωC): 주파수 ↑ → 임피던스 ↓."""
    def construct(self):
        self.add(step_tag(1, BLU))
        c = capacitor((-4.6, 1.8), (-4.6, -.6), ORG)[0]
        beat(self, Create(c), t=.8, rt=.6)
        z = tex(r"Z_C = \frac{1}{j\omega C}", 64, ORG).move_to(LEFT * 4.3 + DOWN * 2.1)
        beat(self, Write(z), t=1.2, rt=.8)
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 10, 2], x_length=6.6, y_length=4.4, tips=True,
                  axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False, "tip_length": .2}).shift(RIGHT * 2.4 + DOWN * .2)
        labs = VGroup(tex(r"\omega", 44, MUTE).next_to(ax.x_axis.get_end(), DOWN, .2), tex(r"|Z_C|", 40, MUTE).next_to(ax.y_axis.get_end(), LEFT, .15))
        beat(self, FadeIn(ax), FadeIn(labs), t=.8, rt=.4)
        cur = ax.plot(lambda x: 4 / x, x_range=[.42, 10, .02], color=ORG, stroke_width=6)
        beat(self, Create(cur), t=1.6, rt=1.4)
        k = ValueTracker(.5)
        d = always_redraw(lambda: Dot(ax.c2p(k.get_value(), 4 / k.get_value()), .13, color=YEL))
        self.add(d); self.play(k.animate.set_value(9.5), run_time=1.6)
        self.play(Indicate(z[0][3:], color=YEL), run_time=.8)


class H5(Scene):
    """직류에선 커패시터가?"""
    def construct(self):
        self.add(step_tag(1, BLU))
        b = battery((-3, 0), RED, 1.2)
        c = capacitor((1.5, 1.4), (1.5, -1.4), ORG)[0]
        loop = VGroup(wire((-3, .22), (-3, 1.4)), wire((-3, 1.4), (1.5, 1.4)), wire((-3, -.22), (-3, -1.4)), wire((-3, -1.4), (1.5, -1.4)))
        beat(self, Create(loop), FadeIn(b), t=1.0, rt=.7)
        beat(self, Create(c), FadeIn(kr("직류", 40, RED).next_to(b, LEFT, .4)), FadeIn(tex(r"f = 0", 48, RED).next_to(b, LEFT, .4).shift(DOWN * .8)), t=1.2, rt=.6)
        q = kr("?", 110, YEL).move_to(RIGHT * 3.6)
        beat(self, FadeIn(q, scale=1.4), t=1.2, rt=.4)
        self.play(Indicate(c, color=YEL, scale_factor=1.0), run_time=1.0)
        self.play(Indicate(q, color=YEL), run_time=1.0)


class H6(Scene):
    """낮은 주파수 = 끊긴 선, 높은 주파수 = 이어진 선."""
    def construct(self):
        self.add(step_tag(1, BLU))
        cL = capacitor((-3.6, 1.6), (-3.6, -1.0), ORG)[0]; cR = capacitor((3.6, 1.6), (3.6, -1.0), ORG)[0]
        beat(self, FadeIn(cL), FadeIn(cR), FadeIn(kr("직류", 38, RED).next_to(cL, UP, .3)), FadeIn(kr("높은 주파수", 38, BLU).next_to(cR, UP, .3)), t=1.0, rt=.5)
        zl = tex(r"Z \to \infty", 56, RED).next_to(cL, DOWN, .4)
        beat(self, Write(zl), t=1.0, rt=.6)
        opn = VGroup(wire((-3.6, 1.6), (-3.6, .5), RED, 6), wire((-3.6, .1), (-3.6, -1.0), RED, 6))
        gap = Cross(Square(.35), stroke_color=RED, stroke_width=6).move_to((-3.6, .3, 0))
        lo = kr("끊긴 선", 44, RED).next_to(zl, DOWN, .35)
        beat(self, FadeOut(cL), FadeIn(opn), Create(gap), FadeIn(lo), t=1.4, rt=.7)
        zr = tex(r"Z \to 0", 56, BLU).next_to(cR, DOWN, .4)
        beat(self, Write(zr), t=1.0, rt=.6)
        sh = wire((3.6, 1.6), (3.6, -1.0), BLU, 6); hi = kr("이어진 선", 44, BLU).next_to(zr, DOWN, .35)
        beat(self, FadeOut(cR), Create(sh), FadeIn(hi), t=1.2, rt=.7)
        pulse(self, VGroup(lo, hi), t=1.2)


# ================= STEP 2 저역통과 =================
class L1(Scene):
    """R 뒤에 C, C 양단 출력."""
    def construct(self):
        self.add(step_tag(2, PUR))
        D = rc_circuit(DOWN * .2)
        g = D["g"]
        beat(self, FadeIn(D["src"]), Create(g[1]), Create(g[2]), t=.8, rt=.6)
        beat(self, Create(D["ser"]), FadeIn(tex("R", 48, BLU).next_to(D["ser"], UP, .3)), t=1.0, rt=.6)
        beat(self, Create(D["sh"]), Create(g[5]), Create(g[6]), FadeIn(tex("C", 48, ORG).next_to(D["sh"], LEFT, .5)), t=1.0, rt=.6)
        beat(self, FadeIn(g[7]), FadeIn(g[8]), FadeIn(D["out"]), t=1.0, rt=.5)
        br = SurroundingRectangle(VGroup(D["sh"], D["out"]), color=YEL, buff=.2, corner_radius=.15)
        beat(self, Create(br), FadeIn(kr("C 양단", 36, YEL).next_to(br, UP, .2)), t=1.4, rt=.6)


class L2(Scene):
    """전압 분배 → H = 1/(1+jωRC)."""
    def construct(self):
        self.add(step_tag(2, PUR))
        e1 = tex(r"H = \frac{Z_C}{R + Z_C}", 72).shift(UP * 1.4)
        beat(self, Write(e1), t=1.4, rt=1.0)
        sub = tex(r"Z_C = \frac{1}{j\omega C}", 48, ORG).to_corner(UL, buff=.6).shift(DOWN * .6)
        beat(self, FadeIn(sub, shift=RIGHT * .2), t=1.0, rt=.4)
        e2 = tex(r"H = \frac{1}{1 + j\omega RC}", 84, YEL).shift(DOWN * 1.2)
        beat(self, TransformFromCopy(e1, e2), t=1.6, rt=1.2)
        pulse(self, e2, t=1.6)


def io_waves(sc, f, amp_out, col_in=BLU, col_out=ORG, lab_out=None, t=1.0):
    ax1 = sine(UP * 1.2 + LEFT * 3.3, .7, f, 5.2, col_in); ax2 = sine(UP * 1.2 + RIGHT * 3.3, .7 * amp_out, f, 5.2, col_out)
    l1 = tex(r"V_{in}", 44, col_in).next_to(ax1, UP, .2); l2 = tex(r"V_{out}", 44, col_out).next_to(ax2, UP, .2).set_y(l1.get_y())
    a = Arrow(LEFT * .4 + UP * 1.2, RIGHT * .4 + UP * 1.2, buff=0, color=MUTE)
    return ax1, ax2, l1, l2, a


class L3(Scene):
    """낮은 주파수: C 끊긴 선 → 출력 = 입력."""
    def construct(self):
        self.add(step_tag(2, PUR))
        a1, a2, l1, l2, a = io_waves(self, 1.5, 1.0)
        beat(self, Create(a1), FadeIn(l1), t=1.0, rt=.7)
        c = capacitor((0, -.7), (0, -2.6), ORG)[0]
        x = Cross(Square(.3), stroke_color=RED, stroke_width=6).move_to(c.get_center())
        beat(self, FadeIn(c), Create(x), FadeIn(kr("끊긴 선", 36, RED).next_to(c, RIGHT, .4)), t=1.2, rt=.6)
        beat(self, GrowArrow(a), Create(a2), FadeIn(l2), t=1.2, rt=.9)
        eq = tex(r"V_{out} = V_{in}", 56, GRN).move_to(DOWN * 3.2 + LEFT * 3.5)
        beat(self, Write(eq), t=1.0, rt=.6)
        pulse(self, a2, t=1.2, c=GRN)


class L4(Scene):
    """높은 주파수: C 이어진 선 → 출력 0."""
    def construct(self):
        self.add(step_tag(2, PUR))
        a1, a2, l1, l2, a = io_waves(self, 8, .08)
        beat(self, Create(a1), FadeIn(l1), t=1.0, rt=.7)
        c = wire((0, -.7), (0, -2.6), BLU, 7)
        beat(self, Create(c), FadeIn(kr("이어진 선", 36, BLU).next_to(c, RIGHT, .4)), t=1.2, rt=.6)
        sh = VGroup(*[Arrow((-.6, -.8 - .5 * k, 0), (-.05, -1.1 - .5 * k, 0), buff=0, color=YEL, stroke_width=4, tip_length=.15) for k in range(3)])
        beat(self, LaggedStart(*[GrowArrow(s) for s in sh], lag_ratio=.2), t=1.0, rt=.6)
        beat(self, GrowArrow(a), Create(a2), FadeIn(l2), t=1.2, rt=.9)
        eq = tex(r"V_{out} \to 0", 56, RED).move_to(DOWN * 3.2 + RIGHT * 3.5)
        beat(self, Write(eq), t=1.0, rt=.6)
        self.play(Indicate(eq, color=RED, scale_factor=1.0), run_time=.8)


class L5(Scene):
    """|H| 곡선: 통과 / 차단 → 저역통과."""
    def construct(self):
        self.add(step_tag(2, PUR))
        ax, g = mag_axes()
        beat(self, FadeIn(g), t=.6, rt=.4)
        cur = ax.plot(lp, x_range=[-2, 2, .02], color=YEL, stroke_width=6)
        beat(self, Create(cur), t=1.6, rt=1.4)
        p = Rectangle(width=ax.c2p(-.3, 0)[0] - ax.c2p(-2, 0)[0], height=3.8, color=GRN, fill_color=GRN, fill_opacity=.12, stroke_width=0).move_to(ax.c2p(-1.15, .55))
        beat(self, FadeIn(p), FadeIn(kr("통과", 44, GRN).move_to(ax.c2p(-1.15, .45))), t=1.0, rt=.5)
        s = Rectangle(width=ax.c2p(2, 0)[0] - ax.c2p(.5, 0)[0], height=3.8, color=RED, fill_color=RED, fill_opacity=.12, stroke_width=0).move_to(ax.c2p(1.25, .55))
        beat(self, FadeIn(s), FadeIn(kr("차단", 44, RED).move_to(ax.c2p(1.25, .6))), t=1.0, rt=.5)
        t = card(kr("저역통과 필터", 48, YEL), YEL, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(t, shift=DOWN * .2), t=1.0, rt=.5)
        pulse(self, t, t=1.2)


class L6(Scene):
    """R·C 자리 바꾸면 고역통과."""
    def construct(self):
        self.add(step_tag(2, PUR))
        D = rc_circuit(LEFT * 3.6 + UP * .9, hp=True, W=4.6, H=2.0)
        beat(self, FadeIn(D["g"]), FadeIn(D["out"]), t=1.0, rt=.6)
        beat(self, FadeIn(tex("C", 44, ORG).next_to(D["ser"], UP, .45)), FadeIn(tex("R", 44, BLU).next_to(D["sh"], LEFT, .4)), t=1.0, rt=.4)
        sw = kr("자리 바꿈", 34, YEL).next_to(D["g"], DOWN, .35)
        beat(self, FadeIn(sw), t=.8, rt=.4)
        ax, g = mag_axes(5.2, 3.2, RIGHT * 3.9 + DOWN * .4)
        beat(self, FadeIn(g), t=.6, rt=.4)
        c1 = ax.plot(lp, x_range=[-2, 2, .02], color=MUTE, stroke_width=4, stroke_opacity=.5)
        c2 = ax.plot(hp_, x_range=[-2, 2, .02], color=YEL, stroke_width=6)
        beat(self, FadeIn(c1), Create(c2), t=1.4, rt=1.2)
        t = card(kr("고역통과 필터", 44, YEL), YEL, .2).next_to(ax, UP, .3)
        beat(self, FadeIn(t, shift=DOWN * .2), t=1.0, rt=.5)


# ================= STEP 3 차단 주파수 =================
class X1(Scene):
    """경계는 어디?"""
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g = mag_axes(); cur = ax.plot(lp, x_range=[-2, 2, .02], color=YEL, stroke_width=6)
        self.add(g, cur)
        p = kr("통과", 40, GRN).move_to(ax.c2p(-1.3, .5)); s = kr("차단", 40, RED).move_to(ax.c2p(1.3, .5))
        beat(self, FadeIn(p), FadeIn(s), t=1.0, rt=.5)
        k = ValueTracker(-1.5)
        ln = always_redraw(lambda: DashedLine(ax.c2p(k.get_value(), 0), ax.c2p(k.get_value(), 1.12), color=INK, stroke_width=3))
        self.add(ln); self.play(k.animate.set_value(1.2), run_time=1.6); self.play(k.animate.set_value(0), run_time=1.0)
        q = kr("경계?", 48, YEL).next_to(ax.c2p(0, 1.0), RIGHT, .4)
        beat(self, FadeIn(q, scale=1.4), t=1.0, rt=.4)
        self.play(Indicate(q, color=YEL), run_time=.8)


class X2(Scene):
    """ωRC = 1 → ω_c = 1/RC."""
    def construct(self):
        self.add(step_tag(3, GRN))
        H = tex(r"H = \frac{1}{1 + j\omega RC}", 72).shift(UP * 1.8)
        beat(self, Write(H), t=1.0, rt=.8)
        box = SurroundingRectangle(H[0][-3:], color=YEL, buff=.1)
        beat(self, Create(box), t=.8, rt=.4)
        e = tex(r"\omega RC = 1", 72, YEL).shift(DOWN * .2)
        beat(self, TransformFromCopy(H[0][-3:], e), t=1.2, rt=.8)
        r = tex(r"\omega_c = \frac{1}{RC}", 84, GRN).shift(DOWN * 2.2)
        beat(self, Write(r), t=1.2, rt=.8)
        pulse(self, r, t=1.4, c=GRN)


class X3(Scene):
    """ω_c 에서 |H| = 1/√2 ≈ 0.707."""
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g = mag_axes(); cur = ax.plot(lp, x_range=[-2, 2, .02], color=YEL, stroke_width=6)
        self.add(g, cur)
        v = DashedLine(ax.c2p(0, 0), ax.c2p(0, lp(0)), color=GRN, stroke_width=4)
        beat(self, Create(v), FadeIn(tex(r"\omega_c", 44, GRN).next_to(ax.c2p(0, 0), DOWN, .2)), t=1.0, rt=.6)
        h = DashedLine(ax.c2p(-2, lp(0)), ax.c2p(0, lp(0)), color=GRN, stroke_width=4)
        d = Dot(ax.c2p(0, lp(0)), .14, color=GRN)
        beat(self, Create(h), FadeIn(d, scale=2), t=1.0, rt=.6)
        e = tex(r"\frac{1}{\sqrt{2}} \approx 0.707", 60, GRN).move_to(ax.c2p(1.05, .95))
        beat(self, Write(e), t=1.4, rt=.8)
        pulse(self, VGroup(d, e), t=1.6, c=GRN)


class X4(Scene):
    """전력 = 전압² → 절반."""
    def construct(self):
        self.add(step_tag(3, GRN))
        e = tex(r"P \propto V^2", 64, INK).shift(UP * 2.4)
        beat(self, Write(e), t=1.0, rt=.6)
        base = DOWN * 2.2
        b1 = Rectangle(width=1.6, height=3.4, color=BLU, fill_color=BLU, fill_opacity=.8, stroke_width=0).move_to(base + LEFT * 2.5, aligned_edge=DOWN)
        b2 = Rectangle(width=1.6, height=1.7, color=GRN, fill_color=GRN, fill_opacity=.8, stroke_width=0).move_to(base + RIGHT * 2.5, aligned_edge=DOWN)
        beat(self, GrowFromEdge(b1, DOWN), FadeIn(kr("입력 전력", 32, BLU).next_to(b1, DOWN, .2)), t=1.0, rt=.6)
        c = tex(r"(0.707)^2 = 0.5", 56, GRN).move_to(RIGHT * 2.5 + UP * 1.2)
        beat(self, Write(c), t=1.2, rt=.8)
        beat(self, GrowFromEdge(b2, DOWN), FadeIn(kr("차단 주파수", 32, GRN).next_to(b2, DOWN, .2)), t=1.0, rt=.6)
        h = kr("절반", 52, YEL).next_to(b2, UP, .25)
        beat(self, FadeIn(h, scale=1.3), t=.6, rt=.4)
        pulse(self, h, t=1.2)


class X5(Scene):
    """R=1.6kΩ, C=0.1μF → f_c = ?"""
    def construct(self):
        self.add(step_tag(3, GRN))
        D = rc_circuit(UP * .5, W=6.0, H=2.4)
        beat(self, FadeIn(D["g"]), FadeIn(D["out"]), t=.8, rt=.5)
        r = tex(r"1.6\,\mathrm{k\Omega}", 50, BLU).next_to(D["ser"], UP, .35)
        beat(self, Write(r), t=1.2, rt=.6)
        c = tex(r"0.1\,\mu\mathrm{F}", 50, ORG).next_to(D["sh"], LEFT, .45)
        beat(self, Write(c), t=1.2, rt=.6)
        q = VGroup(tex(r"f_c =", 64, GRN), kr("? Hz", 60, YEL)).arrange(RIGHT, buff=.25).to_edge(DOWN, buff=.6)
        beat(self, FadeIn(q, scale=1.3), t=1.2, rt=.5)
        self.play(Indicate(q[1], color=YEL), run_time=1.0)


class X6(Scene):
    """f_c = 1/(2πRC) ≈ 1kHz, 그 위는 줄어듦."""
    def construct(self):
        self.add(step_tag(3, GRN))
        e = tex(r"f_c = \frac{1}{2\pi RC}", 60, INK).to_edge(UP, buff=.5).shift(LEFT * 3)
        beat(self, Write(e), t=1.0, rt=.7)
        r = tex(r"\approx 1\,\mathrm{kHz}", 64, GRN).next_to(e, RIGHT, .4)
        beat(self, Write(r), t=1.0, rt=.6)
        ax, _ = mag_axes(10, 3.6, DOWN * .9, xlab=False)
        cur = ax.plot(lp, x_range=[-2, 2, .02], color=YEL, stroke_width=6)
        labs = dec_labels(ax, 0, ("10", "100", "1k", "10k", "100k")); hz = kr("Hz", 26, MUTE).next_to(labs, RIGHT, .2)
        beat(self, FadeIn(ax), FadeIn(labs), FadeIn(hz), Create(cur), t=1.4, rt=1.2)
        d = Dot(ax.c2p(0, lp(0)), .14, color=GRN)
        beat(self, FadeIn(d, scale=2), t=.6, rt=.4)
        k = ValueTracker(0)
        m = always_redraw(lambda: Dot(ax.c2p(k.get_value(), lp(k.get_value())), .12, color=RED))
        hi = kr("고음 ↓", 40, RED).move_to(ax.c2p(1.4, .7))
        self.add(m); self.play(k.animate.set_value(2), FadeIn(hi), run_time=1.6)


# ================= STEP 4 데시벨·보드선도 =================
class B1(Scene):
    """dB = 20 log|H|."""
    def construct(self):
        self.add(step_tag(4, ORG))
        e = tex(r"\mathrm{dB} = 20 \log_{10} |H|", 80, ORG).shift(UP * .8)
        beat(self, Write(e), t=1.6, rt=1.2)
        ex = VGroup(tex(r"|H| = 1", 52), tex(r"\rightarrow", 52, MUTE), tex(r"0\,\mathrm{dB}", 56, YEL)).arrange(RIGHT, buff=.4).shift(DOWN * 1.6)
        beat(self, FadeIn(ex[0]), t=.8, rt=.4)
        beat(self, FadeIn(ex[1]), FadeIn(ex[2], shift=LEFT * .2), t=1.2, rt=.5)
        pulse(self, e, t=1.4, c=ORG)


class B2(Scene):
    """0.707 → −3dB, 0.1 → −20dB."""
    def construct(self):
        self.add(step_tag(4, ORG))
        rows = VGroup(*[VGroup(tex(a, 60), tex(r"\rightarrow", 56, MUTE), tex(b, 64, c)).arrange(RIGHT, buff=.5)
                        for a, b, c in ((r"0.707", r"-3\,\mathrm{dB}", GRN), (r"0.1", r"-20\,\mathrm{dB}", ORG), (r"0.01", r"-40\,\mathrm{dB}", RED))]).arrange(DOWN, buff=.7, aligned_edge=LEFT)
        rows.move_to(ORIGIN)
        for r in rows:
            beat(self, FadeIn(r[0]), t=.6, rt=.3)
            beat(self, FadeIn(r[1]), FadeIn(r[2], shift=LEFT * .2), t=1.0, rt=.5)
        pulse(self, rows[0][2], t=1.2, c=GRN)


def bode_lp(ax):
    return ax.plot(lambda x: db(lp(x)), x_range=[-2, 2, .02], color=YEL, stroke_width=6)


class B3(Scene):
    """로그 가로축 → 보드선도."""
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = bode_axes()
        beat(self, FadeIn(g[1]), t=.6, rt=.4)
        labs = dec_labels(ax, -45)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * .2) for l in labs], lag_ratio=.25), run_time=1.2)
        x10 = VGroup(*[kr("×10", 26, ORG).move_to((ax.c2p(k + .5, -45)[0], ax.c2p(0, -45)[1] - .75, 0)) for k in range(-2, 2)])
        beat(self, FadeIn(x10), t=.8, rt=.4)
        beat(self, FadeIn(g[0]), FadeIn(g[2]), FadeIn(g[3]), t=.6, rt=.4)
        cur = bode_lp(ax)
        beat(self, Create(cur), t=1.6, rt=1.4)
        t = card(kr("보드선도", 48, ORG), ORG, .2).move_to(ax.c2p(-1, -28))
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.5)


class B4(Scene):
    """차단 주파수 아래: 0dB 평평."""
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = bode_axes(); self.add(g, dec_labels(ax, -45))
        cur = bode_lp(ax); self.add(cur)
        v = DashedLine(ax.c2p(0, -45), ax.c2p(0, 6), color=GRN, stroke_width=4)
        beat(self, Create(v), FadeIn(tex(r"f_c", 44, GRN).next_to(ax.c2p(0, 6), UP, .1)), t=1.0, rt=.6)
        a1 = Line(ax.c2p(-2, 0), ax.c2p(0, 0), color=BLU, stroke_width=9)
        beat(self, Create(a1), t=1.2, rt=1.0)
        l = kr("0 dB 평평", 44, BLU).move_to(ax.c2p(-1, -12))
        beat(self, FadeIn(l, shift=UP * .2), t=1.0, rt=.5)
        pulse(self, a1, t=1.4, c=BLU)


class B5(Scene):
    """그 위: 10배마다 −20dB 직선."""
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = bode_axes(); self.add(g, dec_labels(ax, -45))
        cur = bode_lp(ax); self.add(cur, Line(ax.c2p(-2, 0), ax.c2p(0, 0), color=BLU, stroke_width=9))
        a2 = Line(ax.c2p(0, 0), ax.c2p(2, -40), color=RED, stroke_width=9)
        beat(self, Create(a2), t=1.2, rt=1.0)
        for k in (0, 1):
            st = VGroup(DashedLine(ax.c2p(k, -20 * k), ax.c2p(k + 1, -20 * k), color=INK, stroke_width=3),
                        DashedLine(ax.c2p(k + 1, -20 * k), ax.c2p(k + 1, -20 * (k + 1)), color=INK, stroke_width=3))
            lab = VGroup(kr("×10", 26, INK).next_to(st[0], UP, .1), tex(r"-20", 34, RED).next_to(st[1], RIGHT, .1))
            beat(self, Create(st), FadeIn(lab), t=1.2, rt=.6)
        t = card(tex(r"-20\,\mathrm{dB/dec}", 52, RED), RED, .2).move_to(ax.c2p(-1, -30))
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.5)


def sum_rows(items):
    g = VGroup(*[VGroup(kr(a, 34, MUTE), b).arrange(RIGHT, buff=.5) for a, b in items]).arrange(DOWN, buff=.55, aligned_edge=LEFT)
    return g.shift(DOWN * .2)


class Sum1(Scene):
    """중간 정리 (STEP 1~4)."""
    def construct(self):
        self.add(head("여기까지 정리", YEL))
        rows = sum_rows([("경계", tex(r"\omega_c = \frac{1}{RC}", 52, GRN)),
                         ("거기서", tex(r"-3\,\mathrm{dB}", 52, ORG)),
                         ("그 위로", tex(r"\times 10 \;\rightarrow\; -20\,\mathrm{dB}", 52, RED))])
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.5, rt=.5)
        pulse(self, rows, t=1.8)


# ================= STEP 5 공진 =================
class R1(Scene):
    """R, L, C 직렬."""
    def construct(self):
        self.add(step_tag(5, RED))
        g, R, L, C, labs = rlc_circuit(DOWN * .2)
        beat(self, FadeIn(g[0]), Create(g[1]), Create(g[2]), Create(g[6]), Create(g[7]), t=1.0, rt=.6)
        beat(self, Create(R), FadeIn(labs[0]), t=1.0, rt=.5)
        beat(self, Create(L), FadeIn(labs[1]), t=1.0, rt=.5)
        beat(self, Create(C), FadeIn(labs[2]), t=1.0, rt=.5)
        t = kr("직렬", 44, YEL).to_edge(DOWN, buff=.6)
        beat(self, FadeIn(t), t=.8, rt=.4)


def x_axes(o=DOWN * .2):
    ax = Axes(x_range=[0, 4, 1], y_range=[0, 4, 1], x_length=8, y_length=4.6, tips=True,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False, "tip_length": .2}).move_to(o)
    lab = VGroup(tex(r"\omega", 44, MUTE).next_to(ax.x_axis.get_end(), DOWN, .2), kr("임피던스", 28, MUTE).next_to(ax.y_axis.get_end(), LEFT, .2))
    return ax, VGroup(ax, lab)


class R2(Scene):
    """X_L = ωL ↑, X_C = 1/ωC ↓."""
    def construct(self):
        self.add(step_tag(5, RED))
        ax, g = x_axes()
        beat(self, FadeIn(g), t=.6, rt=.4)
        xl = ax.plot(lambda x: x, x_range=[0, 3.9], color=GRN, stroke_width=6)
        beat(self, Create(xl), FadeIn(tex(r"X_L = \omega L", 48, GRN).move_to(ax.c2p(2.3, 3.7))), t=1.6, rt=1.0)
        xc = ax.plot(lambda x: 1 / x, x_range=[.26, 3.9], color=ORG, stroke_width=6)
        beat(self, Create(xc), FadeIn(tex(r"X_C = \frac{1}{\omega C}", 48, ORG).move_to(ax.c2p(1.15, 3.1))), t=1.6, rt=1.0)
        self.play(Indicate(xl, color=GRN, scale_factor=1.0), Indicate(xc, color=ORG, scale_factor=1.0), run_time=1.2)


class R3(Scene):
    """같아지는 점 → 상쇄 → R만."""
    def construct(self):
        self.add(step_tag(5, RED))
        ax, g = x_axes(LEFT * 2.6 + DOWN * .2)
        g.scale(.8, about_point=ax.c2p(0, 0))
        xl = ax.plot(lambda x: x, x_range=[0, 3.9], color=GRN, stroke_width=6)
        xc = ax.plot(lambda x: 1 / x, x_range=[.26, 3.9], color=ORG, stroke_width=6)
        self.add(g, xl, xc)
        d = Dot(ax.c2p(1, 1), .16, color=YEL)
        beat(self, FadeIn(d, scale=2), FadeIn(tex(r"X_L = X_C", 44, YEL).next_to(ax.c2p(1, 1), UR, .2)), t=1.2, rt=.6)
        v = DashedLine(ax.c2p(1, 0), ax.c2p(1, 1), color=YEL, stroke_width=4)
        beat(self, Create(v), FadeIn(tex(r"\omega_0", 44, YEL).next_to(ax.c2p(1, 0), DOWN, .2)), t=1.0, rt=.5)
        z = tex(r"Z = R + j\omega L + \frac{1}{j\omega C}", 46, INK).move_to(RIGHT * 3.6 + UP * 1.3)
        beat(self, Write(z), t=1.2, rt=.8)
        r = tex(r"Z = R", 72, BLU).move_to(RIGHT * 3.6 + DOWN * .8)
        beat(self, TransformFromCopy(z[0][:3], r), t=1.2, rt=.8)
        pulse(self, r, t=1.2, c=BLU)


class R4(Scene):
    """공진: ω0 = 1/√LC."""
    def construct(self):
        self.add(step_tag(5, RED))
        e1 = tex(r"\omega_0 L = \frac{1}{\omega_0 C}", 72).shift(UP * 1.4)
        beat(self, Write(e1), t=1.4, rt=1.0)
        t = kr("공진", 64, YEL).to_edge(UP, buff=.4)
        beat(self, FadeIn(t, scale=1.3), t=.8, rt=.4)
        e2 = tex(r"\omega_0 = \frac{1}{\sqrt{LC}}", 90, RED).shift(DOWN * 1.4)
        beat(self, TransformFromCopy(e1, e2), t=1.6, rt=1.2)
        pulse(self, e2, t=1.6, c=RED)


class R5(Scene):
    """R 에서 출력 → 대역통과."""
    def construct(self):
        self.add(step_tag(5, RED))
        ax, g = mag_axes()
        beat(self, FadeIn(g), t=.6, rt=.4)
        cur = ax.plot(bp, x_range=[-2, 2, .01], color=YEL, stroke_width=6)
        beat(self, Create(cur), t=1.6, rt=1.4)
        v = DashedLine(ax.c2p(0, 0), ax.c2p(0, 1), color=RED, stroke_width=4)
        beat(self, Create(v), FadeIn(tex(r"\omega_0", 44, RED).next_to(ax.c2p(0, 0), DOWN, .2)), t=1.0, rt=.5)
        band = Rectangle(width=ax.c2p(.17, 0)[0] - ax.c2p(-.17, 0)[0], height=3.8, color=GRN, fill_color=GRN, fill_opacity=.18, stroke_width=0).move_to(ax.c2p(0, .55))
        beat(self, FadeIn(band), t=.8, rt=.4)
        t = card(kr("대역통과 필터", 48, YEL), YEL, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(t, shift=DOWN * .2), t=1.0, rt=.5)
        pulse(self, t, t=1.2)


def radio(o=ORIGIN, s=1.0):
    o = P3(o)
    body = RoundedRectangle(width=3.4 * s, height=2.0 * s, corner_radius=.2, color=INK, stroke_width=5).move_to(o)
    spk = VGroup(*[Circle(.12 * s, color=MUTE, stroke_width=3).move_to(o + np.array([(-1.1 + .35 * (i % 3)) * s, (.35 - .35 * (i // 3)) * s, 0])) for i in range(9)])
    dial = Circle(.45 * s, color=YEL, stroke_width=5).move_to(o + RIGHT * .9 * s)
    ant = Line(body.get_corner(UR) + LEFT * .4 * s, body.get_corner(UR) + LEFT * .4 * s + UP * 1.2 * s + LEFT * .5 * s, color=INK, stroke_width=4)
    return VGroup(body, spk, dial, ant), dial


class R6(Scene):
    """다이얼 → C 바뀜 → 공진 봉우리가 방송으로 이동."""
    def construct(self):
        self.add(step_tag(5, RED))
        ax, g = mag_axes(9, 3.2, DOWN * 1.3, xlab=False)
        st = [-1.2, -.3, .7]; names = ["FM 89.1", "FM 95.9", "FM 107.7"]
        stations = VGroup(*[VGroup(Line(ax.c2p(x, 0), ax.c2p(x, .35), color=PUR, stroke_width=8), kr(n, 24, PUR).next_to(ax.c2p(x, 0), DOWN, .15)) for x, n in zip(st, names)])
        beat(self, FadeIn(ax), FadeIn(stations), t=1.0, rt=.6)
        R, dial = radio(UP * 2.0 + LEFT * 3.6, .8)
        beat(self, FadeIn(R), t=.6, rt=.4)
        k = ValueTracker(-1.2)
        cur = always_redraw(lambda: ax.plot(lambda x: bp(x - k.get_value(), 5.0), x_range=[-2, 2, .01], color=YEL, stroke_width=6))
        mark = always_redraw(lambda: Line(dial.get_center(), dial.get_center() + .36 * np.array([np.cos(PI / 2 - (k.get_value() + 1.2) * 1.4), np.sin(PI / 2 - (k.get_value() + 1.2) * 1.4), 0]), color=YEL, stroke_width=5))
        cl = tex(r"C \;\downarrow \;\Rightarrow\; \omega_0 \uparrow", 48, ORG).move_to(UP * 2.0 + RIGHT * 2.6)
        self.add(mark); self.play(Create(cur), run_time=.8)
        beat(self, FadeIn(cl), t=.6, rt=.4)
        self.play(k.animate.set_value(-.3), run_time=1.2); self.wait(.3)
        self.play(k.animate.set_value(.7), run_time=1.2)
        self.play(stations[2][0].animate.set_color(YEL), stations[2][1].animate.set_color(YEL), run_time=.6)
        self.wait(.4)


# ================= 정리 =================
def final_rows():
    return sum_rows([("커패시터", VGroup(kr("직류 = 끊긴 선", 36, RED), kr("·", 36, MUTE), kr("고주파 = 이어진 선", 36, BLU)).arrange(RIGHT, buff=.2)),
                     ("RC 필터", VGroup(tex(r"\omega_c = \frac{1}{RC}", 48, GRN), tex(r"-3\,\mathrm{dB}", 48, ORG), tex(r"-20\,\mathrm{dB/dec}", 48, RED)).arrange(RIGHT, buff=.45)),
                     ("RLC", VGroup(tex(r"\omega_0 = \frac{1}{\sqrt{LC}}", 48, RED), kr("→ 한 대역만", 36, YEL)).arrange(RIGHT, buff=.3))])


class F1(Scene):
    def construct(self):
        self.add(head("정리", YEL)); rows = final_rows()
        self.add(rows[0][0])
        for m in rows[0][1]:
            beat(self, FadeIn(m, shift=RIGHT * .3), t=1.2, rt=.4)
        pulse(self, rows[0], t=1.6, c=BLU)


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
        pulse(self, rows[2], t=2.8, c=RED)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("주파수 응답과 필터", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        beat(self, FadeIn(t[0]), t=.8, rt=.3)
        for m in t[1]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.4, rt=.4)
        pulse(self, t, t=2.0)


class Next(Scene):
    def construct(self):
        items = ["3상", "변압기", "주파수 응답", "2포트 회로"]
        cards = VGroup(*[card(kr(s, 36, YEL if s == "주파수 응답" else MUTE), YEL if s == "주파수 응답" else "#2a2e37", .3) for s in items]).arrange(RIGHT, buff=.35)
        cards.scale_to_fit_width(min(cards.width, 12.5))
        lab = kr("재생목록 · 회로이론 한눈에", 40, INK).next_to(cards, UP, .6)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cards], lag_ratio=.3), run_time=1.6)
        arr = Arrow(cards[2].get_bottom() + DOWN * .2, cards[3].get_bottom() + DOWN * .2, buff=0, color=YEL, path_arc=PI / 2)
        beat(self, Create(arr), t=1.6, rt=.8)


# ================= 쇼츠 전용 =================
class AQ(Scene):
    """R 하나 C 하나로 고음 지우기? (질문)"""
    def construct(self):
        f = lambda x: .55 * np.sin(2 * PI * x * 1.5) + .22 * np.sin(2 * PI * x * 14)
        ax = Axes(x_range=[0, 1, 1], y_range=[-1, 1, 1], x_length=9, y_length=2.4, tips=False, axis_config={"stroke_opacity": 0}).shift(UP * 1.4)
        w = ax.plot(f, x_range=[0, 1, .002], color=PUR, stroke_width=5)
        beat(self, Create(w), t=1.2, rt=1.0)
        r = resistor((-3.2, -1.6), (-.8, -1.6), BLU); c = capacitor((1.6, -.6), (1.6, -2.6), ORG)[0]
        beat(self, Create(r), FadeIn(tex("R", 52, BLU).next_to(r, UP, .25)), t=.9, rt=.5)
        beat(self, Create(c), FadeIn(tex("C", 52, ORG).next_to(c, RIGHT, .3)), t=.9, rt=.5)
        q = kr("고음만 삭제?", 52, YEL).to_edge(DOWN, buff=.3)
        beat(self, FadeIn(q, scale=1.3), t=.8, rt=.4)
        g = ax.plot(lambda x: .55 * np.sin(2 * PI * x * 1.5), x_range=[0, 1, .002], color=GRN, stroke_width=6)
        self.play(Transform(w, g), run_time=1.2)
        self.wait(.4)


class AFlow(Scene):
    """고음은 C 로 빠지고 저음만 출력."""
    def construct(self):
        D = rc_circuit(DOWN * .4, W=6.4, H=3.0, src=False)
        self.add(D["g"], D["out"], tex("R", 44, BLU).next_to(D["ser"], UP, .3), tex("C", 44, ORG).next_to(D["sh"], LEFT, .5))
        x0, xm, yt, yb = D["x0"], D["xm"], D["yt"], D["yb"]
        hi = sine((x0 - .2, yt + 1.1, 0), .12, 6, 2.2, RED, sw=4); lo = sine((x0 - .2, yt + 1.1, 0), .35, 1, 2.2, GRN)
        beat(self, Create(hi), Create(lo), t=1.0, rt=.6)
        down = Arrow((xm + .5, yt - .2, 0), (xm + .5, yb + .2, 0), buff=0, color=RED, stroke_width=6)
        beat(self, hi.animate.move_to((xm - 2.2, yb + .6, 0)).scale(.45), GrowArrow(down), t=1.4, rt=1.0)
        beat(self, FadeIn(kr("고음 → C로 빠짐", 34, RED).next_to(down, RIGHT, .2).shift(DOWN * .6)), t=.8, rt=.4)
        beat(self, lo.animate.move_to((D["x1"] + 1.4, yt + .9, 0)), t=1.2, rt=1.0)
        beat(self, FadeIn(kr("저음만 남음", 36, GRN).next_to(lo, UP, .2)), t=1.0, rt=.4)


class ATone(Scene):
    """톤 조절: 차단 주파수를 움직이는 노브."""
    def construct(self):
        ax, g = mag_axes(9, 3.2, DOWN * .9)
        beat(self, FadeIn(g), t=.5, rt=.4)
        k = ValueTracker(0)
        cur = always_redraw(lambda: ax.plot(lambda x: lp(x - k.get_value()), x_range=[-2, 2, .02], color=YEL, stroke_width=6))
        knob = Circle(.6, color=INK, stroke_width=5).move_to(UP * 2.3 + LEFT * 3)
        mk = always_redraw(lambda: Line(knob.get_center(), knob.get_center() + .5 * np.array([np.cos(PI / 2 - k.get_value()), np.sin(PI / 2 - k.get_value()), 0]), color=YEL, stroke_width=6))
        lab = kr("톤 조절", 44, YEL).next_to(knob, RIGHT, .5)
        self.play(Create(cur), FadeIn(knob), FadeIn(mk), FadeIn(lab), run_time=1.0)
        self.play(k.animate.set_value(-1), run_time=1.3); self.play(k.animate.set_value(1), run_time=1.6); self.play(k.animate.set_value(0), run_time=1.0)
        self.wait(.4)


class BQ(Scene):
    """커패시터: 끊긴 선? 이어진 선?"""
    def construct(self):
        c = capacitor((0, 2.0), (0, -1.2), ORG, w=1.6, gap=.4)[0]
        beat(self, Create(c), t=1.0, rt=.8)
        a = kr("끊긴 선?", 52, RED).move_to(LEFT * 3.6 + UP * .4); b = kr("이어진 선?", 52, BLU).move_to(RIGHT * 3.6 + UP * .4)
        beat(self, FadeIn(a, shift=RIGHT * .3), t=1.0, rt=.4)
        beat(self, FadeIn(b, shift=LEFT * .3), t=1.0, rt=.4)
        q = kr("?", 96, YEL).to_edge(DOWN, buff=.4)
        beat(self, FadeIn(q, scale=1.4), t=.8, rt=.4)
        self.play(Indicate(a, color=RED, scale_factor=1.0), Indicate(b, color=BLU, scale_factor=1.0), run_time=1.0)


class BCoup(Scene):
    """직류 + 신호 → C → 신호만."""
    def construct(self):
        p1 = LEFT * 3.6 + UP * .2; p2 = RIGHT * 3.6 + UP * .2
        inp = VGroup(DashedLine(p1 + LEFT * 1.5 + DOWN * .0, p1 + RIGHT * 1.5, color=MUTE, stroke_width=2), sine(p1 + UP * 1.0, .4, 3, 3, BLU))
        beat(self, Create(inp), FadeIn(kr("직류 + 신호", 34, BLU).next_to(inp, DOWN, .8)), t=1.2, rt=.8)
        c = capacitor((-1.2, .2), (1.2, .2), ORG)[0]
        beat(self, Create(c), FadeIn(tex("C", 48, ORG).next_to(c, UP, .45)), t=1.0, rt=.5)
        out = VGroup(DashedLine(p2 + LEFT * 1.5, p2 + RIGHT * 1.5, color=MUTE, stroke_width=2), sine(p2, .4, 3, 3, GRN))
        beat(self, TransformFromCopy(inp[1], out[1]), FadeIn(out[0]), t=1.2, rt=.9)
        beat(self, FadeIn(kr("신호만", 40, GRN).next_to(out, DOWN, .8)), t=.8, rt=.4)
        pulse(self, out[1], t=1.2, c=GRN)


class CQ(Scene):
    """왜 하필 −3dB?"""
    def construct(self):
        ax, g = bode_axes(o=DOWN * .6); self.add(g)
        cur = bode_lp(ax)
        beat(self, Create(cur), t=1.2, rt=1.0)
        d = Dot(ax.c2p(0, -3), .15, color=GRN)
        beat(self, FadeIn(d, scale=2), t=.6, rt=.4)
        l = tex(r"-3\,\mathrm{dB}", 72, GRN).move_to(ax.c2p(1.0, -8))
        beat(self, Write(l), t=1.0, rt=.6)
        q = kr("왜 하필?", 60, YEL).to_edge(UP, buff=.3)
        beat(self, FadeIn(q, scale=1.3), t=1.0, rt=.4)
        self.play(Indicate(l, color=GRN, scale_factor=1.0), run_time=1.0)


class CHalf(Scene):
    """−3dB = 전력 절반 경계."""
    def construct(self):
        ax, g = mag_axes(9, 3.4, DOWN * .6, xlab=False)
        c2 = ax.plot(lambda x: lp(x) ** 2, x_range=[-2, 2, .02], color=ORG, stroke_width=6)
        self.add(g)
        beat(self, Create(c2), FadeIn(kr("전력", 36, ORG).move_to(ax.c2p(-1.5, 1.1))), t=1.2, rt=1.0)
        h = DashedLine(ax.c2p(-2, .5), ax.c2p(2, .5), color=GRN, stroke_width=4)
        beat(self, Create(h), FadeIn(kr("절반", 36, GRN).next_to(ax.c2p(2, .5), UP, .1)), t=1.0, rt=.6)
        d = Dot(ax.c2p(0, .5), .15, color=YEL)
        beat(self, FadeIn(d, scale=2), FadeIn(tex(r"-3\,\mathrm{dB}", 56, YEL).next_to(ax.c2p(0, .5), UR, .25)), t=1.0, rt=.5)
        pulse(self, d, t=1.2)


class DQ(Scene):
    """보드선도 = 직선 두 개?"""
    def construct(self):
        ax, g = bode_axes(o=DOWN * .6); self.add(g, dec_labels(ax, -45))
        cur = bode_lp(ax)
        beat(self, Create(cur), t=1.2, rt=1.0)
        a1 = Line(ax.c2p(-2, 0), ax.c2p(0, 0), color=BLU, stroke_width=9); a2 = Line(ax.c2p(0, 0), ax.c2p(2, -40), color=RED, stroke_width=9)
        beat(self, Create(a1), t=.9, rt=.6)
        beat(self, Create(a2), t=.9, rt=.6)
        q = kr("직선 두 개면 끝", 56, YEL).to_edge(UP, buff=.3)
        beat(self, FadeIn(q, scale=1.3), t=1.0, rt=.4)
        self.play(Indicate(a1, color=BLU, scale_factor=1.0), Indicate(a2, color=RED, scale_factor=1.0), run_time=1.0)


class DInv(Scene):
    """주파수 ×10 → 출력 1/10 → −20dB."""
    def construct(self):
        e = tex(r"|H| \approx \frac{\omega_c}{\omega}", 76, INK).shift(UP * 1.8)
        beat(self, Write(e), t=1.2, rt=.9)
        r = VGroup(tex(r"\omega \times 10", 60, ORG), tex(r"\Rightarrow", 56, MUTE), tex(r"|H| \times \frac{1}{10}", 60, YEL), tex(r"\Rightarrow", 56, MUTE), tex(r"-20\,\mathrm{dB}", 64, RED)).arrange(RIGHT, buff=.3).shift(DOWN * .8)
        r.scale_to_fit_width(min(r.width, 12.5))
        for m in r:
            beat(self, FadeIn(m, shift=RIGHT * .2), t=.7, rt=.3)
        pulse(self, r[4], t=1.2, c=RED)


class DCorner(Scene):
    """두 직선이 꺾이는 점 = 차단 주파수."""
    def construct(self):
        ax, g = bode_axes(o=DOWN * .6); self.add(g, dec_labels(ax, -45))
        a1 = Line(ax.c2p(-2, 0), ax.c2p(0, 0), color=BLU, stroke_width=9); a2 = Line(ax.c2p(0, 0), ax.c2p(2, -40), color=RED, stroke_width=9)
        self.add(a1, a2)
        d = Dot(ax.c2p(0, 0), .18, color=YEL)
        beat(self, FadeIn(d, scale=2), t=.8, rt=.5)
        c = Circle(.45, color=YEL, stroke_width=5).move_to(d)
        beat(self, Create(c), t=.8, rt=.5)
        l = card(VGroup(kr("꺾인 점 =", 44, INK), kr("차단 주파수", 48, GRN)).arrange(RIGHT, buff=.2), GRN, .2).move_to(ax.c2p(-.6, -28))
        beat(self, FadeIn(l, shift=UP * .2), t=1.0, rt=.5)
        e = tex(r"f_c = \frac{1}{2\pi RC}", 52, GRN).to_edge(UP, buff=.3)
        beat(self, Write(e), t=1.0, rt=.6)
        pulse(self, c, t=1.2)


class EQ(Scene):
    """라디오: 왜 한 방송만?"""
    def construct(self):
        R, dial = radio(DOWN * .3, 1.2)
        beat(self, FadeIn(R), t=.8, rt=.5)
        waves = VGroup(*[sine(LEFT * 4.3 + UP * (1.8 - .7 * k), .18, 3 + 2 * k, 2.6, c, sw=4) for k, c in enumerate([PUR, BLU, GRN, ORG])])
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=.2), run_time=1.2)
        self.play(Rotate(dial, PI / 2), run_time=.8)
        q = kr("한 방송만?", 56, YEL).to_edge(UP, buff=.3)
        beat(self, FadeIn(q, scale=1.3), t=1.0, rt=.4)
        self.play(Indicate(q, color=YEL), run_time=.8)
        self.wait(.4)


class EAnt(Scene):
    """안테나 → 섞인 방송 → RLC."""
    def construct(self):
        ant = VGroup(Line(LEFT * 5 + DOWN * .5, LEFT * 5 + UP * 1.6, color=INK, stroke_width=5),
                     Line(LEFT * 5 + UP * 1.6, LEFT * 5.5 + UP * 2.3, color=INK, stroke_width=5), Line(LEFT * 5 + UP * 1.6, LEFT * 4.5 + UP * 2.3, color=INK, stroke_width=5))
        beat(self, Create(ant), t=.6, rt=.5)
        mix = VGroup(*[sine(LEFT * 2.6 + UP * (1.6 - .55 * k), .15, 3 + 2 * k, 2.6, c, sw=4) for k, c in enumerate([PUR, BLU, GRN, ORG])])
        self.play(LaggedStart(*[Create(w) for w in mix], lag_ratio=.2), run_time=1.0)
        lab = kr("모든 방송이 섞임", 36, MUTE).next_to(mix, DOWN, .3)
        beat(self, FadeIn(lab), t=.8, rt=.4)
        g, Rr, L, C, labs = rlc_circuit(RIGHT * 2.6 + DOWN * .3, W=4.6, H=2.0)
        labs.scale(.8)
        beat(self, FadeIn(g), FadeIn(labs), t=1.2, rt=.7)
        a = Arrow(LEFT * 1.1 + UP * .6, RIGHT * .1 + UP * .6, buff=0, color=YEL)
        beat(self, GrowArrow(a), FadeIn(kr("RLC", 40, YEL).next_to(g, UP, .7)), t=1.2, rt=.5)


# 이 파일의 모든 장면 (render.sh 가 class 이름으로 찾음)
