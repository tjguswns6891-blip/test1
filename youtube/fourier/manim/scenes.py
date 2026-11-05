# 푸리에 급수로 회로 해석 롱폼 모션그래픽. 16:9, 핵심은 가운데(세로 쇼츠에서도 씀). 페이저 편 형식.
# 장면 하나 = 문장 하나. 장면 길이는 dur.json(음성 실제 길이)에 맞춰 fill() 로 채운다 → 멈춘 화면 없음.
# 검산: ±10V 구형파 b_n = 40/(nπ) (홀수 n). RC (ω0RC=1): H(n)=1/(1+jn) → 0.707∠−45°, 0.316∠−71.6°, 0.196∠−78.7°.
#   출력 9.00 / 1.34 / 0.50 V. 3고조파 비: 33% → 14.9%.
# 렌더: sh render_par.sh <쇼츠 장면...>
from manim import *
import numpy as np, os, json

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




# ---------- 푸리에 전용 ----------
_DP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dur.json")
DUR = json.load(open(_DP)) if os.path.exists(_DP) else {}


def fill(sc, m, c=YEL, extra=0.0):
    """장면 길이를 dur.json 에 맞춘다: 남은 시간 동안 m 둘레를 그렸다 지우기 (멈춘 화면 방지)."""
    tgt = DUR.get(type(sc).__name__, 0) + extra
    rem = tgt - sc.renderer.time
    while rem > 1.7:
        sc.play(Circumscribe(m, color=c, buff=.18, fade_out=True, run_time=1.3)); sc.wait(.2); rem -= 1.5
    sc.wait(max(.3, rem))


def sq(th):
    """단위 구형파 (홀함수): 0<θ<π 에서 +1, π<θ<2π 에서 −1."""
    return np.where(np.mod(th, 2 * PI) < PI, 1.0, -1.0)


def ps(th, N, gain=None):
    """구형파 부분합 (4/π)Σ sin(nθ)/n, n 홀수 ≤ N. gain(n) → (크기배, 위상)."""
    th = np.asarray(th, dtype=float); y = np.zeros_like(th)
    for n in range(1, N + 1, 2):
        g, p = gain(n) if gain else (1.0, 0.0)
        y = y + 4 / PI * g * np.sin(n * th + p) / n
    return y


def H(n):
    """RC 저역 통과, ω0RC = 1: H(n) = 1/(1 + jn)."""
    return 1 / np.sqrt(1 + n * n), -np.arctan(n)


def rc_out(th):
    """±1 구형파 → RC (τ = 1/ω0) 정상상태 출력 (정확한 지수 충방전)."""
    th = np.mod(np.asarray(th, dtype=float), 2 * PI); v0 = -np.tanh(PI / 2)
    up = th < PI
    a = 1 + (v0 - 1) * np.exp(-th)
    v1 = 1 + (v0 - 1) * np.exp(-PI)
    b = -1 + (v1 + 1) * np.exp(-(th - PI))
    return np.where(up, a, b)


def curve(o, L, cyc, g, ys, col, sw=5, n=600, sharp=False):
    """o: 왼쪽 가운데, 가로 L 에 cyc 주기, 세로 = ys·g(θ)."""
    o = P3(o); xs = np.linspace(0, L, n); th = 2 * PI * cyc * xs / L; y = g(th)
    pts = [o + np.array([x, ys * v, 0]) for x, v in zip(xs, y)]
    m = VMobject(color=col, stroke_width=sw)
    m.set_points_as_corners(pts) if sharp else m.set_points_smoothly(pts)
    return m


def sqwave(o, L, cyc, A, col=YEL, sw=6):
    """세로 모서리까지 그린 구형파 (높이 ±A)."""
    o = P3(o); seg = L / (2 * cyc); pts = []; v = A
    for k in range(2 * cyc):
        x0, x1 = k * seg, (k + 1) * seg
        pts += [o + np.array([x0, v, 0]), o + np.array([x1, v, 0])]
        v = -v
    return VMobject(color=col, stroke_width=sw).set_points_as_corners(pts)


def wax(o, L, h, lab="t"):
    return taxis(o, L, h, lab)


def sqsrc(p, c=YEL, r=.55):
    """구형파 전원 기호."""
    p = P3(p); s = .28
    w = VMobject(color=c, stroke_width=5).set_points_as_corners(
        [p + np.array(q) for q in [(-.36, -s / 1.4, 0), (-.36, s, 0), (0, s, 0), (0, -s, 0), (.36, -s, 0), (.36, s / 1.4, 0)]])
    return VGroup(Circle(r, color=c, stroke_width=5).move_to(p), w)


def rc(o=ORIGIN, W=6.4, H_=2.6, src=None, rl=r"1\,\mathrm{k\Omega}", cl=r"1\,\mu\mathrm{F}", out=True):
    """RC 저역 통과: 왼쪽 전원 → 위 R → 오른쪽 C(세로) → 출력 단자."""
    o = P3(o); x0, x1 = o[0] - W / 2, o[0] + W / 2; yt, yb = o[1] + H_ / 2, o[1] - H_ / 2
    s = (src or sqsrc)((x0, o[1]))
    xm = o[0] + W * .1
    R = resistor((x0, yt), (xm, yt), BLU)
    C = capacitor((xm, yt), (xm, yb), ORG)[0]
    g = VGroup(s, wire((x0, o[1] + .55), (x0, yt)), wire((x0, o[1] - .55), (x0, yb)), R, C, wire((x0, yb), (xm, yb)))
    D = dict(src=s, R=R, C=C, xm=xm, yt=yt, yb=yb, x0=x0, x1=x1)
    if out:
        g.add(wire((xm, yt), (x1, yt)), wire((xm, yb), (x1, yb)), term((x1, yt)), term((x1, yb)))
        D["vo"] = tex(r"v_C", 44, ORG).move_to((x1 + .1, o[1], 0))
    D["lr"] = tex(rl, 38, BLU).next_to(R, UP, .3); D["lc"] = tex(cl, 38, ORG).next_to(C, LEFT, .25)
    D["g"] = g
    return D


def bars(o, vals, cols, unit=.32, w=.55, gap=.95, labs=None, nums=None, size=30):
    """o: 첫 막대 아래 가운데. 반환 (막대들, 라벨들, 숫자들)."""
    o = P3(o); B, Lb, Nm = VGroup(), VGroup(), VGroup()
    for i, v in enumerate(vals):
        c = cols[i] if isinstance(cols, (list, tuple)) else cols
        b = Rectangle(width=w, height=max(.02, v * unit), fill_color=c, fill_opacity=.9, stroke_width=0)
        b.move_to(o + RIGHT * gap * i, aligned_edge=DOWN); B.add(b)
        if labs: Lb.add(tex(labs[i], size, MUTE).next_to(b, DOWN, .15).set_y(o[1] - .3))
        if nums: Nm.add(tex(nums[i], size, c).next_to(b, UP, .12))
    return B, Lb, Nm


SQ_O = LEFT * 5.2 + DOWN * .4; SQ_L = 10.4


# ================= 인트로 =================
class Hook(Scene):
    """사인파를 더하면 구형파."""
    def construct(self):
        o = SQ_O + UP * .3; ys = 1.5
        ax = wax(o, SQ_L, 2.2); beat(self, FadeIn(ax), t=.4, rt=.3)
        N = ValueTracker(1)
        cv = always_redraw(lambda: curve(o, SQ_L, 2, lambda th: ps(th, int(N.get_value()) | 1), ys, BLU, 6))
        self.add(cv)
        lab = always_redraw(lambda: kr(f"사인파 {(int(N.get_value()) + 1) // 2}개", 40, BLU).to_edge(UP, buff=.5))
        self.add(lab)
        for n in (3, 5, 9, 15, 31):
            self.play(N.animate.set_value(n), run_time=.7, rate_func=lambda t: 1.0 if t > .5 else 0.0); self.wait(.2)
        sw = sqwave(o, SQ_L, 2, ys, YEL, 4).set_stroke(opacity=.6)
        beat(self, Create(sw), FadeIn(kr("= 구형파", 44, YEL).to_edge(DOWN, buff=.5)), t=1.0, rt=.6)
        fill(self, sw)


