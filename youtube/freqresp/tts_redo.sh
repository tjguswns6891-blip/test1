#!/bin/sh
# 발음 검사에서 걸린 조각만 seed 바꿔 다시 (이미 있는 건 건너뜀)
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/freqresp/v; S=${SEED:-9}
$PY tools/tts_voxcpm_para.py freqresp/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed $S --only I_0,S2_0,S2_1,S5_1,S6_0 > raw/freqresp/redo.log 2>&1
$PY tools/tts_voxcpm_para.py freqresp/script.json raw/voice/prompt_hook.wav "$PT" $O --only E --tempo 1.0 --seed $S >> raw/freqresp/redo.log 2>&1
touch $O/REDO_DONE
