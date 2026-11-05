from cards import *

def coil(x, n, y0=120, step=36):
    s = ""
    for i in range(n):
        y = y0 + i * step
        s += f'<path d="M{x},{y} a26,{step/2} 0 0 1 0,{step}" class="w"/>' if x > 450 else f'<path d="M{x},{y} a26,{step/2} 0 0 0 0,{step}" class="w"/>'
    return s

def tx(n1=6, n2=3, l1="", l2="", r=""):
    y1, y2 = 120, 120 + 6 * 36
    s = (f'<rect x="405" y="80" width="90" height="300" rx="10" fill="#1d2330" stroke="{DIM}" stroke-width="3"/>' +
         coil(390, n1) + coil(510, n2, 120 + (6 - n2) * 18) +
         wire((390, 120), (220, 120)) + wire((390, y2), (220, y2)) + vsrc(220, 120, y2, ac=True) +
         wire((510, 120 + (6 - n2) * 18), (700, 120 + (6 - n2) * 18), (700, 120)) + wire((510, 120 + (6 - n2) * 18 + n2 * 36), (700, 120 + (6 - n2) * 18 + n2 * 36), (700, y2)) +
         res(700, 120, 700, y2) + t(390, 60, "N₁", "lbB") + t(520, 60, "N₂", "lbB") + t(160, 245, l1, "lbY", "end") + t(745, 245, l2 or r, "lbY", "start"))
    return svg(s, 420)

SPEC = dict(
    series="보이는 회로이론",
    cover=dict(tag="전기전자 주목!", line1="전압은", line2="'감은 횟수'로 바뀐다", sub="변압기, 비율 하나로 전압·전류·저항까지", visual=tx(l1="220V", l2="11V"),
               chips=["전압비", "전류비", "전력 보존", "임피던스 변환"]),
    cards=[
        dict(title="전압비", sub="감은 횟수 비율 그대로 전압이 바뀌어요", visual=tx(l1="220V", l2="V₂"),
             formula=f"{F('V₂', 'V₁')} = {F('N₂', 'N₁')}",
             ex=f"예) 220V, 1000회 : 50회 &nbsp;→&nbsp; {Y('11V')}",
             trap="<b>함정</b> 직류는 변압이 안 돼요. 자속이 변해야 유도되니까"),
        dict(title="전류비", sub="전류는 반대로, 감은 횟수에 반비례", visual=tx(l1="I₁", l2="I₂ = 2A"),
             formula=f"{F('I₂', 'I₁')} = {F('N₁', 'N₂')}",
             ex=f"예) 1000 : 50 에서 I₂ = 2A &nbsp;→&nbsp; I₁ = {Y('0.1A')}",
             trap="<b>함정</b> 전압비랑 분수가 거꾸로예요"),
        dict(title="전력 보존", sub="이상적 변압기는 전력을 그대로 넘겨요", visual=tx(l1="22W", l2="22W"),
             formula="V₁ I₁ = V₂ I₂",
             ex=f"220V × 0.1A = 11V × 2A = {Y('22W')}",
             trap="<b>기억</b> 전압을 올리면 전류는 줄어요. 공짜는 없어요"),
        dict(title="임피던스 변환", sub="1차에서 보면 부하 저항이 비율의 제곱만큼 커 보여요", visual=tx(l1="800Ω?", r="8Ω"),
             formula=f"Z_in = ({F('N₁', 'N₂')})² Z_L",
             ex=f"예) 10 : 1, 스피커 8Ω &nbsp;→&nbsp; {Y('800Ω')}으로 보임",
             trap="<b>함정</b> 저항은 비율의 제곱! 그냥 비율 곱하면 틀려요"),
    ],
    summary=dict(tag="한 줄 요약", rows=[
        f"{Y('전압')} N₂/N₁ 배",
        f"{Y('전류')} N₁/N₂ 배 (거꾸로)",
        f"{Y('전력')} 그대로 V₁I₁ = V₂I₂",
        f"{Y('저항')} (N₁/N₂)² 배로 보임"]),
)

CAPTION = """전기전자 주목⚡ 전압은 '감은 횟수'로 바뀝니다
1000회 : 50회면 220V가 11V로. 대신 전류는 거꾸로 20배.
전력 보존이랑 임피던스 변환(제곱!)까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '보이는 회로이론' 링크는 프로필에

#회로이론 #변압기 #전기전자 #공대생 #공대공부"""
