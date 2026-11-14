from cards import *

X0, Y0 = 110, 340
def bode(hp=False, mark=True):
    f = (lambda x: 10 ** x / math.sqrt(1 + 10 ** (2 * x))) if hp else (lambda x: 1 / math.sqrt(1 + 10 ** (2 * x)))
    s = axes(X0, Y0, 20, 720, 300, 20, "주파수 (로그)", "|H|") + curve(f, -2, 2, X0 + 340, Y0, 170, 270, YEL, 6)
    if mark:
        y = Y0 - 270 / math.sqrt(2)
        s += (f'<line x1="{X0+340}" y1="{Y0}" x2="{X0+340}" y2="{y:.0f}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 8"/>' + dot(X0 + 340, y, BLUE) +
              t(X0 + 360, y - 14, "f_c, 0.707", "lbB").replace('text-anchor="middle"', 'text-anchor="start"'))
    return svg(s, 400)

def ckt(hp=False):
    a = cap(170, 80, 470, 80) if hp else res(170, 80, 470, 80)
    b = res(470, 80, 470, 340) if hp else cap(470, 80, 470, 340)
    return svg(term(170, 80) + term(170, 340) + a + b + wire((170, 340), (700, 340)) + wire((470, 80), (700, 80)) + term(700, 80) + term(700, 340) + dot(470, 80) + dot(470, 340) +
               t(150, 222, "입력", "lb", "end") + t(720, 222, "출력", "lbY", "start") +
               t(320, 45, "C 1μF" if hp else "R 1kΩ") + t(510, 222, "R 1kΩ" if hp else "C 1μF", anchor="start"))

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="저항 하나, 콘덴서 하나로", line2="잡음 걸러내기", sub="RC 필터, 차단 주파수 하나면 끝", visual=bode(),
               chips=["저역 통과", "차단 주파수", "−3dB", "고역 통과"]),
    cards=[
        dict(title="저역 통과 필터", sub="출력을 C 양끝에서 → 낮은 주파수만 통과", visual=ckt(),
             formula=f"H(jω) = {F('1', '1 + jωRC')}",
             ex=f"높은 주파수에선 C가 {Y('거의 선(단락)')} → 출력 0",
             trap="<b>기억</b> 직류(ω = 0)에서 C는 개방 → 그대로 통과"),
        dict(title="차단 주파수", sub="통과와 차단의 경계", visual=bode(),
             formula=f"f_c = {F('1', '2πRC')}",
             ex=f"예) 1kΩ, 1μF &nbsp;→&nbsp; {Y('약 159Hz')}",
             trap="<b>함정</b> ω_c = 1/RC 는 rad/s. Hz로 바꿀 땐 2π로 나누기"),
        dict(title="−3dB 지점", sub="차단 주파수에서 크기는 0.707배", visual=bode(),
             formula="|H| = 1/√2 &nbsp;=&nbsp; −3dB &nbsp;·&nbsp; 위상 −45°",
             ex=f"그 위로는 주파수 10배마다 {Y('−20dB')} (1차 필터)",
             trap="<b>함정</b> 전력은 절반, 전압 크기는 0.707배. 둘 헷갈리지 말기"),
        dict(title="고역 통과 필터", sub="R과 C 자리만 바꾸면 반대가 돼요", visual=ckt(True),
             formula=f"H(jω) = {F('jωRC', '1 + jωRC')}",
             ex=f"차단 주파수 공식은 {Y('똑같이')} 1 / 2πRC",
             trap="<b>팁</b> 출력이 C 양끝 → 저역, R 양끝 → 고역"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('출력 C')} 저역 통과, {Y('출력 R')} 고역 통과",
        f"{Y('f_c = 1/2πRC')}",
        f"{Y('f_c')}에서 0.707배 = −3dB",
        f"{Y('1차')} 10배마다 −20dB"]),
)

CAPTION = """전기전자 주목⚡ 저항 하나, 콘덴서 하나로 잡음을 걸러냅니다
출력을 C에서 따면 저역 통과, R에서 따면 고역 통과.
차단 주파수 1/2πRC랑 −3dB의 의미까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #RC필터 #필터 #전기전자 #공대생"""
