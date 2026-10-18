#!/usr/bin/env python3
"""만든 음성 조각을 받아쓰기(faster-whisper medium)해서 대본과 비교하고, 발음이 틀린 조각을 골라낸다.

대본의 tts(한글 숫자)·sub(아라비아 숫자) 중 더 잘 맞는 쪽으로 일치도(0~1)를 매기고,
숫자·*강조* 단어·핵심 용어(--terms)가 받아쓰기에 들어 있는지 본다. 빠진 것이 있거나 일치도가 --min 미만이면 '다시'.
받아쓰기는 옆에 .words.json 으로 남아 faceless.py 가 다시 쓴다.
사용: python3 tts_check.py script.json 음성폴더 --ver long [--only A,B] [--terms 라플라스,극점] [--min 0.85]
출력: 조각마다 한 줄 + 마지막 줄에 JSON {"redo": [키, ...]}
"""
import argparse, json, os, re, sys
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(__file__))
from faceless import whisper_words

def nz(t):
    """글자만 남기고, 소리가 같은 ㅐ/ㅔ·ㅒ/ㅖ·ㅚ/ㅙ/ㅞ 는 하나로 (받아쓰기가 곱셈↔곱샘, 감쇠↔감세 처럼 헷갈린다)."""
    t = re.sub(r"[^가-힣a-z0-9]", "", t.lower())
    out = []
    for ch in t:
        c = ord(ch) - 0xAC00
        if 0 <= c < 11172:
            v = c // 28 % 21
            v = {1: 5, 3: 7, 10: 5, 11: 5, 15: 5}.get(v, v)   # ㅐ·ㅙ·ㅚ·ㅞ→ㅔ, ㅒ→ㅖ (감쇠↔감세)
            ch = chr(0xAC00 + c // 588 * 588 + v * 28 + c % 28)
        out.append(ch)
    return "".join(out)


def found(term, txt):
    """term 이 받아쓰기 안에 (한 글자 정도 틀려도) 들어 있나."""
    t = nz(term)
    if not t or t in txt:
        return True
    n = len(t)
    return any(SequenceMatcher(None, t, txt[i:i + n]).ratio() >= (0.8 if n >= 4 else 1.0) for i in range(len(txt) - n + 1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("script"); p.add_argument("voice")
    p.add_argument("--ver", default="long"); p.add_argument("--only", default="")
    p.add_argument("--terms", default="라플라스,극점,커패시터,미분방정식,복소,안정,주파수,초기 조건")
    p.add_argument("--min", type=float, default=0.85)
    a = p.parse_args()
    d = json.load(open(a.script, encoding="utf-8"))
    only = set(filter(None, a.only.split(",")))
    terms = [t for t in a.terms.split(",") if t]
    redo = []
    for k, v in d.items():
        if k.startswith("_") or k.startswith("cta") or (only and k not in only):
            continue
        for ver in a.ver.split(","):
            f = os.path.join(a.voice, f"{k}_{ver}.wav")
            if not os.path.exists(f):
                continue
            lines = v["lines"] + ([d["cta_" + ver]] if "cta_" + ver in d and ver != "long" else [])
            tts = " ".join(ln["tts"] for ln in lines).replace("*", "")
            sub = " ".join(ln.get("sub", ln["tts"]) for ln in lines).replace("*", "")
            heard = "".join(w for w, _, _ in whisper_words(f))
            txt = nz(heard)
            sim = max(SequenceMatcher(None, nz(tts), txt, autojunk=False).ratio(),
                      SequenceMatcher(None, nz(sub), txt, autojunk=False).ratio())
            marks = [m for ln in lines for m in re.findall(r"\*([^*]+)\*", ln.get("sub", ""))]
            want = [t for t in terms if nz(t) in nz(tts)] + marks
            miss = [t for t in dict.fromkeys(want) if not found(t, txt)]
            # 숫자: sub 의 아라비아 숫자는 받아쓰기에 숫자로든 tts 의 한글로든 나와야 한다
            for num in re.findall(r"\d+(?:\.\d+)?", sub):
                if nz(num) not in txt:
                    miss.append(num + "?")
            bad = sim < a.min or any(not m.endswith("?") for m in miss)
            print(f"{'다시' if bad else '  OK'} {k}_{ver}  일치 {sim:.3f}  빠짐 {miss or '-'}\n      들림: {heard}", flush=True)
            if bad:
                redo.append(f"{k}_{ver}")
    print(json.dumps({"redo": redo}, ensure_ascii=False))


if __name__ == "__main__":
    main()
