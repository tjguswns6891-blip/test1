# 음성이 나오기 전 미리보기용 타이밍 (음절 수로 짐작). 실제 타이밍은 timing.py 가 음성 받아쓰기로 만든다.
import json, re, sys
d = json.load(open('../script.json')); out = {}
for k in 'ABC':
    t, S = 0.25, []
    for ln in d[k]['lines'] + [d['cta_reel']]:
        S.append(round(t, 2)); t += len(re.sub(r'[^가-힣]', '', ln['tts'])) / 6.4 + .3
    out[k] = {'S': S, 'end': round(t, 2), 'K': {}}
json.dump(out, open(sys.argv[1], 'w'), indent=1); print({k: v['end'] for k, v in out.items()})
