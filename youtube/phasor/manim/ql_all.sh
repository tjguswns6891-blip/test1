#!/bin/sh
# 빠른 검사: 전체 장면 480p15 렌더 (오류 찾기)
cd "$(dirname "$0")"
for s in $(grep -o '^class [A-Za-z0-9]*' scenes.py | awk '{print $2}'); do
  nice -n 19 ~/.venvs/manim/bin/manim -ql --media_dir media_ql scenes.py $s > ql_$s.log 2>&1 && echo "ok $s" || echo "FAIL $s"
done
