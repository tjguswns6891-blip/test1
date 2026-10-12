# 릴스 2차 대본 페이지(index.html) 생성. 대본 문구는 REELS 에서 고친다.
import pathlib, html

HERE = pathlib.Path(__file__).parent
SP = pathlib.Path("/tmp/claude-0/-home-user-test1/0ea7d802-46f0-5b44-9052-f2947e7fbf85/scratchpad")
STYLE = (HERE / "page_style.css").read_text()
SCRIPT = (HERE / "page_script.js").read_text()

DM_L = '<b>팔로우</b>하고 댓글에 <b>"선대"</b> 남겨 주시면, / <b>DM으로 사이트 링크</b> 보내 드릴게요.'
DM_C = '<b>팔로우</b>하고 댓글에 <b>"회로"</b> 남겨 주시면, / <b>DM으로 사이트 링크</b> 보내 드릴게요.'
SHORTS = '직접 만든 무료 사이트예요. / <b>링크는 고정 댓글</b>에 있어요.'

REELS = [
  dict(id="L1", site="linalg", title="벡터가 3개인데 3차원을 못 채운다?", sec="3.4 일차독립과 일차종속",
       hook="05 상식 파괴형", cover=["벡터 3개인데", "공간을 못 채운다?"], time="약 28초",
       lines=[
         "<b>벡터가 세 개</b>인데, / 3차원을 다 <b>못 채울</b> 수도 있어요.",
         "세 벡터로 상자를 만들어 볼게요. / 상자에 <b>부피</b>가 있으면 / 세 방향이 다 살아 있는 거예요. / 이게 <b>일차독립</b>.",
         "그런데 세 번째 벡터를 / 앞의 두 벡터를 섞어서 만들면, / 상자가 <b>평면으로 납작</b>해져요.",
         "벡터는 세 개인데, / 채우는 공간은 평면 하나뿐인 거죠. / 이게 <b>일차종속</b>이에요.",
         "그래서 <b>랭크가 벡터 개수보다 작으면 종속</b>. / 정의 외우지 말고 / 이 그림으로 기억하세요.",
       ], dm=DM_L,
       rows=[("0–3초", "벡터가 세 개인데…", "Blender 3D: 빛나는 세 벡터와 유리 상자가 천천히 회전 + 첫 화면 문구"),
             ("3–9초", "상자를 만들어… 일차독립", "Blender: 상자 부피 강조 → 사이트 3.4 녹화(벡터 입력, 'span = ℝ³ 전체', 일차독립 배지)"),
             ("9–16초", "세 번째 벡터를 섞어서… 납작", "Blender: 셋째 벡터가 평면으로 내려가며 상자가 납작해지는 장면 (핵심 컷)"),
             ("16–21초", "채우는 공간은 평면 하나… 일차종속", "사이트 3.4: 셋째 열을 1열+2열로 바꿔 입력 → 'span = 평면', 일차종속 배지"),
             ("21–25초", "랭크가 벡터 개수보다 작으면", "HyperFrames 카드: 랭크 2 < 벡터 3 → 종속"),
             ("25–30초", "CTA", "팔로우 + 댓글 '선대' → DM 배너")],
       figs=[("img/l1-span.jpg", "Blender · 상자 → 납작 (전/후)"), ("img/l-rank.jpg", "HyperFrames · 랭크 판정 카드"), ("shots/indep.jpg", "사이트 3.4 일차독립")]),
  dict(id="L2", site="linalg", title="이 빨간 선 위 벡터는 전부 0이 됩니다", sec="4.1 선형 변환: 커널과 상공간",
       hook="17 디테일 분석형", cover=["이 빨간 선 위 벡터는", "전부 0이 됩니다"], time="약 28초",
       lines=[
         "이 <b>빨간 선</b> 위에 있는 벡터들은 / 행렬을 곱하는 순간 / <b>전부 0</b>이 돼요.",
         "변환 애니메이션을 눌러 볼게요. / 평면 전체가 / <b>직선 하나로 눌려</b> 버리죠.",
         "이때 원점으로 사라지는 방향이 <b>커널</b>, / 결과가 모이는 이 초록 직선이 <b>상공간</b>이에요.",
         "2차원에서 / 한 방향이 지워지고, 한 방향이 남았으니까 / <b>1 더하기 1은 2</b>. / 이게 차원 정리, 랭크-널리티예요.",
         "많이 지울수록, / 남는 건 줄어드는 거죠.",
       ], dm=DM_L,
       rows=[("0–3초", "이 빨간 선 위에…", "Manim: 격자 위 빨간 커널 직선과 벡터들, 첫 화면 문구"),
             ("3–9초", "변환 애니메이션을 눌러…", "사이트 4.1 녹화: det 0 행렬 입력 → '변환 애니메이션' 클릭, 격자가 직선으로 눌림"),
             ("9–15초", "커널… 상공간", "Manim: 평면이 눌리며 커널 벡터가 원점으로, 초록 상공간 직선 등장"),
             ("15–23초", "1 더하기 1은 2", "Manim: dim ker + dim range = 2 → 1 + 1 = 2 카운트"),
             ("23–26초", "많이 지울수록…", "얼굴 크게"),
             ("26–30초", "CTA", "팔로우 + 댓글 '선대' → DM 배너")],
       figs=[("img/l2-kernel.jpg", "Manim · 커널과 상공간"), ("shots/lintrans.jpg", "사이트 4.1 선형 변환")]),
  dict(id="L3", site="linalg", title="같은 점인데 좌표가 두 개?", sec="4.3 기저 변환과 닮음 행렬",
       hook="22 빠른 이해형", cover=["같은 점인데", "좌표가 두 개?"], time="약 28초",
       lines=[
         "같은 점인데 / 좌표가 <b>(2, 1)</b>이기도 하고 / <b>(1, 1)</b>이기도 해요.",
         "좌표는 사실 / <b>어떤 자로 쟀느냐</b>예요. / 왼쪽은 우리가 아는 바둑판, / 오른쪽은 b₁, b₂로 만든 <b>기울어진 바둑판</b>이에요.",
         "점은 그대로인데 / 자가 바뀌니까 숫자가 바뀌는 거죠. / 이 번역기가 <b>전이행렬 P</b>예요.",
         "같은 변환도 자를 바꾸면 / <b>P⁻¹AP</b>, 닮음 행렬로 바뀌어요. / 그래서 고유벡터로 자를 잡으면 / 행렬이 <b>제일 단순</b>해져요.",
       ], dm=DM_L,
       rows=[("0–3초", "같은 점인데…", "Manim: 점 x 와 '(2, 1)' / '(1, 1)' 두 라벨이 번갈아"),
             ("3–11초", "어떤 자로 쟀느냐…", "사이트 4.3 녹화: 표준 좌표(왼쪽)와 B 좌표(오른쪽) 나란히, b₂ 끌기"),
             ("11–17초", "점은 그대로인데… 전이행렬 P", "Manim: 표준 격자가 기울어진 격자로 바뀌고 좌표 숫자가 (2,1)→(1,1)"),
             ("17–25초", "P⁻¹AP…", "HyperFrames 카드: [T]_B = P⁻¹AP, 'B좌표 → 표준 → 변환 → B좌표' 화살표"),
             ("25–30초", "CTA", "팔로우 + 댓글 '선대' → DM 배너")],
       figs=[("img/l3-basis.jpg", "Manim · 같은 점, 다른 자"), ("img/l-similarity.jpg", "HyperFrames · 닮음 행렬 카드"), ("shots/cob.jpg", "사이트 4.3 기저 변환")]),
  dict(id="C1", site="circuit", title="복잡한 회로, 전원 하나 저항 하나로", sec="4장 회로 정리 · 테브난, 최대 전력",
       hook="26 쉬운 방법 제시형", cover=["전기전자 주목!", "복잡한 회로, 저항 하나로"], time="약 28초",
       lines=[
         "<b>전기전자</b> 주목. / 이 복잡한 회로, / <b>전원 하나, 저항 하나</b>로 줄일 수 있어요.",
         "부하만 떼어 놓고 보면 / 나머지 회로 전체가 / <b>9볼트 전원 하나, 75옴 저항 하나</b>로 바뀌어요. / 이게 <b>테브난 등가 회로</b>예요.",
         "버튼을 눌러서 바꿔 봐도 / 부하에 흐르는 전류는 <b>85.7밀리암페어, 그대로</b>죠.",
         "그리고 부하 저항을 / 테브난 저항이랑 똑같이 <b>75옴</b>으로 맞추면 / 이 곡선 꼭대기, <b>최대 전력</b>이 나와요.",
       ], dm=DM_C,
       rows=[("0–3초", "전기전자 주목…", "HyperFrames: 원래 회로가 그려지고 '복잡한 회로 → 전원 하나 + 저항 하나' 제목"),
             ("3–11초", "부하만 떼어 놓고…", "HyperFrames: 점선 상자 → 수식 V_Th = 9V, R_Th = 75Ω → 회로가 테브난 등가로 바뀜"),
             ("11–16초", "버튼을 눌러서…", "사이트 4장 녹화: '원래 회로' ↔ '테브난 등가' 버튼, I_L = 85.7 mA 확대"),
             ("16–24초", "75옴으로 맞추면… 최대 전력", "Manim: 부하 전력 곡선을 점이 타고 가다 75Ω 꼭대기 270 mW에서 번쩍 → 사이트 R_L 슬라이더 녹화"),
             ("24–30초", "CTA", "팔로우 + 댓글 '회로' → DM 배너")],
       figs=[("img/c1-thevenin.jpg", "HyperFrames · 테브난 등가로 접히는 회로"), ("img/c1-maxpower.jpg", "Manim · 최대 전력 곡선"), ("shots/ch4.jpg", "사이트 4장")]),
  dict(id="C2", site="circuit", title="전선 세 가닥, 돌아오는 선엔 전류 0", sec="12장 3상 회로",
       hook="05 상식 파괴형", cover=["전기전자 주목!", "돌아오는 선이 필요 없다?"], time="약 28초",
       lines=[
         "<b>전기전자</b> 주목. / 전선 세 가닥에 전류가 흐르는데, / 돌아오는 선에는 <b>전류가 0</b>이에요.",
         "발전소는 전압 세 개를 / <b>120도씩</b> 어긋나게 만들어요. / 이게 <b>3상</b>이에요.",
         "세 페이저를 / 꼬리에 머리를 이어 붙이면 / 딱 <b>원점으로 돌아오죠</b>. / 매 순간 <b>합이 0</b>. / 그래서 평형이면 중성선에 전류가 안 흘러요.",
         "한 상만 크기를 바꿔 볼게요. / 합이 0이 깨지면서 / 바로 <b>중성선 전압</b>이 생겨요.",
       ], dm=DM_C,
       rows=[("0–3초", "전기전자 주목…", "Blender 3D: 회전자가 돌며 세 코일이 차례로 빛나는 3상 발전기 + 첫 화면 문구"),
             ("3–8초", "120도씩 어긋나게…", "Blender 계속 → 사이트 12장 녹화(세 페이저 회전 + 세 사인파)"),
             ("8–17초", "꼬리에 머리를… 합이 0", "Manim: 세 페이저를 이어 붙여 원점으로 닫힘, 세 파형의 합 = 0 노란 직선"),
             ("17–24초", "한 상만 크기를 바꿔…", "사이트 12장: 'c상 크기 비율' 슬라이더 1 → 0.6, 합 ≠ 0 '불평형' 배지 → '평형으로 되돌리기'"),
             ("24–30초", "CTA", "팔로우 + 댓글 '회로' → DM 배너")],
       figs=[("img/c2-generator.jpg", "Blender · 3상 발전기"), ("img/c2-threephase.jpg", "Manim · 세 페이저의 합 = 0"), ("shots/ch12.jpg", "사이트 12장")]),
  dict(id="C3", site="circuit", title="전압을 바꾸는 건 '감은 횟수'", sec="13장 자기 결합 회로 · 이상 변압기",
       hook="17 디테일 분석형", cover=["전기전자 주목!", "전압은 '감은 횟수'로 바뀐다"], time="약 28초",
       lines=[
         "<b>전기전자</b> 주목. / 전압을 바꾸는 건 / 코일을 <b>감은 횟수</b>예요.",
         "철심에 코일 두 개를 감고 / 한쪽에 교류를 걸면, / <b>자속</b>이 철심을 따라 돌면서 / 반대쪽 코일에 전압이 생겨요.",
         "1차를 <b>200번</b>, 2차를 <b>50번</b> 감으면 / 100볼트가 25볼트, / 딱 <b>4분의 1</b>이 돼요.",
         "대신 전류는 <b>4배</b>. / 그래서 <b>전력은 그대로</b>예요. / 직류를 걸면? / 자속이 변하지 않아서 / 전압이 안 생겨요.",
       ], dm=DM_C,
       rows=[("0–3초", "전기전자 주목…", "Blender 3D: 철심 + 촘촘한 1차 코일, 성긴 2차 코일 클로즈업 + 첫 화면 문구"),
             ("3–11초", "자속이 철심을 따라…", "Blender: 초록 자속 입자가 철심을 돌고 코일이 교류로 깜빡임 → 사이트 13장 녹화"),
             ("11–17초", "200번, 50번… 4분의 1", "Manim: 200회 ÷4 → 50회, 100V ÷4 → 25V"),
             ("17–24초", "전류는 4배… 전력은 그대로", "Manim: 625 mA ×4 → 2.5 A, '전력 100V×625mA = 25V×2.5A' / 사이트 N₂ 슬라이더 50→100 녹화"),
             ("24–30초", "CTA", "팔로우 + 댓글 '회로' → DM 배너")],
       figs=[("img/c3-transformer.jpg", "Blender · 변압기와 자속"), ("img/c3-turns.jpg", "Manim · 감은 횟수 비율"), ("shots/ch13.jpg", "사이트 13장")]),
]


