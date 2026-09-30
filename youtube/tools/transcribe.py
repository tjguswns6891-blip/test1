#!/usr/bin/env python3
"""촬영 원본에서 음성을 뽑아 Whisper로 받아쓰고, 단어 타임스탬프 JSON과 .srt 자막을 만드는 도구.

사용 예:
  python3 transcribe.py raw.mp4                       # raw.words.json + raw.srt (로컬 faster-whisper)
  python3 transcribe.py raw.mp4 --engine api          # OpenAI Whisper API (OPENAI_API_KEY 필요)
  python3 transcribe.py raw.mp4 --model ./whisper-dir # 직접 받아 둔 모델 폴더 사용
  python3 transcribe.py --from-json raw.words.json    # JSON만 고친 뒤 자막 다시 만들기
  python3 transcribe.py raw.mp4 --hotwords "호르무즈 해협, SCHD" --fix fixes.txt
                                                      # 용어 미리 알려 주기 + 자막 오인식 교정

컷 편집까지 이어서 할 때:
  python3 transcribe.py raw.mp4                                   # 1) 원본 받아쓰기
  python3 autocut.py raw.mp4 --transcript raw.words.json          # 2) 무음·말버릇 컷
  python3 transcribe.py --from-json raw.words.json --cuts raw.cut.cuts.json
                                                                  # 3) 편집본 시간에 맞춘 자막
                                                                  #    (raw.cut.srt, 장면마다 .sceneNN.srt)

만든 raw.words.json 은 그대로 autocut.py --transcript 에 넣을 수 있다.
ffmpeg 위치: 환경변수 FFMPEG → PATH의 ffmpeg → pip 패키지 imageio-ffmpeg 순서로 찾는다.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

from autocut import DEFAULT_FILLERS, find_ffmpeg, probe

API_LIMIT = 25 * 1024 * 1024        # OpenAI 업로드 한도
API_CHUNK_SEC = 20 * 60             # 한도를 넘으면 20분씩 나눠 보낸다 (32kbps mp3 ≈ 4.8MB)
DEFAULT_PROMPT = "오늘 증시 브리핑입니다. 코스피, 코스닥, 나스닥, S&P500, 외국인 순매수, 기관, 환율, 금리."
SENTENCE_END = re.compile(r"[.?!。？！]$")


def extract_audio(ffmpeg, src, dst, start=None, dur=None, codec="wav"):
    """영상에서 음성만 모노 16kHz로 뽑는다. codec='mp3'면 API 업로드용으로 32kbps 압축."""
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", src]
    if dur is not None:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-vn", "-ac", "1", "-ar", "16000"]
    cmd += ["-c:a", "libmp3lame", "-b:a", "32k"] if codec == "mp3" else ["-c:a", "pcm_s16le"]
    subprocess.run(cmd + [dst], check=True)
    return dst


def load_model(model_name, threads):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper가 없어요. `pip install faster-whisper` 로 설치하세요.")
    print(f"모델 불러오는 중: {model_name} (처음엔 약 1.6GB를 내려받아요)", file=sys.stderr)
    try:
        return WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=threads)
    except Exception as e:  # 네트워크 차단 등
        sys.exit(f"모델을 불러오지 못했어요: {e}\n"
                 "huggingface.co 모델 파일 호스트(*.hf.co, *.xethub.hf.co)가 막혀 있으면 "
                 "모델 폴더를 직접 받아 --model 로 경로를 넘겨 주세요.")


def silences_in(ffmpeg, audio, noise_db=-35, min_len=0.3):
    err = subprocess.run([ffmpeg, "-hide_banner", "-nostats", "-i", audio, "-af",
                          f"silencedetect=n={noise_db}dB:d={min_len}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", err)]
    return [(a, ends[i] if i < len(ends) else float("inf")) for i, a in enumerate(starts)]


def refill_gaps(ffmpeg, audio, words, model, language, prompt, min_gap=1.5, min_voiced=0.8, reach=15.0):
    """받아쓰기가 비었는데 말소리가 있는 곳(되풀이한 NG를 Whisper 가 한 번으로 합친 곳)을
    앞뒤 말 덩어리까지 넓혀 VAD 없이 다시 받아쓰고 그 구간 단어를 바꿔 넣는다."""
    from faster_whisper import decode_audio
    sil = silences_in(ffmpeg, audio)

    def voiced(a, b):
        return (b - a) - sum(max(0.0, min(b, e) - max(a, s)) for s, e in sil)

    wins = []
    for i in range(len(words) - 1):
        # 단어 사이 빈틈, 또는 몇 초씩 늘어진 단어(되풀이한 말을 한 단어로 뭉갠 곳)
        holes = [(words[i]["end"], words[i + 1]["start"]), (words[i]["start"] + 0.6, words[i]["end"])]
        if not any(b - a >= min_gap and voiced(a, b) >= min_voiced for a, b in holes):
            continue
        a, b = words[i]["start"], words[i + 1]["start"]
        k0 = i
        while k0 > 0 and words[k0]["start"] - words[k0 - 1]["end"] < 0.45 and a - words[k0 - 1]["start"] < reach:
            k0 -= 1
        k1 = i + 1
        while (k1 + 1 < len(words) and words[k1 + 1]["start"] - words[k1]["end"] < 0.45
               and words[k1 + 1]["end"] - b < reach):
            k1 += 1
        if wins and k0 <= wins[-1][1]:
            wins[-1][1] = max(wins[-1][1], k1)
        else:
            wins.append([k0, k1])
    if not wins:
        return words
    pcm = decode_audio(audio, sampling_rate=16000)
    for k0, k1 in reversed(wins):
        t0 = max(0.0, words[k0]["start"] - 0.3)
        t1 = words[k1]["end"] + 0.3
        segs, _ = model.transcribe(pcm[int(t0 * 16000):int(t1 * 16000)], language=language,
                                   word_timestamps=True, initial_prompt=prompt or None,
                                   vad_filter=False, condition_on_previous_text=False)
        new = [{"word": w.word, "start": round(w.start + t0, 3), "end": round(w.end + t0, 3),
                "prob": round(w.probability, 3)} for seg in segs for w in seg.words or []]
        if new:
            old = "".join(w["word"] for w in words[k0:k1 + 1]).strip()
            print(f"  다시 받아씀 {t0:.1f}–{t1:.1f}s: {k1 - k0 + 1}단어 → {len(new)}단어", file=sys.stderr)
            print(f"    전: {old[:80]}\n    후: {''.join(w['word'] for w in new).strip()[:160]}", file=sys.stderr)
            words[k0:k1 + 1] = new
    return words


def transcribe_local(audio, model_name, language, prompt, hotwords, threads, verbatim=False, ffmpeg=None):
    model = load_model(model_name, threads)
    segments, info = model.transcribe(audio, language=language, word_timestamps=True,
                                      initial_prompt=prompt or None, hotwords=hotwords or None,
                                      vad_filter=True,
                                      vad_parameters={"min_silence_duration_ms": 500},
                                      # 앞 문장에 끌려 같은 말을 되풀이하거나 무음에서 말을 지어내는 것을 막는다
                                      condition_on_previous_text=False,
                                      hallucination_silence_threshold=2.0,
                                      # --verbatim: NG로 같은 말을 되풀이한 것도 그대로 적어야 retakes.py 가 찾는다
                                      repetition_penalty=1.0 if verbatim else 1.1)
    words = []
    for seg in segments:
        for w in seg.words or []:
            # 앞 공백은 띄어쓰기 표시라서 그대로 둔다 ("5"+".18"+"%" → "5.18%")
            words.append({"word": w.word, "start": round(w.start, 3),
                          "end": round(w.end, 3), "prob": round(w.probability, 3)})
        print(f"  [{seg.end:7.1f}s / {info.duration:.0f}s] {seg.text.strip()}", file=sys.stderr)
    if verbatim and ffmpeg:
        words = refill_gaps(ffmpeg, audio, words, model, language, prompt)
    return words


def transcribe_api(ffmpeg, src, duration, language, prompt, tmp):
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai 패키지가 없어요. `pip install openai` 로 설치하세요.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("환경변수 OPENAI_API_KEY 가 없어요.")
    client = OpenAI()
    whole = extract_audio(ffmpeg, src, os.path.join(tmp, "all.mp3"), codec="mp3")
    if os.path.getsize(whole) <= API_LIMIT:
        chunks = [(0.0, whole)]
    else:
        chunks = []
        for i, t in enumerate(range(0, int(duration) + 1, API_CHUNK_SEC)):
            path = extract_audio(ffmpeg, src, os.path.join(tmp, f"part{i}.mp3"), t, API_CHUNK_SEC, "mp3")
            chunks.append((float(t), path))
    words = []
    for offset, path in chunks:
        print(f"  API 전송: {offset:.0f}s부터 ({os.path.getsize(path) / 1e6:.1f}MB)", file=sys.stderr)
        with open(path, "rb") as f:
            res = client.audio.transcriptions.create(
                model="whisper-1", file=f, language=language, prompt=prompt or None,
                response_format="verbose_json", timestamp_granularities=["word"])
        for w in res.words or []:
            words.append({"word": " " + w.word.strip(), "start": round(w.start + offset, 3),
                          "end": round(w.end + offset, 3)})
    return words


def remap(words, segments):
    """원본 시간의 단어를 컷 편집본 시간으로 옮긴다. 남긴 구간과 가장 많이 겹치는 곳에 붙이고,
    어느 구간과도 겹치지 않는(잘려 나간) 단어만 버린다. Whisper가 단어 시작을 앞 무음까지
    늘려 잡는 일이 있어서, 가운데 지점만 보면 멀쩡한 단어가 빠진다."""
    offsets, acc = [], 0.0
    for a, b in segments:
        offsets.append(acc)
        acc += b - a
    out = []
    for w in words:
        best, idx = 0.0, None
        for i, (a, b) in enumerate(segments):
            ov = min(w["end"], b) - max(w["start"], a)
            if ov > best:
                best, idx = ov, i
        if idx is None:
            continue
        a, b = segments[idx]
        out.append({**w, "start": round(offsets[idx] + max(w["start"], a) - a, 3),
                    "end": round(offsets[idx] + min(w["end"], b) - a, 3)})
    out.sort(key=lambda w: w["start"])
    return out


def load_fixes(path):
    """교정 파일: 한 줄에 `잘못=바른` (예: `슈드=SCHD`). #으로 시작하면 주석."""
    fixes = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                a, b = line.split("=", 1)
                fixes.append((a.strip(), b.strip()))
    return fixes


