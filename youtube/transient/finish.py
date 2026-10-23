# 합성 → 싱크 검사 → 효과음. 사용: python3 finish.py long | A B C ...
import json, os, re, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(here, "..", "tools"); R = os.path.join(here, "..", "raw", "transient")


def run(*a):
    print("$", " ".join(a), flush=True); return subprocess.run(a, check=True, cwd=here, capture_output=True, text=True).stdout


def srt(path):
    return [(i + 1, b.split("\n")[2] if len(b.split("\n")) > 2 else "") for i, b in enumerate(open(path, encoding="utf-8").read().strip().split("\n\n"))]


def sfx(mp4, sr, plan):
    out = mp4[:-4] + ".sfx.mp4"
    print(run("python3", f"{T}/sfx.py", mp4, sr, "--plan", plan, "-o", out)[-300:])
    return out


for k in sys.argv[1:]:
    if k == "long":
        print(run("python3", f"{T}/longform.py", "long.json", "-o", f"{R}/long", "--name", "long")[-400:])
        mp4, sr = f"{R}/long/long.mp4", f"{R}/long/long.srt"
        print(run("python3", f"{T}/sync_check.py", mp4, sr).strip().splitlines()[-1])
        L = json.load(open(f"{here}/long.json", encoding="utf-8")); subs = srt(sr)
        firsts = []                                      # 장마다 첫 자막 번호 → trans
        for s in L["sections"][1:]:
            head = re.sub(r"[*\s]", "", s["lines"][0]["sub"])[:6]
            n = next((i for i, t in subs if re.sub(r"\s", "", t).startswith(head[:4])), None)
            if n: firsts.append(n)
        plan = ",".join(["1:intro"] + [f"{n}:trans" for n in firsts])
        sfx(mp4, sr, plan)
        continue
    for ver, cfg in (("reel", "reels.json"), ("short", "shorts.json")):
        d = f"{R}/{ver}s"
        print(run("python3", f"{T}/faceless.py", cfg, "-o", d, "--only", k)[-200:])
        mp4, sr = f"{d}/{k}.mp4", f"{d}/{k}.srt"
        print(run("python3", f"{T}/sync_check.py", mp4, sr).strip().splitlines()[-1])
        subs = srt(sr); n = len(subs)
        cta = next(i for i, t in subs if t.startswith("팔로우") or t.startswith("직접 만든"))
        mid = max(4, (cta - 1) * 2 // 3)
        sfx(mp4, sr, f"1:intro,3:visual,{mid}:emph,{cta}:cta")
