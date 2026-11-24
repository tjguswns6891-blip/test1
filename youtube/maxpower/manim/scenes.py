# 최대 전력 전달 롱폼 모션그래픽. 16:9, 핵심은 가운데(세로 쇼츠에서도 씀). Y-Δ 편 형식.
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




# ---------- 최대 전력 전달 전용 ----------
def om(v, size=38, c=INK):
    return tex(rf"{v}\,\Omega", size, c)


def W_(v, size=56, c=YEL):
    return tex(rf"{v}\,\mathrm{{W}}", size, c)


def cross(m, c=RED):
    return Cross(m, stroke_color=c, stroke_width=7, scale_factor=1.1)


def info(label, val, c=YEL, size=56, lsize=28):
    """작은 제목 + 큰 값 카드."""
    v = val if isinstance(val, Mobject) else tex(val, size, c)
    return card(VGroup(kr(label, lsize, MUTE), v).arrange(DOWN, buff=.18), c, .25)


def var_arrow(R, c=GRN):
    """가변 저항 화살표 (부하를 바꿔 가며)."""
    ctr = R.get_center()
    return Arrow(ctr + DL * .75, ctr + UR * .75, buff=0, color=c, stroke_width=5, max_tip_length_to_length_ratio=.22)


def thev(o=ORIGIN, s=1.0, v=r"12\,\mathrm{V}", r=r"4\,\Omega", load=r"R_L", rcol=BLU, lcol=GRN, show_load=True):
    """테브난 등가 + 부하. 반환 dict: all, base, bat, R, RL, lv, lr, ll, lw(부하 전선), pts."""
    o = P3(o); W, H = 5.0 * s, 2.8 * s
    x0, x1, yt, yb = o[0] - W / 2, o[0] + W / 2, o[1] + H / 2, o[1] - H / 2
    bat = battery((x0, o[1]), YEL, s)
    R = resistor((x0 + .7 * s, yt), (x0 + 2.9 * s, yt), rcol)
    base = VGroup(wire((x0, o[1] + .18 * s), (x0, yt)), wire((x0, yt), (x0 + .7 * s, yt)), wire((x0 + 2.9 * s, yt), (x1 - .9 * s, yt)),
                  wire((x1 - .9 * s, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .18 * s)))
    ta, tb = term((x1 - .9 * s, yt)), term((x1 - .9 * s, yb))
    lw = VGroup(wire((x1 - .8 * s, yt), (x1, yt)), wire((x1, yb), (x1 - .8 * s, yb)))
    RL = resistor((x1, yt), (x1, yb), lcol)
    lv = tex(v, 38, YEL).next_to(bat, LEFT, .25); lr = tex(r, 38, rcol).next_to(R, UP, .3)
    ll = tex(load, 38, lcol).next_to(RL, RIGHT, .3)
    D = dict(bat=bat, R=R, RL=RL, lv=lv, lr=lr, ll=ll, lw=lw, base=base, terms=VGroup(ta, tb), pts=dict(x0=x0, x1=x1, yt=yt, yb=yb, o=o))
    D["src"] = VGroup(base, bat, R, lv, lr, ta, tb)
    D["ld"] = VGroup(lw, RL, ll)
    D["all"] = VGroup(D["src"], D["ld"]) if show_load else VGroup(D["src"])
    return D


def cur_arrow(D, txt=None, c=YEL):
    p = D["pts"]; s = (p["x1"] - p["x0"]) / 5.0
    a = Arrow((p["x0"] + 3.0 * s, p["yt"] + .5, 0), (p["x1"] - .1, p["yt"] + .5, 0), buff=0, color=c, stroke_width=5, max_tip_length_to_length_ratio=.18)
    g = VGroup(a)
    if txt: g.add(tex(txt, 36, c).next_to(a, UP, .12))
    return g


def build_thev(sc, D, t=.45, load=True):
    beat(sc, FadeIn(D["base"]), FadeIn(D["bat"]), FadeIn(D["terms"]), t=t, rt=.35)
    beat(sc, Create(D["R"]), FadeIn(D["lv"]), FadeIn(D["lr"]), t=t, rt=.4)
    if load:
        beat(sc, FadeIn(D["lw"]), Create(D["RL"]), FadeIn(D["ll"]), t=t, rt=.4)


def set_load(sc, D, txt, t=.6):
    new = tex(txt, 38, D["ll"].get_color()).next_to(D["RL"], RIGHT, .3)
    beat(sc, Transform(D["ll"], new), t=t, rt=.4)


PF = lambda r: 144 * r / (4 + r) ** 2


def pgraph(o=ORIGIN, w=8.0, h=4.0, ticks=(1, 2, 4, 8, 16)):
    """부하 저항(로그 눈금)-전력 그래프. 반환 dict: ax, curve, all, pt(r), lab(r)."""
    ax = Axes(x_range=[0, 8.8, 1], y_range=[0, 10.5, 3], x_length=w, y_length=h, tips=False,
              axis_config=dict(color=MUTE, stroke_width=3, include_ticks=False)).move_to(P3(o))
    X = lambda r: np.log2(r) + 2.4
    f = lambda x: PF(2 ** (x - 2.4))
    curve = ax.plot(f, x_range=[0, 8.8], color=YEL, stroke_width=6)
    tk = VGroup(*[Line(ax.c2p(X(r), 0) + UP * .1, ax.c2p(X(r), 0) + DOWN * .1, color=MUTE, stroke_width=3) for r in ticks])
    xl = VGroup(*[tex(str(r), 30, MUTE).next_to(ax.c2p(X(r), 0), DOWN, .18) for r in ticks])
    xlab = kr("부하 저항 (Ω, 로그 눈금)", 24, MUTE).next_to(ax.x_axis, DOWN, .62)
    ylab = kr("부하 전력 (W)", 24, MUTE).next_to(ax.y_axis, UP, .15)
    D = dict(ax=ax, curve=curve, f=f, X=X, all=VGroup(ax, tk, xl, xlab, ylab))
    D["p"] = lambda r: ax.c2p(X(r), PF(r))
    D["dot"] = lambda r, c=YEL: Dot(D["p"](r), radius=.11, color=c)
    D["lab"] = lambda r, c=INK, d=UP: tex(rf"{PF(r):g}\,\mathrm{{W}}", 30, c).next_to(D["p"](r), d, .18)
    return D


