# 회로 해석 기본(L1) 롱폼(long.json)과 클립 A~E 쇼츠·릴스(shorts.json, reels.json) 설정을 script.json 에서 만든다.
# 그래픽은 Manim 장면만 쓴다. 시작 초는 장면 안에서 그 문장 내용이 막 나오는 시각.
import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{here}/script.json", encoding="utf-8"))
t = json.load(open(f"{here}/long_tts.json", encoding="utf-8"))
S = lambda n: f"img/{n}.mp4"
V = lambda n, at, ss=0: [S(n), at, None, ss]
LONG_VIS = [
    V("Hook", "I:0"),
    V("Basics", "S1:0"), V("Basics", "S1:2", 3.6), V("Basics", "S1:3", 7.7), V("Basics", "S1:4", 11.6), V("Hook", "S1:5", 3.0),
    V("VDivider", "S2:0"), V("VDivider", "S2:2", 3.2), V("CDivider", "S2:3"), V("CDivider", "S2:4", 6.5), V("CDivider", "S2:5", 9.5),
    V("Nodal", "S3:0"), V("Nodal", "S3:1", 1.5), V("Nodal", "S3:2", 5.9), V("Nodal", "S3:4", 10.9), V("Nodal", "S3:5", 17.2),
    V("NodalMatrix", "S3:6"), V("NodalMatrix", "S3:7", 4.0), V("NodalMatrix", "S3:8", 7.3),
    V("Mesh", "S4:0"), V("Mesh", "S4:1", 1.4), V("Mesh", "S4:3", 7.3), V("Mesh", "S4:4", 12.3), V("Mesh", "S4:5", 17.7),
    V("MeshMatrix", "S4:7"),
    V("SourceTransform", "S5:0"), V("SourceTransform", "S5:1", 4.4), V("SourceTransform", "S5:2", 7.3),
    V("SourceTransform", "S5:3", 11.5), V("SourceTransform", "S5:4", 16.5), V("SourceTransform", "S5:5", 21.4),
    V("Dependent", "S6:0"), V("Dependent", "S6:1", 3.8), V("Dependent", "S6:2", 10.3), V("Dependent", "S6:3", .5),
    V("Dependent", "S6:4", 19.3), V("Dependent", "S6:5", 26.8),
    V("Choose", "S7:0"), V("Choose", "S7:1", 3.0), V("Choose", "S7:2", 8.0), V("Choose", "S7:3", 14.0), V("Choose", "S7:4", 20.0),
    V("Check", "S8:0"), V("Check", "S8:1", 3.2), V("Check", "S8:2", 7.7), V("Check", "S8:3", 11.7),
    V("Summary", "O:0"),
]
long = {"title": "회로 해석 기본", "date": "보이는 회로이론 2~4장", "tempo": 0.95, "sections": [], "visuals": LONG_VIS}
for k, v in d.items():
    if k.startswith(("_", "cta")) or k in "ABCDE":
        continue
    long["sections"].append({"key": k, "chapter": "" if k == "I" else v["title"],
                             "audio": [f"../raw/circuitbasics/v/{c}_long.wav" for c in t if c.startswith(k + "_")],
                             "lines": [{"sub": l["sub"]} for l in v["lines"]]})
json.dump(long, open(f"{here}/long.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

VIS = {
    "A": [V("CDivider", 0, 6.5), V("VDivider", 1, 1.5), V("CDivider", 2, 1.5), V("CDivider", 3, 6.5), V("CDivider", 4, 9.5)],
    "B": [V("Nodal", 0, 0), V("Nodal", 1, 1.5), V("Nodal", 2, 5.9), V("Nodal", 3, 10.9), V("Nodal", 4, 17.2)],
    "C": [V("Mesh", 0, 7.3), V("Mesh", 1, 1.4), V("Mesh", 2, 7.3), V("Mesh", 3, 12.3), V("Mesh", 4, 17.7)],
    "D": [V("SourceTransform", 0, 5.8), V("SourceTransform", 1, 0), V("SourceTransform", 2, 7.3), V("SourceTransform", 3, 11.5), V("SourceTransform", 4, 16.5)],
    "E": [V("Dependent", 0, 1.6), V("Dependent", 1, 3.8), V("Dependent", 2, 10.3), V("Dependent", 3, 19.3), V("Dependent", 4, 26.8)],
}
CTA = {"reel": ["시험 전에 저장해 두세요", "사이트 링크는 프로필에"], "short": ["단원 전체 정리 영상", "관련 영상에서 보세요"]}
for ver, fn in (("reel", "reels.json"), ("short", "shorts.json")):
    out = {"_설명": f"회로 해석 기본 {'인스타 릴스' if ver == 'reel' else '유튜브 쇼츠'} (faceless.py). make_cfg.py 로 만든다."}
    for k in "ABCDE":
        v = d[k]
        out[k] = {"title": v["title"], "chapter": v["chapter"], "visuals": VIS[k],
                  "lines": [{"sub": l["sub"]} for l in v["lines"]] + [{"sub": d["cta_" + ver]["sub"]}],
                  "cta": CTA[ver], "audio": f"../raw/circuitbasics/v/{k}_{ver}.wav"}
    json.dump(out, open(f"{here}/{fn}", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
