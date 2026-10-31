#!/bin/bash
# 새 클라우드 세션에서 영상 제작 도구를 자동 설치한다 (이미 있으면 건너뜀).
# ffmpeg · LaTeX(Manim 수식) · Blender · Manim · VoxCPM2(음성 복제) · faster-whisper(받아쓰기) · 한글 폰트 · Playwright
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
log() { echo "[session-start] $*" >&2; }

# 1) 시스템 패키지
need=""
command -v ffmpeg  >/dev/null || need="$need ffmpeg"
command -v latex   >/dev/null || need="$need texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-science dvisvgm"
command -v blender >/dev/null || need="$need blender libegl1 libegl-mesa0 libgl1-mesa-dri"
dpkg -s libpango1.0-dev >/dev/null 2>&1 || need="$need libcairo2-dev libpango1.0-dev pkg-config"
if [ -n "$need" ]; then
  log "apt 설치:$need"
  apt-get update -q >/dev/null
  DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends $need >/dev/null
fi

# 2) 한글 폰트 (tools/shorts.py 가 ~/.fonts 의 이 두 파일을 씀)
mkdir -p ~/.fonts
for w in Black Bold; do
  f=~/.fonts/NotoSansCJKkr-$w.otf
  [ -s "$f" ] || { log "폰트 $w"; curl -fsSL -o "$f" "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/Korean/NotoSansCJKkr-$w.otf"; }
done
fc-cache -f ~/.fonts >/dev/null 2>&1 || true

# 3) 시스템 파이썬: 받아쓰기·강조 처리
python3 -c "import av; assert int(av.__version__.split('.')[0])<17; import faster_whisper, soundfile, PIL, numpy" 2>/dev/null || {
  log "pip: faster-whisper av<17 soundfile pillow numpy (av 17+ 는 faster-whisper 1.2.1 받아쓰기 오류)"
  pip install -q faster-whisper 'av<17' soundfile pillow numpy 2>/dev/null || pip install -q --break-system-packages faster-whisper 'av<17' soundfile pillow numpy
}

# 4) Manim (uv 가상환경)
command -v uv >/dev/null || { log "uv 설치"; curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null; export PATH="$HOME/.local/bin:$PATH"; }
[ -x ~/.venvs/manim/bin/manim ] || {
  log "Manim"; uv venv -q ~/.venvs/manim --python 3.11; uv pip install -q --python ~/.venvs/manim/bin/python manim
}

# 5) VoxCPM2 (CPU) + 모델 미리 받기
[ -x ~/.venvs/voxcpm/bin/python ] && ~/.venvs/voxcpm/bin/python -c "import voxcpm" 2>/dev/null || {
  log "VoxCPM2"; uv venv -q ~/.venvs/voxcpm --python 3.11
  uv pip install -q --python ~/.venvs/voxcpm/bin/python torch torchaudio --index-url https://download.pytorch.org/whl/cpu
  uv pip install -q --python ~/.venvs/voxcpm/bin/python voxcpm
}
~/.venvs/voxcpm/bin/python - <<'PY' >/dev/null 2>&1 || log "VoxCPM2 모델 미리 받기 실패 (처음 쓸 때 받음)"
from huggingface_hub import snapshot_download
snapshot_download("openbmb/VoxCPM2")
PY
python3 - <<'PY' >/dev/null 2>&1 || log "whisper medium 미리 받기 실패 (처음 쓸 때 받음)"
from faster_whisper import WhisperModel
WhisperModel("medium", device="cpu", compute_type="int8")
PY

# 6) Playwright (사이트 녹화용 node 모듈; 브라우저는 /opt/pw-browsers 에 이미 있음)
PW=~/.cache/pw
[ -d "$PW/node_modules/playwright" ] || {
  log "playwright"; mkdir -p "$PW"; (cd "$PW" && npm init -y >/dev/null && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i -s playwright@1.56 >/dev/null)
}
[ -n "${CLAUDE_ENV_FILE:-}" ] && echo "export NODE_PATH=$PW/node_modules" >> "$CLAUDE_ENV_FILE"

# 7) (선택) 음성 복제 프롬프트 = 본인 목소리. 저장소에는 넣지 않는다(raw/ 는 git 제외).
#    VOICE_PROMPT_URL 환경 변수(세션 환경 설정)에 wav 주소가 있을 때만 받는다.
V="$CLAUDE_PROJECT_DIR/youtube/raw/voice"
if [ ! -s "$V/prompt_hook.wav" ] && [ -n "${VOICE_PROMPT_URL:-}" ]; then
  mkdir -p "$V"; curl -fsSL -o "$V/prompt_hook.wav" "$VOICE_PROMPT_URL" && log "음성 프롬프트 받음"
  [ -n "${VOICE_PROMPT_TEXT:-}" ] && printf '%s' "$VOICE_PROMPT_TEXT" > "$V/prompt_hook.txt"
fi
log "완료"
