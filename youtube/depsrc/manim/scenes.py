# 종속 전원 롱폼 모션그래픽. 16:9, 핵심은 가운데(세로 쇼츠에서도 씀). 최대 전력 전달 편 형식.
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




# ---------- 종속 전원 전용 ----------
def om(v, size=38, c=INK):
    return tex(rf"{v}\,\Omega", size, c)


def cross(m, c=RED):
    return Cross(m, stroke_color=c, stroke_width=7, scale_factor=1.1)


def info(label, val, c=YEL, size=56, lsize=28):
    """작은 제목 + 큰 값 카드."""
    v = val if isinstance(val, Mobject) else tex(val, size, c)
    return card(VGroup(kr(label, lsize, MUTE), v).arrange(DOWN, buff=.18), c, .25)


def diamond(p, c=PUR, s=.6, kind="I", rev=False, sw=5):
    """종속 전원 기호(마름모). kind I: 안에 화살표(위로, rev 면 아래로) · V: +/−."""
    p = P3(p)
    poly = Polygon(p + UP * s, p + RIGHT * s, p + DOWN * s, p + LEFT * s, color=c, stroke_width=sw, fill_color=BG, fill_opacity=1)
    if kind == "I":
        a, b = (p + UP * s * .55, p + DOWN * s * .55) if rev else (p + DOWN * s * .55, p + UP * s * .55)
        inner = Arrow(a, b, buff=0, color=c, stroke_width=sw, max_tip_length_to_length_ratio=.4)
    else:
        inner = VGroup(tex("+", 30, c).move_to(p + UP * s * .4), tex("-", 34, c).move_to(p + DOWN * s * .4))
    return VGroup(poly, inner)


def isrc(p, c=YEL, r=.5, kind="I", sw=5):
    """독립 전원 기호(동그라미). kind I: 화살표 · V: +/−."""
    p = P3(p); circ = Circle(r, color=c, stroke_width=sw, fill_color=BG, fill_opacity=1).move_to(p)
    if kind == "I":
        inner = Arrow(p + DOWN * r * .55, p + UP * r * .55, buff=0, color=c, stroke_width=sw, max_tip_length_to_length_ratio=.4)
    else:
        inner = VGroup(tex("+", 28, c).move_to(p + UP * r * .4), tex("-", 32, c).move_to(p + DOWN * r * .4))
    return VGroup(circ, inner)


def dep(o=ORIGIN, s=1.0, gain=r"3i_x", load=r"R_L", show_load=True, rev=False, lcol=GRN, v=r"12\,\mathrm{V}", r=r"8\,\Omega"):
    """본편 회로: 12V - 8Ω(i_x) - 마디 a - 종속 전류원 3i_x(위로) - 단자 a,b - 부하.
    반환 dict: all, src, ld, base, bat, R, dep, lv, lr, lg, ix(화살표+글자), terms, tl, lw, RL, ll, pts."""
    o = P3(o); x0 = o[0] - 3.1 * s; xr0, xr1 = x0 + .6 * s, x0 + 2.4 * s; xa = x0 + 3.4 * s; xt = x0 + 4.7 * s; x1 = x0 + 5.7 * s
    yt, yb = o[1] + 1.4 * s, o[1] - 1.4 * s
    bat = battery((x0, o[1]), YEL, s)
    R = resistor((xr0, yt), (xr1, yt), BLU)
    dp = diamond((xa, o[1]), PUR, .55 * s, "I", rev)
    base = VGroup(wire((x0, o[1] + .18 * s), (x0, yt)), wire((x0, yt), (xr0, yt)), wire((xr1, yt), (xt, yt)),
                  wire((xa, yt), (xa, o[1] + .55 * s)), wire((xa, o[1] - .55 * s), (xa, yb)),
                  wire((xt, yb), (x0, yb)), wire((x0, yb), (x0, o[1] - .18 * s)), Dot((xa, yt, 0), radius=.07, color=INK), Dot((xa, yb, 0), radius=.07, color=INK))
    terms = VGroup(term((xt, yt)), term((xt, yb)))
    tl = VGroup(tex("a", 30, MUTE).next_to(terms[0], UP, .12), tex("b", 30, MUTE).next_to(terms[1], DOWN, .12))
    lv = tex(v, 36 * min(1, s + .2), YEL).next_to(bat, LEFT, .22); lr = tex(r, 36, BLU).next_to(R, UP, .28)
    lg = tex(gain, 36, PUR).next_to(dp, RIGHT, .18)
    ia = Arrow((xr0 + .2 * s, yt + .42 * s, 0), (xr1 - .2 * s, yt + .42 * s, 0), buff=0, color=ORG, stroke_width=4, max_tip_length_to_length_ratio=.2)
    ix = VGroup(ia, tex("i_x", 32, ORG).next_to(ia, UP, .08))
    RL = resistor((x1, yt), (x1, yb), lcol); lw = VGroup(wire((xt + .1 * s, yt), (x1, yt)), wire((x1, yb), (xt + .1 * s, yb)))
    ll = tex(load, 36, lcol).next_to(RL, RIGHT, .25)
    D = dict(bat=bat, R=R, dep=dp, lv=lv, lr=lr, lg=lg, ix=ix, terms=terms, tl=tl, base=base, RL=RL, lw=lw, ll=ll,
             pts=dict(x0=x0, xa=xa, xt=xt, x1=x1, yt=yt, yb=yb, o=o, s=s))
    D["src"] = VGroup(base, bat, R, dp, lv, lr, lg, ix, terms, tl)
    D["ld"] = VGroup(lw, RL, ll)
    D["all"] = VGroup(D["src"], D["ld"]) if show_load else VGroup(D["src"])
    return D


def build_dep(sc, D, t=.45, load=True):
    beat(sc, FadeIn(D["base"]), FadeIn(D["bat"]), FadeIn(D["lv"]), FadeIn(D["terms"]), FadeIn(D["tl"]), t=t, rt=.35)
    beat(sc, Create(D["R"]), FadeIn(D["lr"]), FadeIn(D["ix"]), t=t, rt=.4)
    beat(sc, FadeIn(D["dep"], scale=1.2), FadeIn(D["lg"]), t=t, rt=.4)
    if load:
        beat(sc, FadeIn(D["lw"]), Create(D["RL"]), FadeIn(D["ll"]), t=t, rt=.4)


def thev(o=ORIGIN, s=1.0, v=r"12\,\mathrm{V}", r=r"2\,\Omega", load=r"R_L", rcol=BLU, lcol=GRN, show_load=True):
    """테브난 등가 + 부하."""
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


def short_wire(D, c=GRN):
    p = D["pts"]; x = p["xt"] + .6 * p["s"]
    return VGroup(wire((p["xt"] + .1, p["yt"]), (x, p["yt"]), c, 6), wire((x, p["yt"]), (x, p["yb"]), c, 6), wire((x, p["yb"]), (p["xt"] + .1, p["yb"]), c, 6))


