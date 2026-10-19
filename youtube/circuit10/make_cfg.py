# 회로이론 3분 정리: script.json → 롱폼 long.json, 쇼츠/릴스 reels.json·shorts.json (faceless.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
lt = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
V = "../raw/circuit10/v/"
LONG_VIS = [("Hook", "I:0"), ("Three", "I:1"), ("Circuit", "S1:0"), ("Three", "S2:0"), ("KillRule", "S2:2"),
            ("Sup1", "S2:4"), ("Sup2", "S2:6"), ("SupSum", "S2:8"), ("Thev", "S3:0"), ("Rth", "S3:4"),
            ("ThevDone", "S3:7"), ("Norton", "S4:0"), ("NortonCheck", "S4:5"), ("When", "S5:0"),
            ("MaxPower", "S6:0"), ("Mistakes", "S7:0"), ("Summary", "S8:0")]
SEC = ["I", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
long = {"title": "테브난·노턴·중첩", "date": "회로이론", "tempo": 1.04, "sections": [],
        "visuals": [[f"img/{f}.mp4", at, None, 0] for f, at in LONG_VIS]}
for k in SEC:
    chunks = sorted([c for c in lt if c.startswith(k + "_")], key=lambda c: int(c.split("_")[1]))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else d[k]["title"],
                             "audio": [f"{V}{c}_long.wav" for c in chunks],
                             "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = None   # 16:9 장면 전체를 가로에 맞춤 (오른쪽 수식이 잘리지 않게)
VIS = {
    "A": [["Hook", 0, 0], ["Thev", 1, 0], ["Thev", 2, 5.5], ["Rth", 3, 1.0], ["ThevDone", 4, 4.0]],
    "B": [["NortonCheck", 0, 0], ["Norton", 1, 0], ["Norton", 2, 4.4], ["NortonCheck", 4, 1.2]],
    "C": [["Circuit", 0, 12], ["Three", 1, 0], ["Sup1", 2, 0], ["Sup2", 3, 0], ["SupSum", 4, 0]],
    "D": [["KillRule", 0, 0], ["When", 3, 9.5], ["Mistakes", 4, 0]],
    "E": [["MaxPower", 0, 0], ["MaxPower", 2, 3.0]],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"회로이론 3분 정리 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"],
                  "visuals": [[f"img/{f}.mp4", i, C, ss] for f, i, ss in VIS[k]],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"{V}{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
