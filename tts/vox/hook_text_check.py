#!/usr/bin/env python3
"""첫 대사 후보들을 받아쓰기해서 대본과 얼마나 같은지(0~1) 출력한다. (tts_voxcpm_para.py 가 부름, 시스템 파이썬)
사용: python3 hook_text_check.py "대본" a.wav b.wav ...  →  마지막 줄에 JSON {파일: 일치도}
대본에 "||" 로 여러 표기를 주면(tts 한글 숫자 || 자막 아라비아 숫자) 가장 잘 맞는 쪽 점수를 쓴다."""
import json, re, sys
from difflib import SequenceMatcher
from faster_whisper import WhisperModel

nz = lambda t: re.sub(r"[^가-힣a-z0-9]", "", t.lower())
ref, files = sys.argv[1], sys.argv[2:]
m = WhisperModel("medium", device="cpu", compute_type="int8")
out = {}
for f in files:
    seg, _ = m.transcribe(f, language="ko", beam_size=5)
    txt = "".join(s.text for s in seg)
    out[f] = round(max(SequenceMatcher(None, nz(r), nz(txt)).ratio() for r in ref.split("||")), 3)
print(json.dumps(out, ensure_ascii=False))
