# 증시 롱폼(2026-10-14) 모션그래픽. 16:9, 핵심 내용은 가운데(가로 ±5.1)에 두어 세로 쇼츠에서도 잘라 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>   (1920×1080)
from manim import *
import numpy as np, json, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
D = json.load(open(os.path.join(os.path.dirname(__file__), "../../raw/stock1014/invest/data.json")))
T = json.load(open(os.path.join(os.path.dirname(__file__), "../../raw/stock1014/themes/data.json")))
KOSPI = D["daily"]["kospi"] + [["2026-10-13", 6035.35], ["2026-10-14", 6008.81]]   # 10/13·14 는 마감 기사 값
SPY = D["daily"]["spx"]


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)


class Diverge(Scene):
    """6/22(코스피 꼭대기) 이후 미국 vs 한국: S&P 500 은 최고, 코스피 −34%."""
    def construct(self):
        start = "2026-06-22"
        k = [x for x in KOSPI if x[0] >= start]; s = [x for x in SPY if x[0] >= start]
        kp = [100 * (x[1] / k[0][1] - 1) for x in k]; sp = [100 * (x[1] / s[0][1] - 1) for x in s]
        ax = Axes(x_range=[0, len(k) - 1, 10], y_range=[-40, 15, 10], x_length=10, y_length=5.4,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .4)
        zero = DashedLine(ax.c2p(0, 0), ax.c2p(len(k) - 1, 0), color=MUTE, stroke_width=2)
        h = head("6월 22일 이후, 같은 시장 다른 길")
        self.play(FadeIn(h), Create(ax), Create(zero), run_time=.8)
        n = len(k); xs = np.linspace(0, n - 1, len(s))
        ls = ax.plot_line_graph(xs, sp, line_color=BLU, add_vertex_dots=False, stroke_width=7)
        lk = ax.plot_line_graph(list(range(n)), kp, line_color=RED, add_vertex_dots=False, stroke_width=7)
        self.play(Create(ls), Create(lk), run_time=2.6, rate_func=linear)
        lu = kr(f"미국 S&P 500  {sp[-1]:+.0f}%  사상 최고", 34, BLU).next_to(ax.c2p(n - 1, sp[-1]), UP, .2).shift(LEFT * 2.2)
        lkk = kr(f"코스피  {kp[-1]:+.0f}%", 40, RED).next_to(ax.c2p(n - 1, kp[-1]), DOWN, .2).shift(LEFT * 1.2)
        self.play(FadeIn(lu, shift=UP * .2), FadeIn(lkk, shift=DOWN * .2), Flash(ax.c2p(n - 1, kp[-1]), color=RED), run_time=.9)
        self.wait(3)


class KospiPath(Scene):
    """코스피 1년: 3260 → 9114(6/22) → 6008. +84%(1년) / −34%(고점 대비)."""
    def construct(self):
        v = [x[1] for x in KOSPI]; n = len(v)
        ax = Axes(x_range=[0, n - 1, 50], y_range=[2500, 10000, 1000], x_length=10, y_length=5.6,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .35)
        h = head("코스피 1년")
        self.play(FadeIn(h), Create(ax), run_time=.7)
        line = ax.plot_line_graph(list(range(n)), v, line_color=ORG, add_vertex_dots=False, stroke_width=6)
        self.play(Create(line), run_time=2.4, rate_func=linear)
        ip = int(np.argmax(v))
        pts = [(0, v[0], "1년 전 3,260", MUTE, UP), (ip, v[ip], "꼭대기 9,114 (6/22)", YEL, UP), (n - 1, v[-1], "오늘 6,008", RED, RIGHT)]
        dots = VGroup()
        for i, y, t, c, d in pts:
            p = ax.c2p(i, y); dots.add(VGroup(Dot(p, .12, color=c), kr(t, 30, c).next_to(p, d, .15)))
        self.play(LaggedStart(*[FadeIn(d, scale=1.2) for d in dots], lag_ratio=.35), run_time=1.4)
        b1 = kr("1년 +84%", 44, GRN); b2 = kr("고점 대비 −34%", 44, RED)
        g = VGroup(b1, b2).arrange(RIGHT, buff=1.0)
        self.play(FadeIn(card(g).scale(.9).to_corner(DR, buff=.35).shift(UP * .9 + LEFT * 1.2), shift=UP * .3), run_time=.8)
        self.play(Indicate(b2, color=RED, scale_factor=1.08)); self.wait(2.5)


