# 인스타 댓글 키워드 → 자동 DM

게시물에 `링크`, `사이트`, `link` 중 하나가 들어간 댓글이 달리면, 댓글 단 사람에게 그 게시물에 맞는 사이트 링크를 DM으로 보내고 댓글에 "DM으로 보내드렸어요!" 답글을 남깁니다.

- 서버: Cloudflare Workers 무료 플랜 (하루 10만 요청)
- 코드: `worker.js` 한 파일. 키워드·게시물별 링크·DM 문구는 파일 위쪽에서 수정
- 같은 댓글에는 한 번만 보냄 (KV `DM_SENT`), 내 계정 댓글은 무시
- 인스타 규칙: 댓글 단 지 7일 안에만, 댓글 하나에 DM 1통

## 설정 순서

### 1. 인스타그램
설정 → 메시지 및 스토리 답장 → 메시지 컨트롤 → 연결된 도구 → **메시지 액세스 허용** 켜기

### 2. Meta 앱 권한 + 새 토큰
developers.facebook.com → 앱 → 사용 사례 → Instagram 맞춤 설정 → 권한에 추가:
- `instagram_business_manage_comments`
- `instagram_business_manage_messages`

추가한 뒤 **토큰을 다시 생성**합니다 (기존 토큰엔 새 권한이 없음).
같은 화면의 **Instagram 앱 시크릿**도 확인해 둡니다.

### 3. Cloudflare Worker 만들기
1. dash.cloudflare.com 가입 → Workers 및 Pages → 생성 → Worker 생성 → 이름 `ig-dm` → 배포
2. **코드 편집** → 내용을 모두 지우고 `worker.js`를 붙여넣기 → 배포
3. 저장소 → **KV** → 네임스페이스 생성 `DM_SENT`
4. Worker → 설정 → **바인딩** → KV 네임스페이스 추가: 변수 이름 `DM_SENT`
5. Worker → 설정 → **변수 및 비밀** → 유형 "비밀"로 3개 추가
   - `IG_ACCESS_TOKEN`: 2번에서 새로 만든 토큰
   - `IG_APP_SECRET`: Instagram 앱 시크릿
   - `VERIFY_TOKEN`: 아무 문자열 (예: `markov-dm-2026`)
6. Worker 주소 확인: `https://ig-dm.<내계정>.workers.dev`

### 4. Meta webhook 연결
앱 → 사용 사례 → Instagram 맞춤 설정 → **웹훅 구성**
- 콜백 URL: 3-6의 Worker 주소
- 토큰 확인: 3-5의 `VERIFY_TOKEN`과 같은 값
- 확인 및 저장 → 필드 목록에서 **comments 구독**
- 같은 화면의 계정 목록에서 markovspace **웹훅 구독 켜기**

### 5. 테스트
개발 모드에서는 **앱 역할이 있는 계정의 댓글만** webhook이 옵니다. 앱 역할 → Instagram 테스터에 내 다른 계정을 추가하고 수락한 뒤, 그 계정으로 게시물에 "링크"라고 댓글을 달아 DM이 오는지 확인합니다.
로그는 Cloudflare Worker → 로그(실시간)에서 볼 수 있습니다.

### 6. 모든 사람에게 열기 (앱 검수)
일반 팔로워 댓글에 반응하려면 Meta 앱 검수(App Review)에서 위 두 권한의 **Advanced Access**를 받고 앱을 **라이브 모드**로 바꿔야 합니다.
- 개인정보처리방침 URL 필요
- 기능 시연 화면 녹화 영상 필요 (5번 테스트 화면을 녹화하면 됨)

## 주의
- 토큰은 60일 뒤 만료됩니다. 새로 발급해서 Cloudflare의 `IG_ACCESS_TOKEN`만 바꾸면 됩니다.
- 새 게시물은 `POST_LINKS`에 없으면 메인 사이트 링크가 갑니다. 게시물별 링크를 주려면 media id를 추가하세요.
