# 최대 전력 전달 편 (2026-11-06) 인수인계

회로이론 단원 롱폼 1편 + 쇼츠·릴스 A~E. Y-Δ 변환 편(`youtube/ydelta`)과 같은 방식.

## 예제 숫자 (lines.py 맨 위 검산 참고)
- 테브난 등가 12V · 4Ω. 부하 1Ω → 2.4A, 5.76W / 2Ω 8W / 4Ω 1.5A, **9W(최대)** / 8Ω 8W / 16Ω 0.6A, 5.76W. 곱이 16(=4²)인 짝은 전력이 같다.
- 0Ω: 3A, 전압 0 → 0W. ∞: 12V, 전류 0 → 0W.
- dP/dR_L ∝ (R_th − R_L) → R_L = R_th, P_max = V²/(4R_th) = 144/16 = 9W. 내부 저항도 9W → 효율 50% (전력망은 R_L ≫ R_th).
- 시험 회로: 24V, 8Ω(직렬) + 8Ω(세로). 개방 전압 12V, 들여다본 저항 8∥8 = 4Ω → 부하 4Ω, 9W.
- 교류: Z_th = 4 + j3 → Z_L = 4 − j3, 합 8Ω, 10V → 1.25A, 6.25W. 임피던스 정합(스피커 8Ω, 안테나 50Ω).

## 쇼츠·릴스
A 부하 저항 몇 Ω이 최대? · B 최대 전력 = 효율 50% · C 0Ω도 ∞Ω도 전력 0(그래프) · D 3줄 풀이(테브난) · E 교류 켤레 정합

## 만드는 순서
1. `python3 lines.py && python3 make_cfg.py`
2. 음성: `sh tts_all.sh` (롱폼 → 쇼츠/릴스). 다시 만들기: `tts_redo.sh`(롱폼 조각, seed 9) · `tts_redo2.sh`(A·E). 받아쓰기 비교 후 고른 것: 롱폼 I_0·S2_1·S6_1, A 릴스·쇼츠, E 릴스 = seed 9.
3. `python3 ../tools/scene_dur.py $PWD $PWD/../raw/maxpower/long` (절대 경로) → manim/dur.json
4. `sh manim/render_par.sh <쇼츠 장면들>` → `python3 manim/speed.py` 로 넘친 장면 다시 렌더
5. `python3 finish.py long A B C D E` → `python3 fixsync.py long A_reel ...`
6. 썸네일: `sh thumbnail/frames.sh && node thumbnail/render.js` (thumbs.html 의 MIN 을 실제 길이로)

음성 생성 중엔 Manim 렌더를 같이 돌리지 않는다(크게 느려짐). 결과물은 프로젝트 파일 `maxpower/`.
