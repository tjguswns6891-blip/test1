#!/usr/bin/env python3
"""본편 컷 편집본에서 구간을 골라 세로(9:16) 쇼츠·릴스 영상을 만드는 도구.

화면 구성 (1080×1920):
  위      제목 두 줄 + "투자 권유 아님" 한 줄
  가운데  사진 자료 (머리 위 벽 자리라 얼굴을 가리지 않는다)
  아래    인물 (원본에서 얼굴 주변을 세로로 잘라 확대)
  자막    턱 아래, 쇼츠·릴스 하단 버튼 영역보다 위

구간·제목·사진은 subs/shorts.json 에 적는다 (문구로 시작·끝을 찾는다).

사용 예:
  python3 shorts.py raw.cut.cuts.json raw.script.words.json ../subs/shorts.json -o shorts/
  python3 shorts.py ... --only B          # 하나만
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from autocut import find_ffmpeg
from compose import DISCLAIMER, FONT, ass_color, ass_time, find_phrase, highlight, render_panel, wrap_two
from transcribe import DEFAULT_FILLERS, build_cues, load_fixes, remap, separate, write_srt

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
BG = (17, 19, 24)
# 원본 1920×1080 에서 잘라 쓸 세로 영역 (얼굴이 가로 684~1265px 에서 움직임)
CROP_X, CROP_W = 555, 840
PERSON_H = round(1080 * W / CROP_W)          # 1389
PERSON_Y = H - PERSON_H                      # 531
IMG_BOX = (50, 410, 1030, 930)               # 사진 칸 (머리 꼭대기는 y≈950)
NOTE = DISCLAIMER                            # 제목 아래 작은 안내 문구 (빈 문자열이면 없음)
ACCENT = "#ffc53d"                           # 자막 숫자 강조색
FADE_H = 300                                 # 인물 영상 위쪽을 배경색으로 녹이는 높이
SUB_TOP = 0                                  # 0이면 자막을 아래쪽에, 아니면 이 y 에서 위쪽 정렬
FONT_BLACK = os.path.expanduser("~/.fonts/NotoSansCJKkr-Black.otf")
FONT_BOLD = os.path.expanduser("~/.fonts/NotoSansCJKkr-Bold.otf")


def norm(text):
    return "".join(c.lower() for c in text if c.isalnum())


def find_span(words, start_phrase, end_phrase, t_from=0.0):
    """시작 문구의 첫 단어 시작 ~ 끝 문구의 마지막 단어 끝. 앞뒤 여유는 이웃 단어에 닿지 않게 둔다."""
    ws = [w for w in words if w["start"] >= t_from]
    chars, owner = "", []
    for i, w in enumerate(ws):
        for c in norm(w["word"]):
            chars += c
            owner.append(i)
    a = chars.find(norm(start_phrase))
    if a < 0:
        raise SystemExit(f"시작 문구를 못 찾았어요: {start_phrase}")
    key = norm(end_phrase)
    b = chars.find(key, a)
    if b < 0:
        raise SystemExit(f"끝 문구를 못 찾았어요: {end_phrase}")
    i0, i1 = owner[a], owner[b + len(key) - 1]
    start, end = ws[i0]["start"], ws[i1]["end"]
    before = next((w["end"] for w in reversed(words) if w["end"] <= start - 0.01), 0.0)
    after = next((w["start"] for w in words if w["start"] >= end - 0.01 and w is not ws[i1]), end + 1.0)
    return max(start - 0.15, before + 0.03), min(end + 0.4, after - 0.05)


def title_overlay(lines, path):
    """위쪽 배경·제목·안내 문구, 그리고 인물 영상 위쪽 가장자리를 배경색으로 녹이는 그라데이션."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    top = Image.new("RGBA", (W, PERSON_Y), BG + (255,))
    glow = Image.new("RGBA", (W, PERSON_Y), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-200, -250, 700, 420), fill=(255, 90, 95, 60))
    top.alpha_composite(glow.filter(ImageFilter.GaussianBlur(110)))
    img.alpha_composite(top)
    if FADE_H > 1:
        fade = Image.new("L", (1, FADE_H))
        fade.putdata([int(255 * (1 - i / (FADE_H - 1)) ** 1.6) for i in range(FADE_H)])
        grad = Image.new("RGBA", (W, FADE_H), BG + (0,))
        grad.putalpha(fade.resize((W, FADE_H)))
        img.alpha_composite(grad, (0, PERSON_Y))
    d = ImageDraw.Draw(img)
    sizes, colors = [92, 108], [(255, 255, 255), (255, 197, 61)]
    y = 88
    for i, line in enumerate(lines):
        f = ImageFont.truetype(FONT_BLACK, sizes[min(i, 1)])
        while d.textlength(line, font=f) > W - 80:
            f = ImageFont.truetype(FONT_BLACK, f.size - 4)
        x = (W - d.textlength(line, font=f)) / 2
        d.text((x, y), line, font=f, fill=colors[min(i, 1)], stroke_width=6, stroke_fill=(8, 9, 12))
        y += int(f.size * 1.22)
    if NOTE:
        nf = ImageFont.truetype(FONT_BOLD, 28)
        d.text(((W - d.textlength(NOTE, font=nf)) / 2, y + 8), NOTE, font=nf, fill=(150, 156, 170))
    img.save(path)


