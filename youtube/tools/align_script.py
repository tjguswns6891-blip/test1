"""촬영 대본과 Whisper 받아쓰기를 맞춰 자막 글자를 바로잡는 도구. 시간은 받아쓰기에서 가져온다.

자막은 "실제로 말한 것"을 기준으로 하되,
  · 대본과 같은 부분은 대본의 띄어쓰기·숫자 표기·문장부호를 쓰고
  · 발음이 비슷하게 다른 곳(측주→축제, 해업→해협)과 영문·숫자 표기 차이(슈드→SCHD)는 대본 글자로 고치고
  · 발음이 다른 곳(걸어둘게요 / 넣어둘게요)과 대본에 없는 말은 말한 대로 두고
  · 대본에 있지만 말하지 않은 곳은 뺀다.
고친 곳·남긴 곳은 목록(.diff.txt)으로 뽑아 사람이 확인할 수 있게 한다.

사용 예:
  python3 align_script.py raw.words.json                        # youtube/index.html 본편 대본과 맞춤
  python3 align_script.py raw.words.json --script shorts_a.txt  # 텍스트 대본 (한 줄 = 한 문단)
  python3 align_script.py raw.words.json --part part-shorts     # index.html 의 다른 파트

결과 raw.script.words.json 은 transcribe.py --from-json (필요하면 --cuts) 에 그대로 넣는다.
"""
import argparse
import difflib
import html
import json
import os
import re
import sys

DEFAULT_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
SIMILAR = 0.3   # 자모 유사도가 이 이상이면 받아쓰기 오류로 보고 대본 글자를 쓴다
                # (엉뚱한 단어가 자막에 남는 것보다 대본 표현이 쓰이는 편이 낫다)


def norm_chars(text):
    """비교용 글자: 한글·영문·숫자만 남기고 소문자로."""
    return [c.lower() for c in text if c.isalnum()]


CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
JONG = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"


