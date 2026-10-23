from cards import *

S = 60
def para(v1, v2, X=330, Y=330, c=BLUE, lab=""):
    pts = [(X, Y), (X + v1[0] * S, Y - v1[1] * S), (X + (v1[0] + v2[0]) * S, Y - (v1[1] + v2[1]) * S), (X + v2[0] * S, Y - v2[1] * S)]
    return (f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width="3" stroke-dasharray="10 8"/>'
            + vec(X, Y, S, *v1, YEL, "", w=7) + vec(X, Y, S, *v2, GRN, "", w=7) + (t((pts[0][0] + pts[2][0]) / 2, (pts[0][1] + pts[2][1]) / 2 + 14, lab, "lbB") if lab else ""))

area = svg(grid(330, 330, S, 5, 5) + axes(330, 330, 60, 330, 300, 30) + para((3, 1), (1, 2), lab="넓이 5") +
           t(530, 300, "(3, 1)", "lbY", "start") + t(320, 190, "(1, 2)", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{GRN}"'), 400)
flat = svg(grid(330, 330, S, 5, 5) + axes(330, 330, 60, 330, 300, 30) + vec(330, 330, S, 4, 2, GRN, "", w=7) + vec(330, 330, S, 2, 1, YEL, "", w=9) +
           t(470, 300, "(2, 1)", "lbY", "start") + t(560, 180, "(4, 2)", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"') +
           t(700, 250, "넓이 0", "lbB"), 400)

def sq(x, y, s, c, lab):
    return (f'<rect x="{x}" y="{y - s}" width="{s}" height="{s}" fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width="4"/>' +
            t(x + s / 2, y + 44, lab, "lbC").replace('class="lbC"', f'class="lbC" fill="{c}"'))
prod = svg(sq(60, 300, 80, W, "넓이 1") + t(210, 250, "A", "lbB") + arrow(170, 270, 250, 270, BLUE) +
           sq(290, 300, 113, YEL, "× 2") + t(470, 250, "B", "lbB") + arrow(430, 270, 510, 270, BLUE) +
           sq(560, 300, 196, GRN, "× 6"), 380)
flip = svg(grid(330, 330, S, 5, 5) + axes(330, 330, 60, 330, 300, 30) + para((1, 2), (3, 1), c=PUR, lab="−5") +
           t(320, 190, "① (1, 2)", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{YEL}"') +
           t(530, 300, "② (3, 1)", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"'), 400)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="행렬식, 외우지 말고", line2="넓이로 보세요", sub="ad − bc가 왜 넓이인지, 0이면 무슨 뜻인지", visual=area,
               chips=["넓이", "부호", "det = 0", "곱의 성질"]),
    cards=[
        dict(title="넓이", sub="2×2 행렬식 = 두 열벡터가 만드는 평행사변형 넓이", visual=area,
             formula=f"det {M([['a', 'b'], ['c', 'd']])} = ad − bc",
             ex=f"예) 열 (3,1), (1,2) &nbsp;→&nbsp; 3·2 − 1·1 = {Y('5')}",
             trap="<b>기억</b> 3×3이면 세 열벡터가 만드는 상자의 부피"),
        dict(title="부호", sub="두 열의 순서를 바꾸면 값의 부호가 바뀌어요", visual=flip,
             formula=f"det {M([[1, 3], [2, 1]])} = 1 − 6 = −5",
             ex=f"넓이는 {Y('|−5| = 5')}, 마이너스는 공간이 뒤집혔다는 뜻",
             trap="<b>함정</b> 음수 = 틀린 답이 아니에요. 방향 정보예요"),
        dict(title="det = 0", sub="두 벡터가 한 줄에 서면 넓이가 0", visual=flat,
             formula="det A = 0 &nbsp;⇔&nbsp; 역행렬 없음",
             ex=f"예) 열 (2,1), (4,2) &nbsp;→&nbsp; 2·2 − 4·1 = {Y('0')}",
             trap="<b>함정</b> 납작해진 공간은 되돌릴 수 없어서 A⁻¹이 없어요"),
        dict(title="곱의 성질", sub="변환을 두 번 하면 넓이 배율도 곱해져요", visual=prod,
             formula="det(AB) = det A × det B",
             ex=f"예) 2배 × 3배 = {Y('6배')} &nbsp;·&nbsp; det(A⁻¹) = 1 / det A",
             trap="<b>함정</b> det(A + B) ≠ det A + det B. 더하기는 안 돼요"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('det')} = 넓이(2D) · 부피(3D) 배율",
        f"{Y('부호 −')} 면 공간이 뒤집힘",
        f"{Y('det = 0')} 납작, 역행렬 없음",
        f"{Y('det(AB)')} = det A · det B"]),
)

CAPTION = """공대생 주목🧮 행렬식, 외우지 말고 넓이로 보세요
ad − bc는 두 열벡터가 만드는 평행사변형 넓이예요.
그래서 0이면 납작해지고, 역행렬이 없어요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #행렬식 #행렬 #공대생 #공대수학"""
