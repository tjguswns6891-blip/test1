# 쇼츠·릴스 음성 빠르기만 다시 (raw 에서 강조·빠르기·음량 다시). 사용: python3 retempo.py 1.0 A B ...
import json, os, re, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(here, "..", "raw", "transient", "v")
d = json.load(open(f"{here}/script.json", encoding="utf-8")); tempo = sys.argv[1]
for k in sys.argv[2:]:
    marks = [m for ln in d[k]["lines"] for m in re.findall(r"\*([^*]+)\*", ln["sub"])]
    for ver in ("reel", "short"):
        raw = f"{V}/{k}_{ver}.raw.wav"
        subprocess.run(["python3", f"{here}/../tools/emphasize.py", raw, f"{V}/{k}_{ver}.wav", "--marks", ",".join(marks), "--tempo", tempo], check=True)
