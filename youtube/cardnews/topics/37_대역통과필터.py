from cards import *

ck = svg(vsrc(130, 80, 340, ac=True) + wire((130, 80), (200, 80)) + ind(200, 80, 380, 80) + cap(380, 80, 560, 80) + res(560, 80, 560, 340) +
         wire((130, 340), (760, 340)) + wire((560, 80), (760, 80)) + term(760, 80) + term(760, 340) + dot(560, 80) + dot(560, 340) +
         t(290, 45, "L") + t(470, 45, "C") + t(600, 222, "R", "lb", "start") + t(780, 222, "출력", "lbY", "start"), 400)

X0, Y0 = 110, 340
def g(qs=(3,), bw=False):
    s = axes(X0, Y0, 20, 720, 300, 20, "주파수 (로그)", "|H|")
    for q, c in zip(qs, (YEL, BLUE)):
        f = lambda x, q=q: 1 / math.sqrt(1 + q * q * (10 ** x - 10 ** -x) ** 2)
        s += curve(f, -1.2, 1.2, X0 + 345, Y0, 280, 270, c, 6)
    s += f'<line x1="{X0+345}" y1="{Y0}" x2="{X0+345}" y2="{Y0-270}" stroke="{DIM}" stroke-width="3" stroke-dasharray="8 8"/>' + t(X0 + 345, Y0 + 40, "f₀", "lbS")
    if bw:
        q = qs[0]; d = math.log10((1 + math.sqrt(1 + 4 * q * q)) / (2 * q))
        y = Y0 - 270 / math.sqrt(2)
        s += arrow(X0 + 345 - d * 280, y, X0 + 345 + d * 280, y, BLUE, 4) + arrow(X0 + 345 + d * 280, y, X0 + 345 - d * 280, y, BLUE, 4)
        s += t(X0 + 345 + d * 280 + 20, y + 10, "BW", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    if len(qs) > 1:
        s += t(X0 + 700, 80, "R 큼 (Q 1)", "lbY", "end") + t(X0 + 700, 130, "R 작음 (Q 10)", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    return svg(s, 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="원하는 주파수만", line2="골라 통과시키기", sub="대역통과 필터, 중심과 폭 두 개만", visual=g(),
               chips=["모양", "중심 주파수", "대역폭", "폭 조절"]),
    cards=[
        dict(title="모양", sub="L, C를 직렬로 두고 출력을 R에서", visual=ck,
             formula="저주파는 C가, 고주파는 L이 막아요",
             ex=f"가운데 {Y('f₀')}에서만 L과 C가 서로 지워져요",
             trap="<b>기억</b> f₀에서 출력 = 입력 (이득 1)"),
        dict(title="중심 주파수", sub="L과 C의 리액턴스가 같아지는 곳", visual=g(),
             formula=f"f₀ = {F('1', '2π√(LC)')}",
             ex=f"예) L = 10mH, C = 1μF &nbsp;→&nbsp; {Y('약 1.59kHz')}",
             trap="<b>함정</b> R은 중심 주파수에 영향 없어요"),
        dict(title="대역폭", sub="크기가 0.707배(−3dB) 되는 두 점 사이", visual=g((1.5,), True),
             formula=f"BW = {F('R', '2πL')} [Hz]",
             ex=f"예) R = 10Ω → BW ≈ 159Hz, {Y('Q = f₀/BW = 10')}",
             trap="<b>함정</b> R / L 은 rad/s. Hz로 쓰려면 2π로 나누기"),
        dict(title="폭 조절", sub="f₀는 L·C로, 폭은 R로 따로 정해요", visual=g((1, 10)),
             formula="R ↓ → 폭 좁아짐 (Q ↑)",
             ex=f"채널을 날카롭게 고르려면 {Y('R을 작게')}",
             trap="<b>함정</b> 병렬 RLC는 반대로 R이 클수록 좁아요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"직렬 L·C, 출력은 {Y('R')}",
        f"{Y('f₀ = 1 / 2π√LC')}",
        f"{Y('BW = R / 2πL')}, Q = f₀ / BW",
        f"R ↓ → {Y('더 날카롭게')}"]),
)

CAPTION = """전기전자 주목⚡ 원하는 주파수만 골라 통과시키는 필터
대역통과 필터는 중심 주파수 f₀와 대역폭 BW 두 개만 정하면 돼요.
f₀는 L·C로, 폭은 R로. 숫자 예제까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #대역통과필터 #필터 #전기전자 #공대생"""
