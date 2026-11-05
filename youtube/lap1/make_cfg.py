# 라플라스 심화 1편: script.json → 롱폼 long.json, 쇼츠/릴스 reels.json·shorts.json (faceless.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
lt = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
V = "../raw/lap1/v/"
LONG_VIS = {"I": ["Hook", "Inv", "Three", "Roadmap"],
            "S1": ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"],
            "S2": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9"],
            "S3": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
            "S4": ["M1", "M2", "M3", "M4"],
            "S5": ["V1", "V2", "V3", "V4", "V5", "V6", "V7"],
            "O": ["O1", "O2", "O3", "Site", "Next"]}
SEC = list(LONG_VIS)
for k in SEC:
    assert len(LONG_VIS[k]) == len(d[k]["lines"]), k
long = {"title": "라플라스 역변환", "date": "회로이론", "tempo": 1.0, "sections": [],
        "visuals": [[f"img/{f}.mp4", f"{k}:{i}", None, 0] for k in SEC for i, f in enumerate(LONG_VIS[k])]}
for k in SEC:
    chunks = sorted([c for c in lt if c.startswith(k + "_")], key=lambda c: int(c.split("_")[1]))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else d[k]["title"],
                             "audio": [f"{V}{c}_long.wav" for c in chunks],
                             "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = None   # 16:9 장면 전체를 가로에 맞춤
VIS = {     # 문장마다 장면 하나 (마지막 CTA 문장은 앞 장면 유지)
    "A": ["AQ", "D3", "D4", "D7", "D8"],
    "B": ["BQ", "R5", "R2", "R4", "R6"],
    "C": ["CQ", "C2", "C5", "C6", "C8"],
    "D": ["DQ", "V2", "V5", "V6", "V7"],
    "E": ["EQ", "M2", "R6", "C5", "M4"],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"라플라스 심화 1편 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"],
                  "visuals": [[f"img_s/{f}.mp4", i, C, 0] for i, f in enumerate(VIS[k])],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"{V}{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
