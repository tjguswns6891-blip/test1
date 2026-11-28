# 롱폼(long.json)과 쇼츠·릴스 A~E(shorts.json, reels.json) 설정을 script.json 에서 만든다.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
pieces = json.load(open(f"{here}/pieces.json"))
st = json.load(open(f"{here}/../raw/stock1102/rec/starts.json"))
R = "../raw/stock1102/rec/"
V = lambda s: f"img/{s}.mp4"
LONG_KEYS = ["I", "S1", "S2", "S3", "S4", "S5", "S5T", "S7", "O"]
long = {"title": "11월 첫 주 증시 정리", "date": "11.2 마감 기준", "tempo": 1.0,
        "sections": [{"key": k, "chapter": d[k]["title"] if k != "I" else "",
                      "audio": [f"../raw/stock1102/v/{p}_long.wav" for p in pieces[k]],
                      "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]} for k in LONG_KEYS],
        "visuals": [
            [V("Duel3D"), "I:0", None, 0], [V("Intro3D"), "I:1", None, 0], [V("Agenda"), "I:2", None, 0],
            [V("TodayKospi"), "S1:0", None, 0],
            [V("Intel"), "S2:0", None, 0], [V("UsFri"), "S2:3", None, 0],
            [V("Week"), "S3:0", None, 0],
            [V("Duel3D"), "S4:0", None, 0], [V("Duel"), "S4:2", None, 0],
            [V("AiDoubt"), "S5:0", None, 0], [V("Fomc"), "S5:5", None, 0],
            [R + "th_week.webm", "S5T:0", None, st["th_week"]],
            [V("NextWeek"), "S7:0", None, 0], [V("Summary"), "O:0", None, 0], [R + "site.webm", "O:3", None, st["site"]]]}
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
VIS = {
    "A": [[V("Duel3D"), 0, None, 0], [V("Duel"), 1, None, 6.3], [V("Duel"), 2, None, 8.6],
          [V("Duel"), 3, None, 11.3], [V("Duel3D"), 4, None, 7.0]],
    "B": [[V("Intel"), 0, None, 6.2], [V("Intel"), 1, None, 0], [V("Intel"), 2, None, 6.6],
          [V("UsFri"), 3, None, 0.3], [V("AiDoubt"), 4, None, 1.0]],
    "C": [[V("Week"), 0, None, 2.6], [V("Intro3D"), 1, None, 3.2], [V("Week"), 2, None, 6.0],
          [V("Week"), 3, None, 9.0], [V("Week"), 4, None, 13.5]],
    "D": json.load(open(f"{here}/today.json", encoding="utf-8"))["d_vis"],
    "E": [[V("NextWeek"), 0, None, 0.3], [V("NextWeek"), 1, None, 1.2], [V("NextWeek"), 2, None, 3.8],
          [V("NextWeek"), 3, None, 6.5], [V("NextWeek"), 4, None, 8.6]],
}
CTA = {"reel": ["팔로우 + 댓글 '증시'", "DM으로 사이트 링크 보내 드려요"],
       "short": ["지난주 전체 정리 롱폼 · 사이트 링크", "고정 댓글에 있어요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"증시 2026-11-02 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/stock1102/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
