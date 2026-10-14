#!/usr/bin/env python3
"""AI 음성에 '강조'를 넣는 후처리: 표시한 단어만 음을 올리고 크게, 첫 문장(후킹)은 조금 더 크게, 전체는 살짝 빠르게.

조회수 높은 내 릴스(KVL·페이저·테브난·3상, 실제 목소리)를 재 보니 AI 음성과 이렇게 달랐다 (2026-10-14):
  - 말 속도 5.7~7.5음절/초 (AI 4.8~5.5)        → --tempo 1.12
  - 첫 3초 안에 주제어에서 음이 크게 튐 (+8~19반음) → 첫 대사는 5번 만들어 음이 가장 크게 튀는 것을 고르고(tts_voxcpm_para),
                                                   여기서는 첫 대사 +2dB, 그 안의 표시 단어 +5dB
  - 음을 인위로 올리는 건(--semitones) 발음이 뭉개져 기본은 끔
  - 강조는 주제어·핵심 숫자·대비어에만 몰림        → 대본에서 *단어* 로 2~4곳만 표시
  - 소리 크기 폭이 더 넓음 (21~24dB, AI 19~21)      → 표시 단어 --gain dB

사용:
  python3 emphasize.py in.wav out.wav --marks "페이저,KVL,85" [--semitones 2 --gain 3.5 --hook 2 --hook-sec 3 --tempo 1.12]
  표시 단어는 받아쓰기(faster-whisper) 단어와 글자 비교로 찾는다. 숫자는 받아쓰기 표기(예: 59,049 → 59049)로 써도 된다.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from difflib import SequenceMatcher

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
nz = lambda t: re.sub(r"[^가-힣a-z0-9]", "", t.lower())


def words_of(path):
    """faceless.whisper_words 와 같은 캐시(.words.json)를 쓴다."""
    from faceless import whisper_words
    return whisper_words(path)


def find(marks, words):
    """표시 단어마다 (시작, 끝): 앞에서부터 차례로, 가장 비슷한 받아쓰기 단어(두 단어 붙임까지)."""
    hits, pos = [], 0
    for m in marks:
        key, best = nz(m), None
        for i in range(pos, len(words)):
            for j in (i, min(i + 1, len(words) - 1)):
                cand = nz("".join(w[0] for w in words[i:j + 1]))
                sc = SequenceMatcher(None, key, cand[:len(key) + 2]).ratio()
                if best is None or sc > best[0] + 0.05:
                    best = (sc, i, j)
        if best and best[0] >= 0.55:
            _, i, j = best
            hits.append((m, words[i][1], words[j][2])); pos = j + 1
        else:
            print(f"  ⚠ 못 찾음: {m}")
    return hits


def shift(seg, sr, semis):
    """ffmpeg rubberband 로 음만 올린다 (길이·목소리 결 유지)."""
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        sf.write(a, seg, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af",
                        f"rubberband=pitch={2 ** (semis / 12):.5f}:formant=preserved:pitchq=quality", b], check=True)
        out, _ = sf.read(b)
    return out[:len(seg)] if len(out) >= len(seg) else np.pad(out, (0, len(seg) - len(out)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("inp"); p.add_argument("out")
    p.add_argument("--marks", default="", help="강조할 단어, 쉼표로")
    p.add_argument("--semitones", type=float, default=0.0); p.add_argument("--gain", type=float, default=3.5)
    p.add_argument("--hook", type=float, default=2.0, help="첫 문장(--hook-sec 초) 소리 키우기 dB")
    p.add_argument("--hook-sec", type=float, default=3.0, help="첫 대사 길이(초). 이 안의 표시 단어는 더 세게")
    p.add_argument("--hook-semitones", type=float, default=0.0)
    p.add_argument("--pause", type=float, default=0.09, help="본문 표시 단어 앞에 넣는 짧은 쉼(초)"); p.add_argument("--hook-gain", type=float, default=5.0)
    p.add_argument("--tempo", type=float, default=1.12, help="전체 빠르기 (음높이 그대로)")
    a = p.parse_args()

    y, sr = sf.read(a.inp)
    if y.ndim > 1:
        y = y.mean(1)
    marks = [m.strip() for m in a.marks.split(",") if m.strip()]
    hits = find(marks, words_of(a.inp)) if marks else []
    fade = int(sr * 0.03); pad = int(sr * 0.04)
    env = np.ones(len(y))                               # 소리 크기 곡선 (부드럽게 오르내림)
    for m, s, e in hits:
        i0, i1 = max(0, int(s * sr) - pad), min(len(y), int(e * sr) + pad)
        in_hook = s < a.hook_sec                        # 첫 대사의 주제어는 더 크게 튀게
        semis = a.hook_semitones if in_hook else a.semitones
        w = np.ones(i1 - i0); r = np.linspace(0, 1, min(fade, len(w) // 2))
        w[:len(r)] = r; w[len(w) - len(r):] = r[::-1]
        if semis:                                       # 음 올리기는 발음이 뭉개져서 기본은 끔 (2026-10-14 시험: "엑셀 추세선"→"X에 취재선")
            y[i0:i1] = y[i0:i1] * (1 - w) + shift(y[i0:i1], sr, semis) * w
        g = 10 ** ((a.hook_gain if in_hook else a.gain) / 20)
        env[i0:i1] = np.maximum(env[i0:i1], 1 + (g - 1) * w)
        print(f"  강조 {m}: {s:.2f}~{e:.2f}초{' (첫 대사)' if in_hook else ''}")
    if a.hook:
        n = int(a.hook_sec * sr); g = 10 ** (a.hook / 20)
        ramp = np.ones(min(n, len(y))) * g; k = int(sr * 0.3); ramp[-k:] = np.linspace(g, 1, k)
        env[:len(ramp)] *= ramp
    y = y * env
    if a.pause:                                         # 본문 표시 단어 앞 짧은 쉼 (뒤에서부터 넣어야 앞 시각이 안 밀림)
        for m, s0, e0 in sorted([h for h in hits if h[1] >= a.hook_sec], key=lambda h: -h[1]):
            i = max(0, int(s0 * sr) - pad)
            y = np.concatenate([y[:i], np.zeros(int(a.pause * sr)), y[i:]])
    y = y / max(1.0, np.abs(y).max() / 0.97)            # 넘치면 전체를 살짝 낮춤
    with tempfile.TemporaryDirectory() as d:
        t = os.path.join(d, "t.wav"); sf.write(t, y, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", t, "-af", f"atempo={a.tempo}", a.out], check=True)
    print(f"  → {a.out} (강조 {len(hits)}곳 · 빠르기 ×{a.tempo})")


if __name__ == "__main__":
    main()
