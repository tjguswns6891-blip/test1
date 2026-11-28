# 쇼츠 음성 = 릴스 음성의 본문(끝 대사 앞까지) + 쇼츠 끝 대사(raw/stock1128/v/X_short.wav 의 뒷부분).
# 본문을 두 번 만들지 않아 음성 생성 시간이 절반이고, 쇼츠·릴스의 그래픽 타이밍이 같아진다. 사용: python3 mk_short.py A,B,C
import json, os, sys, numpy as np, soundfile as sf
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here + "/../tools")
import faceless as F
V = here + "/../raw/stock1128/v/"
def first(words, key, after=0.0):
    for w, a, b in words:
        if a >= after and key in w: return a
    raise SystemExit(f"'{key}' 를 받아쓰기에서 못 찾음")
xw = F.whisper_words(V + "X_short.wav"); x, sr = sf.read(V + "X_short.wav")
xs = first(xw, "제가") - 0.10; tail = x[int(xs * sr):].copy()
n = int(sr * 0.015); tail[:n] *= np.linspace(0, 1, n)
for k in sys.argv[1].split(","):
    y, sr2 = sf.read(V + f"{k}_reel.wav"); assert sr2 == sr
    cut = first(F.whisper_words(V + f"{k}_reel.wav"), "팔로우", after=len(y) / sr - 9) - 0.10
    body = y[:int(cut * sr)].copy(); body[-n:] *= np.linspace(1, 0, n)
    sf.write(V + f"{k}_short.wav", np.concatenate([body, tail]), sr)
    print(k, f"본문 {cut:.2f}s + 끝 대사 {len(tail) / sr:.2f}s")
