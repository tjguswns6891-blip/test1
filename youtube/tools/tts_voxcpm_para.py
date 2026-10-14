"""영상 하나의 대본을 '한 덩어리'로 VoxCPM2 음성을 만든다 (문장 사이 억양·쉼이 자연스럽게 이어지게).

본인 목소리 '궁극 복제': 참고 음성 + 그 음성의 정확한 대본(prompt)을 같이 넣어 말투·리듬까지 따라 한다.
사용: ~/.venvs/voxcpm/bin/python tts_voxcpm_para.py script.json prompt.wav "prompt 대본" 출력폴더 [--only N] [--ver reel,short] [--steps 20]
출력: <출력폴더>/<키>_<reel|short>.wav  (이미 있으면 건너뜀)

강조: 대본 sub 에 *단어* 로 표시한 곳(주제어·핵심 숫자·대비어 2~4곳)은 생성 뒤 emphasize.py 로
음을 올리고 크게 한다. 첫 문장도 조금 크게, 전체는 실제 내 말 빠르기에 맞춰 살짝 빠르게 (--no-emph 로 끔).
생성 원본은 <키>_<판>.raw.wav 로 남긴다.

첫 대사(후킹)는 따로 --hook-takes 번 만들어 가장 힘 있는 것을 고른다: 받아쓰기 일치도 0.85 미만은 버리고,
음높이 폭(반음) · 가장 큰 음 튐 · 말 빠르기로 점수를 매긴다. 고른 첫 대사 + 0.3초 쉼 + 나머지 문단을 잇는다.
후보와 점수는 <키>_<판>.hook/ 에 남긴다.
"""
import argparse, json, os, re, subprocess
import numpy as np, soundfile as sf


def trim(y, sr, thr_db=-40):
    """앞뒤 무음 자르기 (앞 0.05초, 뒤 0.08초 여유)."""
    e = np.abs(y); th = e.max() * 10 ** (thr_db / 20); idx = np.where(e > th)[0]
    if not len(idx):
        return y
    return y[max(0, idx[0] - int(sr * 0.05)): idx[-1] + int(sr * 0.08)]


def pick_hook(hook_t, hd, make, sr, n, alt=""):
    """첫 대사 n번 만들기 → 받아쓰기 일치도 0.85 미만 탈락 → 음높이 폭 + 0.5×최고 튐 − 2×|빠르기−6.5| 최고를 고른다."""
    takes = []
    for i in range(n):
        f = os.path.join(hd, f"take{i}.wav")
        if not os.path.exists(f):                       # 이미 만든 후보는 다시 쓰기 (점수만 다시 매길 때)
            sf.write(f, make(hook_t, i), sr)
        takes.append(f)
    ref = hook_t + ("||" + alt if alt else "")         # 숫자 표기가 달라도 맞게: tts(한글 숫자) || 자막(아라비아 숫자)
    sim = json.loads(subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "hook_text_check.py"), ref] + takes,
                                    capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1])
    nsyl = len(re.sub(r"[^가-힣]", "", hook_t)); rows = []
    for f in takes:
        y, _ = sf.read(f); rng, peak, dur = hook_prosody(y, sr); rate = nsyl / dur
        score = rng + 0.5 * peak - 2.0 * abs(rate - 6.5) if sim[f] >= 0.85 else -99
        rows.append({"take": os.path.basename(f), "text_match": sim[f], "pitch_range": round(rng, 1),
                     "peak": round(peak, 1), "syl_per_sec": round(rate, 2), "score": round(score, 2)})
    best = max(rows, key=lambda r: r["score"])
    json.dump({"text": hook_t, "takes": rows, "best": best["take"]}, open(os.path.join(hd, "scores.json"), "w"),
              ensure_ascii=False, indent=1)
    print("  첫 대사 후보:", " | ".join(f"{r['take']} 일치{r['text_match']} 폭{r['pitch_range']} 튐{r['peak']} "
                                    f"{r['syl_per_sec']}음절/초 → {r['score']}" for r in rows), flush=True)
    return best["take"]


