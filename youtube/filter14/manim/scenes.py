# 14장 필터 롱폼 모션그래픽. 16:9, 핵심은 가운데(세로 쇼츠에서도 씀). 종속 전원 편 형식.
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


def PT3(p): return np.array([p[0], p[1], 0.0]) if len(p) == 2 else np.array(p, dtype=float)
def wire(a, b, c=INK, w=4): return Line(PT3(a), PT3(b), color=c, stroke_width=w)

# ---------- 회로 부품 ----------
def coil(a, b, c=INK, n=4, sw=5):
    a, b = PT3(a), PT3(b); d = b - a; L = np.linalg.norm(d); u = d / L
    seg = L * .6; r = seg / n / 2; s0 = a + u * (L - seg) / 2
    g = VGroup(Line(a, s0, color=c, stroke_width=sw))
    ang = np.arctan2(u[1], u[0])
    for i in range(n):
        ctr = s0 + u * (r * (2 * i + 1))
        g.add(Arc(radius=r, start_angle=ang + PI, angle=-PI, color=c, stroke_width=sw).move_arc_center_to(ctr))
    g.add(Line(s0 + u * seg, b, color=c, stroke_width=sw))
    return g


def resistor(a, b, c=INK, sw=5):
    a, b = PT3(a), PT3(b); d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    s0 = a + u * L * .25; seg = L * .5; pts = [a, s0]
    for i in range(6):
        pts.append(s0 + u * seg * (i + .5) / 6 + n * (.22 if i % 2 == 0 else -.22))
    pts += [s0 + u * seg, b]
    return VMobject(color=c, stroke_width=sw).set_points_as_corners(pts)


def capacitor(a, b, c=INK, sw=5, gap=.26, w=.9):
    """a→b 사이 커패시터: 가운데에 판 두 개. 반환 (그룹, 판1, 판2, 리드1, 리드2)."""
    a, b = PT3(a), PT3(b); d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    m = (a + b) / 2; p1 = m - u * gap / 2; p2 = m + u * gap / 2
    l1 = Line(a, p1, color=c, stroke_width=sw); l2 = Line(p2, b, color=c, stroke_width=sw)
    s1 = Line(p1 - n * w / 2, p1 + n * w / 2, color=c, stroke_width=sw + 3); s2 = Line(p2 - n * w / 2, p2 + n * w / 2, color=c, stroke_width=sw + 3)
    return VGroup(l1, s1, s2, l2), s1, s2, l1, l2


def acsrc(p, c=INK, r=.55):
    p = PT3(p); ax = np.linspace(-.35, .35, 30)
    s = VMobject(color=c, stroke_width=5).set_points_smoothly([p + np.array([x, .22 * np.sin(x / .35 * PI), 0]) for x in ax])
    return VGroup(Circle(r, color=c, stroke_width=5).move_to(p), s)


def battery(p, c=INK, s=1.0):
    p = PT3(p)
    return VGroup(Line(p + UP * .18 * s + LEFT * .55 * s, p + UP * .18 * s + RIGHT * .55 * s, color=c, stroke_width=6),
                  Line(p + DOWN * .18 * s + LEFT * .3 * s, p + DOWN * .18 * s + RIGHT * .3 * s, color=c, stroke_width=10))


def term(p, c=INK):
    return Circle(.1, color=c, fill_color=BG, fill_opacity=1, stroke_width=4).move_to(PT3(p))



def U(deg): return np.array([np.cos(deg * DEGREES), np.sin(deg * DEGREES), 0.0])


def sine(pt, amp, cycles, length, col, phase=0, n=200, sw=5, f=np.cos):
    """가운데 pt, 가로 length, 진폭 amp, cycles 주기. f=np.cos 면 왼쪽 끝에서 꼭대기(위상 0)."""
    p = PT3(pt); xs = np.linspace(-length / 2, length / 2, n)
    return VMobject(color=col, stroke_width=sw).set_points_smoothly(
        [p + np.array([x, amp * f(2 * PI * cycles * (x + length / 2) / length + phase), 0]) for x in xs])


def taxis(o, length=8.0, h=1.6, lab="t"):
    o = PT3(o)
    g = VGroup(Arrow(o + LEFT * .2, o + RIGHT * (length + .3), buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.03),
               Line(o + DOWN * h, o + UP * h, color=MUTE, stroke_width=3))
    g.add(tex(lab, 34, MUTE).next_to(g[0].get_end(), DOWN, .1))
    return g


def plane(o=ORIGIN, r=2.6, lab=True):
    """복소평면: 실수축(Re)·허수축(Im)."""
    o = PT3(o)
    g = VGroup(Arrow(o + LEFT * r * .35, o + RIGHT * r, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.06),
               Arrow(o + DOWN * r, o + UP * r, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.06))
    if lab:
        g.add(kr("실수", 24, MUTE).next_to(g[0].get_end(), DOWN, .12), kr("허수 j", 24, MUTE).next_to(g[1].get_end(), RIGHT, .12))
    return g


def vec(a, b, c=YEL, sw=7):
    return Arrow(PT3(a), PT3(b), buff=0, color=c, stroke_width=sw, max_tip_length_to_length_ratio=.18, max_stroke_width_to_length_ratio=12)


def angle_arc(o, a0, a1, r=.7, c=YEL):
    return Arc(radius=r, start_angle=a0 * DEGREES, angle=(a1 - a0) * DEGREES, arc_center=PT3(o), color=c, stroke_width=4)


def right_mark(p, u, v, s=.28, c=INK):
    p = PT3(p); u = PT3(u) / np.linalg.norm(PT3(u)); v = PT3(v) / np.linalg.norm(PT3(v))
    return VMobject(color=c, stroke_width=3).set_points_as_corners([p + u * s, p + u * s + v * s, p + v * s])


def series(o=ORIGIN, W=8.0, H=2.6, withC=False, src_lab=r"10\angle 0^\circ\,\mathrm{V}", rl=r"3\,\Omega", ll=r"4\,\mathrm{mH}", cl=r"-j4\,\Omega"):
    """직렬 R-L(-C) 회로. 반환 dict: g, src, R, L, C, lr, ll, lc, ls, xs, yt, yb."""
    o = PT3(o); x0, x1 = o[0] - W / 2, o[0] + W / 2; yt, yb = o[1] + H / 2, o[1] - H / 2
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




# ---------- 공통 작은 것 ----------
def om(v, size=38, c=INK):
    return tex(rf"{v}\,\Omega", size, c)


def cross(m, c=RED):
    return Cross(m, stroke_color=c, stroke_width=7, scale_factor=1.1)


def info(label, val, c=YEL, size=56, lsize=28):
    """작은 제목 + 큰 값 카드."""
    v = val if isinstance(val, Mobject) else tex(val, size, c)
    return card(VGroup(kr(label, lsize, MUTE), v).arrange(DOWN, buff=.18), c, .25)


def opamp(o=ORIGIN, s=1.0, c=INK):
    o = PT3(o)
    tri = Polygon(o + LEFT * 1.2 * s + UP * 1.1 * s, o + LEFT * 1.2 * s + DOWN * 1.1 * s, o + RIGHT * 1.2 * s, color=c, stroke_width=5)
    pm = VGroup(tex("+", 30, c).move_to(o + LEFT * .8 * s + UP * .5 * s), tex("-", 34, c).move_to(o + LEFT * .8 * s + DOWN * .5 * s))
    ins = VGroup(Line(o + LEFT * 2.2 * s + UP * .5 * s, o + LEFT * 1.2 * s + UP * .5 * s, color=c, stroke_width=5),
                 Line(o + LEFT * 2.2 * s + DOWN * .5 * s, o + LEFT * 1.2 * s + DOWN * .5 * s, color=c, stroke_width=5))
    out = Line(o + RIGHT * 1.2 * s, o + RIGHT * 2.2 * s, color=c, stroke_width=5)
    return dict(g=VGroup(tri, pm, ins, out), vp=o + LEFT * 2.2 * s + UP * .5 * s, vm=o + LEFT * 2.2 * s + DOWN * .5 * s, vo=o + RIGHT * 2.2 * s)


# ---------- 필터 전용 ----------
ELC = {"R": BLU, "L": GRN, "C": ORG}


def element(kind, a, b, c):
    if kind == "R": return resistor(a, b, c)
    if kind == "L": return coil(a, b, c)
    return capacitor(a, b, c)[0]


