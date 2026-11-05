# Y-Δ 변환 롱폼 모션그래픽. 16:9, 핵심은 가운데(세로 쇼츠에서도 씀). 푸리에 편 형식.
# 장면 하나 = 문장 하나. 장면 길이는 dur.json(음성 실제 길이)에 맞춰 fill() 로 채운다 → 멈춘 화면 없음.
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


# 장면 자체 애니메이션이 dur.json 보다 길면(말이 더 짧으면) speed.json 배율로 play/wait 를 줄인다 (잘림 방지)
_SP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speed.json")
SPEED = json.load(open(_SP)) if os.path.exists(_SP) else {}
_play0, _wait0 = Scene.play, Scene.wait


def _play(self, *a, **k):
    f = SPEED.get(type(self).__name__, 1.0)
    if f < 1:
        rt = k.pop("run_time", None)
        if rt is None:
            rt = max([x.run_time for x in a if hasattr(x, "run_time") and isinstance(getattr(x, "run_time"), (int, float))] or [1.0])
        k["run_time"] = rt * f
    return _play0(self, *a, **k)


def _wait(self, duration=1.0, *a, **k):
    return _wait0(self, duration * SPEED.get(type(self).__name__, 1.0), *a, **k)


Scene.play, Scene.wait = _play, _wait
def fill(sc, m, c=YEL, extra=0.0):
    """장면 길이를 dur.json 에 맞춘다: 남은 시간 동안 m 둘레를 그렸다 지우기 (멈춘 화면 방지)."""
    tgt = DUR.get(type(sc).__name__, 0) + extra
    rem = tgt - sc.renderer.time
    while rem > 1.7:
        sc.play(Circumscribe(m, color=c, buff=.18, fade_out=True, run_time=1.3)); sc.wait(.2); rem -= 1.5
    sc.wait(max(.3, rem))




# ---------- Y-Δ 전용 ----------
def om(v, size=38, c=INK):
    return tex(rf"{v}\,\Omega", size, c)


def node(p, lab=None, c=INK, d=UP, size=34):
    g = VGroup(Dot(P3(p), radius=.09, color=c))
    if lab: g.add(tex(lab, size, c).next_to(g[0], d, .12))
    return g


def rlab(R, txt, side, c=INK, size=36, buff=.68):
    """저항 가운데에서 side 방향으로 buff 만큼 떨어진 곳에 라벨 (대각선 저항도 가깝게)."""
    v = P3(side); v = v / max(np.linalg.norm(v), 1e-6)
    return (txt if isinstance(txt, Mobject) else om(txt, size, c)).move_to(R.get_center() + v * buff)


# 브리지 회로 마디 (전원은 왼쪽 세로)
PA, PB, PC, PD, PN = np.array([0, 2.4, 0.]), np.array([-2.4, .2, 0.]), np.array([2.4, .2, 0.]), np.array([0, -2.0, 0.]), np.array([0, 1.25, 0.])
XS = -4.4


def bridge(vals=(6, 18, 12, 10, 6), src=r"18\,\mathrm{V}", cols=None, y=False, yvals=(3, 2, 6), mid=True, labels=True):
    """브리지 회로. vals = (ab, ac, bc, bd, cd). y=True 면 위쪽 Δ 대신 Y(an, nb, nc = yvals).
    반환 dict: all, R{키: 저항}, L{키: 라벨}, N{a,b,c,d[,n]}, src, wires."""
    cols = cols or {}
    R, L = {}, {}
    def add(k, p, q, v, side, c=None):
        R[k] = resistor(p, q, c or cols.get(k, INK))
        if v is not None: L[k] = rlab(R[k], v, side, c or cols.get(k, INK))
    if not y:
        add("ab", PA, PB, vals[0], LEFT + UP * .3); add("ac", PA, PC, vals[1], RIGHT + UP * .3)
        if mid: add("bc", PB, PC, vals[2], DOWN)
    else:
        add("an", PA, PN, yvals[0], RIGHT); add("nb", PN, PB, yvals[1], UP + LEFT * .2); add("nc", PN, PC, yvals[2], UP + RIGHT * .2)
    add("bd", PB, PD, vals[3], LEFT + DOWN * .3); add("cd", PC, PD, vals[4], RIGHT + DOWN * .3)
    N = {"a": node(PA, "a", INK, UP), "b": node(PB, "b", INK, LEFT), "c": node(PC, "c", INK, RIGHT), "d": node(PD, "d", INK, DOWN)}
    if y: N["n"] = node(PN, "n", YEL, DOWN + RIGHT * .3)
    bat = battery((XS, .2), YEL, 1.0)
    wires = VGroup(wire(PA, (XS, 2.4)), wire((XS, 2.4), (XS, .38)), wire((XS, .02), (XS, -2.0)), wire((XS, -2.0), PD))
    lsrc = tex(src, 36, YEL).next_to(bat, LEFT, .25)
    D = dict(R=R, L=L, N=N, src=VGroup(bat, lsrc), wires=wires)
    parts = [wires, bat] + ([lsrc] if src else []) + list(R.values()) + (list(L.values()) if labels else []) + list(N.values())
    D["all"] = VGroup(*parts)
    if not labels: D["all"] = VGroup(*[p for p in parts])
    return D


def delta(o=ORIGIN, s=1.0, vals=(6, 18, 12), cols=None, labels=True, tag=None):
    """삼각형 Δ: 꼭짓점 a(위), b(왼쪽 아래), c(오른쪽 아래). vals = (ab, ac, bc)."""
    o = P3(o); cols = cols or {}
    a, b, c = o + np.array([0, 1.5, 0]) * s, o + np.array([-1.9, -1.3, 0]) * s, o + np.array([1.9, -1.3, 0]) * s
    R = {"ab": resistor(a, b, cols.get("ab", INK)), "ac": resistor(a, c, cols.get("ac", INK)), "bc": resistor(b, c, cols.get("bc", INK))}
    L = {}
    if labels and vals:
        L = {"ab": rlab(R["ab"], vals[0], LEFT + UP * .3, cols.get("ab", INK)), "ac": rlab(R["ac"], vals[1], RIGHT + UP * .3, cols.get("ac", INK)),
             "bc": rlab(R["bc"], vals[2], DOWN, cols.get("bc", INK))}
    N = {"a": node(a, "a", INK, UP), "b": node(b, "b", INK, DOWN + LEFT * .3), "c": node(c, "c", INK, DOWN + RIGHT * .3)}
    D = dict(R=R, L=L, N=N, pts=dict(a=a, b=b, c=c))
    D["all"] = VGroup(*R.values(), *L.values(), *N.values())
    if tag: D["tag"] = kr(tag, 40, YEL).next_to(D["all"], DOWN, .4); D["all"].add(D["tag"])
    return D


