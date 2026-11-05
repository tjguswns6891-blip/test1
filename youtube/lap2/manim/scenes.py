# 라플라스 심화 2편(초기 조건이 있는 s-영역 회로) 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나. 1편(lap1/manim/scenes.py)과 같은 도우미·규칙(2~4초마다 새 요소, dur.json 길이 맞춤 fill).
# 검산은 ../lines.py 맨 위 참고.
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


# ---------- 2편 회로 도우미 ----------
def vsrc(p, c=ORG, r=.42, plus_up=True):
    """전압원(원 + 극성). plus_up: 위쪽이 +."""
    p = P3(p)
    a, b = ("+", "-") if plus_up else ("-", "+")
    return VGroup(Circle(r, color=c, stroke_width=5).move_to(p), tex(a, 34, c).move_to(p + UP * r * .45), tex(b, 34, c).move_to(p + DOWN * r * .45))


def isrc(p, c=ORG, r=.42, up=True):
    p = P3(p)
    d = UP if up else DOWN
    return VGroup(Circle(r, color=c, stroke_width=5).move_to(p), Arrow(p - d * r * .7, p + d * r * .7, buff=0, color=c, stroke_width=5, tip_length=.16))


def branch_series(x, yt, yb, top, bot, gap=.0):
    """세로 가지: 위 소자(top 함수: (a,b)→mob) + 아래 전원(bot mob, 가운데 배치)."""
    ym = (yt + yb) / 2
    e = top((x, yt), (x, ym + .15))
    bot.move_to((x, (ym - .15 + yb) / 2 + .0, 0))
    w1 = wire((x, bot.get_top()[1]), (x, ym + .15)); w2 = wire((x, bot.get_bottom()[1]), (x, yb))
    return VGroup(e, w1, bot, w2)


def L_series(o=ORIGIN, H=3.6, c=GRN, sc=ORG):
    o = P3(o); yt, yb = o[1] + H / 2, o[1] - H / 2
    s = vsrc((o[0], 0), sc, plus_up=False)
    g = branch_series(o[0], yt, yb, lambda a, b: coil(a, b, c), s)
    t1, t2 = term((o[0], yt)), term((o[0], yb))
    labs = VGroup(tex("sL", 48, c).next_to(g[0], RIGHT, .35), tex(r"L\,i(0)", 44, sc).next_to(s, RIGHT, .3))
    return VGroup(g, t1, t2), labs, s


def C_series(o=ORIGIN, H=3.6, c=BLU, sc=ORG, lab=r"\frac{v(0)}{s}"):
    o = P3(o); yt, yb = o[1] + H / 2, o[1] - H / 2
    s = vsrc((o[0], 0), sc, plus_up=True)
    g = branch_series(o[0], yt, yb, lambda a, b: capacitor(a, b, c)[0], s)
    t1, t2 = term((o[0], yt)), term((o[0], yb))
    labs = VGroup(tex(r"\frac{1}{sC}", 48, c).next_to(g[0], RIGHT, .35), tex(lab, 44, sc).next_to(s, RIGHT, .3))
    return VGroup(g, t1, t2), labs, s


def par_model(o=ORIGIN, H=3.2, kind="L", c=GRN, sc=ORG):
    """소자 ∥ 전류원. kind L: 화살표 아래(i(0)/s), C: 위(Cv(0))."""
    o = P3(o); yt, yb = o[1] + H / 2, o[1] - H / 2; xl, xr = o[0] - .9, o[0] + .9
    e = coil((xl, yt - .3), (xl, yb + .3), c) if kind == "L" else capacitor((xl, yt - .3), (xl, yb + .3), c)[0]
    s = isrc((xr, o[1]), sc, up=(kind != "L"))
    g = VGroup(wire((xl, yt), (xr, yt)), wire((xl, yb), (xr, yb)), wire((xl, yt), (xl, yt - .3)), wire((xl, yb), (xl, yb + .3)), e,
               wire((xr, yt), (xr, o[1] + .42)), wire((xr, yb), (xr, o[1] - .42)), s,
               wire((o[0], yt), (o[0], yt + .5)), wire((o[0], yb), (o[0], yb - .5)), term((o[0], yt + .5)), term((o[0], yb - .5)))
    labs = VGroup(tex("sL" if kind == "L" else r"\frac{1}{sC}", 46, c).next_to(e, LEFT, .3),
                  tex(r"\frac{i(0)}{s}" if kind == "L" else r"C\,v(0)", 42, sc).next_to(s, RIGHT, .3))
    return g, labs, s


