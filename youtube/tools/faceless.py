"""얼굴 촬영 없이 만드는 세로(9:16) 쇼츠·릴스: 문장별 음성(wav) + 그래픽·화면 녹화 + 한 줄 자막.

화면 (1080×1920)
  위        제목 두 줄 + 작은 안내 문구 (shorts.py 와 같은 모양)
  가운데    그래픽·녹화 칸 BOX (1080×840)
  그 아래   한 줄 자막 (shorts.py 의 릴스 자막: 단어가 하나씩 나타남)
  맨 아래   장 이름 칩 + 동그란 프로필 사진 (--note 로 작은 문구 추가 가능)
  마지막    cta 배너 (팔로우·댓글 → DM 또는 고정 댓글)

설정 JSON (키마다 영상 하나)
  {"title": [..2줄..], "chapter": "4장 회로 정리", "lines": [{"sub": 자막, "wav": 음성 파일}, ...],
   (문장별 wav 대신 "audio": 한 덩어리 음성 파일 을 주면 쉼을 찾아 문장 경계를 맞춘다)
   "visuals": [[파일, 몇 번째 문장(0부터) 또는 "3.5s", crop [x,y,w,h] 또는 null, 시작 초], ...],
   "cta": ["팔로우 + 댓글 '회로'", "DM으로 사이트 링크 보내 드려요"]}

사용: python3 faceless.py config.json -o 출력폴더 [--only N] [--avatar 사진.png] [--note 문구]
결과: <출력폴더>/<키>.mp4 와 .srt (효과음은 sfx.py 로 따로)
"""
import argparse, json, os, re, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shorts as S
from transcribe import write_srt

W, H = 1080, 1920
BOX = (0, 400, 1080, 1240)          # 그래픽 칸
SUB_Y = 1300                        # 자막 윗선
FOOT_Y = 1470                       # 장 이름 칩 · 프로필
CTA_Y = 1000                        # 마지막 배너 (그래픽 칸 아랫부분)
GAP = 0.28                          # 문장 사이 쉼
LEAD = 0.25
VIDEO_EXT = (".mp4", ".webm", ".mov")


def speech_span(path):
    """wav 에서 말소리가 있는 구간(앞뒤 무음 제외)의 시작·끝 초와 전체 길이."""
    with wave.open(path) as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        x = np.frombuffer(w.readframes(n), dtype={2: np.int16, 4: np.int32}[sw]).astype(np.float32)
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    hop = int(sr * 0.02)
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    thr = max(e.max() * 0.06, 1e-9)
    idx = np.where(e > thr)[0]
    a, b = (idx[0] * hop / sr, (idx[-1] + 1) * hop / sr) if len(idx) else (0, n / sr)
    return a, b, n / sr


def envelope(path):
    with wave.open(path) as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        x = np.frombuffer(w.readframes(n), dtype={2: np.int16, 4: np.int32}[sw]).astype(np.float32)
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    hop = int(sr * 0.01)
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    return e, 0.01, n / sr


def para_spans(path, texts):
    """한 덩어리 음성에서 문장마다 (시작, 끝). 글자 수 비율로 짐작한 경계를 가장 가까운 쉼(무음)에 맞춘다."""
    e, dt, dur = envelope(path)
    thr = e.max() * 0.05
    on = e > thr
    idx = np.where(on)[0]
    s0, s1 = idx[0] * dt, (idx[-1] + 1) * dt
    gaps, i = [], 0                                   # 0.12초 넘는 쉼: (시작, 끝)
    while i < len(on):
        if not on[i]:
            j = i
            while j < len(on) and not on[j]:
                j += 1
            if (j - i) * dt >= 0.12 and i * dt > s0 and j * dt < s1:
                gaps.append((i * dt, j * dt))
            i = j
        else:
            i += 1
    L = [len(re.sub(r"[^가-힣A-Za-z0-9]", "", t)) for t in texts]
    tot, acc, cuts, used = sum(L), 0, [], set()
    for l in L[:-1]:
        acc += l
        guess = s0 + (s1 - s0) * acc / tot
        cand = [(abs((g[0] + g[1]) / 2 - guess) - (g[1] - g[0]) * 0.8, k) for k, g in enumerate(gaps) if k not in used and abs((g[0] + g[1]) / 2 - guess) < 1.6]
        if cand:
            k = min(cand)[1]; used.add(k); cuts.append(gaps[k])
        else:
            cuts.append((guess, guess))
    cuts.sort()
    starts = [s0] + [c[1] for c in cuts]; ends = [c[0] for c in cuts] + [s1]
    return list(zip(starts, ends)), dur


