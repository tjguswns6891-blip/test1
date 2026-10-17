# 라플라스 쇼츠·릴스 A/B/C 의 faceless.py 설정(reels.json, shorts.json)을 script.json 에서 만든다.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
R = "../raw/laplace/rec/"; LAP = [494, 15, 880, 530]
VIS = {
    "A": [["img/Hook.mp4", 0, None, 0.5], ["img/LogAnalogy.mp4", 1, None, 3.2], ["img/Table4.mp4", 2, None, 3.5],
          ["img/RcSolve.mp4", 3, None, 4.0], ["img/LogAnalogy.mp4", 4, None, 5.0]],
    "B": [[R + "lap_drag.webm", 0, LAP, 85], ["img/PoleSurface.mp4", 1, None, 3.0], [R + "lap_drag.webm", 2, LAP, 39],
          [R + "lap_drag.webm", 3, LAP, 76], ["img/Apps.mp4", 4, None, 1.5]],
    "C": [["img/SDomain.mp4", 0, None, 2.0], ["img/SDomain.mp4", 1, None, 3.2], ["img/SDomain.mp4", 2, None, 4.4],
          ["img/SDomain.mp4", 3, None, 6.0], ["img/Summary.mp4", 4, None, 3.0]],
}
CTA = {"reel": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"], "short": ["무료 사이트 '보이는 회로이론'", "링크는 고정 댓글에"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"라플라스 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABC":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/laplace/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
