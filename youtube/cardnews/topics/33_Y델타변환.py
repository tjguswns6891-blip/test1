from cards import *

def rb(x, y, ang, lab, c=YEL, lx=0, ly=0, anc="middle"):
    return (f'<g transform="translate({x},{y}) rotate({ang})"><rect x="-44" y="-15" width="88" height="30" rx="8" fill="#11141b" stroke="{c}" stroke-width="5"/></g>'
            + (t(x + lx, y + ly + 12, lab, "lbC", anc).replace('class="lbC"', f'class="lbC" fill="{c}"') if lab else ""))

def pair(focus=""):
    A, Bp, Cp = (230, 70), (90, 330), (370, 330)
    dc, yc = (YEL if focus != "y" else DIM), (BLUE if focus != "d" else DIM)
    d = (f'<polygon points="{A[0]},{A[1]} {Bp[0]},{Bp[1]} {Cp[0]},{Cp[1]}" fill="none" stroke="{W}" stroke-width="5"/>' +
         rb(160, 200, -62, "R_ab", dc, -36, 0, "end") + rb(300, 200, 62, "R_ca", dc, 36, 0, "start") + rb(230, 330, 0, "R_bc", dc, 0, 50) +
         dot(*A) + dot(*Bp) + dot(*Cp) + t(230, 50, "a") + t(70, 370, "b") + t(390, 370, "c") + t(230, 270, "Δ", "lbB"))
    O = (680, 230); a, b, c = (680, 70), (540, 330), (820, 330)
    y = (wire(O, a) + wire(O, b) + wire(O, c) + rb(680, 150, 90, "R_a", yc, 34, 0, "start") + rb(610, 280, -62, "R_b", yc, -36, -10, "end") +
         rb(750, 280, 62, "R_c", yc, 36, -10, "start") + dot(*O) + dot(*a) + dot(*b) + dot(*c) + t(680, 50, "a") + t(520, 370, "b") + t(840, 370, "c") + t(680, 400, "Y", "lbB"))
    return svg(d + y + t(455, 220, "⇄", "lbY"), 430)

def bridge():
    T, L, R, Bt = (450, 50), (230, 210), (670, 210), (450, 370)
    s = wire(T, L) + wire(T, R) + wire(L, Bt) + wire(R, Bt) + wire(L, R)
    s += rb(340, 130, 36, "") + rb(560, 130, -36, "") + rb(340, 290, -36, "") + rb(560, 290, 36, "") + rb(450, 210, 0, "")
    s += f'<polygon points="{T[0]},{T[1]} {L[0]},{L[1]} {R[0]},{R[1]}" fill="rgba(90,162,255,.12)" stroke="{BLUE}" stroke-width="4" stroke-dasharray="10 8"/>'
    s += "".join(dot(*p) for p in (T, L, R, Bt)) + t(720, 130, "이 Δ를 Y로", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    return svg(s, 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="직렬도 병렬도 아닌", line2="회로 푸는 법", sub="Y-Δ 변환, 공식 두 개면 끝", visual=pair(),
               chips=["언제 쓰나", "Δ → Y", "Y → Δ", "같은 저항"]),
    cards=[
        dict(title="언제 쓰나", sub="직렬·병렬로 안 묶이는 브리지 회로", visual=bridge(),
             formula="삼각형 하나를 Y로 바꾸기",
             ex=f"바꾸고 나면 {Y('직렬·병렬')}로 다 풀려요",
             trap="<b>팁</b> 브리지가 평형이면 가운데 저항은 무시해도 돼요"),
        dict(title="Δ → Y", sub="꼭짓점에 붙은 두 저항의 곱 ÷ 세 저항 합", visual=pair("d"),
             formula=f"R_a = {F('R_ab R_ca', 'R_ab + R_bc + R_ca')}",
             ex=f"예) 2, 3, 5Ω (ab, bc, ca) → R_a = 10/10 = {Y('1Ω')}",
             trap="<b>기억</b> a에 붙은 R<sub>ab</sub>, R<sub>ca</sub>를 곱해요. R<sub>bc</sub>는 분모에만"),
        dict(title="Y → Δ", sub="곱 두 개씩의 합 ÷ 마주 보는 Y 저항", visual=pair("y"),
             formula=f"R_ab = {F('R_a R_b + R_b R_c + R_c R_a', 'R_c')}",
             ex=f"예) Y 각 1, 2, 3Ω → 분자 11 → R_ab = {Y('11/3Ω')}",
             trap="<b>함정</b> R_ab 분모는 R_c (a, b 어디에도 안 붙은 팔)"),
        dict(title="같은 저항", sub="세 저항이 같으면 3배 차이", visual=pair(),
             formula="R_Y = R_Δ / 3",
             ex=f"예) Δ 각 9Ω → {Y('Y 각 3Ω')}",
             trap="<b>기억</b> 3상 Y-Δ 부하 변환도 같은 공식"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"브리지는 {Y('Δ 하나를 Y로')}",
        f"{Y('Δ→Y')} 이웃 둘 곱 ÷ 셋 합",
        f"{Y('Y→Δ')} 곱의 합 ÷ 마주 보는 팔",
        f"같으면 {Y('R_Y = R_Δ / 3')}"]),
)

CAPTION = """전기전자 주목⚡ 직렬도 병렬도 아닌 회로, 어떻게 풀까요?
브리지 회로는 삼각형(Δ) 하나를 Y로 바꾸면 직렬·병렬로 풀려요.
Δ→Y, Y→Δ 공식이랑 숫자 예제까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #Y델타변환 #브리지회로 #전기전자 #공대생"""