class Flows(Scene):
    """오늘(10/14) 코스피 수급: 외국인 −1조1614억, 개인 −3203억, 기관 +7876억."""
    def construct(self):
        h = head("10월 14일 코스피 · 누가 팔았나")
        self.play(FadeIn(h))
        data = [("외국인", -11614, RED), ("개인", -3203, ORG), ("기관", 7876, GRN)]
        base = Line(LEFT * .0 + DOWN * 2.3, UP * 2.3, color=MUTE, stroke_width=3)
        rows = VGroup()
        for i, (nm, val, c) in enumerate(data):
            y = 1.3 - i * 1.5; w = abs(val) / 11614 * 3.6
            bar = Rectangle(width=w, height=.85, stroke_width=0, fill_color=c, fill_opacity=.9)
            bar.move_to([w / 2 if val > 0 else -w / 2, y, 0])
            lab = kr(nm, 38).move_to([-5.9, y, 0])
            num = kr(f"{val:+,}억".replace("-", "−"), 36, c)
            if w > 2.4:
                num.set_color(BG).move_to(bar)
            else:
                num.next_to(bar, RIGHT if val > 0 else LEFT, .2)
            rows.add(VGroup(lab, bar, num))
        self.play(Create(base), run_time=.4)
        for r in rows:
            self.play(FadeIn(r[0]), GrowFromEdge(r[1], LEFT if r[1].get_center()[0] > 0 else RIGHT), FadeIn(r[2]), run_time=.7)
        note = kr("6거래일 연속 하락 · 6,008 (−0.44%)", 34, YEL).to_edge(DOWN, buff=.5)
        self.play(FadeIn(note)); self.wait(2.5)


class ThemeBars(Scene):
    """미국 27개 테마 1주 수익률 줄 세우기: 꼴찌 양자·광통신·데이터센터·드론, 1등 석유가스·핀테크."""
    def construct(self):
        rows = sorted([(t["name"].replace(", ", "·").replace(",", "·"), t["path"]["w1"][-1] * 100) for t in T["themes"]], key=lambda r: -r[1])
        h = head("미국 27개 테마 · 1주 수익률")
        self.play(FadeIn(h))
        n = len(rows); W = 10.4; bw = W / n
        ax0 = Line([-W / 2, 0, 0], [W / 2, 0, 0], color=MUTE, stroke_width=3).shift(UP * .9)
        bars = VGroup()
        for i, (nm, r) in enumerate(rows):
            hgt = abs(r) / 18 * 3.6
            c = GRN if i < 2 else (RED if i >= n - 4 else ("#3a3f4b" if r < 0 else "#4b5363"))
            b = Rectangle(width=bw * .78, height=max(hgt, .02), stroke_width=0, fill_color=c, fill_opacity=1)
            b.move_to([-W / 2 + bw * (i + .5), .9 + (hgt / 2 if r > 0 else -hgt / 2), 0]); bars.add(b)
        self.play(Create(ax0), LaggedStart(*[GrowFromEdge(b, DOWN if b.get_center()[1] > .9 else UP) for b in bars], lag_ratio=.03), run_time=2)
        top = VGroup(*[kr(f"{rows[i][0]} {rows[i][1]:+.1f}%", 30, GRN) for i in range(2)]).arrange(DOWN, aligned_edge=LEFT, buff=.1).move_to([-3.4, 2.1, 0])
        bot = VGroup(*[kr(f"{rows[i][0]} {rows[i][1]:+.1f}%", 32, RED) for i in range(n - 1, n - 5, -1)]).arrange(DOWN, aligned_edge=RIGHT, buff=.1).move_to([-1.2, -1.7, 0])
        self.play(FadeIn(top, shift=RIGHT * .2), run_time=.6)
        self.play(FadeIn(bot, shift=LEFT * .2), *[Indicate(bars[i], color=RED) for i in range(n - 4, n)], run_time=1)
        tag = kr("AI 테마에서 → 실적이 보이는 쪽으로", 36, YEL).to_edge(DOWN, buff=.35)
        self.play(FadeIn(tag)); self.wait(2.5)


