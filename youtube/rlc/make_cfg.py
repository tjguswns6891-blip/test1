# RLC 롱폼(long.json)과 쇼츠·릴스 A/B/C 의 faceless.py 설정(reels.json, shorts.json)을 script.json 에서 만든다.
# 사이트 녹화 시각은 raw/rlc/rec/boxes.json 의 _marks (over 11.5 · sweep 18 · crit 29.9 · under 36.5 · low 45.9 초)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
REC = "../raw/rlc/rec/rlc_sweep.webm"; BOX = [494, 15, 880, 625]
S = lambda n: f"img/{n}.mp4"
LONG_VIS = [
    [S("Hook"), "I:0", None, 0], [REC, "I:3", BOX, 37.5], [S("PoleSweep"), "I:4", None, 0],
    [S("Energy"), "S1:0", None, 0], [S("SDomain"), "S2:0", None, 0], [S("CharEq"), "S3:0", None, 0],
    [S("Overdamped"), "S4:0", None, 0], [REC, "S4:3", BOX, 12.0],
    [S("Critical"), "S5:0", None, 0],
    [S("Underdamped"), "S6:0", None, 0],
    [REC, "S7:0", BOX, 10.5], [REC, "S7:2", BOX, 25.0], [REC, "S7:3", BOX, 36.5], [REC, "S7:4", BOX, 45.5], [S("PoleSweep"), "S7:5", None, 6.0],
    [S("Suspension"), "S8:0", None, 0], [S("Underdamped"), "S8:4", None, 3.0],
    [S("Summary"), "O:0", None, 0], [REC, "O:3", BOX, 45.5],
]
long = {"title": "2차 RLC 회로", "date": "보이는 회로이론 8장", "tempo": 0.95, "sections": [], "visuals": LONG_VIS}
for k, v in d.items():
    if k.startswith(("_", "cta")) or k in "ABC":
        continue
    t = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else v["title"],
                             "audio": [f"../raw/rlc/v/{c}_long.wav" for c in t if c.startswith(k + "_")],
                             "lines": [{"sub": l["sub"]} for l in v["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

VIS = {
    "A": [[S("Hook"), 0, None, 0.5], [S("Overdamped"), 1, None, 3.0], [S("Critical"), 2, None, 3.0],
          [S("Underdamped"), 3, None, 3.0], [S("PoleSweep"), 4, None, 4.0]],
    "B": [[REC, 0, BOX, 29.0], [S("Critical"), 1, None, 6.0], [S("Critical"), 2, None, 7.5],
          [S("PoleSweep"), 3, None, 2.0], [REC, 4, BOX, 30.0]],
    "C": [[S("Suspension"), 0, None, 0.5], [S("Suspension"), 1, None, 3.0], [S("Suspension"), 2, None, 5.5],
          [S("PoleSweep"), 3, None, 8.0], [S("Hook"), 4, None, 4.0]],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"RLC {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABC":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/rlc/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
