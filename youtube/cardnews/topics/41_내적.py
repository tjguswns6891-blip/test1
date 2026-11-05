from cards import *

X0, Y0, S = 330, 300, 80
def pic(a, b, la, lb, ang=True, S=S, extra=""):
    n = int(320 // S)
    s = grid(X0, Y0, S, n, int(260 // S)) + axes(X0, Y0, 300, 380, 280, 100)
    s += vec(X0, Y0, S, *a, YEL, la, 12, -12, 7) + vec(X0, Y0, S, *b, BLUE, lb, 12, -12, 7) + extra
    if ang:
        ta, tb = math.atan2(a[1], a[0]), math.atan2(b[1], b[0])
        r = 70
        s += f'<path d="M{X0+r*math.cos(ta):.1f},{Y0-r*math.sin(ta):.1f} A{r},{r} 0 0 0 {X0+r*math.cos(tb):.1f},{Y0-r*math.sin(tb):.1f}" fill="none" stroke="{W}" stroke-width="4"/>'
        m = (ta + tb) / 2
        s += t(X0 + 100 * math.cos(m), Y0 - 100 * math.sin(m) + 12, "θ", "lb")
    return svg(s, 420)

def perp():
    s = pic((2, 1), (-1, 2), "(2, 1)", "(−1, 2)", False)
    return s.replace("</svg>", f'<path d="M{X0+0.25*S*2/2.236*2:.1f},{Y0-0.25*S*1/2.236*2:.1f} l{-0.25*S/2.236*2:.1f},{-0.25*S*2/2.236*2:.1f} l{-0.25*S*2/2.236*2:.1f},{0.25*S/2.236*2:.1f}" fill="none" stroke="{W}" stroke-width="4"/></svg>')

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="두 벡터가", line2="얼마나 같은 방향?", sub="내적 하나로 각도, 길이, 수직까지", visual=pic((3, 1), (1, 2), "a", "b"),
               chips=["계산", "각도", "수직", "길이"]),
    cards=[
        dict(title="계산", sub="같은 자리끼리 곱해서 더하기", visual=pic((3, 1), (1, 2), "a = (3, 1)", "b = (1, 2)"),
             formula="a · b = a₁b₁ + a₂b₂",
             ex=f"(3, 1) · (1, 2) = 3 + 2 = {Y('5')}",
             trap="<b>함정</b> 결과는 벡터가 아니라 숫자 하나 (스칼라)"),
        dict(title="각도", sub="내적을 두 길이로 나누면 cosθ", visual=pic((1, 0), (1, 1), "(1, 0)", "(1, 1)", S=200),
             formula=f"cosθ = {F('a · b', '‖a‖ ‖b‖')}",
             ex=f"{F('1', '1 × √2')} = 0.707 &nbsp;→&nbsp; {Y('θ = 45°')}",
             trap="<b>기억</b> 내적 &gt; 0 예각, = 0 직각, &lt; 0 둔각"),
        dict(title="수직", sub="내적이 0이면 서로 직각", visual=perp(),
             formula="a · b = 0 &nbsp;⇔&nbsp; a ⊥ b",
             ex=f"(2, 1) · (−1, 2) = −2 + 2 = {Y('0')} ✓",
             trap="<b>함정</b> 영벡터는 어떤 벡터와도 내적이 0"),
        dict(title="길이", sub="자기 자신과 내적하면 길이의 제곱", visual=pic((3, 4), (3, 4), "(3, 4)", "", False, 62, t(X0 + 120, Y0 - 120, "길이 5", "lbY", "end")),
             formula="‖a‖ = √(a · a)",
             ex=f"(3, 4) → √(9 + 16) = {Y('5')}",
             trap="<b>기억</b> 길이로 나누면 단위벡터 (길이 1)"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('a·b = a₁b₁ + a₂b₂')} (숫자)",
        f"{Y('cosθ = a·b / ‖a‖‖b‖')}",
        f"{Y('a·b = 0')} ⇔ 수직",
        f"{Y('‖a‖ = √(a·a)')}"]),
)

CAPTION = """공대생 주목🧮 두 벡터가 얼마나 같은 방향일까?
내적 하나면 각도, 수직 판정, 길이까지 다 나와요.
숫자 예제 4개로 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #내적 #벡터 #공대생 #공대수학"""
