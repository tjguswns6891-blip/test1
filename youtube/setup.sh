#!/usr/bin/env bash
# 영상 편집 도구 설치 (새 세션·새 컨테이너에서 한 번 실행)
#   bash youtube/setup.sh
# 이미 깔린 것은 건너뛴다.
set -e

# 1) 파이썬 패키지: 받아쓰기·카드 영상 읽기·드라이브 받기·썸네일 배경 제거·ffmpeg 예비
pip install -q faster-whisper opencv-python-headless gdown rembg imageio-ffmpeg pillow requests

# 2) 한글 폰트 (자막·썸네일·쇼츠 제목). github raw 는 막혀 있어서 jsDelivr 로 받는다.
mkdir -p ~/.fonts
for w in Black Bold Medium Regular; do
  f=~/.fonts/NotoSansCJKkr-$w.otf
  [ -s "$f" ] || curl -sSfL -o "$f" "https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/OTF/Korean/NotoSansCJKkr-$w.otf"
done
command -v fc-cache >/dev/null && fc-cache -f >/dev/null 2>&1 || true

# 3) 회사 로고용 simple-icons (tools/logos.js)
if [ ! -d ~/simple-icons/package ]; then
  mkdir -p ~/simple-icons && (cd ~/simple-icons && npm pack simple-icons -q >/dev/null && tar xzf simple-icons-*.tgz)
fi
[ -e ~/simple-icons/package/_data ] || ln -s data ~/simple-icons/package/_data

# 4) Whisper 모델 미리 받기 (약 1.6GB, 처음 한 번)
python3 -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"

command -v ffmpeg >/dev/null || echo "ffmpeg 없음 → imageio-ffmpeg 것을 씀"
echo "설치 끝"
