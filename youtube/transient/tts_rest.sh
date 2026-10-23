#!/bin/sh
# 발음 검사에서 걸린 롱폼 조각 다시(seed 8) → 쇼츠/릴스 나머지
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/transient/v
$PY tools/tts_voxcpm_para.py transient/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed 8 --only I_0,S1_0,S3_0,S7_0 > raw/transient/v2.log 2>&1
touch $O/LONG_DONE
$PY tools/tts_voxcpm_para.py transient/script.json raw/voice/prompt_hook.wav "$PT" $O --only A,B,C,D,E > raw/transient/vabc2.log 2>&1
touch $O/ALL_DONE
