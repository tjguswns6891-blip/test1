from cards import *

rc = svg(vsrc(150, 80, 340) + wire((150, 80), (230, 80)) + term(230, 80) + f'<line x1="236" y1="76" x2="320" y2="40" class="w"/>' +
         term(330, 80) + res(330, 80, 640, 80) + cap(640, 80, 640, 340) + wire((150, 340), (640, 340)) +
         t(70, 222, "10V") + t(280, 30, "t = 0") + t(485, 45, "10kΩ") + t(690, 222, "100μF", anchor="start"))

X0, Y0, SX, SY = 110, 350, 130, 280
def graph(fn, mark, lab):
    return svg(axes(X0, Y0, 20, 720, 310, 20, "t", "") + curve(fn, 0, 5.3, X0, Y0, SX, SY, YEL) +
               f'<line x1="{X0+SX}" y1="{Y0}" x2="{X0+SX}" y2="{Y0-mark*SY}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 8"/>' +
               f'<line x1="{X0}" y1="{Y0-mark*SY}" x2="{X0+SX}" y2="{Y0-mark*SY}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 8"/>' +
               dot(X0 + SX, Y0 - mark * SY, BLUE) + t(X0 + SX + 50, Y0 - mark * SY + 50, lab, "lbB", "start").replace('text-anchor="middle"', "") +
               "".join(t(X0 + SX * k, Y0 + 40, f"{k}τ", "lbS") for k in range(1, 6)), 420)

charge = graph(lambda x: 1 - math.exp(-x), 0.632, "63.2%")
dis = graph(lambda x: math.exp(-x), 0.368, "36.8%")

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="과도응답,", line2="63.2%만 기억하세요", sub="시정수 τ 하나로 충전·방전 끝", visual=charge,
               chips=["시정수", "충전", "방전", "만능 공식"]),
    cards=[
        dict(title="시정수 τ", sub="스위치를 켠 뒤 얼마나 빨리 변하는지 나타내는 시간", visual=rc,
             formula="τ = R × C",
             ex=f"예) 10kΩ × 100μF = {Y('1초')}",
             trap="<b>기억</b> RL 회로는 τ = L / R (R이 분모!)"),
        dict(title="충전", sub="τ 하나 지나면 최종값의 63.2%", visual=charge,
             formula="v(t) = V (1 − e<sup>−t/τ</sup>)",
             ex=f"예) 10V, τ = 1초 &nbsp;→&nbsp; 1초에 {Y('6.32V')}, 5τ면 거의 10V",
             trap="<b>시험</b> \"5τ 지나면 정상 상태\" 로 보는 게 관례"),
        dict(title="방전", sub="τ 하나 지나면 36.8%만 남아요", visual=dis,
             formula="v(t) = V e<sup>−t/τ</sup>",
             ex=f"예) 10V에서 방전 &nbsp;→&nbsp; 1초 뒤 {Y('3.68V')}",
             trap="<b>함정</b> 63.2%는 '변한 양', 36.8%는 '남은 양'"),
        dict(title="만능 공식", sub="시작값, 끝값, τ 세 개만 찾으면 어떤 1차 회로든", visual=charge,
             formula="x(t) = x(∞) + [x(0) − x(∞)] e<sup>−t/τ</sup>",
             ex=f"x(0) = 0, x(∞) = 10V 넣으면 {Y('충전 공식')}",
             trap="<b>함정</b> τ의 R은 C 쪽에서 들여다본 테브난 저항"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('τ = RC')} (RL은 L / R)",
        f"{Y('1τ')} 63.2% 변하고 36.8% 남음",
        f"{Y('5τ')} 면 사실상 끝",
        f"{Y('x(0), x(∞), τ')} 셋만 찾기"]),
)

CAPTION = """전기전자 주목⚡ 과도응답, 63.2%만 기억하세요
시정수 τ = RC가 지나면 최종값의 63.2%, 5τ면 사실상 끝.
충전·방전 그래프랑 만능 공식까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #과도응답 #시정수 #전기전자 #공대생"""
