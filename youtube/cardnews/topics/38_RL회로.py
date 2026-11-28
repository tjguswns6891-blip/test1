from cards import *

def sw(x1, y, x2, closed=True):
    a = (x2, y) if closed else (x2 - 10, y - 40)
    return dot(x1, y) + f'<line x1="{x1}" y1="{y}" x2="{a[0]}" y2="{a[1]}" class="w"/>' + term(x2, y)

def ckt(closed=True):
    return svg(vsrc(150, 80, 340) + wire((150, 80), (240, 80)) + sw(240, 80, 330, closed) + res(330, 80, 560, 80) + wire((560, 80), (680, 80)) + ind(680, 80, 680, 340) +
         wire((680, 340), (150, 340)) + t(110, 222, "10V", "lb", "end") + t(445, 45, "R 100Ω") + t(720, 222, "L 10mH", "lb", "start") + t(285, 140, "t = 0", "lbS"), 400)
ck = ckt()

X0, Y0 = 110, 340
def rise(v=False):
    f = (lambda x: math.exp(-x)) if v else (lambda x: 1 - math.exp(-x))
    s = axes(X0, Y0, 20, 720, 300, 20, "t", "v_L" if v else "i")
    s += f'<line x1="{X0}" y1="{Y0-260}" x2="{X0+700}" y2="{Y0-260}" stroke="{DIM}" stroke-width="3" stroke-dasharray="8 8"/>'
    s += curve(f, 0, 5, X0, Y0, 135, 260, YEL if not v else GRN, 6)
    y = Y0 - 260 * f(1)
    s += f'<line x1="{X0+135}" y1="{Y0}" x2="{X0+135}" y2="{y:.0f}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 8"/>' + dot(X0 + 135, y, BLUE)
    s += t(X0 + 135, Y0 + 40, "τ", "lbS") + t(X0 + 155, y + (40 if v else -14), "36.8%" if v else "63.2%", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    s += t(X0 + 690, Y0 - 274, "V" if v else "V/R", "lbS", "end")
    return svg(s, 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="코일은 전류가", line2="갑자기 못 바뀌어요", sub="RL 회로, 시정수 τ = L/R", visual=rise(),
               chips=["시정수", "전류 상승", "코일 전압", "끊는 순간"]),
    cards=[
        dict(title="시정수", sub="RL 회로가 얼마나 빨리 변하는지", visual=ck,
             formula=f"τ = {F('L', 'R')}",
             ex=f"예) L = 10mH, R = 100Ω &nbsp;→&nbsp; {Y('τ = 0.1ms')}",
             trap="<b>함정</b> RC는 곱하기(RC), RL은 나누기(L/R)"),
        dict(title="전류 상승", sub="스위치를 켜면 전류가 천천히 차올라요", visual=rise(),
             formula="i(t) = (V/R)(1 − e<sup>−t/τ</sup>)",
             ex=f"예) 10V, 100Ω → 최종 0.1A, τ 뒤 {Y('63mA')}",
             trap="<b>기억</b> 직류로 오래 지나면 코일은 그냥 선(단락)"),
        dict(title="코일 전압", sub="켜는 순간 전압을 코일이 다 받아요", visual=rise(True),
             formula="v_L(t) = V e<sup>−t/τ</sup>",
             ex=f"켜는 순간 {Y('v_L = V')}, 시간이 지나면 0",
             trap="<b>함정</b> 켜는 순간 코일은 개방처럼, 오래 지나면 단락처럼"),
        dict(title="끊는 순간", sub="흐르던 전류를 갑자기 0으로 만들면?", visual=ckt(False),
             formula=f"v = L {F('di', 'dt')}",
             ex=f"di/dt가 엄청 커져서 {Y('큰 역기전력')} (스파크)",
             trap="<b>그래서</b> 릴레이 코일엔 환류 다이오드를 달아요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('τ = L / R')}",
        f"전류는 {Y('1 − e<sup>−t/τ</sup>')} 꼴로 상승",
        f"켜는 순간 개방, 오래 지나면 {Y('단락')}",
        f"갑자기 끊으면 {Y('역기전력')}"]),
)

CAPTION = """전기전자 주목⚡ 코일은 전류가 갑자기 못 바뀌어요
RL 회로의 시정수는 τ = L/R. RC랑 반대로 나눗셈이에요.
전류 상승, 코일 전압, 스위치를 끊을 때 스파크가 튀는 이유까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #RL회로 #과도응답 #전기전자 #공대생"""
