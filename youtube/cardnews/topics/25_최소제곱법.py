from cards import *

X0, Y0, S = 200, 340, 110
pts = [(0, 1), (1, 2), (2, 2), (3, 3.2)]
def fit(err=False):
    s = grid(X0, Y0, S, 1, 0) + axes(X0, Y0, 40, 560, 300, 20, "x", "y")
    c, m = 7 / 6, 0.5
    s += curve(lambda x: c + m * x, -0.3, 4.3, X0, Y0, S, S * 0.8, BLUE, 5)
    for x, y in pts[:3]:
        if err:
            s += f'<line x1="{X0+x*S}" y1="{Y0-y*S*0.8}" x2="{X0+x*S}" y2="{Y0-(c+m*x)*S*0.8:.0f}" stroke="#ff6b61" stroke-width="4"/>'
        s += dot(X0 + x * S, Y0 - y * S * 0.8, YEL) + f'<circle cx="{X0+x*S}" cy="{Y0-y*S*0.8}" r="11" fill="{YEL}"/>'
    return svg(s + t(X0 + 470, Y0 - (c + m * 4.3) * S * 0.8 - 10, "y = 1.17 + 0.5x", "lbB"), 400)

def proj():
    o = (300, 300)
    s = f'<polygon points="80,340 560,340 820,200 340,200" fill="{BLUE}" fill-opacity=".14" stroke="{BLUE}" stroke-width="3"/>' + t(160, 385, "A의 열공간", "lbB").replace('text-anchor="middle"', 'text-anchor="start"')
    s += arrow(o[0], o[1], 600, 80, YEL, 7) + t(615, 70, "b", "lbY") + arrow(o[0], o[1], 600, 270, GRN, 7) + t(620, 290, "Ax̂", "lbC").replace('class="lbC"', f'class="lbC" fill="{GRN}"')
    s += f'<line x1="600" y1="270" x2="600" y2="90" stroke="#ff6b61" stroke-width="5" stroke-dasharray="10 8"/>' + t(620, 185, "e = b − Ax̂", "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    s += f'<path d="M580,270 L580,250 L600,250" fill="none" stroke="#ff6b61" stroke-width="3"/>'
    return svg(s, 420)

A = M([[1, 0], [1, 1], [1, 2]]) + M([["c"], ["m"]], BLUE) + "≈" + M([[1], [2], [2]], YEL)
SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="점들을 꿰뚫는", line2="가장 그럴듯한 직선", sub="최소제곱법, 해가 없을 때 '가장 가까운' 답", visual=fit(True),
               chips=["문제 상황", "정규방정식", "숫자 예제", "그림의 뜻"]),
    cards=[
        dict(title="문제 상황", sub="점 3개를 지나는 직선은 보통 없어요", visual=A,
             formula="Ax = b 의 해가 없음",
             ex=f"그래서 오차 ‖b − Ax‖ 가 {Y('가장 작은 x̂')} 을 찾아요",
             trap="<b>기억</b> 식이 미지수보다 많으면(세로로 긴 A) 거의 항상 이래요"),
        dict(title="정규방정식", sub="양변에 Aᵀ만 곱하면 풀리는 식이 돼요", visual=M([["AᵀA"]], BLUE) + M([["x̂"]], YEL) + "=" + M([["Aᵀb"]]),
             formula="AᵀA x̂ = Aᵀb",
             ex=f"AᵀA는 {Y('정사각')}이라 보통 역행렬이 있어요",
             trap="<b>함정</b> Ax = b 에서 A⁻¹을 바로 쓰면 안 돼요 (정사각 아님)"),
        dict(title="숫자 예제", sub="점 (0,1), (1,2), (2,2)에 y = c + mx 맞추기", visual=fit(True),
             formula=f"{M([[3, 3], [3, 5]])} {M([['c'], ['m']])} = {M([[5], [6]])}",
             ex=f"→ m = 0.5, c = 7/6 &nbsp;→&nbsp; {Y('y ≈ 1.17 + 0.5x')}",
             trap="<b>기억</b> 빨간 세로 오차들의 제곱합이 최소"),
        dict(title="그림의 뜻", sub="b를 A의 열공간에 수직으로 내린 그림자", visual=proj(),
             formula="오차 e ⊥ 열공간 &nbsp;⇔&nbsp; Aᵀe = 0",
             ex=f"Aᵀ(b − Ax̂) = 0 을 정리한 게 {Y('정규방정식')}",
             trap="<b>팁</b> 열이 정규직교(Q)면 x̂ = Qᵀb 로 끝"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('해가 없으면')} 가장 가까운 x̂",
        f"{Y('AᵀAx̂ = Aᵀb')}",
        f"{Y('오차')} 제곱합 최소",
        f"{Y('그림')} 열공간 위 수직 투영"]),
)

CAPTION = """공대생 주목🧮 점들을 꿰뚫는 가장 그럴듯한 직선
해가 없을 때는 '가장 가까운 답'을 찾아요. 그게 최소제곱법.
정규방정식 AᵀAx̂ = Aᵀb 하나로 숫자 예제까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #최소제곱법 #회귀분석 #공대생 #공대수학"""
