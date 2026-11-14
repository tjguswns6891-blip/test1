from cards import *

X0, Y0 = 100, 260
def g(kind):
    s = axes(X0, Y0, 20, 740, 220, 160, "t", "")
    if kind == "rep":
        s += curve(lambda x: math.exp(-x), 0, 6, X0, Y0, 115, 200, DIM, 4, dash="10 8") + curve(lambda x: x * math.exp(-x), 0, 6, X0, Y0, 115, 200, BLUE, 5, dash="10 8")
        s += curve(lambda x: (1 + x) * math.exp(-x), 0, 6, X0, Y0, 115, 200, YEL, 7) + t(X0 + 260, Y0 - 190, "e^(−t) + t e^(−t)", "lbY", "start")
        s += t(X0 + 300, Y0 - 50, "t e^(−t)", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    else:
        s += curve(lambda x: math.exp(-x), 0, 6, X0, Y0, 115, 140, DIM, 3, dash="8 8") + curve(lambda x: -math.exp(-x), 0, 6, X0, Y0, 115, 140, DIM, 3, dash="8 8")
        s += curve(lambda x: math.exp(-x) * math.cos(2 * x), 0, 6, X0, Y0, 115, 140, YEL, 7) + t(X0 + 330, Y0 - 100, "e^(−t) cos 2t", "lbY", "start")
        s += t(X0 + 330, Y0 + 130, "껍질 ±e^(−t)", "lbS", "start")
    return svg(s, 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="근이 겹치거나", line2="복소수라면?", sub="라플라스 역변환, 나머지 두 경우", visual=g("cx"),
               chips=["중근", "중근 예", "복소근", "복소근 예"]),
    cards=[
        dict(title="중근", sub="같은 근이 두 번 → t가 곱해져요", visual=g("rep"),
             formula=f"{F('1', '(s + a)²')} ↔ t e<sup>−at</sup>",
             ex=f"A/(s + a) + B/(s + a)² {Y('두 항')}으로 쪼개요",
             trap="<b>함정</b> 1/(s + a)² 항 하나만 쓰면 틀려요"),
        dict(title="중근 예", sub="(s + 2) / (s + 1)²", visual=g("rep"),
             formula=f"{F('(s + 1) + 1', '(s + 1)²')} = {F('1', 's + 1')} + {F('1', '(s + 1)²')}",
             ex=f"f(t) = {Y('e<sup>−t</sup> + t e<sup>−t</sup>')}",
             trap="<b>팁</b> 분자를 (s + 1) + 1 로 쪼개면 바로 보여요"),
        dict(title="복소근", sub="출렁이면서 줄어드는 응답", visual=g("cx"),
             formula=f"{F('s + a', '(s + a)² + ω²')} ↔ e<sup>−at</sup> cos ωt",
             ex=f"{F('ω', '(s + a)² + ω²')} ↔ {Y('e<sup>−at</sup> sin ωt')}",
             trap="<b>기억</b> 실수부 a는 줄어드는 속도, ω는 출렁이는 속도"),
        dict(title="복소근 예", sub="(s + 1) / (s² + 2s + 5)", visual=g("cx"),
             formula="s² + 2s + 5 = (s + 1)² + 2²",
             ex=f"f(t) = {Y('e<sup>−t</sup> cos 2t')}",
             trap="<b>함정</b> 완전제곱부터. 복소수로 쪼개면 계산이 길어져요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"중근 {Y('1/(s + a)² ↔ t e^(−at)')}",
        f"중근은 {Y('두 항')} 다 쓰기",
        f"복소근 {Y('완전제곱')} → cos, sin",
        f"a = 줄어드는 속도, {Y('ω = 출렁임')}"]),
)

CAPTION = """전기전자 주목⚡ 근이 겹치거나 복소수라면?
중근이면 t가 곱해지고, 복소근이면 출렁이며 줄어드는 cos·sin이 나와요.
라플라스 역변환 나머지 두 경우를 예제로 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #라플라스변환 #역변환 #전기전자 #공대생"""
