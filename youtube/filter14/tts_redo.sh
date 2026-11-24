#!/bin/sh
# 발음 검사에서 걸린 조각을 다른 seed 로 (접미사 _sN, 원본 그대로) → 받아쓰기 비교해서 고른다
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/filter14/v; S=${SEED:-9}
$PY tools/tts_voxcpm_para.py filter14/long_tts.json raw/voice/prompt_hook.wav "$PT" $O --ver long --tempo 1.0 --seed $S --suffix _s$S --only S3_1 > raw/filter14/redo.log 2>&1
$PY tools/tts_voxcpm_para.py filter14/script.json raw/voice/prompt_hook.wav "$PT" $O --only E --tempo 1.0 --seed $S --suffix _s$S >> raw/filter14/redo.log 2>&1
touch $O/REDO_DONE
