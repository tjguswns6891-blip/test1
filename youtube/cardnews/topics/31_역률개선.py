from cards import *

def tris(after=True, ox=130, oy=340, k=48):
    s = ""
    x2 = ox + 8 * k
    s += arrow(ox, oy, x2, oy, BLUE, 6) + t((ox + x2) / 2, oy + 54, "P = 8kW (그대로)", "lbB")
    s += arrow(x2, oy, x2, oy - 6 * k, "#ff6b61", 5) + arrow(ox, oy, x2, oy - 6 * k, DIM, 5)
    s += t(x2 + 20, oy - 6 * k + 30, "Q_L 6kVAR", "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    s += t(ox + 110, oy - 3 * k - 30, "전 10kVA", "lbS", "end")
    if after:
        s += f'<line x1="{x2+210}" y1="{oy-6*k}" x2="{x2+210}" y2="{oy-k*1.5:.0f}" stroke="{GRN}" stroke-width="6" marker-end="url(#ag)"/>'
        s += t(x2 + 230, oy - 3 * k, "Q_C 상쇄", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"')
        s += arrow(ox, oy, x2, oy - k * 1.5, YEL, 7) + t(x2 + 20, oy - k * 1.5 + 20, "후 S ↓", "lbY", "start")
    return svg(s, 400)

ck = svg(vsrc(150, 80, 340, ac=True) + wire((150, 80), (680, 80)) + wire((150, 340), (680, 340)) +
         res(680, 80, 680, 210) + ind(680, 210, 680, 340) + cap(430, 80, 430, 340) + dot(430, 80) + dot(430, 340) +
         t(720, 220, "모터 (R + L)", "lb", "start") + t(480, 222, "C 추가", "lbY", "start"), 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="콘덴서 하나로", line2="전기요금 줄이기", sub="역률 개선, C가 Q를 대신 공급해요", visual=ck,
               chips=["원리", "필요한 Q_C", "C 구하기", "과보상 주의"]),
    cards=[
        dict(title="원리", sub="부하와 병렬로 C를 달아 지상 Q를 상쇄", visual=tris(),
             formula="Q_후 = Q_L − Q_C",
             ex=f"P는 그대로, {Y('S와 전류만')} 줄어요",
             trap="<b>함정</b> 직렬로 달면 부하 전압이 바뀌어요. 항상 병렬"),
        dict(title="필요한 Q_C", sub="역률을 cosθ₁ → cosθ₂ 로 올리려면", visual=tris(),
             formula="Q_C = P (tanθ₁ − tanθ₂)",
             ex=f"예) 8kW, 0.8 → 1 &nbsp;:&nbsp; 8 × 0.75 = {Y('6kVAR')}",
             trap="<b>기억</b> 역률 0.8 ↔ tanθ = 0.75"),
        dict(title="C 구하기", sub="Q_C = ωCV² 를 C로 정리", visual=ck,
             formula=f"C = {F('Q_C', 'ω V²')}",
             ex=f"예) 6kVAR, 220V, 60Hz &nbsp;→&nbsp; {Y('약 329μF')}",
             trap="<b>함정</b> V는 실효값, ω = 2πf (60Hz면 377)"),
        dict(title="과보상 주의", sub="보통 1이 아니라 0.9~0.95가 목표", visual=tris(),
             formula="Q_C &gt; Q_L → 진상",
             ex=f"C가 너무 크면 역률이 {Y('진상으로')} 다시 떨어져요",
             trap="<b>함정</b> 부하가 줄면 같은 C로도 과보상. 그래서 자동 조절기를 써요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('병렬 C')}가 지상 Q를 상쇄",
        f"{Y('Q_C = P(tanθ₁ − tanθ₂)')}",
        f"{Y('C = Q_C / ωV²')}",
        f"목표 {Y('0.9~0.95')}, 과보상 주의"]),
)

CAPTION = """전기전자 주목⚡ 콘덴서 하나로 전기요금 줄이기
모터 옆에 C를 병렬로 달면 P는 그대로인데 전류가 줄어요.
필요한 Q_C, C 용량 계산, 과보상 주의까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #역률개선 #전력공학 #전기전자 #공대생"""
