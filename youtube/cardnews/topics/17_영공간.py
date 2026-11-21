from cards import *

X0, Y0, S = 450, 210, 50
null_line = (grid(X0, Y0, S, 8, 4) + axes(X0, Y0, 400, 400, 200, 200) +
             f'<line x1="{X0-8*S}" y1="{Y0-4*S}" x2="{X0+8*S}" y2="{Y0+4*S}" stroke="#ff6b61" stroke-width="7"/>' +
             vec(X0, Y0, S, -2, 1, YEL, "(−2, 1)", -150, -14) + vec(X0, Y0, S, 4, -2, YEL, "(4, −2)", 10, 30))
nl = svg(null_line + t(X0 + 330, Y0 + 190, "N(A)", "lbC").replace('class="lbC"', 'class="lbC" fill="#ff6b61"'), 420)
sol = svg(null_line + f'<line x1="{X0-8*S}" y1="{Y0-6*S}" x2="{X0+8*S}" y2="{Y0+2*S}" stroke="{BLUE}" stroke-width="5" stroke-dasharray="12 8"/>' +
          dot(X0 + S, Y0 - 1.5 * S, BLUE) + t(X0 + S + 14, Y0 - 1.5 * S - 16, "특수해", "lbB").replace('text-anchor="middle"', 'text-anchor="start"'), 420)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="이 빨간 선 위 벡터는", line2="전부 0이 됩니다", sub="영공간, 행렬이 '지워 버리는' 방향", visual=nl,
               chips=["정의", "구하기", "차원 공식", "해의 모양"]),
    cards=[
        dict(title="영공간", sub="A를 곱하면 0이 되는 벡터를 전부 모은 것", visual=nl,
             formula="N(A) = { x : Ax = 0 }",
             ex=f"영공간 방향은 변환 뒤 {Y('흔적도 없이 사라져요')}",
             trap="<b>기억</b> 0 벡터는 항상 들어 있어서 빈 집합일 수 없어요"),
        dict(title="구하기", sub="Ax = 0을 풀어서 자유 변수로 표현", visual=M([[1, 2], [2, 4]]) + M([["x"], ["y"]], BLUE) + "=" + M([[0], [0]], YEL),
             formula="x + 2y = 0 &nbsp;→&nbsp; x = t(−2, 1)",
             ex=f"둘째 행은 첫째의 2배 &nbsp;→ 식은 사실 {Y('하나')}",
             trap="<b>팁</b> 행 사다리꼴로 줄이고 피벗 없는 열 = 자유 변수"),
        dict(title="차원 공식", sub="랭크와 영공간 차원을 더하면 열 개수", visual=M([[1, 2], [2, 4]]) + f"<span class=yel>랭크 1</span> + <span class=red>영공간 1</span> = 2",
             formula="rank A + dim N(A) = n (열 개수)",
             ex=f"2×2인데 랭크 1 &nbsp;→ 영공간은 {Y('직선 하나')}",
             trap="<b>함정</b> n은 행 개수가 아니라 열 개수"),
        dict(title="해의 모양", sub="Ax = b의 해 = 특수해 하나 + 영공간 전체", visual=sol,
             formula="x = x_p + (영공간 벡터)",
             ex=f"그래서 영공간이 0이 아니면 해가 {Y('무한히 많아요')}",
             trap="<b>기억</b> 영공간이 {0}뿐 ⇔ 열이 일차독립 ⇔ 해가 많아야 1개"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('N(A)')} Ax = 0 인 x 전부",
        f"{Y('구하기')} 사다리꼴 → 자유 변수",
        f"{Y('rank + nullity')} = 열 개수",
        f"{Y('해')} = 특수해 + 영공간"]),
)

CAPTION = """공대생 주목🧮 이 빨간 선 위 벡터는 전부 0이 됩니다
행렬이 '지워 버리는' 방향, 그게 영공간이에요.
구하는 법, 차원 공식, 해가 무한히 많아지는 이유까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #영공간 #랭크 #공대생 #공대수학"""
