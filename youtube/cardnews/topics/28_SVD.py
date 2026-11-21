from cards import *

def ell(cx, cy, a, b, ang, c):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{a}" ry="{b}" transform="rotate({ang} {cx} {cy})" fill="{c}" fill-opacity=".15" stroke="{c}" stroke-width="5"/>'
steps = svg(f'<circle cx="110" cy="210" r="70" fill="{W}" fill-opacity=".08" stroke="{W}" stroke-width="5"/>' + t(110, 330, "원", "lbS") +
            arrow(195, 210, 245, 210, BLUE) + t(220, 180, "Vᵀ", "lbB") +
            f'<circle cx="330" cy="210" r="70" fill="{GRN}" fill-opacity=".1" stroke="{GRN}" stroke-width="5"/>' + arrow(330, 210, 380, 160, GRN, 4) + t(330, 330, "회전", "lbS") +
            arrow(415, 210, 465, 210, BLUE) + t(440, 180, "Σ", "lbB") +
            ell(570, 210, 95, 35, 0, YEL) + t(570, 330, "늘리기", "lbS") +
            arrow(680, 210, 730, 210, BLUE) + t(705, 180, "U", "lbB") +
            ell(810, 210, 95, 35, -40, PUR) + t(810, 330, "회전", "lbS"), 380)
img = svg("".join(f'<rect x="{80+k*160}" y="{110}" width="120" height="120" rx="10" fill="{YEL}" fill-opacity="{0.9/(k+1):.2f}" stroke="{YEL}" stroke-width="3"/>' +
                  t(140 + k * 160, 280, f"σ{['₁','₂','₃','₄','₅'][k]}", "lbY") for k in range(5)) + t(450, 350, "큰 σ 몇 개만 남기면 대부분의 정보가 남아요", "lbS"), 380)

SPEC = dict(
    series="선형대수 실험실",
    cover=dict(tag="공대생 주목!", line1="모든 행렬은", line2="회전 → 늘리기 → 회전", sub="SVD, 선형대수의 끝판왕", visual=steps,
               chips=["뜻", "σ 구하기", "고유값분해와 차이", "어디에 쓰나"]),
    cards=[
        dict(title="특이값 분해", sub="어떤 행렬이든 세 단계로 쪼개져요", visual=steps,
             formula="A = U Σ Vᵀ",
             ex=f"U, V = {Y('회전(직교)')}, Σ = {Y('축 방향 늘리기')}",
             trap="<b>기억</b> 원이 타원이 되고, 타원의 반지름들이 σ"),
        dict(title="σ 구하기", sub="AᵀA의 고유값에 루트", visual=M([[3, 0], [4, 5]]) + "→ AᵀA =" + M([[25, 20], [20, 25]], YEL),
             formula="σ = √(AᵀA의 고유값)",
             ex=f"고유값 45, 5 &nbsp;→&nbsp; {Y('σ₁ = 3√5 ≈ 6.7, σ₂ = √5 ≈ 2.2')}",
             trap="<b>검산</b> σ₁ × σ₂ = |det A| = 15 ✓"),
        dict(title="고유값분해와 차이", sub="SVD는 모든 행렬에 돼요", visual=('<table style="font-size:44px;border-collapse:collapse">'
                     '<tr><td style="padding:12px 30px">고유값분해 PDP⁻¹</td><td class=red style="padding:12px 30px">정사각 + 조건</td></tr>'
                     '<tr><td style="padding:12px 30px">특이값분해 UΣVᵀ</td><td class=grn style="padding:12px 30px">아무 행렬 OK</td></tr></table>'),
             formula="직사각 행렬도 OK &nbsp;·&nbsp; σ ≥ 0",
             ex=f"대칭 양의 정부호 행렬이면 {Y('둘이 같아요')}",
             trap="<b>함정</b> 고유값은 음수 가능, 특이값은 항상 0 이상"),
        dict(title="어디에 쓰나", sub="큰 σ만 남기면 압축이 돼요", visual=img,
             formula="A ≈ σ₁u₁v₁ᵀ + σ₂u₂v₂ᵀ + …",
             ex=f"{Y('이미지 압축')}, PCA, 추천 시스템이 다 이 원리",
             trap="<b>기억</b> 버린 σ들이 곧 오차 크기"),
    ],
    summary=dict(tag="한 줄 요약", link="무료 사이트 '선형대수 실험실' 링크는 프로필에", rows=[
        f"{Y('A = UΣVᵀ')} 회전·늘리기·회전",
        f"{Y('σ')} = √(AᵀA 고유값)",
        f"{Y('모든 행렬')} 가능, σ ≥ 0",
        f"{Y('큰 σ만')} → 압축·PCA"]),
)

CAPTION = """공대생 주목🧮 모든 행렬은 회전 → 늘리기 → 회전
특이값 분해 A = UΣVᵀ. 직사각 행렬도 예외 없이 쪼개져요.
σ 구하는 법이랑 이미지 압축에 쓰이는 원리까지 넘겨 보세요 👉

📌 시험 전에 저장, 같은 과 친구 태그해 주세요
🔗 무료 사이트 '선형대수 실험실' 링크는 프로필에

#선형대수 #SVD #특이값분해 #공대생 #공대수학"""
