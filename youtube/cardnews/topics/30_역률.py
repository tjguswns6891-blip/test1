from cards import *

def tri(p=8, q=6, k=38, ox=250, oy=330):
    x2, y2 = ox + p * k, oy - q * k
    h = math.hypot(p, q)
    return svg(arrow(ox, oy, x2, oy, BLUE, 6) + arrow(x2, oy, x2, y2, GRN, 6) + arrow(ox, oy, x2, y2, YEL, 7) +
               t((ox + x2) / 2, oy + 54, f"P = {p}kW", "lbB") +
               t(x2 + 20, (oy + y2) / 2 + 12, f"Q = {q}kVAR", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"') +
               t((ox + x2) / 2 - 30, (oy + y2) / 2 - 10, f"S = {h:g}kVA", "lbY", "end") +
               f'<path d="M{ox+70},{oy} A70,70 0 0 0 {ox+70*p/h:.1f},{oy-70*q/h:.1f}" fill="none" stroke="{W}" stroke-width="4"/>' +
               t(ox + 92, oy - 18, "θ", "lb", "start"), 400)

O = (330, 220)
def ph():
    s = axes(*O, 60, 420, 170, 170)
    s += arrow(*O, O[0] + 340, O[1], YEL, 7) + t(O[0] + 350, O[1] - 18, "V", "lbY", "start")
    s += arrow(*O, O[0] + 230, O[1] + 140, BLUE, 6) + t(O[0] + 250, O[1] + 160, "I 지상 (L)", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    s += arrow(*O, O[0] + 230, O[1] - 140, GRN, 6) + t(O[0] + 250, O[1] - 150, "I 진상 (C)", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"')
    return svg(s, 420)

def lines():
    s = ""
    for k, (pf, c) in enumerate(((1.0, GRN), (0.5, "#ff6b61"))):
        y = 110 + k * 190
        i = 8000 / 220 / pf
        s += t(70, y + 12, f"역률 {pf:g}", "lb", "start") + f'<rect x="260" y="{y-24}" width="{i*6:.0f}" height="48" rx="10" fill="{c}" opacity=".85"/>' + t(280 + i * 6, y + 12, f"I ≈ {i:.0f}A", "lb", "start")
    return svg(s + t(450, 400, "같은 8kW, 220V일 때 필요한 전류", "lbS"), 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="같은 일을 해도", line2="전류가 더 드는 이유", sub="역률 cosθ, 낮으면 손해예요", visual=lines(),
               chips=["역률", "지상·진상", "왜 손해일까", "계산 예"]),
    cards=[
        dict(title="역률", sub="공급한 전력(S) 중 실제로 일한 비율", visual=tri(),
             formula=f"pf = cosθ = {F('P', 'S')}",
             ex=f"θ = 전압과 전류의 {Y('위상차')}",
             trap="<b>기억</b> 역률 1 = 저항만 있는 부하"),
        dict(title="지상·진상", sub="전류가 전압보다 늦으면 지상, 빠르면 진상", visual=ph(),
             formula="L 부하 → 지상 &nbsp;·&nbsp; C 부하 → 진상",
             ex=f"공장 모터는 대부분 {Y('L')}이라 지상이에요",
             trap="<b>함정</b> 숫자만으론 몰라요. '0.8 지상'처럼 같이 쓰기"),
        dict(title="왜 손해일까", sub="같은 P를 보내려면 전류가 커져요", visual=lines(),
             formula=f"I = {F('P', 'V cosθ')}",
             ex=f"역률 0.5면 전류 2배 &nbsp;→ 선로 손실 I²R {Y('4배')}",
             trap="<b>그래서</b> 한전은 역률 낮은 곳에 요금을 더 받아요"),
        dict(title="계산 예", sub="P = 8kW, S = 10kVA인 부하", visual=tri(),
             formula=f"cosθ = {F('8', '10')} = 0.8",
             ex=f"Q = √(10² − 8²) = {Y('6kVAR')}",
             trap="<b>기억</b> 역률 0.8이면 sinθ = 0.6. 바로 나오게 외워 두기"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('pf = cosθ = P / S')}",
        f"{Y('지상')} 전류가 늦음 (L), {Y('진상')} 빠름 (C)",
        f"역률 ↓ → {Y('전류 ↑')} → 손실 ↑",
        f"{Y('0.8')} ↔ sinθ 0.6"]),
)

CAPTION = """전기전자 주목⚡ 같은 일을 해도 전류가 더 드는 이유
역률이 0.5면 같은 전력을 보내는 데 전류가 2배, 선로 손실은 4배예요.
지상·진상 구분이랑 0.8 계산 예까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #역률 #전력공학 #전기전자 #공대생"""
