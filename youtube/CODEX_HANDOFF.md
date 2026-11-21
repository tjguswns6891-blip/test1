# 영상 제작 방식 인수인계 (Codex용, 2026-11-19)

이 문서는 **영상을 만드는 방식 자체**만 정리한다(어떤 주제를 다뤘는지는 넣지 않았다).
짧은 규칙 요약은 저장소 맨 위 `AGENTS.md`, 예전 규칙 원문은 `youtube/HANDOFF.md`·`youtube/script_guide.md`, 업로드는 `publish/README.md`.
규칙이 서로 다르면 **이 문서 > AGENTS.md > HANDOFF.md** 순서로 따른다(최신 결정 반영).

---

## 0. 한눈에 보는 흐름

```
대본(lines.py) ─► script.json / long_tts.json ─► 음성(VoxCPM2, tempo 1.0, -16 LUFS)
      │                                              │
      └► make_cfg.py ─► long.json / shorts.json / reels.json
                                                     ▼
                         scene_dur.py ─► manim/dur.json (장면별 말 길이)
                                                     ▼
                         Manim 장면 렌더 (문장 1개 = 장면 1개, 말 길이에 맞춤)
                                                     ▼
                finish.py: 합성(longform.py / faceless.py) → 싱크 검사 → 효과음
                                                     ▼
                fixsync.py: 어긋난 자막 고쳐 다시 합성 (어긋남 0 까지)
                                                     ▼
          썸네일 V1·V2 + 커버 A~E (Manim 마지막 프레임 + HTML → Playwright)
                                                     ▼
       titles.md(제목안 3개·설명·챕터·태그·캡션) → 사용자에게 채팅으로 보여 주고 고르게 함
                                                     ▼
          승인 후: video-files 브랜치에 올리고 queue.json 에 항목 추가 → Actions 가 업로드
```

한 세트 = 롱폼 1(16:9, 약 2~4분) + 쇼츠 A~E(9:16, 17~30초) + 릴스 A~E(쇼츠와 같은 영상, 마지막 CTA만 다름) + 롱폼 썸네일 V1·V2 + 커버 A~E.

---

## 1. 환경 준비

### 도구 설치
`.claude/hooks/session-start.sh` 가 전부 설치한다: ffmpeg, LaTeX(Manim 수식), Blender, Manim(`~/.venvs/manim`), VoxCPM2(`~/.venvs/voxcpm`, CPU), faster-whisper(시스템 파이썬, `av<17` 고정), 한글 폰트(`~/.fonts/NotoSansCJKkr-Black/Bold.otf`), Playwright, simple-icons.
이 스크립트는 `CLAUDE_CODE_REMOTE=true` 일 때만 돈다. Codex 에서는:

```sh
CLAUDE_CODE_REMOTE=true bash .claude/hooks/session-start.sh   # 새 컨테이너에서 약 10분
```

- 네트워크: `download.pytorch.org`, `huggingface.co`(VoxCPM2·whisper 모델), `raw.githubusercontent.com`(폰트·음성 프롬프트), `astral.sh`(uv) 가 열려 있어야 한다.
- GPU 없음(CPU). 음성 생성이 가장 오래 걸린다(아래 7절 소요 시간).

### 음성 프롬프트(본인 목소리)
- `youtube/raw/voice/prompt_hook.wav` + `prompt_hook.txt`(그 음성의 정확한 대본). `raw/` 는 git 에 없어서 새 컨테이너에선 `video-files` 브랜치 `라플라스_작업중/voice/` 에서 받아 둔다(session-start.sh 가 받음).
- 다른 참고 음성을 쓰지 않는다(톤이 달라짐).

### 최신 도구가 있는 브랜치
가장 최근 세트의 제작 폴더와 최신 도구(`youtube/tools/scene_dur.py`, `--tempo` 옵션이 있는 `tts_voxcpm_para.py` 등)는 아직 기본 브랜치에 합쳐지지 않았고 **`claude/project-thread-gzrks8`** 에 있다.
새 세트를 시작할 땐 이 브랜치에서 새 작업 브랜치를 만들고, `youtube/depsrc/` 폴더를 통째로 복사해 새 폴더(예: `youtube/<새폴더>/`)로 시작하는 게 가장 빠르다(내용만 바꾸면 됨).

---

## 2. 폴더 구성 (세트 하나)

