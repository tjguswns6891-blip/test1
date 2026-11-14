from cards import *

X0, Y0 = 90, 210
def sqsum(n):
    return lambda x: 4 / math.pi * sum(math.sin((2 * k + 1) * x) / (2 * k + 1) for k in range(n))
sq = lambda x: 1 if math.sin(x) >= 0 else -1

def g(ns, gibbs=False):
    s = axes(X0, Y0, 20, 760, 180, 180, "t", "") + curve(sq, 0.001, 12.56, X0, Y0, 58, 120, DIM, 3, 800, "8 8")
    cols = [BLUE, GRN, YEL]
    for i, n in enumerate(ns):
        s += curve(sqsum(n), 0, 12.56, X0, Y0, 58, 120, cols[i % 3], 5, 800)
    if gibbs:
        s += f'<circle cx="{X0+58*0.2:.0f}" cy="{Y0-120*1.09:.0f}" r="26" fill="none" stroke="#ff6b61" stroke-width="4"/>' + t(X0 + 70, Y0 - 160, "약 9% 튀어나옴", "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    return svg(s, 420)

spec = svg(axes(100, 360, 20, 720, 320, 0, "주파수", "") +
           "".join(f'<rect x="{100+k*130+40}" y="{360-280/(2*k+1):.0f}" width="60" height="{280/(2*k+1):.0f}" rx="6" fill="{YEL}"/>' +
                   t(100 + k * 130 + 70, 395, f"{2*k+1}f", "lbS") + t(100 + k * 130 + 70, 360 - 280 / (2 * k + 1) - 14, f"1/{2*k+1}" if k else "1", "lbY") for k in range(5)), 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="네모난 신호도", line2="사실 사인파의 합", sub="푸리에 급수, 그림으로 한 번에", visual=g([1, 3, 15]),
               chips=["핵심 아이디어", "구형파", "스펙트럼", "기브스 현상"]),
    cards=[
        dict(title="핵심 아이디어", sub="어떤 주기 신호든 사인·코사인으로 쪼갤 수 있어요", visual=g([1, 3]),
             formula="f(t) = a₀ + Σ (a_n cos nωt + b_n sin nωt)",
             ex=f"항을 많이 더할수록 {Y('원래 모양에 가까워져요')}",
             trap="<b>기억</b> 주파수는 기본 주파수의 정수배만 나와요"),
        dict(title="구형파", sub="홀수 배 사인파만 1/n 크기로", visual=g([1, 3, 15]),
             formula=f"{F('4', 'π')} (sin x + {F('sin 3x', '3')} + {F('sin 5x', '5')} + …)",
             ex=f"파랑 1개, 초록 3개, 노랑 {Y('15개')} 더한 것",
             trap="<b>팁</b> 홀함수 → 사인만, 짝함수 → 코사인만"),
        dict(title="스펙트럼", sub="주파수마다 얼마나 들어 있는지 막대로", visual=spec,
             formula="구형파: 1, 1/3, 1/5, 1/7 …",
             ex=f"시간 그래프 대신 {Y('주파수 그래프')}로 보는 것",
             trap="<b>기억</b> 날카로운 모서리 = 높은 주파수가 많다는 뜻"),
        dict(title="기브스 현상", sub="끊어지는 곳 근처에서 꼭 튀어나와요", visual=g([15], True),
             formula="오버슈트 ≈ 9%",
             ex=f"항을 늘려도 {Y('튀는 높이는 그대로')}, 폭만 좁아져요",
             trap="<b>함정</b> \"항을 무한히 더하면 오차 0\"은 불연속점에선 틀려요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('주기 신호')} = 사인·코사인의 합",
        f"{Y('구형파')} 홀수 배, 1/n 크기",
        f"{Y('스펙트럼')} 주파수별 막대",
        f"{Y('기브스')} 모서리에서 9%"]),
)

CAPTION = """전기전자 주목⚡ 네모난 신호도 사실 사인파의 합이에요
구형파 = 홀수 배 사인파를 1, 1/3, 1/5… 크기로 더한 것.
스펙트럼 읽는 법이랑 기브스 현상 함정까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #푸리에급수 #신호및시스템 #전기전자 #공대생"""
