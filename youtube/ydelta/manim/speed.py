# 렌더된 장면이 dur.json(말 길이)보다 길면 speed.json 에 배율(<1)을 적어 다시 렌더한다. 사용: python3 speed.py → 다시 렌더할 장면 출력
import json, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); dur = json.load(open(f"{here}/dur.json"))
sp = json.load(open(f"{here}/speed.json")) if os.path.exists(f"{here}/speed.json") else {}
redo = []
for d in ("img", "img_s"):
    for f in sorted(os.listdir(f"{here}/../{d}")):
        if not f.endswith(".mp4"): continue
        n = f[:-4]
        if n not in dur: continue
        L = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{here}/../{d}/{f}"], capture_output=True, text=True).stdout)
        if L > dur[n] + 0.25:
            sp[n] = round(sp.get(n, 1.0) * dur[n] / L * 0.97, 3); redo.append((d, n, L, dur[n]))
json.dump(sp, open(f"{here}/speed.json", "w"), indent=0, sort_keys=True)
for d, n, L, t in redo: print(d, n, f"{L:.2f}s > {t:.2f}s → speed {sp[n]}")
print("redo:", " ".join(n for _, n, _, _ in redo))
