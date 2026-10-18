#!/bin/sh
# 회로 해석 기본 음성: 롱폼 첫 조각(첫 대사 5번 중 고르기) → 나머지 조각(빠르기 1.0, longform tempo 로 맞춤)
# → 클립 A~E 릴스·쇼츠(첫 대사 5번). 이미 있는 건 건너뜀. 다른 음성 작업과 동시에 돌리지 않는다(메모리).
cd "$(dirname "$0")/.."
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/circuitbasics/v; mkdir -p $O
$PY tools/tts_voxcpm_para.py circuitbasics/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --only I_0 --hook-takes 5 --tempo 1.0 > raw/circuitbasics/vhook.log 2>&1
$PY tools/tts_voxcpm_para.py circuitbasics/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --hook-takes 1 --tempo 1.0 > raw/circuitbasics/v.log 2>&1
$PY tools/tts_voxcpm_para.py circuitbasics/script.json raw/voice/prompt_hook.wav "$PT" $O --only A,B,C,D,E > raw/circuitbasics/vclip.log 2>&1
touch $O/ALL_DONE