```
youtube/<세트>/
  README.md        이 세트 인수인계 (예제 숫자 검산, 만드는 순서, 상태)
  lines.py         대본 원본 → script.json, long_tts.json
  make_cfg.py      script.json → long.json, shorts.json, reels.json (장면 배치)
  tts_all.sh       음성 전부 (롱폼 조각 → 쇼츠/릴스 A~E)
  tts_redo.sh      특정 조각만 다른 seed 로 다시 (ONLY=조각 SEED=9)
  manim/scenes.py  모션그래픽 장면 (문장 1개 = class 1개)
  manim/one.sh, render_par.sh, speed.py, dur.json, speed.json
  img/  img_s/     렌더된 장면 (롱폼용 / 쇼츠용 NOSTEP)
  finish.py        합성 → 싱크 검사 → 효과음
  fixsync.py       싱크 어긋남 자동 수정
  thumbnail/       frames.sh, thumbs.html, render.js → thumb_V1/V2.png, cover_A~E.png
  titles.md        제목안·설명·챕터·태그·쇼츠 제목·릴스 캡션
youtube/raw/<세트>/  (git 제외) v/ 음성, long/ 롱폼 결과, reels/ shorts/ 결과
```

---

## 3. 대본 쓰기 (lines.py)

### 형식
- 롱폼: `S["I"]`(도입), `S["S1"]`~`S["S5"]`(STEP 1~5), `S["S6"]`(정리). 각 값은 `("STEP n · 장 제목", """여러 줄""")`.
- 쇼츠/릴스: `SH["A"]`~`SH["E"]` = `(["전기전자 주목!", "썸네일 둘째 줄 문구"], "챕터명", """여러 줄""")`. 5문장 안팎.
- 한 줄 = 한 문장 = 화면 장면 하나. 줄 형식: `자막 | tts` (tts 를 비우면 자막에서 `*` 를 뺀 것).
  - 자막은 아라비아 숫자·기호(`12V`, `8Ω`, `i_x`), tts 는 한글 읽기(`십이 볼트`, `팔 옴`, `아이 엑스`).
  - 강조는 자막 쪽에 `*단어*` (첫 대사 주제어 1개 + 문장마다 핵심 숫자·정답 단어 1~2개).
  - 음성 모델이 자주 틀리는 말은 미리 풀어 쓴다. 쉼표로 호흡을 준다.
- 파일 맨 위 주석에 **예제 숫자 검산**을 적는다(모든 숫자를 손으로 다시 계산해 맞는지 확인).
- CTA 는 `d` 에 고정:
  - `cta_reel`: sub `팔로우하고 댓글에 '회로' 남겨 주시면, DM으로 사이트 링크 보내 드릴게요.` / tts `팔로우하고 댓글에 회로 남겨 주시면, 디엠으로 사이트 링크 보내 드릴게요.` (선형대수는 '선대')
  - `cta_short`: `직접 만든 무료 사이트예요. 링크는 고정 댓글에 있어요.`
- `python3 lines.py` 를 돌리면 예상 길이(한글 6.3자/초)가 나온다. 롱폼 약 2분 30초~3분 30초, 쇼츠 20~25초를 목표로 문장 수를 조절한다.
- 롱폼 음성은 3문장씩 조각(`S1_0`, `S1_1`…)으로 나눠 만든다(lines.py 가 long_tts.json 으로 자동 분할).

### 롱폼 구성(고정 틀)
1. **도입(I)**: "전기전자 주목" + 반전 한 줄 → 최종 결과/풀 문제를 먼저 보여 줌 → "오늘은 다섯 단계로…" 로드맵.
2. **STEP 1~5**: 장마다 6문장 안팎. 각 장 첫 문장은 "첫 단계, / 두 번째, …" 로 시작. 중간에 짧은 질문("몇 V일까요?")을 하나씩.
3. 3~4장쯤에 **검산·정리 장면**(숨 돌리기, 앞 결과와 딱 맞아떨어짐).
4. **정리(S6)**: 핵심 3줄 → 무료 사이트 '보이는 회로이론' 안내 → "링크는 설명란… 다음 단원도 재생목록에".

### 쇼츠/릴스 A~E
- 롱폼의 장면을 재사용해 5개 클립을 만든다. 각자 주제 하나: 정의/함정/예외/풀이 요령/의외의 사실 같은 식으로 겹치지 않게.
- 첫 대사 3초 안에 "전기전자 주목" + 주제어 + 반전/질문. 중간에 결과가 나오는 한 장면(중간 보상).
- 마지막은 위 CTA(릴스/쇼츠가 다름).

---

## 4. 음성

