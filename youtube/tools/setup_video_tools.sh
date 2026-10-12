#!/usr/bin/env bash
# 새 세션에서 영상 도구 다시 설치 (스킬은 .claude/skills 에 커밋되어 있음)
set -e
npm i -g hyperframes                       # HyperFrames CLI
apt-get update -q
apt-get install -y -q libcairo2-dev libpango1.0-dev pkg-config ffmpeg
apt-get install -y -q --no-install-recommends texlive-latex-base texlive-latex-extra \
  texlive-fonts-recommended texlive-science dvisvgm   # Manim MathTex 용
# 시스템 pip 은 srt 빌드가 깨져서 uv 가상환경 사용
uv venv -q ~/.venvs/manim --python 3.11
uv pip install -q --python ~/.venvs/manim/bin/python manim
echo "manim: ~/.venvs/manim/bin/manim  ·  hyperframes: $(hyperframes --version)"
# Remotion 은 프로젝트마다: npm i remotion @remotion/cli react react-dom
# Blender 4.2 LTS (헤드리스 렌더용, GPU 없음 → Cycles CPU 로 렌더. EEVEE 는 libEGL 필요해서 안 됨)
if ! command -v blender >/dev/null; then
  mkdir -p ~/opt && curl -sSfL https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz | tar xJ -C ~/opt
  ln -sf ~/opt/blender-4.2.3-linux-x64/blender /usr/local/bin/blender
fi
blender --version | head -1
# HyperFrames 렌더용 크롬 + 선택 기능(받아쓰기 whisper.cpp · 음성 Kokoro · 배경음악 MusicGen · Parakeet)
hyperframes browser ensure
if ! command -v whisper-cli >/dev/null; then
  mkdir -p ~/opt && git clone -q --depth 1 https://github.com/ggml-org/whisper.cpp.git ~/opt/whisper.cpp
  (cd ~/opt/whisper.cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j4 --config Release) >/dev/null
  ln -sf ~/opt/whisper.cpp/build/bin/whisper-cli /usr/local/bin/whisper-cli
fi
pip install -q kokoro-onnx soundfile transformers numpy
pip install -q --index-url https://download.pytorch.org/whl/cpu torch
hyperframes models install parakeet
python3 -c "from rembg import new_session; new_session('u2net')"   # 썸네일 배경 제거 모델 미리 받기
hyperframes doctor | grep -E '✓|✗'