class Goal(Scene):
    """구형파 → RC → ?"""
    def construct(self):
        D = rc(UP * .3, 5.6, 2.4)
        beat(self, FadeIn(D["g"]), FadeIn(D["lr"]), FadeIn(D["lc"]), t=1.0, rt=.6)
        si = sqwave(LEFT * 6.6 + DOWN * 2.6, 2.6, 2, .5, YEL, 5)
        beat(self, Create(si), FadeIn(kr("입력", 30, YEL).next_to(si, UP, .2)), t=1.0, rt=.5)
        q = tex("?", 120, ORG).move_to(RIGHT * 5.6 + DOWN * 2.4)
        ar = Arrow(D["vo"].get_center() + DOWN * .4 + RIGHT * .2, q.get_top() + UP * .1, buff=.1, color=ORG)
        beat(self, FadeIn(D["vo"]), GrowArrow(ar), FadeIn(q, scale=1.3), t=1.2, rt=.6)
        t = card(kr("푸리에 급수", 52, YEL), YEL).to_edge(UP, buff=.35)
        beat(self, FadeIn(t, shift=DOWN * .2), t=1.0, rt=.4)
        fill(self, t)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "사인파의 합", BLU), ("2", "계수·대칭", PUR), ("3", "구형파", GRN), ("4", "고조파 페이저", ORG), ("5", "다시 더하기", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.1, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.0, rt=.8)
        fill(self, cards)


# ================= STEP 1 사인파의 합 =================
def fs_eq(size=50):
    return tex(r"f(t) = a_0 + \sum_{n=1}^{\infty} \left( a_n \cos n\omega_0 t + b_n \sin n\omega_0 t \right)", size, INK)


def demo_f(th):     # 예시 신호: 직류 0.5 + 기본파 + 3고조파 조금
    return .5 + .8 * np.sin(th) + .3 * np.cos(2 * th) + .25 * np.sin(3 * th)


S1_O = LEFT * 5.2 + DOWN * 1.2; S1_L = 10.4


class SUM1(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax = wax(S1_O, S1_L, 1.9); beat(self, FadeIn(ax), t=.4, rt=.3)
        f = curve(S1_O, S1_L, 2, demo_f, 1.0, YEL, 6)
        beat(self, Create(f), FadeIn(kr("반복 신호", 34, YEL).next_to(f, UP, .1).align_to(f, LEFT)), t=1.4, rt=1.0)
        eq = tex(r"= \sin + \sin + \sin + \cdots", 60, BLU).to_edge(UP, buff=.6)
        beat(self, Write(eq), t=1.2, rt=.7)
        fill(self, eq)


class SUM2(Scene):
    def construct(self):
        self.add(step_tag(1))
        eq = fs_eq().to_edge(UP, buff=.5); self.add(eq)
        ax = wax(S1_O, S1_L, 1.9); f = curve(S1_O, S1_L, 2, demo_f, 1.0, MUTE, 4); self.add(ax, f)
        beat(self, eq[0][5:7].animate.set_color(YEL), t=.7, rt=.4)
        dc = DashedLine(S1_O + UP * .5, S1_O + RIGHT * S1_L + UP * .5, color=YEL, stroke_width=5)
        beat(self, Create(dc), FadeIn(tex("a_0", 44, YEL).next_to(dc, RIGHT, .1)), t=1.1, rt=.6)
        beat(self, FadeIn(kr("직류 = 평균값", 36, YEL).move_to(RIGHT * 3 + DOWN * 3.2)), t=1.0, rt=.4)
        fill(self, dc)


class SUM3(Scene):
    def construct(self):
        self.add(step_tag(1))
        eq = fs_eq().to_edge(UP, buff=.5); self.add(eq)
        ax = wax(S1_O, S1_L, 1.9); f = curve(S1_O, S1_L, 2, demo_f, 1.0, MUTE, 3).set_stroke(opacity=.5); self.add(ax, f)
        w1 = curve(S1_O + UP * .5, S1_L, 2, np.sin, .8, BLU, 6)
        beat(self, Create(w1), FadeIn(kr("기본파", 36, BLU).next_to(w1, UP, .05).align_to(w1, LEFT).shift(RIGHT * .6)), t=1.3, rt=1.0)
        T = S1_L / 2
        br = BraceBetweenPoints(S1_O + DOWN * 1.0, S1_O + RIGHT * T + DOWN * 1.0, DOWN, color=BLU)
        beat(self, GrowFromCenter(br), FadeIn(kr("주기 T 에 한 번", 30, BLU).next_to(br, DOWN, .1)), t=1.1, rt=.5)
        w0 = tex(r"\omega_0 = \frac{2\pi}{T}", 56, BLU).move_to(RIGHT * 3.6 + DOWN * 2.9)
        beat(self, Write(w0), t=1.0, rt=.5)
        fill(self, w0)


class SUM4(Scene):
    def construct(self):
        self.add(step_tag(1))
        rows = VGroup()
        for n, c in ((1, BLU), (2, GRN), (3, ORG), (4, PUR)):
            o = LEFT * 4.2 + UP * (2.4 - (n - 1) * 1.45)
            w = curve(o, 7.6, 2 * n, np.sin, .45, c, 5)
            lab = kr("기본파" if n == 1 else f"{n}배", 32, c).next_to(o, LEFT, .3)
            rows.add(VGroup(lab, w))
        for r in rows:
            beat(self, FadeIn(r[0]), Create(r[1]), t=1.0, rt=.7)
        br = Brace(rows[1:], RIGHT, color=YEL)
        beat(self, GrowFromCenter(br), FadeIn(kr("고조파", 40, YEL).next_to(br, RIGHT, .2)), t=1.0, rt=.5)
        fill(self, rows[1:])


class SUM5(Scene):
    def construct(self):
        self.add(step_tag(1))
        eq = fs_eq(56).move_to(UP * 1.6); self.add(eq)
        beat(self, eq[0][14:16].animate.set_color(GRN), eq[0][24:26].animate.set_color(ORG), t=1.0, rt=.5)
        a = SurroundingRectangle(eq[0][14:16], color=GRN, buff=.08); b = SurroundingRectangle(eq[0][24:26], color=ORG, buff=.08)
        beat(self, Create(a), Create(b), t=.9, rt=.5)
        c1 = card(VGroup(tex("a_n", 50, GRN), kr("cos 크기", 32, INK)).arrange(DOWN, buff=.2), GRN)
        c2 = card(VGroup(tex("b_n", 50, ORG), kr("sin 크기", 32, INK)).arrange(DOWN, buff=.2), ORG)
        VGroup(c1, c2).arrange(RIGHT, buff=1.2).shift(DOWN * 1.4)
        beat(self, FadeIn(c1, shift=UP * .3), t=.9, rt=.4)
        beat(self, FadeIn(c2, shift=UP * .3), FadeIn(kr("= 계수", 44, YEL).next_to(VGroup(c1, c2), RIGHT, .5)), t=1.0, rt=.4)
        fill(self, VGroup(c1, c2))


class SUM6(Scene):
    def construct(self):
        self.add(step_tag(1))
        o = LEFT * 5.6 + UP * .6
        f = curve(o, 4.0, 2, demo_f, .8, YEL, 6)
        beat(self, Create(f), t=.9, rt=.7)
        ar = Arrow(o + RIGHT * 4.3, o + RIGHT * 5.8, buff=0, color=MUTE, stroke_width=6)
        beat(self, GrowArrow(ar), t=.6, rt=.4)
        B, Lb, Nm = bars(RIGHT * 1.6 + DOWN * .8, [1.6, 2.5, 1.0, .8], [YEL, BLU, GRN, ORG], unit=1.0, gap=1.25,
                         labs=["0", r"\omega_0", r"2\omega_0", r"3\omega_0"])
        for b, l in zip(B, Lb):
            beat(self, GrowFromEdge(b, DOWN), FadeIn(l), t=.6, rt=.4)
        t = kr("주파수별 재료", 44, YEL).move_to(RIGHT * 3.4 + DOWN * 2.7)
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.4)
        fill(self, VGroup(B, Lb))


