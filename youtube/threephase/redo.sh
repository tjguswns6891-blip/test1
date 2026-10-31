#!/bin/sh
# 발음 검사에서 걸린 롱폼 조각 다시 (집·선간·선관 발음, seed 8). 사용: sh redo.sh I_0,S2_0,...
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/threephase/v
until [ -f $O/ALL_DONE ]; do sleep 30; done
mkdir -p $O/old
for k in $(echo $1 | tr ',' ' '); do mv $O/${k}_long.* $O/old/ 2>/dev/null; done
$PY tools/tts_voxcpm_para.py threephase/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed 8 --only $1 > raw/threephase/v_redo.log 2>&1
touch $O/REDO_DONE
