from cards import *

equiv = svg(box(60, 90, 260, 240, "") + t(190, 205, "복잡한", "lbB") + t(190, 255, "회로", "lbB") +
            wire((320, 130), (380, 130)) + wire((320, 290), (380, 290)) + term(380, 130) + term(380, 290) +
            t(450, 225, "=", "lbB") +
            vsrc(560, 130, 290) + res(560, 130, 790, 130) + wire((560, 290), (790, 290)) + term(790, 130) + term(790, 290) +
            t(505, 222, "V_th", "lbY", "end") + t(675, 95, "R_th", "lbY") +
            t(400, 115, "a") + t(400, 330, "b") + t(810, 115, "a") + t(810, 330, "b"))

def base(short=False):
    src = wire((150, 80), (150, 340)) if short else vsrc(150, 80, 340)
    return (src + res(150, 80, 470, 80) + wire((470, 80), (700, 80)) + res(470, 80, 470, 340) + wire((150, 340), (700, 340)) +
            dot(470, 80) + dot(470, 340) + term(700, 80) + term(700, 340) + t(310, 45, "6Ω") + t(510, 222, "3Ω", anchor="start") +
            t(725, 70, "a", anchor="start") + t(725, 365, "b", anchor="start") + ("" if short else t(70, 222, "12V")))

vth = svg(base() + t(770, 222, "4V", "lbY", "start") + t(760, 160, "+", "lbY") + t(760, 300, "−", "lbY"))
rth = svg(base(True) + t(60, 222, "단락", "lbC").replace('class="lbC"', 'class="lbC" fill="#ff6b61"') +
          arrow(800, 210, 720, 210, BLUE) + t(820, 222, "R?", "lbB", "start").replace('text-anchor="middle"', ""))
pmax = svg(vsrc(150, 80, 340) + res(150, 80, 500, 80) + wire((500, 80), (640, 80)) + res(640, 80, 640, 340) +
           wire((150, 340), (640, 340)) + t(70, 222, "4V") + t(325, 45, "2Ω") + t(680, 222, "R_L = 2Ω", "lbY", "start"))

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="복잡한 회로,", line2="저항 하나로 끝", sub="테브난 등가, 구하는 순서 그대로", visual=equiv,
               chips=["등가 회로", "V_th", "R_th", "최대 전력"]),
    cards=[
        dict(title="테브난 등가", sub="단자 두 개만 보면 어떤 회로든 전압원 + 저항", visual=equiv,
             formula="회로 = V_th + R_th (직렬)",
             ex="부하만 바꿔 가며 계산할 때 제일 빨라요",
             trap="<b>조건</b> 선형 회로만! 다이오드·트랜지스터 들어가면 안 돼요"),
        dict(title="V_th 구하기", sub="부하 떼고, 열린 단자 a–b 전압을 재요", visual=vth,
             formula=f"V_th = 12 × {F('3', '6 + 3')}",
             ex=f"→ {Y('V_th = 4V')} &nbsp;(전압 분배 그대로)",
             trap="<b>함정</b> 부하를 단 채로 구하면 틀려요. 꼭 떼고!"),
        dict(title="R_th 구하기", sub="전원을 끄고 단자에서 들여다본 저항", visual=rth,
             formula=f"R_th = 6 ∥ 3 = {F('6 × 3', '6 + 3')} = 2Ω",
             ex=f"→ 등가 회로는 {Y('4V + 2Ω')}",
             trap="<b>함정</b> 전압원은 단락(선), 전류원은 개방(끊기)"),
        dict(title="최대 전력", sub="부하가 R_th랑 같을 때 전력이 제일 커요", visual=pmax,
             formula=f"P_max = {F('V_th²', '4 R_th')}",
             ex=f"예) {F('4²', '4 × 2')} = {Y('2W')} &nbsp;(R_L = 2Ω일 때)",
             trap="<b>함정</b> 최대 전력일 때 효율은 50%. 효율 최대랑 다른 얘기"),
    ],
    summary=dict(tag="순서대로", rows=[
        f"{Y('①')} 부하 떼기",
        f"{Y('②')} 열린 단자 전압 = V_th",
        f"{Y('③')} 전원 끄고 저항 = R_th",
        f"{Y('④')} 부하 다시 달고 계산"]),
)

CAPTION = """전기전자 주목⚡ 이 복잡한 회로, 저항 하나로 끝납니다
테브난 등가: 단자 두 개만 보면 전압원 하나 + 저항 하나.
V_th, R_th 구하는 순서랑 최대 전력까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #테브난 #전기전자 #공대생 #공대공부"""
