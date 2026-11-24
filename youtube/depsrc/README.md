# 종속 전원 편 (2026-11-06) 인수인계

회로이론 단원 롱폼 1편 + 쇼츠·릴스 A~E. 최대 전력 전달 편(`youtube/maxpower`)과 같은 방식.

## 예제 숫자 (lines.py 맨 위 검산 참고)
- 회로: 12V · 8Ω(전류 i_x) · 종속 전류원 **3i_x**(마디 a 로 들어감) · 단자 a-b · 부하.
- 부하 4Ω 노드 해석: i_x + 3i_x = v/4, i_x = (12−v)/8 → 24 − 2v = v → **v = 8V**. i_x 0.5A, 종속 전원 1.5A, 부하 2A.
- 개방: i_x = 0 → V_oc = 12V. 단락: i_x 1.5A + 4.5A = **6A**. R_th = 12/6 = **2Ω** (저항만 합치면 8Ω ✕).
- 시험 전원: 12V 단락 + 단자 1V → 들어가는 전류 0.5A → 2Ω.
- 테브난 12V·2Ω + 4Ω → 8V(검산). 최대 전력 R_L = 2Ω, 144/8 = 18W.
- 종속 전원을 거꾸로(−3i_x): I_sc = 1.5 − 4.5 = −3A → R_th = **−4Ω**(음저항, 발진기).
- 응용: BJT i_c = β i_b (CCCS), 연산증폭기 v_o = A(v+ − v−) (VCVS), 소신호 모델 r_π + g_m v_π.

## 쇼츠·릴스
A 마름모 전원이 뭐야? · B 테브난 저항 8Ω? 아니 2Ω · C 중첩할 때 끄면 안 되는 전원 · D 종속 전원 노드 해석 3줄 · E 테브난 저항이 음수?

## 만드는 순서
1. `python3 lines.py && python3 make_cfg.py`
2. 음성: `sh tts_all.sh` (롱폼 → 쇼츠/릴스). 다시 만들기: `tts_redo.sh`(ONLY=조각 SEED=9).
3. `python3 ../tools/scene_dur.py $PWD $PWD/../raw/depsrc/long` (절대 경로) → manim/dur.json
4. `sh manim/render_par.sh AQ AUse BQ CQ COff CChg DQ EQ ERev EIsc Q1 Q4 Q5 T2 T3 T4 T5 M3 M4 M5 N2 N4 N5 U5 U6` → `python3 manim/speed.py` 로 넘친 장면 다시 렌더
5. `python3 finish.py long A B C D E` → `python3 fixsync.py long A_reel ...`
6. 썸네일: `sh thumbnail/frames.sh && node thumbnail/render.js` (thumbs.html 의 MIN 을 실제 길이로)

음성 생성 중엔 Manim 렌더를 같이 돌리지 않는다(크게 느려짐). 결과물은 프로젝트 파일 `depsrc/`.
새 컨테이너: `.claude/hooks/session-start.sh` 직접 실행(약 10분), 음성 프롬프트는 raw.githubusercontent video-files/라플라스_작업중/voice 에서 받는다.

## 상태 (2026-11-06 16:30 KST)
- 완료, 업로드 안 함. 롱폼 3:21 (썸네일 V2 "3분 20초 정리"), 쇼츠·릴스 A~E 19~22초, 싱크 어긋남 0.
- 챕터 0:00 / 0:15 / 0:45 / 1:19 / 1:55 / 2:27 / 2:58. 제목·설명·태그·캡션: `titles.md`.
- 음성: seed 7 기본, S4_0·S6_0 롱폼 조각과 D 릴스는 seed 9(_s9) 로 교체(받아쓰기 비교). 자막에 변수는 `i_x` 로 그대로 적혀 있다.
- 결과물: 프로젝트 파일 `depsrc/` (롱폼_종속전원.mp4, 롱폼.srt, 쇼츠_A~E, 릴스_A~E, thumb_V1/V2, cover_A~E). video-files 브랜치에는 아직 안 올림.
