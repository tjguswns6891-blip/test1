#!/usr/bin/env bash
# 새 세션에서 영상 도구 다시 설치 (스킬은 .claude/skills 에 커밋되어 있음)
set -e
npm i -g hyperframes                       # HyperFrames CLI
apt-get update -q
apt-get install -y -q libcairo2-dev libpango1.0-dev pkg-config ffmpeg
apt-get install -y -q --no-install-recommends texlive-latex-base texlive-latex-extra \
  texlive-fonts-recommended texlive-science dvisvgm   # Manim MathTex 용
# Blender: 화면 없이 EEVEE 렌더 (libEGL + Mesa 소프트웨어 GL 필요)
apt-get install -y -q blender libegl1 libegl-mesa0 libgl1-mesa-dri
# 시스템 pip 은 srt 빌드가 깨져서 uv 가상환경 사용
uv venv -q ~/.venvs/manim --python 3.11
uv pip install -q --python ~/.venvs/manim/bin/python manim
echo "blender: $(blender --version | head -1)  ·  manim: ~/.venvs/manim/bin/manim  ·  hyperframes: $(hyperframes --version)"
# Remotion 은 프로젝트마다: npm i remotion @remotion/cli react react-dom
# (선택) VoxCPM2 음성 합성 — CPU 로도 돎(한 문장 ≈ 2분, 모델 6GB). GPU 없으면 torch 는 CPU 판으로
# uv venv -q ~/.venvs/voxcpm --python 3.11
# uv pip install -q --python ~/.venvs/voxcpm/bin/python torch torchaudio --index-url https://download.pytorch.org/whl/cpu
# uv pip install -q --python ~/.venvs/voxcpm/bin/python voxcpm
# ~/.venvs/voxcpm/bin/voxcpm clone --device cpu --no-denoiser --reference-audio ref.wav --text "문장" --output out.wav
pip install --quiet soundfile   # emphasize.py (AI 음성 강조) 가 시스템 파이썬에서 씀