def varrow(x, y0, y1, txt, c=YEL, side=RIGHT):
    a = Arrow((x, y0, 0), (x, y1, 0), buff=0, color=c, stroke_width=5, max_tip_length_to_length_ratio=.2)
    return VGroup(a, tex(txt, 32, c).next_to(a, side, .1))


def rows(items, y=-.4, buff=.3):
    g = VGroup(*[card(VGroup(kr(n, 36, c), kr(t, 36, INK)).arrange(RIGHT, buff=.3), c, .2) for n, t, c in items]).arrange(DOWN, buff=buff, aligned_edge=LEFT).move_to(UP * y)
    return g


# ================= 인트로 =================
class Hook(Scene):
    def construct(self):
        D = dep(LEFT * 2.2 + DOWN * .2, 1.0, show_load=False); build_dep(self, D, .32, load=False)
        beat(self, D["dep"][0].animate.set_stroke(YEL, width=8), t=.5, rt=.3)
        q = card(VGroup(kr("테브난 저항", 34, INK), kr("저항만 합치면 ✕", 42, RED)).arrange(DOWN, buff=.18), RED).move_to(RIGHT * 4.5 + UP * .3)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, D["dep"], YEL)


class Goal(Scene):
    def construct(self):
        D = dep(LEFT * 2.4 + DOWN * .2, 1.0, show_load=False); self.add(D["src"])
        w = card(VGroup(kr("저항만 보면", 30, MUTE), om(8, 60, MUTE)).arrange(DOWN, buff=.12), MUTE, .22).move_to(RIGHT * 4.4 + UP * 1.6)
        beat(self, FadeIn(w), t=.9, rt=.4)
        beat(self, Create(cross(w)), t=.5, rt=.3)
        a = card(VGroup(kr("진짜 테브난 저항", 30, INK), om(2, 76, YEL)).arrange(DOWN, buff=.12), YEL, .25).move_to(RIGHT * 4.4 + DOWN * 1.2)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        fill(self, a)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "종속 전원", BLU), ("2", "노드 해석", PUR), ("3", "테브난 저항", GRN), ("4", "실수 셋", ORG), ("5", "어디에 쓰나", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 34, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.0, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.0, rt=.8)
        fill(self, cards)


# ================= STEP 1 종속 전원이란 =================
class Q1(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = dep(LEFT * 2.4 + DOWN * .2, 1.0, show_load=False); self.add(D["src"])
        beat(self, D["dep"][0].animate.set_stroke(YEL, width=8), t=.7, rt=.4)
        t = card(kr("종속 전원", 44, PUR), PUR, .22).move_to(RIGHT * 4.4 + UP * 2.0)
        beat(self, FadeIn(t, shift=UP * .2), t=.8, rt=.4)
        link = CurvedArrow(D["ix"][1].get_top() + UP * .1, D["lg"].get_top() + UP * .1, angle=-TAU / 5, color=ORG, stroke_width=4)
        beat(self, Create(link), t=.8, rt=.5)
        c = card(VGroup(kr("값이 다른 곳의", 30, INK), kr("전압·전류에 매여 있다", 30, ORG)).arrange(DOWN, buff=.12), ORG, .2).move_to(RIGHT * 4.4 + DOWN * 1.0)
        beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, D["dep"], YEL)


class Q2(Scene):
    def construct(self):
        self.add(step_tag(1))
        b = VGroup(isrc(LEFT * 3.4 + UP * .4, YEL, .75, "V"), tex(r"12\,\mathrm{V}", 44, YEL).move_to(LEFT * 3.4 + DOWN * 1.1))
        beat(self, FadeIn(b[0], scale=1.2), t=.8, rt=.4)
        beat(self, FadeIn(b[1]), t=.7, rt=.3)
        c = card(VGroup(kr("값이 정해져 있다", 30, INK), kr("그냥 12V", 36, YEL)).arrange(DOWN, buff=.12), YEL, .2).move_to(LEFT * 3.4 + DOWN * 2.4)
        beat(self, FadeIn(c), t=.8, rt=.4)
        t = card(kr("독립 전원", 48, YEL), YEL, .3).move_to(RIGHT * 3.2 + UP * 1.2)
        beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        d = VGroup(isrc(RIGHT * 2.0 + DOWN * 1.2, YEL, .5, "I"), isrc(RIGHT * 4.4 + DOWN * 1.2, YEL, .5, "V"), kr("동그라미", 28, MUTE).move_to(RIGHT * 3.2 + DOWN * 2.3))
        beat(self, FadeIn(d), t=.7, rt=.4)
        fill(self, t)


class Q3(Scene):
    def construct(self):
        self.add(step_tag(1))
        D = dep(LEFT * 2.4 + DOWN * .2, 1.0, show_load=False); self.add(D["src"])
        g = card(tex(r"3 \times i_x", 56, PUR), PUR, .25).move_to(RIGHT * 4.4 + UP * 1.8)
        beat(self, FadeIn(g, scale=1.2), Indicate(D["lg"], color=PUR), t=.9, rt=.5)
        beat(self, D["R"].animate.set_stroke(width=8), Indicate(D["ix"], color=ORG, scale_factor=1.3), t=.8, rt=.5)
        c = card(VGroup(tex("i_x", 40, ORG), kr("= 8Ω에 흐르는 전류", 30, INK)).arrange(RIGHT, buff=.2), ORG, .2).move_to(RIGHT * 4.4 + DOWN * .8)
        beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, D["ix"], ORG)


class Q4(Scene):
    def construct(self):
        self.add(step_tag(1))
        dp = diamond(LEFT * 3.6 + UP * .2, PUR, .9); lg = tex(r"3i_x", 44, PUR).next_to(dp, DOWN, .3)
        beat(self, FadeIn(dp), FadeIn(lg), t=.7, rt=.4)
        rows_ = []
        for y, a, b in ((1.3, "1", "3"), (-.6, "2", "6")):
            l = card(tex(rf"i_x = {a}\,\mathrm{{A}}", 40, ORG), ORG, .2).move_to(RIGHT * .6 + UP * y)
            ar = Arrow(l.get_right(), l.get_right() + RIGHT * 1.0, buff=.1, color=INK, stroke_width=5)
            r = card(tex(rf"{b}\,\mathrm{{A}}", 48, PUR), PUR, .2).next_to(ar, RIGHT, .15)
            beat(self, FadeIn(l), t=.6, rt=.3); beat(self, GrowArrow(ar), FadeIn(r), t=.7, rt=.4); rows_.append(r)
        c = card(kr("남이 정해 주는 전원", 36, YEL), YEL, .2).move_to(RIGHT * 2.0 + DOWN * 2.3)
        beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, VGroup(*rows_), PUR)


def kinds():
    items = [("전압 → 전압", r"\mu\, v_x", "V", BLU), ("전압 → 전류", r"g\, v_x", "I", GRN), ("전류 → 전압", r"r\, i_x", "V", ORG), ("전류 → 전류", r"\beta\, i_x", "I", PUR)]
    g = VGroup()
    for t, f, kd, c in items:
        g.add(card(VGroup(diamond(ORIGIN, c, .5, kd), tex(f, 38, c), kr(t, 26, INK)).arrange(DOWN, buff=.18), c, .25))
    return g.arrange(RIGHT, buff=.3).scale_to_fit_width(12.6)


