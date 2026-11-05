# 라플라스 심화 1편(역변환·부분분수 3가지 경우·초기값/최종값 검산) 롱폼 모션그래픽. 16:9, 핵심은 가운데(가로 ±5)에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(long.json 에서 그 문장 시작에 붙임). 주파수 응답 편(freqresp/manim/scenes.py) 형식을 따른다.
# 끝까지 보게 만드는 4원칙: 1.5~2.5초마다 화면에 새 요소(내용으로 변화, 전환·반복 확대 없음), 4초 넘게 멈춘 화면 없음.
# 장면 길이: dur.json(문장 실제 길이)에 맞춰 마지막을 강조 테두리로 채운다 (fill).
# 검산은 ../lines.py 맨 위 참고.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
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


# ================= 인트로 =================
class Hook(Scene):
    """회로 풀이 끝에 남는 분수 → 역변환 → 시간 그래프 (최종 결과를 먼저)."""
    def construct(self):
        F = VGroup(tex("V(s) =", 60), frac("s+3", ["(s+1)", "(s+2)"], 60, YEL)).arrange(RIGHT, buff=.25).move_to(LEFT * 4.0 + UP * .8)
        beat(self, Write(F[0]), t=.7, rt=.5)
        beat(self, FadeIn(F[1], shift=UP * .2), t=1.0, rt=.6)
        q = kr("이 분수를 시간으로?", 34, MUTE).next_to(F, DOWN, .5)
        beat(self, FadeIn(q), t=.9, rt=.4)
        a = Arrow(LEFT * .5 + UP * .8, RIGHT * .7 + UP * .8, buff=0, color=YEL, stroke_width=7)
        ax, g = taxes(RIGHT * 3.6 + UP * .3, 5.4, 3.0, 5, -.1, 1.25, "v(t)")
        cur = ax.plot(f_distinct, x_range=[0, 5, .02], color=GRN, stroke_width=6)
        beat(self, GrowArrow(a), FadeIn(g), t=.8, rt=.5)
        beat(self, Create(cur), t=1.4, rt=1.2)
        ans = tex(r"v(t) = 2e^{-t} - e^{-2t}", 50, GRN).next_to(g, DOWN, .4)
        beat(self, Write(ans), t=1.0, rt=.7)
        fill(self, ans, GRN)


class Inv(Scene):
    """F(s) → f(t) 역변환, 시험 최다 막힘."""
    def construct(self):
        L = card(tex("F(s)", 80, BLU), BLU, .45).shift(LEFT * 3.6 + UP * .6)
        R = card(tex("f(t)", 80, GRN), GRN, .45).shift(RIGHT * 3.6 + UP * .6)
        beat(self, FadeIn(L), t=.8, rt=.4)
        a = Arrow(L.get_right(), R.get_left(), buff=.3, color=YEL, stroke_width=7)
        lab = tex(r"\mathcal{L}^{-1}", 64, YEL).next_to(a, UP, .2)
        beat(self, GrowArrow(a), Write(lab), t=1.0, rt=.6)
        beat(self, FadeIn(R), t=.8, rt=.4)
        t = kr("역변환", 56, YEL).next_to(a, DOWN, .5)
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.4)
        w = card(kr("시험에서 제일 많이 막히는 곳", 38, RED), RED, .3).to_edge(DOWN, buff=.6)
        beat(self, FadeIn(w, shift=UP * .3), t=1.2, rt=.5)
        fill(self, w, RED)


def three_cards(sz=34):
    items = [("서로 다른 극점", r"\frac{1}{(s+1)(s+2)}", BLU), ("중근", r"\frac{1}{(s+1)^2}", PUR), ("복소 극점", r"\frac{1}{s^2+2s+5}", GRN)]
    return VGroup(*[card(VGroup(kr(n, sz, c), tex(f, 50, INK)).arrange(DOWN, buff=.35), c, .35) for n, f, c in items]).arrange(RIGHT, buff=.4)


class Three(Scene):
    """분모 모양은 세 가지."""
    def construct(self):
        h = kr("분모 모양은 딱 3가지", 48, YEL).to_edge(UP, buff=.6)
        beat(self, FadeIn(h), t=.9, rt=.4)
        cs = three_cards().scale_to_fit_width(12.6).shift(DOWN * .3)
        for c in cs:
            beat(self, FadeIn(c, shift=UP * .3), t=1.3, rt=.45)
        fill(self, cs)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "서로 다른 극점", BLU), ("2", "중근", PUR), ("3", "복소 극점", GRN), ("4", "2초 검산", ORG)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.3).scale_to_fit_width(12.8).shift(UP * .3)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.2, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[3].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.0, rt=.8)
        ck = kr("✔ 답 확인까지", 40, ORG).next_to(arrow, DOWN, .4)
        beat(self, FadeIn(ck), t=.8, rt=.4)
        fill(self, cards[3], ORG)


# ================= STEP 1 서로 다른 극점 =================
def F1(size=64, col=YEL):
    return frac("s+3", ["(s+1)", "(s+2)"], size, col)


class D1(Scene):
    """분모 = 서로 다른 일차식 두 개."""
    def construct(self):
        self.add(step_tag(1, BLU))
        d = VGroup(tex("(s+1)", 72, BLU), tex(r"\times", 60, MUTE), tex("(s+2)", 72, BLU)).arrange(RIGHT, buff=.3).shift(UP * .8)
        beat(self, FadeIn(d[0], shift=UP * .2), t=1.0, rt=.4)
        beat(self, FadeIn(d[1]), FadeIn(d[2], shift=UP * .2), t=1.0, rt=.4)
        b1 = Brace(d[0], DOWN, color=MUTE); b2 = Brace(d[2], DOWN, color=MUTE)
        l = VGroup(kr("일차식", 32, MUTE).next_to(b1, DOWN, .15), kr("일차식", 32, MUTE).next_to(b2, DOWN, .15))
        beat(self, GrowFromCenter(b1), GrowFromCenter(b2), FadeIn(l), t=1.2, rt=.5)
        ne = kr("서로 다름", 44, YEL).to_edge(DOWN, buff=1.0)
        beat(self, FadeIn(ne, shift=UP * .2), t=1.0, rt=.4)
        fill(self, ne)


