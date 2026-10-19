#!/bin/sh
# 전체 장면을 1080p30 으로 렌더해서 ../img/ 에 모은다
cd "$(dirname "$0")"; mkdir -p ../img
for s in Hook Three Circuit KillRule Sup1 Sup2 SupSum Thev Rth ThevDone Norton NortonCheck When MaxPower Mistakes Summary; do
  ~/.venvs/manim/bin/manim -qh --fps 30 scenes.py $s > /dev/null 2>&1 && cp media/videos/scenes/1080p30/$s.mp4 ../img/ && echo $s
done
touch ../img/DONE
