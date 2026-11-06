# 페이저·임피던스(정현파 정상상태) 롱폼 모션그래픽. 16:9, 핵심은 가운데에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(long.json 에서 그 문장 시작에 붙임). 연산증폭기 편(opamp/manim/scenes.py) 형식을 따른다.
# 끝까지 보게 만드는 4원칙: 1.5~2.5초마다 화면에 새 요소(내용으로 변화, 전환·반복 확대 없음), 4초 넘게 멈춘 화면 없음.
# 검산: ω=1000, R=3Ω, L=4mH → j4Ω, Z=3+j4=5∠53.13°, I=2∠−53.13°, V_R=6∠−53.13°, V_L=8∠36.87°, 합 10∠0°.
#   C: −j4Ω(250μF) → Z=3, I=3.33, V_L=j13.3, V_C=−j13.3, V_R=10.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>
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



def U(deg): return np.array([np.cos(deg * DEGREES), np.sin(deg * DEGREES), 0.0])


def sine(pt, amp, cycles, length, col, phase=0, n=200, sw=5, f=np.cos):
    """가운데 pt, 가로 length, 진폭 amp, cycles 주기. f=np.cos 면 왼쪽 끝에서 꼭대기(위상 0)."""
    p = P3(pt); xs = np.linspace(-length / 2, length / 2, n)
    return VMobject(color=col, stroke_width=sw).set_points_smoothly(
        [p + np.array([x, amp * f(2 * PI * cycles * (x + length / 2) / length + phase), 0]) for x in xs])


def taxis(o, length=8.0, h=1.6, lab="t"):
    o = P3(o)
    g = VGroup(Arrow(o + LEFT * .2, o + RIGHT * (length + .3), buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.03),
               Line(o + DOWN * h, o + UP * h, color=MUTE, stroke_width=3))
    g.add(tex(lab, 34, MUTE).next_to(g[0].get_end(), DOWN, .1))
    return g


def plane(o=ORIGIN, r=2.6, lab=True):
    """복소평면: 실수축(Re)·허수축(Im)."""
    o = P3(o)
    g = VGroup(Arrow(o + LEFT * r * .35, o + RIGHT * r, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.06),
               Arrow(o + DOWN * r, o + UP * r, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.06))
    if lab:
        g.add(kr("실수", 24, MUTE).next_to(g[0].get_end(), DOWN, .12), kr("허수 j", 24, MUTE).next_to(g[1].get_end(), RIGHT, .12))
    return g


def vec(a, b, c=YEL, sw=7):
    return Arrow(P3(a), P3(b), buff=0, color=c, stroke_width=sw, max_tip_length_to_length_ratio=.18, max_stroke_width_to_length_ratio=12)


def angle_arc(o, a0, a1, r=.7, c=YEL):
    return Arc(radius=r, start_angle=a0 * DEGREES, angle=(a1 - a0) * DEGREES, arc_center=P3(o), color=c, stroke_width=4)


def right_mark(p, u, v, s=.28, c=INK):
    p = P3(p); u = P3(u) / np.linalg.norm(P3(u)); v = P3(v) / np.linalg.norm(P3(v))
    return VMobject(color=c, stroke_width=3).set_points_as_corners([p + u * s, p + u * s + v * s, p + v * s])


def series(o=ORIGIN, W=8.0, H=2.6, withC=False, src_lab=r"10\angle 0^\circ\,\mathrm{V}", rl=r"3\,\Omega", ll=r"4\,\mathrm{mH}", cl=r"-j4\,\Omega"):
    """직렬 R-L(-C) 회로. 반환 dict: g, src, R, L, C, lr, ll, lc, ls, xs, yt, yb."""
    o = P3(o); x0, x1 = o[0] - W / 2, o[0] + W / 2; yt, yb = o[1] + H / 2, o[1] - H / 2
    s = acsrc((x0, o[1]), YEL)
    n = 4 if withC else 3
    xs = np.linspace(x0, x1, n)
    R = resistor((xs[0], yt), (xs[1], yt), BLU); L = coil((xs[1], yt), (xs[2], yt), GRN)
    g = VGroup(s, wire((x0, o[1] + .55), (x0, yt)), wire((x0, o[1] - .55), (x0, yb)), R, L)
    D = dict(src=s, R=R, L=L, xs=xs, yt=yt, yb=yb, x0=x0, x1=x1)
    if withC:
        C = capacitor((xs[2], yt), (xs[3], yt), ORG)[0]; g.add(C); D["C"] = C
        D["lc"] = tex(cl, 40, ORG).next_to(C, UP, .45)
    g.add(wire((x1, yt), (x1, yb)), wire((x0, yb), (x1, yb)))
    D["lr"] = tex(rl, 40, BLU).next_to(R, UP, .35); D["ll"] = tex(ll, 40, GRN).next_to(L, UP, .35)
    D["ls"] = tex(src_lab, 38, YEL).next_to(s, LEFT, .25)
    D["g"] = g
    return D


def meter(m, txt, c, side=DOWN, size=40):
    return card(tex(txt, size, c), c, .14).next_to(m, side, .35)


# ================= 인트로 =================
class Hook(Scene):
    """저항 6V, 코일 8V, 전원 10V → 6+8=10?"""
    def construct(self):
        D = series(UP * .5, 7.0, 2.4, src_lab=r"10\,\mathrm{V}")
        beat(self, FadeIn(D["g"]), FadeIn(D["ls"]), t=1.0, rt=.6)
        m1 = card(tex(r"6\,\mathrm{V}", 50, BLU), BLU, .15).next_to(D["R"], UP, .4)
        m2 = card(tex(r"8\,\mathrm{V}", 50, GRN), GRN, .15).next_to(D["L"], UP, .4)
        beat(self, FadeIn(m1, shift=DOWN * .2), t=1.0, rt=.4)
        beat(self, FadeIn(m2, shift=DOWN * .2), t=1.0, rt=.4)
        q = tex(r"6 + 8 = 10\;?", 90, YEL).move_to(DOWN * 2.5)
        beat(self, Write(q), t=1.0, rt=.6)
        pulse(self, q, t=1.6)


class Goal(Scene):
    """페이저: 미분방정식 대신 옴의 법칙."""
    def construct(self):
        o = LEFT * 3.6 + UP * .9
        P = plane(o, 1.6, lab=False)
        beat(self, FadeIn(P), t=.6, rt=.4)
        a = ValueTracker(20)
        arr = always_redraw(lambda: vec(o, o + 1.4 * U(a.get_value()), YEL))
        self.add(arr)
        t = VGroup(kr("페이저", 64, YEL), kr("Phasor · 회전하는 화살표", 30, MUTE)).arrange(DOWN, buff=.2).next_to(P, RIGHT, 1.0)
        self.play(a.animate.set_value(200), FadeIn(t, shift=LEFT * .3), run_time=1.4, rate_func=linear)
        c1 = card(VGroup(kr("미분방정식", 36, MUTE), Cross(stroke_color=RED, stroke_width=6).scale(.3)).arrange(RIGHT, buff=.3), "#2a2e37")
        c2 = card(VGroup(kr("옴의 법칙 하나로", 36, INK), tex(r"V = ZI", 50, YEL)).arrange(RIGHT, buff=.3), YEL)
        VGroup(c1, c2).arrange(RIGHT, buff=.6).shift(DOWN * 2.0)
        self.play(a.animate.set_value(380), FadeIn(c1, shift=UP * .3), run_time=1.2, rate_func=linear)
        self.play(a.animate.set_value(560), FadeIn(c2, shift=UP * .3), run_time=1.2, rate_func=linear)
        self.play(a.animate.set_value(740), Circumscribe(c2, color=YEL, fade_out=True), run_time=1.4, rate_func=linear)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "정현파", BLU), ("2", "페이저", PUR), ("3", "임피던스", GRN), ("4", "옴의 법칙", ORG), ("5", "공진", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 36, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.2, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.8, rt=1.0)