class D2(Scene):
    """예제 F(s), 변환표에 없음."""
    def construct(self):
        self.add(step_tag(1, BLU))
        F = F1(72).shift(LEFT * 3)
        beat(self, Write(F[0]), Create(F[1]), t=1.0, rt=.7)
        beat(self, FadeIn(F[2], shift=UP * .2), t=1.0, rt=.5)
        tb = VGroup(kr("변환표", 34, MUTE),
                    tex(r"\frac{1}{s} \to 1", 44), tex(r"\frac{1}{s+a} \to e^{-at}", 44), tex(r"\cdots", 44, MUTE)).arrange(DOWN, buff=.3)
        tbc = card(tb, "#2a2e37", .35).shift(RIGHT * 3.4)
        beat(self, FadeIn(tbc), t=1.2, rt=.5)
        x = Cross(F, stroke_color=RED, stroke_width=8)
        beat(self, Create(x), FadeIn(kr("표에 없음", 40, RED).next_to(F, DOWN, .5)), t=1.2, rt=.5)
        fill(self, tbc, RED)


class D3(Scene):
    """부분분수로 쪼개기."""
    def construct(self):
        self.add(step_tag(1, BLU))
        F = F1(64)
        eq = tex("=", 60)
        k1 = frac("K_1", ["s+1"], 60, BLU); pl = tex("+", 60); k2 = frac("K_2", ["s+2"], 60, PUR)
        row = VGroup(F, eq, k1, pl, k2).arrange(RIGHT, buff=.35).shift(UP * .4)
        beat(self, FadeIn(F), t=.9, rt=.4)
        beat(self, Write(eq), TransformFromCopy(F[2][0], k1), t=1.3, rt=.9)
        beat(self, Write(pl), TransformFromCopy(F[2][1], k2), t=1.3, rt=.9)
        lab = kr("부분분수", 52, YEL).next_to(row, DOWN, .9)
        beat(self, FadeIn(lab, shift=UP * .2), t=1.0, rt=.4)
        fill(self, VGroup(k1, k2))


def hand_cover(m, c=BLU):
    """손(가림판)으로 덮기: 둥근 사각형 + 손 모양 텍스트."""
    r = RoundedRectangle(width=m.width + .3, height=m.height + .3, corner_radius=.15, color=c, fill_color=c, fill_opacity=.92, stroke_width=4).move_to(m)
    return VGroup(r, kr("✋", 40, BG).move_to(r))


class D4(Scene):
    """가리기법: (s+1) 가리고 s = −1 대입."""
    def construct(self):
        self.add(step_tag(1, BLU))
        F = F1(80).shift(LEFT * 2.2 + UP * .5)
        self.add(F)
        lab = kr("가리기법", 48, YEL).to_edge(UP, buff=.7).shift(LEFT * 2)
        beat(self, FadeIn(lab), t=.8, rt=.4)
        hc = hand_cover(F[2][0], BLU)
        beat(self, FadeIn(hc, shift=DOWN * .3), t=1.2, rt=.6)
        s = tex(r"s = -1", 64, BLU).move_to(RIGHT * 3.4 + UP * .5)
        beat(self, Write(s), t=1.0, rt=.6)
        a1 = Arrow(s.get_left(), F[0].get_right() + RIGHT * .1, buff=.15, color=BLU, stroke_width=5)
        a2 = Arrow(s.get_left(), F[2][1].get_right() + RIGHT * .1, buff=.15, color=BLU, stroke_width=5)
        beat(self, GrowArrow(a1), GrowArrow(a2), t=1.0, rt=.5)
        v = VGroup(tex(r"\frac{-1+3}{-1+2}", 60, INK)).next_to(F, DOWN, .7).shift(RIGHT * .6)
        beat(self, Write(v), t=1.4, rt=.7)
        fill(self, v)


class D5(Scene):
    """K1 = 2."""
    def construct(self):
        self.add(step_tag(1, BLU))
        v = tex(r"\frac{-1+3}{-1+2} = \frac{2}{1}", 72).shift(UP * 1.0)
        beat(self, Write(v), t=1.2, rt=.8)
        k = tex(r"K_1 = 2", 96, BLU).shift(DOWN * 1.2)
        beat(self, Write(k), t=1.2, rt=.6)
        fill(self, k, BLU)


class D6(Scene):
    """왜? 양변 × (s+1), s=−1 → K2 항 0."""
    def construct(self):
        self.add(step_tag(1, BLU))
        q = kr("왜 가리기만 해도 될까?", 44, YEL).to_edge(UP, buff=.7)
        beat(self, FadeIn(q), t=1.0, rt=.4)
        e1 = MathTex(r"\frac{s+3}{s+2}", r"=", r"K_1", r"+", r"\frac{K_2\,(s+1)}{s+2}", color=INK, font_size=62).shift(UP * .5)
        beat(self, Write(e1), t=1.6, rt=1.1)
        m = kr("양변 × (s+1)", 32, MUTE).next_to(e1, UP, .3)
        beat(self, FadeIn(m), t=.8, rt=.3)
        s = tex(r"s = -1", 56, BLU).next_to(e1, DOWN, .7).shift(LEFT * 3)
        beat(self, Write(s), t=.9, rt=.5)
        z = tex(r"\to 0", 56, RED).next_to(e1[4], DOWN, .5)
        x = Cross(e1[4], stroke_color=RED, stroke_width=7)
        beat(self, Create(x), Write(z), t=1.2, rt=.6)
        r = SurroundingRectangle(e1[2], color=BLU, buff=.15)
        beat(self, Create(r), FadeIn(kr("K₁만 남음", 40, BLU).next_to(r, DOWN, 1.2)), t=1.2, rt=.5)
        fill(self, r, BLU)


class D7(Scene):
    """K2: (s+2) 가리고 s=−2 → −1."""
    def construct(self):
        self.add(step_tag(1, BLU))
        F = F1(80).shift(LEFT * 3 + UP * .6)
        self.add(F)
        hc = hand_cover(F[2][1], PUR)
        beat(self, FadeIn(hc, shift=DOWN * .3), t=1.0, rt=.6)
        s = tex(r"s = -2", 64, PUR).move_to(RIGHT * 2.8 + UP * 1.6)
        beat(self, Write(s), t=.9, rt=.5)
        v = tex(r"\frac{-2+3}{-2+1} = \frac{1}{-1}", 60).move_to(RIGHT * 2.8 + DOWN * .1)
        beat(self, Write(v), t=1.4, rt=.8)
        k = tex(r"K_2 = -1", 84, PUR).move_to(DOWN * 2.3)
        beat(self, Write(k), t=1.0, rt=.6)
        fill(self, k, PUR)


