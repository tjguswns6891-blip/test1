#!/bin/sh
# 쇼츠·릴스 A·E 다른 seed 로 한 번 더 (접미사 _s9) → 받아쓰기 비교해서 고른다
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/maxpower/v
$PY tools/tts_voxcpm_para.py maxpower/script.json raw/voice/prompt_hook.wav "$PT" $O --only A,E --tempo 1.0 --seed 9 --suffix _s9 > raw/maxpower/redo2.log 2>&1
touch $O/REDO2_DONE