class Q5(Scene):
    def construct(self):
        self.add(step_tag(1))
        h = kr("종속 전원 네 종류", 40, INK).move_to(UP * 2.7); beat(self, FadeIn(h), t=.6, rt=.3)
        g = kinds().move_to(DOWN * .3)
        for k in g:
            beat(self, FadeIn(k, shift=UP * .3), t=.85, rt=.4)
        fill(self, g)


class Q6(Scene):
    def construct(self):
        self.add(step_tag(1))
        g = kinds().scale(.55).move_to(UP * 2.3); self.add(g)
        e = MathTex("3", r"\times", "i_x", font_size=120, color=INK).move_to(DOWN * .2)
        e[0].set_color(YEL); e[2].set_color(ORG)
        beat(self, Write(e), t=1.0, rt=.7)
        a = card(kr("이득", 34, YEL), YEL, .18).next_to(e[0], DOWN, .5); b = card(kr("제어 변수", 34, ORG), ORG, .18).next_to(e[2], DOWN, .5)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        beat(self, FadeIn(b, shift=UP * .2), t=.8, rt=.4)
        beat(self, FadeIn(kr("이 둘만 찾으면 끝", 34, GRN).to_edge(DOWN, buff=.4)), t=.6, rt=.3)
        fill(self, e)


# ================= STEP 2 노드 해석 =================
def dep4(o=LEFT * 2.4 + DOWN * .2, s=1.0):
    return dep(o, s, load=r"4\,\Omega")


