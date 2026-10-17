# 증시 롱폼(2026-10-15) 모션그래픽. 16:9, 핵심 내용은 가운데(가로 ±5.1)에 두어 세로 쇼츠에서도 잘라 쓴다.
# 렌더: ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py <Scene>   (1920×1080)
from manim import *
import numpy as np, json, os

BG, INK, MUTE, YEL = "#111318", "#eef0f3", "#8d94a1", "#ffc53d"
BLU, RED, GRN, ORG, PUR = "#6ea8ff", "#ff5d73", "#3ddc97", "#ff9f43", "#c792ff"
KR = "Noto Sans CJK KR"
config.background_color = BG
D = json.load(open(os.path.join(os.path.dirname(__file__), "../../raw/stock1015/invest/data.json")))
T = json.load(open(os.path.join(os.path.dirname(__file__), "../../raw/stock1015/themes/data.json")))
_K = os.path.join(os.path.dirname(__file__), "../../raw/stock1015/kospi_today.json")   # 마감 후 채움: {"close":…, "pct":…, "flows":{…}}
KT = json.load(open(_K)) if os.path.exists(_K) else None
KOSPI = D["daily"]["kospi"] + [["2026-10-14", 6008.81]] + ([["2026-10-15", KT["close"]]] if KT else [])
SPY = D["daily"]["spx"]


def kr(s, size=40, color=INK, weight=BOLD):
    return Text(s, font=KR, font_size=size, color=color, weight=weight)


def card(m, color="#2a2e37", buff=.3):
    return VGroup(SurroundingRectangle(m, color=color, fill_color="#181b21", fill_opacity=.96, buff=buff, corner_radius=.18), m)


def head(s, c=INK):
    return kr(s, 46, c).to_edge(UP, buff=.45)


class CpiShock(Scene):
    """미국 소비자물가(전년 대비) 올해 흐름 + 9월 3.7% vs 예상 3.6%."""
    def construct(self):
        c = [x for x in D["cpi"] if x[0] >= "2025-09-15"]
        h = head("미국 소비자물가 · 9월 3.7%")
        ax = Axes(x_range=[0, len(c) - 1, 1], y_range=[2, 4.5, .5], x_length=10.5, y_length=5,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .5)
        self.play(FadeIn(h), Create(ax), run_time=.7)
        exp = DashedLine(ax.c2p(0, 3.6), ax.c2p(len(c) - 1, 3.6), color=MUTE, stroke_width=3)
        el = kr("예상 3.6%", 28, MUTE).next_to(exp.get_start(), UP, .12).shift(RIGHT * .8)
        line = ax.plot_line_graph(list(range(len(c))), [x[1] for x in c], line_color=ORG, add_vertex_dots=False, stroke_width=7)
        self.play(Create(line), run_time=2.0, rate_func=linear)
        self.play(Create(exp), FadeIn(el), run_time=.6)
        end = ax.c2p(len(c) - 1, c[-1][1]); dot = Dot(end, radius=.13, color=RED)
        lab = kr("9월 3.7%", 40, RED).next_to(dot, UP, .2).shift(LEFT * .6)
        mids = [(i, x) for i, x in enumerate(c) if x[0] in ("2025-09-15", "2026-03-15", "2026-06-15")]
        ticks = VGroup(*[kr(x[0][2:7].replace("-", "."), 24, MUTE).next_to(ax.c2p(i, 2), DOWN, .2) for i, x in mids])
        self.play(FadeIn(dot, scale=2), FadeIn(lab, shift=UP * .2), FadeIn(ticks), Flash(end, color=RED), run_time=.8)
        g = card(VGroup(kr("휘발유", 30, MUTE), kr("한 달 +9.1%", 40, YEL)).arrange(DOWN, buff=.15), color=YEL).scale(.9).to_corner(UL, buff=.5).shift(DOWN * 1.1 + RIGHT * .8)
        self.play(FadeIn(g, shift=RIGHT * .2)); self.wait(3)


