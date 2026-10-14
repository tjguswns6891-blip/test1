#!/usr/bin/env python3
"""얼굴 없는 16:9 롱폼 합성 (AI 음성 + 모션그래픽 · 3D · 사이트 녹화).

설정(json):
  {"title": "영상 제목", "date": "2026.10.14 기준",
   "sections": [{"key": "S1", "chapter": "코스피, 고점 대비 −34%",
                 "audio": ["v/S1_0_long.wav", ...],          # 이 섹션의 음성 조각 (순서대로 잇는다)
                 "lines": [{"sub": "..."}, ...]}, ...],
   "visuals": [["파일", "S1:2", [x, y, w, h] 또는 null, 시작초], ...]}   # "섹션:문장번호" 또는 "12.5s"
- 음성 조각 사이 0.35초, 섹션 사이 0.9초 쉼. 이어 붙인 음성을 받아쓰기해서 자막·문장 시각을 잡는다(faceless.word_cues).
- 자막: 한두 문장씩 통째로, 말하는 순간에 맞춰, 숫자·*강조* 는 노란색. 화면 아래 한 자리.
- 왼쪽 위에는 지금 섹션 이름, 오른쪽 위에는 기준 날짜.
사용: python3 longform.py config.json -o 출력폴더 [--name long]
"""
import argparse, json, os, re, subprocess, sys, tempfile

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import faceless as F
import shorts as S
from compose import ass_time, highlight
from transcribe import shown_until, write_srt

W, H = 1920, 1080
GAP_IN, GAP_SEC, LEAD, TAIL = 0.35, 0.9, 0.4, 1.2
SUB_BOTTOM = 70                                         # 자막 아랫선 (화면 아래에서)


def build_audio(sections, out_wav):
    """섹션·조각을 이어 붙이고, 섹션마다 시작 시각을 돌려준다."""
    sr, parts, t, starts = None, [], LEAD, []
    for si, sec in enumerate(sections):
        if si:
            parts.append(np.zeros(int(GAP_SEC * 48000))); t += GAP_SEC
        starts.append(t)
        for ci, f in enumerate(sec["audio"]):
            y, r = sf.read(f)
            if y.ndim > 1:
                y = y.mean(1)
            if r != 48000:                              # 길이만 맞으면 되니 간단히 선형 보간
                y = np.interp(np.linspace(0, len(y), int(len(y) * 48000 / r), endpoint=False), np.arange(len(y)), y)
            y = F_trim(y)
            if ci:
                parts.append(np.zeros(int(GAP_IN * 48000))); t += GAP_IN
            parts.append(y); t += len(y) / 48000
    y = np.concatenate([np.zeros(int(LEAD * 48000))] + parts + [np.zeros(int(TAIL * 48000))])
    sf.write(out_wav, y, 48000)
    return starts, len(y) / 48000


def F_trim(y, thr_db=-42):
    e = np.abs(y); idx = np.where(e > e.max() * 10 ** (thr_db / 20))[0]
    return y[max(0, idx[0] - 1200): idx[-1] + 2400] if len(idx) else y


def chip(text, path, color=(255, 197, 61)):
    f = ImageFont.truetype(S.FONT_BLACK, 40)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10))); tw = d0.textlength(text, font=f)
    img = Image.new("RGBA", (int(tw) + 70, 76), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, img.width - 1, 75), 20, fill=(17, 19, 24, 220), outline=color + (255,), width=3)
    d.text((35, 38), text, font=f, fill=color + (255,), anchor="lm")
    img.save(path)