# ================= STEP 2 계수와 대칭 =================
def coef_eqs(size=46):
    a = tex(r"a_n = \frac{2}{T}\int_0^T f(t)\cos n\omega_0 t\,dt", size, GRN)
    b = tex(r"b_n = \frac{2}{T}\int_0^T f(t)\sin n\omega_0 t\,dt", size, ORG)
    return VGroup(a, b).arrange(DOWN, buff=.45)


class K1(Scene):
    def construct(self):
        self.add(step_tag(2))
        E = coef_eqs(54).shift(UP * .3)
        beat(self, Write(E[0]), t=1.3, rt=.8)
        beat(self, Write(E[1]), t=1.3, rt=.8)
        u1 = SurroundingRectangle(E[1][0][10:21], color=YEL, buff=.08)
        beat(self, Create(u1), FadeIn(kr("곱해서", 36, YEL).next_to(u1, DOWN, .25)), t=1.0, rt=.4)
        u2 = SurroundingRectangle(E[1][0][5:10], color=BLU, buff=.08)
        beat(self, Create(u2), FadeIn(kr("한 주기 적분", 36, BLU).next_to(E, UP, .4)), t=1.0, rt=.4)
        fill(self, E[1])


class K2(Scene):
    def construct(self):
        self.add(step_tag(2))
        o1 = LEFT * 5.4 + UP * 1.9; o2 = LEFT * 5.4 + DOWN * 1.7; L = 6.0
        a1 = wax(o1, L, 1.0); a2 = wax(o2, L, 1.3)
        f = curve(o1, L, 1, lambda th: ps(th, 7), .7, YEL, 5); s = curve(o1, L, 1, np.sin, .7, BLU, 4)
        beat(self, FadeIn(a1), Create(f), FadeIn(kr("f(t)", 30, YEL).next_to(o1, LEFT, .2)), t=.9, rt=.6)
        beat(self, Create(s), FadeIn(tex(r"\sin\omega_0 t", 34, BLU).next_to(o1 + RIGHT * L * .75 + DOWN * .7, DOWN, .1)), t=.9, rt=.6)
        xs = np.linspace(0, L, 200); th = 2 * PI * xs / L; y = sq(th) * np.sin(th) * 1.0
        area = Polygon(*[o2 + np.array([x, v, 0]) for x, v in zip(xs, y)], o2 + RIGHT * L, o2, color=GRN, fill_color=GRN, fill_opacity=.5, stroke_width=3)
        beat(self, FadeIn(a2), DrawBorderThenFill(area), FadeIn(kr("곱", 34, GRN).next_to(o2, LEFT, .2)), t=1.3, rt=.9)
        c = card(VGroup(kr("넓이 남음", 36, GRN), kr("→ 들어 있다", 36, INK)).arrange(DOWN, buff=.15), GRN).move_to(RIGHT * 4.4 + DOWN * .2)
        beat(self, FadeIn(c, shift=LEFT * .3), t=1.0, rt=.4)
        fill(self, c, GRN)


class K3(Scene):
    def construct(self):
        self.add(step_tag(2))
        E = coef_eqs(44).shift(UP * 1.4)
        beat(self, FadeIn(E), t=.7, rt=.4)
        x = Cross(E, stroke_color=RED, stroke_width=7)
        q = kr("적분 전에", 46, INK).move_to(DOWN * 1.2)
        beat(self, FadeIn(q), t=.8, rt=.3)
        sym = card(kr("대칭부터 확인", 50, YEL), YEL).move_to(DOWN * 2.5)
        beat(self, FadeIn(sym, shift=UP * .2), t=1.0, rt=.4)
        beat(self, Create(x), FadeIn(kr("절반은 0", 44, RED).next_to(E, RIGHT, .3)), t=1.0, rt=.5)
        fill(self, sym)


def sym_axes(o, w=4.4, h=1.4):
    o = P3(o)
    return VGroup(Arrow(o + LEFT * w / 2, o + RIGHT * w / 2, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.04),
                  Arrow(o + DOWN * h, o + UP * h, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.08))


def fpts(o, f, x0, x1, sx=1.0, sy=1.0, n=300, col=YEL, sw=6):
    o = P3(o); xs = np.linspace(x0, x1, n)
    return VMobject(color=col, stroke_width=sw).set_points_smoothly([o + np.array([x * sx, f(x) * sy, 0]) for x in xs])


def sym_scene(sc, kind):
    """kind: even(짝) / odd(홀)."""
    sc.add(step_tag(2))
    o = LEFT * 3.0 + DOWN * .2
    ax = sym_axes(o, 5.6, 1.9); beat(sc, FadeIn(ax), t=.4, rt=.3)
    if kind == "even":
        f = lambda x: np.cos(x) * .9 + .25 * np.cos(3 * x)
        nm, rule, zero, col = "짝함수", "y축 대칭", r"b_n = 0", GRN
    else:
        f = lambda x: np.sin(x) * .9 + .25 * np.sin(3 * x)
        nm, rule, zero, col = "홀함수", "원점 대칭", r"a_0 = a_n = 0", ORG
    right = fpts(o, f, 0, 2.6, .95, 1.2, col=col)
    beat(sc, Create(right), t=.8, rt=.6)
    left = fpts(o, f, -2.6, 0, .95, 1.2, col=col)
    if kind == "even":
        beat(sc, TransformFromCopy(right, left, path_arc=0), FadeIn(kr(rule, 34, col).next_to(ax, UP, .15)), t=1.2, rt=.8)
    else:
        beat(sc, TransformFromCopy(right, left, path_arc=PI), FadeIn(kr(rule, 34, col).next_to(ax, UP, .15)), t=1.2, rt=.8)
    c = card(VGroup(kr(nm, 46, col), tex(zero, 56, YEL), kr("sin 항 전부 0" if kind == "even" else "cos 항 전부 0", 32, INK)).arrange(DOWN, buff=.25), col)
    c.move_to(RIGHT * 3.8 + DOWN * .2)
    beat(sc, FadeIn(c[0]), FadeIn(c[1][0]), t=.9, rt=.4)
    beat(sc, FadeIn(c[1][1:]), t=1.0, rt=.4)
    fill(sc, c[1][1])


class K4(Scene):
    def construct(self): sym_scene(self, "even")


class K5(Scene):
    def construct(self): sym_scene(self, "odd")


