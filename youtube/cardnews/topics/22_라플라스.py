from cards import *

R = lambda s: f'<span class=red>{s}</span>'
flow = (f'<div style="display:flex;flex-direction:column;align-items:center;gap:10px;font-size:44px">'
        f'<span>미분방정식 <span style="opacity:.5">(어려움)</span></span><span class=blue style="font-size:34px">↓ 라플라스 변환</span>'
        f'<span class=yel>s의 분수식 <span style="opacity:.6">(나눗셈·부분분수)</span></span><span class=blue style="font-size:34px">↓ 역변환</span>'
        f'<span class=grn>시간 답 v(t)</span></div>')
table = (f'<table style="font-size:44px;border-collapse:collapse">' +
         "".join(f'<tr><td style="padding:8px 28px">{a}</td><td style="padding:8px 18px;color:{BLUE}">→</td><td style="padding:8px 28px" class=yel>{b}</td></tr>'
                 for a, b in [("1 (계단)", "1 / s"), ("e<sup>−at</sup>", "1 / (s + a)"), ("sin ωt", "ω / (s² + ω²)"), ("f′(t)", "sF(s) − f(0)")]) + "</table>")
zs = svg(res(100, 210, 260, 210) + t(180, 150, "R") + t(180, 290, "R", "lbY") +
         ind(350, 210, 530, 210) + t(440, 150, "L") + t(440, 290, "sL", "lbY") +
         cap(620, 210, 800, 210) + t(710, 150, "C") + t(710, 290, "1 / sC", "lbY"), 360)
X0, Y0 = 110, 340
resp = svg(axes(X0, Y0, 20, 720, 300, 20, "t", "v(t)") + curve(lambda x: 1 - math.exp(-x), 0, 5.3, X0, Y0, 130, 260, YEL, 6) +
           f'<line x1="{X0}" y1="{Y0-260}" x2="{X0+700}" y2="{Y0-260}" stroke="{DIM}" stroke-width="2" stroke-dasharray="6 8"/>' + t(X0 + 700, Y0 - 274, "V", "lbS", "end"), 400)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="미분방정식을", line2="나눗셈으로 바꾸는 법", sub="라플라스 변환, 회로에선 이것만", visual=flow,
               chips=["핵심 아이디어", "변환표", "s영역 회로", "풀이 예"]),
    cards=[
        dict(title="핵심 아이디어", sub="미분이 s 곱하기가 돼요", visual=flow,
             formula="L{ f′(t) } = s F(s) − f(0)",
             ex=f"미분방정식 → {Y('대수 방정식')} → 풀고 → 되돌리기",
             trap="<b>함정</b> 초기값 f(0)을 빼먹으면 답이 통째로 틀려요"),
        dict(title="변환표", sub="회로 시험엔 이 네 줄이면 거의 다 돼요", visual=table,
             formula="e<sup>−at</sup> ↔ 1 / (s + a)",
             ex=f"분모가 0이 되는 s = −a 가 {Y('극점')} → 응답 모양을 결정",
             trap="<b>기억</b> 극점이 왼쪽(음수)이면 사라지는 응답 = 안정"),
        dict(title="s영역 회로", sub="부품을 s 임피던스로 바꾸고 옴의 법칙 그대로", visual=zs,
             formula="Z_R = R &nbsp;·&nbsp; Z_L = sL &nbsp;·&nbsp; Z_C = 1/sC",
             ex=f"페이저의 jω 자리에 {Y('s')}를 넣은 것과 같아요",
             trap="<b>함정</b> 초기 전압·전류가 있으면 전원을 하나 더 그려야 해요"),
        dict(title="풀이 예: RC 충전", sub="계단 전압 V를 RC에 넣으면", visual=resp,
             formula=f"V_C(s) = {F('V', 's')} · {F('1', '1 + sRC')} = V ({F('1', 's')} − {F('1', 's + 1/RC')})",
             ex=f"역변환 → {Y('V (1 − e<sup>−t/RC</sup>)')}, 과도응답 공식 그대로",
             trap="<b>팁</b> 부분분수로 쪼개고 표에서 찾기, 이게 전부"),
    ],
    summary=dict(tag="순서대로", rows=[
        f"{Y('①')} 회로를 s영역으로 (sL, 1/sC)",
        f"{Y('②')} 옴·KVL·KCL로 F(s) 구하기",
        f"{Y('③')} 부분분수로 쪼개기",
        f"{Y('④')} 표 보고 역변환"]),
)

CAPTION = """전기전자 주목⚡ 미분방정식을 나눗셈으로 바꾸는 법
라플라스 변환을 하면 미분이 s 곱하기가 돼요. 회로는 sL, 1/sC로 바꾸고 옴의 법칙 그대로.
변환표 네 줄이랑 RC 충전 풀이까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #라플라스변환 #전기전자 #공대생 #공대수학"""
