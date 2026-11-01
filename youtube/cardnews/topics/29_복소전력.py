from cards import *

def tri(p=3, q=4, k=90, ox=230, oy=340, note=True):
    x2, y2 = ox + p * k, oy - q * k
    s = (f'<polygon points="{ox},{oy} {x2},{oy} {x2},{y2}" fill="rgba(246,195,67,.07)" stroke="none"/>' +
         arrow(ox, oy, x2, oy, BLUE, 6) + arrow(x2, oy, x2, y2, GRN, 6) + arrow(ox, oy, x2, y2, YEL, 7) +
         t((ox + x2) / 2, oy + 54, "P 유효전력 [W]", "lbB") +
         t(x2 + 20, (oy + y2) / 2 + 12, "Q 무효전력 [VAR]", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"') +
         t((ox + x2) / 2 - 40, (oy + y2) / 2 - 10, "S [VA]", "lbY", "end") +
         f'<path d="M{ox+70},{oy} A70,70 0 0 0 {ox+70*p/math.hypot(p,q):.1f},{oy-70*q/math.hypot(p,q):.1f}" fill="none" stroke="{W}" stroke-width="4"/>' +
         t(ox + 92, oy - 22, "θ", "lb", "start"))
    return svg(s, 400)

ZC = svg(vsrc(170, 90, 330, ac=True) + wire((170, 90), (620, 90), (620, 150)) + box(560, 150, 120, 120, "") +
         t(620, 222, "6+j8Ω", "lbY") + wire((620, 270), (620, 330), (170, 330)) +
         t(120, 222, "100V", "lb", "end") + arrow(300, 60, 420, 60, BLUE) + t(360, 40, "I", "lbB"), 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="전력이 세 개라고?", line2="P, Q, S 한 번에", sub="복소전력, 직각삼각형 하나로 정리", visual=tri(),
               chips=["세 전력", "복소전력", "전력 삼각형", "계산 예"]),
    cards=[
        dict(title="세 전력", sub="일하는 P, 오가기만 하는 Q, 둘을 합친 S", visual=tri(),
             formula="P = VI cosθ &nbsp;·&nbsp; Q = VI sinθ",
             ex=f"θ = 전압과 전류의 {Y('위상차')}",
             trap="<b>함정</b> 단위가 다 달라요. S는 W가 아니라 VA"),
        dict(title="복소전력", sub="P와 Q를 복소수 하나에 담기", visual=tri(),
             formula="S = V I* = P + jQ",
             ex=f"전류에 {Y('켤레(*)')}를 붙여야 각도가 θ_v − θ_i",
             trap="<b>함정</b> V × I 그대로 곱하면 각도가 더해져서 틀려요"),
        dict(title="전력 삼각형", sub="빗변 S, 밑변 P, 높이 Q", visual=tri(),
             formula="S² = P² + Q²",
             ex=f"예) P = 3kW, Q = 4kVAR &nbsp;→&nbsp; {Y('S = 5kVA')}",
             trap="<b>기억</b> 코일(유도성) 부하는 Q &gt; 0, 콘덴서(용량성)는 Q &lt; 0"),
        dict(title="계산 예", sub="100V(실효값)에 6 + j8Ω 부하", visual=ZC,
             formula="S = 600 + j800 VA",
             ex=f"|Z| = 10Ω → I = 10A, {Y('P = I²R = 600W')} ✓",
             trap="<b>함정</b> 실효값으로 계산. 최대값을 쓰면 ½을 곱해요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('P')} [W] 일하는 전력",
        f"{Y('Q')} [VAR] 오가기만 하는 전력",
        f"{Y('S = VI* = P + jQ')} [VA]",
        f"{Y('S² = P² + Q²')}"]),
)

CAPTION = """전기전자 주목⚡ 전력이 세 개라고요?
일하는 P, 오가기만 하는 Q, 둘을 합친 S. 직각삼각형 하나면 정리돼요.
복소전력 S = VI* 에서 켤레를 붙이는 이유랑 계산 예까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #복소전력 #무효전력 #전기전자 #공대생"""