# ================= STEP 1 정현파 =================
W_O = LEFT * 4.6 + DOWN * .6; W_L = 9.0; W_A = 1.5


def wave_base(sc, n=1):
    sc.add(step_tag(n))
    ax = taxis(W_O, W_L, 1.9)
    w = sine(W_O + RIGHT * W_L / 2, W_A, 2, W_L, BLU)
    return ax, w


class W1(Scene):
    def construct(self):
        ax, w = wave_base(self)
        beat(self, FadeIn(ax), t=.7, rt=.4)
        beat(self, Create(w), t=1.6, rt=1.4)
        f = tex(r"v(t) = V_m \cos(\omega t + \phi)", 60, INK).to_edge(UP, buff=.7)
        beat(self, Write(f), t=1.6, rt=.8)
        pulse(self, f, t=1.4)


def wfm():
    return tex(r"v(t) = V_m \cos(\omega t + \phi)", 60, INK).to_edge(UP, buff=.7)


class W2(Scene):
    def construct(self):
        ax, w = wave_base(self); f = wfm(); self.add(ax, w, f)
        pk = W_O + UP * W_A
        br = BraceBetweenPoints(W_O, pk, LEFT, color=YEL).shift(LEFT * .1)
        beat(self, f[0][5:7].animate.set_color(YEL), t=.8, rt=.4)
        beat(self, GrowFromCenter(br), FadeIn(tex("V_m", 48, YEL).next_to(br, LEFT, .15)), t=1.2, rt=.5)
        d = Dot(pk, color=YEL, radius=.1)
        beat(self, FadeIn(d, scale=2), FadeIn(kr("진폭 = 꼭대기 높이", 34, YEL).next_to(pk, UR, .2)), t=1.6, rt=.5)


class W3(Scene):
    def construct(self):
        ax, w = wave_base(self); f = wfm(); self.add(ax, w, f)
        beat(self, f[0][11:13].animate.set_color(GRN), t=.7, rt=.4)
        T = W_L / 2
        br = BraceBetweenPoints(W_O + DOWN * 1.7, W_O + RIGHT * T + DOWN * 1.7, DOWN, color=GRN)
        beat(self, GrowFromCenter(br), FadeIn(kr("한 바퀴 = 2π", 32, GRN).next_to(br, DOWN, .12)), t=1.4, rt=.5)
        e = tex(r"\omega = 2\pi f", 60, GRN).move_to(RIGHT * 3.6 + DOWN * 2.6)
        beat(self, Write(e), t=1.4, rt=.6)
        u = kr("rad/s", 32, MUTE).next_to(e, RIGHT, .3)
        beat(self, FadeIn(u), t=1.2, rt=.4)


class W4(Scene):
    def construct(self):
        ax, w = wave_base(self); f = wfm(); self.add(ax, w, f)
        beat(self, f[0][-2].animate.set_color(ORG), t=.7, rt=.4)
        w2 = sine(W_O + RIGHT * W_L / 2, W_A, 2, W_L, ORG, phase=PI / 3)
        beat(self, Create(w2), t=1.4, rt=1.0)
        T = W_L / 2
        p1 = W_O + RIGHT * T + UP * (W_A + .25); p0 = W_O + RIGHT * (T - T / 6) + UP * (W_A + .25)
        a = DoubleArrow(p0, p1, buff=0, color=ORG, stroke_width=5, tip_length=.2)
        beat(self, GrowFromCenter(a), FadeIn(tex(r"\phi", 50, ORG).next_to(a, UP, .1)), t=1.3, rt=.5)
        beat(self, FadeIn(kr("위상 = 얼마나 앞서 출발?", 34, ORG).to_edge(DOWN, buff=.35)), t=1.4, rt=.4)


