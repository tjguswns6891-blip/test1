#!/bin/sh
# 릴스판 A,B,C 를 한 번에 만든 뒤, 쇼츠 끝 대사(cta_short)만 따로 한 번 만든다 (쇼츠 = 릴스 본문 + 쇼츠 끝 대사, mk_short.py)
cd /home/user/test1/youtube
KEYS=A,B,C VER=reel stock1128/tts_all.sh
PT="$(cat raw/voice/prompt_hook.txt)"
~/.venvs/voxcpm/bin/python tools/tts_voxcpm_para.py stock1128/cta_only.json raw/voice/prompt_hook.wav "$PT" raw/stock1128/v --ver short --tempo 1.0 >> raw/stock1128/v.log 2>&1
touch raw/stock1128/v/C_DONE
