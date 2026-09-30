#!/usr/bin/env python3
"""NG 컷 찾기: 같은 대본 줄을 여러 번 읽었으면 마지막 것만 남기고, 군말·말하다 끊긴 부분을 잘라낸다.

받아쓰기(words.json)의 말 덩어리를 하나씩 대본 위치에 맞춰 보고,
  · 뒤에서 대본의 같은 곳을 다시 읽으면 → 앞에서 읽은 부분(끊긴 말 포함)을 자른다 (마지막 테이크만 남김)
  · 대본에 없는 "음·어·아" 같은 군말 → 자른다
  · 대본에 없는 "다시·잠깐·아니·틀렸다" 같은 NG 말 (짧은 덩어리) → 자른다
  · 대본에 없지만 바로 뒤 대본 글자와 거의 같은 말(말하다 끊고 다시 시작) → 자른다
  · 그 밖에 대본에 없는 말(애드리브)은 남긴다
대본 속 "다시"(예: 6,900선을 다시 넘었거든요)는 대본과 맞춰지므로 지우지 않는다.

결과
  <이름>.retakes.json      autocut.py --cut-file 로 넘길 자를 구간
  <이름>.retakes.txt       자른 곳 목록 (사람이 확인용)
  <이름>.clean.words.json  자른 말을 뺀 받아쓰기 → align_script.py 에 이걸 넣는다

사용 예:
  python3 retakes.py raw.words.json --script ../0930/index.html
  python3 autocut.py src.mov -o cut.mp4 --cut-file raw.retakes.json --transcript raw.words.json
  python3 align_script.py raw.clean.words.json --script ../0930/index.html

받아쓰기는 transcribe.py --verbatim 으로 만들어야 되풀이한 말과 군말이 빠지지 않고 적힌다.
"""
import argparse
import difflib
import json
import re
import sys

from align_script import DEFAULT_SCRIPT, load_script, norm_chars

SOUNDS = {"음", "어", "아", "으", "엄", "흠", "음음", "어어", "아아"}   # 어디서든 군말
FILLERS = SOUNDS | {"그", "저"}   # "그·저"는 혼자 떨어져 있을 때만 군말 (애드리브 속 "그 종목"은 남김)
NG_WORDS = re.compile(r"다시|잠깐|잠시만|아니|틀렸|틀려|죄송|엔지|NG|컷|한번더|한 번 더|처음부터")
BACK, AHEAD = 400, 900      # 대본 위치를 찾을 범위(글자): 지금 위치에서 뒤로·앞으로


def token(w):
    return "".join(norm_chars(w["word"]))


def utterances(words, gap):
    """단어 사이가 gap초 넘게 벌어진 곳에서 말 덩어리를 나눈다."""
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and w["start"] - words[cur[-1]]["end"] > gap:
            out.append(cur)
            cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return out


def locate(words, idx, s_chars, cursor):
    """말 덩어리를 대본 cursor 근처에 맞춰 단어별 대본 위치 {단어번호: (처음, 끝)} 과 일치율을 돌려준다."""
    u_chars, owner = [], []
    for i in idx:
        for c in token(words[i]):
            u_chars.append(c)
            owner.append(i)
    if len(u_chars) < 2:
        return {}, 0.0
    lo, hi = max(0, cursor - BACK), min(len(s_chars), cursor + AHEAD)
    blocks = difflib.SequenceMatcher(None, s_chars[lo:hi], u_chars, autojunk=False).get_matching_blocks()
    blocks = [b for b in blocks if b.size]
    if not blocks:
        return {}, 0.0
    anchor = max(blocks, key=lambda b: b.size)
    # 가장 긴 일치를 기준으로 대본 범위를 좁혀 다시 맞춘다 (멀리 떨어진 우연한 일치 제거)
    start = lo + anchor.a - anchor.b
    lo2, hi2 = max(0, start - 10), min(len(s_chars), start + len(u_chars) + 20)
    sm = difflib.SequenceMatcher(None, s_chars[lo2:hi2], u_chars, autojunk=False)
    hit = {}
    for b in sm.get_matching_blocks():
        for k in range(b.size):
            hit[b.b + k] = lo2 + b.a + k
    per_word = {}
    for k, i in enumerate(owner):
        per_word.setdefault(i, []).append(hit.get(k))
    pos = {}
    for i, ps in per_word.items():
        got = [p for p in ps if p is not None]
        if len(got) * 2 > len(ps):
            # 한 단어의 글자가 대본 여기저기에 흩어져 맞으면 끝 위치를 단어 길이로 자른다
            pos[i] = (min(got), min(max(got), min(got) + len(ps) - 1))
    return pos, len(hit) / len(u_chars)


