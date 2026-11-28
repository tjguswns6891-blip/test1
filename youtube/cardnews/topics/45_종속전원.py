from cards import *

def dia(x, y1, y2, cur=True, c=YEL, lab=""):
    m = (y1 + y2) / 2; r = 40
    s = wire((x, y1), (x, m - r)) + wire((x, m + r), (x, y2))
    s += f'<polygon points="{x},{m-r} {x+r},{m} {x},{m+r} {x-r},{m}" fill="#11141b" stroke="{c}" stroke-width="5"/>'
    s += (f'<line x1="{x}" y1="{m+20}" x2="{x}" y2="{m-20}" stroke="{c}" stroke-width="5" marker-end="url(#ay)"/>' if cur else
          f'<text x="{x}" y="{m-6}" class="pm" fill="{c}">+</text><text x="{x}" y="{m+28}" class="pm">−</text>')
    return s + (t(x + 54, m + 12, lab, "lbY", "start") if lab else "")

syms = svg(dia(250, 60, 340, False, lab="μ v_x") + t(250, 395, "종속 전압원", "lbS") + dia(620, 60, 340, True, lab="β i_x") + t(620, 395, "종속 전류원", "lbS") +
           f'<circle cx="80" cy="120" r="30" class="w"/>' + t(80, 190, "독립", "lbS"), 420)

ck = svg(vsrc(120, 80, 340) + wire((120, 80), (190, 80)) + res(190, 80, 420, 80) + wire((420, 80), (650, 80)) + res(420, 80, 420, 340) + dia(650, 80, 340, True, BLUE) +
         wire((650, 340), (120, 340)) + dot(420, 80) + dot(420, 340) + t(80, 222, "12V", "lb", "end") + t(305, 45, "2Ω") + t(450, 222, "2Ω", "lb", "start") +
         t(420, 50, "V", "lbY") + t(700, 222, "0.25 V", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"') +
         t(450, 270, "v_x = V", "lbS", "start"), 400)

tbl = ('<table style="font-size:40px;border-spacing:30px 8px">' +
       "".join(f'<tr><td class="yel">{a}</td><td>{b}</td><td class="blue">{c}</td></tr>' for a, b, c in
               (("VCVS", "전압이 정하는 전압원", "μ v_x"), ("CCVS", "전류가 정하는 전압원", "r i_x"),
                ("VCCS", "전압이 정하는 전류원", "g v_x"), ("CCCS", "전류가 정하는 전류원", "β i_x"))) + "</table>")

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="혼자서는 값이 안 정해지는", line2="종속 전원", sub="회로 안 다른 전압·전류를 따라 바뀌어요", visual=syms,
               chips=["네 종류", "기호", "마디 해석", "테브난 주의"]),
    cards=[
        dict(title="네 종류", sub="무엇이 무엇을 정하느냐로 나눠요", visual=tbl,
             formula="VCVS · CCVS · VCCS · CCCS",
             ex=f"제어하는 값 v_x, i_x는 {Y('회로 안 다른 곳')}에 있어요",
             trap="<b>기억</b> 트랜지스터·옵앰프 모델이 다 종속 전원이에요"),
        dict(title="기호", sub="동그라미는 독립, 마름모는 종속", visual=syms,
             formula="◇ 마름모 = 종속 전원",
             ex=f"안에 {Y('화살표')}면 전류원, {Y('+ −')}면 전압원",
             trap="<b>함정</b> 옆에 적힌 식(β i_x)을 놓치면 그냥 독립 전원으로 착각"),
        dict(title="마디 해석", sub="일단 독립 전원처럼 쓰고, 제어값을 미지수로", visual=ck,
             formula=f"{F('V − 12', '2')} + {F('V', '2')} − 0.25V = 0",
             ex=f"0.75V = 6 &nbsp;→&nbsp; {Y('V = 8V')}",
             trap="<b>순서</b> KCL 쓰기 → 제어값(v_x)을 마디 전압으로 바꿔 넣기"),
        dict(title="테브난 주의", sub="종속 전원이 있으면 R_th 구하는 법이 달라요", visual=syms,
             formula=f"R_th = {F('v_test', 'i_test')}",
             ex=f"단자에 {Y('시험 전원')}을 넣고 전압 ÷ 전류",
             trap="<b>함정</b> 독립 전원만 끄기. 종속 전원은 절대 끄지 않아요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('◇')} 다른 값이 정하는 전원 (4종류)",
        f"화살표 {Y('전류원')}, + − {Y('전압원')}",
        f"해석: 제어값을 {Y('미지수로')} 바꿔 넣기",
        f"테브난: 종속 전원은 {Y('켜 둔 채')} 시험 전원"]),
)

CAPTION = """전기전자 주목⚡ 혼자서는 값이 안 정해지는 전원
종속 전원은 회로 안 다른 전압·전류를 따라 바뀌어요. 트랜지스터 모델이 전부 이거예요.
네 종류, 마디 해석 예제(V = 8V), 테브난 함정까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #종속전원 #마디해석 #전기전자 #공대생"""
