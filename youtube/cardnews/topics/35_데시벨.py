from cards import *

tbl = ('<table style="font-size:44px;border-spacing:40px 6px">' +
       "".join(f'<tr><td style="text-align:right">×{a}</td><td>→</td><td class="{c}" style="text-align:right">{b}</td></tr>'
               for a, b, c in (("100", "+40dB", "yel"), ("10", "+20dB", "yel"), ("2", "+6dB", "blue"), ("√2", "+3dB", "blue"), ("1", "0dB", ""), ("0.707", "−3dB", "red"), ("0.1", "−20dB", "red"))) +
       "</table>")

chain = svg(t(70, 222, "입력", "lb", "start") + arrow(150, 210, 210, 210, W) + box(220, 150, 200, 120, "×10") + t(320, 310, "+20dB", "lbY") +
            arrow(430, 210, 490, 210, W) + box(500, 150, 200, 120, "×2") + t(600, 310, "+6dB", "lbY") + arrow(710, 210, 770, 210, W) +
            t(840, 222, "×20", "lbY") + t(840, 270, "26dB", "lbY"), 400)

pv = svg(t(90, 90, "전압 ×2", "lb", "start") + t(330, 90, "→ 20 log 2", "lbS", "start") + t(800, 90, "6dB", "lbY", "end") +
         t(90, 190, "전력 ×4", "lb", "start") + t(330, 190, "→ 10 log 4", "lbS", "start") + t(800, 190, "6dB", "lbY", "end") +
         t(450, 270, "같은 저항이면 전압 2배 = 전력 4배", "lbS"), 300)

X0, Y0 = 90, 360
def logc():
    s = axes(X0, Y0, 20, 740, 320, 20, "", "dB") + t(X0 + 730, Y0 - 60, "전압비 (로그 눈금)", "lbS", "end")
    s += curve(lambda x: x, 0, 3, X0 + 20, Y0 - 20, 210, 90, YEL, 6)
    for k, lab in enumerate(("×1", "×10", "×100", "×1000")):
        x, y = X0 + 20 + 210 * k, Y0 - 20 - 90 * k
        s += dot(x, y, BLUE) + t(x, Y0 + 40, lab, "lbS") + t(x + 16, y - 16, f"{20*k}dB", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"')
    return svg(s, 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="10배가 왜", line2="20dB일까", sub="데시벨, 곱셈을 덧셈으로 바꾸는 단위", visual=logc(),
               chips=["정의", "외울 값", "더하기", "전력·전압"]),
    cards=[
        dict(title="정의", sub="크기 비율에 로그를 씌운 단위", visual=logc(),
             formula="dB = 20 log₁₀ |H|",
             ex=f"전압 10배 → {Y('20dB')}, 100배 → {Y('40dB')}",
             trap="<b>함정</b> 전압·전류 비는 20, 전력 비는 10을 곱해요"),
        dict(title="자주 쓰는 값", sub="이 일곱 줄은 외워 두세요", visual=tbl,
             formula="0.707배 = −3dB",
             ex=f"그래서 차단 주파수를 {Y('−3dB 지점')}이라 불러요",
             trap="<b>기억</b> 1보다 작으면 dB는 음수"),
        dict(title="이어 붙이기", sub="곱해지는 이득이 dB에선 더하기", visual=chain,
             formula="20dB + 6dB = 26dB",
             ex=f"증폭기 두 개를 이으면 {Y('dB만 더하면')} 끝",
             trap="<b>팁</b> 그래서 보드 선도를 직선 몇 개로 그릴 수 있어요"),
        dict(title="전력 vs 전압", sub="전력은 전압의 제곱이라 계수가 달라요", visual=pv,
             formula=f"dB = 10 log {F('P₂', 'P₁')} = 20 log {F('V₂', 'V₁')}",
             ex=f"그래서 전력 2배 = {Y('3dB')}, 전압 2배 = {Y('6dB')}",
             trap="<b>함정</b> 전력 비에 20을 곱하면 두 배로 틀려요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('dB = 20 log |H|')} (전압)",
        f"×10 = {Y('20dB')}, ×2 = {Y('6dB')}",
        f"0.707 = {Y('−3dB')}",
        f"이득을 곱하는 대신 {Y('dB를 더하기')}"]),
)

CAPTION = """전기전자 주목⚡ 10배가 왜 20dB일까?
데시벨은 곱셈을 덧셈으로 바꾸는 단위예요. 증폭기를 이어 붙여도 dB만 더하면 끝.
꼭 외울 값 일곱 개랑 전력·전압 dB 차이까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #데시벨 #보드선도 #전기전자 #공대생"""