def sloop(o=ORIGIN, W=7.0, H=2.8, parts=("R", "L", "C"), labs=None, src=True):
    """직렬 회로: 왼쪽 교류 전원, 위쪽 선에 parts 차례로, 오른쪽·아래로 돌아옴.
    반환 dict: g, src, el{이름}, lab{이름}, slot{이름: (xa, xb)}, yt, yb, x0, x1."""
    o = PT3(o); x0, x1 = o[0] - W / 2, o[0] + W / 2; yt, yb = o[1] + H / 2, o[1] - H / 2
    labs = labs or {}
    g = VGroup(); D = dict(el={}, lab={}, slot={}, yt=yt, yb=yb, x0=x0, x1=x1)
    s = acsrc((x0, o[1]), YEL, .5); D["src"] = s
    g.add(s, wire((x0, o[1] + .5), (x0, yt)), wire((x0, o[1] - .5), (x0, yb)))
    xs = np.linspace(x0 + .5, x1 - .3, len(parts) + 1)
    g.add(wire((x0, yt), (xs[0], yt)))
    for i, k in enumerate(parts):
        a, b = xs[i] + .15, xs[i + 1] - .15
        g.add(wire((xs[i], yt), (a, yt)), wire((b, yt), (xs[i + 1], yt)))
        e = element(k, (a, yt), (b, yt), ELC[k]); D["el"][k] = e; D["slot"][k] = (a, b)
        D["lab"][k] = tex(labs.get(k, k), 40, ELC[k]).next_to(e, UP, .3)
        g.add(e)
    g.add(wire((xs[-1], yt), (x1, yt)), wire((x1, yt), (x1, yb)), wire((x1, yb), (x0, yb)))
    D["wires"] = g; D["g"] = VGroup(g, *D["lab"].values())
    return D


def obrace(D, names, c=YEL, txt=r"v_o"):
    grp = VGroup(*[D["el"][n] for n in names])
    b = Brace(grp, DOWN, buff=.3, color=c)
    return VGroup(b, tex(txt, 38, c).next_to(b, DOWN, .1))


def short_at(D, k, c=GRN):
    a, b = D["slot"][k]
    return VGroup(Line((a, D["yt"], 0), (b, D["yt"], 0), color=c, stroke_width=8), kr("단락", 28, c).move_to(((a + b) / 2, D["yt"] - .5, 0)))


def open_at(D, k, c=RED):
    a, b = D["slot"][k]; m = (a + b) / 2
    return VGroup(Line((a, D["yt"], 0), (m - .3, D["yt"], 0), color=INK, stroke_width=4), Line((m + .3, D["yt"], 0), (b, D["yt"], 0), color=INK, stroke_width=4),
                  term((m - .3, D["yt"]), c), term((m + .3, D["yt"]), c), kr("개방", 28, c).move_to((m, D["yt"] - .5, 0)))


def hmag(kind, w, Q=1.0):
    """|H| (w = ω/ω_c 또는 ω/ω0)."""
    if kind == "LP": return 1 / np.sqrt(1 + w ** 2)
    if kind == "HP": return w / np.sqrt(1 + w ** 2)
    x = Q * (w - 1 / w)
    if kind == "BP": return 1 / np.sqrt(1 + x ** 2)
    return abs(x) / np.sqrt(1 + x ** 2)


FNAME = {"LP": "저역통과", "HP": "고역통과", "BP": "대역통과", "BR": "대역저지"}
FCOL = {"LP": BLU, "HP": GRN, "BP": YEL, "BR": RED}


def mini(kind, c=None, W=2.4, H=1.3, Q=1.2, name=True):
    """작은 크기 응답 아이콘 (log 축)."""
    c = c or FCOL[kind]
    ax = VGroup(Line(ORIGIN, RIGHT * W, color=MUTE, stroke_width=3), Line(ORIGIN, UP * H, color=MUTE, stroke_width=3))
    xs = np.linspace(-1.5, 1.5, 120)
    pts = [np.array([(x + 1.5) / 3 * W, hmag(kind, 10 ** x, Q) * H * .9, 0]) for x in xs]
    cv = VMobject(color=c, stroke_width=6).set_points_smoothly(pts)
    g = VGroup(ax, cv)
    if name:
        g.add(kr(FNAME[kind], 28, c).next_to(ax, DOWN, .15))
    return g


class LAx(Axes):
    """log 축(x = log10 비율). y 축을 왼쪽 끝에 두려고 내부 좌표는 0..폭, c2p/plot 은 원래 x 로 받는다."""
    def __init__(self, x0, **k):
        super().__init__(**k); self.x0 = x0

    def c2p(self, x, y):
        return self.coords_to_point(x - self.x0, y)

    def plot(self, f, x_range=None, **k):
        a, b, st = x_range
        return super().plot(lambda u: f(u + self.x0), x_range=[a - self.x0, b - self.x0, st], **k)


def logax(W=7.0, H=3.4, xr=(-1.5, 1.5), ylab=r"|H|", xlab=r"\omega"):
    ax = LAx(xr[0], x_range=[0, xr[1] - xr[0], 0.5], y_range=[0, 1.15, 0.5], x_length=W, y_length=H, tips=False,
             axis_config=dict(color=MUTE, stroke_width=3, include_ticks=False))
    lab = VGroup(tex(ylab, 34, MUTE).next_to(ax.y_axis, UP, .1), tex(xlab, 34, MUTE).next_to(ax.x_axis, RIGHT, .1))
    return ax, lab


def curve(ax, kind, c, Q=1.0, K=1.0, sh=0.0, xr=(-1.5, 1.5)):
    return ax.plot(lambda x: K * hmag(kind, 10 ** (x - sh), Q), x_range=[xr[0], xr[1], 0.01], color=c, stroke_width=6)


def hline(ax, y, c=MUTE, txt=None, xr=(-1.5, 1.5)):
    l = DashedLine(ax.c2p(xr[0], y), ax.c2p(xr[1], y), color=c, stroke_width=3, dash_length=.12)
    if txt:
        return VGroup(l, tex(txt, 30, c).next_to(l, LEFT, .12))
    return l


def vmark(ax, x, y, c=YEL, txt=None, below=True):
    l = DashedLine(ax.c2p(x, 0), ax.c2p(x, y), color=c, stroke_width=3, dash_length=.1)
    d = Dot(ax.c2p(x, y), radius=.09, color=c)
    g = VGroup(l, d)
    if txt:
        g.add(tex(txt, 32, c).next_to(ax.c2p(x, 0), DOWN, .15))
    return g


def big(s, c=YEL, size=80, buff=.35):
    return card(tex(s, size, c), c, buff)


def prob(lines, c=YEL, title="시험 문제"):
    body = VGroup(*[l if isinstance(l, Mobject) else kr(l, 36, INK) for l in lines]).arrange(DOWN, buff=.25)
    return card(VGroup(kr(title, 30, c), body).arrange(DOWN, buff=.3), c, .35)


def goal_card():
    return prob([VGroup(tex(r"1\,\mathrm{kHz}", 44, YEL), kr("~", 36, INK), tex(r"10\,\mathrm{kHz}", 44, YEL), kr("만 통과", 36, INK)).arrange(RIGHT, buff=.15),
                 VGroup(tex(r"C = 1\,\mu\mathrm{F}", 44, ORG)),
                 VGroup(tex(r"L = ?", 52, GRN), tex(r"R = ?", 52, BLU)).arrange(RIGHT, buff=.8)])


def wsine(p, cyc, c, L=2.2, A=.35):
    return sine(p, A, cyc, L, c, f=np.sin, sw=4)


# ================= 인트로 =================
def four_icons():
    g = VGroup(*[card(mini(k, W=2.0, H=1.05), FCOL[k], .2) for k in ("BP", "BR", "LP", "HP")])
    return g.arrange_in_grid(2, 2, buff=.25)


class Hook(Scene):
    def construct(self):
        D = sloop(LEFT * 3.0 + DOWN * .1, 6.4, 3.0)
        beat(self, FadeIn(D["wires"]), *[FadeIn(l) for l in D["lab"].values()], t=.7, rt=.4)
        icons = four_icons().scale(.95).move_to(RIGHT * 4.3 + DOWN * .1)
        br = None
        for names, ic in ((("R",), icons[0]), (("L", "C"), icons[1]), (("C",), icons[2]), (("L",), icons[3])):
            nb = obrace(D, names, FCOL[["BP", "BR", "LP", "HP"][list(icons).index(ic)]])
            if br is None:
                beat(self, FadeIn(nb), FadeIn(ic, shift=UP * .2), t=.85, rt=.35)
            else:
                beat(self, ReplacementTransform(br, nb), FadeIn(ic, shift=UP * .2), t=.85, rt=.35)
            br = nb
        fill(self, icons)