def ystar(o=ORIGIN, s=1.0, vals=(3, 2, 6), cols=None, labels=True, tag=None, show=("a", "b", "c")):
    """Y: 가운데 n 에서 a(위), b(왼쪽 아래), c(오른쪽 아래)로. vals = (a, b, c)."""
    o = P3(o); cols = cols or {}
    a, b, c = o + np.array([0, 1.5, 0]) * s, o + np.array([-1.9, -1.3, 0]) * s, o + np.array([1.9, -1.3, 0]) * s
    n = o + np.array([0, -.2, 0]) * s
    R, L = {}, {}
    for k, p, side in (("a", a, RIGHT), ("b", b, UP + LEFT * .3), ("c", c, UP + RIGHT * .3)):
        if k not in show: continue
        R[k] = resistor(n, p, cols.get(k, INK))
        if labels and vals: L[k] = rlab(R[k], vals["abc".index(k)], side, cols.get(k, INK))
    N = {"a": node(a, "a", INK, UP), "b": node(b, "b", INK, DOWN + LEFT * .3), "c": node(c, "c", INK, DOWN + RIGHT * .3), "n": node(n, None, YEL)}
    D = dict(R=R, L=L, N=N, pts=dict(a=a, b=b, c=c, n=n))
    D["all"] = VGroup(*R.values(), *L.values(), *N.values())
    if tag: D["tag"] = kr(tag, 40, YEL).next_to(D["all"], DOWN, .4); D["all"].add(D["tag"])
    return D


def cross(m, c=RED):
    return Cross(m, stroke_color=c, stroke_width=7, scale_factor=1.1)


def big(txt, size=96, c=YEL):
    return tex(txt, size, c)


def frac(num, den, size=48, c=INK):
    return tex(rf"\dfrac{{{num}}}{{{den}}}", size, c)


DY_EQ = r"R_a = \frac{R_{ab}\,R_{ac}}{R_{ab} + R_{bc} + R_{ac}}"
YD_EQ = r"R_{ab} = \frac{R_a R_b + R_b R_c + R_c R_a}{R_c}"


def show_bridge(sc, B, t=.3, with_src=True):
    """브리지를 소자 하나씩 띄운다 (2~4초 안에 화면 변화)."""
    if with_src:
        beat(sc, FadeIn(B["wires"]), FadeIn(B["src"]), t=t, rt=.3)
    for k in B["R"]:
        beat(sc, Create(B["R"][k]), FadeIn(B["L"][k]) if k in B["L"] else FadeIn(VGroup()), t=t, rt=.3)
    beat(sc, *[FadeIn(n) for n in B["N"].values()], t=t, rt=.25)


# ================= 인트로 =================
class Hook(Scene):
    def construct(self):
        B = bridge(); B["all"].shift(LEFT * .4)
        show_bridge(self, B, .32)
        q = card(VGroup(kr("합성 저항", 40, INK), tex("= \\,?", 70, YEL)).arrange(RIGHT, buff=.2), YEL).move_to(RIGHT * 4.6 + UP * .6)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, q)


class Goal(Scene):
    def construct(self):
        B = bridge(); B["all"].scale(.72).shift(LEFT * 3.4 + DOWN * .2); self.add(B["all"])
        beat(self, B["R"]["bc"].animate.set_color(RED), B["L"]["bc"].animate.set_color(RED), t=.8, rt=.4)
        s = kr("직렬 공식", 40, MUTE).move_to(RIGHT * 3.6 + UP * 2.2); p = kr("병렬 공식", 40, MUTE).next_to(s, DOWN, .5)
        beat(self, FadeIn(s), Create(cross(s)), t=.7, rt=.4)
        beat(self, FadeIn(p), Create(cross(p)), t=.7, rt=.4)
        t = card(kr("Y-Δ 변환", 56, YEL), YEL).move_to(RIGHT * 3.6 + DOWN * 1.4)
        beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        fill(self, t)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "왜 안 풀리나", BLU), ("2", "Δ → Y", PUR), ("3", "Y → Δ", GRN), ("4", "예제 풀이", ORG), ("5", "평형 브리지", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.0, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.0, rt=.8)
        fill(self, cards)


# ================= STEP 1 왜 안 풀리나 =================
class W1(Scene):
    def construct(self):
        self.add(step_tag(1))
        # 직렬
        o = LEFT * 3.6 + UP * .3
        r1 = resistor(o + LEFT * 2.2, o + LEFT * .2, BLU); r2 = resistor(o + RIGHT * .2, o + RIGHT * 2.2, BLU)
        w = VGroup(wire(o + LEFT * 2.6, o + LEFT * 2.2), wire(o + LEFT * .2, o + RIGHT * .2), wire(o + RIGHT * 2.2, o + RIGHT * 2.6))
        ar = Arrow(o + LEFT * 2.0 + UP * .7, o + RIGHT * 2.0 + UP * .7, buff=0, color=YEL, stroke_width=5)
        beat(self, FadeIn(kr("직렬", 44, BLU).move_to(o + UP * 2.2)), Create(VGroup(w, r1, r2)), t=.9, rt=.6)
        beat(self, GrowArrow(ar), FadeIn(kr("같은 전류 I", 34, YEL).next_to(ar, UP, .15)), t=1.0, rt=.5)
        # 병렬
        o = RIGHT * 3.6 + UP * .3
        top, bot = o + UP * 1.2, o + DOWN * 1.2
        p1 = resistor(top + LEFT * 1.0, bot + LEFT * 1.0, GRN); p2 = resistor(top + RIGHT * 1.0, bot + RIGHT * 1.0, GRN)
        w2 = VGroup(wire(top + LEFT * 1.6, top + RIGHT * 1.6), wire(bot + LEFT * 1.6, bot + RIGHT * 1.6))
        beat(self, FadeIn(kr("병렬", 44, GRN).move_to(o + UP * 2.2)), Create(VGroup(w2, p1, p2)), t=.9, rt=.6)
        v = VGroup(tex("+", 34, YEL).next_to(top, UP, .1).shift(RIGHT * 2.0), tex("-", 34, YEL).next_to(bot, DOWN, .1).shift(RIGHT * 2.0))
        beat(self, FadeIn(v), FadeIn(kr("같은 전압 V", 34, YEL).next_to(VGroup(p1, p2), DOWN, .5)), t=1.0, rt=.5)
        fill(self, VGroup(ar, v))


class W2(Scene):
    def construct(self):
        self.add(step_tag(1))
        B = bridge(); B["all"].shift(LEFT * .4); self.add(B["all"])
        beat(self, B["R"]["ab"].animate.set_color(BLU), B["L"]["ab"].animate.set_color(BLU), B["R"]["bd"].animate.set_color(BLU), B["L"]["bd"].animate.set_color(BLU), t=.9, rt=.5)
        q = kr("직렬?", 48, BLU).move_to(RIGHT * 4.6 + UP * 1.8)
        beat(self, FadeIn(q), t=.8, rt=.3)
        leak = Arrow(PB + LEFT * .4 + RIGHT * .5, PB + (PC - PB) * .45, buff=.15, color=RED, stroke_width=6).shift(LEFT * .4)
        beat(self, GrowArrow(leak), FadeIn(kr("전류가 새 나감", 32, RED).move_to(RIGHT * 4.6 + DOWN * .3)), t=1.2, rt=.5)
        x = cross(q); beat(self, Create(x), FadeIn(kr("직렬 아님", 40, RED).next_to(q, DOWN, .4)), t=.9, rt=.4)
        fill(self, VGroup(q, x), RED)


class W3(Scene):
    def construct(self):
        self.add(step_tag(1))
        B = bridge(); B["all"].shift(LEFT * .4); self.add(B["all"])
        beat(self, B["R"]["ab"].animate.set_color(GRN), B["L"]["ab"].animate.set_color(GRN), B["R"]["ac"].animate.set_color(GRN), B["L"]["ac"].animate.set_color(GRN), t=.9, rt=.5)
        q = kr("병렬?", 48, GRN).move_to(RIGHT * 4.6 + UP * 1.8)
        beat(self, FadeIn(q), t=.8, rt=.3)
        nb = Circle(.32, color=BLU, stroke_width=5).move_to(PB + LEFT * .4); nc = Circle(.32, color=ORG, stroke_width=5).move_to(PC + LEFT * .4)
        beat(self, Create(nb), Create(nc), FadeIn(kr("끝이 다른 마디", 32, ORG).next_to(nc, RIGHT, .3).shift(DOWN * .9)), t=1.2, rt=.5)
        x = cross(q); beat(self, Create(x), FadeIn(kr("병렬 아님", 40, RED).next_to(q, DOWN, .4)), t=.9, rt=.4)
        fill(self, VGroup(q, x), RED)


