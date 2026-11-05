# 연산증폭기(두 규칙·반전·비반전·가산기·차동) 롱폼 모션그래픽. 16:9, 핵심은 가운데에 두어 세로 쇼츠에서도 쓴다.
# 장면 하나 = 문장 하나(long.json 에서 그 문장 시작에 붙임). 주파수 응답 편(freqresp/manim/scenes.py) 형식을 따른다.
# 끝까지 보게 만드는 4원칙: 1.5~2.5초마다 화면에 새 요소(내용으로 변화, 전환·반복 확대 없음), 4초 넘게 멈춘 화면 없음.
# 검산: 반전 1k·10k → −10배, 2V → 포화(±15V). 비반전 1k·9k → 10배, 0.5V → 5V. 가산 10k 전부 → −(1+2+3) = −6V.
#   차동 vo = R2/R1·(v2−v1). 센서(5V, 내부 10kΩ)에 1kΩ 부하 직결 → 5·1/11 = 0.45V, 버퍼 거치면 5V.
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
def resistor(a, b, c=INK, sw=5):
    a, b = P3(a), P3(b); d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0], 0])
    s0 = a + u * L * .25; seg = L * .5; pts = [a, s0]
    for i in range(6):
        pts.append(s0 + u * seg * (i + .5) / 6 + n * (.22 if i % 2 == 0 else -.22))
    pts += [s0 + u * seg, b]
    return VMobject(color=c, stroke_width=sw).set_points_as_corners(pts)


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


def sine(ax_or_pt, amp, freq, length, col, phase=0, n=200, sw=5):
    """가운데 pt, 길이 length, 진폭 amp(단위), freq 주기 수."""
    p = P3(ax_or_pt); xs = np.linspace(-length / 2, length / 2, n)
    return VMobject(color=col, stroke_width=sw).set_points_smoothly([p + np.array([x, amp * np.sin(2 * PI * freq * (x + length / 2) / length - phase), 0]) for x in xs])


def boxio(lab="회로", w=2.6, h=1.6, c=MUTE):
    b = RoundedRectangle(width=w, height=h, corner_radius=.2, color=c, stroke_width=5, fill_color="#181b21", fill_opacity=1)
    return VGroup(b, kr(lab, 40, INK))




def sum_rows(items, size=34):
    g = VGroup(*[VGroup(kr(a, size, MUTE), b).arrange(RIGHT, buff=.5) for a, b in items]).arrange(DOWN, buff=.55, aligned_edge=LEFT)
    return g.shift(DOWN * .2)


# ---------- 옵앰프 부품 ----------
def poly(pts, c=INK, w=4):
    return VMobject(color=c, stroke_width=w).set_points_as_corners([P3(p) for p in pts])


def jdot(p, c=INK):
    return Dot(P3(p), radius=.08, color=c)


def ground(p, c=INK):
    p = P3(p)
    return VGroup(*[Line(p + DOWN * .14 * k + LEFT * (.34 - .11 * k), p + DOWN * .14 * k + RIGHT * (.34 - .11 * k), color=c, stroke_width=5) for k in range(3)])


def opamp(c=ORIGIN, s=1.1, flip=False, col=INK):
    """삼각형 옵앰프. flip=False: − 위, + 아래 / flip=True: + 위, − 아래.
    반환 dict: g, tri, m(− 입력점), p(+ 입력점), o(출력점), sm, sp."""
    c = P3(c)
    tri = Polygon(c + (LEFT + UP) * s, c + (LEFT + DOWN) * s, c + RIGHT * s, color=col, stroke_width=5, fill_color="#181b21", fill_opacity=1)
    top, bot = c + LEFT * s + UP * .5 * s, c + LEFT * s + DOWN * .5 * s
    m, p = (bot, top) if flip else (top, bot)
    sm = tex("-", 50, col).move_to(m + RIGHT * .32 * s)
    sp = tex("+", 50, col).move_to(p + RIGHT * .32 * s)
    return dict(g=VGroup(tri, sm, sp), tri=tri, m=m, p=p, o=c + RIGHT * s, sm=sm, sp=sp)


def iarrow(a, b, c=YEL, lab=None, side=UP, size=36):
    ar = Arrow(P3(a), P3(b), buff=0, color=c, stroke_width=6, max_tip_length_to_length_ratio=.35)
    g = VGroup(ar)
    if lab is not None:
        g.add(tex(lab, size, c).next_to(ar, side, .12))
    return g


def inv(o=(0, 0), r1="R_1", rf="R_f", vin="v_{in}"):
    """반전 증폭기. 반환 dict: amp, tin, r1, wn, gnd, fb, outw, lab..., 좌표."""
    ox, oy = o
    A = opamp((ox + 1.3, oy - .4))
    m, p, out = A["m"], A["p"], A["o"]
    nx, xin, xo, yf = ox - .5, ox - 4.3, out[0] + .7, oy + 1.5
    D = dict(A=A, amp=A["g"], N=P3((nx, m[1])), xin=xin, nx=nx, xo=xo, yf=yf, m=m, p=p, out=out)
    D["tin"] = term((xin, m[1]))
    D["r1"] = resistor((xin + .1, m[1]), (nx, m[1]), BLU)
    D["wn"] = VGroup(wire((nx, m[1]), m), jdot((nx, m[1])))
    D["gnd"] = VGroup(poly([p, (nx, p[1]), (nx, p[1] - .55)]), ground((nx, p[1] - .55)))
    D["rf"] = resistor((nx, yf), (xo, yf), ORG)
    D["fb"] = VGroup(wire((nx, m[1]), (nx, yf)), D["rf"], poly([(xo, yf), (xo, out[1])]), jdot((xo, out[1])))
    D["outw"] = VGroup(wire(out, (xo + .9, out[1])), term((xo + .9, out[1])))
    D["lr1"] = tex(r1, 40, BLU).next_to(D["r1"], UP, .25)
    D["lrf"] = tex(rf, 40, ORG).next_to(D["rf"], UP, .25)
    D["lin"] = tex(vin, 40, BLU).next_to(D["tin"], LEFT, .15)
    D["lout"] = tex(r"v_{out}", 40, YEL).next_to(D["outw"][1], RIGHT, .15)
    D["all"] = VGroup(D["amp"], D["tin"], D["r1"], D["wn"], D["gnd"], D["fb"], D["outw"], D["lr1"], D["lrf"], D["lin"], D["lout"])
    return D


def noninv(o=(0, 0), r1="R_1", rf="R_f"):
    """비반전 증폭기 (+ 위). R1 은 아래 왼쪽→접지, Rf 는 아래 오른쪽→출력."""
    ox, oy = o
    A = opamp((ox + 1.3, oy + .3), flip=True)
    m, p, out = A["m"], A["p"], A["o"]
    nx, xin, xo, yj = ox - .5, ox - 3.9, out[0] + .7, oy - 1.4
    xg = ox - 3.0
    D = dict(A=A, amp=A["g"], N=P3((nx, m[1])), J=P3((nx, yj)), xin=xin, nx=nx, xo=xo, yj=yj, m=m, p=p, out=out)
    D["tin"] = term((xin, p[1]))
    D["win"] = wire((xin + .1, p[1]), p, BLU, 5)
    D["wn"] = VGroup(poly([m, (nx, m[1]), (nx, yj)]), jdot((nx, yj)))
    D["r1"] = resistor((nx, yj), (xg, yj), BLU)
    D["g1"] = VGroup(wire((xg, yj), (xg, yj - .45)), ground((xg, yj - .45)))
    D["rf"] = resistor((nx, yj), (xo, yj), ORG)
    D["fb"] = VGroup(D["rf"], poly([(xo, yj), (xo, out[1])]), jdot((xo, out[1])))
    D["outw"] = VGroup(wire(out, (xo + .9, out[1])), term((xo + .9, out[1])))
    D["lr1"] = tex(r1, 40, BLU).next_to(D["r1"], DOWN, .3)
    D["lrf"] = tex(rf, 40, ORG).next_to(D["rf"], DOWN, .3)
    D["lin"] = tex(r"v_{in}", 40, BLU).next_to(D["tin"], LEFT, .15)
    D["lout"] = tex(r"v_{out}", 40, YEL).next_to(D["outw"][1], RIGHT, .15)
    D["all"] = VGroup(D["amp"], D["tin"], D["win"], D["wn"], D["r1"], D["g1"], D["fb"], D["outw"], D["lr1"], D["lrf"], D["lin"], D["lout"])
    return D


