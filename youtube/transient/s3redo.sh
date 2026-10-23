#!/bin/sh
# 쇼츠 음성이 끝나면 S3_0(방전 식) 을 문구 바꿔 다시
cd /home/user/test1/youtube; O=raw/transient/v
until [ -f $O/ALL_DONE ]; do sleep 20; done
mkdir -p $O/old2; mv $O/S3_0_long.wav $O/S3_0_long.raw.wav $O/old2/; rm -f $O/S3_0_long.*
~/.venvs/voxcpm/bin/python tools/tts_voxcpm_para.py transient/long_tts.json raw/voice/prompt_hook.wav "$(cat raw/voice/prompt_hook.txt)" $O --ver long --tempo 1.0 --seed 8 --only S3_0 > raw/transient/v3.log 2>&1
touch $O/S3_DONE
