from cards import *

A = M([[1, 2, 3], [2, 4, 6], [1, 1, 1]])
R = M([[1, 2, 3], [0, -1, -2], [0, 0, 0]], YEL)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="3×3 행렬인데", line2="사실은 2차원?", sub="랭크, 쓸모 있는 방향의 개수", visual=A + "→" + R,
               chips=["정의", "구하기", "차원 정리", "해의 개수"]),
    cards=[
        dict(title="랭크", sub="독립인 열(또는 행)의 개수", visual=A + "<span>2행 = 2 × 1행</span>",
             formula="rank = 독립인 열 개수",
             ex=f"열 랭크 = 행 랭크, {Y('항상 같아요')}",
             trap="<b>함정</b> 행렬 크기가 아니라 '쓸모 있는' 방향의 수"),
        dict(title="구하기", sub="행사다리꼴로 만들고 0 아닌 행 세기", visual=A + "→" + R,
             formula="피벗 2개 → rank = 2",
             ex=f"2행 − 2×1행 = 0 &nbsp;→ {Y('한 줄이 사라져요')}",
             trap="<b>기억</b> 정방행렬이면 det = 0 ⇔ rank &lt; n"),
        dict(title="차원 정리", sub="랭크 + 영공간 차원 = 열 개수", visual=A + "<span class=yel>2</span> + <span class=red>1</span> = 3",
             formula="rank A + dim N(A) = n",
             ex=f"3열, 랭크 2 → 영공간 {Y('1차원')} (직선)",
             trap="<b>함정</b> n은 행 개수가 아니라 열 개수"),
        dict(title="해의 개수", sub="n개 미지수 Ax = b 에서", visual=('<div style="display:flex;flex-direction:column;gap:22px;font-size:44px">'
             f'<div>{Y("rank = n")} → 해 0개 또는 1개</div><div>{Y("rank &lt; n")} → 해 0개 또는 무한</div>'
             f'<div>{B("b ∉ C(A)")} → 해 없음</div></div>'),
             formula="정방행렬 rank = n ⇔ 역행렬 있음",
             ex=f"rank = n ⇔ {Y('det ≠ 0')} ⇔ 해 딱 하나",
             trap="<b>기억</b> 해가 있는지는 b, 몇 개인지는 rank가 정해요"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('rank')} = 독립인 열 = 피벗 개수",
        f"{Y('rank + dim N(A) = n')}",
        f"정방: rank = n ⇔ {Y('det ≠ 0')}",
        f"rank &lt; n → 해 {Y('없거나 무한')}"]),
)

CAPTION = """공대생 주목🧮 3×3 행렬인데 사실은 2차원?
랭크는 '쓸모 있는' 방향의 개수예요. 한 행이 다른 행의 배수면 한 줄이 사라져요.
구하는 법, 차원 정리, 해의 개수까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #랭크 #계수 #공대생 #공대수학"""