def follower(o=(0, 0)):
    ox, oy = o
    A = opamp((ox + .9, oy + .3), flip=True)
    m, p, out = A["m"], A["p"], A["o"]
    nx, xin, xo, yb = ox - .9, ox - 3.4, out[0] + .7, oy - 1.2
    D = dict(A=A, amp=A["g"], m=m, p=p, out=out, xo=xo, yb=yb, nx=nx)
    D["tin"] = term((xin, p[1]))
    D["win"] = wire((xin + .1, p[1]), p, BLU, 5)
    D["fb"] = VGroup(poly([(xo, out[1]), (xo, yb), (nx, yb), (nx, m[1]), m], YEL, 5), jdot((xo, out[1]), YEL))
    D["outw"] = VGroup(wire(out, (xo + .9, out[1])), term((xo + .9, out[1])))
    D["lin"] = tex(r"v_{in}", 40, BLU).next_to(D["tin"], LEFT, .15)
    D["lout"] = tex(r"v_{out}", 40, YEL).next_to(D["outw"][1], RIGHT, .15)
    D["all"] = VGroup(D["amp"], D["tin"], D["win"], D["fb"], D["outw"], D["lin"], D["lout"])
    return D


def summer(o=(0, 0), labs=("v_1", "v_2", "v_3"), rl=("R_1", "R_2", "R_3")):
    ox, oy = o
    A = opamp((ox + 1.6, oy - .4))
    m, p, out = A["m"], A["p"], A["o"]
    nx, bx, xin, xo, yf = ox - .2, ox - .9, ox - 4.4, out[0] + .7, oy + 1.9
    ys = [m[1] + 1.0, m[1], m[1] - 1.0]
    cols = [BLU, GRN, PUR]
    D = dict(A=A, amp=A["g"], N=P3((nx, m[1])), m=m, p=p, out=out, ys=ys, bx=bx, nx=nx, xin=xin, xo=xo, yf=yf, cols=cols)
    D["ins"] = VGroup()
    for y, l, r, c in zip(ys, labs, rl, cols):
        D["ins"].add(VGroup(term((xin, y)), resistor((xin + .1, y), (bx, y), c), tex(l, 36, c).next_to(P3((xin, y)), LEFT, .2),
                            tex(r, 30, c).move_to(P3(((xin + bx) / 2, y - .38)))))
    D["bus"] = VGroup(wire((bx, ys[0]), (bx, ys[2])), *[jdot((bx, y)) for y in ys[:1] + ys[2:]], jdot((bx, m[1])), wire((bx, m[1]), m), jdot((nx, m[1])))
    D["gnd"] = VGroup(poly([p, (nx + .3, p[1]), (nx + .3, p[1] - .5)]), ground((nx + .3, p[1] - .5)))
    D["rf"] = resistor((nx, yf), (xo, yf), ORG)
    D["fb"] = VGroup(wire((nx, m[1]), (nx, yf)), D["rf"], poly([(xo, yf), (xo, out[1])]), jdot((xo, out[1])))
    D["lrf"] = tex("R_f", 36, ORG).next_to(D["rf"], UP, .2)
    D["outw"] = VGroup(wire(out, (xo + .8, out[1])), term((xo + .8, out[1])))
    D["lout"] = tex(r"v_{out}", 40, YEL).next_to(D["outw"][1], RIGHT, .15)
    D["all"] = VGroup(D["amp"], D["ins"], D["bus"], D["gnd"], D["fb"], D["lrf"], D["outw"], D["lout"])
    return D


def diffamp(o=(0, 0)):
    ox, oy = o
    A = opamp((ox + 1.4, oy - .2))
    m, p, out = A["m"], A["p"], A["o"]
    nx, xin, xo, yf = ox - .5, ox - 4.2, out[0] + .7, oy + 1.6
    D = dict(A=A, amp=A["g"], m=m, p=p, out=out, nx=nx, xin=xin, xo=xo, yf=yf)
    D["in1"] = VGroup(term((xin, m[1])), resistor((xin + .1, m[1]), (nx, m[1]), BLU), wire((nx, m[1]), m), jdot((nx, m[1])),
                      tex("v_1", 38, BLU).next_to(P3((xin, m[1])), LEFT, .2), tex("R_1", 34, BLU).move_to(P3(((xin + nx) / 2, m[1] + .45))))
    D["in2"] = VGroup(term((xin, p[1])), resistor((xin + .1, p[1]), (nx, p[1]), GRN), wire((nx, p[1]), p), jdot((nx, p[1])),
                      tex("v_2", 38, GRN).next_to(P3((xin, p[1])), LEFT, .2), tex("R_1", 34, GRN).move_to(P3(((xin + nx) / 2, p[1] - .45))))
    D["r4"] = VGroup(resistor((nx, p[1]), (nx, p[1] - 1.4), GRN), ground((nx, p[1] - 1.4)), tex("R_2", 34, GRN).move_to(P3((nx - .55, p[1] - .75))))
    D["rf"] = resistor((nx, yf), (xo, yf), ORG)
    D["fb"] = VGroup(wire((nx, m[1]), (nx, yf)), D["rf"], poly([(xo, yf), (xo, out[1])]), jdot((xo, out[1])), tex("R_2", 36, ORG).next_to(D["rf"], UP, .2))
    D["outw"] = VGroup(wire(out, (xo + .8, out[1])), term((xo + .8, out[1])))
    D["lout"] = tex(r"v_{out}", 40, YEL).next_to(D["outw"][1], RIGHT, .15)
    D["all"] = VGroup(D["amp"], D["in1"], D["in2"], D["r4"], D["fb"], D["outw"], D["lout"])
    return D


def noisy(pt, length, amp, freq, namp, col, seed=3, n=260, sig=True, sw=4):
    rng = np.random.default_rng(seed); p = P3(pt)
    xs = np.linspace(-length / 2, length / 2, n)
    nz = np.convolve(rng.normal(0, 1, n + 6), np.ones(4) / 4, "same")[3:n + 3]
    nz = nz / np.abs(nz).max()
    ys = (amp * np.sin(2 * PI * freq * (xs + length / 2) / length) if sig else 0 * xs) + namp * nz
    return VMobject(color=col, stroke_width=sw).set_points_as_corners([p + np.array([x, y, 0]) for x, y in zip(xs, ys)])


# ================= 인트로 =================
class Hook(Scene):
    """칩 하나 + 저항 두 개 → 0.5V 가 5V 로 (정확히 10배)."""
    def construct(self):
        C = noninv((-.2, -.6), "1\\,k\\Omega", "9\\,k\\Omega")
        C["all"].scale(.8, about_point=ORIGIN).shift(DOWN * .5)
        beat(self, FadeIn(C["amp"]), t=.9, rt=.5)
        beat(self, FadeIn(VGroup(C["tin"], C["win"], C["wn"], C["g1"], C["outw"], C["fb"][1:], C["lin"], C["lout"])),
             Create(C["r1"]), Create(C["rf"]), FadeIn(C["lr1"]), FadeIn(C["lrf"]), t=1.1, rt=.7)
        si = sine(LEFT * 4.3 + UP * 2.4, .14, 2, 3.0, BLU); so = sine(RIGHT * 4.1 + UP * 2.2, 1.0, 2, 3.0, YEL, sw=6)
        beat(self, Create(si), FadeIn(tex(r"0.5\,\mathrm{V}", 40, BLU).next_to(si, DOWN, .3)), t=1.1, rt=.6)
        beat(self, Create(so), FadeIn(tex(r"5\,\mathrm{V}", 44, YEL).next_to(so, LEFT, .3)), t=1.1, rt=.7)
        x = tex(r"\times 10", 90, YEL).move_to(UP * 2.3)
        beat(self, Write(x), t=.8, rt=.5)
        pulse(self, x, t=1.4)


class Goal(Scene):
    """연산증폭기 = 옵앰프, 규칙 두 개."""
    def construct(self):
        A = opamp(UP * 1.5, 1.0)
        beat(self, Create(A["tri"]), FadeIn(A["sm"]), FadeIn(A["sp"]), t=.9, rt=.6)
        t = VGroup(kr("연산증폭기", 48, YEL), kr("Op-Amp · 옵앰프", 30, MUTE)).arrange(DOWN, buff=.15).next_to(A["tri"], RIGHT, .7)
        beat(self, FadeIn(t, shift=LEFT * .3), t=1.2, rt=.5)
        c1 = card(VGroup(kr("규칙 1", 30, BLU), kr("입력 전류 = 0", 38, INK)).arrange(DOWN, buff=.2), BLU)
        c2 = card(VGroup(kr("규칙 2", 30, GRN), tex(r"v_+ = v_-", 52, INK)).arrange(DOWN, buff=.2), GRN)
        VGroup(c1, c2).arrange(RIGHT, buff=.8).shift(DOWN * 1.6)
        beat(self, FadeIn(c1, shift=UP * .3), t=1.2, rt=.5)
        beat(self, FadeIn(c2, shift=UP * .3), t=1.1, rt=.5)
        pulse(self, VGroup(c1, c2), t=1.4)


