# 증시 롱폼(2026-10-17) 모션그래픽. 16:9, 핵심 내용은 가운데(가로 ±5.1)에 두어 세로 쇼츠에서도 잘라 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>   (1920×1080)
from manim import *
import numpy as np, json, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
D = json.load(open(os.path.join(os.path.dirname(__file__), "../../raw/stock1017/invest/data.json")))
T = json.load(open(os.path.join(os.path.dirname(__file__), "../../raw/stock1017/themes/data.json")))
_K = os.path.join(os.path.dirname(__file__), "../../raw/stock1017/kospi_today.json")   # 마감 후 채움: {"close":…, "pct":…, "flows":{…}}
KT = json.load(open(_K)) if os.path.exists(_K) else None
KOSPI = D["daily"]["kospi"] + [["2026-10-16", 5668.05]]   # 10/16 종가는 기사(아시아경제·머니투데이)
SPY = D["daily"]["spx"]


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)


class KospiPath(Scene):
    """코스피 1년: 꼭대기 9114(6/22) → 10/2 7003 → 10/16 5668."""
    def construct(self):
        v = [x[1] for x in KOSPI]; n = len(v)
        ax = Axes(x_range=[0, n - 1, 50], y_range=[2500, 10000, 1000], x_length=10, y_length=5.6,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .35)
        h = head("코스피 1년")
        self.play(FadeIn(h), Create(ax), run_time=.7)
        line = ax.plot_line_graph(list(range(n)), v, line_color=ORG, add_vertex_dots=False, stroke_width=6)
        self.play(Create(line), run_time=2.4, rate_func=linear)
        ip = int(np.argmax(v))
        pts = [(0, v[0], "1년 전 3,260", MUTE, UP), (ip, v[ip], "꼭대기 9,114 (6/22)", YEL, UP), (n - 1, v[-1], "10/16 5,668", RED, DOWN)]
        dots = VGroup()
        for i, y, t, c, d in pts:
            p = ax.c2p(i, y); dots.add(VGroup(Dot(p, .12, color=c), kr(t, 30, c).next_to(p, d, .15)))
        i2 = next(i for i, x in enumerate(KOSPI) if x[0] == "2026-10-02")
        dots.add(VGroup(Dot(ax.c2p(i2, v[i2]), .1, color=INK), kr("10/2 7,003", 26, INK).next_to(ax.c2p(i2, v[i2]), UP, .12)))
        self.play(LaggedStart(*[FadeIn(d, scale=1.2) for d in dots], lag_ratio=.35), run_time=1.4)
        b1 = kr(f"10/2 대비 {100 * (v[-1] / v[i2] - 1):.0f}%".replace("-", "−"), 44, ORG); b2 = kr(f"고점 대비 {100 * (v[-1] / v[ip] - 1):.0f}%".replace("-", "−"), 44, RED)
        g = VGroup(b1, b2).arrange(RIGHT, buff=1.0)
        self.play(FadeIn(card(g).scale(.8).to_corner(DR, buff=.4).shift(UP * 1.0), shift=UP * .3), run_time=.8)
        self.play(Indicate(b2, color=RED, scale_factor=1.08)); self.wait(2.5)



