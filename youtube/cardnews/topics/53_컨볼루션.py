from cards import *

X0, Y0 = 100, 330
def imp():
    s = axes(X0, Y0, 20, 740, 290, 20, "t", "")
    s += f'<line x1="{X0+4}" y1="{Y0}" x2="{X0+4}" y2="{Y0-280}" stroke="{BLUE}" stroke-width="7" marker-end="url(#ab)"/>' + t(X0 + 24, Y0 - 250, "δ(t) 입력", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    s += curve(lambda x: math.exp(-x), 0, 5, X0, Y0, 140, 200, YEL, 7) + t(X0 + 220, Y0 - 110, "h(t) = e^(−t) 출력", "lbY", "start")
    return svg(s, 400)

def conv():
    s = axes(X0, Y0, 20, 740, 290, 20, "t", "")
    for k in range(6):
        s += curve(lambda x, k=k: (math.exp(-(x - k * 0.5)) * 0.3 if x >= k * 0.5 else 0), k * 0.5, 5, X0, Y0, 140, 200, DIM, 3)
    s += curve(lambda x: 1 - math.exp(-x), 0, 5, X0, Y0, 140, 200, YEL, 7) + t(X0 + 700, Y0 - 220, "조각 응답을 다 더하면", "lbY", "end")
    return svg(s, 400)

def step():
    s = axes(X0, Y0, 20, 740, 290, 20, "t", "")
    s += f'<path d="M{X0},{Y0-200} L{X0+700},{Y0-200}" stroke="{BLUE}" stroke-width="4" stroke-dasharray="10 8" fill="none"/>' + t(X0 + 700, Y0 - 220, "입력 1 (계단)", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    s += curve(lambda x: 1 - math.exp(-x), 0, 5, X0, Y0, 140, 200, YEL, 7) + t(X0 + 320, Y0 - 90, "y = 1 − e^(−t)", "lbY", "start")
    return svg(s, 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="망치질 한 번으로", line2="모든 입력의 답", sub="임펄스 응답과 컨볼루션", visual=imp(),
               chips=["임펄스 응답", "컨볼루션", "s 영역", "계산 예"]),
    cards=[
        dict(title="임펄스 응답", sub="아주 짧고 센 입력 δ(t)를 넣었을 때 출력", visual=imp(),
             formula="h(t) = L⁻¹{ H(s) }",
             ex=f"RC 저역 필터 (τ = 1) &nbsp;→ {Y('h(t) = e<sup>−t</sup>')}",
             trap="<b>기억</b> h(t) 하나에 회로 정보가 다 들어 있어요"),
        dict(title="컨볼루션", sub="입력을 잘게 쪼개 각 조각의 응답을 더하기", visual=conv(),
             formula="y(t) = ∫ x(τ) h(t − τ) dτ",
             ex=f"과거 입력일수록 {Y('많이 줄어든')} 응답이 남아요",
             trap="<b>함정</b> h를 뒤집고(t − τ) 밀면서 곱해요"),
        dict(title="s 영역", sub="시간에서 적분이 s에선 곱셈", visual=conv(),
             formula="y = x * h &nbsp;⇔&nbsp; Y(s) = X(s) H(s)",
             ex=f"그래서 {Y('라플라스')}로 푸는 게 훨씬 빨라요",
             trap="<b>함정</b> * 는 곱하기가 아니라 컨볼루션 기호"),
        dict(title="계산 예", sub="h = e<sup>−t</sup> 에 계단 입력 1/s", visual=step(),
             formula=f"Y = {F('1', 's(s + 1)')} = {F('1', 's')} − {F('1', 's + 1')}",
             ex=f"y(t) = {Y('1 − e<sup>−t</sup>')} &nbsp;(RC 충전 곡선)",
             trap="<b>검산</b> 최종값 lim sY = 1 ✓"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('h(t)')} = 임펄스를 넣은 출력",
        f"{Y('y = x * h')} (조각 응답의 합)",
        f"s 영역에선 {Y('Y = X·H')}",
        f"계단 입력 → {Y('1/s')} 곱하기"]),
)

CAPTION = """전기전자 주목⚡ 망치질 한 번으로 모든 입력의 답을 아는 법
임펄스 응답 h(t)만 알면, 어떤 입력이든 컨볼루션으로 출력이 나와요. s 영역에선 그냥 곱셈.
RC 회로 계단 응답 예제까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #컨볼루션 #신호및시스템 #전기전자 #공대생"""