class W5(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax = taxis(W_O, W_L, 1.9); self.add(ax)
        cs = [(BLU, 1.5, 0, "v"), (GRN, .9, -PI / 3, "i_1"), (ORG, 1.2, PI / 4, "i_2")]
        for c, a, ph, lab in cs:
            w = sine(W_O + RIGHT * W_L / 2, a, 2, W_L, c, phase=ph)
            beat(self, Create(w), FadeIn(tex(lab, 40, c).next_to(w.get_end(), RIGHT, .15)), t=1.2, rt=.8)
        s = card(VGroup(kr("모두 같은", 36, INK), tex(r"\omega", 56, YEL)).arrange(RIGHT, buff=.2), YEL).to_edge(UP, buff=.5)
        beat(self, FadeIn(s, shift=DOWN * .2), t=1.0, rt=.4)
        pulse(self, s, t=1.2)


class W6(Scene):
    def construct(self):
        self.add(step_tag(1))
        f = tex(r"V_m \cos(\omega t + \phi)", 72, INK).shift(UP * 1.6)
        beat(self, FadeIn(f), t=.8, rt=.4)
        beat(self, f[0][6].animate.set_color(MUTE).set_opacity(.35), f[0][7].animate.set_opacity(.35), t=1.0, rt=.5)
        c1 = card(VGroup(kr("크기", 46, BLU), tex("V_m", 56, BLU)).arrange(DOWN, buff=.2), BLU)
        c2 = card(VGroup(kr("위상", 46, ORG), tex(r"\phi", 56, ORG)).arrange(DOWN, buff=.2), ORG)
        VGroup(c1, c2).arrange(RIGHT, buff=1.4).shift(DOWN * 1.2)
        beat(self, FadeIn(c1, shift=UP * .3), t=1.1, rt=.4)
        beat(self, FadeIn(c2, shift=UP * .3), t=1.1, rt=.4)
        pulse(self, VGroup(c1, c2), t=1.4)


# ================= STEP 2 페이저 =================
P_O = LEFT * 4.3 + DOWN * .3; P_R = 1.5; P_X = LEFT * 2.0 + DOWN * .3; P_L = 7.2


def spin_trace(sc, t0, t1, rt, extra=None, step=2):
    """왼쪽 원 위 회전 화살표 + 오른쪽에 끝 높이를 따라 그리는 사인파. t 는 회전 각(라디안)."""
    a = ValueTracker(t0)
    circ = Circle(P_R, color="#2a2e37", stroke_width=3).move_to(P_O)
    ax = taxis(P_X, P_L, 1.8)
    arr = always_redraw(lambda: vec(P_O, P_O + P_R * np.array([np.cos(a.get_value()), np.sin(a.get_value()), 0]), YEL))
    k = P_L / (4 * PI)           # 각 1 rad → 가로 k

    def tr():
        ts = np.linspace(0, max(a.get_value(), 1e-3), 120)
        return VMobject(color=BLU, stroke_width=5).set_points_smoothly([P_X + np.array([t * k, P_R * np.sin(t), 0]) for t in ts])
    trace = always_redraw(tr)
    hl = always_redraw(lambda: DashedLine(P_O + P_R * np.array([np.cos(a.get_value()), np.sin(a.get_value()), 0]),
                                          P_X + np.array([a.get_value() * k, P_R * np.sin(a.get_value()), 0]), color=MUTE, stroke_width=2))
    return a, circ, ax, arr, trace, hl


class PH1(Scene):
    def construct(self):
        self.add(step_tag(2))
        a, circ, ax, arr, trace, hl = spin_trace(self, 0, 0, 0)
        beat(self, FadeIn(circ), FadeIn(ax), t=.6, rt=.4)
        self.add(arr)
        lab = kr("회전하는 화살표", 36, YEL).next_to(circ, UP, .3)
        self.play(a.animate.set_value(PI / 2), FadeIn(lab), run_time=1.2, rate_func=linear)
        self.add(trace, hl)
        self.play(a.animate.set_value(2.5 * PI), run_time=3.0, rate_func=linear)


class PH2(Scene):
    def construct(self):
        self.add(step_tag(2))
        a, circ, ax, arr, trace, hl = spin_trace(self, 0, 0, 0)
        a.set_value(.5 * PI)
        self.add(circ, ax, arr, trace, hl)
        tip = always_redraw(lambda: Dot(P_O + P_R * np.array([np.cos(a.get_value()), np.sin(a.get_value()), 0]), color=YEL, radius=.1))
        self.add(tip)
        lab = kr("끝의 높이 = 사인파", 38, BLU).to_edge(UP, buff=.6)
        self.play(a.animate.set_value(2 * PI), FadeIn(lab), run_time=2.0, rate_func=linear)
        self.play(a.animate.set_value(4 * PI), run_time=2.6, rate_func=linear)


class PH3(Scene):
    def construct(self):
        self.add(step_tag(2))
        o = LEFT * 2.2 + DOWN * .5
        P = plane(o, 2.6, lab=False)
        a = ValueTracker(0)
        arr = always_redraw(lambda: vec(o, o + 2.2 * U(a.get_value()), YEL))
        self.add(P, arr)
        sp = VGroup(kr("도는 속도", 34, MUTE), tex(r"\omega", 48, MUTE)).arrange(RIGHT, buff=.2).move_to(RIGHT * 4 + UP * 2.2)
        self.play(a.animate.set_value(390), FadeIn(sp), run_time=1.4, rate_func=linear)
        x = Cross(sp, stroke_color=RED, stroke_width=6)
        beat(self, Create(x), t=.8, rt=.4)
        arc = angle_arc(o, 0, 30, .8, ORG)
        L = BraceBetweenPoints(o, o + 2.2 * U(30), UP, color=BLU)
        beat(self, GrowFromCenter(L), FadeIn(kr("길이 = 크기", 32, BLU).next_to(L.get_center(), UL, .35)), t=1.2, rt=.5)
        beat(self, Create(arc), FadeIn(kr("각도 = 위상", 32, ORG).move_to(o + RIGHT * 1.6 + DOWN * .5)), t=1.4, rt=.5)


class PH4(Scene):
    def construct(self):
        self.add(step_tag(2))
        t1 = tex(r"10\cos(1000t)", 64, BLU).move_to(LEFT * 3.4 + UP * 1.4)
        beat(self, Write(t1), t=1.0, rt=.6)
        ar = Arrow(t1.get_right(), t1.get_right() + RIGHT * 1.6, buff=.2, color=MUTE)
        t2 = tex(r"10\angle 0^\circ", 76, YEL).next_to(ar, RIGHT, .3)
        beat(self, GrowArrow(ar), Write(t2), t=1.3, rt=.7)
        o = LEFT * 1.0 + DOWN * 2.0
        P = plane(o, 1.4, lab=False)
        v = vec(o, o + RIGHT * 2.6, YEL)
        beat(self, FadeIn(P), GrowArrow(v), FadeIn(tex("10", 40, YEL).next_to(v, UP, .1)), t=1.3, rt=.6)
        beat(self, FadeIn(kr("크기 10, 각도 0°", 34, MUTE).next_to(v, RIGHT, .4)), t=1.2, rt=.4)


class PH5(Scene):
    def construct(self):
        self.add(step_tag(2))
        o = LEFT * 1.2 + DOWN * 1.6
        P = plane(o, 3.4, lab=False); self.add(P)
        v = vec(o, o + RIGHT * 1.6, BLU)
        beat(self, GrowArrow(v), FadeIn(tex("V", 44, BLU).next_to(v, DOWN, .15)), t=1.0, rt=.5)
        e = tex(r"\frac{d}{dt} \;\rightarrow\; \times\, j\omega", 64, YEL).move_to(RIGHT * 3.8 + UP * 2.0)
        beat(self, Write(e), t=1.0, rt=.6)
        d = vec(o, o + UP * 3.0, GRN)
        beat(self, TransformFromCopy(v, d), FadeIn(tex(r"j\omega V", 44, GRN).next_to(d, LEFT, .15)), t=1.4, rt=.9)
        arc = angle_arc(o, 0, 90, .8, YEL)
        beat(self, Create(arc), FadeIn(tex(r"90^\circ", 44, YEL).next_to(o + U(45) * .8, UR, .1)), t=1.4, rt=.5)


class PH6(Scene):
    def construct(self):
        self.add(step_tag(2))
        a = tex(r"v = L\,\frac{di}{dt}", 72, INK).move_to(LEFT * 3.2 + UP * .6)
        beat(self, Write(a), t=1.0, rt=.6)
        ar = Arrow(LEFT * .7 + UP * .6, RIGHT * .9 + UP * .6, buff=0, color=YEL)
        b = tex(r"V = j\omega L\, I", 72, YEL).move_to(RIGHT * 3.4 + UP * .6)
        beat(self, GrowArrow(ar), TransformFromCopy(a, b), t=1.4, rt=.8)
        c1 = kr("미분방정식", 38, MUTE).next_to(a, DOWN, .6); c2 = kr("곱셈", 46, YEL).next_to(b, DOWN, .6)
        beat(self, FadeIn(c1), t=.9, rt=.4)
        beat(self, FadeIn(c2, shift=UP * .2), t=.9, rt=.4)
        pulse(self, VGroup(b, c2), t=1.2)


# ================= STEP 3 임피던스 =================
def zcard(sym, txt, c):
    return card(VGroup(sym, tex(txt, 56, c)).arrange(DOWN, buff=.35), c, .3)


def pv(o, ang_v, ang_i, lv=2.0, li=1.4):
    """페이저도: V(노랑)·I(하늘)."""
    v = vec(o, o + lv * U(ang_v), YEL); i = vec(o, o + li * U(ang_i), BLU, 6)
    sv = U(ang_v + 90) if ang_v == 0 else RIGHT
    si = DOWN if ang_i == ang_v else (U(ang_i + 90) if ang_i == 0 else RIGHT)
    return v, i, tex("V", 40, YEL).next_to(o + lv * U(ang_v) * .8, sv, .15), tex("I", 40, BLU).next_to(o + li * U(ang_i) * .8, si, .15)


class Z1(Scene):
    def construct(self):
        self.add(step_tag(3))
        z = tex(r"Z = \frac{V}{I}", 96, YEL).shift(UP * .6)
        beat(self, Write(z), t=1.2, rt=.7)
        s = kr("임피던스", 48, YEL).next_to(z, UP, .5)
        beat(self, FadeIn(s, shift=DOWN * .2), t=1.0, rt=.4)
        c = card(VGroup(kr("교류의 저항", 38, INK), kr("단위", 30, MUTE), tex(r"\Omega", 48, INK)).arrange(RIGHT, buff=.3), "#2a2e37").shift(DOWN * 2.0)
        beat(self, FadeIn(c, shift=UP * .3), t=1.4, rt=.5)
        pulse(self, z, t=1.2)


def comp_row(kind):
    if kind == "R":
        return resistor((-.9, 0), (.9, 0), BLU)
    if kind == "L":
        return coil((-.9, 0), (.9, 0), GRN)
    return capacitor((-.9, 0), (.9, 0), ORG)[0]


def zscene(sc, kind, ztxt, c, av, ai, msg):
    sc.add(step_tag(3))
    sym = comp_row(kind).move_to(LEFT * 4 + UP * 1.2)
    beat(sc, Create(sym), t=.7, rt=.5)
    z = tex(ztxt, 72, c).next_to(sym, DOWN, .6)
    beat(sc, Write(z), t=1.1, rt=.6)
    o = RIGHT * 1.6 + DOWN * .6
    P = plane(o, 2.4, lab=False)
    v, i, lv, li = pv(o, av, ai)
    beat(sc, FadeIn(P), GrowArrow(i), FadeIn(li), t=1.0, rt=.5)
    beat(sc, GrowArrow(v), FadeIn(lv), t=1.0, rt=.5)
    m = kr(msg, 36, c).to_edge(DOWN, buff=.4)
    if av != ai:
        arc = angle_arc(o, min(av, ai), max(av, ai), .7, INK)
        beat(sc, Create(arc), FadeIn(tex(r"90^\circ", 36, INK).next_to(o + .7 * U((av + ai) / 2), U((av + ai) / 2), .1)), FadeIn(m), t=1.4, rt=.5)
    else:
        beat(sc, FadeIn(m), t=1.4, rt=.4)


class Z2(Scene):
    def construct(self):
        zscene(self, "R", r"Z_R = R", BLU, 0, 0, "전압 · 전류 위상 같음")


class Z3(Scene):
    def construct(self):
        zscene(self, "L", r"Z_L = j\omega L", GRN, 90, 0, "전압이 90° 앞섬")


class Z4(Scene):
    def construct(self):
        zscene(self, "C", r"Z_C = \frac{1}{j\omega C}", ORG, 0, 90, "전류가 90° 앞섬")


class Z5(Scene):
    def construct(self):
        self.add(step_tag(3))
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 8, 1], x_length=8.5, y_length=4.4, tips=True,
                  axis_config=dict(color=MUTE, stroke_width=3, include_ticks=False)).shift(DOWN * .4)
        xl = VGroup(kr("주파수", 28, MUTE), tex(r"\omega", 36, MUTE)).arrange(RIGHT, buff=.1).next_to(ax.x_axis.get_end(), DOWN, .15)
        yl = tex(r"|Z|", 40, MUTE).next_to(ax.y_axis.get_end(), LEFT, .15)
        beat(self, Create(ax), FadeIn(xl), FadeIn(yl), t=.9, rt=.6)
        r = ax.plot(lambda x: 2.5, x_range=[0.05, 9.8], color=BLU, stroke_width=5)
        beat(self, Create(r), FadeIn(tex("R", 40, BLU).next_to(ax.c2p(8.8, 2.5), UP, .12)), t=1.0, rt=.6)
        l = ax.plot(lambda x: .75 * x, x_range=[0.05, 9.8], color=GRN, stroke_width=6)
        beat(self, Create(l), FadeIn(tex(r"\omega L", 40, GRN).next_to(l.get_end(), RIGHT, .1)), FadeIn(kr("커짐", 32, GRN).next_to(ax.c2p(7, 5.8), UL, .1)), t=1.4, rt=.8)
        c = ax.plot(lambda x: 4.0 / x, x_range=[0.52, 9.8], color=ORG, stroke_width=6)
        beat(self, Create(c), FadeIn(tex(r"\frac{1}{\omega C}", 40, ORG).next_to(c.get_end(), UR, .1)), FadeIn(kr("작아짐", 32, ORG).next_to(ax.c2p(1.2, 5.5), RIGHT, .25)), t=1.4, rt=.8)


