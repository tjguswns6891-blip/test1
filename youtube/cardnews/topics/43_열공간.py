from cards import *

X0, Y0, S = 400, 220, 55
def pic(bs=True):
    s = grid(X0, Y0, S, 6, 3) + axes(X0, Y0, 340, 360, 190, 190)
    s += f'<line x1="{X0-1.8*S}" y1="{Y0+3.6*S}" x2="{X0+1.8*S}" y2="{Y0-3.6*S}" stroke="{YEL}" stroke-width="8" opacity=".5"/>'
    s += vec(X0, Y0, S, 1, 2, YEL, "1열 (1, 2)", 14, 30, 7)
    if bs:
        s += dot(X0 + 1.5 * S, Y0 - 3 * S, GRN) + t(X0 + 1.5 * S + 16, Y0 - 3 * S + 12, "(3, 6) ✓", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"')
        s += dot(X0 + S, Y0, "#ff6b61") + t(X0 + S + 16, Y0 + 44, "(1, 0) ✕", "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    s += t(X0 - 320, Y0 - 150, "C(A) = 직선 y = 2x", "lbY", "start")
    return svg(s, 420)

two = svg(grid(450, 210, 60, 6, 3) + axes(450, 210, 380, 380, 190, 190) + f'<rect x="80" y="30" width="740" height="360" fill="rgba(246,195,67,.08)"/>' +
          vec(450, 210, 60, 2, 1, YEL, "(2, 1)", 12, -10, 7) + vec(450, 210, 60, -1, 2, BLUE, "(−1, 2)", -140, -10, 7) + t(110, 370, "독립인 열 2개 → 평면 전체", "lbY", "start"), 420)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="Ax = b, 해가", line2="있을까 없을까", sub="열공간 하나로 바로 판정", visual=pic(),
               chips=["정의", "해 존재 조건", "예제", "차원"]),
    cards=[
        dict(title="열공간", sub="A의 열벡터들로 만들 수 있는 모든 벡터", visual=two,
             formula="C(A) = { Ax : x는 아무 벡터 }",
             ex=f"Ax = x₁(1열) + x₂(2열) &nbsp;→ {Y('열의 일차결합')}",
             trap="<b>기억</b> 열공간은 항상 원점을 지나요"),
        dict(title="해 존재 조건", sub="b가 열들로 만들어지면 해가 있어요", visual=pic(),
             formula="해 있음 &nbsp;⇔&nbsp; b ∈ C(A)",
             ex=f"b가 노란 직선 위 → {Y('해 있음')}, 밖 → 해 없음",
             trap="<b>함정</b> 해가 있어도 하나라는 보장은 없어요 (영공간)"),
        dict(title="예제", sub="두 열이 같은 방향이면 공간이 줄어요", visual=M([[1, 2], [2, 4]]) + "<span>2열 = 2 × 1열</span>",
             formula="C(A) = 직선 y = 2x",
             ex=f"b = (3, 6) {Y('해 있음')}, b = (1, 0) 해 없음",
             trap="<b>팁</b> 종속인 열은 열공간을 넓혀 주지 못해요"),
        dict(title="차원", sub="열공간 차원 = 독립인 열 개수", visual=two,
             formula="dim C(A) = rank A",
             ex=f"기저는 {Y('피벗이 있는 원래 A의 열')}",
             trap="<b>함정</b> 소거한 뒤 행렬의 열을 기저로 쓰면 틀려요"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('C(A)')} = 열들의 일차결합 전부",
        f"Ax = b 해 ⇔ {Y('b ∈ C(A)')}",
        f"{Y('dim C(A) = rank')}",
        f"기저 = 원래 A의 {Y('피벗 열')}"]),
)

CAPTION = """공대생 주목🧮 Ax = b, 해가 있을까 없을까?
열공간(A의 열로 만들 수 있는 벡터 전부) 안에 b가 있으면 해가 있어요.
예제 하나로 보고, 차원과 기저 고르는 함정까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #열공간 #연립방정식 #공대생 #공대수학"""