class Warnings(Scene):
    """경고등 3개: 10년물 5.24%(2002년 이후 최고) · 유가 $61→$96(+58%) · 연준 9월 인상 3.75→4.00%. VIX 15."""
    def construct(self):
        h = head("경고등 3개", RED)
        self.play(FadeIn(h))
        b = [x for x in D["bond"] if x[0] >= "1995"]
        ax = Axes(x_range=[0, len(b) - 1, 60], y_range=[0, 7, 1], x_length=3.6, y_length=2.1,
                  axis_config={"stroke_color": MUTE, "stroke_width": 2, "include_ticks": False})
        ln = ax.plot_line_graph(list(range(len(b))), [x[1] for x in b], line_color=PUR, add_vertex_dots=False, stroke_width=4)
        c1 = VGroup(kr("① 미국 10년물 금리", 30, MUTE), kr("5.24%", 64, PUR), VGroup(ax, ln), kr("2002년 이후 최고", 28, PUR)).arrange(DOWN, buff=.2)
        c2 = VGroup(kr("② 국제 유가", 30, MUTE), kr("$96", 64, ORG), kr("1년 전 $61 → +58%", 30, ORG)).arrange(DOWN, buff=.3)
        c3 = VGroup(kr("③ 물가 → 연준", 30, MUTE), kr("4.00%", 64, RED), kr("9월 오히려 인상 (3.75→4.00)", 28, RED)).arrange(DOWN, buff=.3)
        cards = VGroup(*[card(c) for c in (c1, c2, c3)]).arrange(RIGHT, buff=.3).scale(.74).shift(DOWN * .1)
        for cc in cards:
            self.play(FadeIn(cc, shift=UP * .3), run_time=.7); self.wait(.4)
        self.play(Create(ln), run_time=1.2)
        vix = kr("그런데 공포지수 VIX 15 · 시장은 아직 차분", 34, GRN).to_edge(DOWN, buff=.35)
        self.play(FadeIn(vix)); self.wait(2.5)


class Week(Scene):
    """이번 주 체크포인트: 수 밤 CPI(예상 3.6%) · 목 TSMC 실적 · 금 연준 의장."""
    def construct(self):
        h = head("이번 주 체크포인트")
        self.play(FadeIn(h))
        days = [("수 · 오늘 밤 21:30", "미국 9월 소비자물가", "예상 3.6%", YEL), ("목", "TSMC 실적", "AI 반도체 주문, 첫 숫자", BLU), ("금", "연준 의장 발언", "10월 금리 힌트", MUTE)]
        cs = VGroup()
        for d, t, s, c in days:
            cs.add(card(VGroup(kr(d, 30, c), kr(t, 42, INK), kr(s, 30, c)).arrange(DOWN, buff=.25), color=c if c != MUTE else "#2a2e37"))
        cs.arrange(RIGHT, buff=.35).scale(.8).shift(DOWN * .2)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cs], lag_ratio=.4), run_time=1.6)
        self.play(Indicate(cs[0], color=YEL, scale_factor=1.05), run_time=.8); self.wait(.6)
        self.play(Indicate(cs[1], color=BLU, scale_factor=1.05), run_time=.8); self.wait(2.5)


class Scenario(Scene):
    """오늘 밤 물가: 예상보다 낮으면 / 높으면."""
    def construct(self):
        h = head("오늘 밤 물가, 두 갈래")
        top = card(kr("미국 9월 소비자물가 · 예상 3.6%", 38, YEL)).shift(UP * 1.8)
        self.play(FadeIn(h), FadeIn(top))
        L = VGroup(kr("예상보다 낮으면", 40, GRN), kr("10년물 금리 ↓", 34), kr("성장주·반도체 숨통", 34, GRN)).arrange(DOWN, buff=.3)
        R = VGroup(kr("예상보다 높으면", 40, RED), kr("10월 추가 인상 우려 ↑", 34), kr("AI 조정 길어짐 · 실적주 버팀", 32, RED)).arrange(DOWN, buff=.3)
        cl, cr = card(L, GRN), card(R, RED)
        VGroup(cl, cr).arrange(RIGHT, buff=1.0).shift(DOWN * 1.1)
        a1 = Arrow(top.get_bottom(), cl.get_top(), color=GRN, stroke_width=6, buff=.1)
        a2 = Arrow(top.get_bottom(), cr.get_top(), color=RED, stroke_width=6, buff=.1)
        self.play(GrowArrow(a1), FadeIn(cl, shift=DOWN * .2), run_time=.9); self.wait(.8)
        self.play(GrowArrow(a2), FadeIn(cr, shift=DOWN * .2), run_time=.9); self.wait(3)


