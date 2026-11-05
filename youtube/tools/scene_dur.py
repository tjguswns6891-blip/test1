#!/usr/bin/env python3
"""Manim 장면 길이표(dur.json) 만들기: 음성을 받아쓰기해서 장면마다 화면에 머무는 시간을 잰다.
장면을 이 길이에 맞춰 렌더하면(scenes.py 의 fill) 말과 그림 길이가 같아 멈춘 화면이 생기지 않는다.
사용: python3 scene_dur.py 폴더(long.json·reels.json·shorts.json 있는 곳) 롱폼출력폴더
  → 폴더/manim/dur.json  {"장면": 초}. 롱폼 음성은 롱폼출력폴더/long.wav 로 저장(받아쓰기 캐시를 longform.py 가 다시 씀)."""
import json, os, sys
import soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
import faceless as F
import longform as LF

base, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
dur = {}
put = lambda f, d: dur.__setitem__(os.path.splitext(os.path.basename(f))[0], round(max(dur.get(os.path.splitext(os.path.basename(f))[0], 0), d), 2))

os.chdir(base)
cfg = json.load(open("long.json", encoding="utf-8"))
wav = os.path.join(out, "long.wav")
_, total = LF.build_audio(cfg["sections"], wav, cfg.get("tempo", 1.0))
words = F.whisper_words(wav)
subs = [ln["sub"] for s in cfg["sections"] for ln in s["lines"]]
_, spans = F.word_cues(subs, words)
off, k = {}, 0
for s in cfg["sections"]:
    off[s["key"]] = k; k += len(s["lines"])
plan = []
for f, at, _, _ in cfg["visuals"]:
    key, li = at.split(":"); plan.append((f, max(0.0, spans[off[key] + int(li)][0] - 0.2)))
plan.sort(key=lambda p: p[1]); plan[0] = (plan[0][0], 0.0)
for i, (f, t0) in enumerate(plan):
    put(f, (plan[i + 1][1] + 0.3 if i + 1 < len(plan) else total) - t0)
print(f"long {total:.1f}s")

for fn in ("reels.json", "shorts.json"):
    if not os.path.exists(fn):
        continue
    for key, v in json.load(open(fn, encoding="utf-8")).items():
        if key.startswith("_") or not os.path.exists(v["audio"]):
            continue
        w = F.whisper_words(v["audio"])
        y, sr = sf.read(v["audio"]); T = len(y) / sr
        _, sp = F.word_cues([l["sub"] for l in v["lines"]], w)
        vis = [(f, max(0.0, sp[int(at)][0] - 0.15)) for f, at, _, _ in v["visuals"]]
        for i, (f, t0) in enumerate(vis):
            put(f, (vis[i + 1][1] + 0.3 if i + 1 < len(vis) else T) - t0)
        print(fn, key, f"{T:.1f}s")
json.dump(dur, open(os.path.join(base, "manim", "dur.json"), "w"), indent=0, sort_keys=True)
print(len(dur), "scenes")
