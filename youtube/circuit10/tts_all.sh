#!/bin/sh
# 음성 전부: 롱폼 첫 조각(첫 대사 5번) → 롱폼 나머지 → 쇼츠/릴스 A~E
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/circuit10/v
mkdir -p $O
$PY tools/tts_voxcpm_para.py circuit10/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --only I_0 --tempo 1.0 > raw/circuit10/v_i0.log 2>&1
$PY tools/tts_voxcpm_para.py circuit10/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --hook-takes 1 --tempo 1.0 > raw/circuit10/v.log 2>&1
$PY tools/tts_voxcpm_para.py circuit10/script.json raw/voice/prompt_hook.wav "$PT" $O --only A,B,C,D,E > raw/circuit10/vabc.log 2>&1
touch $O/ALL_DONE
