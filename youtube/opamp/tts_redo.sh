#!/bin/sh
# 발음 검사에서 걸린 조각만 seed 바꿔 다시 (이미 있는 건 건너뜀)
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/opamp/v; S=${SEED:-9}
$PY tools/tts_voxcpm_para.py opamp/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed $S --only ${ONLY:-S5_0,S6_0} > raw/opamp/redo.log 2>&1
touch $O/REDO_DONE
