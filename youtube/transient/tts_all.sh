#!/bin/sh
# 음성 전부: 롱폼 조각 → 쇼츠/릴스 A~E (참고 음성 하나, 같은 seed)
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/transient/v
mkdir -p $O
$PY tools/tts_voxcpm_para.py transient/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 > raw/transient/v.log 2>&1
$PY tools/tts_voxcpm_para.py transient/script.json raw/voice/prompt_hook.wav "$PT" $O --only A,B,C,D,E > raw/transient/vabc.log 2>&1
touch $O/ALL_DONE