class HikeOdds(Scene):
    """10월 연준 금리 인상 확률: CPI 전 약 20% → 후 30~40%대 (보도마다 32.7~43.7%)."""
    def construct(self):
        h = head("10월 금리 인상 확률")
        self.play(FadeIn(h))
        def bar(v, c, lab):
            r = Rectangle(width=2.2, height=v * .1, stroke_width=0, fill_color=c, fill_opacity=1)
            return VGroup(r, kr(lab, 36, c))
        base = Line(LEFT * 4, RIGHT * 4, color=MUTE, stroke_width=3).shift(DOWN * 2.3)
        b1 = bar(20, MUTE, "약 20%"); b2 = bar(38, RED, "30~40%대")
        for b, x in ((b1, -1.8), (b2, 1.8)):
            b[0].move_to(base.get_center() + RIGHT * x, aligned_edge=DOWN); b[1].next_to(b[0], UP, .2)
        n1 = kr("물가 발표 전", 32, MUTE).next_to(base, DOWN, .3).shift(LEFT * 1.8)
        n2 = kr("발표 후", 32, INK).next_to(base, DOWN, .3).shift(RIGHT * 1.8)
        self.play(Create(base), FadeIn(n1), FadeIn(n2), run_time=.5)
        self.play(GrowFromEdge(b1[0], DOWN), FadeIn(b1[1]), run_time=.7)
        self.play(GrowFromEdge(b2[0], DOWN), FadeIn(b2[1]), run_time=.9)
        a = Arrow(b1[1].get_right(), b2[1].get_left(), color=YEL, stroke_width=6, buff=.2)
        self.play(GrowArrow(a))
        note = kr("현재 기준금리 3.75~4.00% (9월 인상) · 다음 회의 10/27~28", 28, MUTE).to_edge(DOWN, buff=.35)
        self.play(FadeIn(note)); self.wait(3)


class UsDrop(Scene):
    """10/14 미국장: 나스닥 −1.9% · S&P 500 −1.1% · 다우 −0.1%, 필라델피아 반도체지수 −4.3%."""
    def construct(self):
        h = head("10월 14일 미국장 · 물가 쇼크")
        self.play(FadeIn(h))
        rows = [("나스닥", -1.9, RED), ("S&P 500", -1.1, ORG), ("다우", -0.1, MUTE)]
        g = VGroup()
        for i, (n, v, c) in enumerate(rows):
            y = 1.2 - i * 1.25
            lab = kr(n, 38).move_to(LEFT * 3.0 + UP * y, aligned_edge=RIGHT)
            r = Rectangle(width=abs(v) * 3.2, height=.75, stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to(LEFT * 2.6 + UP * y, aligned_edge=LEFT)
            g.add(VGroup(lab, r, kr(f"{v:+.1f}%", 38, c).next_to(r, RIGHT, .3)))
        for row in g:
            self.play(FadeIn(row[0]), GrowFromEdge(row[1], LEFT), FadeIn(row[2]), run_time=.55)
        tag = card(kr("필라델피아 반도체지수 −4.3%", 38, YEL), color=YEL).to_edge(DOWN, buff=.6)
        self.play(FadeIn(tag, shift=UP * .2)); self.wait(3)


class ThemeDay(Scene):
    """미국 27개 테마 · 10/14 하루 수익률: 26개 하락, 농산물만 +."""
    def construct(self):
        rows = sorted([(100 * x["path"]["d1"][-1], x["name"]) for x in T["themes"]], reverse=True)
        h = head("미국 27개 테마 · 10월 14일 하루")
        self.play(FadeIn(h))
        n = len(rows); w = 11.5 / n; sc = 3.0 / 11
        base = Line(LEFT * 6, RIGHT * 6, color=MUTE, stroke_width=3).shift(UP * 1.4)
        self.play(Create(base), run_time=.4)
        bars = VGroup()
        for i, (v, name) in enumerate(rows):
            c = GRN if v > 0 else (RED if v <= -7 else "#3a3f4b")
            r = Rectangle(width=w * .75, height=max(abs(v) * sc, .04), stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to(base.get_left() + RIGHT * (w * (i + .5) + .25), aligned_edge=UP if v < 0 else DOWN)
            if v > 0: r.align_to(base, DOWN)
            else: r.align_to(base, UP)
            bars.add(r)
        self.play(LaggedStart(*[GrowFromEdge(b, UP if rows[i][0] < 0 else DOWN) for i, b in enumerate(bars)], lag_ratio=.04), run_time=1.8)
        up = kr(f"{rows[0][1]} +{rows[0][0]:.1f}%", 30, GRN).next_to(bars[0], UP, .2).shift(RIGHT * .6)
        worst = VGroup(*[kr(f"{nm.replace(',', '·')} {v:.1f}%", 28, RED) for v, nm in rows[-4:][::-1]]).arrange(DOWN, aligned_edge=RIGHT, buff=.12).next_to(bars[-6], LEFT, .35).align_to(bars[-1], DOWN)
        self.play(FadeIn(up), FadeIn(worst, shift=LEFT * .2), run_time=.8)
        big = kr("27개 중 26개 하락", 46, YEL).to_edge(DOWN, buff=.5)
        self.play(Write(big), run_time=.8); self.wait(3)


class Next(Scene):
    """다음 체크포인트: 내일 연준 의장 발언 · 10/27~28 연준 회의 · 유가."""
    def construct(self):
        h = head("다음 체크포인트")
        self.play(FadeIn(h))
        days = [("내일 (금)", "연준 의장 발언", "추가 인상 힌트?", YEL), ("10월 27~28일", "연준 회의", "인상 확률 30~40%대", RED), ("계속", "유가 $96", "물가를 올린 범인", ORG)]
        cs = VGroup(*[card(VGroup(kr(d, 30, c), kr(t, 42), kr(s2, 30, c)).arrange(DOWN, buff=.25), color=c) for d, t, s2, c in days])
        cs.arrange(RIGHT, buff=.35).scale_to_fit_width(12.5).shift(DOWN * .2)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cs], lag_ratio=.4), run_time=1.6)
        for c, col in zip(cs, (YEL, RED, ORG)):
            self.play(Indicate(c, color=col, scale_factor=1.05), run_time=.6)
        self.wait(2.5)


