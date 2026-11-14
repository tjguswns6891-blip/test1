from cards import *

def parts(focus=""):
    c, l = (YEL if focus != "l" else DIM), (BLUE if focus != "c" else DIM)
    s = (f'<line x1="200" y1="60" x2="200" y2="170" stroke="{c}" stroke-width="6"/>'
         f'<line x1="140" y1="170" x2="260" y2="170" stroke="{c}" stroke-width="8"/><line x1="140" y1="210" x2="260" y2="210" stroke="{c}" stroke-width="8"/>'
         f'<line x1="200" y1="210" x2="200" y2="320" stroke="{c}" stroke-width="6"/>')
    for x in (160, 200, 240):
        s += f'<line x1="{x}" y1="178" x2="{x}" y2="202" stroke="{c}" stroke-width="3" marker-end="url(#ay)"/>'
    s += t(200, 380, "C : 전기장", "lbC").replace('class="lbC"', f'class="lbC" fill="{c}"') + t(300, 200, "½CV²", "lbY", "start")
    s += ind(640, 60, 640, 320, 5, 160).replace('class="w"', f'fill="none" stroke="{l}" stroke-width="6"')
    for r in (70, 110):
        s += f'<ellipse cx="640" cy="190" rx="{r}" ry="{r*1.25:.0f}" fill="none" stroke="{l}" stroke-width="3" stroke-dasharray="8 8"/>'
    s += t(640, 380, "L : 자기장", "lbC").replace('class="lbC"', f'class="lbC" fill="{l}"') + t(780, 200, "½LI²", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    return svg(s, 400)

X0, Y0 = 110, 340
quad = svg(axes(X0, Y0, 20, 720, 300, 20, "V", "W") + curve(lambda x: x * x, 0, 2, X0, Y0, 340, 70, YEL, 6) +
           dot(X0 + 340, Y0 - 70, BLUE) + dot(X0 + 680, Y0 - 280, BLUE) + t(X0 + 360, Y0 - 82, "V → 1배", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"') +
           t(X0 + 660, Y0 - 290, "2V → 4배", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{BLUE}"'), 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="콘덴서와 코일에", line2="숨어 있는 에너지", sub="½CV², ½LI² 두 줄이면 끝", visual=parts(),
               chips=["C 에너지", "L 에너지", "R과 차이", "활용"]),
    cards=[
        dict(title="C 에너지", sub="전압을 걸면 전기장에 에너지가 쌓여요", visual=quad,
             formula="W = ½ C V²",
             ex=f"예) 100μF, 10V &nbsp;→&nbsp; {Y('5mJ')}",
             trap="<b>함정</b> 전압 2배면 에너지는 4배 (제곱!)"),
        dict(title="L 에너지", sub="전류가 흐르면 자기장에 에너지가 쌓여요", visual=parts("l"),
             formula="W = ½ L I²",
             ex=f"예) 10mH, 2A &nbsp;→&nbsp; {Y('20mJ')}",
             trap="<b>기억</b> C는 전압, L은 전류의 제곱. 짝을 맞춰 외우기"),
        dict(title="R은 다르다", sub="저항은 저장하지 않고 바로 열로 바꿔요", visual=parts(),
             formula="P = I²R (소모)",
             ex=f"이상적인 L, C의 평균 전력은 {Y('0')}",
             trap="<b>함정</b> L, C는 받았다가 돌려줄 뿐. 소모는 R에서만"),
        dict(title="어디에 쓰나", sub="천천히 모았다가 한 번에 쓰기", visual=parts(),
             formula="카메라 플래시 · 부스트 컨버터",
             ex=f"플래시는 C에 모은 에너지를 {Y('한 번에')} 터뜨려요",
             trap="<b>주의</b> 큰 콘덴서는 전원을 꺼도 전압이 남아 있어요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('W_C = ½CV²')} 전기장",
        f"{Y('W_L = ½LI²')} 자기장",
        f"전압·전류 2배 → 에너지 {Y('4배')}",
        f"소모는 {Y('R만')}, L·C는 저장"]),
)

CAPTION = """전기전자 주목⚡ 콘덴서와 코일에 숨어 있는 에너지
C는 ½CV², L은 ½LI². 전압이나 전류가 2배면 에너지는 4배예요.
숫자 예제랑 저항과 다른 점, 실제로 어디에 쓰는지까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #콘덴서 #인덕터 #전기전자 #공대생"""
