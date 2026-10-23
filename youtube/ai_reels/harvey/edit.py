#!/usr/bin/env python3
"""하비 릴스 편집: 얼굴 촬영 원본(전체 화면) + 그 위에 뜨는 화면 목업 → 1080×1920 완성본.

1. 얼굴이 화면 가운데 오게 확대·이동해서 자른다(좌우 대칭).
2. 0.3초 넘는 빈 간격을 잘라 낸다.
3. 대사 줄마다 overlay.html 장면을 투명 영상으로 렌더링해 몸 쪽(아래)에 띄운다.
4. 얼굴과 목업 사이에 짧은 자막(키워드는 노랑), 효과음은 시작과 CTA 만.

  python3 edit.py <작업폴더: source.mov, words.json> <출력.mp4>
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, "..", "..", "sfx", "kit")
W, H, FPS = 1080, 1920, 30
MIN_GAP, PAD = 0.30, 0.07
# 얼굴 맞춤: 원본에서 얼굴 가운데가 x≈682 라 오른쪽으로 치우쳐 있다. 864 폭으로 잘라 1.25배 확대하면 거의 가운데로 온다.
CROP = (864, 1536, 216, 150)          # 폭, 높이, x, y (원본 1080×1920 기준)
# 목업 층: overlay.html 의 카드 영역(y 130~1010)을 0.75배로 줄여 몸 쪽에 띄운다
OV_SCALE, OV_TOP = 0.75, 1075
CAP_Y = 1010                          # 자막 줄(턱 아래, 목업 위)

LINES = [  # (원본 시작 시각, 장면)
    (0.00, "repo"),    # 영업만 대신해 주는 클로드 에이전트가 나왔어요
    (4.54, "ask"),     # 뭘 파는지 원하는 고객만 알려 주면
    (6.92, "map"),     # 근처 가게 웹사이트 전부 읽고 … 골라 줘요
    (13.82, "mail"),   # 그 사이트에서 찾은 실제 정보로 메일을 써서
    (18.66, "reply"),  # 답장이 오면 … 승인만 하면 돼요
    (25.08, "plan"),   # 이미 쓰는 클로드 구독, 추가 API 비용 없음
    (31.14, "dash"),   # 대시보드에서 실시간
    (38.28, "cta"),    # 한 장 정리 + 팔로우·댓글 '영업' → DM
]
FIX = {"대신해주는": "대신해 주는", "알려주면": "알려 주면", "골라줘요.": "골라 줘요", "남겨주시면": "남겨 주시면",
       "보내드릴게요.": "보내 드릴게요", "영업": "'영업'", "영업만": "영업만"}
MERGE = [(["실시간", "으로"], "실시간으로"), (["장", "으로"], "장으로")]
KEY = ["영업만", "클로드 에이전트", "근처 가게", "제일 필요한", "실제 정보", "스팸처럼", "승인만", "구독으로", "API", "실시간으로", "한 장으로", "'영업'"]


def sh(cmd):
    subprocess.run(cmd, check=True)


def silences(src):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=noise=-35dB:d=0.2", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en))


def keep_spans(src, dur, first_word, last_word_end):
    spans, cur = [], max(0.0, first_word - PAD)
    for a, b in silences(src):
        if b - a < MIN_GAP or b <= cur:
            continue
        if a + PAD > cur:
            spans.append((cur, a + PAD))
        cur = b - PAD
    spans.append((cur, min(dur, last_word_end + 0.4)))
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
    ws = [dict(w, word=w["word"].strip()) for w in words]
    out, i = [], 0
    while i < len(ws):
        for seq, rep in MERGE:
            if [w["word"].rstrip(".") for w in ws[i:i + len(seq)]] == seq:
                out.append({"start": ws[i]["start"], "end": ws[i + len(seq) - 1]["end"], "word": rep})
                i += len(seq)
                break
        else:
            out.append(ws[i]); i += 1
    for w in out:
        w["word"] = FIX.get(w["word"], w["word"]).rstrip(".")
    return out


def chunks(words, line_starts):
    """줄 경계를 넘지 않게 3~9글자 묶음으로 자른다."""
    out, cur = [], []
    def line_of(t):
        return sum(1 for s in line_starts if t >= s - 0.05) - 1
    for w in words:
        if cur and (line_of(w["start"]) != line_of(cur[0]["start"])
                    or len("".join(x["word"] for x in cur + [w]).replace(" ", "")) > 9):
            out.append(cur); cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [(c[0]["start"], c[-1]["end"], " ".join(x["word"] for x in c)) for c in out]


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_ass(path, caps):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,IBM Plex Sans KR,84,&H00FFFFFF,&H00FFFFFF,&H000E0D0B,&H780E0D0B,-1,0,0,0,100,100,-1,0,1,6,4,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for i, (a, b, txt) in enumerate(caps):
        end = caps[i + 1][0] if i + 1 < len(caps) and caps[i + 1][0] - b < 0.5 else b + 0.15
        body = txt
        for k in sorted(KEY, key=len, reverse=True):
            if k in body:   # 키워드는 사이트의 노랑(#f2c866)
                body = body.replace(k, "{\\c&H66C8F2&}" + k + "{\\c&HFFFFFF&}", 1)
                break
        pop = "{\\fscx86\\fscy86\\t(0,90,\\fscx100\\fscy100)}"
        lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(end)},Cap,,0,0,0,,{{\\pos(540,{CAP_Y})}}{pop}{body}")
    open(path, "w").write(head + "\n".join(lines) + "\n")


def main(work, out):
    src = os.path.join(work, "source.mov")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]))
    words = [w for s in json.load(open(os.path.join(work, "words.json"))) for w in s["words"]]
    spans = keep_spans(src, dur, words[0]["start"], words[-1]["end"])
    m = mapper(spans)
    total = sum(b - a for a, b in spans)
    print("spans", len(spans), "length", round(total, 2), "from", round(dur, 2))

    # 1) 빈 간격 자르고 얼굴 가운데로 맞춘 원본 (30fps)
    cw, ch, cx, cy = CROP
    parts = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];"
                    for i, (a, b) in enumerate(spans))
    cat = "".join(f"[v{i}][a{i}]" for i in range(len(spans))) + f"concat=n={len(spans)}:v=1:a=1[v][a]"
    cut = os.path.join(work, "cut.mp4")
    sh(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex",
        parts + cat + f";[v]fps={FPS},crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos,setsar=1[vo]",
        "-map", "[vo]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", cut])

    # 2) 목업 장면 계획 → 투명 영상
    starts = [0.0] + [m(s) for s, _ in LINES[1:]] + [total]
    plan = [[sc, round(starts[i + 1] - starts[i], 3)] for i, (_, sc) in enumerate(LINES)]
    json.dump(plan, open(os.path.join(work, "plan.json"), "w"))
    ov = os.path.join(work, "overlay.mov")
    if not os.path.exists(ov) or os.environ.get("RERENDER"):
        sh(["node", os.path.join(HERE, "render_overlay.js"), os.path.join(work, "plan.json"), ov, str(FPS)])

    # 3) 합성: 얼굴 + 목업(줄여서 몸 쪽) + 자막
    caps = chunks(words_fixed(words), [s for s, _ in LINES])
    caps = [(m(a), m(b), t) for a, b, t in caps]
    ass = os.path.join(work, "caps.ass")
    write_ass(ass, caps)
    ow = int(W * OV_SCALE)
    oy = OV_TOP - int(130 * OV_SCALE)
    fc = [f"[1:v]scale={ow}:-1,format=rgba[ov]",
          f"[0:v][ov]overlay={(W - ow) // 2}:{oy}:format=auto[b]",
          f"[b]ass={ass}[vout]"]

    # 4) 소리: 목소리 + 효과음(시작, CTA 만)
    sfx = [("intro1_dodon", 0.0, 0.30), ("cta2_enter", max(0, starts[7] - 0.05), 0.26)]
    ins = ["-i", cut, "-i", ov]
    amix = ["[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[voice]"]
    for k, (name, t, vol) in enumerate(sfx):
        ins += ["-i", os.path.join(KIT, name + ".mp3")]
        amix.append(f"[{2 + k}:a]volume={vol},adelay={int(t * 1000)}|{int(t * 1000)}[x{k}]")
    amix.append("[voice]" + "".join(f"[x{k}]" for k in range(len(sfx))) +
                f"amix=inputs={len(sfx) + 1}:normalize=0:duration=first[aout]")
    sh(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fc + amix),
        "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print("done", out, "length", round(total, 2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
