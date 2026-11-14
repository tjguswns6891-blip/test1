from cards import *

X0, Y0, S = 400, 260, 60
def pic(skew=True, std=True):
    s = grid(X0, Y0, S, 6, 4) + axes(X0, Y0, 330, 340, 230, 150)
    if skew:
        for k in range(-4, 5):
            s += f'<line x1="{X0-4*S+k*S}" y1="{Y0+4*S+k*S}" x2="{X0+4*S+k*S}" y2="{Y0-4*S+k*S}" stroke="{PUR}" stroke-opacity=".25" stroke-width="2"/>'
            s += f'<line x1="{X0-4*S+k*S}" y1="{Y0-4*S-k*S}" x2="{X0+4*S+k*S}" y2="{Y0+4*S-k*S}" stroke="{PUR}" stroke-opacity=".25" stroke-width="2"/>'
        s += vec(X0, Y0, S, 1, 1, GRN, "b₁", 8, -8) + vec(X0, Y0, S, 1, -1, PUR, "b₂", 8, 30)
        s += f'<path d="M{X0},{Y0} L{X0+2*S},{Y0-2*S} L{X0+3*S},{Y0-S}" fill="none" stroke="{GRN}" stroke-width="3" stroke-dasharray="8 8"/>'
    s += vec(X0, Y0, S, 3, 1, YEL, "v", 12, -10, 8) + t(X0 + 3 * S + 30, Y0 - S + 40, "(3, 1) = 2b₁ + 1b₂", "lbY", "start")
    return svg(s, 430)

P = [[1, 1], [1, -1]]
SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="같은 점인데", line2="좌표가 두 개?", sub="기저 변환, 눈금자를 바꾸는 일", visual=pic(),
               chips=["좌표의 뜻", "P 행렬", "되돌리기", "닮음 행렬"]),
    cards=[
        dict(title="좌표의 뜻", sub="좌표 = 기저 벡터를 몇 개씩 쓰는지", visual=pic(),
             formula="v = 2b₁ + 1b₂ &nbsp;→&nbsp; [v]<sub>B</sub> = (2, 1)",
             ex=f"표준 기저에선 {Y('(3, 1)')}, 기저 B에선 {Y('(2, 1)')}. 같은 화살표!",
             trap="<b>기억</b> 벡터는 그대로, 바뀌는 건 '읽는 눈금'"),
        dict(title="P 행렬", sub="새 기저 벡터를 열로 세우면 변환 행렬", visual=M(P, GRN) + M([[2], [1]], YEL) + "=" + M([[3], [1]]),
             formula="v = P [v]<sub>B</sub>",
             ex=f"P = [b₁ b₂] &nbsp;→&nbsp; B 좌표를 {Y('표준 좌표')}로",
             trap="<b>함정</b> 기저 벡터를 행이 아니라 열로!"),
        dict(title="되돌리기", sub="표준 좌표 → B 좌표는 역행렬로", visual=M([["½", "½"], ["½", "−½"]], PUR) + M([[3], [1]]) + "=" + M([[2], [1]], YEL),
             formula="[v]<sub>B</sub> = P⁻¹ v",
             ex=f"P⁻¹ = {F('1', '−2')} [[−1, −1], [−1, 1]] &nbsp;→&nbsp; {Y('(2, 1)')}",
             trap="<b>함정</b> 방향 헷갈리면 P 쪽이 'B → 표준'만 기억"),
        dict(title="닮음 행렬", sub="같은 변환도 기저를 바꾸면 행렬이 바뀌어요", visual="A′ = " + M([["P⁻¹"]], PUR) + " A " + M([["P"]], GRN),
             formula="A′ = P⁻¹ A P",
             ex=f"고유벡터로 기저를 잡으면 A′가 {Y('대각행렬')} (= 대각화)",
             trap="<b>기억</b> 닮은 행렬끼리는 det, trace, 고유값이 같아요"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('좌표')} = 기저를 몇 개씩",
        f"{Y('v = P[v]<sub>B</sub>')} P = 기저를 열로",
        f"{Y('[v]<sub>B</sub> = P⁻¹v')}",
        f"{Y('A′ = P⁻¹AP')} 닮음"]),
)

CAPTION = """공대생 주목🧮 같은 점인데 좌표가 두 개?
좌표는 '기저 벡터를 몇 개씩 쓰는지'라서, 기저를 바꾸면 숫자가 바뀌어요.
P 행렬로 오가는 법이랑 닮음 행렬까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #기저변환 #좌표 #공대생 #공대수학"""
