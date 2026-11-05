# 라플라스 심화 3편(2차 RLC 회로, 극점으로 끝내기) 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나. 1편(lap1/manim/scenes.py)과 같은 도우미·규칙(2~4초마다 새 요소, dur.json 길이 맞춤 fill).
# 검산은 ../lines.py 맨 위 참고. 예제 L=1H, C=0.2F (ω0=√5), 1V 계단 입력, 출력 v_C.
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


# ---------- 3편 도우미 ----------
W0 = np.sqrt(5.0)
RC_ = 2 * W0          # 임계 R ≈ 4.47


def poles_R(R):
    a = R / 2
    d = a * a - 5
    if d >= 0:
        return (-a + np.sqrt(d), 0.0), (-a - np.sqrt(d), 0.0)
    w = np.sqrt(-d)
    return (-a, w), (-a, -w)


def step_R(R, t):
    a = R / 2
    if abs(a - W0) < 1e-3:
        return 1 - (1 + a * t) * np.exp(-a * t)
    if a > W0:
        r = np.sqrt(a * a - 5); s1, s2 = -a + r, -a - r
        return 1 + (s2 * np.exp(s1 * t) - s1 * np.exp(s2 * t)) / (s1 - s2)
    w = np.sqrt(5 - a * a)
    return 1 - np.exp(-a * t) * (np.cos(w * t) + a / w * np.sin(w * t))


def f_over(t): return step_R(6, t)
def f_crit(t): return step_R(RC_, t)
def f_under(t): return step_R(2, t)


def step_src(p, c=YEL, r=.45):
    p = P3(p)
    st = VMobject(color=c, stroke_width=5).set_points_as_corners([p + np.array([-.25, -.15, 0]), p + np.array([-.02, -.15, 0]), p + np.array([-.02, .15, 0]), p + np.array([.25, .15, 0])])
    return VGroup(Circle(r, color=c, stroke_width=5).move_to(p), st)


def rlc_step(o=ORIGIN, W=6.4, H=2.6, sdom=False):
    """계단 전원 — R — L — C(세로, 출력)."""
    o = P3(o); x0, x1 = o[0] - W / 2, o[0] + W / 2; yt, yb = o[1] + H / 2, o[1] - H / 2
    xs = np.linspace(x0, x1, 4)
    src = step_src((x0, o[1]))
    R = resistor((xs[0], yt), (xs[1], yt), BLU); L = coil((xs[1], yt), (xs[2], yt), GRN); C = capacitor((xs[3], yt), (xs[3], yb), ORG)[0]
    g = VGroup(wire((x0, yt), (x0, o[1] + .45)), wire((x0, o[1] - .45), (x0, yb)), wire((xs[2], yt), (xs[3], yt)), wire((x0, yb), (xs[3], yb)))
    if sdom:
        labs = VGroup(tex("R", 44, BLU).next_to(R, UP, .25), tex("sL", 44, GRN).next_to(L, UP, .25), tex(r"\frac{1}{sC}", 44, ORG).next_to(C, RIGHT, .3),
                      tex(r"\frac{1}{s}", 42, YEL).next_to(src, LEFT, .25))
    else:
        labs = VGroup(tex("R", 44, BLU).next_to(R, UP, .25), tex("L", 44, GRN).next_to(L, UP, .25), tex("C", 44, ORG).next_to(C, RIGHT, .3),
                      tex(r"1\,\mathrm{V}", 40, YEL).next_to(src, LEFT, .25))
    return dict(src=src, R=R, L=L, C=C, g=g, labs=labs)


def resp_axes(o=ORIGIN, xl=8, yl=3.4, tmax=6, ymax=1.45):
    ax, g = taxes(o, xl, yl, tmax, -.05, ymax, r"v_C")
    one = DashedLine(ax.c2p(0, 1), ax.c2p(tmax, 1), color=MUTE, stroke_width=2)
    return ax, VGroup(g, one, tex("1", 30, MUTE).next_to(ax.c2p(0, 1), LEFT, .12))


CASES = [(6, BLU, "과감쇠"), (RC_, PUR, "임계감쇠"), (2, GRN, "부족감쇠")]


# ================= 인트로 =================
class Hook(Scene):
    """R 노브를 돌리면 응답이 과감쇠 → 임계 → 부족감쇠로."""
    def construct(self):
        D = rlc_step(LEFT * 3.9 + UP * .9, 5.0, 2.0)
        self.add(D["g"], D["src"], D["R"], D["L"], D["C"], D["labs"])
        ax, g = resp_axes(RIGHT * 3.0 + DOWN * .4, 7, 3.8)
        self.add(g)
        k = ValueTracker(7.0)
        cur = always_redraw(lambda: ax.plot(lambda t: step_R(k.get_value(), t), x_range=[0, 6, .02], stroke_width=6,
                                            color=BLU if k.get_value() > RC_ + .05 else (PUR if k.get_value() > RC_ - .05 else GRN)))
        rl = always_redraw(lambda: tex(f"R = {k.get_value():.1f}" + r"\,\Omega", 48, YEL).move_to(LEFT * 3.9 + DOWN * 1.3))
        self.add(cur, rl); self.wait(.6)
        labs = {}
        for R, c, n in CASES:
            self.play(k.animate.set_value(R), run_time=1.3)
            l = kr(n, 40, c).move_to(LEFT * 3.9 + DOWN * 2.4); self.play(FadeIn(l), run_time=.3); self.wait(.4); self.remove(l)
        fill(self, cur, GRN)


