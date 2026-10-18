"""인스타 카드뉴스(1080x1350) HTML 생성 라이브러리.

주제 하나 = topics/<이름>.py 하나. 그 파일이 make() 로 카드 목록을 돌려주면
render.py 가 HTML → PNG → JPG(video-files 카드/<이름>/card_N.jpg) 로 만든다.
"""
import math

W = "#e9edf5"; BLUE = "#5aa2ff"; YEL = "#f6c343"; RED = "#e5332a"; DIM = "#8a93a6"; GRN = "#4fd18b"; PUR = "#b48cff"

# ---------- SVG 회로 부품 ----------

def res(x1, y1, x2, y2, n=6, amp=14, body=90):
    """축 방향 저항 지그재그"""
    if y1 == y2:
        a = (x1 + x2) / 2 - body / 2; step = body / n
        pts = [(x1, y1), (a, y1)] + [(a + step * (i + .5), y1 + (amp if i % 2 else -amp)) for i in range(n)] + [(a + body, y1), (x2, y2)]
    else:
        a = (y1 + y2) / 2 - body / 2; step = body / n
        pts = [(x1, y1), (x1, a)] + [(x1 + (amp if i % 2 else -amp), a + step * (i + .5)) for i in range(n)] + [(x1, a + body), (x2, y2)]
    return '<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '" class="w"/>'

def cap(x1, y1, x2, y2, gap=14, plate=34):
    """축 방향 커패시터"""
    if y1 == y2:
        m = (x1 + x2) / 2
        return (wire((x1, y1), (m - gap, y1)) + wire((m + gap, y1), (x2, y2)) +
                f'<line x1="{m-gap}" y1="{y1-plate}" x2="{m-gap}" y2="{y1+plate}" class="w"/>'
                f'<line x1="{m+gap}" y1="{y1-plate}" x2="{m+gap}" y2="{y1+plate}" class="w"/>')
    m = (y1 + y2) / 2
    return (wire((x1, y1), (x1, m - gap)) + wire((x1, m + gap), (x2, y2)) +
            f'<line x1="{x1-plate}" y1="{m-gap}" x2="{x1+plate}" y2="{m-gap}" class="w"/>'
            f'<line x1="{x1-plate}" y1="{m+gap}" x2="{x1+plate}" y2="{m+gap}" class="w"/>')

def ind(x1, y1, x2, y2, n=4, body=96):
    """축 방향 인덕터 (반원 n개)"""
    r = body / n / 2
    if y1 == y2:
        a = (x1 + x2) / 2 - body / 2
        arcs = "".join(f" A{r},{r} 0 0 1 {a + 2 * r * (i + 1):.1f},{y1}" for i in range(n))
        return f'<path d="M{x1},{y1} L{a},{y1}{arcs} L{x2},{y2}" class="w"/>'
    a = (y1 + y2) / 2 - body / 2
    arcs = "".join(f" A{r},{r} 0 0 1 {x1},{a + 2 * r * (i + 1):.1f}" for i in range(n))
    return f'<path d="M{x1},{y1} L{x1},{a}{arcs} L{x2},{y2}" class="w"/>'

def wire(*pts):
    return '<path d="M' + " L".join(f"{x},{y}" for x, y in pts) + '" class="w"/>'

def vsrc(x, y1, y2, r=36, ac=False):
    m = (y1 + y2) / 2
    inner = (f'<path d="M{x-20},{m} q10,-22 20,0 t20,0" class="w"/>' if ac else
             f'<text x="{x}" y="{m-8}" class="pm">+</text><text x="{x}" y="{m+26}" class="pm">−</text>')
    return wire((x, y1), (x, m - r)) + wire((x, m + r), (x, y2)) + f'<circle cx="{x}" cy="{m}" r="{r}" class="w"/>' + inner