class Goal(Scene):
    def construct(self):
        p = goal_card().scale(.9).move_to(LEFT * 3.4)
        beat(self, FadeIn(p, shift=UP * .2), t=1.0, rt=.5)
        ax, lab = logax(5.2, 2.8, (-1.0, 2.0), xlab=r"f")
        ax.move_to(RIGHT * 3.4 + DOWN * .2)
        lab = VGroup(tex(r"|H|", 34, MUTE).next_to(ax.y_axis, UP, .1), tex("f", 34, MUTE).next_to(ax.x_axis, RIGHT, .1))
        beat(self, Create(ax), FadeIn(lab), t=.6, rt=.4)
        band = Polygon(ax.c2p(0, 0), ax.c2p(0, 1.1), ax.c2p(1, 1.1), ax.c2p(1, 0), stroke_width=0, fill_color=YEL, fill_opacity=.18)
        k1 = tex(r"1\,\mathrm{k}", 30, YEL).next_to(ax.c2p(0, 0), DOWN, .15); k2 = tex(r"10\,\mathrm{k}", 30, YEL).next_to(ax.c2p(1, 0), DOWN, .15)
        beat(self, FadeIn(band), FadeIn(k1), FadeIn(k2), t=.8, rt=.4)
        cv = ax.plot(lambda x: hmag("BP", 10 ** (x - .5), .3514), x_range=[-1, 2, .01], color=YEL, stroke_width=6)
        beat(self, Create(cv), t=1.0, rt=.8)
        fill(self, p)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "필터 판별", BLU), ("2", "1차 설계", PUR), ("3", "대역통과 Q", GRN), ("4", "설계 문제", ORG), ("5", "시험 함정", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=.9, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=.9, rt=.7)
        fill(self, cards)


# ================= STEP 1 회로만 보고 판별 =================
def waxis(y=-1.6):
    a = Arrow(LEFT * 5.5 + UP * y, RIGHT * 5.5 + UP * y, buff=0, color=MUTE, stroke_width=4, max_tip_length_to_length_ratio=.03)
    return VGroup(a, tex(r"\omega", 40, MUTE).next_to(a, RIGHT, .1))


class J1(Scene):
    def construct(self):
        self.add(step_tag(1))
        ax = waxis(-1.0); beat(self, GrowArrow(ax[0]), FadeIn(ax[1]), t=.7, rt=.5)
        z = card(tex(r"\omega = 0", 48, BLU), BLU, .2).move_to(LEFT * 4.2 + UP * .6)
        i = card(tex(r"\omega = \infty", 48, RED), RED, .2).move_to(RIGHT * 4.2 + UP * .6)
        beat(self, FadeIn(z, shift=RIGHT * .3), t=.8, rt=.4)
        beat(self, FadeIn(i, shift=LEFT * .3), t=.8, rt=.4)
        c = card(kr("계산 없이 필터 종류 맞히기", 40, YEL), YEL, .25).move_to(UP * 2.4)
        beat(self, FadeIn(c), t=.8, rt=.4)
        el = VGroup(coil(LEFT * 1.3 + UP * .6, LEFT * .1 + UP * .6, GRN), capacitor(RIGHT * .2 + UP * .6, RIGHT * 1.4 + UP * .6, ORG)[0])
        beat(self, FadeIn(el), t=.6, rt=.4)
        fill(self, VGroup(z, i))


def two_el(y=.3):
    L = coil(LEFT * 4.6 + UP * y, LEFT * 1.6 + UP * y, GRN); C = capacitor(RIGHT * 1.6 + UP * y, RIGHT * 4.6 + UP * y, ORG)[0]
    return L, C


def morph(sc, w, Lres, Cres, rt=.5):
    L, C = two_el()
    beat(sc, FadeIn(L), FadeIn(C), FadeIn(kr("인덕터", 32, GRN).next_to(L, UP, .5)), FadeIn(kr("커패시터", 32, ORG).next_to(C, UP, .5)), t=.8, rt=.4)
    out = []
    for m, res, x in ((L, Lres, -3.1), (C, Cres, 3.1)):
        if res == "short":
            n = VGroup(Line(LEFT * 1.5 + RIGHT * x + UP * .3, RIGHT * 1.5 + RIGHT * x + UP * .3, color=GRN, stroke_width=9), kr("단락", 44, GRN).move_to(RIGHT * x + DOWN * .9))
        else:
            n = VGroup(Line(LEFT * 1.5 + RIGHT * x + UP * .3, LEFT * .35 + RIGHT * x + UP * .3, color=INK, stroke_width=5), Line(RIGHT * .35 + RIGHT * x + UP * .3, RIGHT * 1.5 + RIGHT * x + UP * .3, color=INK, stroke_width=5),
                       term(LEFT * .35 + RIGHT * x + UP * .3, RED), term(RIGHT * .35 + RIGHT * x + UP * .3, RED), kr("개방", 44, RED).move_to(RIGHT * x + DOWN * .9))
        beat(sc, ReplacementTransform(m, n[:-1]), FadeIn(n[-1], shift=UP * .2), t=1.0, rt=rt); out.append(n)
    return out


class J2(Scene):
    def construct(self):
        self.add(step_tag(1))
        h = card(tex(r"\omega = 0", 56, BLU), BLU, .2).move_to(UP * 2.5); beat(self, FadeIn(h), t=.5, rt=.3)
        o = morph(self, 0, "short", "open")
        z = VGroup(tex(r"Z_L = j\omega L \to 0", 34, GRN).move_to(LEFT * 3.1 + DOWN * 2.1), tex(r"Z_C = \tfrac{1}{j\omega C} \to \infty", 34, ORG).move_to(RIGHT * 3.1 + DOWN * 2.1))
        beat(self, FadeIn(z), t=.6, rt=.3)
        fill(self, VGroup(*o))


class J3(Scene):
    def construct(self):
        self.add(step_tag(1))
        h = card(tex(r"\omega = \infty", 56, RED), RED, .2).move_to(UP * 2.5); beat(self, FadeIn(h), t=.5, rt=.3)
        o = morph(self, 0, "open", "short")
        c = card(kr("0일 때와 정반대", 32, YEL), YEL, .18).move_to(DOWN * 2.2); beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, VGroup(*o))


def judge_row(lo, hi, kind):
    ok = lambda b: kr("살아 있음" if b else "0", 30, GRN if b else RED)
    g = VGroup(card(ok(lo), GRN if lo else RED, .15), card(ok(hi), GRN if hi else RED, .15),
               Arrow(LEFT * .5, RIGHT * .5, color=INK, stroke_width=5, buff=0), mini(kind, W=1.8, H=.9, name=False), kr(FNAME[kind], 40, FCOL[kind]))
    for k, x in zip(g, (-4.6, -2.2, -.5, 1.2, 4.2)):
        k.move_to(RIGHT * x)
    return g


def judge_head():
    return VGroup(tex(r"\omega = 0", 38, BLU).move_to(LEFT * 4.6), tex(r"\omega = \infty", 38, RED).move_to(LEFT * 2.2), kr("결과", 30, MUTE).move_to(RIGHT * 2.7))


class J4(Scene):
    def construct(self):
        self.add(step_tag(1))
        hd = judge_head().move_to(UP * 2.3 + RIGHT * .2); beat(self, FadeIn(hd), t=.6, rt=.3)
        for y, (lo, hi, k) in ((.9, (1, 0, "LP")), (-.9, (0, 1, "HP"))):
            r = judge_row(lo, hi, k).shift(UP * y)
            beat(self, FadeIn(r[:2]), t=.6, rt=.3)
            beat(self, GrowArrow(r[2]), Create(r[3]), FadeIn(r[4], shift=LEFT * .2), t=1.0, rt=.6)
        fill(self, hd)


class J5(Scene):
    def construct(self):
        self.add(step_tag(1))
        hd = judge_head().move_to(UP * 2.3 + RIGHT * .2); self.add(hd)
        for y, (lo, hi, k) in ((.9, (0, 0, "BP")), (-.9, (1, 1, "BR"))):
            r = judge_row(lo, hi, k).shift(UP * y)
            beat(self, FadeIn(r[:2]), t=.6, rt=.3)
            beat(self, GrowArrow(r[2]), Create(r[3]), FadeIn(r[4], shift=LEFT * .2), t=1.0, rt=.6)
        fill(self, hd)


class J6(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = sloop(LEFT * 2.6 + DOWN * .2, 6.6, 3.0); self.add(D["g"])
        b1 = obrace(D, ("R",), YEL); i1 = card(mini("BP"), YEL, .2).move_to(RIGHT * 4.6 + UP * 1.2)
        beat(self, FadeIn(b1), FadeIn(i1, shift=LEFT * .2), t=1.4, rt=.5)
        b2 = obrace(D, ("L", "C"), RED); i2 = card(mini("BR"), RED, .2).move_to(RIGHT * 4.6 + DOWN * 1.4)
        beat(self, ReplacementTransform(b1, b2), FadeIn(i2, shift=LEFT * .2), t=1.4, rt=.5)
        c = card(kr("출력 자리만 바꿨다", 30, INK), INK, .15).to_edge(DOWN, buff=.3).shift(LEFT * 2.6)
        beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, VGroup(i1, i2))