def real(o=ORIGIN, s=1.0, load=r"R_L = ?"):
    """시험 문제 회로: 24V - 8Ω(직렬) - 8Ω(세로) - 단자 a,b - 부하."""
    o = P3(o); x0, xa, xt, x1 = o[0] - 3.0 * s, o[0] + .2 * s, o[0] + 1.4 * s, o[0] + 2.8 * s
    yt, yb = o[1] + 1.4 * s, o[1] - 1.4 * s
    bat = battery((x0, o[1]), YEL, s)
    R1 = resistor((x0 + .5 * s, yt), (xa - .2 * s, yt), BLU); R2 = resistor((xa, yt), (xa, yb), BLU)
    base = VGroup(wire((x0, o[1] + .18 * s), (x0, yt)), wire((x0, yt), (x0 + .5 * s, yt)), wire((xa - .2 * s, yt), (xt, yt)),
                  wire((xt, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .18 * s)))
    terms = VGroup(term((xt, yt)), term((xt, yb)))
    tl = VGroup(tex("a", 30, MUTE).next_to(terms[0], UP, .12), tex("b", 30, MUTE).next_to(terms[1], DOWN, .12))
    RL = resistor((x1, yt), (x1, yb), GRN); lw = VGroup(wire((xt + .1, yt), (x1, yt)), wire((x1, yb), (xt + .1, yb)))
    lv = tex(r"24\,\mathrm{V}", 38, YEL).next_to(bat, LEFT, .25)
    l1 = om(8, 38, BLU).next_to(R1, UP, .3); l2 = om(8, 38, BLU).next_to(R2, LEFT, .3)
    ll = tex(load, 36, GRN).next_to(RL, RIGHT, .3)
    D = dict(bat=bat, R1=R1, R2=R2, RL=RL, lv=lv, l1=l1, l2=l2, ll=ll, base=base, terms=VGroup(terms, tl), lw=lw,
             pts=dict(x0=x0, xa=xa, xt=xt, x1=x1, yt=yt, yb=yb, o=o))
    D["src"] = VGroup(base, bat, R1, R2, lv, l1, l2, D["terms"]); D["ld"] = VGroup(lw, RL, ll)
    D["all"] = VGroup(D["src"], D["ld"])
    return D


def acth(o=ORIGIN, s=1.0, load=True):
    """교류 테브난: 10V - 4Ω - j3Ω(코일) - 부하(4Ω + -j3Ω 커패시터)."""
    o = P3(o); x0, x1 = o[0] - 3.0 * s, o[0] + 2.6 * s; yt, yb = o[1] + 1.4 * s, o[1] - 1.4 * s
    src = acsrc((x0, o[1]), YEL, .5 * s)
    R = resistor((x0 + .4 * s, yt), (x0 + 2.3 * s, yt), BLU); L = coil((x0 + 2.5 * s, yt), (x0 + 4.4 * s, yt), PUR)
    base = VGroup(wire((x0, o[1] + .5 * s), (x0, yt)), wire((x0, yt), (x0 + .4 * s, yt)), wire((x0 + 2.3 * s, yt), (x0 + 2.5 * s, yt)),
                  wire((x0 + 4.4 * s, yt), (x1, yt)), wire((x1, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .5 * s)))
    RLr = resistor((x1, yt), (x1, o[1] + .1 * s), GRN); RLc = capacitor((x1, o[1] + .1 * s), (x1, yb), ORG)[0]
    lv = tex(r"10\,\mathrm{V}", 36, YEL).next_to(src, LEFT, .2)
    lr = om(4, 36, BLU).next_to(R, UP, .3); lL = tex(r"j3\,\Omega", 36, PUR).next_to(L, UP, .3)
    lRr = om(4, 36, GRN).next_to(RLr, RIGHT, .3); lRc = tex(r"-j3\,\Omega", 36, ORG).next_to(RLc, RIGHT, .3)
    zc = card(tex(r"Z_L = ?", 40, GRN), GRN, .2).move_to((x1, o[1], 0))
    zq = VGroup(wire((x1, yt), zc.get_top()), wire(zc.get_bottom(), (x1, yb)), zc)
    D = dict(src=src, R=R, L=L, RLr=RLr, RLc=RLc, lv=lv, lr=lr, lL=lL, lRr=lRr, lRc=lRc, base=base, zq=zq, pts=dict(x0=x0, x1=x1, yt=yt, yb=yb, o=o))
    D["th"] = VGroup(base, src, R, L, lv, lr, lL)
    D["ld"] = VGroup(RLr, RLc, lRr, lRc)
    D["all"] = VGroup(D["th"], D["ld"]) if load else VGroup(D["th"], zq)
    return D


# ================= 인트로 =================
class Hook(Scene):
    def construct(self):
        D = thev(LEFT * 2.6 + DOWN * .2, 1.1); build_thev(self, D, .35)
        va = var_arrow(D["RL"]); beat(self, GrowArrow(va), t=.5, rt=.3)
        for v in (r"1\,\Omega", r"16\,\Omega", r"R_L = ?"):
            set_load(self, D, v, .55)
        q = card(VGroup(kr("부하 전력", 34, INK), kr("최대는 몇 Ω?", 46, YEL)).arrange(DOWN, buff=.18), YEL).move_to(RIGHT * 4.4 + UP * .4)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, q)


class Goal(Scene):
    def construct(self):
        G = pgraph(LEFT * 1.6 + DOWN * .3, 7.4, 4.2); self.add(G["all"])
        big = kr("클수록 좋다?", 40, MUTE).move_to(RIGHT * 4.6 + UP * 2.4)
        beat(self, Create(G["curve"]), FadeIn(big), t=1.0, rt=.8)
        beat(self, Create(cross(big)), t=.5, rt=.3)
        d = G["dot"](4, RED); beat(self, FadeIn(d, scale=1.6), t=.5, rt=.3)
        ans = card(VGroup(om(4, 64, YEL), kr("→", 48, INK), W_(9, 64, YEL)).arrange(RIGHT, buff=.25), YEL).move_to(RIGHT * 4.6 + DOWN * .2)
        beat(self, FadeIn(ans, shift=UP * .2), t=.9, rt=.4)
        fill(self, ans)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "부하 전력", BLU), ("2", "전력 그래프", PUR), ("3", "최대 조건", GRN), ("4", "실제 회로", ORG), ("5", "켤레 정합", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.0, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.0, rt=.8)
        fill(self, cards)


