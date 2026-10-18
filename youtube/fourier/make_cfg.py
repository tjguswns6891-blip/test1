# 푸리에 롱폼(long.json)과 쇼츠·릴스 A/B/C 의 faceless.py 설정(reels.json, shorts.json)을 script.json 에서 만든다.
# 사이트 녹화 시각은 raw/fourier/rec/boxes.json 의 _marks (sq_build 9.1 · gibbs 26.1 · saw 31.6 · tri_build 39.6 초)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
REC = "../raw/fourier/rec/fs_build.webm"; BOX = [494, 15, 880, 630]
S = lambda n: f"img/{n}.mp4"
LONG_VIS = [
    [S("Hook"), "I:0", None, 0], [REC, "I:2", BOX, 9.1],
    [S("PhasorLimit"), "S1:0", None, 0], [S("Series"), "S2:0", None, 0], [S("Orthogonality"), "S3:0", None, 0],
    [REC, "S4:0", BOX, 7.5], [S("SquareBuild"), "S4:1", None, 0], [REC, "S4:4", BOX, 9.1],
    [REC, "S5:0", BOX, 24.0], [S("Gibbs"), "S5:2", None, 0],
    [S("TriSaw"), "S6:0", None, 0], [REC, "S6:1", BOX, 39.6], [REC, "S6:2", BOX, 31.6], [S("TriSaw"), "S6:3", None, 5.0],
    [S("Symmetry"), "S7:0", None, 0], [S("RCFilter"), "S8:0", None, 0],
    [S("Timbre"), "S9:0", None, 0], [REC, "S9:2", BOX, 26.1],
    [S("Summary"), "O:0", None, 0], [REC, "O:3", BOX, 9.1],
]
long = {"title": "푸리에 급수", "date": "보이는 회로이론 16장", "tempo": 0.95, "sections": [], "visuals": LONG_VIS}
for k, v in d.items():
    if k.startswith(("_", "cta")) or k in "ABC":
        continue
    t = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else v["title"],
                             "audio": [f"../raw/fourier/v/{c}_long.wav" for c in t if c.startswith(k + "_")],
                             "lines": [{"sub": l["sub"]} for l in v["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

VIS = {
    "A": [[S("Hook"), 0, None, 0.5], [S("SquareBuild"), 1, None, 1.5], [S("SquareBuild"), 2, None, 4.0],
          [REC, 3, BOX, 12.0], [S("Series"), 4, None, 2.0]],
    "B": [[REC, 0, BOX, 26.1], [S("Gibbs"), 1, None, 1.0], [S("Gibbs"), 2, None, 4.0],
          [S("Gibbs"), 3, None, 7.0], [REC, 4, BOX, 26.5]],
    "C": [[S("Timbre"), 0, None, 0.5], [S("Timbre"), 1, None, 2.0], [S("Timbre"), 2, None, 4.0],
          [S("Series"), 3, None, 2.0], [S("PhasorLimit"), 4, None, 3.0]],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"푸리에 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABC":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/fourier/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
