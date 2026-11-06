#!/bin/sh
# 렌더된 장면 마지막 프레임 → 썸네일 그림 (g_*: 롱폼 img, gs_*: 쇼츠 img_s)
cd "$(dirname "$0")"
for p in hook:Hook t5:T5 q5:Q5 goal:Goal; do ffmpeg -v error -y -sseof -0.3 -i ../img/${p#*:}.mp4 -frames:v 1 g_${p%%:*}.png; done
for p in aq:AQ bq:BQ cq:CQ dq:DQ eq:EQ; do ffmpeg -v error -y -sseof -0.3 -i ../img_s/${p#*:}.mp4 -frames:v 1 gs_${p%%:*}.png; done
ls g_*.png gs_*.png
