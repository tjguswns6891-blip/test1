from cards import *

X0, Y0 = 90, 210
cols = [YEL, GRN, PUR]
waves = svg(axes(X0, Y0, 20, 760, 180, 180, "t", "") +
            "".join(curve(lambda x, k=k: math.sin(x - k * 2 * math.pi / 3), 0, 12.56, X0, Y0, 58, 150, cols[k]) for k in range(3)) +
            t(X0 + 700, 50, "A · B · C, 120°씩", "lbS", "end"), 420)

C, R = (450, 220), 150
def star(lines=False):
    s = ""
    for k, c in enumerate(cols):
        a = math.radians(90 + 120 * k)
        x, y = C[0] + R * math.cos(a), C[1] - R * math.sin(a)
        s += arrow(C[0], C[1], x, y, c, 7) + t(x + (30 if x > 450 else -30 if x < 450 else 0), y + (-16 if y < 220 else 40), f"V_{'ABC'[k]}", "lbC", "middle").replace('class="lbC"', f'class="lbC" fill="{c}"')
    if lines:
        a, b = [(C[0] + R * math.cos(math.radians(90 + 120 * k)), C[1] - R * math.sin(math.radians(90 + 120 * k))) for k in (0, 1)]
        s += f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{BLUE}" stroke-width="5" stroke-dasharray="12 8"/>' + t(250, 130, "V_AB = √3 V_상", "lbB")
    return svg(s + dot(*C), 420)

def zbox(x, y, ang):
    return (f'<g transform="translate({x},{y}) rotate({ang})"><rect x="-46" y="-20" width="92" height="40" rx="8" fill="#11141b" stroke="{YEL}" stroke-width="5"/>'
            f'<text x="0" y="12" class="lbY" text-anchor="middle" font-size="30">Z</text></g>')
A, Bv, Cv = (450, 90), (260, 340), (640, 340)
delta = svg(f'<polygon points="{A[0]},{A[1]} {Bv[0]},{Bv[1]} {Cv[0]},{Cv[1]}" fill="none" stroke="{W}" stroke-width="5" stroke-linejoin="round"/>' +
            zbox(355, 215, -52.8) + zbox(545, 215, 52.8) + zbox(450, 340, 0) +
            wire(A, (450, 20)) + wire(Bv, (120, 340)) + wire(Cv, (780, 340)) + dot(*A) + dot(*Bv) + dot(*Cv) +
            arrow(160, 310, 230, 310, BLUE) + t(110, 300, "I_선", "lbB") + t(610, 225, "I_상", "lbY", "start") + t(120, 395, "A·B·C 선이 바로 꼭짓점에", "lbS", "start"), 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="전선 3가닥으로", line2="공장이 돌아가는 이유", sub="3상 교류, √3 하나만 기억하면 돼요", visual=waves,
               chips=["120°", "Y결선", "Δ결선", "3상 전력"]),
    cards=[
        dict(title="120°씩 어긋난 세 파형", sub="세 상을 더하면 언제나 0", visual=waves,
             formula="v_A + v_B + v_C = 0 (평형일 때)",
             ex=f"그래서 {Y('중성선 전류 = 0')} &nbsp;→ 전선을 아낄 수 있어요",
             trap="<b>조건</b> 세 상 부하가 똑같을 때(평형)만 0"),
        dict(title="Y결선", sub="상전압 둘 사이가 선간전압", visual=star(True),
             formula="V_선 = √3 V_상 &nbsp;·&nbsp; I_선 = I_상",
             ex=f"예) 상전압 220V &nbsp;→&nbsp; 선간 {Y('380V')}",
             trap="<b>함정</b> 선간전압은 위상도 30° 앞서요"),
        dict(title="Δ결선", sub="부하가 선과 선 사이에 바로 걸려요", visual=delta,
             formula="V_선 = V_상 &nbsp;·&nbsp; I_선 = √3 I_상",
             ex=f"Y는 {Y('전압')}에 √3, Δ는 {Y('전류')}에 √3",
             trap="<b>기억</b> Y ⇄ Δ 부하 변환은 Z_Y = Z_Δ / 3"),
        dict(title="3상 전력", sub="결선 상관없이 선 값으로 한 줄", visual=star(),
             formula="P = √3 V_L I_L cos θ",
             ex=f"예) 380V, 10A, 역률 1 &nbsp;→&nbsp; {Y('약 6.58kW')}",
             trap="<b>함정</b> 상 값을 넣으면 3 V_상 I_상 cos θ. √3이랑 섞지 말기"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('120°')} 세 상 합 = 0",
        f"{Y('Y')} 전압 √3배 (220 → 380V)",
        f"{Y('Δ')} 전류 √3배",
        f"{Y('P = √3 V_L I_L cosθ')}"]),
)

CAPTION = """전기전자 주목⚡ 전선 3가닥으로 공장이 돌아가는 이유
120°씩 어긋난 세 파형은 더하면 0. 그래서 돌아오는 선이 필요 없어요.
Y결선·Δ결선 √3 위치랑 3상 전력 공식까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #3상교류 #전력공학 #전기전자 #공대생"""
