#!/usr/bin/env python3
"""컷 편집본 위에 화면 녹화(B롤)를 덮고, 그동안 얼굴은 오른쪽 위 작은 창(PIP)으로 남기는 도구.

화면 녹화는 대본 문구로 자리를 잡는다: [녹화 파일, 시작 문구, 끝 문구].
녹화마다 조작한 부분(boxes.json, record.js 가 남김)을 16:9 로 잘라 1920×1080 에 꽉 채우고,
녹화가 말보다 짧으면 마지막 화면을 멈춰 둔다.

결과 영상과 함께 같은 시간축의 cuts.json 을 만들어, compose.py 로 자막을 그대로 얹을 수 있다.

사용 예:
  python3 broll.py ../raw/linalg/cut.cuts.json ../raw/linalg/raw.script.words.json ../linalg/broll.json \\
      --rec ../raw/linalg/rec -o ../raw/linalg/broll.mp4
  python3 compose.py ../raw/linalg/broll.cuts.json ../raw/linalg/raw.script.words.json ...
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

from autocut import find_ffmpeg
from compose import find_phrase, find_phrase_end
from transcribe import remap

W, H = 1920, 1080


def crop_box(box, vw, vh, min_w=1000):
    """조작한 영역을 화면 안으로 자르고 16:9 로 넓혀 (x, y, w, h)."""
    x0, y0 = max(0, box["x"]), max(0, box["y"])
    x1, y1 = min(vw, box["x"] + box["width"]), min(vh, box["y"] + box["height"])
    w, h = x1 - x0, y1 - y0
    w = max(w, h * 16 / 9, min_w)
    w = min(w, vw)
    h = w * 9 / 16
    if h > vh:
        h, w = vh, vh * 16 / 9
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x = min(max(0, cx - w / 2), vw - w)
    y = min(max(0, cy - h / 2), vh - h)
    even = lambda v: int(v) // 2 * 2
    return even(x), even(y), even(w), even(h)


def rounded_mask(size, r, path):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    m.save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cuts", help="autocut.py 의 .cuts.json (편집본 cut.mp4)")
    p.add_argument("words", help="align_script.py 결과 (원본 시간)")
    p.add_argument("plan", help='B롤 계획 JSON: {"clips": [[파일, 시작 문구, 끝 문구], ...], "crop": {파일: [x,y,w,h]}}')
    p.add_argument("--rec", required=True, help="녹화 폴더 (파일.webm, boxes.json)")
    p.add_argument("--face", default="705,180,600,600", help="편집본에서 얼굴을 자를 x,y,w,h")
    p.add_argument("--pip", default="1560,36,330", help="얼굴 창 x,y,한 변")
    p.add_argument("--lead", type=float, default=0.15, help="문구보다 이만큼 먼저 화면을 바꾼다(초)")
    p.add_argument("--tail", type=float, default=0.5, help="끝 문구 뒤로 이만큼 더 보여 준다(초)")
    p.add_argument("--crf", type=int, default=19)
    p.add_argument("--preset", default="fast")
    p.add_argument("-o", "--out", required=True)
    args = p.parse_args()

    ffmpeg = find_ffmpeg()
    with open(args.cuts, encoding="utf-8") as f:
        cuts = json.load(f)
    segments = [seg for s in cuts["scenes"] for seg in s["segments"]]
    duration = sum(b - a for a, b in segments)
    base_dir = os.path.dirname(os.path.abspath(args.cuts))
    src = cuts["scenes"][0]["file"]
    src = src if os.path.isabs(src) else os.path.join(base_dir, os.path.basename(src))
    with open(args.words, encoding="utf-8") as f:
        words = remap(json.load(f)["words"], segments)
    with open(args.plan, encoding="utf-8") as f:
        plan = json.load(f)
    with open(os.path.join(args.rec, "boxes.json"), encoding="utf-8") as f:
        boxes = json.load(f)
    vw, vh = boxes.get("_viewport", [1600, 900])

    # 1) 문구로 시간 잡기 (앞에서부터 차례로 찾는다)
    spans, t = [], 0.0
    for name, a, b in plan["clips"]:
        t0 = find_phrase(words, a, t, duration)
        if t0 is None:
            sys.exit(f"시작 문구를 못 찾았어요: {name} '{a}'")
        t1 = find_phrase_end(words, b, t0, duration)
        if t1 is None:
            sys.exit(f"끝 문구를 못 찾았어요: {name} '{b}'")
        spans.append([name, max(0.0, t0 - args.lead), min(duration, t1 + args.tail)])
        t = t1
    for i in range(len(spans) - 1):                # 다음 녹화와 겹치지 않게
        spans[i][2] = min(spans[i][2], spans[i + 1][1])

    fx, fy, fw, fh = (int(v) for v in args.face.split(","))
    px, py, ps = (int(v) for v in args.pip.split(","))
    with tempfile.TemporaryDirectory() as tmp:
        mask = os.path.join(tmp, "mask.png")
        rounded_mask((ps, ps), ps // 7, mask)
        ring = os.path.join(tmp, "ring.png")
        im = Image.new("RGBA", (ps + 12, ps + 12), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, ps + 11, ps + 11), ps // 7 + 6, fill=(255, 255, 255, 235))
        im.save(ring)

        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-stats", "-y", "-i", src, "-loop", "1", "-i", mask,
               "-loop", "1", "-i", ring]
        chains = ["[0:v]split=2[bg][fc]"]
        prev = "[bg]"
        starts = boxes.get("_start", {})       # record.js 가 남긴, 페이지가 준비되고 조작이 시작된 시각
        for i, (name, t0, t1) in enumerate(spans):
            cmd += ["-ss", f"{starts.get(name, 0):.2f}", "-i", os.path.join(args.rec, name + ".webm")]
            k = i + 3
            x, y, w, h = plan.get("crop", {}).get(name) or crop_box(boxes[name], vw, vh)
            dur = t1 - t0
            # 16:9 가 아니면 높이(또는 폭)에 맞추고 남는 곳은 사이트 배경색으로 채운다
            fit = (f"scale={W}:{H}:flags=lanczos" if abs(w / h - W / H) < 0.02 else
                   f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
                   f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={plan.get('bg', '0xF4F5F8')}")
            chains.append(f"[{k}:v]crop={w}:{h}:{x}:{y},{fit},setsar=1,fps=30,"
                          f"tpad=stop_mode=clone:stop_duration=600,trim=0:{dur:.3f},"
                          f"setpts=PTS-STARTPTS+{t0:.3f}/TB,fade=t=in:st={t0:.3f}:d=0.2:alpha=1,"
                          f"format=yuva420p[c{i}]")
            chains.append(f"{prev}[c{i}]overlay=eof_action=pass:enable='between(t,{t0:.3f},{t1:.3f})'[v{i}]")
            prev = f"[v{i}]"
        on = "+".join(f"between(t,{t0:.3f},{t1:.3f})" for _, t0, t1 in spans) or "0"
        chains.append(f"[fc]crop={fw}:{fh}:{fx}:{fy},scale={ps}:{ps},format=rgba[fs]")
        chains.append("[1:v]format=gray[m]")
        chains.append("[fs][m]alphamerge[face]")
        chains.append(f"{prev}[2:v]overlay={px - 6}:{py - 6}:shortest=0:enable='{on}'[r]")
        chains.append(f"[r][face]overlay={px}:{py}:enable='{on}',format=yuv420p[out]")
        graph = os.path.join(tmp, "graph.txt")
        with open(graph, "w") as f:
            f.write(";\n".join(chains))
        cmd += ["-filter_complex_script", graph, "-map", "[out]", "-map", "0:a", "-t", f"{duration:.3f}",
                "-c:v", "libx264", "-crf", str(args.crf), "-preset", args.preset, "-c:a", "copy",
                "-movflags", "+faststart", args.out]
        for name, t0, t1 in spans:
            print(f"  {t0:6.1f}–{t1:6.1f}s  {name}")
        subprocess.run(cmd, check=True)

    out_cuts = dict(cuts)
    out_cuts["scenes"] = [dict(cuts["scenes"][0], file=os.path.abspath(args.out),
                               segments=[seg for s in cuts["scenes"] for seg in s["segments"]])]
    path = os.path.splitext(args.out)[0] + ".cuts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out_cuts, f, ensure_ascii=False, indent=1)
    print(f"완성: {args.out}  (자막용 컷 기록: {path})")


if __name__ == "__main__":
    main()
