# 유튜브·인스타 공식 API 업로드

`video-files` 브랜치에 있는 완성 영상을 GitHub Actions의 **Publish video** 워크플로로 유튜브와 인스타에 올립니다.
돈이 드는 서비스는 쓰지 않습니다 (YouTube Data API, Instagram API, GitHub Actions 모두 무료 범위).

- 코드: `upload.py` (파이썬 표준 라이브러리만 사용), `.github/workflows/publish.yml`
- 토큰은 저장소 **Settings → Secrets and variables → Actions → New repository secret** 에만 넣습니다. 채팅이나 파일에 붙여 넣지 마세요.

## 1. 유튜브 (한 번만)

1. console.cloud.google.com → 새 프로젝트 만들기 (이름 예: `markov-upload`)
2. **API 및 서비스 → 라이브러리** → `YouTube Data API v3` 사용 설정
3. **OAuth 동의 화면** → 외부 → 앱 이름·이메일 입력 → 테스트 사용자에 내 구글 계정 추가 → 저장 후 **앱 게시(프로덕션으로 푸시)**
   - 테스트 상태로 두면 7일마다 토큰이 만료돼요. 프로덕션으로 바꾸면 "확인되지 않은 앱" 경고만 뜨고 계속 쓸 수 있어요.
4. **사용자 인증 정보 → OAuth 클라이언트 ID 만들기** → 유형 `웹 애플리케이션` → 승인된 리디렉션 URI에 `https://developers.google.com/oauthplayground` 추가 → 클라이언트 ID·보안 비밀 복사
5. developers.google.com/oauthplayground → 오른쪽 위 톱니바퀴 → **Use your own OAuth credentials** 체크 → 4번 값 입력
6. 왼쪽 입력칸에 `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube` 입력 → Authorize APIs → 유튜브 채널 계정으로 로그인·허용 → **Exchange authorization code for tokens** → `Refresh token` 복사
7. 저장소 Secrets에 3개 추가: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`

**중요: 검수 전에는 API로 올린 영상이 전부 비공개로 잠깁니다.** 유튜브 정책상 2020년 이후 만든 API 프로젝트는
[YouTube API 감사(audit) 신청](https://support.google.com/youtube/contact/yt_api_form)을 통과해야 공개·예약 공개가 됩니다 (무료, 보통 몇 주).
통과 전에는 비공개로 올라간 영상을 YouTube Studio에서 공개로 바꾸면 됩니다.
썸네일 적용은 채널 전화번호 인증이 되어 있어야 합니다.

## 2. 인스타 (한 번만)

자동 DM 때 만든 Meta 앱을 그대로 씁니다 (`ig-dm-worker/README.md`).

1. developers.facebook.com → 앱 → 사용 사례 → Instagram 맞춤 설정 → 권한에 `instagram_business_content_publish` 추가
2. 같은 화면에서 markovspace **토큰 다시 생성** (새 권한이 들어간 토큰이어야 해요)
3. 저장소 Secrets에 `IG_ACCESS_TOKEN` 추가
4. 토큰은 60일 뒤 만료됩니다. 새로 만들어 같은 이름으로 덮어쓰면 됩니다.

내 계정에 내 게시물을 올리는 건 앱 검수 없이 개발 모드에서도 됩니다. 하루 최대 50개까지 올릴 수 있어요.

## 3. 올리기

Actions 탭 → **Publish video** → Run workflow → 영상 경로·제목·설명 입력. Claude가 대신 실행할 수도 있습니다.
결과 링크는 실행 화면의 Summary에 나옵니다.

## 4. 채널 관리 모드 (publish.yml platform)

- `youtube-list`: 채널 소개·키워드, 모든 영상(ID·길이·조회수·제목), 재생목록을 로그로 보여 줌 (video 칸은 `-`)
- `youtube-update`: 영상 하나의 제목·설명·태그 수정 (video = 영상 ID)
- `youtube-playlist`: 제목으로 재생목록을 찾거나 만들고 영상 ID들을 넣음 (video = 쉼표로 이은 ID)
- `youtube-channel`: 채널 소개(description)·키워드(tags) 수정. 채널 이름·배너는 API로 못 바꿈
- `youtube-plan`: `publish/plans/*.json` 하나로 채널 소개·재생목록·쇼츠 설명 첫 줄을 한 번에 적용 (형식은 upload.py 의 youtube_plan 설명)
- 쇼츠의 "관련 동영상" 연결은 API가 없어서 YouTube Studio에서 직접 지정

## 5. 업로드 대기열 (자동 업로드)

`.github/workflows/publish-queue.yml` 이 하루 3번(10시·13시·18시, GitHub 사정으로 몇십 분 늦을 수 있음) `video-files` 브랜치의 `queue.json` 을 읽어 시간이 된 항목을 올립니다.
제작 세션은 영상을 `video-files` 에 올린 뒤 `queue.json` 의 `items` 에 항목을 추가하기만 하면 됩니다.

```json
{"playlists": {"circuit": "PLIXOZZwVtrbM", "linalg": "PLJZMddUWRkXs", "stock": "PLS8bubpmpgw8"},
 "items": [
  {"id": "L1", "kind": "long", "at": "2026-10-21T10:00:00+09:00", "video": "L1/long.sfx.mp4", "thumbnail": "L1/thumb_V1.png",
   "yt_title": "...", "yt_description": "...", "yt_tags": "a,b", "playlist": "회로이론 한눈에 (쇼츠 + 단원 정리)", "status": "pending"},
  {"id": "L1-1", "kind": "clip", "after": "L1", "at": "2026-10-21T10:00:00+09:00",
   "short": "L1/쇼츠_1.sfx.mp4", "reel": "L1/릴스_1.sfx.mp4", "cover": "L1/cover_1.png",
   "yt_title": "... #shorts #회로이론 #세부", "yt_description": "📺 전체 정리: {long:L1}\n...", "yt_tags": "...",
   "ig_caption": "...", "playlist": "회로이론 한눈에 (쇼츠 + 단원 정리)", "status": "pending"}]}
```

- 한 번 실행에 롱폼 1개 + 클립 1개까지만 올립니다. 클립은 `after` 의 롱폼이 올라간 뒤에만 올라갑니다.
- 파일이 아직 없으면 건너뛰고 다음 실행 때 다시 봅니다. 그래서 제작이 늦으면 클립이 한 칸씩 밀립니다.
- 설명·캡션의 `{long:L1}` 은 그 롱폼 주소, `{playlist:circuit}` 은 재생목록 주소로 바뀝니다.
- 결과(`status`: done/failed, `youtube`, `instagram`, `error`)는 같은 파일에 기록됩니다. failed 는 다시 시도하지 않으니 고친 뒤 pending 으로 되돌립니다.
