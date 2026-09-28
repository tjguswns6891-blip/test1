#!/usr/bin/env python3
"""구글 드라이브 공유 링크에서 촬영 원본을 내려받는 도구.

드라이브에서 파일(또는 폴더) → 공유 → 일반 액세스를 "링크가 있는 모든 사용자"(뷰어)로 바꾼 뒤 링크를 복사한다.

사용 예:
  python3 fetch_drive.py "https://drive.google.com/file/d/<ID>/view?usp=sharing"
  python3 fetch_drive.py "https://drive.google.com/drive/folders/<ID>"   # 폴더 통째로
  python3 fetch_drive.py <링크> -o youtube/raw/0928                      # 받을 폴더 지정

기본 저장 위치는 youtube/raw/ (git에 올라가지 않는다). 이미 받은 파일은 건너뛴다.
"""
import argparse
import os
import re
import sys

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".mts", ".webm", ".wav", ".m4a", ".mp3"}
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", help="구글 드라이브 파일 또는 폴더 공유 링크")
    p.add_argument("-o", "--out", default=DEFAULT_OUT, help="저장할 폴더 (기본: youtube/raw)")
    args = p.parse_args()

    try:
        import gdown
    except ImportError:
        sys.exit("gdown이 없어요. `pip install gdown` 으로 설치하세요.")

    out = os.path.normpath(args.out)
    os.makedirs(out, exist_ok=True)
    try:
        if "/folders/" in args.url:
            files = gdown.download_folder(args.url, output=out, quiet=False, remaining_ok=True, resume=True)
        else:
            m = re.search(r"/d/([\w-]+)|[?&]id=([\w-]+)", args.url)
            file_id = m and (m.group(1) or m.group(2))
            if not file_id:
                sys.exit("링크에서 파일 ID를 찾지 못했어요. 드라이브의 '링크 복사'로 받은 주소를 넣어 주세요.")
            path = gdown.download(id=file_id, output=out + os.sep, quiet=False, resume=True)
            files = [path] if path else None
    except Exception as e:
        files, err = None, e
    else:
        err = None
    if not files:
        sys.exit(f"내려받지 못했어요{f': {err}' if err else ''}\n"
                 "공유 설정이 '링크가 있는 모든 사용자'인지 확인해 주세요. "
                 "하루 다운로드 한도에 걸린 경우엔 몇 시간 뒤 다시 시도하거나 파일을 사본으로 만들어 새 링크를 주세요.")

    print("\n받은 파일:")
    for f in files:
        size = os.path.getsize(f) / 1e6
        tag = "" if os.path.splitext(f)[1].lower() in VIDEO_EXT else "  (영상·음성 파일 아님)"
        print(f"  {f}  {size:,.1f}MB{tag}")


if __name__ == "__main__":
    main()
