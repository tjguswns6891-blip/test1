from cards import *

def opamp(x=380):
    return (f'<polygon points="{x},110 {x},310 {x+190},210" fill="rgba(90,162,255,.08)" stroke="{W}" stroke-width="5" stroke-linejoin="round"/>'
            + t(x + 26, 162, "−", "lbY") + t(x + 26, 284, "+", "lbY"))

ck = svg(opamp() + wire((330, 150), (330, 50)) + res(330, 50, 640, 50) + wire((640, 50), (640, 210)) + dot(330, 150) + dot(640, 210) +
         term(90, 150) + res(90, 150, 330, 150) + wire((330, 150), (380, 150)) + term(90, 270) + res(90, 270, 330, 270) + wire((330, 270), (380, 270)) +
         dot(330, 270) + res(330, 270, 330, 380, body=70) + ground(330, 380) + wire((570, 210), (780, 210)) + term(780, 210) +
         t(90, 120, "V₁") + t(90, 320, "V₂") + t(210, 120, "R₁") + t(210, 320, "R₁") + t(485, 30, "R_f") + t(360, 345, "R_f", "lb", "start") + t(780, 260, "V_out", "lb"), 430)

X0, Y0 = 90, 210
def noise(diff=False):
    n = lambda x: 0.35 * math.sin(7 * x) + 0.2 * math.sin(13 * x)
    s = axes(X0, Y0, 20, 740, 180, 180, "t", "")
    if diff:
        s += curve(lambda x: 1.2, 0, 6.2, X0, Y0, 115, 70, GRN, 7) + t(X0 + 720, Y0 - 100, "V₂ − V₁ 만 남음", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{GRN}"')
    else:
        s += curve(lambda x: 1.2 + n(x), 0, 6.2, X0, Y0 - 40, 115, 70, YEL, 5) + curve(lambda x: n(x), 0, 6.2, X0, Y0 + 70, 115, 70, BLUE, 5)
        s += t(X0 + 720, 40, "V₂ + 잡음", "lbY", "end") + t(X0 + 720, 405, "V₁ + 같은 잡음", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    return svg(s, 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="두 신호의", line2="차이만 키우기", sub="차동 증폭기, 잡음은 빼고 신호만", visual=noise(),
               chips=["회로", "공식", "공통 잡음", "CMRR"]),
    cards=[
        dict(title="회로", sub="(−)와 (+) 양쪽에 같은 저항 비", visual=ck,
             formula="위아래 모두 R_f / R₁",
             ex=f"(+)쪽은 {Y('전압 분배')}, (−)쪽은 반전 증폭",
             trap="<b>함정</b> 네 저항 비가 어긋나면 잡음이 새어 나와요"),
        dict(title="공식", sub="두 입력의 차에 이득을 곱해요", visual=ck,
             formula=f"V_out = {F('R_f', 'R₁')} (V₂ − V₁)",
             ex=f"예) R_f/R₁ = 10, 1.2V − 1.0V &nbsp;→&nbsp; {Y('2V')}",
             trap="<b>기억</b> V₂ = (+)쪽, V₁ = (−)쪽. 순서 바꾸면 부호가 반대"),
        dict(title="공통 잡음", sub="두 선에 똑같이 탄 잡음은 빼면 0", visual=noise(),
             formula="(V₂ + n) − (V₁ + n) = V₂ − V₁",
             ex=f"긴 센서 선의 {Y('험(60Hz) 잡음')} 제거",
             trap="<b>기억</b> 그래서 측정 장비 입력은 대부분 차동이에요"),
        dict(title="CMRR", sub="차이는 키우고 공통은 얼마나 죽이나", visual=noise(True),
             formula=f"CMRR = {F('A_d', 'A_cm')}",
             ex=f"클수록 잡음 제거를 잘해요 (보통 {Y('dB')}로 표시)",
             trap="<b>함정</b> 저항 오차 1%만 있어도 CMRR이 크게 떨어져요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('V_out = (R_f/R₁)(V₂ − V₁)')}",
        f"공통 잡음은 {Y('빼면 0')}",
        f"네 저항 {Y('비율 맞추기')}",
        f"{Y('CMRR')} 클수록 좋은 차동 증폭기"]),
)

CAPTION = """전기전자 주목⚡ 두 신호의 차이만 키우는 증폭기
두 선에 똑같이 탄 잡음은 빼면 0. 그래서 신호만 남아요.
차동 증폭기 공식, 계산 예, CMRR까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #연산증폭기 #차동증폭기 #전기전자 #공대생"""