class K6(Scene):
    def construct(self):
        self.add(step_tag(2))
        o = LEFT * 5.4 + UP * .9; L = 8.0
        ax = wax(o, L, 1.4); beat(self, FadeIn(ax), t=.3, rt=.3)
        f = curve(o, L, 1, lambda th: ps(th, 9), .9, YEL, 6)
        beat(self, Create(f), t=.8, rt=.6)
        half = L / 2
        first = curve(o, half, .5, lambda th: ps(th, 9), .9, BLU, 8)
        beat(self, Create(first), t=.6, rt=.4)
        mv = first.copy().set_color(GRN)
        beat(self, mv.animate.shift(RIGHT * half).flip(RIGHT, about_point=o + RIGHT * half * 1.5), FadeIn(kr("반 주기 뒤 = 뒤집힘", 32, GRN).next_to(ax, DOWN, .2)), t=1.1, rt=.8)
        c = card(VGroup(kr("반파 대칭", 44, GRN), tex(r"a_2 = b_2 = a_4 = b_4 = \cdots = 0", 48, YEL)).arrange(DOWN, buff=.25), GRN).move_to(DOWN * 2.5)
        beat(self, FadeIn(c, shift=UP * .2), t=1.0, rt=.4)
        fill(self, c[1][1])


# ================= STEP 3 구형파 =================
Q_O = LEFT * 5.2 + DOWN * .3; Q_L = 10.4; Q_YS = .13     # 1V = .13 단위


def q_base(sc, n=3, add=True):
    sc.add(step_tag(n))
    ax = wax(Q_O, Q_L, 2.2)
    sw = sqwave(Q_O, Q_L, 2, 10 * Q_YS, YEL, 6)
    l1 = tex(r"10\,\mathrm{V}", 34, YEL).next_to(Q_O + UP * 10 * Q_YS, LEFT, .15)
    l2 = tex(r"-10\,\mathrm{V}", 34, YEL).next_to(Q_O + DOWN * 10 * Q_YS, LEFT, .15)
    g = VGroup(ax, sw, l1, l2)
    if add: sc.add(g)
    return g


class Q1(Scene):
    def construct(self):
        g = q_base(self, add=False)
        beat(self, FadeIn(g[0]), t=.3, rt=.3)
        beat(self, Create(g[1]), FadeIn(g[2:]), t=1.2, rt=1.0)
        dot = Dot(Q_O, color=ORG, radius=.12)
        beat(self, FadeIn(dot, scale=2), FadeIn(kr("원점 대칭 = 홀함수", 36, ORG).to_edge(UP, buff=.5)), t=1.1, rt=.4)
        c = card(VGroup(tex(r"a_0 = a_n = 0", 50, MUTE), kr("sin 항만", 40, YEL)).arrange(RIGHT, buff=.5), YEL).to_edge(DOWN, buff=.35)
        beat(self, FadeIn(c, shift=UP * .2), t=1.0, rt=.4)
        fill(self, c)


class Q2(Scene):
    def construct(self):
        self.add(step_tag(3))
        t = kr("반파 대칭 → 짝수 고조파 0", 38, GRN).to_edge(UP, buff=.5)
        beat(self, FadeIn(t), t=.6, rt=.3)
        rows = VGroup()
        for i, n in enumerate(range(1, 8)):
            c = YEL if n % 2 else MUTE
            r = card(VGroup(tex(f"{n}", 50, c), kr("배", 28, c)).arrange(RIGHT, buff=.1), c, .2)
            rows.add(r)
        rows.arrange(RIGHT, buff=.3).shift(UP * .3)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * .2) for r in rows], lag_ratio=.2), run_time=1.3)
        xs = VGroup(*[Cross(rows[i], stroke_color=RED, stroke_width=5) for i in (1, 3, 5)])
        beat(self, Create(xs), t=1.0, rt=.5)
        e = tex(r"\sin\omega_0 t,\;\sin 3\omega_0 t,\;\sin 5\omega_0 t,\;\sin 7\omega_0 t", 50, YEL).move_to(DOWN * 2.2)
        beat(self, Write(e), FadeIn(kr("홀수만", 36, YEL).next_to(e, UP, .25)), t=1.2, rt=.7)
        fill(self, e)


class Q3(Scene):
    def construct(self):
        g = q_base(self)
        e = tex(r"b_n = \frac{40}{n\pi}", 60, YEL).to_corner(UL, buff=.4).shift(RIGHT * 1.0)
        beat(self, Write(e), t=1.0, rt=.6)
        w = curve(Q_O, Q_L, 2, lambda th: ps(th, 1) * 10, Q_YS, BLU, 7)
        beat(self, Create(w), t=1.1, rt=.9)
        pk = Q_O + RIGHT * Q_L / 8 + UP * 40 / PI * Q_YS
        d = Dot(pk, color=BLU, radius=.12)
        m = card(tex(r"12.7\,\mathrm{V}", 50, BLU), BLU, .14).next_to(pk, UR, .15)
        beat(self, FadeIn(d, scale=2), FadeIn(m, shift=DOWN * .2), t=1.0, rt=.4)
        gt = tex(r"12.7 > 10", 64, ORG).to_corner(UR, buff=.5).shift(DOWN * .6 + LEFT * .2)
        beat(self, Write(gt), t=1.0, rt=.5)
        fill(self, m, BLU)


class Q4(Scene):
    def construct(self):
        self.add(step_tag(3))
        rows = [(1, BLU, r"12.7\,\mathrm{V}"), (3, GRN, r"4.2\,\mathrm{V}"), (5, ORG, r"2.5\,\mathrm{V}")]
        G = VGroup()
        for i, (n, c, v) in enumerate(rows):
            o = LEFT * 4.6 + UP * (2.0 - i * 2.0)
            w = curve(o, 7.0, 2 * n, np.sin, 40 / PI / n * .06, c, 6)
            lab = kr("기본파" if n == 1 else f"{n}고조파", 32, c).next_to(o, LEFT, .25)
            val = card(tex(v, 44, c), c, .12).next_to(o + RIGHT * 7.0, RIGHT, .3)
            G.add(VGroup(lab, w, val))
        self.add(G[0])
        for r in G[1:]:
            beat(self, FadeIn(r[0]), Create(r[1]), t=1.0, rt=.7)
            beat(self, FadeIn(r[2], shift=LEFT * .2), t=.8, rt=.3)
        f = tex(r"\tfrac{1}{3},\;\tfrac{1}{5}", 50, YEL).to_edge(DOWN, buff=.3)
        beat(self, FadeIn(f), t=.8, rt=.3)
        fill(self, VGroup(G[1][2], G[2][2]))


class Q5(Scene):
    def construct(self):
        g = q_base(self)
        g[1].set_stroke(opacity=.35)
        N = ValueTracker(1)
        cv = always_redraw(lambda: curve(Q_O, Q_L, 2, lambda th: ps(th, int(N.get_value()) | 1) * 10, Q_YS, BLU, 7))
        self.add(cv)
        lab = always_redraw(lambda: kr(f"{(int(N.get_value()) + 1) // 2}개 더함", 40, BLU).to_edge(UP, buff=.45))
        self.add(lab)
        self.wait(.5)
        for n in (3, 5, 7, 11, 15, 25, 41):
            self.play(N.animate.set_value(n), run_time=.5, rate_func=lambda t: 1.0 if t > .5 else 0.0); self.wait(.25)
        t = kr("점점 네모", 44, YEL).to_edge(DOWN, buff=.4)
        beat(self, FadeIn(t, shift=UP * .2), t=.8, rt=.4)
        fill(self, t)


