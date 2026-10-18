# 작업 인수인계 (2026-10-17, 이전 세션 정리)

새 세션은 이 파일부터 읽는다. 사용자와는 한국어로 대화한다.

## 채널과 사이트
- 증시: 금리·주가 50년 https://tjguswns6891-blip.github.io/test1/invest · 미국 테마 강도 https://tjguswns6891-blip.github.io/test1/themes
- 공부 채널: 선형대수 실험실, 보이는 회로이론(로컬 사본 youtube/raw/circuit_site.html — raw 는 git 제외라 새 세션엔 없음, 필요하면 사이트에서 다시 받기)
- 인스타 @markovspace, 유튜브 (Metricool brand blogId 7418408, Asia/Seoul. 무료 한도 월 20건 → 이번 달은 사용자가 직접 올림)

## 이 프로젝트(유튜브, 인스타 운영)로 옮긴 것 (2026-10-18)
- 브랜치 `claude/project-thread-7sdum7` 에 흩어진 작업을 모음: usage-history(최신 도구·RLC·푸리에) + wizardly-cray(10/12 증시, EDITING.md·setup.sh, 로고) + ig-comment-dm(인스타 댓글→DM 워커 `ig-dm-worker/`)
- 새 세션 자동 설치(.claude/hooks/session-start.sh)는 youtube/setup.sh 내용까지 포함. 네트워크가 막혀 실패한 단계는 건너뛰고 나머지를 계속함
- ⚠️ VoxCPM2(torch: download.pytorch.org, 모델: huggingface.co)와 whisper 모델(huggingface.co)은 클라우드 환경 네트워크가 열려 있어야 받음. 영상 세션들은 '대본' 환경에서 돌았음 → 프로젝트 설정에서 그 환경을 고르면 됨
- 목소리 샘플(raw/voice/prompt_hook.*)은 훅이 video-files 브랜치에서 자동으로 꺼냄

## 늘 지키는 규칙
- 릴스 해시태그 5개 · 제목/캡션/태그는 채팅으로 · 효과음 절반 볼륨, 30초당 4~8개 · 사이트 녹화는 다크 모드
- 릴스 마지막(2026-10-18 바뀜, DM 자동화 안 함): "시험 전에 저장해 두세요. 직접 만든 무료 사이트, 링크는 프로필에 있어요" + 배너 "시험 전에 저장 + 친구 태그 / 사이트 링크는 프로필에". 쇼츠 마지막: "링크는 고정 댓글"
- 첫 대사: 회로 = "전기전자 주목", 선형대수 = "공대생 주목"
- 영상에 'AI 음성' 표기 넣지 않음, 올릴 때 AI 표시 끔(사용자 선택)
- 자막: 한두 문장씩 통째로, 목소리와 싱크(받아쓰기 단어 시각 기준). 강조는 대본에 *단어*
- 음성: 첫 대사는 5번 만들어 고르고(tts_voxcpm_para.py --hook-takes 5), 발음은 받아쓰기로 검사 → youtube/script_guide.md 맨 위 '표준 제작 순서'
- 말 빠르기 ×0.95 (≈7.2음절/초, 원본 음성 대비): 쇼츠·릴스 emphasize --tempo 0.95, 롱폼 longform tempo 0.95 (롱폼 조각은 --tempo 1.0 으로 만듦). 1.12 는 너무 빠르고 0.9 는 조금 느림 (2026-10-18 사용자)
- 소리 크기: sfx.py 가 마지막에 -16 LUFS(최고 -1.5 dBTP)로 맞춤 (예전 -19~-23 은 작았음, 2026-10-18 사용자). 효과음 넣지 않는 영상도 sfx.py 를 거치거나 같은 loudnorm 적용
- 썸네일·커버에는 얼굴(인물 사진 person.png) 넣지 않음. 영상은 그대로: 쇼츠·릴스 faceless.py --avatar ../profile/profile_real_B.png (2026-10-18 사용자)
- 키 값 절대 출력 금지 · PR 은 요청할 때만 · 커밋 끝에 Co-Authored-By 줄

## 성장 전략 규칙 (2026-10-18 사용자 결정, Metricool 데이터 기반 · 앞으로 모든 영상에 적용)
근거: 회로이론 릴스 9천~1.9만 회(공유 많음), 선형대수 1.5천~9천 회, 증시 릴스 중간값 약 270회(저장·공유 거의 0). 쇼츠 1만 회 날에도 유튜브 구독 10~15명.

