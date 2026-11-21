from cards import *

def opamp(x=380):
    return (f'<polygon points="{x},110 {x},310 {x+190},210" fill="rgba(90,162,255,.08)" stroke="{W}" stroke-width="5" stroke-linejoin="round"/>'
            + t(x + 26, 162, "−", "lbY") + t(x + 26, 284, "+", "lbY"))

ck = svg(opamp() + wire((380, 150), (330, 150), (330, 50), (640, 50), (640, 210)) + dot(640, 210) + term(120, 270) + wire((120, 270), (380, 270)) +
         wire((570, 210), (780, 210)) + term(780, 210) + t(120, 320, "V_in") + t(780, 260, "V_out = V_in", "lbY") + t(485, 30, "그냥 선", "lbS"), 400)

def load(buf):
    s = vsrc(90, 80, 340) + wire((90, 80), (160, 80)) + res(160, 80, 300, 80, body=80) + wire((300, 80), (300, 80)) + res(300, 80, 300, 340) + dot(300, 80)
    s += t(60, 222, "10V", "lb", "end") + t(230, 45, "10k") + t(270, 222, "10k", "lb", "end") + wire((90, 340), (820, 340))
    if buf:
        s += (f'<polygon points="420,130 420,250 540,190" fill="rgba(90,162,255,.08)" stroke="{BLUE}" stroke-width="5"/>' + wire((300, 80), (400, 80), (400, 220), (420, 220)) +
              wire((540, 190), (700, 190)) + t(480, 290, "버퍼", "lbB"))
    else:
        s += wire((300, 80), (700, 80), (700, 190))
    s += res(700, 190, 700, 340) + t(730, 270, "1kΩ", "lb", "start") + t(760, 160, "5V" if buf else "0.83V", "lbY" if buf else "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    return svg(f'<g transform="translate(40,0)">{s}</g>', 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="1배 증폭기를", line2="왜 쓸까", sub="전압 팔로워, 버퍼의 진짜 역할", visual=ck,
               chips=["회로", "입출력 저항", "부하 효과", "활용"]),
    cards=[
        dict(title="회로", sub="출력을 (−)에 바로 연결", visual=ck,
             formula="V_out = V_in",
             ex=f"비반전 증폭기에서 {Y('R_f = 0, R₁ = ∞')}",
             trap="<b>기억</b> 전압 이득은 1이지만 하는 일이 있어요"),
        dict(title="입출력 저항", sub="앞에서는 전류를 안 빼가고, 뒤에는 힘 있게", visual=ck,
             formula="R_in ≈ ∞ &nbsp;·&nbsp; R_out ≈ 0",
             ex=f"전압은 1배, {Y('전류(전력)')}는 크게 줄 수 있어요",
             trap="<b>함정</b> 전압 이득 1 ≠ 전력 이득 1"),
        dict(title="부하 효과", sub="10V를 10k·10k로 나눈 5V에 1kΩ을 달면", visual=load(False),
             formula="버퍼 없음 → 0.83V",
             ex=f"1k가 10k와 병렬이 돼서 {Y('전압이 무너져요')}",
             trap="<b>함정</b> 분배 공식은 부하가 없을 때만 맞아요"),
        dict(title="어디에 쓰나", sub="사이에 버퍼 하나 끼우면", visual=load(True),
             formula="버퍼 있음 → 5V 그대로",
             ex=f"센서 출력, ADC 입력, {Y('필터 단 사이')}",
             trap="<b>기억</b> 출력 저항이 큰 신호원 뒤에는 꼭 버퍼"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('V_out = V_in')} (이득 1)",
        f"{Y('R_in ∞, R_out 0')}",
        f"부하가 붙어도 {Y('전압 유지')}",
        f"신호원과 부하 {Y('사이 완충')}"]),
)

CAPTION = """전기전자 주목⚡ 1배 증폭기를 왜 쓸까?
전압 팔로워는 전압을 그대로 넘기지만, 앞 회로에서 전류를 안 빼가요.
버퍼가 없으면 5V가 0.83V로 무너지는 예제까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #연산증폭기 #버퍼 #전기전자 #공대생"""