def switch_circuit(o=ORIGIN, pos="A"):
    """t<0: 스위치 A(4V), t=0 에 B(10V + R) 로. C 는 가운데 세로."""
    o = P3(o); x0 = o[0]; yt, yb = o[1] + 1.4, o[1] - 1.8
    C = capacitor((x0, yt - .2), (x0, yb), BLU)[0]
    piv = P3((x0, yt - .2)) + UP * 0
    A, B = P3((x0 - 1.0, yt + .5)), P3((x0 + 1.0, yt + .5))
    b4 = battery((x0 - 3.4, o[1] - .2), ORG, 1.0); b10 = battery((x0 + 3.6, o[1] - .2), RED, 1.0)
    left = VGroup(wire(A, (x0 - 3.4, yt + .5)), wire((x0 - 3.4, yt + .5), (x0 - 3.4, o[1] - .02)), wire((x0 - 3.4, o[1] - .38), (x0 - 3.4, yb)))
    R = resistor(B, (x0 + 3.6, yt + .5), INK)
    right = VGroup(R, wire((x0 + 3.6, yt + .5), (x0 + 3.6, o[1] - .02)), wire((x0 + 3.6, o[1] - .38), (x0 + 3.6, yb)))
    bot = wire((x0 - 3.4, yb), (x0 + 3.6, yb))
    blade = Line(piv, A if pos == "A" else B, color=YEL, stroke_width=7)
    dots = VGroup(Dot(A, .08, color=INK), Dot(B, .08, color=INK), Dot(piv, .1, color=YEL))
    labs = VGroup(tex("4V", 44, ORG).next_to(b4, LEFT, .3), tex("10V", 44, RED).next_to(b10, RIGHT, .3),
                  tex(r"1\,k\Omega", 38, INK).next_to(R, UP, .25), tex("C", 44, BLU).next_to(C, RIGHT, .35),
                  tex("A", 32, MUTE).next_to(A, UP, .12), tex("B", 32, MUTE).next_to(B, UP, .12))
    return dict(g=VGroup(C, left, right, bot, b4, b10, dots), blade=blade, labs=labs, C=C, piv=piv, A=A, B=B, b4=b4, b10=b10, R=R, left=left, right=right)


def sdom_circuit(o=ORIGIN):
    """t>0 s-영역: 10/s — 1kΩ — [1/sC + 4/s]."""
    o = P3(o); xl, xr = o[0] - 3.4, o[0] + 2.0; yt, yb = o[1] + 1.6, o[1] - 1.8
    s10 = vsrc((xl, o[1] - .1), RED)
    R = resistor((xl, yt), (xr, yt), INK)
    cs, cl, c4 = C_series((xr, (yt + yb) / 2), yt - yb, BLU, ORG, r"\frac{4}{s}")
    g = VGroup(wire((xl, yt), (xl, s10.get_top()[1])), wire((xl, s10.get_bottom()[1]), (xl, yb)), wire((xl, yb), (xr, yb)))
    labs = VGroup(tex(r"\frac{10}{s}", 46, RED).next_to(s10, LEFT, .3), tex(r"1\,k\Omega", 40).next_to(R, UP, .25))
    return dict(src=s10, R=R, cap=cs[0][0], csrc=c4, cw=VGroup(cs[0][1], cs[0][3]), g=g, labs=labs, clabs=cl)


def f_vc(t): return 10 - 6 * np.exp(-t)


# ================= 인트로 =================
class Hook(Scene):
    """4V 남은 C, 스위치가 10V 로 → v_C 4→10 (결과 먼저)."""
    def construct(self):
        D = switch_circuit(LEFT * 2.0 + UP * .2)
        VGroup(D["g"], D["labs"], D["blade"]).scale(.8, about_point=LEFT * 2.0 + UP * .2).shift(LEFT * .9)
        D["piv"], D["B"] = D["g"][6][2].get_center(), D["g"][6][1].get_center()
        self.add(D["g"], D["labs"], D["blade"])
        beat(self, Indicate(D["C"], color=ORG, scale_factor=1.0), FadeIn(kr("C에 4V 남아 있음", 32, ORG).next_to(D["g"], DOWN, .3)), t=1.0, rt=.6)
        nb = Line(D["piv"], D["B"], color=YEL, stroke_width=7)
        beat(self, Transform(D["blade"], nb), FadeIn(tex("t=0", 40, YEL).next_to(D["piv"], DOWN + RIGHT, .1)), t=1.0, rt=.6)
        ax, g = taxes(RIGHT * 4.7 + DOWN * .1, 3.4, 3.0, 5, 0, 11, r"v_C")
        cur = ax.plot(f_vc, x_range=[0, 5, .02], color=GRN, stroke_width=6)
        beat(self, FadeIn(g), Create(cur), t=1.4, rt=1.2)
        q = kr("어떻게 풀까?", 40, YEL).to_edge(UP, buff=.4)
        beat(self, FadeIn(q), t=.8, rt=.4)
        fill(self, cur, GRN)


class DiffEq(Scene):
    def construct(self):
        e = tex(r"RC\,\frac{dv}{dt} + v = 10", 72).shift(UP * 1.6)
        beat(self, Write(e), t=1.2, rt=.8)
        s = tex(r"v = 10 + A e^{-t/RC}", 64, MUTE).next_to(e, DOWN, .6)
        beat(self, FadeIn(s), t=1.0, rt=.4)
        a = tex(r"v(0) = 4 \;\Rightarrow\; A = ?", 60, ORG).next_to(s, DOWN, .6)
        beat(self, FadeIn(a), FadeIn(kr("따로", 40, ORG).next_to(a, LEFT, .4)), t=1.2, rt=.5)
        fill(self, a, ORG)


class Src(Scene):
    """초기 조건 → 전원 하나."""
    def construct(self):
        l = card(VGroup(kr("초기 조건", 36, MUTE), tex("v(0) = 4", 56, ORG)).arrange(DOWN, buff=.3), "#2a2e37", .4).shift(LEFT * 3.6)
        beat(self, FadeIn(l), t=.9, rt=.4)
        a = Arrow(LEFT * 1.4, RIGHT * 1.0, buff=0, color=YEL, stroke_width=7)
        beat(self, GrowArrow(a), t=.7, rt=.4)
        s = vsrc(RIGHT * 3.2, ORG, .7)
        beat(self, Create(s), FadeIn(tex(r"\frac{4}{s}", 56, ORG).next_to(s, RIGHT, .35)), t=1.1, rt=.6)
        t = kr("전원 하나로 그려 넣기", 40, YEL).to_edge(DOWN, buff=.8)
        beat(self, FadeIn(t), t=.9, rt=.4)
        fill(self, s, ORG)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "인덕터 모델", GRN), ("2", "커패시터 모델", BLU), ("3", "초기값", ORG), ("4", "s-영역 풀이", PUR)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.3).scale_to_fit_width(12.8).shift(UP * .3)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.1, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[3].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.0, rt=.8)
        fill(self, cards[3], PUR)


