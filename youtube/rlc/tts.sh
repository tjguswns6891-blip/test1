#!/bin/sh
# RLC 음성: 롱폼 조각(빠르기 1.0, longform tempo 로 맞춤) → 쇼츠/릴스 A·B·C(첫 대사 5번, 빠르기 0.95). 이미 있는 건 건너뜀
cd /home/user/test1/youtube
PT="$(cat raw/voice/prompt_hook.txt)"; PY=~/.venvs/voxcpm/bin/python
$PY tools/tts_voxcpm_para.py rlc/long_tts.json raw/voice/prompt_hook.wav "$PT" raw/rlc/v --ver long --hook-takes 1 --tempo 1.0 > raw/rlc/v.log 2>&1
$PY tools/tts_voxcpm_para.py rlc/script.json raw/voice/prompt_hook.wav "$PT" raw/rlc/v --only A,B,C > raw/rlc/vabc.log 2>&1
touch raw/rlc/v/ALL_DONE
# 롱폼 첫 조각은 첫 대사 '전기전자 주목'을 5번 만들어 가장 힘찬 것으로 (2026-10-18)
if [ ! -e raw/rlc/v/I_0.hook/scores.json ]; then
  mv raw/rlc/v/I_0_long.wav raw/rlc/v/I_0_long_t1.wav 2>/dev/null
  $PY tools/tts_voxcpm_para.py rlc/long_tts.json raw/voice/prompt_hook.wav "$PT" raw/rlc/v --ver long --only I_0 --hook-takes 5 --tempo 1.0 > raw/rlc/vhook.log 2>&1
fi
touch raw/rlc/v/HOOK_DONE
