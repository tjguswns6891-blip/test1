# 상황별 효과음 키트

참고 릴스(roy.branding "상황별 효과음 6가지", 캡컷 효과음)의 분류를 그대로 따르고, 같은 느낌의 소리를
**효과음 라보(soundeffect-lab.info)** 에서 골랐다. 상업적 이용 무료 · 출처 표기 불필요 (사이트 이용 규약).
캡컷 원본은 캡컷 앱 안에서만 쓸 수 있어서, 캡컷으로 직접 편집할 때는 오른쪽 이름으로 검색하면 된다.

| 종류 | 파일 | 소리 | 참고 릴스의 캡컷 효과음 |
|---|---|---|---|
| intro 도입 주목 | intro1_dodon · intro2_jan · intro3_pa | 북 "두둥" · "짠!" · "팟" | Dodon! / The sound of tapping the central part of the leather… / Sound effect when telop etc. appear |
| visual 시각자료 등장 | visual1_shutter · visual2_click · visual3_papa | 카메라 셔터 · 마우스 클릭 · "파팟" | 清脆上升双击 / Camera shutter sound (Kasha) / Click_Mouse_Click_02 / Poyoi |
| emph 강조 | emph1_flash · emph2_kira · emph3_correct | 전구 "띠링" · 반짝 · 정답 철금 | Culin. light bulb mark / 마술 소리 / 得分 |
| trans 화면 전환 | trans1_swing · trans2_jump | 날카로운 "휙" · 바람 가르는 "휙" | 휙 / swish_whoosh (large) / "whoosh" (Badminton racket swing) |
| cta 마지막 행동 유도 | cta1_typing · cta2_enter | 키보드 빠르게 타닥 · 엔터 "탁" | Keyboard Typing 01 / Typing sound (keyboard x 3p) / Realistic sound effects for typing |
| base 무난 (아무 데나) | base1_pikot · base2_pon · base3_nyu | "삐콧" · "퐁" · "뉴" | Poyoi / Patterop sound etc / UI提示 |

sfx.py 계획에서 `종류` 만 쓰면 1번 파일, `종류2` 처럼 번호를 붙이면 그 파일을 쓴다. 예: `1:intro,4:visual,7:emph2,9:trans,12:cta`