class N1(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = dep4(); build_dep(self, D, .5)
        p = D["pts"]
        vq = VGroup(tex("+", 36, YEL).next_to(D["terms"][0], LEFT, .15).shift(DOWN * .35), tex("-", 36, YEL).next_to(D["terms"][1], LEFT, .15).shift(UP * .35))
        q = card(VGroup(kr("부하 전압", 32, INK), tex(r"v = ?", 56, YEL)).arrange(DOWN, buff=.15), YEL, .25).move_to(RIGHT * 4.6 + UP * .3)
        beat(self, FadeIn(vq), FadeIn(q, scale=1.2), t=.9, rt=.4)
        fill(self, q)


class N2(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = dep4(LEFT * 2.6 + DOWN * .3, .95); self.add(D["all"]); p = D["pts"]
        vl = tex("v", 40, YEL).move_to((p["xa"] + .55, p["yt"] + .45, 0))
        beat(self, FadeIn(vl, scale=1.3), Indicate(D["base"][7], color=YEL, scale_factor=2.5), t=.8, rt=.5)
        a1 = varrow(p["xa"], p["o"][1] - .05, p["yt"] - .35, r"3i_x", PUR, LEFT)
        a2 = varrow(p["x1"], p["yt"] - .2, p["o"][1] + .25, r"\tfrac{v}{4}", GRN, RIGHT)
        beat(self, Indicate(D["ix"], color=ORG), GrowArrow(a1[0]), FadeIn(a1[1]), t=.8, rt=.5)
        beat(self, GrowArrow(a2[0]), FadeIn(a2[1]), t=.7, rt=.5)
        e = MathTex(r"i_x + 3i_x", "=", r"\frac{v}{4}", font_size=54, color=INK).move_to(RIGHT * 4.3 + UP * 1.3)
        e[0].set_color(ORG); e[2].set_color(GRN)
        beat(self, Write(e), t=1.0, rt=.7)
        c = card(kr("KCL: 들어온 만큼 나간다", 28, YEL), YEL, .18).next_to(e, DOWN, .4)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, e)


class N3(Scene):
    def construct(self):
        self.add(step_tag(2))
        e = MathTex(r"i_x + 3i_x", "=", r"\frac{v}{4}", font_size=64, color=INK).move_to(UP * 1.8)
        e[0].set_color(ORG); e[2].set_color(GRN); self.add(e)
        q = tex("?", 70, RED).next_to(e[0], UP, .15)
        beat(self, FadeIn(q, scale=1.4), t=.8, rt=.4)
        c = card(VGroup(kr("미지수가 둘", 32, INK), tex(r"v,\; i_x", 44, RED)).arrange(RIGHT, buff=.3), RED, .2).move_to(DOWN * .2)
        beat(self, FadeIn(c), t=.8, rt=.4)
        k = card(kr("제어 변수 식을 하나 더", 42, YEL), YEL, .3).move_to(DOWN * 2.0)
        beat(self, FadeIn(k, shift=UP * .2), t=.9, rt=.4)
        fill(self, k)


class N4(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = dep4(LEFT * 3.2 + DOWN * .3, .8); self.add(D["all"]); p = D["pts"]
        vl = tex("v", 34, YEL).move_to((p["xa"] + .5, p["yt"] + .4, 0)); self.add(vl)
        beat(self, D["R"].animate.set_stroke(width=8), Indicate(D["lv"], color=YEL), Indicate(vl, color=YEL), t=.8, rt=.5)
        e = MathTex("i_x", "=", r"\frac{12 - v}{8}", font_size=56, color=INK).move_to(RIGHT * 3.6 + UP * 1.6); e[0].set_color(ORG)
        beat(self, Write(e), t=1.0, rt=.7)
        k = MathTex(r"i_x + 3i_x", "=", r"\frac{v}{4}", font_size=44, color=MUTE).move_to(RIGHT * 3.6 + DOWN * .8)
        ar = Arrow(e.get_bottom(), k[0].get_top(), buff=.15, color=YEL, stroke_width=5)
        beat(self, FadeIn(k), GrowArrow(ar), t=.9, rt=.5)
        c = card(kr("미지수는 v 하나", 32, GRN), GRN, .18).next_to(k, DOWN, .35)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, e, ORG)


class N5(Scene):
    def construct(self):
        self.add(step_tag(2))
        e1 = tex(r"4 \cdot \frac{12 - v}{8} = \frac{v}{4}", 54, INK).move_to(UP * 2.0); beat(self, Write(e1), t=1.1, rt=.8)
        e2 = tex(r"24 - 2v = v", 54, INK).move_to(UP * .4); beat(self, Write(e2), t=1.0, rt=.7)
        a = card(tex(r"v = 8\,\mathrm{V}", 90, YEL), YEL, .35).move_to(DOWN * 1.6); beat(self, FadeIn(a, scale=1.2), t=1.0, rt=.5)
        fill(self, a)


class N6(Scene):
    def construct(self):
        self.add(step_tag(2))
        D = dep4(LEFT * 2.4 + DOWN * .2, 1.0); self.add(D["all"]); p = D["pts"]
        beat(self, Transform(D["ix"][1], tex(r"0.5\,\mathrm{A}", 32, ORG).next_to(D["ix"][0], UP, .08)), t=.8, rt=.5)
        a1 = varrow(p["xa"], p["o"][1] - .05, p["yt"] - .35, r"1.5\,\mathrm{A}", PUR, LEFT)
        beat(self, GrowArrow(a1[0]), FadeIn(a1[1]), t=.8, rt=.5)
        a2 = varrow(p["x1"], p["yt"] - .2, p["o"][1] + .25, r"2\,\mathrm{A}", GRN, RIGHT)
        beat(self, GrowArrow(a2[0]), FadeIn(a2[1]), t=.8, rt=.5)
        c = card(VGroup(tex(r"0.5 + 1.5 = 2\,\mathrm{A}", 40, INK), tex(r"2 \times 4 = 8\,\mathrm{V}", 40, YEL)).arrange(DOWN, buff=.15), YEL, .22).move_to(RIGHT * 4.3 + UP * 1.7)
        beat(self, FadeIn(c), t=.9, rt=.4)
        beat(self, FadeIn(kr("검산 ✓", 40, GRN).move_to(RIGHT * 4.3 + DOWN * .8)), t=.6, rt=.3)
        fill(self, c)


# ================= STEP 3 테브난 저항 =================
class T1(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = dep4(LEFT * 2.4 + DOWN * .2, 1.0); self.add(D["all"])
        beat(self, FadeOut(D["ld"]), t=.8, rt=.5)
        lab = kr("개방", 32, GRN).next_to(D["terms"], RIGHT, .5)
        beat(self, FadeIn(lab), Indicate(D["terms"], color=GRN), t=.8, rt=.5)
        x = cross(VGroup(D["terms"]), RED).scale(1.3)
        beat(self, Create(x), FadeIn(kr("전류 나갈 곳 없음", 30, RED).move_to(RIGHT * 4.6 + UP * 1.8)), t=.8, rt=.4)
        c = card(kr("개방 전압 = ?", 38, YEL), YEL, .2).move_to(RIGHT * 4.6 + DOWN * .9)
        beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, c)


class T2(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = dep(LEFT * 2.6 + DOWN * .3, .95, show_load=False); self.add(D["src"])
        e = MathTex(r"i_x + 3i_x = 0", r"\;\Rightarrow\; i_x = 0", font_size=46, color=INK).move_to(RIGHT * 4.0 + UP * 2.2); e[1].set_color(ORG)
        beat(self, Write(e[0]), t=.9, rt=.6); beat(self, Write(e[1]), t=.8, rt=.5)
        beat(self, Transform(D["ix"][1], tex("0", 34, ORG).next_to(D["ix"][0], UP, .08)), FadeIn(kr("전압 강하 0", 26, BLU).next_to(D["R"], DOWN, .2)), t=.8, rt=.5)
        a = info("개방 전압", r"12\,\mathrm{V}").move_to(RIGHT * 4.0 + DOWN * .6)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        fill(self, a)


class T3(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = dep(LEFT * 2.6 + DOWN * .3, .95, show_load=False); self.add(D["src"])
        w = card(VGroup(kr("전원 끄고 저항만", 28, MUTE), om(8, 56, MUTE)).arrange(DOWN, buff=.12), MUTE, .2).move_to(RIGHT * 4.2 + UP * 1.7)
        beat(self, FadeIn(w), t=.9, rt=.4)
        beat(self, Create(cross(w)), FadeIn(kr("틀렸어요", 36, RED).next_to(w, DOWN, .25)), t=.8, rt=.4)
        beat(self, D["dep"][0].animate.set_stroke(RED, width=8), t=.5, rt=.3)
        c = card(kr("종속 전원은 끄면 안 된다", 34, RED), RED, .2).move_to(RIGHT * 4.2 + DOWN * 1.4)
        beat(self, FadeIn(c, shift=UP * .2), t=.8, rt=.4)
        fill(self, D["dep"], RED)


class T4(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = dep(LEFT * 2.6 + DOWN * .3, .95, show_load=False); self.add(D["src"]); p = D["pts"]
        sw = short_wire(D); beat(self, Create(sw), FadeIn(kr("단락", 30, GRN).next_to(sw, RIGHT, .2)), t=.8, rt=.5)
        beat(self, Transform(D["ix"][1], tex(r"1.5\,\mathrm{A}", 32, ORG).next_to(D["ix"][0], UP, .08)), FadeIn(tex(r"\tfrac{12}{8}", 30, ORG).next_to(D["R"], DOWN, .15)), t=.9, rt=.5)
        a1 = varrow(p["xa"], p["o"][1] - .05, p["yt"] - .35, r"4.5\,\mathrm{A}", PUR, LEFT)
        beat(self, GrowArrow(a1[0]), FadeIn(a1[1]), t=.8, rt=.5)
        e = tex(r"1.5 + 4.5", 44, INK).move_to(RIGHT * 4.3 + UP * 1.8); beat(self, Write(e), t=.8, rt=.5)
        a = info("단락 전류", r"6\,\mathrm{A}", GRN).move_to(RIGHT * 4.3 + DOWN * .5)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        fill(self, a, GRN)


class T5(Scene):
    def construct(self):
        self.add(step_tag(3))
        e1 = tex(r"R_{th} = \frac{V_{oc}}{I_{sc}} = \frac{12}{6}", 60, INK).move_to(UP * 1.6); beat(self, Write(e1), t=1.3, rt=.9)
        a = card(om(2, 100, YEL), YEL, .4).move_to(DOWN * .9); beat(self, FadeIn(a, scale=1.2), t=1.0, rt=.5)
        w = om(8, 50, MUTE).move_to(RIGHT * 4.2 + DOWN * .9); beat(self, FadeIn(w), Create(cross(w)), t=.8, rt=.4)
        fill(self, a)


class T6(Scene):
    def construct(self):
        self.add(step_tag(3))
        D = dep(LEFT * 2.6 + DOWN * .3, .95, show_load=False); self.add(D["src"]); p = D["pts"]
        sv = wire((p["x0"], p["o"][1] + .25), (p["x0"], p["o"][1] - .25), GRN, 6)
        beat(self, FadeOut(D["bat"]), FadeOut(D["lv"]), FadeIn(sv), FadeIn(kr("독립 전원 끄고", 26, GRN).next_to(sv, LEFT, .2)), t=.9, rt=.5)
        ts = isrc((p["xt"] + .9, p["o"][1]), YEL, .45, "V")
        tw = VGroup(wire((p["xt"] + .1, p["yt"]), (p["xt"] + .9, p["yt"])), wire((p["xt"] + .9, p["yt"]), ts.get_top()), wire(ts.get_bottom(), (p["xt"] + .9, p["yb"])), wire((p["xt"] + .9, p["yb"]), (p["xt"] + .1, p["yb"])))
        beat(self, FadeIn(tw), FadeIn(ts, scale=1.2), FadeIn(tex(r"1\,\mathrm{V}", 32, YEL).next_to(ts, RIGHT, .15)), t=.9, rt=.5)
        ia = Arrow((p["xt"] + .9, p["yt"] + .8, 0), (p["xt"] + .9, p["yt"] + .15, 0), buff=0, color=ORG, stroke_width=5)
        beat(self, GrowArrow(ia), FadeIn(tex(r"0.5\,\mathrm{A}", 30, ORG).next_to(ia, RIGHT, .1)), t=.8, rt=.5)
        a = card(VGroup(kr("시험 전원", 28, MUTE), tex(r"R_{th} = \frac{1}{0.5} = 2\,\Omega", 44, YEL)).arrange(DOWN, buff=.15), YEL, .22).move_to(RIGHT * 4.2 + DOWN * 2.2)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        fill(self, a)


# ================= STEP 4 흔한 실수 셋 =================
class M1(Scene):
    def construct(self):
        self.add(step_tag(4))
        T = thev(LEFT * 2.8 + DOWN * .2, 1.0, load=r"4\,\Omega"); beat(self, FadeIn(T["src"]), t=.7, rt=.4)
        beat(self, FadeIn(T["lw"]), Create(T["RL"]), FadeIn(T["ll"]), t=.7, rt=.4)
        e = tex(r"12 \times \frac{4}{2 + 4}", 50, INK).move_to(RIGHT * 4.0 + UP * 1.7); beat(self, Write(e), t=1.0, rt=.7)
        a = info("부하 전압", r"8\,\mathrm{V}").move_to(RIGHT * 4.0 + DOWN * .5); beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        beat(self, FadeIn(kr("노드 해석과 같다 ✓", 32, GRN).to_edge(DOWN, buff=.4)), t=.7, rt=.3)
        fill(self, a)


class M2(Scene):
    def construct(self):
        self.add(step_tag(4))
        T = thev(LEFT * 2.8 + DOWN * .2, 1.0, load=r"2\,\Omega"); self.add(T["all"])
        beat(self, Indicate(T["ll"], color=GRN, scale_factor=1.4), Indicate(T["lr"], color=BLU, scale_factor=1.4), t=.8, rt=.5)
        c = card(tex(r"R_L = R_{th}", 44, INK), MUTE, .2).move_to(RIGHT * 4.0 + UP * 2.2); beat(self, FadeIn(c), t=.7, rt=.4)
        e = tex(r"\frac{12^2}{4 \times 2} = \frac{144}{8}", 48, INK).move_to(RIGHT * 4.0 + UP * .4); beat(self, Write(e), t=1.0, rt=.7)
        a = info("최대 전력", r"18\,\mathrm{W}", YEL, 64).move_to(RIGHT * 4.0 + DOWN * 1.7); beat(self, FadeIn(a, scale=1.2), t=.9, rt=.4)
        fill(self, a)


class M3(Scene):
    def construct(self):
        self.add(step_tag(4))
        h = card(kr("실수 ① 중첩할 때 종속 전원 끄기", 34, RED), RED, .2).to_edge(UP, buff=.45).shift(LEFT * .8); beat(self, FadeIn(h), t=.8, rt=.4)
        a = card(VGroup(isrc(ORIGIN, YEL, .5, "V"), kr("독립 전원", 30, YEL), kr("하나씩 켜고 끄기", 28, INK)).arrange(DOWN, buff=.18), YEL, .3).move_to(LEFT * 3.2 + DOWN * .6)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        b = card(VGroup(diamond(ORIGIN, PUR, .55), kr("종속 전원", 30, PUR), kr("항상 살려 둔다", 28, GRN)).arrange(DOWN, buff=.18), PUR, .3).move_to(RIGHT * 3.2 + DOWN * .6)
        beat(self, FadeIn(b, shift=UP * .2), t=.9, rt=.4)
        x = kr("끄기 ✕", 34, RED).next_to(b, UP, .2); beat(self, FadeIn(x), t=.6, rt=.3)
        fill(self, b, GRN)


class M4(Scene):
    def construct(self):
        self.add(step_tag(4))
        h = card(kr("실수 ② 저항만 합쳐서 테브난 저항", 34, RED), RED, .2).to_edge(UP, buff=.45).shift(LEFT * .8); beat(self, FadeIn(h), t=.8, rt=.4)
        w = om(8, 60, MUTE).move_to(LEFT * 3.4 + DOWN * .5); beat(self, FadeIn(w), Create(cross(w)), t=.8, rt=.4)
        ar = Arrow(LEFT * 1.6 + DOWN * .5, RIGHT * .2 + DOWN * .5, buff=0, color=INK, stroke_width=5)
        e = card(tex(r"R_{th} = \frac{V_{oc}}{I_{sc}}", 60, YEL), YEL, .3).move_to(RIGHT * 3.0 + DOWN * .5)
        beat(self, GrowArrow(ar), FadeIn(e, shift=UP * .2), t=1.0, rt=.5)
        beat(self, FadeIn(kr("종속 전원이 있으면 꼭", 30, GRN).next_to(e, DOWN, .3)), t=.6, rt=.3)
        fill(self, e)


class M5(Scene):
    def construct(self):
        self.add(step_tag(4))
        h = card(kr("실수 ③ 제어 변수 식 빼먹기", 34, RED), RED, .2).to_edge(UP, buff=.45).shift(LEFT * .8); beat(self, FadeIn(h), t=.8, rt=.4)
        a = card(VGroup(kr("미지수", 30, MUTE), tex("+1", 60, ORG)).arrange(DOWN, buff=.12), ORG, .3).move_to(LEFT * 2.6 + DOWN * .5)
        beat(self, FadeIn(a, shift=UP * .2), t=.8, rt=.4)
        ar = Arrow(a.get_right(), a.get_right() + RIGHT * 1.4, buff=.2, color=INK, stroke_width=5)
        b = card(VGroup(kr("식", 30, MUTE), tex("+1", 60, YEL)).arrange(DOWN, buff=.12), YEL, .3).next_to(ar, RIGHT, .2)
        beat(self, GrowArrow(ar), FadeIn(b, shift=UP * .2), t=.9, rt=.4)
        e = tex(r"i_x = \frac{12 - v}{8}", 40, ORG).to_edge(DOWN, buff=.5); beat(self, FadeIn(e), t=.7, rt=.4)
        fill(self, b)


class M6(Scene):
    def construct(self):
        self.add(step_tag(4))
        h = kr("이 셋만 피하면", 42, INK).move_to(UP * 2.6); beat(self, FadeIn(h), t=.6, rt=.3)
        g = rows([("①", "중첩에서 종속 전원 끄기 ✕", YEL), ("②", "저항만 합치기 ✕ → V_oc / I_sc", PUR), ("③", "제어 변수 식 빼먹기 ✕", ORG)], -.2)
        for r in g:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=.8, rt=.4)
        c = card(kr("보통 회로와 똑같이 풀린다", 34, GRN), GRN, .2).to_edge(DOWN, buff=.4); beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, c, GRN)


# ================= STEP 5 어디에 쓰이나 =================
def bjt(o=ORIGIN, s=1.0, c=INK):
    """NPN 트랜지스터 기호. 반환 dict: g, B, C, E (단자 점)."""
    o = P3(o)
    bar = Line(o + UP * .8 * s, o + DOWN * .8 * s, color=c, stroke_width=7)
    B = o + LEFT * 1.2 * s; C = o + RIGHT * .9 * s + UP * 1.3 * s; E = o + RIGHT * .9 * s + DOWN * 1.3 * s
    g = VGroup(bar, Line(B, o, color=c, stroke_width=5), Line(o + UP * .4 * s, C, color=c, stroke_width=5),
               Arrow(o + DOWN * .4 * s, E, buff=0, color=c, stroke_width=5, max_tip_length_to_length_ratio=.25),
               Circle(1.5 * s, color=MUTE, stroke_width=3).move_to(o))
    return dict(g=g, B=B, C=C, E=E)


class U1(Scene):
    def construct(self):
        self.add(step_tag(5))
        q = kr("종속 전원은 어디에?", 40, INK).move_to(UP * 2.6); beat(self, FadeIn(q), t=.7, rt=.4)
        T = bjt(LEFT * 2.6 + DOWN * .4, 1.0); beat(self, Create(T["g"]), t=1.0, rt=.8)
        lab = VGroup(kr("B", 26, MUTE).next_to(T["B"], LEFT, .1), kr("C", 26, MUTE).next_to(T["C"], UP, .1), kr("E", 26, MUTE).next_to(T["E"], DOWN, .1))
        beat(self, FadeIn(lab), t=.6, rt=.3)
        c = card(kr("트랜지스터", 52, YEL), YEL, .3).move_to(RIGHT * 3.2 + DOWN * .4); beat(self, FadeIn(c, scale=1.2), t=.9, rt=.4)
        fill(self, c)


class U2(Scene):
    def construct(self):
        self.add(step_tag(5))
        T = bjt(LEFT * 3.6 + DOWN * .3, 1.0); self.add(T["g"])
        ib = Arrow(T["B"] + LEFT * 1.3, T["B"] + LEFT * .2, buff=0, color=ORG, stroke_width=4, max_tip_length_to_length_ratio=.25)
        beat(self, GrowArrow(ib), FadeIn(tex(r"i_b", 32, ORG).next_to(ib, UP, .1)), FadeIn(kr("작은 전류", 24, ORG).next_to(ib, DOWN, .1)), t=.9, rt=.5)
        ic = Arrow(T["C"] + UP * 1.1, T["C"] + UP * .15, buff=0, color=PUR, stroke_width=7, max_tip_length_to_length_ratio=.3)
        beat(self, GrowArrow(ic), FadeIn(tex(r"i_c = \beta\, i_b", 36, PUR).next_to(ic, RIGHT, .15)), t=.9, rt=.5)
        ar = Arrow(LEFT * .9 + DOWN * .3, RIGHT * .5 + DOWN * .3, buff=0, color=INK, stroke_width=5)
        d = VGroup(diamond(RIGHT * 2.6 + DOWN * .3, PUR, .8), tex(r"\beta\, i_b", 40, PUR).move_to(RIGHT * 4.3 + DOWN * .3))
        beat(self, GrowArrow(ar), FadeIn(d, scale=1.2), t=.9, rt=.5)
        c = card(kr("전류가 전류를 정한다", 30, YEL), YEL, .18).move_to(RIGHT * 3.0 + DOWN * 2.3); beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, d[0])


def opamp(o=ORIGIN, s=1.0, c=INK):
    o = P3(o)
    tri = Polygon(o + LEFT * 1.2 * s + UP * 1.1 * s, o + LEFT * 1.2 * s + DOWN * 1.1 * s, o + RIGHT * 1.2 * s, color=c, stroke_width=5)
    pm = VGroup(tex("+", 30, c).move_to(o + LEFT * .8 * s + UP * .5 * s), tex("-", 34, c).move_to(o + LEFT * .8 * s + DOWN * .5 * s))
    ins = VGroup(Line(o + LEFT * 2.2 * s + UP * .5 * s, o + LEFT * 1.2 * s + UP * .5 * s, color=c, stroke_width=5),
                 Line(o + LEFT * 2.2 * s + DOWN * .5 * s, o + LEFT * 1.2 * s + DOWN * .5 * s, color=c, stroke_width=5))
    out = Line(o + RIGHT * 1.2 * s, o + RIGHT * 2.2 * s, color=c, stroke_width=5)
    return dict(g=VGroup(tri, pm, ins, out), vp=o + LEFT * 2.2 * s + UP * .5 * s, vm=o + LEFT * 2.2 * s + DOWN * .5 * s, vo=o + RIGHT * 2.2 * s)


class U3(Scene):
    def construct(self):
        self.add(step_tag(5))
        A = opamp(LEFT * 3.2 + DOWN * .3, 1.0); beat(self, Create(A["g"]), FadeIn(kr("연산 증폭기", 34, YEL).next_to(A["g"], UP, .3)), t=1.0, rt=.7)
        vd = tex(r"v_+ - v_-", 32, ORG).next_to(A["vp"], LEFT, .15).shift(DOWN * .5)
        beat(self, FadeIn(vd), t=.7, rt=.4)
        vo = tex(r"v_o = A\,(v_+ - v_-)", 36, PUR).next_to(A["vo"], RIGHT, .15)
        beat(self, Write(vo), t=.9, rt=.6)
        d = VGroup(diamond(RIGHT * 4.2 + DOWN * 1.6, PUR, .7, "V"), tex(r"A\, v_d", 36, PUR).next_to(RIGHT * 4.2 + DOWN * 1.6, RIGHT, .9))
        beat(self, FadeIn(d, scale=1.2), t=.8, rt=.4)
        c = card(kr("전압이 전압을 정한다", 30, YEL), YEL, .18).to_edge(DOWN, buff=.4).shift(LEFT * 2.0); beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, d[0])