class W4(Scene):
    def construct(self):
        self.add(step_tag(1))
        B = bridge(); B["all"].scale(.78).shift(LEFT * 3.3 + DOWN * .2); self.add(B["all"])
        tri = VGroup(B["R"]["ab"], B["R"]["ac"], B["R"]["bc"])
        beat(self, tri.animate.set_color(YEL), *[B["L"][k].animate.set_color(YEL) for k in ("ab", "ac", "bc")], t=1.0, rt=.6)
        D = delta(RIGHT * 3.6 + UP * .3, 1.0, cols=dict(ab=YEL, ac=YEL, bc=YEL))
        beat(self, TransformFromCopy(tri, VGroup(*D["R"].values())), FadeIn(VGroup(*D["L"].values(), *D["N"].values())), t=1.3, rt=.9)
        t = card(kr("Δ  델타", 48, YEL), YEL).next_to(D["all"], DOWN, .35)
        beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        fill(self, D["all"])


class W5(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = delta(LEFT * 3.6 + UP * .3, 1.0, cols=dict(ab=MUTE, ac=MUTE, bc=MUTE), labels=False); self.add(D["all"])
        self.add(kr("Δ", 44, MUTE).next_to(D["all"], DOWN, .4))
        Y = ystar(RIGHT * 3.6 + UP * .3, 1.0, cols=dict(a=GRN, b=GRN, c=GRN), labels=False)
        beat(self, FadeIn(Y["N"]["n"]), t=.5, rt=.3)
        for k in "abc":
            beat(self, Create(Y["R"][k]), FadeIn(Y["N"][k]), t=.7, rt=.5)
        t = card(kr("Y  와이", 48, GRN), GRN).next_to(Y["all"], DOWN, .35)
        beat(self, FadeIn(t, shift=UP * .2), FadeIn(kr("한 점에서 세 갈래", 32, GRN).next_to(t, DOWN, .2)), t=.9, rt=.4)
        fill(self, Y["all"], GRN)


class W6(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = delta(LEFT * 3.6 + UP * .4, .95, cols=dict(ab=YEL, ac=YEL, bc=YEL))
        Y = ystar(RIGHT * 3.6 + UP * .4, .95, cols=dict(a=GRN, b=GRN, c=GRN))
        beat(self, FadeIn(D["all"]), t=.7, rt=.4)
        ar = VGroup(Arrow(LEFT * 1.3 + UP * .6, RIGHT * 1.3 + UP * .6, buff=0, color=INK, stroke_width=5), Arrow(RIGHT * 1.3 + UP * .1, LEFT * 1.3 + UP * .1, buff=0, color=INK, stroke_width=5))
        beat(self, GrowArrow(ar[0]), GrowArrow(ar[1]), FadeIn(kr("바꿔 끼우기", 30, INK).next_to(ar, UP, .15)), t=.9, rt=.5)
        beat(self, FadeIn(Y["all"]), t=.9, rt=.5)
        box = SurroundingRectangle(VGroup(D["all"], Y["all"]), color=YEL, buff=.35, corner_radius=.2)
        beat(self, Create(box), FadeIn(kr("a, b, c 바깥에서 보면 똑같이 동작", 36, YEL).next_to(box, DOWN, .25)), t=1.1, rt=.6)
        fill(self, box)


# ================= STEP 2 Δ → Y =================
def d2y_layout(sc, step=2, eq=DY_EQ, dvals=(6, 18, 12), dcols=None):
    sc.add(step_tag(step))
    D = delta(LEFT * 4.2 + DOWN * .6, .9, vals=dvals, cols=dcols); sc.add(D["all"])
    E = tex(eq, 54, INK).move_to(RIGHT * 1.8 + UP * 1.9)
    return D, E


class D1(Scene):
    def construct(self):
        D, E = d2y_layout(self)
        beat(self, Write(E), FadeIn(kr("Δ → Y", 40, PUR).to_edge(UP, buff=.45).shift(LEFT * 2)), t=1.2, rt=.8)
        den = E[0][7:]           # 분모 R_ab + R_bc + R_ac
        br = Brace(den, DOWN, color=YEL)
        beat(self, den.animate.set_color(YEL), GrowFromCenter(br), t=.9, rt=.5)
        s = tex(r"6 + 12 + 18 = 36", 50, YEL).next_to(br, DOWN, .3)
        beat(self, Write(s), FadeIn(kr("세 저항의 합", 34, YEL).next_to(s, DOWN, .25)), t=1.1, rt=.6)
        fill(self, s)


class D2(Scene):
    def construct(self):
        D, E = d2y_layout(self); self.add(E)
        num = E[0][3:7]
        br = Brace(num, UP, color=BLU)
        beat(self, num.animate.set_color(BLU), GrowFromCenter(br), FadeIn(kr("마디 a에 붙은 둘의 곱", 34, BLU).next_to(br, UP, .2)), t=1.0, rt=.6)
        beat(self, D["R"]["ab"].animate.set_color(BLU), D["L"]["ab"].animate.set_color(BLU), D["R"]["ac"].animate.set_color(BLU), D["L"]["ac"].animate.set_color(BLU),
             Circumscribe(D["N"]["a"], color=BLU, buff=.15), t=1.1, rt=.7)
        s = tex(r"6 \times 18", 54, BLU).move_to(RIGHT * 1.8 + DOWN * .8)
        beat(self, Write(s), t=.9, rt=.5)
        fill(self, s, BLU)


def d2y_calc(sc, key, lab, expr, val, col, done):
    """Δ(왼쪽)·Y(오른쪽): 마디 key 의 Y 저항 계산. done = 이미 구한 Y 다리들."""
    sc.add(step_tag(2))
    D = delta(LEFT * 4.3 + DOWN * .3, .85, cols={k: (col if key in k else MUTE) for k in ("ab", "ac", "bc")}); sc.add(D["all"])
    Y = ystar(RIGHT * 4.3 + DOWN * .3, .85, labels=False); sc.add(Y["N"]["n"], *[Y["N"][k] for k in "abc"])
    for k in done:
        sc.add(Y["R"][k].set_color(INK), rlab(Y["R"][k], (3, 2, 6)["abc".index(k)], (RIGHT, UP + LEFT * .3, UP + RIGHT * .3)["abc".index(k)]))
    e = tex(rf"R_{key} = \frac{{{expr}}}{{36}}", 54, INK).move_to(UP * 2.3)
    beat(sc, Write(e), Circumscribe(D["N"][key], color=col, buff=.15), t=1.3, rt=.7)
    r = tex(rf"= {val}\,\Omega", 60, col).next_to(e, DOWN, .35)
    beat(sc, Write(r), t=1.0, rt=.5)
    leg = Y["R"][key].set_color(col)
    beat(sc, Create(leg), FadeIn(rlab(leg, val, (RIGHT, UP + LEFT * .3, UP + RIGHT * .3)["abc".index(key)], col)), t=1.0, rt=.6)
    fill(sc, r, col)


class D3(Scene):
    def construct(self): d2y_calc(self, "a", "a", r"6 \times 18", 3, BLU, "")


class D4(Scene):
    def construct(self): d2y_calc(self, "b", "b", r"6 \times 12", 2, GRN, "a")


class D5(Scene):
    def construct(self): d2y_calc(self, "c", "c", r"18 \times 12", 6, ORG, "ab")


class D6(Scene):
    def construct(self):
        self.add(step_tag(2))
        c = card(VGroup(kr("Δ → Y 외우기", 34, MUTE), kr("이웃 둘의 곱 ÷ 전체 합", 52, YEL)).arrange(DOWN, buff=.25), YEL).move_to(UP * 1.6)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.5)
        D = delta(LEFT * 3.4 + DOWN * 1.9, .62, cols=dict(ab=MUTE, ac=MUTE, bc=MUTE)); Y = ystar(RIGHT * 3.4 + DOWN * 1.9, .62)
        beat(self, FadeIn(D["all"]), FadeIn(Y["all"]), t=.9, rt=.5)
        gt = tex(r"6,\,18,\,12 \;>\; 3,\,2,\,6", 44, GRN).move_to(DOWN * 1.7)
        beat(self, Write(gt), FadeIn(kr("Y 는 항상 더 작음", 32, GRN).next_to(gt, DOWN, .2)), t=1.0, rt=.5)
        fill(self, c)


# ================= STEP 3 Y → Δ =================
def y2d_layout(sc):
    sc.add(step_tag(3))
    Y = ystar(LEFT * 4.3 + DOWN * .5, .9); sc.add(Y["all"])
    E = tex(YD_EQ, 50, INK).move_to(RIGHT * 1.9 + UP * 2.0)
    return Y, E


class Y1(Scene):
    def construct(self):
        Y, E = y2d_layout(self)
        beat(self, Write(E), FadeIn(kr("Y → Δ", 40, GRN).to_edge(UP, buff=.45).shift(LEFT * 2.5)), t=1.2, rt=.8)
        num = E[0][4:16]
        br = Brace(num, UP, color=YEL)
        beat(self, num.animate.set_color(YEL), GrowFromCenter(br), FadeIn(kr("곱의 합", 34, YEL).next_to(br, UP, .15)), t=.9, rt=.5)
        s = tex(r"3\!\cdot\!2 + 2\!\cdot\!6 + 6\!\cdot\!3 = 36", 50, YEL).move_to(RIGHT * 1.9 + DOWN * .5)
        beat(self, Write(s), t=1.2, rt=.8)
        fill(self, s)


class Y2(Scene):
    def construct(self):
        Y, E = y2d_layout(self); self.add(E)
        den = E[0][17:]
        br = Brace(den, DOWN, color=ORG)
        beat(self, den.animate.set_color(ORG), GrowFromCenter(br), FadeIn(kr("맞은편 저항", 34, ORG).next_to(br, DOWN, .15)), t=1.0, rt=.5)
        edge = DashedLine(Y["pts"]["a"], Y["pts"]["b"], color=BLU, stroke_width=5, dash_length=.15)
        beat(self, Create(edge), FadeIn(kr("구하려는 변 ab", 30, BLU).next_to(edge, LEFT, .2)), t=1.0, rt=.5)
        beat(self, Y["R"]["c"].animate.set_color(ORG), Y["L"]["c"].animate.set_color(ORG), Circumscribe(Y["R"]["c"], color=ORG), t=1.0, rt=.6)
        fill(self, VGroup(edge, Y["R"]["c"]), ORG)


def y2d_calc(sc, items, done):
    """Y(왼쪽) → Δ(오른쪽) 변 계산. items = [(변, 맞은편키, 값, 색)], done = 이미 구한 변."""
    sc.add(step_tag(3))
    Y = ystar(LEFT * 4.3 + DOWN * .3, .85); sc.add(Y["all"])
    D = delta(RIGHT * 4.3 + DOWN * .3, .85, labels=False); sc.add(*D["N"].values())
    for k in done:
        sc.add(D["R"][k].set_color(INK), rlab(D["R"][k], dict(ab=6, ac=18, bc=12)[k], dict(ab=LEFT + UP * .3, ac=RIGHT + UP * .3, bc=DOWN)[k]))
    eqs = VGroup()
    for i, (edge, opp, val, col) in enumerate(items):
        e = tex(rf"R_{{{edge}}} = \frac{{36}}{{R_{opp}}} = \frac{{36}}{{{(3, 2, 6)['abc'.index(opp)]}}} = {val}\,\Omega", 48, col)
        e.move_to(UP * (2.6 - i * 1.5)); eqs.add(e)
        beat(sc, Write(e), Y["R"][opp].animate.set_color(col), Y["L"][opp].animate.set_color(col), t=1.3, rt=.7)
        r = D["R"][edge].set_color(col)
        beat(sc, Create(r), FadeIn(rlab(r, val, dict(ab=LEFT + UP * .3, ac=RIGHT + UP * .3, bc=DOWN)[edge], col)), t=1.0, rt=.6)
    return eqs, D


class Y3(Scene):
    def construct(self):
        eqs, D = y2d_calc(self, [("ab", "c", 6, BLU)], ())
        ok = kr("원래 값 ✓", 40, BLU).next_to(eqs, DOWN, .4)
        beat(self, FadeIn(ok), t=.8, rt=.4)
        fill(self, eqs, BLU)


class Y4(Scene):
    def construct(self):
        eqs, D = y2d_calc(self, [("bc", "a", 12, GRN), ("ac", "b", 18, ORG)], ("ab",))
        ok = kr("원래 Δ 그대로", 40, YEL).move_to(RIGHT * 4.3 + DOWN * 3.1)
        beat(self, FadeIn(ok), t=.8, rt=.4)
        fill(self, D["all"])


class Y5(Scene):
    def construct(self):
        self.add(step_tag(3))
        c1 = card(VGroup(kr("Δ → Y", 34, PUR), kr("이웃 둘의 곱 ÷ 합", 40, INK)).arrange(DOWN, buff=.2), PUR).move_to(LEFT * 3.4 + UP * 1.2)
        c2 = card(VGroup(kr("Y → Δ", 34, GRN), kr("곱의 합 ÷ 맞은편", 40, INK)).arrange(DOWN, buff=.2), GRN).move_to(RIGHT * 3.4 + UP * 1.2)
        beat(self, FadeIn(c1), t=.8, rt=.4)
        beat(self, FadeIn(c2), t=.8, rt=.4)
        ar = VGroup(Arrow(c1.get_right() + UP * .25, c2.get_left() + UP * .25, buff=.15, color=YEL, stroke_width=5), Arrow(c2.get_left() + DOWN * .25, c1.get_right() + DOWN * .25, buff=.15, color=YEL, stroke_width=5))
        t = card(kr("서로 역변환", 44, YEL), YEL).move_to(DOWN * 1.2)
        beat(self, GrowArrow(ar[0]), GrowArrow(ar[1]), FadeIn(t), t=1.0, rt=.5)
        beat(self, FadeIn(kr("한쪽만 외우고, 되돌려서 검산", 34, MUTE).next_to(t, DOWN, .3)), t=.9, rt=.4)
        fill(self, t)


def equal_scene(sc, step=3):
    if step: sc.add(step_tag(step))
    D = delta(LEFT * 4.0 + DOWN * .6, .85, vals=("R", "R", "R"), cols=dict(ab=YEL, ac=YEL, bc=YEL))
    Y = ystar(RIGHT * 4.0 + DOWN * .6, .85, vals=(r"\tfrac{R}{3}", r"\tfrac{R}{3}", r"\tfrac{R}{3}"), cols=dict(a=GRN, b=GRN, c=GRN))
    return D, Y


class Y6(Scene):
    def construct(self):
        D, Y = equal_scene(self)
        beat(self, FadeIn(D["all"]), FadeIn(kr("전부 같으면", 40, YEL).to_edge(UP, buff=.5)), t=.9, rt=.5)
        e = tex(r"\frac{R \cdot R}{R + R + R} = \frac{R}{3}", 54, GRN).move_to(UP * 1.4)
        beat(self, Write(e), t=1.2, rt=.8)
        beat(self, FadeIn(Y["all"]), t=.9, rt=.5)
        c = card(VGroup(kr("Y = Δ ÷ 3", 40, GRN), kr("Δ = Y × 3", 40, YEL)).arrange(DOWN, buff=.15), INK, .2).move_to(DOWN * 2.6)
        beat(self, FadeIn(c), t=.9, rt=.4)
        fill(self, e, GRN)


# ================= STEP 4 예제 풀이 =================
class X1(Scene):
    def construct(self):
        self.add(step_tag(4))
        B = bridge(); B["all"].shift(LEFT * .4); self.add(B["all"])
        tri = VGroup(B["R"]["ab"], B["R"]["ac"], B["R"]["bc"], B["L"]["ab"], B["L"]["ac"], B["L"]["bc"])
        beat(self, tri.animate.set_color(YEL), t=.9, rt=.5)
        Yb = bridge(y=True); Yb["all"].shift(LEFT * .4)
        new = VGroup(Yb["R"]["an"], Yb["R"]["nb"], Yb["R"]["nc"], Yb["L"]["an"], Yb["L"]["nb"], Yb["L"]["nc"]).set_color(GRN)
        beat(self, ReplacementTransform(tri, new), FadeIn(Yb["N"]["n"]), t=1.4, rt=1.0)
        beat(self, FadeIn(kr("Δ → Y (3, 2, 6Ω)", 36, GRN).move_to(RIGHT * 4.5 + UP * 2.0)), t=.9, rt=.4)
        fill(self, new, GRN)


def ybridge(sc, step=4, shift=LEFT * .4):
    sc.add(step_tag(step))
    B = bridge(y=True); B["all"].shift(shift); sc.add(B["all"]); return B


class X2(Scene):
    def construct(self):
        B = ybridge(self)
        beat(self, *[B["R"][k].animate.set_color(BLU) for k in ("nb", "bd")], *[B["L"][k].animate.set_color(BLU) for k in ("nb", "bd")], t=.9, rt=.5)
        e = tex(r"2 + 10 = 12\,\Omega", 54, BLU).move_to(RIGHT * 4.4 + UP * 1.8)
        beat(self, Write(e), FadeIn(kr("왼쪽 갈래", 32, BLU).next_to(e, UP, .2)), t=1.0, rt=.6)
        fill(self, e, BLU)


class X3(Scene):
    def construct(self):
        B = ybridge(self)
        for k in ("nb", "bd"): B["R"][k].set_color(BLU); B["L"][k].set_color(BLU)
        self.add(tex(r"12\,\Omega", 40, BLU).move_to(RIGHT * 4.4 + UP * 2.4))
        beat(self, *[B["R"][k].animate.set_color(ORG) for k in ("nc", "cd")], *[B["L"][k].animate.set_color(ORG) for k in ("nc", "cd")], t=.9, rt=.5)
        e = tex(r"6 + 6 = 12\,\Omega", 54, ORG).move_to(RIGHT * 4.4 + UP * 1.3)
        beat(self, Write(e), t=1.0, rt=.6)
        nn = Circle(.3, color=YEL, stroke_width=5).move_to(PN + LEFT * .4); nd = Circle(.3, color=YEL, stroke_width=5).move_to(PD + LEFT * .4)
        beat(self, Create(nn), Create(nd), FadeIn(kr("같은 두 마디 사이 = 병렬", 36, YEL).move_to(RIGHT * 4.4 + DOWN * .6)), t=1.2, rt=.6)
        fill(self, VGroup(nn, nd))


def simple_series(o, c1=BLU, c2=GRN, l1=r"3\,\Omega", l2=r"6\,\Omega", src=r"18\,\mathrm{V}"):
    """전원 - 3Ω - 6Ω 직렬 (예제 최종 형태)."""
    o = P3(o)
    bat = battery(o + LEFT * 2.2, YEL); r1 = resistor(o + LEFT * 1.4 + UP * 1.2, o + RIGHT * .6 + UP * 1.2, c1); r2 = resistor(o + RIGHT * 1.6 + UP * 1.2, o + RIGHT * 1.6 + DOWN * 1.2, c2)
    w = VGroup(wire(o + LEFT * 2.2 + UP * .2, o + LEFT * 2.2 + UP * 1.2), wire(o + LEFT * 2.2 + UP * 1.2, o + LEFT * 1.4 + UP * 1.2), wire(o + RIGHT * .6 + UP * 1.2, o + RIGHT * 1.6 + UP * 1.2),
               wire(o + RIGHT * 1.6 + DOWN * 1.2, o + LEFT * 2.2 + DOWN * 1.2), wire(o + LEFT * 2.2 + DOWN * 1.2, o + LEFT * 2.2 + DOWN * .2))
    g = VGroup(w, bat, r1, r2, tex(l1, 36, c1).next_to(r1, UP, .2), tex(l2, 36, c2).next_to(r2, RIGHT, .2), tex(src, 34, YEL).next_to(bat, LEFT, .2))
    return g, r1, r2, bat


class X4(Scene):
    def construct(self):
        self.add(step_tag(4))
        e1 = tex(r"12 \parallel 12 = 6\,\Omega", 54, GRN).move_to(LEFT * 3.4 + UP * 2.2)
        beat(self, Write(e1), t=1.0, rt=.6)
        g, r1, r2, bat = simple_series(LEFT * 3.4 + DOWN * 1.0)
        beat(self, FadeIn(g), t=1.0, rt=.6)
        e2 = tex(r"3 + 6", 54, INK).move_to(RIGHT * 3.6 + UP * 1.4)
        beat(self, Write(e2), FadeIn(kr("직렬", 32, MUTE).next_to(e2, UP, .2)), t=.9, rt=.5)
        ans = card(VGroup(kr("합성 저항", 34, INK), tex(r"9\,\Omega", 80, YEL)).arrange(DOWN, buff=.15), YEL).move_to(RIGHT * 3.6 + DOWN * 1.0)
        beat(self, FadeIn(ans, scale=1.15), t=1.0, rt=.5)
        fill(self, ans)


class X5(Scene):
    def construct(self):
        self.add(step_tag(4))
        g, r1, r2, bat = simple_series(LEFT * 3.4 + DOWN * .2); self.add(g)
        q = kr("전류는 몇 A?", 44, ORG).move_to(RIGHT * 3.6 + UP * 1.8)
        beat(self, FadeIn(q), t=1.0, rt=.4)
        ar = Arrow(r1.get_left() + UP * .7, r1.get_right() + UP * .7, buff=0, color=ORG, stroke_width=6)
        beat(self, GrowArrow(ar), FadeIn(tex("I", 36, ORG).next_to(ar, UP, .1)), t=.8, rt=.4)
        e = tex(r"I = \frac{18\,\mathrm{V}}{9\,\Omega} = 2\,\mathrm{A}", 56, ORG).move_to(RIGHT * 3.6 + DOWN * .4)
        beat(self, Write(e), t=1.3, rt=.8)
        fill(self, e, ORG)


class X6(Scene):
    def construct(self):
        B = ybridge(self)
        warn = card(kr("Y 저항은 가짜", 36, RED), RED, .18).move_to(RIGHT * 4.5 + UP * 2.4)
        beat(self, FadeIn(warn), *[B["R"][k].animate.set_color(MUTE) for k in ("an", "nb", "nc")], *[B["L"][k].animate.set_color(MUTE) for k in ("an", "nb", "nc")], t=1.0, rt=.5)
        vb = tex(r"10\,\mathrm{V}", 34, BLU).next_to(B["N"]["b"], DOWN + LEFT * .2, .1); vc = tex(r"6\,\mathrm{V}", 34, ORG).next_to(B["N"]["c"], DOWN + RIGHT * .2, .1)
        beat(self, FadeIn(vb), FadeIn(vc), t=.9, rt=.4)
        rbc = resistor(PB + LEFT * .4, PC + LEFT * .4, YEL); lbc = rlab(rbc, 12, DOWN, YEL)
        beat(self, Create(rbc), FadeIn(lbc), FadeIn(kr("원래 12Ω 전류", 30, YEL).move_to(RIGHT * 4.6 + DOWN * .6)), t=1.0, rt=.6)
        e = tex(r"\frac{10 - 6}{12} = 0.33\,\mathrm{A}", 50, YEL).move_to(RIGHT * 4.6 + DOWN * 1.7)
        beat(self, Write(e), t=1.2, rt=.7)
        fill(self, e)


# ================= STEP 5 평형 브리지 =================
def bal_bridge(sc, step=5, mid=True, midlab=None, shift=LEFT * .4):
    if step: sc.add(step_tag(step))
    B = bridge(vals=(6, 4, midlab, 12, 8), src=r"V", mid=mid); B["all"].shift(shift)
    return B


class B1(Scene):
    def construct(self):
        B = bal_bridge(self)
        show_bridge(self, B, .3)
        q = tex("?", 44, MUTE).next_to(B["R"]["bc"], DOWN, .15); self.play(FadeIn(q), run_time=.2)
        t = card(kr("평형 브리지", 48, YEL), YEL).move_to(RIGHT * 4.5 + UP * 1.8)
        beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        r = tex(r"\frac{6}{12} \;\overset{?}{=}\; \frac{4}{8}", 48, INK).next_to(t, DOWN, .5)
        beat(self, Write(r), t=1.0, rt=.6)
        fill(self, t)


class B2(Scene):
    def construct(self):
        B = bal_bridge(self); self.add(B["all"]); self.add(tex("?", 44, MUTE).next_to(B["R"]["bc"], DOWN, .15))
        l = tex(r"\frac{6}{12} = 0.5", 46, BLU).move_to(RIGHT * 4.5 + UP * 2.2); r = tex(r"\frac{4}{8} = 0.5", 46, ORG).next_to(l, DOWN, .4)
        beat(self, *[B["R"][k].animate.set_color(BLU) for k in ("ab", "bd")], *[B["L"][k].animate.set_color(BLU) for k in ("ab", "bd")], Write(l), t=1.0, rt=.6)
        beat(self, *[B["R"][k].animate.set_color(ORG) for k in ("ac", "cd")], *[B["L"][k].animate.set_color(ORG) for k in ("ac", "cd")], Write(r), t=1.0, rt=.6)
        eq = card(tex(r"V_b = V_c", 52, YEL), YEL).next_to(r, DOWN, .5)
        beat(self, FadeIn(eq, scale=1.1), Circumscribe(VGroup(B["N"]["b"][0]), color=YEL), Circumscribe(VGroup(B["N"]["c"][0]), color=YEL), t=1.1, rt=.6)
        fill(self, eq)


class B3(Scene):
    def construct(self):
        B = bal_bridge(self); self.add(B["all"])
        self.add(tex(r"V_b = V_c", 36, YEL).move_to(RIGHT * 4.5 + UP * 2.3))
        beat(self, B["R"]["bc"].animate.set_color(RED), t=.7, rt=.4)
        z = card(tex(r"I = 0", 56, RED), RED).move_to(RIGHT * 4.5 + UP * .9)
        beat(self, FadeIn(z, scale=1.1), FadeIn(kr("전압 차 0", 30, RED).next_to(z, UP, .15)), t=1.0, rt=.5)
        d = DashedLine(PB + LEFT * .4, PC + LEFT * .4, color=MUTE, stroke_width=4, dash_length=.15)
        beat(self, ReplacementTransform(B["R"]["bc"], d), FadeIn(kr("있으나 없으나 같음", 36, YEL).move_to(RIGHT * 4.5 + DOWN * .9)), t=1.1, rt=.6)
        fill(self, z, RED)


class B4(Scene):
    def construct(self):
        B = bal_bridge(self, mid=False); self.add(B["all"])
        beat(self, *[B["R"][k].animate.set_color(BLU) for k in ("ab", "bd")], *[B["R"][k].animate.set_color(ORG) for k in ("ac", "cd")], t=.8, rt=.5)
        e1 = tex(r"(6 + 12) \parallel (4 + 8)", 46, INK).move_to(RIGHT * 4.4 + UP * 2.0)
        beat(self, Write(e1), t=1.0, rt=.6)
        e2 = tex(r"= 18 \parallel 12", 46, INK).next_to(e1, DOWN, .3)
        beat(self, Write(e2), t=.9, rt=.5)
        ans = card(tex(r"= 7.2\,\Omega", 64, YEL), YEL).next_to(e2, DOWN, .4)
        beat(self, FadeIn(ans, scale=1.1), FadeIn(kr("변환 없이 끝", 32, YEL).next_to(ans, DOWN, .2)), t=1.0, rt=.5)
        fill(self, ans)


class B5(Scene):
    def construct(self):
        self.add(step_tag(5))
        B = bridge(vals=("R_1", "R_2", None, "R_3", "R_x"), src=r"V", mid=False); B["all"].shift(LEFT * .4); self.add(B["all"])
        B["R"]["cd"].set_color(ORG); B["L"]["cd"].set_color(ORG)
        g = VGroup(Circle(.35, color=GRN, stroke_width=5).move_to(LEFT * .4 + UP * .2), tex("G", 34, GRN).move_to(LEFT * .4 + UP * .2))
        w = VGroup(wire(PB + LEFT * .4, g[0].get_left()), wire(g[0].get_right(), PC + LEFT * .4))
        beat(self, FadeIn(kr("휘트스톤 브리지", 44, YEL).move_to(RIGHT * 4.4 + UP * 2.2)), t=.8, rt=.4)
        beat(self, Create(w), FadeIn(g), FadeIn(kr("검류계 = 0 이 되게 조절", 30, GRN).move_to(RIGHT * 4.4 + UP * 1.2)), t=1.1, rt=.6)
        beat(self, FadeIn(kr("모르는 저항", 30, ORG).next_to(B["L"]["cd"], DOWN, .15)), t=.8, rt=.4)
        e = tex(r"R_x = \frac{R_2 R_3}{R_1}", 50, ORG).move_to(RIGHT * 4.4 + DOWN * .5)
        beat(self, Write(e), t=1.0, rt=.6)
        fill(self, e, ORG)


def three_phase(o, load="Y", val=r"10\,\Omega", c=GRN, s=.8):
    """3상 부하만 (세 선 + Δ 또는 Y)."""
    o = P3(o)
    if load == "Y": D = ystar(o, s, vals=(val, val, val), cols=dict(a=c, b=c, c=c), labels=True)
    else: D = delta(o, s, vals=(val, val, val), cols=dict(ab=c, ac=c, bc=c), labels=True)
    return D


class B6(Scene):
    def construct(self):
        self.add(step_tag(5))
        D = three_phase(LEFT * 3.8 + DOWN * .5, "D", r"30\,\Omega", YEL)
        beat(self, FadeIn(D["all"]), FadeIn(kr("3상 Δ 부하", 36, YEL).move_to(LEFT * 3.8 + UP * 2.4)), t=.9, rt=.5)
        ar = Arrow(LEFT * 1.4 + DOWN * .5, RIGHT * 1.4 + DOWN * .5, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(tex(r"\div 3", 44, GRN).next_to(ar, UP, .15)), t=.8, rt=.4)
        Y = three_phase(RIGHT * 3.8 + DOWN * .5, "Y", r"10\,\Omega", GRN)
        beat(self, FadeIn(Y["all"]), FadeIn(kr("Y 부하", 36, GRN).move_to(RIGHT * 3.8 + UP * 2.4)), t=.9, rt=.5)
        beat(self, Y["R"]["a"].animate.set_color(ORG), Y["L"]["a"].animate.set_color(ORG), FadeIn(card(kr("한 상만 풀면 끝", 36, ORG), ORG, .18).to_edge(DOWN, buff=.4)), t=1.0, rt=.5)
        fill(self, Y["R"]["a"], ORG)


# ================= 정리 =================
class E1(Scene):
    def construct(self):
        s = kr("직렬도 병렬도 아니면", 48, INK).move_to(UP * 2.2)
        beat(self, FadeIn(s), t=.8, rt=.4)
        D = delta(LEFT * 3.2 + DOWN * .8, .8, labels=False, cols=dict(ab=YEL, ac=YEL, bc=YEL)); Y = ystar(RIGHT * 3.2 + DOWN * .8, .8, labels=False, cols=dict(a=GRN, b=GRN, c=GRN))
        beat(self, FadeIn(D["all"]), FadeIn(kr("Δ 찾기", 36, YEL).next_to(D["all"], DOWN, .3)), t=.9, rt=.5)
        ar = Arrow(LEFT * 1.0 + DOWN * .8, RIGHT * 1.0 + DOWN * .8, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(Y["all"]), FadeIn(kr("Y 로 바꾸기", 36, GRN).next_to(Y["all"], DOWN, .3)), t=1.0, rt=.6)
        fill(self, Y["all"], GRN)


class E2(Scene):
    def construct(self):
        c1 = card(VGroup(kr("Δ → Y", 34, PUR), kr("이웃 둘의 곱 ÷ 합", 44, INK), tex(DY_EQ, 36, MUTE)).arrange(DOWN, buff=.25), PUR).move_to(UP * 1.5)
        c2 = card(VGroup(kr("Y → Δ", 34, GRN), kr("곱의 합 ÷ 맞은편", 44, INK), tex(YD_EQ, 36, MUTE)).arrange(DOWN, buff=.25), GRN).move_to(DOWN * 1.7)
        beat(self, FadeIn(c1, shift=UP * .2), t=1.3, rt=.5)
        beat(self, FadeIn(c2, shift=UP * .2), t=1.3, rt=.5)
        fill(self, VGroup(c1, c2))


class E3(Scene):
    def construct(self):
        B = bal_bridge(self, step=0); self.add(B["all"]); self.add(tex("?", 44, MUTE).next_to(B["R"]["bc"], DOWN, .15))
        r = tex(r"\frac{6}{12} = \frac{4}{8}", 46, YEL).move_to(RIGHT * 4.4 + UP * 2.0)
        beat(self, Write(r), FadeIn(kr("평형 브리지", 36, YEL).next_to(r, UP, .2)), t=1.0, rt=.6)
        x = cross(B["R"]["bc"])
        beat(self, Create(x), FadeIn(kr("가운데는 지우고 풀기", 36, RED).move_to(RIGHT * 4.4 + DOWN * .4)), t=1.0, rt=.5)
        fill(self, x, RED)


class Site(Scene):
    def construct(self):
        c = card(VGroup(kr("무료 사이트", 32, MUTE), kr("보이는 회로이론", 60, YEL)).arrange(DOWN, buff=.2), YEL, .45).move_to(UP * 1.2)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.5)
        items = VGroup(*[card(kr(t, 30, INK), MUTE, .18) for t in ("직렬·병렬", "마디·망 해석", "테브난", "교류", "3상")]).arrange(RIGHT, buff=.25).move_to(DOWN * 1.4)
        for it in items:
            beat(self, FadeIn(it, shift=UP * .15), t=.55, rt=.3)
        beat(self, FadeIn(kr("값을 바꿔 가며 직접 확인", 34, GRN).next_to(items, DOWN, .35)), t=.9, rt=.4)
        fill(self, c)


