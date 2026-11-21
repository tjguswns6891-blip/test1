from cards import *

X0, Y0 = 120, 330
def jump():
    s = axes(X0 + 340, Y0, 360, 380, 290, 20, "t", "")
    s += t(X0 + 340, Y0 + 40, "0", "lbS")
    s += f'<path d="M{X0},{Y0-200} L{X0+340},{Y0-200}" stroke="{YEL}" stroke-width="6" fill="none"/>'
    s += curve(lambda x: 2 * math.exp(-x), 0, 3, X0 + 340, Y0, 120, 100, YEL, 6)
    s += t(X0 + 20, Y0 - 220, "v_C 이어짐", "lbY", "start")
    s += f'<path d="M{X0},{Y0-60} L{X0+340},{Y0-60} L{X0+340},{Y0-270}" stroke="#ff6b61" stroke-width="5" fill="none" stroke-dasharray="12 8"/>'
    s += t(X0 + 360, Y0 - 250, "i_C 는 튈 수 있음", "lbC", "start").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    return svg(s, 400)

def cc(lval="10V", ind=False):
    from cards import ind as L
    part = L(560, 80, 560, 340) if ind else cap(560, 80, 560, 340)
    return svg(vsrc(150, 80, 340) + wire((150, 80), (280, 80)) + res(280, 80, 560, 80) + part + wire((560, 340), (150, 340)) + dot(560, 80) + dot(560, 340) +
               t(110, 222, "10V", "lb", "end") + t(420, 45, "5Ω" if ind else "R") + t(610, 222, "i_L = 2A" if ind else "v_C = 10V", "lbY", "start") +
               t(450, 395, "스위치 바뀌기 직전 (0⁻), 오래 지난 상태", "lbS"), 420)

steps = ('<div style="display:flex;flex-direction:column;gap:22px;font-size:44px">'
         f'<div>{Y("①")} 0⁻ : 바뀌기 전 회로에서 v_C, i_L</div>'
         f'<div>{Y("②")} 0⁺ : 그 값 그대로 이어받기</div>'
         f'<div>{Y("③")} ∞ : 바뀐 뒤 오래 지난 값</div>'
         f'<div>{Y("④")} τ : 바뀐 뒤 회로에서 구하기</div></div>')

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="스위치 바뀐 순간,", line2="뭐가 그대로일까", sub="0⁻ → 0⁺ 연속 조건으로 초기값 구하기", visual=jump(),
               chips=["연속 조건", "C 초기값", "L 초기값", "풀이 순서"]),
    cards=[
        dict(title="연속 조건", sub="C 전압과 L 전류는 순간적으로 못 변해요", visual=jump(),
             formula="v_C(0⁺) = v_C(0⁻) &nbsp;·&nbsp; i_L(0⁺) = i_L(0⁻)",
             ex=f"갑자기 바뀌려면 {Y('무한대 전류·전압')}이 필요해서",
             trap="<b>함정</b> C 전류, L 전압은 순간적으로 튈 수 있어요"),
        dict(title="C 초기값", sub="직류로 오래 두면 C는 끊긴 선(개방)", visual=cc(),
             formula="0⁻ 에서 C = 개방",
             ex=f"예) 10V로 충분히 충전 &nbsp;→&nbsp; {Y('v_C(0⁺) = 10V')}",
             trap="<b>기억</b> 0⁺ 순간 C는 그 전압의 전압원처럼 보면 돼요"),
        dict(title="L 초기값", sub="직류로 오래 두면 L은 그냥 선(단락)", visual=cc(ind=True),
             formula="0⁻ 에서 L = 단락",
             ex=f"예) 10V, 5Ω 직렬 &nbsp;→&nbsp; {Y('i_L(0⁺) = 2A')}",
             trap="<b>기억</b> 0⁺ 순간 L은 그 전류의 전류원처럼 보면 돼요"),
        dict(title="풀이 순서", sub="1차 회로 문제는 이 네 개면 끝", visual=steps,
             formula="x(0⁺), x(∞), τ → 만능 공식",
             ex=f"x(t) = x(∞) + [x(0⁺) − x(∞)] e<sup>−t/τ</sup>",
             trap="<b>함정</b> τ는 스위치가 바뀐 '뒤' 회로로 구해요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('v_C, i_L')}은 0⁻ = 0⁺",
        f"직류 오래 → C {Y('개방')}, L {Y('단락')}",
        f"0⁺ 에서 C는 전압원, L은 전류원",
        f"{Y('x(0⁺), x(∞), τ')} → 만능 공식"]),
)

CAPTION = """전기전자 주목⚡ 스위치가 바뀐 순간, 뭐가 그대로일까?
콘덴서 전압과 코일 전류는 순간적으로 못 바뀌어요. 이것 하나로 초기값이 나와요.
C·L 초기값 예제랑 1차 회로 풀이 순서까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #과도응답 #초기조건 #전기전자 #공대생"""
