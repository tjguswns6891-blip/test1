#!/usr/bin/env python3
"""촬영 원본에서 무음 구간(과 선택적으로 "음·어" 같은 말버릇)을 잘라내는 컷 편집 도구.

사용 예:
  python3 autocut.py raw.mp4                         # raw.cut.mp4 생성
  python3 autocut.py raw.mp4 --dry-run               # 자를 구간만 미리 보기
  python3 autocut.py raw.mp4 --scene-gap 3           # 3초 넘게 쉰 곳에서 장면 파일로 나누기
  python3 autocut.py raw.mp4 --transcript words.json # 말버릇까지 제거 (Whisper 단어 타임스탬프)
  python3 autocut.py raw.mp4 --cut-file raw.retakes.json   # retakes.py 가 찾은 NG 테이크도 제거

ffmpeg 위치: 환경변수 FFMPEG → PATH의 ffmpeg → pip 패키지 imageio-ffmpeg 순서로 찾는다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# "그·저"는 "그 뒤", "저 종목"처럼 실제 말로 더 자주 쓰여서 기본 목록에서 뺐다. 필요하면 --fillers 로 추가.
DEFAULT_FILLERS = ["음", "어", "아", "으", "엄", "흠", "음...", "어...", "뭐지"]


def find_ffmpeg():
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg를 찾을 수 없어요. `pip install imageio-ffmpeg` 로 설치하세요.")


def probe(ffmpeg, src):
    """길이(초), 오디오/비디오 스트림 유무, 영상 프레임 속도를 돌려준다."""
    err = subprocess.run([ffmpeg, "-hide_banner", "-i", src], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    if not m:
        sys.exit(f"영상 길이를 읽지 못했어요: {src}")
    h, mi, s = m.groups()
    fps = re.search(r"Video:.*?, ([\d.]+) fps", err)
    return int(h) * 3600 + int(mi) * 60 + float(s), "Audio:" in err, "Video:" in err, fps and fps.group(1)


# 이어 붙인 영상은 프레임 속도 정보가 없어 ffmpeg이 25fps로 내보내며 프레임을 버린다.
# 원본 속도로 고정하되, NTSC 계열은 정확한 분수로 바꾼다.
NTSC = {"23.98": "24000/1001", "23.976": "24000/1001", "29.97": "30000/1001", "59.94": "60000/1001"}


def detect_silence(ffmpeg, src, noise_db, min_silence):
    cmd = [ffmpeg, "-hide_banner", "-nostats", "-i", src, "-vn",
           "-af", f"silencedetect=n={noise_db}dB:d={min_silence}", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", err)]
    out = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None  # 파일 끝까지 무음이면 end가 없다
        out.append((max(0.0, s), e))
    return out


def load_filler_spans(path, fillers):
    """Whisper verbose_json(words 또는 segments[].words) 또는 [{word,start,end}] 목록에서 말버릇 구간을 뽑는다."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        words = data.get("words") or [w for seg in data.get("segments", []) for w in seg.get("words", [])]
    else:
        words = data
    norm = {f.strip(" .,!?~…") for f in fillers}
    spans = []
    for w in words:
        token = str(w.get("word", w.get("text", ""))).strip(" .,!?~…")
        if token in norm:
            spans.append((float(w["start"]), float(w["end"]), token))
    return spans