class Next(Scene):
    def construct(self):
        a = card(kr("링크는 설명란에", 48, INK), INK, .35).move_to(UP * 1.2)
        beat(self, FadeIn(a, shift=UP * .2), t=1.3, rt=.5)
        b = card(VGroup(kr("재생목록", 32, MUTE), kr("회로이론 한눈에", 48, YEL)).arrange(DOWN, buff=.2), YEL, .35).move_to(DOWN * 1.3)
        beat(self, FadeIn(b, shift=UP * .2), t=1.3, rt=.5)
        fill(self, b)


# ================= 쇼츠·릴스 전용 =================
class AQ(Scene):
    def construct(self):
        B = bridge(); B["all"].shift(LEFT * .4)
        show_bridge(self, B, .28)
        q = card(VGroup(kr("합성 저항은?", 44, YEL)), YEL).move_to(RIGHT * 4.4 + UP * .6)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, q)


class AAns(Scene):
    def construct(self):
        g, r1, r2, bat = simple_series(LEFT * 3.6 + DOWN * .2); self.add(g)
        e = tex(r"6 + 3", 50, INK).move_to(RIGHT * 3.6 + UP * 1.6)
        beat(self, Write(e), t=.8, rt=.5)
        ans = card(tex(r"= 9\,\Omega", 90, YEL), YEL).move_to(RIGHT * 3.6 + DOWN * .4)
        beat(self, FadeIn(ans, scale=1.2), t=1.0, rt=.5)
        beat(self, FadeIn(kr("Y-Δ 변환", 40, GRN).next_to(ans, DOWN, .3)), t=.8, rt=.4)
        fill(self, ans)


