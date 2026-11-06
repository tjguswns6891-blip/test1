#!/bin/sh
# 병렬 렌더(4개씩): 롱폼 장면 → ../img, 인자로 준 쇼츠 장면(NOSTEP) → ../img_s
cd "$(dirname "$0")"; mkdir -p ../img ../img_s
( for s in $(grep -o '^class [A-Za-z0-9]*' scenes.py | awk '{print $2}'); do echo "$s 0"; done
  for s in "$@"; do echo "$s 1"; done ) | xargs -P 4 -n 2 sh one.sh
touch ../img/DONE