def isrc(x, y1, y2, r=36, up=True):
    m = (y1 + y2) / 2
    a, b = (m + 20, m - 20) if up else (m - 20, m + 20)
    return (wire((x, y1), (x, m - r)) + wire((x, m + r), (x, y2)) + f'<circle cx="{x}" cy="{m}" r="{r}" class="w"/>'
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

def arrow(x1, y1, x2, y2, c=YEL, w=5):
    mk = {YEL: "ay", BLUE: "ab", W: "ah", GRN: "ag", RED: "ar", PUR: "ap"}[c]
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" marker-end="url(#{mk})"/>'

def loop(cx, cy, r, label):
    """시계 방향 망 전류 화살표"""
    a0, a1 = math.radians(200), math.radians(500)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    return (f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 1 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{BLUE}" '
            f'stroke-width="5" marker-end="url(#ab)"/>' + t(cx, cy + 16, label, "lbB"))

def box(x, y, w, h, label="", c=BLUE):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="rgba(90,162,255,.08)" stroke="{c}" stroke-width="5"/>'
            + (t(x + w / 2, y + h / 2 + 13, label, "lbB") if label else ""))

def curve(fn, x0, x1, X, Y, sx, sy, c=YEL, w=5, n=200, dash=""):
    """수학 함수 그래프: 원점 (X,Y), 배율 sx, sy (화면 위쪽이 +)"""
    pts = [(X + (x0 + (x1 - x0) * i / n) * sx, Y - fn(x0 + (x1 - x0) * i / n) * sy) for i in range(n + 1)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"' + (f' stroke-dasharray="{dash}"' if dash else "") + '/>'

def axes(X, Y, left, right, up, down, xl="", yl=""):
    return (f'<line x1="{X-left}" y1="{Y}" x2="{X+right}" y2="{Y}" stroke="{DIM}" stroke-width="3" marker-end="url(#ad)"/>'
            f'<line x1="{X}" y1="{Y+down}" x2="{X}" y2="{Y-up}" stroke="{DIM}" stroke-width="3" marker-end="url(#ad)"/>'
            + (t(X + right - 6, Y + 40, xl, "lbS", "end") if xl else "") + (t(X + 14, Y - up + 22, yl, "lbS", "start") if yl else ""))

def grid(X, Y, step, nx, ny, c="#1f2532"):
    s = ""
    for i in range(-nx, nx + 1):
        s += f'<line x1="{X+i*step}" y1="{Y-ny*step}" x2="{X+i*step}" y2="{Y+ny*step}" stroke="{c}" stroke-width="2"/>'
    for j in range(-ny, ny + 1):
        s += f'<line x1="{X-nx*step}" y1="{Y+j*step}" x2="{X+nx*step}" y2="{Y+j*step}" stroke="{c}" stroke-width="2"/>'
    return s

def vec(X, Y, step, vx, vy, c=YEL, label="", dx=12, dy=-12, w=6):
    x2, y2 = X + vx * step, Y - vy * step
    lab = f'<text x="{x2+dx}" y="{y2+dy}" class="lbC" fill="{c}">{label}</text>' if label else ""
    return arrow(X, Y, x2, y2, c, w) + lab

def svg(body, h=420):
    mk = "".join(f'<marker id="{i}" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="{c}"/></marker>'
                 for i, c in (("ay", YEL), ("ab", BLUE), ("ag", GRN), ("ar", "#ff6b61"), ("ap", PUR), ("ad", DIM)))
    return f'''<svg viewBox="0 0 900 {h}" width="920" height="{h*920//900}">
<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="5" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{W}"/></marker>{mk}</defs>{body}</svg>'''

# ---------- 글자 조각 ----------

def F(a, b):
    """분수"""
    return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'

def M(rows, color=""):
    """행렬 (HTML)"""
    body = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in r) + "</tr>" for r in rows)
    return f'<span class="mat"{f" style=color:{color}" if color else ""}><table>{body}</table></span>'

def Y(s):
    return f'<span class="yel">{s}</span>'