def looks_like_false_start(chars, s_chars, q):
    """대본에 없는 말이 바로 뒤에 읽을 대본 글자(q부터)와 거의 같은지 (말하다 끊고 다시 시작).
    대본 글자를 건너뛰고 다른 말을 한 경우(첫째 → 첫 번째)는 여기서 걸러진다: 호출 쪽에서 건너뛴 글자가 없을 때만 부른다."""
    if q is None or len(chars) < 2:
        return False
    seg = s_chars[q: q + len(chars) + 8]
    sm = difflib.SequenceMatcher(None, seg, chars, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / len(chars) >= 0.7


def dubious(w):
    """받아쓰기가 지어냈을 수 있는 단어: 확신도가 낮거나 길이가 0에 가깝다."""
    return w.get("prob", 1.0) < 0.3 or not 0.05 <= w["end"] - w["start"] <= 2.5


def trusted_take(words, p):
    """다시 읽은 테이크로 믿을 만한지: 대본 글자를 이어서 제대로 읽은 단어가 3개 이상."""
    idx = sorted(i for i in p if not dubious(words[i]))
    chain = sum(1 for a, b in zip(idx, idx[1:]) if b == a + 1 and 0 <= p[b][0] - p[a][1] <= 2)
    return len(idx) >= 3 and chain >= 2 and chain >= 0.6 * (len(idx) - 1)


def repeats_before(chars, s_chars, prv):
    """대본에 없는 말이 방금(prv까지) 읽은 대본 글자를 되풀이한 것이면 되풀이가 시작된 대본 위치를 돌려준다."""
    if len(chars) < 5:
        return None
    lo = max(0, prv + 1 - len(chars) - 8)
    sm = difflib.SequenceMatcher(None, s_chars[lo:prv + 1], chars, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size]
    if not blocks or sum(b.size for b in blocks) / len(chars) < 0.8:
        return None
    return lo + blocks[0].a


def find_cuts(words, s_chars, gap=0.45, window=90.0, min_ratio=0.5):
    pos, trusted, cursor = {}, set(), 0
    for idx in utterances(words, gap):
        p, ratio = locate(words, idx, s_chars, cursor)
        if ratio >= min_ratio and sum(len(token(words[i])) for i in p) >= 4:
            pos.update(p)
            cursor = max(e for _, e in p.values())
            if ratio >= 0.6 and trusted_take(words, p):
                trusted.update(p)

    def solid(k):   # 글자가 다 맞고, 다음 단어로 대본을 이어 읽은 단어만 "다시 읽기"의 근거로 쓴다
        n = len(token(words[k]))
        nx = k + 1
        return (pos[k][1] - pos[k][0] + 1 >= n - 1 and nx in pos and 0 <= pos[nx][0] - pos[k][1] <= 2)

    reason = {}
    # 1) 마지막 테이크만: 뒤에서 대본의 같은 곳(또는 더 앞)을 다시 읽으면 앞에서 읽은 말을 자른다
    matched = sorted(pos)
    for n, k in enumerate(matched):
        if k not in trusted or dubious(words[k]) or not solid(k):
            continue
        pk = pos[k][0]
        for m in reversed(matched[:n]):
            if words[k]["start"] - words[m]["start"] > window:
                break
            if m not in reason and pos[m][1] >= pk:
                reason[m] = "다시 읽기 전 테이크"

    # 2) 대본에 없는 말 덩어리
    i = 0
    while i < len(words):
        if i in pos:
            i += 1
            continue
        j = i
        while j < len(words) and j not in pos:
            j += 1
        run = list(range(i, j))
        toks = [token(words[r]) for r in run]
        text = " ".join(words[r]["word"].strip() for r in run)
        prev_cut = i > 0 and (i - 1) in reason
        nxt = next((pos[r][0] for r in range(j, len(words)) if r in trusted and r not in reason), None)
        span_sec = words[j - 1]["end"] - words[i]["start"]
        prv = next((pos[r][1] for r in range(i - 1, -1, -1) if r in pos and r not in reason), None)
        skipped = nxt is not None and prv is not None and nxt - prv > 2   # 대본 글자를 건너뛰고 다른 말로 바꿔 읽음
        chars = [c for t in toks for c in t]
        shaky = any(dubious(words[r]) for r in run) and not all(t in FILLERS for t in toks)
        if all(t in FILLERS for t in toks):
            why = "군말"
        elif len(run) <= 6 and NG_WORDS.search(text):
            why = "NG 말"
        elif shaky:
            why = None      # 받아쓰기가 지어낸 말일 수 있어 시간을 믿기 어렵다 → 건드리지 않는다
        elif prev_cut:
            why = "끊긴 테이크의 나머지"
        elif span_sec <= 8 and not skipped and prv is not None and (back := repeats_before(chars, s_chars, prv)) is not None:
            # 방금 읽은 대본을 쉬지 않고 다시 읽음 → 앞의 것을 자르고 이 말(마지막 테이크)을 남긴다
            why = None
            for r in range(i - 1, -1, -1):
                if words[i]["start"] - words[r]["start"] > window or (r in pos and pos[r][1] < back):
                    break
                reason.setdefault(r, "다시 읽기 전 테이크")
        elif span_sec <= 4 and not skipped and looks_like_false_start(chars, s_chars, nxt):
            why = "말하다 끊김"
        else:
            # 애드리브 속 군말만 골라 자른다
            why = None
            for r, t in zip(run, toks):
                if t in SOUNDS:
                    reason[r] = "군말"
        if why:
            for r in run:
                reason[r] = why
        i = j
    return pos, reason


def spans(words, reason, pad=0.06, reach=3.0):
    """자를 단어를 이어진 덩어리로 묶어 시간 구간으로. 앞뒤 남는 단어 사이의 빈틈(받아쓰기에 안 잡힌 말소리)도 함께 자른다."""
    out, i = [], 0
    while i < len(words):
        if i not in reason:
            i += 1
            continue
        j = i
        while j + 1 < len(words) and (j + 1) in reason:
            j += 1
        prev_end = words[i - 1]["end"] if i > 0 else 0.0
        next_start = words[j + 1]["start"] if j + 1 < len(words) else words[j]["end"] + 0.3
        a = prev_end + pad if words[i]["start"] - prev_end <= reach else words[i]["start"] - 0.25
        b = next_start - pad if next_start - words[j]["end"] <= reach else words[j]["end"] + 0.25
        if b - a < 0.05:
            a, b = words[i]["start"], words[j]["end"]
        whys = []
        for r in range(i, j + 1):
            if reason[r] not in whys:
                whys.append(reason[r])
        out.append({"start": round(max(0.0, a), 3), "end": round(b, 3), "reason": " + ".join(whys),
                    "text": " ".join(words[r]["word"].strip() for r in range(i, j + 1))})
        i = j + 1
    return out


def fmt(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("words", help="transcribe.py 가 만든 words.json (원본 시간)")
    p.add_argument("--script", default=DEFAULT_SCRIPT)
    p.add_argument("--part", default="part-main")
    p.add_argument("--gap", type=float, default=0.45, help="이보다 오래 쉬면 말 덩어리를 나눈다(초)")
    p.add_argument("--window", type=float, default=90, help="이 초 안에서만 다시 읽기를 찾는다")
    p.add_argument("--keep", action="append", default=[], metavar="시작-끝",
                   help="자르지 말 구간(원본 초). 잘못 잡힌 곳을 살릴 때")
    p.add_argument("-o", "--out", help="출력 이름 앞부분 (기본: 입력에서 .words.json 뺀 것)")
    args = p.parse_args()

    with open(args.words, encoding="utf-8") as f:
        data = json.load(f)
    words = [w for w in (data["words"] if isinstance(data, dict) else data) if norm_chars(w["word"])]
    paras = load_script(args.script, args.part)
    s_chars = norm_chars("\n".join(t for t, _ in paras))
    _, reason = find_cuts(words, s_chars, args.gap, args.window)
    for spec in args.keep:
        a, b = (float(v) for v in spec.split("-"))
        for i in [i for i in reason if words[i]["start"] >= a and words[i]["end"] <= b]:
            del reason[i]
    cuts = spans(words, reason)

    stem = args.out or re.sub(r"(\.words)?\.json$", "", args.words)
    with open(stem + ".retakes.json", "w", encoding="utf-8") as f:
        json.dump({"cuts": cuts}, f, ensure_ascii=False, indent=1)
    clean = [w for i, w in enumerate(words) if i not in reason]
    with open(stem + ".clean.words.json", "w", encoding="utf-8") as f:
        json.dump({"language": data.get("language", "ko") if isinstance(data, dict) else "ko",
                   "words": clean}, f, ensure_ascii=False, indent=1)
    total = sum(c["end"] - c["start"] for c in cuts)
    with open(stem + ".retakes.txt", "w", encoding="utf-8") as f:
        for c in cuts:
            f.write(f"{fmt(c['start'])}–{fmt(c['end'])}  [{c['reason']}]  {c['text']}\n")
    counts = {}
    for c in cuts:
        for r in c["reason"].split(" + "):
            counts[r] = counts.get(r, 0) + 1
    print(f"자를 곳 {len(cuts)}곳 · {total:.1f}초 ("
          + ", ".join(f"{k} {v}" for k, v in counts.items()) + f")  목록: {stem}.retakes.txt")
    print(f"남긴 받아쓰기: {stem}.clean.words.json (단어 {len(clean)}/{len(words)})")


if __name__ == "__main__":
    sys.exit(main())
