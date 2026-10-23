#!/usr/bin/env python3
"""클로드 코드 5가지 릴스 편집: 얼굴 촬영 원본 + 위쪽 모션그래픽 → 1080×1920 완성본.

1. 무음 구간(0.3초 넘는 빈 간격)을 잘라 낸다.
2. 대사 줄마다 위쪽 장면을 정해 top.html 을 그 길이대로 렌더링한다(render_seq.js).
3. 아래 얼굴은 줄마다 번갈아 살짝 확대(점프컷 가림), 마지막 CTA 는 얼굴 전체 화면.
4. 분할선에 2~7글자씩 큰 자막(키워드는 주황), 장면 전환마다 효과음.

  python3 edit.py <작업폴더: source.mov, words.json> <출력.mp4>
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, "..", "..", "sfx", "kit")
W, H, TOP = 1080, 1920, 880          # 위쪽 애니메이션 높이, 아래 얼굴은 1040
FPS = 30
MIN_GAP, PAD = 0.30, 0.07            # 이보다 긴 무음은 자르고, 말 앞뒤로 PAD 만큼 남긴다

# 원본 시각 기준 줄 경계(받아쓰기에서 확인), 위쪽 장면 번호
LINES = [  # (시작, 장면)  장면 None = 얼굴 전체 화면
    (0.00, 6),    # 대학생이 직접 써 본 클로드 코드 꿀팁
    (3.80, 0),    # 코드 쓰면서 이거 모르면 토큰 그냥 버리는 중이에요
    (8.00, 7),    # 딱 5개만 바꿔 보세요
    (10.60, 1),   # 첫째 /compact
    (16.70, 2),   # 둘째 ESC 두 번
    (22.00, 3),   # 셋째 CLAUDE.md
    (27.60, 4),   # 넷째 Shift+Tab 두 번
    (33.12, 5),   # 다섯째 서브에이전트
    (39.00, None),  # CTA
]
# 받아쓰기 오류 고침, 여러 단어 묶기
FIX = {"위전으로": "이전으로", "플랫": "플랜", "바뀌어요": "맡겨요", "2번": "두 번", "5개만": "5개만"}
MERGE = [(["Slash", "Compact"], "/compact"), (["클로드", "MD"], "CLAUDE.md"), (["Shift", "탭", "두 번"], "Shift+Tab 두 번"),
         (["ESC", "두 번"], "ESC 두 번"), (["서브", "에이전트"], "서브에이전트")]
KEY = ["토큰", "5개만", "/compact", "ESC 두 번", "CLAUDE.md", "Shift+Tab 두 번", "플랜", "서브에이전트", "'클코'", "꿀팁"]


def sh(cmd):
    subprocess.run(cmd, check=True)


def silences(src):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=noise=-35dB:d=0.2", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en))


def keep_spans(src, dur, last_word_end):
    spans, cur = [], 0.0
    for a, b in silences(src):
        if b - a < MIN_GAP:
            continue
        if a + PAD > cur:
            spans.append((cur, a + PAD))
        cur = b - PAD
    spans.append((cur, min(dur, last_word_end + 0.35)))
    return [(max(0, a), b) for a, b in spans if b - a > 0.05]


def mapper(spans):
    def f(t):
        acc = 0.0
        for a, b in spans:
            if t < a:
                return acc
            if t <= b:
                return acc + t - a
            acc += b - a
        return acc
    return f


def words_fixed(words):
    ws = [dict(w, word=FIX.get(w["word"].strip().rstrip(","), w["word"].strip().rstrip(","))) for w in words]
    out, i = [], 0
    while i < len(ws):
        for seq, rep in MERGE:
            if [w["word"] for w in ws[i:i + len(seq)]] == seq:
                out.append({"start": ws[i]["start"], "end": ws[i + len(seq) - 1]["end"], "word": rep})
                i += len(seq)
                break
        else:
            out.append(ws[i]); i += 1
    # 마지막 '댓글에 코드' 의 코드는 키워드 '클코'
    for j, w in enumerate(out):
        if w["word"] == "코드" and j > 0 and out[j - 1]["word"] == "댓글에":
            w["word"] = "'클코'"
    return out


def chunks(words, line_starts):
    """줄 경계를 넘지 않게 2~7글자 묶음으로 자른다."""
    out, cur = [], []
    def line_of(t):
        return sum(1 for s in line_starts if t >= s - 0.05) - 1
    for w in words:
        if cur and (line_of(w["start"]) != line_of(cur[0]["start"])
                    or len("".join(x["word"] for x in cur + [w]).replace(" ", "")) > 7
                    or any(k == w["word"] or k == cur[-1]["word"] for k in KEY)):
            out.append(cur); cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [(c[0]["start"], c[-1]["end"], " ".join(x["word"] for x in c)) for c in out]


def ass_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(path, caps, cta_from):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Split,Noto Sans CJK KR Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1
Style: Low,Noto Sans CJK KR Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for i, (a, b, txt) in enumerate(caps):
        end = caps[i + 1][0] if i + 1 < len(caps) and caps[i + 1][0] - b < 0.5 else b + 0.15
        cta = a >= cta_from - 0.01
        y = 1000 if cta else TOP
        body = txt
        for k in sorted(KEY, key=len, reverse=True):
            if k in body:
                body = body.replace(k, "{\\c&H1A7AFF&}" + k + "{\\c&HFFFFFF&}", 1)
                break
        pop = "{\\fscx82\\fscy82\\t(0,90,\\fscx100\\fscy100)}"
        lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(end)},{'Low' if cta else 'Split'},,0,0,0,,{{\\pos(540,{y})}}{pop}{body}")
    open(path, "w").write(head + "\n".join(lines) + "\n")


def main(work, out):
    src = os.path.join(work, "source.mov")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]))
    segs = json.load(open(os.path.join(work, "words.json")))
    words = [w for s in segs for w in s["words"]]
    spans = keep_spans(src, dur, words[-1]["end"])
    m = mapper(spans)
    total = sum(b - a for a, b in spans)
    print("spans", len(spans), "length", round(total, 2), "from", round(dur, 2))

    # 1) 무음 자른 원본 (30fps)
    parts = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];"
                    for i, (a, b) in enumerate(spans))
    cat = "".join(f"[v{i}][a{i}]" for i in range(len(spans))) + f"concat=n={len(spans)}:v=1:a=1[v][a]"
    cut = os.path.join(work, "cut.mp4")
    sh(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", parts + cat + f";[v]fps={FPS}[vo]",
        "-map", "[vo]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", cut])

    # 2) 줄 경계(새 시각)와 위쪽 장면 계획
    starts = [0.0] + [m(s) for s, _ in LINES[1:]] + [total]
    plan = [[sc, round(starts[i + 1] - starts[i], 3)] for i, (_, sc) in enumerate(LINES) if sc is not None]
    cta_from = starts[len(LINES) - 1]
    json.dump(plan, open(os.path.join(work, "plan.json"), "w"))
    top = os.path.join(work, "top.mp4")
    sh(["node", os.path.join(HERE, "render_seq.js"), os.path.join(work, "plan.json"), top, str(FPS)])

    # 3) 영상 합성: 줄마다 얼굴 확대를 번갈아, 위+아래 쌓기, CTA 는 얼굴 전체
    fc, segs_v = [], []
    for i in range(len(LINES)):
        a, b = starts[i], starts[i + 1]
        z = 1.0 if i % 2 == 0 else 1.1
        if LINES[i][1] is None:   # CTA: 얼굴 전체 화면, 살짝 확대
            fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,scale={int(W*1.04)}:-2,crop={W}:{H}[s{i}]")
        else:
            cw, ch = int(W / z), int(1040 / z)
            y0 = 300 + int((1040 - ch) * 0.35)
            fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,crop={cw}:{ch}:{(W-cw)//2}:{y0},scale={W}:1040,setsar=1[f{i}];"
                      f"[1:v]trim={a}:{b},setpts=PTS-STARTPTS[t{i}];[t{i}][f{i}]vstack[s{i}]")
        segs_v.append(f"[s{i}]")
    fc.append("".join(segs_v) + f"concat=n={len(LINES)}:v=1:a=0[base]")

    caps = chunks(words_fixed(words), [s for s, _ in LINES])
    caps = [(m(a), m(b), t) for a, b, t in caps]
    ass = os.path.join(work, "caps.ass")
    write_ass(ass, caps, cta_from)
    card = os.path.join(work, "cta_card.png")
    fc.append(f"[2:v]format=rgba,fade=in:st=0:d=0.3:alpha=1[card];"
              f"[base][card]overlay=0:0:enable='gte(t,{cta_from + 0.3})'[withcard];"
              f"[withcard]ass={ass}[vout]")

    # 4) 소리: 목소리 + 효과음(목소리보다 확실히 작게)
    sfx = [("intro1_dodon", 0.0, 0.32)]
    for i in range(1, len(LINES)):
        name = "cta2_enter" if LINES[i][1] is None else ("emph1_flash" if LINES[i][1] == 7 else "trans1_swing")
        sfx.append((name, max(0, starts[i] - 0.05), 0.28))
    ins = ["-i", cut, "-i", top, "-loop", "1", "-t", str(total), "-i", card]
    amix = ["[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[voice]"]
    for k, (name, t, vol) in enumerate(sfx):
        ins += ["-i", os.path.join(KIT, name + ".mp3")]
        amix.append(f"[{3 + k}:a]volume={vol},adelay={int(t * 1000)}|{int(t * 1000)}[x{k}]")
    amix.append("[voice]" + "".join(f"[x{k}]" for k in range(len(sfx))) +
                f"amix=inputs={len(sfx) + 1}:normalize=0:duration=first[aout]")
    sh(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fc + amix),
        "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print("done", out, "cta_from", round(cta_from, 2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
