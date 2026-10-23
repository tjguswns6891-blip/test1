# 싱크 검사에서 어긋난 자막: 받아쓰기 단어 시작을 실제로 들린 시각으로 고치고 다시 합성 (최대 3번)
# 사용: python3 fixsync.py long | A_reel | B_short ...
import json, os, re, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(here, "..", "raw", "transient")
sys.path.insert(0, os.path.join(here, "..", "tools")); import faceless
nz = lambda t: re.sub(r"[^가-힣a-z0-9]", "", t.lower())
for job in sys.argv[1:]:
    if job == "long":
        mp4, srt, wj, off, fin = f"{R}/long/long.mp4", f"{R}/long/long.srt", f"{R}/long/long.words.json", 0.0, "long"
    else:
        k, ver = job.split("_")
        mp4, srt, wj, off, fin = f"{R}/{ver}s/{k}.mp4", f"{R}/{ver}s/{k}.srt", f"{R}/v/{k}_{ver}.words.json", faceless.LEAD, k
    for rnd in range(3):
        out = subprocess.run(["python3", f"{here}/../tools/sync_check.py", mp4, srt], capture_output=True, text=True).stdout
        bad = re.findall(r"^\s+\d+\s+([\d.]+)s\s+[-+][\d.]+s\s+'([^']*)' ← 들림 '([^']*)' ([\d.]+)s", out, re.M)
        print(job, out.strip().splitlines()[-1], flush=True)
        if not bad:
            break
        W = json.load(open(wj))
        for t, sub, heard, T in bad:
            t, T = float(t) - off, float(T) - off; key = nz(heard)[:2]
            c = [w for w in W if abs(w[1] - t) < 1.5 and nz(w[0]).startswith(key)]
            if c:
                w = min(c, key=lambda w: abs(w[1] - t)); print(f"  {w[0]} {w[1]:.2f} → {T:.2f}"); w[1] = round(T, 2)
        json.dump(W, open(wj, "w"), ensure_ascii=False)
        subprocess.run(["python3", f"{here}/finish.py", fin], env=dict(os.environ, KEEP_WORDS="1"), cwd=here, capture_output=True, check=True)