class Q6(Scene):
    def construct(self):
        self.add(step_tag(3))
        vals = [40 / PI / n for n in (1, 3, 5, 7, 9)]
        o = LEFT * 4.0 + DOWN * 2.3
        base = Line(o + LEFT * .6, o + RIGHT * 9.0, color=MUTE, stroke_width=3)
        beat(self, Create(base), FadeIn(kr("진폭 스펙트럼", 44, YEL).to_edge(UP, buff=.45)), t=.8, rt=.4)
        B, Lb, Nm = bars(o, vals, [BLU, GRN, ORG, PUR, RED], unit=.33, gap=2.0, w=.7,
                         labs=[r"\omega_0", r"3\omega_0", r"5\omega_0", r"7\omega_0", r"9\omega_0"],
                         nums=["12.7", "4.2", "2.5", "1.8", "1.4"], size=34)
        for b, l, n in zip(B, Lb, Nm):
            beat(self, GrowFromEdge(b, DOWN), FadeIn(l), FadeIn(n), t=.55, rt=.35)
        xs = np.linspace(0, 8.4, 100)
        env = VMobject(color=YEL, stroke_width=4).set_points_smoothly(
            [o + np.array([x, 40 / PI / (1 + x / 1.0) * .33, 0]) for x in xs]).set_stroke(opacity=.8)
        env = DashedVMobject(env, num_dashes=40)
        beat(self, Create(env), FadeIn(tex(r"\propto \frac{1}{n}", 56, YEL).move_to(RIGHT * 3.2 + UP * 1.0)), t=1.1, rt=.6)
        fill(self, B)