class BQ(Scene):
    def construct(self):
        D = delta(LEFT * 4.0 + DOWN * .6, .85, cols=dict(ab=YEL, ac=YEL, bc=YEL)); Y = ystar(RIGHT * 4.0 + DOWN * .6, .85, labels=False, cols=dict(a=GRN, b=GRN, c=GRN))
        beat(self, FadeIn(D["all"]), t=.7, rt=.4)
        ar = Arrow(LEFT * 1.4 + DOWN * .6, RIGHT * 1.4 + DOWN * .6, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(Y["all"]), t=.8, rt=.5)
        e = tex(DY_EQ, 50, INK).move_to(UP * 2.0)
        beat(self, Write(e), t=1.0, rt=.7)
        c = card(kr("한 줄로 외우기", 40, YEL), YEL, .2).to_edge(DOWN, buff=.4)
        beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, e)


class BD45(Scene):
    def construct(self):
        D = delta(LEFT * 4.3 + DOWN * .3, .85, cols=dict(ab=MUTE, ac=MUTE, bc=MUTE)); self.add(D["all"])
        Y = ystar(RIGHT * 4.3 + DOWN * .3, .85, labels=False); self.add(Y["N"]["n"], *[Y["N"][k] for k in "abc"], Y["R"]["a"], rlab(Y["R"]["a"], 3, RIGHT))
        e1 = tex(r"R_b = \frac{6 \times 12}{36} = 2\,\Omega", 48, GRN).move_to(UP * 2.3)
        beat(self, Write(e1), D["R"]["ab"].animate.set_color(GRN), D["R"]["bc"].animate.set_color(GRN), t=1.1, rt=.7)
        beat(self, Create(Y["R"]["b"].set_color(GRN)), FadeIn(rlab(Y["R"]["b"], 2, UP + LEFT * .3, GRN)), t=.8, rt=.5)
        e2 = tex(r"R_c = \frac{18 \times 12}{36} = 6\,\Omega", 48, ORG).next_to(e1, DOWN, .3)
        beat(self, Write(e2), D["R"]["ab"].animate.set_color(MUTE), D["R"]["ac"].animate.set_color(ORG), D["R"]["bc"].animate.set_color(ORG), t=1.1, rt=.7)
        beat(self, Create(Y["R"]["c"].set_color(ORG)), FadeIn(rlab(Y["R"]["c"], 6, UP + RIGHT * .3, ORG)), t=.8, rt=.5)
        fill(self, Y["all"], ORG)