class Roadmap(Scene):
    def construct(self):
        items = [("1", "두 규칙", BLU), ("2", "반전", PUR), ("3", "비반전", GRN), ("4", "가산기", ORG), ("5", "차동", RED)]
        cards = VGroup(*[card(VGroup(kr("STEP " + n, 26, MUTE), kr(t, 36, c)).arrange(DOWN, buff=.2), c, .28) for n, t, c in items])
        cards.arrange(RIGHT, buff=.25).scale_to_fit_width(13).shift(UP * .2)
        for k in cards:
            beat(self, FadeIn(k, shift=UP * .3), t=1.2, rt=.4)
        arrow = Arrow(cards[0].get_bottom() + DOWN * .3, cards[4].get_bottom() + DOWN * .3, buff=0, color=YEL, stroke_width=5)
        beat(self, GrowArrow(arrow), t=1.8, rt=1.0)


# ================= STEP 1 두 규칙 =================
class O1(Scene):
    """삼각형 기호: − 입력, + 입력, 출력."""
    def construct(self):
        self.add(step_tag(1, BLU))
        A = opamp(ORIGIN + DOWN * .2, 1.5)
        beat(self, Create(A["tri"]), t=1.0, rt=.8)
        lm = VGroup(wire(A["m"] + LEFT * 1.2, A["m"]), kr("− 입력", 34, RED).next_to(A["m"] + LEFT * 1.2, LEFT, .2))
        beat(self, FadeIn(A["sm"]), Create(lm[0]), FadeIn(lm[1]), t=1.3, rt=.5)
        lp = VGroup(wire(A["p"] + LEFT * 1.2, A["p"]), kr("+ 입력", 34, BLU).next_to(A["p"] + LEFT * 1.2, LEFT, .2))
        beat(self, FadeIn(A["sp"]), Create(lp[0]), FadeIn(lp[1]), t=1.3, rt=.5)
        lo = VGroup(wire(A["o"], A["o"] + RIGHT * 1.2), kr("출력", 34, YEL).next_to(A["o"] + RIGHT * 1.2, RIGHT, .2))
        beat(self, Create(lo[0]), FadeIn(lo[1]), t=1.2, rt=.5)
        pulse(self, A["tri"], t=1.4)


class O2(Scene):
    """두 입력의 차이를 수십만 배."""
    def construct(self):
        self.add(step_tag(1, BLU))
        A = opamp(LEFT * .3 + UP * .6, 1.2)
        self.add(A["g"], wire(A["m"] + LEFT * 1, A["m"]), wire(A["p"] + LEFT * 1, A["p"]), wire(A["o"], A["o"] + RIGHT * .8))
        vm = tex(r"v_-", 44, RED).next_to(A["m"] + LEFT * 1, LEFT, .15); vp = tex(r"v_+", 44, BLU).next_to(A["p"] + LEFT * 1, LEFT, .15)
        beat(self, FadeIn(vm), FadeIn(vp), t=1.0, rt=.4)
        d = tex(r"v_+ - v_-", 50, INK).move_to(DOWN * 1.6 + LEFT * 3.4)
        small = Arrow(d.get_right() + RIGHT * .1, d.get_right() + RIGHT * .6, buff=0, color=BLU, stroke_width=5)
        beat(self, Write(d), GrowArrow(small), t=1.3, rt=.6)
        big = Arrow(DOWN * 1.6 + RIGHT * .2, DOWN * 1.6 + RIGHT * 4.6, buff=0, color=YEL, stroke_width=10)
        beat(self, GrowArrow(big), FadeIn(tex(r"v_{out}", 50, YEL).next_to(big, RIGHT, .2)), t=1.3, rt=.7)
        g = VGroup(kr("×", 44, YEL), kr("수십만 배", 44, YEL)).arrange(RIGHT, buff=.1).next_to(big, UP, .2)
        beat(self, FadeIn(g, shift=UP * .2), t=1.0, rt=.4)
        pulse(self, g, t=1.4)


class O3(Scene):
    """규칙 1: 입력 단자로 전류가 안 들어감."""
    def construct(self):
        self.add(step_tag(1, BLU))
        A = opamp(RIGHT * 1.0 + UP * .5, 1.3)
        self.add(A["g"], wire(A["m"] + LEFT * 2.2, A["m"]), wire(A["p"] + LEFT * 2.2, A["p"]), wire(A["o"], A["o"] + RIGHT * 1))
        a1 = iarrow(A["m"] + LEFT * 1.9, A["m"] + LEFT * .5, YEL, "i", UP); a2 = iarrow(A["p"] + LEFT * 1.9, A["p"] + LEFT * .5, YEL, "i", DOWN)
        beat(self, GrowArrow(a1[0]), FadeIn(a1[1]), GrowArrow(a2[0]), FadeIn(a2[1]), t=1.4, rt=.6)
        x1, x2 = Cross(a1, stroke_color=RED, stroke_width=8), Cross(a2, stroke_color=RED, stroke_width=8)
        beat(self, Create(x1), Create(x2), t=1.4, rt=.6)
        c = card(VGroup(kr("규칙 1", 32, BLU), VGroup(kr("입력 전류", 42), tex("= 0", 56, YEL)).arrange(RIGHT, buff=.2)).arrange(DOWN, buff=.2), BLU).shift(DOWN * 2.2)
        beat(self, FadeIn(c, shift=UP * .3), t=1.4, rt=.5)
        pulse(self, c, t=1.4)


class O4(Scene):
    """규칙 2: 출력 → − 단자 되먹임이면 v+ = v−."""
    def construct(self):
        self.add(step_tag(1, BLU))
        A = opamp(RIGHT * .4 + UP * .6, 1.2)
        self.add(A["g"], wire(A["p"] + LEFT * 2, A["p"]), wire(A["m"] + LEFT * .6, A["m"]))
        ow = wire(A["o"], A["o"] + RIGHT * 1.6)
        beat(self, Create(ow), FadeIn(tex(r"v_{out}", 40, YEL).next_to(ow, RIGHT, .15)), t=1.0, rt=.4)
        x = A["o"][0] + .8; yt = A["tri"].get_top()[1] + .5
        fb = poly([(x, A["o"][1]), (x, yt), (A["m"][0] - .6, yt), A["m"] + LEFT * .6], YEL, 6)
        beat(self, Create(fb), FadeIn(jdot((x, A["o"][1]), YEL)), t=1.6, rt=1.1)
        lab = kr("되먹임", 32, YEL).next_to(fb, UP, .15)
        beat(self, FadeIn(lab), t=.8, rt=.3)
        c = card(VGroup(kr("규칙 2", 32, GRN), tex(r"v_+ = v_-", 64, YEL)).arrange(DOWN, buff=.2), GRN).shift(DOWN * 2.2)
        beat(self, FadeIn(c, shift=UP * .3), t=1.4, rt=.5)
        pulse(self, c, t=1.4)


class O5(Scene):
    """차이가 생기면 출력이 크게 움직여 차이를 0으로."""
    def construct(self):
        self.add(step_tag(1, BLU))
        C = follower((-1.5, .4))
        self.add(C["all"])
        self.add(tex(r"1\,\mathrm{V}", 38, BLU).next_to(C["lin"], DOWN, .2))
        vm = ValueTracker(.90)
        row = lambda lab, f, col: VGroup(tex(lab, 44, col), DecimalNumber(f(), num_decimal_places=2, font_size=48, color=col)).arrange(RIGHT, buff=.25)
        R1 = always_redraw(lambda: row(r"v_- =", lambda: vm.get_value(), RED).move_to(RIGHT * 4.4 + UP * 1.0))
        R2 = always_redraw(lambda: VGroup(kr("차이", 36, ORG), DecimalNumber(1 - vm.get_value(), num_decimal_places=2, font_size=48, color=ORG)).arrange(RIGHT, buff=.25).move_to(RIGHT * 4.4 + DOWN * .1))
        beat(self, FadeIn(R1), FadeIn(R2), t=1.2, rt=.4)
        up = Arrow(RIGHT * 4.4 + DOWN * 2.6, RIGHT * 4.4 + DOWN * 1.0, buff=0, color=YEL, stroke_width=8)
        beat(self, GrowArrow(up), FadeIn(kr("출력 ↑", 34, YEL).next_to(up, LEFT, .2)), t=1.0, rt=.4)
        self.play(vm.animate.set_value(1.0), run_time=2.0, rate_func=smooth)
        t = VGroup(kr("차이", 44, ORG), tex(r"\rightarrow 0", 60, YEL)).arrange(RIGHT, buff=.2).move_to(DOWN * 2.7 + LEFT * 1.5)
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.4)
        pulse(self, t, t=1.2)


