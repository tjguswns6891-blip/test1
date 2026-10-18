# 카드뉴스 HTML 생성 (1080x1350, 4:5)
import os
OUT = os.path.dirname(os.path.abspath(__file__)) + "/html"
os.makedirs(OUT, exist_ok=True)
TOTAL = 7

W = "#e9edf5"; BLUE = "#5aa2ff"; YEL = "#f6c343"; RED = "#e5332a"; DIM = "#8a93a6"

def res(x1, y1, x2, y2, n=6, amp=14, body=90):
    """축 방향 저항 지그재그"""
    if y1 == y2:
        mid = (x1 + x2) / 2; a = mid - body / 2; step = body / n
        pts = [(x1, y1), (a, y1)]
        for i in range(n):
            pts.append((a + step * (i + .5), y1 + (amp if i % 2 else -amp)))
        pts += [(a + body, y1), (x2, y2)]
    else:
        mid = (y1 + y2) / 2; a = mid - body / 2; step = body / n
        pts = [(x1, y1), (x1, a)]
        for i in range(n):
            pts.append((x1 + (amp if i % 2 else -amp), a + step * (i + .5)))
        pts += [(x1, a + body), (x2, y2)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<path d="{d}" class="w"/>'

def wire(*pts):
    return '<path d="M' + " L".join(f"{x},{y}" for x, y in pts) + '" class="w"/>'

def vsrc(x, y1, y2, r=36):
    m = (y1 + y2) / 2
    return (wire((x, y1), (x, m - r)) + wire((x, m + r), (x, y2)) +
            f'<circle cx="{x}" cy="{m}" r="{r}" class="w"/>'
            f'<text x="{x}" y="{m-8}" class="pm">+</text><text x="{x}" y="{m+26}" class="pm">−</text>')

def isrc(x, y1, y2, r=36, up=True):
    m = (y1 + y2) / 2
    a, b = (m + 20, m - 20) if up else (m - 20, m + 20)
    return (wire((x, y1), (x, m - r)) + wire((x, m + r), (x, y2)) +
            f'<circle cx="{x}" cy="{m}" r="{r}" class="w"/>'
            f'<line x1="{x}" y1="{a}" x2="{x}" y2="{b}" class="w" marker-end="url(#ah)"/>')

def dot(x, y, c=W):
    return f'<circle cx="{x}" cy="{y}" r="7" fill="{c}"/>'

def term(x, y):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="#0b0d12" stroke="{W}" stroke-width="4"/>'

def ground(x, y):
    return (wire((x, y), (x, y + 24)) + f'<line x1="{x-26}" y1="{y+24}" x2="{x+26}" y2="{y+24}" class="w"/>'
            f'<line x1="{x-16}" y1="{y+34}" x2="{x+16}" y2="{y+34}" class="w"/>'
            f'<line x1="{x-7}" y1="{y+44}" x2="{x+7}" y2="{y+44}" class="w"/>')

def t(x, y, s, cls="lb", anchor="middle"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{s}</text>'

def arrow(x1, y1, x2, y2, c=YEL):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="5" marker-end="url(#ay)"/>'

def loop(cx, cy, r, label):
    # 시계 방향 원호 화살표
    import math
    a0, a1 = math.radians(200), math.radians(500)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    return (f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 1 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{BLUE}" '
            f'stroke-width="5" marker-end="url(#ab)"/>' + t(cx, cy + 16, label, "lbB"))

def svg(body, h=420):
    return f'''<svg viewBox="0 0 900 {h}" width="920" height="{h*920//900}">
<defs>
<marker id="ah" markerWidth="8" markerHeight="8" refX="5" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{W}"/></marker>
<marker id="ay" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="{YEL}"/></marker>
<marker id="ab" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="{BLUE}"/></marker>
</defs>{body}</svg>'''

CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:#0b0d12;color:{W};font-family:'Noto Sans CJK KR',sans-serif;overflow:hidden;position:relative}}
.glow{{position:absolute;inset:0;background:radial-gradient(900px 600px at 85% -10%,rgba(90,162,255,.16),transparent 70%),radial-gradient(700px 500px at -10% 110%,rgba(246,195,67,.08),transparent 70%)}}
.wrap{{position:relative;padding:70px 76px 0}}
.tag{{display:inline-block;background:{RED};color:#fff;font-weight:900;font-size:40px;padding:8px 26px;border-radius:12px;transform:rotate(-2deg)}}
.num{{display:inline-block;font-weight:900;font-size:34px;color:#0b0d12;background:{YEL};border-radius:10px;padding:4px 16px;margin-right:18px;vertical-align:middle}}
h1{{font-weight:900;font-size:86px;line-height:1.12;letter-spacing:-2px}}
h2{{font-weight:900;font-size:72px;letter-spacing:-1.5px;display:inline;vertical-align:middle}}
.sub{{font-size:38px;color:{DIM};margin-top:14px;font-weight:700}}
.blue{{color:{BLUE}}} .yel{{color:{YEL}}} .red{{color:#ff6b61}}
.card{{margin-top:44px;background:#11141b;border:3px solid #262c38;border-radius:28px;padding:34px 0 24px;display:flex;justify-content:center}}
.formula{{margin-top:40px;background:rgba(246,195,67,.08);border:3px solid rgba(246,195,67,.55);border-radius:22px;padding:28px 30px;font-size:54px;font-weight:900;color:{YEL};text-align:center;line-height:1.4}}
.frac{{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;font-size:.82em;margin:0 6px}}
.frac>span:first-child{{border-bottom:4px solid currentColor;padding:0 8px}}
.ex{{margin-top:34px;font-size:40px;font-weight:700;line-height:1.5}}
.trap{{margin-top:30px;font-size:36px;font-weight:700;line-height:1.45;border-left:8px solid {RED};padding:6px 0 6px 22px;color:#f3d7d5}}
.trap b{{color:#ff6b61}}
.foot{{position:absolute;left:76px;right:76px;bottom:46px;display:flex;justify-content:space-between;font-size:28px;color:{DIM};font-weight:700}}
svg .w{{fill:none;stroke:{W};stroke-width:5;stroke-linejoin:round;stroke-linecap:round}}
svg .pm{{fill:{W};font-size:30px;font-weight:900;text-anchor:middle}}
svg .lb{{fill:{W};font-size:34px;font-weight:700;font-family:'Noto Sans CJK KR'}}
svg .lbY{{fill:{YEL};font-size:36px;font-weight:900;font-family:'Noto Sans CJK KR'}}
svg .lbB{{fill:{BLUE};font-size:40px;font-weight:900;font-family:'Noto Sans CJK KR';text-anchor:middle}}
'''

def page(i, inner):
    foot = f'<div class="foot"><span>@markovspace · 보이는 회로이론</span><span>{i} / {TOTAL}{"  →" if i < TOTAL else ""}</span></div>'
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="glow"></div><div class="wrap">{inner}</div>{foot}</body></html>'
    open(f"{OUT}/{i}.html", "w").write(html)

def F(a, b):
    return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'

def content(i, title, sub, circuit, formula, ex, trap):
    page(i, f'<div><span class="num">{i-1:02d}</span><h2>{title}</h2></div><div class="sub">{sub}</div>'
            f'<div class="card">{circuit}</div><div class="formula">{formula}</div>'
            f'<div class="ex">{ex}</div><div class="trap">{trap}</div>')

# 1. 표지
cover_svg = svg(
    vsrc(130, 90, 330) + wire((130, 90), (240, 90)) + res(240, 90, 440, 90) + wire((440, 90), (520, 90)) +
    res(520, 90, 520, 330) + wire((520, 90), (600, 90)) + res(600, 90, 770, 90) + wire((770, 90), (770, 330)) +
    wire((130, 330), (770, 330)) + dot(520, 90, BLUE) + dot(520, 330) +
    t(520, 60, "V = ?", "lbY") + loop(330, 225, 58, "I₁") + loop(660, 225, 58, "I₂"), 400)
page(1, f'<div class="tag">전기전자 주목!</div>'
        f'<h1 style="margin-top:34px">복잡한 회로도<br><span class="blue">이 5개면 풀립니다</span></h1>'
        f'<div class="sub" style="margin-top:18px">공식 + 예제 숫자 + 시험 함정까지</div>'
        f'<div class="card" style="margin-top:36px">{cover_svg}</div>'
        f'<div style="margin-top:32px;display:flex;gap:14px;flex-wrap:wrap">' + "".join(f'<span style="border:3px solid #2f3746;border-radius:40px;padding:8px 24px;font-size:32px;font-weight:700"><span class="yel">{k:02d}</span> {n}</span>' for k, n in enumerate(["전압 분배","전류 분배","마디 해석","망 해석","전원 변환"],1)) + '</div>'
        f'<div class="ex" style="margin-top:30px;font-size:40px">📌 <span class="yel">저장</span>해 두고 시험 전에 넘겨 보세요</div>')

# 2. 전압 분배
c = svg(vsrc(170, 90, 330) + wire((170, 90), (250, 90)) + res(250, 90, 470, 90) + wire((470, 90), (560, 90)) +
        res(560, 90, 560, 330) + wire((170, 330), (560, 330)) +
        wire((560, 90), (700, 90)) + wire((560, 330), (700, 330)) + term(700, 90) + term(700, 330) +
        t(95, 222, "12V") + t(360, 55, "R₁ = 2kΩ") + t(605, 222, "R₂", anchor="start") + t(605, 262, "4kΩ", anchor="start") +
        t(760, 165, "+", "lbY") + t(760, 222, "V₂", "lbY") + t(760, 300, "−", "lbY"))
content(2, "전압 분배", "직렬이면 전압은 저항 크기만큼 나눠 가져요", c,
        f'V₂ = V × {F("R₂", "R₁ + R₂")}',
        f'예) 12V × {F("4", "2 + 4")} = <span class="yel">8V</span> &nbsp;·&nbsp; R₁엔 나머지 4V',
        '<b>함정</b> 부하를 달면 R₂ ∥ 부하로 바꿔서 다시 나누기')

# 3. 전류 분배
c = svg(isrc(150, 90, 330) + wire((150, 90), (740, 90)) + res(420, 90, 420, 330) + res(740, 90, 740, 330) +
        wire((150, 330), (740, 330)) + dot(420, 90) + dot(420, 330) +
        t(70, 222, "6mA") + t(460, 222, "R₁", anchor="start") + t(460, 262, "1kΩ", anchor="start") + t(780, 222, "R₂", anchor="start") + t(780, 262, "2kΩ", anchor="start") +
        arrow(380, 130, 380, 190) + t(352, 180, "I₁", "lbY", "end") + arrow(700, 130, 700, 190) + t(672, 180, "I₂", "lbY", "end"))
content(3, "전류 분배", "병렬이면 전류는 작은 저항 쪽으로 더 몰려요", c,
        f'I₁ = I × {F("R₂", "R₁ + R₂")}',
        f'예) 6mA × {F("2", "1 + 2")} = <span class="yel">4mA</span> &nbsp;·&nbsp; I₂ = 2mA',
        '<b>함정</b> 분자는 <b>반대편</b> 저항! 전압 분배랑 헷갈리는 1순위')

# 4. 마디 해석
c = svg(vsrc(140, 90, 330) + wire((140, 90), (200, 90)) + res(200, 90, 420, 90) + wire((420, 90), (680, 90)) +
        res(420, 90, 420, 330) + isrc(680, 90, 330) + wire((140, 330), (680, 330)) + dot(420, 90, BLUE) + dot(420, 330) + ground(420, 330) +
        t(65, 222, "10V") + t(310, 55, "2Ω") + t(460, 222, "2Ω", anchor="start") + t(730, 222, "1A", anchor="start") +
        t(420, 55, "V", "lbB"), 400)
content(4, "마디 해석", "마디 전압을 미지수로, 나가는 전류 합 = 0 (KCL)", c,
        f'{F("V − 10", "2")} + {F("V", "2")} − 1 = 0',
        f'→ 2V − 10 = 2 &nbsp;→&nbsp; <span class="yel">V = 6V</span>',
        '<b>순서</b> 기준 마디(접지) 정하기 → 나머지 마디에 V 붙이기 → 마디마다 KCL')

# 5. 망 해석
c = svg(vsrc(130, 90, 330) + wire((130, 90), (190, 90)) + res(190, 90, 430, 90) + wire((430, 90), (520, 90)) +
        res(520, 90, 760, 90) + wire((760, 90), (760, 330)) + res(430, 90, 430, 330) + wire((130, 330), (760, 330)) +
        dot(430, 90) + dot(430, 330) +
        t(55, 222, "10V") + t(310, 55, "2Ω") + t(640, 55, "2Ω") + t(470, 300, "4Ω", anchor="start") +
        loop(300, 220, 52, "I₁") + loop(610, 220, 52, "I₂"), 400)
content(5, "망 해석", "망 전류를 미지수로, 한 바퀴 전압 합 = 0 (KVL)", c,
        '6I₁ − 4I₂ = 10 &nbsp;/&nbsp; −4I₁ + 6I₂ = 0',
        f'→ <span class="yel">I₁ = 3A, I₂ = 2A</span> &nbsp;·&nbsp; 가운데 4Ω엔 1A',
        '<b>함정</b> 두 망이 같이 쓰는 저항엔 (I₁ − I₂), 내 망 기준으로 빼기')

# 6. 전원 변환
c = svg(vsrc(140, 100, 320) + wire((140, 100), (170, 100)) + res(170, 100, 340, 100) + wire((140, 320), (340, 320)) +
        term(340, 100) + term(340, 320) + t(92, 222, "12V", anchor="end") + t(255, 62, "3Ω") +
        t(440, 232, "⇄", "lbB") +
        wire((620, 100), (830, 100)) + wire((620, 320), (830, 320)) + isrc(620, 100, 320) + res(730, 100, 730, 320) +
        term(830, 100) + term(830, 320) + dot(730, 100) + dot(730, 320) +
        t(572, 222, "4A", anchor="end") + t(765, 222, "3Ω", anchor="start") +
        t(358, 80, "a", anchor="start") + t(848, 80, "a", anchor="start") + t(358, 365, "b", anchor="start") + t(848, 365, "b", anchor="start"), 400)
content(6, "전원 변환", "직렬 전압원 ⇄ 병렬 전류원, 밖에서 보면 똑같아요", c,
        f'I = {F("V", "R")} &nbsp;·&nbsp; R은 그대로',
        f'예) {F("12V", "3Ω")} = <span class="yel">4A</span>, 3Ω은 직렬 → 병렬로 옮기기만',
        '<b>함정</b> 전류원 화살표는 전압원 <b>+</b> 쪽 단자를 향하게')

# 7. 마무리
page(7, f'<div class="tag">언제 뭘 쓸까</div>'
        f'<div class="card" style="margin-top:44px;flex-direction:column;padding:34px 44px;gap:30px;font-size:44px;font-weight:700;line-height:1.4">'
        f'<div><span class="yel">저항 2개</span>만 보이면 → 분배 공식</div>'
        f'<div><span class="yel">전류원</span>이 많으면 → 마디 해석</div>'
        f'<div><span class="yel">전압원</span>이 많으면 → 망 해석</div>'
        f'<div><span class="yel">모양이 애매</span>하면 → 전원 변환으로 정리</div></div>'
        f'<h1 style="margin-top:80px;font-size:80px">📌 시험 전에 <span class="blue">저장</span></h1>'
        f'<div class="ex" style="font-size:40px;margin-top:20px">같은 과 친구 태그해 주세요</div>'
        f'<div class="sub" style="margin-top:44px;font-size:36px">🔗 무료 사이트 \'보이는 회로이론\' 링크는 프로필에</div>')
print("ok")
