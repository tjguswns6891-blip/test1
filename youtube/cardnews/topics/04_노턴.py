from cards import *

def blackbox():
    return (box(60, 90, 240, 240, "") + t(180, 205, "복잡한", "lbB") + t(180, 255, "회로", "lbB") +
            wire((300, 130), (360, 130)) + wire((300, 290), (360, 290)) + term(360, 130) + term(360, 290))

def norton(x0, i_lab="I_N", r_lab="R_N"):
    return (isrc(x0, 130, 290) + wire((x0, 130), (x0 + 250, 130)) + wire((x0, 290), (x0 + 250, 290)) +
            res(x0 + 130, 130, x0 + 130, 290) + dot(x0 + 130, 130) + dot(x0 + 130, 290) + term(x0 + 250, 130) + term(x0 + 250, 290) +
            t(x0 - 50, 222, i_lab, "lbY", "end") + t(x0 + 165, 222, r_lab, "lbY", "start"))

equiv = svg(blackbox() + t(430, 225, "=", "lbB") + norton(580))

def base(short_ab=False):
    s = (vsrc(150, 80, 340) + res(150, 80, 470, 80) + wire((470, 80), (700, 80)) + res(470, 80, 470, 340) + wire((150, 340), (700, 340)) +
         dot(470, 80) + dot(470, 340) + t(70, 222, "12V") + t(310, 45, "6Ω") + t(510, 222, "3Ω", anchor="start"))
    if short_ab:
        s += wire((700, 80), (700, 340)) + arrow(730, 140, 730, 280, BLUE) + t(750, 222, "I_N", "lbB", "start").replace('text-anchor="middle"', "")
    return s

inorm = svg(base(True))
conv = svg(vsrc(120, 130, 290) + res(120, 130, 330, 130) + wire((120, 290), (330, 290)) + term(330, 130) + term(330, 290) +
           t(65, 222, "4V", "lbY", "end") + t(225, 95, "2Ω", "lbY") + t(420, 225, "⇄", "lbB") + norton(580, "2A", "2Ω"))
load = svg(isrc(150, 80, 340) + wire((150, 80), (700, 80)) + wire((150, 340), (700, 340)) + res(420, 80, 420, 340) + res(700, 80, 700, 340) +
           dot(420, 80) + dot(420, 340) + t(95, 222, "2A", "lbY", "end") + t(460, 222, "R_N 2Ω", anchor="start") +
           t(740, 222, "R_L 2Ω", anchor="start") + arrow(660, 130, 660, 190) + t(640, 175, "I_L", "lbY", "end"))

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="테브난 알면", line2="노턴은 공짜", sub="전류원 + 병렬 저항으로 바꾸기", visual=equiv,
               chips=["노턴 등가", "I_N 구하기", "테브난 ⇄ 노턴", "언제 쓰나"]),
    cards=[
        dict(title="노턴 등가", sub="어떤 선형 회로든 전류원 하나 + 저항 하나", visual=equiv,
             formula="회로 = I_N ∥ R_N (병렬)",
             ex=f"{Y('R_N = R_th')} &nbsp;구하는 법이 완전히 같아요",
             trap="<b>함정</b> 노턴은 병렬, 테브난은 직렬. 여기서 제일 많이 틀려요"),
        dict(title="I_N 구하기", sub="단자 a–b를 선으로 잇고(단락) 흐르는 전류", visual=inorm,
             formula=f"I_N = {F('12V', '6Ω')} = 2A",
             ex="단락하면 3Ω 양끝 전압이 0 → 3Ω엔 전류 0",
             trap="<b>함정</b> 단락 전류 방향을 a → b 로 정하고 시작하기"),
        dict(title="테브난 ⇄ 노턴", sub="셋 중 둘만 구하면 나머지는 공짜", visual=conv,
             formula="V_th = I_N × R_N",
             ex=f"2A × 2Ω = {Y('4V')} &nbsp;(테브난 결과랑 똑같아요)",
             trap="<b>팁</b> R_th가 구하기 귀찮으면 V_th ÷ I_N 으로 끝"),
        dict(title="언제 쓰나", sub="부하가 병렬로 붙으면 노턴이 계산이 짧아요", visual=load,
             formula=f"I_L = I_N × {F('R_N', 'R_N + R_L')}",
             ex=f"2A × {F('2', '2 + 2')} = {Y('1A')} &nbsp;(전류 분배 한 번)",
             trap="<b>팁</b> 직렬 부하 → 테브난, 병렬 부하 → 노턴"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('I_N')} 단자 단락 전류",
        f"{Y('R_N')} = R_th (전원 끄고 저항)",
        f"{Y('V_th = I_N R_N')} 로 서로 변환",
        f"{Y('병렬 부하')}면 노턴이 편해요"]),
)

CAPTION = """전기전자 주목⚡ 테브난 알면 노턴은 공짜예요
전압원 + 직렬 저항 → 전류원 + 병렬 저항, 저항값은 그대로.
I_N 구하는 법이랑 변환 공식까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #노턴 #테브난 #전기전자 #공대생"""
