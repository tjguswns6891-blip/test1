#!/bin/sh
# 쇼츠·릴스 C 다시 (밑변·빗변을 소리 나는 대로 믿뼌·빋뼌, seed 8). redo.sh 끝난 뒤
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python; O=raw/acpower/v
until [ -f $O/REDO_DONE ]; do sleep 30; done
mkdir -p $O/old; mv $O/C_reel.* $O/C_short.* $O/old/ 2>/dev/null
$PY tools/tts_voxcpm_para.py acpower/script.json raw/voice/prompt_hook.wav "$PT" $O --only C --tempo 1.0 --seed 8 > raw/acpower/v_redoC.log 2>&1
touch $O/REDO_C_DONE