# ================= STEP 2 1차 필터 설계 =================
class F1(Scene):
    def construct(self):
        self.add(step_tag(2))
        L = coil(LEFT * 4.8 + UP * .6, LEFT * 2.0 + UP * .6, GRN); C = capacitor(RIGHT * 2.0 + UP * .6, RIGHT * 4.8 + UP * .6, ORG)[0]
        beat(self, FadeIn(L), FadeIn(kr("L", 44, GRN).next_to(L, UP, .4)), t=.6, rt=.3)
        hs = wsine(LEFT * 3.4 + DOWN * 1.0, 6, GRN, 2.8); beat(self, Create(hs), FadeIn(kr("고주파를 붙잡는다", 34, GRN).next_to(hs, DOWN, .3)), t=1.2, rt=.6)
        beat(self, FadeIn(C), FadeIn(kr("C", 44, ORG).next_to(C, UP, .4)), t=.6, rt=.3)
        ls = wsine(RIGHT * 3.4 + DOWN * 1.0, 1, ORG, 2.8); beat(self, Create(ls), FadeIn(kr("저주파를 붙잡는다", 34, ORG).next_to(ls, DOWN, .3)), t=1.2, rt=.6)
        fill(self, VGroup(hs, ls))


class F2(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = sloop(LEFT * 2.8 + DOWN * .1, 5.6, 3.0, ("R", "C")); beat(self, FadeIn(D["g"]), t=.5, rt=.3)
        b = obrace(D, ("C",), BLU); i1 = card(mini("LP"), BLU, .2).move_to(RIGHT * 4.3 + UP * 1.3)
        beat(self, FadeIn(b), FadeIn(i1, shift=LEFT * .2), t=1.2, rt=.5)
        b2 = obrace(D, ("R",), GRN); i2 = card(mini("HP"), GRN, .2).move_to(RIGHT * 4.3 + DOWN * 1.1)
        beat(self, ReplacementTransform(b, b2), FadeIn(i2, shift=LEFT * .2), t=1.2, rt=.5)
        e = card(tex(r"v_R + v_C = v_i", 44, YEL), YEL, .18).to_edge(DOWN, buff=.25).shift(LEFT * 2.8)
        beat(self, FadeIn(e, shift=UP * .2), t=.8, rt=.4)
        fill(self, e)


class F3(Scene):
    def construct(self):
        self.add(step_tag(2))
        a = card(VGroup(kr("RC", 30, ORG), tex(r"\omega_c = \frac{1}{RC}", 56, ORG)).arrange(DOWN, buff=.15), ORG, .25).move_to(LEFT * 4.4 + UP * 1.2)
        b = card(VGroup(kr("RL", 30, GRN), tex(r"\omega_c = \frac{R}{L}", 56, GRN)).arrange(DOWN, buff=.15), GRN, .25).move_to(LEFT * 4.4 + DOWN * 1.4)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        beat(self, FadeIn(b, shift=UP * .2), t=.8, rt=.4)
        ax, lab = logax(6.0, 3.2); VGroup(ax, lab).move_to(RIGHT * 2.6 + DOWN * .1)
        cv = curve(ax, "LP", BLU)
        beat(self, Create(ax), FadeIn(lab), Create(cv), t=1.0, rt=.7)
        h = hline(ax, 1 / np.sqrt(2), YEL, r"0.707"); m = vmark(ax, 0, 1 / np.sqrt(2), YEL, r"\omega_c")
        beat(self, Create(h), FadeIn(m), t=1.0, rt=.5)
        fill(self, m)


def f4card():
    return prob([tex(r"C = 1\,\mu\mathrm{F}", 50, ORG), VGroup(kr("차단 주파수", 34, INK), tex(r"3\,\mathrm{kHz}", 50, YEL)).arrange(RIGHT, buff=.25),
                 tex(r"R = \;?", 60, BLU)], YEL, "저역통과 필터 설계")


class F4(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = sloop(LEFT * 3.6 + DOWN * .2, 5.0, 2.8, ("R", "C"), labs={"R": "R=?", "C": r"1\,\mu\mathrm{F}"}); beat(self, FadeIn(D["g"]), FadeIn(obrace(D, ("C",), BLU)), t=.8, rt=.4)
        p = f4card().move_to(RIGHT * 3.4)
        beat(self, FadeIn(p, shift=UP * .2), t=1.0, rt=.5)
        fill(self, p)


class F5(Scene):
    def construct(self):
        self.add(step_tag(2))
        w = tex(r"R = \frac{1}{3000 \times 10^{-6}} = 333\,\Omega", 54, MUTE).move_to(UP * 1.9)
        beat(self, Write(w), t=1.2, rt=.8)
        x = cross(w); beat(self, Create(x), FadeIn(kr("함정!", 40, RED).next_to(w, RIGHT, .3).shift(DOWN * .1)), t=.8, rt=.4)
        k = card(VGroup(tex(r"\omega_c", 56, YEL), tex(r"= 2\pi f_c", 56, INK)).arrange(RIGHT, buff=.15), YEL, .3).move_to(DOWN * .5)
        beat(self, FadeIn(k, scale=1.2), t=.9, rt=.4)
        n = VGroup(kr("공식은 각주파수 rad/s", 30, MUTE), kr("문제는 Hz", 30, MUTE)).arrange(RIGHT, buff=.8).move_to(DOWN * 2.2)
        beat(self, FadeIn(n), t=.6, rt=.3)
        fill(self, k)


class F6(Scene):
    def construct(self):
        self.add(step_tag(2))
        e = tex(r"R = \frac{1}{2\pi \times 3000 \times 10^{-6}}", 56, INK).move_to(UP * 1.7)
        e[0][4:6].set_color(YEL) if len(e[0]) > 6 else None
        beat(self, Write(e), t=1.2, rt=.8)
        a = big(r"R = 53\,\Omega", YEL, 96).move_to(DOWN * .6); beat(self, FadeIn(a, scale=1.2), t=1.0, rt=.5)
        c = card(kr("시험 최다 실수", 30, RED), RED, .15).next_to(a, DOWN, .35); beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, a)


# ================= STEP 3 대역통과 ω0·β·Q =================
def bp_axes(W=7.0, H=3.4, Q=2.0, c=YEL):
    ax, lab = logax(W, H, (-1.0, 1.0)); cv = ax.plot(lambda x: hmag("BP", 10 ** x, Q), x_range=[-1, 1, .005], color=c, stroke_width=6)
    return ax, lab, cv


def bp_cut(Q):
    r = 1 / (2 * Q); return -r + np.sqrt(1 + r * r), r + np.sqrt(1 + r * r)


class B1(Scene):
    def construct(self):
        self.add(step_tag(3))
        ax, lab, cv = bp_axes(6.2, 3.2); VGroup(ax, lab, cv).move_to(LEFT * 2.6 + DOWN * .4)
        beat(self, Create(ax), FadeIn(lab), Create(cv), t=.9, rt=.6)
        items = [(r"\omega_0", "중심 주파수", YEL), (r"\beta", "대역폭", GRN), (r"Q", "뾰족함", PUR)]
        cs = VGroup(*[card(VGroup(tex(s, 50, c), kr(t, 30, INK)).arrange(RIGHT, buff=.3), c, .2) for s, t, c in items]).arrange(DOWN, buff=.3, aligned_edge=LEFT).move_to(RIGHT * 4.3)
        m0 = vmark(ax, 0, 1, YEL)
        l1, l2 = bp_cut(2.0); y = 1 / np.sqrt(2)
        bw = DoubleArrow(ax.c2p(np.log10(l1), y), ax.c2p(np.log10(l2), y), buff=0, color=GRN, stroke_width=5, tip_length=.2)
        beat(self, FadeIn(cs[0], shift=LEFT * .2), FadeIn(m0), t=.8, rt=.4)
        beat(self, FadeIn(cs[1], shift=LEFT * .2), GrowFromCenter(bw), t=.8, rt=.4)
        beat(self, FadeIn(cs[2], shift=LEFT * .2), Indicate(cv, color=PUR, scale_factor=1.02), t=.8, rt=.5)
        fill(self, cs)


class B2(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = sloop(LEFT * 3.0 + UP * .6, 6.0, 2.4); self.add(D["g"])
        e = tex(r"j\omega L + \frac{1}{j\omega C} = 0", 48, INK).move_to(RIGHT * 3.6 + UP * 1.6)
        beat(self, Indicate(D["el"]["L"], color=GRN), Indicate(D["el"]["C"], color=ORG), Write(e), t=1.2, rt=.8)
        c = card(kr("L과 C가 상쇄", 30, GRN), GRN, .15).next_to(e, DOWN, .3); beat(self, FadeIn(c), t=.6, rt=.3)
        a = big(r"\omega_0 = \frac{1}{\sqrt{LC}}", YEL, 70).move_to(LEFT * 1.6 + DOWN * 2.1); beat(self, FadeIn(a, scale=1.2), t=1.0, rt=.5)
        r = card(VGroup(tex("R", 44, BLU), kr("과 무관", 34, INK)).arrange(RIGHT, buff=.15), BLU, .2).next_to(a, RIGHT, .6)
        beat(self, FadeIn(r, shift=LEFT * .2), t=.7, rt=.3)
        fill(self, a)


class B3(Scene):
    def construct(self):
        self.add(step_tag(3))
        ax, lab, cv = bp_axes(7.0, 3.4); VGroup(ax, lab, cv).move_to(LEFT * 1.8 + DOWN * .2); self.add(ax, lab, cv)
        l1, l2 = bp_cut(2.0); y = 1 / np.sqrt(2)
        h = hline(ax, y, MUTE, r"0.707", (-1, 1)); beat(self, Create(h), t=.6, rt=.4)
        m1 = vmark(ax, np.log10(l1), y, GRN, r"\omega_{c1}"); m2 = vmark(ax, np.log10(l2), y, GRN, r"\omega_{c2}")
        beat(self, FadeIn(m1), t=.6, rt=.3); beat(self, FadeIn(m2), t=.6, rt=.3)
        bw = DoubleArrow(ax.c2p(np.log10(l1), y + .12), ax.c2p(np.log10(l2), y + .12), buff=0, color=GRN, stroke_width=5, tip_length=.2)
        beat(self, GrowFromCenter(bw), FadeIn(tex(r"\beta", 44, GRN).next_to(bw, UP, .1)), t=.7, rt=.4)
        e = card(VGroup(tex(r"\beta = \omega_{c2} - \omega_{c1}", 44, INK), tex(r"= \frac{R}{L}", 56, GRN)).arrange(DOWN, buff=.2), GRN, .25).move_to(RIGHT * 4.6 + UP * .3)
        beat(self, FadeIn(e, shift=LEFT * .2), t=1.0, rt=.5)
        fill(self, e, GRN)


class B4(Scene):
    def construct(self):
        self.add(step_tag(3))
        q = big(r"Q = \frac{\omega_0}{\beta}", PUR, 70).move_to(LEFT * 4.2 + UP * .6); beat(self, FadeIn(q, scale=1.2), t=.9, rt=.4)
        ax, lab = logax(6.4, 3.4, (-1, 1)); VGroup(ax, lab).move_to(RIGHT * 2.4 + DOWN * .2)
        c1 = ax.plot(lambda x: hmag("BP", 10 ** x, .7), x_range=[-1, 1, .005], color=MUTE, stroke_width=5)
        c2 = ax.plot(lambda x: hmag("BP", 10 ** x, 5), x_range=[-1, 1, .003], color=PUR, stroke_width=6)
        beat(self, Create(ax), FadeIn(lab), Create(c1), FadeIn(tex("Q=0.7", 30, MUTE).next_to(ax.c2p(-.75, .45), UP, .1)), t=1.0, rt=.6)
        beat(self, Create(c2), FadeIn(tex("Q=5", 34, PUR).next_to(ax.c2p(.12, .95), RIGHT, .1)), t=1.0, rt=.6)
        c = card(kr("클수록 좁고 뾰족", 32, PUR), PUR, .15).next_to(q, DOWN, .5); beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, c2, PUR)


class B5(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = sloop(UP * 1.6, 7.0, 1.8, labs={"R": r"100\,\Omega", "L": r"50\,\mathrm{mH}", "C": r"0.2\,\mu\mathrm{F}"})
        beat(self, FadeIn(D["g"]), t=.8, rt=.4)
        rs = VGroup(info("중심", r"\omega_0 = 10^4", YEL, 48), info("대역폭", r"\beta = 2000", GRN, 48), info("Q", r"Q = 5", PUR, 60)).arrange(RIGHT, buff=.35).move_to(DOWN * 1.7)
        for r in rs:
            beat(self, FadeIn(r, shift=UP * .2), t=.9, rt=.4)
        fill(self, rs[2], PUR)


class B6(Scene):
    def construct(self):
        self.add(step_tag(3))
        ax, lab = logax(7.6, 3.0, (-.13, .13)); VGroup(ax, lab).move_to(UP * .5)
        cv = ax.plot(lambda x: hmag("BP", 10 ** x, 5), x_range=[-.13, .13, .002], color=YEL, stroke_width=6)
        beat(self, Create(ax), FadeIn(lab), Create(cv), t=.8, rt=.6)
        y = 1 / np.sqrt(2)
        m1 = vmark(ax, np.log10(.90499), y, GRN, r"9050"); m2 = vmark(ax, np.log10(1.10499), y, GRN, r"11050"); m0 = VGroup(vmark(ax, 0, 1, YEL), tex(r"\omega_0 = 10^4", 34, YEL).next_to(ax.c2p(0, 1), UP, .15))
        beat(self, FadeIn(m1), FadeIn(m2), t=.8, rt=.4)
        beat(self, FadeIn(m0), t=.5, rt=.3)
        e = card(tex(r"9050 \times 11050 = 10^8 = \omega_0^{\,2}", 46, YEL), YEL, .2).move_to(DOWN * 2.6)
        beat(self, FadeIn(e, shift=UP * .2), t=1.0, rt=.5)
        fill(self, e)


# ================= STEP 4 처음 문제 =================
class D1(Scene):
    def construct(self):
        self.add(step_tag(4))
        p = goal_card().move_to(LEFT * 2.8); beat(self, FadeIn(p, shift=UP * .2), t=1.0, rt=.5)
        D = sloop(RIGHT * 3.6 + DOWN * .1, 4.6, 2.6, labs={"R": "R=?", "L": "L=?", "C": r"1\,\mu\mathrm{F}"}); beat(self, FadeIn(D["g"]), FadeIn(obrace(D, ("R",), YEL)), t=1.0, rt=.5)
        fill(self, p)


class D2(Scene):
    def construct(self):
        self.add(step_tag(4))
        w = tex(r"\frac{1\,\mathrm{k} + 10\,\mathrm{k}}{2} = 5.5\,\mathrm{kHz}", 54, MUTE).move_to(UP * 2.0)
        beat(self, Write(w), t=1.0, rt=.6); beat(self, Create(cross(w)), t=.6, rt=.3)
        e = tex(r"f_0 = \sqrt{f_{c1} f_{c2}} = \sqrt{1\,\mathrm{k} \times 10\,\mathrm{k}}", 52, INK).move_to(UP * .2)
        beat(self, Write(e), t=1.2, rt=.8)
        a = big(r"f_0 = 3162\,\mathrm{Hz}", YEL, 80).move_to(DOWN * 1.9); beat(self, FadeIn(a, scale=1.2), t=1.0, rt=.5)
        fill(self, a)


class D3(Scene):
    def construct(self):
        self.add(step_tag(4))
        e1 = tex(r"\omega_0^{\,2} = \frac{1}{LC}", 56, INK).move_to(UP * 2.0 + LEFT * 3.0); beat(self, Write(e1), t=.9, rt=.6)
        ar = Arrow(e1.get_right(), e1.get_right() + RIGHT * 1.2, buff=.2, color=YEL, stroke_width=5)
        e2 = tex(r"L = \frac{1}{\omega_0^{\,2} C}", 56, GRN).next_to(ar, RIGHT, .2); beat(self, GrowArrow(ar), Write(e2), t=1.0, rt=.6)
        e3 = tex(r"= \frac{1}{(2\pi \cdot 3162)^2 \times 10^{-6}}", 48, INK).move_to(UP * .1); beat(self, Write(e3), t=1.0, rt=.7)
        a = big(r"L = 2.53\,\mathrm{mH}", GRN, 84).move_to(DOWN * 2.0); beat(self, FadeIn(a, scale=1.2), t=.9, rt=.4)
        fill(self, a, GRN)


class D4(Scene):
    def construct(self):
        self.add(step_tag(4))
        e1 = tex(r"\beta = 2\pi \times 9000", 54, GRN).move_to(UP * 2.0); beat(self, Write(e1), t=.9, rt=.6)
        e2 = tex(r"\beta = \frac{R}{L} \;\Rightarrow\; R = \beta L", 54, INK).move_to(UP * .4); beat(self, Write(e2), t=1.0, rt=.6)
        e3 = tex(r"= 2\pi \times 9000 \times 2.53\,\mathrm{mH}", 46, MUTE).move_to(DOWN * .8); beat(self, FadeIn(e3), t=.8, rt=.4)
        a = big(r"R = 143\,\Omega", BLU, 84).move_to(DOWN * 2.3); beat(self, FadeIn(a, scale=1.2), t=.9, rt=.4)
        fill(self, a, BLU)


class D5(Scene):
    def construct(self):
        self.add(step_tag(4))
        ax, lab = logax(6.4, 3.2, (-1.0, 2.0), xlab="f"); VGroup(ax, lab).move_to(LEFT * 2.4 + DOWN * .3)
        cv = ax.plot(lambda x: hmag("BP", 10 ** (x - .5), .3514), x_range=[-1, 2, .01], color=YEL, stroke_width=6)
        beat(self, Create(ax), FadeIn(lab), Create(cv), t=1.0, rt=.7)
        y = 1 / np.sqrt(2)
        m1 = vmark(ax, 0, y, GRN, r"1\,\mathrm{k}\,\checkmark"); m2 = vmark(ax, 1, y, GRN, r"10\,\mathrm{k}\,\checkmark")
        beat(self, Create(hline(ax, y, MUTE, None, (-1, 2))), FadeIn(m1), FadeIn(m2), t=1.0, rt=.5)
        ans = card(VGroup(kr("정답", 30, YEL), tex(r"L = 2.53\,\mathrm{mH}", 48, GRN), tex(r"R = 143\,\Omega", 48, BLU), tex(r"Q = 0.35", 40, PUR)).arrange(DOWN, buff=.2), YEL, .3).move_to(RIGHT * 4.4)
        beat(self, FadeIn(ans, shift=LEFT * .2), t=1.0, rt=.5)
        fill(self, ans)


# ================= STEP 5 시험 함정 셋 =================
def trap(n):
    return card(kr(f"함정 {n}", 32, RED), RED, .15).to_corner(UL, buff=.4).shift(DOWN * .75)


class P1(Scene):
    def construct(self):
        self.add(step_tag(5)); beat(self, FadeIn(trap(1)), t=.4, rt=.3)
        ax, lab = logax(6.6, 3.4, (-1, 1)); VGroup(ax, lab).move_to(LEFT * 1.6 + DOWN * .3)
        cv = ax.plot(lambda x: hmag("BR", 10 ** x, 2.5), x_range=[-1, 1, .002], color=RED, stroke_width=6)
        beat(self, Create(ax), FadeIn(lab), Create(cv), FadeIn(kr("대역저지", 34, RED).next_to(ax, UP, .2)), t=1.2, rt=.8)
        m = vmark(ax, 0, 0, YEL, r"\omega_0"); d = Dot(ax.c2p(0, 0), radius=.14, color=YEL)
        beat(self, FadeIn(m), FadeIn(d, scale=1.5), t=.7, rt=.4)
        c = card(VGroup(kr("중심 주파수에서", 30, INK), VGroup(kr("최대", 40, MUTE), kr("→", 40, INK), tex(r"|H| = 0", 50, YEL)).arrange(RIGHT, buff=.2)).arrange(DOWN, buff=.2), YEL, .25).move_to(RIGHT * 4.5)
        beat(self, FadeIn(c, shift=LEFT * .2), t=.9, rt=.4)
        fill(self, d)


def qcards():
    a = card(VGroup(kr("직렬 RLC", 34, BLU), tex(r"Q = \frac{1}{R}\sqrt{\frac{L}{C}}", 56, BLU), VGroup(tex("R", 40, YEL), tex(r"\downarrow", 40, YEL), kr("일수록 뾰족", 30, INK)).arrange(RIGHT, buff=.12)).arrange(DOWN, buff=.25), BLU, .3)
    b = card(VGroup(kr("병렬 RLC", 34, GRN), tex(r"Q = R\sqrt{\frac{C}{L}}", 56, GRN), VGroup(tex("R", 40, YEL), tex(r"\uparrow", 40, YEL), kr("일수록 뾰족", 30, INK)).arrange(RIGHT, buff=.12)).arrange(DOWN, buff=.25), GRN, .3)
    return a, b


class P2(Scene):
    def construct(self):
        self.add(step_tag(5)); self.add(trap(2))
        a, b = qcards(); a.move_to(LEFT * 3.3 + DOWN * .1); b.move_to(RIGHT * 3.3 + DOWN * .1)
        beat(self, FadeIn(a, shift=UP * .2), t=1.4, rt=.5)
        beat(self, FadeIn(b, shift=UP * .2), t=1.4, rt=.5)
        v = kr("정반대!", 44, RED).move_to(UP * 2.6); beat(self, FadeIn(v, scale=1.3), t=.6, rt=.3)
        fill(self, VGroup(a, b), RED)


def hp_loop(o, s=1.0, load=False):
    """RL 고역통과: 교류전원 - R(위) - L(오른쪽 세로, 출력) [- R_L 병렬]."""
    o = PT3(o); x0, xm, x1 = o[0] - 2.6 * s, o[0] + .6 * s, o[0] + 2.6 * s; yt, yb = o[1] + 1.4 * s, o[1] - 1.4 * s
    src = acsrc((x0, o[1]), YEL, .5)
    R = resistor((x0 + .5, yt), (xm - .3, yt), BLU); L = coil((xm, yt - .3), (xm, yb + .3), GRN)
    w = VGroup(wire((x0, o[1] + .5), (x0, yt)), wire((x0, yt), (x0 + .5, yt)), wire((xm - .3, yt), (xm, yt)), wire((xm, yt), (xm, yt - .3)),
               wire((xm, yb + .3), (xm, yb)), wire((xm, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .5)))
    lr = tex(r"500\,\Omega", 36, BLU).next_to(R, UP, .3); ll = tex(r"5.3\,\mathrm{mH}", 36, GRN).next_to(L, LEFT, .25)
    D = dict(g=VGroup(src, w, R, L, lr, ll), L=L, R=R)
    RLw = VGroup(wire((xm, yt), (x1, yt)), wire((x1, yb), (xm, yb)), Dot((xm, yt, 0), radius=.07, color=INK), Dot((xm, yb, 0), radius=.07, color=INK))
    RL = resistor((x1, yt - .2), (x1, yb + .2), RED); RLw.add(wire((x1, yt), (x1, yt - .2)), wire((x1, yb + .2), (x1, yb)))
    D["load"] = VGroup(RLw, RL, tex(r"R_L = 500\,\Omega", 34, RED).next_to(RL, RIGHT, .2))
    return D


class P3(Scene):
    def construct(self):
        self.add(step_tag(5)); self.add(trap(3))
        D = hp_loop(LEFT * 3.4 + DOWN * .2); beat(self, FadeIn(D["g"]), t=.8, rt=.4)
        c = card(kr("고역통과", 34, GRN), GRN, .15).next_to(D["L"], RIGHT, .5); beat(self, FadeIn(c), t=.5, rt=.3)
        e = tex(r"f_c = \frac{R}{2\pi L}", 50, INK).move_to(RIGHT * 3.8 + UP * 1.3); beat(self, Write(e), t=.9, rt=.6)
        a = big(r"15\,\mathrm{kHz}", YEL, 80).move_to(RIGHT * 3.8 + DOWN * 1.0); beat(self, FadeIn(a, scale=1.2), t=.8, rt=.4)
        fill(self, a)


class P4(Scene):
    def construct(self):
        self.add(step_tag(5)); self.add(trap(3))
        D = hp_loop(LEFT * 3.6 + DOWN * .2, .95); self.add(D["g"])
        beat(self, FadeIn(D["load"], shift=LEFT * .2), t=.8, rt=.4)
        k = card(VGroup(kr("통과 크기", 28, MUTE), tex(r"1 \to 0.5", 54, YEL)).arrange(DOWN, buff=.15), YEL, .22).move_to(RIGHT * 4.3 + UP * 1.3)
        beat(self, FadeIn(k, shift=LEFT * .2), t=1.0, rt=.4)
        f = card(VGroup(kr("차단 주파수", 28, MUTE), tex(r"15 \to 7.5\,\mathrm{kHz}", 50, RED)).arrange(DOWN, buff=.15), RED, .22).move_to(RIGHT * 4.3 + DOWN * 1.2)
        beat(self, FadeIn(f, shift=LEFT * .2), t=1.0, rt=.4)
        fill(self, VGroup(k, f))


def hp_plot(W=7.0, H=3.4):
    ax, lab = logax(W, H, (-1.0, 1.0), xlab="f")
    c1 = ax.plot(lambda x: hmag("HP", 10 ** x / 1.0), x_range=[-1, 1, .01], color=GRN, stroke_width=6)
    c2 = ax.plot(lambda x: .5 * hmag("HP", 10 ** x / .5), x_range=[-1, 1, .01], color=RED, stroke_width=6)
    return ax, lab, c1, c2


class P5(Scene):
    def construct(self):
        self.add(step_tag(5))
        ax, lab, c1, c2 = hp_plot(6.6, 3.4); VGroup(ax, lab, c1, c2).move_to(LEFT * 2.2 + DOWN * .2)
        beat(self, Create(ax), FadeIn(lab), Create(c1), Create(c2), t=1.0, rt=.6)
        h = hline(ax, .5 / np.sqrt(2), RED, r"0.35", (-1, 1)); m = vmark(ax, np.log10(.5), .5 / np.sqrt(2), RED)
        beat(self, Create(h), FadeIn(m), t=.9, rt=.5)
        c = card(VGroup(kr("기준은", 28, MUTE), kr("새 최대값 × 0.707", 36, YEL)).arrange(DOWN, buff=.15), YEL, .22).move_to(RIGHT * 4.3 + UP * 1.2)
        beat(self, FadeIn(c), t=.8, rt=.4)
        A = opamp(RIGHT * 4.3 + DOWN * 1.5, .5, PUR); beat(self, Create(A["g"]), FadeIn(kr("연산증폭기 필터", 30, PUR).next_to(A["g"], DOWN, .2)), t=.9, rt=.5)
        fill(self, c)


# ================= 정리 =================
class E1(Scene):
    def construct(self):
        hd = judge_head().move_to(UP * 2.9 + RIGHT * .2)
        rows_ = VGroup(*[judge_row(lo, hi, k).move_to(RIGHT * .2 + UP * y) for (lo, hi, k), y in zip(((1, 0, "LP"), (0, 1, "HP"), (0, 0, "BP"), (1, 1, "BR")), (1.6, .3, -1.0, -2.3))])
        VGroup(hd, rows_).scale(.88, about_point=ORIGIN)
        beat(self, FadeIn(hd), t=.5, rt=.3)
        for r in rows_:
            beat(self, FadeIn(r, shift=UP * .15), t=.8, rt=.3)
        fill(self, rows_)


class E2(Scene):
    def construct(self):
        a = card(VGroup(kr("1차 필터", 30, MUTE), tex(r"\omega_c = \frac{1}{RC},\;\; \frac{R}{L}", 60, BLU)).arrange(DOWN, buff=.2), BLU, .3).move_to(UP * 1.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.2, rt=.5)
        b = card(VGroup(kr("Hz로 주면", 30, MUTE), tex(r"\times 2\pi", 60, YEL)).arrange(RIGHT, buff=.3), YEL, .25).move_to(DOWN * 1.4)
        beat(self, FadeIn(b, shift=UP * .2), t=1.2, rt=.5)
        fill(self, b)


class E3(Scene):
    def construct(self):
        a = card(VGroup(kr("중심", 30, MUTE), tex(r"\omega_0 = \sqrt{\omega_{c1}\omega_{c2}}", 56, YEL)).arrange(DOWN, buff=.2), YEL, .3).move_to(LEFT * 3.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.2, rt=.5)
        b = card(VGroup(kr("뾰족함", 30, MUTE), tex(r"Q = \frac{\omega_0}{\beta}", 60, PUR)).arrange(DOWN, buff=.2), PUR, .3).move_to(RIGHT * 3.4)
        beat(self, FadeIn(b, shift=UP * .2), t=1.2, rt=.5)
        fill(self, VGroup(a, b))


class Site(Scene):
    def construct(self):
        c = card(VGroup(kr("무료 사이트", 32, MUTE), kr("보이는 회로이론", 60, YEL)).arrange(DOWN, buff=.2), YEL, .45).move_to(UP * 1.4)
        beat(self, FadeIn(c, shift=UP * .2), t=1.1, rt=.5)
        items = VGroup(*[card(mini(k, W=1.7, H=.9, name=False), FCOL[k], .15) for k in ("LP", "HP", "BP", "BR")]).arrange(RIGHT, buff=.3).move_to(DOWN * 1.0)
        for it in items:
            beat(self, FadeIn(it, shift=UP * .15), t=.55, rt=.3)
        beat(self, FadeIn(kr("소자 값을 바꿔 가며 직접 확인", 34, GRN).next_to(items, DOWN, .35)), t=.9, rt=.4)
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
        D = sloop(LEFT * 2.6 + DOWN * .1, 6.4, 3.0)
        beat(self, FadeIn(D["wires"]), *[FadeIn(l) for l in D["lab"].values()], t=.7, rt=.4)
        q = card(VGroup(kr("직렬 RLC 하나로", 32, INK), kr("필터 4개", 56, YEL)).arrange(DOWN, buff=.15), YEL, .3).move_to(RIGHT * 4.4 + UP * .2)
        beat(self, FadeIn(q, scale=1.2), t=.9, rt=.4)
        fill(self, q)


class AEnds(Scene):
    def construct(self):
        D = sloop(LEFT * 3.4 + DOWN * .2, 6.0, 3.0); self.add(D["g"])
        h = card(tex(r"\omega = 0", 44, BLU), BLU, .18).move_to(RIGHT * 4.0 + UP * 2.2); beat(self, FadeIn(h), t=.4, rt=.3)
        o1 = open_at(D, "C"); beat(self, FadeOut(D["el"]["C"]), FadeIn(o1), t=1.0, rt=.4)
        h2 = card(tex(r"\omega = \infty", 44, RED), RED, .18).move_to(RIGHT * 4.0 + UP * .6)
        beat(self, FadeOut(o1), FadeIn(D["el"]["C"]), FadeIn(h2), t=.5, rt=.3)
        o2 = open_at(D, "L"); beat(self, FadeOut(D["el"]["L"]), FadeIn(o2), t=1.0, rt=.4)
        c = card(kr("전류가 끊긴다", 36, RED), RED, .2).move_to(RIGHT * 4.0 + DOWN * 1.2); beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, c, RED)


class ABP(Scene):
    def construct(self):
        D = sloop(LEFT * 2.8 + DOWN * .2, 6.2, 3.0); self.add(D["g"])
        b = obrace(D, ("R",), YEL); beat(self, FadeIn(b), t=.7, rt=.4)
        i = card(mini("BP", W=3.0, H=1.6), YEL, .25).move_to(RIGHT * 4.3); beat(self, FadeIn(i, shift=LEFT * .2), t=1.0, rt=.5)
        fill(self, i)


class ABR(Scene):
    def construct(self):
        D = sloop(LEFT * 2.8 + DOWN * .2, 6.2, 3.0); self.add(D["g"])
        b = obrace(D, ("L", "C"), RED); beat(self, FadeIn(b), t=.7, rt=.4)
        i = card(mini("BR", W=3.0, H=1.6), RED, .25).move_to(RIGHT * 4.3); beat(self, FadeIn(i, shift=LEFT * .2), t=1.0, rt=.5)
        fill(self, i, RED)


class AAll(Scene):
    def construct(self):
        D = sloop(LEFT * 3.0 + DOWN * .1, 6.0, 3.0); self.add(D["g"])
        icons = four_icons().scale(.95).move_to(RIGHT * 4.2 + DOWN * .1)
        self.add(icons[0], icons[1])
        b = obrace(D, ("C",), BLU); beat(self, FadeIn(b), FadeIn(icons[2], shift=UP * .2), t=1.0, rt=.4)
        b2 = obrace(D, ("L",), GRN); beat(self, ReplacementTransform(b, b2), FadeIn(icons[3], shift=UP * .2), t=1.0, rt=.4)
        fill(self, icons)


class BQ(Scene):
    def construct(self):
        p = f4card().move_to(ORIGIN); beat(self, FadeIn(p, shift=UP * .2), t=1.0, rt=.5)
        fill(self, p)


class BWrong(Scene):
    def construct(self):
        w = tex(r"R = \frac{1}{3000 \times 10^{-6}}", 60, INK).move_to(UP * 1.4); beat(self, Write(w), t=1.0, rt=.6)
        a = card(tex(r"= 333\,\Omega", 80, MUTE), MUTE, .3).move_to(DOWN * .9); beat(self, FadeIn(a), t=.7, rt=.3)
        beat(self, Create(cross(a)), FadeIn(kr("틀림", 44, RED).next_to(a, RIGHT, .4)), t=.8, rt=.3)
        fill(self, a, RED)


class CQ(Scene):
    def construct(self):
        ax, lab = logax(6.8, 3.0, (-1.0, 2.0), xlab="f"); VGroup(ax, lab).move_to(UP * .3)
        cv = ax.plot(lambda x: hmag("BP", 10 ** (x - .5), .3514), x_range=[-1, 2, .01], color=YEL, stroke_width=6)
        beat(self, Create(ax), FadeIn(lab), Create(cv), FadeIn(tex(r"1\,\mathrm{k}", 30, YEL).next_to(ax.c2p(0, 0), DOWN, .15)), FadeIn(tex(r"10\,\mathrm{k}", 30, YEL).next_to(ax.c2p(1, 0), DOWN, .15)), t=1.0, rt=.6)
        q = card(VGroup(kr("중심 주파수", 32, INK), tex(r"5.5\,\mathrm{kHz}\;?", 56, MUTE)).arrange(RIGHT, buff=.3), MUTE, .2).move_to(DOWN * 2.4)
        beat(self, FadeIn(q, shift=UP * .2), t=.9, rt=.4)
        beat(self, Create(cross(q[1][1])), t=.5, rt=.3)
        fill(self, q, RED)


class CGeo(Scene):
    def construct(self):
        a = card(VGroup(kr("산술평균", 30, MUTE), tex(r"\frac{f_{c1} + f_{c2}}{2}", 56, MUTE)).arrange(DOWN, buff=.2), MUTE, .25).move_to(LEFT * 3.4)
        beat(self, FadeIn(a), t=.7, rt=.3); beat(self, Create(cross(a)), t=.5, rt=.3)
        b = card(VGroup(kr("기하평균", 30, YEL), tex(r"\sqrt{f_{c1} f_{c2}}", 64, YEL)).arrange(DOWN, buff=.2), YEL, .3).move_to(RIGHT * 3.4)
        beat(self, FadeIn(b, scale=1.2), t=1.0, rt=.5)
        fill(self, b)


class CPlot(Scene):
    def construct(self):
        ax, lab = logax(5.4, 2.6, (-1.0, 2.0), xlab="f"); VGroup(ax, lab).move_to(RIGHT * 3.4 + DOWN * .2)
        cv = ax.plot(lambda x: hmag("BP", 10 ** (x - .5), .3514), x_range=[-1, 2, .01], color=YEL, stroke_width=6)
        lin = Axes(x_range=[0, 14000, 2000], y_range=[0, 1.15, .5], x_length=5.4, y_length=2.6, tips=False, axis_config=dict(color=MUTE, stroke_width=3, include_ticks=False)).move_to(LEFT * 3.4 + DOWN * .2)
        lc = lin.plot(lambda f: hmag("BP", max(f, 30) / 3162.3, .3514), x_range=[30, 14000, 20], color=BLU, stroke_width=6)
        beat(self, Create(lin), Create(lc), FadeIn(kr("보통 축: 비대칭", 32, BLU).next_to(lin, UP, .3)), t=1.0, rt=.6)
        beat(self, Create(ax), Create(cv), FadeIn(kr("로그 축: 좌우 대칭", 32, YEL).next_to(ax, UP, .3)), t=1.0, rt=.6)
        m = vmark(ax, .5, 1, YEL); beat(self, FadeIn(m), t=.5, rt=.3)
        fill(self, cv)


class CSum(Scene):
    def construct(self):
        a = card(VGroup(kr("대역폭", 30, MUTE), tex(r"\beta = \omega_{c2} - \omega_{c1}", 52, GRN)).arrange(DOWN, buff=.2), GRN, .3).move_to(UP * 1.4)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.4)
        b = card(VGroup(kr("중심", 30, MUTE), tex(r"\omega_0 = \sqrt{\omega_{c1}\omega_{c2}}", 52, YEL)).arrange(DOWN, buff=.2), YEL, .3).move_to(DOWN * 1.4)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.4)
        fill(self, b)