class Three(Scene):
    def construct(self):
        ax, g = resp_axes(DOWN * .3, 10, 4.4)
        beat(self, FadeIn(g), t=.5, rt=.4)
        for (R, c, n), x in zip(CASES, (-3.6, 0, 3.6)):
            cur = ax.plot(lambda t, R=R: step_R(R, t), x_range=[0, 6, .02], color=c, stroke_width=6)
            beat(self, Create(cur), FadeIn(kr(n, 40, c).move_to(RIGHT * x + UP * 3.0)), t=1.3, rt=1.0)
        fill(self, g[0])


class Poles2(Scene):
    """분모의 극점 두 개가 전부 정함."""
    def construct(self):
        F = frac("1", ["LCs^2 + RCs + 1"], 64, INK).shift(LEFT * 3.4)
        beat(self, FadeIn(F), t=.9, rt=.4)
        b = SurroundingRectangle(F[2], color=YEL, buff=.12)
        beat(self, Create(b), FadeIn(kr("이차식 → 극점 2개", 34, YEL).next_to(F, DOWN, .5)), t=1.1, rt=.5)
        ax, gg = splane(RIGHT * 3.4, 4.4, 4.4, (-4, 1), (-3, 3))
        beat(self, FadeIn(gg), t=.5, rt=.4)
        k = ValueTracker(6)
        ps = always_redraw(lambda: VGroup(*[pole(ax, x, y, YEL) for x, y in poles_R(k.get_value())]))
        self.add(ps); self.play(k.animate.set_value(2), run_time=2.0)
        fill(self, b)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "전달함수", BLU), ("2", "극점 공식", PUR), ("3", "세 경우 풀이", GRN), ("4", "오버슈트", ORG)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.3).scale_to_fit_width(12.8).shift(UP * .3)
        for kk in cards:
            beat(self, FadeIn(kk, shift=UP * .3), t=1.1, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[3].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.0, rt=.8)
        fill(self, cards[3], ORG)


