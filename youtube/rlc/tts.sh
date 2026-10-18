#!/bin/sh
# RLC 음성: 롱폼 조각(빠르기 1.0, longform tempo 로 맞춤) → 쇼츠/릴스 A·B·C(첫 대사 5번, 빠르기 0.95). 이미 있는 건 건너뜀
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python
$PY tools/tts_voxcpm_para.py rlc/long_tts.json raw/voice/prompt_hook.wav "$PT" raw/rlc/v --ver long --hook-takes 1 --tempo 1.0 > raw/rlc/v.log 2>&1
$PY tools/tts_voxcpm_para.py rlc/script.json raw/voice/prompt_hook.wav "$PT" raw/rlc/v --only A,B,C > raw/rlc/vabc.log 2>&1
touch raw/rlc/v/ALL_DONE