class DQ(Scene):
    def construct(self):
        ax, lab, cv = bp_axes(6.0, 3.0, 1.0); VGroup(ax, lab, cv).move_to(LEFT * 2.6)
        c2 = ax.plot(lambda x: hmag("BP", 10 ** x, 5), x_range=[-1, 1, .003], color=PUR, stroke_width=6)
        beat(self, Create(ax), FadeIn(lab), Create(cv), t=.8, rt=.5)
        beat(self, ReplacementTransform(cv, c2), t=.8, rt=.6)
        q = card(VGroup(kr("더 뾰족하게?", 34, INK), VGroup(tex(r"R\uparrow", 56, YEL), kr("or", 30, MUTE), tex(r"R\downarrow", 56, YEL)).arrange(RIGHT, buff=.3)).arrange(DOWN, buff=.2), YEL, .3).move_to(RIGHT * 4.3)
        beat(self, FadeIn(q, scale=1.2), t=.9, rt=.4)
        fill(self, q)


class DSer(Scene):
    def construct(self):
        a, b = qcards(); a.move_to(LEFT * 3.3)
        D = sloop(RIGHT * 3.3 + UP * .2, 5.0, 2.6); beat(self, FadeIn(D["g"]), t=.5, rt=.3)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.4)
        beat(self, Indicate(D["el"]["R"], color=YEL, scale_factor=1.3), Indicate(a[1][2], color=YEL), t=1.0, rt=.6)
        fill(self, a, BLU)