class ThemeWeek(Scene):
    """미국 27개 테마 · 10/14 하루 수익률: 26개 하락, 농산물만 +."""
    def construct(self):
        rows = sorted([(100 * x["path"]["w1"][-1], x["name"]) for x in T["themes"]], reverse=True)
        h = head("미국 27개 테마 · 이번 주 (5거래일)")
        self.play(FadeIn(h))
        n = len(rows); w = 11.5 / n; sc = 3.0 / 24
        base = Line(LEFT * 6, RIGHT * 6, color=MUTE, stroke_width=3).shift(UP * 1.4)
        self.play(Create(base), run_time=.4)
        bars = VGroup()
        for i, (v, name) in enumerate(rows):
            c = GRN if v > 0 else (RED if v <= -14 else "#3a3f4b")
            r = Rectangle(width=w * .75, height=max(abs(v) * sc, .04), stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to(base.get_left() + RIGHT * (w * (i + .5) + .25), aligned_edge=UP if v < 0 else DOWN)
            if v > 0: r.align_to(base, DOWN)
            else: r.align_to(base, UP)
            bars.add(r)
        self.play(LaggedStart(*[GrowFromEdge(b, UP if rows[i][0] < 0 else DOWN) for i, b in enumerate(bars)], lag_ratio=.04), run_time=1.8)
        up = VGroup(*[kr(f"{nm.replace(',', '·')} +{v:.1f}%", 26, GRN) for v, nm in rows[:3]]).arrange(DOWN, aligned_edge=LEFT, buff=.1).move_to(base.get_left() + RIGHT * 1.7 + DOWN * .9)
        worst = VGroup(*[kr(f"{nm.replace(',', '·')} {v:.1f}%", 28, RED) for v, nm in rows[-3:][::-1]]).arrange(DOWN, aligned_edge=RIGHT, buff=.12).next_to(bars[-6], LEFT, .35).align_to(bars[-1], DOWN)
        self.play(FadeIn(up), FadeIn(worst, shift=LEFT * .2), run_time=.8)
        big = kr("27개 중 23개 하락", 46, YEL).to_edge(DOWN, buff=.5)
        self.play(Write(big), run_time=.8); self.wait(3)



class BlackThursday(Scene):
    """이번 주 코스피 종가: 10/12 6384 → 10/13 6035 → 10/14 6009 → 10/15 5554(−7.57%, 서킷브레이커) → 10/16 5668(+2.05%)."""
    def construct(self):
        h = head("이번 주 코스피 · 검은 목요일")
        self.play(FadeIn(h))
        days = [("월", 6384.24), ("화", 6035.35), ("수", 6008.81), ("목", 5554.22), ("금", 5668.05)]
        ax = Axes(x_range=[-.5, 4.5, 1], y_range=[5300, 6700, 200], x_length=10, y_length=4.8,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .55)
        self.play(Create(ax), run_time=.5)
        bars = VGroup(); labs = VGroup()
        for i, (dn, v) in enumerate(days):
            c = RED if i == 3 else (GRN if i == 4 else "#3a3f4b")
            top = ax.c2p(i, v); bot = ax.c2p(i, 5300)
            r = Rectangle(width=1.2, height=top[1] - bot[1], stroke_width=0, fill_color=c, fill_opacity=1).move_to(bot, aligned_edge=DOWN)
            bars.add(r); labs.add(VGroup(kr(dn, 32, MUTE).next_to(bot, DOWN, .2), kr(f"{v:,.0f}", 30, c if i >= 3 else INK).next_to(r, UP, .12)))
        for r, l in zip(bars, labs):
            self.play(GrowFromEdge(r, DOWN), FadeIn(l), run_time=.45)
        ev = VGroup(kr("09:07 사이드카", 26, YEL), kr("12:38 서킷브레이커", 26, RED), kr("−7.57%", 40, RED)).arrange(DOWN, buff=.1).move_to(ax.c2p(2.6, 6480))
        self.play(FadeIn(ev, shift=DOWN * .2), Flash(bars[3].get_top(), color=RED), run_time=.8)
        fr = kr("+2.05%", 34, GRN).next_to(labs[4][1], UP, .1)
        wk = card(kr("한 주 −14.5%", 40, RED), color=RED).to_corner(UR, buff=.5).shift(DOWN * .9)
        self.play(FadeIn(fr), FadeIn(wk, shift=LEFT * .2)); self.wait(3)


class ForeignSell(Scene):
    """외국인 순매도: 10/15 하루 3조 6243억 · 10월 누적 17조 8345억(그중 삼성전자·SK하이닉스 14조)."""
    def construct(self):
        h = head("외국인, 얼마나 팔았나")
        self.play(FadeIn(h))
        a = card(VGroup(kr("10월 15일 하루", 30, MUTE), kr("−3조 6천억", 60, RED)).arrange(DOWN, buff=.2), color=RED)
        b = card(VGroup(kr("10월 누적 (2일~15일)", 30, MUTE), kr("−17조 8천억", 60, RED), kr("그중 삼성전자·SK하이닉스 14조", 28, ORG)).arrange(DOWN, buff=.2), color=RED)
        VGroup(a, b).arrange(RIGHT, buff=.8).shift(UP * .2)
        self.play(FadeIn(a, shift=UP * .3)); self.play(FadeIn(b, shift=UP * .3))
        n = kr("16일(금)엔 3,410억 순매수로 돌아섬", 32, GRN).to_edge(DOWN, buff=.7)
        self.play(FadeIn(n)); self.wait(3)


class Paradox(Scene):
    """실적 vs 주가: TSMC 순이익 +68.7% · 4분기 매출 전망 최대 543억 달러 · 삼성 107.4조 ↔ 미국 반도체 8일 연속 하락(2008년 이후 최장), 시총 약 2조 달러 증발."""
    def construct(self):
        h = head("실적은 역대 최고 · 주가는 폭락")
        self.play(FadeIn(h))
        L = card(VGroup(kr("실적", 34, GRN), kr("TSMC 순이익 +68.7%", 36), kr("4분기 매출 전망 최대 $543억", 28, MUTE), kr("삼성전자 영업이익 107조", 36), kr("국내 첫 분기 100조", 28, MUTE)).arrange(DOWN, buff=.2), color=GRN)
        R = card(VGroup(kr("주가", 34, RED), kr("미국 반도체 8일 연속 ↓", 36), kr("2008년 이후 최장", 28, MUTE), kr("시총 약 2조 달러 증발", 36), kr("≈ 2,700조 원", 28, MUTE)).arrange(DOWN, buff=.2), color=RED)
        VGroup(L, R).arrange(RIGHT, buff=1.4).shift(DOWN * .2)
        vs = kr("VS", 48, YEL).move_to((L.get_right() + R.get_left()) / 2)
        self.play(FadeIn(L, shift=RIGHT * .3)); self.play(FadeIn(vs, scale=1.5)); self.play(FadeIn(R, shift=LEFT * .3))
        self.wait(3)


class AiDebt(Scene):
    """AI 거품 논쟁의 고리: 빚 → 데이터센터 → 금리↑ → 비용↑ → '앞으로도 벌어서 갚을 수 있나?'"""
    def construct(self):
        h = head("시장이 의심하는 것")
        self.play(FadeIn(h))
        steps = [("빚을 내서", MUTE), ("AI 데이터센터 건설", BLU), ("금리 ↑ → 이자 비용 ↑", ORG), ("앞으로도 벌어서 갚을 수 있나?", RED)]
        boxes = VGroup(*[card(kr(t, 40, c if c != MUTE else INK), color=c) for t, c in steps]).arrange(DOWN, buff=.4).scale(.9).shift(DOWN * .45 + LEFT * 2.2)
        arrows = VGroup(*[Arrow(boxes[i].get_bottom(), boxes[i + 1].get_top(), buff=.05, color=MUTE, stroke_width=5) for i in range(3)])
        for i, b in enumerate(boxes):
            self.play(FadeIn(b, shift=RIGHT * .2), *( [GrowArrow(arrows[i - 1])] if i else []), run_time=.55)
        ex = VGroup(kr("예) 코어위브", 30, INK), kr("채권 가격 '위험 신호' 수준", 28, MUTE), kr("한국 반도체 추가 악재", 30, INK), kr("중국 D램 추격", 28, MUTE), kr("자사주 매입 종료", 28, MUTE), kr("유가 100달러", 28, MUTE)).arrange(DOWN, aligned_edge=LEFT, buff=.18).to_edge(RIGHT, buff=.9).shift(DOWN * .2)
        self.play(FadeIn(ex, shift=UP * .2)); self.play(Indicate(boxes[3], color=RED, scale_factor=1.06)); self.wait(2.5)


class Warsh(Scene):
    """10/16 연준 의장 케빈 워시: 10월 인상 신호 없음 · 'AI 길은 매우 울퉁불퉁' · 인상 확률 27%→15%(FT)."""
    def construct(self):
        h = head("연준 의장 케빈 워시 · 10월 16일")
        self.play(FadeIn(h))
        q1 = card(kr("“회의 결과를 미리 판단하지 않는다”", 36), color=BLU).shift(UP * 1.4)
        q2 = card(kr("“AI가 가는 길은 매우 울퉁불퉁할 것”", 36), color=ORG).next_to(q1, DOWN, .4)
        self.play(FadeIn(q1, shift=UP * .2)); self.play(FadeIn(q2, shift=UP * .2))
        a = kr("10월 인상 확률  27%", 40, MUTE); b = kr("15%", 48, GRN)
        g = VGroup(a, Arrow(LEFT, RIGHT, color=YEL, stroke_width=6).scale(.6), b).arrange(RIGHT, buff=.3).to_edge(DOWN, buff=1.0)
        self.play(FadeIn(g)); src = kr("파이낸셜타임스 보도 기준", 24, MUTE).next_to(g, DOWN, .2)
        self.play(FadeIn(src)); self.wait(3)


class SignalChange(Scene):
    """내 사이트 '오늘의 신호' 변화: 10/14 → 10/16. S&P 분할 매수→보유, SCHD 보유→추가 매수 보류, QQQ 추가 매수 보류→비중 축소, 10년 국채 일부 매수 유지."""
    def construct(self):
        h = head("내 사이트 신호가 바뀌었다")
        sub = kr("10월 14일 → 10월 16일 · 매일 자동 계산", 28, MUTE).next_to(h, DOWN, .25)
        self.play(FadeIn(h), FadeIn(sub))
        rows = [("S&P 500", "분할 매수", RED, "보유", MUTE), ("SCHD", "보유", MUTE, "추가 매수 보류", YEL), ("QQQ", "추가 매수 보류", YEL, "비중 축소", BLU), ("10년 국채", "일부 매수", RED, "일부 매수", RED)]
        def pill(t, c):
            p = VGroup(RoundedRectangle(corner_radius=.25, width=3.4, height=.72, fill_color=c, fill_opacity=.18, stroke_color=c, stroke_width=3), kr(t, 30, c)); p[1].move_to(p[0]); return p
        g = VGroup()
        for i, (n, a, ca, b, cb) in enumerate(rows):
            y = 1.25 - i * 1.0
            r = VGroup(kr(n, 34).move_to([-4.6, y, 0]), pill(a, ca).move_to([-1.3, y, 0]), Arrow([.6, y, 0], [1.6, y, 0], color=MUTE, stroke_width=5, buff=0), pill(b, cb).move_to([3.6, y, 0]))
            g.add(r)
        for r in g:
            self.play(FadeIn(r[0]), FadeIn(r[1]), run_time=.35)
        self.play(*[AnimationGroup(GrowArrow(r[2]), FadeIn(r[3], shift=RIGHT * .2)) for r in g], run_time=1.0)
        self.play(Indicate(g[2][3], color=BLU, scale_factor=1.08), run_time=.9)
        self.wait(2.5)


class NextWeek(Scene):
    """다음 주 이후 일정: 10/20 넷플릭스 · 10/21 테슬라·TI · 10/27~28 연준 회의 · 10/29 삼성전자 확정 실적 · 이달 말 SK하이닉스."""
    def construct(self):
        h = head("다음 주부터 꼭 볼 날짜")
        self.play(FadeIn(h))
        items = [("10/20 (화)", "넷플릭스", MUTE), ("10/21 (수)", "테슬라 · TI", YEL), ("10/27~28", "연준 회의", RED), ("10/29 (목)", "삼성전자 확정 실적", BLU), ("10월 말", "SK하이닉스 실적", BLU)]
        cs = VGroup(*[card(VGroup(kr(d, 28, c if c != MUTE else INK), kr(t, 34)).arrange(DOWN, buff=.2), color=c if c != MUTE else "#2a2e37") for d, t, c in items])
        top = VGroup(*cs[:3]).arrange(RIGHT, buff=.35); bot = VGroup(*cs[3:]).arrange(RIGHT, buff=.35)
        VGroup(top, bot).arrange(DOWN, buff=.45).scale_to_fit_width(11.5).shift(UP * .15)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cs], lag_ratio=.3), run_time=1.8)
        self.play(Indicate(cs[1], color=YEL, scale_factor=1.06), run_time=.7)
        n = kr("TI = 반도체 경기의 온도계 · 키움 '실적 약하면 코스피 5100'", 28, MUTE).to_edge(DOWN, buff=.8)
        self.play(FadeIn(n)); self.wait(2.5)


