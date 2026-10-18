from cards import *

def d(v):
    return f'<span style="opacity:.2">{v}</span>'

A = [[2, 0, 1], [1, 3, 2], [0, 1, 1]]
minor = M([[d(2), d(0), d(1)], [d(1), 3, 2], [d(0), 1, 1]]) + "→" + M([[3, 2], [1, 1]], YEL)
signs = M([[B("+"), "<span class=red>−</span>", B("+")], ["<span class=red>−</span>", B("+"), "<span class=red>−</span>"], [B("+"), "<span class=red>−</span>", B("+")]])
row = M([[Y(2), Y(0), Y(1)], [1, 3, 2], [0, 1, 1]])
col = M([[Y(2), 0, 1], [Y(1), 3, 2], [Y(0), 1, 1]])

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="3×3 행렬식,", line2="한 줄만 고르면 끝", sub="여인수 전개를 숫자로 다 펼쳐 봤어요", visual=M(A) + f"<span class=yel>det = 3</span>",
               chips=["소행렬식", "부호판", "전개", "줄 고르기"]),
    cards=[
        dict(title="소행렬식", sub="i행과 j열을 지우고 남은 작은 행렬식", visual=minor,
             formula="M₁₁ = 3·1 − 2·1 = 1",
             ex="1행 1열을 지우면 2×2가 남아요",
             trap="<b>기억</b> 3×3 하나 = 2×2 세 개로 쪼개는 것"),
        dict(title="부호판", sub="자리마다 +, − 가 체크무늬로", visual=signs,
             formula="C_ij = (−1)<sup>i+j</sup> M_ij",
             ex=f"여인수 C = {Y('부호')} × 소행렬식",
             trap="<b>함정</b> 부호 빼먹는 게 1등 실수. 대각선은 항상 +"),
        dict(title="1행으로 전개", sub="고른 줄의 숫자 × 여인수를 다 더해요", visual=row,
             formula="2·(1) − 0·(…) + 1·(1) = 3",
             ex=f"M₁₃ = det{M([[1, 3], [0, 1]])} = 1 &nbsp;→&nbsp; {Y('det A = 3')}",
             trap="<b>팁</b> 0 곱하는 칸은 계산 안 해도 돼요"),
        dict(title="줄 고르기", sub="어느 행·열로 해도 답은 같아요", visual=col,
             formula="2·(1) − 1·(−1) + 0·(…) = 3",
             ex=f"1열로 해도 {Y('3')} ✓",
             trap="<b>팁</b> 0이 제일 많은 줄을 고르면 계산이 제일 짧아요"),
    ],
    summary=dict(tag="순서대로", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('①')} 0이 많은 줄 고르기",
        f"{Y('②')} 칸마다 소행렬식 (2×2)",
        f"{Y('③')} 체크무늬 부호 붙이기",
        f"{Y('④')} 숫자 × 여인수 다 더하기"]),
)

CAPTION = """공대생 주목🧮 3×3 행렬식, 한 줄만 고르면 끝나요
여인수 전개: 줄 하나 골라서 숫자 × 여인수를 더하기.
부호판이랑 줄 고르는 요령까지 숫자로 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #행렬식 #여인수전개 #공대생 #공대수학"""
