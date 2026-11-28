#!/bin/sh
# 3D 인트로 렌더 → mp4 → 범례 얹기. 사용: sh make_intro.sh  (youtube/ 에서)
set -e
R=raw/stock1024
cd stock1024/blender && nice -n 19 blender -t 2 -b --python intro.py -- "$PWD/../../$R/b_intro" > "../../$R/b_intro.log" 2>&1 && cd ../..
python3 stock1024/blender/legend.py $R/intro_legend.png
ffmpeg -v error -y -framerate 30 -i $R/b_intro/f_%04d.png -loop 1 -i $R/intro_legend.png \
  -filter_complex "[0]scale=1920:1080:flags=lanczos[v];[1]format=rgba,fade=t=in:st=4.3:d=0.5:alpha=1[l];[v][l]overlay=shortest=1,format=yuv420p" \
  -c:v libx264 -crf 18 stock1024/img/Intro3D.mp4
rm -rf $R/b_intro                                  # 프레임 PNG 는 250MB 라 지운다
