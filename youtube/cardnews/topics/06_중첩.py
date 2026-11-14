from cards import *

def base(v=True, i=True, lab=""):
    s = ((vsrc(140, 80, 340) if v else wire((140, 80), (140, 340))) + res(140, 80, 450, 80) + res(450, 80, 450, 340) +
         wire((140, 340), (700, 340)) + dot(450, 80, BLUE) + dot(450, 340) + t(295, 45, "6Ω") + t(490, 222, "3Ω", anchor="start"))
    s += t(60, 222, "12V") if v else t(80, 222, "단락", "lbC").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    if i:
        s += wire((450, 80), (700, 80)) + isrc(700, 80, 340) + t(750, 222, "3A", anchor="start")
    else:
        s += wire((450, 80), (600, 80)) + term(600, 80) + term(600, 340) + wire((600, 340), (700, 340)) + t(650, 222, "개방", "lbC").replace('class="lbC"', 'class="lbC" fill="#ff6b61"')
    return svg(s + t(450, 45, lab, "lbB"))

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="전원이 두 개면", line2="하나씩 꺼라", sub="중첩의 원리, 끄는 법만 알면 끝", visual=base(lab="V = ?"),
               chips=["원리", "전류원 끄기", "전압원 끄기", "합치기"]),
    cards=[
        dict(title="중첩의 원리", sub="전원 여러 개 = 전원 하나짜리 회로 여러 개의 합", visual=base(lab="V"),
             formula="V = V(12V만) + V(3A만)",
             ex="어려운 회로 1개 → 쉬운 회로 2개",
             trap="<b>조건</b> 선형 회로만, 전압·전류만 더할 수 있어요"),
        dict(title="12V만 남기기", sub="전류원을 끄면 끊긴 선(개방)", visual=base(i=False, lab="V′"),
             formula=f"V′ = 12 × {F('3', '6 + 3')} = 4V",
             ex=f"→ 전압 분배 한 번이면 {Y('V′ = 4V')}",
             trap="<b>함정</b> 전류원 끄기 = 끊기(개방). 선으로 이으면 틀려요"),
        dict(title="3A만 남기기", sub="전압원을 끄면 그냥 선(단락)", visual=base(v=False, lab="V″"),
             formula="V″ = 3 × (6 ∥ 3) = 3 × 2 = 6V",
             ex=f"→ 두 저항이 병렬이 돼서 {Y('V″ = 6V')}",
             trap="<b>함정</b> 전압원 끄기 = 선(단락). 끊으면 틀려요"),
        dict(title="합치기", sub="따로 구한 값을 그대로 더해요", visual=base(lab="V = 10V"),
             formula="V = V′ + V″ = 4 + 6 = 10V",
             ex=f"마디 해석으로 풀어도 {Y('10V')} ✓",
             trap="<b>함정</b> 전력은 더하면 안 돼요! P는 V²에 비례해서"),
    ],
    summary=dict(tag="순서대로", rows=[
        f"{Y('①')} 전원 하나만 남기고 끄기",
        f"{Y('②')} 전압원 → 단락, 전류원 → 개방",
        f"{Y('③')} 전원마다 반복",
        f"{Y('④')} 전압·전류만 더하기 (전력 X)"]),
)

CAPTION = """전기전자 주목⚡ 전원이 두 개면, 하나씩 꺼 보세요
중첩의 원리: 전원 하나씩 남겨서 풀고 마지막에 더하기.
전압원·전류원 끄는 법이랑 전력 함정까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #중첩의원리 #전기전자 #공대생 #공대공부"""