class O6(Scene):
    """가상 단락: 닿지 않았는데 같은 전압."""
    def construct(self):
        self.add(step_tag(1, BLU))
        A = opamp(RIGHT * 1.6 + UP * .5, 1.5)
        self.add(A["g"], wire(A["m"] + LEFT * 2.3, A["m"]), wire(A["p"] + LEFT * 2.3, A["p"]), wire(A["o"], A["o"] + RIGHT * .8))
        x = A["m"][0] - .9
        dl = DashedLine(P3((x, A["m"][1])), P3((x, A["p"][1])), color=YEL, stroke_width=7, dash_length=.15)
        beat(self, Create(dl), FadeIn(jdot((x, A["m"][1]), YEL)), FadeIn(jdot((x, A["p"][1]), YEL)), t=1.4, rt=.7)
        eq = tex("=", 70, YEL).next_to(dl, LEFT, .3)
        beat(self, FadeIn(eq), t=.9, rt=.3)
        t = kr("가상 단락", 60, YEL).move_to(LEFT * 4.2 + UP * .5)
        beat(self, Write(t), t=1.3, rt=.7)
        s = VGroup(kr("닿지 않았는데", 34, MUTE), kr("같은 전압", 40, INK)).arrange(DOWN, buff=.15).move_to(DOWN * 2.3)
        beat(self, FadeIn(s, shift=UP * .2), t=1.3, rt=.4)
        pulse(self, t, t=1.4)


# ================= STEP 2 반전 증폭기 =================
def inv_full(sc, o=(0, .2), **kw):
    C = inv(o, **kw); sc.add(C["all"]); return C


class V1(Scene):
    """반전 증폭기 조립: + 는 접지, 입력은 R1 거쳐 − 로."""
    def construct(self):
        self.add(step_tag(2, PUR))
        C = inv((0, .2))
        beat(self, FadeIn(C["amp"]), t=.8, rt=.4)
        beat(self, Create(C["gnd"]), FadeIn(kr("+ 는 접지", 30, MUTE).next_to(C["gnd"][1], LEFT, .3)), t=1.4, rt=.6)
        beat(self, FadeIn(C["tin"]), FadeIn(C["lin"]), Create(C["r1"]), FadeIn(C["lr1"]), t=1.4, rt=.7)
        beat(self, Create(C["wn"]), t=.8, rt=.4)
        beat(self, Create(C["fb"]), FadeIn(C["lrf"]), Create(C["outw"]), FadeIn(C["lout"]), t=1.6, rt=.9)


class V2(Scene):
    """− 단자 = 0V (가상 접지), R1 전류 = vin/R1."""
    def construct(self):
        self.add(step_tag(2, PUR))
        C = inv_full(self)
        N = C["N"]
        z = card(tex(r"0\,\mathrm{V}", 44, YEL), YEL, .12).next_to(N, UP + LEFT, .15)
        beat(self, FadeIn(z, shift=UP * .2), Flash(N, color=YEL), t=1.5, rt=.6)
        dl = DashedLine(C["m"] + LEFT * .25, C["p"] + LEFT * .25, color=YEL, stroke_width=5)
        beat(self, Create(dl), t=1.0, rt=.5)
        a = iarrow(P3((C["xin"] + .5, N[1] - .55)), P3((N[0] - .5, N[1] - .55)), YEL, None)
        beat(self, GrowArrow(a[0]), t=1.0, rt=.6)
        f = tex(r"i = \frac{v_{in}}{R_1}", 60, YEL).move_to(DOWN * 2.6 + LEFT * 2.6)
        beat(self, Write(f), t=1.4, rt=.7)
        pulse(self, f, t=1.2)


class V3(Scene):
    """전류는 옵앰프로 못 들어가고 Rf 로 전부."""
    def construct(self):
        self.add(step_tag(2, PUR))
        C = inv_full(self)
        N = C["N"]
        a = iarrow(P3((C["xin"] + .5, N[1] - .55)), P3((N[0] - .9, N[1] - .55)), YEL, "i", DOWN)
        self.add(a)
        b = iarrow(N + RIGHT * .2 + DOWN * .35, C["m"] + LEFT * .1 + DOWN * .35, RED)
        beat(self, GrowArrow(b[0]), t=.9, rt=.4)
        beat(self, Create(Cross(b, stroke_color=RED, stroke_width=7)), t=1.0, rt=.4)
        up = iarrow(N + LEFT * .35 + UP * .4, P3((N[0] - .35, C["yf"] - .3)), YEL)
        rf = iarrow(P3((N[0] + .5, C["yf"] + 1.0)), P3((C["xo"] - .5, C["yf"] + 1.0)), YEL, "i", RIGHT)
        C["lrf"].shift(UP * .0)
        beat(self, GrowArrow(up[0]), t=.9, rt=.5)
        beat(self, GrowArrow(rf[0]), FadeIn(rf[1]), C["rf"].animate.set_color(YEL), t=1.4, rt=.7)
        t = kr("전부 Rf 로", 44, YEL).move_to(DOWN * 2.7)
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.4)
        pulse(self, t, t=1.0)


class V4(Scene):
    """vout = −Rf/R1 vin, 1k·10k → −10배."""
    def construct(self):
        self.add(step_tag(2, PUR))
        C = inv((0, 1.0), r1=r"1\,k\Omega", rf=r"10\,k\Omega")
        C["all"].scale(.8, about_point=UP * 1.2)
        beat(self, FadeIn(VGroup(*[m for k, m in enumerate(C["all"]) if k not in (7, 8)])), t=.6, rt=.4)
        f = tex(r"v_{out} = -\frac{R_f}{R_1}\, v_{in}", 64, INK).move_to(DOWN * 2.0)
        beat(self, Write(f), t=1.6, rt=.9)
        beat(self, FadeIn(C["lr1"], shift=DOWN * .2), FadeIn(C["lrf"], shift=DOWN * .2), t=1.2, rt=.5)
        g = tex(r"= -\frac{10\,k}{1\,k} = -10", 60, YEL).next_to(f, RIGHT, .3)
        VGroup(f, g).move_to(DOWN * 2.0)
        beat(self, f.animate.shift(LEFT * 0), FadeIn(g, shift=LEFT * .2), t=1.4, rt=.6)
        pulse(self, g, t=1.2)


def vv_axes(o=DOWN * .2):
    ax = Axes(x_range=[-2.5, 2.5, 1], y_range=[-25, 25, 5], x_length=7.5, y_length=5.2, tips=False,
              axis_config={"color": MUTE, "stroke_width": 3, "include_ticks": False}).move_to(o)
    g = VGroup(ax, tex(r"v_{in}", 36, BLU).next_to(ax.x_axis.get_end(), DOWN, .15), tex(r"v_{out}", 36, YEL).next_to(ax.y_axis.get_end(), RIGHT, .15))
    return ax, g


class V5(Scene):
    """2V 넣으면 −20V?"""
    def construct(self):
        self.add(step_tag(2, PUR))
        ax, g = vv_axes()
        beat(self, FadeIn(g), t=.6, rt=.4)
        ln = ax.plot(lambda x: -10 * x, x_range=[-2.3, 2.3], color=PUR, stroke_width=6)
        beat(self, Create(ln), FadeIn(tex(r"\times(-10)", 40, PUR).next_to(ax.c2p(-1.0, 10), LEFT, .5)), t=1.4, rt=.9)
        d = Dot(ax.c2p(2, -20), color=YEL, radius=.12)
        guide = VGroup(DashedLine(ax.c2p(2, 0), ax.c2p(2, -20), color=MUTE), DashedLine(ax.c2p(0, -20), ax.c2p(2, -20), color=MUTE))
        beat(self, Create(guide), FadeIn(tex(r"2\,\mathrm{V}", 36, BLU).next_to(ax.c2p(2, 0), UP, .15)), t=1.0, rt=.5)
        beat(self, FadeIn(d, scale=.5), t=.5, rt=.3)
        q = tex(r"-20\,\mathrm{V}\;?", 60, YEL).next_to(ax.c2p(0, -20), LEFT, .25)
        beat(self, Write(q), t=1.2, rt=.6)
        pulse(self, q, t=1.2)


class V6(Scene):
    """±15V 전원 → 포화."""
    def construct(self):
        self.add(step_tag(2, PUR))
        ax, g = vv_axes()
        self.add(g)
        ln = ax.plot(lambda x: -10 * x, x_range=[-2.3, 2.3], color=PUR, stroke_width=4, stroke_opacity=.35)
        self.add(ln)
        rails = VGroup(DashedLine(ax.c2p(-2.5, 15), ax.c2p(2.5, 15), color=RED, stroke_width=4),
                       DashedLine(ax.c2p(-2.5, -15), ax.c2p(2.5, -15), color=RED, stroke_width=4))
        rl = VGroup(tex(r"+15\,\mathrm{V}", 34, RED).next_to(rails[0], RIGHT, .15), tex(r"-15\,\mathrm{V}", 34, RED).next_to(rails[1], RIGHT, .15))
        beat(self, Create(rails), FadeIn(rl), t=1.4, rt=.7)
        cl = ax.plot(lambda x: float(np.clip(-10 * x, -15, 15)), x_range=[-2.3, 2.3, .01], color=YEL, stroke_width=7)
        beat(self, Create(cl), t=1.6, rt=1.2)
        d = Dot(ax.c2p(2, -15), color=YEL, radius=.13)
        beat(self, FadeIn(d, scale=.5), FadeIn(tex(r"\approx -15\,\mathrm{V}", 40, YEL).next_to(d, DOWN, .35).shift(LEFT * 1.0)), t=1.0, rt=.4)
        t = kr("포화", 64, YEL).move_to(ax.c2p(1.6, 8))
        beat(self, Write(t), t=1.0, rt=.5)
        pulse(self, t, t=1.2)