class U4(Scene):
    def construct(self):
        self.add(step_tag(5))
        T = bjt(LEFT * 4.2 + DOWN * .3, .8); beat(self, FadeIn(T["g"]), t=.7, rt=.4)
        ar = Arrow(LEFT * 2.2 + DOWN * .3, LEFT * 1.0 + DOWN * .3, buff=0, color=INK, stroke_width=5)
        o = RIGHT * 2.2 + DOWN * .3
        rp = resistor(o + LEFT * 1.6 + UP * .9, o + LEFT * 1.6 + DOWN * .9, BLU); dp = diamond(o + RIGHT * 1.2, PUR, .55)
        wires = VGroup(wire(o + LEFT * 2.6 + UP * .9, o + RIGHT * 1.2 + UP * .9), wire(o + RIGHT * 1.2 + UP * .9, o + RIGHT * 1.2 + UP * .55),
                       wire(o + RIGHT * 1.2 + DOWN * .55, o + RIGHT * 1.2 + DOWN * .9), wire(o + LEFT * 2.6 + DOWN * .9, o + RIGHT * 2.6 + DOWN * .9), wire(o + RIGHT * 1.2 + UP * .9, o + RIGHT * 2.6 + UP * .9))
        model = VGroup(wires, rp, dp, tex(r"r_\pi", 30, BLU).next_to(rp, LEFT, .15), tex(r"g_m v_\pi", 30, PUR).next_to(dp, RIGHT, .15))
        beat(self, GrowArrow(ar), FadeIn(model), t=1.0, rt=.6)
        c = card(kr("소신호 모델", 44, YEL), YEL, .25).to_edge(UP, buff=.5).shift(RIGHT * 2.0); beat(self, FadeIn(c, shift=UP * .2), t=.9, rt=.4)
        beat(self, FadeIn(kr("트랜지스터 → 저항 + 종속 전원", 30, GRN).to_edge(DOWN, buff=.4)), t=.7, rt=.3)
        fill(self, dp)