def reel(r):
    e = html.escape
    figs = "".join(f'<figure><img src="{src}" alt="{e(cap)}" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>' for src, cap in r["figs"])
    rows = "".join(f"<tr><td>{a}</td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in r["rows"])
    lines = "".join(f"<p>{l}</p>" for l in r["lines"])
    return f'''
<article class="scene" id="r{r["id"]}">
  <div class="shead"><span class="sno">릴스 {r["id"]}</span><h2>{e(r["title"])}</h2><span class="time">{r["time"]}</span><button class="done">읽음</button></div>
  <div class="meta"><span class="pill">{e(r["sec"])}</span><span class="pill hk">후킹 {e(r["hook"])}</span><span class="pill cv">첫 화면: {e(" / ".join(r["cover"]))}</span></div>
  <div class="script">{lines}
    <p class="cta"><span class="tag">릴스</span>{r["dm"]}</p>
    <p class="cta"><span class="tag">쇼츠</span>{SHORTS}</p>
  </div>
  <div class="shots">{figs}</div>
  <div class="edit"><strong>장면 구성</strong>
    <div class="tbl"><table><thead><tr><th>시간</th><th>말</th><th>화면</th></tr></thead><tbody>{rows}</tbody></table></div>
  </div>
</article>'''


def part(site):
    return "".join(reel(r) for r in REELS if r["site"] == site)


page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>사이트 소개 릴스 2탄</title>
<meta name="description" content="선형대수 실험실·보이는 회로이론 사이트의 지난번에 소개하지 않은 파트로 만든 릴스·쇼츠 대본 6개">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@500&display=swap">
{STYLE}
</head>
<body>
<div class="wrap">
<header class="bar">
  <nav class="tabs" aria-label="구역">
    <button data-tab="linalg" aria-pressed="true">선형대수 3개</button>
    <button data-tab="circuit" aria-pressed="false">회로이론 3개</button>
    <button data-tab="edit" aria-pressed="false">편집 노트</button>
  </nav>
  <div class="tools">
    <button id="prompter" aria-pressed="false">읽기 모드</button>
    <button id="smaller" aria-label="글자 작게">가−</button>
    <button id="bigger" aria-label="글자 크게">가+</button>
  </div>
</header>
<div class="intro">
  <h1>사이트 소개 릴스 2탄 · 지난번에 안 나온 파트만</h1>
  <p>선형대수는 지난번에 1·2·5·6·7장을 보여 줬으니 이번엔 <b>3장 벡터 공간, 4장 선형 변환</b>. 회로이론은 2·7·8·9·14·16장을 보여 줬으니 이번엔 <b>4장 회로 정리, 12장 3상, 13장 변압기</b>예요.
  릴스마다 <b>얼굴만</b> 따로 찍어 주세요(각 25~30초). 마지막에 <b>릴스용 문장</b>과 <b>쇼츠용 문장</b>을 이어서 둘 다 읽으면, 편집 때 릴스판·쇼츠판을 따로 뽑을게요.</p>
  <div class="legend"><span><i class="sw" style="background:var(--warn)"></i>굵은 노란 글씨 = 힘줘서</span><span>/ = 잠깐 쉬기</span><span><i class="sw" style="background:var(--cue)"></i>장면 구성 = 읽지 않음</span></div>
</div>
<section class="part" id="part-linalg">{part("linalg")}</section>
<section class="part" id="part-circuit" hidden>{part("circuit")}</section>
<section class="part note" id="part-edit" hidden>
  <h3>새 도구로 만드는 그래픽</h3>
  <ul>
    <li><b>Blender 3D</b>: L1 상자가 납작해지는 일차종속, C2 3상 발전기, C3 변압기 자속. 다크 배경 + 사이트 색(주황·청록·보라 / 전압 파랑·전류 주황).</li>
    <li><b>Manim</b>(3Blue1Brown 스타일): L2 커널, L3 기저 변환, C1 최대 전력 곡선, C2 페이저 합 0, C3 감은 횟수 비율.</li>
    <li><b>HyperFrames</b>: C1 테브난 등가로 접히는 회로, L1 랭크 판정 카드, L3 닮음 행렬 카드. 첫 화면 문구는 쇼츠 편집기에서 크게 넣어요.</li><li>그래픽 미리보기 영상(mp4)은 video-files 브랜치 <b>사이트소개_릴스2/그래픽</b> 폴더에 있어요.</li>
    <li>사이트 화면은 촬영본을 받은 뒤 다크 모드로 직접 조작하며 녹화해서 말에 맞춰 넣어요.</li>
  </ul>
  <h3>화면 배치 (9:16)</h3>
  <ul>
    <li>위쪽 칸: 그래픽·사이트 녹화(16:9 카드가 꽉 차게), 아래: 얼굴(지난번처럼 얼굴을 낮고 작게).</li>
    <li>자막: 리지팍 스타일 한 줄(흰 굵은 글씨, 그림자, 단어별 등장), 한 자리 고정.</li>
    <li>효과음: 상황별 키트, 볼륨은 예전의 절반. 첫 문장 intro · 핵심 컷 emph · 그래픽 등장 visual · 마지막 cta.</li>
  </ul>
  <h3>릴스판 / 쇼츠판</h3>
  <ul>
    <li><b>인스타 릴스</b>: 마지막 3초 '팔로우 + 댓글 → DM' 배너. 키워드는 선형대수 <b>"선대"</b>, 회로 <b>"회로"</b>.</li>
    <li><b>유튜브 쇼츠</b>: 같은 영상에서 마지막 문장만 쇼츠용으로 바꾸고 '사이트 링크는 고정 댓글' 배너.</li>
  </ul>
  <h3>후킹 (henry_upnomad 26패턴 적용)</h3>
  <ul>
    <li>L1·C2 상식 파괴형, L2·C3 디테일 분석형, L3 빠른 이해형, C1 쉬운 방법 제시형. 첫 문장 = 첫 자막 = 커버 문구.</li>
  </ul>
  <h3>사이트에서 확인한 숫자</h3>
  <div class="tbl"><table><thead><tr><th>릴스</th><th>대본 속 숫자</th><th>사이트 실제</th></tr></thead><tbody>
    <tr><td>L3</td><td>(2, 1) ↔ (1, 1)</td><td>4.3 기본값 b₁ = (1, 0), b₂ = (1, 1), x = (2, 1) → [x]_B = (1, 1)</td></tr>
    <tr><td>C1</td><td>9V, 75Ω, 85.7 mA, 최대 270 mW</td><td>4-1 기본값 Vs 12V, R₁ 100Ω, R₂ 300Ω, R_L 30Ω → V_Th 9V, R_Th 75Ω, I_L 85.7 mA, 최대 270 mW</td></tr>
    <tr><td>C2</td><td>120°, 합 0, 중성선</td><td>12-1 '세 상의 합 = 0 V 평형', c상 크기 비율·위상 오차 슬라이더, '평형으로 되돌리기'</td></tr>
    <tr><td>C3</td><td>200회 / 50회, 100V → 25V, 625 mA → 2.5 A</td><td>13-1 기본값 V₁ 100V, N₁ 200, N₂ 50, R_L 10Ω → V₂ 25V, I₂ 2.5A, I₁ 625 mA</td></tr>
  </tbody></table></div>
</section>
</div>
{SCRIPT}
</body>
</html>'''
(HERE / "index.html").write_text(page)
print("ok", len(page))
