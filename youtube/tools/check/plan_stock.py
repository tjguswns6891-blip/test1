# 쇼츠/릴스 효과음 계획(sfx.py --plan) 만들기. 사용: python3 plan_stock.py reels.json A X.srt
import json, re, sys
nz = lambda t: re.sub(r"[^가-힣a-zA-Z0-9]", "", t)
cfgf, key, srt = sys.argv[1:4]
lines = [l["sub"] for l in json.load(open(cfgf))[key]["lines"]]
cues = [b.split("\n", 2)[2] for b in open(srt).read().strip().split("\n\n")]
def first(i):
    h = nz(lines[i])[:6]
    for j, c in enumerate(cues):
        if nz(c).startswith(h): return j + 1
plan = [f"1:intro", f"{first(1)}:visual", f"{first(2)}:emph", f"{first(3)}:trans", f"{first(len(lines)-1)}:cta"]
print(",".join(plan))