def build_cues(words, max_chars, max_sec, gap, fillers=(), fixes=()):
    """단어들을 문장 단위 자막 줄로 묶는다. 문장 끝, 긴 쉼, 글자 수·길이 한도에서 끊고,
    반 이상 찼으면 쉼표에서 먼저 끊는다. 줄은 띄어쓰기 자리에서만 나눈다(“22 / %” 방지).
    문장 끝 단어 하나만 다음 줄로 밀려나지 않도록, 그 단어는 한도를 30%까지 넘겨도 붙인다."""
    cues, cur = [], []
    fillers = {f.strip(" .,!?~…") for f in fillers}
    # 예전 형식(앞 공백을 지운 단어)이면 단어마다 띄어 쓴다
    spaced = any(w["word"].startswith(" ") for w in words)
    text = lambda ws: "".join(x["word"] if spaced else " " + x["word"] for x in ws).strip()

    def flush():
        if cur:
            t = text(cur)
            for a, b in fixes:
                t = t.replace(a, b)
            cues.append({"start": cur[0]["start"], "end": cur[-1]["end"], "text": t})
            cur.clear()

    for w in words:
        token = w["word"].strip()
        if not token or token.strip(" .,!?~…") in fillers:
            continue
        ends = SENTENCE_END.search(token)
        boundary = not spaced or w["word"].startswith(" ")
        if cur and boundary:
            limit = max_chars * 1.3 if ends else max_chars
            if (w["start"] - cur[-1]["end"] > gap or len(text(cur + [w])) > limit
                    or w["end"] - cur[0]["start"] > max_sec):
                flush()
        cur.append(w)
        if ends or (token.endswith(",") and len(text(cur)) >= max_chars * 0.5):
            flush()
    flush()
    return cues


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(cues, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, c in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src", nargs="?", help="촬영 원본 영상(또는 음성) 파일")
    p.add_argument("--engine", choices=["local", "api"], default="local", help="local=faster-whisper, api=OpenAI")
    p.add_argument("--model", default="large-v3-turbo", help="faster-whisper 모델 이름 또는 폴더 경로")
    p.add_argument("--language", default="ko")
    p.add_argument("--prompt", default=DEFAULT_PROMPT, help="자주 나오는 용어(인식 정확도 향상). 빈 문자열이면 끔")
    p.add_argument("--hotwords", default="", help="꼭 맞혀야 할 고유명사·용어 (쉼표 구분, 로컬 엔진)")
    p.add_argument("--fix", help="자막 교정 파일 (한 줄에 `잘못=바른`)")
    p.add_argument("--threads", type=int, default=os.cpu_count() or 4)
    p.add_argument("--verbatim", action="store_true",
                   help="되풀이한 말(NG)과 '음·어'도 빼지 않고 받아쓴다 (retakes.py 로 NG 컷할 때)")
    p.add_argument("--from-json", help="기존 words.json 으로 자막만 다시 만들기")
    p.add_argument("--cuts", help="autocut.py 가 만든 .cuts.json — 편집본(장면별) 시간에 맞춰 자막 생성")
    p.add_argument("--keep-fillers", action="store_true", help="자막에 '음·어' 같은 말버릇도 남기기")
    p.add_argument("--max-chars", type=int, default=28, help="자막 한 줄 최대 글자 수 (쇼츠는 16 정도)")
    p.add_argument("--max-sec", type=float, default=6.0, help="자막 한 줄 최대 길이(초)")
    p.add_argument("--gap", type=float, default=0.7, help="이보다 오래 쉬면 자막을 끊음(초)")
    p.add_argument("-o", "--out", help="출력 이름 앞부분 (기본: 원본 이름)")
    args = p.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            data = json.load(f)
        words = data["words"] if isinstance(data, dict) else data
        base = args.out or re.sub(r"(\.words)?\.json$", "", args.from_json)
        if args.verbatim and args.src:
            # 이미 받아쓴 것에 빈 곳 다시 받아쓰기만 더한다
            ffmpeg = find_ffmpeg()
            with tempfile.TemporaryDirectory() as tmp:
                audio = extract_audio(ffmpeg, args.src, os.path.join(tmp, "audio.wav"))
                prompt = args.prompt + " 음, 어, 그러니까... 아 다시 할게요."
                words = refill_gaps(ffmpeg, audio, words, load_model(args.model, args.threads),
                                    args.language, prompt)
            data["words"] = words
            with open(base + ".words.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
    else:
        if not args.src:
            p.error("원본 파일이나 --from-json 중 하나가 필요해요.")
        ffmpeg = find_ffmpeg()
        duration = probe(ffmpeg, args.src)[0]
        base = args.out or os.path.splitext(args.src)[0]
        with tempfile.TemporaryDirectory() as tmp:
            if args.engine == "api":
                prompt = " ".join(x for x in (args.prompt, args.hotwords) if x)
                words = transcribe_api(ffmpeg, args.src, duration, args.language, prompt, tmp)
            else:
                audio = extract_audio(ffmpeg, args.src, os.path.join(tmp, "audio.wav"))
                # 프롬프트에 군말을 섞어 두면 Whisper 가 "음·어"를 지우지 않고 적는다
                prompt = (args.prompt + " 음, 어, 그러니까... 아 다시 할게요.") if args.verbatim else args.prompt
                words = transcribe_local(audio, args.model, args.language, prompt, args.hotwords,
                                         args.threads, args.verbatim, ffmpeg)
        with open(base + ".words.json", "w", encoding="utf-8") as f:
            json.dump({"language": args.language, "duration": round(duration, 3), "words": words},
                      f, ensure_ascii=False, indent=1)
        print(f"단어 타임스탬프: {base}.words.json ({len(words)}단어)", file=sys.stderr)

    fillers = () if args.keep_fillers else DEFAULT_FILLERS
    fixes = load_fixes(args.fix) if args.fix else ()
    targets = [(base, words)]
    if args.cuts:
        with open(args.cuts, encoding="utf-8") as f:
            scenes = json.load(f)["scenes"]
        targets = []
        for sc in scenes:
            stem = os.path.splitext(sc["file"])[0]
            scene_words = remap(words, sc["segments"])
            with open(stem + ".words.json", "w", encoding="utf-8") as f:
                json.dump({"language": args.language, "duration": sc["length"], "words": scene_words},
                          f, ensure_ascii=False, indent=1)
            targets.append((stem, scene_words))
    for stem, ws in targets:
        cues = build_cues(ws, args.max_chars, args.max_sec, args.gap, fillers, fixes)
        write_srt(cues, stem + ".srt")
        print(f"자막: {stem}.srt ({len(cues)}줄)", file=sys.stderr)


if __name__ == "__main__":
    main()
