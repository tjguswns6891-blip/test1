# 능동 필터 1편 롱폼 모션그래픽. 16:9, 핵심은 가운데(세로 쇼츠에서도 씀). 종속 전원 편 형식.
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




# ---------- 장면 길이(dur.json)·배율(speed.json) ----------
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




# ---------- 능동 필터 전용 ----------
def poly(pts, c=INK, w=4):
    return VMobject(color=c, stroke_width=w).set_points_as_corners([P3(p) for p in pts])


def jdot(p, c=INK):
    return Dot(P3(p), radius=.08, color=c)


def ground(p, c=INK):
    p = P3(p)
    return VGroup(*[Line(p + DOWN * .14 * k + LEFT * (.34 - .11 * k), p + DOWN * .14 * k + RIGHT * (.34 - .11 * k), color=c, stroke_width=5) for k in range(3)])


def opamp(c=ORIGIN, s=1.1, col=INK):
    """삼각형 옵앰프 (− 위, + 아래). 반환 dict: g, tri, m, p, o."""
    c = P3(c)
    tri = Polygon(c + (LEFT + UP) * s, c + (LEFT + DOWN) * s, c + RIGHT * s, color=col, stroke_width=5, fill_color="#181b21", fill_opacity=1)
    m, p = c + LEFT * s + UP * .5 * s, c + LEFT * s + DOWN * .5 * s
    sm = tex("-", 50 * s / 1.1, col).move_to(m + RIGHT * .32 * s); sp = tex("+", 50 * s / 1.1, col).move_to(p + RIGHT * .32 * s)
    return dict(g=VGroup(tri, sm, sp), tri=tri, m=m, p=p, o=c + RIGHT * s)


CR1, CR2, CC = BLU, ORG, GRN


def opf(o=(0, 0), mode="lp", r1="R_1", r2="R_2", cl="C", s=1.0, labs=True):
    """반전 증폭기 기반 1차 능동 필터. mode: amp | lp (R2∥C 피드백) | hp (입력에 C 직렬).
    반환 dict: all, amp, tin, r1, c(커패시터 그룹), cw(커패시터 연결선), r2, fb, wn, gnd, outw, lr1, lr2, lc, lin, lout, pts."""
    ox, oy = o
    A = opamp((ox + 1.3 * s, oy - .4 * s), 1.1 * s)
    m, p, out = A["m"], A["p"], A["o"]
    nx, xin, xo, yf = ox - .5 * s, ox - 4.3 * s, out[0] + .7 * s, oy + 1.4 * s
    D = dict(A=A, amp=A["g"])
    D["tin"] = term((xin, m[1]))
    if mode == "hp":
        xc = xin + 1.6 * s
        c = capacitor((xin + .1, m[1]), (xc, m[1]), CC, gap=.24 * s, w=.8 * s)[0]
        D["r1"] = resistor((xc, m[1]), (nx, m[1]), CR1)
        D["c"] = c; D["cw"] = VGroup()
    else:
        D["r1"] = resistor((xin + .1, m[1]), (nx, m[1]), CR1)
    D["wn"] = VGroup(wire((nx, m[1]), m), jdot((nx, m[1])))
    D["gnd"] = VGroup(poly([p, (nx, p[1]), (nx, p[1] - .5 * s)]), ground((nx, p[1] - .5 * s)))
    D["r2"] = resistor((nx, yf), (xo, yf), CR2)
    D["fb"] = VGroup(wire((nx, m[1]), (nx, yf)), poly([(xo, yf), (xo, out[1])]), jdot((xo, out[1])))
    if mode == "lp":
        yc = yf + 1.05 * s
        D["c"] = capacitor((nx + .9 * s, yc), (xo - .9 * s, yc), CC, gap=.24 * s, w=.8 * s)[0]
        D["cw"] = VGroup(poly([(nx, yf), (nx, yc), (nx + .9 * s, yc)]), poly([(xo - .9 * s, yc), (xo, yc), (xo, yf)]), jdot((nx, yf)), jdot((xo, yf)))
    D["outw"] = VGroup(wire(out, (xo + .8 * s, out[1])), term((xo + .8 * s, out[1])))
    sz = 38 * min(1.0, s + .1)
    D["lr1"] = tex(r1, sz, CR1).next_to(D["r1"], DOWN if mode == "hp" else UP, .25)
    D["lr2"] = tex(r2, sz, CR2).next_to(D["r2"], DOWN if mode == "lp" else UP, .22)
    D["lc"] = tex(cl, sz, CC).next_to(D["c"], UP, .2) if mode != "amp" else VGroup()
    D["lin"] = tex(r"v_{in}", sz, INK).next_to(D["tin"], LEFT, .12)
    D["lout"] = tex(r"v_{out}", sz, YEL).next_to(D["outw"][1], RIGHT, .12)
    D["pts"] = dict(nx=nx, xin=xin, xo=xo, yf=yf, m=m, p=p, out=out)
    parts = [D["amp"], D["tin"], D["r1"], D["wn"], D["gnd"], D["r2"], D["fb"], D["outw"]]
    if mode != "amp":
        parts += [D["c"], D["cw"]]
    D["body"] = VGroup(*parts)
    D["labels"] = VGroup(D["lr1"], D["lr2"], D["lc"], D["lin"], D["lout"]) if labs else VGroup()
    D["all"] = VGroup(D["body"], D["labels"])
    return D


def build_opf(sc, D, t=.45):
    beat(sc, FadeIn(D["amp"]), FadeIn(D["gnd"]), FadeIn(D["wn"]), t=t, rt=.35)
    beat(sc, FadeIn(D["tin"]), Create(D["r1"]), FadeIn(D["lin"]), FadeIn(D["lr1"]), t=t, rt=.4)
    beat(sc, Create(D["fb"]), Create(D["r2"]), FadeIn(D["lr2"]), FadeIn(D["outw"]), FadeIn(D["lout"]), t=t, rt=.4)
    if "c" in D and len(D["c"]):
        beat(sc, Create(D["cw"]), FadeIn(D["c"], scale=1.2), FadeIn(D["lc"]), t=t, rt=.4)


# 보드 선도 (가로 = log10(ω), 세로 = dB)
def bode(x0, x1, y0, y1, xl=9.0, yl=4.2, o=DOWN * .3, xt=None, yt=None, ylab="dB", xlab=r"\omega"):
    """xt: [(log10 값, 글자)], yt: [dB 값]."""
    ax = Axes(x_range=[x0, x1, 1], y_range=[y0, y1, 10], x_length=xl, y_length=yl, tips=False,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False}).move_to(o)
    g = VGroup()
    for v in (yt or []):
        g.add(DashedLine(ax.c2p(x0, v), ax.c2p(x1, v), color="#2a2e37", stroke_width=2))
        g.add(tex(f"{v}", 28, MUTE).next_to(ax.c2p(x0, v), LEFT, .12))
    for xv, s in (xt or []):
        g.add(kr(s, 24, MUTE).next_to(ax.c2p(xv, y0), DOWN, .14))
    g.add(kr(ylab, 26, MUTE).next_to(ax.c2p(x0, y1), UP, .1))
    g.add(tex(xlab, 32, MUTE).next_to(ax.c2p(x1, y0), RIGHT, .12))
    return ax, VGroup(g, ax)


def lpdb(w, K=1.0, wc=1.0, n=1): return 20 * np.log10(K / np.sqrt(1 + (w / wc) ** 2) ** n)
def hpdb(w, K=1.0, wc=1.0): r = w / wc; return 20 * np.log10(K * r / np.sqrt(1 + r * r))