```sh
python3 lines.py && python3 make_cfg.py
sh tts_all.sh            # 롱폼 조각 → A~E 의 reel/short 음성. 끝나면 v/LONG_DONE, v/ALL_DONE 생김
```

`tts_all.sh` 안의 실제 호출:
```sh
~/.venvs/voxcpm/bin/python tools/tts_voxcpm_para.py <세트>/long_tts.json raw/voice/prompt_hook.wav "$(cat raw/voice/prompt_hook.txt)" raw/<세트>/v --ver long --tempo 1.0
~/.venvs/voxcpm/bin/python tools/tts_voxcpm_para.py <세트>/script.json  raw/voice/prompt_hook.wav "$(cat raw/voice/prompt_hook.txt)" raw/<세트>/v --only A,B,C,D,E --tempo 1.0
```

- 문단을 한 번에 생성 → emphasize.py 후처리 자동: 강조 +1.5dB, 빠르기 1.0, -16 LUFS, 첫 대사 "전기전자 주목"만 살짝 밝게.
- 바꾸면 안 되는 값: 참고 음성 1개, seed 7(기본), tempo 1.0, -16 LUFS, `--hook-takes 1`, 단어 앞 쉼 없음.
- 오래 걸리니 `setsid nohup sh tts_all.sh &` 로 백그라운드 실행. **VoxCPM 2개 동시 실행 금지**(15GB 메모리 부족), **음성 생성 중 Manim 렌더 금지**(매우 느려짐).

### 발음 검사
- `tools/tts_check.py` 로 조각마다 받아쓰기(faster-whisper medium) → 대본과 일치도, 숫자·강조 단어·핵심 용어가 들어 있는지 확인. '다시'로 나온 조각만 `tts_redo.sh`(ONLY=조각 SEED=9)로 다시 만들고 둘 중 받아쓰기가 더 맞는 쪽을 쓴다.
- 받아쓰기 모델이 특정 고유명사를 늘 다르게 적는 경우(예: '테브난'→'태분한')는 음성 문제가 아니니 귀로 확인하고 넘어간다.

---

## 5. 모션그래픽 (Manim)

### 스타일 (manim/scenes.py 맨 위 그대로 쓰기)
- 16:9, 배경 `#111318`, 글자 `#eef0f3`, 흐린 글자 `#8d94a1`, 강조 노랑 `#ffc53d`
- 색: 파랑 `#6ea8ff`, 빨강 `#ff5d73`, 초록 `#3ddc97`, 주황 `#ff9f43`, 보라 `#c792ff` (STEP 1~5 색 순서 STEPC)
- 한글 `Noto Sans CJK KR` BOLD, 수식은 MathTex(amsmath). 카드(`card()`), 제목(`head()`), 오른쪽 위 **STEP n/5 ●●●○○ 진행 표시**(`step_tag()`).
- **핵심은 가운데에** 둔다(같은 장면을 세로 쇼츠에서도 가로에 맞춰 쓰기 때문). 쇼츠용 렌더는 `NOSTEP=1` 로 진행 표시를 뺀다.
- 회로 부품(저항·코일·전원·마름모 종속 전원 등) 그리는 함수가 scenes.py 에 있다. 복사해서 쓴다.

### 리텐션 규칙(장면 설계)
- **문장 1개 = 장면 1개**, 장면 길이는 그 문장의 실제 말 길이(dur.json)에 맞춰 `fill()` 로 채운다 → 멈춘 화면 없음.
- 장면 안에서 **2~4초마다 새 정보**가 하나씩: 소자 등장, 전류 화살표, 수식 한 줄, 값 강조(`beat()`), 마지막 몇 초는 테두리 강조(`pulse()`, 확대 없이).
- 금지: 장면 넘김 전환 효과, 확대·축소 반복(사용자가 싫어함), 4초 넘게 아무것도 안 바뀌는 구간, 소리 공백.
- 클래스 이름 = 장면 라벨. make_cfg.py 의 `LONG_VIS`(롱폼 장별 장면 목록, 문장 수와 같아야 함 — assert 있음)와 `VIS`(쇼츠 A~E 문장별 장면)에 적는다. 쇼츠 전용 장면은 `AQ`(A의 질문 훅)처럼 이름 짓는다.

### 렌더
```sh
python3 ../tools/scene_dur.py $PWD $PWD/../raw/<세트>/long      # 절대 경로. 음성 끝난 뒤 → manim/dur.json
sh manim/render_par.sh <쇼츠에 쓰는 장면들...>                   # 롱폼 전부 → img/, 인자로 준 장면 NOSTEP → img_s/ (4개 병렬)
python3 manim/speed.py                                           # 말보다 길게 렌더된 장면 → speed.json 배율 → 출력된 장면만 다시 렌더
```

