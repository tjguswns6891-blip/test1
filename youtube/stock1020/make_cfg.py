# 롱폼(long.json)과 쇼츠·릴스 A/B/C(shorts.json, reels.json) 설정을 script.json 에서 만든다.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
pieces = json.load(open(f"{here}/pieces.json"))
st = json.load(open(f"{here}/../raw/stock1020/rec/starts.json"))
R = "../raw/stock1020/rec/"
V = lambda s: f"img/{s}.mp4"
LONG_KEYS = ["I", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "O"]
long = {"title": "오늘 증시 분석", "date": "2026.10.20 마감 기준", "tempo": 1.0,   # 음성 파일에 이미 ×1.05
        "sections": [{"key": k, "chapter": d[k]["title"] if k != "I" else "",
                      "audio": [f"../raw/stock1020/v/{p}_long.wav" for p in pieces[k]],
                      "lines": [{"sub": l["sub"]} for l in d[k]["lines"]]} for k in LONG_KEYS],
        "visuals": [
            [V("Intro3D"), "I:0", None, 0], [V("KoreaVsUs"), "I:2", None, 0],
            [V("KospiDay"), "S1:0", None, 0], [V("Flows"), "S1:3", None, 0], [V("BigTwo"), "S1:4", None, 0],
            [V("TenDays"), "S1:5", None, 0], [V("KospiYear"), "S1:6", None, 0],
            [V("UsNight"), "S2:0", None, 0], [R + "th_day.webm", "S2:1", None, st["th_day"] + 3], [V("UsNight"), "S2:2", None, 5.0],
            [V("Elice"), "S3:0", None, 0], [V("DcDoubt"), "S3:2", None, 0], [R + "th_week.webm", "S3:3", None, st["th_week"] + 4],
            [R + "th_day.webm", "S3:4", None, st["th_day"] + 4],
            [V("Concentration"), "S4:0", None, 0], [V("KoreaVsUs"), "S4:2", None, 2.0],
            [V("Rates"), "S5:0", None, 0], [V("Defense"), "S6:0", None, 0],
            [V("ThisWeek"), "S7:0", None, 0], [V("Summary"), "O:0", None, 0]]}
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
TH = [180, 40, 1350, 1050]                                   # 사이트 녹화에서 테마 지도 칸
VIS = {
    "A": [[V("KoreaVsUs"), 0, None, 0.5], [V("KospiDay"), 1, None, 6.5], [V("TenDays"), 2, None, 3.0],
          [V("Flows"), 3, None, 1.0], [V("DcDoubt"), 4, None, 1.5]],
    "B": [[V("Elice"), 0, None, 1.0], [V("Elice"), 1, None, 0.3], [V("Elice"), 2, None, 2.8],
          [V("DcDoubt"), 3, None, 0.5], [R + "th_week.webm", 4, TH, st["th_week"] + 4]],
    "C": [[V("Defense"), 0, None, 1.0], [V("Defense"), 1, None, 2.2], [V("Defense"), 2, None, 2.6],
          [V("Defense"), 3, None, 4.0], [V("KospiDay"), 4, None, 6.5]],
    "D": [[V("Concentration"), 0, None, 1.0], [V("Concentration"), 1, None, 4.0], [V("BigTwo"), 2, None, 1.0],
          [V("Concentration"), 3, None, 6.5], [V("KoreaVsUs"), 4, None, 2.0]],
    "E": [[V("UsNight"), 0, None, 5.0], [V("UsNight"), 1, None, 5.5], [V("Rates"), 2, None, 0.5],
          [V("Rates"), 3, None, 3.5], [V("KospiDay"), 4, None, 6.5]],
    "F": [[V("ThisWeek"), 0, None, 0.5], [V("ThisWeek"), 1, None, 2.5], [V("ThisWeek"), 2, None, 5.0],
          [V("DcDoubt"), 3, None, 1.5], [V("KospiDay"), 4, None, 4.0]],
}
CTA = {"reel": ["팔로우 + 댓글 '증시'", "DM으로 사이트 링크 보내 드려요"],
       "short": ["전체 분석 롱폼 · 사이트 링크", "고정 댓글에 있어요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"증시 2026-10-20 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDEF":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/stock1020/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
