# 쇼츠·릴스 A~C 설정(shorts.json, reels.json)을 script.json + 타이밍으로 만든다. 그래픽은 영상마다 통짜 한 편(raw/stock1128/mg/<키>.mp4),
# 사이트 녹화가 들어가는 문장만 그 위에 덮는다.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8")); tm = json.load(open(f"{here}/../raw/stock1128/mg/timing.json"))
M = lambda k: f"../raw/stock1128/mg/{k}.mp4"; R = "../raw/stock1128/rec/"
SITE = {"B": (4, R + "chart.mp4"), "C": (1, R + "signal.mp4")}      # (문장 번호, 녹화)
CTA = {"reel": ["팔로우 + 댓글 '증시'", "DM으로 사이트 링크 보내 드려요"], "short": ["제가 만든 증시 사이트 링크", "고정 댓글에 있어요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"증시 2026-11-28 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABC":
        if k not in tm: continue
        v = d[k]; vis = [[M(k), 0, None, 0]]
        if k in SITE:
            i, f = SITE[k]; vis += [[f, i, None, 0], [M(k), i + 1, None, tm[k]["S"][i + 1]]]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": vis,
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/stock1128/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