---

## 6. 합성·검사·효과음

```sh
python3 finish.py long A B C D E          # 롱폼(longform.py) + 쇼츠/릴스(faceless.py) 합성 → sync_check → sfx
python3 fixsync.py long A_reel A_short B_reel ...   # 어긋난 자막만 고쳐 다시 합성(최대 3회). fixsync 가 finish 를 다시 부르니 그 뒤에 finish 를 또 돌리지 않는다
```

- **롱폼** `tools/longform.py`(16:9): long.json 의 섹션별 음성 조각을 잇고, 장 제목을 챕터로, 장면 영상을 문장 시각에 맞춰 깐다. 결과 `raw/<세트>/long/long.mp4`, `long.srt`.
- **쇼츠/릴스** `tools/faceless.py`(1080×1920): 위 제목 두 줄 + 가운데 장면 칸(1080×840) + 그 아래 한 줄 자막 + 끝 CTA 배너(릴스 "팔로우 + 댓글 '회로' / DM으로 사이트 링크 보내 드려요", 쇼츠 "무료 사이트 '보이는 회로이론' / 링크는 고정 댓글에").
- **자막**: 한두 문장씩 통째로, 받아쓰기 단어 시각 기준, 강조 단어 노란색, 위치 고정. `tools/sync_check.py` 로 자막마다 첫 어절이 들리는 시각과 비교 → **어긋남 0** 이어야 끝.
- **효과음** `tools/sfx.py`(youtube/sfx/kit, 반 볼륨): 롱폼은 첫 자막 intro + 장마다 첫 자막 trans. 쇼츠/릴스는 `1:intro, 3:visual, 중간:emph, CTA:cta` (30초당 4~8개 이내). 결과는 `*.sfx.mp4`.
- **끊김 검사** `tools/gap_check.py`(소리 공백).
- 마지막에 **완성본을 처음부터 직접 본다**(프레임 몇 장 뽑아 확인): 장면이 말과 맞는지, 정지 화면·늘어지는 곳이 없는지. 늘어지면 대본을 줄이고 다시 만든다.

---

## 7. 썸네일·커버

```sh
sh thumbnail/frames.sh       # 장면 마지막 프레임 → g_*.png(롱폼), gs_*.png(쇼츠)
node thumbnail/render.js     # thumbs.html → thumb_V1.png, thumb_V2.png(1280×720), cover_A~E.png(1080×1920)
```
- 롱폼 썸네일은 **두 안(V1·V2)** 을 만들어 사용자가 고른다(말이 없으면 V2 를 기본으로 씀).
- 썸네일 문구의 "N분 정리"는 thumbs.html 의 `MIN` 을 **실제 롱폼 길이**에 맞춘다(예: 3:21 → "3분 20초 정리"). 영상 안에는 길이를 쓰지 않는다.
- 인스타 커버는 올린 뒤 API 로 못 바꾸니 업로드 때 같이 넣는다.

### 소요 시간(클라우드 CPU 기준)
- 도구 설치 약 10분 · 롱폼 음성 약 50~60분(23조각) · 다시 만들 조각 몇 개 약 20분 · Manim 렌더 수 분 · 합성 약 2분.

---

## 8. 제목·설명·태그·캡션 (titles.md)

