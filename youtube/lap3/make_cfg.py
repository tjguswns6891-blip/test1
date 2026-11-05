# 라플라스 심화 3편: script.json → 롱폼 long.json, 쇼츠/릴스 reels.json·shorts.json (faceless.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
lt = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
V = "../raw/lap3/v/"
LONG_VIS = {"I": ["Hook", "Three", "Poles2", "Roadmap"],
            "S1": ["E1", "E2", "E3", "E4", "E5", "E6"],
            "S2": ["F1", "F2", "F3", "F4", "F5", "F6"],
            "S3": ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"],
            "S4": ["H1", "H2", "H3", "H4"],
            "S5": ["J1", "J2", "J3", "J4"],
            "O": ["O1", "O2", "O3", "Site", "Next"]}
SEC = list(LONG_VIS)
for k in SEC:
    assert len(LONG_VIS[k]) == len(d[k]["lines"]), k
long = {"title": "2차 RLC", "date": "회로이론", "tempo": 1.0, "sections": [],
        "visuals": [[f"img/{f}.mp4", f"{k}:{i}", None, 0] for k in SEC for i, f in enumerate(LONG_VIS[k])]}
for k in SEC:
    chunks = sorted([c for c in lt if c.startswith(k + "_")], key=lambda c: int(c.split("_")[1]))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else d[k]["title"],
                             "audio": [f"{V}{c}_long.wav" for c in chunks],
                             "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = None   # 16:9 장면 전체를 가로에 맞춤
VIS = {     # 문장마다 장면 하나 (마지막 CTA 문장은 앞 장면 유지)
    "A": ["AQ", "G3", "G5", "G8", "Poles2"],
    "B": ["BQ", "F2", "G2", "G6", "G4"],
    "C": ["CQ", "G6", "J2", "J3", "J4"],
    "D": ["DQ", "H3", "H4", "DOsc", "DLC"],
    "E": ["EQ", "EOver", "G8", "G4", "ECrit"],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"라플라스 심화 3편 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"],
                  "visuals": [[f"img_s/{f}.mp4", i, C, 0] for i, f in enumerate(VIS[k])],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"{V}{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