class UsWeek(Scene):
    """10/16(금) 미국장: 나스닥 −2.1% · S&P 500 −1.1% · 다우 −0.3% · 나스닥 작년 4월 이후 최악의 주."""
    def construct(self):
        h = head("10월 16일(금) 미국장")
        self.play(FadeIn(h))
        rows = [("나스닥", -2.1, RED), ("S&P 500", -1.1, ORG), ("다우", -0.3, MUTE)]
        g = VGroup()
        for i, (n, v, c) in enumerate(rows):
            y = 1.2 - i * 1.25
            lab = kr(n, 38).move_to(LEFT * 3.0 + UP * y, aligned_edge=RIGHT)
            r = Rectangle(width=abs(v) * 2.8, height=.75, stroke_width=0, fill_color=c, fill_opacity=1).move_to(LEFT * 2.6 + UP * y, aligned_edge=LEFT)
            g.add(VGroup(lab, r, kr(f"{v:+.1f}%", 38, c).next_to(r, RIGHT, .3)))
        for row in g:
            self.play(FadeIn(row[0]), GrowFromEdge(row[1], LEFT), FadeIn(row[2]), run_time=.5)
        tag = card(kr("나스닥 · 작년 4월 관세 충격 이후 최악의 한 주", 32, YEL), color=YEL).to_edge(DOWN, buff=.6)
        self.play(FadeIn(tag, shift=UP * .2)); self.wait(3)


