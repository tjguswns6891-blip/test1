from cards import *

X0, Y0, SX, SY = 100, 200, 140, 4.2   # x: 1칸 = 10배, y: 1dB = 4.2px

def P(x, db):
    return X0 + x * SX, Y0 - db * SY

def plot(pts, real=None, c=YEL, ylab=True):
    s = axes(X0, Y0, 20, 740, Y0 - 20, 400 - Y0, "ω (로그)", "dB" if ylab else "")
    for k in range(1, 6):
        s += f'<line x1="{X0+k*SX}" y1="30" x2="{X0+k*SX}" y2="400" stroke="#1f2532" stroke-width="2"/>'
    if real:
        s += curve(real, 0, pts[-1][0], X0, Y0, SX, SY, BLUE, 4, dash="10 8")
    d = "M" + " L".join(f"{P(x, y)[0]:.0f},{P(x, y)[1]:.0f}" for x, y in pts)
    return s + f'<path d="{d}" fill="none" stroke="{c}" stroke-width="7" stroke-linejoin="round"/>'

def pole():
    s = plot([(0, 0), (2, 0), (5, -60)], lambda x: -10 * math.log10(1 + 10 ** (2 * (x - 2))))
    x, y = P(2, -3)
    return svg(s + dot(x, y, BLUE) + t(x - 16, y + 46, "−3dB", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{BLUE}"') +
               t(P(2, 0)[0], Y0 - 22, "ω_p", "lbY") + t(P(4, -40)[0] + 20, P(4, -40)[1] - 10, "−20dB/dec", "lbY", "start"), 420)

def zero():
    s = plot([(0, -40), (2, -40), (4, 0), (5, 20)], c=GRN)
    return svg(s + t(P(2, -40)[0] - 14, P(2, -40)[1] - 20, "ω_z", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{GRN}"') +
               t(P(3, -20)[0] - 20, P(3, -20)[1] - 10, "+20dB/dec", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{GRN}"'), 420)

def ex():
    global Y0, SY
    Y0, SY = 230, 2.6
    s = plot([(0, 40), (1, 40), (3, 0), (4, -40), (5, -80)][:4] + [(4.5, -60)], lambda x: 40 - 10 * math.log10(1 + 10 ** (2 * (x - 1))) - 10 * math.log10(1 + 10 ** (2 * (x - 3))))
    s += t(P(0, 40)[0] + 30, P(0, 40)[1] - 16, "40dB", "lbY", "start")
    s += t(P(1, 40)[0], Y0 + 40, "10", "lbS") + t(P(3, 0)[0], Y0 + 40, "1000", "lbS")
    s += t(P(2, 20)[0] + 16, P(2, 20)[1] - 6, "−20", "lbY", "start") + t(P(4, -40)[0] + 16, P(4, -40)[1] - 10, "−40", "lbY", "start")
    Y0, SY = 200, 4.2
    return svg(s, 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="곡선 그래프를", line2="직선 몇 개로", sub="보드 선도, 꺾이는 점과 기울기만 보면 돼요", visual=ex(),
               chips=["축", "극 하나", "영점 하나", "그리기 예"]),
    cards=[
        dict(title="축", sub="가로는 주파수 로그 눈금, 세로는 dB", visual=pole(),
             formula="한 칸 = 10배 (decade)",
             ex=f"곱하기가 더하기가 돼서 {Y('직선')}으로 근사돼요",
             trap="<b>기억</b> 크기 그래프 밑에 위상 그래프도 같이 그려요"),
        dict(title="극 하나", sub="H = 1 / (1 + s/ω_p)", visual=pole(),
             formula="ω_p 이후 −20dB/dec",
             ex=f"꺾이는 점의 실제 값은 직선보다 {Y('3dB')} 아래 (점선)",
             trap="<b>함정</b> 위상은 −90°까지, 꺾이는 점에서 −45°"),
        dict(title="영점 하나", sub="H = 1 + s/ω_z", visual=zero(),
             formula="ω_z 이후 +20dB/dec",
             ex=f"위상은 {Y('+90°')}까지 올라가요",
             trap="<b>기억</b> 같은 점에 극이 n개 겹치면 −20n dB/dec"),
        dict(title="그리기 예", sub="H(s) = 100 / (1 + s/10)(1 + s/1000)", visual=ex(),
             formula="40dB → 10에서 −20 → 1000에서 −40",
             ex=f"저주파 이득 100 = {Y('40dB')}에서 시작",
             trap="<b>팁</b> 왼쪽부터 꺾이는 점마다 기울기만 바꾸면 끝"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"가로 {Y('log ω')}, 세로 {Y('dB')}",
        f"극마다 {Y('−20dB/dec')}, 영점마다 {Y('+20')}",
        f"꺾이는 점 실제 값 {Y('±3dB')}",
        f"시작값 → 꺾이는 점에서 {Y('기울기 변경')}"]),
)

CAPTION = """전기전자 주목⚡ 곡선 그래프를 직선 몇 개로 그리는 요령
보드 선도는 꺾이는 점마다 기울기만 바꾸면 돼요. 극은 −20dB/dec, 영점은 +20dB/dec.
극 하나, 영점 하나, 실제 그리기 예까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #보드선도 #주파수응답 #전기전자 #공대생"""
