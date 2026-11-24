# 능동 필터 2편 (버터워스·좁은 대역) 롱폼 모션그래픽. 1편 형식.
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




# ---------- 2편 전용 ----------
def casc(w, n): return 1 / (1 + w * w) ** (n / 2)
def butter(w, n): return 1 / np.sqrt(1 + w ** (2 * n))
def dbv(v): return 20 * np.log10(max(v, 1e-9))


def lin_axes(o=DOWN * .3, xl=8.0, yl=3.6, xmax=3.0, labels=True):
    ax = Axes(x_range=[0, xmax, 1], y_range=[0, 1.15, .5], x_length=xl, y_length=yl, tips=False,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False}).move_to(o)
    g = VGroup(ax)
    if labels:
        g.add(tex("1", 30, MUTE).next_to(ax.c2p(0, 1), LEFT, .12), tex(r"0.707", 28, MUTE).next_to(ax.c2p(0, .707), LEFT, .12),
              DashedLine(ax.c2p(0, .707), ax.c2p(xmax, .707), color="#2a2e37", stroke_width=2),
              tex(r"\omega_c", 32, MUTE).next_to(ax.c2p(1, 0), DOWN, .12), tex(r"|H|", 34, MUTE).next_to(ax.c2p(0, 1.15), UP, .08))
    return ax, g


def lcurve(ax, f, x0=0.0, x1=3.0, c=YEL, sw=6, n=200):
    xs = np.linspace(x0, x1, n)
    return VMobject(color=c, stroke_width=sw).set_points_smoothly([ax.c2p(x, f(x)) for x in xs])


def sallen(o=(0, 0), s=1.0, c1="C_1", c2="C_2", rl=r"1\,\Omega"):
    """2차 저역 통과 (Fig 15.21, 살렌-키 단위 이득). Vi-R-a-R-(+), C1: a→출력, C2: (+)→접지, 출력→(−) 팔로워."""
    ox, oy = o
    A = opamp((ox + 2.3 * s, oy), 1.0 * s)
    p, m, out = A["p"], A["m"], A["o"]
    xin, xa, xp = ox - 4.2 * s, ox - 2.0 * s, p[0] - .3 * s
    yp = p[1]
    D = dict(A=A, amp=A["g"])
    D["tin"] = term((xin, yp))
    D["ra"] = resistor((xin + .1, yp), (xa, yp), BLU)
    D["rb"] = resistor((xa, yp), (xp - .2 * s, yp), BLU)
    D["wp"] = VGroup(wire((xp - .2 * s, yp), p), jdot((xa, yp)), jdot((xp - .2 * s, yp)))
    ytop = m[1] + 1.4 * s; xo = out[0] + .5 * s
    D["c1"] = capacitor((xa, yp + .6 * s), (xa, ytop), ORG, w=.7 * s)[0]
    D["c1w"] = VGroup(wire((xa, yp), (xa, yp + .6 * s)), poly([(xa, ytop), (xo, ytop), (xo, out[1])]))
    D["c2"] = capacitor((xp - .2 * s, yp), (xp - .2 * s, yp - 1.4 * s), GRN, w=.7 * s)[0]
    D["c2g"] = ground((xp - .2 * s, yp - 1.4 * s))
    D["fol"] = VGroup(poly([(xo, out[1]), (xo, m[1] + .55 * s), (m[0] - .35 * s, m[1] + .55 * s), (m[0] - .35 * s, m[1]), m], YEL, 5), jdot((xo, out[1]), YEL))
    D["outw"] = VGroup(wire(out, (xo + .8 * s, out[1])), term((xo + .8 * s, out[1])))
    D["labs"] = VGroup(tex(rl, 32, BLU).next_to(D["ra"], DOWN, .22), tex(rl, 32, BLU).next_to(D["rb"], DOWN, .22),
                       tex(c1, 36, ORG).next_to(D["c1"], LEFT, .2), tex(c2, 36, GRN).next_to(D["c2"], LEFT, .2),
                       tex(r"V_i", 34, INK).next_to(D["tin"], LEFT, .12), tex(r"V_o", 34, YEL).next_to(D["outw"][1], RIGHT, .12))
    D["all"] = VGroup(D["amp"], D["tin"], D["ra"], D["rb"], D["wp"], D["c1"], D["c1w"], D["c2"], D["c2g"], D["fol"], D["outw"], D["labs"])
    return D


def mfb(o=(0, 0), s=1.0, labs=("R_1", "R_2", "R_3")):
    """좁은 대역 BPF (다중 피드백). Vi-R1-a, a-R2-접지, a-C-출력, a-C-(−), 출력-R3-(−), + 접지."""
    ox, oy = o
    A = opamp((ox + 2.4 * s, oy - .3 * s), 1.0 * s)
    m, p, out = A["m"], A["p"], A["o"]
    xin, xa, xn = ox - 4.2 * s, ox - 1.9 * s, m[0] - .5 * s
    ya = m[1]; xo = out[0] + .5 * s
    D = dict(A=A, amp=A["g"])
    D["tin"] = term((xin, ya))
    D["r1"] = resistor((xin + .1, ya), (xa, ya), BLU)
    D["cb"] = capacitor((xa + .2 * s, ya), (xn, ya), GRN, w=.7 * s)[0]
    D["wn"] = VGroup(wire((xa, ya), (xa + .2 * s, ya)), wire((xn, ya), m), jdot((xa, ya)), jdot((xn, ya)))
    D["r2"] = resistor((xa, ya), (xa, ya - 1.6 * s), PUR); D["g2"] = ground((xa, ya - 1.6 * s))
    yt1, yt2 = ya + 1.1 * s, ya + 2.1 * s
    D["fb1"] = VGroup(wire((xa, ya), (xa, yt2)), capacitor((xa, yt2), (xo, yt2), ORG, w=.7 * s)[0], poly([(xo, yt2), (xo, out[1])]))
    D["fb2"] = VGroup(wire((xn, ya), (xn, yt1)), resistor((xn, yt1), (xo, yt1), RED), jdot((xo, yt1)), jdot((xo, out[1])))
    D["gp"] = VGroup(poly([p, (p[0] - .4 * s, p[1]), (p[0] - .4 * s, p[1] - .4 * s)]), ground((p[0] - .4 * s, p[1] - .4 * s)))
    D["outw"] = VGroup(wire(out, (xo + .8 * s, out[1])), term((xo + .8 * s, out[1])))
    D["labs"] = VGroup(tex(labs[0], 34, BLU).next_to(D["r1"], DOWN, .22), tex(labs[1], 34, PUR).next_to(D["r2"], RIGHT, .2),
                       tex(labs[2], 34, RED).next_to(D["fb2"][1], UP, .15), tex("C", 34, ORG).next_to(D["fb1"][1], UP, .15),
                       tex("C", 34, GRN).next_to(D["cb"], DOWN, .3))
    D["all"] = VGroup(D["amp"], D["tin"], D["r1"], D["cb"], D["wn"], D["r2"], D["g2"], D["fb1"], D["fb2"], D["gp"], D["outw"], D["labs"])
    return D


