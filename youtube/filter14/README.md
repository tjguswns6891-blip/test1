# 14장 필터(주파수 선택 회로) 편 (2026-11-24) 인수인계

사용자가 보낸 14장 시험대비 정리로 만든 롱폼 1편 + 쇼츠·릴스 A~E. 종속 전원 편(`youtube/depsrc`)과 같은 방식.
예전 '주파수 응답' 편(freqresp: 저역통과·−3dB·보드선도·공진 라디오)과 겹치지 않게 판별·설계·Q·시험 함정 중심.

## 숫자 (lines.py 맨 위 검산)
- 설계 문제: 1k~10kHz 대역통과, C 1μF → f0 3162Hz, L 2.53mH, R 143Ω, Q 0.35
- 1차 설계: C 1μF, 3kHz → 53Ω (2π 빼면 333Ω ✕)
- 직렬 RLC 100Ω·50mH·0.2μF → ω0 1e4, β 2000, Q 5, 9050·11050
- 부하: 500Ω·5.3mH RL 고역통과 15kHz → 500Ω 부하 시 크기 0.5, 7.5kHz

## 만드는 순서
depsrc README 와 같음. 쇼츠 장면: `sh manim/render_par.sh AQ AEnds ABP ABR AAll BQ F3 BWrong F5 F6 CQ CGeo D2 CPlot CSum DQ B4 DSer DPar P2 EQ P3 P4 ECut EOp`
- scenes.py: 좌표 함수는 PT3 (장면 P3 와 이름 충돌 피함). log 축 그래프는 LAx(y 축 왼쪽).
- 음성 교체: S3_1·E_reel 은 seed 9, E_short 는 seed 11 (원본은 raw/filter14/v/orig).

## 상태
- 완료, 업로드 안 함. 롱폼 2:58 (썸네일 "3분 정리"), 쇼츠·릴스 19~23초, 싱크 어긋남 롱폼 1곳 0.26s 외 0.
- 결과물: 프로젝트 파일 `filter14/`. 제목·설명·태그·캡션 `titles.md`.
