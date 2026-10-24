#!/bin/sh
# 주간 성적표 3D 렌더 → stock1024/img/Score3D.mp4  (youtube/ 에서)
set -e
R=raw/stock1024
cd stock1024/blender && nice -n 19 blender -t 2 -b --python scorecard.py -- "$PWD/../../$R/b_score" > "../../$R/b_score.log" 2>&1 && cd ../..
ffmpeg -v error -y -framerate 30 -i $R/b_score/f_%04d.png -vf "scale=1920:1080:flags=lanczos,format=yuv420p" -c:v libx264 -crf 18 stock1024/img/Score3D.mp4
rm -rf $R/b_score
