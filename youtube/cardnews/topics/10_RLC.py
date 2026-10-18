from cards import *

def step(z):
    def f(t):
        if abs(z - 1) < 1e-9:
            return 1 - (1 + t) * math.exp(-t)
        if z < 1:
            wd = math.sqrt(1 - z * z)
            return 1 - math.exp(-z * t) * (math.cos(wd * t) + z / wd * math.sin(wd * t))
        s1, s2 = -z + math.sqrt(z * z - 1), -z - math.sqrt(z * z - 1)
        return 1 + (s2 * math.exp(s1 * t) - s1 * math.exp(s2 * t)) / (s1 - s2)
    return f

X0, Y0 = 100, 330
def g(*zs):
    cols = {2.0: BLUE, 1.0: GRN, 0.2: YEL}
    s = axes(X0, Y0, 20, 740, 300, 30, "t", "")
    s += f'<line x1="{X0}" y1="{Y0-160}" x2="{X0+720}" y2="{Y0-160}" stroke="{DIM}" stroke-width="2" stroke-dasharray="6 8"/>'
    for z in zs:
        s += curve(step(z), 0, 14, X0, Y0, 50, 160, cols[z], 6)
    return svg(s, 400)

ckt = svg(vsrc(150, 80, 340) + res(150, 80, 400, 80) + ind(400, 80, 660, 80) + cap(660, 80, 660, 340) + wire((150, 340), (660, 340)) +
          t(275, 45, "R") + t(530, 45, "10mH") + t(710, 222, "10μF", anchor="start"))

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="저항 하나로", line2="모양이 세 가지", sub="2차 RLC 회로, 과감쇠 · 임계 · 부족 감쇠", visual=g(2.0, 1.0, 0.2),
               chips=["왜 2차?", "과감쇠", "임계 감쇠", "부족 감쇠"]),
    cards=[
        dict(title="왜 2차?", sub="L과 C가 에너지를 주고받아서 식이 2차가 돼요", visual=ckt,
             formula=f"s² + {F('R', 'L')} s + {F('1', 'LC')} = 0",
             ex=f"α = {F('R', '2L')}, &nbsp;ω₀ = {F('1', '√(LC)')} &nbsp;→ 둘을 비교",
             trap="<b>함정</b> 병렬 RLC는 α = 1 / (2RC). 직렬이랑 달라요"),
        dict(title="과감쇠", sub="α > ω₀, 극점 두 개가 실수로 따로", visual=g(2.0),
             formula="R > 2√(L/C)",
             ex=f"10mH, 10μF면 {Y('R > 63Ω')} &nbsp;→ 느릿느릿 올라감",
             trap="<b>특징</b> 출렁임은 없지만 목표에 늦게 도착"),
        dict(title="임계 감쇠", sub="α = ω₀, 극점 두 개가 딱 겹쳐요", visual=g(1.0),
             formula="R = 2√(L/C)",
             ex=f"2√(10mH ÷ 10μF) = 2√1000 ≈ {Y('63Ω')}",
             trap="<b>특징</b> 출렁임 없이 가장 빨리 도착 (서스펜션 목표)"),
        dict(title="부족 감쇠", sub="α < ω₀, 극점이 복소수 → 출렁출렁", visual=g(0.2),
             formula="ω_d = √(ω₀² − α²)",
             ex="R이 작을수록 더 오래, 더 크게 출렁여요",
             trap="<b>함정</b> 출렁이는 주파수는 ω₀가 아니라 ω_d"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('α = R/2L')} vs {Y('ω₀ = 1/√LC')}",
        f"{Y('α > ω₀')} 과감쇠, 느림",
        f"{Y('α = ω₀')} 임계, 가장 빠름",
        f"{Y('α < ω₀')} 부족, 출렁임"]),
)

CAPTION = """전기전자 주목⚡ 같은 RLC 회로인데 저항 하나로 모양이 세 가지
과감쇠는 느릿느릿, 임계 감쇠는 가장 빠르게, 부족 감쇠는 출렁출렁.
경계 저항 R = 2√(L/C)까지 숫자로 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #RLC회로 #과도응답 #전기전자 #공대생"""
