#!/usr/bin/env bash
# 블렌더 장면을 차례로 렌더해 youtube/1012/img/<이름>.mp4 로 만든다.
# 사용: bash render_all.sh [b01_kospi b02_flow b03_iphone]
set -e
cd "$(dirname "$0")"
OUT=${OUT:-/tmp/blender_1012}
mkdir -p ../img
for n in ${@:-b01_kospi b02_flow b03_iphone}; do
  rm -rf "$OUT/$n"; mkdir -p "$OUT/$n"
  blender -b -P "$n.py" -- "$OUT/$n" > "$OUT/$n.log" 2>&1
  ffmpeg -hide_banner -loglevel error -y -framerate 30 -i "$OUT/$n/f_%04d.png" -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -movflags +faststart "../img/$n.mp4"
  cp "$(ls "$OUT/$n"/f_*.png | tail -1)" "../img/$n.png"
  echo "done $n"
done