def jamo(text):
    out = []
    for c in text:
        code = ord(c) - 0xAC00
        if 0 <= code < 11172:
            out += [CHO[code // 588], JUNG[code % 588 // 28]] + ([JONG[code % 28]] if code % 28 else [])
        else:
            out.append(c)
    return out


def is_misheard(said, wrote):
    """받아쓰기 오류로 볼 만한 차이인지: 발음이 비슷하거나, 한쪽만 영문·숫자 표기."""
    if not said or not wrote:
        return False
    hangul = lambda t: any("가" <= c <= "힣" for c in t)
    latin = lambda t: any(c.isascii() and c.isalnum() for c in t)
    if (latin(said) != latin(wrote)) or (hangul(said) != hangul(wrote)):
        return True
    return difflib.SequenceMatcher(None, jamo(said), jamo(wrote)).ratio() >= SIMILAR


def load_script(path, part):
    """대본을 (문단, 장면 id) 목록으로 읽는다. index.html 이면 지정한 파트의 .script 문단만."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    if path.endswith((".html", ".htm")):
        m = re.search(rf'<section[^>]*id="{re.escape(part)}".*?(?=<section|\Z)', src, re.S)
        if not m:
            sys.exit(f"{path} 에서 id=\"{part}\" 파트를 찾지 못했어요.")
        paras = []
        for sid, body in re.findall(r'<article class="scene" id="([^"]+)"(.*?)</article>', m.group(0), re.S):
            for block in re.findall(r'<div class="script">(.*?)</div>', body, re.S):
                # 점선 칸(<span class="fill">)은 실물을 보고 채워 말할 자리 표시라 대본 글자에서 뺀다
                block = re.sub(r'<span class="fill">.*?</span>', " ", block, flags=re.S)
                paras += [(html.unescape(re.sub(r"<[^>]+>", "", p)), sid)
                          for p in re.findall(r"<p[^>]*>(.*?)</p>", block, re.S)]
    else:
        paras = [(line, None) for line in src.splitlines()]
    out = []
    for p, sid in paras:
        p = re.sub(r"\([^)]*\)", "", p)             # (채널명) 같은 자리 표시
        p = re.sub(r"\s+/\s+", " ", p)              # 끊어 읽기 표시
        p = re.sub(r"\s+([,.?!])", r"\1", p)
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            out.append((p, sid))
    return out


def align(words, paras):
    # 받아쓰기: 비교용 글자 → 단어 번호. 기호를 소리로 읽은 말(45퍼, 마이너스 14)은
    # 대본의 %·− 기호가 대신하므로 비교에서 뺀다.
    joined, owner_at = "", []
    for i, w in enumerate(words):
        joined += w["word"] if w["word"].startswith(" ") else " " + w["word"]
        owner_at += [i] * (len(joined) - len(owner_at))
    spoken_symbol = set()
    for m in re.finditer(r"(?<=\d)\s*퍼(센트)?|마이너스(?=\s*\d)", joined):
        spoken_symbol.update(range(m.start(), m.end()))
    t_chars, t_owner, t_at = [], [], []
    for j, c in enumerate(joined):
        if c.isalnum() and j not in spoken_symbol:
            t_chars.append(c.lower())
            t_owner.append(owner_at[j])
            t_at.append(j)
    # 대본: 문단을 이어 붙인 문자열과, 비교용 글자의 위치·장면
    text, scene_at = "", []
    for p, sid in paras:
        text += p + "\n"
        scene_at += [sid] * (len(p) + 1)
    s_pos = [i for i, c in enumerate(text) if c.isalnum()]
    s_chars = [text[i].lower() for i in s_pos]

    keep = [None] * len(s_pos)          # 대본 글자별: 쓸 경우 받아쓰기 단어 번호 목록
    inserts = {}                        # 대본 글자 번호 앞에 끼워 넣을 (말한 글자, 단어 번호들)
    diffs = []

    def owners(b1, b2):
        return sorted({t_owner[k] for k in range(b1, b2)})

    def spoken(b1, b2):   # 받아쓰기 원문 그대로 (띄어쓰기 유지, 소리로 읽은 기호 제외)
        if b1 >= b2:
            return ""
        return "".join(c for j, c in enumerate(joined[t_at[b1]:t_at[b2 - 1] + 1], t_at[b1])
                       if j not in spoken_symbol).strip()

    def pieces(b1, b2):   # 끼워 넣을 말을 받아쓰기 단어별 조각으로: [(글자, [단어 번호], 단어 첫머리인지)]
        out = []
        for j in range(t_at[b1], t_at[b2 - 1] + 1):
            if j in spoken_symbol:
                continue
            o = owner_at[j]
            if not out or out[-1][1][0] != o:
                out.append(["", [o], joined[j].isspace() or j == 0 or joined[j - 1].isspace()])
            out[-1][0] += joined[j]
        return [(t.strip(), ids, first) for t, ids, first in out if t.strip()]

    sm = difflib.SequenceMatcher(None, s_chars, t_chars, autojunk=False)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        at = words[t_owner[min(b1, len(t_owner) - 1)]]["start"]
        wrote = text[s_pos[a1]:s_pos[a2 - 1] + 1] if a2 > a1 else ""
        said = spoken(b1, b2)
        if op == "equal":
            for k in range(a2 - a1):
                keep[a1 + k] = [t_owner[b1 + k]]
        elif op == "replace" and is_misheard(said, wrote):
            for k in range(a1, a2):
                keep[k] = owners(b1, b2)
            diffs.append((at, "대본으로 교정", said, wrote))
        else:
            if b2 > b1:
                # 받아쓰기 단어 중간에서 시작하면 앞 글자에 붙이고, 중간에서 끝나면 뒤 글자에 붙인다
                mid_start = b1 > 0 and t_owner[b1 - 1] == t_owner[b1]
                mid_end = b2 < len(t_owner) and t_owner[b2] == t_owner[b2 - 1]
                inserts.setdefault(a1, []).append((pieces(b1, b2), mid_start, mid_end))
            kind = "말한 대로" if op == "replace" else "대본에 없는 말" if op == "insert" else "말하지 않아 뺌"
            diffs.append((at, kind, said, wrote))

    # 대본 문자열을 따라가며 자막 글자를 만든다: (글자, 단어 번호들, 장면)
    out_chars, space, prev_kept = [], False, False

    def emit(chunk, ids, sid):
        nonlocal space
        if space and out_chars:
            out_chars.append((" ", [], None))
        space = False
        out_chars.append((chunk, ids, sid))

    def scene_now():
        return next((c[2] for c in reversed(out_chars) if c[2]), paras[0][1])

    for k, pos in enumerate(s_pos + [None]):
        ins = inserts.get(k, [])
        for parts, mid_start, mid_end in ins:               # 앞 단어에 이어지는 말: 문장부호보다 앞
            if mid_start:
                for n, (t, ids, first) in enumerate(parts):
                    if n and first:
                        out_chars.append((" ", [], None))
                    out_chars.append((t, ids, scene_now()))
        if pos is None:
            break
        gap = text[(s_pos[k - 1] + 1 if k else 0):pos]      # 앞 글자와의 사이 (공백·문장부호)
        m = re.match(r"(\S*)(\s*)(\S*)$", gap) if re.fullmatch(r"\S*\s*\S*", gap) else None
        pre, ws, post = m.groups() if m else (re.sub(r"\s", "", gap), "", "")
        if pre and prev_kept:
            out_chars.append((pre, [], None))                # 닫는 문장부호는 앞 글자에 붙이고
        space = space or bool(ws)
        for parts, mid_start, mid_end in ins:
            if not mid_start:
                space = space or bool(out_chars)
                for n, (t, ids, first) in enumerate(parts):
                    if n:
                        space = first
                    emit(t, ids, scene_now())
                space = not mid_end
        prev_kept = keep[k] is not None
        if prev_kept:
            emit(post + text[pos], keep[k], scene_at[pos])   # 여는 문장부호(" ' −)는 뒤 글자에 붙인다
    if s_pos and prev_kept:
        out_chars.append((re.sub(r"\s", "", text[s_pos[-1] + 1:]), [], None))

    # 공백 기준으로 단어를 나누고, 단어 안 글자들의 시간 범위를 붙인다
    result, cur, ids, scene = [], "", [], None
    def push():
        if cur.strip() and ids:
            result.append({"word": " " + cur.strip(), "start": round(min(words[i]["start"] for i in ids), 3),
                           "end": round(max(words[i]["end"] for i in ids), 3), "scene": scene})
        elif cur.strip() and result:   # 시간 없는 조각(문장부호 등)은 앞 단어에 붙인다
            result[-1]["word"] += cur.strip()
    for chunk, cids, sid in out_chars:
        for c in chunk:
            if c.isspace():
                push()
                cur, ids, scene = "", [], None
            else:
                cur += c
                ids += [i for i in cids if i not in ids]   # 조각 안 공백 뒤 단어도 시간을 갖게
                if sid and scene is None:
                    scene = sid
    push()
    return result, diffs


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("words", help="transcribe.py 가 만든 words.json")
    p.add_argument("--script", default=DEFAULT_SCRIPT, help="대본 (index.html 또는 한 줄 = 한 문단 텍스트)")
    p.add_argument("--part", default="part-main", help="index.html 에서 쓸 파트 id (기본 본편)")
    p.add_argument("-o", "--out", help="출력 (기본: <이름>.script.words.json)")
    args = p.parse_args()

    with open(args.words, encoding="utf-8") as f:
        data = json.load(f)
    words = [w for w in (data["words"] if isinstance(data, dict) else data) if norm_chars(w["word"])]
    paras = load_script(args.script, args.part)
    aligned, diffs = align(words, paras)

    out = args.out or re.sub(r"(\.words)?\.json$", "", args.words) + ".script.words.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"language": data.get("language", "ko") if isinstance(data, dict) else "ko",
                   "source": "script", "words": aligned}, f, ensure_ascii=False, indent=1)
    report = re.sub(r"(\.words)?\.json$", "", out) + ".diff.txt"
    with open(report, "w", encoding="utf-8") as f:
        for at, kind, said, wrote in diffs:
            f.write(f"{int(at // 60)}:{at % 60:05.2f}  [{kind}]  말함: {said or '-'}  |  대본: {wrote or '-'}\n")
    counts = {k: sum(1 for d in diffs if d[1] == k) for k in ("대본으로 교정", "말한 대로", "대본에 없는 말", "말하지 않아 뺌")}
    print(f"대본 문단 {len(paras)}개 · 어절 {len(aligned)}개 → {out}")
    print("차이: " + ", ".join(f"{k} {v}곳" for k, v in counts.items()) + f"  (목록: {report})")


if __name__ == "__main__":
    main()
