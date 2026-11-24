# 종속 전원: script.json → 롱폼 long.json, 쇼츠/릴스 reels.json·shorts.json (faceless.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
lt = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
V = "../raw/depsrc/v/"
LONG_VIS = {"I": ["Hook", "Goal", "Roadmap"],
            "S1": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
            "S2": ["N1", "N2", "N3", "N4", "N5", "N6"],
            "S3": ["T1", "T2", "T3", "T4", "T5", "T6"],
            "S4": ["M1", "M2", "M3", "M4", "M5", "M6"],
            "S5": ["U1", "U2", "U3", "U4", "U5", "U6"],
            "S6": ["E1", "E2", "E3", "Site", "Next"]}
SEC = list(LONG_VIS)
for k in SEC:
    assert len(LONG_VIS[k]) == len(d[k]["lines"]), k
long = {"title": "종속 전원", "date": "회로이론", "tempo": 1.0, "sections": [],
        "visuals": [[f"img/{f}.mp4", f"{k}:{i}", None, 0] for k in SEC for i, f in enumerate(LONG_VIS[k])]}
for k in SEC:
    chunks = sorted([c for c in lt if c.startswith(k + "_")], key=lambda c: int(c.split("_")[1]))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else d[k]["title"],
                             "audio": [f"{V}{c}_long.wav" for c in chunks],
                             "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = None   # 16:9 장면 전체를 가로에 맞춤
VIS = {     # 문장마다 장면 하나 (마지막 CTA 문장은 앞 장면 유지)
    "A": ["AQ", "Q1", "Q4", "Q5", "AUse"],
    "B": ["BQ", "T3", "T2", "T4", "T5"],
    "C": ["CQ", "COff", "CChg", "M3", "M4"],
    "D": ["DQ", "N2", "N4", "N5", "M5"],
    "E": ["EQ", "ERev", "EIsc", "U5", "U6"],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"종속 전원 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"],
                  "visuals": [[f"img_s/{f}.mp4", i, C, 0] for i, f in enumerate(VIS[k])],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"{V}{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