def ploop(o, s=1.0):
    """병렬 RLC 대역통과: 전원 - R(직렬) - L‖C (출력)."""
    o = PT3(o); x0 = o[0] - 2.5 * s; xr0, xr1 = x0 + .5, x0 + 2.2 * s; xl, xc = o[0] + .5 * s, o[0] + 2.1 * s; yt, yb = o[1] + 1.3 * s, o[1] - 1.3 * s
    src = acsrc((x0, o[1]), YEL, .45)
    R = resistor((xr0, yt), (xr1, yt), BLU); L = coil((xl, yt - .25), (xl, yb + .25), GRN); C = capacitor((xc, yt - .25), (xc, yb + .25), ORG)[0]
    w = VGroup(wire((x0, o[1] + .45), (x0, yt)), wire((x0, yt), (xr0, yt)), wire((xr1, yt), (xc, yt)), wire((xl, yt), (xl, yt - .25)), wire((xc, yt), (xc, yt - .25)),
               wire((xl, yb + .25), (xl, yb)), wire((xc, yb + .25), (xc, yb)), wire((xc, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .45)))
    return dict(g=VGroup(src, w, R, L, C, tex("R", 36, BLU).next_to(R, UP, .25)), R=R)


class DPar(Scene):
    def construct(self):
        a, b = qcards(); b.move_to(LEFT * 3.3)
        D = ploop(RIGHT * 3.4 + UP * .2, 1.0); beat(self, FadeIn(D["g"]), t=.5, rt=.3)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.4)
        beat(self, Indicate(D["R"], color=YEL, scale_factor=1.3), Indicate(b[1][2], color=YEL), t=1.0, rt=.6)
        fill(self, b, GRN)