def twint(o=(0, 0), s=1.0):
    """트윈 T 노치 (σ 피드백은 다리 끝 'σVo' 로 표시). 반환 dict: top, bot, amp, all."""
    ox, oy = o
    xin, xm, xc = ox - 4.2 * s, ox - 2.0 * s, ox + .2 * s
    yt, yb = oy + 1.0 * s, oy - 1.0 * s
    A = opamp((xc + 1.9 * s, oy), .9 * s, )
    p = A["m"] if False else A["p"]
    D = dict(A=A, amp=A["g"])
    D["tin"] = VGroup(term((xin - .3 * s, oy)), wire((xin - .2 * s, oy), (xin, oy)), wire((xin, yb), (xin, yt)))
    top = VGroup(capacitor((xin, yt), (xm, yt), ORG, w=.6 * s)[0], capacitor((xm, yt), (xc, yt), ORG, w=.6 * s)[0],
                 resistor((xm, yt), (xm, yt + 1.2 * s), ORG), jdot((xm, yt)))
    bot = VGroup(resistor((xin, yb), (xm, yb), BLU), resistor((xm, yb), (xc, yb), BLU),
                 capacitor((xm, yb), (xm, yb - 1.2 * s), BLU, w=.6 * s)[0], jdot((xm, yb)))
    D["top"], D["bot"] = top, bot
    D["leg"] = VGroup(tex(r"\tfrac{R}{2}", 30, ORG).next_to(top[2], RIGHT, .15), tex(r"2C", 30, BLU).next_to(bot[2], LEFT, .25),
                      tex(r"\sigma V_o", 28, MUTE).next_to(top[2], UP, .1), tex(r"\sigma V_o", 28, MUTE).next_to(bot[2], DOWN, .1),
                      tex("C", 30, ORG).next_to(top[0], UP, .2), tex("C", 30, ORG).next_to(top[1], UP, .2),
                      tex("R", 30, BLU).next_to(bot[0], DOWN, .25), tex("R", 30, BLU).next_to(bot[1], DOWN, .25))
    D["join"] = VGroup(wire((xc, yt), (xc, yb)), poly([(xc, oy), (A["p"][0] - .3 * s, oy), (A["p"][0] - .3 * s, A["p"][1]), A["p"]]), jdot((xc, oy)))
    out = A["o"]; xo = out[0] + .4 * s
    D["fol"] = VGroup(poly([out, (xo, out[1]), (xo, A["m"][1] + .5 * s), (A["m"][0] - .3 * s, A["m"][1] + .5 * s), (A["m"][0] - .3 * s, A["m"][1]), A["m"]], INK, 4),
                      wire((xo, out[1]), (xo + .7 * s, out[1])), term((xo + .8 * s, out[1])))
    D["all"] = VGroup(D["amp"], D["tin"], top, bot, D["leg"], D["join"], D["fol"])
    return D


def splane(o=ORIGIN, r=1.8):
    o = P3(o)
    g = VGroup(Arrow(o + LEFT * (r + .6), o + RIGHT * (r + .6), buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.04),
               Arrow(o + DOWN * (r + .5), o + UP * (r + .6), buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.04),
               tex(r"\sigma", 30, MUTE).next_to(o + RIGHT * (r + .6), DOWN, .1), tex(r"j\omega", 30, MUTE).next_to(o + UP * (r + .6), RIGHT, .1))
    circ = DashedVMobject(Circle(r, color=MUTE, stroke_width=3).move_to(o), num_dashes=40)
    return g, circ


def xmark(p, c=YEL, s=.16):
    p = P3(p)
    return VGroup(Line(p + (UL) * s, p + (DR) * s, color=c, stroke_width=7), Line(p + (UR) * s, p + (DL) * s, color=c, stroke_width=7))


def casc_bode(o=DOWN * .4, xl=9.0, yl=4.0, ns=(1, 2, 3, 4), cols=(BLU, PUR, GRN, ORG), lab=True):
    ax, g = bode(-1, 1.5, -60, 6, xl, yl, o, yt=[0, -20, -40], xt=[(0, "1")])
    cs = VGroup(*[curve(ax, lambda w, n=n: dbv(casc(w, n)), -1, 1.5, c, 5, ylo=-60) for n, c in zip(ns, cols)])
    return ax, g, cs


# ================= 인트로 =================
class Hook(Scene):
    def construct(self):
        g, ar = chain([block("500Hz", "lp", BLU, 2.2, 1.5) for _ in range(4)], .4)
        g.move_to(UP * 1.2)
        for i, b in enumerate(g):
            beat(self, FadeIn(b, shift=UP * .2), *([GrowArrow(ar[i - 1])] if i else []), t=.4, rt=.3)
        q = card(VGroup(kr("전체 컷오프", 30, MUTE), tex(r"217\,\mathrm{Hz}", 72, RED)).arrange(DOWN, buff=.12), RED, .25).move_to(DOWN * 1.8)
        beat(self, FadeIn(q, scale=1.3), t=.7, rt=.4)
        fill(self, q, RED)


class Goal(Scene):
    def construct(self):
        ax, g = bode(-1, 1.2, -60, 6, 7.4, 4.0, LEFT * 2.6 + DOWN * .3, yt=[0, -20, -40], xt=[(0, "500Hz")])
        beat(self, FadeIn(g), t=.4, rt=.3)
        c0 = curve(ax, lambda w: dbv(casc(w * .435, 4)), -1, 1.2, MUTE, 4, ylo=-60)
        c1 = curve(ax, lambda w: dbv(butter(w, 4)), -1, 1.2, YEL, 7, ylo=-60)
        beat(self, Create(c0), FadeIn(kr("이어 붙인 4차", 24, MUTE).next_to(ax.c2p(-1, -12), UP, .05).shift(RIGHT * .9)), t=.7, rt=.6)
        beat(self, Create(c1), FadeIn(kr("버터워스 4차", 28, YEL).next_to(ax.c2p(-.95, 0), UP, .15).shift(RIGHT * .9)), t=.8, rt=.7)
        r = card(VGroup(kr("커패시터까지", 26, MUTE), tex(r"831\ \ 121", 44, ORG), tex(r"344\ \ 294\ \mathrm{nF}", 44, ORG)).arrange(DOWN, buff=.15), ORG, .25).move_to(RIGHT * 4.8 + UP * .2)
        beat(self, FadeIn(r, shift=UP * .2), t=.7, rt=.4)
        fill(self, c1)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "이어 붙이기 함정", BLU), ("2", "버터워스", PUR), ("3", "2차 회로", GRN), ("4", "몇 차?", ORG), ("5", "좁은 대역", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 30, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=.9, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=.8, rt=.7)
        fill(self, cards)


# ================= STEP 1 이어 붙이기의 함정 =================
class X1(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax, g, cs = casc_bode(LEFT * .8 + DOWN * .4, 9.0, 4.2, ns=(1,), cols=(BLU,))
        beat(self, FadeIn(g), t=.5, rt=.4)
        beat(self, Create(cs[0]), t=.9, rt=.8)
        sl = Line(ax.c2p(0, 0), ax.c2p(1.5, -30), color=RED, stroke_width=4)
        beat(self, Create(DashedVMobject(sl)), FadeIn(card(tex(r"-20\,\mathrm{dB/dec}", 40, RED), RED, .15).next_to(ax.c2p(1.2, -24), RIGHT, .1)), t=.9, rt=.5)
        c = card(kr("경계가 완만", 36, MUTE), MUTE, .2).move_to(UP * 2.6 + RIGHT * 3.5); beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, cs[0], BLU)


