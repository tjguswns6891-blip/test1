# 라플라스 심화 5편(스위칭 임펄스) 모션그래픽. 16:9, 핵심은 가운데(세로 쇼츠에서도 씀). 종속 전원 편 형식.
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



# ---------- 스위칭 임펄스 전용 ----------
def cross(m, c=RED):
    return Cross(m, stroke_color=c, stroke_width=7, scale_factor=1.1)


def vtag(txt, c=YEL, size=40):
    return card(tex(txt, size, c), c, .14)


def switch(a, b, closed=False, c=INK, sw=5):
    """a→b 스위치. 반환 (그룹, 레버). 열림이면 레버가 30° 들림."""
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    end = b if closed else a + (u * np.cos(.55) + n * np.sin(.55)) * L
    lever = Line(a, end, color=c, stroke_width=sw + 1)
    return VGroup(term(a, c), term(b, c), lever), lever


def lever_to(sw_g, closed=True):
    a, b = sw_g[0].get_center(), sw_g[1].get_center()
    if closed:
        return Line(a, b, color=sw_g[2].get_color(), stroke_width=sw_g[2].get_stroke_width())
    d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    return Line(a, a + (u * np.cos(.55) + n * np.sin(.55)) * L, color=sw_g[2].get_color(), stroke_width=sw_g[2].get_stroke_width())


def capcirc(o=ORIGIN, rlab=r"R", closed=False, v1=r"10\,\mathrm{V}", v2=r"0\,\mathrm{V}", withR=True):
    """충전된 C1(왼쪽) - 스위치 - R - 빈 C2(오른쪽). dict: all, C1, C2, sw, R, lr, t1, t2, base, pts."""
    o = P3(o); x0, x1 = o[0] - 2.8, o[0] + 2.8; yt, yb = o[1] + 1.3, o[1] - 1.3
    C1 = capacitor((x0, yt), (x0, yb), YEL)[0]; C2 = capacitor((x1, yt), (x1, yb), BLU)[0]
    swg, lev = switch((x0 + .9, yt), (x0 + 1.8, yt), closed)
    base = VGroup(wire((x0, yt), (x0 + .9, yt)), wire((x0, yb), (x1, yb)))
    if withR:
        R = resistor((x0 + 2.2, yt), (x1 - .6, yt), RED); base.add(wire((x0 + 1.8, yt), (x0 + 2.2, yt)), wire((x1 - .6, yt), (x1, yt)))
        lr = tex(rlab, 40, RED).next_to(R, UP, .3)
    else:
        R = wire((x0 + 1.8, yt), (x1, yt)); lr = VGroup()
    l1 = VGroup(tex("C_1", 34, YEL), tex(r"1\,\mu\mathrm{F}", 30, MUTE)).arrange(DOWN, buff=.08).next_to(C1, LEFT, .3)
    l2 = VGroup(tex("C_2", 34, BLU), tex(r"1\,\mu\mathrm{F}", 30, MUTE)).arrange(DOWN, buff=.08).next_to(C2, RIGHT, .3)
    t1 = vtag(v1, YEL).next_to(l1, DOWN, .25); t2 = vtag(v2, MUTE if v2.startswith("0") else BLU).next_to(l2, DOWN, .25)
    D = dict(C1=C1, C2=C2, sw=swg, R=R, lr=lr, l1=l1, l2=l2, t1=t1, t2=t2, base=base, pts=dict(x0=x0, x1=x1, yt=yt, yb=yb))
    D["all"] = VGroup(base, C1, C2, swg, R, lr, l1, l2, t1, t2)
    return D


def build_cap(sc, D, t=.4):
    beat(sc, FadeIn(D["base"]), Create(D["C1"]), FadeIn(D["l1"]), t=t, rt=.35)
    beat(sc, FadeIn(D["t1"], scale=1.2), t=t, rt=.3)
    beat(sc, Create(D["C2"]), FadeIn(D["l2"]), FadeIn(D["t2"]), t=t, rt=.35)
    beat(sc, FadeIn(D["sw"]), Create(D["R"]), FadeIn(D["lr"]), t=t, rt=.35)


def indcirc(o=ORIGIN, closed=True, s_dom=False):
    """100V - 10Ω - L1(3H) - 마디 a - [스위치 ∥ (15Ω - L2(2H))]. dict: all, sw, L1, L2, R1, R2, ...
    s_dom: 라벨을 s-영역(3s, 2s, 100/s, 초기값 전원 30)으로."""
    o = P3(o); xb = o[0] - 3.7; yt, yb = o[1] + 1.4, o[1] - 1.4; xa = xb + 5.0; xc = xa + 2.8
    bat = battery((xb, o[1]), YEL)
    R1 = resistor((xb + .5, yt), (xb + 2.1, yt), INK); L1 = coil((xb + 2.5, yt), (xa - .4, yt), GRN)
    R2 = resistor((xa + .5, yt), (xc - .6, yt), INK); L2 = coil((xc, yt - .2), (xc, yb + .2), BLU)
    swg, lev = switch((xa, o[1] + .45), (xa, o[1] - .45), closed)
    base = VGroup(wire((xb, o[1] + .18), (xb, yt)), wire((xb, yt), (xb + .5, yt)), wire((xb + 2.1, yt), (xb + 2.5, yt)),
                  wire((xa - .4, yt), (xa + .5, yt)), wire((xc - .6, yt), (xc, yt)), wire((xc, yt), (xc, yt - .2)), wire((xc, yb + .2), (xc, yb)),
                  wire((xc, yb), (xb, yb)), wire((xb, yb), (xb, o[1] - .18)),
                  wire((xa, yt), (xa, o[1] + .45)), wire((xa, o[1] - .45), (xa, yb)),
                  Dot((xa, yt, 0), radius=.07, color=INK), Dot((xa, yb, 0), radius=.07, color=INK))
    if s_dom:
        lv, l1, l2 = tex(r"\frac{100}{s}", 44, YEL), tex("3s", 40, GRN), tex("2s", 40, BLU)
    else:
        lv, l1, l2 = tex(r"100\,\mathrm{V}", 36, YEL), tex(r"3\,\mathrm{H}", 38, GRN), tex(r"2\,\mathrm{H}", 38, BLU)
    lv.next_to(bat, LEFT, .2); l1.next_to(L1, UP, .3); l2.next_to(L2, RIGHT, .25)
    lr1 = tex(r"10\,\Omega", 34, INK).next_to(R1, UP, .3); lr2 = tex(r"15\,\Omega", 34, INK).next_to(R2, UP, .3)
    D = dict(bat=bat, R1=R1, L1=L1, R2=R2, L2=L2, sw=swg, base=base, lv=lv, l1=l1, l2=l2, lr1=lr1, lr2=lr2,
             pts=dict(xb=xb, xa=xa, xc=xc, yt=yt, yb=yb, o=o))
    D["all"] = VGroup(base, bat, R1, L1, R2, L2, swg, lv, l1, l2, lr1, lr2)
    return D


def build_ind(sc, D, t=.4):
    beat(sc, FadeIn(D["base"]), FadeIn(D["bat"]), FadeIn(D["lv"]), FadeIn(D["sw"]), t=t, rt=.35)
    beat(sc, Create(D["R1"]), FadeIn(D["lr1"]), Create(D["L1"]), FadeIn(D["l1"]), t=t, rt=.4)
    beat(sc, Create(D["R2"]), FadeIn(D["lr2"]), Create(D["L2"]), FadeIn(D["l2"]), t=t, rt=.4)


