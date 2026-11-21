from cards import *

th = svg(box(90, 40, 360, 330, "") + t(270, 30, "테브난 등가", "lbS") + vsrc(170, 110, 310) + wire((170, 110), (230, 110)) + res(230, 110, 450, 110) +
         wire((170, 310), (450, 310)) + term(450, 110) + term(450, 310) + wire((450, 110), (650, 110)) + wire((450, 310), (650, 310)) +
         res(650, 110, 650, 310) + t(120, 222, "V_th", "lb", "end") + t(340, 80, "R_th") + t(690, 222, "R_L ?", "lbY", "start"), 400)

X0, Y0 = 110, 340
def pc():
    f = lambda r: 4 * r / (1 + r) ** 2
    s = axes(X0, Y0, 20, 720, 300, 20, "R_L / R_th", "P") + curve(f, 0.02, 6, X0, Y0, 115, 240, YEL, 6)
    s += f'<line x1="{X0+115}" y1="{Y0}" x2="{X0+115}" y2="{Y0-240}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 8"/>' + dot(X0 + 115, Y0 - 240, BLUE)
    s += t(X0 + 135, Y0 - 250, "R_L = R_th 에서 최대", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"') + t(X0 + 115, Y0 + 40, "1", "lbS")
    return svg(s, 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="부하 저항을 얼마로 해야", line2="전력이 최대일까", sub="최대 전력 전달, 답은 R_L = R_th", visual=pc(),
               chips=["조건", "최대 전력", "효율 50%", "교류"]),
    cards=[
        dict(title="조건", sub="회로를 테브난 등가로 바꾸고 부하 R<sub>L</sub>만 고르기", visual=th,
             formula="R_L = R_th",
             ex=f"부하 저항이 {Y('내부 저항과 같을 때')} 전력 최대",
             trap="<b>함정</b> R<sub>th</sub>를 줄이는 게 아니라 R<sub>L</sub>을 고르는 문제"),
        dict(title="최대 전력", sub="R_L = R_th 를 넣고 정리하면", visual=pc(),
             formula=f"P_max = {F('V_th²', '4 R_th')}",
             ex=f"예) 12V, 3Ω &nbsp;→&nbsp; 144 / 12 = {Y('12W')}",
             trap="<b>함정</b> 분모의 4를 빼먹는 실수가 제일 많아요"),
        dict(title="효율 50%", sub="내부 저항 R<sub>th</sub>에서도 같은 전력이 열로 사라져요", visual=th,
             formula="η = 50%",
             ex=f"그래서 전력망은 이 조건을 {Y('안 써요')} (효율이 우선)",
             trap="<b>기억</b> 통신·안테나처럼 신호를 최대로 받을 때 쓰는 조건"),
        dict(title="교류", sub="임피던스면 허수부를 지워야 해요", visual=th,
             formula="Z_L = Z_th*",
             ex=f"예) Z_th = 4 + j3 &nbsp;→&nbsp; {Y('Z_L = 4 − j3 Ω')}",
             trap="<b>함정</b> 켤레! 허수부 부호만 반대. P_max = |V_th|² / 4R_th"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('R_L = R_th')} 일 때 최대",
        f"{Y('P_max = V_th² / 4R_th')}",
        f"그때 효율은 {Y('50%')}",
        f"교류는 {Y('Z_L = Z_th*')}"]),
)

CAPTION = """전기전자 주목⚡ 부하 저항을 얼마로 해야 전력이 최대일까?
답은 내부 저항과 같을 때(R_L = R_th). 대신 효율은 딱 50%예요.
P_max 공식이랑 교류에서 켤레를 쓰는 이유까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #최대전력전달 #테브난 #전기전자 #공대생"""