# ================= STEP 1 인덕터 =================
class L1(Scene):
    def construct(self):
        self.add(step_tag(1, GRN))
        l = coil((-4, 1.6), (-4, -1.6), GRN)
        beat(self, Create(l), FadeIn(tex("L", 50, GRN).next_to(l, LEFT, .3)), t=.9, rt=.6)
        e = tex(r"v = L\,\frac{di}{dt}", 84).shift(RIGHT * 1.4)
        beat(self, Write(e), t=1.3, rt=.9)
        b = SurroundingRectangle(e[0][3:], color=YEL, buff=.12)
        beat(self, Create(b), FadeIn(kr("미분", 40, YEL).next_to(b, DOWN, .3)), t=1.0, rt=.5)
        fill(self, b)


class L2(Scene):
    def construct(self):
        self.add(step_tag(1, GRN))
        h = kr("지난 편 변환표", 34, MUTE).to_edge(UP, buff=.8)
        beat(self, FadeIn(h), t=.6, rt=.3)
        e = tex(r"\frac{df}{dt} \;\to\; s\,F(s) - f(0)", 80, YEL)
        beat(self, Write(e), t=1.4, rt=1.0)
        a = Brace(e[0][6:11], DOWN, color=BLU); b = Brace(e[0][11:], DOWN, color=ORG)
        beat(self, GrowFromCenter(a), FadeIn(kr("s 곱하기", 32, BLU).next_to(a, DOWN, .15)), t=.9, rt=.4)
        beat(self, GrowFromCenter(b), FadeIn(kr("초기값 빼기", 32, ORG).next_to(b, DOWN, .15)), t=.9, rt=.4)
        fill(self, e)


class L3(Scene):
    def construct(self):
        self.add(step_tag(1, GRN))
        a = tex(r"v = L\,\frac{di}{dt}", 64, MUTE).shift(UP * 1.8)
        beat(self, FadeIn(a), t=.7, rt=.4)
        e = MathTex(r"V(s) =", r"sL\,I(s)", r"-", r"L\,i(0)", font_size=80, color=INK)
        e[1].set_color(GRN); e[3].set_color(ORG)
        beat(self, TransformFromCopy(a, e[:2]), t=1.2, rt=.9)
        beat(self, FadeIn(e[2:], shift=LEFT * .2), t=1.0, rt=.5)
        b = SurroundingRectangle(e[3], color=ORG, buff=.12)
        beat(self, Create(b), FadeIn(kr("초기값이 식 안에", 34, ORG).next_to(b, DOWN, .3)), t=1.0, rt=.5)
        fill(self, b, ORG)


class L4(Scene):
    """직렬 모델: sL + 전압원 L i(0)."""
    def construct(self):
        self.add(step_tag(1, GRN))
        e = tex(r"V = sL\,I - L\,i(0)", 50, MUTE).to_edge(UP, buff=.7).shift(LEFT * 2.5)
        self.add(e)
        g, labs, s = L_series(LEFT * .4 + DOWN * .4, 4.4)
        beat(self, Create(g[0][0]), FadeIn(g[1]), FadeIn(labs[0]), t=1.0, rt=.6)
        beat(self, Create(g[0][1:]), FadeIn(g[2]), FadeIn(labs[1]), t=1.2, rt=.7)
        t = kr("직렬", 50, YEL).move_to(RIGHT * 4.2 + DOWN * .4)
        beat(self, FadeIn(t), FadeIn(kr("임피던스 + 전압원", 30, MUTE).next_to(t, DOWN, .25)), t=1.0, rt=.4)
        fill(self, s, ORG)


class L5(Scene):
    """병렬 모델: sL ∥ 전류원 i(0)/s."""
    def construct(self):
        self.add(step_tag(1, GRN))
        e = tex(r"I = \frac{V}{sL} + \frac{i(0)}{s}", 50, MUTE).to_edge(UP, buff=.6).shift(LEFT * 2.5)
        beat(self, Write(e), t=1.0, rt=.6)
        g, labs, s = par_model(LEFT * .2 + DOWN * .5, 3.4, "L", GRN)
        beat(self, Create(g[:5]), FadeIn(labs[0]), FadeIn(g[8:]), t=1.0, rt=.6)
        beat(self, Create(g[5:8]), FadeIn(labs[1]), t=1.1, rt=.6)
        t = kr("병렬", 50, YEL).move_to(RIGHT * 4.4 + DOWN * .4)
        beat(self, FadeIn(t), FadeIn(kr("임피던스 ∥ 전류원", 30, MUTE).next_to(t, DOWN, .25)), t=1.0, rt=.4)
        fill(self, s, ORG)


class L6(Scene):
    def construct(self):
        self.add(step_tag(1, GRN))
        g1, l1, _ = L_series(LEFT * 4.6 + DOWN * .2, 3.4); g2, l2, _ = par_model(RIGHT * 2.2 + DOWN * .2, 2.8, "L", GRN)
        beat(self, FadeIn(g1), FadeIn(l1), t=.8, rt=.4)
        eq = tex("=", 80, YEL).move_to(LEFT * 1.4 + DOWN * .2)
        beat(self, FadeIn(eq), FadeIn(g2), FadeIn(l2), t=1.0, rt=.4)
        a = card(kr("메시 · KVL → 직렬", 32, GRN), GRN, .22).next_to(g1, UP, .3).shift(RIGHT * .4)
        b = card(kr("노드 · KCL → 병렬", 32, BLU), BLU, .22).next_to(g2, UP, .3)
        beat(self, FadeIn(a, shift=DOWN * .2), t=1.1, rt=.4)
        beat(self, FadeIn(b, shift=DOWN * .2), t=1.1, rt=.4)
        fill(self, VGroup(a, b))