class Signals(Scene):
    """내 사이트 '오늘의 신호' (10/13 데이터): S&P 500 분할 매수 · 10년 국채 일부 매수 · SCHD 보유 · QQQ 추가 매수 보류."""
    def construct(self):
        h = head("내 사이트 · 오늘의 신호")
        sub = kr("10월 14일 데이터 · 매일 자동 계산", 28, MUTE).next_to(h, DOWN, .25)
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
        q = kr("“주가는 고점 근처, 금리·물가·유가는 경고등”", 32, MUTE).to_edge(DOWN, buff=.9)
        self.play(FadeIn(q, shift=UP * .2)); self.wait(3)


class ChipDrop(Scene):
    """10/14 반도체·AI 종목: 코어위브 −16% · AMD −5.7% · 마이크론 −4.1% · TSMC(미국) −3.4% · 엔비디아 −3.2%."""
    def construct(self):
        h = head("반도체·AI 종목 · 10월 14일")
        self.play(FadeIn(h))
        rows = [("코어위브", -16.0, RED, "빚 부담 우려"), ("AMD", -5.7, RED, ""), ("마이크론", -4.1, ORG, ""), ("TSMC (미국)", -3.4, ORG, ""), ("엔비디아", -3.2, ORG, "")]
        g = VGroup()
        for i, (n, v, c, note) in enumerate(rows):
            y = 1.9 - i * 1.0
            lab = kr(n, 36).move_to(LEFT * 3.3 + UP * y, aligned_edge=RIGHT)
            r = Rectangle(width=abs(v) * .36, height=.62, stroke_width=0, fill_color=c, fill_opacity=1).move_to(LEFT * 2.9 + UP * y, aligned_edge=LEFT)
            val = kr(f"{v:+.1f}%", 34, c).next_to(r, RIGHT, .25)
            row = VGroup(lab, r, val)
            if note: row.add(kr(note, 26, MUTE).next_to(val, RIGHT, .3))
            g.add(row)
        for row in g:
            self.play(FadeIn(row[0]), GrowFromEdge(row[1], LEFT), *[FadeIn(x) for x in row[2:]], run_time=.5)
        foot = kr("금리 ↑ → 돈 빌려 짓는 AI 데이터센터 비용 ↑", 32, YEL).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot, shift=UP * .2)); self.wait(3)


