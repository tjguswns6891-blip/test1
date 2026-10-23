from cards import *

def opamp(x=380):
    return (f'<polygon points="{x},110 {x},310 {x+190},210" fill="rgba(90,162,255,.08)" stroke="{W}" stroke-width="5" stroke-linejoin="round"/>'
            + t(x + 26, 162, "−", "lbY") + t(x + 26, 284, "+", "lbY"))

rules = svg(opamp() + wire((200, 150), (380, 150)) + wire((200, 270), (380, 270)) + wire((570, 210), (760, 210)) + term(760, 210) +
            t(190, 162, "V₋", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{W}"') +
            t(190, 284, "V₊", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{W}"') + t(780, 222, "출력", "lb", "start") +
            t(290, 220, "같은 전압", "lbB") + t(290, 360, "전류 0", "lbB"))

def fb():
    return wire((330, 150), (330, 50)) + res(330, 50, 640, 50) + wire((640, 50), (640, 210)) + dot(330, 150) + dot(640, 210)

inv = svg(opamp() + fb() + term(110, 150) + res(110, 150, 380, 150) + wire((380, 270), (330, 270)) + ground(330, 270) +
          wire((570, 210), (780, 210)) + term(780, 210) + t(110, 115, "V_in") + t(230, 115, "1kΩ") + t(485, 30, "10kΩ") +
          t(780, 260, "V_out", "lb"), 400)
noninv = svg(opamp() + fb() + term(110, 270) + wire((110, 270), (380, 270)) + res(150, 150, 380, 150) + ground(150, 150) +
             wire((570, 210), (780, 210)) + term(780, 210) + t(110, 320, "V_in") + t(250, 115, "1kΩ") + t(485, 30, "9kΩ") +
             t(780, 260, "V_out", "lb"), 400)

X0, Y0 = 120, 210
sat = svg(axes(X0, Y0, 30, 720, 170, 170, "t", "") +
          curve(lambda x: max(-2.6, min(2.6, -4 * math.sin(x))), 0, 6.28, X0, Y0, 110, 60, YEL) +
          curve(lambda x: -4 * math.sin(x), 0, 6.28, X0, Y0, 110, 60, DIM, 3, dash="10 10") +
          f'<line x1="{X0}" y1="{Y0-156}" x2="{X0+700}" y2="{Y0-156}" stroke="#ff6b61" stroke-width="3" stroke-dasharray="6 8"/>' +
          f'<line x1="{X0}" y1="{Y0+156}" x2="{X0+700}" y2="{Y0+156}" stroke="#ff6b61" stroke-width="3" stroke-dasharray="6 8"/>' +
          t(X0 + 700, Y0 - 170, "+15V", "lbC", "end").replace('class="lbC"', 'class="lbC" fill="#ff6b61"') +
          t(X0 + 700, Y0 + 196, "−15V", "lbC", "end").replace('class="lbC"', 'class="lbC" fill="#ff6b61"'), 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="연산증폭기,", line2="두 줄이면 끝", sub="가상 단락 하나로 증폭기 공식이 다 나와요", visual=rules,
               chips=["두 규칙", "반전", "비반전", "포화"]),
    cards=[
        dict(title="이상적 op amp 두 규칙", sub="음의 피드백이 걸려 있으면 이 두 줄로 다 풀려요", visual=rules,
             formula="V₊ = V₋ &nbsp;·&nbsp; 입력 전류 = 0",
             ex=f"앞의 것이 {Y('가상 단락')}, 뒤의 것이 입력 저항 무한대",
             trap="<b>함정</b> 피드백이 출력→(−)로 와야 성립. 없으면 비교기예요"),
        dict(title="반전 증폭기", sub="입력이 (−) 쪽, 출력은 부호가 뒤집혀요", visual=inv,
             formula=f"V_out = −{F('R_f', 'R_in')} V_in",
             ex=f"예) −{F('10k', '1k')} × 0.5V = {Y('−5V')}",
             trap="<b>왜?</b> V₋ = 0V(가상 접지) → 1kΩ 전류가 전부 10kΩ로"),
        dict(title="비반전 증폭기", sub="입력이 (+) 쪽, 부호 그대로", visual=noninv,
             formula=f"V_out = (1 + {F('R_f', 'R_g')}) V_in",
             ex=f"예) (1 + {F('9k', '1k')}) × 0.5V = {Y('5V')}",
             trap="<b>함정</b> 이득은 항상 1 이상. 1배짜리가 전압 폴로어"),
        dict(title="포화", sub="출력은 전원 전압을 못 넘어요", visual=sat,
             formula="|V_out| ≤ 전원 전압 (±15V)",
             ex=f"예) 이득 −10 × 2V = −20V &nbsp;→&nbsp; {Y('−15V 근처에서 잘림')}",
             trap="<b>함정</b> 공식 답이 전원보다 크면 그대로 쓰면 안 돼요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('V₊ = V₋')}, 입력 전류 0",
        f"{Y('반전')} −R_f / R_in",
        f"{Y('비반전')} 1 + R_f / R_g",
        f"{Y('포화')} 전원 전압이 천장"]),
)

CAPTION = """전기전자 주목⚡ 연산증폭기, 규칙 두 줄이면 끝나요
V₊ = V₋, 입력 전류 0. 이것만으로 반전·비반전 공식이 다 나와요.
시험에 꼭 나오는 포화 함정까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #연산증폭기 #opamp #전기전자 #공대생"""
