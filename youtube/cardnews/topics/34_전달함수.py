from cards import *

blk = svg(t(110, 222, "X(s)", "lbY") + arrow(170, 210, 320, 210, W) + box(330, 140, 240, 140, "H(s)") + arrow(580, 210, 730, 210, W) + t(790, 222, "Y(s)", "lbY") +
          t(450, 340, "입력 → 회로 → 출력", "lbS"), 400)

ck = svg(term(170, 80) + term(170, 340) + res(170, 80, 470, 80) + cap(470, 80, 470, 340) + wire((170, 340), (700, 340)) + wire((470, 80), (700, 80)) +
         term(700, 80) + term(700, 340) + dot(470, 80) + dot(470, 340) + t(150, 222, "X", "lb", "end") + t(720, 222, "Y", "lbY", "start") +
         t(320, 45, "R") + t(520, 222, "1/sC", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"'), 400)

X0, Y0 = 560, 210
def splane(stable=False):
    s = ""
    if stable:
        s += f'<rect x="80" y="30" width="{X0-80}" height="360" fill="rgba(79,209,139,.10)"/>' + t(300, 380, "안정 (왼쪽)", "lbC").replace('class="lbC"', f'class="lbC" fill="{GRN}"')
        s += t(X0 + 160, 380, "불안정", "lbC").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    s += axes(X0, Y0, 480, 300, 180, 180, "σ (실수)", "jω")
    for p in (-2, -3):
        x = X0 + p * 110
        s += f'<path d="M{x-14},{Y0-14} L{x+14},{Y0+14} M{x-14},{Y0+14} L{x+14},{Y0-14}" stroke="{YEL}" stroke-width="6"/>' + t(x, Y0 + 52, str(p).replace("-", "−"), "lbS")
    x = X0 - 110
    s += f'<circle cx="{x}" cy="{Y0}" r="14" fill="none" stroke="{BLUE}" stroke-width="6"/>' + t(x, Y0 + 52, "−1", "lbS")
    if not stable:
        s += t(X0 - 450, 80, "✕ 극", "lbY", "start") + t(X0 - 450, 130, "○ 영점", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    return svg(s, 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="회로 전체를", line2="분수 하나로 요약", sub="전달함수 H(s), 극과 영점까지", visual=blk,
               chips=["정의", "구하는 법", "극·영점", "안정성"]),
    cards=[
        dict(title="정의", sub="출력을 입력으로 나눈 것 (s 영역)", visual=blk,
             formula=f"H(s) = {F('Y(s)', 'X(s)')}",
             ex=f"초기값은 {Y('전부 0')}으로 두고 구해요",
             trap="<b>기억</b> 임펄스 응답을 라플라스 변환하면 H(s)"),
        dict(title="구하는 법", sub="부품을 s 임피던스로 바꾸고 전압 분배", visual=ck,
             formula=f"H(s) = {F('1/sC', 'R + 1/sC')} = {F('1', '1 + sRC')}",
             ex=f"s = jω 를 넣으면 {Y('주파수 응답')}",
             trap="<b>팁</b> 분모·분자에 s를 곱해서 번분수를 정리하기"),
        dict(title="극·영점", sub="분자 = 0 이면 영점, 분모 = 0 이면 극", visual=splane(),
             formula=f"H(s) = {F('s + 1', '(s + 2)(s + 3)')}",
             ex=f"영점 {B('−1')}, 극 {Y('−2, −3')}",
             trap="<b>함정</b> s + 2 의 극은 +2가 아니라 −2"),
        dict(title="안정성", sub="극의 위치가 응답 모양을 정해요", visual=splane(True),
             formula="극이 전부 왼쪽 → 안정",
             ex=f"극 −2 → e<sup>−2t</sup> {Y('사라짐')}, 극 +2 → e<sup>2t</sup> 폭주",
             trap="<b>함정</b> 허수축 위의 극은 계속 진동 (안정 아님)"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('H(s) = Y(s) / X(s)')}, 초기값 0",
        f"RC 저역 → {Y('1 / (1 + sRC)')}",
        f"분자 0 {B('영점')}, 분모 0 {Y('극')}",
        f"극 전부 {Y('왼쪽')} → 안정"]),
)

CAPTION = """전기전자 주목⚡ 회로 전체를 분수 하나로 요약하는 법
전달함수 H(s) = 출력 ÷ 입력. 분모의 근(극)만 보면 안정한지도 알 수 있어요.
RC 회로로 구하는 법이랑 극·영점 읽는 법까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #전달함수 #신호및시스템 #전기전자 #공대생"""