# ================= STEP 2 커패시터 =================
class K1(Scene):
    def construct(self):
        self.add(step_tag(2, BLU))
        c = capacitor((-4, 1.4), (-4, -1.4), BLU)[0]
        beat(self, Create(c), FadeIn(tex("C", 50, BLU).next_to(c, LEFT, .4)), t=.9, rt=.6)
        e = tex(r"i = C\,\frac{dv}{dt}", 84).shift(RIGHT * 1.4)
        beat(self, Write(e), t=1.3, rt=.9)
        x = kr("인덕터와 반대: 전류 = 전압의 미분", 32, MUTE).next_to(e, DOWN, .6)
        beat(self, FadeIn(x), t=1.0, rt=.4)
        fill(self, e, BLU)


class K2(Scene):
    def construct(self):
        self.add(step_tag(2, BLU))
        a = tex(r"i = C\,\frac{dv}{dt}", 64, MUTE).shift(UP * 1.8)
        beat(self, FadeIn(a), t=.7, rt=.4)
        e = MathTex(r"I(s) =", r"sC\,V(s)", r"-", r"C\,v(0)", font_size=80, color=INK)
        e[1].set_color(BLU); e[3].set_color(ORG)
        beat(self, TransformFromCopy(a, e[:2]), t=1.2, rt=.9)
        beat(self, FadeIn(e[2:], shift=LEFT * .2), t=1.0, rt=.5)
        fill(self, e[3], ORG)


class K3(Scene):
    """직렬: 1/sC + 전압원 v(0)/s."""
    def construct(self):
        self.add(step_tag(2, BLU))
        e = tex(r"V = \frac{I}{sC} + \frac{v(0)}{s}", 52, MUTE).to_edge(UP, buff=.6).shift(LEFT * 2.6)
        beat(self, Write(e), t=1.0, rt=.6)
        g, labs, s = C_series(LEFT * .4 + DOWN * .5, 4.2)
        beat(self, Create(g[0][0]), FadeIn(g[1]), FadeIn(labs[0]), t=1.0, rt=.6)
        beat(self, Create(g[0][1:]), FadeIn(g[2]), FadeIn(labs[1]), t=1.1, rt=.6)
        fill(self, s, ORG)


class K4(Scene):
    """v(0) 가 아니라 v(0)/s: 계단처럼 계속 남는 전압."""
    def construct(self):
        self.add(step_tag(2, BLU))
        w = tex(r"v(0)", 70, RED).shift(LEFT * 3.4 + UP * 1.6); x = Cross(w, stroke_color=RED, stroke_width=7)
        r = tex(r"\frac{v(0)}{s}", 80, GRN).shift(RIGHT * 3.0 + UP * 1.6)
        beat(self, FadeIn(w), Create(x), t=1.0, rt=.5)
        beat(self, FadeIn(r, shift=LEFT * .2), t=1.0, rt=.5)
        ax, g = taxes(DOWN * 1.4, 8, 2.4, 5, 0, 1.3, r"")
        st = VMobject(color=ORG, stroke_width=7).set_points_as_corners([ax.c2p(0, 0), ax.c2p(0, 1), ax.c2p(5, 1)])
        beat(self, FadeIn(g), Create(st), FadeIn(kr("계속 남는 전압 = 계단", 32, ORG).move_to(ax.c2p(2.8, 1.25))), t=1.4, rt=1.0)
        f = tex(r"\frac{1}{s}", 52, ORG).next_to(ax.c2p(5, 1), RIGHT, .2)
        beat(self, FadeIn(f), t=.8, rt=.4)
        fill(self, r, GRN)


class K5(Scene):
    def construct(self):
        self.add(step_tag(2, BLU))
        g1, l1, _ = C_series(LEFT * 4.4 + DOWN * .2, 3.4); g2, l2, s = par_model(RIGHT * 2.2 + DOWN * .2, 2.8, "C", BLU)
        beat(self, FadeIn(g1), FadeIn(l1), t=.8, rt=.4)
        eq = tex("=", 80, YEL).move_to(LEFT * 1.4 + DOWN * .2)
        beat(self, FadeIn(eq), Create(g2), FadeIn(l2[0]), t=1.2, rt=.8)
        beat(self, FadeIn(l2[1]), t=.8, rt=.4)
        t = kr("병렬: 전류원 Cv(0)", 36, YEL).to_edge(UP, buff=.6)
        beat(self, FadeIn(t), t=.8, rt=.4)
        fill(self, s, ORG)


# ================= STEP 3 초기값 =================
class T1(Scene):
    def construct(self):
        self.add(step_tag(3, ORG))
        D = switch_circuit(DOWN * .3)
        beat(self, FadeIn(D["g"]), FadeIn(D["labs"]), Create(D["blade"]), t=1.2, rt=.6)
        lab = kr("t < 0: A (오래)", 34, ORG).to_edge(UP, buff=.6)
        beat(self, FadeIn(lab), t=.8, rt=.3)
        nb = Line(D["piv"], D["B"], color=YEL, stroke_width=7)
        beat(self, Transform(D["blade"], nb), FadeIn(kr("t = 0: B로", 34, RED).next_to(lab, DOWN, .2)), t=1.2, rt=.6)
        fill(self, D["blade"])


