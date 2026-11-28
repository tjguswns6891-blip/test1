#!/bin/sh
# 음성이 다 나온 뒤: 타이밍 → 모션그래픽 렌더 → 쇼츠 음성 → 합성 + 효과음. 사용: ./build.sh "A B C"
cd "$(dirname "$0")"; RAW=../raw/stock1128; C=$RAW/clips; mkdir -p $C/reel $C/short
KEYS="${1:-A B C}"; CSV=$(echo $KEYS | tr ' ' ',')
python3 timing.py $CSV 2>&1 | grep -v Warn
[ -n "$NOMG" ] || for k in $KEYS; do nice -n 5 node mg/render.js $k $RAW/mg/timing.json $RAW/mg/$k.mp4; done
[ -f $RAW/v/X_short.wav ] && python3 mk_short.py $CSV; python3 make_cfg.py
for k in $KEYS; do for ver in ${VERS:-reel short}; do
  [ -f $RAW/v/${k}_$ver.wav ] || continue
  cfg=$([ $ver = reel ] && echo reels.json || echo shorts.json)
  nice -n 5 python3 ../tools/faceless.py $cfg -o $C/$ver --only $k --avatar ../profile/profile_real_A.png 2>&1 | grep "→\|초"
  plan=$(python3 ../tools/check/plan_stock.py $cfg $k $C/$ver/$k.srt)
  python3 ../tools/sfx.py $C/$ver/$k.mp4 $C/$ver/$k.srt --plan "$plan" -o $C/$ver/$k.sfx.mp4 2>&1 | tail -1
done; done; echo ALLDONE
