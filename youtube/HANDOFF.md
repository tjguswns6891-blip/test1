# 작업 인수인계 (2026-10-17, 이전 세션 정리)

새 세션은 이 파일부터 읽는다. 사용자와는 한국어로 대화한다.

## 채널과 사이트
- 증시: 금리·주가 50년 https://tjguswns6891-blip.github.io/test1/invest · 미국 테마 강도 https://tjguswns6891-blip.github.io/test1/themes
- 공부 채널: 선형대수 실험실, 보이는 회로이론(로컬 사본 youtube/raw/circuit_site.html — raw 는 git 제외라 새 세션엔 없음, 필요하면 사이트에서 다시 받기)
- 인스타 @markovspace, 유튜브 (Metricool brand blogId 7418408, Asia/Seoul. 무료 한도 월 20건 → 이번 달은 사용자가 직접 올림)

## 늘 지키는 규칙
- 릴스 해시태그 5개 · 제목/캡션/태그는 채팅으로 · 효과음 절반 볼륨, 30초당 4~8개 · 사이트 녹화는 다크 모드
- 릴스 마지막: "팔로우하고 댓글에 '키워드' 남겨 주시면, DM으로 사이트 링크 보내 드릴게요" + 배너. 쇼츠 마지막: "링크는 고정 댓글"
- 첫 대사: 회로 = "전기전자 주목", 선형대수 = "공대생 주목"
- 영상에 'AI 음성' 표기 넣지 않음, 올릴 때 AI 표시 끔(사용자 선택)
- 자막: 한두 문장씩 통째로, 목소리와 싱크(받아쓰기 단어 시각 기준). 강조는 대본에 *단어*
- 음성: 첫 대사는 5번 만들어 고르고(tts_voxcpm_para.py --hook-takes 5), 발음은 받아쓰기로 검사 → youtube/script_guide.md 맨 위 '표준 제작 순서'
- 말 빠르기 ×0.95 (≈7.2음절/초, 원본 음성 대비): 쇼츠·릴스 emphasize --tempo 0.95, 롱폼 longform tempo 0.95 (롱폼 조각은 --tempo 1.0 으로 만듦). 1.12 는 너무 빠르고 0.9 는 조금 느림 (2026-10-18 사용자)
- 키 값 절대 출력 금지 · PR 은 요청할 때만 · 커밋 끝에 Co-Authored-By 줄

## 도구 (youtube/tools)
- tts_voxcpm_para.py(문단 음성) · emphasize.py(강조) · hook_text_check.py · tts_check.py(발음 검사)
- faceless.py(9:16 쇼츠/릴스) · longform.py(16:9 롱폼) · shorts.py · sfx.py(효과음) · compose.py · thumbnail.py
- check/synccheck.py(자막 싱크) · check/chk_long.py(발음) · check/plan_stock.py(효과음 계획)
- 새 세션 자동 설치: .claude/hooks/session-start.sh (작업 브랜치에 있음 → 기본 브랜치에 합쳐야 모든 세션에 적용)

## 결과물 보관
- 완성 영상·썸네일: video-files 브랜치 (증시_0929~1017, 회로, 선형대수, 클라우드소마 등)
- 원본 촬영본: 사용자 구글 드라이브 (tools/fetch_drive.py 로 받음). 중간 파일(raw/)은 git 에 없고 다시 만들 수 있음

## 진행 중
- 라플라스 롱폼 + 쇼츠3·릴스3: 완료 (video-files `라플라스/`, 기록 youtube/laplace/이어하기.md)
- ⚠️ test1 저장소는 공개. video-files '라플라스_작업중/voice/' 에 사용자 목소리 샘플이 올라가 있음 → 사용자 결정(2026-10-18): 그대로 둠