- **롱폼 제목**: 검색어를 맨 앞에. 제목안 3개(예: "<개념>, <반전 포인트> (N분 정리)", "<개념> N분 정리 | 부제", "회로이론 <개념> — <훅>").
- **롱폼 설명**: 2~3문장 요약 → 무료 사이트 링크(https://tjguswns6891-blip.github.io/test1/circuit/) → 챕터(0:00 도입, STEP 1~5, 정리 — 실제 시각) → 해시태그 3개. 태그 20~25개.
- **쇼츠 제목**: 검색어 먼저 + `#shorts #회로이론 #세부주제` 3개. 쇼츠 태그 20~25개(세부 주제 동의어 7~8개 + 공통: 회로이론, 전기회로, 회로해석, 전기전자, 전자공학, 전기공학, 전기기사, 공대생, 공대, 대학생, 전공공부, 시험공부, 중간고사, 기말고사, shorts…), 500자 안.
- **쇼츠 설명**: 첫 줄 롱폼 링크(`{long:ID}` 로 대기열이 채움), 둘째 줄 무료 사이트 링크. 카테고리 교육, 아동용 아님, AI 표시 끔.
- **릴스 캡션**: `전기전자 주목⚡ <한 줄 반전>. <핵심 1~2문장>. 시험 전에 저장 📌 (또는 같은 과 친구 태그해 주세요) 팔로우하고 댓글에 '회로' 남겨 주시면 DM으로 사이트 링크 보내 드릴게요. #회로이론 #세부 #세부 #전기기사 #공대생` (해시태그 정확히 5개).
- 재생목록: 회로이론 쇼츠·롱폼은 "회로이론 한눈에", 선형대수는 "선형대수 한눈에", 증시는 "증시 브리핑".
- 이 내용은 사용자에게 **채팅 본문으로** 보여 준다(파일 첨부 대신).

---

## 9. 결과물 전달·업로드

### 전달
- 완성되면 결과 파일을 사용자에게 보여 줄 곳에 둔다(이전엔 프로젝트 공유 폴더 `<세트>/`: `롱폼_<주제>.mp4`, `롱폼.srt`, `쇼츠_A~E.mp4`, `릴스_A~E.mp4`, `thumb_V1/V2.png`, `cover_A~E.png`).
- 사용자에게 보낼 것: 롱폼 길이·챕터, 썸네일 V1/V2, 제목안 3개, 쇼츠 제목 5개, 릴스 캡션 5개 → **썸네일·제목·업로드 시각을 고르게** 한다. 승인 전엔 올리지 않는다.

### 업로드 (승인 후)
1. 완성 파일을 `video-files` 브랜치의 새 폴더에 커밋.
2. `video-files` 의 `queue.json` `items` 에 롱폼 1개(`kind: long`) + 클립 5개(`kind: clip`, `after: 롱폼 id`, `short`·`reel`·`cover`·`yt_title`·`yt_description`·`yt_tags`·`ig_caption`·`playlist`)를 `status: pending` 으로 추가. 형식은 `publish/README.md` 5절.
3. `publish-queue.yml` 이 하루 3번(9:30/12:30/17:30 KST 실행 → 10/13/18시 항목, 1시간 앞까지) 시간이 된 항목을 올린다. 한 번 실행에 롱폼 1 + 클립 1 까지만.
4. **"지금 다 올려"** 요청이면: 항목의 `at` 을 지금으로 넣고 `publish-queue.yml` 을 클립마다 한 번씩 수동 실행(앞 실행이 끝난 뒤 다음).
5. 결과(`status` done/failed, `youtube` ID, `instagram` ID)가 queue.json 에 기록된다. failed 는 고친 뒤 pending 으로 되돌린다.
6. 롱폼이 올라가면 다음 편 설명에 이전 편 링크, 쇼츠 설명 첫 줄에 롱폼 링크가 들어갔는지 확인.
- 단건 업로드·제목/썸네일 수정·재생목록·채널 설정은 `publish.yml` 의 `platform` 모드(`youtube`, `instagram`, `youtube-update`, `youtube-playlist`, `youtube-plan`, `youtube-list` …) — `publish/README.md` 참고.
- 유튜브 API 는 검수 전이면 비공개로만 올라갈 수 있다. 쇼츠 "관련 동영상" 연결과 고정 댓글은 API 가 없어 사용자가 Studio 에서 직접 한다.

### 올린 뒤
- 3일째 `video-files/stats/날짜.json`(18시 실행이 자동 수집)으로 조회·저장·공유·평균 시청 시간을 보고, 빠진 구간을 다음 대본에 반영한다.

---

## 10. 체크리스트 (올리기 전)
- [ ] 예제 숫자 검산 주석과 화면·자막 숫자가 모두 같다
- [ ] 음성: 참고 음성 1개, seed 동일, tempo 1.0, -16 LUFS, 발음 검사 통과
- [ ] 릴스 5개 모두 마지막에 "팔로우하고 댓글에 '회로' 남겨 주시면, DM으로 사이트 링크 보내 드릴게요" + 배너
- [ ] 쇼츠 5개 마지막은 "링크는 고정 댓글" 안내
- [ ] 싱크 어긋남 0, 소리 공백 없음, 4초 넘는 정지 화면 없음
- [ ] 영상 안에 길이 표기 없음, 썸네일 "N분 정리" = 실제 길이
- [ ] 썸네일 V1·V2, 커버 A~E, titles.md 준비
- [ ] 사용자 승인(썸네일·제목·시각) 받음