class T2(Scene):
    """t<0 회로: C = 끊긴 선."""
    def construct(self):
        self.add(step_tag(3, ORG))
        D = switch_circuit(DOWN * .3)
        self.add(D["g"], D["labs"], D["blade"])
        beat(self, D["right"].animate.set_opacity(.2), D["b10"].animate.set_opacity(.2), FadeIn(kr("t < 0 회로", 36, ORG).to_edge(UP, buff=.6)), t=1.0, rt=.6)
        x = Cross(Square(.5), stroke_color=RED, stroke_width=7).move_to(D["C"])
        beat(self, Create(x), FadeIn(kr("직류 오래 → 끊긴 선", 34, RED).next_to(D["g"], DOWN, .3)), t=1.2, rt=.5)
        fill(self, x, RED)


class T3(Scene):
    def construct(self):
        self.add(step_tag(3, ORG))
        D = switch_circuit(DOWN * .3)
        self.add(D["g"], D["labs"], D["blade"])
        i0 = tex("i = 0", 48, MUTE).next_to(D["left"][0], UP, .2)
        beat(self, FadeIn(i0), t=.8, rt=.4)
        v = tex(r"v_C = 4\,\mathrm{V}", 60, ORG).next_to(D["g"], DOWN, .3)
        beat(self, Write(v), t=1.0, rt=.6)
        fill(self, v, ORG)


class T4(Scene):
    """커패시터 전압은 순간적으로 못 바뀜: v(0−) = v(0+) = 4."""
    def construct(self):
        self.add(step_tag(3, ORG))
        ax, g = taxes(DOWN * .6, 9.6, 4.0, 5, 0, 11, r"v_C")
        ax.shift(RIGHT * 1.2); g[1:].shift(RIGHT * 1.2)
        pre = Line(ax.c2p(0, 4) + LEFT * 2.2, ax.c2p(0, 4), color=ORG, stroke_width=6)
        beat(self, FadeIn(g), Create(pre), FadeIn(kr("t < 0", 30, ORG).next_to(pre, UP, .15)), t=1.2, rt=.7)
        d = Dot(ax.c2p(0, 4), .14, color=YEL)
        beat(self, FadeIn(d, scale=1.6), FadeIn(tex(r"v(0) = 4", 48, YEL).next_to(d, DR, .3)), t=1.0, rt=.4)
        jump = DashedLine(ax.c2p(0, 4), ax.c2p(0, 10), color=RED)
        beat(self, Create(jump), FadeIn(kr("순간 점프 ✕", 34, RED).next_to(ax.c2p(0, 9), LEFT, .3)), t=1.1, rt=.5)
        cur = ax.plot(f_vc, x_range=[0, 5, .02], color=GRN, stroke_width=6)
        beat(self, Create(cur), t=1.2, rt=1.0)
        fill(self, d)


class T5(Scene):
    """인덕터: 전류 연속, 직류에선 이어진 선."""
    def construct(self):
        self.add(step_tag(3, ORG))
        c = capacitor((-3.6, 1.4), (-3.6, -1.0), BLU)[0]; l = coil((3.6, 1.4), (3.6, -1.0), GRN)
        beat(self, FadeIn(c), FadeIn(l), t=.8, rt=.4)
        a = VGroup(kr("전압 연속", 34, BLU), kr("직류 → 끊긴 선", 34, MUTE)).arrange(DOWN, buff=.2).next_to(c, DOWN, .5)
        b = VGroup(kr("전류 연속", 34, GRN), kr("직류 → 이어진 선", 34, MUTE)).arrange(DOWN, buff=.2).next_to(l, DOWN, .5)
        beat(self, FadeIn(a), t=1.0, rt=.4)
        beat(self, FadeIn(b), t=1.0, rt=.4)
        sh = wire((3.6, 1.4), (3.6, -1.0), GRN, 7)
        beat(self, Transform(l, sh), t=1.0, rt=.7)
        fill(self, b, GRN)


# ================= STEP 4 s-영역 풀이 =================
class Q1(Scene):
    def construct(self):
        self.add(step_tag(4, PUR))
        D = sdom_circuit(DOWN * .2)
        beat(self, Create(D["g"]), Create(D["src"]), FadeIn(D["labs"][0]), t=1.2, rt=.8)
        beat(self, Create(D["R"]), FadeIn(D["labs"][1]), t=1.0, rt=.6)
        t = kr("t > 0 · s-영역", 36, PUR).to_edge(UP, buff=.6)
        beat(self, FadeIn(t), t=.8, rt=.3)
        fill(self, D["src"], RED)


class Q2(Scene):
    def construct(self):
        self.add(step_tag(4, PUR))
        D = sdom_circuit(DOWN * .2)
        self.add(D["g"], D["src"], D["labs"], D["R"])
        beat(self, Create(D["cap"]), FadeIn(D["clabs"][0]), Create(D["cw"]), t=1.1, rt=.7)
        beat(self, Create(D["csrc"]), FadeIn(D["clabs"][1]), t=1.1, rt=.7)
        fill(self, D["csrc"], ORG)



class Q3(Scene):
    """C = 1mF → RC = 1초, KVL 한 줄."""
    def construct(self):
        self.add(step_tag(4, PUR))
        a = tex(r"R = 1\,k\Omega,\;\; C = 1\,mF", 56).shift(UP * 1.8)
        beat(self, FadeIn(a), t=.9, rt=.4)
        b = tex(r"RC = 1\,\mathrm{s}", 80, YEL).shift(UP * .3)
        beat(self, Write(b), t=1.0, rt=.6)
        c = card(kr("미분 없이 KVL 한 줄", 40, PUR), PUR, .3).shift(DOWN * 1.8)
        beat(self, FadeIn(c, shift=UP * .2), t=1.0, rt=.4)
        fill(self, b)