def itag(D, which, txt, c):
    """인덕터 옆 전류 표시."""
    L = D[which]
    return vtag(txt, c, 36).next_to(L, DOWN if which == "L1" else LEFT, .3)


def axes(o, W=6.0, H=3.0, xl="t", yl="i"):
    o = P3(o)
    g = VGroup(Arrow(o + LEFT * .15, o + RIGHT * W, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.04),
               Arrow(o + DOWN * .15, o + UP * H, buff=0, color=MUTE, stroke_width=3, max_tip_length_to_length_ratio=.06))
    g.add(tex(xl, 30, MUTE).next_to(g[0].get_end(), DOWN, .1), tex(yl, 30, MUTE).next_to(g[1].get_end(), LEFT, .1))
    return g


def pulse(o, h, w, L=5.5, c=BLU, n=160):
    """i = h·e^(−x/w), x∈[0, L]. 반환 (곡선, 채운 넓이)."""
    o = P3(o); xs = np.linspace(0, L, n)
    pts = [o + np.array([x, h * np.exp(-x / w), 0]) for x in xs]
    curve = VMobject(color=c, stroke_width=5).set_points_as_corners([o + UP * h] + pts[1:] if False else [o] + pts)
    area = VMobject(stroke_width=0, fill_color=c, fill_opacity=.3).set_points_as_corners([o] + pts + [o + RIGHT * L, o])
    return curve, area


def impulse_arrow(o, H=3.0, c=YEL, lab=None):
    o = P3(o)
    a = Arrow(o, o + UP * H, buff=0, color=c, stroke_width=8, max_tip_length_to_length_ratio=.12)
    g = VGroup(a)
    if lab:
        g.add(tex(lab, 40, c).next_to(a.get_end(), RIGHT, .15))
    return g


def bars(o, vals, cols, labs, unit, maxv, H=2.6, W=.9, gap=.6):
    """세로 막대들. vals 크기, labs 아래 라벨, 위에 값."""
    o = P3(o); g = VGroup()
    for i, (v, c, l) in enumerate(zip(vals, cols, labs)):
        x = o + RIGHT * i * (W + gap)
        frame = Rectangle(width=W, height=H, color=MUTE, stroke_width=3).move_to(x + UP * H / 2)
        h = max(.001, H * v / maxv)
        fillr = Rectangle(width=W, height=h, stroke_width=0, fill_color=c, fill_opacity=.85).move_to(x + UP * h / 2)
        g.add(VGroup(frame, fillr, kr(l, 26, INK).next_to(frame, DOWN, .15), tex(f"{v:g}\\,{unit}", 32, c).next_to(frame, UP, .12)))
    return g


def rows2(items, w=12.4):
    g = VGroup()
    for cells, c in items:
        g.add(card(VGroup(*[kr(t, 30, cc) for t, cc in cells]).arrange(RIGHT, buff=.45), c, .2))
    return g.arrange(DOWN, buff=.3)


# ================= 인트로 =================
class Hook(Scene):
    def construct(self):
        D = indcirc(DOWN * .3, closed=True); build_ind(self, D, .3)
        a = itag(D, "L1", r"10\,\mathrm{A}", GRN); b = itag(D, "L2", r"0\,\mathrm{A}", MUTE)
        beat(self, FadeIn(a, scale=1.2), FadeIn(b, scale=1.2), t=.8, rt=.35)
        beat(self, Transform(D["sw"][2], lever_to(D["sw"], False)), t=.6, rt=.4)
        a2 = itag(D, "L1", r"6\,\mathrm{A}", YEL); b2 = itag(D, "L2", r"6\,\mathrm{A}", YEL)
        beat(self, Transform(a, a2), Transform(b, b2), Flash(a2, color=YEL), Flash(b2, color=YEL), t=1.0, rt=.4)
        q = card(kr("연속이라며?", 40, RED), RED, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(q, shift=DOWN * .2), t=.8, rt=.35)
        fill(self, VGroup(a, b), YEL)


class Goal(Scene):
    def construct(self):
        D = capcirc(DOWN * .3); build_cap(self, D, .3)
        beat(self, Transform(D["sw"][2], lever_to(D["sw"], True)), t=.6, rt=.4)
        n1 = vtag(r"5\,\mathrm{V}", YEL).move_to(D["t1"]); n2 = vtag(r"5\,\mathrm{V}", YEL).move_to(D["t2"])
        beat(self, Transform(D["t1"], n1), Transform(D["t2"], n2), Flash(n1, color=YEL), Flash(n2, color=YEL), t=1.0, rt=.4)
        q = card(VGroup(kr("스위치 한 번에", 30, INK), tex(r"10\,\mathrm{V}\to 5\,\mathrm{V}", 48, YEL)).arrange(RIGHT, buff=.3), YEL, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(q, shift=DOWN * .2), t=.8, rt=.35)
        fill(self, VGroup(D["t1"], D["t2"]), YEL)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "연속성 규칙", BLU), ("2", "커패시터", PUR), ("3", "임펄스", GRN), ("4", "인덕터", ORG)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 36, c)).arrange(DOWN, buff=.2), c, .3) for n, t, c in items])
        cards.arrange(RIGHT, buff=.3).scale_to_fit_width(12.4).shift(UP * .3)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=.9, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[3].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), FadeIn(kr("라플라스 심화 5편", 32, YEL).next_to(arrow, DOWN, .3)), t=1.0, rt=.7)
        fill(self, cards)


# ================= STEP 1 연속성 규칙 =================
class R1(Scene):
    def construct(self):
        self.add(step_tag(1))
        c = capacitor(LEFT * 3.4 + UP * 1.6, LEFT * 3.4 + DOWN * .2, YEL)[0]
        l = coil(RIGHT * 3.0 + UP * 1.6, RIGHT * 3.0 + DOWN * .2, GRN)
        beat(self, Create(c), FadeIn(kr("커패시터", 32, YEL).next_to(c, LEFT, .3)), t=.9, rt=.5)
        a = card(VGroup(tex("v_C", 52, YEL), kr("연속", 40, INK)).arrange(RIGHT, buff=.25), YEL, .22).move_to(LEFT * 3.4 + DOWN * 1.8)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.4)
        beat(self, Create(l), FadeIn(kr("인덕터", 32, GRN).next_to(l, RIGHT, .3)), t=.9, rt=.5)
        b = card(VGroup(tex("i_L", 52, GRN), kr("연속", 40, INK)).arrange(RIGHT, buff=.25), GRN, .22).move_to(RIGHT * 3.0 + DOWN * 1.8)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.4)
        fill(self, VGroup(a, b))


def jump_graph(o, c, lab):
    """t=0 에서 값이 뚝 바뀌는 그래프."""
    o = P3(o); ax = axes(o, 4.2, 2.4, "t", lab)
    p = VGroup(Line(o + UP * 1.8 + LEFT * 0, o + UP * 1.8 + RIGHT * 1.4, color=c, stroke_width=6),
               DashedLine(o + UP * 1.8 + RIGHT * 1.4, o + UP * .8 + RIGHT * 1.4, color=RED, stroke_width=5),
               Line(o + UP * .8 + RIGHT * 1.4, o + UP * .8 + RIGHT * 3.8, color=c, stroke_width=6))
    return ax, p


