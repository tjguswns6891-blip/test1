#!/bin/sh
cd "$(dirname "$0")"
nice -n 19 sh render.sh > render.log 2> render_s.log 2>&1
nice -n 19 sh render_shorts.sh AQ H4 AFlow X6 ATone BQ H5 H6 BCoup CQ X3 B2 X4 CHalf DQ B4 B5 DInv DCorner EQ EAnt R3 R5 R6 > render_s.log 2>&1
