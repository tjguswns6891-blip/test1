#!/bin/sh
cd "$(dirname "$0")"
nice -n 19 sh render.sh > render.log 2>&1
nice -n 19 sh render_shorts.sh AQ AWrong Z3 L6 ATri BQ PH1 BDiff PH5 PH6 CQ CDC Z6 Z5 DQ L2 L3 DMag DCur EQ C2 C3 C4 C5 > render_s.log 2>&1
