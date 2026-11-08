# 롱폼(long.json)과 쇼츠·릴스 A~E(shorts.json, reels.json) 설정을 script.json 에서 만든다.
# 장면 시작초(네 번째 값)는 manim 장면 안에서 그 대사에 맞는 그림이 나오는 시각.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
pieces = json.load(open(f"{here}/pieces.json"))
st = json.load(open(f"{here}/../raw/stock1108/rec/starts.json"))
R = "../raw/stock1108/rec/"
V = lambda s: f"img/{s}.mp4"
LONG_KEYS = ["I", "S1", "S2", "S3", "R", "S4", "S5T", "S7", "O"]
long = {"title": "11월 둘째 주 증시 정리", "date": "11.6 마감 기준", "tempo": 1.0,
        "sections": [{"key": k, "chapter": d[k]["title"] if k != "I" else "",
                      "audio": [f"../raw/stock1108/v/{p}_long.wav" for p in pieces[k]],
                      "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]} for k in LONG_KEYS],
        "visuals": [
            [V("Intro3D"), "I:0", None, 0], [V("Breaker"), "I:1", None, 3.3], [V("Agenda"), "I:2", None, 0],
            [V("Week"), "S1:0", None, 0], [V("Week"), "S1:3", None, 13.2], [V("Week"), "S1:4", None, 19.0],
            [V("Election"), "S2:0", None, 0], [V("Election"), "S2:1", None, 5.4], [V("Election"), "S2:2", None, 11.8],
            [V("Election"), "S2:3", None, 15.8], [V("UsCrash"), "S2:4", None, 0], [V("UsCrash"), "S2:5", None, 8.2],
            [V("Week"), "S3:0", None, 8.4], [V("Chips"), "S3:1", None, 12.3], [V("Breaker"), "S3:2", None, 0],
            [V("Breaker"), "S3:3", None, 8.0], [V("Chips"), "S3:4", None, 0],
            [V("Recap"), "R:0", None, 0],
            [V("UsFri"), "S4:0", None, 0], [V("UsFri"), "S4:2", None, 5.6], [V("UsFri"), "S4:3", None, 10.6], [V("UsFri"), "S4:4", None, 16.8],
            [R + "th_week.webm", "S5T:0", None, st["th_week"] + .5], [R + "th_week.webm", "S5T:1", None, st["th_week"] + 11.5],
            [R + "th_week.webm", "S5T:2", None, st["th_week"] + 17.0],
            [V("NextWeek"), "S7:0", None, 0], [V("NextWeek"), "S7:2", None, 3.8], [V("NextWeek"), "S7:3", None, 6.9],
            [V("NextWeek"), "S7:4", None, 10.0], [V("NextWeek"), "S7:5", None, 13.3],
            [V("Summary"), "O:0", None, 0], [V("Summary"), "O:1", None, 4.9], [V("Summary"), "O:2", None, 8.6],
            [R + "site.webm", "O:3", None, st["site"]]]}
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
VIS = {
    "A": [[V("Intro3D"), 0, None, 0], [V("Week"), 1, None, 0], [V("Breaker"), 2, None, 3.3],
          [V("Week"), 3, None, 13.2], [V("Recap"), 4, None, 0]],
    "B": [[V("UsCrash"), 0, None, 0], [V("Election"), 1, None, 5.4], [V("Election"), 2, None, 11.8],
          [V("UsCrash"), 3, None, 8.2], [V("UsFri"), 4, None, 0]],
    "C": [[V("Breaker"), 0, None, 3.3], [V("UsCrash"), 1, None, 0], [V("Breaker"), 2, None, 6.4],
          [V("Breaker"), 3, None, 8.4], [V("NextWeek"), 4, None, 13.5]],
    "D": [[V("Chips"), 0, None, 0], [V("Chips"), 2, None, 5.8], [V("Chips"), 3, None, 12.3],
          [V("Election"), 4, None, 15.8]],
    "E": [[V("NextWeek"), 0, None, 0], [V("UsFri"), 1, None, 6.1], [V("NextWeek"), 2, None, 3.8],
          [V("NextWeek"), 3, None, 6.9], [V("NextWeek"), 4, None, 13.5]],
}
CTA = {"reel": ["팔로우 + 댓글 '증시'", "DM으로 사이트 링크 보내 드려요"],
       "short": ["지난주 전체 정리 롱폼 · 사이트 링크", "고정 댓글에 있어요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"증시 2026-11-08 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/stock1108/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
