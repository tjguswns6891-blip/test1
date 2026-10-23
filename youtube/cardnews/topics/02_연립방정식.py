from cards import *

S = 50
lines2 = svg(grid(450, 220, S, 8, 4) + axes(450, 220, 400, 400, 200, 200) +
             curve(lambda x: 3 - x, -1.4, 4.4, 450, 220, S, S, BLUE) +
             curve(lambda x: x - 1, -2.4, 4.4, 450, 220, S, S, GRN) +
             dot(550, 170, YEL) + t(565, 155, "(2, 1)", "lbY", "start") +
             t(130, 110, "x + y = 3", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{BLUE}"') +
             t(700, 90, "x − y = 1", "lbC", "start").replace('class="lbC"', f'class="lbC" fill="{GRN}"'), 440)

def plane(pts, c):
    return f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width="4"/>'

planes = svg(plane([(140, 300), (560, 300), (760, 200), (340, 200)], BLUE) +
             plane([(300, 380), (420, 40), (600, 60), (480, 400)], GRN) +
             plane([(180, 120), (620, 360), (760, 300), (320, 60)], PUR) +
             dot(450, 230, YEL) + t(470, 222, "(1, 2, 3)", "lbY", "start"), 420)

A = M([[1, 1, 1], [0, 1, 1], [0, 0, 1]]) + M([["x"], ["y"], ["z"]], BLUE) + "=" + M([[6], [5], [3]], YEL)

def mini(X, l1, l2, label):
    s = f'<rect x="{X}" y="40" width="250" height="250" rx="16" fill="none" stroke="#262c38" stroke-width="3"/>'
    s += f'<line x1="{X+20}" y1="{l1[0]}" x2="{X+230}" y2="{l1[1]}" stroke="{BLUE}" stroke-width="6"/>'
    s += f'<line x1="{X+20}" y1="{l2[0]}" x2="{X+230}" y2="{l2[1]}" stroke="{GRN}" stroke-width="6"' + (' stroke-dasharray="14 12"' if l1 == l2 else "") + '/>'
    return s + t(X + 125, 350, label, "lbY")

kinds = svg(mini(30, (270, 60), (60, 270), "딱 1개") + dot(155, 165, YEL) + mini(325, (250, 110), (200, 60), "0개 (평행)") +
            mini(620, (240, 90), (240, 90), "무한 (겹침)"), 380)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="연립방정식 3개는", line2="사실 평면 3개", sub="식을 그림으로 보면 해가 보여요", visual=planes,
               chips=["식 = 직선", "식 = 평면", "Ax = b", "해의 개수"]),
    cards=[
        dict(title="식 하나 = 직선", sub="미지수 2개짜리 식은 평면 위의 직선이에요", visual=lines2,
             formula="해 = 두 직선이 만나는 점",
             ex=f"예) x + y = 3, x − y = 1 &nbsp;→&nbsp; {Y('(2, 1)')}",
             trap="<b>함정</b> 계산이 막히면 그려 보세요. 평행이면 해가 없어요"),
        dict(title="식 하나 = 평면", sub="미지수가 3개면 식 하나가 공간 속 평면", visual=planes,
             formula="해 = 세 평면이 다 지나는 점",
             ex=f"예) x+y+z=6, y+z=5, z=3 &nbsp;→&nbsp; {Y('(1, 2, 3)')}",
             trap="<b>팁</b> 아래 식부터 z → y → x 순서로 넣으면 끝 (후진 대입)"),
        dict(title="Ax = b", sub="계수만 모으면 행렬 하나로 끝나요", visual=A,
             formula="A x = b",
             ex=f"A = 계수, x = {B('미지수')}, b = {Y('오른쪽 숫자')}",
             trap="<b>기억</b> 행 하나 = 식 하나, 열 하나 = 미지수 하나"),
        dict(title="해의 개수", sub="딱 1개, 0개, 무한, 이 세 가지뿐", visual=kinds,
             formula="det A ≠ 0 &nbsp;⇔&nbsp; 해가 딱 하나",
             ex="det A = 0 이면 &nbsp;→&nbsp; 없거나 무한",
             trap="<b>함정</b> 없음 / 무한 구분은 A만 보면 안 되고 b까지 봐야 해요"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('식 하나')} = 직선(2D) / 평면(3D)",
        f"{Y('해')} = 도형이 전부 만나는 점",
        f"{Y('Ax = b')} 행은 식, 열은 미지수",
        f"{Y('det A ≠ 0')} 이면 해가 딱 하나"]),
)

CAPTION = """공대생 주목🧮 연립방정식 3개는 사실 평면 3개예요
식 하나가 도형 하나, 해는 그 도형들이 만나는 점.
그래서 해는 1개, 0개, 무한 셋 중 하나뿐이에요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #연립방정식 #행렬 #공대생 #공대수학"""