class R2(Scene):
    def construct(self):
        self.add(step_tag(1))
        f = tex(r"i_C = C\,\frac{dv}{dt}", 72, YEL).move_to(UP * 2.0)
        beat(self, Write(f), t=1.2, rt=.7)
        ax, p = jump_graph(LEFT * 5.2 + DOWN * 2.4, YEL, "v")
        beat(self, FadeIn(ax), Create(p[0]), t=.8, rt=.4)
        beat(self, Create(p[1]), Create(p[2]), FadeIn(kr("순간 점프", 28, RED).next_to(p[1], RIGHT, .15)), t=1.0, rt=.5)
        r = card(VGroup(tex(r"\frac{dv}{dt}\to\infty", 52, RED), tex(r"\Rightarrow\; i_C=\infty", 52, RED)).arrange(DOWN, buff=.25), RED, .25).move_to(RIGHT * 3.4 + DOWN * 1.0)
        beat(self, FadeIn(r, shift=LEFT * .3), t=1.0, rt=.4)
        fill(self, r, RED)


class R3(Scene):
    def construct(self):
        self.add(step_tag(1))
        f = tex(r"v_L = L\,\frac{di}{dt}", 72, GRN).move_to(UP * 2.0)
        beat(self, Write(f), t=1.2, rt=.7)
        ax, p = jump_graph(LEFT * 5.2 + DOWN * 2.4, GRN, "i")
        beat(self, FadeIn(ax), Create(p[0]), t=.8, rt=.4)
        beat(self, Create(p[1]), Create(p[2]), FadeIn(kr("전류가 튐", 28, RED).next_to(p[1], RIGHT, .15)), t=1.0, rt=.5)
        r = card(VGroup(tex(r"\frac{di}{dt}\to\infty", 52, RED), tex(r"\Rightarrow\; v_L=\infty", 52, RED)).arrange(DOWN, buff=.25), RED, .25).move_to(RIGHT * 3.4 + DOWN * 1.0)
        beat(self, FadeIn(r, shift=LEFT * .3), t=1.0, rt=.4)
        fill(self, r, RED)


class R4(Scene):
    def construct(self):
        self.add(step_tag(1))
        o = LEFT * 3.0 + DOWN * .2; x0, x1, yt, yb = o[0] - 2, o[0] + 2, 1.2, -1.6
        bat = battery((x0, -.2), YEL); R = resistor((x0 + .3, yt), (x1 - .3, yt), RED)
        C = capacitor((x1, yt), (x1, yb), BLU)[0]
        g = VGroup(wire((x0, 0), (x0, yt)), wire((x0, yt), (x0 + .3, yt)), wire((x1 - .3, yt), (x1, yt)), wire((x1, yb), (x0, yb)), wire((x0, yb), (x0, -.4)))
        beat(self, FadeIn(g), FadeIn(bat), Create(C), t=.8, rt=.5)
        beat(self, Create(R), FadeIn(kr("저항", 32, RED).next_to(R, UP, .25)), t=.9, rt=.5)
        beat(self, R.animate.set_stroke(width=9), t=.6, rt=.4)
        f = card(VGroup(kr("전류는 기껏해야", 30, INK), tex(r"i \le \frac{V}{R}", 64, RED)).arrange(DOWN, buff=.2), RED, .25).move_to(RIGHT * 3.6 + UP * .8)
        beat(self, FadeIn(f, shift=LEFT * .3), t=1.0, rt=.4)
        ok = card(kr("무한대 전류 ✕ → 규칙 ✓", 32, GRN), GRN, .2).move_to(RIGHT * 3.6 + DOWN * 1.6)
        beat(self, FadeIn(ok), t=.9, rt=.4)
        fill(self, ok, GRN)


class R5(Scene):
    def construct(self):
        self.add(step_tag(1))
        x = LEFT * 3.6
        c1 = capacitor(x + LEFT * 1.2 + UP * 1.0, x + LEFT * 1.2 + DOWN * 1.0, YEL)[0]; c2 = capacitor(x + RIGHT * 1.2 + UP * 1.0, x + RIGHT * 1.2 + DOWN * 1.0, BLU)[0]
        w = VGroup(wire(x + LEFT * 1.2 + UP * 1.0, x + RIGHT * 1.2 + UP * 1.0, RED, 6), wire(x + LEFT * 1.2 + DOWN * 1.0, x + RIGHT * 1.2 + DOWN * 1.0))
        beat(self, Create(c1), Create(c2), FadeIn(w), t=.9, rt=.5)
        a = card(kr("C끼리 저항 없이", 32, YEL), YEL, .2).move_to(x + DOWN * 2.2)
        beat(self, FadeIn(a), t=.8, rt=.4)
        y = RIGHT * 3.4
        l1 = coil(y + LEFT * 1.9 + UP * .6, y + LEFT * .2 + UP * .6, GRN); l2 = coil(y + RIGHT * .2 + UP * .6, y + RIGHT * 1.9 + UP * .6, BLU)
        beat(self, Create(l1), Create(l2), FadeIn(wire(y + LEFT * .2 + UP * .6, y + RIGHT * .2 + UP * .6, RED, 6)), t=.9, rt=.5)
        bt = card(kr("L끼리 직렬 강제", 32, GRN), GRN, .2).move_to(y + DOWN * 1.0)
        beat(self, FadeIn(bt), t=.8, rt=.4)
        e = card(kr("예외!", 48, RED), RED, .22).to_edge(UP, buff=.5)
        beat(self, FadeIn(e, scale=1.3), t=.8, rt=.4)
        fill(self, e, RED)


