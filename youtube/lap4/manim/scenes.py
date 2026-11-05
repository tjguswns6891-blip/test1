# 라플라스 심화 4편(전달함수·임펄스 응답·컨볼루션) 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나. 1편(lap1/manim/scenes.py)과 같은 도우미·규칙(2~4초마다 새 요소, dur.json 길이 맞춤 fill).
# 검산은 ../lines.py 맨 위 참고. 예제 RC 저역통과 RC=1s → H = 1/(s+1), h = e^−t.
from manim import *
import numpy as np, os, json
from manim import *
import numpy as np, os, json
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
                    for k in range(4)]).arrange(RIGHT, buff=.14)
    return VGroup(kr(f"STEP {n}/4", 28, c), dots).arrange(RIGHT, buff=.25).to_corner(UR, buff=.35)


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



_DP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dur.json")
DUR = json.load(open(_DP)) if os.path.exists(_DP) else {}


def fill(sc, m, c=YEL, extra=0.0):
    """장면 길이를 dur.json 에 맞춘다: 남은 시간 동안 m 둘레를 그렸다 지우기 (멈춘 화면 방지)."""
    tgt = DUR.get(type(sc).__name__, 0) + extra
    rem = tgt - sc.renderer.time
    while rem > 1.7:
        sc.play(Circumscribe(m, color=c, buff=.18, fade_out=True, run_time=1.3)); sc.wait(.2); rem -= 1.5
    sc.wait(max(.3, rem))


def frac(num, dens, size=60, color=INK, dcols=None):
    """분수: 분모는 조각(dens) 별로 따로 집을 수 있게. 반환 VGroup(분자, 막대, 분모그룹)."""
    n = tex(num, size, color)
    d = VGroup(*[tex(x, size, (dcols[i] if dcols else color)) for i, x in enumerate(dens)]).arrange(RIGHT, buff=.06)
    w = max(n.width, d.width) + .25
    bar = Line(LEFT * w / 2, RIGHT * w / 2, stroke_width=4, color=color)
    n.next_to(bar, UP, .14); d.next_to(bar, DOWN, .14)
    return VGroup(n, bar, d)


def taxes(o=ORIGIN, xl=8, yl=3.4, tmax=5, ymin=-.2, ymax=1.2, lab=r"f(t)"):
    ax = Axes(x_range=[0, tmax, 1], y_range=[ymin, ymax, .5], x_length=xl, y_length=yl, tips=True,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False, "tip_length": .18}).move_to(o)
    g = VGroup(ax, tex("t", 36, MUTE).next_to(ax.x_axis.get_end(), DOWN, .15), tex(lab, 34, MUTE).next_to(ax.y_axis.get_end(), RIGHT, .15))
    return ax, g


