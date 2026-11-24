# 라플라스 심화 5편: 스위칭 순간의 임펄스 (2026-11-24) 인수인계

교재 회로이론 13장(The Laplace Transform in Circuit Analysis) 13.8 절. 라플라스 심화 1~4편(`lap1`~`lap4`)이 안 다룬 부분.
롱폼 1편 + 쇼츠·릴스 A~E. 종속 전원 편(`youtube/depsrc`) 파이프라인을 그대로 복사했다.

## 예제 숫자 (lines.py 맨 위 검산 참고)
- 커패시터: C1 = C2 = 1μF, C1 10V, C2 0V, 저항 R 로 연결. Ce = 0.5μF, i = (10/R)e^(−t/RCe), 넓이 = 10·Ce = 5μC (R 없음).
  전하 보존 → 둘 다 5V. 에너지 50μJ → 25μJ (절반 손실). R = 0 이면 I(s) = 10·Ce = 5×10⁻⁶ (상수) → 5μ·δ(t).
- 인덕터: 100V, 10Ω, L1 = 3H 에 10A (스위치가 15Ω·L2 우회), L2 = 2H 0A. 스위치 열면 직렬.
  I = (100/s + 30)/(5s + 25) = 4/s + 2/(s+5), i = 4 + 2e^(−5t), i(0⁺) = 6A. 자속 보존 3·10 + 2·0 = 5·6.
  v_o(15Ω + L2) = 12δ(t) + 60 + 10e^(−5t). 최종 4A, 60V.

## 쇼츠·릴스
A 인덕터 전류 점프(자속 보존) · B 에너지 절반 증발(전하 보존) · C 저항을 0으로(임펄스 전류) · D 라플라스 답이 상수면?(δ(t)) · E 연속성 규칙은 법칙이 아니다

## 만드는 순서
1. `python3 lines.py && python3 make_cfg.py`
2. 음성: `sh tts_all.sh` (롱폼 → 쇼츠/릴스)
3. `python3 ../tools/scene_dur.py $PWD $PWD/../raw/lap5/long` (절대 경로) → manim/dur.json
4. `sh manim/render_par.sh AQ BQ BHeat CQ DQ DQ2 DLine EQ ETwo L2 L4 L5 L6 C1 C4 C6 C3 K2 K3 K4 K5 K6 R4 E2 E3` → `python3 manim/speed.py` 로 넘친 장면 다시 렌더
5. `python3 finish.py long A B C D E` → `python3 fixsync.py long A_reel ...`
6. 썸네일: `sh thumbnail/frames.sh && node thumbnail/render.js` (thumbs.html 의 MIN 을 실제 길이로)

장면 이름 주의: scenes.py 의 도우미 함수 `P3` 와 겹치지 않게 STEP 3 장면은 K1~K6 이다.
결과물은 프로젝트 파일 `laplace5/`. 업로드는 사용자가 썸네일·제목·시간을 고른 뒤에.
