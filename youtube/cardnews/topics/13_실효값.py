from cards import *

X0, Y0 = 90, 210
def wave(fn, rms, lab, extra=""):
    return svg(axes(X0, Y0, 20, 760, 180, 180, "t", "") + curve(fn, 0, 12.56, X0, Y0, 58, 150, YEL) +
               f'<line x1="{X0}" y1="{Y0-rms*150}" x2="{X0+740}" y2="{Y0-rms*150}" stroke="{BLUE}" stroke-width="4" stroke-dasharray="12 8"/>' +
               t(X0 + 740, Y0 - rms * 150 - 14, lab, "lbB").replace('text-anchor="middle"', 'text-anchor="end"') + extra, 420)

sine = wave(math.sin, 1 / math.sqrt(2), "V_rms", t(X0 + 16, Y0 - 160, "V_m", "lbY", "start"))
heat = svg(box(80, 110, 300, 200, "") + t(230, 200, "교류 220V", "lbB") + t(230, 250, "(실효값)", "lbS") +
           t(450, 225, "=", "lbB") + box(520, 110, 300, 200, "", YEL) + t(670, 200, "직류 220V", "lbY") + t(670, 250, "같은 열", "lbS"), 400)
sq = lambda x: 1 if math.sin(x) >= 0 else -1
tri = lambda x: 2 / math.pi * math.asin(math.sin(x))
shapes = svg(axes(X0, 110, 20, 760, 90, 90) + curve(sq, 0, 12.56, X0, 110, 58, 70, GRN, 5, 600) + t(X0 + 740, 60, "구형파: V_m", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{GRN}"') +
             axes(X0, 320, 20, 760, 90, 90) + curve(tri, 0, 12.56, X0, 320, 58, 70, PUR) + t(X0 + 740, 270, "삼각파: V_m / √3", "lbC", "end").replace('class="lbC"', f'class="lbC" fill="{PUR}"'), 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="콘센트 220V,", line2="사실 최대는 311V", sub="실효값 = 열을 기준으로 한 '진짜 크기'", visual=sine,
               chips=["정의", "사인파", "전력", "다른 파형"]),
    cards=[
        dict(title="실효값의 뜻", sub="저항에서 같은 열을 내는 직류 크기", visual=heat,
             formula="V_rms = √( v² 의 평균 )",
             ex=f"이름 그대로 {Y('제곱 → 평균 → 루트')} (RMS)",
             trap="<b>함정</b> 사인파의 그냥 평균은 0. 평균이랑 다른 말이에요"),
        dict(title="사인파", sub="최대값을 √2로 나누면 끝", visual=sine,
             formula=f"V_rms = {F('V_m', '√2')} ≈ 0.707 V_m",
             ex=f"콘센트 220V &nbsp;→&nbsp; 최대 220 × √2 ≈ {Y('311V')}",
             trap="<b>기억</b> 계측기·콘센트 숫자는 전부 실효값"),
        dict(title="전력", sub="교류 전력 계산은 실효값으로 해요", visual=heat,
             formula="P = V_rms × I_rms × cos θ",
             ex=f"예) 220V, 5A, 저항 부하(θ = 0) &nbsp;→&nbsp; {Y('1100W')}",
             trap="<b>함정</b> 최대값끼리 곱하면 2배로 나와요. ½ V_m I_m 이 맞아요"),
        dict(title="다른 파형", sub="모양마다 나누는 숫자가 달라요", visual=shapes,
             formula="구형파 V_m &nbsp;·&nbsp; 사인파 V_m/√2 &nbsp;·&nbsp; 삼각파 V_m/√3",
             ex=f"꽉 찬 모양일수록 {Y('실효값이 커요')}",
             trap="<b>함정</b> √2는 사인파 전용. 다른 파형엔 쓰면 안 돼요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('실효값')} = 같은 열을 내는 직류",
        f"{Y('사인파')} V_m / √2",
        f"{Y('220V')} 콘센트는 최대 311V",
        f"{Y('P = V_rms I_rms cosθ')}"]),
)

CAPTION = """전기전자 주목⚡ 콘센트 220V, 사실 최대값은 311V예요
220V는 '같은 열을 내는 직류 크기', 실효값이라서요.
√2가 어디서 나오는지, 다른 파형은 어떻게 되는지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #실효값 #교류회로 #전기전자 #공대생"""