class D8(Scene):
    """표: 1/(s+a) → e^-at, 답 + 그래프."""
    def construct(self):
        self.add(step_tag(1, BLU))
        tb = card(tex(r"\frac{1}{s+a} \;\to\; e^{-at}", 54, YEL), YEL, .3).to_edge(UP, buff=.8)
        beat(self, FadeIn(tb), t=1.0, rt=.4)
        e = MathTex(r"\frac{2}{s+1}", r"-", r"\frac{1}{s+2}", color=INK, font_size=58).shift(LEFT * 3.6 + DOWN * .2)
        beat(self, FadeIn(e), t=1.0, rt=.4)
        a = Arrow(e.get_right(), e.get_right() + RIGHT * 1.0, buff=.2, color=YEL)
        r = MathTex(r"2e^{-t}", r"-", r"e^{-2t}", font_size=62, color=GRN).next_to(a, RIGHT, .2)
        beat(self, GrowArrow(a), TransformFromCopy(e[0], r[0]), t=1.2, rt=.8)
        beat(self, TransformFromCopy(e[1], r[1]), TransformFromCopy(e[2], r[2]), t=1.2, rt=.8)
        ax, g = taxes(DOWN * 2.3 + RIGHT * 2.6, 6.0, 2.2, 5, -.1, 1.25)
        cur = ax.plot(f_distinct, x_range=[0, 5, .02], color=GRN, stroke_width=6)
        beat(self, FadeIn(g), Create(cur), t=1.6, rt=1.3)
        fill(self, r, GRN)


class D9(Scene):
    """극점 −1, −2 (실수) → 지수 함수 두 개의 합."""
    def construct(self):
        self.add(step_tag(1, BLU))
        ax, g = splane(LEFT * 4.2 + DOWN * .2, 4.4, 4.0)
        beat(self, FadeIn(g), t=.7, rt=.4)
        p1, p2 = pole(ax, -1, 0, BLU), pole(ax, -2, 0, PUR)
        beat(self, Create(p1), Create(p2), FadeIn(kr("실수 극점", 32, YEL).next_to(ax, UP, .2)), t=1.0, rt=.5)
        tx, tg = taxes(RIGHT * 2.6 + DOWN * .2, 6.4, 4.0, 5, -1.2, 2.2)
        self.play(FadeIn(tg), run_time=.4)
        c1 = tx.plot(lambda t: 2 * np.exp(-t), x_range=[0, 5, .02], color=BLU, stroke_width=4)
        c2 = tx.plot(lambda t: -np.exp(-2 * t), x_range=[0, 5, .02], color=PUR, stroke_width=4)
        beat(self, Create(c1), FadeIn(tex(r"2e^{-t}", 36, BLU).move_to(tx.c2p(1.4, 1.5))), t=1.1, rt=.8)
        beat(self, Create(c2), FadeIn(tex(r"-e^{-2t}", 36, PUR).move_to(tx.c2p(1.4, -.8))), t=1.1, rt=.8)
        s = tx.plot(f_distinct, x_range=[0, 5, .02], color=GRN, stroke_width=7)
        beat(self, Create(s), FadeIn(kr("합 = 진동 없이 감소", 32, GRN).move_to(tx.c2p(3.3, 1.4))), t=1.4, rt=1.0)
        fill(self, s, GRN)