# ================= STEP 2 커패시터 두 개 =================
class C1(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = capcirc(DOWN * .3); build_cap(self, D, .55)
        beat(self, Transform(D["sw"][2], lever_to(D["sw"], True)), FadeIn(kr("t = 0", 32, MUTE).next_to(D["sw"], UP, .25)), t=.9, rt=.5)
        fill(self, D["R"], RED)


class C2(Scene):
    def construct(self):
        self.add(step_tag(2))
        x = LEFT * 4.6 + UP * .4
        c = capacitor(x + UP * 1.2, x + DOWN * 1.2, YEL)[0]
        beat(self, Create(c), FadeIn(vtag(r"10\,\mathrm{V}", YEL, 34).next_to(c, LEFT, .3)), t=.8, rt=.4)
        ar = Arrow(x + RIGHT * .8, x + RIGHT * 2.2, buff=0, color=INK, stroke_width=5)
        beat(self, GrowArrow(ar), FadeIn(kr("s-영역", 26, MUTE).next_to(ar, UP, .1)), t=.6, rt=.35)
        y = x + RIGHT * 3.2
        z = Rectangle(width=1.3, height=1.1, color=YEL, stroke_width=4).move_to(y + UP * .9)
        b = battery(y + DOWN * .9, YEL)
        g = VGroup(wire(y + UP * 1.6, y + UP * 1.45), wire(y + UP * .35, y + DOWN * .72), wire(y + DOWN * 1.08, y + DOWN * 1.6))
        beat(self, FadeIn(g), FadeIn(z), FadeIn(tex(r"\frac{1}{sC_1}", 36, YEL).move_to(z)), t=.9, rt=.4)
        beat(self, FadeIn(b), FadeIn(tex(r"\frac{10}{s}", 48, YEL).next_to(b, RIGHT, .3)), t=.9, rt=.4)
        f = card(tex(r"I(s)=\frac{10/s}{R+\frac{1}{sC_1}+\frac{1}{sC_2}}", 50, INK), BLU, .25).move_to(RIGHT * 3.2 + DOWN * 1.9)
        beat(self, FadeIn(kr("KVL 한 줄", 30, BLU).move_to(RIGHT * 3.2 + UP * 1.2)), t=.6, rt=.3)
        beat(self, FadeIn(f, shift=UP * .2), t=1.0, rt=.5)
        fill(self, f, BLU)


class C3(Scene):
    def construct(self):
        self.add(step_tag(2))
        a = card(tex(r"C_e=\frac{C_1C_2}{C_1+C_2}=0.5\,\mu\mathrm{F}", 46, PUR), PUR, .22).move_to(UP * 2.4)
        beat(self, FadeIn(a, shift=DOWN * .2), t=1.0, rt=.4)
        f = tex(r"i(t)=\frac{10}{R}\,e^{-t/RC_e}", 56, BLU).move_to(RIGHT * 3.4 + DOWN * .3)
        ax = axes(LEFT * 6.0 + DOWN * 2.6, 5.6, 3.6, "t", "i")
        beat(self, FadeIn(ax), t=.6, rt=.3)
        cu, ar = pulse(LEFT * 6.0 + DOWN * 2.6, 3.0, 1.2, 5.2, BLU)
        beat(self, Create(cu), t=1.2, rt=1.0)
        beat(self, FadeIn(tex(r"\frac{10}{R}", 48, BLU).next_to(cu.get_start() + UP * 3.0, RIGHT, .15)), t=.6, rt=.3)
        beat(self, Write(f), t=1.0, rt=.6)
        fill(self, f, BLU)


def charge_tanks(o, v1, v2, H=2.6):
    """두 커패시터의 전하를 물통 높이로 (10V 가득 = H)."""
    return bars(P3(o), [v1, v2], [YEL, BLU], ["C₁", "C₂"], r"\mathrm{V}", 10, H=H, W=1.2, gap=1.0)


class C4(Scene):
    def construct(self):
        self.add(step_tag(2))
        o = LEFT * 4.2 + DOWN * 1.6
        t0 = charge_tanks(o, 10, 0)
        lab = kr("연결 전", 32, MUTE).next_to(t0, UP, .45)
        beat(self, FadeIn(t0), FadeIn(lab), t=1.0, rt=.4)
        q0 = card(tex(r"Q=10\,\mu\mathrm{C}", 44, YEL), YEL, .18).move_to(RIGHT * 3.4 + UP * 1.6)
        beat(self, FadeIn(q0), t=.8, rt=.35)
        t1 = charge_tanks(o, 5, 5)
        beat(self, Transform(t0, t1), Transform(lab, kr("연결 후", 32, YEL).move_to(lab)), t=1.4, rt=1.0)
        q1 = card(tex(r"5\,\mu\mathrm{C}+5\,\mu\mathrm{C}", 44, YEL), YEL, .18).move_to(RIGHT * 3.4 + DOWN * .1)
        beat(self, FadeIn(q1, shift=DOWN * .2), t=.8, rt=.35)
        r = card(kr("둘 다 5V", 44, YEL), YEL, .22).move_to(RIGHT * 3.4 + DOWN * 1.8)
        beat(self, FadeIn(r, scale=1.2), t=.8, rt=.35)
        fill(self, r)


class C5(Scene):
    def construct(self):
        self.add(step_tag(2))
        h = card(kr("전하 보존", 52, YEL), YEL, .25).move_to(UP * 2.4)
        beat(self, FadeIn(h, scale=1.2), t=.9, rt=.4)
        a = tex(r"1\,\mu\mathrm{F}\times 10\,\mathrm{V}", 56, YEL).move_to(LEFT * 3.4 + UP * .2)
        b = tex(r"2\,\mu\mathrm{F}\times 5\,\mathrm{V}", 56, BLU).move_to(RIGHT * 3.4 + UP * .2)
        eq = tex("=", 72, INK).move_to(UP * .2)
        beat(self, Write(a), t=1.0, rt=.6)
        beat(self, FadeIn(eq), Write(b), t=1.0, rt=.6)
        c = card(tex(r"C_1V_0=(C_1+C_2)\,v", 48, INK), MUTE, .2).move_to(DOWN * 2.0)
        beat(self, FadeIn(c, shift=UP * .2), t=.9, rt=.4)
        fill(self, c)


class C6(Scene):
    def construct(self):
        self.add(step_tag(2))
        f = tex(r"W=\tfrac12 CV^2", 52, ORG).move_to(UP * 2.6)
        beat(self, Write(f), t=.8, rt=.5)
        b = bars(LEFT * 2.0 + DOWN * 1.8, [50, 25], [ORG, ORG], ["연결 전", "연결 후"], r"\mu\mathrm{J}", 50, H=3.0, W=1.4, gap=1.4)
        beat(self, FadeIn(b[0]), t=.9, rt=.4)
        beat(self, FadeIn(b[1]), t=.9, rt=.4)
        lost = Rectangle(width=1.4, height=1.5, stroke_color=RED, stroke_width=4, fill_color=RED, fill_opacity=.25).move_to(b[1][0].get_top() + DOWN * .75)
        beat(self, FadeIn(lost), FadeIn(kr("절반 = 열", 34, RED).next_to(lost, RIGHT, .3)), t=1.0, rt=.4)
        fill(self, lost, RED)


# ================= STEP 3 R 을 0 으로 =================
class K1(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = capcirc(DOWN * .3, rlab=r"R", closed=True, v2=r"0\,\mathrm{V}"); self.add(D["all"])
        for v in (r"10\,\Omega", r"1\,\Omega", r"0.1\,\Omega"):
            n = tex(v, 48, RED).move_to(D["lr"])
            beat(self, Transform(D["lr"], n), Indicate(D["R"], color=RED, scale_factor=1.0), t=1.0, rt=.5)
        fill(self, D["lr"], RED)


class K2(Scene):
    def construct(self):
        self.add(step_tag(3))
        o = LEFT * 5.0 + DOWN * 2.8; ax = axes(o, 9.6, 5.4, "t", "i")
        beat(self, FadeIn(ax), t=.5, rt=.3)
        cols = [BLU, PUR, YEL]; labs = [r"10\,\Omega", r"1\,\Omega", r"0.1\,\Omega"]
        for k, (h, w) in enumerate(((1.1, 2.4), (2.2, 1.2), (4.4, .6))):
            cu, _ = pulse(o, h, w, 9.0, cols[k])
            beat(self, Create(cu), FadeIn(VGroup(Line(ORIGIN, RIGHT * .6, color=cols[k], stroke_width=6), tex("R=" + labs[k], 36, cols[k])).arrange(RIGHT, buff=.2).move_to(RIGHT * 3.4 + DOWN * (k * .8))), t=1.0, rt=.6)
        c = card(kr("높아지고 · 좁아진다", 36, YEL), YEL, .2).move_to(RIGHT * 3.0 + UP * 2.0)
        beat(self, FadeIn(c), t=.8, rt=.35)
        fill(self, c)


class K3(Scene):
    def construct(self):
        self.add(step_tag(3))
        cols = [BLU, PUR, YEL]; g = VGroup()
        for k, (h, w) in enumerate(((.8, 1.6), (1.6, .8), (3.2, .4))):
            o = LEFT * 5.6 + RIGHT * k * 3.0 + DOWN * 2.6
            ax = axes(o, 2.6, 3.6, "t", "i"); cu, ar = pulse(o, h, w, 2.4, cols[k])
            g.add(VGroup(ax, cu, ar))
            beat(self, FadeIn(ax), Create(cu), FadeIn(ar), FadeIn(tex(r"5\,\mu\mathrm{C}", 38, cols[k]).move_to(o + RIGHT * 1.2 + DOWN * .55)), t=.8, rt=.45)
        f = card(VGroup(tex(r"Q=\int i\,dt=10\,C_e", 44, INK), tex(r"=5\,\mu\mathrm{C}", 52, YEL)).arrange(DOWN, buff=.2), YEL, .25).move_to(RIGHT * 4.6 + UP * .6)
        beat(self, FadeIn(f, shift=LEFT * .3), t=1.0, rt=.4)
        n = card(kr("R 이 없다", 36, RED), RED, .2).next_to(f, DOWN, .35)
        beat(self, FadeIn(n, scale=1.2), t=.8, rt=.35)
        fill(self, n, RED)


class K4(Scene):
    def construct(self):
        self.add(step_tag(3))
        o = LEFT * 5.0 + DOWN * 2.6; ax = axes(o, 6.0, 5.0, "t", "i")
        beat(self, FadeIn(ax), t=.5, rt=.3)
        o = o + RIGHT * 1.0
        cu, ar = pulse(o, 4.4, .25, 4.6, YEL)
        beat(self, Create(cu), FadeIn(ar), t=.9, rt=.5)
        imp = impulse_arrow(o, 4.6, YEL, r"5\,\mu\,\delta(t)")
        beat(self, ReplacementTransform(VGroup(cu, ar), imp), t=1.1, rt=.7)
        c = card(VGroup(kr("높이 ∞", 34, INK), kr("폭 0", 34, INK), kr("넓이 5μC", 34, YEL)).arrange(DOWN, buff=.2, aligned_edge=LEFT), YEL, .25).move_to(RIGHT * 3.8 + UP * .6)
        beat(self, FadeIn(c, shift=LEFT * .3), t=.9, rt=.4)
        t = card(kr("임펄스", 48, YEL), YEL, .22).next_to(c, DOWN, .4)
        beat(self, FadeIn(t, scale=1.3), t=.8, rt=.35)
        fill(self, imp, YEL)


class K5(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = capcirc(UP * 1.3 + LEFT * .2, closed=True, withR=False).get("all")
        D.scale(.8).move_to(UP * 1.5)
        beat(self, FadeIn(D), FadeIn(kr("R = 0", 34, RED).next_to(D, RIGHT, .3)), t=.9, rt=.4)
        f = tex(r"I(s)=\frac{10/s}{\frac{1}{sC_1}+\frac{1}{sC_2}}", 54, INK).move_to(LEFT * 2.2 + DOWN * 1.6)
        beat(self, Write(f), t=1.2, rt=.7)
        g = tex(r"=10\,C_e=5\times10^{-6}", 54, YEL).next_to(f, RIGHT, .2)
        beat(self, Write(g), t=1.0, rt=.6)
        c = card(kr("상수!", 44, YEL), YEL, .2).next_to(g, UP, .35)
        beat(self, FadeIn(c, scale=1.3), t=.8, rt=.35)
        fill(self, g)


class K6(Scene):
    def construct(self):
        self.add(step_tag(3))
        f = tex(r"\mathcal{L}^{-1}\{\,\text{const}\,\}=\delta(t)", 60, YEL).move_to(UP * 2.4)
        beat(self, Write(f), t=1.1, rt=.6)
        o = LEFT * 5.0 + DOWN * 2.4; ax = axes(o, 5.0, 3.6, "t", "i")
        beat(self, FadeIn(ax), t=.5, rt=.3)
        imp = impulse_arrow(o, 3.2, YEL, r"5\,\mu\,\delta(t)")
        beat(self, GrowArrow(imp[0]), FadeIn(imp[1]), t=.9, rt=.5)
        D = capcirc(RIGHT * 3.4 + DOWN * .6, closed=True, withR=False, v2=r"0\,\mathrm{V}")["all"].scale(.55).move_to(RIGHT * 3.6 + DOWN * .8)
        beat(self, FadeIn(D), t=.6, rt=.3)
        dots = VGroup(*[Dot(radius=.09, color=YEL) for _ in range(5)])
        p = D[4]   # 위 도선(R 자리)
        for k, d in enumerate(dots): d.move_to(p.get_start() + RIGHT * .15 * k)
        beat(self, FadeIn(dots), t=.3, rt=.2)
        beat(self, dots.animate.shift(RIGHT * (p.get_length() - .7)), t=.6, rt=.25)
        c = card(kr("한순간에 붓고 끝", 34, YEL), YEL, .2).next_to(D, DOWN, .35)
        beat(self, FadeIn(c), t=.8, rt=.35)
        fill(self, imp, YEL)


# ================= 중간 정리 =================
class M1(Scene):
    def construct(self):
        h = card(kr("여기까지 정리", 40, INK), MUTE, .2).move_to(UP * 2.7)
        beat(self, FadeIn(h), t=.6, rt=.3)
        a = card(VGroup(kr("커패시터 전압", 36, YEL), kr("순간 변화", 36, INK)).arrange(DOWN, buff=.15), YEL, .3).move_to(LEFT * 3.4 + DOWN * .2)
        beat(self, FadeIn(a, shift=RIGHT * .2), t=.9, rt=.4)
        ar = Arrow(LEFT * 1.0 + DOWN * .2, RIGHT * 1.0 + DOWN * .2, buff=0, color=INK, stroke_width=6)
        beat(self, GrowArrow(ar), FadeIn(kr("필요", 28, MUTE).next_to(ar, UP, .1)), t=.7, rt=.4)
        b = card(VGroup(kr("임펄스 전류", 40, YEL), tex(r"\delta(t)", 48, YEL)).arrange(DOWN, buff=.15), YEL, .3).move_to(RIGHT * 3.4 + DOWN * .2)
        beat(self, FadeIn(b, shift=LEFT * .2), t=.9, rt=.4)
        fill(self, b)


class M2(Scene):
    def construct(self):
        h = card(kr("전하 보존", 48, YEL), YEL, .22).move_to(UP * 2.6)
        beat(self, FadeIn(h), t=.7, rt=.3)
        o = LEFT * 1.7 + DOWN * 1.8
        t0 = charge_tanks(o, 10, 0); beat(self, FadeIn(t0), t=.9, rt=.4)
        beat(self, Transform(t0, charge_tanks(o, 5, 5)), t=1.2, rt=.6)
        c = card(tex(r"\sum CV\ \text{일정}", 44, YEL), YEL, .2).move_to(RIGHT * 4.2 + DOWN * .4) if False else card(VGroup(tex(r"\sum CV", 48, YEL), kr("일정", 36, INK)).arrange(RIGHT, buff=.2), YEL, .2).move_to(RIGHT * 4.4 + DOWN * .4)
        beat(self, FadeIn(c, shift=LEFT * .2), t=.8, rt=.35)
        fill(self, c)


class M3(Scene):
    def construct(self):
        h = card(VGroup(kr("에너지 보존", 44, ORG), kr("✕", 48, RED)).arrange(RIGHT, buff=.2), ORG, .22).move_to(UP * 2.6)
        beat(self, FadeIn(h), t=.7, rt=.3)
        b = bars(LEFT * 1.9 + DOWN * 1.9, [50, 25], [ORG, ORG], ["연결 전", "연결 후"], r"\mu\mathrm{J}", 50, H=2.8, W=1.4, gap=1.4)
        beat(self, FadeIn(b), t=.9, rt=.4)
        c = card(VGroup(kr("R → 0 이어도", 30, RED), kr("절반 손실", 36, RED)).arrange(DOWN, buff=.12), RED, .2).move_to(RIGHT * 4.4 + DOWN * .4)
        beat(self, FadeIn(c, shift=LEFT * .2), t=.8, rt=.35)
        fill(self, c, RED)


# ================= STEP 4 인덕터 직렬 =================
class L1(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = indcirc(DOWN * .3, closed=True); build_ind(self, D, .6)
        a = itag(D, "L1", r"10\,\mathrm{A}", GRN); b = itag(D, "L2", r"0\,\mathrm{A}", MUTE)
        beat(self, FadeIn(a, scale=1.2), t=.9, rt=.35)
        beat(self, FadeIn(b, scale=1.2), FadeIn(kr("쉬는 중", 26, MUTE).next_to(b, DOWN, .15)), t=.9, rt=.35)
        fill(self, a, GRN)


class L2(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = indcirc(DOWN * .3, closed=True); self.add(D["all"])
        a = itag(D, "L1", r"10\,\mathrm{A}", GRN); b = itag(D, "L2", r"0\,\mathrm{A}", MUTE); self.add(a, b)
        beat(self, Transform(D["sw"][2], lever_to(D["sw"], False)), FadeIn(kr("t = 0 열림", 28, MUTE).next_to(D["sw"], LEFT, .25)), t=.9, rt=.5)
        beat(self, D["L1"].animate.set_stroke(YEL, width=8), D["L2"].animate.set_stroke(YEL, width=8), t=.8, rt=.4)
        c = card(kr("직렬 → 같은 전류", 34, YEL), YEL, .2).to_corner(UL, buff=.35)
        beat(self, FadeIn(c), t=.8, rt=.35)
        q = card(tex(r"10\,\mathrm{A}\;\overset{?}{=}\;0\,\mathrm{A}", 46, RED), RED, .2).next_to(c, RIGHT, .4)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.35)
        fill(self, q, RED)


class L3(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = indcirc(UP * 1.2, closed=False, s_dom=True); D["all"].scale(.82).move_to(UP * 1.3)
        beat(self, FadeIn(D["all"]), t=.8, rt=.4)
        src = card(kr("초기값 전원 3×10 = 30", 28, GRN), GRN, .15).to_corner(UL, buff=.3)
        beat(self, FadeIn(src), t=.8, rt=.35)
        f = tex(r"I(s)=\frac{100/s+30}{5s+25}", 56, INK).move_to(LEFT * 3.0 + DOWN * 1.9)
        beat(self, Write(f), t=1.2, rt=.7)
        g = tex(r"=\frac{4}{s}+\frac{2}{s+5}", 60, YEL).next_to(f, RIGHT, .25)
        beat(self, Write(g), t=1.1, rt=.6)
        fill(self, g)


def step_curves(o, k=.55):
    """i1: 10 → 6 → 4, i2: 0 → 6 → 4. 세로 1A = k."""
    o = P3(o); f = lambda t: 4 + 2 * np.exp(-5 * t)
    xs = np.linspace(0, 1.0, 80); sx = 4.6
    after = [o + np.array([1.2 + sx * t, k * f(t), 0]) for t in xs]
    i1 = VMobject(color=GRN, stroke_width=6).set_points_as_corners([o + UP * k * 10, o + UP * k * 10 + RIGHT * 1.2] + after)
    i2 = VMobject(color=BLU, stroke_width=6).set_points_as_corners([o + RIGHT * .02, o + RIGHT * 1.2] + after)
    j1 = DashedLine(o + RIGHT * 1.2 + UP * k * 10, o + RIGHT * 1.2 + UP * k * 6, color=GRN, stroke_width=4)
    j2 = DashedLine(o + RIGHT * 1.2, o + RIGHT * 1.2 + UP * k * 6, color=BLU, stroke_width=4)
    return i1, i2, j1, j2


class L4(Scene):
    def construct(self):
        self.add(step_tag(4))
        f = tex(r"i(t)=4+2e^{-5t}", 60, YEL).move_to(RIGHT * 3.6 + UP * 2.2)
        beat(self, Write(f), t=1.0, rt=.6)
        o = LEFT * 6.2 + DOWN * 3.0; ax = axes(o, 6.6, 6.0, "t", "i")
        beat(self, FadeIn(ax), t=.4, rt=.3)
        i1, i2, j1, j2 = step_curves(o)
        beat(self, Create(i1), Create(j1), FadeIn(tex(r"3\mathrm{H}:\,10\to6", 34, GRN).move_to(o + RIGHT * 3.6 + UP * 5.0)), t=1.2, rt=.8)
        beat(self, Create(i2), Create(j2), FadeIn(tex(r"2\mathrm{H}:\,0\to6", 34, BLU).move_to(o + RIGHT * 3.6 + UP * 1.8)), t=1.2, rt=.8)
        c = card(VGroup(tex(r"i(0^+)=6\,\mathrm{A}", 48, YEL), kr("순간 점프", 34, RED)).arrange(DOWN, buff=.2), YEL, .25).move_to(RIGHT * 3.6 + DOWN * .6)
        beat(self, FadeIn(c, scale=1.2), t=.9, rt=.4)
        fill(self, c)


class L5(Scene):
    def construct(self):
        self.add(step_tag(4))
        h = card(kr("자속 보존", 52, GRN), GRN, .25).move_to(UP * 2.5)
        beat(self, FadeIn(h, scale=1.2), t=.9, rt=.4)
        a = tex(r"3\cdot10", 60, GRN).move_to(LEFT * 4.2 + UP * .4)
        b = tex(r"+\;2\cdot0", 60, BLU).next_to(a, RIGHT, .3)
        c = tex(r"=\;5\cdot i(0^+)", 60, YEL).next_to(b, RIGHT, .3)
        beat(self, Write(a), t=.8, rt=.5); beat(self, Write(b), t=.8, rt=.5); beat(self, Write(c), t=.8, rt=.5)
        r = card(VGroup(tex(r"30=5\times6", 52, YEL), tex(r"i(0^+)=6\,\mathrm{A}", 52, YEL)).arrange(RIGHT, buff=.6), YEL, .25).move_to(DOWN * 1.6)
        beat(self, FadeIn(r, shift=UP * .2), t=.9, rt=.4)
        s = tex(r"\sum L\,i\;\text{일정}", 40, MUTE).next_to(r, DOWN, .3) if False else kr("ΣLi 일정", 32, MUTE).next_to(r, DOWN, .3)
        beat(self, FadeIn(s), t=.6, rt=.3)
        fill(self, r)


class L6(Scene):
    def construct(self):
        self.add(step_tag(4))
        f = tex(r"v_o=12\,\delta(t)+(60+10e^{-5t})", 52, INK).move_to(UP * 2.5)
        beat(self, Write(f), t=1.1, rt=.7)
        o = LEFT * 5.6 + DOWN * 2.8; ax = axes(o, 6.0, 4.2, "t", "v_o")
        beat(self, FadeIn(ax), t=.4, rt=.3)
        xs = np.linspace(0, 1.0, 60)
        tail = VMobject(color=BLU, stroke_width=6).set_points_as_corners([o + np.array([.05 + 5.0 * t, .035 * (60 + 10 * np.exp(-5 * t)), 0]) for t in xs])
        beat(self, Create(tail), t=.8, rt=.6)
        imp = impulse_arrow(o + RIGHT * .05, 3.9, RED, r"12\,\delta(t)")
        beat(self, GrowArrow(imp[0]), FadeIn(imp[1]), t=.9, rt=.5)
        c = card(VGroup(tex(r"v=L_2\frac{di}{dt}", 44, INK), tex(r"=2\times6\,\delta(t)", 44, RED)).arrange(DOWN, buff=.2), RED, .25).move_to(RIGHT * 3.8 + DOWN * .6)
        beat(self, FadeIn(c, shift=LEFT * .3), t=.9, rt=.4)
        fill(self, imp, RED)


class L7(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = indcirc(UP * .6, closed=False); D["all"].scale(.72).move_to(UP * 1.4); self.add(D["all"])
        a = card(VGroup(tex(r"i(\infty)=\frac{100}{10+15}", 46, INK), tex(r"=4\,\mathrm{A}", 52, GRN), kr("✓", 44, GRN)).arrange(RIGHT, buff=.25), GRN, .22).move_to(DOWN * 1.4)
        beat(self, FadeIn(a, shift=UP * .2), t=1.1, rt=.4)
        b = card(VGroup(tex(r"v_o(\infty)=15\times4=60\,\mathrm{V}", 42, INK), kr("✓", 44, GRN)).arrange(RIGHT, buff=.25), GRN, .2).next_to(a, DOWN, .3)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.4)
        fill(self, a, GRN)


# ================= 정리 =================
class E1(Scene):
    def construct(self):
        a = kr("연속성 규칙", 52, INK).move_to(UP * 1.8)
        beat(self, FadeIn(a), t=.7, rt=.3)
        l = card(kr("법칙", 48, MUTE), MUTE, .25).move_to(LEFT * 2.6 + DOWN * .4)
        beat(self, FadeIn(l), t=.6, rt=.3); beat(self, Create(cross(l)), t=.6, rt=.3)
        r = card(VGroup(kr("경험 규칙", 48, YEL), kr("rule of thumb", 28, MUTE)).arrange(DOWN, buff=.12), YEL, .25).move_to(RIGHT * 2.6 + DOWN * .4)
        beat(self, FadeIn(r, scale=1.2), t=.9, rt=.4)
        fill(self, r)


class E2(Scene):
    def construct(self):
        c = capacitor(LEFT * 5.4 + UP * 1.0, LEFT * 5.4 + DOWN * 1.0, YEL)[0]
        beat(self, Create(c), t=.6, rt=.4)
        g = VGroup(card(kr("저항 없이 연결", 34, INK), MUTE, .2), card(kr("임펄스 전류", 38, RED), RED, .2), card(kr("전하 보존 ΣCV", 38, YEL), YEL, .2)).arrange(RIGHT, buff=.55).move_to(RIGHT * .9)
        ar = VGroup(*[Arrow(g[i].get_right(), g[i + 1].get_left(), buff=.08, color=INK, stroke_width=5) for i in range(2)])
        beat(self, FadeIn(g[0]), t=.7, rt=.3); beat(self, GrowArrow(ar[0]), FadeIn(g[1]), t=.8, rt=.35); beat(self, GrowArrow(ar[1]), FadeIn(g[2]), t=.8, rt=.35)
        fill(self, g[2])


class E3(Scene):
    def construct(self):
        l = coil(LEFT * 5.4 + UP * 1.0, LEFT * 5.4 + DOWN * 1.0, GRN)
        beat(self, Create(l), t=.6, rt=.4)
        g = VGroup(card(kr("직렬로 강제", 34, INK), MUTE, .2), card(kr("임펄스 전압", 38, RED), RED, .2), card(kr("자속 보존 ΣLi", 38, GRN), GRN, .2)).arrange(RIGHT, buff=.55).move_to(RIGHT * .9)
        ar = VGroup(*[Arrow(g[i].get_right(), g[i + 1].get_left(), buff=.08, color=INK, stroke_width=5) for i in range(2)])
        beat(self, FadeIn(g[0]), t=.7, rt=.3); beat(self, GrowArrow(ar[0]), FadeIn(g[1]), t=.8, rt=.35); beat(self, GrowArrow(ar[1]), FadeIn(g[2]), t=.8, rt=.35)
        fill(self, g[2], GRN)


class Site(Scene):
    def construct(self):
        c = card(VGroup(kr("무료 사이트", 32, MUTE), kr("보이는 회로이론", 60, YEL)).arrange(DOWN, buff=.2), YEL, .45).move_to(UP * 1.2)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.5)
        items = VGroup(*[card(kr(t, 30, INK), MUTE, .18) for t in ("라플라스 변환", "s-영역 회로", "전달함수", "임펄스")]).arrange(RIGHT, buff=.25).move_to(DOWN * 1.4)
        for it in items:
            beat(self, FadeIn(it, shift=UP * .15), t=.6, rt=.3)
        fill(self, c)


class Next(Scene):
    def construct(self):
        a = card(kr("링크는 설명란에", 48, INK), INK, .35).move_to(UP * 1.6)
        beat(self, FadeIn(a, shift=UP * .2), t=1.1, rt=.5)
        eps = VGroup(*[card(kr(f"{n}편", 34, YEL if n == 5 else MUTE), YEL if n == 5 else MUTE, .2) for n in range(1, 6)]).arrange(RIGHT, buff=.3).move_to(DOWN * .6)
        beat(self, LaggedStart(*[FadeIn(e, shift=UP * .15) for e in eps], lag_ratio=.2), t=1.3, rt=1.0)
        b = kr("재생목록 '회로이론 한눈에'", 36, INK).move_to(DOWN * 2.2)
        beat(self, FadeIn(b), t=.8, rt=.35)
        fill(self, eps[4])


# ================= 쇼츠·릴스 전용 =================
class AQ(Scene):
    def construct(self):
        D = indcirc(DOWN * .4, closed=True); build_ind(self, D, .25)
        a = itag(D, "L1", r"10\,\mathrm{A}", GRN); b = itag(D, "L2", r"0\,\mathrm{A}", MUTE)
        beat(self, FadeIn(a), FadeIn(b), t=.5, rt=.3)
        beat(self, Transform(D["sw"][2], lever_to(D["sw"], False)), t=.5, rt=.35)
        beat(self, Transform(a, itag(D, "L1", r"6\,\mathrm{A}", YEL)), Transform(b, itag(D, "L2", r"6\,\mathrm{A}", YEL)), t=.7, rt=.4)
        q = card(kr("인덕터 전류가 튄다?", 40, RED), RED, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(q, scale=1.2), t=.7, rt=.35)
        fill(self, VGroup(a, b), YEL)


class BQ(Scene):
    def construct(self):
        D = capcirc(UP * .6 + LEFT * 2.6); D["all"].scale(.78).move_to(LEFT * 3.0 + DOWN * .2)
        beat(self, FadeIn(D["all"]), t=.6, rt=.4)
        beat(self, Transform(D["sw"][2], lever_to(D["sw"], True)), t=.5, rt=.3)
        b = bars(RIGHT * 2.6 + DOWN * 1.8, [50, 25], [ORG, ORG], ["전", "후"], r"\mu\mathrm{J}", 50, H=3.0, W=1.2, gap=1.0)
        beat(self, FadeIn(b), t=.8, rt=.4)
        q = card(kr("에너지 절반 증발?", 40, RED), RED, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(q, scale=1.2), t=.7, rt=.35)
        fill(self, b[1], RED)


class BHeat(Scene):
    def construct(self):
        R = resistor(LEFT * 2.0, RIGHT * 2.0, RED, 7).shift(UP * 1.0)
        beat(self, Create(R), FadeIn(tex("R", 48, RED).next_to(R, RIGHT, .3)), t=.7, rt=.4)
        waves = VGroup(*[sine(UP * (1.9 + .0) + RIGHT * x, .12, 1.5, .8, ORG).rotate(PI / 2) for x in (-1.2, 0, 1.2)])
        beat(self, Create(waves), R.animate.set_stroke(ORG, width=10), t=.9, rt=.5)
        c = card(VGroup(kr("열로 손실", 40, ORG), tex(r"25\,\mu\mathrm{J}", 52, ORG)).arrange(RIGHT, buff=.3), ORG, .22).move_to(DOWN * .6)
        beat(self, FadeIn(c, shift=UP * .2), t=.8, rt=.35)
        d = card(VGroup(tex(r"R\to0", 44, INK), kr("이어도 그대로", 36, INK)).arrange(RIGHT, buff=.25), MUTE, .2).move_to(DOWN * 2.2)
        beat(self, FadeIn(d), t=.8, rt=.35)
        fill(self, c, ORG)


class CQ(Scene):
    def construct(self):
        D = capcirc(DOWN * .3, closed=True); build_cap(self, D, .25)
        n = tex(r"R=0\,?", 52, RED).move_to(D["lr"])
        beat(self, Transform(D["lr"], n), D["R"].animate.set_stroke(width=9), t=.7, rt=.4)
        q = card(kr("전류는 어떻게 될까?", 40, YEL), YEL, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(q, scale=1.2), t=.7, rt=.35)
        fill(self, D["lr"], RED)


class DQ(Scene):
    def construct(self):
        f = tex(r"I(s)=5\times10^{-6}", 72, YEL).move_to(UP * .6)
        beat(self, Write(f), t=1.0, rt=.6)
        q = card(kr("답이 상수?!", 44, RED), RED, .22).move_to(DOWN * 1.4)
        beat(self, FadeIn(q, scale=1.3), t=.7, rt=.35)
        ok = card(kr("틀린 게 아니에요", 34, GRN), GRN, .2).next_to(q, DOWN, .35)
        beat(self, FadeIn(ok), t=.7, rt=.35)
        fill(self, f)


class DQ2(Scene):
    def construct(self):
        D = capcirc(DOWN * .2, closed=True, withR=False); self.add(D["all"])
        p = D["R"]
        dots = VGroup(*[Dot(radius=.1, color=YEL) for _ in range(6)])
        for k, d in enumerate(dots): d.move_to(p.get_start() + RIGHT * .15 * k)
        beat(self, FadeIn(dots), t=.4, rt=.2)
        beat(self, dots.animate.shift(RIGHT * (p.get_length() - .9)), t=.5, rt=.2)
        n1 = vtag(r"5\,\mathrm{V}", YEL).move_to(D["t1"]); n2 = vtag(r"5\,\mathrm{V}", YEL).move_to(D["t2"])
        beat(self, Transform(D["t1"], n1), Transform(D["t2"], n2), t=.7, rt=.3)
        c = card(VGroup(tex(r"5\,\mu\mathrm{C}", 48, YEL), kr("한순간에", 36, INK)).arrange(RIGHT, buff=.25), YEL, .2).to_edge(UP, buff=.35)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, c)


class DLine(Scene):
    def construct(self):
        a = card(VGroup(kr("시간 영역", 36, MUTE), kr("전압이 순간에 바뀐다?", 30, INK), kr("다루기 곤란", 34, RED)).arrange(DOWN, buff=.2), MUTE, .3).move_to(LEFT * 3.4)
        beat(self, FadeIn(a, shift=RIGHT * .2), t=.9, rt=.4)
        b = card(VGroup(kr("라플라스", 36, YEL), tex(r"I=C_eV_0", 44, INK), tex(r"\Rightarrow\;C_eV_0\,\delta(t)", 40, YEL)).arrange(DOWN, buff=.2), YEL, .3).move_to(RIGHT * 3.4)
        beat(self, FadeIn(b, shift=LEFT * .2), t=.9, rt=.4)
        c = card(kr("한 줄", 44, YEL), YEL, .2).next_to(b, UP, .3)
        beat(self, FadeIn(c, scale=1.3), t=.7, rt=.3)
        fill(self, b)


class EQ(Scene):
    def construct(self):
        a = VGroup(VGroup(capacitor(UP * .8, DOWN * .8, YEL)[0], tex("v_C", 44, YEL)).arrange(DOWN, buff=.2),
                   VGroup(coil(UP * .8, DOWN * .8, GRN), tex("i_L", 44, GRN)).arrange(DOWN, buff=.2)).arrange(RIGHT, buff=1.6).move_to(LEFT * 3.0 + DOWN * .2)
        beat(self, FadeIn(a), FadeIn(kr("연속", 40, INK).next_to(a, UP, .3)), t=.8, rt=.4)
        l = card(kr("법칙?", 52, INK), MUTE, .25).move_to(RIGHT * 3.4 + DOWN * .2)
        beat(self, FadeIn(l, scale=1.2), t=.6, rt=.3)
        beat(self, Create(cross(l)), t=.6, rt=.3)
        fill(self, l, RED)


class ETwo(Scene):
    def construct(self):
        a = card(VGroup(kr("커패시터", 34, YEL), kr("전하 보존", 48, YEL), tex(r"\sum CV", 44, INK)).arrange(DOWN, buff=.2), YEL, .3).move_to(LEFT * 3.2)
        b = card(VGroup(kr("인덕터", 34, GRN), kr("자속 보존", 48, GRN), tex(r"\sum L\,i", 44, INK)).arrange(DOWN, buff=.2), GRN, .3).move_to(RIGHT * 3.2)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.35); beat(self, FadeIn(b, shift=UP * .2), t=.8, rt=.35)
        fill(self, VGroup(a, b))
