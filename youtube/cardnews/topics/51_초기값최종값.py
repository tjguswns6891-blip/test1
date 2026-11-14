from cards import *

X0, Y0 = 110, 340
def g(osc=False):
    s = axes(X0, Y0 - (130 if osc else 0), 20, 720, 300 if not osc else 170, 20 if not osc else 150, "t", "")
    if osc:
        s += curve(lambda x: 0.5 * math.sin(2 * x), 0, 9, X0, Y0 - 130, 75, 230, YEL, 6) + t(X0 + 700, 50, "끝이 없음", "lbC", "end").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    else:
        s += f'<line x1="{X0}" y1="{Y0-260}" x2="{X0+700}" y2="{Y0-260}" stroke="{DIM}" stroke-width="3" stroke-dasharray="8 8"/>'
        s += curve(lambda x: 2 * (1 - math.exp(-5 * x)), 0, 1.6, X0, Y0, 430, 130, YEL, 7)
        s += dot(X0, Y0, BLUE) + t(X0 + 20, Y0 - 20, "f(0⁺) = 0", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
        s += t(X0 + 690, Y0 - 280, "f(∞) = 2", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{GRN}"')
    return svg(s, 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="역변환 안 하고", line2="처음과 끝 알기", sub="초기값·최종값 정리, s 하나만 곱하면 돼요", visual=g(),
               chips=["초기값", "최종값", "검산", "조건"]),
    cards=[
        dict(title="초기값", sub="s를 크게 보내면 t = 0⁺", visual=g(),
             formula="f(0⁺) = lim<sub>s→∞</sub> sF(s)",
             ex=f"예) F = 10 / s(s + 5) &nbsp;→ {F('10', 's + 5')} → {Y('0')}",
             trap="<b>기억</b> s → ∞ 가 t → 0 (서로 반대)"),
        dict(title="최종값", sub="s를 0으로 보내면 t = ∞", visual=g(),
             formula="f(∞) = lim<sub>s→0</sub> sF(s)",
             ex=f"같은 F &nbsp;→ 10 / 5 = {Y('2')}",
             trap="<b>기억</b> s → 0 이 t → ∞"),
        dict(title="검산", sub="실제로 역변환해 보면", visual=g(),
             formula="f(t) = 2(1 − e<sup>−5t</sup>)",
             ex=f"0에서 시작해서 {Y('2')}로 ✓",
             trap="<b>팁</b> 회로 직관이랑 같아요. C가 0V에서 충전돼 최종값으로"),
        dict(title="조건", sub="최종값 정리는 아무 때나 못 써요", visual=g(True),
             formula="sF(s)의 극이 전부 왼쪽일 때만",
             ex=f"예) 1 / (s² + 4) → sin 진동, {Y('최종값 없음')}",
             trap="<b>함정</b> 조건 무시하고 s = 0 넣으면 엉뚱한 0이 나와요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('f(0⁺) = lim s→∞ sF(s)')}",
        f"{Y('f(∞) = lim s→0 sF(s)')}",
        f"역변환 결과 {Y('검산')}에 딱",
        f"최종값은 극이 {Y('전부 왼쪽')}일 때만"]),
)

CAPTION = """전기전자 주목⚡ 역변환 안 하고 처음과 끝을 아는 법
초기값은 s → ∞, 최종값은 s → 0. sF(s)에 넣기만 하면 돼요.
예제랑 최종값 정리를 쓰면 안 되는 경우까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #라플라스변환 #최종값정리 #전기전자 #공대생"""