class Q4(Scene):
    """I(s) = (10/s − 4/s)/(R + 1/sC) = 6mA/(s+1)."""
    def construct(self):
        self.add(step_tag(4, PUR))
        e1 = tex(r"I(s) = \frac{\frac{10}{s} - \frac{4}{s}}{R + \frac{1}{sC}}", 64).shift(UP * 1.3)
        beat(self, Write(e1), t=1.5, rt=1.0)
        b1 = Brace(e1[0][5:14], UP, color=ORG); b2 = Brace(e1[0][15:], DOWN, color=BLU)
        beat(self, GrowFromCenter(b1), FadeIn(kr("전원 차이", 28, ORG).next_to(b1, UP, .1)), t=.9, rt=.4)
        beat(self, GrowFromCenter(b2), FadeIn(kr("임피던스 합", 28, BLU).next_to(b2, DOWN, .1)), t=.9, rt=.4)
        e2 = tex(r"= \frac{6\,\mathrm{mA}}{s+1}", 76, YEL).shift(DOWN * 2.1)
        beat(self, Write(e2), t=1.2, rt=.8)
        fill(self, e2)


class Q5(Scene):
    def construct(self):
        self.add(step_tag(4, PUR))
        e = tex(r"i(t) = 6\,e^{-t}\;\mathrm{mA}", 70, YEL).to_edge(UP, buff=.8)
        beat(self, Write(e), t=1.0, rt=.7)
        ax, g = taxes(DOWN * 1.0, 9.6, 3.8, 5, 0, 7, "i(t)")
        cur = ax.plot(lambda t: 6 * np.exp(-t), x_range=[0, 5, .02], color=YEL, stroke_width=6)
        beat(self, FadeIn(g), Create(cur), t=1.6, rt=1.3)
        d = Dot(ax.c2p(0, 6), .13, color=RED)
        beat(self, FadeIn(d, scale=1.5), FadeIn(kr("넘긴 순간 6mA", 34, RED).next_to(d, RIGHT, .3)), t=1.0, rt=.4)
        fill(self, d, RED)


class Q6(Scene):
    """V_C = I/sC + 4/s = 6/(s(s+1)) + 4/s."""
    def construct(self):
        self.add(step_tag(4, PUR))
        D = sdom_circuit(LEFT * 2.6 + DOWN * .1)
        grp = VGroup(D["g"], D["src"], D["labs"], D["R"], D["cap"], D["cw"], D["csrc"], D["clabs"]).scale(.62)
        self.add(grp)
        br = SurroundingRectangle(VGroup(D["cap"], D["csrc"], D["clabs"]), color=BLU, buff=.15)
        beat(self, Create(br), FadeIn(tex("V_C", 44, BLU).next_to(br, UP, .15)), t=.9, rt=.5)
        e1 = tex(r"V_C = \frac{I}{sC} + \frac{4}{s}", 58).move_to(RIGHT * 3.4 + UP * 1.1)
        beat(self, Write(e1), t=1.2, rt=.8)
        e2 = tex(r"= \frac{6}{s(s+1)} + \frac{4}{s}", 58, BLU).next_to(e1, DOWN, .5).align_to(e1, LEFT)
        beat(self, Write(e2), t=1.2, rt=.8)
        fill(self, e2, BLU)


class Q7(Scene):
    """가리기법: 6/(s(s+1)) = 6/s − 6/(s+1) → 10/s − 6/(s+1)."""
    def construct(self):
        self.add(step_tag(4, PUR))
        e1 = tex(r"\frac{6}{s(s+1)} = \frac{6}{s} - \frac{6}{s+1}", 62).shift(UP * 1.6)
        beat(self, Write(e1), t=1.3, rt=.9)
        h = kr("1편 가리기법", 30, MUTE).next_to(e1, UP, .3)
        beat(self, FadeIn(h), t=.6, rt=.3)
        e2 = tex(r"V_C = \frac{10}{s} - \frac{6}{s+1}", 76, YEL).shift(DOWN * .8)
        beat(self, Write(e2), t=1.3, rt=.9)
        n = kr("6/s + 4/s = 10/s", 32, MUTE).next_to(e2, DOWN, .4)
        beat(self, FadeIn(n), t=.8, rt=.4)
        fill(self, e2)


class Q8(Scene):
    def construct(self):
        self.add(step_tag(4, PUR))
        e = tex(r"v_C(t) = 10 - 6\,e^{-t}\;\mathrm{V}", 66, GRN).to_edge(UP, buff=.8)
        beat(self, Write(e), t=1.2, rt=.8)
        ax, g = taxes(DOWN * 1.0, 9.6, 3.8, 5, 0, 11, r"v_C")
        cur = ax.plot(f_vc, x_range=[0, 5, .02], color=GRN, stroke_width=6)
        beat(self, FadeIn(g), Create(cur), t=1.6, rt=1.3)
        a = Dot(ax.c2p(0, 4), .13, color=ORG); b = DashedLine(ax.c2p(0, 10), ax.c2p(5, 10), color=MUTE)
        beat(self, FadeIn(a, scale=1.5), FadeIn(tex("4", 40, ORG).next_to(a, LEFT, .2)), t=.8, rt=.4)
        beat(self, Create(b), FadeIn(tex("10", 40, MUTE).next_to(b, LEFT, .2)), t=.9, rt=.5)
        fill(self, cur, GRN)


