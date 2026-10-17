# 자막 싱크 검사: 각 자막 첫 단어 시각 vs 받아쓰기 단어 시각. 사용: python3 synccheck.py X.srt X.words.json [앞여백초=0.25, 롱폼은 0]
import json, sys, re
srt, words = sys.argv[1], sys.argv[2]; lead = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
W = json.load(open(words))
cues = []
for b in open(srt).read().strip().split("\n\n"):
    l = b.split("\n"); h, m, x = l[1].split(" --> ")[0].split(":"); t = int(m) * 60 + float(x.replace(",", "."))
    cues.append((t, l[2]))
bad = 0
for t, txt in cues:
    w = min(W, key=lambda w: abs(w[1] + lead - t))
    first = txt.split()[0]
    d = w[1] + lead - t
    ok = abs(d) < 0.15
    bad += not ok
    print(f"{'  ' if ok else '✗ '}{t:6.2f}  자막 '{first}'  ↔  들리는 '{w[0]}' {d:+.2f}s")
print("어긋남", bad, "/", len(cues))