class Summary(Scene):
    def construct(self):
        h = head("세 줄 요약", YEL)
        ls = [("1", "코스피 고점 대비 −34% · 외국인 차익 실현", RED), ("2", "미국 지수는 최고 · AI → 실적주 자리 바꾸기", BLU), ("3", "이번 주: 오늘 밤 물가 · 목요일 TSMC", YEL)]
        g = VGroup()
        for n, t, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), kr(t, 40)).arrange(RIGHT, buff=.4))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.55).shift(DOWN * .1)
        self.play(FadeIn(h))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * .3) for r in g], lag_ratio=.5), run_time=2)
        foot = kr("📊 금리·주가 50년 /invest   ·   🔥 테마 강도 /themes", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(3)


def theme_ret(name, p):
    t = next(x for x in T["themes"] if x["name"] == name)
    return 100 * t["path"][p][-1]


class LongView(Scene):
    """같은 테마, 1주 vs 올해: 광통신 −16% / +80%, 반도체 −10% / +81%, 양자 −17% / −37%, 석유·가스 +3% / +52%."""
    def construct(self):
        h = head("1주일 vs 올해, 같은 테마 다른 그림")
        self.play(FadeIn(h))
        names = [("광통신", "광통신"), ("반도체", "반도체"), ("양자", "양자"), ("석유,가스", "석유·가스")]
        ax_y = DOWN * .75; sc = 2.2 / 90                       # 90% = 2.6 단위
        base = Line(LEFT * 6, RIGHT * 6, color=MUTE, stroke_width=3).shift(ax_y)
        self.play(Create(base), run_time=.5)
        groups = []
        for i, (key, lab) in enumerate(names):
            x = -4.5 + i * 3.0
            w, y = theme_ret(key, "w1"), theme_ret(key, "ytd")
            bars = VGroup()
            for dx, v, c in ((-.42, w, MUTE), (.42, y, GRN if y > 0 else RED)):
                r = Rectangle(width=.7, height=max(abs(v) * sc, .04), stroke_width=0, fill_color=c, fill_opacity=1)
                r.move_to(ax_y + RIGHT * (x + dx) + UP * (np.sign(v) * abs(v) * sc / 2))
                t = kr(f"{v:+.0f}%", 30, c if c != MUTE else INK).next_to(r, UP if v > 0 else DOWN, .12)
                bars.add(VGroup(r, t))
            name = kr(lab, 36).move_to(RIGHT * x + DOWN * 3.3)
            groups.append((bars, name))
        leg = VGroup(VGroup(Square(.3, fill_color=MUTE, fill_opacity=1, stroke_width=0), kr("이번 주", 28, MUTE)).arrange(RIGHT, buff=.15),
                     VGroup(Square(.3, fill_color=GRN, fill_opacity=1, stroke_width=0), kr("올해", 28, GRN)).arrange(RIGHT, buff=.15)).arrange(RIGHT, buff=.5).next_to(h, DOWN, .2)
        self.play(FadeIn(leg))
        for bars, name in groups:
            self.play(FadeIn(name), GrowFromEdge(bars[0][0], UP if bars[0][0].get_center()[1] < ax_y[1] else DOWN), FadeIn(bars[0][1]), run_time=.45)
        self.wait(.4)
        self.play(*[AnimationGroup(GrowFromEdge(b[1][0], DOWN if b[1][0].get_center()[1] > ax_y[1] else UP), FadeIn(b[1][1])) for b, _ in groups], run_time=1.2)
        self.play(Indicate(groups[2][0][1], color=RED, scale_factor=1.08), run_time=.9)
        self.wait(3)


class Signals(Scene):
    """내 사이트 '오늘의 신호' (10/13 데이터): S&P 500 분할 매수 · 10년 국채 일부 매수 · SCHD 보유 · QQQ 추가 매수 보류."""
    def construct(self):
        h = head("내 사이트 · 오늘의 신호")
        sub = kr("10월 13일 데이터 · 매일 자동 계산", 28, MUTE).next_to(h, DOWN, .25)
        self.play(FadeIn(h), FadeIn(sub))
        rows = [("S&P 500", "분할 매수", RED), ("10년 국채", "일부 매수", RED), ("SCHD", "보유", MUTE), ("QQQ", "추가 매수 보류", YEL)]
        cs = VGroup()
        for n, s, c in rows:
            pill = VGroup(RoundedRectangle(corner_radius=.25, width=3.3, height=.8, fill_color=c, fill_opacity=.18, stroke_color=c, stroke_width=3), kr(s, 34, c))
            pill[1].move_to(pill[0])
            cs.add(card(VGroup(kr(n, 40), pill).arrange(DOWN, buff=.35), color="#2a2e37"))
        cs.arrange(RIGHT, buff=.3).scale_to_fit_width(13).shift(DOWN * .1)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cs], lag_ratio=.35), run_time=1.6)
        self.wait(.8)
        self.play(Indicate(cs[3], color=YEL, scale_factor=1.06), run_time=.9)
        q = kr("“금리·물가·유가가 한꺼번에 불리했던 적은 많지 않다”", 32, MUTE).to_edge(DOWN, buff=.9)
        self.play(FadeIn(q, shift=UP * .2)); self.wait(3)