def speech_gaps(path, duration, min_gap):
    """받아쓰기 단어 사이가 min_gap초보다 긴 구간 (말 없이 화면으로 보여주는 장면)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    words = data.get("words") if isinstance(data, dict) else data
    gaps, prev = [], 0.0
    for w in words:
        if w["start"] - prev > min_gap:
            gaps.append((prev, w["start"]))
        prev = max(prev, w["end"])
    if duration - prev > min_gap:
        gaps.append((prev, duration))
    return gaps


def build_keeps(duration, silences, fillers, pad, min_keep, merge_gap):
    """잘라낼 구간을 모아 남길 구간 목록을 만든다. 무음 앞뒤로 pad초씩 여유를 남긴다."""
    cuts = []
    for s, e in silences:
        e = duration if e is None else e
        a, b = s + pad, e - pad
        if b - a > 0.05:
            cuts.append((a, b, "silence", e - s))
    for s, e, tok in fillers:
        cuts.append((s, e, tok if tok.startswith("ng:") else f"filler:{tok}", e - s))
    cuts.sort()

    keeps, t = [], 0.0
    for a, b, _, _ in cuts:
        if a > t:
            keeps.append([t, a])
        t = max(t, b)
    if t < duration:
        keeps.append([t, duration])

    merged = []
    for seg in keeps:
        if merged and seg[0] - merged[-1][1] < merge_gap:
            merged[-1][1] = seg[1]
        else:
            merged.append(seg)
    return [(round(a, 3), round(b, 3)) for a, b in merged if b - a >= min_keep], cuts


def split_scenes(keeps, silences, scene_gap):
    """scene_gap초보다 길게 쉰 곳을 경계로 남길 구간을 장면별로 묶는다."""
    if not scene_gap:
        return [keeps]
    long_gaps = [(s, e) for s, e in silences if e is not None and e - s >= scene_gap]
    scenes, cur = [], []
    for seg in keeps:
        # 앞 조각 끝과 이번 조각 시작 사이에 긴 무음이 걸쳐 있으면 새 장면
        if cur and any(s < seg[0] and e > cur[-1][1] for s, e in long_gaps):
            scenes.append(cur)
            cur = []
        cur.append(seg)
    if cur:
        scenes.append(cur)
    return scenes


def render(ffmpeg, src, segs, dst, has_audio, has_video, fps, crf, preset):
    parts, labels = [], ""
    for i, (a, b) in enumerate(segs):
        if has_video:
            parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}];")
            labels += f"[v{i}]"
        if has_audio:
            parts.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
                         f"afade=t=in:d=0.01,afade=t=out:st={max(0.0, b - a - 0.01):.3f}:d=0.01[a{i}];")
            labels += f"[a{i}]"
    outs = ("[vout]" if has_video else "") + ("[aout]" if has_audio else "")
    graph = "".join(parts) + f"{labels}concat=n={len(segs)}:v={int(has_video)}:a={int(has_audio)}{outs}"

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(graph)
        script = f.name
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-stats", "-y", "-i", src,
           "-filter_complex_script", script]
    if has_video:
        if fps:
            cmd += ["-fps_mode", "cfr", "-r", NTSC.get(fps, fps)]
        cmd += ["-map", "[vout]", "-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p"]
    if has_audio:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart", dst]
    try:
        subprocess.run(cmd, check=True)
    finally:
        os.unlink(script)


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:05.2f}"


def main():
    p = argparse.ArgumentParser(description="무음·말버릇 자동 컷 편집")
    p.add_argument("input")
    p.add_argument("-o", "--output", help="출력 파일 (기본: 입력이름.cut.mp4)")
    p.add_argument("--noise", type=float, default=-35, help="이 dB보다 작으면 무음으로 본다 (기본 -35)")
    p.add_argument("--min-silence", type=float, default=0.6, help="이 초 이상 이어진 무음만 자른다 (기본 0.6)")
    p.add_argument("--pad", type=float, default=0.15, help="무음 앞뒤로 남길 여유 초 (기본 0.15)")
    p.add_argument("--min-keep", type=float, default=0.2, help="이보다 짧게 남는 조각은 버린다 (기본 0.2초)")
    p.add_argument("--merge-gap", type=float, default=0.08, help="이보다 가까운 조각은 이어 붙인다")
    p.add_argument("--scene-gap", type=float, default=0, help="이 초 넘게 쉰 곳에서 장면 파일로 나눈다 (0이면 한 파일)")
    p.add_argument("--transcript", help="Whisper 단어 타임스탬프 JSON (말버릇 제거용)")
    p.add_argument("--fillers", default=",".join(DEFAULT_FILLERS), help="제거할 말버릇 (쉼표 구분)")
    p.add_argument("--crf", type=int, default=18, help="화질 (낮을수록 좋음, 기본 18)")
    p.add_argument("--preset", default="medium", help="x264 인코딩 속도 (ultrafast~slow)")
    p.add_argument("--dry-run", action="store_true", help="자를 구간만 출력하고 영상은 만들지 않는다")
    p.add_argument("--max-silence", type=float, default=0,
                   help="이 초보다 긴 무음은 자르지 않는다 (말 없이 보여주는 장면 보호, 0이면 제한 없음)")
    p.add_argument("--protect-gaps", type=float, default=0,
                   help="받아쓰기에서 말이 이 초 넘게 없는 구간은 통째로 보호 (--transcript 필요)")
    p.add_argument("--cut-file", help="retakes.py 가 만든 .retakes.json — NG 테이크·군말 구간을 함께 자른다")
    p.add_argument("--cut", action="append", default=[], metavar="시작-끝",
                   help="직접 잘라낼 구간(원본 초). 여러 번 쓸 수 있다. 예: --cut 46.5-49.3")
    args = p.parse_args()

    ffmpeg = find_ffmpeg()
    duration, has_audio, has_video, fps = probe(ffmpeg, args.input)
    if not has_audio:
        sys.exit("오디오 트랙이 없어서 무음을 찾을 수 없어요.")

    silences = detect_silence(ffmpeg, args.input, args.noise, args.min_silence)
    if args.max_silence:
        silences = [(a, b) for a, b in silences if (duration if b is None else b) - a <= args.max_silence]
    if args.protect_gaps and args.transcript:
        protected = speech_gaps(args.transcript, duration, args.protect_gaps)
        silences = [(a, b) for a, b in silences
                    if not any(pa <= a and (duration if b is None else b) <= pb for pa, pb in protected)]
        print(f"말 없이 보여주는 구간 {len(protected)}곳 보호: "
              + ", ".join(f"{fmt(a)}–{fmt(b)}" for a, b in protected))
    fillers = load_filler_spans(args.transcript, args.fillers.split(",")) if args.transcript else []
    if args.cut_file:
        with open(args.cut_file, encoding="utf-8") as f:
            for c in json.load(f)["cuts"]:
                fillers.append((c["start"], c["end"], "ng:" + c["reason"]))
    for spec in args.cut:
        a, b = (float(v) for v in spec.split("-"))
        fillers.append((a, b, "manual"))
    keeps, cuts = build_keeps(duration, silences, fillers, args.pad, args.min_keep, args.merge_gap)
    if not keeps:
        sys.exit("남길 구간이 없어요. --noise 값을 낮춰(예: -45) 다시 시도해 보세요.")
    scenes = split_scenes(keeps, silences, args.scene_gap)

    kept = sum(b - a for a, b in keeps)
    n_fill = sum(1 for c in cuts if c[2].startswith(("filler", "ng:")))
    print(f"원본 {fmt(duration)} → 편집본 {fmt(kept)}  ({duration - kept:.1f}초 제거, "
          f"무음 {len(cuts) - n_fill}곳 · 말버릇·NG {n_fill}곳 · 장면 {len(scenes)}개)")

    base = args.output or os.path.splitext(args.input)[0] + ".cut.mp4"
    stem, ext = os.path.splitext(base)
    report = {"input": args.input, "duration": round(duration, 3), "kept": round(kept, 3),
              "settings": {k: v for k, v in vars(args).items() if k not in ("input", "output")},
              "cuts": [{"start": round(a, 3), "end": round(b, 3), "reason": r} for a, b, r, _ in cuts],
              "scenes": []}

    for i, segs in enumerate(scenes, 1):
        dst = base if len(scenes) == 1 else f"{stem}.scene{i:02d}{ext}"
        length = sum(b - a for a, b in segs)
        print(f"  {os.path.basename(dst)}  원본 {fmt(segs[0][0])}–{fmt(segs[-1][1])}  → {fmt(length)}  ({len(segs)}조각)")
        report["scenes"].append({"file": dst, "segments": segs, "length": round(length, 3)})
        if not args.dry_run:
            render(ffmpeg, args.input, segs, dst, has_audio, has_video, fps, args.crf, args.preset)

    with open(stem + ".cuts.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"컷 기록: {stem}.cuts.json")


if __name__ == "__main__":
    main()