# ================= STEP 4 고조파마다 페이저 =================
class R1(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = rc(UP * .4, 7.0, 2.8)
        beat(self, FadeIn(D["g"]), t=.8, rt=.5)
        beat(self, FadeIn(D["lr"], shift=DOWN * .2), t=.8, rt=.3)
        beat(self, FadeIn(D["lc"], shift=RIGHT * .2), t=.8, rt=.3)
        beat(self, FadeIn(D["vo"]), Indicate(D["C"], color=ORG), t=1.0, rt=.6)
        w = card(tex(r"\omega_0 = 1000\,\mathrm{rad/s}", 46, YEL), YEL, .15).to_edge(DOWN, buff=.35)
        beat(self, FadeIn(w, shift=UP * .2), t=1.0, rt=.4)
        fill(self, w)


class R2(Scene):
    def construct(self):
        self.add(step_tag(4))
        cols = [BLU, GRN, ORG]
        G = VGroup()
        for i, (n, c) in enumerate(zip((1, 3, 5), cols)):
            y = 2.2 - i * 2.0
            s = acsrc((-5.2, y), c, .45)
            lab = tex(f"n={n}", 34, c).next_to(s, LEFT, .2)
            box = card(kr("RC", 34, INK), MUTE, .25).move_to((-1.2, y, 0))
            a1 = Arrow(s.get_right(), box.get_left(), buff=.15, color=c, stroke_width=5)
            out = tex(r"V_{%d}" % n, 44, c).move_to((2.0, y, 0))
            a2 = Arrow(box.get_right(), out.get_left(), buff=.15, color=c, stroke_width=5)
            G.add(VGroup(lab, s, a1, box, a2, out))
        for r in G:
            beat(self, FadeIn(r, shift=RIGHT * .2), t=.9, rt=.5)
        plus = tex(r"+", 80, YEL).move_to((3.6, .2, 0))
        br = Brace(VGroup(*[r[5] for r in G]), RIGHT, color=YEL)
        beat(self, GrowFromCenter(br), FadeIn(kr("따로 풀고 더하기", 34, YEL).next_to(br, RIGHT, .2)), t=1.0, rt=.5)
        t = kr("선형 → 중첩", 40, YEL).to_edge(UP, buff=.35).shift(LEFT * 2)
        beat(self, FadeIn(t), t=.8, rt=.3)
        fill(self, br)


class R3(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = rc(LEFT * 2.6 + UP * 1.4, 5.0, 2.2, src=acsrc, rl="R", cl=r"\tfrac{1}{j\omega C}")
        beat(self, FadeIn(D["g"]), FadeIn(D["lr"]), FadeIn(D["lc"]), FadeIn(D["vo"]), t=1.0, rt=.6)
        e1 = tex(r"H = \frac{V_C}{V_s} = \frac{1/j\omega C}{R + 1/j\omega C}", 52, INK).move_to(DOWN * 1.4)
        beat(self, Write(e1), FadeIn(kr("전압 분배", 32, MUTE).next_to(e1, UP, .2).align_to(e1, LEFT)), t=1.4, rt=.9)
        e2 = tex(r"= \frac{1}{1 + j\omega RC}", 64, YEL).next_to(e1, DOWN, .35).align_to(e1, RIGHT)
        beat(self, Write(e2), t=1.2, rt=.7)
        fill(self, e2)


def hplane(sc, n, o=LEFT * 3.6 + DOWN * .2, s=3.0):
    m, p = H(n)
    P = plane(o, s + .4, lab=False)
    v = vec(o, o + s * m * U(p * 180 / PI), [BLU, GRN, ORG][(n - 1) // 2])
    return P, v, m, p


class R4(Scene):
    def construct(self):
        self.add(step_tag(4))
        e = tex(r"n=1:\;\omega RC = 1", 52, BLU).to_edge(UP, buff=.5)
        beat(self, Write(e), t=.9, rt=.5)
        e2 = tex(r"H = \frac{1}{1 + j}", 60, INK).move_to(RIGHT * 3.2 + UP * 1.0)
        beat(self, Write(e2), t=1.0, rt=.5)
        o = LEFT * 3.4 + DOWN * .4
        P, v, m, p = hplane(self, 1, o)
        ref = DashedLine(o, o + RIGHT * 3.0, color=MUTE, stroke_width=3)
        beat(self, FadeIn(P), Create(ref), FadeIn(tex("1", 34, MUTE).next_to(ref.get_end(), UP, .1)), t=.7, rt=.4)
        beat(self, GrowArrow(v), t=.9, rt=.6)
        arc = angle_arc(o, -45, 0, .9, YEL)
        beat(self, Create(arc), FadeIn(tex(r"-45^\circ", 40, YEL).next_to(o + U(-22) * .9, RIGHT, .1)), t=.9, rt=.4)
        r = tex(r"0.71\angle -45^\circ", 66, YEL).next_to(e2, DOWN, .6)
        beat(self, Write(r), t=1.0, rt=.5)
        fill(self, r)


class R5(Scene):
    def construct(self):
        self.add(step_tag(4))
        rows = [(1, BLU, r"\frac{1}{1+j}", r"0.71"), (3, GRN, r"\frac{1}{1+3j}", r"0.32"), (5, ORG, r"\frac{1}{1+5j}", r"0.20")]
        T = VGroup()
        for n, c, h, m in rows:
            T.add(VGroup(tex(f"n={n}", 46, c), tex(h, 50, INK), tex(r"\rightarrow", 46, MUTE), tex(m + r"\times", 60, c)).arrange(RIGHT, buff=.5))
        T.arrange(DOWN, buff=.55, aligned_edge=LEFT).shift(UP * .2)
        for r in T:
            beat(self, FadeIn(r[:3], shift=RIGHT * .2), t=.7, rt=.4)
            beat(self, FadeIn(r[3], scale=1.3), t=.7, rt=.3)
        fill(self, VGroup(T[1][3], T[2][3]))


class R6(Scene):
    def construct(self):
        self.add(step_tag(4))
        o = LEFT * 4.6 + DOWN * 2.2
        base = Line(o + LEFT * .6, o + RIGHT * 9.6, color=MUTE, stroke_width=3)
        beat(self, Create(base), FadeIn(tex(r"|H(n\omega_0)|", 50, INK).to_edge(UP, buff=.45)), t=.7, rt=.4)
        ns = [1, 3, 5, 7, 9]; vals = [H(n)[0] for n in ns]
        B, Lb, Nm = bars(o, vals, [BLU, GRN, ORG, PUR, RED], unit=3.8, gap=2.1, w=.8,
                         labs=[f"{n}" for n in ns], nums=[f"{v:.2f}" for v in vals], size=36)
        for b, l, n in zip(B, Lb, Nm):
            beat(self, GrowFromEdge(b, DOWN), FadeIn(l), FadeIn(n), t=.55, rt=.35)
        ar = Arrow(o + RIGHT * 1.0 + UP * 3.4, o + RIGHT * 8.6 + UP * 1.4, buff=0, color=YEL, stroke_width=6)
        beat(self, GrowArrow(ar), FadeIn(kr("빠를수록 더 깎음", 40, YEL).move_to(RIGHT * 2.6 + UP * 1.9)), t=1.1, rt=.6)
        fill(self, B)


# ================= STEP 5 다시 더하기 =================
class T1(Scene):
    def construct(self):
        self.add(step_tag(5))
        e = tex(r"12.7", 70, BLU); x = tex(r"\times", 60, MUTE); h = tex(r"0.71", 70, INK); eq = tex("=", 60, MUTE)
        r = tex(r"9.0\,\mathrm{V}", 84, YEL)
        g = VGroup(e, x, h, eq, r).arrange(RIGHT, buff=.35).shift(UP * 1.2)
        beat(self, FadeIn(e), FadeIn(kr("입력 기본파", 30, BLU).next_to(e, UP, .3)), t=.8, rt=.3)
        beat(self, FadeIn(x), FadeIn(h), FadeIn(kr("H", 30, MUTE).next_to(h, UP, .3)), t=.8, rt=.3)
        beat(self, FadeIn(eq), Write(r), t=1.0, rt=.5)
        o = LEFT * 4.6 + DOWN * 2.0; L = 9.2
        ax = wax(o, L, 1.4)
        w1 = curve(o, L, 2, lambda th: 40 / PI * np.sin(th), .07, BLU, 4).set_stroke(opacity=.5)
        w2 = curve(o, L, 2, lambda th: 40 / PI * .7071 * np.sin(th - PI / 4), .07, YEL, 6)
        beat(self, FadeIn(ax), Create(w1), t=.7, rt=.5)
        beat(self, Create(w2), t=.9, rt=.7)
        fill(self, r)


class T2(Scene):
    def construct(self):
        self.add(step_tag(5))
        q = kr("출력 3고조파는 몇 V?", 54, GRN).move_to(UP * 2.2)
        beat(self, FadeIn(q, shift=DOWN * .2), t=1.4, rt=.4)
        e = tex(r"4.2 \times 0.32", 76, INK).move_to(UP * .3)
        beat(self, Write(e), t=1.2, rt=.6)
        r = tex(r"\approx 1.3\,\mathrm{V}", 90, YEL).next_to(e, DOWN, .5)
        beat(self, Write(r), t=1.0, rt=.5)
        fill(self, r)


class T3(Scene):
    def construct(self):
        self.add(step_tag(5))
        def grp(o, a1, a3, title, c):
            B, Lb, Nm = bars(o, [a1, a3], [BLU, GRN], unit=.28, gap=1.6, w=.9, labs=[r"\omega_0", r"3\omega_0"],
                             nums=[f"{a1:.1f}", f"{a3:.1f}"], size=34)
            t = kr(title, 40, c).move_to(o + RIGHT * .8 + DOWN * 1.2)
            return VGroup(B, Lb, Nm, t)
        A = grp(LEFT * 5.0 + DOWN * 1.6, 12.7, 4.2, "입력", MUTE)
        Bg = grp(RIGHT * 1.6 + DOWN * 1.6, 9.0, 1.3, "출력", YEL)
        beat(self, FadeIn(A), t=.9, rt=.5)
        p1 = card(tex(r"33\%", 56, MUTE), MUTE, .15).next_to(A[0], UP, .5)
        beat(self, FadeIn(p1), t=.8, rt=.3)
        ar = Arrow(LEFT * 1.6 + DOWN * .4, RIGHT * .8 + DOWN * .4, buff=0, color=YEL, stroke_width=6)
        beat(self, GrowArrow(ar), FadeIn(Bg), t=1.0, rt=.6)
        p2 = card(tex(r"15\%", 66, YEL), YEL, .15).next_to(Bg[0], UP, .5)
        beat(self, FadeIn(p2, scale=1.3), t=.9, rt=.4)
        fill(self, p2)


class T4(Scene):
    def construct(self):
        self.add(step_tag(5))
        o1 = LEFT * 3.4 + UP * .2; o2 = RIGHT * 3.4 + UP * .2
        a = ValueTracker(0)
        P1 = plane(o1, 2.0, lab=False); P2 = plane(o2, 2.0, lab=False)
        v1 = always_redraw(lambda: vec(o1, o1 + 1.7 * U(a.get_value()), BLU))
        v3 = always_redraw(lambda: vec(o2, o2 + 1.1 * U(3 * a.get_value()), GRN))
        l1 = tex(r"\omega_0", 44, BLU).next_to(P1, DOWN, .2); l3 = tex(r"3\omega_0", 44, GRN).next_to(P2, DOWN, .2)
        beat(self, FadeIn(P1), FadeIn(P2), FadeIn(l1), FadeIn(l3), t=.4, rt=.3)
        self.add(v1, v3)
        self.play(a.animate.set_value(240), run_time=2.0, rate_func=linear)
        pl = tex("+", 90, RED).move_to(UP * .2)
        x = Cross(pl, stroke_color=RED, stroke_width=8).scale(1.3)
        self.play(a.animate.set_value(330), FadeIn(pl), run_time=.8, rate_func=linear)
        self.play(a.animate.set_value(420), Create(x), FadeIn(kr("페이저끼리 X", 40, RED).to_edge(UP, buff=.4)), run_time=.9, rate_func=linear)
        t = card(kr("시간 함수로 바꿔서 더하기", 40, YEL), YEL).to_edge(DOWN, buff=.3)
        self.play(a.animate.set_value(520), FadeIn(t, shift=UP * .2), run_time=1.0, rate_func=linear)
        tgt = DUR.get("T4", 0); rem = tgt - self.renderer.time
        if rem > .3:
            self.play(a.animate.set_value(520 + 90 * rem), run_time=rem, rate_func=linear)


class T5(Scene):
    def construct(self):
        self.add(step_tag(5))
        o = Q_O + UP * .2; ys = Q_YS
        ax = wax(o, Q_L, 2.2); self.add(ax)
        sw = sqwave(o, Q_L, 2, 10 * ys, YEL, 4).set_stroke(opacity=.4)
        beat(self, FadeIn(sw), FadeIn(kr("입력", 30, YEL).next_to(o + UP * 10 * ys, UP, .15).shift(RIGHT * .5)), t=.6, rt=.4)
        N = ValueTracker(1)
        cv = always_redraw(lambda: curve(o, Q_L, 2, lambda th: ps(th, int(N.get_value()) | 1, H) * 10, ys, ORG, 7))
        self.add(cv)
        for n in (3, 5, 9, 21):
            self.play(N.animate.set_value(n), run_time=.4, rate_func=lambda t: 1.0 if t > .5 else 0.0); self.wait(.2)
        ex = curve(o, Q_L, 2, rc_out, 10 * ys, WHITE, 3)
        ex = DashedVMobject(ex, num_dashes=90)
        beat(self, Create(ex), FadeIn(kr("모서리가 둥글게", 40, ORG).to_edge(UP, buff=.45)), t=1.0, rt=.7)
        c = kr("충전 → 방전", 36, INK).to_edge(DOWN, buff=.4)
        beat(self, FadeIn(c), t=.8, rt=.3)
        fill(self, c, ORG)


class T6(Scene):
    def construct(self):
        self.add(step_tag(5))
        ns = [1, 3, 5, 7, 9]
        def sp(o, g, c, title):
            vals = [40 / PI / n * (H(n)[0] if g else 1) for n in ns]
            B, Lb, _ = bars(o, vals, c, unit=.18, gap=.85, w=.5, labs=[f"{n}" for n in ns], size=28)
            return VGroup(B, Lb, kr(title, 36, c).next_to(o + RIGHT * 1.7, UP, 2.7))
        A = sp(LEFT * 5.6 + DOWN * 1.6, False, MUTE, "입력 스펙트럼")
        Bg = sp(RIGHT * 1.6 + DOWN * 1.6, True, ORG, "출력 스펙트럼")
        beat(self, FadeIn(A), t=.8, rt=.4)
        ar = Arrow(LEFT * 1.2 + DOWN * .6, RIGHT * 1.0 + DOWN * .6, buff=0, color=YEL, stroke_width=6)
        beat(self, GrowArrow(ar), TransformFromCopy(A, Bg), t=1.3, rt=.8)
        c = card(kr("저역 통과 필터", 52, YEL), YEL).to_edge(UP, buff=.35)
        beat(self, FadeIn(c, shift=DOWN * .2), t=1.0, rt=.4)
        fill(self, c)


# ================= 정리 =================
def sum_rows(items, size=34):
    g = VGroup(*[VGroup(kr(a, size, MUTE), b).arrange(RIGHT, buff=.5) for a, b in items]).arrange(DOWN, buff=.55, aligned_edge=LEFT)
    return g.shift(DOWN * .2)


class E1(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        rows = sum_rows([("직류", tex("a_0", 56, YEL)), ("기본파", tex(r"\omega_0", 56, BLU)), ("고조파", tex(r"2\omega_0,\;3\omega_0,\;\cdots", 56, GRN))], 38)
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.0, rt=.4)
        fill(self, rows)


class E2(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        rows = sum_rows([("짝함수", tex(r"b_n = 0", 54, GRN)), ("홀함수", tex(r"a_0 = a_n = 0", 54, ORG)), ("반파 대칭", tex(r"\text{짝수 } n = 0", 54, PUR) if False else kr("짝수 고조파 0", 40, PUR))], 38)
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.0, rt=.4)
        fill(self, rows)


class E3(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        steps = VGroup(card(kr("고조파 나누기", 36, BLU), BLU), card(VGroup(kr("페이저", 36, ORG), tex(r"\times H(n\omega_0)", 44, ORG)).arrange(DOWN, buff=.15), ORG),
                       card(kr("시간 함수로 더하기", 36, YEL), YEL)).arrange(RIGHT, buff=.9).shift(DOWN * .2)
        steps.scale_to_fit_width(min(steps.width, 13))
        beat(self, FadeIn(steps[0], shift=UP * .3), t=.9, rt=.4)
        for i in (1, 2):
            ar = Arrow(steps[i - 1].get_right(), steps[i].get_left(), buff=.12, color=MUTE)
            beat(self, GrowArrow(ar), FadeIn(steps[i], shift=UP * .3), t=1.0, rt=.4)
        fill(self, steps[2])


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("16장 · 푸리에 급수", 34, MUTE),
                        kr("고조파를 직접 더해 보기", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        beat(self, FadeIn(t[0]), t=.6, rt=.3)
        for m in t[1]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.0, rt=.4)
        o = DOWN * 3.0 + LEFT * 2.5
        N = ValueTracker(1)
        cv = always_redraw(lambda: curve(o, 5.0, 2, lambda th: ps(th, int(N.get_value()) | 1), .35, BLU, 5))
        self.add(cv)
        self.play(N.animate.set_value(15), run_time=2.0, rate_func=linear)
        fill(self, t)


class Next(Scene):
    def construct(self):
        items = ["주파수 응답", "라플라스", "푸리에 급수", "2포트"]
        cards = VGroup(*[card(kr(s, 36, YEL if s == "푸리에 급수" else MUTE), YEL if s == "푸리에 급수" else "#2a2e37", .3) for s in items]).arrange(RIGHT, buff=.35)
        cards.scale_to_fit_width(min(cards.width, 12.5))
        lab = kr("재생목록 · 회로이론 한눈에", 40, INK).next_to(cards, UP, .6)
        beat(self, FadeIn(lab), t=.8, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cards], lag_ratio=.3), run_time=1.6)
        arr = Arrow(cards[2].get_bottom() + DOWN * .2, cards[3].get_bottom() + DOWN * .2, buff=0, color=YEL, path_arc=PI / 2)
        beat(self, Create(arr), t=1.2, rt=.8)
        fill(self, cards[2])


# ================= 쇼츠 전용 =================
class AQ(Scene):
    def construct(self):
        o = LEFT * 5.0 + UP * .9; L = 10.0
        s1 = curve(o, 2.6, 1, np.sin, .7, BLU, 6)
        beat(self, Create(s1), t=.7, rt=.5)
        p = tex("+", 70, MUTE).next_to(s1, RIGHT, .3)
        s2 = curve(p.get_right() + RIGHT * .3, 2.6, 3, np.sin, .3, GRN, 6)
        beat(self, FadeIn(p), Create(s2), t=.7, rt=.5)
        p2 = tex(r"+\,\cdots =", 70, MUTE).next_to(s2, RIGHT, .3)
        beat(self, FadeIn(p2), t=.5, rt=.3)
        sw = sqwave(LEFT * 2.6 + DOWN * 2.0, 5.2, 2, .8, YEL, 7)
        beat(self, Create(sw), t=.9, rt=.7)
        q = tex("?", 110, YEL).next_to(sw, RIGHT, .4)
        beat(self, FadeIn(q, scale=1.4), t=.8, rt=.3)
        fill(self, sw)


def a_add(sc, N, msg):
    o = LEFT * 5.0 + UP * .2; L = 10.0; ys = 1.6
    ax = wax(o, L, 2.2); sc.add(ax)
    prev = curve(o, L, 2, lambda th: ps(th, N - 2), ys, BLU, 5).set_stroke(opacity=.5); sc.add(prev)
    h = curve(o, L, 2, lambda th: 4 / PI * np.sin(N * th) / N, ys, GRN, 4)
    beat(sc, Create(h), FadeIn(tex(r"\tfrac{1}{%d}\sin %d\omega_0 t" % (N, N), 52, GRN).to_edge(UP, buff=.5)), t=1.0, rt=.8)
    new = curve(o, L, 2, lambda th: ps(th, N), ys, BLU, 7)
    beat(sc, ReplacementTransform(VGroup(prev, h), new), t=1.0, rt=.7)
    t = kr(msg, 40, YEL).to_edge(DOWN, buff=.4)
    beat(sc, FadeIn(t), t=.6, rt=.3)
    fill(sc, new, BLU)


class A3(Scene):
    def construct(self): a_add(self, 3, "3배 빠르게, 1/3 크기")


class A5(Scene):
    def construct(self): a_add(self, 5, "5배 빠르게, 1/5 크기")


class BQ(Scene):
    def construct(self):
        ax = wax(Q_O, Q_L, 2.2); sw = sqwave(Q_O, Q_L, 2, 10 * Q_YS, YEL, 6)
        beat(self, FadeIn(ax), Create(sw), FadeIn(tex(r"10\,\mathrm{V}", 40, YEL).next_to(Q_O + UP * 10 * Q_YS, LEFT, .15)), t=.9, rt=.6)
        w = curve(Q_O, Q_L, 2, lambda th: ps(th, 1) * 10, Q_YS, BLU, 7)
        beat(self, Create(w), t=.9, rt=.7)
        q = tex(r"12.7\,\mathrm{V}\;?", 90, BLU).to_edge(UP, buff=.4)
        beat(self, Write(q), t=1.0, rt=.5)
        fill(self, q, BLU)


class BCoef(Scene):
    def construct(self):
        e = tex(r"b_1 = \frac{4 \times 10}{\pi}", 80, INK).move_to(UP * 1.0)
        beat(self, Write(e), t=1.0, rt=.6)
        r = tex(r"= \frac{40}{\pi} \approx 12.7", 80, BLU).next_to(e, DOWN, .5)
        beat(self, Write(r), t=1.2, rt=.6)
        fill(self, r, BLU)


class BCut(Scene):
    def construct(self):
        g = VGroup(wax(Q_O, Q_L, 2.2), sqwave(Q_O, Q_L, 2, 10 * Q_YS, YEL, 5).set_stroke(opacity=.5)); self.add(g)
        w1 = curve(Q_O, Q_L, 2, lambda th: ps(th, 1) * 10, Q_YS, BLU, 6); self.add(w1)
        h3 = curve(Q_O, Q_L, 2, lambda th: 40 / PI / 3 * np.sin(3 * th), Q_YS, GRN, 5)
        beat(self, Create(h3), FadeIn(kr("3배 고조파", 40, GRN).to_edge(UP, buff=.45)), t=.9, rt=.6)
        w13 = curve(Q_O, Q_L, 2, lambda th: ps(th, 3) * 10, Q_YS, BLU, 7)
        beat(self, ReplacementTransform(VGroup(w1, h3), w13), FadeIn(kr("꼭대기가 깎임", 36, BLU).to_edge(DOWN, buff=.4)), t=1.0, rt=.7)
        w5 = curve(Q_O, Q_L, 2, lambda th: ps(th, 5) * 10, Q_YS, BLU, 7)
        beat(self, Transform(w13, w5), t=.9, rt=.6)
        fill(self, w13, BLU)


class CQ(Scene):
    def construct(self):
        E = coef_eqs(50).shift(UP * .8)
        beat(self, FadeIn(E), t=.8, rt=.4)
        x = Cross(E, stroke_color=RED, stroke_width=7)
        beat(self, Create(x), t=.7, rt=.4)
        t = kr("적분 전에 절반은 0", 60, YEL).move_to(DOWN * 2.2)
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.4)
        fill(self, t)


class CSq(Scene):
    def construct(self):
        ax = wax(Q_O + UP * 1.0, Q_L, 1.6); sw = sqwave(Q_O + UP * 1.0, Q_L, 2, 1.2, YEL, 6)
        beat(self, FadeIn(ax), Create(sw), t=.9, rt=.7)
        e = tex(r"\frac{40}{\pi}\left(\sin\omega_0 t + \tfrac{1}{3}\sin 3\omega_0 t + \tfrac{1}{5}\sin 5\omega_0 t + \cdots\right)", 46, YEL).move_to(DOWN * 1.9)
        beat(self, Write(e), t=1.4, rt=1.0)
        t = kr("홀수 sin 항만", 40, GRN).next_to(e, DOWN, .35)
        beat(self, FadeIn(t), t=.8, rt=.3)
        fill(self, e)


class DQ(Scene):
    def construct(self):
        D = rc(UP * 1.2, 5.0, 2.0, rl="", cl="")
        beat(self, FadeIn(D["g"]), t=.7, rt=.4)
        o1 = LEFT * 6.2 + DOWN * 2.2; o2 = RIGHT * 1.0 + DOWN * 2.2
        si = sqwave(o1, 5.0, 2, .7, YEL, 6)
        beat(self, Create(si), t=.8, rt=.6)
        ar = Arrow(o1 + RIGHT * 5.2, o2 + LEFT * .1, buff=0, color=MUTE, stroke_width=5)
        so = curve(o2, 5.0, 2, rc_out, .7, ORG, 7)
        beat(self, GrowArrow(ar), Create(so), t=1.1, rt=.8)
        fill(self, so, ORG)


class EQ(Scene):
    def construct(self):
        o = LEFT * 1.6 + DOWN * .4
        P = plane(o, 2.4, lab=False); beat(self, FadeIn(P), t=.3, rt=.3)
        v1 = vec(o, o + 2.0 * U(-45), BLU); v3 = vec(o + 2.0 * U(-45), o + 2.0 * U(-45) + 1.0 * U(-72), GRN)
        beat(self, GrowArrow(v1), FadeIn(tex(r"\omega_0", 40, BLU).next_to(v1.get_center(), UR, .1)), t=.7, rt=.4)
        beat(self, GrowArrow(v3), FadeIn(tex(r"3\omega_0", 40, GRN).next_to(v3.get_center(), RIGHT, .15)), t=.7, rt=.4)
        s = vec(o, o + 2.0 * U(-45) + 1.0 * U(-72), YEL, 8)
        beat(self, GrowArrow(s), t=.6, rt=.4)
        q = tex(r"= ?", 100, RED).move_to(RIGHT * 3.6 + UP * .6)
        beat(self, FadeIn(q, scale=1.3), FadeIn(kr("틀린 계산", 44, RED).next_to(q, DOWN, .3)), t=.9, rt=.3)
        fill(self, q, RED)


class ESame(Scene):
    def construct(self):
        o = LEFT * 1.8 + DOWN * 1.6; s = .5
        a = o + RIGHT * 6 * s; b = a + UP * 8 * s
        vr = vec(o, a, BLU); vl = vec(a, b, GRN); vs = vec(o, b, YEL, 9)
        t = kr("같은 주파수", 48, YEL).to_edge(UP, buff=.5)
        beat(self, FadeIn(t), t=.6, rt=.3)
        beat(self, GrowArrow(vr), t=.6, rt=.4)
        beat(self, GrowArrow(vl), t=.6, rt=.4)
        beat(self, GrowArrow(vs), FadeIn(kr("화살표로 더하기 OK", 38, YEL).next_to(vs.get_center(), LEFT, .5)), t=.9, rt=.5)
        fill(self, vs)


class ETime(Scene):
    def construct(self):
        r1 = tex(r"9.0\sin(\omega_0 t - 45^\circ)", 52, BLU)
        r2 = tex(r"+\;1.3\sin(3\omega_0 t - 72^\circ)", 52, GRN)
        r3 = tex(r"+\;\cdots", 52, MUTE)
        G = VGroup(r1, r2, r3).arrange(DOWN, buff=.3, aligned_edge=LEFT).shift(UP * 1.6)
        beat(self, Write(r1), t=.8, rt=.5)
        beat(self, Write(r2), t=.8, rt=.5)
        beat(self, FadeIn(r3), t=.4, rt=.3)
        o = LEFT * 4.6 + DOWN * 2.0; L = 9.2
        ax = wax(o, L, 1.3)
        w = curve(o, L, 2, lambda th: ps(th, 21, H), 1.0, ORG, 6)
        beat(self, FadeIn(ax), Create(w), FadeIn(kr("시간 함수로 더하기", 34, ORG).next_to(ax, UP, .05).align_to(ax, RIGHT)), t=1.2, rt=.8)
        fill(self, w, ORG)


class EWarn(Scene):
    def construct(self):
        c = card(VGroup(kr("가장 많이 틀리는 곳", 48, RED), VGroup(kr("주파수 다른 페이저", 40, INK), tex(r"\mathbf{V}_1 + \mathbf{V}_3", 56, INK)).arrange(RIGHT, buff=.3)).arrange(DOWN, buff=.35), RED)
        c.shift(UP * 1.0)
        beat(self, FadeIn(c[0]), FadeIn(c[1][0]), t=.8, rt=.4)
        x = Cross(c[1][1][1], stroke_color=RED, stroke_width=6)
        beat(self, FadeIn(c[1][1]), Create(x), t=1.0, rt=.6)
        ok = card(kr("시간 함수로 바꿔서 더하기", 44, YEL), YEL).move_to(DOWN * 2.0)
        beat(self, FadeIn(ok, shift=UP * .2), t=1.0, rt=.4)
        fill(self, ok)