인스타
- 주제: 회로이론·선형대수가 메인. 증시는 주 1~2개까지, 패션·잡주제는 올리지 않음
- 첫 줄(캡션·영상 첫 대사): "전기전자 주목⚡"/"공대생 주목" + 한 줄 반전 (예: "돌아오는 선엔 전류 0?", "이 복잡한 회로, 저항 하나로 끝납니다")
- 하루 1~2개, 평일 오전 10시 또는 저녁 6시. 하루에 몰아서 여러 개 올리지 않음 (10/14 10개 → 개당 조회수 하락)
- 캡션 마무리: 저장·공유 유도 ("시험 전에 저장 📌", "같은 과 친구 태그해 주세요"). 새 캡션의 링크 안내는 "링크는 프로필" (DM 자동화 안 함. 이미 올린 캡션은 고치지 않음)
- 교재 목차 순서 시리즈로 이어 가기 (12월 기말고사 시즌 겨냥)

유튜브
- 쇼츠 제목: 검색어를 맨 앞에 + 해시태그 3개. 예: "테브난 정리, 저항 하나로 끝 #shorts #회로이론 #테브난"
- 단원마다 롱폼(10분 안팎 단원 정리)을 만들고, 그 단원 쇼츠는 같은 단원 재생목록에 넣음 (publish.yml youtube-playlist)
- 쇼츠 설명 첫 줄에 해당 단원 롱폼 링크. 쇼츠의 "관련 동영상" 연결은 API로 안 돼서 사용자가 Studio에서 지정
- 유튜브에선 증시 쇼츠도 1~3천 회로 회로 쇼츠와 비슷해서 계속 올림. 대신 "증시 브리핑" 재생목록으로 분리하고, 채널 소개·키워드는 "공대 수학·회로" 중심 (publish.yml youtube-channel)
- 새 영상을 올리면 같은 주제 재생목록에 넣고 설명 첫 줄에 모아보기 링크를 넣음. 한 번에 적용: publish/plans/*.json 을 만들고 publish.yml platform=youtube-plan, video=그 경로
- 재생목록 (2026-10-18 생성): 회로이론 한눈에 PLIXOZZwVtrbM · 선형대수 한눈에 PLJZMddUWRkXs · 증시 브리핑 PLS8bubpmpgw8. 2024년 3DS·화폐 영상과 패션 영상은 넣지 않음

## 도구 (youtube/tools)
- tts_voxcpm_para.py(문단 음성) · emphasize.py(강조) · hook_text_check.py · tts_check.py(발음 검사)
- faceless.py(9:16 쇼츠/릴스) · longform.py(16:9 롱폼) · shorts.py · sfx.py(효과음) · compose.py · thumbnail.py
- sync_check.py(완성 영상 자막 싱크 검사) · check/synccheck.py(자막 싱크) · check/chk_long.py(발음) · check/plan_stock.py(효과음 계획)
- 새 세션 자동 설치: .claude/hooks/session-start.sh (작업 브랜치에 있음 → 기본 브랜치에 합쳐야 모든 세션에 적용)

## 결과물 보관
- 완성 영상·썸네일: video-files 브랜치 (증시_0929~1017, 회로, 선형대수, 클라우드소마 등)
- 원본 촬영본: 사용자 구글 드라이브 (tools/fetch_drive.py 로 받음). 중간 파일(raw/)은 git 에 없고 다시 만들 수 있음

## 진행 중
- RLC 롱폼(라플라스 후속) + 쇼츠3·릴스3: 대본·Manim 10장면·썸네일·커버 준비됨 (youtube/rlc), 음성 만들기부터 이어서
- 2포트 회로 롱폼(푸리에 후속, 회로 17장) + 쇼츠3·릴스3: 대본·롱폼 음성 조각·Manim 10장면 1080p·사이트 녹화 스크립트·합성 설정·썸네일(V2로 확정)·커버 3종 준비 (youtube/twoport). 다음은 `sh youtube/twoport/tts.sh` 로 음성('대본' 환경 필요) → 발음 검사 → 합성
- 푸리에 급수 롱폼(RLC 후속) + 쇼츠3·릴스3: 대본·음성 스크립트·Manim 11장면·녹화 스크립트 미리 준비 (youtube/fourier)
- 라플라스 롱폼 + 쇼츠3·릴스3: 완료 (video-files `라플라스/`, 기록 youtube/laplace/이어하기.md)
- ⚠️ test1 저장소는 공개. video-files '라플라스_작업중/voice/' 에 사용자 목소리 샘플이 올라가 있음 → 사용자 결정(2026-10-18): 그대로 둠
