from cards import *

X0, Y0, S = 450, 210, 45
def pic(after=True):
    s = grid(X0, Y0, S, 9, 4) + axes(X0, Y0, 400, 400, 200, 200)
    s += vec(X0, Y0, S, 1, 1, DIM if after else YEL, "" if after else "v₁", w=6) + vec(X0, Y0, S, 1, -1, DIM if after else GRN, "" if after else "v₂", w=6)
    s += vec(X0, Y0, S, 2, 0, DIM, "", w=3) + vec(X0, Y0, S, 4, 2, "#ff6b61", "다른 벡터는 꺾임" if after else "", 14, 14, 3)
    if after:
        s += vec(X0, Y0, S, 3, 3, YEL, "Av₁ = 3v₁", 10, 0, 7) + vec(X0, Y0, S, 1, -1, GRN, "Av₂ = 1·v₂", 10, 34, 7)
    return svg(s, 420)

A = [[2, 1], [1, 2]]
SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="방향이 안 바뀌는", line2="특별한 벡터", sub="고유값·고유벡터, 2×2를 끝까지 손으로", visual=pic(),
               chips=["뜻", "고유값 구하기", "고유벡터 구하기", "검산 요령"]),
    cards=[
        dict(title="뜻", sub="변환해도 방향은 그대로, 길이만 λ배", visual=pic(),
             formula="A v = λ v",
             ex=f"A = [[2, 1], [1, 2]] 에서 (1, 1)은 {Y('3배')}, (1, −1)은 {Y('1배')}",
             trap="<b>함정</b> 0 벡터는 고유벡터가 아니에요 (정의에서 뺌)"),
        dict(title="고유값 구하기", sub="det(A − λI) = 0 (특성방정식)", visual=M([["2 − λ", 1], [1, "2 − λ"]]) + "<span class=yel>det = 0</span>",
             formula="(2 − λ)² − 1 = 0",
             ex=f"→ λ − 2 = ±1 &nbsp;→&nbsp; {Y('λ = 3, 1')}",
             trap="<b>왜?</b> (A − λI)v = 0 에 0 아닌 해가 있으려면 det = 0"),
        dict(title="고유벡터 구하기", sub="λ를 하나씩 넣고 영공간 구하기", visual=M([[-1, 1], [1, -1]]) + M([["x"], ["y"]], BLUE) + "=" + M([[0], [0]], YEL),
             formula="λ = 3: −x + y = 0 &nbsp;→&nbsp; v = (1, 1)",
             ex=f"λ = 1: x + y = 0 &nbsp;→&nbsp; {Y('v = (1, −1)')}",
             trap="<b>기억</b> 고유벡터는 방향만 중요. 2배, −1배 해도 같은 답"),
        dict(title="검산 요령", sub="계산 끝나면 이 두 줄로 바로 확인", visual=M(A) + "<span class=yel>3 + 1 = 4 ✓</span> <span class=grn>3 × 1 = 3 ✓</span>",
             formula="λ 합 = trace(A) &nbsp;·&nbsp; λ 곱 = det(A)",
             ex="trace = 2 + 2 = 4, &nbsp;det = 4 − 1 = 3",
             trap="<b>팁</b> 대칭 행렬이면 고유벡터끼리 항상 수직"),
    ],
    summary=dict(tag="순서대로", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('①')} det(A − λI) = 0 풀기",
        f"{Y('②')} λ마다 (A − λI)v = 0",
        f"{Y('③')} 자유 변수로 v 쓰기",
        f"{Y('④')} 합 = trace, 곱 = det 검산"]),
)

CAPTION = """공대생 주목🧮 변환해도 방향이 안 바뀌는 특별한 벡터
Av = λv. 방향은 그대로, 길이만 λ배 되는 게 고유벡터예요.
2×2를 끝까지 손으로 풀고 검산하는 요령까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #고유값 #고유벡터 #공대생 #공대수학"""
