"""대본 JSON 의 문장마다 VoxCPM2 로 본인 목소리(참고 음성 복제) 음성을 만든다.

사용: ~/.venvs/voxcpm/bin/python tts_voxcpm.py script.json ref.wav 출력폴더 [--only N,S] [--seed 7]
출력: <출력폴더>/<키>_<번호>.wav (cta_reel.wav, cta_short.wav 도). 이미 있으면 건너뛴다(다시 뽑을 땐 지우고).
"""
import argparse, json, os, sys
import numpy as np, soundfile as sf


def main():
    p = argparse.ArgumentParser()
    p.add_argument("script"); p.add_argument("ref"); p.add_argument("out")
    p.add_argument("--only", default=""); p.add_argument("--seed", type=int, default=7)
    p.add_argument("--steps", type=int, default=12)
    a = p.parse_args()
    from voxcpm import VoxCPM
    import torch
    torch.manual_seed(a.seed)
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False, device="cpu")
    sr = model.tts_model.sample_rate
    d = json.load(open(a.script, encoding="utf-8"))
    jobs = [("cta_reel", d["cta_reel"]["tts"]), ("cta_short", d["cta_short"]["tts"])]
    only = set(filter(None, a.only.split(",")))
    for k, v in d.items():
        if k.startswith("_") or k.startswith("cta") or (only and k not in only):
            continue
        jobs += [(f"{k}_{i:02d}", ln["tts"]) for i, ln in enumerate(v["lines"])]
    os.makedirs(a.out, exist_ok=True)
    for name, text in jobs:
        path = os.path.join(a.out, name + ".wav")
        if os.path.exists(path):
            continue
        wav = model.generate(text=text, reference_wav_path=a.ref, cfg_value=2.0, inference_timesteps=a.steps)
        sf.write(path, np.asarray(wav), sr)
        print(name, f"{len(wav) / sr:.2f}s", flush=True)


if __name__ == "__main__":
    main()
