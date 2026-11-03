#!/usr/bin/env python3
"""음성 조각에서 '말이 끊기는 곳'을 찾는다: 문장 중간의 긴 무음, 뚝 잘린 끝.

- 무음: ffmpeg silencedetect (-40dB) 로 --max 초(기본 0.7)보다 긴 쉼을 모두 적는다 (첫·끝 무음 제외).
- 끝 잘림: 마지막 0.05초 소리가 아직 크면(-30dB 이상) 잘린 것으로 본다.
사용: python3 gap_check.py 음성.wav ... [--max 0.7]
출력: 파일마다 한 줄, 마지막 줄 JSON {"bad": [파일, ...]}
"""
import argparse, json, re, subprocess

import numpy as np
import soundfile as sf


def silences(path, thr=-40, min_d=0.25):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={thr}dB:d={min_d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(st, en + [None] * (len(st) - len(en))))


def main():
    p = argparse.ArgumentParser(); p.add_argument("wavs", nargs="+"); p.add_argument("--max", type=float, default=0.7)
    a = p.parse_args(); bad = []
    for f in a.wavs:
        y, sr = sf.read(f)
        if y.ndim > 1:
            y = y.mean(1)
        dur = len(y) / sr
        gaps = [(s, e) for s, e in silences(f) if s > 0.05 and e is not None and e < dur - 0.05 and e - s > a.max]
        tail = 20 * np.log10(np.sqrt(np.mean(y[-int(sr * .05):] ** 2)) + 1e-9) - 20 * np.log10(np.abs(y).max() + 1e-9)
        cut = tail > -30
        msg = " ".join(f"{s:.1f}~{e:.1f}s({e - s:.1f})" for s, e in gaps)
        print(f"{f}: {dur:.1f}s  긴 쉼 {len(gaps)}개 {msg}  끝 {tail:.0f}dB{' 잘림?' if cut else ''}")
        if gaps or cut:
            bad.append(f)
    print(json.dumps({"bad": bad}, ensure_ascii=False))


if __name__ == "__main__":
    main()
