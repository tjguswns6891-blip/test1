#!/usr/bin/env python3
"""구글 드라이브 공유 링크에서 촬영 원본을 내려받는 도구.

드라이브에서 파일(또는 폴더) → 공유 → 일반 액세스를 "링크가 있는 모든 사용자"(뷰어)로 바꾼 뒤 링크를 복사한다.

사용 예:
  python3 fetch_drive.py "https://drive.google.com/file/d/<ID>/view?usp=sharing"
  python3 fetch_drive.py "https://drive.google.com/drive/folders/<ID>"   # 폴더 통째로 (gdown 필요)
  python3 fetch_drive.py <링크> -o youtube/raw/0928                      # 받을 폴더 지정

기본 저장 위치는 youtube/raw/ (git에 올라가지 않는다). 끊기면 다시 실행해 이어받는다.
파일 본문은 drive.usercontent.google.com 에서 받는다. (gdown 기본 경로인
*.googleusercontent.com 은 이 작업 환경의 네트워크에서 막혀 있다.)
"""
import argparse
import html
import os
import re
import sys

import requests

DL_URL = "https://drive.usercontent.google.com/download"
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".mts", ".webm", ".wav", ".m4a", ".mp3"}
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
CHUNK = 8 * 1024 * 1024


def file_id_of(url):
    m = re.search(r"/d/([\w-]+)|[?&]id=([\w-]+)", url)
    return m and (m.group(1) or m.group(2))


def resolve(session, file_id):
    """큰 파일의 '바이러스 검사 불가' 안내 페이지를 넘겨 실제 다운로드 파라미터를 얻는다."""
    params = {"id": file_id, "export": "download"}
    r = session.get(DL_URL, params=params, stream=True, timeout=60)
    r.raise_for_status()
    if "text/html" not in r.headers.get("content-type", ""):
        r.close()
        return params
    page = r.text
    fields = dict(re.findall(r'name="([^"]+)" value="([^"]*)"', page))
    if "confirm" not in fields:
        title = re.search(r"<title>(.*?)</title>", page, re.S)
        raise RuntimeError(f"다운로드 페이지를 해석하지 못했어요 ({title and title.group(1).strip()}). "
                           "공유 설정이나 하루 다운로드 한도를 확인해 주세요.")
    return {k: html.unescape(v) for k, v in fields.items()}


def download(session, file_id, out_dir, name=None):
    params = resolve(session, file_id)
    with session.get(DL_URL, params=params, stream=True, timeout=60) as r:
        r.raise_for_status()
        m = re.search(r'filename="([^"]+)"', r.headers.get("content-disposition", ""))
        name = name or (m.group(1) if m else file_id)
        total = int(r.headers.get("content-length", 0))
    dst = os.path.join(out_dir, name)
    have = os.path.getsize(dst) if os.path.exists(dst) else 0
    if total and have == total:
        print(f"이미 받음: {dst}")
        return dst
    headers = {"Range": f"bytes={have}-"} if have else {}
    with session.get(DL_URL, params=params, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        if have and r.status_code != 206:  # 이어받기를 지원하지 않으면 처음부터
            have = 0
        total = have + int(r.headers.get("content-length", 0))
        with open(dst, "ab" if have else "wb") as f:
            done = have
            for chunk in r.iter_content(CHUNK):
                f.write(chunk)
                done += len(chunk)
                pct = f"{done * 100 / total:5.1f}%" if total else ""
                print(f"\r  {name}  {done / 1e6:,.0f}/{total / 1e6:,.0f}MB {pct}", end="", file=sys.stderr)
    print(file=sys.stderr)
    if total and os.path.getsize(dst) != total:
        raise RuntimeError(f"받다가 끊겼어요 ({os.path.getsize(dst):,}/{total:,}바이트). 다시 실행하면 이어받아요.")
    return dst


def folder_files(url, out_dir):
    try:
        import gdown
    except ImportError:
        sys.exit("폴더 링크는 gdown이 필요해요. `pip install gdown` 으로 설치하세요.")
    items = gdown.download_folder(url, output=out_dir, quiet=True, remaining_ok=True, skip_download=True)
    if not items:
        raise RuntimeError("폴더 목록을 읽지 못했어요.")
    return [(it.id, it.local_path) for it in items]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", help="구글 드라이브 파일 또는 폴더 공유 링크")
    p.add_argument("-o", "--out", default=DEFAULT_OUT, help="저장할 폴더 (기본: youtube/raw)")
    args = p.parse_args()

    out = os.path.normpath(args.out)
    os.makedirs(out, exist_ok=True)
    session = requests.Session()
    files = []
    try:
        if "/folders/" in args.url:
            for fid, local in folder_files(args.url, out):
                os.makedirs(os.path.dirname(local), exist_ok=True)
                files.append(download(session, fid, os.path.dirname(local), os.path.basename(local)))
        else:
            fid = file_id_of(args.url)
            if not fid:
                sys.exit("링크에서 파일 ID를 찾지 못했어요. 드라이브의 '링크 복사'로 받은 주소를 넣어 주세요.")
            files.append(download(session, fid, out))
    except (requests.RequestException, RuntimeError) as e:
        sys.exit(f"내려받지 못했어요: {e}\n"
                 "공유 설정이 '링크가 있는 모든 사용자'인지 확인해 주세요. 하루 다운로드 한도에 걸린 경우엔 "
                 "몇 시간 뒤 다시 시도하거나 파일을 사본으로 만들어 새 링크를 주세요.")

    print("\n받은 파일:")
    for f in files:
        tag = "" if os.path.splitext(f)[1].lower() in VIDEO_EXT else "  (영상·음성 파일 아님)"
        print(f"  {f}  {os.path.getsize(f) / 1e6:,.1f}MB{tag}")


if __name__ == "__main__":
    main()
