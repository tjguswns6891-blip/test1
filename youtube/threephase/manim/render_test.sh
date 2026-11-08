#!/bin/sh
cd "$(dirname "$0")"
for s in $(grep -o '^class [A-Za-z0-9]*' scenes.py | awk '{print $2}'); do
  nice -n 19 ~/.venvs/manim/bin/manim -ql --media_dir media_ql scenes.py $s > log_$s.txt 2>&1 && echo "OK $s" || echo "FAIL $s"
done
echo END
