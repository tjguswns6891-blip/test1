# 쇼츠·릴스 음성이 다 나오면 합성 + 효과음. 결과: raw/stock1024/clips/{reel,short}_X.sfx.mp4
cd "$(dirname "$0")"
C=../raw/stock1024/clips; mkdir -p $C/reel $C/short
for k in ${KEYS:-A B C D E}; do
  for ver in reel short; do
    until [ -f ../raw/stock1024/v/${k}_${ver}.wav ]; do sleep 30; done
    cfg=$([ $ver = reel ] && echo reels.json || echo shorts.json)
    nice -n 5 python3 ../tools/faceless.py $cfg -o $C/$ver --only $k --avatar ../profile/profile_real_A.png 2>&1 | grep "→"
    plan=$(python3 ../tools/check/plan_stock.py $cfg $k $C/$ver/$k.srt)
    python3 ../tools/sfx.py $C/$ver/$k.mp4 $C/$ver/$k.srt --plan "$plan" -o $C/$ver/$k.sfx.mp4 2>&1 | tail -1
    echo "DONE $ver $k"
  done
done
echo ALLDONE