class CQ(Scene):
    def construct(self):
        Y = ystar(LEFT * 4.0 + DOWN * .6, .85, cols=dict(a=GRN, b=GRN, c=GRN)); D = delta(RIGHT * 4.0 + DOWN * .6, .85, labels=False, cols=dict(ab=YEL, ac=YEL, bc=YEL))
        beat(self, FadeIn(Y["all"]), t=.7, rt=.4)
        ar = Arrow(LEFT * 1.4 + DOWN * .6, RIGHT * 1.4 + DOWN * .6, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(D["all"]), t=.8, rt=.5)
        e = tex(YD_EQ, 48, INK).move_to(UP * 2.0)
        beat(self, Write(e), t=1.0, rt=.7)
        c = card(kr("거꾸로", 44, YEL), YEL, .2).to_edge(DOWN, buff=.4)
        beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, e)


class DQ(Scene):
    def construct(self):
        D, Y = equal_scene(self, 0)
        beat(self, FadeIn(D["all"]), FadeIn(kr("저항이 전부 같은 Δ", 40, YEL).to_edge(UP, buff=.5)), t=.9, rt=.5)
        ar = Arrow(LEFT * 1.4 + DOWN * .6, RIGHT * 1.4 + DOWN * .6, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(tex(r"\div 3", 56, GRN).next_to(ar, UP, .15)), t=.8, rt=.4)
        beat(self, FadeIn(Y["all"]), t=.9, rt=.5)
        fill(self, Y["all"], GRN)


