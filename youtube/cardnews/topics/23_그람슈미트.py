from cards import *

X0, Y0, S = 330, 250, 100
def pic(step):
    s = grid(X0, Y0, S, 3, 2) + axes(X0, Y0, 250, 330, 200, 150)
    s += vec(X0, Y0, S, 2, 0, DIM if step >= 2 else GRN, "v₂ = (2, 0)", -40, 44, 6)
    s += vec(X0, Y0, S, 1, 1, YEL, "u₁ = v₁ = (1, 1)", -200, -20, 7)
    if step >= 2:
        s += f'<line x1="{X0+2*S}" y1="{Y0}" x2="{X0+S}" y2="{Y0-S}" stroke="{BLUE}" stroke-width="4" stroke-dasharray="10 8"/>'
        s += vec(X0, Y0, S, 1, 1, BLUE, "", w=4) + t(X0 + 175, Y0 - 62, "그림자", "lbB").replace('text-anchor="middle"', 'text-anchor="start"')
        s += vec(X0, Y0, S, 1, -1, GRN, "u₂ = (1, −1)", 16, 40, 7)
    return svg(s, 420)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="삐뚤어진 기저를", line2="직각으로 펴는 법", sub="그람-슈미트, 그림자 빼기 한 번", visual=pic(2),
               chips=["목표", "그림자 빼기", "정규화", "QR 분해"]),
    cards=[
        dict(title="목표", sub="아무 기저 → 서로 수직인 기저(직교 기저)", visual=pic(1),
             formula="v₁, v₂ → u₁ ⊥ u₂",
             ex=f"수직이면 좌표 구하기가 {Y('내적 한 번')}으로 끝나요",
             trap="<b>기억</b> 만들어진 공간(span)은 그대로, 방향만 정리"),
        dict(title="그림자 빼기", sub="v₂에서 u₁ 방향 성분(투영)을 빼요", visual=pic(2),
             formula=f"u₂ = v₂ − {F('v₂ · u₁', 'u₁ · u₁')} u₁",
             ex=f"(2, 0) − {F('2', '2')}(1, 1) = {Y('(1, −1)')} &nbsp;→ u₁·u₂ = 0 ✓",
             trap="<b>함정</b> 분모는 u₁·u₁ (길이의 제곱). 길이 아님!"),
        dict(title="정규화", sub="길이로 나눠서 길이 1로 맞추기", visual=pic(2),
             formula=f"e = {F('u', '‖u‖')}",
             ex=f"e₁ = {F('(1, 1)', '√2')}, &nbsp;e₂ = {F('(1, −1)', '√2')} &nbsp;→ {Y('정규직교 기저')}",
             trap="<b>팁</b> 3개 이상이면 앞에서 만든 u 전부의 그림자를 빼요"),
        dict(title="QR 분해", sub="그람-슈미트 결과를 행렬로 쓰면", visual="A = " + M([["Q"]], GRN) + M([["R"]], YEL),
             formula="A = Q R",
             ex=f"Q = 정규직교 열, R = {Y('위삼각행렬')}",
             trap="<b>기억</b> QᵀQ = I 라서 최소제곱 계산이 쉬워져요"),
    ],
    summary=dict(tag="순서대로", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('①')} u₁ = v₁",
        f"{Y('②')} u₂ = v₂ − (u₁ 위 그림자)",
        f"{Y('③')} 다음 벡터도 앞 u들 그림자 빼기",
        f"{Y('④')} 길이로 나누기 → A = QR"]),
)

CAPTION = """공대생 주목🧮 삐뚤어진 기저를 직각으로 펴는 법
그람-슈미트: 앞 벡터 방향의 '그림자(투영)'를 빼면 수직인 벡터가 남아요.
숫자 예제랑 정규화, QR 분해까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #그람슈미트 #직교 #공대생 #공대수학"""