# ================= STEP 2 중근 =================
class R1(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        d = VGroup(tex("(s+1)", 72, PUR), tex("(s+1)", 72, PUR)).arrange(RIGHT, buff=.15).shift(UP * .9)
        beat(self, FadeIn(d[0], shift=UP * .2), t=.9, rt=.4)
        beat(self, FadeIn(d[1], shift=UP * .2), t=.9, rt=.4)
        sq = tex("(s+1)^2", 96, PUR).move_to(DOWN * 1.2)
        beat(self, TransformFromCopy(d, sq), t=1.2, rt=.8)
        lab = kr("같은 인수 두 번 = 중근", 40, YEL).next_to(sq, DOWN, .5)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        fill(self, sq, PUR)


class R2(Scene):
    """1/(s+1)^2: 가리기법 그대로는 X."""
    def construct(self):
        self.add(step_tag(2, PUR))
        F = frac("1", ["(s+1)^2"], 90, YEL).shift(LEFT * 2.6)
        beat(self, Write(F), t=1.2, rt=.8)
        hc = hand_cover(F[2], PUR)
        beat(self, FadeIn(hc, shift=DOWN * .3), t=.9, rt=.5)
        q = tex(r"s=-1 \;\Rightarrow\; ?", 60, MUTE).shift(RIGHT * 3 + UP * .4)
        beat(self, Write(q), t=1.0, rt=.6)
        x = kr("가리기법 그대로 ✕", 40, RED).shift(RIGHT * 3 + DOWN * 1.0)
        beat(self, FadeOut(hc), FadeIn(x), t=1.2, rt=.4)
        fill(self, x, RED)


class R3(Scene):
    """표에 한 줄 추가: 1/(s+a)^2 → t e^-at."""
    def construct(self):
        self.add(step_tag(2, PUR))
        r1 = tex(r"\frac{1}{s+a} \;\to\; e^{-at}", 60, MUTE)
        r2 = tex(r"\frac{1}{(s+a)^2} \;\to\; t\,e^{-at}", 66, YEL)
        tb = VGroup(r1, r2).arrange(DOWN, buff=.6, aligned_edge=LEFT).shift(UP * .2)
        beat(self, FadeIn(r1), t=1.0, rt=.4)
        beat(self, FadeIn(r2, shift=UP * .3), t=1.3, rt=.6)
        nw = kr("NEW", 34, BG).add_background_rectangle(YEL, 1, buff=.12).next_to(r2, LEFT, .4)
        beat(self, FadeIn(nw, scale=1.3), t=.9, rt=.4)
        r = SurroundingRectangle(r2[0][-6:], color=PUR, buff=.12)
        beat(self, Create(r), FadeIn(kr("t가 붙음", 36, PUR).next_to(r, DOWN, .3)), t=1.0, rt=.5)
        fill(self, r2)


class R4(Scene):
    """s 로 미분 ↔ −t 곱하기."""
    def construct(self):
        self.add(step_tag(2, PUR))
        q = kr("왜 t가 붙을까?", 44, YEL).to_edge(UP, buff=.7)
        beat(self, FadeIn(q), t=.9, rt=.4)
        L = card(VGroup(kr("s-영역", 30, BLU), tex(r"\frac{d}{ds}F(s)", 60, BLU)).arrange(DOWN, buff=.3), BLU, .35).shift(LEFT * 3.4)
        R = card(VGroup(kr("시간 영역", 30, GRN), tex(r"-t\,f(t)", 60, GRN)).arrange(DOWN, buff=.3), GRN, .35).shift(RIGHT * 3.4)
        beat(self, FadeIn(L, shift=RIGHT * .2), t=1.1, rt=.5)
        arr = DoubleArrow(L.get_right(), R.get_left(), buff=.2, color=YEL, stroke_width=6)
        beat(self, GrowFromCenter(arr), t=.8, rt=.5)
        beat(self, FadeIn(R, shift=LEFT * .2), t=1.1, rt=.5)
        fill(self, R, GRN)


class R5(Scene):
    """1/(s+1) 미분 → −1/(s+1)^2 → t e^-t."""
    def construct(self):
        self.add(step_tag(2, PUR))
        a = tex(r"\frac{1}{s+1} \;\leftrightarrow\; e^{-t}", 60).shift(UP * 1.9)
        beat(self, Write(a), t=1.1, rt=.7)
        d = tex(r"\frac{d}{ds}\,\frac{1}{s+1} = -\frac{1}{(s+1)^2}", 60, BLU)
        beat(self, Write(d), t=1.5, rt=1.0)
        r = tex(r"\frac{1}{(s+1)^2} \;\leftrightarrow\; t\,e^{-t}", 68, YEL).shift(DOWN * 2.0)
        ar = Arrow(d.get_bottom(), r.get_top(), buff=.15, color=MUTE)
        beat(self, GrowArrow(ar), Write(r), t=1.5, rt=1.0)
        fill(self, r)


class R6(Scene):
    """t e^-t 그래프: t=1 에서 꼭대기."""
    def construct(self):
        self.add(step_tag(2, PUR))
        ax, g = taxes(DOWN * .4, 9.6, 4.6, 6, -.05, .5, "f(t)")
        beat(self, FadeIn(g), t=.6, rt=.4)
        cur = ax.plot(f_double, x_range=[0, 6, .02], color=PUR, stroke_width=7)
        beat(self, Create(cur), FadeIn(tex(r"t\,e^{-t}", 50, PUR).move_to(ax.c2p(3.5, .38))), t=1.8, rt=1.5)
        o = Dot(ax.c2p(0, 0), .12, color=YEL)
        beat(self, FadeIn(o, scale=1.5), FadeIn(kr("0에서 출발", 30, YEL).next_to(o, UR, .15)), t=.9, rt=.4)
        pk = Dot(ax.c2p(1, np.exp(-1)), .13, color=YEL)
        dl = DashedLine(ax.c2p(1, 0), ax.c2p(1, np.exp(-1)), color=YEL)
        beat(self, Create(dl), FadeIn(pk, scale=1.5), FadeIn(tex("t=1", 40, YEL).next_to(ax.c2p(1, 0), DOWN, .2)), t=1.2, rt=.6)
        fill(self, pk)


class R7(Scene):
    """(s+2)/(s+1)^2 = K1/(s+1)^2 + K2/(s+1)."""
    def construct(self):
        self.add(step_tag(2, PUR))
        F = frac("s+2", ["(s+1)^2"], 62, YEL)
        k1 = frac("K_1", ["(s+1)^2"], 58, PUR); k2 = frac("K_2", ["s+1"], 58, BLU)
        row = VGroup(F, tex("=", 58), k1, tex("+", 58), k2).arrange(RIGHT, buff=.3).shift(UP * .3)
        beat(self, FadeIn(F), t=1.0, rt=.4)
        beat(self, FadeIn(row[1]), FadeIn(k1, shift=UP * .2), t=1.2, rt=.5)
        beat(self, FadeIn(row[3]), FadeIn(k2, shift=UP * .2), t=1.2, rt=.5)
        lab = kr("두 개로 쪼개기", 40, MUTE).next_to(row, DOWN, .8)
        beat(self, FadeIn(lab), t=.9, rt=.4)
        fill(self, VGroup(k1, k2), PUR)


class R8(Scene):
    """K1 = 1 (가리기), K2 = 1 (미분) → 답."""
    def construct(self):
        self.add(step_tag(2, PUR))
        a = VGroup(kr("가리기법", 32, PUR), tex(r"K_1 = (s+2)\big|_{s=-1} = 1", 54, PUR)).arrange(RIGHT, buff=.4).shift(UP * 2.0)
        beat(self, FadeIn(a), t=1.4, rt=.6)
        b = VGroup(kr("미분 한 번", 32, BLU), tex(r"K_2 = \frac{d}{ds}(s+2) = 1", 54, BLU)).arrange(RIGHT, buff=.4).shift(UP * .4)
        beat(self, FadeIn(b), t=1.4, rt=.6)
        r = tex(r"f(t) = t\,e^{-t} + e^{-t}", 72, YEL).shift(DOWN * 1.6)
        beat(self, Write(r), t=1.4, rt=.9)
        fill(self, r)


def rlc_series(o=ORIGIN, W=6.0, H=2.0):
    o = P3(o); x0, x1 = o[0] - W / 2, o[0] + W / 2; yt, yb = o[1] + H / 2, o[1] - H / 2
    xs = np.linspace(x0, x1, 4)
    R = resistor((xs[0], yt), (xs[1], yt), BLU); L = coil((xs[1], yt), (xs[2], yt), GRN); C = capacitor((xs[3], yt), (xs[3], yb), ORG)[0]
    sw = VGroup(wire((x0, yt), (x0, o[1] + .3)), Line(P3((x0, o[1] + .3)), P3((x0 - .35, o[1] - .25)), color=INK, stroke_width=4), wire((x0, o[1] - .3), (x0, yb)))
    g = VGroup(R, L, wire((xs[2], yt), (xs[3], yt)), C, wire((x0, yb), (x1, yb)), sw)
    return VGroup(g, tex("R", 40, BLU).next_to(R, UP, .25), tex("L", 40, GRN).next_to(L, UP, .25), tex("C", 40, ORG).next_to(C, RIGHT, .3))


class R9(Scene):
    """임계감쇠: 진동 없이 가장 빨리 제자리."""
    def construct(self):
        self.add(step_tag(2, PUR))
        c = rlc_series(LEFT * 3.8 + UP * .6, 4.4, 1.8)
        beat(self, Create(c), t=1.0, rt=.7)
        ax, g = taxes(RIGHT * 2.8 + DOWN * .2, 6.6, 3.8, 6, -.6, 1.15, "v(t)")
        beat(self, FadeIn(g), t=.5, rt=.4)
        over = ax.plot(lambda t: (1.207 * np.exp(-.414 * t) - .207 * np.exp(-2.414 * t)), x_range=[0, 6, .02], color=BLU, stroke_width=4)
        und = ax.plot(lambda t: np.exp(-.5 * t) * np.cos(2.5 * t), x_range=[0, 6, .02], color=GRN, stroke_width=4)
        crit = ax.plot(lambda t: (1 + 1.6 * t) * np.exp(-1.6 * t), x_range=[0, 6, .02], color=PUR, stroke_width=8)
        beat(self, Create(over), Create(und), t=1.2, rt=1.0)
        beat(self, Create(crit), t=1.2, rt=1.0)
        lab = kr("임계감쇠", 48, PUR).next_to(c, DOWN, .7)
        beat(self, FadeIn(lab), FadeIn(kr("진동 없이 가장 빨리", 30, MUTE).next_to(lab, DOWN, .2)), t=1.0, rt=.4)
        fill(self, crit, PUR)


# ================= STEP 3 복소 극점 =================
class C1(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        e = tex(r"s^2 + 2s + 5", 90).shift(UP * .9)
        beat(self, Write(e), t=1.1, rt=.7)
        q = tex(r"= (s - \ ?\,)(s - \ ?\,)", 60, MUTE).next_to(e, DOWN, .6)
        beat(self, FadeIn(q), t=1.0, rt=.4)
        x = kr("실수로 안 쪼개짐", 46, RED).next_to(q, DOWN, .6)
        beat(self, FadeIn(x, shift=UP * .2), t=1.0, rt=.4)
        fill(self, x, RED)


class C2(Scene):
    """근의 공식 → −1 ± j2, s 평면에 찍기."""
    def construct(self):
        self.add(step_tag(3, GRN))
        f = tex(r"s = \frac{-2 \pm \sqrt{4-20}}{2}", 56).move_to(LEFT * 3.3 + UP * 1.4)
        beat(self, Write(f), t=1.3, rt=.9)
        r = tex(r"s = -1 \pm j2", 66, GRN).move_to(LEFT * 3.3 + DOWN * .6)
        beat(self, Write(r), t=1.0, rt=.6)
        ax, g = splane(RIGHT * 3.6 + DOWN * .1, 4.2, 4.6)
        beat(self, FadeIn(g), t=.5, rt=.4)
        p = VGroup(pole(ax, -1, 2, GRN), pole(ax, -1, -2, GRN))
        beat(self, Create(p), FadeIn(kr("복소수", 40, GRN).next_to(r, DOWN, .5)), t=1.2, rt=.6)
        fill(self, p, GRN)


class C3(Scene):
    """완전제곱: (s+1)^2 + 2^2."""
    def construct(self):
        self.add(step_tag(3, GRN))
        a = tex(r"s^2 + 2s + 5", 72).shift(UP * 1.6)
        beat(self, FadeIn(a), t=.8, rt=.4)
        b = tex(r"= (s^2 + 2s + 1) + 4", 64, MUTE).next_to(a, DOWN, .5)
        beat(self, Write(b), t=1.2, rt=.8)
        c = tex(r"= (s+1)^2 + 2^2", 80, GRN).next_to(b, DOWN, .6)
        beat(self, Write(c), t=1.2, rt=.8)
        lab = kr("완전제곱", 44, YEL).to_edge(DOWN, buff=.5)
        beat(self, FadeIn(lab), t=.8, rt=.4)
        fill(self, c, GRN)


class C4(Scene):
    """표: 분자 s+a → cos, ω → sin."""
    def construct(self):
        self.add(step_tag(3, GRN))
        r1 = tex(r"\frac{s+a}{(s+a)^2+\omega^2} \;\to\; e^{-at}\cos\omega t", 58, BLU)
        r2 = tex(r"\frac{\omega}{(s+a)^2+\omega^2} \;\to\; e^{-at}\sin\omega t", 58, ORG)
        tb = VGroup(r1, r2).arrange(DOWN, buff=.7).shift(UP * .2)
        beat(self, FadeIn(r1, shift=UP * .2), t=1.4, rt=.5)
        beat(self, FadeIn(VGroup(kr("분자 s+a → 코사인", 30, BLU)).next_to(r1, UP, .2)), t=.9, rt=.4)
        beat(self, FadeIn(r2, shift=UP * .2), t=1.4, rt=.5)
        beat(self, FadeIn(kr("분자 ω → 사인", 30, ORG).next_to(r2, DOWN, .25)), t=.9, rt=.4)
        fill(self, tb)


class C5(Scene):
    """(s+1)/((s+1)^2+4) → e^-t cos 2t + 그래프(포락선)."""
    def construct(self):
        self.add(step_tag(3, GRN))
        e = tex(r"\frac{s+1}{(s+1)^2+4} \;\to\; e^{-t}\cos 2t", 58, YEL).to_edge(UP, buff=.8)
        beat(self, Write(e), t=1.5, rt=1.0)
        ax, g = taxes(DOWN * 1.0, 10, 4.2, 5, -1.1, 1.2)
        beat(self, FadeIn(g), t=.5, rt=.4)
        env = VGroup(ax.plot(lambda t: np.exp(-t), x_range=[0, 5, .02], color=MUTE, stroke_width=3).set_stroke(opacity=.7),
                     ax.plot(lambda t: -np.exp(-t), x_range=[0, 5, .02], color=MUTE, stroke_width=3).set_stroke(opacity=.7))
        cur = ax.plot(f_cplx, x_range=[0, 5, .01], color=GRN, stroke_width=7)
        beat(self, Create(cur), t=1.8, rt=1.6)
        beat(self, Create(env), FadeIn(kr("감쇠 진동", 36, GRN).move_to(ax.c2p(3.6, .8))), t=1.0, rt=.6)
        fill(self, cur, GRN)


class C6(Scene):
    """실수부 → 포락선(줄어드는 빠르기), 허수부 → 진동 빠르기."""
    def construct(self):
        self.add(step_tag(3, GRN))
        p = MathTex(r"s = ", r"-1", r"\pm", r"j2", color=INK, font_size=80).to_edge(UP, buff=.5)
        beat(self, FadeIn(p), t=.8, rt=.4)
        b1 = SurroundingRectangle(p[1], color=ORG, buff=.12); b2 = SurroundingRectangle(p[3], color=BLU, buff=.12)
        ax, g = taxes(DOWN * 1.3, 10, 3.8, 5, -1.1, 1.2)
        self.add(g, ax.plot(f_cplx, x_range=[0, 5, .01], color=GRN, stroke_width=5))
        env = ax.plot(lambda t: np.exp(-t), x_range=[0, 5, .02], color=ORG, stroke_width=6)
        beat(self, Create(b1), Create(env), FadeIn(kr("줄어드는 빠르기", 34, ORG).move_to(ax.c2p(2.6, .75))), t=1.6, rt=1.0)
        per = DoubleArrow(ax.c2p(0, -1.0), ax.c2p(PI, -1.0), buff=0, color=BLU, tip_length=.16)
        beat(self, Create(b2), GrowFromCenter(per), FadeIn(kr("진동 빠르기", 34, BLU).next_to(per, UP, .15)), t=1.6, rt=.8)
        fill(self, VGroup(b1, b2))


class C7(Scene):
    """s+3 = (s+1) + 2 → cos + sin."""
    def construct(self):
        self.add(step_tag(3, GRN))
        a = tex(r"\frac{s+3}{(s+1)^2+4}", 64).shift(UP * 2.0)
        beat(self, FadeIn(a), t=.9, rt=.4)
        b = MathTex(r"= \frac{s+1}{(s+1)^2+4}", r"+", r"\frac{2}{(s+1)^2+4}", color=INK, font_size=56)
        b[0].set_color(BLU); b[2].set_color(ORG)
        beat(self, Write(b), t=1.5, rt=1.0)
        c = MathTex(r"e^{-t}\cos 2t", r"+", r"e^{-t}\sin 2t", color=INK, font_size=62).shift(DOWN * 2.0)
        c[0].set_color(BLU); c[2].set_color(ORG)
        beat(self, TransformFromCopy(b[0], c[0]), t=1.0, rt=.7)
        beat(self, FadeIn(c[1]), TransformFromCopy(b[2], c[2]), t=1.0, rt=.7)
        fill(self, c)


class C8(Scene):
    """부족감쇠: 출렁이면서 줄어듦."""
    def construct(self):
        self.add(step_tag(3, GRN))
        c = rlc_series(LEFT * 3.8 + UP * .6, 4.4, 1.8)
        beat(self, Create(c), t=1.0, rt=.7)
        ax, g = taxes(RIGHT * 2.8 + DOWN * .2, 6.6, 3.8, 6, -.8, 1.15, "v(t)")
        beat(self, FadeIn(g), t=.5, rt=.4)
        und = ax.plot(lambda t: np.exp(-.5 * t) * np.cos(2.5 * t), x_range=[0, 6, .01], color=GRN, stroke_width=8)
        beat(self, Create(und), t=1.8, rt=1.5)
        lab = kr("부족감쇠", 48, GRN).next_to(c, DOWN, .7)
        beat(self, FadeIn(lab), FadeIn(kr("출렁이며 감소", 30, MUTE).next_to(lab, DOWN, .2)), t=1.0, rt=.4)
        fill(self, und, GRN)


# ================= 중간 정리 =================
class M1(Scene):
    """극점 = 분모의 근이 답의 모양을 정함."""
    def construct(self):
        h = kr("중간 정리", 40, MUTE).to_edge(UP, buff=.5)
        self.add(h)
        F = frac("N(s)", ["D(s)"], 72, INK).shift(LEFT * 3.6)
        beat(self, FadeIn(F), t=.8, rt=.4)
        b = SurroundingRectangle(F[2], color=YEL, buff=.12)
        beat(self, Create(b), FadeIn(kr("분모의 근 = 극점", 34, YEL).next_to(F, DOWN, .5)), t=1.1, rt=.5)
        ax, g = splane(RIGHT * 3.2, 4.4, 4.4)
        beat(self, FadeIn(g), t=.5, rt=.4)
        ps = VGroup(pole(ax, -1, 0, BLU), pole(ax, -2, 0, BLU), pole(ax, -1.5, 2, GRN), pole(ax, -1.5, -2, GRN))
        beat(self, LaggedStart(*[Create(p) for p in ps], lag_ratio=.25), t=1.4, rt=1.0)
        fill(self, ps)


def shape_panel(i, w=3.8):
    names = [("실수 극점", BLU, f_distinct, (-.1, 1.2)), ("중근", PUR, lambda t: 2.4 * f_double(t), (-.1, 1.2)), ("복소 극점", GRN, f_cplx, (-1.1, 1.2))]
    n, c, f, yr = names[i]
    ax = Axes(x_range=[0, 5, 1], y_range=[yr[0], yr[1], .5], x_length=w, y_length=2.4, tips=False,
              axis_config={"color": MUTE, "stroke_width": 2, "include_ticks": False})
    cur = ax.plot(f, x_range=[0, 5, .01], color=c, stroke_width=6)
    return VGroup(kr(n, 34, c).next_to(ax, UP, .25), ax, cur)


class M2(Scene):
    def construct(self):
        self.add(kr("중간 정리", 40, MUTE).to_edge(UP, buff=.5))
        ax, g = splane(LEFT * 3.4, 4.0, 4.0)
        beat(self, FadeIn(g), Create(pole(ax, -1, 0, BLU)), Create(pole(ax, -2, 0, BLU)), t=1.0, rt=.6)
        p = shape_panel(0, 5.2).shift(RIGHT * 3.0)
        beat(self, FadeIn(p[0]), FadeIn(p[1]), t=.6, rt=.4)
        beat(self, Create(p[2]), t=1.4, rt=1.2)
        beat(self, FadeIn(kr("진동 없이 감소", 34, YEL).next_to(p, DOWN, .4)), t=.8, rt=.4)
        fill(self, p[2], BLU)


class M3(Scene):
    def construct(self):
        self.add(kr("중간 정리", 40, MUTE).to_edge(UP, buff=.5))
        a = shape_panel(1, 5.0).shift(LEFT * 3.2 + DOWN * .2); b = shape_panel(2, 5.0).shift(RIGHT * 3.2 + DOWN * .2)
        beat(self, FadeIn(a[0]), FadeIn(a[1]), Create(a[2]), t=1.4, rt=1.0)
        beat(self, FadeIn(kr("t가 붙음", 34, PUR).next_to(a, DOWN, .35)), t=.8, rt=.4)
        beat(self, FadeIn(b[0]), FadeIn(b[1]), Create(b[2]), t=1.4, rt=1.0)
        beat(self, FadeIn(kr("출렁이며 감소", 34, GRN).next_to(b, DOWN, .35)), t=.8, rt=.4)
        fill(self, VGroup(a, b))


class M4(Scene):
    """3종 한눈에 + '계산 전에 모양을 안다'."""
    def construct(self):
        ps = VGroup(*[shape_panel(i, 3.6) for i in range(3)]).arrange(RIGHT, buff=.6).shift(UP * .5)
        for p in ps:
            beat(self, FadeIn(p), t=.8, rt=.4)
        lab = card(kr("극점 위치 → 답의 모양", 42, YEL), YEL, .3).to_edge(DOWN, buff=.6)
        beat(self, FadeIn(lab, shift=UP * .3), t=1.2, rt=.5)
        fill(self, lab)


# ================= STEP 4 검산 =================
class V1(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        a = tex(r"f(t) = 2e^{-t} - e^{-2t}", 70, GRN).shift(UP * .6)
        beat(self, FadeIn(a), t=.9, rt=.4)
        q = kr("맞았을까?", 52, YEL).next_to(a, DOWN, .8)
        beat(self, FadeIn(q, scale=1.2), t=1.0, rt=.4)
        fill(self, q)


class V2(Scene):
    """초기값 정리."""
    def construct(self):
        self.add(step_tag(4, ORG))
        h = kr("초기값 정리", 48, ORG).to_edge(UP, buff=.8)
        beat(self, FadeIn(h), t=.8, rt=.4)
        e = tex(r"f(0^+) = \lim_{s\to\infty} s\,F(s)", 80, INK).shift(UP * .1)
        beat(self, Write(e), t=1.6, rt=1.1)
        b = Brace(e, DOWN, color=MUTE)
        beat(self, GrowFromCenter(b), FadeIn(kr("s를 무한대로", 34, MUTE).next_to(b, DOWN, .2)), t=1.1, rt=.5)
        fill(self, e, ORG)


class V3(Scene):
    """예제 sF(s) → s→∞ → 1."""
    def construct(self):
        self.add(step_tag(4, ORG))
        e = tex(r"s\,F(s) = \frac{s(s+3)}{(s+1)(s+2)}", 64).shift(UP * 1.4)
        beat(self, Write(e), t=1.4, rt=1.0)
        a = tex(r"= \frac{s^2+3s}{s^2+3s+2}", 58, MUTE).next_to(e, DOWN, .5)
        beat(self, FadeIn(a), t=1.1, rt=.5)
        r = tex(r"\xrightarrow{\;s\to\infty\;} 1", 76, ORG).next_to(a, DOWN, .5)
        beat(self, Write(r), t=1.2, rt=.8)
        fill(self, r, ORG)


class V4(Scene):
    """f(0) = 2 − 1 = 1 ✔."""
    def construct(self):
        self.add(step_tag(4, ORG))
        e = tex(r"f(0) = 2e^{0} - e^{0}", 64).shift(UP * 1.3)
        beat(self, Write(e), t=1.2, rt=.8)
        r = tex(r"= 2 - 1 = 1", 72, GRN).next_to(e, DOWN, .5)
        beat(self, Write(r), t=1.0, rt=.7)
        ok = kr("✔ 맞음", 64, GRN).next_to(r, DOWN, .6)
        beat(self, FadeIn(ok, scale=1.4), t=1.0, rt=.4)
        fill(self, ok, GRN)


class V5(Scene):
    """최종값 정리."""
    def construct(self):
        self.add(step_tag(4, ORG))
        h = kr("최종값 정리", 48, ORG).to_edge(UP, buff=.8)
        beat(self, FadeIn(h), t=.8, rt=.4)
        e = tex(r"f(\infty) = \lim_{s\to 0} s\,F(s)", 80, INK).shift(UP * .1)
        beat(self, Write(e), t=1.6, rt=1.1)
        b = Brace(e, DOWN, color=MUTE)
        beat(self, GrowFromCenter(b), FadeIn(kr("s를 0으로", 34, MUTE).next_to(b, DOWN, .2)), t=1.1, rt=.5)
        fill(self, e, ORG)


class V6(Scene):
    """s→0 → 0, 그래프 꼬리도 0."""
    def construct(self):
        self.add(step_tag(4, ORG))
        e = tex(r"\lim_{s\to 0}\frac{s(s+3)}{(s+1)(s+2)} = 0", 58).to_edge(UP, buff=.9)
        beat(self, Write(e), t=1.4, rt=1.0)
        ax, g = taxes(DOWN * 1.0, 9.4, 3.8, 6, -.1, 1.25)
        cur = ax.plot(f_distinct, x_range=[0, 6, .02], color=GRN, stroke_width=6)
        beat(self, FadeIn(g), Create(cur), t=1.4, rt=1.1)
        d = Dot(ax.c2p(5.8, f_distinct(5.8)), .13, color=YEL)
        beat(self, FadeIn(d, scale=1.5), FadeIn(kr("→ 0 ✔", 40, GRN).next_to(d, UP, .3).shift(LEFT * .5)), t=1.0, rt=.4)
        fill(self, d)


class V7(Scene):
    """조건: 극점이 전부 왼쪽 반평면. 오른쪽·허수축이면 X."""
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = splane(LEFT * 2.8 + DOWN * .2, 5.4, 5.0, (-3, 3), (-3, 3))
        beat(self, FadeIn(g), t=.5, rt=.4)
        lhp = Polygon(ax.c2p(-3, -3), ax.c2p(0, -3), ax.c2p(0, 3), ax.c2p(-3, 3), stroke_width=0, fill_color=GRN, fill_opacity=.18)
        beat(self, FadeIn(lhp), FadeIn(kr("왼쪽 반평면", 32, GRN).move_to(ax.c2p(-1.6, 2.4))), t=1.2, rt=.5)
        ok = kr("최종값 정리 ✔", 38, GRN).move_to(RIGHT * 3.8 + UP * 1.6)
        beat(self, Create(pole(ax, -1, 0, GRN)), Create(pole(ax, -2, 0, GRN)), FadeIn(ok), t=1.2, rt=.5)
        bad = VGroup(pole(ax, 1, 0, RED), pole(ax, 0, 2, RED), pole(ax, 0, -2, RED))
        no = kr("발산·계속 진동 ✕", 38, RED).move_to(RIGHT * 3.8 + DOWN * .2)
        beat(self, Create(bad), FadeIn(no), t=1.4, rt=.6)
        nf = kr("최종값 없음", 34, RED).next_to(no, DOWN, .3)
        beat(self, FadeIn(nf), t=.8, rt=.4)
        fill(self, lhp, GRN)


# ================= 정리 =================
class O1(Scene):
    def construct(self):
        st = [("F(s)", BLU), ("부분분수", PUR), ("변환표", ORG), ("f(t)", GRN)]
        cs = VGroup(*[card(kr(s, 40, c) if not s.endswith(")") else tex(s, 54, c), c, .3) for s, c in st]).arrange(RIGHT, buff=.8)
        cs.scale_to_fit_width(min(cs.width, 12.6))
        arrs = VGroup(*[Arrow(cs[i].get_right(), cs[i + 1].get_left(), buff=.1, color=MUTE) for i in range(3)])
        beat(self, FadeIn(cs[0]), t=.7, rt=.3)
        for i in range(3):
            beat(self, GrowArrow(arrs[i]), FadeIn(cs[i + 1], shift=RIGHT * .2), t=1.0, rt=.4)
        fill(self, cs[1], PUR)


class O2(Scene):
    def construct(self):
        items = [("서로 다른 극점", "가리기법", BLU), ("중근", "t가 붙음", PUR), ("복소 극점", "완전제곱", GRN)]
        cs = VGroup(*[card(VGroup(kr(a, 32, MUTE), kr(b, 42, c)).arrange(DOWN, buff=.3), c, .35) for a, b, c in items]).arrange(RIGHT, buff=.4)
        cs.scale_to_fit_width(min(cs.width, 12.6))
        for c in cs:
            beat(self, FadeIn(c, shift=UP * .3), t=1.3, rt=.4)
        fill(self, cs)


class O3(Scene):
    def construct(self):
        a = card(VGroup(kr("초기값", 32, ORG), tex(r"s\to\infty", 50)).arrange(DOWN, buff=.25), ORG, .35).shift(LEFT * 3)
        b = card(VGroup(kr("최종값", 32, ORG), tex(r"s\to 0", 50)).arrange(DOWN, buff=.25), ORG, .35).shift(RIGHT * 3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.4)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.4)
        ck = kr("✔ 검산", 56, GRN).shift(DOWN * 2.2)
        beat(self, FadeIn(ck, scale=1.3), t=.9, rt=.4)
        fill(self, ck, GRN)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("라플라스 · 극점 옮겨 보기", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55).shift(LEFT * 2.6)
        beat(self, FadeIn(t[0]), FadeIn(t[1][0]), t=.8, rt=.3)
        ax, g = splane(RIGHT * 4.2, 3.4, 3.6, (-3, 1), (-3, 3))
        self.add(g)
        k = ValueTracker(-2.2)
        p = always_redraw(lambda: VGroup(pole(ax, k.get_value(), 1.5, GRN if k.get_value() < 0 else RED), pole(ax, k.get_value(), -1.5, GRN if k.get_value() < 0 else RED)))
        self.add(p)
        for m in t[1][1:]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.2, rt=.4)
        self.play(k.animate.set_value(.6), run_time=2.0); self.play(k.animate.set_value(-1.5), run_time=1.4)
        fill(self, t, YEL)


class Next(Scene):
    """다음 편: 초기 조건 → s-영역 회로 (인덕터 = sL + Li(0) 전원)."""
    def construct(self):
        lab = kr("다음 편 · 초기 조건이 있는 s-영역 회로", 38, YEL).to_edge(UP, buff=.7)
        beat(self, FadeIn(lab), t=.9, rt=.4)
        l = coil((-4.6, 1.0), (-4.6, -1.4), GRN)
        beat(self, Create(l), FadeIn(tex(r"i(0)", 44, GRN).next_to(l, LEFT, .3)), t=1.0, rt=.5)
        a = Arrow(LEFT * 3.4, LEFT * 1.6, buff=0, color=YEL)
        r = VGroup(tex("sL", 56, GRN), tex("+", 50), tex(r"L\,i(0)", 56, ORG)).arrange(RIGHT, buff=.25).next_to(a, RIGHT, .4)
        beat(self, GrowArrow(a), FadeIn(r[0]), t=1.0, rt=.5)
        beat(self, FadeIn(r[1]), FadeIn(r[2], shift=UP * .2), t=1.0, rt=.5)
        pl = kr("재생목록 · 라플라스 심화", 34, MUTE).to_edge(DOWN, buff=.6)
        beat(self, FadeIn(pl), t=.8, rt=.4)
        fill(self, r[2], ORG)


# ================= 쇼츠 전용 =================
class AQ(Scene):
    """손으로 가리면 3초."""
    def construct(self):
        F = F1(96).shift(UP * .6)
        beat(self, FadeIn(F), t=.8, rt=.4)
        hc = hand_cover(F[2][0], BLU)
        beat(self, FadeIn(hc, shift=DOWN * .4), t=.9, rt=.5)
        t = kr("3초 컷", 64, YEL).next_to(F, DOWN, .8)
        beat(self, FadeIn(t, scale=1.4), t=1.0, rt=.4)
        fill(self, t)


class BQ(Scene):
    def construct(self):
        F = frac("1", ["(s+1)^2"], 96, PUR).shift(LEFT * 3)
        beat(self, FadeIn(F), t=.8, rt=.4)
        a = Arrow(LEFT * .9, RIGHT * .9, buff=0, color=YEL, stroke_width=7)
        r = tex(r"?\cdot e^{-t}", 90, GRN).shift(RIGHT * 3)
        beat(self, GrowArrow(a), FadeIn(r), t=1.0, rt=.5)
        t = tex(r"t", 110, YEL).move_to(r[0][0])
        beat(self, Transform(r[0][0], t), t=1.0, rt=.6)
        fill(self, r, YEL)


class CQ(Scene):
    def construct(self):
        e = tex(r"\frac{1}{s^2+2s+5}", 84).shift(UP * 1.6)
        beat(self, FadeIn(e), t=.8, rt=.4)
        ax, g = taxes(DOWN * 1.4, 10, 3.4, 5, -1.1, 1.2)
        cur = ax.plot(f_cplx, x_range=[0, 5, .01], color=GRN, stroke_width=7)
        beat(self, FadeIn(g), Create(cur), t=1.6, rt=1.4)
        fill(self, cur, GRN)


class DQ(Scene):
    def construct(self):
        a = tex(r"f(t) = 2e^{-t} - e^{-2t}", 72, GRN).shift(UP * 1.0)
        beat(self, FadeIn(a), t=.8, rt=.4)
        ck = kr("2초 검산 ✔", 64, YEL).shift(DOWN * 1.2)
        beat(self, FadeIn(ck, scale=1.4), t=1.0, rt=.4)
        fill(self, ck)


class EQ(Scene):
    def construct(self):
        fs = VGroup(tex(r"\frac{1}{(s+1)(s+2)}", 52, BLU), tex(r"\frac{1}{(s+1)^2}", 52, PUR), tex(r"\frac{1}{s^2+2s+5}", 52, GRN)).arrange(RIGHT, buff=.9).shift(UP * 1.6)
        beat(self, FadeIn(fs[0]), FadeIn(fs[1]), FadeIn(fs[2]), t=.8, rt=.4)
        ps = VGroup(*[shape_panel(i, 3.4)[1:] for i in range(3)])
        for p, f in zip(ps, fs):
            p.next_to(f, DOWN, .6)
        beat(self, *[Create(p[1]) for p in ps], *[FadeIn(p[0]) for p in ps], t=1.6, rt=1.3)
        fill(self, ps)