# ================= STEP 3 비반전 증폭기 =================
class N1(Scene):
    """입력을 + 단자에 바로."""
    def construct(self):
        self.add(step_tag(3, GRN))
        C = noninv((0, .5))
        beat(self, FadeIn(C["amp"]), t=.7, rt=.4)
        beat(self, FadeIn(C["tin"]), FadeIn(C["lin"]), t=.6, rt=.3)
        beat(self, Create(C["win"]), Flash(C["p"], color=BLU), t=1.4, rt=.8)
        beat(self, Create(C["wn"]), Create(C["r1"]), Create(C["g1"]), FadeIn(C["lr1"]), t=1.3, rt=.8)
        beat(self, Create(C["fb"]), FadeIn(C["lrf"]), Create(C["outw"]), FadeIn(C["lout"]), t=1.6, rt=.9)


class N2(Scene):
    """− 단자도 vin, R1·Rf 가 출력을 나눠 그 전압."""
    def construct(self):
        self.add(step_tag(3, GRN))
        C = noninv((0, .7)); self.add(C["all"])
        dl = DashedLine(C["p"] + LEFT * .25, C["m"] + LEFT * .25, color=YEL, stroke_width=5)
        beat(self, Create(dl), t=.8, rt=.4)
        lab = tex(r"v_- = v_{in}", 44, YEL).next_to(C["N"], LEFT, .3).shift(UP * .1)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        br = Brace(VGroup(C["r1"], C["rf"]), DOWN, color=MUTE).shift(DOWN * .55)
        beat(self, GrowFromCenter(br), FadeIn(kr("출력을 나눔", 32, MUTE).next_to(br, DOWN, .1)), t=1.4, rt=.6)
        f = tex(r"v_{in} = v_{out}\cdot\frac{R_1}{R_1+R_f}", 54, INK).move_to(DOWN * 2.7 + RIGHT * 4.05)
        beat(self, Write(f), t=1.6, rt=.9)
        pulse(self, f, t=1.2)


class N3(Scene):
    """이득 1 + Rf/R1, 부호 그대로."""
    def construct(self):
        self.add(step_tag(3, GRN))
        f = tex(r"v_{out} = \left(1 + \frac{R_f}{R_1}\right) v_{in}", 72, INK).shift(UP * 1.7)
        beat(self, Write(f), t=1.6, rt=1.0)
        beat(self, Circumscribe(f[0][5:13], color=GRN, buff=.1), t=1.0, rt=.8)
        si = sine(LEFT * 3.6 + DOWN * 1.3, .35, 2, 3.4, BLU); so = sine(RIGHT * 3.0 + DOWN * 1.3, 1.0, 2, 3.4, GRN, sw=6)
        beat(self, Create(si), FadeIn(kr("입력", 30, BLU).next_to(si, DOWN, .5)), t=1.0, rt=.6)
        beat(self, Create(so), FadeIn(kr("출력", 30, GRN).next_to(so, DOWN, .2)), t=1.0, rt=.6)
        t = kr("부호 그대로", 44, YEL).move_to(DOWN * 3.2)
        beat(self, FadeIn(t, shift=UP * .2), t=.9, rt=.4)
        pulse(self, t, t=1.0)


class N4(Scene):
    """1k·9k → 0.5V 가 5V."""
    def construct(self):
        self.add(step_tag(3, GRN))
        C = noninv((-.3, 1.2), r"1\,k\Omega", r"9\,k\Omega")
        C["all"].scale(.75, about_point=UP * 1.2)
        beat(self, FadeIn(C["all"]), t=.9, rt=.5)
        i = tex(r"0.5\,\mathrm{V}", 44, BLU).next_to(C["lin"], DOWN, .25)
        beat(self, FadeIn(i, shift=RIGHT * .2), t=1.0, rt=.4)
        f = tex(r"1 + \frac{9\,k}{1\,k} = 10", 60, INK).move_to(DOWN * 2.2 + LEFT * 2.4)
        beat(self, Write(f), t=1.6, rt=.9)
        o = tex(r"0.5\,\mathrm{V} \times 10 = 5\,\mathrm{V}", 60, YEL).move_to(DOWN * 2.2 + RIGHT * 3.0)
        beat(self, FadeIn(o, shift=LEFT * .2), t=1.2, rt=.5)
        pulse(self, o, t=1.2)


class N5(Scene):
    """Rf = 0 → 1배 전압 팔로워, 버퍼."""
    def construct(self):
        self.add(step_tag(3, GRN))
        C = follower((-.6, 1.2)); C["all"].scale(.85, about_point=UP * 1.2)
        beat(self, FadeIn(VGroup(C["amp"], C["tin"], C["win"], C["outw"], C["lin"], C["lout"])), t=.6, rt=.4)
        beat(self, Create(C["fb"]), FadeIn(kr("Rf = 0", 34, YEL).next_to(C["fb"], DOWN, .15)), t=1.4, rt=.8)
        g = tex(r"v_{out} = v_{in}\;\;(\times 1)", 52, YEL).move_to(RIGHT * 4.3 + DOWN * .5)
        beat(self, FadeIn(g, shift=UP * .2), t=1.2, rt=.4)
        boxes = VGroup(boxio("센서", 2.2, 1.0, BLU), boxio("버퍼", 2.2, 1.0, YEL), boxio("부하", 2.2, 1.0, MUTE)).arrange(RIGHT, buff=1.0).move_to(DOWN * 2.5)
        for b in boxes: b[1].scale(.8)
        ars = VGroup(*[Arrow(boxes[k].get_right(), boxes[k + 1].get_left(), buff=.1, color=INK, stroke_width=5) for k in range(2)])
        beat(self, FadeIn(boxes[0]), FadeIn(boxes[1]), GrowArrow(ars[0]), t=1.0, rt=.5)
        beat(self, FadeIn(boxes[2]), GrowArrow(ars[1]), t=1.0, rt=.5)
        pulse(self, boxes[1], t=1.0)


class Sum1(Scene):
    """중간 정리 (STEP 1~3)."""
    def construct(self):
        self.add(head("여기까지 정리", YEL))
        rows = sum_rows([("반전", tex(r"-\frac{R_f}{R_1}", 60, PUR)),
                         ("비반전", tex(r"1 + \frac{R_f}{R_1}", 60, GRN)),
                         ("팔로워", tex(r"1", 60, YEL))], 38)
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.5, rt=.5)
        pulse(self, rows, t=1.8)


# ================= STEP 4 가산기 =================
class A1(Scene):
    def construct(self):
        self.add(step_tag(4, ORG))
        C = summer((0, .1))
        beat(self, FadeIn(VGroup(C["amp"], C["gnd"], C["fb"], C["lrf"], C["outw"], C["lout"])), t=1.0, rt=.5)
        beat(self, FadeIn(C["bus"][1:]), FadeIn(C["bus"][0]), t=.5, rt=.3)
        for k in range(3):
            beat(self, FadeIn(C["ins"][k], shift=RIGHT * .3), t=1.2, rt=.5)
        pulse(self, C["ins"], t=1.0)


def sum_arrows(C):
    return VGroup(*[iarrow(P3((C["xin"] + .5, y + .35 if k != 1 else y + .35)), P3((C["bx"] - .4, y + .35)), c, f"i_{k + 1}", UP, 32)
                    for k, (y, c) in enumerate(zip(C["ys"], C["cols"]))])


class A2(Scene):
    """− 단자 0V, 입력마다 따로 전류."""
    def construct(self):
        self.add(step_tag(4, ORG))
        C = summer((0, .1)); self.add(C["all"])
        z = card(tex(r"0\,\mathrm{V}", 40, YEL), YEL, .1).next_to(C["N"], DOWN + RIGHT, .05).shift(RIGHT * .05)
        beat(self, FadeIn(z, shift=UP * .2), Flash(C["N"], color=YEL), t=1.4, rt=.6)
        ars = sum_arrows(C)
        for a in ars:
            for m in a[1:]: m.shift(UP * 0)
            beat(self, GrowArrow(a[0]), t=1.1, rt=.5)
        pulse(self, ars, t=1.2)


