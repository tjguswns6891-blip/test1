#!/bin/sh
# 받아쓰기에서 걸린 조각 seed 9 로 한 번 더 (접미사 _s9): 롱폼 S1_1·S4_0·S6_0, 릴스 C·D, 쇼츠 C·E
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/depsrc/v; S=9
$PY tools/tts_voxcpm_para.py depsrc/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed $S --suffix _s$S --only S1_1,S4_0,S6_0 > raw/depsrc/redo.log 2>&1
$PY tools/tts_voxcpm_para.py depsrc/script.json raw/voice/prompt_hook.wav "$PT" $O --ver reel --tempo 1.0 --seed $S --suffix _s$S --only C,D >> raw/depsrc/redo.log 2>&1
$PY tools/tts_voxcpm_para.py depsrc/script.json raw/voice/prompt_hook.wav "$PT" $O --ver short --tempo 1.0 --seed $S --suffix _s$S --only C,E >> raw/depsrc/redo.log 2>&1
touch $O/REDO_DONE
