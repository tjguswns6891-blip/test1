#!/bin/sh
# 미리보기 시트: ./sheet.sh A "0,1,2,..." [timing.json]
R=../../raw/stock1128/mg; node render.js $1 ${3:-$R/est.json} $R/sheet_$1.png --sheet "$2" && ffmpeg -loglevel error -y -pattern_type glob -i "$R/sheet_$1_f/*.png" -vf "scale=540:-1,tile=${4:-4x3}" -frames:v 1 $R/sheet_$1.png