class A3(Scene):
    """Rf 에서 합쳐짐 → vout ∝ 합."""
    def construct(self):
        self.add(step_tag(4, ORG))
        C = summer((0, .6)); C["all"].scale(.85, about_point=UP * .6); self.add(C["all"])
        ars = VGroup(*[a[0] for a in sum_arrows(C)]); ars.scale(.85, about_point=UP * .6); self.add(ars)
        rf = iarrow(C["rf"].get_left() + UP * .5 + RIGHT * .3, C["rf"].get_right() + UP * .5 + LEFT * .3, YEL)
        beat(self, GrowArrow(rf[0]), C["rf"].animate.set_color(YEL), t=1.3, rt=.7)
        s = tex(r"i_1 + i_2 + i_3", 44, YEL).next_to(rf, UP, .1)
        C["lrf"].next_to(C["rf"], DOWN, .15)
        beat(self, FadeIn(s), t=1.0, rt=.4)
        f = tex(r"v_{out} = -R_f\left(\frac{v_1}{R_1} + \frac{v_2}{R_2} + \frac{v_3}{R_3}\right)", 52, INK).move_to(DOWN * 2.8)
        beat(self, Write(f), t=2.0, rt=1.2)
        pulse(self, f, t=1.2)


class A4(Scene):
    """전부 10kΩ, 1V·2V·3V → ?"""
    def construct(self):
        self.add(step_tag(4, ORG))
        C = summer((0, .1), labs=(r"1\,\mathrm{V}", r"2\,\mathrm{V}", r"3\,\mathrm{V}"), rl=(r"10\,k", r"10\,k", r"10\,k"))
        base = VGroup(C["amp"], C["bus"], C["gnd"], C["fb"], C["outw"], *[m[:2] for m in C["ins"]])
        self.add(base)
        rl = VGroup(*[m[3] for m in C["ins"]], tex(r"10\,k", 36, ORG).next_to(C["rf"], UP, .2))
        beat(self, FadeIn(rl), t=1.2, rt=.5)
        for m in C["ins"]:
            beat(self, FadeIn(m[2], shift=RIGHT * .2), t=.8, rt=.3)
        q = tex(r"v_{out} = \,?", 60, YEL).next_to(C["outw"], DOWN, .6).shift(RIGHT * .8)
        beat(self, Write(q), t=1.2, rt=.6)
        pulse(self, q, t=1.2)


class A5(Scene):
    """−(1+2+3) = −6V."""
    def construct(self):
        self.add(step_tag(4, ORG))
        f1 = tex(r"1 + 2 + 3 = 6", 76, INK).shift(UP * 1.4)
        beat(self, Write(f1), t=1.6, rt=1.0)
        f2 = tex(r"v_{out} = -6\,\mathrm{V}", 96, YEL).shift(DOWN * .6)
        beat(self, FadeIn(f2, shift=UP * .3), t=1.4, rt=.6)
        t = kr("부호가 바뀜", 40, PUR).next_to(f2, DOWN, .6)
        beat(self, FadeIn(t), t=1.2, rt=.4)
        pulse(self, f2, t=1.4)


def mixer(o=ORIGIN, names=("마이크", "기타", "드럼"), cols=(BLU, GRN, PUR)):
    g = VGroup()
    for k, (n, c) in enumerate(zip(names, cols)):
        x = (k - 1) * 1.7
        track = Line(P3((x, -1.0)), P3((x, 1.0)), color="#2a2e37", stroke_width=10)
        knob = RoundedRectangle(width=.7, height=.32, corner_radius=.08, color=c, fill_color=c, fill_opacity=1).move_to(P3((x, .2 - .4 * k)))
        g.add(VGroup(track, knob, kr(n, 28, c).next_to(track, DOWN, .25)))
    return g.shift(P3(o))


class A6(Scene):
    """오디오 믹서 = 가산기, 입력 저항 = 채널 볼륨."""
    def construct(self):
        self.add(step_tag(4, ORG))
        M = mixer(LEFT * 3.0 + UP * .2)
        beat(self, FadeIn(M, lag_ratio=.3), t=1.3, rt=.8)
        S = card(tex(r"\Sigma", 80, YEL), YEL, .3).move_to(RIGHT * 1.6 + UP * .2)
        ars = VGroup(*[Arrow(M[k][0].get_top() + UP * .1, S.get_left(), buff=.15, color=M[k][1].get_color(), stroke_width=4) for k in range(3)])
        beat(self, FadeIn(S), *[GrowArrow(a) for a in ars], t=1.4, rt=.7)
        sp = VGroup(Polygon(P3((4.2, .5)), P3((4.2, -.1)), P3((4.6, -.1)), P3((5.2, -.6)), P3((5.2, 1.0)), P3((4.6, .5)), color=INK, stroke_width=5))
        beat(self, FadeIn(sp), GrowArrow(Arrow(S.get_right(), P3((4.1, .2)), buff=.1, color=YEL)), t=1.0, rt=.5)
        beat(self, M[0][1].animate.shift(UP * .7), M[2][1].animate.shift(DOWN * .4), t=1.2, rt=.8)
        t = VGroup(kr("입력 저항", 36, INK), kr("= 채널 볼륨", 36, YEL)).arrange(RIGHT, buff=.2).move_to(DOWN * 2.7)
        beat(self, FadeIn(t, shift=UP * .2), t=1.2, rt=.4)


# ================= STEP 5 차동 증폭기 =================
class D1(Scene):
    def construct(self):
        self.add(step_tag(5, RED))
        C = diffamp((0, .2))
        beat(self, FadeIn(VGroup(C["amp"], C["fb"], C["outw"], C["lout"])), t=1.0, rt=.5)
        beat(self, FadeIn(C["in1"], shift=RIGHT * .3), FadeIn(kr("− 쪽", 28, BLU).next_to(C["in1"][1], UP, .5)), t=1.6, rt=.6)
        beat(self, FadeIn(C["in2"], shift=RIGHT * .3), FadeIn(C["r4"]), FadeIn(kr("+ 쪽", 28, GRN).next_to(C["in2"][1], DOWN, .6)), t=1.6, rt=.6)
        pulse(self, C["amp"], t=1.2)


def bar(x, h, c, lab, y0=-2.2, w=.8):
    r = Rectangle(width=w, height=h, color=c, fill_color=c, fill_opacity=.85, stroke_width=0).move_to(P3((x, y0 + h / 2)))
    return VGroup(r, tex(lab, 36, c).next_to(r, DOWN, .15).set_y(y0 - .3))


class D2(Scene):
    """차이만 키움."""
    def construct(self):
        self.add(step_tag(5, RED))
        base = Line(P3((-5.5, -2.2)), P3((5.5, -2.2)), color=MUTE, stroke_width=3)
        self.add(base)
        b1, b2 = bar(-4.2, 2.6, BLU, "v_1"), bar(-3.0, 3.2, GRN, "v_2")
        beat(self, GrowFromEdge(b1[0], DOWN), FadeIn(b1[1]), GrowFromEdge(b2[0], DOWN), FadeIn(b2[1]), t=1.4, rt=.7)
        d = Rectangle(width=.9, height=.6, color=YEL, stroke_width=4).move_to(P3((-3.0, -2.2 + 2.9)))
        dl = tex(r"v_2 - v_1", 36, YEL).next_to(d, RIGHT, .2)
        beat(self, Create(d), FadeIn(dl), t=1.2, rt=.5)
        ar = Arrow(P3((-.8, -.5)), P3((1.0, -.5)), buff=0, color=YEL, stroke_width=8)
        beat(self, GrowArrow(ar), FadeIn(kr("× 증폭", 32, YEL).next_to(ar, UP, .15)), t=1.0, rt=.5)
        bo = bar(3.0, 4.2, YEL, r"v_{out}", w=1.2)
        beat(self, GrowFromEdge(bo[0], DOWN), FadeIn(bo[1]), t=1.2, rt=.7)
        pulse(self, bo[0], t=1.0)


class D3(Scene):
    """vout = R2/R1 (v2 − v1)."""
    def construct(self):
        self.add(step_tag(5, RED))
        f = tex(r"v_{out} = \frac{R_2}{R_1}\,(v_2 - v_1)", 80, INK).shift(UP * .9)
        beat(self, Write(f), t=1.8, rt=1.1)
        beat(self, Circumscribe(f[0][5:10], color=ORG, buff=.1), t=1.1, rt=.8)
        beat(self, Circumscribe(f[0][10:], color=YEL, buff=.1), t=1.1, rt=.8)
        c = card(kr("양쪽 저항 비를 같게", 38, INK), MUTE).shift(DOWN * 2.0)
        beat(self, FadeIn(c, shift=UP * .2), t=1.4, rt=.5)


