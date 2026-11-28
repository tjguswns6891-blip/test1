#!/bin/sh
# 음성: 쇼츠/릴스 A~C (참고 음성 하나, 같은 seed, 빠르기 1.0). 릴스 먼저.
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/stock1128/v
mkdir -p $O
$PY tools/tts_voxcpm_para.py stock1128/script.json raw/voice/prompt_hook.wav "$PT" $O --only ${KEYS:-A,B,C} --ver ${VER:-reel} --tempo 1.0 >> raw/stock1128/v.log 2>&1
touch $O/ALL_DONE
