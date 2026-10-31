#!/bin/sh
cd "$(dirname "$0")"
nice -n 19 sh render.sh > render.log 2>&1
nice -n 19 sh render_shorts.sh Hook Y2 Y3 Y4 Y5 N1 N2 A2 N4 N5 CQ Y1 D3 D4 D5 MS0 MS1 MS2 D6 EQ W5 ES1 W6 A1 > render_s.log 2>&1
