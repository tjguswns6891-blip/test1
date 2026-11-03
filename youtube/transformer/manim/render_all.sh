#!/bin/sh
cd "$(dirname "$0")"
nice -n 19 sh render.sh > render.log 2>&1
nice -n 19 sh render_shorts.sh Hook T2 T3 T4 T5 BQ M3 M4 M6 T6 CQ Dot1 Dot2 Dot3 Dot5 DQ C2 C3 C4 DW EQ EZ1 C5 ESpk > render_s.log 2>&1
