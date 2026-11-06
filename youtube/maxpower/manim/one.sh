#!/bin/sh
# 장면 하나 렌더: sh one.sh 장면 NOSTEP(0/1)
cd "$(dirname "$0")"
if [ "$2" = 1 ]; then d=media_s_$1; o=../img_s; else d=media_$1; o=../img; fi
NOSTEP=$2 nice -n 10 ~/.venvs/manim/bin/manim -qh --fps 30 --media_dir $d scenes.py $1 > $d.log 2>&1 \
  && cp $d/videos/scenes/1080p30/$1.mp4 $o/ && rm -rf $d $d.log && echo "$o/$1"