class D4(Scene):
    """두 선에 같은 잡음."""
    def construct(self):
        self.add(step_tag(5, RED))
        s2 = sine(UP * 1.4 + LEFT * .8, .7, 2, 7.0, GRN); s1 = Line(P3((-4.3, -1.4)), P3((2.7, -1.4)), color=BLU, stroke_width=5)
        beat(self, Create(s2), FadeIn(tex("v_2", 44, GRN).next_to(s2, LEFT, .3)), t=1.0, rt=.6)
        beat(self, Create(s1), FadeIn(tex("v_1", 44, BLU).next_to(s1, LEFT, .3)), t=.8, rt=.5)
        n2 = noisy(UP * 1.4 + LEFT * .8, 7.0, .7, 2, .35, GRN, seed=5); n1 = noisy(DOWN * 1.4 + LEFT * .8, 7.0, 0, 2, .35, BLU, seed=5, sig=False)
        bolt = VGroup(*[kr("⚡", 50, RED).move_to(P3((4.3, y))) for y in (1.4, -1.4)])
        beat(self, FadeIn(bolt), t=.6, rt=.3)
        beat(self, Transform(s2, n2), Transform(s1, n1), t=1.4, rt=.9)
        t = kr("같은 잡음", 44, RED).move_to(RIGHT * 4.3)
        beat(self, FadeIn(t), t=.8, rt=.3)
        q = kr("빼면?", 48, YEL).move_to(DOWN * 3.0)
        beat(self, FadeIn(q, shift=UP * .2), t=1.0, rt=.4)


class D5(Scene):
    """빼면 잡음 사라지고 신호만 커짐."""
    def construct(self):
        self.add(step_tag(5, RED))
        n2 = noisy(UP * 2.2 + LEFT * 3.0, 4.4, .45, 2, .22, GRN, seed=5, sw=3)
        n1 = noisy(UP * .4 + LEFT * 3.0, 4.4, 0, 2, .22, BLU, seed=5, sig=False, sw=3)
        self.add(n2, n1, tex("v_2", 38, GRN).next_to(n2, LEFT, .2), tex("v_1", 38, BLU).next_to(n1, LEFT, .2))
        mi = tex("-", 70, YEL).move_to(LEFT * 3.0 + UP * 1.3)
        beat(self, FadeIn(mi), t=.8, rt=.3)
        ar = Arrow(LEFT * .4 + UP * 1.3, RIGHT * 1.0 + UP * 1.3, buff=0, color=YEL, stroke_width=8)
        beat(self, GrowArrow(ar), t=.8, rt=.4)
        out = sine(RIGHT * 3.6 + UP * 1.3, 1.3, 2, 4.0, YEL, sw=7)
        beat(self, Create(out), t=1.4, rt=1.0)
        t1 = VGroup(kr("잡음", 40, RED), tex(r"\rightarrow 0", 56, RED)).arrange(RIGHT, buff=.2).move_to(DOWN * 1.6 + LEFT * 2.6)
        t2 = kr("신호만 커짐", 44, YEL).move_to(DOWN * 1.6 + RIGHT * 3.4)
        beat(self, FadeIn(t1, shift=UP * .2), t=1.0, rt=.4)
        beat(self, FadeIn(t2, shift=UP * .2), t=1.0, rt=.4)
        pulse(self, t2, t=1.0)


class D6(Scene):
    """긴 마이크 케이블: 두 선에 같은 잡음 → 끝에서 빼기."""
    def construct(self):
        self.add(step_tag(5, RED))
        mic = VGroup(Circle(.45, color=INK, stroke_width=5, fill_color="#181b21", fill_opacity=1), Line(P3((0, -.45)), P3((0, -1.1)), color=INK, stroke_width=6)).move_to(LEFT * 5.4 + UP * .6)
        beat(self, FadeIn(mic), FadeIn(kr("마이크", 30, MUTE).next_to(mic, DOWN, .2)), t=.8, rt=.4)
        xs = np.linspace(-4.8, 2.4, 120)
        w1 = VMobject(color=GRN, stroke_width=5).set_points_smoothly([P3((x, .6 + .25 * np.sin(x * 3))) for x in xs])
        w2 = VMobject(color=BLU, stroke_width=5).set_points_smoothly([P3((x, .6 - .25 * np.sin(x * 3))) for x in xs])
        beat(self, Create(w1), Create(w2), FadeIn(kr("긴 케이블", 30, MUTE).move_to(LEFT * 1.2 + DOWN * .3)), t=1.4, rt=1.0)
        bolts = VGroup(*[kr("⚡", 46, RED).move_to(P3((x, 1.7))) for x in (-3.2, -.8, 1.4)])
        beat(self, LaggedStart(*[FadeIn(b, shift=DOWN * .4) for b in bolts], lag_ratio=.3), t=1.3, rt=.9)
        A = opamp(RIGHT * 3.6 + UP * .6, .8)
        beat(self, FadeIn(A["g"]), t=.8, rt=.4)
        out = sine(RIGHT * 5.6 + UP * .6, .4, 1.5, 1.4, YEL, sw=6)
        beat(self, Create(out), t=.9, rt=.5)
        t = kr("잡음은 지우고 신호만", 40, YEL).move_to(DOWN * 2.3)
        beat(self, FadeIn(t, shift=UP * .2), t=1.0, rt=.4)


# ================= 정리 =================
class F1(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        c1 = card(VGroup(kr("규칙 1", 32, BLU), VGroup(kr("입력 전류", 40), tex("= 0", 56, YEL)).arrange(RIGHT, buff=.2)).arrange(DOWN, buff=.2), BLU)
        c2 = card(VGroup(kr("규칙 2", 32, GRN), tex(r"v_+ = v_-", 60, YEL)).arrange(DOWN, buff=.25), GRN)
        VGroup(c1, c2).arrange(RIGHT, buff=1.0).shift(DOWN * .2)
        beat(self, FadeIn(c1, shift=UP * .3), t=1.8, rt=.5)
        beat(self, FadeIn(c2, shift=UP * .3), t=1.8, rt=.5)
        pulse(self, VGroup(c1, c2), t=1.6)


class F2(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        rows = sum_rows([("반전", tex(r"-\frac{R_f}{R_1}", 58, PUR)),
                         ("비반전", tex(r"1 + \frac{R_f}{R_1}", 58, GRN)),
                         ("버퍼", tex(r"\times 1", 58, YEL))], 38)
        for r in rows:
            beat(self, FadeIn(r, shift=RIGHT * .3), t=1.6, rt=.5)
        pulse(self, rows, t=1.6)


class F3(Scene):
    def construct(self):
        self.add(head("정리", YEL))
        a = card(VGroup(kr("입력 여러 개", 34, MUTE), kr("더하기", 52, ORG), tex(r"v_1 + v_2 + v_3", 44, ORG)).arrange(DOWN, buff=.25), ORG)
        b = card(VGroup(kr("양쪽 입력", 34, MUTE), kr("빼기", 52, RED), tex(r"v_2 - v_1", 44, RED)).arrange(DOWN, buff=.25), RED)
        VGroup(a, b).arrange(RIGHT, buff=1.2).shift(DOWN * .3)
        beat(self, FadeIn(a, shift=UP * .3), t=1.8, rt=.5)
        beat(self, FadeIn(b, shift=UP * .3), t=1.8, rt=.5)
        pulse(self, VGroup(a, b), t=1.4)


class Site(Scene):
    def construct(self):
        t = card(VGroup(kr("보이는 회로이론", 60, YEL), kr("연산 증폭기 단원", 34, MUTE),
                        kr("링크는 설명란", 34, INK)).arrange(DOWN, buff=.35), YEL, .55)
        beat(self, FadeIn(t[0]), t=.8, rt=.3)
        for m in t[1]:
            beat(self, FadeIn(m, shift=UP * .2), t=1.4, rt=.4)
        pulse(self, t, t=2.0)


class Next(Scene):
    def construct(self):
        items = ["변압기", "주파수 응답", "연산증폭기", "다음 편"]
        cards = VGroup(*[card(kr(s, 36, YEL if s == "연산증폭기" else MUTE), YEL if s == "연산증폭기" else "#2a2e37", .3) for s in items]).arrange(RIGHT, buff=.35)
        cards.scale_to_fit_width(min(cards.width, 12.5))
        lab = kr("재생목록 · 회로이론 한눈에", 40, INK).next_to(cards, UP, .6)
        beat(self, FadeIn(lab), t=1.0, rt=.4)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cards], lag_ratio=.3), run_time=1.6)
        arr = Arrow(cards[2].get_bottom() + DOWN * .2, cards[3].get_bottom() + DOWN * .2, buff=0, color=YEL, path_arc=PI / 2)
        beat(self, Create(arr), t=1.6, rt=.8)


