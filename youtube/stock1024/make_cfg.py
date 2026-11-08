# 롱폼(long.json)과 쇼츠·릴스 A~E(shorts.json, reels.json) 설정을 script.json 에서 만든다.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
pieces = json.load(open(f"{here}/pieces.json"))
st = json.load(open(f"{here}/../raw/stock1024/rec/starts.json"))
R = "../raw/stock1024/rec/"
V = lambda s: f"img/{s}.mp4"
LONG_KEYS = ["I", "S1", "S2", "S3", "S4", "S4T", "S5", "S6", "S7", "O"]
long = {"title": "이번 주 증시 정리", "date": "10.23 마감 기준", "tempo": 1.0,
        "sections": [{"key": k, "chapter": d[k]["title"] if k != "I" else "",
                      "audio": [f"../raw/stock1024/v/{p}_long.wav" for p in pieces[k]],
                      "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]} for k in LONG_KEYS],
        "visuals": [
            [V("Intro3D"), "I:0", None, 0], [V("Agenda"), "I:2", None, 0],
            [V("FriKospi"), "S1:0", None, 0], [V("Hynix"), "S1:2", None, 0], [V("Flows"), "S1:4", None, 0],
            [V("UsNight"), "S2:0", None, 0], [V("Oil"), "S2:2", None, 0], [V("Spread"), "S2:4", None, 0],
            [V("Zigzag"), "S3:0", None, 0], [V("Intro3D"), "S3:2", None, 0], [V("Zigzag"), "S3:3", None, 9.7],
            [V("AiTimeline"), "S4:0", None, 0], [V("AiBars"), "S4:3", None, 0],
            [R + "th_week.webm", "S4T:0", None, st["th_week"]],
            [V("Oil"), "S5:0", None, 0], [V("Macro"), "S5:2", None, 0],
            [V("Score3D"), "S6:0", None, 0], [V("BigTwoFlat"), "S6:2", None, 0], [V("Score3D"), "S6:4", None, 6.0],
            [V("NextWeek"), "S7:0", None, 0], [V("Summary"), "O:0", None, 0], [R + "site.webm", "O:3", None, st["site"]]]}
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
VIS = {
    "A": [[V("FriKospi"), 0, None, 4.5], [V("FriKospi"), 1, None, 1.0], [V("Hynix"), 2, None, 0.3],
          [V("Hynix"), 3, None, 2.2], [V("Flows"), 4, None, 0.8]],
    "B": [[V("Intro3D"), 0, None, 0], [V("Zigzag"), 1, None, 0.5], [V("Zigzag"), 2, None, 9.7],
          [V("BigTwoFlat"), 3, None, 0.5], [V("Score3D"), 4, None, 4.0]],
    "C": [[V("AiTimeline"), 0, None, 3.5], [V("AiTimeline"), 1, None, 5.0], [V("AiBars"), 2, None, 0.3],
          [V("AiBars"), 3, None, 3.0], [R + "th_week.webm", 4, None, st["th_week"]]],
    "D": [[V("UsNight"), 0, None, 1.5], [V("Oil"), 1, None, 4.8], [V("Oil"), 2, None, 5.6],
          [V("Macro"), 3, None, 0.3], [V("Spread"), 4, None, 0.3]],
    "E": [[V("NextWeek"), 0, None, 0.3], [V("NextWeek"), 1, None, 1.0], [V("NextWeek"), 2, None, 3.4],
          [V("AiBars"), 3, None, 3.5], [V("FriKospi"), 4, None, 6.0]],
}
CTA = {"reel": ["팔로우 + 댓글 '증시'", "DM으로 사이트 링크 보내 드려요"],
       "short": ["이번 주 전체 정리 롱폼 · 사이트 링크", "고정 댓글에 있어요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"증시 2026-10-24 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/stock1024/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
