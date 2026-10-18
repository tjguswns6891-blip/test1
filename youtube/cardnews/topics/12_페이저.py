from cards import *

X0, Y0, S = 330, 230, 26
def plane(*vs, extra=""):
    s = axes(X0, Y0, 240, 330, 200, 180, "실수", "허수")
    for x, y, c, lab in vs:
        s += vec(X0, Y0, S, x, y, c, lab, w=7)
    return svg(s + extra, 430)

ph = plane((8.66, 5, YEL, "10∠30°"), extra=f'<path d="M{X0+90},{Y0} A90,90 0 0 0 {X0+78},{Y0-45}" fill="none" stroke="{BLUE}" stroke-width="4"/>' + t(X0 + 120, Y0 - 12, "30°", "lbB"))
imp = plane((7, 0, W, ""), (0, 6, GRN, ""), (0, -6, PUR, ""), extra=t(X0 + 190, Y0 - 16, "R", "lb") + t(X0 + 20, Y0 - 110, "jωL", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"') + t(X0 + 20, Y0 + 130, "1/jωC", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{PUR}"'))
calc = plane((7, 7, YEL, "Z = 10 + j10"), (7, 0, W, ""), extra=t(X0 + 130, Y0 - 40, "45°", "lbB"))
lag = svg(axes(90, 210, 20, 760, 170, 170, "t", "") + curve(lambda x: math.sin(x), 0, 12, 90, 210, 60, 140, YEL) +
          curve(lambda x: math.sin(x - math.pi / 2), 0, 12, 90, 210, 60, 140, GRN) +
          t(170, 60, "v", "lbY") + t(270, 60, "i (인덕터)", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"'), 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="페이저,", line2="아직도 외우세요?", sub="사인파를 화살표 하나로, 미분을 곱셈으로", visual=ph,
               chips=["페이저", "임피던스", "계산", "위상"]),
    cards=[
        dict(title="페이저", sub="같은 주파수 사인파는 크기 + 각도만 있으면 돼요", visual=ph,
             formula="10 cos(ωt + 30°) → 10∠30°",
             ex=f"화살표 길이 = {Y('크기')}, 각도 = {Y('위상')}",
             trap="<b>조건</b> 주파수가 다른 신호끼리는 페이저로 못 더해요"),
        dict(title="임피던스", sub="R, L, C를 전부 복소수 저항으로", visual=imp,
             formula=f"Z_R = R &nbsp;·&nbsp; Z_L = jωL &nbsp;·&nbsp; Z_C = {F('1', 'jωC')}",
             ex=f"예) ω = 1000, 10mH → {Y('j10Ω')}, 100μF → {Y('−j10Ω')}",
             trap="<b>함정</b> 1/j = −j. 커패시터는 아래쪽(−j)"),
        dict(title="계산", sub="미분방정식 대신 복소수 나눗셈 한 번", visual=calc,
             formula=f"I = {F('10∠0°', '14.1∠45°')} = 0.71∠−45° A",
             ex="R 10Ω + L j10Ω → Z = 10 + j10 = 14.1∠45°",
             trap="<b>팁</b> 곱셈·나눗셈은 극형식(∠), 덧셈은 직교형식(a + jb)"),
        dict(title="위상", sub="인덕터는 전류가 늦고, 커패시터는 전류가 빨라요", visual=lag,
             formula="L: 전류 90° 늦음 &nbsp;·&nbsp; C: 전류 90° 빠름",
             ex=f"외우는 법 {Y('CIVIL')}: C는 I가 먼저, L은 V가 먼저",
             trap="<b>함정</b> 저항은 위상차 0, 전압·전류가 같이 움직여요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('페이저')} = 크기∠각도",
        f"{Y('Z_L = jωL')}, {Y('Z_C = 1/jωC')}",
        f"{Y('옴의 법칙')} 그대로, 복소수로",
        f"{Y('CIVIL')} 위상 순서"]),
)

CAPTION = """전기전자 주목⚡ 페이저, 아직도 외우세요?
사인파는 크기와 각도만 있으면 화살표 하나로 끝나요.
임피던스, 복소수 계산, 위상 외우는 법까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #페이저 #교류회로 #전기전자 #공대생"""