def curve(ax, f, x0, x1, c=YEL, sw=6, n=200, ylo=None):
    xs = np.linspace(x0, x1, n); pts = []
    for x in xs:
        y = f(10 ** x)
        if ylo is not None: y = max(y, ylo)
        pts.append(ax.c2p(x, y))
    return VMobject(color=c, stroke_width=sw).set_points_smoothly(pts)


def minicurve(kind="lp", w=1.6, h=.8, c=YEL):
    """블록 안에 넣는 작은 응답 모양."""
    xs = np.linspace(-1.5, 1.5, 60)
    if kind == "lp": ys = [1 / np.sqrt(1 + 10 ** (2 * x)) for x in xs]
    elif kind == "hp": ys = [10 ** x / np.sqrt(1 + 10 ** (2 * x)) for x in xs]
    elif kind == "bp": ys = [(1 / np.sqrt(1 + 10 ** (2 * (x - .9)))) * (10 ** (x + .9) / np.sqrt(1 + 10 ** (2 * (x + .9)))) for x in xs]
    elif kind == "br": ys = [abs(1 / (1 + 1j * 10 ** (x + .9)) + (1j * 10 ** (x - .9)) / (1 + 1j * 10 ** (x - .9))) for x in xs]
    else: ys = [.8 for x in xs]
    ys = np.array(ys) / max(ys)
    pts = [np.array([x / 1.5 * w / 2, (y - .5) * h, 0]) for x, y in zip(xs, ys)]
    return VMobject(color=c, stroke_width=5).set_points_smoothly(pts)


def block(name, kind, c, w=2.3, h=1.7):
    box = RoundedRectangle(width=w, height=h, corner_radius=.15, color=c, stroke_width=4, fill_color="#181b21", fill_opacity=1)
    g = VGroup(box, minicurve(kind, w * .7, h * .34, c).move_to(box.get_center() + UP * h * .14), kr(name, 24, c).move_to(box.get_center() + DOWN * h * .3))
    return g


def chain(blocks, buff=.55, c=MUTE):
    g = VGroup(*blocks).arrange(RIGHT, buff=buff)
    arrows = VGroup(*[Arrow(g[i].get_right(), g[i + 1].get_left(), buff=.06, color=c, stroke_width=4, max_tip_length_to_length_ratio=.3) for i in range(len(g) - 1)])
    return g, arrows


def ok(m, c=GRN):
    return kr("✓", 60, c).next_to(m, RIGHT, .25)


def cross(m, c=RED):
    return Cross(m, stroke_color=c, stroke_width=7, scale_factor=1.05)


def eqcard(label, s, c=YEL, size=52, lsize=26):
    return card(VGroup(kr(label, lsize, MUTE), tex(s, size, c)).arrange(DOWN, buff=.16), c, .22)


def hp_example(o=RIGHT * 0 + DOWN * .3, xl=8.6, yl=4.0):
    """예제 15.2 보드 선도: 고역 통과, K = 10 (20dB), ωc = 500 rad/s. 가로 10~10⁵."""
    ax, g = bode(1, 5, -10, 30, xl, yl, o, xt=[(1, "10"), (2, "100"), (3, "1k"), (4, "10k"), (5, "100k")], yt=[0, 20])
    cv = curve(ax, lambda w: hpdb(w, 10, 500), 1, 5, YEL, ylo=-10)
    return ax, g, cv


# ================= 인트로 =================
class Hook(Scene):
    def construct(self):
        D = opf((-1.6, -.5), "lp", s=.9); build_opf(self, D, .3)
        beat(self, D["c"].animate.set_color(YEL), t=.4, rt=.3)
        L = card(VGroup(coil((0, 0), (2.4, 0), GRN, 4, 7), kr("인덕터", 28, MUTE)).arrange(DOWN, buff=.2), MUTE, .2).move_to(RIGHT * 4.6 + UP * 1.5)
        beat(self, FadeIn(L), t=.5, rt=.4)
        beat(self, Create(cross(L)), FadeIn(kr("없이", 30, RED).next_to(L, DOWN, .15)), t=.5, rt=.3)
        k = card(VGroup(kr("증폭까지", 30, INK), tex(r"K > 1", 52, YEL)).arrange(DOWN, buff=.12), YEL, .22).move_to(RIGHT * 4.6 + DOWN * .9)
        beat(self, FadeIn(k, scale=1.2), t=.6, rt=.4)
        fill(self, D["c"], YEL)


class Goal(Scene):
    def construct(self):
        ax, g, cv = hp_example(LEFT * 2.3 + DOWN * .3, 7.6, 4.0)
        beat(self, FadeIn(g), t=.5, rt=.4)
        beat(self, Create(cv), t=.9, rt=.8)
        a = card(VGroup(tex(r"R_1 = ?", 48, CR1), tex(r"R_2 = ?", 48, CR2)).arrange(DOWN, buff=.3), MUTE, .3).move_to(RIGHT * 4.9 + UP * .3)
        beat(self, FadeIn(a), t=.8, rt=.4)
        b = card(VGroup(tex(r"R_1 = 20\,\mathrm{k\Omega}", 44, CR1), tex(r"R_2 = 200\,\mathrm{k\Omega}", 44, CR2)).arrange(DOWN, buff=.3), YEL, .3).move_to(a)
        beat(self, Transform(a, b), t=.8, rt=.6)
        fill(self, a)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "왜 능동 필터", BLU), ("2", "커패시터 자리", PUR), ("3", "보드 선도", GRN), ("4", "스케일링", ORG), ("5", "대역 필터", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 32, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=.9, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=.8, rt=.7)
        fill(self, cards)


# ================= STEP 1 왜 능동 필터 =================
def passive_rlc(o=ORIGIN, s=1.0):
    o = P3(o); x0, x1, yt, yb = o[0] - 3 * s, o[0] + 3 * s, o[1] + 1.1 * s, o[1] - 1.1 * s
    src = acsrc((x0, o[1]), YEL, .45 * s)
    xs = np.linspace(x0 + .3, x1 - .3, 4)
    R = resistor((xs[0], yt), (xs[1], yt), BLU); L = coil((xs[1], yt), (xs[2], yt), GRN); C = capacitor((xs[2], yt), (xs[3], yt), ORG)[0]
    w = VGroup(wire((x0, o[1] + .45 * s), (x0, yt)), wire((x0, yt), (xs[0], yt)), wire((xs[3], yt), (x1, yt)), resistor((x1, yt), (x1, yb), MUTE),
               wire((x1, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .45 * s)))
    labs = VGroup(kr("R", 30, BLU).next_to(R, UP, .25), kr("L", 30, GRN).next_to(L, UP, .25), kr("C", 30, ORG).next_to(C, UP, .25))
    return dict(g=VGroup(src, w, R, L, C, labs), R=R, L=L, C=C)


class W1(Scene):
    def construct(self):
        self.add(step_tag(1))
        P = passive_rlc(UP * 1.2, .95)
        beat(self, FadeIn(P["g"]), FadeIn(kr("수동 필터", 34, MUTE).move_to(UP * 3.0)), t=.8, rt=.5)
        slots = VGroup(*[card(VGroup(kr(f"약점 {n}", 30, RED), kr("?", 30, MUTE)).arrange(RIGHT, buff=.3), RED, .2) for n in "①②③"]).arrange(RIGHT, buff=.4).move_to(DOWN * 1.9)
        for s in slots:
            beat(self, FadeIn(s, shift=UP * .2), t=.55, rt=.3)
        fill(self, slots, RED)