MAXC = 26                           # 자막 한 덩어리(최대 두 줄) 글자 수


def gaps_of(path, offset=0.0, min_gap=0.06):
    """말소리 사이 쉼 (절대 시각, 시작·끝)."""
    e, dt, _ = envelope(path)
    on = e > e.max() * 0.05
    out, i = [], 0
    while i < len(on):
        if not on[i]:
            j = i
            while j < len(on) and not on[j]:
                j += 1
            if (j - i) * dt >= min_gap:
                out.append((offset + i * dt, offset + j * dt))
            i = j
        else:
            i += 1
    return out


def groups(text, maxc=MAXC):
    """자막 덩어리: 문장 단위로 끊고, 짧은 문장은 두 개까지 묶고, 긴 문장은 쉼표(없으면 가운데 띄어쓰기)에서 나눈다."""
    parts = []
    for sent in [x.strip() for x in re.findall(r"(?:[^.?!]|\.(?=\d))+[.?!]?", text) if x.strip()]:
        if len(sent) <= maxc:
            parts.append(sent); continue
        cur = ""
        for bit in [b.strip() for b in re.findall(r"(?:[^,]|,(?=\d))+,?", sent) if b.strip()]:
            if cur and len(cur) + 1 + len(bit) > maxc:
                parts.append(cur); cur = bit
            else:
                cur = (cur + " " + bit).strip()
        parts.append(cur)
    fixed = []
    for x in parts:                                   # 그래도 길면 가운데 띄어쓰기에서 반으로
        if len(x) > maxc * 1.25 and " " in x:
            m = min((i for i, c in enumerate(x) if c == " "), key=lambda i: abs(i - len(x) / 2))
            fixed += [x[:m], x[m + 1:]]
        else:
            fixed.append(x)
    out, n = [], 0
    for x in fixed:                                   # 짧은 문장은 두 개까지 한 화면에
        if out and n < 2 and re.search(r"[.?!]$", out[-1]) and len(out[-1]) + 1 + len(x) <= maxc:
            out[-1] += " " + x; n += 1
        else:
            out.append(x); n = 1
    return out


def whisper_words(path, offset=0.0):
    """음성의 단어별 시각 (받아쓰기, 결과는 옆에 .words.json 으로 저장해 다시 쓴다)."""
    cache = os.path.splitext(path)[0] + ".words.json"
    keep = os.environ.get("KEEP_WORDS") and os.path.exists(cache)   # 받아쓰기를 손으로 고친 뒤 다시 합성할 때 (음성은 그대로)
    if not keep and (not os.path.exists(cache) or os.path.getmtime(cache) < os.path.getmtime(path)):
        from faster_whisper import WhisperModel
        m = WhisperModel("medium", device="cpu", compute_type="int8")
        seg, _ = m.transcribe(path, language="ko", beam_size=5, word_timestamps=True)
        json.dump([[w.word.strip(), w.start, w.end] for sg in seg for w in sg.words], open(cache, "w"), ensure_ascii=False)
    return [(w, a + offset, b + offset) for w, a, b in json.load(open(cache))]


def snap_word(first, guess, words, lo, hi):
    """다음 덩어리의 첫 어절과 가장 비슷한 받아쓰기 단어(짐작 시각 근처)를 찾아 (앞 단어 끝, 그 단어 시작)."""
    from difflib import SequenceMatcher
    key = re.sub(r"[^가-힣A-Za-z0-9]", "", first)
    best = None
    for i, (w, a, b) in enumerate(words):
        if not (lo < a < hi) or abs(a - guess) > 4.0 or i == 0:
            continue
        ww = re.sub(r"[^가-힣A-Za-z0-9]", "", w)
        if len(ww) > len(key) + 1:                    # 받아쓰기가 다음 말까지 붙여 쓴 경우: 앞부분만 비교
            ww = ww[:len(key) + 1]
        sc = SequenceMatcher(None, key.lower(), ww.lower()).ratio() - abs(a - guess) * 0.08
        if best is None or sc > best[0]:
            best = (sc, words[i - 1][2], a)
    return (min(best[1], best[2]), best[2]) if best and best[0] > 0.3 else None