def splane(o=ORIGIN, w=5.0, h=4.4, xr=(-3, 1), yr=(-3, 3)):
    ax = Axes(x_range=[xr[0], xr[1], 1], y_range=[yr[0], yr[1], 1], x_length=w, y_length=h, tips=True,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": True, "tick_size": .05, "tip_length": .16}).move_to(o)
    g = VGroup(ax, tex(r"\sigma", 36, MUTE).next_to(ax.x_axis.get_end(), DOWN, .12), tex(r"j\omega", 34, MUTE).next_to(ax.y_axis.get_end(), RIGHT, .12))
    return ax, g


def pole(ax, x, y=0, c=YEL, s=.16):
    p = ax.c2p(x, y)
    return VGroup(Line(p + (UL * s), p + (DR * s), color=c, stroke_width=7), Line(p + (UR * s), p + (DL * s), color=c, stroke_width=7))


def f_distinct(t): return 2 * np.exp(-t) - np.exp(-2 * t)
def f_double(t): return t * np.exp(-t)
def f_cplx(t): return np.exp(-t) * np.cos(2 * t)


# ---------- 4편 도우미 ----------
def h_rc(t): return np.exp(-t) if t >= 0 else 0.0


def rc_lp(o=ORIGIN, W=5.6, H=2.4):
    D = rc_circuit(o, W=W, H=H)
    return VGroup(D["g"], D["out"], tex("R", 40, BLU).next_to(D["ser"], UP, .25), tex("C", 40, ORG).next_to(D["sh"], LEFT, .4))


def impulse_arrow(ax, t0=0, h=1.0, c=YEL):
    return Arrow(ax.c2p(t0, 0), ax.c2p(t0, h), buff=0, color=c, stroke_width=7, tip_length=.22)


def conv_num(xf, hf, t, n=400):
    if t <= 0: return 0.0
    tau = np.linspace(0, t, n)
    return np.trapezoid([hf(a) * xf(t - a) for a in tau], tau)


# ================= 인트로 =================
class Hook(Scene):
    """회로 상자를 한 번 툭 → h(t), 그걸로 아무 입력의 출력."""
    def construct(self):
        b = boxio("회로", 2.4, 1.4).shift(UP * 1.6)
        beat(self, FadeIn(b), t=.6, rt=.3)
        ax1, g1 = taxes(LEFT * 4.3 + UP * 1.4, 3.0, 1.8, 3, -.1, 1.3, "x")
        ax2, g2 = taxes(RIGHT * 4.3 + UP * 1.4, 3.0, 1.8, 3, -.1, 1.3, "h")
        im = impulse_arrow(ax1, .05, 1.1)
        beat(self, FadeIn(g1), GrowArrow(im), FadeIn(kr("툭!", 40, YEL).next_to(im, RIGHT, .2)), t=1.0, rt=.5)
        a1 = Arrow(LEFT * 2.6 + UP * 1.6, LEFT * 1.3 + UP * 1.6, buff=0, color=MUTE); a2 = Arrow(RIGHT * 1.3 + UP * 1.6, RIGHT * 2.6 + UP * 1.6, buff=0, color=MUTE)
        h = ax2.plot(lambda t: np.exp(-1.5 * t), x_range=[0, 3, .02], color=GRN, stroke_width=6)
        beat(self, GrowArrow(a1), GrowArrow(a2), FadeIn(g2), Create(h), t=1.2, rt=.9)
        ax3, g3 = taxes(LEFT * 4.3 + DOWN * 1.8, 3.0, 1.8, 3, -.1, 1.3, "x")
        ax4, g4 = taxes(RIGHT * 4.3 + DOWN * 1.8, 3.0, 1.8, 3, -.1, 1.3, "y")
        xin = ax3.plot(lambda t: .5 + .4 * np.sin(4 * t), x_range=[0, 3, .02], color=BLU, stroke_width=5)
        yout = ax4.plot(lambda t: conv_num(lambda u: .5 + .4 * np.sin(4 * u), lambda u: 1.5 * np.exp(-1.5 * u), t, 150), x_range=[0, 3, .03], color=ORG, stroke_width=5)
        beat(self, FadeIn(g3), Create(xin), t=.8, rt=.6)
        q = kr("아무 입력 → 출력 예측", 34, YEL).move_to(DOWN * 1.8)
        beat(self, FadeIn(q), FadeIn(g4), Create(yout), t=1.2, rt=1.0)
        fill(self, yout, ORG)


class Finger(Scene):
    def construct(self):
        ax, g = taxes(LEFT * 2.6 + DOWN * .3, 6.4, 3.8, 5, -.1, 1.2, "h(t)")
        h = ax.plot(lambda t: np.exp(-t), x_range=[0, 5, .02], color=GRN, stroke_width=7)
        beat(self, FadeIn(g), Create(h), t=1.4, rt=1.2)
        t = card(VGroup(kr("임펄스 응답", 40, GRN), kr("= 회로의 지문", 40, YEL)).arrange(DOWN, buff=.25), GRN, .35).move_to(RIGHT * 4.2)
        beat(self, FadeIn(t, shift=LEFT * .2), t=1.1, rt=.5)
        fill(self, t, GRN)


class ConvMul(Scene):
    def construct(self):
        a = tex(r"y(t) = \int_0^t h(\tau)\,x(t-\tau)\,d\tau", 62, MUTE).shift(UP * 1.6)
        beat(self, Write(a), FadeIn(kr("컨볼루션 (적분)", 32, MUTE).next_to(a, UP, .3)), t=1.4, rt=1.0)
        ar = Arrow(UP * .7, DOWN * .5, buff=0, color=YEL, stroke_width=7)
        lab = tex(r"\mathcal{L}", 50, YEL).next_to(ar, RIGHT, .3)
        beat(self, GrowArrow(ar), FadeIn(lab), t=.8, rt=.4)
        b = tex(r"Y(s) = H(s)\,X(s)", 80, YEL).shift(DOWN * 1.6)
        beat(self, Write(b), FadeIn(kr("곱셈", 44, YEL).next_to(b, DOWN, .3)), t=1.2, rt=.7)
        fill(self, b)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "전달함수", BLU), ("2", "임펄스 응답", GRN), ("3", "컨볼루션", PUR), ("4", "곱셈으로 풀기", ORG)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.3).scale_to_fit_width(12.8).shift(UP * .3)
        for kk in cards:
            beat(self, FadeIn(kk, shift=UP * .3), t=1.1, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[3].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), FadeIn(kr("시리즈 마지막 편", 34, MUTE).next_to(arrow, DOWN, .3)), t=1.0, rt=.6)
        fill(self, cards[3], ORG)


