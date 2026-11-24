#!/bin/sh
# 빠른 확인: 480p15 로 전부 렌더 → media_ql
cd "$(dirname "$0")"
for s in $(grep -o '^class [A-Za-z0-9]*' scenes.py | awk '{print $2}'); do
  ~/.venvs/manim/bin/manim -ql --media_dir media_ql scenes.py $s > /tmp/mtest_$s.log 2>&1 && echo "ok $s" || echo "FAIL $s"
done