def spoken(t):
    """자막 표기를 읽는 순서로: 1/(s+a) → s플러스a분의1, e의 −at승 → e의 마이너스at승, σ·ω → 시그마·오메가.
    받아쓰기와 글자 맞추기(word_cues) 전에 양쪽에 똑같이 쓴다."""
    t = re.sub(r"([A-Za-z0-9.ωσ]+)/\(?([A-Za-z0-9ωσ+−]+)\)?", lambda m: m.group(2) + "분의" + m.group(1), t)
    for a, b in (("+", "플러스"), ("−", "마이너스"), ("σ", "시그마"), ("ω", "오메가")):
        t = t.replace(a, b)
    return t


def word_cues(texts, words):
    """대본 전체를 덩어리로 나누고, 대본 글자열과 받아쓰기 글자열을 통째로 맞춰(difflib) 덩어리 첫 글자가
    실제로 말해진 단어의 시작 시각을 찾는다. 숫자 표기처럼 안 맞는 곳은 앞뒤 맞은 글자 사이를 비례로 메운다.
    돌려주는 것: (자막, 문장별 구간)."""
    from difflib import SequenceMatcher
    import numpy as np
    nz = lambda t: re.sub(r"[^가-힣a-z0-9]", "", t.lower())
    items = [(li, g) for li, t in enumerate(texts) for g in groups(t)]   # g 에는 *강조* 표시가 남아 있다 (자막 색칠용)
    S, offs = "", []
    for _, g in items:
        offs.append(len(S)); S += nz(spoken(g))
    Wt, owner = "", []
    for k, (w, a, b) in enumerate(words):
        x = nz(spoken(w)); Wt += x; owner += [k] * len(x)
    xs, ys = [], []
    for blk in SequenceMatcher(None, S, Wt, autojunk=False).get_matching_blocks():
        for d in range(blk.size):
            xs.append(blk.a + d); ys.append(blk.b + d)
    xs = [-1] + xs + [len(S)]; ys = [-1] + ys + [len(Wt)]
    first = []
    for o in offs:
        wp = int(round(float(np.interp(o, xs, ys))))
        first.append(owner[min(max(wp, 0), len(owner) - 1)])
    for k in range(1, len(first)):                    # 덩어리마다 다른 단어에서 시작 (뒤로만)
        first[k] = max(first[k], first[k - 1] + 1) if first[k - 1] + 1 < len(words) else first[k]
    starts = [words[first[0]][1]] + [words[f][1] for f in first[1:]]
    ends = [words[f - 1][2] for f in first[1:]] + [words[-1][2]]
    cues = [{"start": a, "end": max(min(b, n - 0.05) if n else b, a + 0.3), "text": g}
            for (_, g), a, b, n in zip(items, starts, ends, starts[1:] + [None])]
    spans = []
    for li in range(len(texts)):
        ks = [k for k, (l, _) in enumerate(items) if l == li]
        spans.append((starts[ks[0]], ends[ks[-1]]))
    return cues, spans


def snap_gaps(cues, gaps, max_shift=0.7):
    """받아쓰기는 쉼 앞 단어 끝을 다음 단어 시작으로 붙여 쓰곤 해서 자막이 말보다 먼저 뜬다.
    자막 시작이 쉼(0.1초 이상) 안에 떨어지면 쉼이 끝나는 순간(말 시작)으로 옮긴다."""
    for i, c in enumerate(cues):
        for a, b in gaps:
            if b - a >= 0.1 and a - 0.02 <= c["start"] < b and b - c["start"] <= max_shift:
                c["start"] = b - 0.03
                c["end"] = max(c["end"], c["start"] + 0.3)
                if i:
                    cues[i - 1]["end"] = min(cues[i - 1]["end"], c["start"] - 0.02)
                break
    return cues


def timed_groups(text, a, b, gaps, words=None):
    """덩어리마다 (시작, 끝): 글자 수 비율로 짐작한 경계를 그 문장 안의 가장 가까운 쉼에 맞춘다."""
    gs = groups(text)
    L = [len(re.sub(r"[^가-힣A-Za-z0-9]", "", g)) or 1 for g in gs]
    inner = [g for g in gaps if a < g[0] and g[1] < b]
    tot, acc, cuts, used = sum(L), 0, [], set()
    for l in L[:-1]:
        acc += l; guess = a + (b - a) * acc / tot
        prev = cuts[-1][1] if cuts else a
        if words:                                     # 받아쓰기가 있으면 실제 단어 시각에 맞춘다 (앞 경계보다 뒤에서만)
            hit = snap_word(gs[len(cuts) + 1].split()[0], max(guess, prev + 0.4), words, prev + 0.3, b - 0.3)
            if hit:
                cuts.append(hit); continue
        cand = [(abs((g[0] + g[1]) / 2 - guess) - (g[1] - g[0]) * 1.5, k) for k, g in enumerate(inner)
                if k not in used and abs((g[0] + g[1]) / 2 - guess) < 1.2 and g[0] > prev + 0.3]
        if cand:
            k = min(cand)[1]; used.add(k); cuts.append(inner[k])
        else:
            g2 = max(guess, prev + 0.3); cuts.append((g2, g2))
    st = [a] + [c[1] for c in cuts]; en = [c[0] for c in cuts] + [b]
    return [{"start": x, "end": y, "text": g} for g, x, y in zip(gs, st, en)]