def hook_prosody(y, sr):
    """첫 대사 힘: (음높이 폭 반음, 가장 큰 음 튐 반음, 길이 초)."""
    import librosa
    y16 = librosa.resample(y.astype(np.float32), orig_sr=sr, target_sr=16000)
    f0, _, _ = librosa.pyin(y16, fmin=70, fmax=400, sr=16000, frame_length=1024, hop_length=160)
    v = f0[~np.isnan(f0)]
    if len(v) < 10:
        return 0.0, 0.0, len(y) / sr
    st = 12 * np.log2(v / np.median(v))
    return float(np.percentile(st, 95) - np.percentile(st, 5)), float(st.max()), len(y) / sr


def main():
    p = argparse.ArgumentParser()
    p.add_argument("script"); p.add_argument("prompt_wav"); p.add_argument("prompt_text"); p.add_argument("out")
    p.add_argument("--only", default=""); p.add_argument("--ver", default="reel,short")
    p.add_argument("--steps", type=int, default=20); p.add_argument("--cfg", type=float, default=2.0)
    p.add_argument("--seed", type=int, default=7); p.add_argument("--suffix", default="")
    p.add_argument("--no-emph", action="store_true", help="강조 후처리 안 함")
    p.add_argument("--hook-takes", type=int, default=5, help="첫 대사 후보 수 (1이면 문단 통째로 한 번)")
    p.add_argument("--tempo", default="1.12", help="강조 후처리 빠르기 (롱폼은 1.0)")
    a = p.parse_args()
    import torch
    from voxcpm import VoxCPM
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False, device="cpu")
    sr = model.tts_model.sample_rate
    d = json.load(open(a.script, encoding="utf-8"))
    only = set(filter(None, a.only.split(",")))
    os.makedirs(a.out, exist_ok=True)
    for k, v in d.items():
        if k.startswith("_") or k.startswith("cta") or (only and k not in only):
            continue
        body = " ".join(ln["tts"] for ln in v["lines"]).replace("*", "")
        marks = [m for ln in v["lines"] for m in re.findall(r"\*([^*]+)\*", ln["sub"])]
        for ver in a.ver.split(","):
            path = os.path.join(a.out, f"{k}_{ver}{a.suffix}.wav")
            if os.path.exists(path):
                continue
            gen = lambda t, seed: (torch.manual_seed(seed), np.asarray(model.generate(
                text=t, prompt_wav_path=a.prompt_wav, prompt_text=a.prompt_text, reference_wav_path=a.prompt_wav,
                cfg_value=a.cfg, inference_timesteps=a.steps)))[1]
            hook_len = 0.0
            if a.hook_takes > 1 and len(v["lines"]) > 1:
                hook_t = v["lines"][0]["tts"].replace("*", "")
                rest = " ".join(ln["tts"] for ln in v["lines"][1:]).replace("*", "") + " " + d["cta_" + ver]["tts"]
                hd = os.path.join(a.out, f"{k}{a.suffix}.hook"); os.makedirs(hd, exist_ok=True)   # 릴스·쇼츠가 같은 첫 대사를 같이 쓴다
                sc = os.path.join(hd, "scores.json")
                if not os.path.exists(sc):
                    best = pick_hook(hook_t, hd, lambda t, i: trim(gen(t, a.seed + 100 + i), sr), sr, a.hook_takes,
                                     alt=v["lines"][0]["sub"].replace("*", ""))
                else:
                    best = json.load(open(sc))["best"]
                hy, _ = sf.read(os.path.join(hd, best))
                by = trim(gen(rest, a.seed), sr)
                hook_len = 0.1 + len(hy) / sr
                wav = np.concatenate([np.zeros(int(sr * 0.1)), hy, np.zeros(int(sr * 0.3)), by])
            else:
                wav = gen(body + " " + d["cta_" + ver]["tts"], a.seed)
            raw = path[:-4] + ".raw.wav"
            sf.write(raw if not a.no_emph else path, np.asarray(wav), sr)
            print(k, ver, f"{len(wav) / sr:.1f}s", flush=True)
            if not a.no_emph:                         # 받아쓰기가 필요해서 시스템 파이썬으로
                subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "emphasize.py"), raw, path,
                                "--marks", ",".join(marks), "--tempo", a.tempo] + (["--hook-sec", f"{hook_len:.2f}"] if hook_len else []), check=True)


if __name__ == "__main__":
    main()