def crop_for_box(src, dst, box_w, box_h):
    """세로로 긴 캡처는 위쪽(제목·점수·차트 부분)만 칸 비율로 잘라 크게 보이게 한다."""
    im = Image.open(src)
    if im.height > im.width and im.height / im.width > box_h / box_w * 1.15:   # 세로형 캡처만
        im = im.crop((0, 0, im.width, int(im.width * box_h / box_w)))
    im.save(dst)
    return dst


def write_ass(cues, path):
    cues = separate(cues)   # 화면에 두 줄이 겹쳐 뜨지 않게
    fs = 74
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
        "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{FONT},{fs},&H00FFFFFF,&H00FFFFFF,{ass_color('#111318')},&H80000000,-1,0,0,0,100,100,0,0,1,"
        f"7,2,{8 if SUB_TOP else 2},60,60,{SUB_TOP or 400},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for c in cues:
        end = max(c["end"] + 0.12, c["start"] + 0.5)
        lines.append(f"Dialogue: 1,{ass_time(c['start'])},{ass_time(end)},Sub,,0,0,0,,"
                     f"{{\\fad(60,40)\\fscx92\\fscy92\\t(0,120,\\fscx100\\fscy100)}}{highlight(wrap_two(c['text'], 14), ACCENT)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def build_short(name, cfg, words, files, ffmpeg, out_dir, fixes, script_dir):
    spans, t = [], 0.0
    for start_p, end_p in cfg["ranges"]:
        a, b = find_span(words, start_p, end_p, t)
        spans.append((max(0.0, a), b))
        t = b
    clip_words = remap(words, spans)
    duration = sum(b - a for a, b in spans)
    cues = build_cues(clip_words, 28, 4.5, 0.6, DEFAULT_FILLERS, fixes)   # 한 줄 14자, 두 줄까지

    plan = []
    for k, (img, phrase) in enumerate(cfg.get("images", [])):
        t0 = find_phrase(clip_words, phrase, 0, duration)
        if t0 is None:
            print(f"  ! {name}: '{phrase}' 문구를 못 찾아 {img} 건너뜀", file=sys.stderr)
            continue
        plan.append([os.path.join(script_dir, "img", img), max(0.0, t0 - 0.2)])
    plan.sort(key=lambda p: p[1])
    if plan:
        plan[0][1] = 0.0                                   # 첫 사진은 처음부터

    base = os.path.join(out_dir, f"short_{name}")
    write_srt(cues, base + ".srt")
    print(f"쇼츠 {name}: {duration:.1f}초 · 구간 {len(spans)}개 · 자막 {len(cues)}줄 · 사진 {len(plan)}장")

    with tempfile.TemporaryDirectory() as tmp:
        concat = os.path.join(tmp, "concat.txt")
        with open(concat, "w") as f:
            f.writelines(f"file '{os.path.abspath(x)}'\n" for x in files)
        title_png = os.path.join(tmp, "title.png")
        title_overlay(cfg["title"], title_png)
        ass = os.path.join(tmp, "subs.ass")
        write_ass(cues, ass)

        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-stats", "-y",
               "-f", "concat", "-safe", "0", "-i", concat,
               "-loop", "1", "-framerate", "30", "-t", f"{duration:.3f}", "-i", title_png]
        n = len(spans)
        chains = [f"[0:v]split={n}" + "".join(f"[vs{i}]" for i in range(n)),
                  f"[0:a]asplit={n}" + "".join(f"[as{i}]" for i in range(n))]
        for i, (a, b) in enumerate(spans):
            chains.append(f"[vs{i}]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
            chains.append(f"[as{i}]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
                          f"afade=t=in:d=0.04,afade=t=out:st={b - a - 0.08:.3f}:d=0.08[a{i}]")
        chains.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
        shown = min(PERSON_H, H - PERSON_Y)                  # 인물을 내리면 아래쪽은 잘린다
        chains.append(f"[vc]fps=30,crop={CROP_W}:1080:{CROP_X}:0,scale={W}:{PERSON_H}:flags=lanczos,"
                      f"crop={W}:{shown}:0:0,pad={W}:{H}:0:{PERSON_Y}:color=0x111318[bg]")
        chains.append("[bg][1:v]overlay=0:0:eof_action=pass[t0]")
        prev = "[t0]"
        bx1, by1, bx2, by2 = IMG_BOX
        for i, (src, t0) in enumerate(plan):
            t1 = plan[i + 1][1] + 0.3 if i + 1 < len(plan) else duration
            png = os.path.join(tmp, f"img{i}.png")
            cropped = crop_for_box(src, os.path.join(tmp, f"src{i}.png"), bx2 - bx1, by2 - by1)
            (pw, ph), pad = render_panel(cropped, bx2 - bx1, by2 - by1, png, 1.0)
            x = bx1 - pad + (bx2 - bx1 - (pw - 2 * pad)) // 2
            y = by1 - pad + (by2 - by1 - (ph - 2 * pad)) // 2
            dur = t1 - t0
            cmd += ["-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", png]
            idx = i + 2
            chains.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,"
                          f"fade=t=out:st={max(0, dur - 0.3):.3f}:d=0.3:alpha=1,"
                          f"setpts=PTS-STARTPTS+{t0:.3f}/TB[p{i}]")
            chains.append(f"{prev}[p{i}]overlay=x='{x}+60*max(0\\,1-(t-{t0:.3f})/0.3)':y={y}"
                          f":eof_action=pass:enable='between(t,{t0:.3f},{t1:.3f})'[o{i}]")
            prev = f"[o{i}]"
        chains.append(f"{prev}ass={ass}:fontsdir={os.path.expanduser('~/.fonts')}[out]")
        cmd += ["-filter_complex", ";".join(chains), "-map", "[out]", "-map", "[ac]",
                "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", base + ".mp4"]
        subprocess.run(cmd, check=True)
    print(f"  → {base}.mp4 ({os.path.getsize(base + '.mp4') / 1e6:.1f}MB)")