class W2(Scene):
    def construct(self):
        self.add(step_tag(1))
        L = coil((-5.2, .6), (-1.2, .6), GRN, 5, 9)
        beat(self, Create(L), FadeIn(kr("인덕터", 40, GRN).next_to(L, UP, .4)), t=.9, rt=.6)
        c = card(VGroup(kr("크고 무겁다", 34, INK), kr("낮은 주파수일수록 더 커짐", 26, MUTE)).arrange(DOWN, buff=.12), RED, .22).move_to(LEFT * 3.2 + DOWN * 1.6)
        beat(self, FadeIn(c), t=.8, rt=.4)
        chip = VGroup(RoundedRectangle(width=2.4, height=2.4, corner_radius=.15, color=MUTE, stroke_width=4, fill_color="#181b21", fill_opacity=1),
                      *[Line(LEFT * 1.5 + UP * y, LEFT * 1.2 + UP * y, color=MUTE, stroke_width=4) for y in (-.8, -.3, .2, .7)],
                      *[Line(RIGHT * 1.5 + UP * y, RIGHT * 1.2 + UP * y, color=MUTE, stroke_width=4) for y in (-.8, -.3, .2, .7)],
                      kr("칩(IC)", 30, MUTE)).move_to(RIGHT * 3.6 + UP * .3)
        beat(self, FadeIn(chip), t=.6, rt=.4)
        a = Arrow(L.get_right() + RIGHT * .2, chip.get_left() + LEFT * .1, buff=.1, color=RED, stroke_width=5)
        beat(self, GrowArrow(a), Create(cross(a)), t=.8, rt=.5)
        fill(self, L, RED)


