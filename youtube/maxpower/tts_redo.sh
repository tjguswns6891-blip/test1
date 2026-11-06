#!/bin/sh
# 발음 검사에서 걸린 조각을 다른 seed 로 한 번 더 (접미사 _sN, 원본은 그대로) → 받아쓰기 비교해서 고른다
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/maxpower/v; S=${SEED:-9}
$PY tools/tts_voxcpm_para.py maxpower/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed $S --suffix _s$S --only ${ONLY:-I_0,S2_1,S4_1,S6_1} > raw/maxpower/redo.log 2>&1
touch $O/REDO_DONE
