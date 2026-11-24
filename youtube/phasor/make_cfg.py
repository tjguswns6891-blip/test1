# 페이저: script.json → 롱폼 long.json, 쇼츠/릴스 reels.json·shorts.json (faceless.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
lt = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
V = "../raw/phasor/v/"
LONG_VIS = {"I": ["Hook", "Goal", "Roadmap"],
            "S1": ["W1", "W2", "W3", "W4", "W5", "W6"],
            "S2": ["PH1", "PH2", "PH3", "PH4", "PH5", "PH6"],
            "S3": ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"],
            "S4": ["L1", "L2", "L3", "L4", "L5", "L6"],
            "S5": ["C1", "C2", "C3", "C4", "C5", "C6"],
            "S6": ["F1", "F2", "F3", "Site", "Next"]}
SEC = list(LONG_VIS)
for k in SEC:
    assert len(LONG_VIS[k]) == len(d[k]["lines"]), k
long = {"title": "페이저와 임피던스", "date": "회로이론", "tempo": 1.0, "sections": [],
        "visuals": [[f"img/{f}.mp4", f"{k}:{i}", None, 0] for k in SEC for i, f in enumerate(LONG_VIS[k])]}
for k in SEC:
    chunks = sorted([c for c in lt if c.startswith(k + "_")], key=lambda c: int(c.split("_")[1]))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else d[k]["title"],
                             "audio": [f"{V}{c}_long.wav" for c in chunks],
                             "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = None   # 16:9 장면 전체를 가로에 맞춤
VIS = {     # 문장마다 장면 하나 (마지막 CTA 문장은 앞 장면 유지)
    "A": ["AQ", "AWrong", "Z3", "L6", "ATri"],
    "B": ["BQ", "PH1", "BDiff", "PH5", "PH6"],
    "C": ["CQ", "Z3", "CDC", "Z6", "Z5"],
    "D": ["DQ", "L2", "L3", "DMag", "DCur"],
    "E": ["EQ", "C2", "C3", "C4", "C5"],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"페이저 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"],
                  "visuals": [[f"img_s/{f}.mp4", i, C, 0] for i, f in enumerate(VIS[k])],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"{V}{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
