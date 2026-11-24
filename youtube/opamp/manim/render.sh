#!/bin/sh
# 전체 장면을 1080p30 으로 렌더해서 ../img/ 에 모은다
cd "$(dirname "$0")"; mkdir -p ../img
for s in $(grep -o '^class [A-Za-z0-9]*' scenes.py | awk '{print $2}'); do
  [ -f ../img/$s.mp4 ] && continue
  nice -n 19 ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py $s > /dev/null 2>&1 && cp media/videos/scenes/1080p30/$s.mp4 ../img/ && echo $s
done
touch ../img/DONE