def chunks(text, maxc=12):
    """한 줄 자막 조각: 어절을 이어 붙이다 maxc 글자를 넘거나 문장부호에서 끊는다."""
    out, cur = [], []
    for w in text.split():
        if cur and (len(" ".join(cur + [w])) > maxc):
            out.append(" ".join(cur)); cur = []
        cur.append(w)
        if re.search(r"[.?!,]$", w) and len(" ".join(cur)) >= 6:
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def footer(chapter, avatar, note, path):
    img = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 60
    if avatar and os.path.exists(avatar):
        av = Image.open(avatar).convert("RGBA").resize((130, 130))
        m = Image.new("L", (130, 130), 0); ImageDraw.Draw(m).ellipse((0, 0, 129, 129), fill=255)
        ring = Image.new("RGBA", (142, 142), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 141, 141), fill=(255, 197, 61, 255))
        img.alpha_composite(ring, (x - 6, 24)); img.paste(av, (x, 30), m)
        x += 160
    fb = ImageFont.truetype(S.FONT_BLACK, 44); fs = ImageFont.truetype(S.FONT_BOLD, 30)
    tw, y = d.textlength(chapter, font=fb), (34 if note else 60)   # 문구가 없으면 칩을 사진 가운데 높이로
    d.rounded_rectangle((x, y, x + tw + 44, y + 70), 18, fill=(255, 197, 61, 255))
    d.text((x + 22, y + 35), chapter, font=fb, fill=(17, 19, 24), anchor="lm")
    if note:
        d.text((x + 2, 140), note, font=fs, fill=(150, 156, 170), anchor="lm")
    img.save(path)