class Z6(Scene):
    def construct(self):
        self.add(step_tag(3))
        t = VGroup(kr("직류", 44, YEL), tex(r"\omega = 0", 56, YEL)).arrange(RIGHT, buff=.3).to_edge(UP, buff=.6)
        beat(self, FadeIn(t), t=.8, rt=.4)
        L = coil((-5.2, .4), (-1.8, .4), GRN); C = capacitor((1.8, .4), (5.2, .4), ORG)
        beat(self, Create(L), Create(C[0]), t=.9, rt=.6)
        zl = tex(r"j\omega L = 0", 50, GRN).next_to(L, DOWN, .6); zc = tex(r"\frac{1}{j\omega C} = \infty", 50, ORG).next_to(C[0], DOWN, .45)
        beat(self, Write(zl), Write(zc), t=1.0, rt=.6)
        w = wire((-5.2, .4), (-1.8, .4), GRN, 6)
        beat(self, Transform(L, w), FadeIn(kr("전선", 44, GRN).next_to(w, UP, .35)), t=1.2, rt=.7)
        gap = VGroup(Line(P3((1.8, .4)), P3((3.2, .4)), color=ORG, stroke_width=6), Line(P3((3.8, .4)), P3((5.2, .4)), color=ORG, stroke_width=6))
        beat(self, Transform(C[0], gap), FadeIn(kr("끊긴 선", 44, ORG).next_to(gap, UP, .35)), t=1.4, rt=.7)


# ================= STEP 4 교류 옴의 법칙 =================
L_O = UP * 1.0


def circ4(sc, n=4, withC=False, **kw):
    sc.add(step_tag(n))
    D = series(L_O, 7.6, 2.0, withC=withC, **kw)
    return D


class L1(Scene):
    def construct(self):
        D = circ4(self)
        beat(self, FadeIn(D["g"]), t=.8, rt=.5)
        beat(self, FadeIn(D["ls"]), t=.8, rt=.3)
        beat(self, FadeIn(D["lr"]), t=.8, rt=.3)
        beat(self, FadeIn(D["ll"]), t=.8, rt=.3)
        w = tex(r"\omega = 1000\ \mathrm{rad/s}", 50, INK).move_to(DOWN * 1.6)
        beat(self, Write(w), t=1.0, rt=.5)
        c = kr("직류처럼 풀기", 40, YEL).to_edge(DOWN, buff=.4)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.4)


