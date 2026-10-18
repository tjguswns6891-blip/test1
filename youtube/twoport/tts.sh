#!/bin/sh
# 2포트 음성: 롱폼 첫 조각(첫 대사 '전기전자 주목' 5번 중 고르기) → 나머지 조각(빠르기 1.0, longform tempo 로 맞춤)
# → 쇼츠/릴스 A·B·C(첫 대사 5번, 빠르기 0.95). 이미 있는 건 건너뜀. 다른 음성 작업과 동시에 돌리지 않는다(메모리).
cd "$(dirname "$0")/.."
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; mkdir -p raw/twoport/v
$PY tools/tts_voxcpm_para.py twoport/long_tts.json raw/voice/prompt_hook.wav "$PT" raw/twoport/v --ver long --only I_0 --hook-takes 5 --tempo 1.0 > raw/twoport/vhook.log 2>&1
$PY tools/tts_voxcpm_para.py twoport/long_tts.json raw/voice/prompt_hook.wav "$PT" raw/twoport/v --ver long --hook-takes 1 --tempo 1.0 > raw/twoport/v.log 2>&1
$PY tools/tts_voxcpm_para.py twoport/script.json raw/voice/prompt_hook.wav "$PT" raw/twoport/v --only A,B,C > raw/twoport/vabc.log 2>&1
touch raw/twoport/v/ALL_DONE
