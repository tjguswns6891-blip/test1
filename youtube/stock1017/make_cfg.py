# 증시 쇼츠·릴스 A/B/C 의 faceless.py 설정(reels.json, shorts.json)을 script.json 에서 만든다.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
st = json.load(open(f"{here}/../raw/stock1017/rec/starts.json"))
R = "../raw/stock1017/rec/"
M = [120, 0, 1680, 1080]                                   # Manim 16:9 → 가운데 칸
TOP, CH, TH = [285, 120, 1350, 1050], [300, 60, 1300, 1010], [180, 40, 1350, 1050]
VIS = {
    "A": [["img/BlackThursday.mp4", 0, None, 4.0], ["img/BlackThursday.mp4", 1, None, 5.5], ["img/ForeignSell.mp4", 2, None, 1.0],
          ["img/KospiPath.mp4", 3, None, 4.0], ["img/BlackThursday.mp4", 4, None, 6.5]],
    "B": [["img/Paradox.mp4", 0, None, 2.5], [R + "th_week.webm", 1, TH, st["th_week"] + 4], ["img/Paradox.mp4", 2, None, 3.5],
          ["img/AiDebt.mp4", 3, None, 2.5], ["img/AiDebt.mp4", 4, None, 4.0]],
    "C": [["img/NextWeek.mp4", 0, None, 2.5], ["img/NextWeek.mp4", 1, None, 3.0], ["img/Warsh.mp4", 2, None, 3.5],
          ["img/NextWeek.mp4", 3, None, 3.5], ["img/KospiPath.mp4", 4, None, 4.0]],
}
CTA = {"reel": ["팔로우 + 댓글 '증시'", "DM으로 사이트 링크 보내 드려요"],
       "short": ["전체 분석 롱폼 · 사이트 링크", "고정 댓글에 있어요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"증시 2026-10-17 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABC":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/stock1017/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
