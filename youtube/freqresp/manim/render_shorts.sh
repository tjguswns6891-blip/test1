#!/bin/sh
# 쇼츠·릴스용: STEP 표시 없이 ../img_s/ 에 렌더 (NOSTEP=1)
cd "$(dirname "$0")"; mkdir -p ../img_s
for s in "$@"; do
  NOSTEP=1 nice -n 19 ~/.venvs/manim/bin/manim -qh --fps 30 --media_dir media_s scenes.py $s > /dev/null 2>&1 && cp media_s/videos/scenes/1080p30/$s.mp4 ../img_s/ && echo $s
done
touch ../img_s/DONE