# ================= 검산 · 자주 틀리는 곳 =================
class X1(Scene):
    def construct(self):
        a = card(VGroup(kr("초기값 정리", 32, ORG), tex(r"\lim_{s\to\infty} sV_C = 4", 50)).arrange(DOWN, buff=.3), ORG, .35).shift(LEFT * 3.3)
        b = card(VGroup(kr("최종값 정리", 32, ORG), tex(r"\lim_{s\to 0} sV_C = 10", 50)).arrange(DOWN, buff=.3), ORG, .35).shift(RIGHT * 3.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.4, rt=.5)
        beat(self, FadeIn(b, shift=UP * .2), t=1.4, rt=.5)
        ok = kr("✔ 4 → 10 딱 맞음", 48, GRN).shift(DOWN * 2.3)
        beat(self, FadeIn(ok, scale=1.3), t=1.0, rt=.4)
        fill(self, ok, GRN)


def mistake(n, c=RED):
    return kr(f"자주 틀리는 곳 {n}", 36, c).to_edge(UP, buff=.6)


class X2(Scene):
    def construct(self):
        self.add(mistake(1))
        w = tex(r"v(0)", 80, RED).shift(LEFT * 3); x = Cross(w, stroke_color=RED, stroke_width=8)
        r = tex(r"\frac{v(0)}{s}", 90, GRN).shift(RIGHT * 3)
        beat(self, FadeIn(w), t=.8, rt=.4)
        beat(self, Create(x), FadeIn(kr("s 빼먹기", 40, RED).next_to(w, DOWN, .5)), t=1.0, rt=.4)
        beat(self, FadeIn(r, shift=LEFT * .3), FadeIn(kr("커패시터 전원", 34, GRN).next_to(r, DOWN, .4)), t=1.1, rt=.5)
        fill(self, r, GRN)


class X3(Scene):
    def construct(self):
        self.add(mistake(2))
        c = capacitor((-3.6, 1.4), (-3.6, -1.4), BLU)[0]
        pl = VGroup(tex("+", 56, ORG).next_to(c, LEFT, .4).shift(UP * .9), tex("-", 56, ORG).next_to(c, LEFT, .4).shift(DOWN * .9), tex("4V", 44, ORG).next_to(c, LEFT, .5))
        beat(self, FadeIn(c), FadeIn(pl), t=1.0, rt=.5)
        a = Arrow(LEFT * 2.2, LEFT * .6, buff=0, color=YEL)
        g, labs, s = C_series(RIGHT * 1.6, 3.4, BLU, ORG, r"\frac{4}{s}")
        beat(self, GrowArrow(a), FadeIn(g), FadeIn(labs), t=1.2, rt=.6)
        ok = kr("같은 방향 (+ 위)", 36, GRN).move_to(RIGHT * 4.4 + DOWN * 2.4)
        beat(self, Indicate(s, color=GRN, scale_factor=1.0), FadeIn(ok), t=1.2, rt=.6)
        fill(self, s, GRN)


class X4(Scene):
    def construct(self):
        self.add(mistake(3))
        D = switch_circuit(DOWN * .4)
        self.add(D["g"], D["labs"], D["blade"])
        w = kr("✕ t > 0 회로에서", 36, RED).move_to(RIGHT * 3.6 + UP * 2.4)
        beat(self, FadeIn(w), t=1.0, rt=.4)
        o = kr("✔ 넘기기 전 회로에서", 36, GRN).next_to(w, DOWN, .25)
        beat(self, FadeIn(o), Indicate(D["blade"], color=GRN, scale_factor=1.0), t=1.2, rt=.6)
        fill(self, o, GRN)


# ================= 정리 =================
class O1(Scene):
    def construct(self):
        g1, l1, _ = L_series(LEFT * 3.6 + DOWN * .4, 3.6); g2, l2, _ = C_series(RIGHT * 2.2 + DOWN * .4, 3.6)
        beat(self, FadeIn(g1), FadeIn(l1), FadeIn(kr("인덕터", 36, GRN).next_to(g1, UP, .3)), t=1.4, rt=.5)
        beat(self, FadeIn(g2), FadeIn(l2), FadeIn(kr("커패시터", 36, BLU).next_to(g2, UP, .3)), t=1.4, rt=.5)
        fill(self, VGroup(l1[1], l2[1]), ORG)


class O2(Scene):
    def construct(self):
        items = [("1", "초기값", ORG), ("2", "s-영역 회로", BLU), ("3", "KVL·KCL", PUR), ("4", "역변환", GRN)]
        cs = VGroup(*[card(VGroup(kr(n, 30, MUTE), kr(t, 36, c)).arrange(DOWN, buff=.2), c, .3) for n, t, c in items]).arrange(RIGHT, buff=.5)
        cs.scale_to_fit_width(min(cs.width, 12.6))
        arrs = VGroup(*[Arrow(cs[i].get_right(), cs[i + 1].get_left(), buff=.08, color=MUTE) for i in range(3)])
        beat(self, FadeIn(cs[0]), t=.7, rt=.3)
        for i in range(3):
            beat(self, GrowArrow(arrs[i]), FadeIn(cs[i + 1], shift=RIGHT * .2), t=.9, rt=.4)
        fill(self, cs)


