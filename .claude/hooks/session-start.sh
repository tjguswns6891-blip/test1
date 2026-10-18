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
  apt-get update -q >/dev/null || true
  DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends $need >/dev/null || log "apt 설치 일부 실패"
fi

# 2) 한글 폰트 (tools/shorts.py 가 ~/.fonts 의 이 두 파일을 씀)
mkdir -p ~/.fonts
for w in Black Bold; do
  f=~/.fonts/NotoSansCJKkr-$w.otf
  [ -s "$f" ] || { log "폰트 $w"; curl -fsSL -o "$f" "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/Korean/NotoSansCJKkr-$w.otf"; }
done
fc-cache -f ~/.fonts >/dev/null 2>&1 || true

# 3) 시스템 파이썬: 받아쓰기·강조 처리
#    + youtube/setup.sh 에 있던 것: 카드 영상 읽기(opencv)·드라이브 받기(gdown)·썸네일 배경 제거(rembg)
PYPKG="faster-whisper soundfile pillow numpy opencv-python-headless gdown rembg imageio-ffmpeg requests"
python3 -c "import faster_whisper, soundfile, PIL, numpy, cv2, gdown, rembg, imageio_ffmpeg, requests" 2>/dev/null || {
  log "pip: $PYPKG"
  pip install -q $PYPKG 2>/dev/null || pip install -q --break-system-packages $PYPKG || log "pip 설치 일부 실패"
}

# 3-1) 회사 로고용 simple-icons (tools/logos.js)
[ -d ~/simple-icons/package ] || { log "simple-icons"; mkdir -p ~/simple-icons && (cd ~/simple-icons && npm pack simple-icons -q >/dev/null && tar xzf simple-icons-*.tgz) || log "simple-icons 실패"; }
[ -e ~/simple-icons/package/_data ] || ln -s data ~/simple-icons/package/_data 2>/dev/null || true

# 4) Manim (uv 가상환경)
command -v uv >/dev/null || { log "uv 설치"; curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null; export PATH="$HOME/.local/bin:$PATH"; }
[ -x ~/.venvs/manim/bin/manim ] || {
  log "Manim"; uv venv -q ~/.venvs/manim --python 3.11; uv pip install -q --python ~/.venvs/manim/bin/python manim
}

# 5) VoxCPM2 (CPU) + 모델 미리 받기
#    torch 는 download.pytorch.org, 모델은 huggingface.co 에서 받는다 → 클라우드 환경 네트워크가 막혀 있으면 실패(나머지 설치는 계속)
~/.venvs/voxcpm/bin/python -c "import voxcpm" 2>/dev/null || {
  log "VoxCPM2"; [ -x ~/.venvs/voxcpm/bin/python ] || uv venv -q ~/.venvs/voxcpm --python 3.11
  { uv pip install -q --python ~/.venvs/voxcpm/bin/python torch torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && uv pip install -q --python ~/.venvs/voxcpm/bin/python voxcpm; } || log "VoxCPM2 설치 실패 (download.pytorch.org 접속 확인)"
}
[ -x ~/.venvs/voxcpm/bin/python ] && ~/.venvs/voxcpm/bin/python - <<'PY' >/dev/null 2>&1 || log "VoxCPM2 모델 미리 받기 실패 (처음 쓸 때 받음)"
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
  log "playwright"; mkdir -p "$PW"; (cd "$PW" && npm init -y >/dev/null && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i -s playwright@1.56 >/dev/null) || log "playwright 실패"
}
[ -n "${CLAUDE_ENV_FILE:-}" ] && echo "export NODE_PATH=$PW/node_modules" >> "$CLAUDE_ENV_FILE"

# 7) (선택) 음성 복제 프롬프트 = 본인 목소리. 저장소에는 넣지 않는다(raw/ 는 git 제외).
#    VOICE_PROMPT_URL 환경 변수(세션 환경 설정)에 wav 주소가 있을 때만 받는다.
V="$CLAUDE_PROJECT_DIR/youtube/raw/voice"
if [ ! -s "$V/prompt_hook.wav" ] && [ -n "${VOICE_PROMPT_URL:-}" ]; then
  mkdir -p "$V"; curl -fsSL -o "$V/prompt_hook.wav" "$VOICE_PROMPT_URL" && log "음성 프롬프트 받음"
  [ -n "${VOICE_PROMPT_TEXT:-}" ] && printf '%s' "$VOICE_PROMPT_TEXT" > "$V/prompt_hook.txt"
fi
#    없으면 video-files 브랜치에 올려 둔 샘플(라플라스_작업중/voice/)에서 꺼낸다 (파일 내용만 받음)
if [ ! -s "$V/prompt_hook.wav" ]; then
  mkdir -p "$V"; VF="라플라스_작업중/voice"
  ( cd "$CLAUDE_PROJECT_DIR" && git -c remote.origin.promisor=true -c remote.origin.partialclonefilter=blob:none fetch -q --filter=blob:none origin video-files \
    && git -c remote.origin.promisor=true show "origin/video-files:$VF/prompt_hook.wav" > "$V/prompt_hook.wav" \
    && git -c remote.origin.promisor=true show "origin/video-files:$VF/prompt_hook.txt" > "$V/prompt_hook.txt" ) \
    && log "음성 프롬프트: video-files 에서 받음" || { rm -f "$V/prompt_hook.wav"; log "음성 프롬프트 못 받음"; }
fi
log "완료"