class EQ(Scene):
    def construct(self):
        ax, lab, c1, c2 = hp_plot(6.4, 3.2); VGroup(ax, lab, c1, c2).move_to(LEFT * 2.0 + DOWN * .2)
        beat(self, Create(ax), FadeIn(lab), Create(c1), t=.8, rt=.5)
        beat(self, ReplacementTransform(c1.copy(), c2), t=.9, rt=.6)
        q = card(VGroup(kr("부하 달면", 32, INK), kr("차단 주파수 반토막", 40, RED)).arrange(DOWN, buff=.15), RED, .3).move_to(RIGHT * 4.3)
        beat(self, FadeIn(q, scale=1.2), t=.9, rt=.4)
        fill(self, q, RED)


class ECut(Scene):
    def construct(self):
        ax, lab, c1, c2 = hp_plot(7.0, 3.4); VGroup(ax, lab, c1, c2).move_to(LEFT * 1.6 + DOWN * .2); self.add(ax, lab, c1)
        m1 = vmark(ax, 0, 1 / np.sqrt(2), GRN, r"15\,\mathrm{k}"); beat(self, FadeIn(m1), t=.6, rt=.3)
        beat(self, Create(c2), t=.8, rt=.6)
        m2 = vmark(ax, np.log10(.5), .5 / np.sqrt(2), RED, r"7.5\,\mathrm{k}"); beat(self, FadeIn(m2), t=.7, rt=.4)
        a = big(r"7.5\,\mathrm{kHz}", RED, 70).move_to(RIGHT * 4.6 + UP * .4); beat(self, FadeIn(a, scale=1.2), t=.8, rt=.4)
        fill(self, a, RED)


class EOp(Scene):
    def construct(self):
        c = card(kr("수동 필터의 한계", 40, RED), RED, .25).move_to(UP * 2.6 + LEFT * 3.2); beat(self, FadeIn(c), t=.7, rt=.3)
        A = opamp(UP * .5 + LEFT * 3.2, 1.0, PUR); beat(self, Create(A["g"]), t=.8, rt=.6)
        t = card(kr("연산증폭기 필터", 48, PUR), PUR, .3).move_to(RIGHT * 3.4 + UP * .5); beat(self, FadeIn(t, shift=UP * .2), t=.8, rt=.4)
        fill(self, t, PUR)
