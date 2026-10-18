from cards import *

X0, Y0 = 100, 360
def resp(Q):
    return lambda u: 1 / math.sqrt(1 + Q * Q * (u - 1 / u) ** 2) if u > 0 else 0
def g(qs, bw=False):
    s = axes(X0, Y0, 20, 740, 320, 20, "ω", "")
    cols = {1: BLUE, 3: YEL, 10: GRN}
    for q in qs:
        s += curve(resp(q), 0.05, 3, X0, Y0, 240, 290, cols[q], 6)
    s += f'<line x1="{X0+240}" y1="{Y0}" x2="{X0+240}" y2="{Y0-300}" stroke="{DIM}" stroke-width="2" stroke-dasharray="6 8"/>' + t(X0 + 240, Y0 + 40, "ω₀", "lbS")
    if bw:
        y = Y0 - 290 / math.sqrt(2)
        u1, u2 = (-1 / 3 + math.sqrt(1 / 9 + 4)) / 2, (1 / 3 + math.sqrt(1 / 9 + 4)) / 2
        s += f'<line x1="{X0+240*u1:.0f}" y1="{y:.0f}" x2="{X0+240*u2:.0f}" y2="{y:.0f}" stroke="{BLUE}" stroke-width="5" marker-end="url(#ab)" marker-start="url(#ab)"/>' + t(X0 + 240 * u2 + 110, y + 12, "대역폭 B", "lbB")
    return svg(s, 400)

ckt = svg(vsrc(150, 80, 340, ac=True) + res(150, 80, 400, 80) + ind(400, 80, 660, 80) + cap(660, 80, 660, 340) + wire((150, 340), (660, 340)) +
          t(275, 45, "10Ω") + t(530, 45, "10mH") + t(710, 222, "10μF", anchor="start"))

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="라디오가 한 방송만", line2="골라 듣는 원리", sub="공진과 Q값, 숫자로 한 번에", visual=g([1, 3, 10]),
               chips=["공진 주파수", "직렬 공진", "Q값", "대역폭"]),
    cards=[
        dict(title="공진 주파수", sub="L과 C의 리액턴스가 똑같아지는 주파수", visual=ckt,
             formula=f"ω₀ = {F('1', '√(LC)')}",
             ex=f"10mH, 10μF &nbsp;→&nbsp; ω₀ ≈ 3162 rad/s, {Y('f₀ ≈ 503Hz')}",
             trap="<b>함정</b> f₀ = ω₀ / 2π. rad/s랑 Hz 섞지 말기"),
        dict(title="직렬 공진", sub="X_L과 X_C가 서로 지워져요", visual=g([3]),
             formula="Z = R (최소) &nbsp;→&nbsp; 전류 최대",
             ex=f"10V 넣으면 10V ÷ 10Ω = {Y('1A')}, 공진에서만",
             trap="<b>함정</b> 병렬 공진은 반대로 임피던스가 최대"),
        dict(title="Q값", sub="공진이 얼마나 뾰족한지", visual=g([1, 3, 10]),
             formula=f"Q = {F('ω₀ L', 'R')} = {F('1', 'R')}√{F('L', 'C')}",
             ex=f"3162 × 0.01 ÷ 10 ≈ {Y('3.2')} &nbsp;(R이 작을수록 뾰족)",
             trap="<b>기억</b> Q가 크면 원하는 주파수만 쏙, 잡음은 걸러져요"),
        dict(title="대역폭", sub="전력이 절반(크기 1/√2)이 되는 두 주파수 사이", visual=g([3], True),
             formula=f"B = {F('ω₀', 'Q')} = {F('R', 'L')}",
             ex=f"10Ω ÷ 10mH = {Y('1000 rad/s')}",
             trap="<b>함정</b> Q가 커지면 대역폭은 좁아져요. 반비례!"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('ω₀ = 1/√LC')}",
        f"{Y('직렬 공진')} Z = R, 전류 최대",
        f"{Y('Q = ω₀L/R')} 클수록 뾰족",
        f"{Y('B = ω₀/Q')} 반비례"]),
)

CAPTION = """전기전자 주목⚡ 라디오가 한 방송만 골라 듣는 원리
L과 C가 딱 맞는 주파수에서 서로 지워지는 공진, 얼마나 뾰족한지는 Q값.
공진 주파수부터 대역폭까지 숫자로 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #공진 #Q값 #전기전자 #공대생"""