class D30(Scene):
    def construct(self):
        D = three_phase(LEFT * 3.8 + DOWN * .5, "D", r"30\,\Omega", YEL); Y = three_phase(RIGHT * 3.8 + DOWN * .5, "Y", r"10\,\Omega", GRN)
        beat(self, FadeIn(D["all"]), t=.8, rt=.5)
        ar = Arrow(LEFT * 1.4 + DOWN * .5, RIGHT * 1.4 + DOWN * .5, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(tex(r"30 \div 3", 44, GRN).next_to(ar, UP, .15)), t=.8, rt=.4)
        beat(self, FadeIn(Y["all"]), t=.8, rt=.5)
        beat(self, FadeIn(card(kr("똑같이 동작", 40, GRN), GRN, .18).to_edge(DOWN, buff=.4)), t=.8, rt=.4)
        fill(self, Y["all"], GRN)


class D3ph(Scene):
    def construct(self):
        Y = three_phase(RIGHT * 3.2 + DOWN * .3, "Y", r"10\,\Omega", GRN, .9)
        srcs = VGroup(*[VGroup(acsrc((-4.6, y), c), tex(l, 30, c).next_to((-4.6, y, 0), LEFT, .7)) for y, c, l in ((1.5, BLU, "V_a"), (0, ORG, "V_b"), (-1.5, PUR, "V_c"))])
        lines = VGroup(wire((-4.0, 1.5), Y["pts"]["a"], BLU), wire((-4.0, 0), Y["pts"]["b"], ORG), wire((-4.0, -1.5), Y["pts"]["c"], PUR))
        beat(self, FadeIn(srcs), FadeIn(kr("3상 회로", 40, INK).to_edge(UP, buff=.5)), t=.8, rt=.4)
        beat(self, Create(lines), FadeIn(Y["all"]), t=1.0, rt=.6)
        rest = VGroup(srcs[1], srcs[2], lines[1], lines[2], Y["R"]["b"], Y["R"]["c"], Y["L"]["b"], Y["L"]["c"])
        beat(self, rest.animate.set_opacity(.25), FadeIn(card(kr("한 상만 풀면 끝", 40, ORG), ORG, .18).to_edge(DOWN, buff=.4)), t=1.0, rt=.6)
        fill(self, VGroup(lines[0], Y["R"]["a"]), ORG)


