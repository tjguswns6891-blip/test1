#!/usr/bin/env python3
"""쇼츠·릴스에 효과음을 얹는 도구.

자막(.srt) 줄 번호에 효과음 종류를 붙인 계획대로, 그 줄이 시작하기 0.05초 전에 효과음을 넣는다.
상황별 6종류 (youtube/sfx/kit, README 참고):
  intro   도입 주목 (첫 문장)          visual  시각자료·카드 등장
  emph    강조 (반전·숫자)            trans   화면·주제 전환
  cta     마지막 행동 유도 (댓글·팔로우) base    무난해서 아무 데나
  종류 뒤에 번호를 붙이면 그 변형을 쓴다 (emph2 = emph2_*.mp3). 예전 이름도 된다:
  whoosh→intro, swoosh→trans, pop·ding→emph, click→visual
30초 기준 4~8개가 넘지 않게 계획을 짠다 (넘으면 경고).

효과음 파일 찾는 순서
  1. --kit 폴더(기본 youtube/sfx/kit)에서 이름이 종류로 시작하는 파일
  2. --local 폴더(기본 ~/릴스효과음)에 이름에 종류가 들어간 파일 (whoosh.mp3, pop_1.wav …)
  3. 없으면 Openverse(CC0·CC BY)에서 종류 이름으로 검색해 4초 이하인 첫 결과를 받아 --cache 에 둔다.
     CC BY 는 출처 표기가 필요해서 받은 목록을 credits.txt 에 남긴다.

사용 예:
  python3 sfx.py short_A.mp4 short_A.srt --plan "1:intro,3:visual,5:emph,7:trans,9:cta" -o short_A.sfx.mp4
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

from autocut import find_ffmpeg

KINDS = ("intro", "visual", "emph", "trans", "cta", "base")
ALIASES = {"whoosh": "intro", "swoosh": "trans", "pop": "emph", "ding": "emph", "click": "visual"}
KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sfx", "kit")
LEAD = 0.05
API = "https://api.openverse.org/v1/audio/?q={q}&license=cc0,by&page_size=20"
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".aif", ".aiff")


def srt_starts(path):
    with open(path, encoding="utf-8") as f:
        blocks = re.split(r"\n\s*\n", f.read().strip())
    out = {}
    for b in blocks:
        lines = b.strip().splitlines()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+)", lines[1]) if len(lines) > 1 else None
        if m:
            h, mi, s, ms = map(int, m.groups())
            out[int(lines[0])] = h * 3600 + mi * 60 + s + ms / 1000
    return out


def kit_file(folder, kind):
    """kit 에서 이름이 종류(+번호)로 시작하는 파일. 번호가 없으면 가장 앞 번호."""
    for p in sorted(glob.glob(os.path.join(folder, "*"))):
        name = os.path.basename(p).lower()
        if name.endswith(AUDIO_EXT) and name.startswith(kind) and (kind[-1].isdigit() or name[len(kind)].isdigit()):
            return p
    return None


def local_file(folder, kind):
    for p in sorted(glob.glob(os.path.join(os.path.expanduser(folder), "*"))):
        name = os.path.basename(p).lower()
        if name.endswith(AUDIO_EXT) and kind in name:
            # swoosh 를 찾을 때 whoosh 파일이 걸리지 않게 (그 반대도)
            if kind == "whoosh" and "swoosh" in name:
                continue
            return p
    return None


def openverse_file(kind, cache, credits):
    os.makedirs(cache, exist_ok=True)
    meta_path = os.path.join(cache, kind + ".json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        if os.path.exists(meta["file"]):
            credits[kind] = meta
            return meta["file"]
    req = urllib.request.Request(API.format(q=urllib.parse.quote(kind)), headers={"User-Agent": "sfx.py"})
    with urllib.request.urlopen(req, timeout=30) as r:
        results = json.load(r)["results"]
    for it in results:
        dur = it.get("duration")
        if dur is None or dur > 4000 or not it.get("url"):
            continue
        ext = os.path.splitext(urllib.parse.urlparse(it["url"]).path)[1] or ".mp3"
        path = os.path.join(cache, kind + ext)
        req = urllib.request.Request(it["url"], headers={"User-Agent": "sfx.py"})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
        meta = {"file": path, "title": it.get("title"), "creator": it.get("creator"),
                "license": ("CC0 " if it.get("license") == "cc0" else "CC BY ") + str(it.get("license_version", "")),
                "source": it.get("foreign_landing_url"), "duration_ms": dur}
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
        credits[kind] = meta
        return path
    sys.exit(f"Openverse 에서 4초 이하 '{kind}' 효과음을 찾지 못했어요.")


def peak_db(ffmpeg, path):
    err = subprocess.run([ffmpeg, "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"max_volume: (-?[\d.]+) dB", err)
    return float(m.group(1)) if m else 0.0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("srt")
    p.add_argument("--plan", required=True, help='"자막 줄 번호:종류" 쉼표 구분. 예: "1:whoosh,4:pop,7:swoosh"')
    p.add_argument("--kit", default=KIT, help="상황별 효과음 키트 폴더")
    p.add_argument("--local", default="~/릴스효과음", help="키트에 없으면 찾아볼 효과음 폴더")
    p.add_argument("--cache", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sfx"),
                   help="Openverse 에서 받은 효과음을 둘 폴더")
    p.add_argument("--gain", type=float, default=-8, help="효과음 최고점(dBFS). 목소리 최고점이 -3 안팎이라 그보다 작게")
    p.add_argument("-o", "--out")
    args = p.parse_args()

    starts = srt_starts(args.srt)
    plan = []
    for item in args.plan.split(","):
        n, kind = item.split(":")
        kind = kind.strip().lower()
        base = kind.rstrip("0123456789")
        if base in ALIASES:
            kind = ALIASES[base] + kind[len(base):]
            base = ALIASES[base]
        if base not in KINDS:
            sys.exit(f"모르는 효과음 종류: {kind} (쓸 수 있는 것: {', '.join(KINDS)})")
        plan.append((max(0.0, starts[int(n)] - LEAD), kind, int(n)))

    ffmpeg = find_ffmpeg()
    err = subprocess.run([ffmpeg, "-hide_banner", "-i", args.video], capture_output=True, text=True).stderr
    h, mi, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    dur = int(h) * 3600 + int(mi) * 60 + float(s)
    per30 = len(plan) / dur * 30
    if not 4 <= per30 <= 8:
        print(f"주의: 30초 기준 {per30:.1f}개 (권장 4~8개)", file=sys.stderr)

    credits, files = {}, {}
    for _, kind, _ in plan:
        if kind not in files:
            base = kind.rstrip("0123456789")
            files[kind] = (kit_file(args.kit, kind) or local_file(args.local, base)
                           or openverse_file({v: k for k, v in ALIASES.items()}.get(base, base), args.cache, credits))

    peaks = {k: peak_db(ffmpeg, f) for k, f in files.items()}
    inputs, chains, labels = ["-i", args.video], [], []
    for i, (t, kind, _) in enumerate(plan, 1):
        inputs += ["-i", files[kind]]
        ms = int(round(t * 1000))
        # 파일마다 원래 크기가 달라서 최고점을 맞춘 뒤 --gain 만큼 줄인다
        vol = args.gain - peaks[kind]
        # 파일 앞 무음을 잘라 소리가 정확히 그 시점에 시작하게 한다
        chains.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                      f"silenceremove=start_periods=1:start_threshold=-45dB,"
                      f"volume={vol:.1f}dB,adelay={ms}|{ms}[s{i}]")
        labels.append(f"[s{i}]")
    graph = ";".join(chains) + f";[0:a]{''.join(labels)}amix=inputs={len(plan) + 1}:normalize=0:duration=first[a]"
    out = args.out or os.path.splitext(args.video)[0] + ".sfx.mp4"
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", graph,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", out], check=True)

    for t, kind, n in plan:
        src = files[kind]
        print(f"  {t:6.2f}s  {kind:6s}  (자막 {n}번)  ← {os.path.basename(src)}")
    print(f"완성: {out}  · 효과음 {len(plan)}개 · 30초 기준 {per30:.1f}개")
    if credits:
        cpath = os.path.join(args.cache, "credits.txt")
        lines = {}
        if os.path.exists(cpath):
            with open(cpath, encoding="utf-8") as f:
                lines = {l.split("\t")[0]: l for l in f.read().splitlines() if l}
        for kind, m in credits.items():
            lines[kind] = f"{kind}\t\"{m['title']}\" by {m['creator']} ({m['license']}) {m['source']}"
        with open(cpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines[k] for k in sorted(lines)) + "\n")
        print(f"출처: {cpath}")


if __name__ == "__main__":
    main()
