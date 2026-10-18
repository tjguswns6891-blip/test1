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