class U5(Scene):
    def construct(self):
        self.add(step_tag(5))
        D = dep(LEFT * 2.6 + DOWN * .3, .95, gain=r"3i_x", show_load=False, rev=True); self.add(D["src"])
        beat(self, D["dep"][0].animate.set_stroke(RED, width=8), FadeIn(kr("거꾸로", 28, RED).next_to(D["dep"], LEFT, .15)), t=.8, rt=.5)
        e = MathTex(r"I_{sc} = 1.5 - 4.5 = -3\,\mathrm{A}", font_size=40, color=INK).move_to(RIGHT * 4.0 + UP * 2.0); beat(self, Write(e), t=1.0, rt=.7)
        a = card(VGroup(kr("테브난 저항", 28, MUTE), tex(r"\frac{12}{-3} = -4\,\Omega", 50, RED)).arrange(DOWN, buff=.15), RED, .25).move_to(RIGHT * 4.0 + DOWN * .5)
        beat(self, FadeIn(a, shift=UP * .2), t=1.0, rt=.4)
        beat(self, FadeIn(kr("음수!", 40, RED).next_to(a, DOWN, .25)), t=.6, rt=.3)
        fill(self, a, RED)


class U6(Scene):
    def construct(self):
        self.add(step_tag(5))
        a = card(VGroup(kr("음저항", 44, RED), kr("전력을 내놓는 저항", 30, INK)).arrange(DOWN, buff=.15), RED, .3).move_to(LEFT * 3.4 + UP * .8)
        beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        ax = taxis(RIGHT * .6 + DOWN * 1.4, 5.6, 1.5)
        xs = np.linspace(0, 5.4, 300)
        w = VMobject(color=YEL, stroke_width=5).set_points_smoothly([RIGHT * .6 + DOWN * 1.4 + np.array([x, .08 * np.exp(.5 * x) * np.sin(4 * x), 0]) for x in xs])
        beat(self, FadeIn(ax), Create(w), t=1.2, rt=1.0)
        b = card(kr("발진기", 44, YEL), YEL, .25).move_to(RIGHT * 3.6 + UP * 1.6); beat(self, FadeIn(b, scale=1.2), t=.8, rt=.4)
        c = kr("종속 전원이 있으면 이런 것도", 30, GRN).to_edge(DOWN, buff=.35); beat(self, FadeIn(c), t=.7, rt=.3)
        fill(self, b)