def B(s):
    return f'<span class="blue">{s}</span>'

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
.blue{{color:{BLUE}}} .yel{{color:{YEL}}} .red{{color:#ff6b61}} .grn{{color:{GRN}}}
.card{{margin-top:44px;background:#11141b;border:3px solid #262c38;border-radius:28px;padding:34px 0 24px;display:flex;justify-content:center;align-items:center}}
.card.html{{min-height:440px;font-size:48px;font-weight:900;gap:30px;flex-wrap:wrap;padding:34px 40px}}
.formula{{margin-top:40px;background:rgba(246,195,67,.08);border:3px solid rgba(246,195,67,.55);border-radius:22px;padding:28px 30px;font-size:54px;font-weight:900;color:{YEL};text-align:center;line-height:1.4}}
.frac{{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;font-size:.82em;margin:0 6px}}
.frac>span:first-child{{border-bottom:4px solid currentColor;padding:0 8px}}
.mat{{display:inline-block;vertical-align:middle;border-left:5px solid currentColor;border-right:5px solid currentColor;border-radius:14px;padding:4px 10px;margin:0 6px}}
.mat td{{padding:2px 16px;text-align:center;font-weight:900}}
.ex{{margin-top:34px;font-size:40px;font-weight:700;line-height:1.5}}
.trap{{margin-top:30px;font-size:36px;font-weight:700;line-height:1.45;border-left:8px solid {RED};padding:6px 0 6px 22px;color:#f3d7d5}}
.trap b{{color:#ff6b61}}
sub{{font-size:.62em;vertical-align:-.25em}}
.chip{{border:3px solid #2f3746;border-radius:40px;padding:8px 24px;font-size:32px;font-weight:700}}
.foot{{position:absolute;left:76px;right:76px;bottom:46px;display:flex;justify-content:space-between;font-size:28px;color:{DIM};font-weight:700}}
svg .w{{fill:none;stroke:{W};stroke-width:5;stroke-linejoin:round;stroke-linecap:round}}
svg .pm{{fill:{W};font-size:30px;font-weight:900;text-anchor:middle}}
svg text{{font-family:'Noto Sans CJK KR'}}
svg .lb{{fill:{W};font-size:34px;font-weight:700}}
svg .lbS{{fill:{DIM};font-size:30px;font-weight:700}}
svg .lbY{{fill:{YEL};font-size:36px;font-weight:900}}
svg .lbC{{font-size:36px;font-weight:900}}
svg .lbB{{fill:{BLUE};font-size:40px;font-weight:900;text-anchor:middle}}
'''

# ---------- 카드 틀 ----------

def subs(html):
    """V_th → 아래 첨자 (SVG 글자는 tspan, 나머지는 <sub>)"""
    import re
    pat = re.compile(r"([A-Za-z])_([A-Za-z0-9]+)")
    html = re.sub(r"(<text[^>]*>)(.*?)(</text>)", lambda m: m.group(1) + pat.sub(
        r'\1<tspan baseline-shift="sub" font-size="70%">\2</tspan>', m.group(2)) + m.group(3), html)
    parts = re.split(r"(<[^>]+>)", html)
    return "".join(x if x.startswith("<") else pat.sub(r"\1<sub>\2</sub>", x) for x in parts)


def page(i, total, inner, series):
    inner = subs(inner)
    foot = f'<div class="foot"><span>@markovspace · {series}</span><span>{i} / {total}{"  →" if i < total else ""}</span></div>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="glow"></div><div class="wrap">{inner}</div>{foot}</body></html>'

def cover(tag, line1, line2, sub, visual, chips):
    chip = "".join(f'<span class="chip"><span class="yel">{k:02d}</span> {n}</span>' for k, n in enumerate(chips, 1))
    return (f'<div class="tag">{tag}</div><h1 style="margin-top:34px">{line1}<br><span class="blue">{line2}</span></h1>'
            f'<div class="sub" style="margin-top:18px">{sub}</div>' + vis(visual, 36) +
            f'<div style="margin-top:32px;display:flex;gap:14px;flex-wrap:wrap">{chip}</div>'
            f'<div class="ex" style="margin-top:30px;font-size:40px">📌 {Y("저장")}해 두고 시험 전에 넘겨 보세요</div>')

def vis(visual, top=44):
    if visual.lstrip().startswith("<svg"):
        return f'<div class="card" style="margin-top:{top}px">{visual}</div>'
    return f'<div class="card html" style="margin-top:{top}px">{visual}</div>'

def content(n, title, sub, visual, formula, ex, trap):
    return (f'<div><span class="num">{n:02d}</span><h2>{title}</h2></div><div class="sub">{sub}</div>' + vis(visual) +
            f'<div class="formula">{formula}</div><div class="ex">{ex}</div><div class="trap">{trap}</div>')

def summary(tag, rows, link="무료 사이트 '보이는 회로이론' 링크는 프로필에"):
    body = "".join(f"<div>{r}</div>" for r in rows)
    return (f'<div class="tag">{tag}</div>'
            f'<div class="card" style="margin-top:44px;flex-direction:column;align-items:flex-start;padding:34px 44px;gap:30px;font-size:44px;font-weight:700;line-height:1.4">{body}</div>'
            f'<h1 style="margin-top:80px;font-size:80px">📌 시험 전에 <span class="blue">저장</span></h1>'
            f'<div class="ex" style="font-size:40px;margin-top:20px">같은 과 친구 태그해 주세요</div>'
            f'<div class="sub" style="margin-top:44px;font-size:36px">🔗 {link}</div>')

def build(spec):
    """spec: dict(series, cover=dict, cards=[dict], summary=dict) → HTML 문자열 목록"""
    inner = [cover(**spec["cover"])] + [content(k, **c) for k, c in enumerate(spec["cards"], 1)] + [summary(**spec["summary"])]
    return [page(i, len(inner), h, spec["series"]) for i, h in enumerate(inner, 1)]
