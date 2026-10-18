# 발음 검사: 대본(tts·sub) vs faster-whisper 받아쓰기 일치도. 사용: python3 chk_long.py script.json 음성폴더 [long|reel|short]
import json, re, sys
from difflib import SequenceMatcher
from faster_whisper import WhisperModel
nz = lambda t: re.sub(r"[^가-힣a-z0-9]", "", t.lower())
d = json.load(open(sys.argv[1])); vdir = sys.argv[2]; ver = sys.argv[3] if len(sys.argv) > 3 else "long"
m = WhisperModel("medium", device="cpu", compute_type="int8")
for k, v in d.items():
    if not isinstance(v, dict) or "lines" not in v or k.startswith("cta"): continue
    import os
    f = f"{vdir}/{k}_{ver}.wav"
    if not os.path.exists(f): continue
    txt = "".join(s.text for s in m.transcribe(f, language="ko", beam_size=5)[0])
    refs = [" ".join(l["tts"] for l in v["lines"]), " ".join(l["sub"] for l in v["lines"]).replace("*", "")]
    sc = max(SequenceMatcher(None, nz(r), nz(txt)).ratio() for r in refs)
    print(f"{k}\t{sc:.3f}\t{txt}", flush=True)