# ================= 정리 =================
class E1(Scene):
    def construct(self):
        dp = diamond(LEFT * 3.4 + UP * .3, PUR, 1.0); beat(self, FadeIn(dp, scale=1.2), t=.8, rt=.4)
        c = card(kr("종속 전원", 52, PUR), PUR, .3).move_to(RIGHT * 2.4 + UP * 1.2); beat(self, FadeIn(c, shift=UP * .2), t=.9, rt=.4)
        d = card(kr("값이 다른 곳의 전압·전류에 매여 있다", 32, INK), MUTE, .22).move_to(RIGHT * 2.4 + DOWN * .6); beat(self, FadeIn(d, shift=UP * .2), t=.9, rt=.4)
        fill(self, c, PUR)


class E2(Scene):
    def construct(self):
        c1 = card(VGroup(kr("풀 땐", 30, MUTE), kr("제어 변수 식 하나 더", 40, ORG)).arrange(DOWN, buff=.15), ORG, .3).move_to(UP * 1.4)
        beat(self, FadeIn(c1, shift=UP * .2), t=1.2, rt=.5)
        c2 = card(VGroup(kr("중첩에서도", 30, MUTE), kr("종속 전원은 끄지 않는다", 40, GRN)).arrange(DOWN, buff=.15), GRN, .3).move_to(DOWN * 1.4)
        beat(self, FadeIn(c2, shift=UP * .2), t=1.2, rt=.5)
        fill(self, VGroup(c1, c2))


class E3(Scene):
    def construct(self):
        c1 = card(VGroup(kr("테브난 저항", 30, MUTE), tex(r"R_{th} = \frac{V_{oc}}{I_{sc}}", 64, YEL)).arrange(DOWN, buff=.2), YEL, .3).move_to(LEFT * 3.2)
        beat(self, FadeIn(c1, shift=UP * .2), t=1.2, rt=.5)
        c2 = card(VGroup(kr("독립 전원이 없으면", 30, MUTE), kr("1V 시험 전원", 44, BLU)).arrange(DOWN, buff=.2), BLU, .3).move_to(RIGHT * 3.4)
        beat(self, FadeIn(c2, shift=UP * .2), t=1.2, rt=.5)
        fill(self, VGroup(c1, c2))


class Site(Scene):
    def construct(self):
        c = card(VGroup(kr("무료 사이트", 32, MUTE), kr("보이는 회로이론", 60, YEL)).arrange(DOWN, buff=.2), YEL, .45).move_to(UP * 1.2)
        beat(self, FadeIn(c, shift=UP * .2), t=1.2, rt=.5)
        items = VGroup(*[card(kr(t, 30, INK), MUTE, .18) for t in ("종속 전원", "노드 해석", "테브난", "중첩", "연산 증폭기")]).arrange(RIGHT, buff=.25).move_to(DOWN * 1.4)
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
        D = dep(LEFT * 2.2 + DOWN * .2, 1.0, show_load=False); build_dep(self, D, .32, load=False)
        beat(self, D["dep"][0].animate.set_stroke(YEL, width=8), t=.5, rt=.3)
        q = card(VGroup(kr("마름모 전원 =", 34, INK), kr("종속 전원", 52, PUR)).arrange(DOWN, buff=.15), PUR).move_to(RIGHT * 4.5 + UP * .3)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, D["dep"], YEL)


class AUse(Scene):
    def construct(self):
        T = bjt(LEFT * 3.6 + UP * .3, .85); A = opamp(RIGHT * 3.2 + UP * .3, .85)
        beat(self, Create(T["g"]), FadeIn(kr("트랜지스터", 34, YEL).next_to(T["g"], DOWN, .3)), t=.9, rt=.6)
        beat(self, Create(A["g"]), FadeIn(kr("연산 증폭기", 34, YEL).next_to(A["g"], DOWN, .3)), t=.9, rt=.6)
        c = card(VGroup(kr("= 종속 전원", 48, PUR)), PUR, .3).to_edge(DOWN, buff=.4); beat(self, FadeIn(c, scale=1.2), t=.9, rt=.4)
        fill(self, c, PUR)