class W3(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax, g = bode(-2, 2, -30, 8, 8.6, 3.6, DOWN * .6, yt=[0], xt=[(0, "컷오프")])
        beat(self, FadeIn(g), t=.5, rt=.4)
        cv = curve(ax, lambda w: lpdb(w), -2, 2, BLU, ylo=-30)
        beat(self, Create(cv), FadeIn(kr("수동 RC", 28, BLU).next_to(ax.c2p(-1.6, 0), UP, .2)), t=.9, rt=.7)
        top = DashedLine(ax.c2p(-2, 0), ax.c2p(2, 0), color=RED, stroke_width=4)
        beat(self, Create(top), FadeIn(card(tex(r"|H| \le 1 \;(0\,\mathrm{dB})", 44, RED), RED, .18).move_to(UP * 2.6)), t=.9, rt=.5)
        w1 = sine(RIGHT * 3.8 + UP * 2.7, .45, 2, 1.6, INK); w2 = sine(RIGHT * 5.8 + UP * 2.7, .2, 2, 1.6, MUTE)
        beat(self, Create(w1), Create(w2), FadeIn(Arrow(RIGHT * 4.6 + UP * 2.7, RIGHT * 5.0 + UP * 2.7, buff=0, color=MUTE)), t=.8, rt=.6)
        fill(self, top, RED)


def rc_passive(o=ORIGIN, load=False, s=1.0):
    o = P3(o); x0, xr, xc, x1, yt, yb = o[0] - 2.8 * s, o[0] - 1.8 * s, o[0] + .2 * s, o[0] + 1.6 * s, o[1] + 1.0 * s, o[1] - 1.0 * s
    R = resistor((xr, yt), (xc, yt), BLU); C = capacitor((xc, yt), (xc, yb), ORG, w=.7)[0]
    g = VGroup(acsrc((x0, o[1]), YEL, .42), wire((x0, o[1] + .42), (x0, yt)), wire((x0, yt), (xr, yt)), R, C, wire((xc, yt), (x1, yt)), wire((xc, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .42)),
               wire((xc, yb), (x1, yb)), term((x1, yt)), term((x1, yb)))
    RL = VGroup(wire((x1 + .1, yt), (x1 + .9, yt), RED), resistor((x1 + .9, yt), (x1 + .9, yb), RED), wire((x1 + .9, yb), (x1 + .1, yb), RED), kr("부하", 26, RED).move_to((x1 + 1.6, o[1], 0)))
    return g, RL


class W4(Scene):
    def construct(self):
        self.add(step_tag(1))
        g, RL = rc_passive(LEFT * 3.6 + UP * .2, s=.9)
        beat(self, FadeIn(g), t=.6, rt=.4)
        ax, bg = bode(-2, 2, -30, 6, 5.6, 3.2, RIGHT * 3.4 + DOWN * .2, yt=[0])
        c0 = curve(ax, lambda w: lpdb(w), -2, 2, BLU, ylo=-30)
        beat(self, FadeIn(bg), Create(c0), t=.8, rt=.6)
        beat(self, FadeIn(RL), t=.6, rt=.4)
        c1 = curve(ax, lambda w: lpdb(w, .5, 2.0), -2, 2, RED, ylo=-30)
        d0 = Dot(ax.c2p(0, -3), color=BLU, radius=.1); d1 = Dot(ax.c2p(np.log10(2), -9), color=RED, radius=.1)
        beat(self, TransformFromCopy(c0, c1), FadeIn(d0), FadeIn(d1), t=.9, rt=.7)
        beat(self, FadeIn(card(kr("컷오프가 바뀐다", 34, RED), RED, .2).move_to(DOWN * 2.8)), t=.7, rt=.4)
        fill(self, c1, RED)


class W5(Scene):
    def construct(self):
        self.add(step_tag(1))
        A = opamp(LEFT * 2.2 + UP * .2, 1.4)
        beat(self, FadeIn(A["g"], scale=1.1), FadeIn(kr("OP amp", 32, INK).next_to(A["g"], DOWN, .3)), t=.8, rt=.5)
        o = A["o"]; ow = wire(o, o + RIGHT * 2.2); tt = term(o + RIGHT * 2.3)
        beat(self, Create(ow), FadeIn(tt), FadeIn(card(tex(r"R_o = 0", 48, YEL), YEL, .2).next_to(ow, UP, .45)), t=.9, rt=.5)
        RL = VGroup(wire(o + RIGHT * 2.4, o + RIGHT * 3.4, RED), resistor(o + RIGHT * 3.4, o + RIGHT * 3.4 + DOWN * 2.0, RED), ground(o + RIGHT * 3.4 + DOWN * 2.0, RED))
        beat(self, FadeIn(RL), FadeIn(kr("부하", 28, RED).next_to(RL[1], RIGHT, .2)), t=.7, rt=.4)
        c = card(kr("출력 그대로 ✓", 40, GRN), GRN, .22).move_to(DOWN * 2.6 + LEFT * 1.0)
        beat(self, FadeIn(c, scale=1.2), t=.7, rt=.4)
        fill(self, c, GRN)


def zbox(lab, c, w=1.5, h=.75):
    b = RoundedRectangle(width=w, height=h, corner_radius=.12, color=c, stroke_width=5, fill_color="#181b21", fill_opacity=1)
    return VGroup(b, tex(lab, 40, c).move_to(b))


class W6(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = opf((-1.2, .2), "amp", labs=False, s=.9)
        zi = zbox("Z_i", CR1).move_to(D["r1"]); zf = zbox("Z_f", CR2).move_to(D["r2"])
        beat(self, FadeIn(VGroup(D["amp"], D["tin"], D["wn"], D["gnd"], D["fb"], D["outw"])), t=.5, rt=.4)
        beat(self, FadeIn(zi, scale=1.2), t=.5, rt=.3)
        beat(self, FadeIn(zf, scale=1.2), t=.5, rt=.3)
        e = card(tex(r"H = -\frac{Z_f}{Z_i}", 76, YEL), YEL, .3).move_to(RIGHT * 4.6 + DOWN * 1.5)
        beat(self, Write(e), t=1.0, rt=.7)
        fill(self, e)


# ================= STEP 2 커패시터 자리 =================
class C1(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        D = opf((-.6, -.6), "lp", s=.95)
        beat(self, FadeIn(VGroup(D["amp"], D["tin"], D["r1"], D["wn"], D["gnd"], D["r2"], D["fb"], D["outw"], D["lr1"], D["lr2"], D["lin"], D["lout"])), t=.7, rt=.5)
        beat(self, Indicate(D["r2"], color=CR2), FadeIn(kr("피드백 저항", 26, CR2).next_to(D["lr2"], DOWN, .1)), t=.8, rt=.5)
        beat(self, Create(D["cw"]), FadeIn(D["c"], scale=1.3), FadeIn(D["lc"]), t=.9, rt=.6)
        beat(self, FadeIn(card(kr("나란히", 34, CC), CC, .18).next_to(D["c"], RIGHT, 1.4)), t=.6, rt=.4)
        fill(self, D["c"], CC)


class C2(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        D = opf((-1.6, -.6), "lp", s=.9); self.add(D["all"])
        h = card(kr("낮은 주파수", 32, BLU), BLU, .18).move_to(RIGHT * 4.6 + UP * 2.6); beat(self, FadeIn(h), t=.5, rt=.3)
        beat(self, Create(cross(D["c"])), FadeIn(kr("끊긴 선", 28, RED).next_to(D["c"], RIGHT, .9)), t=.8, rt=.4)
        beat(self, D["c"].animate.set_opacity(.25), D["cw"].animate.set_opacity(.25), t=.5, rt=.4)
        e = eqcard("반전 증폭기", r"-\frac{R_2}{R_1}", YEL, 64).move_to(RIGHT * 4.6 + DOWN * .6)
        beat(self, FadeIn(e, shift=UP * .2), t=.8, rt=.4)
        fill(self, e)


class C3(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        D = opf((-1.6, -.6), "lp", s=.9); self.add(D["all"])
        h = card(kr("높은 주파수", 32, RED), RED, .18).move_to(RIGHT * 4.6 + UP * 2.6); beat(self, FadeIn(h), t=.5, rt=.3)
        yc = D["pts"]["yf"] + 1.05 * .9; nx, xo = D["pts"]["nx"], D["pts"]["xo"]
        sh = wire((nx + .9 * .9, yc), (xo - .9 * .9, yc), GRN, 8)
        beat(self, FadeOut(D["c"]), FadeOut(D["lc"]), Create(sh), FadeIn(kr("이어진 선", 28, GRN).next_to(sh, UP, .15)), t=.8, rt=.5)
        z = card(tex(r"v_{out} = 0", 44, RED), RED, .18).next_to(D["lout"], DOWN, .5).shift(LEFT * .3)
        beat(self, FadeIn(z), t=.6, rt=.3)
        ax, g = bode(-2, 2, -30, 6, 3.6, 2.0, RIGHT * 4.6 + DOWN * .9, yt=[])
        beat(self, FadeIn(g), Create(curve(ax, lambda w: lpdb(w), -2, 2, YEL, ylo=-30)), t=.8, rt=.6)
        t = card(kr("저역 통과", 38, YEL), YEL, .2).move_to(RIGHT * 4.6 + DOWN * 2.8); beat(self, FadeIn(t, scale=1.2), t=.6, rt=.3)
        fill(self, t)


class C4(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        D = opf((-1.6, -.4), "hp", s=.9)
        beat(self, FadeIn(VGroup(D["amp"], D["tin"], D["wn"], D["gnd"], D["r2"], D["fb"], D["outw"], D["lr2"], D["lin"], D["lout"], D["r1"], D["lr1"])), t=.6, rt=.4)
        beat(self, FadeIn(D["c"], scale=1.3), FadeIn(D["lc"]), FadeIn(kr("직렬", 30, CC).next_to(D["lc"], UP, .15)), t=.9, rt=.5)
        beat(self, Create(cross(D["c"])), FadeIn(kr("낮은 주파수 → 끊김", 26, RED).move_to(LEFT * 3.6 + DOWN * 2.3)), t=.8, rt=.4)
        ax, g = bode(-2, 2, -30, 6, 3.6, 2.0, RIGHT * 4.6 + UP * 1.0, yt=[])
        beat(self, FadeIn(g), Create(curve(ax, lambda w: hpdb(w), -2, 2, YEL, ylo=-30)), t=.8, rt=.6)
        t = card(kr("고역 통과", 38, YEL), YEL, .2).move_to(RIGHT * 4.6 + DOWN * 1.0); beat(self, FadeIn(t, scale=1.2), t=.6, rt=.3)
        fill(self, t)


class C5(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        L = opf((-4.0, .2), "lp", s=.62, labs=True); H = opf((3.0, .2), "hp", s=.62, labs=True)
        beat(self, FadeIn(L["all"]), FadeIn(kr("저역 통과", 28, YEL).move_to(LEFT * 3.4 + UP * 2.9)), t=.6, rt=.4)
        beat(self, FadeIn(H["all"]), FadeIn(kr("고역 통과", 28, YEL).move_to(RIGHT * 3.4 + UP * 2.9)), t=.6, rt=.4)
        k = card(VGroup(kr("이득 둘 다", 28, MUTE), tex(r"K = \frac{R_2}{R_1}", 52, YEL)).arrange(RIGHT, buff=.3), YEL, .2).move_to(DOWN * 2.0)
        beat(self, FadeIn(k, shift=UP * .2), t=.8, rt=.4)
        l1 = SurroundingRectangle(VGroup(L["r2"], L["c"]), color=CC, buff=.12, corner_radius=.1)
        l2 = SurroundingRectangle(VGroup(H["r1"], H["c"]), color=CC, buff=.12, corner_radius=.1)
        beat(self, Create(l1), Create(l2), t=.6, rt=.4)
        c = card(kr("컷오프 = C와 붙은 저항", 34, CC), CC, .2).move_to(DOWN * 3.2)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, c, CC)


class C6(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        L = opf((-4.0, .5), "lp", s=.62); H = opf((3.0, .5), "hp", s=.62)
        self.add(L["all"], H["all"])
        a = eqcard("저역 통과", r"\omega_c = \frac{1}{R_2 C}", CR2, 56).move_to(LEFT * 3.4 + DOWN * 2.2)
        beat(self, FadeIn(a, shift=UP * .2), Indicate(L["r2"], color=CR2), t=1.0, rt=.5)
        b = eqcard("고역 통과", r"\omega_c = \frac{1}{R_1 C}", CR1, 56).move_to(RIGHT * 3.4 + DOWN * 2.2)
        beat(self, FadeIn(b, shift=UP * .2), Indicate(H["r1"], color=CR1), t=1.0, rt=.5)
        w = card(kr("시험 단골!", 30, RED), RED, .15).move_to(UP * 3.2)
        beat(self, FadeIn(w, scale=1.2), t=.6, rt=.3)
        fill(self, VGroup(a, b))


# ================= STEP 3 보드 선도로 설계 (예제 15.2) =================
class B1(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g, cv = hp_example(LEFT * 1.6 + DOWN * .3, 8.6, 4.2)
        beat(self, FadeIn(g), t=.6, rt=.4)
        beat(self, Create(cv), t=1.0, rt=.9)
        t = card(kr("고역 통과 설계", 32, YEL), YEL, .2).move_to(RIGHT * 4.9 + UP * 2.6); beat(self, FadeIn(t), t=.6, rt=.3)
        c = eqcard("커패시터", r"C = 0.1\,\mu\mathrm{F}", CC, 44).move_to(RIGHT * 4.9 + UP * .9); beat(self, FadeIn(c, shift=UP * .2), t=.7, rt=.4)
        fill(self, cv)


class B2(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g, cv = hp_example(LEFT * 1.6 + DOWN * .3, 8.6, 4.2); self.add(g, cv)
        hi = Line(ax.c2p(3.6, 20), ax.c2p(5, 20), color=GRN, stroke_width=12)
        beat(self, Create(hi), FadeIn(kr("평평한 높이 20dB", 28, GRN).next_to(hi, UP, .15)), t=.9, rt=.5)
        a = card(VGroup(tex(r"20\,\mathrm{dB}", 44, INK), kr("= 10배", 36, INK)).arrange(RIGHT, buff=.2), MUTE, .2).move_to(RIGHT * 4.9 + UP * 1.4)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        k = card(tex(r"K = 10", 64, YEL), YEL, .25).move_to(RIGHT * 4.9 + DOWN * .5)
        beat(self, FadeIn(k, scale=1.2), t=.7, rt=.4)
        fill(self, k)


class B3(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        ax, g, cv = hp_example(LEFT * 1.6 + DOWN * .3, 8.6, 4.2); self.add(g, cv)
        d17 = DashedLine(ax.c2p(1, 17), ax.c2p(5, 17), color=ORG, stroke_width=4)
        beat(self, Create(d17), FadeIn(tex(r"17\,\mathrm{dB}", 32, ORG).next_to(ax.c2p(1, 17), LEFT, .1).shift(UP * .25)), t=.8, rt=.5)
        x = np.log10(500); dot = Dot(ax.c2p(x, 17), color=YEL, radius=.13)
        vl = DashedLine(ax.c2p(x, 17), ax.c2p(x, -10), color=YEL, stroke_width=4)
        beat(self, FadeIn(dot, scale=1.5), Create(vl), t=.7, rt=.5)
        a = card(VGroup(kr("3dB 아래", 28, MUTE), tex(r"\omega_c = 500\ \mathrm{rad/s}", 46, YEL)).arrange(DOWN, buff=.15), YEL, .22).move_to(RIGHT * 4.9 + UP * 1.0)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        fill(self, dot)


class B4(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        D = opf((-2.9, .6), "hp", r1=r"R_1", r2=r"R_2", cl=r"0.1\,\mu\mathrm{F}", s=.78); self.add(D["all"])
        e1 = tex(r"R_1 = \frac{1}{\omega_c C} = \frac{1}{500 \times 0.1\,\mu}", 48, CR1).move_to(RIGHT * 3.2 + UP * 1.9)
        beat(self, Write(e1), t=1.0, rt=.7)
        r1 = card(tex(r"R_1 = 20\,\mathrm{k\Omega}", 52, CR1), CR1, .2).move_to(RIGHT * 3.2 + UP * .3)
        beat(self, FadeIn(r1, shift=UP * .2), Transform(D["lr1"], tex(r"20\,\mathrm{k\Omega}", 30, CR1).move_to(D["lr1"])), t=.9, rt=.5)
        e2 = tex(r"R_2 = K R_1 = 10 \times 20\,\mathrm{k}", 46, CR2).move_to(RIGHT * 3.2 + DOWN * 1.2)
        beat(self, Write(e2), t=.9, rt=.6)
        r2 = card(tex(r"R_2 = 200\,\mathrm{k\Omega}", 52, CR2), CR2, .2).move_to(RIGHT * 3.2 + DOWN * 2.6)
        beat(self, FadeIn(r2, shift=UP * .2), Transform(D["lr2"], tex(r"200\,\mathrm{k\Omega}", 30, CR2).move_to(D["lr2"])), t=.9, rt=.5)
        fill(self, VGroup(r1, r2))


class B5(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        D = opf((-3.4, 1.0), "hp", r1=r"20\,\mathrm{k\Omega}", r2=r"200\,\mathrm{k\Omega}", cl=r"0.1\,\mu\mathrm{F}", s=.7); self.add(D["all"])
        o = D["outw"][1].get_center()
        RL = VGroup(wire(o + RIGHT * .1, o + RIGHT * 1.0, RED), resistor(o + RIGHT * 1.0, o + RIGHT * 1.0 + DOWN * 1.6, RED), ground(o + RIGHT * 1.0 + DOWN * 1.6, RED))
        beat(self, FadeIn(RL), FadeIn(tex(r"10\,\mathrm{k\Omega}", 32, RED).next_to(RL[1], RIGHT, .15)), t=.9, rt=.5)
        ax, g, cv = hp_example(RIGHT * 3.2 + DOWN * 1.3, 6.0, 2.8)
        beat(self, FadeIn(g), Create(cv), t=.9, rt=.7)
        cv2 = cv.copy().set_color(RED).set_stroke(width=3)
        beat(self, Create(cv2), t=.6, rt=.5)
        c = card(kr("그대로 ✓", 44, GRN), GRN, .22).move_to(LEFT * 3.4 + DOWN * 2.4)
        beat(self, FadeIn(c, scale=1.2), t=.6, rt=.3)
        n = card(kr("수동 필터라면 바뀜", 26, MUTE), MUTE, .15).move_to(RIGHT * 3.2 + UP * 2.9)
        beat(self, FadeIn(n), t=.6, rt=.3)
        fill(self, c, GRN)


# ================= STEP 4 스케일링 =================
class K1(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        p = card(VGroup(kr("설계용", 26, MUTE), tex(r"1\,\Omega", 48, INK), tex(r"1\,\mathrm{F}", 48, INK), tex(r"1\ \mathrm{rad/s}", 44, INK)).arrange(DOWN, buff=.2), MUTE, .3).move_to(LEFT * 4.4)
        beat(self, FadeIn(p, shift=UP * .2), t=.9, rt=.4)
        a1 = card(tex(r"\times k_f", 52, ORG), ORG, .2).move_to(LEFT * 1.0 + UP * .9); a2 = card(tex(r"\times k_m", 52, PUR), PUR, .2).move_to(LEFT * 1.0 + DOWN * .9)
        beat(self, FadeIn(a1, shift=RIGHT * .3), t=.6, rt=.3)
        beat(self, FadeIn(a2, shift=RIGHT * .3), t=.6, rt=.3)
        r = card(VGroup(kr("실제 부품", 26, MUTE), tex(r"15.9\,\mathrm{k\Omega}", 44, YEL), tex(r"0.01\,\mu\mathrm{F}", 44, YEL), tex(r"1\,\mathrm{kHz}", 44, YEL)).arrange(DOWN, buff=.2), YEL, .3).move_to(RIGHT * 3.8)
        ar = Arrow(LEFT * .0, RIGHT * 2.0, buff=0, color=YEL, stroke_width=6)
        beat(self, GrowArrow(ar), FadeIn(r, shift=RIGHT * .3), t=.9, rt=.5)
        fill(self, r)


class K2(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = bode(-1, 5, -30, 6, 10.4, 3.4, DOWN * 1.3, yt=[0], xt=[(0, "1"), (np.log10(6283), "6283")], xlab=r"\omega")
        beat(self, FadeIn(g), t=.5, rt=.4)
        c0 = curve(ax, lambda w: lpdb(w), -1, 3, MUTE, ylo=-30)
        beat(self, Create(c0), t=.6, rt=.5)
        c1 = curve(ax, lambda w: lpdb(w, 1, 6283), 2.8, 5, YEL, ylo=-30)
        e = tex(r"k_f = \frac{2\pi \times 1000}{1} = 6283", 56, ORG).move_to(UP * 2.2)
        beat(self, Write(e), t=1.0, rt=.7)
        beat(self, TransformFromCopy(c0, c1), t=1.0, rt=.9)
        fill(self, e, ORG)


class K3(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        a = tex(r"C' = \frac{C}{k_m k_f}", 64, INK).move_to(UP * 2.0)
        beat(self, Write(a), t=.9, rt=.6)
        b = card(VGroup(kr("쓰고 싶은 C", 26, MUTE), tex(r"0.01\,\mu\mathrm{F}", 48, CC)).arrange(DOWN, buff=.15), CC, .2).move_to(LEFT * 4.0 + DOWN * .5)
        beat(self, FadeIn(b, shift=UP * .2), t=.7, rt=.4)
        e = tex(r"k_m = \frac{1}{6283 \times 10^{-8}}", 52, PUR).move_to(RIGHT * 1.6 + DOWN * .4)
        beat(self, Write(e), t=.9, rt=.6)
        r = card(tex(r"k_m \approx 15900", 60, PUR), PUR, .25).move_to(RIGHT * 1.6 + DOWN * 2.3)
        beat(self, FadeIn(r, scale=1.2), t=.7, rt=.4)
        fill(self, r, PUR)


class K4(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        a = card(VGroup(kr("저항", 28, MUTE), tex(r"R' = k_m R", 56, CR2)).arrange(DOWN, buff=.15), CR2, .25).move_to(LEFT * 3.6 + UP * 1.6)
        b = card(VGroup(kr("커패시터", 28, MUTE), tex(r"C' = \frac{C}{k_m k_f}", 56, CC)).arrange(DOWN, buff=.15), CC, .25).move_to(RIGHT * 3.6 + UP * 1.6)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        beat(self, FadeIn(b, shift=UP * .2), t=.8, rt=.4)
        x = tex(r"1\,\Omega", 64, MUTE).move_to(LEFT * 2.4 + DOWN * 1.5); y = tex(r"15.9\,\mathrm{k\Omega}", 72, YEL).move_to(RIGHT * 2.0 + DOWN * 1.5)
        ar = Arrow(x.get_right(), y.get_left(), buff=.3, color=YEL, stroke_width=6)
        beat(self, FadeIn(x), t=.4, rt=.3)
        beat(self, GrowArrow(ar), FadeIn(y, shift=RIGHT * .3), t=.9, rt=.5)
        fill(self, y)


class K5(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        e = card(VGroup(kr("이득은 저항 비", 28, MUTE), tex(r"K = \frac{k_m R_2}{k_m R_1} = \frac{R_2}{R_1}", 52, INK)).arrange(DOWN, buff=.15), MUTE, .25).move_to(UP * 2.0)
        beat(self, FadeIn(e, shift=UP * .2), t=1.0, rt=.5)
        a = tex(r"K' = 5 \;\Rightarrow\; R_1' = \frac{15.9\,\mathrm{k}}{5}", 52, ORG).move_to(DOWN * .3)
        beat(self, Write(a), t=1.0, rt=.6)
        r = card(tex(r"R_1' = 3.18\,\mathrm{k\Omega}", 60, YEL), YEL, .25).move_to(DOWN * 2.2)
        beat(self, FadeIn(r, scale=1.2), t=.7, rt=.4)
        fill(self, r)


class K6(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        w = card(kr("주의!", 40, RED), RED, .2).move_to(UP * 2.4); beat(self, FadeIn(w, scale=1.2), t=.6, rt=.3)
        a = card(VGroup(tex(r"k_f", 56, ORG), kr("에는 rad/s", 40, INK)).arrange(RIGHT, buff=.25), ORG, .25).move_to(UP * .5)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        b = tex(r"1000\,\mathrm{Hz} \times 2\pi = 6283\ \mathrm{rad/s}", 52, YEL).move_to(DOWN * 1.5)
        beat(self, Write(b), t=1.0, rt=.7)
        fill(self, b)


# ================= STEP 5 대역 통과·저지 =================
class F1(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        g, ar = chain([block("필터 1", "lp", BLU), block("필터 2", "hp", PUR), block("필터 3", "flat", ORG)])
        g.move_to(UP * .9); ar.shift(g.get_center() - g.get_center())
        for i, b in enumerate(g):
            beat(self, FadeIn(b, shift=UP * .2), *( [GrowArrow(ar[i - 1])] if i else []), t=.6, rt=.4)
        r = card(tex(r"R_o = 0", 44, GRN), GRN, .18).move_to(UP * 2.9); beat(self, FadeIn(r), t=.5, rt=.3)
        e = card(tex(r"H = H_1 \times H_2 \times H_3", 60, YEL), YEL, .25).move_to(DOWN * 1.8)
        beat(self, Write(e), t=.9, rt=.6)
        fill(self, e)


def band_axes(o=DOWN * 1.2, xl=10.0, yl=3.0):
    return bode(0, 6, -40, 12, xl, yl, o, yt=[0], xt=[(2, "100Hz"), (4, "10kHz")], xlab="f")


class F2(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        g, ar = chain([block("저역 통과", "lp", BLU, 2.3, 1.5), block("고역 통과", "hp", PUR, 2.3, 1.5), block("이득 K", "flat", ORG, 2.3, 1.5)], .45)
        g.move_to(UP * 2.2)
        beat(self, FadeIn(g[0]), t=.4, rt=.3); beat(self, GrowArrow(ar[0]), FadeIn(g[1]), t=.4, rt=.3); beat(self, GrowArrow(ar[1]), FadeIn(g[2]), t=.5, rt=.3)
        ax, bg = band_axes()
        beat(self, FadeIn(bg), t=.4, rt=.3)
        lpC = curve(ax, lambda f: lpdb(f, 1, 1e4), 0, 6, BLU, 4, ylo=-40); hpC = curve(ax, lambda f: hpdb(f, 1, 100), 0, 6, PUR, 4, ylo=-40)
        beat(self, Create(lpC), Create(hpC), t=.8, rt=.6)
        bp = curve(ax, lambda f: 20 * np.log10(2 * (1 / np.sqrt(1 + (f / 1e4) ** 2)) * ((f / 100) / np.sqrt(1 + (f / 100) ** 2))), 0, 6, YEL, 7, ylo=-40)
        beat(self, Create(bp), FadeIn(card(kr("곱 = 대역 통과", 32, YEL), YEL, .15).move_to(RIGHT * 4.6 + DOWN * .1)), t=.9, rt=.7)
        fill(self, bp)


class F3(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        s = card(VGroup(kr("목표", 26, MUTE), kr("100Hz ~ 10kHz · 이득 2", 34, INK), tex(r"C = 0.2\,\mu\mathrm{F}", 40, CC)).arrange(DOWN, buff=.15), MUTE, .25).move_to(UP * 2.3)
        beat(self, FadeIn(s, shift=UP * .2), t=.9, rt=.4)
        a = eqcard("위쪽 끝 (저역 통과)", r"R = \frac{1}{2\pi \cdot 10^4 \cdot 0.2\,\mu} \approx 80\,\Omega", BLU, 42).move_to(LEFT * 3.4 + DOWN * .5)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.4)
        b = eqcard("아래쪽 끝 (고역 통과)", r"R = \frac{1}{2\pi \cdot 100 \cdot 0.2\,\mu} \approx 8\,\mathrm{k\Omega}", PUR, 42).move_to(RIGHT * 3.4 + DOWN * .5)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.4)
        c = card(tex(r"R_f : R_i = 2 : 1", 44, ORG), ORG, .2).move_to(DOWN * 2.6); beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, VGroup(a, b))


class F4(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        ax, bg = band_axes(DOWN * .5, 10.4, 3.8); self.add(bg)
        bp = curve(ax, lambda f: 20 * np.log10(2 * (1 / np.sqrt(1 + (f / 1e4) ** 2)) * ((f / 100) / np.sqrt(1 + (f / 100) ** 2))), 0, 6, YEL, 7, ylo=-40)
        beat(self, Create(bp), t=.8, rt=.7)
        r = Arrow(ax.c2p(5.3, 8), ax.c2p(4.1, 4), buff=0, color=BLU, stroke_width=5)
        beat(self, GrowArrow(r), FadeIn(card(VGroup(kr("위쪽 끝", 26, MUTE), kr("저역 통과", 34, BLU)).arrange(DOWN, buff=.1), BLU, .15).next_to(ax.c2p(5.3, 8), UP, .1)), t=1.0, rt=.5)
        l = Arrow(ax.c2p(.7, 8), ax.c2p(1.9, 4), buff=0, color=PUR, stroke_width=5)
        beat(self, GrowArrow(l), FadeIn(card(VGroup(kr("아래쪽 끝", 26, MUTE), kr("고역 통과", 34, PUR)).arrange(DOWN, buff=.1), PUR, .15).next_to(ax.c2p(.7, 8), UP, .1)), t=1.0, rt=.5)
        fill(self, bp)


class F5(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        lp = block("저역 통과", "lp", BLU, 2.2, 1.3).move_to(LEFT * 2.0 + UP * 2.5); hp = block("고역 통과", "hp", PUR, 2.2, 1.3).move_to(LEFT * 2.0 + UP * .7)
        sm = VGroup(Circle(.5, color=ORG, stroke_width=5, fill_color="#181b21", fill_opacity=1), tex(r"\Sigma", 48, ORG)).move_to(RIGHT * 1.6 + UP * 1.6)
        inp = Dot(LEFT * 5.0 + UP * 1.6, color=INK)
        w = VGroup(poly([inp.get_center(), LEFT * 4.0 + UP * 1.6]), poly([LEFT * 4.0 + UP * 2.5, LEFT * 4.0 + UP * .7]),
                   Arrow(LEFT * 4.0 + UP * 2.5, lp.get_left(), buff=0, color=INK, stroke_width=4), Arrow(LEFT * 4.0 + UP * .7, hp.get_left(), buff=0, color=INK, stroke_width=4))
        beat(self, FadeIn(inp), Create(w), FadeIn(lp), FadeIn(hp), t=.8, rt=.5)
        a1 = Arrow(lp.get_right(), sm.get_left() + UP * .2, buff=.05, color=INK, stroke_width=4); a2 = Arrow(hp.get_right(), sm.get_left() + DOWN * .2, buff=.05, color=INK, stroke_width=4)
        beat(self, GrowArrow(a1), GrowArrow(a2), FadeIn(sm, scale=1.2), t=.7, rt=.4)
        ax, bg = bode(0, 4, -20, 12, 6.4, 2.4, DOWN * 2.0 + RIGHT * 1.0, yt=[0], xlab=r"\omega")
        br = curve(ax, lambda w: 20 * np.log10(abs(3 * (1 / (1 + 1j * w / 100) + (1j * w / 2000) / (1 + 1j * w / 2000)))), 0, 4, YEL, 7, ylo=-20)
        beat(self, FadeIn(bg), Create(br), t=.9, rt=.7)
        beat(self, FadeIn(card(kr("합 = 대역 저지", 32, YEL), YEL, .15).move_to(RIGHT * 5.0 + UP * 1.6)), t=.6, rt=.3)
        fill(self, br)


class F6(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        ax, bg = bode(0, 4, -20, 14, 7.0, 3.6, LEFT * 2.6 + DOWN * .6, yt=[0], xlab=r"\omega")
        br = curve(ax, lambda w: 20 * np.log10(abs(3 * (1 / (1 + 1j * w / 100) + (1j * w / 2000) / (1 + 1j * w / 2000)))), 0, 4, YEL, 7, ylo=-20)
        self.add(bg, br)
        x0 = np.log10(np.sqrt(100 * 2000)); d = Dot(ax.c2p(x0, -10.9), color=RED, radius=.12)
        beat(self, FadeIn(d, scale=1.5), FadeIn(tex(r"-10.9\,\mathrm{dB}", 34, RED).next_to(d, DOWN, .15)), t=.8, rt=.4)
        a = card(kr("0까지 안 파인다", 32, RED), RED, .18).move_to(RIGHT * 4.4 + UP * 1.9); beat(self, FadeIn(a), t=.7, rt=.3)
        q = card(tex(r"Q \le 0.5", 56, RED), RED, .22).move_to(RIGHT * 4.4 + UP * .2); beat(self, FadeIn(q, scale=1.2), t=.7, rt=.4)
        n = card(VGroup(kr("좁은 필터는", 26, MUTE), kr("다음 편 →", 34, YEL)).arrange(DOWN, buff=.1), YEL, .2).move_to(RIGHT * 4.4 + DOWN * 1.8)
        beat(self, FadeIn(n, shift=RIGHT * .2), t=.7, rt=.4)
        fill(self, q, RED)


# ================= 정리 =================
class E1(Scene):
    def construct(self):
        e = card(tex(r"H = -\frac{Z_f}{Z_i}", 80, YEL), YEL, .3).move_to(UP * 1.8); beat(self, FadeIn(e, shift=UP * .2), t=.9, rt=.5)
        L = opf((-4.0, -1.6), "lp", s=.5, labs=False); H = opf((3.0, -1.6), "hp", s=.5, labs=False)
        beat(self, FadeIn(L["all"]), FadeIn(kr("저역 통과", 28, YEL).next_to(L["all"], DOWN, .2)), t=.7, rt=.4)
        beat(self, FadeIn(H["all"]), FadeIn(kr("고역 통과", 28, YEL).next_to(H["all"], DOWN, .2)), t=.7, rt=.4)
        fill(self, e)


class E2(Scene):
    def construct(self):
        c1 = card(VGroup(kr("컷오프", 30, MUTE), kr("C와 붙은 저항", 44, CC)).arrange(DOWN, buff=.15), CC, .3).move_to(LEFT * 3.4)
        beat(self, FadeIn(c1, shift=UP * .2), t=1.0, rt=.5)
        c2 = card(VGroup(kr("이득", 30, MUTE), tex(r"K = \frac{R_2}{R_1}", 60, YEL)).arrange(DOWN, buff=.15), YEL, .3).move_to(RIGHT * 3.4)
        beat(self, FadeIn(c2, shift=UP * .2), t=1.0, rt=.5)
        fill(self, VGroup(c1, c2))


class E3(Scene):
    def construct(self):
        p = card(VGroup(tex(r"1\,\Omega", 48, INK), tex(r"1\,\mathrm{F}", 48, INK)).arrange(DOWN, buff=.2), MUTE, .3).move_to(LEFT * 4.2)
        beat(self, FadeIn(p), t=.7, rt=.4)
        a = card(VGroup(tex(r"\times k_f", 48, ORG), tex(r"\times k_m", 48, PUR)).arrange(DOWN, buff=.2), ORG, .25)
        beat(self, FadeIn(a, shift=RIGHT * .3), t=.8, rt=.4)
        r = card(kr("실제 부품", 44, YEL), YEL, .3).move_to(RIGHT * 4.2)
        beat(self, GrowArrow(Arrow(a.get_right(), r.get_left(), buff=.15, color=YEL, stroke_width=6)), FadeIn(r), t=.9, rt=.5)
        fill(self, r)


class Site(Scene):
    def construct(self):
        c = card(VGroup(kr("무료 사이트", 32, MUTE), kr("보이는 회로이론", 60, YEL)).arrange(DOWN, buff=.2), YEL, .45).move_to(UP * 1.2)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.5)
        items = VGroup(*[card(kr(t, 30, INK), MUTE, .18) for t in ("주파수 응답과 필터", "보드 선도", "연산 증폭기", "라플라스")]).arrange(RIGHT, buff=.25).move_to(DOWN * 1.4)
        for it in items:
            beat(self, FadeIn(it, shift=UP * .15), t=.6, rt=.3)
        fill(self, c)


class Next(Scene):
    def construct(self):
        a = card(VGroup(kr("다음 편", 32, MUTE), kr("버터워스 필터", 52, YEL)).arrange(DOWN, buff=.2), YEL, .35).move_to(UP * 1.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.2, rt=.5)
        b = card(VGroup(kr("재생목록", 30, MUTE), kr("회로이론 한눈에", 44, INK)).arrange(DOWN, buff=.2), INK, .3).move_to(DOWN * 1.4)
        beat(self, FadeIn(b, shift=UP * .2), t=1.1, rt=.5)
        fill(self, a)


# ================= 쇼츠·릴스 전용 =================
class AQ(Scene):
    def construct(self):
        D = opf((-1.8, -.6), "lp", s=.85); build_opf(self, D, .3)
        q = card(VGroup(kr("필터에", 30, INK), kr("OP amp?", 52, YEL)).arrange(DOWN, buff=.15), YEL, .25).move_to(RIGHT * 4.6 + UP * 1.6)
        beat(self, FadeIn(q, scale=1.2), t=.6, rt=.4)
        r = card(kr("이유 3가지", 40, GRN), GRN, .2).move_to(RIGHT * 4.6 + DOWN * .6); beat(self, FadeIn(r), t=.5, rt=.3)
        fill(self, D["amp"], YEL)


class AMul(Scene):
    def construct(self):
        g, ar = chain([block("필터 1", "lp", BLU), block("필터 2", "hp", PUR), block("필터 3", "flat", ORG)])
        g.move_to(UP * 1.0)
        for i, b in enumerate(g):
            beat(self, FadeIn(b, shift=UP * .2), *([GrowArrow(ar[i - 1])] if i else []), t=.5, rt=.35)
        e = card(tex(r"H = H_1 \times H_2 \times H_3", 60, YEL), YEL, .25).move_to(DOWN * 1.6)
        beat(self, Write(e), t=.9, rt=.6)
        fill(self, e)


class BQ(Scene):
    def construct(self):
        L = opf((-4.0, .1), "lp", s=.62); H = opf((3.0, .1), "hp", s=.62)
        beat(self, FadeIn(L["all"]), t=.5, rt=.4); beat(self, FadeIn(H["all"]), t=.5, rt=.4)
        beat(self, L["c"].animate.set_color(YEL), H["c"].animate.set_color(YEL), t=.5, rt=.3)
        c = card(kr("커패시터 자리 하나로", 40, YEL), YEL, .22).move_to(DOWN * 2.6); beat(self, FadeIn(c, scale=1.2), t=.6, rt=.4)
        fill(self, VGroup(L["c"], H["c"]))


class BOut(Scene):
    def construct(self):
        a = sine(LEFT * 3.4 + UP * 1.4, .7, 7, 4.6, INK); b = Line(RIGHT * 1.1 + UP * 1.4, RIGHT * 5.7 + UP * 1.4, color=RED, stroke_width=6)
        beat(self, Create(a), FadeIn(kr("높은 주파수 입력", 28, INK).next_to(a, UP, .25)), t=.7, rt=.5)
        beat(self, GrowArrow(Arrow(LEFT * .6 + UP * 1.4, RIGHT * .8 + UP * 1.4, buff=0, color=MUTE)), Create(b), FadeIn(kr("출력 0", 32, RED).next_to(b, UP, .45)), t=.8, rt=.5)
        ax, g = bode(-2, 2, -30, 6, 6.0, 2.4, DOWN * 1.6, yt=[])
        beat(self, FadeIn(g), Create(curve(ax, lambda w: lpdb(w), -2, 2, YEL, ylo=-30)), FadeIn(kr("저역 통과", 34, YEL).next_to(ax, RIGHT, .1)), t=.9, rt=.6)
        fill(self, b, RED)


class CQ(Scene):
    def construct(self):
        ax, g, cv = hp_example(LEFT * 1.6 + DOWN * .3, 8.6, 4.2)
        beat(self, FadeIn(g), Create(cv), t=.8, rt=.7)
        a = card(VGroup(tex(r"R_1 = ?", 48, CR1), tex(r"R_2 = ?", 48, CR2)).arrange(DOWN, buff=.3), MUTE, .3).move_to(RIGHT * 4.9 + UP * .7)
        beat(self, FadeIn(a, scale=1.2), t=.6, rt=.4)
        c = card(tex(r"C = 0.1\,\mu\mathrm{F}", 40, CC), CC, .18).move_to(RIGHT * 4.9 + DOWN * 1.4); beat(self, FadeIn(c), t=.5, rt=.3)
        fill(self, a)


class CRa(Scene):
    def construct(self):
        e = tex(r"R_1 = \frac{1}{\omega_c C} = \frac{1}{500 \times 0.1\,\mu}", 60, CR1).move_to(UP * 1.2)
        beat(self, Write(e), t=1.0, rt=.8)
        r = card(tex(r"R_1 = 20\,\mathrm{k\Omega}", 76, YEL), YEL, .3).move_to(DOWN * 1.4)
        beat(self, FadeIn(r, scale=1.2), t=.8, rt=.4)
        fill(self, r)


class CRb(Scene):
    def construct(self):
        D = opf((-1.4, .6), "hp", r1=r"20\,\mathrm{k\Omega}", r2=r"200\,\mathrm{k\Omega}", cl=r"0.1\,\mu\mathrm{F}", s=.8)
        beat(self, FadeIn(D["all"]), t=.6, rt=.4)
        e = card(tex(r"R_2 = 10 \times 20\,\mathrm{k} = 200\,\mathrm{k\Omega}", 52, CR2), CR2, .22).move_to(DOWN * 2.6)
        beat(self, FadeIn(e, shift=UP * .2), Indicate(D["lr2"], color=CR2), t=.9, rt=.5)
        fill(self, e, CR2)


class DQ(Scene):
    def construct(self):
        D = opf((-1.8, -.6), "lp", r1=r"1\,\Omega", r2=r"1\,\Omega", cl=r"1\,\mathrm{F}", s=.85); build_opf(self, D, .3)
        q = card(VGroup(kr("왜 전부", 30, INK), kr("1로?", 56, YEL)).arrange(DOWN, buff=.15), YEL, .25).move_to(RIGHT * 4.6 + UP * .4)
        beat(self, FadeIn(q, scale=1.2), t=.6, rt=.4)
        fill(self, q)


class DRes(Scene):
    def construct(self):
        rows_ = [(r"1\,\Omega", r"15.9\,\mathrm{k\Omega}", CR2), (r"1\,\mathrm{F}", r"0.01\,\mu\mathrm{F}", CC), (r"1\ \mathrm{rad/s}", r"1\,\mathrm{kHz}", ORG)]
        g = VGroup()
        for i, (a, b, c) in enumerate(rows_):
            y = 1.8 - i * 1.6
            l = tex(a, 56, MUTE).move_to(LEFT * 3.0 + UP * y); r = tex(b, 60, c).move_to(RIGHT * 2.6 + UP * y)
            ar = Arrow(LEFT * 1.6 + UP * y, RIGHT * .6 + UP * y, buff=0, color=c, stroke_width=5)
            beat(self, FadeIn(l), GrowArrow(ar), FadeIn(r, shift=RIGHT * .2), t=.8, rt=.4); g.add(r)
        fill(self, g)


class EQ(Scene):
    def construct(self):
        a = block("저역 통과", "lp", BLU, 2.8, 2.0).move_to(LEFT * 3.2 + UP * .6); b = block("고역 통과", "hp", PUR, 2.8, 2.0).move_to(RIGHT * 3.2 + UP * .6)
        beat(self, FadeIn(a, shift=UP * .2), t=.5, rt=.3); beat(self, FadeIn(b, shift=UP * .2), t=.5, rt=.3)
        p = tex("+", 72, INK).move_to(UP * .6); beat(self, FadeIn(p), t=.3, rt=.2)
        c = card(kr("= 대역 필터 2개", 44, YEL), YEL, .22).move_to(DOWN * 2.0); beat(self, FadeIn(c, scale=1.2), t=.6, rt=.4)
        fill(self, c)