# ================= STEP 1 부하 전력 계산 =================
class K1(Scene):
    def construct(self):
        self.add(step_tag(1))
        o = LEFT * 4.7 + DOWN * .2
        box = RoundedRectangle(width=4.2, height=3.4, corner_radius=.25, color=MUTE, stroke_width=4).move_to(o)
        rs = VGroup(resistor(o + LEFT * 1.4 + UP * .9, o + LEFT * .2 + UP * .9, MUTE), resistor(o + RIGHT * .2 + UP * .9, o + RIGHT * 1.4 + UP * .9, MUTE),
                    resistor(o + LEFT * .6 + UP * .4, o + LEFT * .6 + DOWN * 1.0, MUTE), resistor(o + RIGHT * .8 + UP * .4, o + RIGHT * .8 + DOWN * 1.0, MUTE),
                    battery(o + LEFT * 1.5 + DOWN * .4, YEL, .7))
        beat(self, Create(box), FadeIn(rs), FadeIn(kr("어떤 회로든", 34, INK).next_to(box, UP, .25)), t=1.0, rt=.6)
        L = resistor(o + RIGHT * 2.8 + UP * 1.0, o + RIGHT * 2.8 + DOWN * 1.0, GRN)
        lw = VGroup(wire(o + RIGHT * 2.1 + UP * 1.0, o + RIGHT * 2.8 + UP * 1.0), wire(o + RIGHT * 2.1 + DOWN * 1.0, o + RIGHT * 2.8 + DOWN * 1.0))
        beat(self, FadeIn(lw), Create(L), FadeIn(kr("부하", 30, GRN).next_to(L, DOWN, .2)), t=.9, rt=.5)
        ar = Arrow(LEFT * .9, RIGHT * .5, buff=0, color=INK, stroke_width=5).shift(DOWN * .2)
        D = thev(RIGHT * 3.9 + DOWN * .2, .72, v=r"V_{th}", r=r"R_{th}")
        beat(self, GrowArrow(ar), FadeIn(D["all"]), t=1.0, rt=.6)
        t = card(kr("테브난 등가", 36, YEL), YEL, .2).next_to(D["all"], UP, .3)
        beat(self, FadeIn(t, shift=UP * .2), t=.8, rt=.4)
        fill(self, D["src"])


class K2(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = thev(LEFT * 2.4 + DOWN * .2, 1.1, v=r"V_{th}", r=r"R_{th}"); self.add(D["all"])
        beat(self, Transform(D["lv"], tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25)), t=.9, rt=.5)
        beat(self, Transform(D["lr"], om(4, 38, BLU).next_to(D["R"], UP, .3)), t=.9, rt=.5)
        va = var_arrow(D["RL"]); beat(self, GrowArrow(va), t=.6, rt=.3)
        c = card(VGroup(kr("부하 저항을", 34, INK), kr("바꿔 가며", 34, GRN)).arrange(DOWN, buff=.15), GRN, .25).move_to(RIGHT * 4.6 + UP * .3)
        beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, VGroup(D["RL"], va), GRN)


