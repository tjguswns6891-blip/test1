#!/bin/sh
# 107조 vs 83조 3D 렌더 → stock1102/img/Duel3D.mp4  (youtube/ 에서)
set -e
R=raw/stock1102
cd stock1102/blender && nice -n 19 blender -t 2 -b --python duel.py -- "$PWD/../../$R/b_duel" > "../../$R/b_duel.log" 2>&1 && cd ../..
ffmpeg -v error -y -framerate 30 -i $R/b_duel/f_%04d.png -vf "scale=1920:1080:flags=lanczos,format=yuv420p" -c:v libx264 -crf 18 stock1102/img/Duel3D.mp4
rm -rf $R/b_duel
