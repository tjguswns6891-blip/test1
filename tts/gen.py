"""내 목소리(6편 녹음 10초)로 7편 대사를 합성: Chatterbox multilingual(ko), 줄마다 TAKES개 → faster-whisper로 받아쓰기 비교해 제일 정확한 것 고름."""
import json, os, re, sys, time, torch, torchaudio as ta
_l = torch.load
torch.load = lambda *a, **k: _l(*a, **{**k, 'map_location': k.get('map_location', 'cpu')})
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel
L = json.load(open('tts/lines.json', encoding='utf-8'))
only = [x for x in os.environ.get('ONLY', '').split(',') if x]
TAKES = int(os.environ.get("TAKES", "8" if only else "4"))
REF = os.environ.get('REF', 'tts/ref.wav')
EXG = float(os.environ.get('EXG', '0.5')); CFG = float(os.environ.get('CFG', '0.5'))
os.makedirs('out', exist_ok=True)
m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
w = WhisperModel('small', device='cpu', compute_type='int8')
LET = {'A':'에이','B':'비','C':'씨','D':'디','P':'피','S':'에스','W':'더블유','X':'엑스','6':'육'}
def norm(s):
    s = ''.join(LET.get(ch, ch) for ch in s.upper())
    return re.sub(r'[^가-힣]', '', s)
def cer(a, b):
    a, b = norm(a), norm(b); d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[len(b)] / max(1, len(a))
rep = {}
for k, t in L.items():
    if only and k not in only: continue
    say = t['say'] if isinstance(t, dict) else t   # 발음대로 적은 글(싸이트, 께임)로 합성
    t = t['text'] if isinstance(t, dict) else t     # 받아쓰기 비교는 원래 표기
    best = None
    for n in range(TAKES):
        torch.manual_seed(1000 * int(k) + n); t0 = time.time()
        wav = m.generate(say, language_id='ko', audio_prompt_path=REF, exaggeration=EXG, cfg_weight=CFG)
        p = f'out/l{int(k):02d}_t{n}.wav'; ta.save(p, wav, m.sr)
        hyp = ''.join(s.text for s in w.transcribe(p, language='ko')[0])
        c = cer(t, hyp); dur = wav.shape[-1] / m.sr
        print(f'line {k} take {n}: cer {c:.3f} dur {dur:.1f}s gen {time.time()-t0:.0f}s | {hyp}', flush=True)
        rep.setdefault(k, []).append({'take': n, 'cer': c, 'dur': dur, 'hyp': hyp})
        syl = len(norm(t)); rate = syl / max(0.5, dur)
        score = c + max(0.0, abs(rate - 5.6) - 0.8) * 0.05   # 받아쓰기 정확도 + 말 빠르기(초당 5.6음절 근처)
        rep[k][-1].update(rate=rate, score=score)
        if best is None or score < best[0]: best = (score, p)
    os.system(f'cp {best[1]} out/l{int(k):02d}.wav')
json.dump(rep, open('out/report.json', 'w'), ensure_ascii=False, indent=1)
