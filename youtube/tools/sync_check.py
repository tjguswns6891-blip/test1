#!/usr/bin/env python3
"""완성 영상의 자막 싱크 검사: 영상 소리를 새로 받아쓰기해서, 자막마다 첫 어절이 실제로 말해진 시각과
자막 시작 시각의 차이를 잰다. 받아쓰기 단어 시각은 문장 경계에서 0.5초쯤 흔들리므로,
그 단어 0.6초 안에 무음이 끝나는 곳(silencedetect, 실제 말 시작)이 있으면 그 시각을 쓴다. 차이가 --tol 초를 넘는 자막은 그 근처 2초만 잘라 다시 받아쓰기해서 첫 어절 시각을 한 번 더 잰다
(통째 받아쓰기는 문장 경계에서 단어 시각이 0.5초쯤 틀린다). 그래도 넘으면 '어긋남'으로 센다.
사용: python3 sync_check.py 영상.mp4 자막.srt [--tol 0.25]
"""
import argparse, os, re, subprocess, sys, tempfile
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(__file__))
from sfx import srt_starts

nz = lambda t: re.sub(r"[^가-힣a-z0-9]", "", t.lower())


def srt_texts(path):
    out = {}
    for b in re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip()):
        ls = b.strip().splitlines()
        if len(ls) > 2:
            out[int(ls[0])] = " ".join(ls[2:])
    return out


def slice_ok(m, video, t, first, tol, sil):
    """자막 시작 t 앞뒤(−0.7~+1.3초)만 잘라 다시 받아쓰기해서, 첫 어절이 시작하는 시각이 t 와 tol 안인가.
    짧게 자르면 문장 경계의 단어 시각이 훨씬 정확하다."""
    a = max(0.0, t - 0.7)
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, "s.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-to", f"{t + 1.3:.2f}", "-i", video,
                        "-ac", "1", "-ar", "16000", w], check=True)
        seg, _ = m.transcribe(w, language="ko", beam_size=5, word_timestamps=True)
        ws = [(nz(x.word), a + x.start, a + x.end) for sg in seg for x in sg.words if nz(x.word)]
    # 받아쓰기는 단어 앞의 쉼까지 그 단어에 넣곤 한다: 단어 구간 안에 0.15초 넘는 무음이 있으면 그 무음 끝이 말 시작
    ws = [(x, max([s] + [b for a0, b in sil if s - 0.05 <= a0 and b < e and b - a0 >= 0.15])) for x, s, e in ws]
    hit = [s for x, s in ws if SequenceMatcher(None, first, x[:len(first)]).ratio() >= 0.6]
    return bool(hit) and min(abs(s - t) for s in hit) <= tol


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video"); p.add_argument("srt"); p.add_argument("--tol", type=float, default=0.25)
    a = p.parse_args()
    from faster_whisper import WhisperModel
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-ac", "1", "-ar", "16000", wav], check=True)
        m = WhisperModel("medium", device="cpu", compute_type="int8")
        seg, _ = m.transcribe(wav, language="ko", beam_size=5, word_timestamps=True)
        words = [(nz(w.word), w.start) for s in seg for w in s.words if nz(w.word)]
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.video, "-af", "silencedetect=n=-35dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    onsets = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.video, "-af", "silencedetect=n=-30dB:d=0.05", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    sil = list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", err)), map(float, re.findall(r"silence_end: ([\d.]+)", err))))
    starts, texts = srt_starts(a.srt), srt_texts(a.srt)
    bad, worst, rechecked = 0, 0.0, 0
    for n in sorted(starts):
        t, first = starts[n], nz(texts[n].split()[0])[:4]
        cand = [(SequenceMatcher(None, first, w[:len(first)]).ratio() - abs(s - t) * 0.1, s, w)
                for w, s in words if abs(s - t) < 2.0]
        if not cand or max(cand)[0] < 0.4:
            print(f"  {n:3d} {t:7.2f}s  ?  '{texts[n]}' (받아쓰기에서 못 찾음)")
            continue
        _, s, w = max(cand)
        near = [o for o in onsets if abs(o - s) < 0.6]
        if near:
            s = min(near, key=lambda o: abs(o - s))
        dt = t - s
        if abs(dt) > a.tol and slice_ok(m, a.video, t, first, a.tol, sil):
            rechecked += 1; continue                    # 잘라서 다시 재 보니 맞음 (통째 받아쓰기 시각 탓)
        worst = max(worst, abs(dt)); flag = abs(dt) > a.tol; bad += flag
        if flag:
            print(f"  {n:3d} {t:7.2f}s  {dt:+.2f}s  '{texts[n]}' ← 들림 '{w}' {s:.2f}s")
    print(f"{os.path.basename(a.video)}: 자막 {len(starts)} · 어긋남 {bad} (±{a.tol}s 넘음) · 최대 차이 {worst:.2f}s · 다시 재서 맞은 것 {rechecked}")


if __name__ == "__main__":
    main()