# ================= STEP 1 전달함수 =================
class E1(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        D = rlc_step(UP * .3, 7.0, 3.0)
        beat(self, Create(D["g"]), Create(D["src"]), FadeIn(D["labs"][3]), t=1.0, rt=.6)
        beat(self, Create(D["R"]), Create(D["L"]), FadeIn(D["labs"][0]), FadeIn(D["labs"][1]), t=1.1, rt=.6)
        beat(self, Create(D["C"]), FadeIn(D["labs"][2]), t=.8, rt=.5)
        b = SurroundingRectangle(D["C"], color=YEL, buff=.25)
        beat(self, Create(b), FadeIn(kr("출력 = 커패시터 전압", 34, YEL).next_to(D["g"], DOWN, .5)), t=1.0, rt=.5)
        fill(self, b)


class E2(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        D = rlc_step(UP * .5, 7.0, 3.0, sdom=True)
        self.add(D["g"], D["src"], D["R"], D["L"], D["C"], D["labs"][0], D["labs"][3])
        beat(self, Indicate(D["labs"][0], color=BLU), t=.8, rt=.6)
        beat(self, FadeIn(D["labs"][1], shift=DOWN * .2), t=1.0, rt=.5)
        beat(self, FadeIn(D["labs"][2], shift=LEFT * .2), t=1.0, rt=.5)
        t = kr("s-영역", 44, YEL).to_edge(DOWN, buff=.6)
        beat(self, FadeIn(t), t=.8, rt=.4)
        fill(self, VGroup(D["labs"][1], D["labs"][2]))


class E3(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        e = tex(r"V_C = \frac{\frac{1}{sC}}{R + sL + \frac{1}{sC}} \cdot \frac{1}{s}", 70)
        beat(self, Write(e), t=1.5, rt=1.1)
        b = Brace(e[0][9:21], DOWN, color=MUTE)
        beat(self, GrowFromCenter(b), FadeIn(kr("세 임피던스의 합", 34, MUTE).next_to(b, DOWN, .2)), t=1.1, rt=.5)
        h = kr("전압 분배", 40, YEL).to_edge(UP, buff=.8)
        beat(self, FadeIn(h), t=.7, rt=.3)
        fill(self, e)


class E4(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        a = tex(r"\frac{\frac{1}{sC}}{R + sL + \frac{1}{sC}}", 60, MUTE).shift(UP * 1.7)
        beat(self, FadeIn(a), t=.8, rt=.4)
        m = kr("× sC / sC", 32, MUTE).next_to(a, RIGHT, .5)
        beat(self, FadeIn(m), t=.8, rt=.3)
        r = tex(r"= \frac{1}{LCs^2 + RCs + 1}", 84, YEL).shift(DOWN * .9)
        beat(self, TransformFromCopy(a, r), t=1.5, rt=1.0)
        fill(self, r)


class E5(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        h = tex(r"H(s) = \frac{V_{out}(s)}{V_{in}(s)}", 76, YEL).shift(UP * 1.2)
        beat(self, Write(h), t=1.2, rt=.8)
        b = boxio("회로", 2.4, 1.3).shift(DOWN * 1.6)
        i = Arrow(LEFT * 3.4 + DOWN * 1.6, LEFT * 1.2 + DOWN * 1.6, buff=0, color=BLU); o = Arrow(RIGHT * 1.2 + DOWN * 1.6, RIGHT * 3.4 + DOWN * 1.6, buff=0, color=ORG)
        beat(self, FadeIn(b), GrowArrow(i), GrowArrow(o), t=1.0, rt=.5)
        beat(self, FadeIn(kr("전달함수", 44, YEL).next_to(h, UP, .4)), t=.8, rt=.3)
        fill(self, h)


class E6(Scene):
    def construct(self):
        self.add(step_tag(1, BLU))
        F = frac("1", ["LCs^2 + RCs + 1"], 64, INK).shift(LEFT * 3.4 + UP * .3)
        self.add(F)
        b = SurroundingRectangle(F[2][0][2:4], color=YEL, buff=.08)
        beat(self, Create(b), FadeIn(kr("s² → 이차식", 34, YEL).next_to(F, DOWN, .5)), t=1.0, rt=.5)
        ax, gg = splane(RIGHT * 3.4, 4.4, 4.4, (-4, 1), (-3, 3))
        beat(self, FadeIn(gg), t=.5, rt=.4)
        ps = VGroup(*[pole(ax, x, y, YEL) for x, y in poles_R(2)])
        beat(self, LaggedStart(*[Create(p) for p in ps], lag_ratio=.4), FadeIn(kr("극점 2개", 40, YEL).next_to(ax, UP, .1)), t=1.4, rt=.9)
        fill(self, ps)


# ================= STEP 2 극점 공식 =================
class F1(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        a = tex(r"LCs^2 + RCs + 1", 60, MUTE).shift(UP * 1.8)
        beat(self, FadeIn(a), t=.7, rt=.4)
        m = kr("÷ LC", 32, MUTE).next_to(a, RIGHT, .4)
        beat(self, FadeIn(m), t=.6, rt=.3)
        b = tex(r"s^2 + \frac{R}{L}s + \frac{1}{LC}", 80, YEL)
        beat(self, TransformFromCopy(a, b), t=1.3, rt=.9)
        q = kr("근의 공식", 40, PUR).shift(DOWN * 2.0)
        beat(self, FadeIn(q), t=.7, rt=.3)
        fill(self, b)


class F2(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        e = MathTex(r"s = ", r"-\alpha", r"\pm", r"\sqrt{\alpha^2 - \omega_0^2}", font_size=96, color=INK)
        e[1].set_color(ORG); e[3].set_color(BLU)
        beat(self, Write(e), t=1.6, rt=1.2)
        lab = kr("극점 공식", 44, YEL).next_to(e, UP, .7)
        beat(self, FadeIn(lab), t=.8, rt=.3)
        fill(self, e)


class F3(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        e = tex(r"\alpha = \frac{R}{2L}", 90, ORG).shift(LEFT * 3 + UP * .4)
        beat(self, Write(e), t=1.1, rt=.7)
        beat(self, FadeIn(kr("줄어드는 힘", 40, ORG).next_to(e, DOWN, .5)), t=.8, rt=.3)
        k = ValueTracker(.3)
        bar = always_redraw(lambda: Rectangle(width=.9, height=4 * k.get_value(), color=ORG, fill_color=ORG, fill_opacity=.6).move_to(RIGHT * 3.2 + DOWN * 1.6, aligned_edge=DOWN))
        rl = kr("R ↑ → α ↑", 36, MUTE).move_to(RIGHT * 3.2 + UP * 2.8)
        self.add(bar); beat(self, FadeIn(rl), t=.4, rt=.3)
        self.play(k.animate.set_value(.95 * 3.4 / 4), run_time=1.6)
        fill(self, e, ORG)


class F4(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        e = tex(r"\omega_0 = \frac{1}{\sqrt{LC}}", 90, BLU).shift(LEFT * 3 + UP * .4)
        beat(self, Write(e), t=1.1, rt=.7)
        beat(self, FadeIn(kr("진동하려는 빠르기", 38, BLU).next_to(e, DOWN, .5)), t=.8, rt=.3)
        w = sine(RIGHT * 3.2 + UP * .3, .7, 3, 4.6, BLU)
        beat(self, Create(w), FadeIn(kr("L, C로만 결정", 34, MUTE).next_to(w, DOWN, .6)), t=1.4, rt=1.0)
        fill(self, e, BLU)


class F5(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        r = tex(r"\sqrt{\alpha^2 - \omega_0^2}", 80, YEL).to_edge(UP, buff=.8)
        beat(self, FadeIn(r), t=.7, rt=.4)
        rows = [(r"\alpha > \omega_0", "양수 → 실수 극점 2개", BLU), (r"\alpha = \omega_0", "0 → 중근", PUR), (r"\alpha < \omega_0", "음수 → 복소 극점", GRN)]
        tb = VGroup(*[VGroup(tex(a, 56, c), kr(b, 36, c)).arrange(RIGHT, buff=.6) for a, b, c in rows]).arrange(DOWN, buff=.45, aligned_edge=LEFT).shift(DOWN * .6)
        for row in tb:
            beat(self, FadeIn(row, shift=RIGHT * .2), t=1.1, rt=.4)
        fill(self, tb)


class F6(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        a = tex(r"L = 1\,\mathrm{H},\quad C = 0.2\,\mathrm{F}", 64).shift(UP * 1.4)
        beat(self, FadeIn(a), t=.9, rt=.4)
        b = tex(r"\omega_0^2 = \frac{1}{LC} = 5", 84, BLU).shift(DOWN * .6)
        beat(self, Write(b), t=1.3, rt=.9)
        c = kr("예제", 34, MUTE).next_to(a, UP, .4)
        beat(self, FadeIn(c), t=.5, rt=.3)
        fill(self, b, BLU)


# ================= STEP 3 세 경우 =================
def case_head(R, c):
    return tex(f"R = {R}" + r"\,\Omega", 54, c).to_corner(UL, buff=.6)


class G1(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        h = case_head(6, BLU); beat(self, FadeIn(h), t=.6, rt=.3)
        a = tex(r"s^2 + 6s + 5", 84).shift(UP * .7)
        beat(self, Write(a), t=1.1, rt=.7)
        b = tex(r"= (s+1)(s+5)", 84, BLU).next_to(a, DOWN, .5)
        beat(self, Write(b), t=1.2, rt=.8)
        fill(self, b, BLU)


class G2(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        self.add(case_head(6, BLU))
        ax, gg = splane(LEFT * 1.6 + DOWN * .2, 7.0, 4.4, (-6, 1), (-3, 3))
        beat(self, FadeIn(gg), t=.5, rt=.4)
        ps = VGroup(pole(ax, -1, 0, BLU), pole(ax, -5, 0, BLU))
        beat(self, Create(ps), FadeIn(tex("-1", 36, BLU).next_to(ps[0], DOWN, .3)), FadeIn(tex("-5", 36, BLU).next_to(ps[1], DOWN, .3)), t=1.2, rt=.6)
        t = card(VGroup(kr("실수 극점 2개", 32, MUTE), kr("과감쇠", 48, BLU)).arrange(DOWN, buff=.2), BLU, .3).move_to(RIGHT * 4.6 + UP * .4)
        beat(self, FadeIn(t, shift=LEFT * .2), t=1.0, rt=.4)
        fill(self, t, BLU)


class G3(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        self.add(case_head(6, BLU))
        e = tex(r"v_C = 1 - 1.25e^{-t} + 0.25e^{-5t}", 56, BLU).to_edge(UP, buff=1.0)
        beat(self, Write(e), t=1.3, rt=.9)
        ax, g = resp_axes(DOWN * 1.1, 9.4, 3.6)
        cur = ax.plot(f_over, x_range=[0, 6, .02], color=BLU, stroke_width=7)
        beat(self, FadeIn(g), Create(cur), t=2.0, rt=1.7)
        beat(self, FadeIn(kr("진동 없이 천천히", 34, BLU).move_to(ax.c2p(4.4, .55))), t=.8, rt=.3)
        fill(self, cur, BLU)


class G4(Scene):
    """R=2√5: 두 극점이 −√5 에서 만남."""
    def construct(self):
        self.add(step_tag(3, GRN))
        h = tex(r"R = 2\sqrt{5} \approx 4.47\,\Omega", 50, PUR).to_corner(UL, buff=.6)
        beat(self, FadeIn(h), t=.6, rt=.3)
        ax, gg = splane(LEFT * 1.4 + DOWN * .3, 7.0, 4.4, (-6, 1), (-3, 3))
        self.add(gg)
        k = ValueTracker(6)
        ps = always_redraw(lambda: VGroup(*[pole(ax, x, y, PUR) for x, y in poles_R(k.get_value())]))
        self.add(ps)
        self.play(k.animate.set_value(RC_), run_time=1.8)
        d = Dot(ax.c2p(-W0, 0), .12, color=YEL)
        beat(self, FadeIn(d, scale=1.5), FadeIn(tex(r"-\sqrt{5}", 40, YEL).next_to(d, DOWN, .35)), t=.9, rt=.4)
        t = kr("두 극점이 만남", 40, PUR).move_to(RIGHT * 4.4 + UP * .8)
        beat(self, FadeIn(t), t=.8, rt=.3)
        fill(self, d)


class G5(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g = resp_axes(DOWN * .6, 10, 4.4)
        beat(self, FadeIn(g), t=.4, rt=.3)
        o = ax.plot(f_over, x_range=[0, 6, .02], color=BLU, stroke_width=4).set_stroke(opacity=.5)
        beat(self, Create(o), t=.8, rt=.6)
        c = ax.plot(f_crit, x_range=[0, 6, .02], color=PUR, stroke_width=8)
        beat(self, Create(c), t=1.4, rt=1.2)
        l = card(VGroup(kr("임계감쇠", 42, PUR), kr("출렁임 없이 가장 빨리", 30, MUTE)).arrange(DOWN, buff=.15), PUR, .25).move_to(ax.c2p(4.3, .45))
        beat(self, FadeIn(l), t=.8, rt=.4)
        fill(self, c, PUR)


class G6(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        self.add(case_head(2, GRN))
        a = tex(r"s^2 + 2s + 5", 64).move_to(LEFT * 3.2 + UP * .8)
        beat(self, FadeIn(a), FadeIn(kr("1편의 그 식", 30, MUTE).next_to(a, UP, .3)), t=1.0, rt=.4)
        r = tex(r"s = -1 \pm j2", 64, GRN).next_to(a, DOWN, .6)
        beat(self, Write(r), t=1.0, rt=.6)
        ax, gg = splane(RIGHT * 3.4 + DOWN * .2, 4.2, 4.6, (-3, 1), (-3, 3))
        beat(self, FadeIn(gg), Create(pole(ax, -1, 2, GRN)), Create(pole(ax, -1, -2, GRN)), t=1.2, rt=.7)
        fill(self, r, GRN)


class G7(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        self.add(case_head(2, GRN))
        t = kr("ω₀가 이김 → 부족감쇠", 40, GRN).to_edge(UP, buff=1.2)
        beat(self, FadeIn(t), t=.8, rt=.3)
        e = tex(r"v_C = 1 - e^{-t}\cos 2t - \tfrac{1}{2}e^{-t}\sin 2t", 58)
        beat(self, Write(e), t=1.6, rt=1.2)
        n = kr("완전제곱 (1편 STEP 3)", 32, MUTE).next_to(e, DOWN, .6)
        beat(self, FadeIn(n), t=.8, rt=.3)
        fill(self, e, GRN)


class G8(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g = resp_axes(DOWN * .4, 10, 4.8)
        beat(self, FadeIn(g), t=.4, rt=.3)
        c = ax.plot(f_under, x_range=[0, 6, .01], color=GRN, stroke_width=7)
        beat(self, Create(c), t=1.8, rt=1.6)
        pk = Dot(ax.c2p(PI / 2, f_under(PI / 2)), .12, color=YEL)
        beat(self, FadeIn(pk, scale=1.5), FadeIn(kr("1을 넘음", 34, YEL).next_to(pk, UR, .15)), t=.9, rt=.4)
        fill(self, c, GRN)


class G9(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g = resp_axes(DOWN * .9, 9.6, 3.8)
        self.add(g)
        cs = VGroup(*[ax.plot(lambda t, R=R: step_R(R, t), x_range=[0, 6, .02], color=c, stroke_width=5) for R, c, n in CASES])
        beat(self, LaggedStart(*[Create(c) for c in cs], lag_ratio=.3), t=1.6, rt=1.4)
        e = tex(r"\lim_{s\to 0} s\cdot\frac{1}{s}\cdot\frac{5}{s^2+Rs+5} = 1", 52, YEL).to_edge(UP, buff=.7)
        beat(self, Write(e), t=1.3, rt=.9)
        fill(self, g[1], YEL)


# ================= 중간 정리 · 극점 궤적 =================
def locus_scene(sc, R0, R1, rt=2.0, circle=False, extra=None):
    ax, gg = splane(LEFT * 2.6 + DOWN * .2, 7.4, 5.4, (-6.5, 1), (-3, 3))
    sc.add(gg)
    if circle:
        sc.add(Arc(radius=ax.c2p(W0, 0)[0] - ax.c2p(0, 0)[0], start_angle=PI / 2, angle=PI, arc_center=ax.c2p(0, 0), color=MUTE, stroke_width=2).set_stroke(opacity=.6))
    k = ValueTracker(R0)
    ps = always_redraw(lambda: VGroup(*[pole(ax, x, y, YEL) for x, y in poles_R(k.get_value())]))
    lab = always_redraw(lambda: tex(f"R = {k.get_value():.1f}" + r"\,\Omega", 46, YEL).move_to(RIGHT * 4.6 + UP * 2.4))
    sc.add(ps, lab)
    rax, rg = resp_axes(RIGHT * 4.6 + DOWN * .7, 4.0, 2.6, 6, 2.1)
    cur = always_redraw(lambda: rax.plot(lambda t: step_R(k.get_value(), t), x_range=[0, 6, .02], color=GRN, stroke_width=4))
    sc.add(rg, cur)
    sc.play(k.animate.set_value(R1), run_time=rt)
    return ax, k


class H1(Scene):
    def construct(self):
        self.add(kr("중간 정리", 36, MUTE).to_corner(UL, buff=.5))
        ax, k = locus_scene(self, 12, 9, 1.5)
        a = Arrow(ax.c2p(-.3, .6), ax.c2p(-1.3, .6), buff=0, color=MUTE); b = Arrow(ax.c2p(-6.2, .6), ax.c2p(-5.2, .6), buff=0, color=MUTE)
        beat(self, GrowArrow(a), GrowArrow(b), FadeIn(kr("R 줄이기", 34, YEL).move_to(ax.c2p(-3, 2.4))), t=1.0, rt=.5)
        self.play(k.animate.set_value(7), run_time=1.4)
        fill(self, VGroup(a, b))


class H2(Scene):
    def construct(self):
        self.add(kr("중간 정리", 36, MUTE).to_corner(UL, buff=.5))
        ax, k = locus_scene(self, 7, RC_, 2.6)
        d = Dot(ax.c2p(-W0, 0), .12, color=PUR)
        beat(self, FadeIn(d, scale=1.6), FadeIn(kr("만남", 40, PUR).next_to(d, UP, .4)), t=1.0, rt=.4)
        fill(self, d, PUR)


class H3(Scene):
    def construct(self):
        self.add(kr("중간 정리", 36, MUTE).to_corner(UL, buff=.5))
        ax, k = locus_scene(self, RC_, 1.2, 3.0, circle=True)
        r = kr("반지름 √5 원", 36, MUTE).move_to(ax.c2p(-4.4, 2.5))
        beat(self, FadeIn(r), t=.8, rt=.3)
        fill(self, r, MUTE)


class H4(Scene):
    def construct(self):
        self.add(kr("중간 정리", 36, MUTE).to_corner(UL, buff=.5))
        ax, k = locus_scene(self, 1.2, 0.0, 1.6, circle=True)
        ia = Line(ax.c2p(0, -3), ax.c2p(0, 3), color=RED, stroke_width=6)
        beat(self, Create(ia), FadeIn(tex(r"\pm j\sqrt{5}", 44, RED).move_to(ax.c2p(-1.1, 2.6))), t=1.0, rt=.6)
        t = kr("영원히 진동 = LC 회로", 34, RED).move_to(RIGHT * 4.6 + DOWN * 2.6)
        beat(self, FadeIn(t), t=.9, rt=.3)
        fill(self, t, RED)


# ================= STEP 4 오버슈트 =================
class J1(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = resp_axes(DOWN * .5, 10, 4.6)
        c = ax.plot(f_under, x_range=[0, 6, .01], color=GRN, stroke_width=6)
        beat(self, FadeIn(g), Create(c), t=1.6, rt=1.3)
        q = kr("얼마나 넘칠까?", 46, YEL).to_edge(UP, buff=.6)
        beat(self, FadeIn(q), t=.8, rt=.3)
        fill(self, q)


class J2(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = resp_axes(DOWN * .9, 10, 4.0)
        self.add(g, ax.plot(f_under, x_range=[0, 6, .01], color=GRN, stroke_width=6))
        e = tex(r"t_p = \frac{\pi}{\omega_d} = \frac{\pi}{2} \approx 1.57\,\mathrm{s}", 56, ORG).to_edge(UP, buff=.6)
        beat(self, Write(e), t=1.3, rt=.9)
        pk = ax.c2p(PI / 2, f_under(PI / 2))
        dl = DashedLine(ax.c2p(PI / 2, 0), pk, color=ORG)
        beat(self, Create(dl), FadeIn(Dot(pk, .12, color=ORG), scale=1.5), FadeIn(tex("1.57", 36, ORG).next_to(ax.c2p(PI / 2, 0), DOWN, .2)), t=1.2, rt=.6)
        fill(self, e, ORG)


class J3(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = resp_axes(DOWN * .9, 10, 4.0)
        self.add(g, ax.plot(f_under, x_range=[0, 6, .01], color=GRN, stroke_width=6))
        e = tex(r"e^{-\alpha\pi/\omega_d} = e^{-\pi/2} \approx 0.21", 58, YEL).to_edge(UP, buff=.6)
        beat(self, Write(e), t=1.3, rt=.9)
        pk = ax.c2p(PI / 2, f_under(PI / 2)); one = ax.c2p(PI / 2, 1)
        br = DoubleArrow(one, pk, buff=0, color=YEL, tip_length=.15)
        beat(self, GrowFromCenter(br), FadeIn(kr("21% 넘침", 40, YEL).move_to(ax.c2p(3.0, 1.33))), t=1.1, rt=.5)
        fill(self, br)


class J4(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        z = tex(r"\zeta = \frac{\alpha}{\omega_0}", 84, YEL).shift(UP * 1.8)
        beat(self, Write(z), FadeIn(kr("감쇠비", 38, YEL).next_to(z, LEFT, .5)), t=1.1, rt=.7)
        rows = [(r"\zeta > 1", "과감쇠", BLU), (r"\zeta = 1", "임계감쇠", PUR), (r"\zeta < 1", "부족감쇠", GRN)]
        tb = VGroup(*[card(VGroup(tex(a, 50, c), kr(b, 36, c)).arrange(DOWN, buff=.2), c, .28) for a, b, c in rows]).arrange(RIGHT, buff=.5).shift(DOWN * 1.2)
        for r in tb:
            beat(self, FadeIn(r, shift=UP * .2), t=.9, rt=.4)
        fill(self, tb)


# ================= 정리 =================
class O1(Scene):
    def construct(self):
        h = tex(r"H(s) = \frac{1}{LCs^2 + RCs + 1}", 80, YEL)
        beat(self, Write(h), t=1.4, rt=1.0)
        fill(self, h)


class O2(Scene):
    def construct(self):
        items = [("실수 2개", "과감쇠", BLU, 0), ("겹침", "임계감쇠", PUR, 1), ("복소수", "부족감쇠", GRN, 2)]
        cs = VGroup()
        for a, b, c, i in items:
            ax = Axes(x_range=[0, 6, 1], y_range=[0, 1.4, .5], x_length=3.2, y_length=1.6, tips=False, axis_config={"color": MUTE, "stroke_width": 2, "include_ticks": False})
            cur = ax.plot(lambda t, R=CASES[i][0]: step_R(R, t), x_range=[0, 6, .02], color=c, stroke_width=5)
            cs.add(card(VGroup(kr(a, 30, MUTE), kr(b, 40, c), VGroup(ax, cur)).arrange(DOWN, buff=.25), c, .3))
        cs.arrange(RIGHT, buff=.4).scale_to_fit_width(min(cs.width, 12.6))
        for c in cs:
            beat(self, FadeIn(c, shift=UP * .3), t=1.2, rt=.4)
        fill(self, cs)


class O3(Scene):
    def construct(self):
        ax, k = locus_scene(self, 9, .4, 3.2, circle=True)
        fill(self, ax)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("RLC · 극점과 응답 같이 보기", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55).shift(LEFT * 3.0)
        beat(self, FadeIn(t[0]), FadeIn(t[1][0]), t=.8, rt=.3)
        rax, rg = resp_axes(RIGHT * 3.9, 4.2, 3.0, 6, 1.5)
        k = ValueTracker(7)
        cur = always_redraw(lambda: rax.plot(lambda tt: step_R(k.get_value(), tt), x_range=[0, 6, .02], color=GRN, stroke_width=5))
        self.add(rg, cur)
        for m in t[1][1:]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.0, rt=.4)
        self.play(k.animate.set_value(1.5), run_time=2.2)
        fill(self, t, YEL)


class Next(Scene):
    def construct(self):
        lab = kr("마지막 편 · 전달함수와 컨볼루션", 40, YEL).to_edge(UP, buff=.7)
        beat(self, FadeIn(lab), t=.9, rt=.4)
        a = tex(r"Y(s) = H(s)\,X(s)", 70, BLU).shift(UP * .6)
        beat(self, Write(a), t=1.1, rt=.7)
        b = tex(r"y(t) = h(t) * x(t)", 70, GRN).shift(DOWN * 1.2)
        ar = Arrow(a.get_bottom(), b.get_top(), buff=.15, color=MUTE)
        beat(self, GrowArrow(ar), FadeIn(b), FadeIn(kr("곱셈 = ?", 36, YEL).next_to(ar, RIGHT, .3)), t=1.2, rt=.6)
        fill(self, b, GRN)


# ================= 쇼츠 전용 =================
class AQ(Scene):
    def construct(self):
        D = rlc_step(UP * 1.4, 6.0, 2.2)
        self.add(D["g"], D["src"], D["R"], D["L"], D["C"], D["labs"])
        k = ValueTracker(7)
        ax, g = resp_axes(DOWN * 1.9, 8, 2.6)
        cur = always_redraw(lambda: ax.plot(lambda t: step_R(k.get_value(), t), x_range=[0, 6, .02], color=YEL, stroke_width=6))
        self.add(g, cur)
        r = SurroundingRectangle(D["R"], color=YEL, buff=.2)
        beat(self, Create(r), t=.5, rt=.4)
        self.play(k.animate.set_value(RC_), run_time=1.0); self.play(k.animate.set_value(1.6), run_time=1.0)
        fill(self, r)


class BQ(Scene):
    def construct(self):
        e = MathTex(r"s = ", r"-\alpha", r"\pm", r"\sqrt{\alpha^2 - \omega_0^2}", font_size=90, color=INK).shift(UP * .5)
        e[3].set_color(YEL)
        beat(self, FadeIn(e), t=.8, rt=.4)
        q = kr("출렁일까?", 56, YEL).shift(DOWN * 1.8)
        beat(self, FadeIn(q, scale=1.3), t=.8, rt=.4)
        fill(self, e[3])


class CQ(Scene):
    def construct(self):
        ax, g = resp_axes(DOWN * .3, 10, 4.6)
        c = ax.plot(f_under, x_range=[0, 6, .01], color=GRN, stroke_width=7)
        beat(self, FadeIn(g), Create(c), t=1.4, rt=1.2)
        t = kr("+21%", 70, YEL).move_to(ax.c2p(PI / 2 + .3, 1.32))
        beat(self, FadeIn(t, scale=1.4), t=.8, rt=.4)
        fill(self, t)


class DQ(Scene):
    def construct(self):
        D = rlc_step(UP * .6, 7.0, 2.6)
        self.add(D["g"], D["src"], D["R"], D["L"], D["C"], D["labs"])
        z = tex(r"R = 0\;?", 80, RED).shift(DOWN * 2.0)
        beat(self, Indicate(D["R"], color=RED, scale_factor=1.0), FadeIn(z), t=1.0, rt=.6)
        fill(self, z, RED)


class DOsc(Scene):
    def construct(self):
        ax, g = taxes(DOWN * .4, 10.4, 4.4, 10, -1.2, 1.2, "v(t)")
        c = ax.plot(lambda t: np.cos(W0 * t), x_range=[0, 10, .01], color=RED, stroke_width=6)
        beat(self, FadeIn(g), Create(c), t=2.0, rt=1.8)
        beat(self, FadeIn(kr("줄지 않는 진동", 40, RED).to_edge(UP, buff=.7)), t=.8, rt=.3)
        fill(self, c, RED)


class DLC(Scene):
    def construct(self):
        l = coil((-3, 1.2), (-3, -1.2), GRN); c = capacitor((3, 1.2), (3, -1.2), ORG)[0]
        loop = VGroup(wire((-3, 1.2), (3, 1.2)), wire((-3, -1.2), (3, -1.2)))
        beat(self, Create(loop), FadeIn(l), FadeIn(c), FadeIn(tex("L", 48, GRN).next_to(l, LEFT, .3)), FadeIn(tex("C", 48, ORG).next_to(c, RIGHT, .3)), t=1.0, rt=.6)
        e = Dot(color=YEL, radius=.2).move_to((-3, 0, 0))
        self.add(e)
        for _ in range(2):
            self.play(e.animate.move_to((3, 0, 0)), run_time=.8, rate_func=there_and_back_with_pause if False else smooth)
            self.play(e.animate.move_to((-3, 0, 0)), run_time=.8)
        beat(self, FadeIn(kr("에너지가 오가는 LC 발진", 40, YEL).to_edge(DOWN, buff=.8)), t=.6, rt=.3)
        fill(self, e)


class EQ(Scene):
    def construct(self):
        ax, g = resp_axes(DOWN * .3, 10, 4.6)
        beat(self, FadeIn(g), t=.4, rt=.3)
        cs = VGroup(*[ax.plot(lambda t, R=R: step_R(R, t), x_range=[0, 6, .02], color=c, stroke_width=5) for R, c, n in CASES])
        beat(self, Create(cs[0]), Create(cs[2]), t=1.0, rt=.8)
        beat(self, Create(cs[1].set_stroke(width=9)), FadeIn(kr("가장 빨리?", 44, PUR).to_edge(UP, buff=.6)), t=1.0, rt=.8)
        fill(self, cs[1], PUR)


class EOver(Scene):
    def construct(self):
        ax, gg = splane(LEFT * 2.6 + DOWN * .2, 7.0, 4.4, (-12, 1), (-3, 3))
        self.add(gg)
        ps = VGroup(*[pole(ax, x, y, BLU) for x, y in poles_R(12)])
        beat(self, Create(ps), t=.8, rt=.5)
        d = SurroundingRectangle(ps[0], color=YEL, buff=.15)
        beat(self, Create(d), FadeIn(kr("원점 근처 = 느림", 34, YEL).next_to(d, UP, .3)), t=1.0, rt=.5)
        rax, rg = resp_axes(RIGHT * 4.4 + DOWN * .3, 4.0, 2.8)
        beat(self, FadeIn(rg), Create(rax.plot(lambda t: step_R(12, t), x_range=[0, 6, .02], color=BLU, stroke_width=5)), t=1.2, rt=1.0)
        fill(self, d)


class ECrit(Scene):
    def construct(self):
        e = tex(r"R = 2\sqrt{\frac{L}{C}}", 90, PUR).shift(UP * .9)
        beat(self, Write(e), t=1.2, rt=.8)
        r = tex(r"= 2\sqrt{5} \approx 4.47\,\Omega", 70, YEL).shift(DOWN * 1.2)
        beat(self, Write(r), t=1.0, rt=.6)
        fill(self, r)