def write_ass(cues, path):
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2",
        "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{S.FONT},58,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,-1,0,1,4,2,2,120,120,{SUB_BOTTOM},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for i, c in enumerate(cues):
        end = shown_until(cues, i, 0.35, 0.6, gap=0.02)
        lines.append(f"Dialogue: 1,{ass_time(c['start'])},{ass_time(end)},Sub,,0,0,0,,"
                     f"{{\\an2\\pos({W // 2},{H - SUB_BOTTOM})}}{S.star(highlight(S.wrap_block(c['text'], 24), S.ACCENT))}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def build(cfg, out_dir, name, ffmpeg):
    secs = cfg["sections"]
    wav = os.path.join(out_dir, name + ".wav")
    starts, total = build_audio(secs, wav)
    words = F.whisper_words(wav)
    subs = [ln["sub"] for s in secs for ln in s["lines"]]
    cues, spans = F.word_cues(subs, words)
    write_srt([dict(c, text=c["text"].replace("*", "")) for c in cues], os.path.join(out_dir, name + ".srt"))
    # 섹션:문장 → 전체 문장 번호
    off, k = {}, 0
    for s in secs:
        off[s["key"]] = k; k += len(s["lines"])
    sec_rng = []
    for i, s in enumerate(secs):
        a = spans[off[s["key"]]][0] - 0.3
        b = spans[off[s["key"]] + len(s["lines"]) - 1][1] + 0.6
        sec_rng.append((max(0, a), b))
    plan = []
    for f, at, crop, ss in cfg["visuals"]:
        if isinstance(at, str) and at.endswith("s"):
            t0 = float(at[:-1])
        else:
            key, li = at.split(":"); t0 = max(0.0, spans[off[key] + int(li)][0] - 0.2)
        plan.append([f, t0, crop, ss])
    plan.sort(key=lambda p: p[1]); plan[0][1] = 0.0
    print(f"{name}: {total:.1f}초 · 섹션 {len(secs)} · 문장 {len(subs)} · 자막 {len(cues)} · 그래픽 {len(plan)}")
    with tempfile.TemporaryDirectory() as tmp:
        ass = os.path.join(tmp, "s.ass"); write_ass(cues, ass)
        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
               "-f", "lavfi", "-t", f"{total:.3f}", "-i", f"color=c=0x111318:s={W}x{H}:r=30", "-i", wav]
        chains, prev, idx = [], "[0:v]", 2
        for i, (src, t0, crop, ss) in enumerate(plan):
            t1 = plan[i + 1][1] + 0.3 if i + 1 < len(plan) else total
            cr = "crop={}:{}:{}:{},".format(*[int(v) // 2 * 2 for v in (crop[2], crop[3], crop[0], crop[1])]) if crop else ""
            cmd += ["-ss", f"{ss:.2f}", "-i", src]
            chains.append(f"[{idx}:v]{cr}scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x111318,"
                          f"setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=600,trim=0:{t1 - t0:.3f},"
                          f"format=rgba,fade=t=in:st=0:d=0.3:alpha=1,setpts=PTS-STARTPTS+{t0:.3f}/TB[p{i}]")
            chains.append(f"{prev}[p{i}]overlay=0:0:eof_action=pass:enable='between(t,{t0:.3f},{t1:.3f})'[o{i}]")
            prev, idx = f"[o{i}]", idx + 1
        # 아래 자막 받침(그라데이션) · 섹션 이름 · 날짜
        grad = os.path.join(tmp, "grad.png")
        g = Image.new("RGBA", (W, 300)); gd = ImageDraw.Draw(g)
        for y in range(300):
            gd.line([(0, y), (W, y)], fill=(10, 11, 14, int(210 * (y / 300) ** 1.4)))
        g.save(grad)
        cmd += ["-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", grad]
        chains.append(f"{prev}[{idx}:v]overlay=0:{H - 300}[g]"); prev, idx = "[g]", idx + 1
        date = os.path.join(tmp, "date.png"); chip(cfg.get("date", ""), date, (141, 148, 161))
        cmd += ["-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", date]
        chains.append(f"{prev}[{idx}:v]overlay=W-w-40:36[d]"); prev, idx = "[d]", idx + 1
        for i, (s, (a, b)) in enumerate(zip(secs, sec_rng)):
            if not s.get("chapter"):
                continue
            p = os.path.join(tmp, f"c{i}.png"); chip(s["chapter"], p)
            cmd += ["-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", p]
            chains.append(f"[{idx}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.3:alpha=1[ci{i}]")
            chains.append(f"{prev}[ci{i}]overlay=40:36:enable='between(t,{a:.3f},{b:.3f})'[c{i}]"); prev, idx = f"[c{i}]", idx + 1
        chains.append(f"{prev}ass={ass}:fontsdir={os.path.expanduser('~/.fonts')}[out]")
        out = os.path.join(out_dir, name + ".mp4")
        cmd += ["-filter_complex", ";".join(chains), "-map", "[out]", "-map", "1:a", "-t", f"{total:.3f}",
                "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)
    json.dump({"sections": [{"key": s["key"], "chapter": s.get("chapter", ""), "start": round(a, 2)} for s, (a, b) in zip(secs, sec_rng)]},
              open(os.path.join(out_dir, name + ".chapters.json"), "w"), ensure_ascii=False, indent=1)
    print(f"  → {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("config"); p.add_argument("-o", "--out", default="."); p.add_argument("--name", default="long")
    a = p.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)
    base = os.path.dirname(os.path.abspath(a.config))
    for s in cfg["sections"]:
        s["audio"] = [os.path.join(base, x) for x in s["audio"]]
    cfg["visuals"] = [[os.path.join(base, v[0])] + v[1:] for v in cfg["visuals"]]
    build(cfg, a.out, a.name, S.find_ffmpeg())


if __name__ == "__main__":
    main()