# ================= 쇼츠 전용 =================
class AQ(Scene):
    """닿지 않았는데 전압이 같다?"""
    def construct(self):
        A = opamp(RIGHT * 1.6 + UP * .3, 1.5)
        beat(self, FadeIn(A["g"]), Create(wire(A["m"] + LEFT * 2.6, A["m"])), Create(wire(A["p"] + LEFT * 2.6, A["p"])), t=1.0, rt=.6)
        v1 = card(tex(r"2.00\,\mathrm{V}", 44, YEL), YEL, .15).next_to(A["m"] + LEFT * 2.6, LEFT, .2)
        v2 = card(tex(r"2.00\,\mathrm{V}", 44, YEL), YEL, .15).next_to(A["p"] + LEFT * 2.6, LEFT, .2)
        beat(self, FadeIn(v1, shift=RIGHT * .2), t=1.0, rt=.4)
        beat(self, FadeIn(v2, shift=RIGHT * .2), t=1.0, rt=.4)
        gap = Brace(VGroup(A["sm"], A["sp"]), LEFT, color=RED).shift(LEFT * .2)
        beat(self, GrowFromCenter(gap), FadeIn(kr("안 닿음", 34, RED).next_to(A["tri"], DOWN, .3)), t=1.2, rt=.5)
        q = kr("같은 전압?", 54, YEL).move_to(DOWN * 2.8)
        beat(self, Write(q), t=1.2, rt=.6)


class BQ(Scene):
    """저항 두 개로 10배 (반전)."""
    def construct(self):
        C = inv((0, -.6), r"1\,k\Omega", r"10\,k\Omega"); C["all"].scale(.8, about_point=DOWN * .6).shift(DOWN * .4)
        beat(self, FadeIn(VGroup(C["amp"], C["tin"], C["wn"], C["gnd"], C["outw"], C["lin"], C["lout"], C["fb"][0], C["fb"][2:])), t=.9, rt=.5)
        beat(self, Create(C["r1"]), FadeIn(C["lr1"]), Create(C["rf"]), FadeIn(C["lrf"]), t=1.3, rt=.8)
        si = sine(LEFT * 4.3 + UP * 2.4, .14, 2, 3.0, BLU); so = sine(RIGHT * 4.1 + UP * 2.2, 1.0, 2, 3.0, YEL, phase=PI, sw=6)
        beat(self, Create(si), t=1.0, rt=.6)
        beat(self, Create(so), t=1.0, rt=.7)
        x = tex(r"\times 10", 90, YEL).move_to(UP * 2.3)
        beat(self, Write(x), t=.8, rt=.5)
        pulse(self, x, t=1.2)


class BRatio(Scene):
    """저항 비만 바꾸면 원하는 배율."""
    def construct(self):
        rf = ValueTracker(10)
        f = always_redraw(lambda: VGroup(tex(r"-\frac{R_f}{1\,k} =", 64, INK), DecimalNumber(-rf.get_value(), num_decimal_places=0, font_size=80, color=YEL), kr("배", 50, YEL)).arrange(RIGHT, buff=.25).shift(DOWN * 1.6))
        C = inv((0, 1.4)); C["all"].scale(.7, about_point=UP * 1.4)
        beat(self, FadeIn(C["all"]), FadeIn(f), t=1.0, rt=.5)
        for v in (20, 47, 100):
            self.play(rf.animate.set_value(v), C["rf"].animate.set_color(YEL), run_time=1.0)
            self.wait(.4)
        pulse(self, f, t=1.0)


class CQ(Scene):
    """1배 증폭기, 왜?"""
    def construct(self):
        A = opamp(UP * .5, 1.3)
        beat(self, FadeIn(A["g"]), t=.8, rt=.4)
        si = sine(LEFT * 4.4 + UP * .5, .6, 2, 2.6, BLU); so = sine(RIGHT * 4.4 + UP * .5, .6, 2, 2.6, YEL, sw=6)
        beat(self, Create(si), t=1.0, rt=.6)
        beat(self, Create(so), t=1.0, rt=.6)
        x = tex(r"\times 1", 90, YEL).move_to(DOWN * 2.0 + LEFT * 1.0)
        beat(self, Write(x), t=1.0, rt=.5)
        q = kr("왜 쓸까?", 56, INK).next_to(x, RIGHT, .6)
        beat(self, FadeIn(q, shift=LEFT * .2), t=1.2, rt=.4)


class CFol(Scene):
    """출력을 − 에 바로 → 그대로 따라감."""
    def construct(self):
        C = follower((-.6, .8))
        beat(self, FadeIn(VGroup(C["amp"], C["tin"], C["win"], C["outw"], C["lin"], C["lout"])), t=.8, rt=.4)
        beat(self, Create(C["fb"]), t=1.4, rt=1.0)
        si = sine(LEFT * 3.4 + DOWN * 2.4, .4, 2, 3.0, BLU); so = sine(RIGHT * 2.6 + DOWN * 2.4, .4, 2, 3.0, YEL, sw=6)
        beat(self, Create(si), Create(so), t=1.4, rt=.9)
        e = tex("=", 80, YEL).move_to(DOWN * 2.4 + LEFT * .4)
        beat(self, FadeIn(e), t=1.2, rt=.4)


class CCur(Scene):
    """입력 쪽 전류 거의 0."""
    def construct(self):
        C = follower((0, .8)); self.add(C["all"])
        a = iarrow(C["tin"].get_center() + RIGHT * .4 + UP * .4, C["p"] + LEFT * .5 + UP * .4, YEL, "i")
        beat(self, GrowArrow(a[0]), FadeIn(a[1]), t=1.0, rt=.5)
        x = Cross(a, stroke_color=RED, stroke_width=7)
        beat(self, Create(x), t=1.0, rt=.4)
        t = VGroup(kr("입력 전류", 46), tex(r"\approx 0", 70, YEL)).arrange(RIGHT, buff=.25).move_to(DOWN * 2.5)
        beat(self, FadeIn(t, shift=UP * .2), t=1.4, rt=.5)
        pulse(self, t, t=1.2)


class CLoad(Scene):
    """센서(5V, 10kΩ)에 1kΩ 부하: 바로 → 0.45V, 버퍼 → 5V."""
    def construct(self):
        r1 = VGroup(boxio("센서 5V", 2.4, 1.0, BLU), Arrow(ORIGIN, RIGHT * 1.3, buff=0, color=INK), boxio("부하", 1.8, 1.0, MUTE)).arrange(RIGHT, buff=.2).move_to(UP * 1.6 + LEFT * 1.6)
        for b in (r1[0], r1[2]): b[1].scale(.75)
        beat(self, FadeIn(r1), t=.9, rt=.4)
        v1 = tex(r"0.45\,\mathrm{V}", 60, RED).next_to(r1, RIGHT, .5)
        beat(self, FadeIn(v1), FadeIn(Cross(r1[1], stroke_color=RED, stroke_width=6)), t=1.4, rt=.5)
        r2 = VGroup(boxio("센서 5V", 2.4, 1.0, BLU), Arrow(ORIGIN, RIGHT * .6, buff=0, color=INK), opamp(ORIGIN, .5)["g"], Arrow(ORIGIN, RIGHT * .6, buff=0, color=INK), boxio("부하", 1.8, 1.0, MUTE)).arrange(RIGHT, buff=.2).move_to(DOWN * 1.2 + LEFT * 1.6)
        for b in (r2[0], r2[4]): b[1].scale(.75)
        beat(self, FadeIn(r2), t=1.0, rt=.4)
        v2 = tex(r"5\,\mathrm{V}", 60, YEL).next_to(r2, RIGHT, .5)
        beat(self, FadeIn(v2), t=1.2, rt=.4)
        pulse(self, v2, t=1.0)


class DQ(Scene):
    """오디오 믹서 속 덧셈 회로?"""
    def construct(self):
        M = mixer(LEFT * 2.6 + UP * .4)
        beat(self, FadeIn(M, lag_ratio=.3), t=1.2, rt=.8)
        p = tex("+", 120, YEL).move_to(RIGHT * 3.0 + UP * .4)
        beat(self, FadeIn(p, scale=.6), t=1.0, rt=.4)
        q = kr("덧셈 회로?", 56, YEL).move_to(DOWN * 2.7)
        beat(self, Write(q), t=1.2, rt=.6)
        beat(self, M[1][1].animate.shift(UP * .6), t=1.0, rt=.7)


class EQ(Scene):
    """잡음 섞인 신호 → ? → 깨끗한 신호."""
    def construct(self):
        n = noisy(LEFT * 4.0 + UP * .4, 3.6, .6, 2, .3, GRN, seed=7)
        beat(self, Create(n), FadeIn(kr("신호 + 잡음", 30, GRN).next_to(n, DOWN, .5)), t=1.2, rt=.8)
        b = boxio("?", 1.8, 1.4, YEL).move_to(UP * .4)
        beat(self, FadeIn(b), GrowArrow(Arrow(LEFT * 2.0 + UP * .4, LEFT * 1.0 + UP * .4, buff=0, color=INK)), t=1.0, rt=.4)
        c = sine(RIGHT * 4.0 + UP * .4, .9, 2, 3.6, YEL, sw=6)
        beat(self, GrowArrow(Arrow(RIGHT * 1.0 + UP * .4, RIGHT * 2.0 + UP * .4, buff=0, color=INK)), Create(c), t=1.4, rt=.9)
        t = kr("잡음만 쏙", 50, YEL).move_to(DOWN * 2.6)
        beat(self, Write(t), t=1.2, rt=.6)