def build(name, cfg, out_dir, avatar, note, ffmpeg):
    lines = cfg["lines"]
    # 1) 음성: 한 덩어리(audio)면 쉼으로 문장 경계를 찾고, 아니면 문장별 wav 를 이어 붙인다
    if cfg.get("audio"):
        sp, dur = para_spans(cfg["audio"], [ln["sub"] for ln in lines])
        spans = [(LEAD + a, LEAD + b) for a, b in sp]; parts = [(cfg["audio"], LEAD)]; total = LEAD + dur + 0.6
        gaps = gaps_of(cfg["audio"], LEAD); words = whisper_words(cfg["audio"], LEAD)
    else:
        t, spans, parts, gaps, words = LEAD, [], [], [], None
        for ln in lines:
            a, b, dur = speech_span(ln["wav"])
            spans.append((t + a, t + b)); parts.append((ln["wav"], t)); gaps += gaps_of(ln["wav"], t); t += dur + GAP
        total = t + 0.6
    # 2) 자막: 한두 문장씩 묶은 덩어리를, 실제 말소리 쉼에 맞춰 통째로 띄운다
    if words:                                         # 한 덩어리 음성: 받아쓰기 단어 시각으로 자막·문장 구간을 다시 잡는다
        cues, spans = word_cues([ln["sub"] for ln in lines], words)
        cues = snap_gaps(cues, gaps)
    else:
        cues = []
        for ln, (a, b) in zip(lines, spans):
            cues += timed_groups(ln["sub"], a, b, gaps)
    base = os.path.join(out_dir, name)
    write_srt([dict(c, text=c["text"].replace("*", "")) for c in cues], base + ".srt")
    # 3) 그래픽 배치: 문장 번호 → 그 문장 말소리 시작 시각
    plan = []
    for f, at, crop, ss in cfg.get("visuals", []):
        t0 = float(at[:-1]) if isinstance(at, str) and at.endswith("s") else max(0.0, spans[int(at)][0] - 0.15)
        plan.append([f, t0, crop, ss])
    plan.sort(key=lambda p: p[1]); plan[0][1] = 0.0
    print(f"{name}: {total:.1f}초 · 문장 {len(lines)} · 자막 {len(cues)} · 그래픽 {len(plan)}")
    with tempfile.TemporaryDirectory() as tmp:
        S.PERSON_Y, S.FADE_H, S.NOTE, S.SUB_TOP = BOX[1] - 10, 0, cfg.get("note", ""), SUB_Y
        title = os.path.join(tmp, "title.png"); S.title_overlay(cfg["title"], title)
        foot = os.path.join(tmp, "foot.png"); footer(cfg.get("chapter", ""), avatar, note, foot)
        ass = os.path.join(tmp, "s.ass"); S.write_ass_block(cues, ass)
        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
               "-f", "lavfi", "-t", f"{total:.3f}", "-i", f"color=c=0x111318:s={W}x{H}:r=30"]
        amix = []
        for k, (wav, at) in enumerate(parts):
            cmd += ["-i", wav]; amix.append(f"[{k + 1}:a]aresample=48000,adelay={int(at * 1000)}|{int(at * 1000)}[a{k}]")
        nA = len(parts)
        chains = amix + ["".join(f"[a{k}]" for k in range(nA)) + f"amix=inputs={nA}:normalize=0,apad,atrim=0:{total:.3f}[aout]"]
        idx = nA + 1
        cmd += ["-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", title, "-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", foot]
        chains.append(f"[0:v][{idx}:v]overlay=0:0[v0]"); chains.append(f"[v0][{idx + 1}:v]overlay=0:{FOOT_Y}[v1]")
        prev, idx = "[v1]", idx + 2
        bx1, by1, bx2, by2 = BOX; bw, bh = bx2 - bx1, by2 - by1
        for i, (src, t0, crop, ss) in enumerate(plan):
            t1 = plan[i + 1][1] + 0.25 if i + 1 < len(plan) else total
            cr = "crop={}:{}:{}:{},".format(*[int(v) // 2 * 2 for v in (crop[2], crop[3], crop[0], crop[1])]) if crop else ""
            if src.endswith(VIDEO_EXT):
                cmd += ["-ss", f"{ss:.2f}", "-i", src]
                pre = f"[{idx}:v]{cr}scale={bw}:{bh}:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=600,trim=0:{t1 - t0:.3f},"
            else:
                cmd += ["-loop", "1", "-framerate", "30", "-t", f"{t1 - t0:.3f}", "-i", src]
                pre = f"[{idx}:v]{cr}scale={bw}:{bh}:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1,"
            chains.append(pre + f"format=rgba,fade=t=in:st=0:d=0.25:alpha=1,setpts=PTS-STARTPTS+{t0:.3f}/TB[p{i}]")
            chains.append(f"{prev}[p{i}]overlay=x={bx1}+({bw}-w)/2:y={by1}+({bh}-h)/2:eof_action=pass:enable='between(t,{t0:.3f},{t1:.3f})'[o{i}]")
            prev, idx = f"[o{i}]", idx + 1
        if cfg.get("cta"):
            cta = os.path.join(tmp, "cta.png"); S.cta_banner(cfg["cta"], cta)
            ct = max(0.0, spans[-1][0] - 0.2)
            cmd += ["-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", cta]
            chains.append(f"[{idx}:v]format=rgba,fade=t=in:st={ct:.3f}:d=0.25:alpha=1[cta]")
            chains.append(f"{prev}[cta]overlay=0:{CTA_Y}:enable='gte(t,{ct:.3f})'[ctav]"); prev = "[ctav]"
        chains.append(f"{prev}ass={ass}:fontsdir={os.path.expanduser('~/.fonts')}[out]")
        cmd += ["-filter_complex", ";".join(chains), "-map", "[out]", "-map", "[aout]", "-t", f"{total:.3f}",
                "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", base + ".mp4"]
        subprocess.run(cmd, check=True)
    print(f"  → {base}.mp4")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("config"); p.add_argument("-o", "--out", default=".")
    p.add_argument("--only", default=""); p.add_argument("--avatar", default="")
    p.add_argument("--note", default="")
    a = p.parse_args()
    cfg = {k: v for k, v in json.load(open(a.config, encoding="utf-8")).items() if not k.startswith("_")}
    os.makedirs(a.out, exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    for k, v in cfg.items():
        if not only or k in only:
            build(k, v, a.out, a.avatar, a.note, S.find_ffmpeg())


if __name__ == "__main__":
    main()