class K3(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = thev(LEFT * 2.9 + DOWN * .2, 1.0, r=r"4\,\Omega"); D["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25)); self.add(D["all"])
        ca = cur_arrow(D, "I"); beat(self, GrowArrow(ca[0]), FadeIn(ca[1]), t=.8, rt=.5)
        e1 = tex(r"I = \frac{12}{4 + R_L}", 52, INK).move_to(RIGHT * 3.6 + UP * 1.4)
        beat(self, Write(e1), t=1.2, rt=.8)
        e2 = tex(r"P = I^2 R_L", 60, YEL).move_to(RIGHT * 3.6 + DOWN * .6)
        beat(self, Write(e2), t=1.0, rt=.7)
        beat(self, FadeIn(kr("부하가 받는 전력", 30, MUTE).next_to(e2, DOWN, .3)), t=.6, rt=.3)
        fill(self, e2)


class K4(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = thev(LEFT * 2.9 + DOWN * .2, 1.0, r=r"4\,\Omega"); D["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25)); self.add(D["all"])
        set_load(self, D, r"1\,\Omega", .8)
        i = tex(r"I = \frac{12}{5} = 2.4\,\mathrm{A}", 46, INK).move_to(RIGHT * 3.6 + UP * 1.5)
        beat(self, Write(i), t=1.1, rt=.7)
        p = info("부하 전력", r"5.76\,\mathrm{W}").move_to(RIGHT * 3.6 + DOWN * .6)
        beat(self, FadeIn(p, shift=UP * .2), t=.9, rt=.4)
        fill(self, p)


class K5(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = thev(LEFT * 2.9 + DOWN * .4, 1.0, r=r"4\,\Omega"); D["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25)); self.add(D["all"])
        old = card(VGroup(om(1, 34, MUTE), tex(r"\to 5.76\,\mathrm{W}", 34, MUTE)).arrange(RIGHT, buff=.15), MUTE, .15).move_to(RIGHT * 3.6 + UP * 2.4)
        self.add(old)
        set_load(self, D, r"16\,\Omega", .8)
        i = tex(r"I = \frac{12}{20} = 0.6\,\mathrm{A}", 46, INK).move_to(RIGHT * 3.6 + UP * .9)
        beat(self, Write(i), t=1.1, rt=.7)
        p = info("부하 전력", r"5.76\,\mathrm{W}").move_to(RIGHT * 3.6 + DOWN * 1.3)
        beat(self, FadeIn(p, shift=UP * .2), t=.8, rt=.4)
        beat(self, old[0].animate.set_stroke(YEL), old[1].animate.set_color(YEL), FadeIn(kr("또 같다!", 34, RED).next_to(p, DOWN, .25)), t=.7, rt=.4)
        fill(self, VGroup(old, p))


class K6(Scene):
    def construct(self):
        self.add(step_tag(1))
        G = pgraph(LEFT * .8 + DOWN * .4, 8.2, 4.4); beat(self, FadeIn(G["all"]), t=.5, rt=.4)
        for r in (1, 16):
            beat(self, FadeIn(G["dot"](r), scale=1.5), FadeIn(G["lab"](r)), t=.7, rt=.3)
        q = tex("?", 90, RED).move_to(G["p"](4) + UP * .3)
        beat(self, FadeIn(q, scale=1.3), t=.7, rt=.3)
        c = card(kr("어딘가에 꼭대기", 38, YEL), YEL, .2).move_to(RIGHT * 4.8 + UP * 2.6)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, q, RED)


# ================= STEP 2 전력 그래프 =================
class G1(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = thev(LEFT * 2.9 + DOWN * .2, 1.0, r=r"4\,\Omega", show_load=False); D["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25)); self.add(D["src"])
        p = D["pts"]; sh = VGroup(wire((p["x1"] - .8, p["yt"]), (p["x1"], p["yt"]), GRN), wire((p["x1"], p["yt"]), (p["x1"], p["yb"]), GRN), wire((p["x1"], p["yb"]), (p["x1"] - .8, p["yb"]), GRN))
        beat(self, Create(sh), FadeIn(kr("0Ω (단락)", 32, GRN).next_to(sh, RIGHT, .25)), t=.9, rt=.5)
        ca = cur_arrow(D, r"3\,\mathrm{A}"); beat(self, GrowArrow(ca[0]), FadeIn(ca[1]), FadeIn(kr("전류 최대", 30, YEL).move_to(RIGHT * 4.0 + UP * 2.4)), t=.9, rt=.5)
        v = tex(r"V = 0", 52, RED).move_to(RIGHT * 4.0 + UP * .9); beat(self, Write(v), t=.8, rt=.5)
        pw = info("부하 전력", r"0\,\mathrm{W}", RED).move_to(RIGHT * 4.0 + DOWN * 1.0)
        beat(self, FadeIn(pw, shift=UP * .2), t=.8, rt=.4)
        fill(self, pw, RED)


class G2(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = thev(LEFT * 2.9 + DOWN * .2, 1.0, r=r"4\,\Omega", show_load=False); D["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25)); self.add(D["src"])
        lab = kr("∞ (개방)", 32, GRN).next_to(D["terms"], RIGHT, .8)
        beat(self, FadeIn(lab), Indicate(D["terms"], color=GRN), t=.9, rt=.6)
        p = D["pts"]
        vv = VGroup(tex("+", 40, YEL).next_to(D["terms"][0], RIGHT, .2), tex("-", 40, YEL).next_to(D["terms"][1], RIGHT, .2))
        beat(self, FadeIn(vv), FadeIn(tex(r"V = 12\,\mathrm{V}", 44, YEL).move_to(RIGHT * 4.0 + UP * 2.2)), t=.9, rt=.4)
        i = tex(r"I = 0", 52, RED).move_to(RIGHT * 4.0 + UP * .9); beat(self, Write(i), t=.8, rt=.5)
        pw = info("부하 전력", r"0\,\mathrm{W}", RED).move_to(RIGHT * 4.0 + DOWN * 1.0)
        beat(self, FadeIn(pw, shift=UP * .2), t=.8, rt=.4)
        fill(self, pw, RED)


class G3(Scene):
    def construct(self):
        self.add(step_tag(2))
        G = pgraph(LEFT * .6 + DOWN * .4, 8.6, 4.4); beat(self, FadeIn(G["all"]), t=.6, rt=.4)
        ax = G["ax"]
        l0 = VGroup(Dot(ax.c2p(0, 0), radius=.12, color=RED), kr("0Ω 쪽 → 0", 28, RED).next_to(ax.c2p(0, 0), UP + RIGHT * .3, .3))
        beat(self, FadeIn(l0), t=.8, rt=.4)
        l1 = VGroup(Dot(ax.c2p(8.8, 0), radius=.12, color=RED), kr("∞ 쪽 → 0", 28, RED).next_to(ax.c2p(8.8, 0), UP + LEFT * .3, .3))
        beat(self, FadeIn(l1), t=.8, rt=.4)
        q = tex("?", 90, YEL).move_to(G["p"](4) + DOWN * .6); beat(self, FadeIn(q, scale=1.3), t=.7, rt=.3)
        c = card(kr("점 찍어 보기", 36, YEL), YEL, .2).move_to(RIGHT * 4.8 + UP * 2.6); beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, q)


class G4(Scene):
    def construct(self):
        self.add(step_tag(2))
        G = pgraph(LEFT * .6 + DOWN * .4, 8.6, 4.4); self.add(G["all"])
        for r in (1, 2, 4, 8, 16):
            c = RED if r == 4 else YEL
            beat(self, FadeIn(G["dot"](r, c), scale=1.5), FadeIn(G["lab"](r, c if r == 4 else INK)), t=1.0, rt=.3)
        beat(self, Create(G["curve"]), t=1.0, rt=.8)
        fill(self, G["curve"])


class G5(Scene):
    def construct(self):
        G = pgraph(LEFT * .6 + DOWN * .4, 8.6, 4.4); self.add(step_tag(2), G["all"], G["curve"])
        d = G["dot"](4, RED); beat(self, FadeIn(d, scale=1.6), FadeIn(G["lab"](4, RED)), t=.8, rt=.4)
        vl = DashedLine(G["ax"].c2p(G["X"](4), 0), G["p"](4), color=RED, stroke_width=4)
        beat(self, Create(vl), t=.7, rt=.5)
        c = card(VGroup(tex(r"R_L = 4\,\Omega", 48, YEL), kr("= 테브난 저항", 34, INK)).arrange(DOWN, buff=.15), YEL, .22).move_to(RIGHT * 4.7 + UP * 2.4)
        beat(self, FadeIn(c, shift=UP * .2), t=.9, rt=.4)
        fill(self, c)


class G6(Scene):
    def construct(self):
        G = pgraph(LEFT * .6 + DOWN * .4, 8.6, 4.4); self.add(step_tag(2), G["all"], G["curve"])
        for (a, b), c in (((1, 16), BLU), ((2, 8), GRN)):
            l = DashedLine(G["p"](a), G["p"](b), color=c, stroke_width=4)
            lb = tex(rf"{PF(a):g}\,\mathrm{{W}}", 32, c).next_to(l, DOWN, .15)
            beat(self, FadeIn(G["dot"](a, c)), FadeIn(G["dot"](b, c)), Create(l), FadeIn(lb), t=1.1, rt=.6)
        e = tex(r"1 \times 16 = 2 \times 8 = 16 = 4^2", 44, YEL).to_edge(UP, buff=.5).shift(LEFT * .6)
        beat(self, Write(e), t=1.1, rt=.7)
        fill(self, e)


# ================= STEP 3 최대 전력 조건 =================
PEQ = r"P = \frac{V_{th}^2\, R_L}{(R_{th} + R_L)^2}"


class M1(Scene):
    def construct(self):
        self.add(step_tag(3))
        G = pgraph(LEFT * 3.6 + DOWN * .6, 5.4, 3.4, ticks=(1, 4, 16)); self.add(G["all"], G["curve"])
        e = tex(PEQ, 50, INK).move_to(RIGHT * 3.4 + UP * 1.6); beat(self, Write(e), t=1.2, rt=.8)
        tan = Line(G["p"](4) + LEFT * 1.3, G["p"](4) + RIGHT * 1.3, color=RED, stroke_width=5)
        beat(self, Create(tan), FadeIn(G["dot"](4, RED)), FadeIn(kr("기울기 0", 28, RED).next_to(tan, UP, .15)), t=1.0, rt=.6)
        d = tex(r"\frac{dP}{dR_L} = 0", 56, YEL).move_to(RIGHT * 3.4 + DOWN * .8); beat(self, Write(d), t=1.0, rt=.7)
        fill(self, d)


class M2(Scene):
    def construct(self):
        self.add(step_tag(3))
        e0 = tex(PEQ, 44, MUTE).move_to(UP * 2.3); self.add(e0)
        e = MathTex(r"\frac{dP}{dR_L} = V_{th}^2\,", r"\frac{R_{th} - R_L}{(R_{th} + R_L)^3}", font_size=58, color=INK).move_to(UP * .2)
        beat(self, Write(e), t=1.4, rt=1.0)
        hl = SurroundingRectangle(e[1][0:6], color=YEL, buff=.1, stroke_width=5)
        beat(self, Create(hl), t=.8, rt=.5)
        c = card(kr("분자만 남겨 보면", 34, YEL), YEL, .2).move_to(DOWN * 2.2)
        beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, hl)


class M3(Scene):
    def construct(self):
        self.add(step_tag(3))
        e = tex(r"R_{th} - R_L = 0", 56, MUTE).move_to(UP * 2.2); beat(self, FadeIn(e), t=.8, rt=.4)
        c = card(tex(r"R_L = R_{th}", 110, YEL), YEL, .4).move_to(DOWN * .1)
        beat(self, FadeIn(c, scale=1.2), t=1.0, rt=.5)
        t = kr("최대 전력 전달 정리", 48, GRN).next_to(c, DOWN, .45)
        beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        fill(self, c)


class M4(Scene):
    def construct(self):
        self.add(step_tag(3))
        e1 = tex(r"P_{max} = \frac{V_{th}^2}{4 R_{th}}", 64, INK).move_to(UP * 1.8); beat(self, Write(e1), t=1.3, rt=.9)
        e2 = tex(r"= \frac{12^2}{4 \times 4} = \frac{144}{16}", 56, INK).move_to(DOWN * .2); beat(self, Write(e2), t=1.3, rt=.9)
        a = card(W_(9, 80), YEL, .3).move_to(DOWN * 2.3); beat(self, FadeIn(a, scale=1.2), t=.9, rt=.4)
        fill(self, a)


def both9(sc, o=LEFT * 2.6 + DOWN * .2, s=1.05):
    D = thev(o, s, r=r"4\,\Omega", load=r"4\,\Omega"); D["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25))
    return D


class M5(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = both9(self); self.add(D["all"])
        ca = cur_arrow(D, r"1.5\,\mathrm{A}"); beat(self, GrowArrow(ca[0]), FadeIn(ca[1]), t=.8, rt=.5)
        g = card(VGroup(kr("부하", 28, MUTE), W_(9, 52, GRN)).arrange(DOWN, buff=.12), GRN, .2).next_to(D["ll"], RIGHT, .3)
        beat(self, FadeIn(g), t=.8, rt=.4)
        r = card(VGroup(kr("내부 저항", 28, MUTE), W_(9, 52, RED)).arrange(DOWN, buff=.12), RED, .2).next_to(D["R"], DOWN, .45)
        beat(self, D["R"].animate.set_color(RED), FadeIn(r), t=.9, rt=.5)
        beat(self, FadeIn(kr("안에서도 태운다", 34, RED).to_edge(DOWN, buff=.5)), t=.6, rt=.3)
        fill(self, r, RED)


def eff_bar(o=ORIGIN, w=8.0):
    o = P3(o)
    a = Rectangle(width=w / 2, height=1.0, fill_color=GRN, fill_opacity=.85, stroke_width=0).move_to(o + LEFT * w / 4)
    b = Rectangle(width=w / 2, height=1.0, fill_color=RED, fill_opacity=.85, stroke_width=0).move_to(o + RIGHT * w / 4)
    la = kr("부하 9W", 32, BG).move_to(a); lb = kr("내부 손실 9W", 32, BG).move_to(b)
    tot = kr("전원이 내는 18W", 30, MUTE).next_to(VGroup(a, b), UP, .25)
    return VGroup(a, la), VGroup(b, lb), tot


class B50(Scene):
    def construct(self):
        a, b, tot = eff_bar(UP * .6, 9.0)
        beat(self, FadeIn(tot), GrowFromEdge(a, LEFT), t=.8, rt=.5)
        beat(self, GrowFromEdge(b, LEFT), t=.8, rt=.5)
        c = card(VGroup(kr("효율", 40, INK), tex(r"50\%", 90, YEL)).arrange(RIGHT, buff=.3), YEL, .3).move_to(DOWN * 1.8)
        beat(self, FadeIn(c, scale=1.2), t=.9, rt=.4)
        fill(self, c)


class M6(Scene):
    def construct(self):
        self.add(step_tag(3))
        a, b, tot = eff_bar(UP * 2.0, 8.0)
        beat(self, FadeIn(tot), GrowFromEdge(a, LEFT), GrowFromEdge(b, LEFT), t=.9, rt=.6)
        e = card(VGroup(kr("효율", 34, INK), tex(r"50\%", 64, YEL)).arrange(RIGHT, buff=.25), YEL, .2).move_to(LEFT * 3.4 + DOWN * .6)
        beat(self, FadeIn(e), t=.8, rt=.4)
        g = card(VGroup(kr("전력망", 40, BLU), tex(r"R_L \gg R_{th}", 48, INK), kr("효율이 먼저", 32, GRN)).arrange(DOWN, buff=.2), BLU, .25).move_to(RIGHT * 3.0 + DOWN * 1.0)
        beat(self, FadeIn(g, shift=UP * .2), t=1.0, rt=.5)
        x = kr("최대 전력 조건 ✕", 30, RED).next_to(g, UP, .2)
        beat(self, FadeIn(x), t=.6, rt=.3)
        fill(self, g, BLU)


# ================= STEP 4 실제 회로 =================
class T1(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = real(LEFT * 1.6 + DOWN * .2)
        beat(self, FadeIn(D["base"]), FadeIn(D["bat"]), FadeIn(D["lv"]), t=.6, rt=.4)
        beat(self, Create(D["R1"]), FadeIn(D["l1"]), t=.6, rt=.4)
        beat(self, Create(D["R2"]), FadeIn(D["l2"]), FadeIn(D["terms"]), t=.6, rt=.4)
        beat(self, FadeIn(D["lw"]), Create(D["RL"]), FadeIn(D["ll"]), t=.7, rt=.4)
        q = card(kr("전력 최대?", 40, YEL), YEL, .2).move_to(RIGHT * 5.2 + UP * 2.4)
        beat(self, FadeIn(q, scale=1.2), t=.7, rt=.3)
        fill(self, q)


class T2(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = real(LEFT * 2.4 + DOWN * .2); self.add(D["all"])
        beat(self, FadeOut(D["ld"]), t=.7, rt=.5)
        p = D["pts"]
        vv = VGroup(tex("+", 40, YEL).next_to(D["terms"][0][0], RIGHT, .2), tex("-", 40, YEL).next_to(D["terms"][0][1], RIGHT, .2),
                    kr("개방 전압", 30, YEL).move_to((p["xt"] + 1.1, p["o"][1], 0)))
        beat(self, FadeIn(vv), t=.8, rt=.4)
        e = tex(r"24 \times \frac{8}{8 + 8}", 50, INK).move_to(RIGHT * 4.4 + UP * 1.6); beat(self, Write(e), t=1.0, rt=.7)
        a = info("테브난 전압", r"12\,\mathrm{V}").move_to(RIGHT * 4.4 + DOWN * .8)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        fill(self, a)


class T3(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = real(LEFT * 2.4 + DOWN * .2); self.add(D["src"])
        p = D["pts"]; sw = wire((p["x0"], p["o"][1] + .25), (p["x0"], p["o"][1] - .25), GRN, 6)
        beat(self, FadeOut(D["bat"]), FadeOut(D["lv"]), FadeIn(sw), FadeIn(kr("단락", 30, GRN).next_to(sw, LEFT, .25)), t=.9, rt=.5)
        look = Arrow((p["xt"] + 1.6, p["o"][1], 0), (p["xt"] + .25, p["o"][1], 0), buff=0, color=YEL, stroke_width=6)
        beat(self, GrowArrow(look), FadeIn(kr("들여다보기", 28, YEL).next_to(look, DOWN, .15)), t=.8, rt=.5)
        beat(self, D["R1"].animate.set_color(PUR), D["R2"].animate.set_color(PUR), t=.6, rt=.4)
        e = tex(r"8 \parallel 8", 54, INK).move_to(RIGHT * 4.6 + UP * 1.6); beat(self, Write(e), t=.8, rt=.5)
        a = info("테브난 저항", r"4\,\Omega", PUR).move_to(RIGHT * 4.6 + DOWN * .6)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        fill(self, a, PUR)


class T4(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = real(LEFT * 3.9 + DOWN * .2, .62); self.add(D["src"])
        ar = Arrow(LEFT * .9 + DOWN * .2, RIGHT * .5 + DOWN * .2, buff=0, color=INK, stroke_width=5)
        T = thev(RIGHT * 4.1 + DOWN * .2, .8, r=r"4\,\Omega", show_load=False); T["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(T["bat"], LEFT, .25))
        beat(self, GrowArrow(ar), FadeIn(T["src"]), t=1.0, rt=.6)
        beat(self, Indicate(T["lv"], color=YEL), Indicate(T["lr"], color=BLU), t=.8, rt=.6)
        c = card(kr("STEP 1 회로와 똑같다", 36, GRN), GRN, .2).to_edge(DOWN, buff=.45)
        beat(self, FadeIn(c, shift=UP * .2), t=.8, rt=.4)
        fill(self, T["src"], GRN)


class T5(Scene):
    def construct(self):
        self.add(step_tag(4))
        D = real(LEFT * 2.0 + DOWN * .2, 1.0, load=r"4\,\Omega"); self.add(D["src"])
        beat(self, FadeIn(D["lw"]), Create(D["RL"]), FadeIn(D["ll"]), t=.9, rt=.5)
        beat(self, Indicate(D["ll"], color=GRN, scale_factor=1.4), t=.7, rt=.5)
        a = info("부하 전력 최대", r"9\,\mathrm{W}", GRN, 70).move_to(RIGHT * 5.0 + UP * .4)
        beat(self, FadeIn(a, scale=1.2), t=.9, rt=.4)
        fill(self, a, GRN)


class T6(Scene):
    def construct(self):
        self.add(step_tag(4))
        h = kr("몇 Ω일 때 최대?", 44, INK).move_to(UP * 2.6); beat(self, FadeIn(h), t=.6, rt=.3)
        rows = [("①", "부하 떼고 개방 전압", YEL), ("②", "전원 끄고 들여다본 저항", PUR), ("③", "부하 = 테브난 저항", GRN)]
        g = VGroup(*[card(VGroup(kr(n, 36, c), kr(t, 36, INK)).arrange(RIGHT, buff=.3), c, .2) for n, t, c in rows]).arrange(DOWN, buff=.3, aligned_edge=LEFT).move_to(DOWN * .4)
        for r in g:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=.8, rt=.4)
        fill(self, g[2], GRN)


# ================= STEP 5 교류 켤레 정합 =================
class Z1(Scene):
    def construct(self):
        self.add(step_tag(5))
        D = acth(LEFT * 2.2 + DOWN * .3, .95, load=False)
        beat(self, FadeIn(D["base"]), FadeIn(D["src"]), FadeIn(D["lv"]), t=.6, rt=.4)
        beat(self, Create(D["R"]), FadeIn(D["lr"]), t=.6, rt=.4)
        beat(self, Create(D["L"]), FadeIn(D["lL"]), t=.6, rt=.4)
        z = tex(r"Z_{th} = 4 + j3\,\Omega", 46, INK).to_edge(UP, buff=.5).shift(LEFT * 1.5)
        beat(self, Write(z), t=.8, rt=.5)
        beat(self, FadeIn(D["zq"], scale=1.2), t=.7, rt=.4)
        fill(self, D["zq"], GRN)


def cplane(o, s=.55):
    o = P3(o)
    P = plane(o, 2.2)
    a = vec(o, o + np.array([4, 3, 0]) * s * .55, PUR); b = vec(o, o + np.array([4, -3, 0]) * s * .55, ORG)
    la = tex(r"4 + j3", 36, PUR).next_to(a.get_end(), RIGHT, .1); lb = tex(r"4 - j3", 36, ORG).next_to(b.get_end(), RIGHT, .1)
    return P, a, b, la, lb


class Z2(Scene):
    def construct(self):
        self.add(step_tag(5))
        D = acth(LEFT * 3.0 + DOWN * .3, .8); self.add(D["th"])
        P, a, b, la, lb = cplane(RIGHT * 3.6 + DOWN * .1)
        beat(self, FadeIn(P), GrowArrow(a), FadeIn(la), t=.9, rt=.5)
        m = DashedLine(a.get_end(), b.get_end(), color=MUTE, stroke_width=3)
        beat(self, Create(m), GrowArrow(b), FadeIn(lb), t=.9, rt=.5)
        beat(self, Create(D["RLr"]), Create(D["RLc"]), FadeIn(D["lRr"]), FadeIn(D["lRc"]), t=.9, rt=.5)
        c = card(kr("켤레 복소수", 36, ORG), ORG, .2).move_to(RIGHT * 3.6 + DOWN * 2.9)
        beat(self, FadeIn(c), t=.6, rt=.3)
        fill(self, VGroup(D["RLr"], D["RLc"]), ORG)


class Z3(Scene):
    def construct(self):
        self.add(step_tag(5))
        D = acth(LEFT * 2.6 + DOWN * .3, .9); self.add(D["all"])
        beat(self, D["L"].animate.set_stroke(width=8), D["RLc"].animate.set_stroke(width=8), Indicate(D["lL"], color=PUR), Indicate(D["lRc"], color=ORG), t=.9, rt=.6)
        e = tex(r"j3 + (-j3) = 0", 50, INK).move_to(RIGHT * 4.3 + UP * 2.2); beat(self, Write(e), t=.9, rt=.6)
        beat(self, Create(cross(D["lL"])), Create(cross(D["lRc"])), t=.7, rt=.4)
        a = info("순수 저항", r"4 + 4 = 8\,\Omega", GRN, 48).move_to(RIGHT * 4.3 + DOWN * .6)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        fill(self, a, GRN)


class Z4(Scene):
    def construct(self):
        self.add(step_tag(5))
        D = acth(LEFT * 3.2 + DOWN * .3, .8); self.add(D["all"])
        i = tex(r"I = \frac{10}{8} = 1.25\,\mathrm{A}", 46, INK).move_to(RIGHT * 3.9 + UP * 2.0); beat(self, Write(i), t=1.1, rt=.7)
        p = tex(r"P = 1.25^2 \times 4", 46, INK).move_to(RIGHT * 3.9 + UP * .5); beat(self, Write(p), t=1.0, rt=.7)
        a = info("부하 전력 최대", r"6.25\,\mathrm{W}", YEL, 64).move_to(RIGHT * 3.9 + DOWN * 1.6)
        beat(self, FadeIn(a, scale=1.2), t=.9, rt=.4)
        fill(self, a)


class Z5(Scene):
    def construct(self):
        self.add(step_tag(5))
        def row(y, c1, n1, c2, n2, m1, m2):
            a = card(VGroup(m1, kr(n1, 34, c1)).arrange(DOWN, buff=.2), c1, .25).move_to(LEFT * 3.4 + UP * y)
            b = card(VGroup(m2, kr(n2, 34, c2)).arrange(DOWN, buff=.2), c2, .25).move_to(RIGHT * 3.4 + UP * y)
            ar = Arrow(a.get_right(), b.get_left(), buff=.25, color=INK, stroke_width=5)
            return a, ar, b, kr("상쇄", 28, YEL).next_to(ar, UP, .1)
        L1 = coil((-1.0, 0), (1.0, 0), PUR); C1 = capacitor((-1.0, 0), (1.0, 0), ORG)[0]
        L2 = coil((-1.0, 0), (1.0, 0), PUR); C2 = capacitor((-1.0, 0), (1.0, 0), ORG)[0]
        r1 = row(1.4, PUR, "인덕터 성분 (+j)", ORG, "커패시터로", L1, C1)
        r2 = row(-1.6, ORG, "커패시터 성분 (−j)", PUR, "인덕터로", C2, L2)
        for r in (r1, r2):
            beat(self, FadeIn(r[0]), t=.7, rt=.4)
            beat(self, GrowArrow(r[1]), FadeIn(r[3]), FadeIn(r[2]), t=.9, rt=.5)
        fill(self, VGroup(r1[2], r2[2]))


class Z6(Scene):
    def construct(self):
        self.add(step_tag(5))
        t = card(kr("임피던스 정합", 52, YEL), YEL, .3).move_to(UP * 2.3); beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        spk = VGroup(Rectangle(width=.5, height=.7, color=INK, stroke_width=4), Polygon([.25, .35, 0], [.9, .8, 0], [.9, -.8, 0], [.25, -.35, 0], color=INK, stroke_width=4))
        ant = VGroup(Line(DOWN * .8, UP * .6, color=INK, stroke_width=5), Line(UP * .6, UP * .1 + LEFT * .5, color=INK, stroke_width=5), Line(UP * .6, UP * .1 + RIGHT * .5, color=INK, stroke_width=5))
        a = card(VGroup(spk, kr("앰프 → 스피커", 34, INK), om(8, 40, GRN)).arrange(DOWN, buff=.2), GRN, .3).move_to(LEFT * 3.2 + DOWN * .9)
        b = card(VGroup(ant, kr("안테나 · 케이블", 34, INK), om(50, 40, BLU)).arrange(DOWN, buff=.2), BLU, .3).move_to(RIGHT * 3.2 + DOWN * .9)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.4)
        beat(self, FadeIn(b, shift=UP * .2), t=1.0, rt=.4)
        fill(self, t)


# ================= 정리 =================
class E1(Scene):
    def construct(self):
        h = kr("부하 쪽에서 보면", 46, INK).move_to(UP * 2.6); beat(self, FadeIn(h), t=.7, rt=.4)
        D = thev(DOWN * .3, 1.1, v=r"V_{th}", r=r"R_{th}"); beat(self, FadeIn(D["all"]), t=.9, rt=.5)
        c = card(kr("테브난 등가부터", 40, YEL), YEL, .2).to_edge(DOWN, buff=.35); beat(self, FadeIn(c, shift=UP * .2), t=.8, rt=.4)
        fill(self, D["src"])


class E2(Scene):
    def construct(self):
        c1 = card(VGroup(kr("직류", 32, BLU), tex(r"R_L = R_{th}", 70, YEL)).arrange(DOWN, buff=.2), BLU, .3).move_to(UP * 1.4)
        beat(self, FadeIn(c1, shift=UP * .2), t=1.2, rt=.5)
        c2 = card(tex(r"P_{max} = \frac{V_{th}^2}{4 R_{th}}", 58, INK), MUTE, .3).move_to(DOWN * 1.6)
        beat(self, FadeIn(c2, shift=UP * .2), t=1.2, rt=.5)
        fill(self, c1)


class E3(Scene):
    def construct(self):
        c1 = card(VGroup(kr("교류 · 켤레 정합", 32, ORG), tex(r"Z_L = Z_{th}^{\,*}", 70, YEL)).arrange(DOWN, buff=.2), ORG, .3).move_to(LEFT * 3.4)
        beat(self, FadeIn(c1, shift=UP * .2), t=1.2, rt=.5)
        c2 = card(VGroup(kr("최대 전력일 때 효율", 32, RED), tex(r"50\%", 90, RED)).arrange(DOWN, buff=.2), RED, .3).move_to(RIGHT * 3.4)
        beat(self, FadeIn(c2, shift=UP * .2), t=1.2, rt=.5)
        fill(self, VGroup(c1, c2))


class Site(Scene):
    def construct(self):
        c = card(VGroup(kr("무료 사이트", 32, MUTE), kr("보이는 회로이론", 60, YEL)).arrange(DOWN, buff=.2), YEL, .45).move_to(UP * 1.2)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.5)
        items = VGroup(*[card(kr(t, 30, INK), MUTE, .18) for t in ("테브난", "최대 전력", "교류 전력", "페이저", "3상")]).arrange(RIGHT, buff=.25).move_to(DOWN * 1.4)
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
        D = thev(LEFT * 2.6 + DOWN * .2, 1.1, r=r"4\,\Omega", load=r"R_L = ?"); D["lv"].become(tex(r"12\,\mathrm{V}", 38, YEL).next_to(D["bat"], LEFT, .25))
        build_thev(self, D, .35)
        va = var_arrow(D["RL"]); beat(self, GrowArrow(va), t=.5, rt=.3)
        q = card(VGroup(kr("전력 최대는", 36, INK), kr("몇 Ω?", 56, YEL)).arrange(DOWN, buff=.15), YEL).move_to(RIGHT * 4.4 + UP * .4)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, q)


class AMax(Scene):
    def construct(self):
        D = both9(self, LEFT * 3.0 + DOWN * .2, 1.0); self.add(D["src"], D["lw"], D["RL"])
        D["ll"].set_color(GRN); beat(self, FadeIn(D["ll"], scale=1.4), t=.6, rt=.4)
        ca = cur_arrow(D, r"1.5\,\mathrm{A}"); beat(self, GrowArrow(ca[0]), FadeIn(ca[1]), t=.8, rt=.5)
        a = info("부하 전력", r"9\,\mathrm{W}", YEL, 80).move_to(RIGHT * 4.0 + DOWN * .1)
        beat(self, FadeIn(a, scale=1.2), t=.8, rt=.4)
        beat(self, FadeIn(kr("제일 크다", 36, GRN).next_to(a, DOWN, .3)), t=.6, rt=.3)
        fill(self, a)


class AAns(Scene):
    def construct(self):
        c = card(tex(r"R_L = R_{th}", 110, YEL), YEL, .4).move_to(UP * .6)
        beat(self, FadeIn(c, scale=1.2), t=1.0, rt=.5)
        t = kr("최대 전력 전달 정리", 52, GRN).next_to(c, DOWN, .5)
        beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        fill(self, c)


class BQ(Scene):
    def construct(self):
        a = card(VGroup(kr("전력 최대", 48, YEL)), YEL, .3).move_to(LEFT * 3.4 + UP * .6)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        ar = Arrow(LEFT * 1.0 + UP * .6, RIGHT * 1.0 + UP * .6, buff=0, color=INK, stroke_width=5)
        b = card(VGroup(kr("효율도 최고?", 48, INK)), INK, .3).move_to(RIGHT * 3.6 + UP * .6)
        beat(self, GrowArrow(ar), FadeIn(b), t=.8, rt=.4)
        x = cross(b); beat(self, Create(x), FadeIn(kr("아니에요", 44, RED).next_to(b, DOWN, .4)), t=.9, rt=.4)
        fill(self, b, RED)


class BSame(Scene):
    def construct(self):
        D = both9(self, LEFT * .4 + DOWN * .2, 1.15); self.add(D["all"])
        beat(self, D["R"].animate.set_color(RED), t=.5, rt=.3)
        ca = cur_arrow(D, r"1.5\,\mathrm{A}"); beat(self, GrowArrow(ca[0]), FadeIn(ca[1]), t=.8, rt=.5)
        p = D["pts"]
        a2 = Arrow((p["x1"] + 1.4, p["yt"] - .3, 0), (p["x1"] + 1.4, p["yb"] + .3, 0), buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(a2), t=.7, rt=.5)
        c = card(kr("같은 전류가 양쪽에", 38, YEL), YEL, .2).to_edge(DOWN, buff=.35)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, VGroup(D["R"], D["RL"]))


class C3(Scene):
    def construct(self):
        G = pgraph(LEFT * .6 + DOWN * .4, 8.6, 4.4); self.add(G["all"])
        for r in (1, 2, 4):
            c = RED if r == 4 else YEL
            beat(self, FadeIn(G["dot"](r, c), scale=1.5), FadeIn(G["lab"](r, c if r == 4 else INK)), t=1.0, rt=.3)
        part = G["ax"].plot(G["f"], x_range=[0, 4.4], color=YEL, stroke_width=6)
        beat(self, Create(part), t=.9, rt=.7)
        fill(self, part)


class DQ(Scene):
    def construct(self):
        D = real(LEFT * 1.8 + DOWN * .2)
        beat(self, FadeIn(D["src"]), t=.7, rt=.4)
        beat(self, FadeIn(D["lw"]), Create(D["RL"]), FadeIn(D["ll"]), t=.7, rt=.4)
        q = card(VGroup(kr("전력 최대?", 36, INK), kr("3줄 풀이", 50, YEL)).arrange(DOWN, buff=.15), YEL, .25).move_to(RIGHT * 5.2 + UP * 1.9)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, q)


class EQ(Scene):
    def construct(self):
        D = acth(LEFT * 2.2 + DOWN * .3, .95, load=False)
        beat(self, FadeIn(D["base"]), FadeIn(D["src"]), FadeIn(D["lv"]), Create(D["R"]), FadeIn(D["lr"]), t=.7, rt=.4)
        beat(self, Create(D["L"]), FadeIn(D["lL"]), t=.6, rt=.4)
        beat(self, FadeIn(D["zq"], scale=1.2), t=.6, rt=.3)
        c = card(kr("켤레 복소수", 40, ORG), ORG, .2).to_edge(UP, buff=.4).shift(RIGHT * 3.8)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, D["zq"], GRN)
