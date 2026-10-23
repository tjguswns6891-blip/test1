# RC·RL 과도응답: script.json → 롱폼 long.json, 쇼츠/릴스 reels.json·shorts.json (faceless.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
lt = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
V = "../raw/transient/v/"
LONG_VIS = {"I": ["Hook", "Roadmap", "OneFormula"],
            "S1": ["Cont1", "Cont2", "Cont3", "Dual"],
            "S2": ["RCckt", "RCstart", "Slow", "Tau", "TauCalc", "Ch1", "Ch2", "Ch5"],
            "S3": ["Dis1", "Dis2", "Dis3", "Dis4"],
            "S4": ["RL1", "RL2", "RL3", "RL4", "RL5"],
            "S5": ["Uni1", "Uni2", "Uni3", "Uni4"],
            "S6": ["Sw1", "Sw2", "Sw3", "Sw4", "Sw5", "Sw6", "Sw7", "Sw8"],
            "S7": ["Sum1", "Sum2", "Sum3", "Site"]}
SEC = list(LONG_VIS)
for k in SEC:
    assert len(LONG_VIS[k]) <= len(d[k]["lines"]), k
long = {"title": "RC·RL 과도응답", "date": "회로이론", "tempo": 1.0, "sections": [],
        "visuals": [[f"img/{f}.mp4", f"{k}:{i}", None, 0] for k in SEC for i, f in enumerate(LONG_VIS[k])]}
for k in SEC:
    chunks = sorted([c for c in lt if c.startswith(k + "_")], key=lambda c: int(c.split("_")[1]))
    long["sections"].append({"key": k, "chapter": "" if k == "I" else d[k]["title"],
                             "audio": [f"{V}{c}_long.wav" for c in chunks],
                             "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = None   # 16:9 장면 전체를 가로에 맞춤
VIS = {
    "A": ["Ch1", "TauCalc", "Ch1", "Dis3", "Ch5"],
    "B": ["Hook", "Cont1", "Cont2", "Cont3", "Dual"],
    "C": ["Sw1", "Sw4", "Sw5", "Sw6", "Sw8"],
    "D": ["RL1", "RL2", "RL3", "RL5", "Sum2"],
    "E": ["Uni1", "Uni2", "Uni3", "Uni4", "Sw8"],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"RC·RL 과도응답 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"],
                  "visuals": [[f"img/{f}.mp4", i, C, 0] for i, f in enumerate(VIS[k])],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"{V}{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
