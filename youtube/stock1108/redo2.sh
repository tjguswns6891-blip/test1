#!/bin/sh
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/stock1108/v
$PY tools/tts_voxcpm_para.py stock1108/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed 9 --only S4_1 > raw/stock1108/v_redo2.log 2>&1
$PY tools/tts_voxcpm_para.py stock1108/script.json raw/voice/prompt_hook.wav "$PT" $O --only C,E --seed 8 --tempo 1.0 >> raw/stock1108/v_redo2.log 2>&1
touch $O/REDO2_DONE
