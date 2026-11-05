"""내 목소리(6편 녹음 10초)로 7편 대사를 합성: Chatterbox multilingual(ko), 줄마다 TAKES개 → faster-whisper로 받아쓰기 비교해 제일 정확한 것 고름."""
import json, os, re, sys, time, torch, torchaudio as ta
_l = torch.load
torch.load = lambda *a, **k: _l(*a, **{**k, 'map_location': k.get('map_location', 'cpu')})
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel
L = json.load(open('tts/lines.json', encoding='utf-8'))
only = [x for x in os.environ.get('ONLY', '').split(',') if x]
TAKES = int(os.environ.get('TAKES', '3'))
REF = os.environ.get('REF', 'tts/ref.wav')
EXG = float(os.environ.get('EXG', '0.5')); CFG = float(os.environ.get('CFG', '0.5'))
os.makedirs('out', exist_ok=True)
m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
w = WhisperModel('small', device='cpu', compute_type='int8')
norm = lambda s: re.sub(r'[^가-힣]', '', s)
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
    best = None
    for n in range(TAKES):
        torch.manual_seed(1000 * int(k) + n); t0 = time.time()
        wav = m.generate(t, language_id='ko', audio_prompt_path=REF, exaggeration=EXG, cfg_weight=CFG)
        p = f'out/l{int(k):02d}_t{n}.wav'; ta.save(p, wav, m.sr)
        hyp = ''.join(s.text for s in w.transcribe(p, language='ko')[0])
        c = cer(t, hyp); dur = wav.shape[-1] / m.sr
        print(f'line {k} take {n}: cer {c:.3f} dur {dur:.1f}s gen {time.time()-t0:.0f}s | {hyp}', flush=True)
        rep.setdefault(k, []).append({'take': n, 'cer': c, 'dur': dur, 'hyp': hyp})
        if best is None or c < best[0]: best = (c, p)
    os.system(f'cp {best[1]} out/l{int(k):02d}.wav')
json.dump(rep, open('out/report.json', 'w'), ensure_ascii=False, indent=1)
