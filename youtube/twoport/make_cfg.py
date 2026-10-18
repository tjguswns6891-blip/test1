# 2포트 롱폼(long.json)과 쇼츠·릴스 A/B/C 의 faceless.py 설정(reels.json, shorts.json)을 script.json 에서 만든다.
# 사이트 녹화 시각은 raw/twoport/rec/boxes.json 의 _marks (p1 8.0 · p2 17.5 · recip 27.5 · p1_again 35.5 초)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
REC = "../raw/twoport/rec/tp_measure.webm"; BOX = [494, 15, 880, 608]
S = lambda n: f"img/{n}.mp4"
LONG_VIS = [
    [S("Hook"), "I:0", None, 0], [REC, "I:3", BOX, 8.0],
    [S("BlackBox"), "S1:0", None, 0], [S("ZParams"), "S2:0", None, 0],
    [REC, "S3:0", BOX, 8.0], [S("MeasureOpen"), "S3:3", None, 0],
    [REC, "S4:0", BOX, 17.5], [S("Reciprocity"), "S4:2", None, 0], [REC, "S4:3", BOX, 27.5],
    [S("YTrap"), "S5:0", None, 0], [S("HParam"), "S6:0", None, 0], [S("Cascade"), "S7:0", None, 0],
    [S("Connections"), "S8:0", None, 0], [S("HParam"), "S9:0", None, 4.0], [S("Cascade"), "S9:1", None, 4.0],
    [S("Summary"), "O:0", None, 0], [REC, "O:3", BOX, 35.5],
]
long = {"title": "2포트 회로", "date": "보이는 회로이론 17장", "tempo": 0.95, "sections": [], "visuals": LONG_VIS}
for k, v in d.items():
    if k.startswith(("_", "cta")) or k in "ABC":
        continue
    t = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else v["title"],
                             "audio": [f"../raw/twoport/v/{c}_long.wav" for c in t if c.startswith(k + "_")],
                             "lines": [{"sub": l["sub"]} for l in v["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

VIS = {
    "A": [[S("Hook"), 0, None, 0.5], [S("BlackBox"), 1, None, 1.5], [REC, 2, BOX, 8.0],
          [REC, 3, BOX, 17.5], [S("Hook"), 4, None, 4.0]],
    "B": [[S("HParam"), 0, None, 0.5], [S("BlackBox"), 1, None, 1.5], [S("HParam"), 2, None, 2.5],
          [S("HParam"), 3, None, 4.5], [S("Summary"), 4, None, 3.0]],
    "C": [[S("Cascade"), 0, None, 0.5], [S("Cascade"), 1, None, 1.5], [S("Cascade"), 2, None, 3.5],
          [S("Connections"), 3, None, 3.0], [S("Cascade"), 4, None, 5.0]],
}
CTA = {"reel": ["시험 전에 저장 + 친구 태그", "사이트 링크는 프로필에"], "short": ["2포트 회로 전체 정리", "관련 영상에서 보세요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"2포트 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABC":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/twoport/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
