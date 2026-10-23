#!/bin/sh
# 남은 음성이 나오는 대로: 빠르기 1.0 → 합성·싱크·효과음 → 자막 보정. 마지막에 롱폼(방전 조각 다시 만든 뒤)
cd /home/user/test1/youtube/transient; V=../raw/transient/v
for k in C D E; do
  until [ -f $V/${k}_short.wav ]; do sleep 20; done
  python3 retempo.py 1.0 $k && python3 finish.py $k && python3 fixsync.py ${k}_reel ${k}_short
done
until [ -f $V/S3_DONE ]; do sleep 20; done
python3 finish.py long && python3 fixsync.py long
touch $V/PIPE_DONE
