# 교류 전력: script.json → 롱폼 long.json, 쇼츠/릴스 reels.json·shorts.json (faceless.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
lt = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
V = "../raw/acpower/v/"
LONG_VIS = {"I": ["Hook", "Goal", "Roadmap"],
            "S1": ["P1", "P2", "P3f", "P4", "P5", "P6"],
            "S2": ["R1", "R2", "R3", "R4", "R5", "R6"],
            "S3": ["A1", "A2", "A3", "A4", "A5", "Sum1"],
            "S4": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
            "S5": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "Sum2"],
            "S6": ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9"],
            "S7": ["F1", "F2", "F3", "Site", "Next"]}
SEC = list(LONG_VIS)
for k in SEC:
    assert len(LONG_VIS[k]) == len(d[k]["lines"]), k
long = {"title": "교류 전력", "date": "회로이론", "tempo": 1.0, "sections": [],
        "visuals": [[f"img/{f}.mp4", f"{k}:{i}", None, 0] for k in SEC for i, f in enumerate(LONG_VIS[k])]}
for k in SEC:
    chunks = sorted([c for c in lt if c.startswith(k + "_")], key=lambda c: int(c.split("_")[1]))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else d[k]["title"],
                             "audio": [f"{V}{c}_long.wav" for c in chunks],
                             "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = None   # 16:9 장면 전체를 가로에 맞춤
VIS = {     # 문장마다 장면 하나 (마지막 CTA 문장은 앞 장면 유지)
    "A": ["R2", "R4", "R3", "R5", "R6"],
    "B": ["Q1", "P6", "Q2", "Q3", "Q4"],
    "C": ["T1", "T2", "T3", "T4", "E4"],
    "D": ["D1", "T6", "D2", "T7", "E9"],
    "E": ["Hook", "E3", "E6", "E7", "E9"],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"교류 전력 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"],
                  "visuals": [[f"img_s/{f}.mp4", i, C, 0] for i, f in enumerate(VIS[k])],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"{V}{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
