from cards import *

X0, Y0, S = 250, 330, 85
def pic(step=3):
    s = grid(X0, Y0, S, 2, 3) + axes(X0, Y0, 180, 560, 300, 60)
    s += f'<line x1="{X0-2*S}" y1="{Y0+S}" x2="{X0+6.2*S}" y2="{Y0-3.1*S}" stroke="#2f3746" stroke-width="3"/>'
    s += vec(X0, Y0, S, 1, 3, BLUE, "b = (1, 3)", -210, -10, 7)
    if step >= 1:
        s += vec(X0, Y0, S, 2, 1, YEL, "", w=9) + t(X0 + 2 * S + 20, Y0 - S + 44, "p = (2, 1)", "lbY", "start")
    if step >= 2:
        s += f'<line x1="{X0+S}" y1="{Y0-3*S}" x2="{X0+2*S}" y2="{Y0-S}" stroke="#ff6b61" stroke-width="5" stroke-dasharray="10 8"/>'
        s += t(X0 + 1.6 * S + 20, Y0 - 2 * S, "e = (−1, 2)", "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
        u = (2 / 5 ** .5, 1 / 5 ** .5); v = (-1 / 5 ** .5, 2 / 5 ** .5); k = 20
        x, y = X0 + 2 * S, Y0 - S
        s += f'<path d="M{x-u[0]*k:.1f},{y+u[1]*k:.1f} l{v[0]*k:.1f},{-v[1]*k:.1f} l{u[0]*k:.1f},{-u[1]*k:.1f}" fill="none" stroke="{W}" stroke-width="3"/>'
    s += t(X0 + 5.6 * S, Y0 - 2.8 * S - 16, "a 방향", "lbS")
    return svg(s, 420)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="벡터의 그림자", line2="정확히 구하기", sub="투영, 최소제곱법의 출발점", visual=pic(2),
               chips=["그림자", "공식", "오차는 수직", "투영 행렬"]),
    cards=[
        dict(title="그림자", sub="b에서 a 방향 직선에 수직으로 내린 발", visual=pic(1),
             formula="p = (숫자) × a",
             ex=f"그림자는 항상 {Y('a와 같은 직선')} 위에 있어요",
             trap="<b>기억</b> a·b가 음수면 그림자는 a 반대 방향"),
        dict(title="공식", sub="a = (2, 1), b = (1, 3)", visual=pic(1),
             formula=f"p = {F('a · b', 'a · a')} a",
             ex=f"{F('5', '5')} × (2, 1) = {Y('(2, 1)')}",
             trap="<b>함정</b> 분모는 a·a (a 길이의 제곱). b 길이가 아니에요"),
        dict(title="오차는 수직", sub="b − p 는 a와 직각", visual=pic(2),
             formula="e = b − p &nbsp;⊥&nbsp; a",
             ex=f"(−1, 2) · (2, 1) = {Y('0')} ✓ &nbsp;→ 가장 가까운 점",
             trap="<b>기억</b> 이 직각 조건이 최소제곱법 정규방정식이 돼요"),
        dict(title="투영 행렬", sub="어떤 b든 곱하면 그림자가 나오는 행렬", visual=f"P = {F('1', '5')}" + M([[4, 2], [2, 1]], YEL),
             formula=f"P = {F('a aᵀ', 'aᵀ a')}",
             ex=f"P (1, 3) = {F('1', '5')}(10, 5) = {Y('(2, 1)')} ✓",
             trap="<b>기억</b> P² = P (그림자의 그림자는 그대로)"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('p = (a·b / a·a) a')}",
        f"오차 {Y('e = b − p')} 는 a와 수직",
        f"{Y('P = aaᵀ / aᵀa')}",
        f"{Y('P² = P')}"]),
)

CAPTION = """공대생 주목🧮 벡터의 그림자, 정확히 구하는 법
투영 p = (a·b / a·a) a. 남은 오차 b − p 는 항상 a와 수직이에요.
숫자 예제랑 투영 행렬, 최소제곱법과 이어지는 부분까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #투영 #최소제곱법 #공대생 #공대수학"""