class L2(Scene):
    def construct(self):
        D = circ4(self); self.add(D["g"], D["ls"], D["lr"], D["ll"])
        e = tex(r"j\omega L = j \times 1000 \times 0.004", 54, GRN).move_to(DOWN * 1.4)
        beat(self, Write(e), t=1.4, rt=.8)
        r = tex(r"= j4\,\Omega", 70, GRN).next_to(e, DOWN, .35)
        beat(self, Write(r), t=1.2, rt=.5)
        n = tex(r"j4\,\Omega", 44, GRN).move_to(D["ll"])
        beat(self, Transform(D["ll"], n), t=1.2, rt=.6)
        pulse(self, r, t=1.0)


def zplane(o=RIGHT * .2 + DOWN * 2.6, s=.85):
    """Z 평면: 3 (실수), j4 (허수), 빗변 5."""
    o = P3(o)
    return o, s


class L3(Scene):
    def construct(self):
        self.add(step_tag(4))
        o = LEFT * 3.4 + DOWN * 2.2; s = .9
        P = plane(o, 4.6 * s + .6)
        beat(self, FadeIn(P), t=.5, rt=.3)
        r = vec(o, o + RIGHT * 3 * s, BLU)
        beat(self, GrowArrow(r), FadeIn(tex("3", 44, BLU).next_to(r, DOWN, .15)), t=1.0, rt=.5)
        l = vec(o + RIGHT * 3 * s, o + RIGHT * 3 * s + UP * 4 * s, GRN)
        beat(self, GrowArrow(l), FadeIn(tex("j4", 44, GRN).next_to(l, RIGHT, .15)), t=1.0, rt=.5)
        z = vec(o, o + RIGHT * 3 * s + UP * 4 * s, YEL, 8)
        beat(self, GrowArrow(z), FadeIn(tex("5", 50, YEL).next_to(z.get_center(), UL, .15)), t=1.0, rt=.5)
        arc = angle_arc(o, 0, 53.13, .9, YEL)
        beat(self, Create(arc), FadeIn(tex(r"53.1^\circ", 36, YEL).next_to(o + .9 * U(26), RIGHT, .1)), t=.9, rt=.4)
        e = VGroup(tex(r"Z = 3 + j4", 60, INK), tex(r"= 5\angle 53.1^\circ\,\Omega", 60, YEL)).arrange(DOWN, buff=.3, aligned_edge=LEFT).move_to(RIGHT * 3.4 + UP * .4)
        beat(self, Write(e[0]), t=.9, rt=.5)
        beat(self, Write(e[1]), t=1.2, rt=.6)


class L4(Scene):
    def construct(self):
        self.add(step_tag(4))
        e = tex(r"I = \frac{10\angle 0^\circ}{5\angle 53.1^\circ}", 64, INK).move_to(LEFT * 3.0 + UP * 1.6)
        beat(self, Write(e), t=1.2, rt=.7)
        r = tex(r"= 2\angle -53.1^\circ\ \mathrm{A}", 64, BLU).next_to(e, DOWN, .4, aligned_edge=LEFT)
        beat(self, Write(r), t=1.2, rt=.6)
        o = RIGHT * 3.0 + UP * .2
        P = plane(o, 2.8, lab=False)
        v = vec(o, o + RIGHT * 2.5, YEL); i = vec(o, o + 1.6 * U(-53.13), BLU)
        beat(self, FadeIn(P), GrowArrow(v), FadeIn(tex("V", 40, YEL).next_to(v, UP, .1)), t=.9, rt=.5)
        beat(self, GrowArrow(i), FadeIn(tex("I", 40, BLU).next_to(i.get_end(), DOWN, .1)), t=.9, rt=.5)
        arc = angle_arc(o, -53.13, 0, .8, BLU)
        beat(self, Create(arc), FadeIn(kr("53.1° 늦음", 34, BLU).move_to(o + RIGHT * 1.9 + DOWN * 1.1)), t=1.2, rt=.4)


class L5(Scene):
    def construct(self):
        D = circ4(self, src_lab=r"10\,\mathrm{V}", rl=r"3\,\Omega", ll=r"j4\,\Omega"); self.add(D["g"], D["ls"], D["lr"], D["ll"])
        i = tex(r"I = 2\,\mathrm{A}", 52, BLU).move_to(DOWN * .55)
        beat(self, FadeIn(i), t=.8, rt=.4)
        e1 = tex(r"V_R = 2 \times 3 = 6\,\mathrm{V}", 56, BLU).move_to(LEFT * 3.2 + DOWN * 2.0)
        e2 = tex(r"V_L = 2 \times 4 = 8\,\mathrm{V}", 56, GRN).move_to(RIGHT * 3.2 + DOWN * 2.0)
        beat(self, Write(e1), t=1.2, rt=.6)
        beat(self, Write(e2), t=1.2, rt=.6)
        m1 = card(tex(r"6\,\mathrm{V}", 44, BLU), BLU, .12).next_to(D["R"], DOWN, .3)
        m2 = card(tex(r"8\,\mathrm{V}", 44, GRN), GRN, .12).next_to(D["L"], DOWN, .3)
        beat(self, FadeIn(m1, shift=DOWN * .2), FadeIn(m2, shift=DOWN * .2), t=1.0, rt=.4)
        pulse(self, VGroup(m1, m2), t=1.2)


def kvl_tri(sc, o=LEFT * 2.6 + DOWN * 2.0, s=.42, big=False):
    """V_R(6∠−53.1°) + V_L(8∠36.9°) = 10∠0° 꼬리 물기."""
    o = P3(o)
    a = o + 6 * s * U(-53.13); b = a + 8 * s * U(36.87)
    vr = vec(o, a, BLU); vl = vec(a, b, GRN); vs = vec(o, b, YEL, 8)
    beat(sc, GrowArrow(vr), FadeIn(tex("6", 48, BLU).next_to(vr.get_center(), DL, .1)), t=1.0, rt=.5)
    beat(sc, GrowArrow(vl), FadeIn(tex("8", 48, GRN).next_to(vl.get_center(), DR, .1)), t=1.0, rt=.5)
    rm = right_mark(a, o - a, b - a, .3)
    beat(sc, Create(rm), t=.7, rt=.3)
    ten = tex("10", 72 if big else 56, YEL).next_to(vs, UP, .15)
    beat(sc, GrowArrow(vs), FadeIn(ten), t=1.1, rt=.6)
    return VGroup(vr, vl, vs, rm, ten)


class L6(Scene):
    def construct(self):
        self.add(step_tag(4))
        g = kvl_tri(self, LEFT * 4.4 + UP * .6, .5)
        e = tex(r"\sqrt{6^2 + 8^2} = 10", 60, YEL).move_to(RIGHT * 3.2 + UP * .8)
        beat(self, Write(e), t=1.0, rt=.6)
        k = card(VGroup(kr("KVL", 40, YEL), kr("페이저로 성립", 36, INK)).arrange(RIGHT, buff=.3), YEL).next_to(e, DOWN, .7)
        beat(self, FadeIn(k, shift=UP * .2), t=1.0, rt=.4)
        pulse(self, k, t=1.2)


# ================= STEP 5 커패시터와 공진 =================
def circ5(sc, **kw):
    sc.add(step_tag(5))
    return series(UP * .6, 9.0, 2.0, withC=True, src_lab=r"10\,\mathrm{V}", ll=r"j4\,\Omega", **kw)


