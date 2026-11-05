#!/bin/sh
cd "$(dirname "$0")"
for s in $(grep -o '^class [A-Za-z0-9]*' scenes.py | awk '{print $2}'); do
  nice -n 19 ~/.venvs/manim/bin/manim -ql -s --media_dir media_t scenes.py $s > t_$s.log 2>&1 && echo "OK $s" || echo "FAIL $s"
done
echo DONE
