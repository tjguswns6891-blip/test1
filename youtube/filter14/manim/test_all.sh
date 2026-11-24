#!/bin/sh
# 전 장면 저해상도 테스트 렌더 (오류 찾기). 결과: test_media/ok.txt, test_media/fail.txt
cd "$(dirname "$0")"; mkdir -p test_media; : > test_media/ok.txt; : > test_media/fail.txt
for s in $(grep -o '^class [A-Za-z0-9]*' scenes.py | awk '{print $2}'); do
  if nice -n 15 ~/.venvs/manim/bin/manim -ql --fps 10 --media_dir test_media scenes.py $s > test_media/$s.log 2>&1; then echo $s >> test_media/ok.txt; else echo $s >> test_media/fail.txt; fi
done
echo DONE >> test_media/ok.txt