class C1(Scene):
    def construct(self):
        self.add(step_tag(5))
        D = series(UP * .6, 9.0, 2.0, withC=True, src_lab=r"10\,\mathrm{V}", ll=r"j4\,\Omega")
        base = VGroup(*[m for m in D["g"] if m is not D["C"]])
        self.add(base, D["ls"], D["lr"], D["ll"])
        beat(self, Create(D["C"]), t=1.0, rt=.8)
        beat(self, FadeIn(D["lc"], shift=DOWN * .2), t=.9, rt=.4)
        e = tex(r"Z_C = \frac{1}{j\omega C} = -j4\,\Omega", 58, ORG).move_to(DOWN * 1.8)
        beat(self, Write(e), t=1.4, rt=.7)
        pulse(self, D["lc"], t=1.2, c=ORG)


class C2(Scene):
    def construct(self):
        self.add(step_tag(5))
        o = LEFT * 3.6 + DOWN * .2; s = .55
        P = plane(o, 2.8)
        beat(self, FadeIn(P), t=.4, rt=.3)
        l = vec(o, o + UP * 4 * s, GRN); c = vec(o + RIGHT * .12, o + RIGHT * .12 + DOWN * 4 * s, ORG)
        beat(self, GrowArrow(l), FadeIn(tex("+j4", 44, GRN).next_to(l, LEFT, .15)), t=.9, rt=.4)
        beat(self, GrowArrow(c), FadeIn(tex("-j4", 44, ORG).next_to(c, RIGHT, .15)), t=.9, rt=.4)
        e = tex(r"Z = 3 + j4 - j4", 62, INK).move_to(RIGHT * 2.8 + UP * 1.0)
        beat(self, Write(e), t=1.0, rt=.6)
        beat(self, FadeOut(l), FadeOut(c), t=.6, rt=.4)
        r = vec(o, o + RIGHT * 3 * s, BLU)
        beat(self, GrowArrow(r), FadeIn(tex("3", 44, BLU).next_to(r, DOWN, .15)), t=.8, rt=.4)
        z = tex(r"= 3\,\Omega", 80, YEL).next_to(e, DOWN, .4)
        beat(self, Write(z), t=1.2, rt=.5)


def ibar(x, v, c, lab, scale=.75, y0=-2.4, w=1.1):
    b = Rectangle(width=w, height=max(v * scale, .02), color=c, fill_color=c, fill_opacity=.85, stroke_width=0)
    b.move_to(P3((x, y0)) + UP * v * scale / 2)
    return b, tex(lab, 44, c).next_to(b, UP, .15)


class C3(Scene):
    def construct(self):
        self.add(step_tag(5))
        e = tex(r"I = \frac{10}{3} \approx 3.3\,\mathrm{A}", 70, YEL).move_to(UP * 2.3)
        beat(self, Write(e), t=1.2, rt=.7)
        base = Line(P3((-3.4, -2.4)), P3((3.4, -2.4)), color=MUTE, stroke_width=3)
        beat(self, Create(base), t=.4, rt=.3)
        b1, l1 = ibar(-1.6, 2.0, BLU, r"2\,\mathrm{A}"); b2, l2 = ibar(1.6, 3.33, YEL, r"3.3\,\mathrm{A}")
        n1 = kr("C 없을 때", 30, MUTE).next_to(b1, DOWN, .25); n2 = kr("C 넣으면", 30, YEL).next_to(b2, DOWN, .25)
        beat(self, GrowFromEdge(b1, DOWN), FadeIn(l1), FadeIn(n1), t=1.0, rt=.6)
        beat(self, GrowFromEdge(b2, DOWN), FadeIn(l2), FadeIn(n2), t=1.4, rt=.8)
        ar = Arrow(l1.get_right(), l2.get_left(), buff=.2, color=YEL, path_arc=-.5)
        beat(self, Create(ar), t=1.0, rt=.5)


class C4(Scene):
    def construct(self):
        D = circ5(self); self.add(D["g"], D["ls"], D["lr"], D["ll"], D["lc"])
        q = card(tex(r"V_L = \;?", 50, GRN), GRN, .14).next_to(D["L"], DOWN, .3)
        beat(self, FadeIn(q, shift=DOWN * .2), t=1.0, rt=.4)
        e = tex(r"V_L = 4 \times 3.3 \approx 13.3\,\mathrm{V}", 60, GRN).move_to(DOWN * 1.1)
        beat(self, Write(e), t=1.2, rt=.6)
        nq = card(tex(r"13.3\,\mathrm{V}", 50, GRN), GRN, .14).move_to(q)
        beat(self, Transform(q, nq), t=.8, rt=.4)
        c = VGroup(tex(r"13.3\,\mathrm{V}", 60, GRN), tex(">", 60, INK), tex(r"10\,\mathrm{V}", 60, YEL), kr("전원", 32, YEL)).arrange(RIGHT, buff=.3).move_to(DOWN * 2.6)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.4)
        pulse(self, c, t=1.0)


class C5(Scene):
    def construct(self):
        self.add(step_tag(5))
        o = LEFT * 2.0 + DOWN * .1; s = .2
        P = plane(o, 3.2, lab=False); self.add(P)
        vl = vec(o, o + UP * 13.3 * s, GRN); vc = vec(o + RIGHT * .15, o + RIGHT * .15 + DOWN * 13.3 * s, ORG)
        beat(self, GrowArrow(vl), FadeIn(tex(r"V_L\ 13.3", 40, GRN).next_to(vl.get_end(), LEFT, .15)), t=1.0, rt=.5)
        beat(self, GrowArrow(vc), FadeIn(tex(r"V_C\ 13.3", 40, ORG).next_to(vc.get_end(), RIGHT, .15)), t=1.0, rt=.5)
        k = kr("반대 방향 → 서로 지움", 36, INK).move_to(RIGHT * 3.4 + UP * 1.4)
        beat(self, FadeIn(k), t=1.0, rt=.4)
        x = VGroup(Cross(vl, stroke_color=MUTE, stroke_width=4).scale(.4), Cross(vc, stroke_color=MUTE, stroke_width=4).scale(.4))
        vr = vec(o, o + RIGHT * 10 * s * 1.3, BLU)
        beat(self, Create(x), GrowArrow(vr), FadeIn(tex(r"V_R = 10", 40, BLU).next_to(vr, DOWN, .15)), t=1.2, rt=.6)
        e = tex(r"V_R + V_L + V_C = 10\,\mathrm{V}", 52, YEL).move_to(RIGHT * 3.2 + DOWN * 1.8)
        beat(self, Write(e), t=1.2, rt=.6)