class DRev(Scene):
    def construct(self):
        Y = ystar(LEFT * 4.0 + DOWN * .6, .85, vals=("R", "R", "R"), cols=dict(a=GRN, b=GRN, c=GRN))
        D = delta(RIGHT * 4.0 + DOWN * .6, .85, vals=("3R", "3R", "3R"), cols=dict(ab=YEL, ac=YEL, bc=YEL))
        beat(self, FadeIn(Y["all"]), FadeIn(kr("반대로 Y → Δ", 40, INK).to_edge(UP, buff=.5)), t=.8, rt=.5)
        ar = Arrow(LEFT * 1.4 + DOWN * .6, RIGHT * 1.4 + DOWN * .6, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(tex(r"\times 3", 56, YEL).next_to(ar, UP, .15)), t=.8, rt=.4)
        beat(self, FadeIn(D["all"]), t=.9, rt=.5)
        fill(self, D["all"])


class EQ(Scene):
    def construct(self):
        B = bal_bridge(self, step=0)
        show_bridge(self, B, .28)
        beat(self, B["R"]["bc"].animate.set_color(RED), t=.6, rt=.4)
        q = card(VGroup(kr("가운데 저항", 36, INK), kr("없는 셈?", 52, RED)).arrange(DOWN, buff=.15), RED).move_to(RIGHT * 4.5 + UP * .6)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, q, RED)


class EBal(Scene):
    def construct(self):
        c = card(VGroup(kr("평형 브리지", 56, YEL), tex(r"\frac{R_1}{R_3} = \frac{R_2}{R_4}", 50, INK)).arrange(DOWN, buff=.3), YEL).move_to(UP * 1.2)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.5)
        t = card(kr("비율부터 확인 → 변환 필요 없음", 40, GRN), GRN, .2).move_to(DOWN * 1.8)
        beat(self, FadeIn(t), t=1.0, rt=.4)
        fill(self, c)
