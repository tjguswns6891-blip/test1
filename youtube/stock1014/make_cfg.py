# 증시 쇼츠·릴스 A/B/C 의 faceless.py 설정(reels.json, shorts.json)을 script.json 에서 만든다.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
st = json.load(open(f"{here}/../raw/stock1014/rec/starts.json"))
R = "../raw/stock1014/rec/"
M = [120, 0, 1680, 1080]                                   # Manim 16:9 → 가운데 칸
TOP, CH, TH = [285, 120, 1350, 1050], [300, 60, 1300, 1010], [180, 40, 1350, 1050]
VIS = {
    "A": [["img/KospiPath.mp4", 0, M, 1.2], ["img/Flows.mp4", 1, M, 0], ["img/KospiPath.mp4", 2, M, 6],
          ["img/Diverge.mp4", 3, M, 0], ["img/Week.mp4", 4, M, 0]],
    "B": [["img/ThemeBars.mp4", 0, M, 2.2], [R + "inv_top.webm", 1, TOP, st["inv_top"]],
          [R + "th_week.webm", 2, TH, st["th_week"] + 4], [R + "th_week.webm", 3, [150, 560, 670, 520], st["th_week"] + 8],
          ["img/ThemeBars.mp4", 4, M, 5]],
    "C": [["img/Week.mp4", 0, M, 2.3], ["img/Scenario.mp4", 1, M, 0], [R + "inv_rates.webm", 2, CH, st["inv_rates"] + 6],
          ["img/Scenario.mp4", 3, M, 3], ["img/Week.mp4", 4, M, 4]],
}
CTA = {"reel": ["팔로우 + 댓글 '증시'", "DM으로 사이트 링크 보내 드려요"],
       "short": ["전체 분석 롱폼 · 사이트 링크", "고정 댓글에 있어요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"증시 2026-10-14 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABC":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/stock1014/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