class C6(Scene):
    def construct(self):
        self.add(step_tag(5))
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 4, 1], x_length=9, y_length=4.0, tips=True,
                  axis_config=dict(color=MUTE, stroke_width=3, include_ticks=False)).shift(DOWN * .6)
        xl = VGroup(kr("주파수", 28, MUTE), tex(r"\omega", 36, MUTE)).arrange(RIGHT, buff=.1).next_to(ax.x_axis.get_end(), DOWN, .15)
        yl = kr("전류", 28, MUTE).next_to(ax.y_axis.get_end(), LEFT, .15)
        beat(self, Create(ax), FadeIn(xl), FadeIn(yl), t=.7, rt=.5)
        f = lambda x: 3.33 / np.sqrt(1 + (2.2 * (x / 5 - 5 / x)) ** 2)
        c = ax.plot(f, x_range=[.3, 9.8, .02], color=YEL, stroke_width=6)
        beat(self, Create(c), t=1.4, rt=1.0)
        d = DashedLine(ax.c2p(5, 0), ax.c2p(5, 3.33), color=YEL, stroke_width=3)
        lab = tex(r"\omega_0 = 1000", 40, YEL).next_to(ax.c2p(5, 3.33), UP, .15)
        beat(self, Create(d), FadeIn(lab), t=1.0, rt=.5)
        t = card(VGroup(kr("직렬 공진", 44, YEL), kr("한 방송만 골라 듣기", 30, INK)).arrange(DOWN, buff=.15), YEL).to_corner(UR, buff=.4).shift(DOWN * .8)
        beat(self, FadeIn(t, shift=LEFT * .3), t=1.2, rt=.4)
        st = VGroup(*[kr(s, 26, MUTE).move_to(ax.c2p(x, -.35)) for s, x in (("A 방송", 2.4), ("B 방송", 5), ("C 방송", 7.8))])
        st[1].set_color(YEL)
        beat(self, FadeIn(st), t=1.2, rt=.4)


# ================= 정리 =================
def sum_rows(items, size=34):
    g = VGroup(*[VGroup(kr(a, size, MUTE), b).arrange(RIGHT, buff=.5) for a, b in items]).arrange(DOWN, buff=.55, aligned_edge=LEFT)
    return g.shift(DOWN * .2)


class F1(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        c1 = card(VGroup(kr("사인파", 32, BLU), kr("크기 + 위상", 42, INK)).arrange(DOWN, buff=.2), BLU)
        c2 = card(VGroup(kr("페이저", 32, YEL), tex(r"10\angle 0^\circ", 60, YEL)).arrange(DOWN, buff=.2), YEL)
        VGroup(c1, c2).arrange(RIGHT, buff=1.6).shift(DOWN * .2)
        ar = Arrow(c1.get_right(), c2.get_left(), buff=.2, color=MUTE)
        beat(self, FadeIn(c1, shift=UP * .3), t=1.6, rt=.5)
        beat(self, GrowArrow(ar), FadeIn(c2, shift=UP * .3), t=1.8, rt=.5)
        pulse(self, c2, t=1.4)


class F2(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        rows = sum_rows([("저항", tex("R", 58, BLU)), ("코일", tex(r"j\omega L", 58, GRN)), ("커패시터", tex(r"\frac{1}{j\omega C}", 58, ORG))], 38)
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.4, rt=.5)
        pulse(self, rows, t=1.4)


class F3(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        a = card(VGroup(kr("옴의 법칙 · KVL", 36, INK), kr("직류처럼", 48, YEL), tex(r"V = ZI", 50, YEL)).arrange(DOWN, buff=.25), YEL)
        a.move_to(LEFT * 3.2 + DOWN * .3)
        beat(self, FadeIn(a, shift=UP * .3), t=1.6, rt=.5)
        o = RIGHT * 1.6 + DOWN * 1.6; s = .3
        p = o + 6 * s * U(-53.13) + UP * 1.8; q = p + 8 * s * U(36.87); o2 = o + UP * 1.8
        g = VGroup(vec(o2, p, BLU, 6), vec(p, q, GRN, 6), vec(o2, q, YEL, 7))
        t = kr("더할 땐 화살표로", 40, INK).next_to(g, UP, .4)
        beat(self, FadeIn(t), Create(g), t=1.8, rt=.9)
        pulse(self, VGroup(t, g), t=1.4)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("페이저와 임피던스 단원", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        beat(self, FadeIn(t[0]), t=.8, rt=.3)
        for m in t[1]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.4, rt=.4)
        pulse(self, t, t=2.0)


class Next(Scene):
    def construct(self):
        items = ["과도응답", "페이저", "교류 전력", "3상 회로"]
        cards = VGroup(*[card(kr(s, 36, YEL if s == "페이저" else MUTE), YEL if s == "페이저" else "#2a2e37", .3) for s in items]).arrange(RIGHT, buff=.35)
        cards.scale_to_fit_width(min(cards.width, 12.5))
        lab = kr("재생목록 · 회로이론 한눈에", 40, INK).next_to(cards, UP, .6)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cards], lag_ratio=.3), run_time=1.6)
        arr = Arrow(cards[1].get_bottom() + DOWN * .2, cards[2].get_bottom() + DOWN * .2, buff=0, color=YEL, path_arc=PI / 2)
        beat(self, Create(arr), t=1.6, rt=.8)


# ================= 쇼츠 전용 =================
class AQ(Scene):
    """6V + 8V = 10V?"""
    def construct(self):
        D = series(UP * .9, 6.6, 2.2, src_lab=r"10\,\mathrm{V}", rl="", ll="")
        beat(self, FadeIn(D["g"]), FadeIn(D["ls"]), t=.8, rt=.5)
        m1 = card(tex(r"6\,\mathrm{V}", 54, BLU), BLU, .15).next_to(D["R"], UP, .35)
        m2 = card(tex(r"8\,\mathrm{V}", 54, GRN), GRN, .15).next_to(D["L"], UP, .35)
        beat(self, FadeIn(m1, shift=DOWN * .2), t=.8, rt=.4)
        beat(self, FadeIn(m2, shift=DOWN * .2), t=.8, rt=.4)
        q = tex(r"6 + 8 = 10\;?", 96, YEL).move_to(DOWN * 2.3)
        beat(self, Write(q), t=1.0, rt=.5)
        pulse(self, q, t=1.2)


class AWrong(Scene):
    def construct(self):
        k = kr("KVL", 60, INK).move_to(UP * 2.2)
        beat(self, FadeIn(k), t=.6, rt=.3)
        e = tex(r"6 + 8 = 14", 90, INK).move_to(UP * .3)
        beat(self, Write(e), t=1.0, rt=.5)
        ne = tex(r"\neq 10", 90, RED).next_to(e, RIGHT, .4)
        beat(self, FadeIn(ne, shift=LEFT * .2), t=.9, rt=.4)
        a = kr("틀렸다?", 56, RED).move_to(DOWN * 1.8)
        beat(self, FadeIn(a), t=.8, rt=.3)
        no = kr("아니에요!", 64, YEL).move_to(DOWN * 1.8)
        beat(self, Transform(a, no), t=1.0, rt=.4)


class ATri(Scene):
    def construct(self):
        o = LEFT * 2.0 + DOWN * 2.4; s = .5
        a = o + RIGHT * 6 * s; b = a + UP * 8 * s
        sc = 1.0
        vr = vec(o, a, BLU); vl = vec(a, b, GRN); vs = vec(o, b, YEL, 9)
        beat(self, GrowArrow(vr), FadeIn(tex("6", 60, BLU).next_to(vr, DOWN, .2)), t=.9, rt=.5)
        beat(self, GrowArrow(vl), FadeIn(tex("8", 60, GRN).next_to(vl, RIGHT, .2)), Create(right_mark(a, o - a, b - a, .35)), t=.9, rt=.5)
        beat(self, GrowArrow(vs), t=.8, rt=.6)
        ten = tex("10", 110, YEL).next_to(vs.get_center(), UL, .2)
        beat(self, FadeIn(ten, scale=1.3), t=1.0, rt=.4)
        pulse(self, ten, t=1.2)