class O3(Scene):
    def construct(self):
        a = tex(r"v = 10 + A e^{-t}", 60, MUTE).shift(UP * 1.2)
        x = Cross(a, stroke_color=RED, stroke_width=6)
        beat(self, FadeIn(a), t=.8, rt=.4)
        beat(self, Create(x), FadeIn(kr("상수 A 따로 구하기", 32, RED).next_to(a, UP, .3)), t=1.0, rt=.5)
        ok = card(kr("초기 조건이 회로 안에", 44, GRN), GRN, .3).shift(DOWN * 1.4)
        beat(self, FadeIn(ok, shift=UP * .2), t=1.0, rt=.4)
        fill(self, ok, GRN)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("과도응답 · 스위치 전후", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55).shift(LEFT * 2.6)
        beat(self, FadeIn(t[0]), FadeIn(t[1][0]), t=.8, rt=.3)
        ax, g = taxes(RIGHT * 4.0, 3.6, 2.8, 5, 0, 11, r"v_C")
        self.add(g)
        cur = ax.plot(f_vc, x_range=[0, 5, .02], color=GRN, stroke_width=5)
        for m in t[1][1:]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.1, rt=.4)
        beat(self, Create(cur), t=1.8, rt=1.6)
        fill(self, t, YEL)


class Next(Scene):
    def construct(self):
        lab = kr("다음 편 · 2차 RLC 회로, 극점으로 끝내기", 38, YEL).to_edge(UP, buff=.7)
        beat(self, FadeIn(lab), t=.9, rt=.4)
        ax, g = taxes(DOWN * .6, 9, 3.6, 6, -.7, 1.2, "v(t)")
        beat(self, FadeIn(g), t=.4, rt=.3)
        cs = [(lambda t: (1.207 * np.exp(-.414 * t) - .207 * np.exp(-2.414 * t)), BLU, "과감쇠"),
              (lambda t: (1 + 1.6 * t) * np.exp(-1.6 * t), PUR, "임계감쇠"), (lambda t: np.exp(-.5 * t) * np.cos(2.5 * t), GRN, "부족감쇠")]
        labs = VGroup()
        for i, (f, c, n) in enumerate(cs):
            cur = ax.plot(f, x_range=[0, 6, .02], color=c, stroke_width=5)
            l = kr(n, 30, c).move_to(RIGHT * (2.6 + 0) + UP * (1.0 - .5 * i))
            beat(self, Create(cur), FadeIn(l), t=1.0, rt=.7)
            labs.add(l)
        fill(self, labs)


# ================= 쇼츠 전용 =================
class AQ(Scene):
    def construct(self):
        l = card(VGroup(kr("초기 조건", 40, MUTE), tex("v(0)", 64, ORG)).arrange(DOWN, buff=.3), "#2a2e37", .4).shift(LEFT * 3.2)
        beat(self, FadeIn(l), t=.8, rt=.4)
        eq = tex("=", 90, YEL)
        s = vsrc(RIGHT * 3.0, ORG, .8)
        beat(self, FadeIn(eq), Create(s), t=1.0, rt=.6)
        t = kr("전원 하나", 52, YEL).to_edge(DOWN, buff=.8)
        beat(self, FadeIn(t, scale=1.3), t=.8, rt=.4)
        fill(self, s, ORG)


class BQ(Scene):
    def construct(self):
        w = tex("4", 110, RED).shift(LEFT * 3); r = tex(r"\frac{4}{s}", 110, GRN).shift(RIGHT * 3)
        beat(self, FadeIn(w), t=.7, rt=.3)
        beat(self, Create(Cross(w, stroke_color=RED, stroke_width=9)), t=.7, rt=.4)
        beat(self, FadeIn(r, shift=LEFT * .3), FadeIn(kr("s 빼먹기 주의", 44, YEL).to_edge(DOWN, buff=.8)), t=1.0, rt=.5)
        fill(self, r, GRN)


class CQ(Scene):
    def construct(self):
        D = switch_circuit(DOWN * .2)
        self.add(D["g"], D["labs"], D["blade"])
        q = kr("초기값 3초 컷", 52, YEL).to_edge(UP, buff=.5)
        beat(self, FadeIn(q, scale=1.3), t=.8, rt=.4)
        fill(self, q)


class DQ(Scene):
    def construct(self):
        a = VGroup(tex("4V", 80, ORG), Arrow(LEFT, RIGHT, color=YEL, stroke_width=7), tex("10V", 80, RED)).arrange(RIGHT, buff=.5).shift(UP * 1.4)
        beat(self, FadeIn(a[0]), t=.6, rt=.3)
        beat(self, GrowArrow(a[1]), FadeIn(a[2]), t=.8, rt=.4)
        ax, g = taxes(DOWN * 1.4, 8, 2.6, 5, 0, 11, r"v_C")
        cur = ax.plot(f_vc, x_range=[0, 5, .02], color=GRN, stroke_width=6)
        q = kr("?", 80, YEL).move_to(ax.c2p(2.5, 6))
        beat(self, FadeIn(g), FadeIn(q), t=.8, rt=.4)
        beat(self, Create(cur), FadeOut(q), t=1.2, rt=1.0)
        fill(self, cur, GRN)


class EQ(Scene):
    def construct(self):
        g1, l1, _ = L_series(LEFT * 3.6 + DOWN * .2, 3.4); g2, l2, _ = par_model(RIGHT * 2.6 + DOWN * .2, 2.8, "L", GRN)
        beat(self, FadeIn(g1), FadeIn(l1), FadeIn(kr("직렬?", 44, YEL).next_to(g1, UP, .3)), t=.9, rt=.4)
        beat(self, FadeIn(g2), FadeIn(l2), FadeIn(kr("병렬?", 44, YEL).next_to(g2, UP, .3)), t=.9, rt=.4)
        fill(self, VGroup(g1, g2))