def main():
    global CROP_X, CROP_W, PERSON_H, PERSON_Y, IMG_BOX, NOTE, ACCENT, FADE_H, SUB_TOP
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cuts", help="autocut.py 가 만든 .cuts.json")
    p.add_argument("words", help="align_script.py 결과 (.script.words.json, 원본 시간 기준)")
    p.add_argument("config", help="쇼츠 구성 JSON (subs/shorts.json)")
    p.add_argument("--script", default=os.path.join(HERE, "..", "index.html"), help="사진 폴더 기준 (index.html 위치)")
    p.add_argument("--fix", help="자막 교정 파일")
    p.add_argument("--only", help="이 이름의 쇼츠만 (쉼표 구분)")
    p.add_argument("-o", "--out", default="shorts", help="출력 폴더")
    p.add_argument("--crop-x", type=int, default=CROP_X, help="원본에서 잘라 쓸 세로 영역의 왼쪽 x")
    p.add_argument("--crop-w", type=int, default=CROP_W, help="잘라 쓸 폭 (넓힐수록 인물이 작아짐)")
    p.add_argument("--person-y", type=int, default=PERSON_Y, help="인물 영상이 시작하는 y (내리면 아래가 잘림)")
    p.add_argument("--img-box", default=",".join(map(str, IMG_BOX)), help="사진 칸 x1,y1,x2,y2")
    p.add_argument("--note", default=NOTE, help="제목 아래 안내 문구 (빈 문자열이면 없음)")
    p.add_argument("--accent", default=ACCENT, help="자막 숫자 강조색")
    p.add_argument("--fade", type=int, default=FADE_H, help="인물 영상 위쪽을 배경색으로 녹이는 높이(px)")
    p.add_argument("--sub-top", type=int, default=0, help="자막을 이 y 부터 위쪽 정렬로 (사진 칸과 얼굴 사이에 둘 때)")
    args = p.parse_args()
    CROP_X, CROP_W, NOTE, ACCENT, FADE_H = args.crop_x, args.crop_w, args.note, args.accent, args.fade
    PERSON_H = round(1080 * W / CROP_W)
    SUB_TOP = args.sub_top
    PERSON_Y = args.person_y if args.person_y != H - round(1080 * W / 840) else H - PERSON_H
    IMG_BOX = tuple(int(v) for v in args.img_box.split(","))

    ffmpeg = find_ffmpeg()
    with open(args.cuts, encoding="utf-8") as f:
        scenes = json.load(f)["scenes"]
    base_dir = os.path.dirname(os.path.abspath(args.cuts))
    files = [s["file"] if os.path.isabs(s["file"]) else os.path.join(base_dir, os.path.basename(s["file"]))
             for s in scenes]
    segments = [seg for s in scenes for seg in s["segments"]]
    with open(args.words, encoding="utf-8") as f:
        words = remap(json.load(f)["words"], segments)      # 편집본 시간
    with open(args.config, encoding="utf-8") as f:
        config = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    fixes = load_fixes(args.fix) if args.fix else ()
    only = set(args.only.split(",")) if args.only else None
    os.makedirs(args.out, exist_ok=True)
    for name, cfg in config.items():
        if only and name not in only:
            continue
        build_short(name, cfg, words, files, ffmpeg, args.out, fixes, os.path.dirname(os.path.abspath(args.script)))


if __name__ == "__main__":
    main()
