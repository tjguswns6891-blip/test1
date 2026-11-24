#!/bin/sh
# 사용: sh sheet.sh out.png Scene1 Scene2 ...   (ql 렌더 마지막 프레임 모음)
out=$1; shift; d=$(mktemp -d); i=0
for s in "$@"; do
  f=media_ql/videos/scenes/480p15/$s.mp4
  ffmpeg -loglevel error -sseof -0.1 -i $f -frames:v 1 -vf "drawtext=text=$s:x=10:y=10:fontsize=28:fontcolor=yellow" $d/$(printf %03d $i).png; i=$((i+1))
done
ffmpeg -loglevel error -y -pattern_type glob -i "$d/*.png" -vf "tile=3x4:padding=6" -frames:v 1 $out