class Summary(Scene):
    def construct(self):
        h = head("세 줄 요약", YEL)
        ls = [("1", "물가 3.7% → 서킷브레이커 · 코스피 한 주 −14.5%", RED), ("2", "실적은 최고 · 'AI 투자가 계속 돈이 될까' 의심", BLU), ("3", "다음: 21일 테슬라·TI → 연준 회의 → 삼성·하이닉스", YEL)]
        g = VGroup()
        for n, t, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), kr(t, 36)).arrange(RIGHT, buff=.4))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.55).shift(DOWN * .1)
        self.play(FadeIn(h))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * .3) for r in g], lag_ratio=.5), run_time=2)
        foot = kr("금리·주가 50년 /invest   ·   테마 강도 /themes", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(3)


class CircuitHistory(Scene):
    """서킷브레이커 다음 날: 역대 15일 중 9일 상승(파이낸셜뉴스) · 7월 말 그 주에 하루 +17.9%(이투데이) · NH 다음 주 5100~6100."""
    def construct(self):
        h = head("서킷브레이커, 그다음엔?")
        self.play(FadeIn(h))
        dots = VGroup(*[Circle(.32, stroke_width=0, fill_color=GRN if i < 9 else "#3a3f4b", fill_opacity=1) for i in range(15)]).arrange(RIGHT, buff=.18).shift(UP * 1.3)
        lab = kr("코스피 서킷브레이커 15번 중 9번, 다음 날 상승", 36, GRN).next_to(dots, DOWN, .35)
        self.play(LaggedStart(*[FadeIn(d, scale=.5) for d in dots], lag_ratio=.06), run_time=1.4); self.play(FadeIn(lab))
        a = card(VGroup(kr("이번 주 금요일", 28, MUTE), kr("+2.05%", 48, GRN)).arrange(DOWN, buff=.15), color=GRN)
        b = card(VGroup(kr("7월 말 서킷 주간", 28, MUTE), kr("하루 +17.9%", 48, YEL)).arrange(DOWN, buff=.15), color=YEL)
        c = card(VGroup(kr("NH투자증권 다음 주", 28, MUTE), kr("5100 ~ 6100", 48, BLU)).arrange(DOWN, buff=.15), color=BLU)
        VGroup(a, b, c).arrange(RIGHT, buff=.4).scale_to_fit_width(12).shift(DOWN * 1.5)
        self.play(LaggedStart(FadeIn(a, shift=UP * .2), FadeIn(b, shift=UP * .2), FadeIn(c, shift=UP * .2), lag_ratio=.4), run_time=1.4)
        self.wait(3)


class KoreaVsUs(Scene):
    """이번 주(10/12~16) 하락률: S&P 500 −2.0% · QQQ −5.5% · 코스피 −14.5% — 반도체 비중 때문."""
    def construct(self):
        h = head("이번 주, 왜 한국만 더 빠졌나")
        self.play(FadeIn(h))
        rows = [("S&P 500", -2.0, MUTE), ("QQQ (나스닥100)", -5.5, ORG), ("코스피", -14.5, RED)]
        g = VGroup()
        for i, (n, v, c) in enumerate(rows):
            y = 1.3 - i * 1.25
            lab = kr(n, 36).move_to(LEFT * 2.6 + UP * y, aligned_edge=RIGHT)
            r = Rectangle(width=abs(v) * .4, height=.75, stroke_width=0, fill_color=c, fill_opacity=1).move_to(LEFT * 2.2 + UP * y, aligned_edge=LEFT)
            g.add(VGroup(lab, r, kr(f"{v:+.1f}%".replace("-", "−"), 38, c).next_to(r, RIGHT, .3)))
        for row in g:
            self.play(FadeIn(row[0]), GrowFromEdge(row[1], LEFT), FadeIn(row[2]), run_time=.55)
        n = card(kr("외국인 10월 매도 17.8조 중 14조 = 삼성전자 + SK하이닉스", 30, YEL), color=YEL).to_edge(DOWN, buff=.55)
        self.play(FadeIn(n, shift=UP * .2)); self.wait(3)
