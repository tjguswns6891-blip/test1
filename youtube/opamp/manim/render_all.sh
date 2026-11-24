#!/bin/sh
cd "$(dirname "$0")"
nice -n 19 sh render.sh > render.log 2>&1
nice -n 19 sh render_shorts.sh AQ O2 O5 O4 O6 BQ V1 V3 V4 BRatio CQ CFol CCur CLoad N5 DQ A1 A3 A5 A6 EQ D2 D4 D5 D6 > render_s.log 2>&1
