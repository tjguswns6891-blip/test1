from cards import *

X0, Y0 = 100, 300
def resp(parts=True):
    s = axes(X0, Y0, 20, 740, 260, 120, "t", "")
    if parts:
        s += curve(lambda x: 2 * math.exp(-x), 0, 5, X0, Y0, 140, 110, BLUE, 4, dash="10 8") + t(X0 + 70, Y0 - 230, "2e^(−t)", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
        s += curve(lambda x: -math.exp(-2 * x), 0, 5, X0, Y0, 140, 110, "#ff6b61", 4, dash="10 8") + t(X0 + 60, Y0 + 100, "−e^(−2t)", "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    s += curve(lambda x: 2 * math.exp(-x) - math.exp(-2 * x), 0, 5, X0, Y0, 140, 110, YEL, 7) + t(X0 + 330, Y0 - 120, "f(t) = 2e^(−t) − e^(−2t)", "lbY", "start")
    return svg(s, 420)

split = (f'<span>{F("s + 3", "(s + 1)(s + 2)")}</span><span>=</span><span class=yel>{F("A", "s + 1")}</span><span>+</span><span class=blue>{F("B", "s + 2")}</span>')
cover_up = (f'<span>A = </span><span>{F("s + 3", "<s style=opacity:.35>(s + 1)</s>(s + 2)")}</span><span class=yel>s = −1</span><span>→ {Y("2")}</span>')

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="라플라스 역변환,", line2="부분분수면 끝", sub="커버업 한 번에 계수 구하기", visual=resp(),
               chips=["왜 나누나", "커버업", "계산 예", "검산"]),
    cards=[
        dict(title="왜 나누나", sub="쪼개면 변환표 한 줄씩으로 돌아가요", visual=split,
             formula=f"{F('1', 's + a')} ↔ e<sup>−at</sup>",
             ex=f"분모 인수 하나 = {Y('지수 함수 하나')}",
             trap="<b>조건</b> 분자 차수 &lt; 분모 차수. 아니면 먼저 나눗셈"),
        dict(title="커버업", sub="그 인수를 손으로 가리고 근을 넣기", visual=cover_up,
             formula="A = (s + 1) F(s) |<sub>s = −1</sub>",
             ex=f"(−1 + 3) / (−1 + 2) = {Y('2')}",
             trap="<b>함정</b> s + 1 의 근은 −1. 부호 실수가 제일 많아요"),
        dict(title="계산 예", sub="B도 같은 방법, s = −2 넣기", visual=resp(),
             formula="A = 2, &nbsp;B = (−2 + 3)/(−2 + 1) = −1",
             ex=f"f(t) = {Y('2e<sup>−t</sup> − e<sup>−2t</sup>')}",
             trap="<b>기억</b> 극 하나마다 지수 하나씩 생겨요"),
        dict(title="검산", sub="t = 0 값을 두 가지로 비교", visual=resp(False),
             formula="f(0) = 2 − 1 = 1",
             ex=f"초기값 정리 lim sF(s) = {Y('1')} ✓",
             trap="<b>팁</b> 시험장에서 30초면 끝나는 검산"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"분모 인수마다 {Y('A/(s + a)')} 로 쪼개기",
        f"{Y('커버업')} 가리고 근 넣기",
        f"{Y('1/(s + a) ↔ e^(−at)')}",
        f"끝나면 {Y('f(0)')} 로 검산"]),
)

CAPTION = """전기전자 주목⚡ 라플라스 역변환, 부분분수면 끝
분모 인수 하나마다 지수 함수 하나. 계수는 커버업으로 한 번에 구해요.
(s+3)/((s+1)(s+2)) 예제랑 30초 검산법까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #라플라스변환 #부분분수 #전기전자 #공대생"""