class KospiPath(Scene):
    """코스피 1년: 꼭대기 9114(6/22) → 10/2 7003 → 오늘 오전 5620. 10/2 대비 −20%, 고점 대비 −38%."""
    def construct(self):
        v = [x[1] for x in KOSPI]; n = len(v)
        ax = Axes(x_range=[0, n - 1, 50], y_range=[2500, 10000, 1000], x_length=10, y_length=5.6,
                  axis_config={"stroke_color": MUTE, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .35)
        h = head("코스피 1년")
        self.play(FadeIn(h), Create(ax), run_time=.7)
        line = ax.plot_line_graph(list(range(n)), v, line_color=ORG, add_vertex_dots=False, stroke_width=6)
        self.play(Create(line), run_time=2.4, rate_func=linear)
        ip = int(np.argmax(v))
        pts = [(0, v[0], "1년 전 3,260", MUTE, UP), (ip, v[ip], "꼭대기 9,114 (6/22)", YEL, UP), (n - 1, v[-1], KT["label"], RED, DOWN)]
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


class Flows(Scene):
    """오늘(10/15) 오전 코스피 수급 (장중): 외국인 −9432억, 개인 +113억, 기관 +9075억."""
    def construct(self):
        h = head("10월 15일 오전 코스피 · 누가 팔았나")
        self.play(FadeIn(h))
        data = [("외국인", KT["flows"]["외국인"], RED), ("개인", KT["flows"]["개인"], ORG), ("기관", KT["flows"]["기관"], GRN)]
        base = Line(LEFT * .0 + DOWN * 2.3, UP * 2.3, color=MUTE, stroke_width=3)
        rows = VGroup()
        for i, (nm, val, c) in enumerate(data):
            y = 1.3 - i * 1.5; w = max(abs(val) / 9432 * 3.6, .06)
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
        note = kr("외국인 8거래일 연속 순매도 · 매도 사이드카 (09:07)", 34, YEL).to_edge(DOWN, buff=.5)
        self.play(FadeIn(note)); self.wait(2.5)




class Samsung(Scene):
    """삼성전자 3분기 영업이익 107.4조(사상 최대, +782%) vs 오늘 주가 −7%."""
    def construct(self):
        h = head("삼성전자 · 실적과 주가가 반대로")
        self.play(FadeIn(h))
        L = card(VGroup(kr("3분기 영업이익", 32, MUTE), kr("107.4조 원", 64, GRN), kr("사상 최대 · 1년 전보다 +782%", 28, GRN)).arrange(DOWN, buff=.25), color=GRN)
        R = card(VGroup(kr("오늘 오전 주가", 32, MUTE), kr(f"{KT['samsung']:.1f}%".replace("-", "−"), 64, RED), kr(f"SK하이닉스 {KT['hynix']:.1f}%".replace("-", "−"), 28, RED)).arrange(DOWN, buff=.25), color=RED)
        VGroup(L, R).arrange(RIGHT, buff=2.2).shift(UP * .2)
        L.shift(LEFT * .3); R.shift(RIGHT * .3)
        vs = kr("그런데", 40, YEL).move_to((L.get_right() + R.get_left()) / 2)
        self.play(FadeIn(L, shift=RIGHT * .3), run_time=.7); self.play(FadeIn(vs), run_time=.4); self.play(FadeIn(R, shift=LEFT * .3), run_time=.7)
        why = VGroup(*[kr(t, 30, INK) for t in ("① 중국 D램(CXMT) 추격", "② 자사주 매입 종료", "③ AI 투자 수익 의심")]).arrange(RIGHT, buff=.6).to_edge(DOWN, buff=.6)
        self.play(LaggedStart(*[FadeIn(w, shift=UP * .2) for w in why], lag_ratio=.3), run_time=1.2)
        src = kr("기사들이 꼽은 이유 (세계일보 등)", 22, MUTE).next_to(why, UP, .2)
        self.play(FadeIn(src)); self.wait(2.5)


class TsmcPreview(Scene):
    """오늘 15:00 TSMC 실적: 3분기 매출 1.494조 대만달러(+51%, 분기 최대) · 이익 +60% 안팎 기대 · 다음 분기 전망."""
    def construct(self):
        h = head("오늘 오후 3시 · TSMC 실적")
        self.play(FadeIn(h))
        cs = VGroup(
            card(VGroup(kr("이미 나온 숫자", 28, MUTE), kr("3분기 매출 +51%", 42, GRN), kr("1조 4,942억 대만달러 · 분기 최대", 26, MUTE)).arrange(DOWN, buff=.22), color=GRN),
            card(VGroup(kr("오늘 볼 숫자 ①", 28, MUTE), kr("이익 +60% 안팎?", 42, YEL), kr("시장 기대", 26, MUTE)).arrange(DOWN, buff=.22), color=YEL),
            card(VGroup(kr("오늘 볼 숫자 ②", 28, MUTE), kr("다음 분기 전망", 42, BLU), kr("AI 주문이 이어지는지", 26, MUTE)).arrange(DOWN, buff=.22), color=BLU))
        cs.arrange(RIGHT, buff=.35).scale_to_fit_width(12.6).shift(DOWN * .1)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * .3) for c in cs], lag_ratio=.4), run_time=1.6)
        self.play(Indicate(cs[2], color=BLU, scale_factor=1.05)); self.wait(3)


class Summary(Scene):
    def construct(self):
        h = head("세 줄 요약", YEL)
        ls = [("1", "미국 물가 3.7% · 휘발유 +9% → 금리 인상 걱정", RED), ("2", "미국 반도체 −4.3% · 코스피 오전 −6.5% 사이드카", BLU), ("3", "다음: 오늘 TSMC · 내일 연준 의장 · 10월 말 회의", YEL)]
        g = VGroup()
        for n, t, c in ls:
            g.add(VGroup(VGroup(Circle(.36, color=c, fill_color=c, fill_opacity=1, stroke_width=0), kr(n, 34, BG)), kr(t, 38)).arrange(RIGHT, buff=.4))
        for r in g:
            r[0][1].move_to(r[0][0])
        g.arrange(DOWN, aligned_edge=LEFT, buff=.55).shift(DOWN * .1)
        self.play(FadeIn(h))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * .3) for r in g], lag_ratio=.5), run_time=2)
        foot = kr("금리·주가 50년 /invest   ·   테마 강도 /themes", 30, MUTE).to_edge(DOWN, buff=.45)
        self.play(FadeIn(foot)); self.wait(3)