# ================= STEP 1 전달함수 =================
class A1(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        h = tex(r"H(s) = \frac{Y(s)}{X(s)}", 90, YEL).shift(UP * .6)
        beat(self, Write(h), t=1.3, rt=.9)
        c = card(kr("초기 조건 = 0", 36, MUTE), "#2a2e37", .25).next_to(h, DOWN, .8)
        beat(self, FadeIn(c), t=.8, rt=.3)
        beat(self, FadeIn(kr("전달함수", 44, BLU).next_to(h, UP, .5)), t=.7, rt=.3)
        fill(self, h)


class A2(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        b = boxio("H(s)", 2.6, 1.5)
        b[1].become(tex("H(s)", 56, YEL).move_to(b[0]))
        beat(self, FadeIn(b), t=.6, rt=.3)
        i = VGroup(Arrow(LEFT * 4.2, LEFT * 1.4, buff=0, color=BLU), tex("X(s)", 52, BLU).move_to(LEFT * 5.2))
        o = VGroup(Arrow(RIGHT * 1.4, RIGHT * 4.2, buff=0, color=ORG), tex("Y(s)", 52, ORG).move_to(RIGHT * 5.2))
        beat(self, GrowArrow(i[0]), FadeIn(i[1]), t=.8, rt=.4)
        beat(self, GrowArrow(o[0]), FadeIn(o[1]), t=.8, rt=.4)
        e = tex(r"Y = H \cdot X", 84, YEL).shift(DOWN * 2.1)
        beat(self, Write(e), t=1.0, rt=.6)
        fill(self, e)


class A3(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        c = rc_lp(UP * 1.0, 5.4, 2.2)
        beat(self, Create(c), t=1.2, rt=.9)
        e = tex(r"H(s) = \frac{\frac{1}{sC}}{R + \frac{1}{sC}} = \frac{1}{RCs + 1}", 58, YEL).move_to(DOWN * 2.2)
        beat(self, Write(e), FadeIn(kr("전압 분배", 30, MUTE).next_to(e, LEFT, .4)), t=1.6, rt=1.1)
        fill(self, e)


class A4(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        a = tex(r"RC = 1\,\mathrm{s}", 50, MUTE).move_to(LEFT * 3.4 + UP * 1.8)
        beat(self, FadeIn(a), t=.6, rt=.3)
        h = tex(r"H(s) = \frac{1}{s+1}", 80, YEL).move_to(LEFT * 3.2 + DOWN * .2)
        beat(self, Write(h), t=1.1, rt=.7)
        ax, gg = splane(RIGHT * 3.4, 4.2, 4.2, (-3, 1), (-2, 2))
        p = pole(ax, -1, 0, YEL)
        beat(self, FadeIn(gg), Create(p), FadeIn(tex("-1", 38, YEL).next_to(p, DOWN, .3)), t=1.1, rt=.6)
        fill(self, p)


class A5(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        b = boxio("", 2.4, 1.4); b[1].become(tex(r"\frac{1}{s+1}", 52, YEL).move_to(b[0]))
        self.add(b)
        ins = [(lambda t: 1.0, "계단"), (lambda t: np.sin(3 * t) * .8, "사인파"), (lambda t: np.exp(-2 * t), "지수")]
        prev = None
        for f, n in ins:
            ax, g = taxes(LEFT * 4.6, 2.8, 1.8, 3, -1, 1.2, "x")
            cur = ax.plot(f, x_range=[0, 3, .02], color=BLU, stroke_width=5)
            grp = VGroup(g, cur, kr(n, 30, BLU).next_to(g, DOWN, .2))
            if prev: self.play(FadeOut(prev), run_time=.3)
            beat(self, FadeIn(grp), t=.9, rt=.4); prev = grp
        t = kr("H는 회로만으로 결정", 40, YEL).to_edge(DOWN, buff=.7)
        beat(self, FadeIn(t), Indicate(b[1], color=YEL), t=1.0, rt=.6)
        fill(self, b)


# ================= STEP 2 임펄스 응답 =================
class B1(Scene):
    def construct(self):
        self.add(step_tag(2, GRN))
        ax, g = taxes(DOWN * .6, 9, 4.2, 4, 0, 4.4, "")
        self.add(g)
        k = ValueTracker(1.2)
        rect = always_redraw(lambda: Rectangle(width=ax.c2p(k.get_value(), 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, 1 / k.get_value())[1] - ax.c2p(0, 0)[1],
                                               color=YEL, fill_color=YEL, fill_opacity=.35, stroke_width=4).move_to(ax.c2p(0, 0), aligned_edge=DL))
        lab = kr("넓이 = 1", 40, YEL).move_to(RIGHT * 3 + UP * 2.4)
        self.add(rect); beat(self, FadeIn(lab), t=.6, rt=.3)
        self.play(k.animate.set_value(.25), run_time=2.0)
        d = tex(r"\delta(t)", 70, YEL).move_to(RIGHT * 3 + UP * 1.3)
        beat(self, Write(d), t=.8, rt=.5)
        fill(self, d)


class B2(Scene):
    def construct(self):
        self.add(step_tag(2, GRN))
        e1 = tex(r"\mathcal{L}\{\delta(t)\} = \int_0^\infty \delta(t)\,e^{-st}\,dt", 64).shift(UP * 1.4)
        beat(self, Write(e1), t=1.4, rt=1.0)
        n = kr("t = 0 에서만 값이 있음", 34, MUTE).next_to(e1, DOWN, .4)
        beat(self, FadeIn(n), t=.8, rt=.3)
        e2 = tex(r"= e^{0} = 1", 84, YEL).shift(DOWN * 1.6)
        beat(self, Write(e2), t=1.0, rt=.6)
        fill(self, e2)


class B3(Scene):
    def construct(self):
        self.add(step_tag(2, GRN))
        e = MathTex(r"Y = H \cdot", r"X", font_size=90, color=INK).shift(UP * 1.2)
        beat(self, FadeIn(e), t=.6, rt=.3)
        one = tex("1", 90, YEL).move_to(e[1])
        beat(self, Transform(e[1], one), FadeIn(tex(r"(\delta)", 44, MUTE).next_to(e, RIGHT, .3)), t=1.0, rt=.6)
        r = tex(r"Y = H(s)", 90, GRN).shift(DOWN * 1.2)
        beat(self, Write(r), FadeIn(kr("출력 = H 그 자체", 36, GRN).next_to(r, DOWN, .3)), t=1.0, rt=.6)
        fill(self, r, GRN)


class B4(Scene):
    def construct(self):
        self.add(step_tag(2, GRN))
        e = tex(r"h(t) = \mathcal{L}^{-1}\Big\{\frac{1}{s+1}\Big\} = e^{-t}", 60, GRN).to_edge(UP, buff=.8)
        beat(self, Write(e), t=1.3, rt=.9)
        ax, g = taxes(DOWN * 1.0, 9.6, 3.8, 5, -.1, 1.2, "h(t)")
        h = ax.plot(lambda t: np.exp(-t), x_range=[0, 5, .02], color=GRN, stroke_width=7)
        beat(self, FadeIn(g), Create(h), t=1.5, rt=1.2)
        beat(self, FadeIn(kr("임펄스 응답", 40, GRN).move_to(ax.c2p(3.2, .7))), t=.7, rt=.3)
        fill(self, h, GRN)


class B5(Scene):
    def construct(self):
        self.add(step_tag(2, GRN))
        bell = VGroup(Arc(radius=1.1, start_angle=0, angle=PI, color=ORG, stroke_width=7), Line(LEFT * 1.4, RIGHT * 1.4, color=ORG, stroke_width=7).shift(DOWN * .05),
                      Dot(DOWN * .35, .14, color=ORG)).move_to(LEFT * 4.2 + UP * .4)
        beat(self, FadeIn(bell), t=.7, rt=.3)
        hm = Line(LEFT * 6.2 + UP * 1.4, LEFT * 5.2 + UP * .6, color=MUTE, stroke_width=8)
        beat(self, Create(hm), Wiggle(bell), t=.9, rt=.6)
        ax, g = taxes(RIGHT * 2.0 + UP * .3, 7, 3, 6, -1.1, 1.1, "")
        s = ax.plot(lambda t: np.exp(-.6 * t) * np.sin(7 * t), x_range=[0, 6, .01], color=ORG, stroke_width=4)
        beat(self, FadeIn(g), Create(s), t=1.4, rt=1.2)
        t = kr("한 번 친 소리 = 종의 성격", 38, YEL).to_edge(DOWN, buff=.7)
        beat(self, FadeIn(t), t=.8, rt=.3)
        fill(self, t)


class B6(Scene):
    def construct(self):
        self.add(step_tag(2, GRN))
        e = tex(r"\frac{5}{s^2 + 2s + 5}", 64, GRN).move_to(LEFT * 4.2 + UP * 1.2)
        beat(self, FadeIn(e), FadeIn(kr("3편 부족감쇠 RLC", 30, MUTE).next_to(e, UP, .3)), t=.9, rt=.4)
        ax, g = taxes(RIGHT * 1.6 + DOWN * .4, 8, 3.8, 6, -1.2, 2.0, "h(t)")
        h = ax.plot(lambda t: 2.5 * np.exp(-t) * np.sin(2 * t), x_range=[0, 6, .01], color=GRN, stroke_width=6)
        beat(self, FadeIn(g), Create(h), t=1.6, rt=1.4)
        beat(self, FadeIn(kr("h(t)도 출렁임", 36, GRN).move_to(ax.c2p(4.2, 1.4))), t=.7, rt=.3)
        fill(self, h, GRN)


# ================= STEP 3 컨볼루션 =================
def xin(t): return .6 + .35 * np.sin(2.2 * t) if t >= 0 else 0.0


class C1(Scene):
    def construct(self):
        self.add(step_tag(3, PUR))
        ax, g = taxes(DOWN * .3, 10, 4.2, 5, -.05, 1.1, "x(t)")
        c = ax.plot(xin, x_range=[0, 5, .02], color=BLU, stroke_width=6)
        beat(self, FadeIn(g), Create(c), t=1.1, rt=.8)
        bars = VGroup(*[Rectangle(width=ax.c2p(.25, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, xin(t + .125))[1] - ax.c2p(0, 0)[1],
                                  stroke_color=BLU, stroke_width=2, fill_color=BLU, fill_opacity=.35).move_to(ax.c2p(t, 0), aligned_edge=DL) for t in np.arange(0, 5, .25)])
        beat(self, LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=.05), t=1.4, rt=1.2)
        beat(self, FadeIn(kr("조각 하나 = 작은 임펄스", 36, YEL).to_edge(UP, buff=.7)), t=.7, rt=.3)
        fill(self, bars, BLU)


class C2(Scene):
    def construct(self):
        self.add(step_tag(3, PUR))
        ax, g = taxes(DOWN * .3, 10, 4.2, 5, -.05, 1.1, "")
        self.add(g)
        cols = [BLU, PUR, ORG, GRN]
        for i, t0 in enumerate([0, .8, 1.6, 2.4]):
            a = xin(t0) * .35
            ar = impulse_arrow(ax, t0, a * 2.2, cols[i])
            hc = ax.plot(lambda t, t0=t0, a=a: a * np.exp(-(t - t0)) if t >= t0 else 0, x_range=[t0, 5, .02], color=cols[i], stroke_width=5)
            beat(self, GrowArrow(ar), Create(hc), t=.9, rt=.6)
        beat(self, FadeIn(kr("높이만큼 · 늦게 시작하는 h", 34, YEL).to_edge(UP, buff=.7)), t=.7, rt=.3)
        fill(self, g[0])


class C3(Scene):
    def construct(self):
        self.add(step_tag(3, PUR))
        ax, g = taxes(DOWN * .3, 10, 4.2, 5, -.05, 1.2, "")
        self.add(g)
        dt = .25
        hs = VGroup(*[ax.plot(lambda t, t0=t0: xin(t0) * dt * np.exp(-(t - t0)) if t >= t0 else 0, x_range=[t0, 5, .02], color=MUTE, stroke_width=2) for t0 in np.arange(0, 5, dt)])
        beat(self, LaggedStart(*[Create(h) for h in hs], lag_ratio=.05), t=1.4, rt=1.2)
        y = ax.plot(lambda t: conv_num(xin, h_rc, t, 200), x_range=[0, 5, .03], color=ORG, stroke_width=7)
        beat(self, Create(y), FadeIn(kr("전부 더하면 = 출력", 36, ORG).to_edge(UP, buff=.7)), t=1.4, rt=1.1)
        fill(self, y, ORG)


class C4(Scene):
    def construct(self):
        self.add(step_tag(3, PUR))
        a = tex(r"y = \sum x(\tau)\,\Delta\tau\; h(t-\tau)", 60, MUTE).shift(UP * 1.5)
        beat(self, FadeIn(a), t=.9, rt=.4)
        b = tex(r"y(t) = \int_0^t x(\tau)\,h(t-\tau)\,d\tau", 72, PUR).shift(DOWN * .4)
        beat(self, TransformFromCopy(a, b), t=1.3, rt=.9)
        c = tex(r"= (x * h)(t)", 64, YEL).next_to(b, DOWN, .5)
        beat(self, Write(c), FadeIn(kr("컨볼루션", 40, YEL).next_to(c, RIGHT, .4)), t=1.0, rt=.6)
        fill(self, b, PUR)


class C5(Scene):
    """뒤집고 밀기: h(t−τ) 를 밀면서 겹치는 넓이."""
    def construct(self):
        self.add(step_tag(3, PUR))
        ax, g = taxes(UP * .9, 10, 2.6, 5, -.05, 1.1, "")
        self.add(g)
        xs = ax.plot(lambda t: 1.0, x_range=[0, 5, .02], color=BLU, stroke_width=5)
        self.add(xs, tex("x(\\tau)", 36, BLU).next_to(ax.c2p(5, 1), UP, .1))
        k = ValueTracker(.2)
        hf = always_redraw(lambda: ax.plot(lambda t: np.exp(-(k.get_value() - t)) if t <= k.get_value() else 0, x_range=[max(0, k.get_value() - 5), k.get_value(), .02], color=GRN, stroke_width=5))
        area = always_redraw(lambda: ax.get_area(ax.plot(lambda t: np.exp(-(k.get_value() - t)), x_range=[0, k.get_value(), .02]), x_range=[0, k.get_value()], color=YEL, opacity=.35))
        beat(self, FadeIn(hf), FadeIn(kr("뒤집은 h", 30, GRN).move_to(UP * 3.3 + LEFT * 3)), t=.8, rt=.4)
        self.add(area)
        ay, gy = taxes(DOWN * 2.2, 10, 2.0, 5, -.05, 1.1, "y")
        self.add(gy)
        tr = always_redraw(lambda: ay.plot(lambda t: 1 - np.exp(-t), x_range=[0, max(.02, k.get_value()), .02], color=ORG, stroke_width=6))
        self.add(tr)
        self.play(k.animate.set_value(4.8), run_time=3.2, rate_func=linear)
        fill(self, tr, ORG)


class C6(Scene):
    def construct(self):
        self.add(step_tag(3, PUR))
        e = tex(r"\int_0^t e^{-\tau}\cdot 1\,d\tau", 72).shift(UP * 1.4)
        beat(self, Write(e), FadeIn(kr("계단 입력", 32, BLU).next_to(e, LEFT, .5)), t=1.2, rt=.8)
        r = tex(r"= 1 - e^{-t}", 84, ORG).shift(DOWN * .6)
        beat(self, Write(r), t=1.0, rt=.6)
        fill(self, r, ORG)


class C7(Scene):
    def construct(self):
        self.add(step_tag(3, PUR))
        e = tex(r"\int_0^t e^{-\tau}\,\big(0.6 + 0.35\sin 2.2(t-\tau)\big)\,d\tau", 54, MUTE).shift(UP * .8)
        beat(self, Write(e), t=1.4, rt=1.0)
        w = kr("입력이 복잡하면 적분이 금방 어려움", 36, RED).shift(DOWN * 1.2)
        beat(self, FadeIn(w), t=.8, rt=.3)
        fill(self, w, RED)


# ================= 중간 정리 =================
class M1(Scene):
    def construct(self):
        self.add(kr("중간 정리", 36, MUTE).to_corner(UL, buff=.5))
        a = card(VGroup(kr("시간 영역", 30, MUTE), tex(r"h * x", 64, PUR)).arrange(DOWN, buff=.25), PUR, .35).shift(LEFT * 3.4)
        b = card(VGroup(kr("s-영역", 30, MUTE), tex(r"H \cdot X", 64, YEL)).arrange(DOWN, buff=.25), YEL, .35).shift(RIGHT * 3.4)
        beat(self, FadeIn(a), t=.8, rt=.4)
        ar = DoubleArrow(a.get_right(), b.get_left(), buff=.2, color=MUTE)
        beat(self, GrowFromCenter(ar), FadeIn(b), t=1.0, rt=.5)
        t = kr("컨볼루션 = 곱셈", 48, YEL).to_edge(DOWN, buff=.8)
        beat(self, FadeIn(t), t=.8, rt=.3)
        fill(self, t)


class M2(Scene):
    def construct(self):
        self.add(kr("중간 정리", 36, MUTE).to_corner(UL, buff=.5))
        a = tex(r"Y = \frac{1}{s+1}\cdot\frac{1}{s}", 70).shift(UP * 1.2)
        beat(self, Write(a), t=1.1, rt=.7)
        b = tex(r"= \frac{1}{s} - \frac{1}{s+1}", 70, YEL).shift(DOWN * .8)
        beat(self, Write(b), FadeIn(kr("가리기법", 30, MUTE).next_to(b, RIGHT, .4)), t=1.1, rt=.7)
        fill(self, b)


class M3(Scene):
    def construct(self):
        self.add(kr("중간 정리", 36, MUTE).to_corner(UL, buff=.5))
        r = tex(r"y(t) = 1 - e^{-t}", 80, ORG).shift(UP * 1.4)
        beat(self, Write(r), t=1.0, rt=.6)
        ax, g = taxes(DOWN * 1.4, 8, 2.6, 5, -.05, 1.1, "y")
        beat(self, FadeIn(g), Create(ax.plot(lambda t: 1 - np.exp(-t), x_range=[0, 5, .02], color=ORG, stroke_width=6)), t=1.2, rt=1.0)
        beat(self, FadeIn(kr("적분 없이 같은 답 ✔", 36, GRN).next_to(r, RIGHT, .4)), t=.7, rt=.3)
        fill(self, r, ORG)


# ================= STEP 4 곱셈으로 풀기 =================
class N1(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        e = tex(r"x(t) = e^{-2t}", 80, BLU).shift(UP * 1.4)
        beat(self, Write(e), t=1.0, rt=.6)
        ax, g = taxes(DOWN * 1.3, 8, 2.6, 4, -.05, 1.1, "x")
        beat(self, FadeIn(g), Create(ax.plot(lambda t: np.exp(-2 * t), x_range=[0, 4, .02], color=BLU, stroke_width=6)), t=1.2, rt=1.0)
        fill(self, e, BLU)


class N2(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        a = tex(r"X(s) = \frac{1}{s+2}", 64, BLU).shift(UP * 1.8)
        beat(self, Write(a), t=1.0, rt=.6)
        b = tex(r"Y = H\cdot X = \frac{1}{s+1}\cdot\frac{1}{s+2}", 60).shift(DOWN * .1)
        beat(self, Write(b), t=1.3, rt=.9)
        c = tex(r"= \frac{1}{(s+1)(s+2)}", 64, YEL).shift(DOWN * 1.9)
        beat(self, Write(c), t=1.0, rt=.6)
        fill(self, c)


class N3(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        F = frac("1", ["(s+1)", "(s+2)"], 76, YEL).shift(LEFT * 3.4)
        self.add(F)
        hc = hand_cover(F[2][0], BLU) if "hand_cover" in globals() else SurroundingRectangle(F[2][0], color=BLU, fill_color=BLU, fill_opacity=.85)
        beat(self, FadeIn(hc), FadeIn(tex(r"s=-1 \Rightarrow 1", 44, BLU).move_to(RIGHT * 2.4 + UP * 1.4)), t=1.1, rt=.6)
        beat(self, FadeOut(hc), FadeIn(tex(r"s=-2 \Rightarrow -1", 44, PUR).move_to(RIGHT * 2.4 + UP * .2)), t=1.1, rt=.6)
        r = tex(r"= \frac{1}{s+1} - \frac{1}{s+2}", 64, YEL).shift(DOWN * 1.9)
        beat(self, Write(r), t=1.0, rt=.6)
        fill(self, r)


class N4(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        r = tex(r"y(t) = e^{-t} - e^{-2t}", 76, ORG).shift(UP * 1.8)
        beat(self, Write(r), t=1.0, rt=.6)
        c = tex(r"\int_0^t e^{-\tau} e^{-2(t-\tau)}\,d\tau = e^{-t} - e^{-2t}", 52, MUTE).shift(UP * .2)
        beat(self, FadeIn(c), FadeIn(kr("컨볼루션으로도 ✔", 32, GRN).next_to(c, DOWN, .3)), t=1.4, rt=.6)
        ax, g = taxes(DOWN * 2.2, 7, 1.8, 5, -.02, .3, "y")
        beat(self, FadeIn(g), Create(ax.plot(lambda t: np.exp(-t) - np.exp(-2 * t), x_range=[0, 5, .02], color=ORG, stroke_width=6)), t=1.0, rt=.8)
        fill(self, r, ORG)


class N5(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        a = tex(r"H(s) = \frac{1}{s+1}", 64).shift(UP * 1.8 + LEFT * 2.6)
        beat(self, FadeIn(a), FadeIn(kr("보너스", 32, YEL).next_to(a, UP, .3)), t=.8, rt=.4)
        b = tex(r"s \to j\omega", 64, YEL).next_to(a, RIGHT, 1.0)
        beat(self, Write(b), t=.8, rt=.5)
        c = tex(r"H(j\omega) = \frac{1}{1 + j\omega}", 80, GRN).shift(DOWN * .6)
        beat(self, Write(c), t=1.1, rt=.7)
        w = sine(DOWN * 2.6 + LEFT * 2.4, .4, 3, 4, BLU); w2 = sine(DOWN * 2.6 + RIGHT * 2.4, .25, 3, 4, ORG, phase=.8)
        beat(self, Create(w), Create(w2), FadeIn(Arrow(LEFT * .3 + DOWN * 2.6, RIGHT * .3 + DOWN * 2.6, buff=0, color=MUTE)), t=1.0, rt=.7)
        fill(self, c, GRN)


class N6(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax = Axes(x_range=[-2, 2, 1], y_range=[0, 1.15, .5], x_length=8, y_length=3.2, tips=True,
                  axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False, "tip_length": .2}).shift(DOWN * .4 + LEFT * 1.2)
        cur = ax.plot(lambda x: 1 / np.sqrt(1 + 10 ** (2 * x)), x_range=[-2, 2, .02], color=YEL, stroke_width=6)
        beat(self, FadeIn(ax), FadeIn(kr("주파수 →", 26, MUTE).next_to(ax.x_axis.get_end(), DOWN, .2)), Create(cur), t=1.4, rt=1.2)
        t = card(kr("지난 영상 · 주파수 응답", 32, MUTE), "#2a2e37", .25).to_edge(UP, buff=.6)
        beat(self, FadeIn(t), t=.7, rt=.3)
        h = card(tex("H(s)", 60, YEL), YEL, .3).move_to(RIGHT * 4.8 + DOWN * .4)
        beat(self, FadeIn(h), FadeIn(kr("전부 여기서", 30, YEL).next_to(h, DOWN, .25)), t=.9, rt=.4)
        fill(self, h)


# ================= 정리 =================
class O1(Scene):
    def construct(self):
        e = tex(r"Y(s) = H(s)\,X(s)", 90, YEL)
        beat(self, Write(e), t=1.2, rt=.8)
        beat(self, FadeIn(kr("H는 회로만으로", 36, MUTE).next_to(e, DOWN, .6)), t=.7, rt=.3)
        fill(self, e)


class O2(Scene):
    def construct(self):
        a = tex(r"h(t) = \mathcal{L}^{-1}\{H(s)\}", 70, GRN).shift(UP * 1.0)
        beat(self, Write(a), t=1.1, rt=.7)
        b = card(kr("임펄스 응답 = 회로의 지문", 40, GRN), GRN, .3).shift(DOWN * 1.3)
        beat(self, FadeIn(b), t=.8, rt=.3)
        fill(self, b, GRN)


class O3(Scene):
    def construct(self):
        a = tex(r"\int_0^t h(\tau)x(t-\tau)d\tau", 54, MUTE).shift(LEFT * 3.4); x = Cross(a, stroke_color=RED, stroke_width=5)
        b = tex(r"H\cdot X", 76, YEL).shift(RIGHT * 3.4)
        beat(self, FadeIn(a), t=.7, rt=.3)
        beat(self, Create(x), GrowArrow(Arrow(LEFT * .8, RIGHT * 1.8, buff=0, color=YEL)), FadeIn(b), t=1.1, rt=.6)
        beat(self, FadeIn(kr("적분 대신 분수 계산", 40, YEL).to_edge(DOWN, buff=.8)), t=.7, rt=.3)
        fill(self, b)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("입력 바꿔 보며 출력 확인", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55).shift(LEFT * 3.0)
        beat(self, FadeIn(t[0]), FadeIn(t[1][0]), t=.8, rt=.3)
        ax, g = taxes(RIGHT * 3.9, 4.0, 2.6, 5, -.05, 1.1, "y")
        self.add(g)
        for m in t[1][1:]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.0, rt=.4)
        beat(self, Create(ax.plot(lambda tt: conv_num(xin, h_rc, tt, 150), x_range=[0, 5, .04], color=ORG, stroke_width=5)), t=2.0, rt=1.8)
        fill(self, t, YEL)


class End(Scene):
    def construct(self):
        items = ["1편 역변환", "2편 s-영역 회로", "3편 2차 RLC", "4편 컨볼루션"]
        cs = VGroup(*[card(kr(s, 32, YEL if i == 3 else INK), YEL if i == 3 else "#2a2e37", .28) for i, s in enumerate(items)]).arrange(RIGHT, buff=.3)
        cs.scale_to_fit_width(min(cs.width, 12.8))
        lab = kr("재생목록 · 라플라스 심화", 40, INK).next_to(cs, UP, .7)
        beat(self, FadeIn(lab), t=.8, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cs], lag_ratio=.3), run_time=1.6)
        beat(self, FadeIn(kr("시리즈 완결 ✔", 44, GRN).next_to(cs, DOWN, .7)), t=.9, rt=.4)
        fill(self, cs)


# ================= 쇼츠 전용 =================
class AQ(Scene):
    def construct(self):
        b = boxio("회로", 3.0, 1.8).shift(UP * .4)
        beat(self, FadeIn(b), t=.6, rt=.3)
        hm = Line(LEFT * 3.6 + UP * 2.4, LEFT * 1.6 + UP * 1.2, color=YEL, stroke_width=10)
        beat(self, Create(hm), Wiggle(b), t=1.0, rt=.6)
        t = kr("한 번 치면 다 안다", 52, YEL).to_edge(DOWN, buff=.9)
        beat(self, FadeIn(t, scale=1.3), t=.8, rt=.4)
        fill(self, t)


class BQ(Scene):
    def construct(self):
        e = tex(r"(x * h)(t)", 100, PUR).shift(UP * .6)
        beat(self, FadeIn(e), t=.7, rt=.3)
        t = kr("그림으로 보면 쉬움", 50, YEL).shift(DOWN * 1.6)
        beat(self, FadeIn(t, scale=1.3), t=.8, rt=.4)
        fill(self, e, PUR)


class BFlip(Scene):
    def construct(self):
        ax, g = taxes(DOWN * .2, 10, 3.6, 5, -.05, 1.1, "")
        ax.shift(RIGHT * 0); self.add(g)
        h = ax.plot(lambda t: np.exp(-t), x_range=[0, 5, .02], color=GRN, stroke_width=6)
        beat(self, Create(h), FadeIn(tex(r"h(\tau)", 44, GRN).move_to(ax.c2p(1.6, .8))), t=1.0, rt=.6)
        hf = ax.plot(lambda t: np.exp(-(2.5 - t)), x_range=[0, 2.5, .02], color=YEL, stroke_width=6)
        beat(self, TransformFromCopy(h, hf), FadeIn(kr("좌우로 뒤집기", 40, YEL).to_edge(UP, buff=.7)), t=1.4, rt=1.0)
        fill(self, hf)


class BTrace(Scene):
    def construct(self):
        ay, gy = taxes(DOWN * .2, 10, 3.8, 5, -.05, 1.1, "y")
        self.add(gy)
        k = ValueTracker(.05)
        tr = always_redraw(lambda: ay.plot(lambda t: 1 - np.exp(-t), x_range=[0, k.get_value(), .02], color=ORG, stroke_width=7))
        dot = always_redraw(lambda: Dot(ay.c2p(k.get_value(), 1 - np.exp(-k.get_value())), .12, color=YEL))
        self.add(tr, dot)
        beat(self, FadeIn(kr("t마다 겹친 넓이를 찍으면", 38, YEL).to_edge(UP, buff=.7)), t=.5, rt=.3)
        self.play(k.animate.set_value(5), run_time=2.6, rate_func=linear)
        fill(self, tr, ORG)


class CQ(Scene):
    def construct(self):
        a = tex(r"\int", 140, MUTE).shift(LEFT * 3); b = tex(r"\times", 140, YEL).shift(RIGHT * 3)
        beat(self, FadeIn(a), t=.6, rt=.3)
        beat(self, GrowArrow(Arrow(LEFT * 1.6, RIGHT * 1.6, buff=0, color=YEL, stroke_width=8)), FadeIn(b), t=.9, rt=.5)
        t = kr("적분 → 곱셈", 56, YEL).to_edge(DOWN, buff=.9)
        beat(self, FadeIn(t), t=.7, rt=.3)
        fill(self, b)


class DQ(Scene):
    def construct(self):
        e = tex(r"\mathcal{L}\{\delta(t)\} = 1\;?", 100, YEL)
        beat(self, Write(e), t=1.0, rt=.6)
        fill(self, e)


class DOne(Scene):
    def construct(self):
        e = tex(r"e^{-s\cdot 0} = e^{0} = 1", 96, YEL)
        beat(self, Write(e), t=1.2, rt=.8)
        fill(self, e)


class EQ(Scene):
    def construct(self):
        a = tex(r"s", 140, YEL).shift(LEFT * 2.4); b = tex(r"j\omega", 140, GRN).shift(RIGHT * 2.4)
        beat(self, FadeIn(a), t=.6, rt=.3)
        beat(self, GrowArrow(Arrow(LEFT * 1.3, RIGHT * 1.0, buff=0, color=MUTE, stroke_width=8)), FadeIn(b), t=.9, rt=.5)
        t = kr("주파수 응답", 52, GRN).to_edge(DOWN, buff=.9)
        beat(self, FadeIn(t), t=.7, rt=.3)
        fill(self, b, GRN)
