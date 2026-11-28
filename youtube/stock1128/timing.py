# 음성(릴스판) 받아쓰기 → 모션그래픽 타이밍. 문장 시작초 S, 끝 end, 장면 코드의 K(문장, '키워드') 가 실제로 말해지는 시각 K.
# 사용: python3 timing.py A,B,C  → ../raw/stock1128/mg/timing.json
import json, os, re, sys, wave
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here + "/../tools")
import faceless as F
nz = lambda t: re.sub(r"[^가-힣a-z0-9]", "", F.spoken(t).lower())
d = json.load(open(here + "/script.json")); outf = here + "/../raw/stock1128/mg/timing.json"
out = json.load(open(outf)) if os.path.exists(outf) else {}
for k in sys.argv[1].split(","):
    wav = f"{here}/../raw/stock1128/v/{k}_reel.wav"
    subs = [l["sub"] for l in d[k]["lines"]] + [d["cta_reel"]["sub"]]
    words = F.whisper_words(wav, F.LEAD); cues, spans = F.word_cues(subs, words)
    with wave.open(wav) as w: dur = w.getnframes() / w.getframerate()
    S = [round(max(0.0, a - 0.15), 3) for a, b in spans]; S[0] = 0.0
    K, miss = {}, []
    src = open(f"{here}/mg/scenes_{k}.js").read()
    for i, kw in sorted(set((int(a), b) for a, b in re.findall(r"K\((\d+), '([^']+)'", src))):
        a, b = spans[i]; ws = [w for w in words if a - 0.05 <= w[1] < b + 0.05]
        txt, own = "", []
        for j, w in enumerate(ws):
            x = nz(w[0]); txt += x; own += [j] * len(x)
        p = txt.find(nz(kw))
        if p < 0 and len(nz(kw)) > 2: p = txt.find(nz(kw)[:2])
        if p >= 0: K[f"{i}:{kw}"] = round(ws[own[p]][1], 3)
        else: miss.append((i, kw, txt))
    out[k] = {"S": S, "end": round(F.LEAD + dur, 3), "K": K}
    print(k, "S", S, "end", out[k]["end"]); print("  K", K)
    for m in miss: print("  못 찾음:", m)
json.dump(out, open(outf, "w"), ensure_ascii=False, indent=1)
