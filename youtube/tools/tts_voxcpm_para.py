"""영상 하나의 대본을 '한 덩어리'로 VoxCPM2 음성을 만든다 (문장 사이 억양·쉼이 자연스럽게 이어지게).

본인 목소리 '궁극 복제': 참고 음성 + 그 음성의 정확한 대본(prompt)을 같이 넣어 말투·리듬까지 따라 한다.
사용: ~/.venvs/voxcpm/bin/python tts_voxcpm_para.py script.json prompt.wav "prompt 대본" 출력폴더 [--only N] [--ver reel,short] [--steps 20]
출력: <출력폴더>/<키>_<reel|short>.wav  (이미 있으면 건너뜀)

강조: 대본 sub 에 *단어* 로 표시한 곳(주제어·핵심 숫자·대비어 2~4곳)은 생성 뒤 emphasize.py 로
음을 올리고 크게 한다. 첫 문장도 조금 크게, 전체는 실제 내 말 빠르기에 맞춰 살짝 빠르게 (--no-emph 로 끔).
생성 원본은 <키>_<판>.raw.wav 로 남긴다.
"""
import argparse, json, os, re, subprocess
import numpy as np, soundfile as sf


def main():
    p = argparse.ArgumentParser()
    p.add_argument("script"); p.add_argument("prompt_wav"); p.add_argument("prompt_text"); p.add_argument("out")
    p.add_argument("--only", default=""); p.add_argument("--ver", default="reel,short")
    p.add_argument("--steps", type=int, default=20); p.add_argument("--cfg", type=float, default=2.0)
    p.add_argument("--seed", type=int, default=7); p.add_argument("--suffix", default="")
    p.add_argument("--no-emph", action="store_true", help="강조 후처리 안 함")
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
            torch.manual_seed(a.seed)
            text = body + " " + d["cta_" + ver]["tts"]
            wav = model.generate(text=text, prompt_wav_path=a.prompt_wav, prompt_text=a.prompt_text,
                                 reference_wav_path=a.prompt_wav, cfg_value=a.cfg, inference_timesteps=a.steps)
            raw = path[:-4] + ".raw.wav"
            sf.write(raw if not a.no_emph else path, np.asarray(wav), sr)
            print(k, ver, f"{len(wav) / sr:.1f}s", flush=True)
            if not a.no_emph:                         # 받아쓰기가 필요해서 시스템 파이썬으로
                subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "emphasize.py"), raw, path,
                                "--marks", ",".join(marks)], check=True)


if __name__ == "__main__":
    main()
