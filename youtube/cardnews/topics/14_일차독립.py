from cards import *

X0, Y0, S = 400, 330, 70
def g(*vs, extra=""):
    s = grid(X0, Y0, S, 5, 4) + axes(X0, Y0, 300, 330, 290, 40)
    for x, y, c, lab in vs:
        s += vec(X0, Y0, S, x, y, c, lab, w=7)
    return svg(s + extra, 400)

indep = g((3, 1, YEL, "v₁"), (1, 3, GRN, "v₂"))
dep = g((3, 1.5, GRN, "v₂ = 1.5 v₁"), (2, 1, YEL, "v₁"), extra=f'<line x1="{X0-4*S}" y1="{Y0+2*S}" x2="{X0+4.5*S}" y2="{Y0-2.25*S}" stroke="#ff6b61" stroke-width="3" stroke-dasharray="10 8"/>')
three = g((2, 0, YEL, "v₁"), (0, 2, GRN, "v₂"), (2, 2, PUR, "v₃ = v₁ + v₂"))

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="벡터 3개인데", line2="공간을 못 채운다?", sub="일차독립, 한 벡터가 '쓸모없을' 때", visual=three,
               chips=["정의", "종속의 모양", "판정법", "기저"]),
    cards=[
        dict(title="일차독립", sub="0을 만드는 방법이 '전부 0 곱하기' 하나뿐", visual=indep,
             formula="c₁v₁ + c₂v₂ = 0 &nbsp;→&nbsp; c₁ = c₂ = 0 뿐",
             ex=f"서로 다른 방향 두 개 &nbsp;→&nbsp; {Y('평면을 꽉 채워요')}",
             trap="<b>기억</b> 다른 해가 하나라도 있으면 종속"),
        dict(title="종속의 모양", sub="한 벡터가 다른 벡터들로 만들어지면 종속", visual=three,
             formula="v₃ = v₁ + v₂ &nbsp;→&nbsp; 종속",
             ex=f"v₃는 새 방향을 못 더해요 &nbsp;→ 3개여도 {Y('평면까지만')}",
             trap="<b>함정</b> 2개가 한 줄 위에 있어도 종속 (서로 배수)"),
        dict(title="판정법", sub="벡터를 열로 세워 행렬을 만들어요", visual=M([[1, 0, 1], [0, 1, 1], [0, 0, 0]]) + "<span class=red>det = 0</span>",
             formula="랭크 = 벡터 개수 &nbsp;→&nbsp; 독립",
             ex=f"정사각이면 det ≠ 0 으로도 OK &nbsp;·&nbsp; 위 예는 {Y('det = 0, 종속')}",
             trap="<b>함정</b> R³에 벡터 4개면 계산할 필요도 없이 종속"),
        dict(title="기저", sub="독립이면서 공간을 다 채우는 벡터 묶음", visual=indep,
             formula="기저 = 일차독립 + 공간 생성",
             ex=f"R²의 기저는 항상 {Y('2개')}, R³는 {Y('3개')} (= 차원)",
             trap="<b>기억</b> 기저는 여러 개, 개수(차원)는 하나"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('독립')} 0 만드는 법이 전부 0뿐",
        f"{Y('종속')} 다른 벡터로 만들 수 있음",
        f"{Y('판정')} det ≠ 0, 랭크 = 개수",
        f"{Y('기저')} 독립 + 공간 채움"]),
)

CAPTION = """공대생 주목🧮 벡터가 3개인데 공간을 못 채운다?
한 벡터가 나머지로 만들어지면 새 방향을 못 더해요. 그게 일차종속.
det·랭크로 판정하는 법이랑 기저까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #일차독립 #기저 #공대생 #공대수학"""
