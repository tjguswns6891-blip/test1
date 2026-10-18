#!/bin/sh
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python
$PY tools/tts_voxcpm_para.py laplace/long_tts.json raw/voice/prompt_hook.wav "$PT" raw/laplace/v --ver long --hook-takes 1 --tempo 1.0 > raw/laplace/v.log 2>&1
$PY tools/tts_voxcpm_para.py laplace/script.json raw/voice/prompt_hook.wav "$PT" raw/laplace/v --only A,B,C > raw/laplace/vabc.log 2>&1
touch raw/laplace/v/ALL_DONE
