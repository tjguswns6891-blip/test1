from cards import *

P = M([[1, 1], [1, -1]], GRN)
D = M([[3, 0], [0, 1]], YEL)
Pi = M([["½", "½"], ["½", "−½"]], PUR)
SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="행렬 100제곱,", line2="손으로 하는 법", sub="대각화 A = PDP⁻¹", visual="A = " + P + D + Pi,
               chips=["뜻", "만드는 법", "거듭제곱", "안 될 때"]),
    cards=[
        dict(title="대각화", sub="고유벡터 기저로 보면 그냥 늘리기만 하는 변환", visual='<span style="font-size:40px">' + M([[2, 1], [1, 2]]) + "=" + P + D + Pi + "</span>",
             formula="A = P D P⁻¹",
             ex=f"P = {Y('고유벡터')}를 열로, D = {Y('고유값')}을 대각에",
             trap="<b>함정</b> P의 열 순서와 D의 대각 순서를 꼭 맞추기"),
        dict(title="만드는 법", sub="고유값·고유벡터만 구하면 바로 써요", visual=f"<span class=yel>λ = 3</span> → <span class=grn>(1, 1)</span> &nbsp; <span class=yel>λ = 1</span> → <span class=grn>(1, −1)</span>",
             formula=f"P = {M([[1, 1], [1, -1]])}, &nbsp;D = {M([[3, 0], [0, 1]])}",
             ex=f"P⁻¹ = {F('1', '−2')} [[−1, −1], [−1, 1]] = {Y('[[½, ½], [½, −½]]')}",
             trap="<b>팁</b> 대칭 행렬이면 P를 직교행렬로: P⁻¹ = Pᵀ"),
        dict(title="거듭제곱", sub="가운데 P⁻¹P가 다 지워져요", visual='<span style="font-size:40px">Aⁿ = ' + P + M([["3ⁿ", 0], [0, 1]], YEL) + Pi + "</span>",
             formula="Aⁿ = P Dⁿ P⁻¹",
             ex=f"D¹⁰⁰ = 대각 원소만 100제곱 &nbsp;→ {Y('3¹⁰⁰, 1')}",
             trap="<b>기억</b> 마르코프 체인 정상 상태, 피보나치 일반항이 다 이 방법"),
        dict(title="안 될 때", sub="일차독립 고유벡터가 n개 있어야 해요", visual=M([[1, 1], [0, 1]]) + "<span class=red>λ = 1 (중복), 고유벡터 1개</span>",
             formula="대각화 가능 ⇔ 독립 고유벡터 n개",
             ex=f"고유값이 전부 다르면 {Y('무조건 가능')}",
             trap="<b>함정</b> 고유값이 겹쳐도 될 때가 있어요 (예: 단위행렬)"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('A = PDP⁻¹')}",
        f"{Y('P')} 고유벡터 열, {Y('D')} 고유값 대각",
        f"{Y('Aⁿ = PDⁿP⁻¹')} 거듭제곱 쉬움",
        f"{Y('조건')} 독립 고유벡터 n개"]),
)

CAPTION = """공대생 주목🧮 행렬 100제곱, 손으로 하는 법
대각화 A = PDP⁻¹ 하면 Aⁿ = PDⁿP⁻¹, 대각 원소만 거듭제곱하면 끝.
P·D 만드는 법이랑 대각화가 안 되는 경우까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #대각화 #고유값 #공대생 #공대수학"""