class BQ(Scene):
    def construct(self):
        a = tex(r"\frac{d}{dt}", 120, MUTE).move_to(LEFT * 3 + UP * .4)
        beat(self, FadeIn(a), t=.7, rt=.3)
        ar = Arrow(LEFT * 1.4 + UP * .4, RIGHT * .8 + UP * .4, buff=0, color=YEL, stroke_width=8)
        b = tex(r"\times\, j\omega", 120, YEL).move_to(RIGHT * 3 + UP * .4)
        beat(self, GrowArrow(ar), Write(b), t=1.2, rt=.6)
        t = kr("미분이 곱셈으로?", 60, YEL).move_to(DOWN * 2.2)
        beat(self, FadeIn(t, shift=UP * .2), t=1.2, rt=.4)
        pulse(self, b, t=1.2)


class BDiff(Scene):
    def construct(self):
        o = LEFT * 4.6 + DOWN * .2; Ln = 9.0
        ax = taxis(o, Ln, 2.0); self.add(ax)
        w = sine(o + RIGHT * Ln / 2, 1.0, 2, Ln, BLU)
        beat(self, Create(w), FadeIn(tex(r"\cos", 44, BLU).next_to(w.get_end(), RIGHT, .1)), t=1.0, rt=.8)
        d = sine(o + RIGHT * Ln / 2, 1.7, 2, Ln, GRN, phase=PI / 2)
        beat(self, Create(d), FadeIn(tex(r"\frac{d}{dt}", 44, GRN).next_to(d.get_end(), RIGHT, .1)), t=1.2, rt=.8)
        T = Ln / 2
        p1 = o + RIGHT * T + UP * 2.0; p0 = o + RIGHT * (T * .75) + UP * 2.0
        a = DoubleArrow(p0, p1, buff=0, color=YEL, stroke_width=5, tip_length=.2)
        beat(self, GrowFromCenter(a), FadeIn(kr("90° 앞섬", 40, YEL).next_to(a, UP, .1)), t=1.4, rt=.5)


class CQ(Scene):
    def construct(self):
        L = coil((-4.6, .6), (-1.2, .6), GRN, 5)
        beat(self, Create(L), t=.8, rt=.6)
        e = tex("=", 100, INK).move_to(RIGHT * .2 + UP * .6)
        w = wire((1.4, .6), (4.8, .6), INK, 7)
        beat(self, FadeIn(e), Create(w), t=1.0, rt=.5)
        q = kr("직류에선 그냥 전선?", 60, YEL).move_to(DOWN * 1.8)
        beat(self, FadeIn(q, shift=UP * .2), t=1.2, rt=.4)
        pulse(self, q, t=1.2)


class CDC(Scene):
    def construct(self):
        e = tex(r"Z_L = j\omega L", 80, GRN).move_to(UP * 1.8)
        beat(self, Write(e), t=.8, rt=.5)
        w = tex(r"\omega = 0", 70, YEL).move_to(LEFT * 2.6 + UP * .1)
        beat(self, FadeIn(w), t=.8, rt=.3)
        z = tex(r"Z_L = 0", 80, YEL).move_to(RIGHT * 2.4 + UP * .1)
        beat(self, Write(z), t=1.0, rt=.5)
        L = coil((-3.2, -2.0), (3.2, -2.0), GRN, 5)
        beat(self, Create(L), t=.6, rt=.5)
        beat(self, Transform(L, wire((-3.2, -2.0), (3.2, -2.0), GRN, 7)), FadeIn(kr("전선", 44, GRN).move_to(DOWN * 2.8)), t=1.2, rt=.7)


class DQ(Scene):
    def construct(self):
        R = resistor((-5.0, .8), (-2.4, .8), BLU); L = coil((-.4, .8), (2.4, .8), GRN)
        beat(self, Create(R), FadeIn(tex(r"3\,\Omega", 54, BLU).next_to(R, UP, .35)), t=.9, rt=.5)
        beat(self, Create(L), FadeIn(tex(r"4\,\Omega", 54, GRN).next_to(L, UP, .35)), t=.9, rt=.5)
        e = tex(r"3 + 4 = 5\;?", 100, YEL).move_to(DOWN * 1.8)
        beat(self, Write(e), t=1.2, rt=.6)
        pulse(self, e, t=1.2)


class DMag(Scene):
    def construct(self):
        o = LEFT * 4.6 + DOWN * 2.4; s = .9
        r = vec(o, o + RIGHT * 3 * s, BLU); l = vec(o + RIGHT * 3 * s, o + RIGHT * 3 * s + UP * 4 * s, GRN); z = vec(o, o + RIGHT * 3 * s + UP * 4 * s, YEL, 8)
        self.add(r, l, z, tex("3", 44, BLU).next_to(r, DOWN, .15), tex("4", 44, GRN).next_to(l, RIGHT, .15))
        e = tex(r"|Z| = \sqrt{3^2 + 4^2}", 70, INK).move_to(RIGHT * 2.6 + UP * 1.2)
        beat(self, Write(e), t=1.2, rt=.7)
        e2 = tex(r"= \sqrt{9 + 16}", 70, INK).next_to(e, DOWN, .35, aligned_edge=LEFT)
        beat(self, Write(e2), t=1.0, rt=.5)
        e3 = tex(r"= 5\,\Omega", 90, YEL).next_to(e2, DOWN, .35, aligned_edge=LEFT)
        beat(self, Write(e3), FadeIn(tex("5", 54, YEL).next_to(z.get_center(), UL, .15)), t=1.0, rt=.5)
        pulse(self, e3, t=1.2)


class DCur(Scene):
    def construct(self):
        a = tex(r"I = \frac{10}{5} = 2\,\mathrm{A}", 80, YEL).move_to(UP * 1.2)
        beat(self, Write(a), t=1.2, rt=.7)
        b = tex(r"\frac{10}{7} \approx 1.4\,\mathrm{A}", 64, MUTE).move_to(DOWN * 1.4)
        beat(self, FadeIn(b), t=.9, rt=.4)
        x = Cross(b, stroke_color=RED, stroke_width=6)
        beat(self, Create(x), FadeIn(kr("7Ω로 계산하면 틀려요", 36, RED).next_to(b, DOWN, .4)), t=1.2, rt=.5)
        pulse(self, a, t=1.2)


class EQ(Scene):
    def construct(self):
        D = series(UP * .9, 6.6, 2.2, src_lab=r"10\,\mathrm{V}", rl="", ll="")
        beat(self, FadeIn(D["g"]), FadeIn(D["ls"]), t=.8, rt=.5)
        m = card(tex(r"13.3\,\mathrm{V}", 54, GRN), GRN, .15).next_to(D["L"], UP, .35)
        beat(self, FadeIn(m, shift=DOWN * .2), t=.9, rt=.4)
        q = VGroup(tex(r"13.3 > 10", 90, YEL), tex("?", 90, YEL)).arrange(RIGHT, buff=.3).move_to(DOWN * 2.3)
        beat(self, Write(q), t=1.2, rt=.6)
        pulse(self, q, t=1.2)
