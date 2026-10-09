#!/usr/bin/env python3
"""컷 편집본에 자막과 장면별 사진 자료를 얹어 완성 영상을 만드는 도구.

  · autocut.py 가 만든 장면 파일들을 이어 붙이고
  · align_script.py 결과(대본 장면 id가 붙은 단어)로 편집본에서 각 장면이 언제인지 찾고
  · 대본(index.html)에 장면마다 적힌 사진을 얼굴 양옆 빈자리에 번갈아 띄우고
  · 자막(숫자 강조)과 "투자 권유 아님" 고정 문구를 입힌다.

사용 예:
  python3 compose.py raw.cut.cuts.json raw.script.words.json -o final.mp4 --cues ../subs/image_cues.json
  python3 compose.py raw.cut.cuts.json raw.script.words.json -o preview.mp4 --preview   # 720p 빠른 확인용

사진 자리는 기본값이 1920×1080 화면에서 얼굴이 가로 684~1265px 에 있는 촬영본 기준이다.
구도가 바뀌면 --left / --right 로 사진 칸(x1,x2)을 바꾼다.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

from autocut import find_ffmpeg
from transcribe import DEFAULT_FILLERS, build_cues, load_fixes, remap, separate, shown_until, write_srt

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCRIPT = os.path.join(HERE, "..", "index.html")
W, H = 1920, 1080
VIDEO_EXT = (".mp4", ".mov", ".webm")
BG = (17, 19, 24)                 # #111318
BORDER = (58, 64, 80)
DISCLAIMER = "투자 권유 아님 · 과거 데이터 기반 정보"
FONT = "Noto Sans CJK KR"


def ass_color(hex_rgb, alpha=0):
    r, g, b = (int(hex_rgb[i:i + 2], 16) for i in (1, 3, 5))
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


UP, DOWN, ACCENT = "#ff5a5f", "#4c8dff", "#ffc53d"
NUMBER = re.compile(r"[−+-]?\d[\d.,]*(?:%p|%포인트|%|달러|점|배|년|개월|종목|개)?")


def highlight(text, accent=ACCENT):
    """숫자는 강조색, 마이너스 숫자는 하락색, 플러스 숫자는 상승색."""
    def color(m):
        tok = m.group(0)
        c = DOWN if tok[0] in "−-" else UP if tok[0] == "+" else accent
        return f"{{\\c{ass_color(c)}}}{tok}{{\\c&H00FFFFFF}}"
    return NUMBER.sub(color, text.replace("{", "(").replace("}", ")"))


def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def wrap_two(text, per_line):
    """한 줄에 per_line 글자를 넘으면 가운데에 가장 가까운 띄어쓰기에서 두 줄로 나눈다."""
    if len(text) <= per_line or " " not in text:
        return text
    mid = len(text) / 2
    cut = min((i for i, c in enumerate(text) if c == " "), key=lambda i: abs(i - mid))
    return text[:cut] + "\\N" + text[cut + 1:]


def write_ass(cues, duration, path, scale, note=DISCLAIMER, accent=ACCENT, per_line=0, box=False):
    """box=True 면 자막 뒤에 반투명 어두운 띠를 깐다 (흰 화면 녹화 위에서도 읽히게)."""
    cues = separate(cues)   # 화면에 두 줄이 겹쳐 뜨지 않게
    fs, outline, margin = round(58 * scale), round(4 * scale, 1), round(54 * scale)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {round(W * scale)}", f"PlayResY: {round(H * scale)}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        (f"Style: Sub,{FONT},{fs},&H00FFFFFF,&H00FFFFFF,&H33111318,&H33111318,-1,0,0,0,100,100,0,0,3,"
         f"{round(12 * scale)},0,2,{margin},{margin},{margin},1" if box else
         f"Style: Sub,{FONT},{fs},&H00FFFFFF,&H00FFFFFF,{ass_color('#111318')},&H80000000,-1,0,0,0,100,100,0,0,1,"
         f"{outline},{round(2 * scale, 1)},2,{margin},{margin},{margin},1"),
        f"Style: Note,{FONT},{round(24 * scale)},&H40FFFFFF,&H40FFFFFF,&H80111318,&H00000000,-1,0,0,0,100,100,0,0,1,"
        f"{round(2 * scale, 1)},0,7,{round(40 * scale)},{round(40 * scale)},{round(30 * scale)},1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    if note:
        lines.append(f"Dialogue: 0,{ass_time(0)},{ass_time(duration)},Note,,0,0,0,,{note}")
    # 자막 자리 고정: 아래 가운데에 \pos 로 못박아, 한 줄·두 줄이어도 아래 기준선이 같고 다른 글자와 겹쳐도 밀리지 않는다
    pos = f"\\an2\\pos({round(W * scale / 2)},{round(H * scale) - margin})"
    for i, c in enumerate(cues):
        end = shown_until(cues, i, 0.15, 0.6)
        lines.append(f"Dialogue: 1,{ass_time(c['start'])},{ass_time(end)},Sub,,0,0,0,,"
                     f"{{{pos}\\fad(80,60)}}{highlight(wrap_two(c['text'], per_line) if per_line else c['text'], accent)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def scene_images(script_path, part="part-main"):
    with open(script_path, encoding="utf-8") as f:
        src = f.read()
    m = re.search(rf'<section[^>]*id="{part}".*?(?=<section|\Z)', src, re.S)
    out = {}
    for sid, body in re.findall(r'<article class="scene" id="([^"]+)"(.*?)</article>', m.group(0), re.S):
        out[sid] = [os.path.join(os.path.dirname(script_path), html.unescape(p))
                    for p in re.findall(r'<img src="([^"]+)"', body)]
    return out


def scene_ranges(words, order, duration):
    """편집본에서 장면마다 첫 단어가 나오는 시각으로 장면 구간을 나눈다."""
    first = {}
    for w in words:
        if w.get("scene") and w["scene"] not in first:
            first[w["scene"]] = w["start"]
    starts = [(sid, first[sid]) for sid in order if sid in first]
    ranges = []
    for i, (sid, t) in enumerate(starts):
        start = 0.0 if i == 0 else max(0.0, t - 0.3)
        end = starts[i + 1][1] - 0.3 if i + 1 < len(starts) else duration
        ranges.append((sid, start, end))
    return ranges


def render_panel(src, box_w, box_h, dst, scale):
    """사진을 칸 크기에 맞추고 둥근 모서리·테두리·그림자를 입힌 PNG로 만든다."""
    img = Image.open(src).convert("RGB")
    ratio = min(box_w / img.width, box_h / img.height)
    iw, ih = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((iw, ih), Image.LANCZOS)
    r, pad, bw = round(18 * scale), round(24 * scale), max(2, round(3 * scale))
    canvas = Image.new("RGBA", (iw + 2 * pad, ih + 2 * pad), (0, 0, 0, 0))
    shadow = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle((pad, pad + round(6 * scale), pad + iw, pad + ih + round(6 * scale)),
                                             r, fill=150)
    canvas.putalpha(shadow.filter(ImageFilter.GaussianBlur(pad // 2)))   # 검은 그림자
    mask = Image.new("L", (iw, ih), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, iw - 1, ih - 1), r, fill=255)
    framed = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    framed.paste(img, (0, 0), mask)
    ImageDraw.Draw(framed).rounded_rectangle((0, 0, iw - 1, ih - 1), r, outline=BORDER + (255,), width=bw)
    canvas.alpha_composite(framed, (pad, pad))
    canvas.save(dst)
    return canvas.size, pad


def find_phrase(words, phrase, t_from, t_to):
    """[t_from, t_to) 안에서 문구를 말하기 시작하는 시각. 못 찾으면 None."""
    key = "".join(c.lower() for c in phrase if c.isalnum())
    ws = [w for w in words if t_from <= w["start"] < t_to]
    chars, owner = "", []
    for i, w in enumerate(ws):
        for c in w["word"]:
            if c.isalnum():
                chars += c.lower()
                owner.append(i)
    at = chars.find(key)
    return None if at < 0 or not key else ws[owner[at]]["start"]


def find_phrase_end(words, phrase, t_from, t_to):
    """[t_from, t_to) 안에서 문구를 다 말한 시각. 못 찾으면 None."""
    key = "".join(c.lower() for c in phrase if c.isalnum())
    ws = [w for w in words if t_from <= w["start"] < t_to]
    chars, owner = "", []
    for i, w in enumerate(ws):
        for c in w["word"]:
            if c.isalnum():
                chars += c.lower()
                owner.append(i)
    at = chars.find(key)
    return None if at < 0 or not key else ws[owner[at + len(key) - 1]]["end"]


def face_intervals(files, step=0.5, min_len=2.0, bridge=3.0):
    """이어 붙인 장면 파일들에서 얼굴이 보이는 시간 구간. 신발 클로즈업처럼 얼굴이 없는 컷을 가려낸다."""
    import cv2
    front = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    prof = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    hits, offset = [], 0.0
    for path in files:
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        f = 0
        while f < n:
            cap.set(cv2.CAP_PROP_POS_FRAMES, f)
            ok, img = cap.read()
            if not ok:
                break
            g = cv2.cvtColor(cv2.resize(img, (640, 360)), cv2.COLOR_BGR2GRAY)
            found = (len(front.detectMultiScale(g, 1.1, 5, minSize=(40, 40))) or
                     len(prof.detectMultiScale(g, 1.1, 5, minSize=(40, 40))) or
                     len(prof.detectMultiScale(cv2.flip(g, 1), 1.1, 5, minSize=(40, 40))))
            if found:
                hits.append(offset + f / fps)
            f += max(1, int(fps * step))
        offset += n / fps
        cap.release()
    spans = []
    for t in hits:
        if spans and t - spans[-1][1] <= bridge:
            spans[-1][1] = t
        else:
            spans.append([t, t])
    return [(a - step / 2, b + step / 2) for a, b in spans if b - a + step >= min_len]


def gate_to_faces(plan, faces, min_show=1.5):
    """옆 칸 사진은 얼굴이 보이는 컷에서만 띄운다 (클로즈업 컷에서 신발을 가리지 않게)."""
    out = []
    for o in plan:
        if o.get("full"):
            out.append(o)
            continue
        best = None
        for a, b in faces:
            lo, hi = max(o["t0"], a), min(o["t1"], b)
            if hi - lo >= min_show:
                best = (lo, hi)
                break
        if best:
            out.append({**o, "t0": best[0], "t1": best[1]})
        else:
            print(f"  · {os.path.basename(o['src'])} 은 얼굴 없는 컷이라 옆 칸에 띄우지 않음", file=sys.stderr)
    return out


def plan_overlays(ranges, images, cues, words, script_dir, left, right, top, bottom, sides="both"):
    """장면 안에서 사진을 차례로 왼쪽·오른쪽에 번갈아 띄운다. 같은 쪽에 다음 사진이 오면 바뀐다.
    cues 에 장면별 (사진, 등장 문구)가 있으면 그 문구를 말할 때, 없으면 장면을 고르게 나눠 띄운다.
    cue 가 [사진, 시작 문구, "full", 끝 문구] 이면 끝 문구를 다 말할 때까지 사진이 화면 전체를 덮는다
    (인물은 가리고 목소리만). 끝 문구가 없으면 다음 사진이나 장면 끝까지."""
    plan = []
    for n, (sid, start, end) in enumerate(ranges):
        if sid in cues:
            items, fulls = [], []
            for cue in cues[sid]:
                name, phrase = cue[0], cue[1]
                t = find_phrase(words, phrase, start, end)
                if t is None:
                    print(f"  ! {sid}: '{phrase}' 문구를 찾지 못해 {name} 은 건너뜀", file=sys.stderr)
                    continue
                path = os.path.join(script_dir, "img", name)
                if len(cue) > 2 and cue[2] == "full":
                    until = find_phrase_end(words, cue[3], t, end) if len(cue) > 3 else None
                    if len(cue) > 3 and until is None:
                        print(f"  ! {sid}: 끝 문구 '{cue[3]}' 를 못 찾아 {name} 은 다음 사진까지 풀화면", file=sys.stderr)
                    fulls.append([path, max(start, t - 0.25), until + 0.25 if until else None])
                else:
                    items.append((path, max(start, t - 0.2)))
            starts = sorted([f[1] for f in fulls] + [i[1] for i in items])
            for f in fulls:
                if f[2] is None:
                    f[2] = next((x for x in starts if x > f[1]), end) + 0.1
                plan.append({"src": f[0], "full": True, "t0": f[1], "t1": min(f[2], end)})
        else:
            imgs = images.get(sid, [])
            slot = (end - start) / max(1, len(imgs))
            items = [(path, start + k * slot + (0.4 if k == 0 else 0)) for k, path in enumerate(imgs)]
        step = 2 if sides == "both" else 1   # 같은 칸에 다음 사진이 오면 바뀐다
        for k, (path, t0) in enumerate(items):
            side = (k + n) % 2 if sides == "both" else (0 if sides == "left" else 1)
            t1 = items[k + step][1] + 0.3 if k + step < len(items) else end
            plan.append({"src": path, "side": side, "t0": t0, "t1": min(t1, end),
                         "box": left if side == 0 else right, "top": top, "bottom": bottom})
    plan.sort(key=lambda o: o.get("full", False))    # 풀화면은 옆 칸 사진 위에 그린다
    return plan


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cuts", help="autocut.py 가 만든 .cuts.json")
    p.add_argument("words", help="align_script.py 결과 (.script.words.json, 원본 시간 기준)")
    p.add_argument("--script", default=DEFAULT_SCRIPT, help="대본 index.html (장면별 사진 목록)")
    p.add_argument("--fix", help="자막 교정 파일 (transcribe.py --fix 와 같은 형식)")
    p.add_argument("--cues", help="장면별 사진 등장 문구 JSON (예: subs/image_cues.json)")
    p.add_argument("--left", default="40,665", help="왼쪽 사진 칸 x1,x2 (1920 기준)")
    p.add_argument("--right", default="1280,1890", help="오른쪽 사진 칸 x1,x2 (1920 기준)")
    p.add_argument("--top", type=int, default=110, help="사진 칸 위쪽 y")
    p.add_argument("--bottom", type=int, default=860, help="사진 칸 아래쪽 y (자막과 겹치지 않게)")
    p.add_argument("--max-chars", type=int, default=28)
    p.add_argument("--preview", action="store_true", help="720p·빠른 인코딩으로 미리보기")
    p.add_argument("--limit", type=float, help="앞에서부터 이 초까지만 렌더 (확인용)")
    p.add_argument("--sides", choices=["both", "left", "right"], default="both", help="옆 칸 사진을 넣을 쪽")
    p.add_argument("--face-gate", action="store_true", help="얼굴이 보이는 컷에서만 옆 칸 사진을 띄운다")
    p.add_argument("--lines", type=int, choices=[1, 2], default=1, help="자막 최대 줄 수")
    p.add_argument("--line-chars", type=int, default=24, help="두 줄 자막일 때 한 줄 글자 수")
    p.add_argument("--note", default=DISCLAIMER, help="화면 왼쪽 위 고정 문구 (빈 문자열이면 없음)")
    p.add_argument("--accent", default=ACCENT, help="자막 숫자 강조색")
    p.add_argument("--full-inset", type=float, default=1.0,
                   help="풀화면 사진 크기 비율 (1보다 작으면 위에 두고 아래를 자막 자리로 비움, 예: 0.82)")
    p.add_argument("--sub-box", action="store_true", help="자막 뒤에 반투명 어두운 띠 (밝은 화면 녹화가 많을 때)")
    p.add_argument("--crf", type=int, default=19)
    p.add_argument("--preset", default="medium")
    p.add_argument("-o", "--out", default="final.mp4")
    args = p.parse_args()

    ffmpeg = find_ffmpeg()
    with open(args.cuts, encoding="utf-8") as f:
        scenes = json.load(f)["scenes"]
    base_dir = os.path.dirname(os.path.abspath(args.cuts))
    files = [s["file"] if os.path.isabs(s["file"]) else os.path.join(base_dir, os.path.basename(s["file"]))
             for s in scenes]
    for fpath in files:
        if not os.path.exists(fpath):
            sys.exit(f"장면 파일이 없어요: {fpath}  (autocut.py 를 --dry-run 없이 먼저 실행하세요)")
    segments = [seg for s in scenes for seg in s["segments"]]
    duration = sum(b - a for a, b in segments)

    with open(args.words, encoding="utf-8") as f:
        words = json.load(f)["words"]
    words = remap(words, segments)
    last = None
    for w in words:                      # 장면 id 없는 단어는 앞 단어의 장면으로
        w["scene"] = w.get("scene") or last
        last = w["scene"]

    fixes = load_fixes(args.fix) if args.fix else ()
    if args.lines == 2:
        cues = build_cues(words, args.line_chars * 2, 7.0, 0.7, DEFAULT_FILLERS, fixes)
    else:
        cues = build_cues(words, args.max_chars, 6.0, 0.7, DEFAULT_FILLERS, fixes)
    stem = os.path.splitext(args.out)[0]
    write_srt(cues, stem + ".srt")

    images = scene_images(args.script)
    ranges = scene_ranges(words, list(images), duration)
    scale = 2 / 3 if args.preview else 1.0
    L = [int(v) for v in args.left.split(",")]
    R = [int(v) for v in args.right.split(",")]
    cues_cfg = {}
    if args.cues:
        with open(args.cues, encoding="utf-8") as f:
            cues_cfg = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    plan = plan_overlays(ranges, images, cues_cfg, words, os.path.dirname(args.script), L, R, args.top, args.bottom,
                         args.sides)
    if args.face_gate:
        faces = face_intervals(files)
        print(f"얼굴이 보이는 구간 {len(faces)}곳 (합계 {sum(b - a for a, b in faces):.0f}초)")
        plan = gate_to_faces(plan, faces)

    print(f"편집본 {int(duration // 60)}분 {duration % 60:04.1f}초 · 자막 {len(cues)}줄 · 사진 {len(plan)}장")
    for sid, a, b in ranges:
        names = [f"{os.path.basename(x['src'])}@{x['t0']:.0f}{'F' if x.get('full') else 'LR'[x['side']]}"
                 for x in plan if a <= x["t0"] < b]
        print(f"  {sid:4s} {a:6.1f}–{b:6.1f}s  {', '.join(names)}")

    with tempfile.TemporaryDirectory() as tmp:
        ass = os.path.join(tmp, "subs.ass")
        write_ass(cues, duration, ass, scale, args.note, args.accent, args.line_chars if args.lines == 2 else 0,
                  args.sub_box)
        concat = os.path.join(tmp, "concat.txt")
        with open(concat, "w") as f:
            f.writelines(f"file '{os.path.abspath(x)}'\n" for x in files)

        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-stats", "-y",
               "-f", "concat", "-safe", "0", "-i", concat]
        chains, prev = [], "[0:v]"
        if args.preview:
            chains.append(f"[0:v]scale={round(W * scale)}:-2[base]")
            prev = "[base]"
        slide = round(50 * scale)
        n_in = [0]                                             # 마지막 입력 번호 (0 은 원본)

        def add_input(*opts):
            n_in[0] += 1
            cmd.extend(opts)
            return n_in[0]

        def clip_chain(path, w, h, dur, label, mask=None):
            """모션 카드(mp4)를 w×h 로 맞추고, 말보다 짧으면 마지막 화면을 멈춰 dur 초로 만든다."""
            k = add_input("-i", path)
            c = (f"[{k}:v]scale={w}:{h}:flags=lanczos,setsar=1,fps=30,"
                 f"tpad=stop_mode=clone:stop_duration=600,trim=0:{dur:.3f},setpts=PTS-STARTPTS,format=rgba")
            if mask:
                m = add_input("-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", mask)
                chains.append(c + f"[cv{label}]")
                chains.append(f"[{m}:v]format=gray,scale={w}:{h}[cm{label}]")
                chains.append(f"[cv{label}][cm{label}]alphamerge[{label}]")
            else:
                chains.append(c + f"[{label}]")

        for i, o in enumerate(plan, 1):
            video = o["src"].lower().endswith(VIDEO_EXT)
            still = os.path.splitext(o["src"])[0] + ".png" if video else o["src"]
            dur = o["t1"] - o["t0"]
            if o.get("full"):                                  # 화면 전체를 사진으로 덮는다
                png = os.path.join(tmp, f"img{i:02d}.png")
                card = Image.open(still).convert("RGB")
                fw, fh = round(W * scale), round(H * scale)
                if video:
                    clip_chain(o["src"], fw, fh, dur, f"m{i}")
                    chains.append(f"[m{i}]fade=t=in:st=0:d=0.3:alpha=1,"
                                  f"fade=t=out:st={max(0, dur - 0.3):.3f}:d=0.3:alpha=1,"
                                  f"setpts=PTS-STARTPTS+{o['t0']:.3f}/TB[p{i}]")
                else:
                    if args.full_inset < 1:          # 카드를 줄여 위에 두고, 아래는 자막 자리로 비운다
                        frame = Image.new("RGB", (fw, fh), card.getpixel((4, 4)))
                        cw, ch = round(fw * args.full_inset), round(fh * args.full_inset)
                        frame.paste(card.resize((cw, ch), Image.LANCZOS), ((fw - cw) // 2, round(fh * 0.025)))
                        frame.save(png)
                    else:
                        card.resize((fw, fh), Image.LANCZOS).save(png)
                    k = add_input("-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", png)
                    chains.append(
                        f"[{k}:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,"
                        f"fade=t=out:st={max(0, dur - 0.3):.3f}:d=0.3:alpha=1,setpts=PTS-STARTPTS+{o['t0']:.3f}/TB[p{i}]")
                chains.append(f"{prev}[p{i}]overlay=0:0:eof_action=pass"
                              f":enable='between(t,{o['t0']:.3f},{o['t1']:.3f})'[v{i}]")
                prev = f"[v{i}]"
                continue
            x1, x2 = (round(v * scale) for v in o["box"])
            top, bottom = round(o["top"] * scale), round(o["bottom"] * scale)
            png = os.path.join(tmp, f"img{i:02d}.png")
            (pw, ph), pad = render_panel(still, x2 - x1, bottom - top, png, scale)
            x = x1 - pad + (x2 - x1 - (pw - 2 * pad)) // 2
            y = top - pad + (bottom - top - (ph - 2 * pad)) // 2
            k = add_input("-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", png)
            panel = f"[{k}:v]format=rgba"
            if video:                       # 테두리·그림자 PNG 안쪽에 움직이는 카드를 둥근 모서리로 얹는다
                iw, ih = pw - 2 * pad, ph - 2 * pad
                bw = max(2, round(3 * scale))
                mask = os.path.join(tmp, f"mask{i:02d}.png")
                mk = Image.new("L", (iw - 2 * bw, ih - 2 * bw), 0)
                ImageDraw.Draw(mk).rounded_rectangle((0, 0, mk.width - 1, mk.height - 1), round(16 * scale), fill=255)
                mk.save(mask)
                clip_chain(o["src"], iw - 2 * bw, ih - 2 * bw, dur, f"m{i}", mask)
                chains.append(f"{panel}[pb{i}]")
                chains.append(f"[pb{i}][m{i}]overlay={pad + bw}:{pad + bw}:shortest=1[pc{i}]")
                panel = f"[pc{i}]format=rgba"
            direction = -1 if o["side"] == 0 else 1          # 바깥쪽에서 안쪽으로 밀려 들어온다
            chains.append(
                f"{panel},fade=t=in:st=0:d=0.35:alpha=1,"
                f"fade=t=out:st={max(0, dur - 0.3):.3f}:d=0.3:alpha=1,setpts=PTS-STARTPTS+{o['t0']:.3f}/TB[p{i}]")
            chains.append(
                f"{prev}[p{i}]overlay=x='{x}+{direction * slide}*max(0\\,1-(t-{o['t0']:.3f})/0.35)':y={y}"
                f":eof_action=pass:enable='between(t,{o['t0']:.3f},{o['t1']:.3f})'[v{i}]")
            prev = f"[v{i}]"
        fontsdir = os.path.expanduser("~/.fonts")
        chains.append(f"{prev}ass={ass}:fontsdir={fontsdir}[out]")
        cmd += ["-filter_complex", ";".join(chains), "-map", "[out]", "-map", "0:a",
                "-c:v", "libx264", "-crf", str(28 if args.preview else args.crf),
                "-preset", "veryfast" if args.preview else args.preset, "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart"]
        if args.limit:
            cmd += ["-t", f"{args.limit:.3f}"]
        cmd.append(args.out)
        subprocess.run(cmd, check=True)
    print(f"완성: {args.out}  (자막 파일: {stem}.srt)")


if __name__ == "__main__":
    main()
