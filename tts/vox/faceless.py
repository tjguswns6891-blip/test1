"""faceless.py 에서 whisper_words() 하나만 가져옴 (사용자 인수인계 2026-11-20)."""
import json, os


def whisper_words(path, offset=0.0):
    """음성의 단어별 시각 (받아쓰기, 결과는 옆에 .words.json 으로 저장해 다시 쓴다)."""
    cache = os.path.splitext(path)[0] + ".words.json"
    if not os.path.exists(cache) or os.path.getmtime(cache) < os.path.getmtime(path):
        from faster_whisper import WhisperModel
        m = WhisperModel("medium", device="cpu", compute_type="int8")
        seg, _ = m.transcribe(path, language="ko", beam_size=5, word_timestamps=True)
        json.dump([[w.word.strip(), w.start, w.end] for sg in seg for w in sg.words], open(cache, "w"), ensure_ascii=False)
    return [(w, a + offset, b + offset) for w, a, b in json.load(open(cache))]