class BQ(Scene):
    def construct(self):
        D = dep(LEFT * 2.2 + DOWN * .2, 1.0, show_load=False); build_dep(self, D, .32, load=False)
        w = card(VGroup(kr("테브난 저항", 30, INK), om(8, 56, MUTE), kr("?", 40, MUTE)).arrange(DOWN, buff=.1), MUTE, .2).move_to(RIGHT * 4.5 + UP * .3)
        beat(self, FadeIn(w, scale=1.2), t=.8, rt=.4)
        beat(self, Create(cross(w)), t=.6, rt=.3)
        fill(self, w, RED)


class CQ(Scene):
    def construct(self):
        h = card(kr("중첩 원리", 44, YEL), YEL, .25).move_to(UP * 2.3); beat(self, FadeIn(h), t=.7, rt=.4)
        a = VGroup(isrc(LEFT * 3.0 + DOWN * .5, YEL, .6, "V"), kr("하나씩 끈다", 28, INK).move_to(LEFT * 3.0 + DOWN * 1.8)); beat(self, FadeIn(a), t=.8, rt=.4)
        b = VGroup(diamond(RIGHT * 3.0 + DOWN * .5, PUR, .7), kr("종속 전원은?", 28, INK).move_to(RIGHT * 3.0 + DOWN * 1.8)); beat(self, FadeIn(b), t=.8, rt=.4)
        c = card(kr("예외!", 48, RED), RED, .25).move_to(RIGHT * 3.0 + UP * .9); beat(self, FadeIn(c, scale=1.3), t=.8, rt=.4)
        fill(self, b[0], RED)


class COff(Scene):
    def construct(self):
        h = kr("독립 전원 끄는 법", 40, INK).move_to(UP * 2.6); beat(self, FadeIn(h), t=.6, rt=.3)
        v = isrc(LEFT * 3.2 + UP * .5, YEL, .6, "V"); sw = wire(LEFT * 3.2 + UP * 1.3, LEFT * 3.2 + DOWN * .3, GRN, 7)
        beat(self, FadeIn(v), FadeIn(kr("전압원", 30, YEL).next_to(v, DOWN, .3)), t=.7, rt=.4)
        beat(self, FadeOut(v), FadeIn(sw), FadeIn(kr("단락", 36, GRN).next_to(sw, DOWN, .35)), t=.9, rt=.5)
        i = isrc(RIGHT * 3.2 + UP * .5, YEL, .6, "I"); op = VGroup(wire(RIGHT * 3.2 + UP * 1.3, RIGHT * 3.2 + UP * .9), wire(RIGHT * 3.2 + UP * .1, RIGHT * 3.2 + DOWN * .3), term(RIGHT * 3.2 + UP * .9), term(RIGHT * 3.2 + UP * .1))
        beat(self, FadeIn(i), FadeIn(kr("전류원", 30, YEL).next_to(i, DOWN, .3)), t=.7, rt=.4)
        beat(self, FadeOut(i), FadeIn(op), FadeIn(kr("개방", 36, GRN).next_to(op, DOWN, .35)), t=.9, rt=.5)
        fill(self, VGroup(sw, op), GRN)


class CChg(Scene):
    def construct(self):
        D = dep(LEFT * 2.4 + DOWN * .2, 1.0, show_load=False); self.add(D["src"])
        link = CurvedArrow(D["ix"][1].get_top() + UP * .1, D["lg"].get_top() + UP * .1, angle=-TAU / 5, color=ORG, stroke_width=4)
        beat(self, Create(link), FadeIn(kr("회로에 매여 있다", 28, ORG).move_to(RIGHT * 4.4 + UP * 2.2)), t=.9, rt=.5)
        x = cross(D["dep"], RED); beat(self, Create(x), t=.7, rt=.4)
        c = card(kr("끄면 회로 자체가 바뀐다", 32, RED), RED, .2).move_to(RIGHT * 4.4 + DOWN * .8); beat(self, FadeIn(c), t=.8, rt=.4)
        fill(self, c, RED)


class DQ(Scene):
    def construct(self):
        D = dep4(LEFT * 2.2 + DOWN * .2, 1.0); build_dep(self, D, .32)
        q = card(VGroup(kr("노드 해석", 34, INK), kr("3줄 풀이", 52, YEL)).arrange(DOWN, buff=.15), YEL, .25).move_to(RIGHT * 4.6 + UP * .3)
        beat(self, FadeIn(q, scale=1.2), t=.8, rt=.4)
        fill(self, q)


class EQ(Scene):
    def construct(self):
        e = tex(r"R_{th} < 0\;?", 90, RED).move_to(UP * .9); beat(self, FadeIn(e, scale=1.2), t=1.0, rt=.5)
        c = card(kr("테브난 저항이 음수?", 44, INK), INK, .3).move_to(DOWN * 1.2); beat(self, FadeIn(c, shift=UP * .2), t=.9, rt=.4)
        d = VGroup(diamond(RIGHT * 4.6 + DOWN * 1.2, PUR, .5), kr("종속 전원 때문", 26, PUR).move_to(RIGHT * 4.6 + DOWN * 2.3)); beat(self, FadeIn(d), t=.7, rt=.4)
        fill(self, e, RED)


class ERev(Scene):
    def construct(self):
        D = dep(LEFT * 2.4 + DOWN * .2, 1.0, show_load=False); self.add(D["src"])
        D2 = dep(LEFT * 2.4 + DOWN * .2, 1.0, show_load=False, rev=True)
        beat(self, Transform(D["dep"], D2["dep"]), t=1.0, rt=.6)
        beat(self, D["dep"][0].animate.set_stroke(RED, width=8), FadeIn(kr("거꾸로", 36, RED).move_to(RIGHT * 4.4 + UP * .3)), t=.8, rt=.4)
        fill(self, D["dep"], RED)


class EIsc(Scene):
    def construct(self):
        D = dep(LEFT * 2.6 + DOWN * .3, .95, show_load=False, rev=True); self.add(D["src"]); p = D["pts"]
        v = tex(r"V_{oc} = 12\,\mathrm{V}", 36, YEL).move_to(RIGHT * 4.2 + UP * 2.3); beat(self, FadeIn(v), t=.7, rt=.4)
        sw = short_wire(D); beat(self, Create(sw), Transform(D["ix"][1], tex(r"1.5\,\mathrm{A}", 32, ORG).next_to(D["ix"][0], UP, .08)), t=.8, rt=.5)
        a1 = varrow(p["xa"], p["yt"] - .35, p["o"][1] - .05, r"4.5\,\mathrm{A}", RED, LEFT); beat(self, GrowArrow(a1[0]), FadeIn(a1[1]), t=.8, rt=.5)
        a = info("단락 전류", r"1.5 - 4.5 = -3\,\mathrm{A}", RED, 40).move_to(RIGHT * 4.2 + DOWN * .6); beat(self, FadeIn(a, shift=UP * .2), t=.9, rt=.4)
        fill(self, a, RED)