class X2(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax, g, cs = casc_bode(LEFT * 1.2 + DOWN * .4, 8.6, 4.2)
        self.add(g)
        labs = ["-20", "-40", "-60", "-80"]
        for i, c in enumerate(cs):
            beat(self, Create(c), FadeIn(tex(labs[i], 30, c.get_color()).move_to(RIGHT * (4.6 + .0) + UP * (1.6 - i * .6))), t=.7, rt=.5)
        n = card(VGroup(kr("기울기", 26, MUTE), tex(r"-20n\ \mathrm{dB/dec}", 40, YEL)).arrange(DOWN, buff=.1), YEL, .2).move_to(RIGHT * 4.9 + DOWN * 1.7)
        beat(self, FadeIn(n), t=.6, rt=.3)
        fill(self, cs[3], ORG)


class X3(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax, g, cs = casc_bode(LEFT * 1.6 + DOWN * .4, 8.0, 4.2); self.add(g, cs)
        dots = VGroup(*[Dot(ax.c2p(0, -3 * n), color=c.get_color(), radius=.1) for n, c in zip((1, 2, 3, 4), cs)])
        beat(self, LaggedStart(*[FadeIn(d, scale=1.5) for d in dots], lag_ratio=.3), t=1.0, rt=.8)
        e = card(tex(r"0.707^4 = 0.25", 48, ORG), ORG, .2).move_to(RIGHT * 4.6 + UP * 1.6)
        beat(self, FadeIn(e, shift=UP * .2), t=.8, rt=.4)
        x4 = np.log10(.435); d = Dot(ax.c2p(x4, -3), color=YEL, radius=.13)
        ar = Arrow(ax.c2p(0, -3) + UP * .35, ax.c2p(x4, -3) + UP * .35, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(d, scale=1.5), FadeIn(kr("3dB 점이 왼쪽으로", 28, YEL).move_to(RIGHT * 4.6 + DOWN * .2)), t=1.0, rt=.6)
        fill(self, d)


class X4(Scene):
    def construct(self):
        self.add(step_tag(1))
        e = tex(r"\omega_{c4} = \sqrt{\sqrt[4]{2} - 1} = 0.435", 64, YEL).move_to(UP * 2.2)
        beat(self, Write(e), t=1.0, rt=.8)
        a = card(tex(r"500\,\mathrm{Hz} \times 0.435 = 217\,\mathrm{Hz}", 52, RED), RED, .22).move_to(UP * .3)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        b = card(VGroup(kr("보정", 30, GRN), tex(r"\frac{500}{0.435} = 1149\,\mathrm{Hz}", 52, GRN)).arrange(RIGHT, buff=.3), GRN, .22).move_to(DOWN * 1.9)
        beat(self, FadeIn(b, shift=UP * .2), t=.9, rt=.4)
        fill(self, a, RED)


class X5(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax, g = lin_axes(DOWN * .4, 9.0, 4.0, 2.5)
        beat(self, FadeIn(g), t=.4, rt=.3)
        box = VMobject(color=MUTE, stroke_width=3).set_points_as_corners([ax.c2p(0, 1), ax.c2p(1, 1), ax.c2p(1, 0)])
        beat(self, Create(DashedVMobject(box)), FadeIn(kr("이상적", 26, MUTE).next_to(ax.c2p(.5, 1), UP, .1)), t=.7, rt=.5)
        c = lcurve(ax, lambda x: casc(x * .435, 4), 0, 2.5, ORG, 6)
        beat(self, Create(c), t=.9, rt=.8)
        br = SurroundingRectangle(VGroup(Dot(ax.c2p(.3, .95)), Dot(ax.c2p(.95, .72))), color=RED, buff=.2, corner_radius=.12)
        beat(self, Create(br), FadeIn(kr("일찍부터 처짐", 32, RED).next_to(br, UP, .15).shift(RIGHT * 1.2)), t=.9, rt=.5)
        fill(self, c, ORG)


# ================= STEP 2 버터워스 =================
class Y1(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        t = card(kr("버터워스 필터", 56, PUR), PUR, .3).move_to(UP * 2.0); beat(self, FadeIn(t, scale=1.2), t=.8, rt=.4)
        a = card(kr("원하는 모양", 36, YEL), YEL, .22).move_to(LEFT * 3.4 + DOWN * .9); b = card(kr("회로", 36, INK), MUTE, .22).move_to(RIGHT * 3.4 + DOWN * .9)
        beat(self, FadeIn(a, shift=UP * .2), t=.6, rt=.3)
        beat(self, GrowArrow(Arrow(a.get_right(), b.get_left(), buff=.2, color=YEL, stroke_width=6)), FadeIn(b), t=.8, rt=.5)
        beat(self, FadeIn(kr("거꾸로 찾기", 30, MUTE).move_to(DOWN * 2.3)), t=.5, rt=.3)
        fill(self, a)


class Y2(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        e = tex(r"|H(j\omega)| = \frac{1}{\sqrt{1 + (\omega/\omega_c)^{2n}}}", 76, INK).move_to(UP * .6)
        beat(self, Write(e), t=1.2, rt=1.0)
        hl = SurroundingRectangle(e[0][-8:], color=YEL, buff=.08, corner_radius=.08)
        beat(self, Create(hl), FadeIn(kr("주파수 비의 2n제곱", 32, YEL).next_to(e, DOWN, .5)), t=.9, rt=.5)
        fill(self, hl)


class Y3(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        ax, g = lin_axes(DOWN * .5, 9.0, 4.2, 2.5); self.add(g)
        cols = (BLU, PUR, GRN, YEL)
        for n, c in zip((1, 2, 4, 8), cols):
            beat(self, Create(lcurve(ax, lambda x, n=n: butter(x, n), 0, 2.5, c, 5)), FadeIn(tex(f"n={n}", 30, c).move_to(RIGHT * 5.4 + UP * (1.6 - .5 * [1, 2, 4, 8].index(n)))), t=.5, rt=.4)
        d = Dot(ax.c2p(1, .707), color=RED, radius=.14)
        beat(self, FadeIn(d, scale=1.6), FadeIn(card(kr("모두 0.707", 32, RED), RED, .15).next_to(ax.c2p(1, .707), UR, .3)), t=.8, rt=.4)
        fill(self, d, RED)


class Y4(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        a = tex(r"\omega < \omega_c :\ 0.8^{16} = 0.028 \approx 0", 52, INK).move_to(UP * 2.4)
        beat(self, Write(a), t=1.0, rt=.7)
        ax, g = lin_axes(DOWN * .9, 8.0, 3.4, 2.2); self.add(g)
        c = lcurve(ax, lambda x: butter(x, 8), 0, 2.2, YEL, 7)
        beat(self, FadeIn(g), Create(c), t=.9, rt=.8)
        f = Line(ax.c2p(0, 1.04), ax.c2p(.9, 1.04), color=GRN, stroke_width=10)
        beat(self, Create(f), FadeIn(kr("가장 평평", 32, GRN).next_to(f, UP, .1)), t=.8, rt=.4)
        fill(self, f, GRN)


class Y5(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        o = LEFT * 2.6 + DOWN * .2; g, circ = splane(o, 2.1)
        beat(self, FadeIn(g), Create(circ), t=.7, rt=.5)
        pts = [o + 2.1 * U(a) for a in (45, 135, 225, 315)]
        L = VGroup(xmark(pts[1]), xmark(pts[2])); R = VGroup(xmark(pts[0], MUTE), xmark(pts[3], MUTE))
        beat(self, FadeIn(R), FadeIn(L), FadeIn(kr("단위원 위 같은 간격", 28, INK).move_to(RIGHT * 3.6 + UP * 2.4)), t=.9, rt=.5)
        beat(self, R.animate.set_opacity(.25), Indicate(L, color=YEL, scale_factor=1.3), t=.8, rt=.6)
        c = card(VGroup(kr("왼쪽 반만", 32, YEL), kr("= 안정한 회로", 32, GRN)).arrange(DOWN, buff=.12), YEL, .22).move_to(RIGHT * 3.6 + DOWN * .3)
        beat(self, FadeIn(c, shift=UP * .2), t=.7, rt=.4)
        fill(self, L)


class Y6(Scene):
    def construct(self):
        self.add(step_tag(2, PUR))
        rows_ = [("n = 2", r"s^2 + 1.414\,s + 1"), ("n = 3", r"(s+1)(s^2 + s + 1)"), ("n = 4", r"(s^2 + 0.765\,s + 1)(s^2 + 1.848\,s + 1)")]
        g = VGroup()
        for i, (a, b) in enumerate(rows_):
            r = VGroup(kr(a, 32, MUTE), tex(b, 46, INK)).arrange(RIGHT, buff=.5)
            g.add(r)
        g.arrange(DOWN, buff=.55, aligned_edge=LEFT).move_to(UP * .3)
        for r in g:
            beat(self, FadeIn(r, shift=UP * .2), t=.7, rt=.35)
        hl = VGroup(SurroundingRectangle(g[2][1][0][4:9], color=YEL, buff=.06), SurroundingRectangle(g[2][1][0][17:22], color=YEL, buff=.06))
        beat(self, Create(hl), FadeIn(card(kr("b 값만 읽기", 32, YEL), YEL, .18).move_to(DOWN * 2.6)), t=.8, rt=.5)
        fill(self, hl)


# ================= STEP 3 2차 회로 =================
class Z1(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        D = sallen((-.6, -.4), 1.0)
        beat(self, FadeIn(D["amp"]), FadeIn(D["tin"]), FadeIn(D["labs"][4]), t=.5, rt=.3)
        beat(self, Create(D["ra"]), Create(D["rb"]), FadeIn(D["wp"]), FadeIn(D["labs"][0:2]), t=.6, rt=.4)
        beat(self, Create(D["c1w"]), FadeIn(D["c1"]), FadeIn(D["labs"][2]), t=.6, rt=.4)
        beat(self, FadeIn(D["c2"]), FadeIn(D["c2g"]), FadeIn(D["labs"][3]), t=.6, rt=.4)
        beat(self, Create(D["fol"]), FadeIn(D["outw"]), FadeIn(D["labs"][5]), FadeIn(kr("전압 팔로워", 28, YEL).move_to(RIGHT * 4.6 + UP * 2.6)), t=.8, rt=.5)
        fill(self, D["fol"])


class Z2(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        D = sallen((-4.0, 1.4), .62); self.add(D["all"]); self.remove(D["labs"][0], D["labs"][1])
        e = tex(r"H = \frac{1/C_1C_2}{s^2 + \frac{2}{C_1}s + \frac{1}{C_1C_2}}", 62, INK).move_to(RIGHT * 2.6 + UP * 1.2)
        beat(self, Write(e), t=1.1, rt=.9)
        a = card(VGroup(kr("s 계수", 28, MUTE), tex(r"\frac{2}{C_1}", 52, ORG)).arrange(RIGHT, buff=.3), ORG, .2).move_to(LEFT * 2.6 + DOWN * 1.9)
        b = card(VGroup(kr("상수", 28, MUTE), tex(r"\frac{1}{C_1C_2}", 52, GRN)).arrange(RIGHT, buff=.3), GRN, .2).move_to(RIGHT * 2.6 + DOWN * 1.9)
        beat(self, FadeIn(a, shift=UP * .2), t=.7, rt=.4); beat(self, FadeIn(b, shift=UP * .2), t=.7, rt=.4)
        fill(self, e)


class Z3(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        t = tex(r"s^2 + b\,s + 1", 64, YEL).move_to(UP * 2.3); beat(self, FadeIn(t), t=.7, rt=.4)
        a = card(tex(r"C_1 = \frac{2}{b}", 72, ORG), ORG, .3).move_to(LEFT * 3.0 + DOWN * .4)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        b = card(tex(r"C_2 = \frac{1}{C_1}", 72, GRN), GRN, .3).move_to(RIGHT * 3.0 + DOWN * .4)
        beat(self, FadeIn(b, shift=UP * .2), t=.9, rt=.4)
        fill(self, VGroup(a, b))


class Z4(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        h = VGroup(kr("4차", 32, MUTE), tex(r"(s^2 + 0.765s + 1)(s^2 + 1.848s + 1)", 44, INK)).arrange(RIGHT, buff=.4).move_to(UP * 2.5)
        beat(self, FadeIn(h), t=.7, rt=.4)
        r1 = card(VGroup(kr("1단", 28, MUTE), tex(r"b = 0.765", 40, INK), tex(r"C_1 = 2.61,\ C_2 = 0.38\,\mathrm{F}", 42, ORG)).arrange(DOWN, buff=.15), ORG, .25).move_to(LEFT * 3.4 + DOWN * .4)
        beat(self, FadeIn(r1, shift=UP * .2), t=.9, rt=.4)
        r2 = card(VGroup(kr("2단", 28, MUTE), tex(r"b = 1.848", 40, INK), tex(r"C_3 = 1.08,\ C_4 = 0.92\,\mathrm{F}", 42, GRN)).arrange(DOWN, buff=.15), GRN, .25).move_to(RIGHT * 3.4 + DOWN * .4)
        beat(self, FadeIn(r2, shift=UP * .2), t=.9, rt=.4)
        fill(self, VGroup(r1, r2))


class Z5(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        a = card(tex(r"k_m = 1000", 48, PUR), PUR, .2).move_to(LEFT * 3.2 + UP * 2.3); b = card(tex(r"k_f = 2\pi \times 500", 48, ORG), ORG, .2).move_to(RIGHT * 3.2 + UP * 2.3)
        beat(self, FadeIn(a), t=.6, rt=.3); beat(self, FadeIn(b), t=.6, rt=.3)
        vals = [("2.61", "831"), ("0.38", "121"), ("1.08", "344"), ("0.92", "294")]
        g = VGroup()
        for i, (p, r) in enumerate(vals):
            x = -4.8 + i * 3.2
            g.add(VGroup(tex(rf"{p}\,\mathrm{{F}}", 36, MUTE), Arrow(UP * .3, DOWN * .3, buff=0, color=YEL, stroke_width=4), tex(rf"{r}\,\mathrm{{nF}}", 48, YEL)).arrange(DOWN, buff=.15).move_to(RIGHT * x + DOWN * .6))
        for k in g:
            beat(self, FadeIn(k, shift=DOWN * .2), t=.5, rt=.3)
        fill(self, g)


class Z6(Scene):
    def construct(self):
        self.add(step_tag(3, GRN))
        bl, ar = chain([block("2차", "lp", ORG, 1.8, 1.3), block("2차", "lp", GRN, 1.8, 1.3), block("×10", "flat", BLU, 1.8, 1.3)], .4)
        bl.move_to(UP * 2.5); beat(self, FadeIn(bl), FadeIn(ar), t=.6, rt=.4)
        ax, g = bode(-1, 1.2, -60, 26, 8.6, 3.6, DOWN * 1.1, yt=[20, 0, -20, -40], xt=[(0, "500Hz")])
        c0 = curve(ax, lambda w: dbv(10 * casc(w * .435, 4)), -1, 1.2, MUTE, 4, ylo=-60)
        c1 = curve(ax, lambda w: dbv(10 * butter(w, 4)), -1, 1.2, YEL, 7, ylo=-60)
        beat(self, FadeIn(g), Create(c0), FadeIn(kr("이어 붙인 4차", 24, MUTE).move_to(RIGHT * 5.4 + DOWN * .2)), t=.8, rt=.6)
        beat(self, Create(c1), FadeIn(kr("버터워스 4차", 28, YEL).move_to(RIGHT * 5.4 + DOWN * .7)), t=.9, rt=.7)
        fill(self, c1)


# ================= STEP 4 몇 차가 필요할까 =================
def order_axes(o=DOWN * .4, xl=9.0, yl=4.2):
    ax, g = bode(2.5, 4.2, -80, 6, xl, yl, o, yt=[0, -50], xt=[(3, "1kHz"), (np.log10(6000), "6kHz")], xlab="f")
    return ax, g


class O1(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = lin_axes(DOWN * .5, 8.4, 3.8, 2.5); self.add(g)
        cols = (BLU, PUR, GRN, ORG, RED, YEL)
        for i, c in enumerate(cols):
            beat(self, Create(lcurve(ax, lambda x, n=i + 1: butter(x, n), 0, 2.5, c, 4)), t=.3, rt=.25)
        a = card(VGroup(kr("차수 ↑", 32, GRN), kr("부품 ↑", 32, RED)).arrange(RIGHT, buff=.5), MUTE, .2).move_to(UP * 2.8)
        beat(self, FadeIn(a), t=.6, rt=.3)
        b = card(kr("최소 차수는?", 36, YEL), YEL, .2).move_to(RIGHT * 4.4 + UP * 1.0); beat(self, FadeIn(b, scale=1.2), t=.6, rt=.3)
        fill(self, b)


class O2(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = order_axes(); beat(self, FadeIn(g), t=.5, rt=.4)
        x6 = np.log10(6000)
        zone = Polygon(ax.c2p(x6, -50), ax.c2p(4.2, -50), ax.c2p(4.2, 6), ax.c2p(x6, 6), color=RED, fill_color=RED, fill_opacity=.18, stroke_width=0)
        beat(self, FadeIn(zone), t=.6, rt=.4)
        d = Dot(ax.c2p(x6, -50), color=RED, radius=.13)
        beat(self, FadeIn(d, scale=1.5), FadeIn(card(VGroup(tex(r"6\,\mathrm{kHz}", 36, INK), tex(r"\le -50\,\mathrm{dB}", 40, RED)).arrange(DOWN, buff=.1), RED, .15).next_to(ax.c2p(x6, -50), DL, .2)), t=.9, rt=.5)
        c = card(VGroup(kr("컷오프", 26, MUTE), tex(r"1\,\mathrm{kHz}", 40, YEL)).arrange(DOWN, buff=.1), YEL, .15).next_to(ax.c2p(3, 0), UP, .25)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, d, RED)


class O3(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        a = tex(r"n = \frac{-0.05\,A_s}{\log_{10}(\omega_s/\omega_p)}", 70, INK).move_to(UP * 1.6)
        beat(self, Write(a), t=1.2, rt=.9)
        b = tex(r"= \frac{0.05 \times 50}{\log_{10} 6}", 70, YEL).move_to(DOWN * 1.2)
        beat(self, Write(b), t=1.0, rt=.8)
        fill(self, b)


class O4(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        a = tex(r"n = 3.21", 96, INK).move_to(UP * 1.5); beat(self, FadeIn(a, scale=1.2), t=.8, rt=.4)
        r = card(kr("반올림 → 3", 36, MUTE), MUTE, .2).move_to(LEFT * 3.0 + DOWN * 1.0); beat(self, FadeIn(r), t=.5, rt=.3)
        beat(self, Create(cross(r)), t=.5, rt=.3)
        u = card(VGroup(kr("올림", 36, GRN), tex(r"n = 4", 64, GRN)).arrange(RIGHT, buff=.3), GRN, .25).move_to(RIGHT * 3.0 + DOWN * 1.0)
        beat(self, FadeIn(u, scale=1.2), t=.8, rt=.4)
        fill(self, u, GRN)


class O5(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        ax, g = order_axes(LEFT * 1.2 + DOWN * .4, 8.4, 4.2); self.add(g)
        x6 = np.log10(6000)
        self.add(Polygon(ax.c2p(x6, -50), ax.c2p(4.2, -50), ax.c2p(4.2, 6), ax.c2p(x6, 6), color=RED, fill_color=RED, fill_opacity=.18, stroke_width=0))
        c3 = curve(ax, lambda f: dbv(butter(f / 1000, 3)), 2.5, 4.2, PUR, 5, ylo=-80)
        c4 = curve(ax, lambda f: dbv(butter(f / 1000, 4)), 2.5, 4.2, GRN, 7, ylo=-80)
        beat(self, Create(c3), t=.7, rt=.6)
        d3 = Dot(ax.c2p(x6, -46.7), color=PUR, radius=.12)
        beat(self, FadeIn(d3, scale=1.5), FadeIn(card(VGroup(kr("3차", 28, PUR), tex(r"-46.7\,\mathrm{dB}", 36, PUR), kr("부족", 28, RED)).arrange(RIGHT, buff=.2), PUR, .15).move_to(RIGHT * 4.6 + UP * 1.4)), t=.9, rt=.4)
        beat(self, Create(c4), t=.7, rt=.6)
        d4 = Dot(ax.c2p(x6, -62.3), color=GRN, radius=.12)
        beat(self, FadeIn(d4, scale=1.5), FadeIn(card(VGroup(kr("4차", 28, GRN), tex(r"-62\,\mathrm{dB}", 36, GRN), kr("통과", 28, GRN)).arrange(RIGHT, buff=.2), GRN, .15).move_to(RIGHT * 4.6 + DOWN * .2)), t=.9, rt=.4)
        fill(self, d4, GRN)


# ================= STEP 5 좁은 대역 =================
class G1(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        o = LEFT * 3.6 + DOWN * .2; g, circ = splane(o, 1.8)
        beat(self, FadeIn(g), t=.5, rt=.3)
        p = VGroup(xmark(o + LEFT * .5), xmark(o + LEFT * 1.6))
        beat(self, FadeIn(p, scale=1.4), FadeIn(kr("실수 극점뿐", 28, RED).next_to(o + DOWN * 2.4, DOWN, .05)), t=.8, rt=.4)
        ax, bg = bode(-2, 2, -30, 6, 5.6, 3.0, RIGHT * 3.2 + DOWN * .2, yt=[0])
        w = curve(ax, lambda w: dbv(abs((1j * w) / ((1j * w + .5) * (1j * w + 2)) * 2.5)), -2, 2, MUTE, 5, ylo=-30)
        beat(self, FadeIn(bg), Create(w), t=.8, rt=.6)
        q = card(tex(r"Q \le 0.5", 48, RED), RED, .2).move_to(RIGHT * 3.2 + UP * 2.3); beat(self, FadeIn(q, scale=1.2), t=.6, rt=.3)
        fill(self, q, RED)


class G2(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        D = mfb((-.8, -.6), .95)
        beat(self, FadeIn(VGroup(D["amp"], D["tin"], D["r1"], D["cb"], D["wn"], D["r2"], D["g2"], D["gp"], D["outw"])), FadeIn(D["labs"][0:2]), FadeIn(D["labs"][4]), t=.7, rt=.5)
        beat(self, Create(D["fb1"]), FadeIn(D["labs"][3]), t=.6, rt=.4)
        beat(self, Create(D["fb2"]), FadeIn(D["labs"][2]), t=.6, rt=.4)
        beat(self, D["fb1"].animate.set_color(YEL), D["fb2"].animate.set_color(YEL), FadeIn(card(kr("피드백 두 갈래", 32, YEL), YEL, .18).move_to(RIGHT * 4.6 + UP * 2.8)), t=.8, rt=.4)
        fill(self, VGroup(D["fb1"], D["fb2"]))


class G3(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        a = card(VGroup(kr("이득", 26, MUTE), tex(r"R_1 = \frac{Q}{K}", 60, BLU)).arrange(DOWN, buff=.12), BLU, .25).move_to(LEFT * 4.2 + UP * .6)
        b = card(VGroup(kr("대역폭", 26, MUTE), tex(r"R_3 = 2Q", 60, RED)).arrange(DOWN, buff=.12), RED, .25).move_to(UP * .6)
        c = card(VGroup(kr("조정용", 26, MUTE), tex(r"R_2 = \frac{Q}{2Q^2 - K}", 52, PUR)).arrange(DOWN, buff=.12), PUR, .25).move_to(RIGHT * 4.3 + UP * .6)
        for k in (a, b, c):
            beat(self, FadeIn(k, shift=UP * .2), t=.8, rt=.4)
        n = kr("(C = 1F, 중심 1 rad/s 기준)", 26, MUTE).move_to(DOWN * 1.6); beat(self, FadeIn(n), t=.5, rt=.3)
        fill(self, VGroup(a, b))


class G4(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        ax = Axes(x_range=[2400, 3600, 200], y_range=[0, 2.3, 1], x_length=7.6, y_length=3.8, tips=False, axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False}).move_to(LEFT * 2.4 + DOWN * .4)
        f0, Q, K = 3000, 10, 2
        H = lambda f: K / np.sqrt(1 + Q * Q * (f / f0 - f0 / f) ** 2)
        c = VMobject(color=YEL, stroke_width=7).set_points_smoothly([ax.c2p(f, H(f)) for f in np.linspace(2400, 3600, 300)])
        beat(self, FadeIn(ax), FadeIn(kr("3kHz", 26, MUTE).next_to(ax.c2p(3000, 0), DOWN, .12)), t=.4, rt=.3)
        beat(self, Create(c), t=1.0, rt=.9)
        bw = DoubleArrow(ax.c2p(2854, 1.414), ax.c2p(3154, 1.414), buff=0, color=GRN, stroke_width=5, tip_length=.18)
        beat(self, GrowFromCenter(bw), FadeIn(tex(r"300\,\mathrm{Hz}", 36, GRN).next_to(bw, LEFT, .15)), t=.8, rt=.4)
        v = card(VGroup(tex(r"R_1 = 26.5\,\mathrm{k\Omega}", 40, BLU), tex(r"R_2 = 268\,\Omega", 40, PUR), tex(r"R_3 = 106\,\mathrm{k\Omega}", 40, RED)).arrange(DOWN, buff=.2, aligned_edge=LEFT), MUTE, .25).move_to(RIGHT * 4.5 + DOWN * .2)
        beat(self, FadeIn(v, shift=UP * .2), t=.8, rt=.4)
        fill(self, c)


class G5(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        D = twint((-.4, -.3), .95)
        beat(self, FadeIn(D["tin"]), FadeIn(D["amp"]), FadeIn(D["join"]), FadeIn(D["fol"]), t=.6, rt=.4)
        beat(self, Create(D["top"]), FadeIn(D["leg"][0]), FadeIn(D["leg"][2]), FadeIn(D["leg"][4:6]), t=.7, rt=.5)
        beat(self, Create(D["bot"]), FadeIn(D["leg"][1]), FadeIn(D["leg"][3]), FadeIn(D["leg"][6:8]), t=.7, rt=.5)
        t = card(kr("트윈 T", 40, YEL), YEL, .2).move_to(RIGHT * 4.8 + UP * 2.6); beat(self, FadeIn(t, scale=1.2), t=.5, rt=.3)
        beat(self, Indicate(D["top"], color=YEL), Indicate(D["bot"], color=YEL), FadeIn(kr("중심 주파수에서 상쇄", 28, RED).move_to(RIGHT * 4.8 + DOWN * 2.4)), t=.9, rt=.6)
        fill(self, VGroup(D["top"], D["bot"]))


def notch_curve(ax, Q=5, x0=-1, x1=1, c=YEL):
    def h(w):
        s = 1j * w; return abs((s * s + 1) / (s * s + s / Q + 1))
    return curve(ax, lambda w: dbv(h(w)), x0, x1, c, 7, n=400, ylo=-40)


class G6(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        ax, g = bode(-1, 1, -40, 6, 7.2, 3.8, LEFT * 2.6 + DOWN * .4, yt=[0, -20], xt=[(0, "60Hz")], xlab="f")
        beat(self, FadeIn(g), Create(notch_curve(ax)), t=1.0, rt=.9)
        d = Dot(ax.c2p(0, -40), color=RED, radius=.13); beat(self, FadeIn(d, scale=1.5), FadeIn(kr("완전히 0", 30, RED).next_to(d, RIGHT, .2)), t=.7, rt=.4)
        a = card(tex(r"R = \frac{1}{\omega_0 C}", 52, BLU), BLU, .2).move_to(RIGHT * 4.5 + UP * 1.4)
        b = card(tex(r"\sigma = 1 - \frac{1}{4Q}", 52, ORG), ORG, .2).move_to(RIGHT * 4.5 + DOWN * .5)
        beat(self, FadeIn(a, shift=UP * .2), t=.7, rt=.4); beat(self, FadeIn(b, shift=UP * .2), t=.7, rt=.4)
        fill(self, d, RED)


# ================= 정리 =================
class E1(Scene):
    def construct(self):
        a = card(VGroup(kr("같은 필터 이어 붙이기", 30, MUTE), tex(r"\omega_c \times 0.435", 56, RED)).arrange(DOWN, buff=.15), RED, .3).move_to(LEFT * 3.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.5)
        b = card(VGroup(kr("통과 대역", 30, MUTE), kr("처짐", 48, RED)).arrange(DOWN, buff=.15), RED, .3).move_to(RIGHT * 3.3)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.5)
        fill(self, a, RED)


class E2(Scene):
    def construct(self):
        a = card(VGroup(kr("버터워스", 30, MUTE), kr("가장 평평", 48, PUR)).arrange(DOWN, buff=.15), PUR, .3).move_to(LEFT * 3.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.5)
        b = card(VGroup(kr("2차 회로", 30, MUTE), tex(r"C_1 = \frac{2}{b}", 60, ORG)).arrange(DOWN, buff=.15), ORG, .3).move_to(RIGHT * 3.3)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.5)
        fill(self, VGroup(a, b))


class E3(Scene):
    def construct(self):
        items = [("차수", "올림", GRN), ("좁은 대역", "다중 피드백", BLU), ("노치", "트윈 T", YEL)]
        g = VGroup(*[card(VGroup(kr(a, 28, MUTE), kr(b, 40, c)).arrange(DOWN, buff=.15), c, .28) for a, b, c in items]).arrange(RIGHT, buff=.5)
        for k in g:
            beat(self, FadeIn(k, shift=UP * .2), t=.8, rt=.4)
        fill(self, g)


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
        a = card(VGroup(kr("1편", 32, MUTE), kr("인덕터 없이 필터 · 스케일링", 44, YEL)).arrange(DOWN, buff=.2), YEL, .35).move_to(UP * 1.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.2, rt=.5)
        b = card(VGroup(kr("재생목록", 30, MUTE), kr("회로이론 한눈에", 44, INK)).arrange(DOWN, buff=.2), INK, .3).move_to(DOWN * 1.4)
        beat(self, FadeIn(b, shift=UP * .2), t=1.1, rt=.5)
        fill(self, a)


# ================= 쇼츠·릴스 전용 =================
class AQ(Scene):
    def construct(self):
        g, ar = chain([block("500Hz", "lp", BLU, 2.2, 1.5) for _ in range(4)], .4)
        g.move_to(UP * 1.2)
        beat(self, FadeIn(g), FadeIn(ar), t=.6, rt=.4)
        q = card(VGroup(kr("전체 컷오프", 30, MUTE), kr("몇 Hz?", 60, YEL)).arrange(DOWN, buff=.12), YEL, .25).move_to(DOWN * 1.8)
        beat(self, FadeIn(q, scale=1.3), t=.6, rt=.4)
        fill(self, q)


class AAns(Scene):
    def construct(self):
        a = tex(r"500\,\mathrm{Hz}", 80, MUTE).move_to(LEFT * 3.2 + UP * .3); beat(self, FadeIn(a), t=.5, rt=.3)
        beat(self, Create(cross(a)), t=.4, rt=.3)
        b = card(tex(r"217\,\mathrm{Hz}", 96, RED), RED, .3).move_to(RIGHT * 3.0 + UP * .3); beat(self, FadeIn(b, scale=1.3), t=.7, rt=.4)
        fill(self, b, RED)


class AFix(Scene):
    def construct(self):
        g, ar = chain([block("1149Hz", "lp", GRN, 2.2, 1.5) for _ in range(4)], .4)
        g.move_to(UP * 1.4); beat(self, FadeIn(g), FadeIn(ar), t=.7, rt=.4)
        c = card(VGroup(kr("전체", 30, MUTE), tex(r"500\,\mathrm{Hz}", 64, GRN)).arrange(RIGHT, buff=.3), GRN, .25).move_to(DOWN * 1.6)
        beat(self, FadeIn(c, scale=1.2), t=.7, rt=.4)
        fill(self, c, GRN)


class BQ(Scene):
    def construct(self):
        ax, g = lin_axes(DOWN * .4, 9.0, 4.2, 2.5); self.add(g)
        cs = VGroup(*[lcurve(ax, lambda x, n=n: butter(x, n), 0, 2.5, c, 5) for n, c in zip((1, 2, 4, 8), (BLU, PUR, GRN, YEL))])
        beat(self, LaggedStart(*[Create(c) for c in cs], lag_ratio=.3), t=1.2, rt=1.0)
        d = Dot(ax.c2p(1, .707), color=RED, radius=.14); beat(self, FadeIn(d, scale=1.6), t=.4, rt=.3)
        q = card(kr("몇 차든 같은 점", 34, RED), RED, .18).move_to(RIGHT * 3.6 + UP * 2.4); beat(self, FadeIn(q), t=.5, rt=.3)
        fill(self, d, RED)


class BFlat(Scene):
    def construct(self):
        ax, g = lin_axes(DOWN * .6, 8.4, 3.8, 2.2); self.add(g)
        c = lcurve(ax, lambda x: butter(x, 8), 0, 2.2, YEL, 7); beat(self, Create(c), t=.8, rt=.7)
        t = card(VGroup(kr("별명", 28, MUTE), kr("최대 평탄", 52, YEL)).arrange(DOWN, buff=.12), YEL, .25).move_to(RIGHT * 3.6 + UP * 1.6)
        beat(self, FadeIn(t, scale=1.2), t=.7, rt=.4)
        fill(self, t)


class CQ(Scene):
    def construct(self):
        D = sallen((-.6, -.2), .95); beat(self, FadeIn(D["all"]), t=.6, rt=.4)
        beat(self, D["c1"].animate.set_color(YEL), D["c2"].animate.set_color(YEL), t=.4, rt=.3)
        q = card(kr("C 두 개를 한 줄로", 36, YEL), YEL, .2).move_to(UP * 3.0); beat(self, FadeIn(q, scale=1.2), t=.6, rt=.3)
        fill(self, VGroup(D["c1"], D["c2"]))


class CMatch(Scene):
    def construct(self):
        a = tex(r"s^2 + \frac{2}{C_1}s + \frac{1}{C_1C_2}", 64, INK).move_to(UP * 1.5); b = tex(r"s^2 + b\,s + 1", 64, YEL).move_to(DOWN * 1.2)
        beat(self, Write(a), t=.9, rt=.7)
        beat(self, FadeIn(kr("= (표)", 32, MUTE).move_to(LEFT * 3.4 + DOWN * 1.2)), Write(b), t=.9, rt=.6)
        fill(self, b)


class CEx(Scene):
    def construct(self):
        t = card(VGroup(kr("2차", 30, MUTE), tex(r"b = \sqrt{2}", 52, INK)).arrange(RIGHT, buff=.3), MUTE, .2).move_to(UP * 2.3); beat(self, FadeIn(t), t=.6, rt=.3)
        a = card(tex(r"C_1 = 1.414\,\mathrm{F}", 60, ORG), ORG, .25).move_to(LEFT * 3.2 + DOWN * .5); beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        b = card(tex(r"C_2 = 0.707\,\mathrm{F}", 60, GRN), GRN, .25).move_to(RIGHT * 3.2 + DOWN * .5); beat(self, FadeIn(b, shift=UP * .2), t=.8, rt=.4)
        fill(self, VGroup(a, b))


class CScale(Scene):
    def construct(self):
        p = card(VGroup(tex(r"1\,\Omega", 44, INK), tex(r"1.414\,\mathrm{F}", 44, INK)).arrange(DOWN, buff=.2), MUTE, .25).move_to(LEFT * 4.0)
        beat(self, FadeIn(p), t=.5, rt=.3)
        a = card(VGroup(tex(r"\times k_f", 44, ORG), tex(r"\times k_m", 44, PUR)).arrange(DOWN, buff=.2), ORG, .2); beat(self, FadeIn(a, shift=RIGHT * .3), t=.6, rt=.3)
        r = card(kr("실제 값", 44, YEL), YEL, .3).move_to(RIGHT * 4.0)
        beat(self, GrowArrow(Arrow(a.get_right(), r.get_left(), buff=.15, color=YEL, stroke_width=6)), FadeIn(r), t=.8, rt=.5)
        fill(self, r)


class DQ(Scene):
    def construct(self):
        ax, g = order_axes(DOWN * .6, 8.6, 3.8); self.add(g)
        x6 = np.log10(6000)
        self.add(Polygon(ax.c2p(x6, -50), ax.c2p(4.2, -50), ax.c2p(4.2, 6), ax.c2p(x6, 6), color=RED, fill_color=RED, fill_opacity=.18, stroke_width=0))
        beat(self, FadeIn(Dot(ax.c2p(x6, -50), color=RED, radius=.13), scale=1.5), t=.4, rt=.3)
        q = card(kr("몇 차?", 60, YEL), YEL, .25).move_to(UP * 2.8); beat(self, FadeIn(q, scale=1.3), t=.6, rt=.4)
        fill(self, q)


class DFail(Scene):
    def construct(self):
        ax, g = order_axes(LEFT * .8 + DOWN * .5, 8.6, 4.0); self.add(g)
        x6 = np.log10(6000)
        self.add(Polygon(ax.c2p(x6, -50), ax.c2p(4.2, -50), ax.c2p(4.2, 6), ax.c2p(x6, 6), color=RED, fill_color=RED, fill_opacity=.18, stroke_width=0))
        c3 = curve(ax, lambda f: dbv(butter(f / 1000, 3)), 2.5, 4.2, PUR, 6, ylo=-80); beat(self, Create(c3), t=.7, rt=.6)
        d = Dot(ax.c2p(x6, -46.7), color=PUR, radius=.13)
        beat(self, FadeIn(d, scale=1.5), FadeIn(card(VGroup(kr("3차", 30, PUR), tex(r"-46.7\,\mathrm{dB}", 40, PUR)).arrange(RIGHT, buff=.2), PUR, .15).move_to(RIGHT * 3.6 + UP * 2.4)), t=.7, rt=.4)
        beat(self, FadeIn(card(kr("부족", 40, RED), RED, .18).move_to(RIGHT * 3.6 + UP * 1.2)), t=.5, rt=.3)
        fill(self, d, RED)


class DPass(Scene):
    def construct(self):
        ax, g = order_axes(LEFT * .8 + DOWN * .5, 8.6, 4.0); self.add(g)
        x6 = np.log10(6000)
        self.add(Polygon(ax.c2p(x6, -50), ax.c2p(4.2, -50), ax.c2p(4.2, 6), ax.c2p(x6, 6), color=RED, fill_color=RED, fill_opacity=.18, stroke_width=0))
        c4 = curve(ax, lambda f: dbv(butter(f / 1000, 4)), 2.5, 4.2, GRN, 7, ylo=-80); beat(self, Create(c4), t=.7, rt=.6)
        d = Dot(ax.c2p(x6, -62.3), color=GRN, radius=.13)
        beat(self, FadeIn(d, scale=1.5), FadeIn(card(VGroup(kr("4차", 30, GRN), tex(r"-62\,\mathrm{dB}", 40, GRN)).arrange(RIGHT, buff=.2), GRN, .15).move_to(RIGHT * 3.6 + UP * 2.4)), t=.7, rt=.4)
        beat(self, FadeIn(card(kr("정답 4차", 40, GRN), GRN, .18).move_to(RIGHT * 3.6 + UP * 1.2)), t=.5, rt=.3)
        fill(self, d, GRN)


class EQ(Scene):
    def construct(self):
        a = sine(UP * 1.2, .9, 6, 9.0, INK); beat(self, Create(a), FadeIn(kr("60Hz 잡음", 32, RED).move_to(UP * 2.7)), t=.8, rt=.6)
        q = card(VGroup(kr("그 주파수만", 32, MUTE), kr("0으로", 60, YEL)).arrange(DOWN, buff=.12), YEL, .25).move_to(DOWN * 1.6)
        beat(self, FadeIn(q, scale=1.2), t=.6, rt=.4)
        fill(self, q)


class ECancel(Scene):
    def construct(self):
        a = sine(LEFT * 3.0 + UP * 1.6, .8, 2, 4.6, ORG); b = sine(LEFT * 3.0 + DOWN * .8, .8, 2, 4.6, BLU, phase=PI)
        beat(self, Create(a), FadeIn(kr("위쪽 T", 28, ORG).next_to(a, LEFT, .2)), t=.6, rt=.5)
        beat(self, Create(b), FadeIn(kr("아래쪽 T", 28, BLU).next_to(b, LEFT, .2)), t=.6, rt=.5)
        s = Line(RIGHT * 1.6 + UP * .4, RIGHT * 5.8 + UP * .4, color=GRN, stroke_width=7)
        beat(self, GrowArrow(Arrow(LEFT * .4 + UP * .4, RIGHT * 1.2 + UP * .4, buff=0, color=MUTE)), Create(s), FadeIn(kr("합 = 0", 36, GRN).next_to(s, UP, .3)), t=.8, rt=.5)
        fill(self, s, GRN)


class EZoom(Scene):
    def construct(self):
        ax, g = bode(-1, 1, -40, 6, 9.0, 4.0, DOWN * .4, yt=[0, -20], xt=[(0, "60Hz")], xlab="f")
        beat(self, FadeIn(g), Create(notch_curve(ax, 8)), t=1.0, rt=.9)
        a = card(kr("옆 주파수는 그대로", 32, GRN), GRN, .18).move_to(UP * 2.9); beat(self, FadeIn(a), t=.6, rt=.3)
        fill(self, a, GRN)
